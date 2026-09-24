use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{PlayedCard, StatusCondition},
    test_support::get_initialized_game_with_board,
};

#[test]
fn bad_dreams_ko_is_not_undone_before_glimmoras_point_denial_coin() {
    let mut denied = 0;
    let mut scored = 0;

    for seed in 0..40 {
        let glimmora = PlayedCard::from_id(CardId::B3a045Glimmora)
            .with_remaining_hp(10)
            .with_status_condition(StatusCondition::Asleep)
            .with_tool(get_card_by_enum(CardId::B1218SitrusBerry));
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![
                PlayedCard::from_id(CardId::B2b040Darkrai),
                PlayedCard::from_id(CardId::A1001Bulbasaur),
            ],
            vec![glimmora, PlayedCard::from_id(CardId::A1033Charmander)],
        );

        game.apply_action(&Action {
            actor: 0,
            action: SimpleAction::EndTurn,
            is_stack: false,
        });

        let pending = game.get_state_clone();
        let holder = pending.in_play_pokemon[1][0]
            .as_ref()
            .expect("Glimmora stays in play only until its point-denial coin resolves");
        assert_eq!(
            holder.get_remaining_hp(),
            0,
            "seed {seed}: Sitrus Berry must not heal a zero-HP pending knockout"
        );
        assert!(
            holder
                .attached_tools
                .iter()
                .any(|tool| tool == &get_card_by_enum(CardId::B1218SitrusBerry)),
            "seed {seed}: an ineligible Sitrus Berry must remain attached until the holder is discarded"
        );
        assert_eq!(
            pending
                .move_generation_stack
                .iter()
                .flat_map(|(_, choices)| choices)
                .filter(|action| matches!(action, SimpleAction::ResolveKnockoutPoints { .. }))
                .count(),
            1,
            "seed {seed}: the knockout should queue exactly one point-denial coin"
        );

        let (_, actions) = pending.generate_possible_actions();
        assert_eq!(
            actions.len(),
            1,
            "seed {seed}: the denial coin is mandatory"
        );
        assert!(matches!(
            actions[0].action,
            SimpleAction::ResolveKnockoutPoints { .. }
        ));
        game.apply_action(&actions[0]);

        let resolved = game.get_state_clone();
        assert!(
            resolved.in_play_pokemon[1][0].is_none(),
            "seed {seed}: the coin can deny points but must not prevent the knockout"
        );
        assert_eq!(
            resolved
                .move_generation_stack
                .iter()
                .flat_map(|(_, choices)| choices)
                .filter(|action| matches!(action, SimpleAction::ResolveKnockoutPoints { .. }))
                .count(),
            0,
            "seed {seed}: resolving the coin once must not queue a second coin"
        );
        match resolved.points[0] {
            0 => denied += 1,
            1 => scored += 1,
            points => panic!("seed {seed}: unexpected point total {points}"),
        }
    }

    assert!(denied > 0, "the point-denial coin never produced heads");
    assert!(scored > 0, "the point-denial coin never produced tails");
}
