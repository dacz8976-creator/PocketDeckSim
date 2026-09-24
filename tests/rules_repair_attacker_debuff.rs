use deckgym::{
    actions::SimpleAction,
    card_ids::CardId,
    database::get_card_by_enum,
    effects::CardEffect,
    models::{Card, EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
    Game,
};

fn choose(game: &mut Game<'static>, expected: SimpleAction) {
    let (actor, actions) = game.get_state_clone().generate_possible_actions();
    let action = actions.into_iter().find(|a| a.action == expected)
        .unwrap_or_else(|| panic!("missing legal action {expected:?} for player {actor}"));
    game.apply_action(&action);
}

fn settle_forced(game: &mut Game<'static>) {
    for _ in 0..32 {
        let state = game.get_state_clone();
        if state.winner.is_some() { return; }
        let (_, actions) = state.generate_possible_actions();
        if actions.len() != 1 || !actions[0].is_stack { return; }
        game.apply_action(&actions[0]);
    }
    panic!("forced continuation did not settle");
}

fn finish_attack_turn(game: &mut Game<'static>) {
    settle_forced(game);
    if game.get_state_clone().winner.is_none() {
        choose(game, SimpleAction::EndTurn);
        settle_forced(game);
    }
}

fn play_sabrina(game: &mut Game<'static>) {
    let Card::Trainer(trainer_card) = get_card_by_enum(CardId::A1225Sabrina) else { unreachable!() };
    choose(game, SimpleAction::Play { trainer_card });
    settle_forced(game);
}

#[test]
fn mapped_debuffs_follow_the_defender_after_sabrina_changes_its_target() {
    for (card, reduction) in [(CardId::A1151Cubone, 20), (CardId::A2a030Clefable, 30), (CardId::B3078Bonsly, 30)] {
        let mut game = get_initialized_game_with_board(77, 0, 3,
            vec![PlayedCard::from_id(card).with_energy(vec![EnergyType::Psychic; 3]), PlayedCard::from_id(CardId::A1211Snorlax)],
            vec![PlayedCard::from_id(CardId::A1190Raticate).with_energy(vec![EnergyType::Fire])]);
        let mut state = game.get_state_clone();
        state.hands[1] = vec![get_card_by_enum(CardId::A1225Sabrina)];
        game.set_state(state);
        choose(&mut game, attack_action(card, 0));
        finish_attack_turn(&mut game);
        play_sabrina(&mut game);
        assert_eq!(game.get_state_clone().get_active(0).get_name(), "Snorlax");
        choose(&mut game, attack_action(CardId::A1190Raticate, 0));
        finish_attack_turn(&mut game);
        assert_eq!(game.get_state_clone().get_active(0).get_remaining_hp(), 150 - (40 - reduction), "{card:?}");
    }
}

#[test]
fn recorded_rattata_evolution_clears_teary_attack_and_bite_scores() {
    let mut game = get_initialized_game_with_board(77, 0, 3,
        vec![PlayedCard::from_id(CardId::B3078Bonsly), PlayedCard::from_id(CardId::A1211Snorlax)],
        vec![PlayedCard::from_id(CardId::A1189Rattata).with_energy(vec![EnergyType::Fire])]);
    let mut state=game.get_state_clone();
    state.hands[1]=vec![get_card_by_enum(CardId::A1190Raticate)];
    game.set_state(state);
    choose(&mut game, attack_action(CardId::B3078Bonsly, 0));
    finish_attack_turn(&mut game);
    assert_eq!(game.get_state_clone().get_active(1).get_remaining_hp(), 10);
    choose(&mut game, SimpleAction::Evolve { evolution: get_card_by_enum(CardId::A1190Raticate), in_play_idx: 0, from_deck: false });
    assert_eq!(game.get_state_clone().get_active(1).get_remaining_hp(), 50);
    choose(&mut game, attack_action(CardId::A1190Raticate, 0));
    assert_eq!(game.get_state_clone().points, [0, 1]);
    assert!(game.get_state_clone().in_play_pokemon[0][0].is_none());
}

#[test]
fn a_different_attacker_after_retreat_is_not_reduced() {
    let raticate = PlayedCard::from_id(CardId::A1190Raticate).with_energy(vec![EnergyType::Fire]);
    let mut game=get_initialized_game_with_board(77,0,3,
        vec![PlayedCard::from_id(CardId::B3078Bonsly), PlayedCard::from_id(CardId::A1211Snorlax)],
        vec![raticate.clone(), raticate]);
    choose(&mut game, attack_action(CardId::B3078Bonsly,0));
    finish_attack_turn(&mut game);
    choose(&mut game, SimpleAction::Retreat(1));
    settle_forced(&mut game);
    choose(&mut game, attack_action(CardId::A1190Raticate,0));
    assert_eq!(game.get_state_clone().points,[0,1]);
}

#[test]
fn reduced_attack_damage_applies_to_bench_targets() {
    let mut game=get_initialized_game_with_board(77,0,3,
        vec![PlayedCard::from_id(CardId::B3078Bonsly), PlayedCard::from_id(CardId::A1211Snorlax)],
        vec![PlayedCard::from_id(CardId::A1154Hitmonlee).with_energy(vec![EnergyType::Fighting])]);
    choose(&mut game, attack_action(CardId::B3078Bonsly,0));
    finish_attack_turn(&mut game);
    choose(&mut game, attack_action(CardId::A1154Hitmonlee,0));
    finish_attack_turn(&mut game);
    assert_eq!(game.get_state_clone().in_play_pokemon[0][1].as_ref().unwrap().get_remaining_hp(),150);
}

#[test]
fn outgoing_reduction_precedes_bounded_field_weakness() {
    let mut attacker=PlayedCard::from_id(CardId::A1155Hitmonchan).with_energy(vec![EnergyType::Fighting]);
    attacker.add_effect(CardEffect::ReducedAttackDamage { amount: 20 },1);
    let mut game=get_initialized_game_with_board(77,0,3,vec![attacker],vec![PlayedCard::from_id(CardId::A1211Snorlax)]);
    let mut state=game.get_state_clone();state.set_active_stadium(get_card_by_enum(CardId::B3155BoundedField));game.set_state(state);
    choose(&mut game,attack_action(CardId::A1155Hitmonchan,0));
    assert_eq!(game.get_state_clone().get_active(1).get_remaining_hp(),130,"(30 - 20) x 2 = 20, not 30 x 2 - 20");
}

#[test]
fn teary_attack_expires_after_the_next_opponent_turn() {
    let mut game=get_initialized_game_with_board(77,0,3,
        vec![PlayedCard::from_id(CardId::B3078Bonsly),PlayedCard::from_id(CardId::A1211Snorlax)],
        vec![PlayedCard::from_id(CardId::A1190Raticate).with_energy(vec![EnergyType::Fire])]);
    choose(&mut game,attack_action(CardId::B3078Bonsly,0));
    finish_attack_turn(&mut game);
    choose(&mut game,attack_action(CardId::A1190Raticate,0));
    finish_attack_turn(&mut game);
    assert_eq!(game.get_state_clone().get_active(0).get_remaining_hp(),20);
    choose(&mut game,SimpleAction::EndTurn);
    settle_forced(&mut game);
    choose(&mut game,attack_action(CardId::A1190Raticate,0));
    assert_eq!(game.get_state_clone().points,[0,1]);
}
