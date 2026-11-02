//! Every Trainer reprint against its canonical printing: the first `CardId`, in enum order, with
//! the same name and effect text. That is the printing upstream's #395 dispatches a reprint to
//! (`trainer_identity::canonical_trainer_id`, which keys on the effect text alone; every Trainer
//! name has one text, and the only text two names share is the Fossils'). Until R8-02 this fork
//! keyed Trainer logic by CardId, with every printing listed in its arm or list; these tests pass
//! on that dispatch and hold R8-02's dispatch on the canonical id to the same results.
//!
//! - The rule: every printing resolves to a printing of the same name, text and type, and, but
//!   for the Fossils (played as Pokémon, dispatched by type), to upstream's effect-text printing.
//! - (a) The twin test, `b4b_reprint_arms_test.rs` widened to every set (its helpers are copied
//!   here, since each tests/*.rs file is its own crate). Every reprint has the card_status of its
//!   canonical printing, and from one prepared board (that test's Main board) both have the same
//!   legal actions (labels, id swapped). Where the canonical printing is legal there, both are
//!   played with the same seed and leave the same state (ids swapped) through every choice the
//!   play opens (the first offered choice each time); where it is not, the labels alone are
//!   compared.
//! - (b) The fork's id-keyed Trainer predicates give a reprint the answer they give its canonical
//!   printing. None of them is public, so each is read through the closest public path:
//!   - `is_misty_trainer` and `is_sweet_honey_trainer` (state/mod.rs, private): Game adoption
//!     (`Game::from_state` runs `State::sanitize_pending_choice_state`) keeps a staged Misty target
//!     only for a Misty source, a staged Sweet Honey target (the same slot, its own route) only for
//!     a Sweet Honey source, and a staged Luxury Coin choice with no fixed target only for a source
//!     that is neither (both fix their target before the coins).
//!   - `is_misty_card`, `is_researcher_card` (crate-only) and the Luxury Coin producer check
//!     (`trainer_coin_plan::is_registered_direct_producer`, private): the route a play takes from
//!     a board where Misty, Team Rocket's Researcher and the coin Trainers are legal, once with
//!     Luxury Coin used this turn (the plain route) and once with it ready (the coin route).
//!   - `stadium_route` (trainer_coin_plan.rs, private): using a Stadium reprint in play under
//!     Luxury Coin.

use std::collections::{BTreeMap, HashMap};

use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    card_validation::{get_implementation_status, ImplementationStatus},
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard, TrainerCard, TrainerType},
    state::{MistySourceRoute, TrainerCoinEffectRoute},
    test_support::{get_initialized_game, init_random_players},
    Game, State,
};
use strum::IntoEnumIterator;

const SEED: u64 = 7;
/// Choices a single play may open before the course must be over.
const MAX_CHOICES: usize = 8;

/// A Trainer printing and its canonical printing.
struct Printing {
    id: CardId,
    card: TrainerCard,
    canonical: CardId,
}

/// Every Trainer printing, in enum order, each with the first `CardId` of the same name and text.
fn printings() -> Vec<Printing> {
    let mut first: BTreeMap<(String, String), CardId> = BTreeMap::new();
    CardId::iter()
        .filter_map(|id| match get_card_by_enum(id) {
            Card::Trainer(card) => Some((id, card)),
            _ => None,
        })
        .map(|(id, card)| {
            let canonical = *first
                .entry((card.name.clone(), card.effect.clone()))
                .or_insert(id);
            Printing { id, card, canonical }
        })
        .collect()
}

/// The reprints: every printing that is not its own canonical printing.
fn reprints() -> Vec<Printing> {
    printings()
        .into_iter()
        .filter(|printing| printing.id != printing.canonical)
        .collect()
}

fn is_implemented(status: ImplementationStatus) -> bool {
    matches!(status, ImplementationStatus::Complete | ImplementationStatus::RulesUnverified)
}

#[test]
fn every_printing_resolves_to_the_first_printing_of_its_name_and_text() {
    let all = printings();
    let mut first_by_text: BTreeMap<String, CardId> = BTreeMap::new();
    for printing in &all {
        let card = &printing.card;
        let canonical = get_card_by_enum(printing.canonical).as_trainer();
        assert_eq!(canonical.name, card.name, "{} -> {}", card.id, canonical.id);
        assert_eq!(canonical.effect, card.effect, "{} -> {}", card.id, canonical.id);
        assert_eq!(canonical.trainer_card_type, card.trainer_card_type, "{}", card.id);
        let by_text = *first_by_text.entry(card.effect.clone()).or_insert(printing.id);
        if card.trainer_card_type != TrainerType::Fossil {
            assert_eq!(by_text, printing.canonical, "{}: upstream keys on the text alone", card.id);
        }
    }
    let reprints = all.iter().filter(|p| p.id != p.canonical).count();
    let fossil_reprints = all
        .iter()
        .filter(|p| p.id != p.canonical && p.card.trainer_card_type == TrainerType::Fossil)
        .count();
    // 416 Trainer printings; 239 reprints, 3 of them Old Amber.
    assert_eq!((all.len(), reprints, fossil_reprints), (416, 239, 3));
}

/// Player 0 to act on turn 3, a nonempty deck (from the initialized game), a Charmander in hand,
/// a [R] Energy in the discard pile and no Stadium.
fn ready(mut state: State) -> State {
    state.current_player = 0;
    state.turn_count = 3;
    state.active_stadium = None;
    state.active_stadium_owner = None;
    state.discard_energies[0] = vec![EnergyType::Fire];
    state.hands[0] = vec![get_card_by_enum(CardId::A1033Charmander)];
    assert!(!state.decks[0].cards.is_empty(), "the searches need a nonempty deck");
    assert!(state.move_generation_stack.is_empty());
    state
}

/// The twin test's board, `b4b_reprint_arms_test.rs`'s Main board. Active: Charmeleon (Stage 1
/// [R], 30 damage). Bench: Pikachu ([L], holding Giant Cape), Venusaur (Stage 2 [G]), Abra ([P],
/// 20 damage, two [P] Energy). The opponent has a Bulbasaur.
fn main_board() -> State {
    let mut state = get_initialized_game(SEED).get_state_clone();
    state.set_board(
        vec![
            PlayedCard::from_id(CardId::A1034Charmeleon).with_damage(30),
            PlayedCard::from_id(CardId::A1094Pikachu)
                .with_tool(get_card_by_enum(CardId::A2147GiantCape)),
            PlayedCard::from_id(CardId::A1003Venusaur),
            PlayedCard::from_id(CardId::A1115Abra)
                .with_energy(vec![EnergyType::Psychic, EnergyType::Psychic])
                .with_damage(20),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    ready(state)
}

/// The predicate board. As the Main board, with Magikarp ([W], Misty's target) and Gholdengo
/// (Luxury Coin) on the Bench in place of Venusaur and Abra, a Squirtle in the discard pile
/// (Fisher's target) and a [G] Energy on the opponent's Bulbasaur (Team Rocket Grunt's target).
/// With `luxury_coin_ready` false, Luxury Coin has been used this turn.
fn coin_board(luxury_coin_ready: bool) -> State {
    let mut state = get_initialized_game(SEED).get_state_clone();
    state.set_board(
        vec![
            PlayedCard::from_id(CardId::A1034Charmeleon).with_damage(30),
            PlayedCard::from_id(CardId::A1094Pikachu)
                .with_tool(get_card_by_enum(CardId::A2147GiantCape)),
            PlayedCard::from_id(CardId::A1077Magikarp),
            PlayedCard::from_id(CardId::B4a051Gholdengo),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur).with_energy(vec![EnergyType::Grass])],
    );
    state.discard_piles[0] = vec![get_card_by_enum(CardId::A1053Squirtle)];
    state.luxury_coin_used_this_turn[0] = !luxury_coin_ready;
    ready(state)
}

fn drop_printings(cards: &mut Vec<Card>, pair: &[String; 2]) {
    cards.retain(|card| !pair.contains(&card.get_id()));
}

/// `board` with every copy of the pair's two printings taken out of the hands, decks and discard
/// piles (the example decks hold P-A 005 and P-A 007, both reprints), so that the card under test
/// is the only place where the two states differ.
fn without_pair(board: &State, pair: &[String; 2]) -> State {
    let mut state = board.clone();
    for player in 0..2 {
        drop_printings(&mut state.hands[player], pair);
        drop_printings(&mut state.decks[player].cards, pair);
        drop_printings(&mut state.discard_piles[player], pair);
    }
    state
}

fn holding(board: &State, id: CardId, pair: &[String; 2]) -> State {
    let mut state = without_pair(board, pair);
    state.hands[0].push(get_card_by_enum(id));
    state
}

fn label(action: &Action) -> String {
    format!("{}|{}|{}", action.actor, action.is_stack, action.action)
}

fn labels(state: &State) -> Vec<String> {
    state.generate_possible_actions().1.iter().map(label).collect()
}

/// The first legal action that plays `id` from the hand: a Play, or a Fossil's Place.
fn play_of(state: &State, id: CardId) -> Option<Action> {
    let wanted = get_card_by_enum(id).get_id();
    state
        .generate_possible_actions()
        .1
        .into_iter()
        .find(|action| match &action.action {
            SimpleAction::Play { trainer_card } => trainer_card.id == wanted,
            SimpleAction::Place(Card::Trainer(trainer_card), _) => trainer_card.id == wanted,
            _ => false,
        })
}

fn use_of_stadium(state: &State) -> Option<Action> {
    state
        .generate_possible_actions()
        .1
        .into_iter()
        .find(|action| matches!(action.action, SimpleAction::UseStadium))
}

/// What a play leaves pending, read right after it.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Route {
    /// Neither of the two below.
    Plain,
    /// The pre-coin target choice in Misty's slot: Misty's (`is_misty_card`, or the coin plan's own
    /// Misty check) or, since R8-07a, Sweet Honey's.
    MistyTarget,
    /// Luxury Coin's keep-or-reroll choice (a registered producer, or `stadium_route`).
    LuxuryCoin,
}

fn route_of(state: &State) -> Route {
    if state.pending_misty_target_choice.is_some() {
        Route::MistyTarget
    } else if state.pending_trainer_coin_choice.is_some() {
        Route::LuxuryCoin
    } else {
        Route::Plain
    }
}

fn assert_same_text(base: &str, twin: &str, what: &str) {
    if base == twin {
        return;
    }
    let at = base.chars().zip(twin.chars()).take_while(|(a, b)| a == b).count();
    let window = |s: &str| s.chars().skip(at.saturating_sub(160)).take(320).collect::<String>();
    panic!(
        "{what}: first difference at character {at}\n  base: ...{}...\n  twin: ...{}...",
        window(base),
        window(twin)
    );
}

/// Plays `base_first` and `twin_first` from their states with the same seed, then the first offered
/// choice (matched by label) until no choice is pending, comparing the twin's labels and state, with
/// the twin's id written as the base's, with the base's at every step. Returns the route the base's
/// play took.
fn assert_same_course(
    ctx: &str,
    (base, base_first): (State, Action),
    (twin, twin_first): (State, Action),
    (base_id, twin_id): (&str, &str),
) -> Route {
    let as_base = |text: String| text.replace(twin_id, base_id);
    let twin_labels = |state: &State| labels(state).into_iter().map(as_base).collect::<Vec<_>>();
    assert_eq!(as_base(label(&twin_first)), label(&base_first), "{ctx}: the play itself");

    let mut base_game = Game::from_state(base, init_random_players(), SEED);
    let mut twin_game = Game::from_state(twin, init_random_players(), SEED);
    base_game.apply_action(&base_first);
    twin_game.apply_action(&twin_first);
    let route = route_of(&base_game.get_state_clone());
    for step in 1..=MAX_CHOICES {
        let (b, t) = (base_game.get_state_clone(), twin_game.get_state_clone());
        assert_same_text(
            &format!("{b:?}"),
            &as_base(format!("{t:?}")),
            &format!("{ctx}: state after step {step}"),
        );
        assert_eq!(twin_labels(&t), labels(&b), "{ctx}: legal actions after step {step}");
        if b.move_generation_stack.is_empty() {
            return route;
        }
        let base_actions = b.generate_possible_actions().1;
        let Some(base_next) = base_actions.first() else {
            return route;
        };
        let twin_next = t
            .generate_possible_actions()
            .1
            .into_iter()
            .find(|action| as_base(label(action)) == label(base_next))
            .unwrap_or_else(|| panic!("{ctx}: the twin is offered {}", label(base_next)));
        base_game.apply_action(base_next);
        twin_game.apply_action(&twin_next);
    }
    panic!("{ctx}: still choosing after {MAX_CHOICES} choices");
}

/// A reprint and its canonical printing, each alone in hand slot 1 of the same board: the same
/// legal actions (id swapped) and, where the canonical printing is legal, the same course. Returns
/// the route the play took, or `None` where only the labels could be compared.
fn compare_on_board(board_name: &str, board: &State, printing: &Printing) -> Option<Route> {
    let twin_id = printing.card.id.clone();
    let base_id = get_card_by_enum(printing.canonical).get_id();
    let ctx = format!("{twin_id} {} v {base_id} on {board_name}", printing.card.name);
    let pair = [twin_id.clone(), base_id.clone()];
    let base = holding(board, printing.canonical, &pair);
    let twin = holding(board, printing.id, &pair);
    let as_base = |text: String| text.replace(twin_id.as_str(), base_id.as_str());
    let twin_labels = labels(&twin).into_iter().map(as_base).collect::<Vec<_>>();
    assert_eq!(twin_labels, labels(&base), "{ctx}: legal actions before the play");
    let base_play = play_of(&base, printing.canonical)?;
    let twin_play = play_of(&twin, printing.id).expect("the labels match");
    Some(assert_same_course(
        &ctx,
        (base, base_play),
        (twin, twin_play),
        (base_id.as_str(), twin_id.as_str()),
    ))
}

/// (a) Every reprint in every set: the card_status of its canonical printing, and the same labels
/// and course from the Main board.
#[test]
fn every_reprint_plays_as_its_canonical_printing() {
    let board = main_board();
    let reprints = reprints();
    let mut played = Vec::new();
    for printing in &reprints {
        let status = get_implementation_status(printing.canonical);
        assert_eq!(
            get_implementation_status(printing.id),
            status,
            "{} {}: card_status v its canonical printing {:?}",
            printing.card.id,
            printing.card.name,
            printing.canonical
        );
        // A Trainer without an implementation in hand stops move generation ("Trainer card not
        // implemented"), so a refused pair is compared by its status alone.
        if !is_implemented(status) {
            continue;
        }
        if compare_on_board("the Main board", &board, printing).is_some() {
            played.push(printing.id);
        }
    }
    assert_eq!(reprints.len(), 239);
    // Every B4b reprint but Wallace's is legal on this board (`b4b_reprint_arms_test.rs`), so at
    // least those 80 went through their whole course here.
    for printing in &reprints {
        if printing.card.id.starts_with("B4b ") && printing.card.name != "Wallace" {
            assert!(
                played.contains(&printing.id),
                "{} {} should be legal on the Main board",
                printing.card.id,
                printing.card.name
            );
        }
    }
}

/// `board` after playing `id` from hand (the play must be legal there).
fn after_playing(board: &State, id: CardId) -> State {
    let mut state = board.clone();
    state.hands[0].push(get_card_by_enum(id));
    let play = play_of(&state, id).unwrap_or_else(|| panic!("{id:?} should be legal here"));
    let mut game = Game::from_state(state, init_random_players(), SEED);
    game.apply_action(&play);
    game.get_state_clone()
}

fn adopted(state: State) -> State {
    Game::from_state(state, init_random_players(), SEED).get_state_clone()
}

/// (b) `is_misty_trainer`, read where Game adopts a State. A staged Misty target (from A1 220
/// Misty) and a staged Luxury Coin choice (from B4 145 Order Pad, so no fixed Misty target) get
/// each printing written in as their source: the target survives adoption only for a Misty
/// printing, the coin choice only for any other but Sweet Honey (whose batch, like Misty's, needs
/// its fixed target since R8-07a), and a reprint's answers are its canonical printing's.
#[test]
fn adoption_keeps_a_pending_choice_alike_for_every_printing_and_its_canonical() {
    let misty_target = after_playing(&coin_board(false), CardId::A1220Misty);
    assert!(misty_target.pending_misty_target_choice.is_some());
    let coin_choice = after_playing(&coin_board(true), CardId::B4145OrderPad);
    assert!(coin_choice.pending_trainer_coin_choice.is_some());
    let kept = |source: &TrainerCard| -> (bool, bool) {
        let mut target_state = misty_target.clone();
        let pending = target_state.pending_misty_target_choice.as_mut().unwrap();
        pending.original_action = SimpleAction::Play {
            trainer_card: source.clone(),
        };
        pending.route = Some(MistySourceRoute::Direct {
            misty: source.clone(),
        });
        let mut coin_state = coin_choice.clone();
        let pending = coin_state.pending_trainer_coin_choice.as_mut().unwrap();
        pending.original_action = SimpleAction::Play {
            trainer_card: source.clone(),
        };
        pending.route = Some(TrainerCoinEffectRoute::Direct {
            trainer: source.clone(),
        });
        (
            adopted(target_state).pending_misty_target_choice.is_some(),
            adopted(coin_state).pending_trainer_coin_choice.is_some(),
        )
    };
    let all = printings();
    let answers: HashMap<CardId, (bool, bool)> =
        all.iter().map(|printing| (printing.id, kept(&printing.card))).collect();
    for printing in &all {
        let (id, name) = (&printing.card.id, &printing.card.name);
        let misty = name.as_str() == "Misty";
        let sweet_honey = name.as_str() == "Sweet Honey";
        assert_eq!(answers[&printing.id], (misty, !misty && !sweet_honey), "{id} {name}");
        assert_eq!(
            answers[&printing.id],
            answers[&printing.canonical],
            "{id} {name} v its canonical printing {:?}",
            printing.canonical
        );
    }
}

/// (b) `is_sweet_honey_trainer`, read where Game adopts a State. A Sweet Honey target phase (from
/// C1 119, Luxury Coin used: its route and its damaged-target frame) and a Luxury Coin choice with
/// Sweet Honey's fixed target (Luxury Coin ready, the Charmeleon chosen) get each printing written
/// in as their source: both survive adoption only for a Sweet Honey printing, and C1 152's answers
/// are C1 119's.
#[test]
fn adoption_keeps_sweet_honeys_target_phase_and_fixed_target_alike_for_both_printings() {
    let target_phase = after_playing(&coin_board(false), CardId::C1119SweetHoney);
    assert!(target_phase.pending_misty_target_choice.is_some());
    let mut game = Game::from_state(
        after_playing(&coin_board(true), CardId::C1119SweetHoney),
        init_random_players(),
        SEED,
    );
    let choice = game.get_state_clone().generate_possible_actions().1.remove(0);
    game.apply_action(&choice);
    let paused = game.get_state_clone();
    let pending = paused.pending_trainer_coin_choice.as_ref().unwrap();
    assert_eq!(pending.misty_target_in_play_idx, Some(0), "the Charmeleon, 30 damage");
    let kept = |source: &TrainerCard| -> (bool, bool) {
        let mut target_state = target_phase.clone();
        let pending = target_state.pending_misty_target_choice.as_mut().unwrap();
        pending.original_action = SimpleAction::Play {
            trainer_card: source.clone(),
        };
        pending.route = Some(MistySourceRoute::SweetHoney {
            sweet_honey: source.clone(),
        });
        let mut coin_state = paused.clone();
        let pending = coin_state.pending_trainer_coin_choice.as_mut().unwrap();
        pending.original_action = SimpleAction::Play {
            trainer_card: source.clone(),
        };
        pending.route = Some(TrainerCoinEffectRoute::Direct {
            trainer: source.clone(),
        });
        (
            adopted(target_state).pending_misty_target_choice.is_some(),
            adopted(coin_state).pending_trainer_coin_choice.is_some(),
        )
    };
    for printing in printings() {
        let (id, name) = (&printing.card.id, &printing.card.name);
        let sweet_honey = name.as_str() == "Sweet Honey";
        assert_eq!(kept(&printing.card), (sweet_honey, sweet_honey), "{id} {name}");
    }
}

/// (b) `is_misty_card` and `is_researcher_card` send a played Trainer to Misty's target choice or
/// to the Researcher's own sampler (a Researcher that missed it would reach its unreachable
/// forecast arm), and the Luxury Coin producer check sends a coin Trainer's batch to Luxury Coin's
/// keep-or-reroll choice. Every reprint plays as its canonical printing from the coin board, with
/// Luxury Coin used this turn and with it ready.
#[test]
fn every_reprint_takes_the_route_its_canonical_printing_takes() {
    let reprints = reprints();
    for luxury_coin_ready in [false, true] {
        let board = coin_board(luxury_coin_ready);
        let board_name = if luxury_coin_ready {
            "the coin board, Luxury Coin ready"
        } else {
            "the coin board, Luxury Coin used"
        };
        let mut routes: Vec<(String, Route)> = Vec::new();
        for printing in &reprints {
            if !is_implemented(get_implementation_status(printing.canonical)) {
                continue;
            }
            if let Some(route) = compare_on_board(board_name, &board, printing) {
                routes.push((printing.card.name.clone(), route));
            }
        }
        let routes_of = |name: &str| -> Vec<Route> {
            routes
                .iter()
                .filter(|(played, _)| played.as_str() == name)
                .map(|(_, route)| *route)
                .collect()
        };
        // Misty's one reprint stages its target on either route (before its batch on the coin one).
        assert_eq!(routes_of("Misty"), vec![Route::MistyTarget], "{board_name}");
        // So does Sweet Honey's (R8-07a), in the same slot: the Charmeleon's 30 damage makes it
        // legal.
        assert_eq!(routes_of("Sweet Honey"), vec![Route::MistyTarget], "{board_name}");
        assert_eq!(routes_of("Team Rocket's Researcher").len(), 1, "{board_name}");
        // The coin Trainers that `b4b_reprint_arms_test.rs` runs under Luxury Coin.
        let coin_route = if luxury_coin_ready { Route::LuxuryCoin } else { Route::Plain };
        for name in ["Lucky Ice Pop", "Electric Generator", "Order Pad", "Arven"] {
            let found = routes_of(name);
            assert!(!found.is_empty(), "{name} should be legal on {board_name}");
            assert!(
                found.iter().all(|route| *route == coin_route),
                "{name} on {board_name}: {found:?}"
            );
        }
        if !luxury_coin_ready {
            assert!(
                routes.iter().all(|(_, route)| *route != Route::LuxuryCoin),
                "Luxury Coin was used this turn"
            );
        }
    }
}

/// (b) `stadium_route` sends a Stadium's coins to Luxury Coin. Every Stadium reprint in play
/// (played by player 0, Luxury Coin ready) offers what its canonical printing offers, and using it
/// takes the same course. Mesagoza's two reprints take the Luxury Coin route, as
/// `b4b_reprint_arms_test.rs` (c) checks for them.
#[test]
fn every_stadium_reprint_in_play_takes_the_route_its_canonical_printing_takes() {
    let board = coin_board(true);
    let mut used: Vec<(String, Route)> = Vec::new();
    for printing in reprints() {
        if printing.card.trainer_card_type != TrainerType::Stadium {
            continue;
        }
        let twin_id = printing.card.id.clone();
        let base_id = get_card_by_enum(printing.canonical).get_id();
        let ctx = format!("{twin_id} {} v {base_id} in play under Luxury Coin", printing.card.name);
        let pair = [twin_id.clone(), base_id.clone()];
        let in_play = |id: CardId| {
            let mut state = without_pair(&board, &pair);
            state.active_stadium = Some(get_card_by_enum(id));
            state.active_stadium_owner = Some(0);
            state
        };
        let (base, twin) = (in_play(printing.canonical), in_play(printing.id));
        let as_base = |text: String| text.replace(twin_id.as_str(), base_id.as_str());
        let twin_labels = labels(&twin).into_iter().map(as_base).collect::<Vec<_>>();
        assert_eq!(twin_labels, labels(&base), "{ctx}: legal actions");
        let Some(base_use) = use_of_stadium(&base) else {
            continue;
        };
        let twin_use = use_of_stadium(&twin).expect("the labels match");
        let route = assert_same_course(
            &ctx,
            (base, base_use),
            (twin, twin_use),
            (base_id.as_str(), twin_id.as_str()),
        );
        used.push((printing.card.name.clone(), route));
    }
    let mesagoza = used
        .iter()
        .filter(|(name, _)| name.as_str() == "Mesagoza")
        .map(|(_, route)| *route)
        .collect::<Vec<_>>();
    assert_eq!(mesagoza, vec![Route::LuxuryCoin; 2]);
}
