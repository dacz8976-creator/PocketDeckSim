use deckgym::{
    actions::Action,
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game, get_initialized_game_with_board},
    Game,
};

/// Full-flow setup for the vengeance attacks: the opponent (player 1) KOs player 0's
/// Active with Mega Latios ex's Sonic Impulse, player 0 promotes their only benched
/// Pokémon, the turn passes, and player 0's promoted attacker is ready to strike back.
fn game_after_own_active_was_koed(koed_active: CardId, avenger: PlayedCard) -> Game<'static> {
    let mut game = get_initialized_game_with_board(
        0,
        1,
        4,
        vec![PlayedCard::from_id(koed_active), avenger],
        vec![
            PlayedCard::from_id(CardId::PB024MegaLatiosEx).with_energy(vec![
                EnergyType::Water,
                EnergyType::Water,
                EnergyType::Psychic,
            ]),
        ],
    );

    // Player 1 KOs player 0's Active with Sonic Impulse (160).
    game.apply_action(&Action {
        actor: 1,
        action: attack_action(CardId::PB024MegaLatiosEx, 0),
        is_stack: false,
    });

    // Player 0 promotes their only benched Pokémon.
    let (actor, actions) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0, "player 0 should be promoting after the knockout");
    assert_eq!(actions.len(), 1);
    game.apply_action(&actions[0]);

    // Player 1 ends their turn; the Pokémon Checkup shifts the knockout flags.
    let (actor, actions) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 1, "player 1 should be ending their turn");
    assert_eq!(actions.len(), 1);
    game.apply_action(&actions[0]);

    // Resolve player 0's start-of-turn draw.
    game.play_until_stable();
    let state = game.get_state_clone();
    assert_eq!(state.current_player, 0);
    game
}

/// Zarude's Dark Vengeance: 40, +80 if any of your [D] Pokémon were Knocked Out by damage
/// from an attack during the opponent's last turn. Full flow: a Darkness-type Seviper is
/// KO'd, so the recorded knockout type satisfies the filter.
#[test]
fn test_dark_vengeance_boosted_after_darkness_ko() {
    let mut game = game_after_own_active_was_koed(
        CardId::A4a048Seviper, // [D], 80 HP — KO'd by Sonic Impulse
        PlayedCard::from_id(CardId::B3114Zarude)
            .with_energy(vec![EnergyType::Darkness, EnergyType::Darkness]),
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3114Zarude, 0),
        is_stack: false,
    });

    // 40 + 80 = 120. Mega Latios ex: 180 - 120 = 60.
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 60,
        "Dark Vengeance should deal 120 after a [D] Pokémon was KO'd last turn"
    );
}

/// Negative (type filter): a Colorless Snorlax being KO'd does NOT satisfy Zarude's [D]
/// requirement, so Dark Vengeance stays at its base 40 even though a knockout happened.
#[test]
fn test_dark_vengeance_base_damage_after_non_darkness_ko() {
    let mut game = game_after_own_active_was_koed(
        CardId::A1211Snorlax, // Colorless, 150 HP — KO'd by Sonic Impulse
        PlayedCard::from_id(CardId::B3114Zarude)
            .with_energy(vec![EnergyType::Darkness, EnergyType::Darkness]),
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3114Zarude, 0),
        is_stack: false,
    });

    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 140,
        "Dark Vengeance should deal only 40 when the KO'd Pokémon was not [D]"
    );
}

/// Negative (no knockout at all): without any KO last turn, Dark Vengeance deals 40.
#[test]
fn test_dark_vengeance_base_damage_without_ko() {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![PlayedCard::from_id(CardId::B3114Zarude)
            .with_energy(vec![EnergyType::Darkness, EnergyType::Darkness])],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );
    state.current_player = 0;
    state.set_knocked_out_by_opponent_attack_last_turn(false);
    state.set_knocked_out_types_by_opponent_attack_last_turn(vec![]);
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3114Zarude, 0),
        is_stack: false,
    });

    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    assert_eq!(
        hp, 140,
        "Dark Vengeance should deal 40 without a KO last turn"
    );
}

/// Lapras's Raging Freeze: 60, and the opponent's Active is Paralyzed if any of your
/// Pokémon were Knocked Out by damage from an attack during the opponent's last turn.
#[test]
fn test_raging_freeze_paralyzes_after_ko() {
    let mut game = game_after_own_active_was_koed(
        CardId::A1211Snorlax,
        PlayedCard::from_id(CardId::B2b017Lapras).with_energy(vec![
            EnergyType::Water,
            EnergyType::Water,
            EnergyType::Colorless,
        ]),
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2b017Lapras, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    let defender = state.get_active(1);
    assert_eq!(
        defender.get_remaining_hp(),
        120,
        "Raging Freeze always deals its printed 60"
    );
    assert!(
        defender.is_paralyzed(),
        "Raging Freeze should Paralyze after a KO last turn"
    );
}

/// Negative: without a KO last turn, Raging Freeze deals its 60 but does not Paralyze.
#[test]
fn test_raging_freeze_no_paralysis_without_ko() {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![PlayedCard::from_id(CardId::B2b017Lapras).with_energy(vec![
            EnergyType::Water,
            EnergyType::Water,
            EnergyType::Colorless,
        ])],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );
    state.current_player = 0;
    state.set_knocked_out_by_opponent_attack_last_turn(false);
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2b017Lapras, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    let defender = state.get_active(1);
    assert_eq!(defender.get_remaining_hp(), 120);
    assert!(
        !defender.is_paralyzed(),
        "Raging Freeze should not Paralyze without a KO last turn"
    );
}

/// Toxtricity's Vengeful Shock: 40, and +60 AND Paralysis if any of your Pokémon were
/// Knocked Out by damage from an attack during the opponent's last turn.
#[test]
fn test_vengeful_shock_boosted_and_paralyzes_after_ko() {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![PlayedCard::from_id(CardId::B3061Toxtricity)
            .with_energy(vec![EnergyType::Lightning, EnergyType::Lightning])],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );
    state.current_player = 0;
    state.set_knocked_out_by_opponent_attack_last_turn(true);
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3061Toxtricity, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    let defender = state.get_active(1);
    // 40 + 60 = 100. 180 - 100 = 80.
    assert_eq!(
        defender.get_remaining_hp(),
        80,
        "Vengeful Shock should deal 100 after a KO last turn"
    );
    assert!(
        defender.is_paralyzed(),
        "Vengeful Shock should Paralyze after a KO last turn"
    );
}

/// Negative: without a KO last turn, Vengeful Shock deals 40 and does not Paralyze.
#[test]
fn test_vengeful_shock_base_damage_without_ko() {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![PlayedCard::from_id(CardId::B3061Toxtricity)
            .with_energy(vec![EnergyType::Lightning, EnergyType::Lightning])],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );
    state.current_player = 0;
    state.set_knocked_out_by_opponent_attack_last_turn(false);
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3061Toxtricity, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    let defender = state.get_active(1);
    assert_eq!(defender.get_remaining_hp(), 140);
    assert!(
        !defender.is_paralyzed(),
        "Vengeful Shock should not Paralyze without a KO last turn"
    );
}
