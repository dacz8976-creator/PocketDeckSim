use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
};

/// Memory Light (A4a 068): "The Pokémon this card is attached to can use any attack from its
/// previous Evolutions."
///
/// Same effect as Celebi's Time Recall, but scoped to the holder instead of every evolved Pokémon
/// you control — so the attack it unlocks must appear for the holder and only the holder.
#[test]
fn test_memory_light_unlocks_previous_evolution_attacks() {
    let mut venusaur = PlayedCard::from_id(CardId::A1003Venusaur)
        .with_energy(vec![
            EnergyType::Grass,
            EnergyType::Grass,
            EnergyType::Colorless,
            EnergyType::Colorless,
        ])
        .with_tool(get_card_by_enum(CardId::A4a068MemoryLight));
    venusaur.cards_behind = vec![
        get_card_by_enum(CardId::A1001Bulbasaur),
        get_card_by_enum(CardId::A1002Ivysaur),
    ];

    let game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![venusaur, PlayedCard::from_id(CardId::A1033Charmander)],
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );

    let (_, choices) = game.get_state_clone().generate_possible_actions();
    let attack_titles: Vec<String> = choices
        .iter()
        .filter_map(|choice| match &choice.action {
            SimpleAction::Attack(attack) => Some(attack.title.clone()),
            _ => None,
        })
        .collect();

    assert!(
        attack_titles.iter().any(|t| t == "Vine Whip"),
        "Memory Light should unlock Bulbasaur's Vine Whip; saw {attack_titles:?}"
    );
    assert!(
        attack_titles.iter().any(|t| t == "Razor Leaf"),
        "Memory Light should unlock Ivysaur's Razor Leaf; saw {attack_titles:?}"
    );
}

/// Without the tool attached, the previous-evolution attacks must not be offered — otherwise the
/// test above would pass for the wrong reason.
#[test]
fn test_previous_evolution_attacks_are_locked_without_memory_light() {
    let mut venusaur = PlayedCard::from_id(CardId::A1003Venusaur).with_energy(vec![
        EnergyType::Grass,
        EnergyType::Grass,
        EnergyType::Colorless,
        EnergyType::Colorless,
    ]);
    venusaur.cards_behind = vec![
        get_card_by_enum(CardId::A1001Bulbasaur),
        get_card_by_enum(CardId::A1002Ivysaur),
    ];

    let game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![venusaur, PlayedCard::from_id(CardId::A1033Charmander)],
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );

    let (_, choices) = game.get_state_clone().generate_possible_actions();
    assert!(
        !choices.iter().any(|choice| matches!(
            &choice.action,
            SimpleAction::Attack(attack) if attack.title == "Vine Whip"
        )),
        "Vine Whip must not be available without Memory Light"
    );
}

/// Leftovers (A3b 067): "At the end of your turn, if the Pokémon this card is attached to is in
/// the Active Spot, heal 10 damage from that Pokémon."
#[test]
fn test_leftovers_heals_the_active_at_end_of_turn() {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![
            PlayedCard::from_id(CardId::A1003Venusaur)
                .with_remaining_hp(100)
                .with_tool(get_card_by_enum(CardId::A3b067Leftovers)),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );

    let before = game.get_state_clone().in_play_pokemon[0][0]
        .as_ref()
        .map(|p| p.get_remaining_hp())
        .expect("active should exist");

    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });

    let after = game.get_state_clone().in_play_pokemon[0][0]
        .as_ref()
        .map(|p| p.get_remaining_hp())
        .expect("active should still be in play");

    assert_eq!(after, before + 10, "Leftovers heals 10 at end of your turn");
}

/// Lucky Mittens (B1 220): "Whenever your opponent's Pokémon is Knocked Out by damage from an
/// attack used by the Pokémon this card is attached to, draw a card."
#[test]
fn test_lucky_mittens_draws_on_attack_knockout() {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![
            PlayedCard::from_id(CardId::A1095Raichu)
                .with_energy(vec![
                    EnergyType::Lightning,
                    EnergyType::Lightning,
                    EnergyType::Lightning,
                ])
                .with_tool(get_card_by_enum(CardId::B1220LuckyMittens)),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
        vec![
            // 10 HP: Thunderbolt certainly knocks it out.
            PlayedCard::from_id(CardId::A1001Bulbasaur).with_remaining_hp(10),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );

    let hand_before = game.get_state_clone().hands[0].len();

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A1095Raichu, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert!(
        state.in_play_pokemon[1][0].is_none(),
        "the opponent's active should have been knocked out"
    );
    assert_eq!(
        state.hands[0].len(),
        hand_before + 1,
        "Lucky Mittens draws a card when its holder's attack scores a knockout"
    );
}
