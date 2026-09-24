use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{PlayedCard, StatusCondition},
    test_support::{attack_action, get_initialized_game_with_board, get_test_game_with_board},
};

fn has_evolution(actions: &[Action], card_id: &str, in_play_idx: usize) -> bool {
    actions.iter().any(|action| {
        matches!(
            &action.action,
            SimpleAction::Evolve {
                evolution,
                in_play_idx: candidate_idx,
                from_deck: false,
            } if evolution.get_id() == card_id && *candidate_idx == in_play_idx
        )
    })
}

fn has_ability(actions: &[Action], in_play_idx: usize) -> bool {
    actions.iter().any(|action| {
        matches!(
            action.action,
            SimpleAction::UseAbility {
                in_play_idx: candidate_idx
            } if candidate_idx == in_play_idx
        )
    })
}

#[test]
fn asleep_paralyzed_and_confused_replace_one_another_without_clearing_poison_or_burn() {
    let exclusive = [
        StatusCondition::Asleep,
        StatusCondition::Paralyzed,
        StatusCondition::Confused,
    ];

    for previous in exclusive {
        for replacement in exclusive {
            if previous == replacement {
                continue;
            }
            let pokemon = PlayedCard::from_id(CardId::A1001Bulbasaur)
                .with_status_condition(StatusCondition::Poisoned)
                .with_status_condition(StatusCondition::Burned)
                .with_status_condition(previous)
                .with_status_condition(replacement);

            assert!(pokemon.has_status(replacement));
            assert!(!pokemon.has_status(previous));
            assert!(pokemon.is_poisoned(), "Poison must remain independent");
            assert!(pokemon.is_burned(), "Burn must remain independent");
        }
    }
}

#[test]
fn boosted_evolution_applies_only_to_the_active_eevee() {
    let mut eevee = PlayedCard::from_id(CardId::B1184Eevee);
    eevee.played_this_turn = true;
    let mut game = get_initialized_game_with_board(
        19_301,
        0,
        1,
        vec![eevee, PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    let mut state = game.get_state_clone();
    state.hands[0] = vec![
        get_card_by_enum(CardId::A1a019Vaporeon),
        get_card_by_enum(CardId::A1002Ivysaur),
    ];
    game.set_state(state);

    let actions = game.get_state_clone().generate_possible_actions().1;
    assert!(has_evolution(&actions, "A1a 019", 0));
    assert!(
        !has_evolution(&actions, "A1 002", 1),
        "Active Eevee's Boosted Evolution must not unlock its Benched teammate"
    );
}

#[test]
fn power_of_alchemy_removes_boosted_evolution_timing_exception() {
    let mut eevee = PlayedCard::from_id(CardId::B1184Eevee);
    eevee.played_this_turn = true;
    let mut game = get_initialized_game_with_board(
        19_302,
        0,
        3,
        vec![eevee],
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::B2097AlolanMuk),
        ],
    );
    let mut state = game.get_state_clone();
    state.hands[0] = vec![get_card_by_enum(CardId::A1a019Vaporeon)];
    game.set_state(state);

    let actions = game.get_state_clone().generate_possible_actions().1;
    assert!(
        !has_evolution(&actions, "A1a 019", 0),
        "suppressed Boosted Evolution must not bypass played-this-turn timing"
    );
}

#[test]
fn pichu_crackly_toss_targets_only_benched_basics() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A4066Pichu),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A1002Ivysaur),
        ],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A4066Pichu, 0),
        is_stack: false,
    });

    let actions = game.get_state_clone().generate_possible_actions().1;
    let target_indices = actions
        .iter()
        .filter_map(|action| match &action.action {
            SimpleAction::Attach { attachments, .. } => {
                attachments.first().map(|(_, _, in_play_idx)| *in_play_idx)
            }
            _ => None,
        })
        .collect::<Vec<_>>();
    assert_eq!(target_indices, vec![1]);
}

#[test]
fn reckless_shearing_requires_both_a_hand_card_and_a_card_to_draw() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A2123Garchomp)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    let mut state = game.get_state_clone();
    state.hands[0] = vec![get_card_by_enum(CardId::A1001Bulbasaur)];
    state.decks[0].cards.clear();
    game.set_state(state);

    let actions = game.get_state_clone().generate_possible_actions().1;
    assert!(!has_ability(&actions, 0));

    let mut state = game.get_state_clone();
    state.decks[0].cards = vec![get_card_by_enum(CardId::A1002Ivysaur)];
    game.set_state(state);
    let actions = game.get_state_clone().generate_possible_actions().1;
    assert!(has_ability(&actions, 0));
}

#[test]
fn hidden_deck_contents_do_not_block_search_abilities() {
    for (ability_holder, nonmatching_deck_card) in [
        (CardId::A3b059Ambipom, CardId::A1001Bulbasaur),
        (CardId::A3a027Shiinotic, CardId::PA001Potion),
    ] {
        let mut game = get_test_game_with_board(
            vec![PlayedCard::from_id(ability_holder)],
            vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        );
        let mut state = game.get_state_clone();
        state.decks[0].cards = vec![get_card_by_enum(nonmatching_deck_card)];
        game.set_state(state);
        let actions = game.get_state_clone().generate_possible_actions().1;
        assert!(
            has_ability(&actions, 0),
            "a nonempty hidden deck must permit the search attempt"
        );

        let mut state = game.get_state_clone();
        state.decks[0].cards.clear();
        game.set_state(state);
        let actions = game.get_state_clone().generate_possible_actions().1;
        assert!(
            !has_ability(&actions, 0),
            "an empty deck is visibly unable to supply a card"
        );
    }
}
