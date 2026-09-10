use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Attack, Card, EnergyType, PlayedCard, StatusCondition, TrainerCard},
    players::{expectiminimax_player::ExpectiMiniMaxPlayer, Player, ValueFunctionPlayer},
    test_support::{attack_action, get_initialized_game_with_board},
    Deck, Game,
};
use rand::{rngs::StdRng, SeedableRng};

fn houndoom() -> PlayedCard {
    PlayedCard::from_id(CardId::PB080MegaHoundoomEx).with_energy(vec![
        EnergyType::Fire,
        EnergyType::Fire,
        EnergyType::Colorless,
    ])
}

fn victini(card_id: CardId) -> PlayedCard {
    PlayedCard::from_id(card_id)
}

fn sponge(hp: u32) -> PlayedCard {
    let card = get_card_by_enum(CardId::PB024MegaLatiosEx);
    PlayedCard::new(card, 0, hp, vec![], false, vec![])
}

fn game(seed: u64, victini_id: CardId, defender: PlayedCard) -> Game<'static> {
    get_initialized_game_with_board(
        seed,
        0,
        3,
        vec![houndoom(), victini(victini_id)],
        vec![defender],
    )
}

fn attack() -> Action {
    Action {
        actor: 0,
        action: attack_action(CardId::PB080MegaHoundoomEx, 0),
        is_stack: false,
    }
}

fn keep() -> Action {
    Action {
        actor: 0,
        action: SimpleAction::KeepAttackCoinResults,
        is_stack: true,
    }
}

fn reroll(source: usize) -> Action {
    Action {
        actor: 0,
        action: SimpleAction::RerollAttackCoins {
            victory_star_in_play_idx: source,
        },
        is_stack: true,
    }
}

fn hidden_zone_coin_attack() -> Action {
    Action {
        actor: 0,
        action: SimpleAction::Attack(Attack {
            energy_required: Vec::new(),
            title: "Astonish".into(),
            fixed_damage: 0,
            effect: Some("Flip a coin. If heads, your opponent reveals a random card from their hand and shuffles it into their deck.".into()),
        }),
        is_stack: false,
    }
}

fn trainer(card_id: CardId) -> TrainerCard {
    match get_card_by_enum(card_id) {
        Card::Trainer(card) => card,
        _ => panic!("expected Trainer card"),
    }
}

#[test]
fn both_victini_printings_are_passive_and_do_not_break_move_generation() {
    for card_id in [CardId::B3025Victini, CardId::PB049Victini] {
        let game = game(0, card_id, sponge(400));
        let (_, actions) = game.get_state_clone().generate_possible_actions();
        assert!(actions
            .iter()
            .any(|action| matches!(action.action, SimpleAction::Attack(_))));
        assert!(!actions
            .iter()
            .any(|action| matches!(action.action, SimpleAction::UseAbility { in_play_idx: 1 })));
    }
}

#[test]
fn two_victini_offer_one_reroll_with_deterministic_source_attribution() {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![
            houndoom(),
            victini(CardId::PB049Victini),
            victini(CardId::B3025Victini),
        ],
        vec![sponge(400)],
    );
    game.apply_action(&attack());
    let state = game.get_state_clone();
    assert_eq!(
        state
            .pending_attack_coin_choice
            .as_ref()
            .unwrap()
            .victory_star_in_play_idx,
        1
    );
    let (_, choices) = state.generate_possible_actions();
    assert_eq!(
        choices
            .iter()
            .filter(|choice| matches!(choice.action, SimpleAction::RerollAttackCoins { .. }))
            .count(),
        1
    );
}

#[test]
fn non_fire_attacker_does_not_receive_victory_star_prompt() {
    let farigiraf = PlayedCard::from_id(CardId::B3a058Farigiraf)
        .with_energy(vec![EnergyType::Colorless, EnergyType::Colorless]);
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![farigiraf, victini(CardId::B3025Victini)],
        vec![sponge(400)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3a058Farigiraf, 0),
        is_stack: false,
    });
    assert!(game.get_state_clone().pending_attack_coin_choice.is_none());
}

#[test]
fn sampled_result_pauses_without_damage_then_keep_commits_exactly_once() {
    for seed in 0..20 {
        let mut game = game(seed, CardId::B3025Victini, sponge(400));
        game.apply_action(&attack());

        let paused = game.get_state_clone();
        let pending = paused
            .pending_attack_coin_choice
            .as_ref()
            .expect("coin attack should pause for Victory Star");
        let expected_damage = pending.flips.iter().filter(|heads| **heads).count() as u32 * 80;
        assert_eq!(
            paused.get_active(1).get_remaining_hp(),
            400,
            "sample must not commit damage"
        );
        let (_, choices) = paused.generate_possible_actions();
        assert_eq!(choices.len(), 2);
        assert!(choices.iter().all(|choice| choice.is_stack));

        game.apply_action(&keep());
        let committed = game.get_state_clone();
        assert!(committed.pending_attack_coin_choice.is_none());
        assert!(committed.move_generation_stack.is_empty());
        assert_eq!(
            400 - committed.get_active(1).get_remaining_hp(),
            expected_damage
        );
        assert_eq!(committed.generate_possible_actions().1.len(), 1);
        assert!(matches!(
            committed.generate_possible_actions().1[0].action,
            SimpleAction::EndTurn
        ));
    }
}

#[test]
fn favorable_result_can_be_voluntarily_replaced_by_a_worse_binding_result() {
    let mut found = None;
    for seed in 0..500 {
        let mut game = game(seed, CardId::B3025Victini, sponge(400));
        game.apply_action(&attack());
        let pending = game
            .get_state_clone()
            .pending_attack_coin_choice
            .expect("Victory Star prompt");
        if pending.flips.iter().all(|heads| *heads) {
            game.apply_action(&reroll(pending.victory_star_in_play_idx));
            let damage = 400 - game.get_state_clone().get_active(1).get_remaining_hp();
            if damage < 240 {
                found = Some((seed, damage));
                break;
            }
        }
    }
    let (_, damage) = found.expect("a favorable first batch must be replaceable by a worse batch");
    assert!(
        damage < 240,
        "the replacement is binding rather than a keep-the-better heuristic"
    );
}

#[test]
fn will_forces_first_batch_only_and_is_consumed_before_reroll() {
    let mut saw_all_tails_replacement = false;
    for seed in 0..500 {
        let mut game = game(seed, CardId::B3025Victini, sponge(400));
        let will = trainer(CardId::A4156Will);
        let mut state = game.get_state_clone();
        state.hands[0].push(Card::Trainer(will.clone()));
        game.set_state(state);
        game.apply_action(&Action {
            actor: 0,
            action: SimpleAction::Play { trainer_card: will },
            is_stack: false,
        });
        game.apply_action(&attack());
        let pending = game
            .get_state_clone()
            .pending_attack_coin_choice
            .expect("Victory Star prompt");
        assert_eq!(
            pending.flips.first(),
            Some(&true),
            "Will must force the first sampled flip"
        );
        game.apply_action(&reroll(pending.victory_star_in_play_idx));
        saw_all_tails_replacement |= game.get_state_clone().get_active(1).get_remaining_hp() == 400;
        if saw_all_tails_replacement {
            break;
        }
    }
    assert!(
        saw_all_tails_replacement,
        "the replacement batch must be able to start tails after Will was consumed"
    );
}

#[test]
fn reroll_sets_global_once_per_turn_flag_and_it_resets_on_next_own_turn() {
    let mut game = game(7, CardId::B3025Victini, sponge(400));
    game.apply_action(&attack());
    let source = game
        .get_state_clone()
        .pending_attack_coin_choice
        .as_ref()
        .unwrap()
        .victory_star_in_play_idx;
    game.apply_action(&reroll(source));
    assert!(game.get_state_clone().victory_star_used_this_turn[0]);

    // End player 0's turn, resolve player 1's forced draw, then end player 1's turn.
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });
    game.play_until_stable();
    assert!(game.get_state_clone().victory_star_used_this_turn[0]);
    game.apply_action(&Action {
        actor: 1,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });
    game.play_until_stable();
    assert!(!game.get_state_clone().victory_star_used_this_turn[0]);
}

#[test]
fn copied_attack_stack_is_not_popped_until_commit_and_is_popped_once() {
    let mut game = game(11, CardId::B3025Victini, sponge(400));
    let mut state = game.get_state_clone();
    let copied = attack_action(CardId::PB080MegaHoundoomEx, 0);
    state.move_generation_stack.push((0, vec![copied.clone()]));
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: copied,
        is_stack: true,
    });
    let paused = game.get_state_clone();
    assert_eq!(
        paused.move_generation_stack.len(),
        2,
        "original copy frame and pause frame remain"
    );
    let flips = paused
        .pending_attack_coin_choice
        .as_ref()
        .unwrap()
        .flips
        .clone();

    game.apply_action(&keep());
    let committed = game.get_state_clone();
    assert!(committed.move_generation_stack.is_empty());
    assert_eq!(
        400 - committed.get_active(1).get_remaining_hp(),
        flips.iter().filter(|heads| **heads).count() as u32 * 80
    );
}

#[test]
fn defender_coin_is_resolved_after_choice_and_never_becomes_the_pending_batch() {
    for seed in 0..20 {
        let mut game = game(
            seed,
            CardId::B3025Victini,
            PlayedCard::from_id(CardId::B2124Meowth),
        );
        game.apply_action(&attack());
        let paused = game.get_state_clone();
        assert_eq!(paused.get_active(1).get_remaining_hp(), 50);
        assert_eq!(
            paused
                .pending_attack_coin_choice
                .as_ref()
                .unwrap()
                .flips
                .len(),
            3
        );
        game.apply_action(&keep());
        assert!(game.get_state_clone().pending_attack_coin_choice.is_none());
    }
}

#[test]
fn confusion_combination_stays_on_explicit_legacy_boundary() {
    let mut game = game(3, CardId::B3025Victini, sponge(400));
    let mut state = game.get_state_clone();
    state.apply_status_condition(0, 0, StatusCondition::Confused);
    game.set_state(state);
    game.apply_action(&attack());
    assert!(
        game.get_state_clone().pending_attack_coin_choice.is_none(),
        "unverified confusion/Victory Star interaction must not use the attack-effect pause"
    );
}

#[test]
fn pending_result_is_public_but_only_controller_receives_choice_payload() {
    let mut game = game(19, CardId::PB049Victini, sponge(400));
    game.apply_action(&attack());
    let controller = game.observation(0);
    let opponent = game.observation(1);
    assert_eq!(
        controller.visible_state().pending_attack_coin_choice,
        opponent.visible_state().pending_attack_coin_choice
    );
    assert_eq!(
        controller
            .visible_state()
            .move_generation_stack
            .last()
            .unwrap()
            .1
            .len(),
        2
    );
    assert!(opponent
        .visible_state()
        .move_generation_stack
        .last()
        .unwrap()
        .1
        .is_empty());

    let serialized = serde_json::to_string(controller.visible_state()).unwrap();
    let round_trip: deckgym::State = serde_json::from_str(&serialized).unwrap();
    assert_eq!(&round_trip, controller.visible_state());
}

#[test]
fn keep_and_reroll_inherit_the_original_attacks_hidden_information_cutoff() {
    let mut game = game(23, CardId::B3025Victini, sponge(400));
    let mut state = game.get_state_clone();
    state.hands[1].push(get_card_by_enum(CardId::A1001Bulbasaur));
    state.decks[1]
        .cards
        .push(get_card_by_enum(CardId::A1033Charmander));
    game.set_state(state);
    game.apply_action(&hidden_zone_coin_attack());

    let mut search_rng = StdRng::seed_from_u64(23);
    let search_state = game.observation(0).search_state(&mut search_rng);
    let (_, choices) = search_state.generate_possible_actions();
    assert_eq!(choices.len(), 2);
    for choice in &choices {
        assert_eq!(
            deckgym::observation::hidden_continuation_reason(&search_state, choice),
            Some("effect or choice depends on unrevealed opponent cards"),
        );
    }
}

#[test]
fn same_game_seed_reproduces_sample_choice_and_replacement_despite_search_work() {
    let mut first = game(123, CardId::B3025Victini, sponge(400));
    let mut second = game(123, CardId::B3025Victini, sponge(400));

    // Speculative policy work uses a caller-owned search RNG and cloned states only.
    let mut search_rng = StdRng::seed_from_u64(999_999);
    let mut search_player = ValueFunctionPlayer {
        deck: Deck::default(),
    };
    let root_state = first.get_state_clone();
    for _ in 0..8 {
        let chosen = search_player.decide_omniscient(
            &mut search_rng,
            &root_state,
            &[
                attack(),
                Action {
                    actor: 0,
                    action: SimpleAction::EndTurn,
                    is_stack: false,
                },
            ],
        );
        assert!(matches!(
            chosen.action,
            SimpleAction::Attack(_) | SimpleAction::EndTurn
        ));
    }

    first.apply_action(&attack());
    second.apply_action(&attack());
    let first_pending = first.get_state_clone().pending_attack_coin_choice.unwrap();
    let second_pending = second.get_state_clone().pending_attack_coin_choice.unwrap();
    assert_eq!(first_pending, second_pending);
    first.apply_action(&reroll(first_pending.victory_star_in_play_idx));
    second.apply_action(&reroll(second_pending.victory_star_in_play_idx));
    assert_eq!(first.get_state_clone(), second.get_state_clone());
}

#[test]
fn search_players_resolve_the_pause_instead_of_scoring_it_as_zero_damage() {
    let root_game = game(31, CardId::B3025Victini, sponge(80));
    let state = root_game.get_state_clone();
    let offered = vec![
        attack(),
        Action {
            actor: 0,
            action: SimpleAction::EndTurn,
            is_stack: false,
        },
    ];
    let mut value_player = ValueFunctionPlayer {
        deck: Deck::default(),
    };
    let mut rng = StdRng::seed_from_u64(1);
    assert!(matches!(
        value_player
            .decide_omniscient(&mut rng, &state, &offered)
            .action,
        SimpleAction::Attack(_)
    ));

    // A tails pause should make an HP-sensitive expectiminimax player choose the replacement.
    let mut tails_state = None;
    for seed in 0..100 {
        let mut candidate = game(seed, CardId::B3025Victini, sponge(400));
        candidate.apply_action(&attack());
        if candidate
            .get_state_clone()
            .pending_attack_coin_choice
            .as_ref()
            .is_some_and(|pending| pending.flips.iter().all(|heads| !*heads))
        {
            tails_state = Some(candidate.get_state_clone());
            break;
        }
    }
    let tails_state = tails_state.expect("seed sweep must contain an all-tails first batch");
    let (_, choices) = tails_state.generate_possible_actions();
    let mut expecti = ExpectiMiniMaxPlayer {
        deck: Deck::default(),
        max_depth: 1,
        write_debug_trees: false,
        value_function: Box::new(|state, myself| {
            -(state.get_active(1 - myself).get_remaining_hp() as f64)
        }),
        opponent_ply: 0,
        consistent_horizon: false,
        soft_opponent: false,
    };
    assert!(matches!(
        expecti
            .decide_omniscient(&mut rng, &tails_state, &choices)
            .action,
        SimpleAction::RerollAttackCoins { .. }
    ));
}
