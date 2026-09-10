use deckgym::{
    actions::Action,
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
};

#[test]
fn electrical_cord_keeps_untransferred_energy_for_knockout_discard() {
    for bench_count in 0..=2 {
        let mut defender_board = vec![PlayedCard::from_id(CardId::A1096PikachuEx)
            .with_damage(40)
            .with_energy(vec![
                EnergyType::Lightning,
                EnergyType::Lightning,
                EnergyType::Lightning,
                EnergyType::Water,
            ])
            .with_tool(get_card_by_enum(CardId::A3a065ElectricalCord))];
        defender_board
            .extend((0..bench_count).map(|_| PlayedCard::from_id(CardId::A1001Bulbasaur)));
        let mut game = get_initialized_game_with_board(
            9,
            0,
            3,
            vec![PlayedCard::from_id(CardId::A1038Ninetales)
                .with_energy(vec![EnergyType::Fire, EnergyType::Fire])],
            defender_board,
        );
        game.apply_action(&Action {
            actor: 0,
            action: attack_action(CardId::A1038Ninetales, 0),
            is_stack: false,
        });
        let state = game.get_state_clone();
        let attached: Vec<_> = state.in_play_pokemon[1]
            .iter()
            .flatten()
            .flat_map(|pokemon| pokemon.attached_energy.iter().copied())
            .collect();
        assert_eq!(attached, vec![EnergyType::Lightning; bench_count]);
        assert_eq!(state.discard_energies[1].len(), 4 - bench_count);
        assert_eq!(
            state.discard_energies[1]
                .iter()
                .filter(|energy| **energy == EnergyType::Lightning)
                .count(),
            3 - bench_count
        );
        assert!(state.discard_energies[1].contains(&EnergyType::Water));
        assert_eq!(
            attached.len() + state.discard_energies[1].len(),
            4,
            "Electrical Cord must conserve Energy with {bench_count} Bench recipients"
        );
    }
}
