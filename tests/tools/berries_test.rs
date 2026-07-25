use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{PlayedCard, StatusCondition},
    test_support::get_initialized_game_with_board,
};

/// Lum Berry (A2 149): "At the end of each turn, if the Pokémon this card is attached to is
/// affected by any Special Conditions, it recovers from all of them, and discard this card."
#[test]
fn test_lum_berry_cures_status_and_discards_itself() {
    let holder = PlayedCard::from_id(CardId::A1003Venusaur)
        .with_tool(get_card_by_enum(CardId::A2149LumBerry))
        .with_status_condition(StatusCondition::Poisoned);

    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![holder, PlayedCard::from_id(CardId::A1033Charmander)],
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );

    assert!(
        game.get_state_clone().in_play_pokemon[0][0]
            .as_ref()
            .unwrap()
            .is_poisoned(),
        "setup: holder should start poisoned"
    );

    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });

    let state = game.get_state_clone();
    let holder = state.in_play_pokemon[0][0]
        .as_ref()
        .expect("holder should still be in play");
    assert!(!holder.is_poisoned(), "Lum Berry cures Special Conditions");
    assert!(
        holder.attached_tool.is_none(),
        "Lum Berry discards itself after curing"
    );
}

/// With no Special Condition to cure, Lum Berry must stay attached — otherwise it would burn
/// itself off on the first turn of every game.
#[test]
fn test_lum_berry_stays_attached_when_there_is_nothing_to_cure() {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![
            PlayedCard::from_id(CardId::A1003Venusaur)
                .with_tool(get_card_by_enum(CardId::A2149LumBerry)),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );

    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });

    assert!(
        game.get_state_clone().in_play_pokemon[0][0]
            .as_ref()
            .unwrap()
            .attached_tool
            .is_some(),
        "Lum Berry should not discard itself with no Special Condition present"
    );
}

/// Sitrus Berry (B1 218): "At the end of each turn, if the Pokémon this card is attached to has
/// half of its maximum HP or less remaining, heal 30 damage from it. If you do, discard this
/// card." Venusaur is 160 HP, so 60 remaining is comfortably under half.
#[test]
fn test_sitrus_berry_heals_at_half_hp_and_discards_itself() {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![
            PlayedCard::from_id(CardId::A1003Venusaur)
                .with_remaining_hp(60)
                .with_tool(get_card_by_enum(CardId::B1218SitrusBerry)),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );

    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });

    let state = game.get_state_clone();
    let holder = state.in_play_pokemon[0][0].as_ref().unwrap();
    assert_eq!(holder.get_remaining_hp(), 90, "Sitrus Berry heals 30");
    assert!(
        holder.attached_tool.is_none(),
        "Sitrus Berry discards itself after healing"
    );
}

/// Above half HP the berry must not fire, and must stay attached for later.
#[test]
fn test_sitrus_berry_does_nothing_above_half_hp() {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![
            PlayedCard::from_id(CardId::A1003Venusaur)
                .with_remaining_hp(150)
                .with_tool(get_card_by_enum(CardId::B1218SitrusBerry)),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );

    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });

    let state = game.get_state_clone();
    let holder = state.in_play_pokemon[0][0].as_ref().unwrap();
    assert_eq!(holder.get_remaining_hp(), 150, "no heal above half HP");
    assert!(
        holder.attached_tool.is_some(),
        "Sitrus Berry stays attached until it actually heals"
    );
}
