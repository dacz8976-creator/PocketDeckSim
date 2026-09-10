use deckgym::{
    actions::Action,
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
};

fn use_attack(game: &mut deckgym::Game<'static>, card: CardId) {
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(card, 0),
        is_stack: false,
    });
    game.play_until_stable();
}

#[test]
fn clear_veil_blocks_hyper_whirlpool_energy_effect_but_not_damage() {
    let attacker = PlayedCard::from_id(CardId::A3b016Vaporeon).with_energy(vec![
        EnergyType::Water,
        EnergyType::Water,
        EnergyType::Colorless,
    ]);
    let clear_veil = get_card_by_enum(CardId::B4149ClearVeil);
    let defender = PlayedCard::from_id(CardId::B4115Revavroom)
        .with_energy(vec![EnergyType::Fire; 7])
        .with_tool(clear_veil);
    let mut game = get_initialized_game_with_board(9, 0, 3, vec![attacker], vec![defender]);
    let hp_before = game.get_state_clone().get_active(1).get_remaining_hp();

    use_attack(&mut game, CardId::A3b016Vaporeon);

    let state = game.get_state_clone();
    assert_eq!(hp_before - state.get_active(1).get_remaining_hp(), 70);
    assert_eq!(
        state.get_active(1).attached_energy,
        vec![EnergyType::Fire; 7]
    );
    assert!(state.discard_energies[1].is_empty());
}

#[test]
fn lethal_hyper_whirlpool_conserves_all_attached_energy_through_knockout() {
    let attacker = PlayedCard::from_id(CardId::A3b016Vaporeon).with_energy(vec![
        EnergyType::Water,
        EnergyType::Water,
        EnergyType::Colorless,
    ]);
    let defender =
        PlayedCard::from_id(CardId::B4a034Gimmighoul).with_energy(vec![EnergyType::Lightning; 7]);
    let mut game = get_initialized_game_with_board(13, 0, 3, vec![attacker], vec![defender]);

    use_attack(&mut game, CardId::A3b016Vaporeon);

    let state = game.get_state_clone();
    assert!(state.in_play_pokemon[1][0].is_none());
    assert_eq!(state.points[0], 1);
    assert_eq!(state.discard_energies[1], vec![EnergyType::Lightning; 7]);
}
