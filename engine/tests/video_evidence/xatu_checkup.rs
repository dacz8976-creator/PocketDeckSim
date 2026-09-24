//! Video-grounded Xatu tactical search and physical controls; partial constructed states.
//!
//! Predeclared tactical objective: maximize an immediate, rules-determined knockout before the
//! opponent can act. A Poisoned 190-HP Mega Lucario ex is knocked out after a successful Life
//! Drain sets it to 10 HP and the forced EndTurn performs Pokemon Checkup. With Will, that line is
//! certain. Extra Energy and delayed setup are worth only a one-point tiebreak in the first probe.
//!
//! Recording evidence: Luckycad 03:30-03:47 (Will, Life Drain, Poison KO for three points)
//! and 15:16-15:28 (Life Drain does not trigger Indeedee ex's Poison Barb).
//! The fixture adds explicit Bench fillers and clears hidden zones; it is not a full replay.

use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard, StatusCondition, TrainerCard},
    observation::{canonical_actions, PlayerObservation, RevealedKnowledge},
    players::{ExpectiMiniMaxPlayer, Player, ValueFunction},
    test_support::{attack_action, get_initialized_game, get_initialized_game_with_board},
    Deck, State,
};
use rand::{rngs::StdRng, SeedableRng};

fn will() -> TrainerCard {
    match get_card_by_enum(CardId::A4156Will) {
        Card::Trainer(card) => card,
        other => panic!("expected Will Trainer, got {other:?}"),
    }
}

fn play_will() -> Action {
    Action {
        actor: 0,
        action: SimpleAction::Play { trainer_card: will() },
        is_stack: false,
    }
}

fn end_turn() -> Action {
    Action {
        actor: 0,
        action: SimpleAction::EndTurn,
        is_stack: false,
    }
}

fn life_drain() -> Action {
    Action {
        actor: 0,
        action: attack_action(CardId::A4082Xatu, 0),
        is_stack: false,
    }
}

fn is_life_drain(action: &Action) -> bool {
    matches!(&action.action, SimpleAction::Attack(attack) if attack.title == "Life Drain")
}

fn is_will(action: &Action) -> bool {
    matches!(&action.action, SimpleAction::Play { trainer_card } if trainer_card.name == "Will")
}

fn action_label(action: &Action) -> String {
    match &action.action {
        SimpleAction::Attack(attack) => format!("Attack({})", attack.title),
        SimpleAction::Play { trainer_card } => format!("Play({})", trainer_card.name),
        SimpleAction::Attach { attachments, is_turn_energy: true } => {
            format!("Attach({attachments:?})")
        }
        other => format!("{other:?}"),
    }
}

fn xatu_vs_poisoned_lucario(with_will: bool, attach_available: bool) -> State {
    let mut game = get_initialized_game_with_board(
        47,
        0,
        3,
        vec![
            PlayedCard::from_id(CardId::A4082Xatu)
                .with_energy(vec![EnergyType::Psychic, EnergyType::Psychic]),
            PlayedCard::from_id(CardId::A4081Natu),
        ],
        vec![
            PlayedCard::from_id(CardId::B3081MegaLucarioEx)
                .with_status_condition(StatusCondition::Poisoned),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );
    let mut state = game.get_state_clone();
    state.current_player = 0;
    state.turn_count = 3;
    state.points = [0, 0];
    state.hands = [Vec::new(), Vec::new()];
    state.decks[0].cards.clear();
    state.decks[1].cards.clear();
    state.energy_zone[0].current = attach_available.then_some(EnergyType::Psychic);
    if with_will {
        state.hands[0].push(Card::Trainer(will()));
    }
    game.set_state(state);
    game.get_state_clone()
}

fn terminal_value(state: &State, myself: usize) -> f64 {
    match state.winner {
        Some(deckgym::state::GameOutcome::Win(player)) if player == myself => 1_000.0,
        Some(deckgym::state::GameOutcome::Win(_)) => -1_000.0,
        _ => 0.0,
    }
}

fn terminal_then_overcharge_tiebreak(state: &State, myself: usize) -> f64 {
    let terminal = terminal_value(state, myself);
    if terminal != 0.0 {
        return terminal;
    }
    usize::from(state.get_active(myself).attached_energy.len() >= 3) as f64
}

fn choose(state: &State, depth: usize, value_function: ValueFunction, seed: u64) -> Action {
    let actor = state.current_player;
    let (_, mut actions) = state.generate_possible_actions();
    canonical_actions(&mut actions);
    let observation = PlayerObservation::from_state(state, actor, &RevealedKnowledge::default());
    assert_eq!(observation.visible_state().generate_possible_actions().1.len(), actions.len());
    let deck: Deck = state.decks[actor].clone();
    let mut bot = ExpectiMiniMaxPlayer {
        deck,
        max_depth: depth,
        write_debug_trees: false,
        value_function,
        opponent_ply: 0,
        consistent_horizon: false,
        soft_opponent: false,
    };
    let choice = bot.decision_fn(
        &mut StdRng::seed_from_u64(seed),
        &observation,
        &actions,
    );
    assert!(actions.contains(&choice));
    choice
}

#[test]
fn shallow_xatu_search_prices_the_committed_poison_checkup() {
    let state = xatu_vs_poisoned_lucario(false, true);
    let (_, actions) = state.generate_possible_actions();
    assert!(actions.iter().any(is_life_drain));
    assert!(actions
        .iter()
        .any(|action| matches!(&action.action, SimpleAction::Attach { .. })));

    // At depth one only Attack completes the immediate KO chance. Deeper searches may
    // legitimately attach first if they still complete the same attack in this turn.
    for depth in [1] {
        let choice = choose(
            &state,
            depth,
            Box::new(terminal_then_overcharge_tiebreak),
            91,
        );
        assert!(is_life_drain(&choice), "{}", action_label(&choice));
    }
}

#[test]
fn will_then_life_drain_needs_two_ordinary_choices() {
    let state = xatu_vs_poisoned_lucario(true, false);
    let (_, actions) = state.generate_possible_actions();
    assert!(actions.iter().any(is_life_drain));
    assert!(actions.iter().any(is_will));

    // Correct immediate-KO objective: Will. With forced EndTurn priced as part of the attack,
    // depth 2 covers Will -> Life Drain -> mandatory Checkup. Requiring depth 3 identifies the
    // extra ordinary-ply charge caused by stopping at the attack's 10-HP state.
    for depth in [2, 3] {
        let choice = choose(&state, depth, Box::new(terminal_value), 97);
        assert!(is_will(&choice), "{}", action_label(&choice));
    }
}

fn resolve_will_life_drain(mut state: State) -> State {
    let mut game = get_initialized_game(17);
    state.current_player = 0;
    state.turn_count = 3;
    state.hands[0] = vec![Card::Trainer(will())];
    state.energy_zone[0].current = None;
    game.set_state(state);
    game.apply_action(&play_will());
    game.apply_action(&life_drain());
    game.apply_action(&end_turn());
    game.get_state_clone()
}

fn mechanics_base(defender: PlayedCard) -> State {
    let mut game = get_initialized_game_with_board(
        17,
        0,
        3,
        vec![PlayedCard::from_id(CardId::A4082Xatu)
            .with_energy(vec![EnergyType::Psychic, EnergyType::Psychic])],
        vec![defender, PlayedCard::from_id(CardId::A1033Charmander)],
    );
    let mut state = game.get_state_clone();
    state.points = [0, 0];
    state.decks[0].cards.clear();
    state.decks[1].cards.clear();
    game.set_state(state);
    game.get_state_clone()
}

#[test]
fn mechanical_controls_keep_hp_setting_separate_from_damage() {
    let poisoned = mechanics_base(
        PlayedCard::from_id(CardId::B3081MegaLucarioEx)
            .with_status_condition(StatusCondition::Poisoned),
    );
    let core = resolve_will_life_drain(poisoned);
    assert_eq!(core.points[0], 3);
    assert_eq!(core.winner, Some(deckgym::state::GameOutcome::Win(0)));

    let clean = mechanics_base(PlayedCard::from_id(CardId::B3081MegaLucarioEx));
    let no_poison = resolve_will_life_drain(clean);
    assert_eq!(no_poison.get_active(1).get_remaining_hp(), 10);
    assert_eq!(no_poison.points[0], 0);
    assert!(no_poison.winner.is_none());

    // Clear Veil prevents effects but does not prevent damage. Blocking Life Drain here proves
    // that the 190 -> 10 transition is an effect, not Psychic damage or weakness damage.
    let protected = mechanics_base(
        PlayedCard::from_id(CardId::B3081MegaLucarioEx)
            .with_status_condition(StatusCondition::Poisoned)
            .with_tool(get_card_by_enum(CardId::B4149ClearVeil)),
    );
    let prevented = resolve_will_life_drain(protected);
    assert_eq!(prevented.get_active(1).get_remaining_hp(), 180);
    assert_eq!(prevented.points[0], 0);
    assert!(prevented.winner.is_none());
}

#[test]
fn real_switch_control_removes_the_poison_ko_target() {
    let mut state = mechanics_base(
        PlayedCard::from_id(CardId::B3081MegaLucarioEx)
            .with_energy(vec![EnergyType::Fighting])
            .with_status_condition(StatusCondition::Poisoned),
    );
    state.current_player = 1;
    let (_, actions) = state.generate_possible_actions();
    let retreat = actions
        .into_iter()
        .find(|action| matches!(action.action, SimpleAction::Retreat(1)))
        .expect("Mega Lucario must be able to retreat to the clean Charmander");

    let mut game = get_initialized_game(23);
    game.set_state(state);
    game.apply_action(&retreat);
    let mut switched = game.get_state_clone();
    assert_eq!(switched.get_active(1).get_name(), "Charmander");
    assert!(!switched.in_play_pokemon[1][1].as_ref().unwrap().is_poisoned());
    switched.current_player = 0;

    let after = resolve_will_life_drain(switched);
    assert_eq!(after.get_active(1).get_name(), "Charmander");
    assert_eq!(after.get_active(1).get_remaining_hp(), 10);
    assert_eq!(after.points[0], 0);
    assert!(after.winner.is_none());
}

#[test]
fn shipped_public_policies_choose_the_certain_will_line_at_depth_two() {
    use deckgym::players::{public_clock_effect_value_function, public_effect_value_function};
    let state = xatu_vs_poisoned_lucario(true, false);
    for evaluator in [public_effect_value_function as fn(&State, usize) -> f64,
        public_clock_effect_value_function as fn(&State, usize) -> f64] {
        let choice = choose(&state, 2, Box::new(evaluator), 97);
        assert!(is_will(&choice), "{}", action_label(&choice));
    }
}

#[test]
fn life_drain_into_poison_barb_does_not_poison_xatu() {
    // Luckycad 15:16-15:28: Indeedee ex has 120 HP, Poison and Poison Barb.
    // Use a synthetic 0-0 score and backup so its two-point KO remains inspectable.
    let state = mechanics_base(PlayedCard::from_id(CardId::B1121IndeedeeEx)
        .with_remaining_hp(120)
        .with_status_condition(StatusCondition::Poisoned)
        .with_tool(get_card_by_enum(CardId::A3146PoisonBarb)));
    let after = resolve_will_life_drain(state);
    assert!(after.in_play_pokemon[1][0].is_none());
    assert_eq!(after.get_active(0).get_remaining_hp(), 80);
    assert!(!after.get_active(0).is_poisoned());
    assert_eq!(after.points, [2, 0]);
    assert!(after.winner.is_none());
}
