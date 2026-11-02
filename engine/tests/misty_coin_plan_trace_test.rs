//! R8-07a's before/after record of Misty and the shared Trainer coin plan. Each scenario plays a
//! fixed board through every pending choice, a scripted pick at each one, and after every action
//! records: the State (serde_json), the offered actions (canonical order) with
//! `try_forecast_action`'s probabilities or error and the state each branch leaves, whether the
//! game RNG advanced, both seats' `PlayerObservation`, Game adoption of the referee state and of
//! each seat's redacted `search_state`, a fixed-seed `search_state_with_opponent_list`, and the
//! picks of WeightedRandomPlayer (every seed) and km3 (seed 0, pending choices). A Red Card at the
//! end shuffles the opponent's deck, so the record also fingerprints the RNG state left behind.
//!
//! With `MISTY_TRACE_OUT` set, the record is written to that file, and two commits' records can be
//! compared byte for byte; without it the scenarios run as a smoke test. Hashes are FNV-1a over
//! the JSON. The test names no card added after c4431a48, so the same file builds at both.

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
    models::{EnergyType, PlayedCard},
    observation::canonical_actions,
    players::{create_players, Player, PlayerCode},
    protocol::PublicEvent,
    test_support::get_initialized_game,
    Deck, Game, State,
};
use rand::{rngs::StdRng, SeedableRng};
use strum::IntoEnumIterator;

const SEEDS: u64 = 16;
const MAX_STEPS: usize = 16;

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

/// A scripted pick: the first offered action it matches. `Force` plays the card from hand
/// directly, past move generation (the one-Supporter scaffold of `misty_unbounded_test.rs`).
#[derive(Clone, Copy, Debug)]
enum Pick {
    Play(&'static str),
    Force(CardId),
    UseAbility(usize),
    UseStadium,
    Target(usize),
    Keep,
    Reroll,
}

impl Pick {
    fn matches(self, action: &SimpleAction) -> bool {
        match (self, action) {
            (Pick::Play(name), SimpleAction::Play { trainer_card }) => trainer_card.name == name,
            (Pick::UseAbility(index), SimpleAction::UseAbility { in_play_idx }) => {
                *in_play_idx == index
            }
            (Pick::UseStadium, SimpleAction::UseStadium) => true,
            (Pick::Target(index), SimpleAction::ChooseMistyTarget { in_play_idx }) => {
                *in_play_idx == index
            }
            (Pick::Keep, SimpleAction::KeepTrainerCoinResults) => true,
            (Pick::Reroll, SimpleAction::RerollTrainerCoins { .. }) => true,
            _ => false,
        }
    }
}

/// Plays the script inside `Game::play_tick`; the first offered action when nothing matches.
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
        actions[0].clone()
    }
}

/// The board every scenario starts from: player 0 to act on turn 3.
#[derive(Clone)]
struct Setup {
    own: Vec<PlayedCard>,
    hand0: Vec<CardId>,
    hand1: Vec<CardId>,
    deck1: Vec<CardId>,
    discard0: Vec<CardId>,
    stadium: Option<CardId>,
    luxury_coin_used: bool,
}

/// Active Squirtle (20 damage, Lucky Ice Pop's heal), Benched Psyduck ([W], Misty's other target)
/// and Pikachu (Electric Generator's [L]); with `gholdengo`, Gholdengo on the last Bench slot.
fn water_board(gholdengo: bool) -> Vec<PlayedCard> {
    let mut own = vec![
        PlayedCard::from_id(CardId::A1053Squirtle).with_damage(20),
        PlayedCard::from_id(CardId::A1057Psyduck),
        PlayedCard::from_id(CardId::A1094Pikachu),
    ];
    if gholdengo {
        own.push(PlayedCard::from_id(CardId::B4a051Gholdengo));
    }
    own
}

/// Smeargle (Portrait) Active, Squirtle and Psyduck Benched; with `gholdengo`, Gholdengo too.
fn portrait_board(gholdengo: bool) -> Vec<PlayedCard> {
    let mut own = vec![
        PlayedCard::from_id(CardId::B2130Smeargle),
        PlayedCard::from_id(CardId::A1053Squirtle),
        PlayedCard::from_id(CardId::A1057Psyduck),
    ];
    if gholdengo {
        own.push(PlayedCard::from_id(CardId::B4a051Gholdengo));
    }
    own
}

fn setup(own: Vec<PlayedCard>, hand0: &[CardId]) -> Setup {
    Setup {
        own,
        hand0: hand0.to_vec(),
        hand1: vec![CardId::A1001Bulbasaur, CardId::A1033Charmander],
        deck1: vec![
            CardId::A1220Misty,
            CardId::A1220Misty,
            CardId::A1225Sabrina,
            CardId::PA001Potion,
            CardId::PA005PokeBall,
            CardId::A1001Bulbasaur,
            CardId::A1033Charmander,
        ],
        discard0: vec![],
        stadium: None,
        luxury_coin_used: false,
    }
}

impl Setup {
    fn state(&self, seed: u64) -> State {
        let mut state = get_initialized_game(seed).get_state_clone();
        state.current_player = 0;
        state.turn_count = 3;
        state.set_board(
            self.own.clone(),
            vec![PlayedCard::from_id(CardId::A1001Bulbasaur)
                .with_energy(vec![EnergyType::Grass, EnergyType::Grass])],
        );
        state.hands[0] = self.hand0.iter().map(|id| get_card_by_enum(*id)).collect();
        state.hands[1] = self.hand1.iter().map(|id| get_card_by_enum(*id)).collect();
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
        state.discard_piles = [
            self.discard0.iter().map(|id| get_card_by_enum(*id)).collect(),
            vec![],
        ];
        state.active_stadium = self.stadium.map(get_card_by_enum);
        state.active_stadium_owner = self.stadium.map(|_| 0);
        state.luxury_coin_used_this_turn[0] = self.luxury_coin_used;
        state
    }
}

/// Each seat's guess at the other's list, for `search_state_with_opponent_list`.
fn opponent_list(seat: usize) -> Deck {
    let ids: &[CardId] = if seat == 0 {
        &[
            CardId::A1220Misty,
            CardId::A1220Misty,
            CardId::A1225Sabrina,
            CardId::A3b069Penny,
            CardId::A4156Will,
            CardId::PA001Potion,
            CardId::PA005PokeBall,
            CardId::A1001Bulbasaur,
            CardId::A1001Bulbasaur,
            CardId::A1033Charmander,
            CardId::A1033Charmander,
        ]
    } else {
        &[
            CardId::A1220Misty,
            CardId::A3b069Penny,
            CardId::A4156Will,
            CardId::PA001Potion,
            CardId::PA005PokeBall,
            CardId::A1053Squirtle,
            CardId::A1057Psyduck,
            CardId::A1094Pikachu,
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

fn record(game: &Game<'static>, km3: bool, out: &mut String) {
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
        if km3 && !state.move_generation_stack.is_empty() {
            let _ = writeln!(
                out,
                "  km3 {}",
                pick_of(PlayerCode::KM { max_depth: 3 }, game, actor, &actions)
            );
        }
    }
}

fn run(name: &str, setup: &Setup, picks: &[Pick], out: &mut String) {
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
        for _ in 0..MAX_STEPS {
            let current = game.get_state_clone();
            let next = queue.borrow().front().copied();
            if next.is_none() && current.move_generation_stack.is_empty() {
                break;
            }
            let (_, actions) = current.generate_possible_actions();
            if let Some(Pick::Force(id)) = next {
                queue.borrow_mut().pop_front();
                let action = Action {
                    actor: 0,
                    action: SimpleAction::Play {
                        trainer_card: get_card_by_enum(id).as_trainer(),
                    },
                    is_stack: false,
                };
                game.apply_action(&action);
                let _ = writeln!(out, "forced {}", label(&action));
            } else {
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
            }
            record(&game, seed == 0, out);
        }
        let _ = writeln!(out, "luxury coin {:?}", game.luxury_coin_resolution_history());
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
}

fn with_gholdengo_variants(name: &str, base: &Setup, play: Pick, out: &mut String) {
    run(&format!("{name} keep"), base, &[play, Pick::Keep], out);
    run(&format!("{name} reroll"), base, &[play, Pick::Reroll], out);
}

#[test]
fn misty_and_the_trainer_coin_plan_trace() {
    use CardId::*;
    let mut out = String::new();

    // Misty, direct.
    run("misty", &setup(water_board(false), &[A1220Misty]), &[Pick::Play("Misty"), Pick::Target(1)], &mut out);
    let mut heal_block = water_board(false);
    heal_block[2] = PlayedCard::from_id(A3a031Claydol);
    run("misty heal block", &setup(heal_block, &[A1220Misty]), &[Pick::Play("Misty"), Pick::Target(1)], &mut out);
    for (name, reroll) in [("misty gholdengo keep", false), ("misty gholdengo reroll", true)] {
        let last = if reroll { Pick::Reroll } else { Pick::Keep };
        run(name, &setup(water_board(true), &[A1220Misty]), &[Pick::Play("Misty"), Pick::Target(1), last], &mut out);
    }
    let mut spent = setup(water_board(true), &[A1220Misty]);
    spent.luxury_coin_used = true;
    run("misty spent luxury coin", &spent, &[Pick::Play("Misty"), Pick::Target(1)], &mut out);
    run("will then misty", &setup(water_board(false), &[A4156Will, A1220Misty]), &[Pick::Play("Will"), Pick::Force(A1220Misty), Pick::Target(1)], &mut out);
    run("will then misty gholdengo", &setup(water_board(true), &[A4156Will, A1220Misty]), &[Pick::Play("Will"), Pick::Force(A1220Misty), Pick::Target(1), Pick::Reroll], &mut out);

    // Penny copying Misty.
    run("penny misty", &setup(water_board(false), &[A3b069Penny]), &[Pick::Play("Penny"), Pick::Target(1)], &mut out);
    for (name, last) in [("penny misty gholdengo keep", Pick::Keep), ("penny misty gholdengo reroll", Pick::Reroll)] {
        run(name, &setup(water_board(true), &[A3b069Penny]), &[Pick::Play("Penny"), Pick::Target(1), last], &mut out);
    }
    run("will then penny misty gholdengo", &setup(water_board(true), &[A4156Will, A3b069Penny]), &[Pick::Play("Will"), Pick::Force(A3b069Penny), Pick::Target(1), Pick::Reroll], &mut out);
    let mut nonproducer = setup(water_board(true), &[A3b069Penny]);
    nonproducer.deck1 = vec![A1225Sabrina, PA001Potion, A1001Bulbasaur];
    run("penny non-producer gholdengo", &nonproducer, &[Pick::Play("Penny")], &mut out);

    // Portrait copying Misty, Penny, or Will.
    for gholdengo in [false, true] {
        let mut portrait = setup(portrait_board(gholdengo), &[]);
        portrait.hand1 = vec![A1220Misty, A1001Bulbasaur];
        run(&format!("portrait misty gholdengo {gholdengo}"), &portrait, &[Pick::UseAbility(0), Pick::Target(1)], &mut out);
    }
    let mut portrait_penny = setup(portrait_board(true), &[]);
    portrait_penny.hand1 = vec![A3b069Penny, A1001Bulbasaur];
    run("portrait penny misty gholdengo", &portrait_penny, &[Pick::UseAbility(0), Pick::Target(1)], &mut out);
    let mut portrait_will = setup(portrait_board(true), &[A1220Misty]);
    portrait_will.hand1 = vec![A4156Will, A1001Bulbasaur];
    run("portrait will then misty gholdengo", &portrait_will, &[Pick::UseAbility(0), Pick::Play("Misty"), Pick::Target(1), Pick::Reroll], &mut out);
    let mut portrait_will_penny = setup(portrait_board(true), &[A3b069Penny]);
    portrait_will_penny.hand1 = vec![A4156Will, A1001Bulbasaur];
    run("portrait will then penny misty gholdengo", &portrait_will_penny, &[Pick::UseAbility(0), Pick::Play("Penny"), Pick::Target(1), Pick::Reroll], &mut out);

    // The other registered producers and the Stadium route under Luxury Coin.
    for (name, id) in [
        ("Team Rocket Grunt", A2b072TeamRocketGrunt),
        ("Order Pad", B4145OrderPad),
        ("Lucky Ice Pop", B2145LuckyIcePop),
        ("Team Rocket's Researcher", B4a069TeamRocketsResearcher),
        ("Team Rocket's Master Plan", B4a070TeamRocketsMasterPlan),
        ("Hitting Hammer", B1215HittingHammer),
        ("Electric Generator", B2a086ElectricGenerator),
        ("Arven", B2a091Arven),
    ] {
        assert_eq!(get_card_by_enum(id).get_name(), name);
        with_gholdengo_variants(name, &setup(water_board(true), &[id]), Pick::Play(name), &mut out);
    }
    let mut fisher = setup(water_board(true), &[A4159Fisher]);
    fisher.discard0 = vec![A1053Squirtle, A1057Psyduck];
    with_gholdengo_variants("fisher", &fisher, Pick::Play("Fisher"), &mut out);
    for (name, stadium) in [("mesagoza", B2a093Mesagoza), ("arcade", B4a072Arcade)] {
        let mut board = setup(water_board(true), &[]);
        board.stadium = Some(stadium);
        with_gholdengo_variants(name, &board, Pick::UseStadium, &mut out);
    }
    run("potion", &setup(water_board(false), &[PA001Potion]), &[Pick::Play("Potion")], &mut out);

    assert!(out.contains("== potion seed 15"));
    if let Ok(path) = std::env::var("MISTY_TRACE_OUT") {
        std::fs::write(path, &out).unwrap();
    }
}
