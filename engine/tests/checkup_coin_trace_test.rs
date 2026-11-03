//! R8-08d's before/after record of Pokémon Checkup. Each scenario plays a fixed board from player
//! 0's turn 3 through two Checkups (to player 0's turn 5), a scripted pick at each decision, and
//! after every action records: the State (serde_json), the offered actions (canonical order) with
//! `try_forecast_action`'s probabilities or error and the state each branch leaves (this is every
//! Checkup outcome list, for `EndTurn`, `ResolvePokemonCheckup` and `FinishPokemonCheckup` alike),
//! whether the game RNG advanced, both seats' `PlayerObservation`, Game adoption of the referee
//! state and of each seat's redacted `search_state`, a fixed-seed
//! `search_state_with_opponent_list`, and at every decision with two or more options the picks of
//! WeightedRandomPlayer (every seed) and of km3, y3 and x3 (seed 0). All three price the Checkup
//! forecast of an `EndTurn` they reach, except one whose next player's Active searches a deck
//! unknown to them (`observation.rs:389-405`; 24a's Meloetta), and none searches the opponent's
//! reply: run through `decision_fn` on an observation, the opponent's hand and deck are Unknown,
//! so every opponent node returns at once (`expectiminimax_player.rs:773-798`). y3 and x3 add a
//! different evaluator (`public_baseline`), and y3 (consistent horizon) its inline `EndTurn`
//! forecast at depth 0. A Red Card at the end shuffles the opponent's deck, so the record also
//! fingerprints the RNG state left behind.
//!
//! Every scenario also asserts what its first Checkup forecast (turn 3's `EndTurn` and the
//! deferred Checkup frames after it) looked like: the branch count of each step, every branch
//! equally likely, or, where Meloetta's start-of-turn search splits the Checkup further, each
//! step's exact probabilities. This proves each board reaches the path it is meant to exercise.
//!
//! The record is pinned: its FNV-1a must equal `EXPECTED_RECORD_FNV`, the record at 8484daa8, so
//! the test fails on any change to it (in the suite's release build). With `CHECKUP_TRACE_OUT`
//! set, the record is also written to that file, and two commits' records can be compared byte for
//! byte. Hashes are FNV-1a over the JSON. The test names no card added after 8484daa8, so the same
//! file builds at both.

use std::{
    cell::RefCell,
    collections::VecDeque,
    fmt::Write as _,
    panic::{catch_unwind, AssertUnwindSafe},
    rc::Rc,
};

use deckgym::{
    actions::{try_forecast_action, Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard, StatusCondition},
    observation::canonical_actions,
    players::{create_players, Player, PlayerCode},
    protocol::PublicEvent,
    state::GameOutcome,
    test_support::get_initialized_game,
    Deck, Game, State,
};
use rand::{rngs::StdRng, SeedableRng};
use strum::IntoEnumIterator;

const SEEDS: u64 = 16;
/// Enough ticks to pass both Checkups on every board; a scenario that does not reach player 0's
/// turn 5 within it fails.
const MAX_STEPS: usize = 24;
/// FNV-1a of the whole record at 8484daa8 (R8-08 part 1 fix, before Soothing Lullaby and Wings of
/// the Moone), 1,990,788 bytes. The boards added in the R8-08 part 2a fix (20 steel apron, 20
/// soothing wind, 24a-24d, 25) and in R8-08f (16b, 20 steel apron on a non-[M] holder, 21 sand
/// slammer on the bench) were recorded on that commit's engine as well; every board's lines are
/// byte for byte those of the record it was added in.
const EXPECTED_RECORD_FNV: &str = "1e07ca5347ea46f4";

fn fnv(text: &str) -> u64 {
    let mut hash = 0xcbf2_9ce4_8422_2325_u64;
    for byte in text.bytes() {
        hash ^= u64::from(byte);
        hash = hash.wrapping_mul(0x0000_0100_0000_01b3);
    }
    hash
}

fn hash<T: serde::Serialize>(value: &T) -> String {
    format!("{:016x}", fnv(&serde_json::to_string(value).unwrap()))
}

fn label(action: &Action) -> String {
    format!("{}|{}|{}", action.actor, action.is_stack, action.action)
}

/// A scripted pick: the first offered action it matches.
#[derive(Clone, Copy, Debug)]
enum Pick {
    Play(&'static str),
    Attack(&'static str),
    UseAbility(usize),
    Evolve(usize),
}

impl Pick {
    fn matches(self, action: &SimpleAction) -> bool {
        match (self, action) {
            (Pick::Play(name), SimpleAction::Play { trainer_card }) => trainer_card.name == name,
            (Pick::Attack(title), SimpleAction::Attack(attack)) => attack.title == title,
            (Pick::UseAbility(index), SimpleAction::UseAbility { in_play_idx }) => {
                *in_play_idx == index
            }
            (Pick::Evolve(index), SimpleAction::Evolve { in_play_idx, .. }) => {
                *in_play_idx == index
            }
            _ => false,
        }
    }
}

/// Plays the script inside `Game::play_tick`. When nothing matches it ends the turn if it may,
/// and otherwise takes the first offered action.
#[derive(Debug)]
struct Scripted {
    seat: usize,
    picks: Rc<RefCell<VecDeque<Pick>>>,
    chances: Rc<RefCell<Vec<bool>>>,
}

impl Player for Scripted {
    fn get_deck(&self) -> Deck {
        Deck::default()
    }

    fn on_public_event(&mut self, event: &PublicEvent) {
        if self.seat == 0 {
            self.chances.borrow_mut().push(event.chance);
        }
    }

    fn decide_omniscient(&mut self, _: &mut StdRng, _: &State, actions: &[Action]) -> Action {
        let mut picks = self.picks.borrow_mut();
        if let Some(pick) = picks.front().copied() {
            if let Some(action) = actions.iter().find(|action| pick.matches(&action.action)) {
                picks.pop_front();
                return action.clone();
            }
        }
        actions
            .iter()
            .find(|action| matches!(action.action, SimpleAction::EndTurn))
            .unwrap_or(&actions[0])
            .clone()
    }
}

/// What a scenario's first Checkup must look like: each step applied on turn 3 from `EndTurn`
/// on (`checkup_step`) with its forecast's branch count.
enum First {
    Always(Vec<(&'static str, usize)>),
    /// Decided by an earlier random pick: `asleep` when `seat`'s Active is Asleep at `EndTurn`,
    /// otherwise `awake`. Both must occur across the seeds.
    IfAsleep {
        seat: usize,
        asleep: Vec<(&'static str, usize)>,
        awake: Vec<(&'static str, usize)>,
    },
    /// Each step with its forecast's exact probabilities: the Checkup coins times the next
    /// player's start-of-turn search (Meloetta's Strange Singing), coin outer, search inner.
    Exact(Vec<(&'static str, Vec<f64>)>),
}

/// A first Checkup with no deferred frame: `EndTurn` alone, with `branches` outcomes.
fn end_turn(branches: usize) -> First {
    First::Always(vec![("EndTurn", branches)])
}

/// The end-of-turn steps whose forecasts make up a Checkup.
fn checkup_step(action: &SimpleAction) -> Option<&'static str> {
    match action {
        SimpleAction::EndTurn => Some("EndTurn"),
        SimpleAction::ResolveEndTurnEvolution { .. } => Some("ResolveEndTurnEvolution"),
        SimpleAction::ResolveKnockoutPoints { .. } => Some("ResolveKnockoutPoints"),
        SimpleAction::ResolvePokemonCheckup => Some("ResolvePokemonCheckup"),
        SimpleAction::FinishPokemonCheckup => Some("FinishPokemonCheckup"),
        _ => None,
    }
}

/// The board every scenario starts from: player 0 to act on turn 3.
#[derive(Clone)]
struct Setup {
    own: Vec<PlayedCard>,
    opp: Vec<PlayedCard>,
    hand0: Vec<CardId>,
    deck1: Vec<CardId>,
}

fn setup(own: Vec<PlayedCard>, opp: Vec<PlayedCard>, hand0: &[CardId]) -> Setup {
    Setup {
        own,
        opp,
        hand0: hand0.to_vec(),
        deck1: vec![
            CardId::A1220Misty,
            CardId::A1220Misty,
            CardId::A1225Sabrina,
            CardId::PA001Potion,
            CardId::PA005PokeBall,
            CardId::A1001Bulbasaur,
            CardId::A1033Charmander,
        ],
    }
}

impl Setup {
    fn state(&self, seed: u64) -> State {
        let mut state = get_initialized_game(seed).get_state_clone();
        state.current_player = 0;
        state.turn_count = 3;
        state.set_board(self.own.clone(), self.opp.clone());
        state.hands[0] = self.hand0.iter().map(|id| get_card_by_enum(*id)).collect();
        state.hands[1] = [CardId::A1001Bulbasaur, CardId::A1033Charmander]
            .iter()
            .map(|id| get_card_by_enum(*id))
            .collect();
        state.decks[0].cards = [
            CardId::A1001Bulbasaur,
            CardId::A1033Charmander,
            CardId::PA001Potion,
            CardId::PA005PokeBall,
            CardId::A2147GiantCape,
            CardId::A1053Squirtle,
        ]
        .iter()
        .map(|id| get_card_by_enum(*id))
        .collect();
        state.decks[1].cards = self.deck1.iter().map(|id| get_card_by_enum(*id)).collect();
        state.discard_piles = [vec![], vec![]];
        state
    }
}

/// `id` in play with `conditions`, set directly as `with_status_condition` does (a mid-game board).
fn with(id: CardId, conditions: &[StatusCondition]) -> PlayedCard {
    conditions
        .iter()
        .fold(PlayedCard::from_id(id), |card, &condition| card.with_status_condition(condition))
}

/// Also Poisoned for 20 at Checkup, as Toxicroak's Toxic (A2a 052) leaves it, built as
/// `comfey_recovery_test.rs` builds one: only that attack sets the amount, and an Asleep Active
/// cannot attack.
fn toxic(card: PlayedCard) -> PlayedCard {
    let mut encoded =
        serde_json::to_value(card.with_status_condition(StatusCondition::Poisoned)).unwrap();
    encoded["poison_checkup_damage"] = serde_json::json!(20);
    let card: PlayedCard = serde_json::from_value(encoded).unwrap();
    assert_eq!(serde_json::to_value(&card).unwrap()["poison_checkup_damage"], 20);
    card
}

/// Player 1's board: `active`, with Charmander on the Bench to promote after a knockout.
fn opp(active: PlayedCard) -> Vec<PlayedCard> {
    vec![active, PlayedCard::from_id(CardId::A1033Charmander)]
}

/// Bulbasaur with Vine Whip's [G][C] attached: player 1's Active, ready to attack on turn 4.
fn ready_bulbasaur(conditions: &[StatusCondition]) -> PlayedCard {
    with(CardId::A1001Bulbasaur, conditions).with_energy(vec![EnergyType::Grass, EnergyType::Grass])
}

/// `setup` with two Abra and a Ralts on top of player 1's deck, for Meloetta's Strange Singing (B2
/// 070): "At the beginning of your turn, if this Pokémon is in the Active Spot, put a random [P]
/// Pokémon from your deck into your hand." One branch per card: 3 searches, each 1/3.
fn strange_singing(mut setup: Setup) -> Setup {
    setup.deck1.splice(0..0, [CardId::A1115Abra, CardId::A1115Abra, CardId::A1130Ralts]);
    setup
}

/// Each seat's guess at the other's list, for `search_state_with_opponent_list`.
fn opponent_list(seat: usize) -> Deck {
    let ids: &[CardId] = if seat == 0 {
        &[
            CardId::A1220Misty,
            CardId::A1220Misty,
            CardId::A1225Sabrina,
            CardId::A4156Will,
            CardId::PA001Potion,
            CardId::PA005PokeBall,
            CardId::A1001Bulbasaur,
            CardId::A1001Bulbasaur,
            CardId::A1033Charmander,
            CardId::A1033Charmander,
            CardId::B3b002Metapod,
        ]
    } else {
        &[
            CardId::A4156Will,
            CardId::C1122FullHeal,
            CardId::A3142BigMalasada,
            CardId::A1225Sabrina,
            CardId::PA001Potion,
            CardId::PA005PokeBall,
            CardId::A1053Squirtle,
            CardId::A1057Psyduck,
            CardId::A1001Bulbasaur,
            CardId::A1033Charmander,
            CardId::A2147GiantCape,
        ]
    };
    let mut deck = Deck::default();
    deck.cards = ids.iter().map(|id| get_card_by_enum(*id)).collect();
    deck
}

/// `try_forecast_action`'s probabilities and the state each branch leaves, or its error.
fn forecast(state: &State, action: &Action) -> String {
    catch_unwind(AssertUnwindSafe(|| match try_forecast_action(state, action) {
        Ok(outcomes) => {
            let (probabilities, mutations) = outcomes.into_branches();
            let successors = mutations
                .into_iter()
                .map(|mutation| {
                    let mut next = state.clone();
                    mutation(&mut StdRng::seed_from_u64(9), &mut next, action);
                    hash(&next)
                })
                .collect::<Vec<_>>();
            format!("ok {probabilities:?} {successors:?}")
        }
        Err(error) => format!("err {:?} {}", error.kind, error.reason),
    }))
    .unwrap_or_else(|_| "panic".to_string())
}

fn pick_of(code: PlayerCode, game: &Game<'static>, actor: usize, actions: &[Action]) -> String {
    let mut players = create_players(Deck::default(), Deck::default(), vec![code.clone(), code]);
    let observation = game.observation(actor);
    let chosen = players[actor].decision_fn(&mut StdRng::seed_from_u64(4), &observation, actions);
    label(&chosen)
}

/// The searches priced at seed 0.
fn searches() -> [(&'static str, PlayerCode); 3] {
    [
        ("km3", PlayerCode::KM { max_depth: 3 }),
        ("y3", PlayerCode::Y { max_depth: 3, opponent_ply: 3 }),
        ("x3", PlayerCode::X { max_depth: 3, opponent_ply: 3 }),
    ]
}

fn record(game: &Game<'static>, search: bool, out: &mut String) {
    let state = game.get_state_clone();
    let _ = writeln!(out, "  state {}", hash(&state));
    for seat in 0..2 {
        let observation = game.observation(seat);
        let redacted = observation.search_state(&mut StdRng::seed_from_u64(2));
        let adopted = Game::from_state(redacted, Vec::new(), 0).get_state_clone();
        let listed = observation
            .search_state_with_opponent_list(&mut StdRng::seed_from_u64(3), &opponent_list(seat));
        let _ = writeln!(
            out,
            "  seat {seat} observation {} redacted-adopted {} listed {}",
            hash(&observation),
            hash(&adopted),
            hash(&listed)
        );
    }
    let adopted = Game::from_state(state.clone(), Vec::new(), 0).get_state_clone();
    let _ = writeln!(out, "  adopted {} kept {}", hash(&adopted), adopted == state);
    if state.winner.is_some() {
        return;
    }
    let (actor, mut actions) = state.generate_possible_actions();
    canonical_actions(&mut actions);
    for action in &actions {
        let _ = writeln!(out, "  offer {} {}", label(action), forecast(&state, action));
    }
    if actions.len() > 1 {
        let _ = writeln!(out, "  w {}", pick_of(PlayerCode::W, game, actor, &actions));
        if search {
            for (name, code) in searches() {
                let _ = writeln!(out, "  {name} {}", pick_of(code, game, actor, &actions));
            }
        }
    }
}

fn run(name: &str, setup: &Setup, picks: &[Pick], first: First, out: &mut String) {
    let mut asleep_seen = [false; 2];
    for seed in 0..SEEDS {
        let _ = writeln!(out, "== {name} seed {seed}");
        let queue = Rc::new(RefCell::new(picks.iter().copied().collect::<VecDeque<_>>()));
        let chances = Rc::new(RefCell::new(Vec::new()));
        let players = (0..2)
            .map(|seat| {
                Box::new(Scripted {
                    seat,
                    picks: queue.clone(),
                    chances: chances.clone(),
                }) as Box<dyn Player>
            })
            .collect();
        let mut game = Game::from_state(setup.state(seed), players, seed);
        let _ = writeln!(out, "start");
        record(&game, seed == 0, out);
        let mut checkup: Vec<(&str, Vec<f64>)> = Vec::new();
        let mut asleep_at_end_turn = None;
        for _ in 0..MAX_STEPS {
            let current = game.get_state_clone();
            if game.is_game_over()
                || (current.turn_count >= 5 && current.move_generation_stack.is_empty())
            {
                break;
            }
            let (_, actions) = current.generate_possible_actions();
            let next = queue.borrow().front().copied();
            if let Some(pick) = next {
                let offered = actions.iter().any(|action| pick.matches(&action.action));
                if !offered && current.move_generation_stack.is_empty() {
                    let _ = writeln!(out, "not offered {pick:?}");
                    break;
                }
                if offered && actions.len() == 1 {
                    queue.borrow_mut().pop_front();
                }
            }
            let seen = chances.borrow().len();
            let action = game.play_tick();
            let chance = chances.borrow().get(seen).copied();
            let _ = writeln!(out, "tick {} chance {chance:?}", label(&action));
            if let Some(step) = checkup_step(&action.action).filter(|_| current.turn_count == 3) {
                if step == "EndTurn" {
                    asleep_at_end_turn = Some([0, 1].map(|player| {
                        current.in_play_pokemon[player][0]
                            .as_ref()
                            .is_some_and(|pokemon| pokemon.is_asleep())
                    }));
                }
                let (probabilities, _) = try_forecast_action(&current, &action).unwrap().into_branches();
                checkup.push((step, probabilities));
            }
            record(&game, seed == 0, out);
        }
        let state = game.get_state_clone();
        assert!(
            game.is_game_over() || (state.turn_count >= 5 && state.move_generation_stack.is_empty()),
            "{name} seed {seed}: did not pass two Checkups in {MAX_STEPS} steps"
        );

        let counts = checkup.iter().map(|(step, branches)| (*step, branches.len())).collect::<Vec<_>>();
        let _ = writeln!(out, "first checkup {counts:?}");
        if !matches!(first, First::Exact(_)) {
            for (step, probabilities) in &checkup {
                let equal = 1.0 / probabilities.len() as f64;
                assert!(
                    probabilities.iter().all(|probability| *probability == equal),
                    "{name} seed {seed}: {step} branches are not equally likely: {probabilities:?}"
                );
            }
        }
        let asleep = asleep_at_end_turn
            .unwrap_or_else(|| panic!("{name} seed {seed}: turn 3 never reached EndTurn"));
        let expected = match &first {
            First::Always(expected) => expected.clone(),
            First::IfAsleep { seat, asleep: when_asleep, awake } => {
                asleep_seen[usize::from(asleep[*seat])] = true;
                (if asleep[*seat] { when_asleep } else { awake }).clone()
            }
            First::Exact(steps) => {
                assert_eq!(&checkup, steps, "{name} seed {seed}: first Checkup probabilities");
                steps.iter().map(|(step, probabilities)| (*step, probabilities.len())).collect()
            }
        };
        assert_eq!(counts, expected, "{name} seed {seed}: first Checkup");

        // Red Card: the opponent shuffles their hand into their deck, so the order they draw from
        // fingerprints the gameplay RNG the scenario left behind. A small deck is a weak print
        // (rand 0.8 draws a short shuffle's indices from one word), so the deck is 60 distinct
        // cards.
        let mut state = game.get_state_clone();
        let red_card = get_card_by_enum(CardId::PA006RedCard);
        state.hands[0].push(red_card.clone());
        state.hands[1].clear();
        state.decks[1].cards = CardId::iter().take(60).map(get_card_by_enum).collect();
        game.set_state(state);
        game.apply_action(&Action {
            actor: 0,
            action: SimpleAction::Play {
                trainer_card: red_card.as_trainer(),
            },
            is_stack: false,
        });
        let after = game.get_state_clone();
        let _ = writeln!(
            out,
            "end rng {} {}",
            hash(&after.decks[1].cards),
            hash(&after.hands[1])
        );
    }
    if let First::IfAsleep { .. } = first {
        assert_eq!(asleep_seen, [true, true], "{name}: both outcomes of the earlier pick must occur");
    }
}

/// The states turn 3's `EndTurn` leaves at seed 0, one per branch of its forecast.
fn after_end_turn(setup: &Setup) -> Vec<State> {
    let state = setup.state(0);
    let action = Action {
        actor: 0,
        action: SimpleAction::EndTurn,
        is_stack: false,
    };
    let (_, mutations) = try_forecast_action(&state, &action).unwrap().into_branches();
    mutations
        .into_iter()
        .map(|mutation| {
            let mut next = state.clone();
            mutation(&mut StdRng::seed_from_u64(9), &mut next, &action);
            next
        })
        .collect()
}

#[test]
fn pokemon_checkup_coin_trace() {
    use CardId::*;
    use EnergyType::{Darkness, Fire, Grass, Lightning, Water};
    use StatusCondition::{Asleep, Burned, Poisoned};
    let mut out = String::new();
    let squirtle = |conditions: &[StatusCondition]| with(A1053Squirtle, conditions);
    let frosmoth = || PlayedCard::from_id(A1093Frosmoth).with_energy(vec![Water, Water]);

    // One coin per sleeper, then one per Burn, both seats in global order.
    run("1 own sleeper", &setup(vec![squirtle(&[Asleep])], opp(ready_bulbasaur(&[])), &[]), &[], end_turn(2), &mut out);
    run("2 powder snow", &setup(vec![frosmoth()], opp(ready_bulbasaur(&[])), &[]), &[Pick::Attack("Powder Snow")], end_turn(2), &mut out);
    run("3 both asleep", &setup(vec![squirtle(&[Asleep])], opp(ready_bulbasaur(&[Asleep])), &[]), &[], end_turn(4), &mut out);
    let magcargo = PlayedCard::from_id(A2026Magcargo).with_energy(vec![Fire, Fire]);
    run("4 searing flame on a sleeper", &setup(vec![magcargo], opp(with(A2026Magcargo, &[Asleep])), &[]), &[Pick::Attack("Searing Flame")], end_turn(4), &mut out);
    run("5 burned here asleep there", &setup(vec![squirtle(&[Burned])], opp(ready_bulbasaur(&[Asleep])), &[]), &[], end_turn(4), &mut out);
    let both = setup(
        vec![with(A2026Magcargo, &[Asleep, Burned, Poisoned])],
        opp(toxic(with(A2026Magcargo, &[Asleep, Burned]))),
        &[],
    );
    run("6 two sleeps two burns two poisons", &both, &[], end_turn(16), &mut out);
    let toxicroak = with(A2a052Toxicroak, &[Burned, Poisoned]).with_energy(vec![Darkness]);
    run("6b toxic on a burned sleeper", &setup(vec![toxicroak], opp(with(A2026Magcargo, &[Asleep, Burned])), &[]), &[Pick::Attack("Toxic")], end_turn(8), &mut out);
    run("7 burned only", &setup(vec![squirtle(&[Burned])], opp(ready_bulbasaur(&[])), &[]), &[], end_turn(2), &mut out);

    // Sleep replaced or removed before the Checkup.
    let galvantula = PlayedCard::from_id(A3b027Galvantula).with_energy(vec![Lightning, Lightning]);
    run("8 paralysis replaces sleep", &setup(vec![galvantula], opp(with(A2026Magcargo, &[Asleep])), &[]), &[Pick::Attack("Electric Shock")], end_turn(1), &mut out);
    let kricketune = PlayedCard::from_id(A2014Kricketune).with_energy(vec![Grass, Grass]);
    run("9 confusion replaces sleep", &setup(vec![kricketune], opp(ready_bulbasaur(&[Asleep])), &[]), &[Pick::Attack("Entrancing Melody")], end_turn(1), &mut out);
    run("10 full heal", &setup(vec![squirtle(&[Asleep])], opp(ready_bulbasaur(&[])), &[C1122FullHeal]), &[Pick::Play("Full Heal")], end_turn(1), &mut out);
    let lum_berry = squirtle(&[Asleep]).with_tool(get_card_by_enum(A2149LumBerry));
    run("11 lum berry", &setup(vec![lum_berry], opp(ready_bulbasaur(&[])), &[]), &[], end_turn(1), &mut out);
    run(
        "12 big malasada",
        &setup(vec![squirtle(&[Asleep, Poisoned])], opp(ready_bulbasaur(&[])), &[A3142BigMalasada]),
        &[Pick::Play("Big Malasada")],
        First::IfAsleep { seat: 0, asleep: vec![("EndTurn", 2)], awake: vec![("EndTurn", 1)] },
        &mut out,
    );
    run("13 evolution", &setup(vec![with(A1001Bulbasaur, &[Asleep])], opp(ready_bulbasaur(&[])), &[A1002Ivysaur]), &[Pick::Evolve(0)], end_turn(1), &mut out);
    let mut sabrina_opp = opp(ready_bulbasaur(&[Asleep]));
    sabrina_opp.push(PlayedCard::from_id(A1053Squirtle));
    run("14 sabrina", &setup(vec![squirtle(&[])], sabrina_opp, &[A1225Sabrina]), &[Pick::Play("Sabrina")], end_turn(1), &mut out);

    // Knockouts in the Checkup and at the end of the turn, and the deferred Checkup frames.
    let poisoned_sleeper = || with(A1001Bulbasaur, &[Asleep, Poisoned]).with_remaining_hp(10);
    run(
        "15 checkup knockout",
        &setup(vec![squirtle(&[])], opp(poisoned_sleeper()), &[]),
        &[],
        First::Always(vec![("EndTurn", 2), ("FinishPokemonCheckup", 1)]),
        &mut out,
    );
    let darkrai = || PlayedCard::from_id(B2b040Darkrai);
    run(
        "16 bad dreams knockout",
        &setup(vec![squirtle(&[]), darkrai()], opp(with(A1001Bulbasaur, &[Asleep]).with_remaining_hp(20)), &[]),
        &[],
        First::Always(vec![("EndTurn", 1), ("FinishPokemonCheckup", 1)]),
        &mut out,
    );
    // With no Benched Pokémon left to promote, Bad Dreams wins the game inside `on_end_turn`,
    // before the coins. Player 0's own sleeper stays in play, so `EndTurn` still has its coin's 2
    // branches, and in both the game is over with that Pokémon still Asleep: no coin was applied.
    let bad_dreams_win = setup(vec![squirtle(&[Asleep]), darkrai()], vec![with(A1001Bulbasaur, &[Asleep]).with_remaining_hp(20)], &[]);
    run("16b bad dreams win", &bad_dreams_win, &[], end_turn(2), &mut out);
    for state in after_end_turn(&bad_dreams_win) {
        assert_eq!(state.winner, Some(GameOutcome::Win(0)), "16b: Bad Dreams wins the game");
        assert!(
            state.in_play_pokemon[0][0].as_ref().is_some_and(|pokemon| pokemon.is_asleep()),
            "16b: no Checkup coin after the win"
        );
    }
    let mut quick_growth = setup(vec![squirtle(&[Asleep])], opp(PlayedCard::from_id(B3b001Caterpie)), &[]);
    quick_growth.deck1.insert(0, B3b002Metapod);
    run(
        "17a quick growth",
        &quick_growth,
        &[],
        First::Always(vec![("EndTurn", 1), ("ResolveEndTurnEvolution", 1), ("ResolvePokemonCheckup", 2)]),
        &mut out,
    );
    run(
        "17b shattering crystal",
        &setup(vec![squirtle(&[Asleep]), darkrai()], opp(with(B3a045Glimmora, &[Asleep]).with_remaining_hp(20)), &[]),
        &[],
        First::Always(vec![("EndTurn", 1), ("ResolveKnockoutPoints", 2), ("ResolvePokemonCheckup", 2)]),
        &mut out,
    );

    // Coins outside the Checkup: Will, and the Sleep Pendulum Ability.
    run("18 will", &setup(vec![squirtle(&[Asleep])], opp(ready_bulbasaur(&[])), &[A4156Will]), &[Pick::Play("Will")], end_turn(2), &mut out);
    run(
        "19 sleep pendulum",
        &setup(vec![PlayedCard::from_id(A1125Hypno)], opp(ready_bulbasaur(&[])), &[]),
        &[Pick::UseAbility(0)],
        First::IfAsleep { seat: 1, asleep: vec![("EndTurn", 2)], awake: vec![("EndTurn", 1)] },
        &mut out,
    );

    // Sleep prevented or immune: no sleeper. Crystal Body and Clear Veil stop the attack's effect;
    // Insomnia, Steel Apron on a [M] Pokémon and Soothing Wind (Ogerpon ex on the Bench, the
    // defender has Energy) are `apply_status_condition`'s own returns.
    let clear_veil = PlayedCard::from_id(A1001Bulbasaur).with_tool(get_card_by_enum(B4149ClearVeil));
    let steel_apron = PlayedCard::from_id(A1181Meltan).with_tool(get_card_by_enum(A4153SteelApron));
    for (name, defender) in [
        ("20 crystal body", PlayedCard::from_id(A2034Regice)),
        ("20 clear veil", clear_veil),
        ("20 insomnia", PlayedCard::from_id(A4140Hoothoot)),
        ("20 steel apron", steel_apron),
    ] {
        run(name, &setup(vec![frosmoth()], opp(defender), &[]), &[Pick::Attack("Powder Snow")], end_turn(1), &mut out);
    }
    let soothing_wind = vec![ready_bulbasaur(&[]), PlayedCard::from_id(B2017TealMaskOgerponEx), PlayedCard::from_id(A1033Charmander)];
    run("20 soothing wind", &setup(vec![frosmoth()], soothing_wind, &[]), &[Pick::Attack("Powder Snow")], end_turn(1), &mut out);
    // Steel Apron protects only a [M] holder: on Bulbasaur the Sleep lands.
    let apron_on_bulbasaur = PlayedCard::from_id(A1001Bulbasaur).with_tool(get_card_by_enum(A4153SteelApron));
    run("20 steel apron on a non-[M] holder", &setup(vec![frosmoth()], opp(apron_on_bulbasaur), &[]), &[Pick::Attack("Powder Snow")], end_turn(2), &mut out);

    // Checkup Abilities after the coins, then one knockout wave.
    run(
        "21 sand slammer",
        &setup(vec![squirtle(&[Asleep]).with_remaining_hp(10), PlayedCard::from_id(A1057Psyduck)], opp(PlayedCard::from_id(B3126FlygonEx)), &[]),
        &[],
        First::Always(vec![("EndTurn", 2), ("FinishPokemonCheckup", 1)]),
        &mut out,
    );
    // Sand Slammer, "do 10 damage to each of your opponent's Pokémon", Knocks Out only a Benched
    // Pokémon: a point for player 1, but no promotion and no winner, so player 1's turn starts.
    let bench_knockout = setup(vec![squirtle(&[Asleep]), PlayedCard::from_id(A1057Psyduck).with_remaining_hp(10)], opp(PlayedCard::from_id(B3126FlygonEx)), &[]);
    run("21 sand slammer on the bench", &bench_knockout, &[], end_turn(2), &mut out);
    for state in after_end_turn(&bench_knockout) {
        assert!(
            state.in_play_pokemon[0][0].is_some() && state.in_play_pokemon[0][1].is_none(),
            "21: only the Benched Psyduck is Knocked Out"
        );
        assert_eq!((state.points, state.winner, state.current_player), ([0, 1], None, 1), "21: the turn passes");
    }
    run("21 snowy terrain", &setup(vec![squirtle(&[Asleep])], opp(PlayedCard::from_id(A2a022GlaceonEx)), &[]), &[], end_turn(2), &mut out);
    let salted = vec![squirtle(&[Asleep]).with_damage(20), PlayedCard::from_id(B3a033Garganacl)];
    run("21 blessed salt", &setup(salted, opp(ready_bulbasaur(&[])), &[]), &[], end_turn(2), &mut out);

    // A sleeper's own turn with several options, priced by every search.
    run("22 searched sleeper", &setup(vec![squirtle(&[Asleep])], opp(ready_bulbasaur(&[])), &[A1033Charmander]), &[], end_turn(2), &mut out);

    // An ordinary Sleep on a Pokémon already Asleep.
    run("23a powder snow on a sleeper", &setup(vec![frosmoth()], opp(ready_bulbasaur(&[Asleep])), &[]), &[Pick::Attack("Powder Snow")], end_turn(2), &mut out);
    run("23b sleep pendulum on a sleeper", &setup(vec![PlayedCard::from_id(A1125Hypno)], opp(ready_bulbasaur(&[Asleep])), &[]), &[Pick::UseAbility(0)], end_turn(2), &mut out);

    // The next player's start-of-turn search after the coins (Meloetta's Strange Singing): one
    // branch per coin outcome and search, coin outer, search inner, each the product (24a). It
    // rides on `FinishPokemonCheckup` for a Meloetta promoted in the Checkup (24b), and it waits
    // there while player 0's Active, Knocked Out in the Checkup, is promoted (24c) or its
    // point-denial coin is pending (24d). Player 0 holds a Basic in 24a, so the searches decide
    // there; they leave that `EndTurn` unpriced (Meloetta next, player 1's deck unknown to them:
    // `observation.rs:389-405`).
    let meloetta = || PlayedCard::from_id(B2070Meloetta);
    run(
        "24a strange singing",
        &strange_singing(setup(vec![squirtle(&[Asleep])], opp(meloetta()), &[A1033Charmander])),
        &[],
        First::Exact(vec![("EndTurn", vec![1.0 / 6.0; 6])]),
        &mut out,
    );
    run(
        "24b strange singing after a promotion",
        &strange_singing(setup(vec![squirtle(&[])], vec![poisoned_sleeper(), meloetta()], &[])),
        &[],
        First::Exact(vec![("EndTurn", vec![0.5; 2]), ("FinishPokemonCheckup", vec![1.0 / 3.0; 3])]),
        &mut out,
    );
    let own_poisoned_sleeper = |id| vec![with(id, &[Asleep, Poisoned]).with_remaining_hp(10), PlayedCard::from_id(A1057Psyduck)];
    run(
        "24c strange singing waits for a promotion",
        &strange_singing(setup(own_poisoned_sleeper(A1053Squirtle), opp(meloetta()), &[])),
        &[],
        First::Exact(vec![("EndTurn", vec![0.5; 2]), ("FinishPokemonCheckup", vec![1.0 / 3.0; 3])]),
        &mut out,
    );
    run(
        "24d strange singing waits for a point-denial coin",
        &strange_singing(setup(own_poisoned_sleeper(B3a045Glimmora), opp(meloetta()), &[])),
        &[],
        First::Exact(vec![
            ("EndTurn", vec![0.5; 2]),
            ("ResolveKnockoutPoints", vec![0.5; 2]),
            ("FinishPokemonCheckup", vec![1.0 / 3.0; 3]),
        ]),
        &mut out,
    );

    // A Checkup Knock Out that ends the game: no turn follows it.
    run("25 checkup win", &setup(vec![squirtle(&[])], vec![poisoned_sleeper()], &[]), &[], end_turn(2), &mut out);

    assert!(out.contains("== 25 checkup win seed 15"));
    if let Ok(path) = std::env::var("CHECKUP_TRACE_OUT") {
        std::fs::write(path, &out).unwrap();
    }
    assert_eq!(
        format!("{:016x}", fnv(&out)),
        EXPECTED_RECORD_FNV,
        "the Pokémon Checkup record changed: rerun with CHECKUP_TRACE_OUT and diff it against the \
         record at 8484daa8"
    );
}
