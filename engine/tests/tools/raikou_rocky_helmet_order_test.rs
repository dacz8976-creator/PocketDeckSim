use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game},
};

#[test]
fn test_raikou_rocky_helmet_promotion_order() {
    let mut game = get_initialized_game(0);
    game.play_until_stable();

    // Set Raikou against Rocky Helmet
    let mut state = game.get_state_clone();
    state.set_board(
        vec![
            PlayedCard::from_id(CardId::A4a025RaikouEx)
                .with_energy(vec![EnergyType::Lightning, EnergyType::Lightning])
                .with_remaining_hp(20),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur)
                .with_tool(get_card_by_enum(CardId::A2148RockyHelmet)),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );
    state.current_player = 0;
    game.set_state(state);

    let attack_action = Action {
        actor: 0,
        action: attack_action(CardId::A4a025RaikouEx, 0),
        is_stack: false,
    };
    game.apply_action(&attack_action);

    // Assert Player has to choose target
    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0);
    assert!(choices
        .iter()
        .all(|choice| matches!(choice.action, SimpleAction::ApplyQueuedAttackDamage { .. })));

    let apply_damage_action = choices[0].clone();
    game.apply_action(&apply_damage_action);

    // Both hits resolve before the Rocky Helmet knockout requires promotion.
    let resolved = game.get_state_clone();
    assert!(resolved.in_play_pokemon[0][0].is_none());
    assert_eq!(resolved.points, [0, 2]);
    assert_eq!(resolved.get_active(1).get_remaining_hp(), 10);
    assert_eq!(resolved.in_play_pokemon[1][1].as_ref().unwrap().get_remaining_hp(), 50);

    // Assert Raikou was K.O. and attacker must activate
    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0);
    assert!(choices.iter().all(|choice| {
        matches!(
            choice.action,
            SimpleAction::Promote {
                player: 0,
                in_play_idx: _
            }
        )
    }));

    let promote_action = choices[0].clone();
    game.apply_action(&promote_action);

    // TODO: Assert this way, or assert directly it should be the next player's turn.
    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0);
    assert!(choices
        .iter()
        .all(|choice| matches!(choice.action, SimpleAction::EndTurn)));
}

#[test]
fn test_jumpluff_ex_takes_rocky_helmet_damage_even_when_switching() {
    let mut game = get_initialized_game(0);
    game.play_until_stable();

    let mut state = game.get_state_clone();
    state.set_board(
        vec![
            PlayedCard::from_id(CardId::A4a003JumpluffEx).with_energy(vec![EnergyType::Grass]),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
        vec![PlayedCard::from_id(CardId::A1004VenusaurEx)
            .with_tool(get_card_by_enum(CardId::A2148RockyHelmet))],
    );
    state.current_player = 0;
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A4a003JumpluffEx, 0),
        is_stack: false,
    });

    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0);
    let switch_action = choices
        .iter()
        .find(|choice| {
            matches!(
                choice.action,
                SimpleAction::Activate {
                    player: 0,
                    in_play_idx: 1
                }
            )
        })
        .expect("Jumpluff ex should be able to switch with its bench")
        .clone();
    game.apply_action(&switch_action);

    let (_, choices) = game.get_state_clone().generate_possible_actions();
    let reaction = choices
        .iter()
        .find(|choice| matches!(choice.action, SimpleAction::ResolveAttackRetaliation { .. }))
        .expect("Rocky Helmet retaliation should follow Jumpluff's switch")
        .clone();
    game.apply_action(&reaction);

    let state = game.get_state_clone();
    assert_eq!(state.get_active(0).get_name(), "Charmander");
    assert_eq!(
        state.get_active(0).get_remaining_hp(),
        60,
        "the replacement Active must not take Rocky Helmet damage"
    );

    let benched_jumpluff = state.in_play_pokemon[0][1]
        .as_ref()
        .expect("Jumpluff ex should be on the bench after switching");
    assert_eq!(benched_jumpluff.get_name(), "Jumpluff ex");
    assert_eq!(
        benched_jumpluff.get_remaining_hp(),
        140,
        "Rocky Helmet damage follows the original attacker to the Bench"
    );
}
