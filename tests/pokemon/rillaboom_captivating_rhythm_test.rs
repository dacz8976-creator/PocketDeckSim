use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::PlayedCard,
    test_support::{get_initialized_game_with_board, get_test_game_with_board},
};

fn use_ability_action(actions: &[Action], in_play_idx: usize) -> Option<Action> {
    actions
        .iter()
        .find(|action| matches!(action.action, SimpleAction::UseAbility { in_play_idx: idx } if idx == in_play_idx))
        .cloned()
}

/// Rillaboom's Captivating Rhythm: "Once during your turn, you may flip a coin. If heads, switch
/// in 1 of your opponent's Benched Pokémon to the Active Spot."
///
/// The chooser is *you*, not your opponent, so on heads the follow-up `Activate` choice must be
/// offered to the acting player (actor 0) while targeting the opponent's board.
#[test]
fn test_captivating_rhythm_lets_you_choose_the_opponents_new_active_on_heads() {
    let mut saw_heads = false;
    let mut saw_tails = false;

    for seed in 0..40u64 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![PlayedCard::from_id(CardId::B1027Rillaboom)],
            vec![
                PlayedCard::from_id(CardId::A1001Bulbasaur),
                PlayedCard::from_id(CardId::A1033Charmander),
                PlayedCard::from_id(CardId::A1053Squirtle),
            ],
        );

        game.apply_action(&Action {
            actor: 0,
            action: SimpleAction::UseAbility { in_play_idx: 0 },
            is_stack: false,
        });

        let (actor, choices) = game.get_state_clone().generate_possible_actions();
        let switch_choices: Vec<Action> = choices
            .iter()
            .filter(|choice| matches!(choice.action, SimpleAction::Activate { player: 1, .. }))
            .cloned()
            .collect();

        if switch_choices.is_empty() {
            // Tails: nothing happened, the opponent keeps their Active Pokémon.
            saw_tails = true;
            assert_eq!(
                game.get_state_clone().get_active(1).get_name(),
                "Bulbasaur",
                "seed {seed}: a tails flip must not switch the opponent's Active"
            );
            continue;
        }

        saw_heads = true;
        assert_eq!(
            actor, 0,
            "seed {seed}: Captivating Rhythm lets the Rillaboom player pick the new Active"
        );
        assert_eq!(
            switch_choices.len(),
            2,
            "seed {seed}: both of the opponent's Benched Pokémon should be selectable"
        );

        let promote_charmander = switch_choices
            .iter()
            .find(|choice| {
                matches!(
                    choice.action,
                    SimpleAction::Activate {
                        player: 1,
                        in_play_idx: 1
                    }
                )
            })
            .expect("Charmander should be a selectable target")
            .clone();
        game.apply_action(&promote_charmander);

        assert_eq!(
            game.get_state_clone().get_active(1).get_name(),
            "Charmander",
            "seed {seed}: the chosen Benched Pokémon should become the opponent's Active"
        );
    }

    assert!(
        saw_heads,
        "expected at least one heads flip across the seeds"
    );
    assert!(
        saw_tails,
        "expected at least one tails flip across the seeds"
    );
}

/// B1 229 is the same card at a different rarity.
#[test]
fn test_captivating_rhythm_full_art_shares_the_ability() {
    let game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B1229Rillaboom)],
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    assert!(
        use_ability_action(&actions, 0).is_some(),
        "B1 229 Rillaboom should share Captivating Rhythm"
    );
}

/// NEGATIVE: with nothing on the opponent's Bench there is nothing to switch in, so the ability
/// must not be offered at all rather than burning the once-per-turn use on a no-op.
#[test]
fn test_captivating_rhythm_not_offered_when_opponent_bench_is_empty() {
    let game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B1027Rillaboom)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    assert!(
        use_ability_action(&actions, 0).is_none(),
        "Captivating Rhythm should not be offered when the opponent has no Benched Pokémon"
    );
}

/// NEGATIVE: "Once during your turn".
#[test]
fn test_captivating_rhythm_is_once_per_turn() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B1027Rillaboom)],
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    let ability_action =
        use_ability_action(&actions, 0).expect("Captivating Rhythm should be available");
    game.apply_action(&ability_action);

    // Resolve any pending switch choice so move generation returns to the normal turn actions.
    let (_actor, choices) = game.get_state_clone().generate_possible_actions();
    if let Some(switch) = choices
        .iter()
        .find(|choice| matches!(choice.action, SimpleAction::Activate { player: 1, .. }))
    {
        game.apply_action(&switch.clone());
    }

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    assert!(
        use_ability_action(&actions, 0).is_none(),
        "Captivating Rhythm should not be usable twice in the same turn"
    );
}
