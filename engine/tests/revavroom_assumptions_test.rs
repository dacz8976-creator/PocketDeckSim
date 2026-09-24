use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, PlayedCard, StatusCondition},
    test_support::{attack_action, get_initialized_game_with_board, get_test_game_with_board},
};

fn card(id: CardId) -> Card {
    get_card_by_enum(id)
}

fn revavroom(tools: Vec<Card>) -> PlayedCard {
    PlayedCard::from_id(CardId::B4115Revavroom).with_tools(tools)
}

fn action(actor: usize, action: SimpleAction) -> Action {
    Action {
        actor,
        action,
        is_stack: false,
    }
}

fn end_turn(game: &mut deckgym::Game<'static>) {
    game.apply_action(&action(0, SimpleAction::EndTurn));
}

#[test]
fn duplicate_sitrus_rechecks_hp_and_leaves_the_second_above_half() {
    let sitrus = card(CardId::B1218SitrusBerry);
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![revavroom(vec![sitrus.clone(), sitrus.clone()]).with_damage(70)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    end_turn(&mut game);

    let state = game.get_state_clone();
    let holder = state.get_active(0);
    assert_eq!(holder.get_remaining_hp(), 80);
    assert_eq!(holder.attached_tools, vec![sitrus.clone()]);
    assert_eq!(state.discard_piles[0], vec![sitrus]);
}

#[test]
fn duplicate_sitrus_both_resolve_when_holder_remains_at_half() {
    let sitrus = card(CardId::B1218SitrusBerry);
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![revavroom(vec![sitrus.clone(), sitrus.clone()]).with_damage(100)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    end_turn(&mut game);

    let state = game.get_state_clone();
    let holder = state.get_active(0);
    assert_eq!(holder.get_remaining_hp(), 80);
    assert!(holder.attached_tools.is_empty());
    assert_eq!(
        state.discard_piles[0]
            .iter()
            .filter(|tool| tool.get_name() == "Sitrus Berry")
            .count(),
        2
    );
}

#[test]
fn heal_block_stops_duplicate_sitrus_without_consuming_either() {
    let sitrus = card(CardId::B1218SitrusBerry);
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![revavroom(vec![sitrus.clone(), sitrus.clone()]).with_damage(100)],
        vec![PlayedCard::from_id(CardId::A3a031Claydol)],
    );

    end_turn(&mut game);

    let state = game.get_state_clone();
    let holder = state.get_active(0);
    assert_eq!(holder.get_remaining_hp(), 20);
    assert_eq!(holder.attached_tools, vec![sitrus.clone(), sitrus]);
    assert!(state.discard_piles[0].is_empty());
}

#[test]
fn duplicate_lum_cures_once_and_leaves_the_later_copy() {
    let lum = card(CardId::A2149LumBerry);
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![revavroom(vec![lum.clone(), lum.clone()])
            .with_status_condition(StatusCondition::Poisoned)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    end_turn(&mut game);

    let state = game.get_state_clone();
    let holder = state.get_active(0);
    assert!(!holder.is_poisoned());
    assert_eq!(holder.attached_tools, vec![lum.clone()]);
    assert_eq!(state.discard_piles[0], vec![lum]);
}

#[test]
fn suppression_discards_most_recent_tool_and_preserves_the_first() {
    let cape = card(CardId::A2147GiantCape);
    let helmet = card(CardId::A2148RockyHelmet);
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B3013Budew)],
        vec![
            revavroom(vec![cape.clone(), helmet.clone()]),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );

    game.apply_action(&action(0, attack_action(CardId::B3013Budew, 0)));

    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).attached_tools, vec![cape]);
    assert!(state.discard_piles[1].contains(&helmet));
}

#[test]
fn suppression_tool_loss_can_knock_out_the_holder() {
    let helmet = card(CardId::A2148RockyHelmet);
    let cape = card(CardId::A2147GiantCape);
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B3013Budew)],
        vec![
            revavroom(vec![helmet.clone(), cape.clone()]).with_damage(110),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );

    game.apply_action(&action(0, attack_action(CardId::B3013Budew, 0)));

    let state = game.get_state_clone();
    assert!(state.in_play_pokemon[1][0].is_none());
    assert_eq!(state.points[0], 1);
    assert!(state.discard_piles[1].contains(&cape));
    assert!(state.discard_piles[1].contains(&helmet));
    assert!(state.discard_piles[1]
        .iter()
        .any(|discarded| discarded.get_name() == "Revavroom"));
}

#[test]
fn devolution_discards_most_recent_tool_and_preserves_the_first() {
    let cape = card(CardId::A2147GiantCape);
    let helmet = card(CardId::A2148RockyHelmet);
    let mut evolved = revavroom(vec![cape.clone(), helmet.clone()]);
    evolved.cards_behind = vec![card(CardId::B4114Varoom)];
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A4a006Celebi)],
        vec![evolved],
    );

    game.apply_action(&action(0, attack_action(CardId::A4a006Celebi, 0)));

    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_name(), "Varoom");
    assert_eq!(state.get_active(1).attached_tools, vec![cape]);
    assert!(state.discard_piles[1].contains(&helmet));
    assert!(state.hands[1]
        .iter()
        .any(|returned| returned.get_name() == "Revavroom"));
}

#[test]
fn devolution_capacity_loss_can_knock_out_the_lower_stage() {
    let helmet = card(CardId::A2148RockyHelmet);
    let cape = card(CardId::A2147GiantCape);
    let mut evolved = revavroom(vec![helmet.clone(), cape.clone()]).with_damage(40);
    evolved.cards_behind = vec![card(CardId::B4114Varoom)];
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A4a006Celebi)],
        vec![evolved, PlayedCard::from_id(CardId::A1033Charmander)],
    );

    game.apply_action(&action(0, attack_action(CardId::A4a006Celebi, 0)));

    let state = game.get_state_clone();
    assert!(state.in_play_pokemon[1][0].is_none());
    assert_eq!(state.points[0], 1);
    assert!(state.discard_piles[1].contains(&cape));
    assert!(state.discard_piles[1].contains(&helmet));
    assert!(state.discard_piles[1]
        .iter()
        .any(|discarded| discarded.get_name() == "Varoom"));
    assert!(state.hands[1]
        .iter()
        .any(|returned| returned.get_name() == "Revavroom"));
}

#[test]
fn limitations_label_the_owner_approved_assumptions_as_unverified() {
    let limitations = deckgym::card_validation::implementation_limitations(CardId::B4115Revavroom);
    assert_eq!(limitations.len(), 3);
    assert!(limitations.iter().all(
        |limitation| limitation.contains("Owner-approved assumption")
            && limitation.contains("not verified in Pokémon TCG Pocket")
    ));
}
