//! B4b's 82 Trainer reprints (40 names) against their base printings. A base printing is a Trainer
//! of another set with the same name AND the same effect text. In this fork Trainer logic is keyed
//! by CardId, so for the Oct 24 release every twin was added wherever its base is named by id
//! (`rl/results/dual_type_seam_2026-10-23/tools/add_reprint_arms.py`, plus `is_ice_pop` by hand);
//! upstream's #395 (Trainer logic keyed by effect text) replaces those arms after the release.
//!
//! - The table below is every B4b Trainer, each with a base of the same name and text.
//! - (a) card_status's own function (`card_validation::get_implementation_status`) gives every twin
//!   the status of every one of its bases.
//! - (b) From one prepared board where the base is legal, the twin in the same hand slot has the
//!   same legal actions (labels, id swapped) and, played with the same seed, leaves the same state
//!   (ids swapped), through every choice the play opens (the first offered choice each time). The
//!   coin Trainers run a second time under Luxury Coin, where an unregistered coin Trainer panics.
//!   Supporters and Items are the required part; the Tools and Stadiums (keyed by effect text
//!   already) run the same check in their own test.
//! - (c) The Mesagoza twins take the Luxury Coin Stadium route as their base does.

use std::collections::BTreeSet;

use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    card_validation::{get_implementation_status, ImplementationStatus},
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard, TrainerCard, TrainerType},
    test_support::{get_initialized_game, init_random_players},
    Game, State,
};
use strum::IntoEnumIterator;

const SEED: u64 = 7;
/// Choices a single play may open before the course must be over (the deepest here is two).
const MAX_CHOICES: usize = 6;

/// (twin, base): every B4b Trainer, in id order, with its lowest-id base printing.
const REPRINTS: [(CardId, CardId); 82] = [
    (CardId::B4b198LuckyIcePop, CardId::B2145LuckyIcePop),
    (CardId::B4b199ElectricGenerator, CardId::B2a086ElectricGenerator),
    (CardId::B4b200OrderPad, CardId::B4145OrderPad),
    (CardId::B4b201QuickGrowExtract, CardId::B1a067QuickGrowExtract),
    (CardId::B4b202FieldBlower, CardId::B3147FieldBlower),
    (CardId::B4b203FlamePatch, CardId::B1217FlamePatch),
    (CardId::B4b204DeceptiveNeedle, CardId::B4148DeceptiveNeedle),
    (CardId::B4b205LuckyEgg, CardId::B3148LuckyEgg),
    (CardId::B4b206SmallBalloon, CardId::B3b064SmallBalloon),
    (CardId::B4b207AncientBoosterEnergyCapsule, CardId::B3a069AncientBoosterEnergyCapsule),
    (CardId::B4b208FutureBoosterEnergyCapsule, CardId::B3a070FutureBoosterEnergyCapsule),
    (CardId::B4b209ProtectivePoncho, CardId::B2147ProtectivePoncho),
    (CardId::B4b210MetalCoreBarrier, CardId::B2148MetalCoreBarrier),
    (CardId::B4b211ElegantCape, CardId::B3b065ElegantCape),
    (CardId::B4b212Iris, CardId::B2b067Iris),
    (CardId::B4b213Juliana, CardId::B3a071Juliana),
    (CardId::B4b214Diantha, CardId::B2149Diantha),
    (CardId::B4b215Calem, CardId::B2b068Calem),
    (CardId::B4b216PuppyLovingGirl, CardId::B3b067PuppyLovingGirl),
    (CardId::B4b217Korrina, CardId::B3149Korrina),
    (CardId::B4b218Clemont, CardId::B1a068Clemont),
    (CardId::B4b219Serena, CardId::B1a069Serena),
    (CardId::B4b220May, CardId::B1223May),
    (CardId::B4b221Skyla, CardId::B4152Skyla),
    (CardId::B4b222Arven, CardId::B2a091Arven),
    (CardId::B4b223Wallace, CardId::B3b068Wallace),
    (CardId::B4b224Wally, CardId::B4153Wally),
    (CardId::B4b225Copycat, CardId::B1225Copycat),
    (CardId::B4b226Lisia, CardId::B1226Lisia),
    (CardId::B4b227FragrantForest, CardId::B3153FragrantForest),
    (CardId::B4b228ArenaofAntiquity, CardId::B3154ArenaofAntiquity),
    (CardId::B4b229SoothingShore, CardId::B4154SoothingShore),
    (CardId::B4b230BoundedField, CardId::B3155BoundedField),
    (CardId::B4b231Mesagoza, CardId::B2a093Mesagoza),
    (CardId::B4b232TrainingArea, CardId::B2153TrainingArea),
    (CardId::B4b233RainbowCave, CardId::B4155RainbowCave),
    (CardId::B4b234HikingTrail, CardId::B2b069HikingTrail),
    (CardId::B4b235StartingPlains, CardId::B2154StartingPlains),
    (CardId::B4b236PeculiarPlaza, CardId::B2155PeculiarPlaza),
    (CardId::B4b364LuckyIcePop, CardId::B2145LuckyIcePop),
    (CardId::B4b365ElectricGenerator, CardId::B2a086ElectricGenerator),
    (CardId::B4b366OrderPad, CardId::B4145OrderPad),
    (CardId::B4b367QuickGrowExtract, CardId::B1a067QuickGrowExtract),
    (CardId::B4b368FieldBlower, CardId::B3147FieldBlower),
    (CardId::B4b369FlamePatch, CardId::B1217FlamePatch),
    (CardId::B4b370DeceptiveNeedle, CardId::B4148DeceptiveNeedle),
    (CardId::B4b371LuckyEgg, CardId::B3148LuckyEgg),
    (CardId::B4b372SmallBalloon, CardId::B3b064SmallBalloon),
    (CardId::B4b373AncientBoosterEnergyCapsule, CardId::B3a069AncientBoosterEnergyCapsule),
    (CardId::B4b374FutureBoosterEnergyCapsule, CardId::B3a070FutureBoosterEnergyCapsule),
    (CardId::B4b375ProtectivePoncho, CardId::B2147ProtectivePoncho),
    (CardId::B4b376MetalCoreBarrier, CardId::B2148MetalCoreBarrier),
    (CardId::B4b377ElegantCape, CardId::B3b065ElegantCape),
    (CardId::B4b378Iris, CardId::B2b067Iris),
    (CardId::B4b379Juliana, CardId::B3a071Juliana),
    (CardId::B4b380Diantha, CardId::B2149Diantha),
    (CardId::B4b381Calem, CardId::B2b068Calem),
    (CardId::B4b382PuppyLovingGirl, CardId::B3b067PuppyLovingGirl),
    (CardId::B4b383Korrina, CardId::B3149Korrina),
    (CardId::B4b384Clemont, CardId::B1a068Clemont),
    (CardId::B4b385Serena, CardId::B1a069Serena),
    (CardId::B4b386May, CardId::B1223May),
    (CardId::B4b387Skyla, CardId::B4152Skyla),
    (CardId::B4b388Arven, CardId::B2a091Arven),
    (CardId::B4b389Wallace, CardId::B3b068Wallace),
    (CardId::B4b390Wally, CardId::B4153Wally),
    (CardId::B4b391Copycat, CardId::B1225Copycat),
    (CardId::B4b392Lisia, CardId::B1226Lisia),
    (CardId::B4b393FragrantForest, CardId::B3153FragrantForest),
    (CardId::B4b394ArenaofAntiquity, CardId::B3154ArenaofAntiquity),
    (CardId::B4b395SoothingShore, CardId::B4154SoothingShore),
    (CardId::B4b396BoundedField, CardId::B3155BoundedField),
    (CardId::B4b397Mesagoza, CardId::B2a093Mesagoza),
    (CardId::B4b398TrainingArea, CardId::B2153TrainingArea),
    (CardId::B4b399RainbowCave, CardId::B4155RainbowCave),
    (CardId::B4b400HikingTrail, CardId::B2b069HikingTrail),
    (CardId::B4b401StartingPlains, CardId::B2154StartingPlains),
    (CardId::B4b402PeculiarPlaza, CardId::B2155PeculiarPlaza),
    (CardId::B4b421Iris, CardId::B2b067Iris),
    (CardId::B4b422Elesa, CardId::B3b066Elesa),
    (CardId::B4b423Arven, CardId::B2a091Arven),
    (CardId::B4b424Copycat, CardId::B1225Copycat),
];

fn set_of(card_id: &str) -> &str {
    card_id.split(' ').next().unwrap_or("")
}

fn trainer_catalog() -> Vec<(CardId, TrainerCard)> {
    CardId::iter()
        .filter_map(|id| match get_card_by_enum(id) {
            Card::Trainer(trainer) => Some((id, trainer)),
            _ => None,
        })
        .collect()
}

/// Every printing of another set with the twin's name and effect text.
fn bases_of(catalog: &[(CardId, TrainerCard)], twin: &TrainerCard) -> Vec<CardId> {
    catalog
        .iter()
        .filter(|(_, t)| set_of(&t.id) != "B4b" && t.name == twin.name && t.effect == twin.effect)
        .map(|(id, _)| *id)
        .collect()
}

#[test]
fn the_table_is_every_b4b_trainer_and_a_base_of_the_same_name_and_text() {
    let catalog = trainer_catalog();
    let mut in_data: Vec<String> = catalog
        .iter()
        .filter(|(_, t)| set_of(&t.id) == "B4b")
        .map(|(_, t)| t.id.clone())
        .collect();
    let mut in_table: Vec<String> = REPRINTS
        .iter()
        .map(|(twin, _)| get_card_by_enum(*twin).get_id())
        .collect();
    in_data.sort();
    in_table.sort();
    assert_eq!(in_table, in_data, "the table lists every B4b Trainer exactly once");
    assert_eq!(in_table.len(), 82);
    let names: BTreeSet<String> = REPRINTS
        .iter()
        .map(|(twin, _)| get_card_by_enum(*twin).get_name())
        .collect();
    assert_eq!(names.len(), 40);
    for (twin, base) in REPRINTS {
        let (t, b) = (get_card_by_enum(twin).as_trainer(), get_card_by_enum(base).as_trainer());
        assert_ne!(set_of(&b.id), "B4b", "{}: the base must be another set's printing", t.id);
        assert_eq!(t.name, b.name, "{} v {}", t.id, b.id);
        assert_eq!(t.effect, b.effect, "{} v {}: the same effect text", t.id, b.id);
        assert_eq!(t.trainer_card_type, b.trainer_card_type, "{} v {}", t.id, b.id);
        assert!(bases_of(&catalog, &t).contains(&base), "{} v {}", t.id, b.id);
    }
}

/// (a) The status card_status reports: the same for the twin as for each of its bases.
#[test]
fn every_twin_has_the_card_status_of_its_bases() {
    let catalog = trainer_catalog();
    for (twin, _) in REPRINTS {
        let card = get_card_by_enum(twin).as_trainer();
        let status = get_implementation_status(twin);
        assert!(
            matches!(status, ImplementationStatus::Complete | ImplementationStatus::RulesUnverified),
            "{} {}: {status:?}",
            card.id,
            card.name
        );
        let bases = bases_of(&catalog, &card);
        assert!(!bases.is_empty(), "{} {} has a base printing", card.id, card.name);
        for base in bases {
            assert_eq!(
                status,
                get_implementation_status(base),
                "{} {} v its base {base:?}",
                card.id,
                card.name
            );
        }
    }
}

/// The prepared boards. Player 0 to act on turn 3, a nonempty deck (from the initialized game),
/// a Charmander in hand slot 0 and the Trainer under test in slot 1; the opponent has a Bulbasaur.
#[derive(Clone, Copy, Debug, PartialEq)]
enum Board {
    /// Active: Charmeleon (Stage 1 [R], 30 damage). Bench: Pikachu ([L], holding Giant Cape),
    /// Venusaur (Stage 2 [G], not played this turn), Abra ([P], 20 damage, two [P] Energy).
    /// A [R] Energy in the discard pile. Every Supporter and Item twin except Wallace is legal.
    Main,
    /// As Main with a 30-HP [W] Magikarp in place of Abra: Wallace's target.
    Water,
    /// As Main with Gholdengo (Luxury Coin) in place of Abra: the Trainer coin route.
    LuxuryCoin,
}

fn boards_for(name: &str) -> Vec<Board> {
    match name {
        "Wallace" => vec![Board::Water],
        "Lucky Ice Pop" | "Electric Generator" | "Order Pad" | "Arven" => {
            vec![Board::Main, Board::LuxuryCoin]
        }
        _ => vec![Board::Main],
    }
}

fn board_state(board: Board) -> State {
    let mut state = get_initialized_game(SEED).get_state_clone();
    let third = match board {
        Board::Main => PlayedCard::from_id(CardId::A1115Abra)
            .with_energy(vec![EnergyType::Psychic, EnergyType::Psychic])
            .with_damage(20),
        Board::Water => PlayedCard::from_id(CardId::A1077Magikarp),
        Board::LuxuryCoin => PlayedCard::from_id(CardId::B4a051Gholdengo),
    };
    state.set_board(
        vec![
            PlayedCard::from_id(CardId::A1034Charmeleon).with_damage(30),
            PlayedCard::from_id(CardId::A1094Pikachu)
                .with_tool(get_card_by_enum(CardId::A2147GiantCape)),
            PlayedCard::from_id(CardId::A1003Venusaur),
            third,
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
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

fn label(action: &Action) -> String {
    format!("{}|{}|{}", action.actor, action.is_stack, action.action)
}

fn labels(state: &State) -> Vec<String> {
    state.generate_possible_actions().1.iter().map(label).collect()
}

fn play_of(state: &State, id: CardId) -> Action {
    let wanted = get_card_by_enum(id).get_id();
    state
        .generate_possible_actions()
        .1
        .into_iter()
        .find(|action| {
            matches!(&action.action, SimpleAction::Play { trainer_card } if trainer_card.id == wanted)
        })
        .unwrap_or_else(|| panic!("{wanted} should be legal to play on this board"))
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
/// the twin's id written as the base's, with the base's at every step.
fn assert_same_course(
    ctx: &str,
    (base, base_first): (State, Action),
    (twin, twin_first): (State, Action),
    (base_id, twin_id): (&str, &str),
    luxury_coin: bool,
) {
    let as_base = |text: String| text.replace(twin_id, base_id);
    let twin_labels = |state: &State| labels(state).into_iter().map(as_base).collect::<Vec<_>>();
    assert_eq!(twin_labels(&twin), labels(&base), "{ctx}: legal actions before the play");
    assert_eq!(as_base(label(&twin_first)), label(&base_first), "{ctx}: the play itself");

    let mut base_game = Game::from_state(base, init_random_players(), SEED);
    let mut twin_game = Game::from_state(twin, init_random_players(), SEED);
    base_game.apply_action(&base_first);
    twin_game.apply_action(&twin_first);
    if luxury_coin {
        assert!(
            base_game.get_state_clone().pending_trainer_coin_choice.is_some(),
            "{ctx}: the base takes the Luxury Coin route"
        );
    }
    for step in 1..=MAX_CHOICES {
        let (b, t) = (base_game.get_state_clone(), twin_game.get_state_clone());
        assert_same_text(
            &format!("{b:?}"),
            &as_base(format!("{t:?}")),
            &format!("{ctx}: state after step {step}"),
        );
        assert_eq!(twin_labels(&t), labels(&b), "{ctx}: legal actions after step {step}");
        if b.move_generation_stack.is_empty() {
            return;
        }
        let base_actions = b.generate_possible_actions().1;
        let Some(base_next) = base_actions.first() else {
            return;
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

fn assert_twin_plays_as_base(twin: CardId, base: CardId, board: Board) {
    let (twin_id, base_id) = (get_card_by_enum(twin).get_id(), get_card_by_enum(base).get_id());
    let ctx = format!("{twin_id} {} v {base_id} on {board:?}", get_card_by_enum(twin).get_name());
    let template = board_state(board);
    let holding = |id: CardId| {
        let mut state = template.clone();
        state.hands[0].push(get_card_by_enum(id));
        state
    };
    let (base_state, twin_state) = (holding(base), holding(twin));
    let base_play = play_of(&base_state, base);
    let twin_play = play_of(&twin_state, twin);
    assert_same_course(
        &ctx,
        (base_state, base_play),
        (twin_state, twin_play),
        (base_id.as_str(), twin_id.as_str()),
        board == Board::LuxuryCoin,
    );
}

/// (b) Every Supporter and Item twin (each has an arm in move_generation_trainer.rs and in
/// apply_trainer_action.rs through its base).
#[test]
fn supporter_and_item_twins_play_as_their_bases() {
    let (mut rows, mut runs) = (0, 0);
    for (twin, base) in REPRINTS {
        let card = get_card_by_enum(twin).as_trainer();
        if !matches!(card.trainer_card_type, TrainerType::Supporter | TrainerType::Item) {
            continue;
        }
        rows += 1;
        for board in boards_for(&card.name) {
            assert_twin_plays_as_base(twin, base, board);
            runs += 1;
        }
    }
    // 46 twins; the 9 coin twins (Lucky Ice Pop 2, Electric Generator 2, Order Pad 2, Arven 3) twice.
    assert_eq!((rows, runs), (46, 55));
}

/// The same check for the Tool and Stadium twins: played, then the Tool attached to the first
/// offered Pokémon, or the Stadium put in play.
#[test]
fn tool_and_stadium_twins_play_as_their_bases() {
    let mut rows = 0;
    for (twin, base) in REPRINTS {
        let card = get_card_by_enum(twin).as_trainer();
        if !matches!(card.trainer_card_type, TrainerType::Tool | TrainerType::Stadium) {
            continue;
        }
        rows += 1;
        assert_twin_plays_as_base(twin, base, Board::Main);
    }
    assert_eq!(rows, 36);
}

/// (c) Using a Mesagoza twin with Luxury Coin in play takes the Stadium coin route its base takes
/// (`trainer_coin_plan::stadium_route`); a Stadium with coins and no route panics there.
#[test]
fn mesagoza_twins_take_the_luxury_coin_route_as_their_base_does() {
    let base = CardId::B2a093Mesagoza;
    for twin in [CardId::B4b231Mesagoza, CardId::B4b397Mesagoza] {
        let (twin_id, base_id) = (get_card_by_enum(twin).get_id(), get_card_by_enum(base).get_id());
        let with_stadium = |id: CardId| {
            let mut state = board_state(Board::LuxuryCoin);
            state.active_stadium = Some(get_card_by_enum(id));
            state.active_stadium_owner = Some(0);
            state
        };
        let use_stadium = |state: &State| {
            state
                .generate_possible_actions()
                .1
                .into_iter()
                .find(|action| matches!(action.action, SimpleAction::UseStadium))
                .expect("Mesagoza can be used")
        };
        let (base_state, twin_state) = (with_stadium(base), with_stadium(twin));
        let (base_use, twin_use) = (use_stadium(&base_state), use_stadium(&twin_state));
        assert_same_course(
            &format!("{twin_id} Mesagoza v {base_id} under Luxury Coin"),
            (base_state, base_use),
            (twin_state, twin_use),
            (base_id.as_str(), twin_id.as_str()),
            true,
        );
    }
}
