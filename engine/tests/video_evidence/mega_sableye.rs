//! Integrated regressions for the observed Mega Sableye ex Cursed Jewel sequence.
//!
//! The direct-KO case binds the recorded public transition. The delayed-counter and prevention
//! cases are constructed mechanics controls, and all three cases exercise the three mechanically
//! identical prints because the recording does not resolve the two-star collector number.
//!
//! Source recording: `20260907_224312000_iOS.MP4`, SHA-256
//! `6f5bd2f13e548f8b5856132f7faab690641fd9a6f10f45d173802e09c9708593`.
//! Published review: `Boss Folder/video-mechanics-flygon-sableye-2026-09-07/sableye-video/`
//! `{EVIDENCE.md,SOURCE_BINDINGS.md}`.

use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    effects::CardEffect,
    models::{EnergyType, PlayedCard},
    players::{EndTurnPlayer, Player},
    state::GameOutcome,
    Game, State,
};

const SEED: u64 = 715_041;
const SABLEYE_PRINTS: [CardId; 3] = [
    CardId::B3b041MegaSableyeEx,
    CardId::B3b081MegaSableyeEx,
    CardId::B3b088MegaSableyeEx,
];

fn game_with_board(
    player_0: Vec<PlayedCard>,
    player_1: Vec<PlayedCard>,
    current_player: usize,
    points: [u8; 2],
) -> Game<'static> {
    let mut state = State::default();
    state.current_player = current_player;
    state.turn_count = 10;
    state.points = points;
    state.hands = [vec![], vec![]];
    state.energy_zone[0].current = None;
    state.energy_zone[0].next = None;
    state.energy_zone[1].current = None;
    state.energy_zone[1].next = None;
    state.set_board(player_0, player_1);

    let players: Vec<Box<dyn Player>> = vec![
        Box::new(EndTurnPlayer {
            deck: state.decks[0].clone(),
        }),
        Box::new(EndTurnPlayer {
            deck: state.decks[1].clone(),
        }),
    ];
    Game::from_state(state, players, SEED)
}

fn action_matching(
    game: &Game<'_>,
    label: &str,
    predicate: impl Fn(&SimpleAction) -> bool,
) -> Action {
    let (_, choices) = game.get_state_clone().generate_possible_actions();
    choices
        .into_iter()
        .find(|choice| predicate(&choice.action))
        .unwrap_or_else(|| panic!("missing legal action: {label}"))
}

fn apply_attack(game: &mut Game<'_>, title: &str) {
    let action = action_matching(game, title, |choice| {
        matches!(choice, SimpleAction::Attack(attack) if attack.title == title)
    });
    game.apply_action(&action);
}

fn end_turn_and_resolve_forced_actions(game: &mut Game<'_>, actor: usize) {
    let end = action_matching(game, "end turn", |choice| {
        matches!(choice, SimpleAction::EndTurn)
    });
    assert_eq!(end.actor, actor);
    game.apply_action(&end);

    loop {
        let (_, choices) = game.get_state_clone().generate_possible_actions();
        if choices.len() != 1 || !choices[0].is_stack {
            break;
        }
        let forced = choices[0].clone();
        game.apply_action(&forced);
    }
}

fn discard_contains(state: &State, player: usize, id: CardId) -> bool {
    state.discard_piles[player]
        .iter()
        .any(|card| card.get_card_id() == id)
}

fn payable_sableye(id: CardId) -> PlayedCard {
    PlayedCard::from_id(id).with_energy(vec![EnergyType::Darkness, EnergyType::Darkness])
}

fn assert_counterattack_armed(state: &State, player: usize) {
    // PlayedCard::get_active_effects is crate-private in eval15. State's public serialized
    // representation exposes the same stored `(CardEffect, duration)` list to an external
    // harness without changing the engine API.
    let serialized = serde_json::to_value(state).expect("state should serialize");
    let effects = serialized["in_play_pokemon"][player][0]["effects"]
        .as_array()
        .expect("active effects should be an array");
    assert!(
        effects
            .iter()
            .any(|entry| entry == &serde_json::json!([{"Counterattack": {"amount": 40}}, 1])),
        "Cursed Jewel should immediately store Counterattack {{ amount: 40 }} for duration 1: {effects:?}"
    );
}

fn video_bound_direct_ko(id: CardId) {
    // Observed public inputs: opponent turn 10; points 1-2; Gabite at 60/80 with no Bench;
    // full-HP Mega Sableye ex; Rainbow Cave in play. The two Darkness Energy are a
    // constructed payable assignment because the video does not resolve both attached types.
    let gabite = PlayedCard::from_id(CardId::B4a053Gabite)
        .with_energy(vec![EnergyType::Water, EnergyType::Fighting])
        .with_remaining_hp(60);
    let mut game = game_with_board(vec![gabite], vec![payable_sableye(id)], 1, [1, 2]);
    {
        let mut state = game.get_state_clone();
        state.active_stadium = Some(get_card_by_enum(CardId::B4155RainbowCave));
        // Stadium ownership is not needed by this symmetric Energy-Zone effect and was not
        // established by the focused evidence.
        state.active_stadium_owner = None;
        game.set_state(state);
    }

    apply_attack(&mut game, "Cursed Jewel");
    let settled = game.get_state_clone();
    assert_counterattack_armed(&settled, 1);
    assert!(settled.in_play_pokemon[0][0].is_none());
    assert!(settled.enumerate_bench_pokemon(0).next().is_none());
    assert_eq!(settled.points, [1, 3]);
    assert_eq!(settled.winner, Some(GameOutcome::Win(1)));
    assert_eq!(settled.get_active(1).get_remaining_hp(), 170);
    assert!(discard_contains(&settled, 0, CardId::B4a053Gabite));
    assert!(settled.move_generation_stack.is_empty());

    println!(
        "VIDEO_DIRECT id={id:?} damage=80 gabite_hp=60_to_0 points=1-2_to_1-3 winner=1 sableye_hp=170 counter_damage_now=0"
    );
}

fn delayed_counter_state(id: CardId, prevent_incoming_damage: bool) -> State {
    // Synthetic neutral target: Starmie ex avoids Mewtwo ex's Darkness Weakness, so Cursed
    // Jewel's base 80 takes an explicit 120 HP to 40 before the delayed counter is tested.
    let starmie = PlayedCard::from_id(CardId::A1076StarmieEx)
        .with_energy(vec![EnergyType::Water, EnergyType::Water])
        .with_remaining_hp(120);
    let mut sableye = payable_sableye(id);
    if prevent_incoming_damage {
        // Constructed precondition solely for the zero-applied-damage control. Duration 1
        // leaves the shield active during the opponent's immediately following turn.
        sableye.add_effect(CardEffect::PreventAllDamageAndEffects, 1);
    }
    let mut game = game_with_board(vec![starmie], vec![sableye], 1, [0, 1]);

    apply_attack(&mut game, "Cursed Jewel");
    let after_cursed_jewel = game.get_state_clone();
    assert_counterattack_armed(&after_cursed_jewel, 1);
    assert_eq!(after_cursed_jewel.get_active(0).get_remaining_hp(), 40);
    assert_eq!(after_cursed_jewel.get_active(1).get_remaining_hp(), 170);
    assert_eq!(after_cursed_jewel.points, [0, 1]);

    end_turn_and_resolve_forced_actions(&mut game, 1);
    assert_eq!(game.get_state_clone().current_player, 0);
    apply_attack(&mut game, "Hydro Splash");
    game.get_state_clone()
}

fn synthetic_delayed_counter_terminal(id: CardId) {
    let settled = delayed_counter_state(id, false);
    assert_eq!(settled.get_active(1).get_remaining_hp(), 80);
    assert!(settled.in_play_pokemon[0][0].is_none());
    assert!(discard_contains(&settled, 0, CardId::A1076StarmieEx));
    assert_eq!(settled.points, [0, 3]);
    assert_eq!(settled.winner, Some(GameOutcome::Win(1)));
    assert!(settled.move_generation_stack.is_empty());

    println!(
        "SYNTHETIC_COUNTER id={id:?} cursed_jewel=80 starmie_hp=120_to_40 hydro_splash=90 sableye_hp=170_to_80 counter=40 starmie_ko=true points=0-1_to_0-3 winner=1"
    );
}

fn prevented_damage_does_not_trigger_counter(id: CardId) {
    let settled = delayed_counter_state(id, true);
    assert_eq!(settled.get_active(1).get_remaining_hp(), 170);
    assert_eq!(settled.get_active(0).get_remaining_hp(), 40);
    assert_eq!(settled.points, [0, 1]);
    assert_eq!(settled.winner, None);

    println!(
        "PREVENTION_CONTROL id={id:?} incoming_hydro_splash_applied=0 counter_damage=0 sableye_hp=170 starmie_hp=40 points=0-1 winner=none"
    );
}

#[test]
fn video_bound_direct_ko_for_all_mechanically_identical_prints() {
    for id in SABLEYE_PRINTS {
        video_bound_direct_ko(id);
    }
}

#[test]
fn synthetic_delayed_counter_terminal_for_all_mechanically_identical_prints() {
    for id in SABLEYE_PRINTS {
        synthetic_delayed_counter_terminal(id);
    }
}

#[test]
fn prevented_damage_does_not_trigger_counter_for_all_mechanically_identical_prints() {
    for id in SABLEYE_PRINTS {
        prevented_damage_does_not_trigger_counter(id);
    }
}
