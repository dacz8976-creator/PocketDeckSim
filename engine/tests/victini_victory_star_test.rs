use deckgym::{
    actions::{try_forecast_action, Action, SimpleAction},
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

/// rules/04 §9 (seen in Pocket Sept 29): a Confused attacker's Confusion coin is flipped first and
/// is never offered for a reroll. Tails ends the attack with nothing done and no reroll offered, as
/// before the repair; only heads reaches the attack-effect pause, on the attack's own coins and
/// still before any damage.
#[test]
fn confusion_coin_comes_before_the_attack_effect_pause_and_tails_does_nothing() {
    let (mut paused, mut confusion_tails) = (0, 0);
    for seed in 0..40 {
        let mut game = game(seed, CardId::B3025Victini, sponge(400));
        let mut state = game.get_state_clone();
        state.apply_status_condition(0, 0, StatusCondition::Confused);
        game.set_state(state);
        game.apply_action(&attack());
        let after = game.get_state_clone();
        assert_eq!(after.get_active(1).get_remaining_hp(), 400, "seed {seed}");
        let offers_victory_star = after.generate_possible_actions().1.iter().any(|choice| {
            matches!(
                choice.action,
                SimpleAction::KeepAttackCoinResults | SimpleAction::RerollAttackCoins { .. }
            )
        });
        match &after.pending_attack_coin_choice {
            // Heads: the offer is on Grimhound Flare's own three coins, never on the Confusion coin.
            Some(pending) => {
                assert_eq!(pending.flips.len(), 3, "seed {seed}");
                assert!(offers_victory_star, "seed {seed}");
                paused += 1;
            }
            // Tails: the attack does nothing and no reroll is offered.
            None => {
                assert!(!offers_victory_star, "seed {seed}");
                assert!(!after.victory_star_used_this_turn[0], "seed {seed}");
                confusion_tails += 1;
            }
        }
    }
    assert!(
        paused > 5 && confusion_tails > 5,
        "{paused} pauses, {confusion_tails} Confusion tails"
    );
}

/// A Confusion tails on the repaired path ends the attack, and the turn moves on as after any attack: the one action
/// left is `EndTurn`, as after a committed Keep (`sampled_result_pauses_without_damage_then_keep_commits_exactly_once`).
/// The tails half is committed through `wrap_with_common_logic` in `try_forecast_victory_star_attack`; without that wrap
/// the attack would stay available and the turn would not move on, and no other test would notice (Sonnet's F3).
#[test]
fn a_confusion_tails_on_the_victory_star_path_ends_the_attack_and_the_turn_moves_on() {
    let mut confusion_tails = 0;
    for seed in 0..40 {
        let mut game = game(seed, CardId::B3025Victini, sponge(400));
        let mut state = game.get_state_clone();
        state.apply_status_condition(0, 0, StatusCondition::Confused);
        game.set_state(state);
        game.apply_action(&attack());
        let after = game.get_state_clone();
        if after.pending_attack_coin_choice.is_some() {
            continue; // Confusion heads: the pause, covered above
        }
        confusion_tails += 1;
        let actions = after.generate_possible_actions().1;
        assert_eq!(
            actions.len(),
            1,
            "seed {seed}: after a Confusion tails only EndTurn is left, got {actions:?}"
        );
        assert!(
            matches!(actions[0].action, SimpleAction::EndTurn),
            "seed {seed}: {:?}",
            actions[0]
        );
        assert_eq!(after.get_active(1).get_remaining_hp(), 400, "seed {seed}: tails does nothing");
    }
    assert!(confusion_tails > 5, "{confusion_tails} Confusion tails");
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

// Repairs A and B together (Sonnet's F7: nothing tested them meeting). A Confused Fire attacker with Victory Star takes
// Keep or Reroll after its Confusion heads, and the attack then runs into a defender whose coin-flip Ability cuts
// damage: `finish_attack_after_confusion_heads`, then B's heads cut, which comes off after the attacker's bonuses and
// Weakness (rules/02, step 4). Grimhound Flare is 80 per heads. The defenders get 400 HP so that no branch is a Knock Out.
// Training Area is in play in every case (+10 for a Stage 1 attacker, which Mega Houndoom ex is): without a bonus the old
// order, the cut off the raw damage, and the new one give the same numbers on heads (a hit cut to 0 first was dropped and
// Weakness never applied to it), so the tests could not tell them apart (the laptop Opus's second read of F1-F7). With the
// bonus they can: one head on Bastiodon is 80 + 10 + 20 = 110, and 110 - 100 = 10 comes off after the bonus, against 0 if the
// raw 80 were cut first. All three coin tests fail on the engine with repair A only (d4fbc2a), where the cut is the old one.

fn cut_defender(card_id: CardId) -> PlayedCard {
    PlayedCard::new(get_card_by_enum(card_id), 0, 400, vec![], false, vec![])
}

/// The state paused on a Confused Houndoom's Grimhound Flare after its Confusion heads, under Training Area (+10), with
/// exactly `heads` heads among the three coins, against `defender`.
fn paused_after_confusion_heads(defender: CardId, heads: usize) -> deckgym::State {
    for seed in 0..500 {
        let mut game = game(seed, CardId::B3025Victini, cut_defender(defender));
        let mut state = game.get_state_clone();
        state.apply_status_condition(0, 0, StatusCondition::Confused);
        state.active_stadium = Some(get_card_by_enum(CardId::B2153TrainingArea));
        game.set_state(state);
        game.apply_action(&attack());
        let paused = game.get_state_clone();
        let flips = paused.pending_attack_coin_choice.as_ref().map(|pending| pending.flips.clone());
        if flips.is_some_and(|flips| flips.iter().filter(|face| **face).count() == heads) {
            return paused;
        }
    }
    panic!("no seed paused with {heads} heads");
}

/// (probability, HP the defender loses) of each branch of `choice`, taken on the paused `state`.
fn damage_branches(state: &deckgym::State, choice: &Action) -> Vec<(f64, u32)> {
    let before = state.get_active(1).get_remaining_hp();
    let (probabilities, mutations) = try_forecast_action(state, choice).unwrap().into_branches();
    probabilities
        .iter()
        .zip(mutations)
        .map(|(probability, mutate)| {
            let mut branch = state.clone();
            mutate(&mut StdRng::seed_from_u64(7), &mut branch, choice);
            (*probability, before - branch.get_active(1).get_remaining_hp())
        })
        .collect()
}

fn expected_loss(branches: &[(f64, u32)]) -> f64 {
    assert!((branches.iter().map(|(p, _)| p).sum::<f64>() - 1.0).abs() < 1e-9, "{branches:?}");
    branches.iter().map(|(p, loss)| p * f64::from(*loss)).sum()
}

/// Keep after a Confusion heads into Bastiodon (Metal, weak to Fire; Guarded Grill: heads takes -100). One head is 80, 110
/// with Training Area and Weakness: tails 110, heads 110 - 100 = 10. Cutting the raw 80 first would leave 0 on heads (the hit
/// is dropped before the bonus and Weakness apply).
#[test]
fn keep_after_confusion_heads_takes_guarded_grills_cut_after_weakness() {
    let paused = paused_after_confusion_heads(CardId::A2114Bastiodon, 1);
    let mut branches = damage_branches(&paused, &keep());
    branches.sort_by_key(|(_, loss)| *loss);
    assert_eq!(branches.len(), 2, "{branches:?}");
    assert_eq!((branches[0].1, branches[1].1), (10, 110), "{branches:?}");
    assert!(branches.iter().all(|(probability, _)| (probability - 0.5).abs() < 1e-12), "{branches:?}");
}

/// Reroll after a Confusion heads into Bastiodon: the fresh batch of three coins, then the cut, over every outcome.
/// k heads (Training Area +10 and Weakness +20 on any damage): k = 1 loses 110 or 10, k = 2 loses 190 or 90, k = 3 loses 270
/// or 170, k = 0 nothing (no damage, so no bonus). Expected 3/8 x 60 + 3/8 x 140 + 1/8 x 220 = 102.5. With the cut off the raw
/// damage first the k = 1 heads branch would lose 0 and the expectation would be 100.625.
#[test]
fn reroll_after_confusion_heads_takes_guarded_grills_cut_after_weakness_over_the_whole_batch() {
    let paused = paused_after_confusion_heads(CardId::A2114Bastiodon, 0);
    let source = paused.pending_attack_coin_choice.as_ref().unwrap().victory_star_in_play_idx;
    let branches = damage_branches(&paused, &reroll(source));
    assert!((expected_loss(&branches) - 102.5).abs() < 1e-9, "{branches:?}");
    assert!(branches.iter().any(|(_, loss)| *loss == 10), "the k = 1 heads branch loses 10: {branches:?}");
}

/// The same into Hisuian Goodra (no Weakness; Securely Sheltered: heads takes -80), a finite cut and not a prevention, and
/// after the +10: Keep on one head loses 90 or 10 (80 + 10 - 80; the raw cut would leave 0); Reroll expects 3/8 x 50 + 3/8 x 130
/// + 1/8 x 210 = 93.75 (the raw cut: 91.875; a full prevention on heads: 64.375).
#[test]
fn keep_and_reroll_after_confusion_heads_take_securely_sheltered_as_a_finite_cut() {
    let paused = paused_after_confusion_heads(CardId::B3b050HisuianGoodra, 1);
    let mut kept: Vec<u32> = damage_branches(&paused, &keep()).into_iter().map(|(_, loss)| loss).collect();
    kept.sort_unstable();
    assert_eq!(kept, vec![10, 90]);
    let source = paused.pending_attack_coin_choice.as_ref().unwrap().victory_star_in_play_idx;
    let rerolled = damage_branches(&paused, &reroll(source));
    assert!((expected_loss(&rerolled) - 93.75).abs() < 1e-9, "{rerolled:?}");
}

/// A Confused attacker whose attack flips no coins keeps the old path (`try_forecast_victory_star_attack` returns None
/// when the attack has no coin batch): no pause, no offer, and the same result as with Victory Star already used this
/// turn, where the gate is shut before it starts. Victini's own V-Flame (40, no coins) is the attack; Victini is its own
/// Victory Star source.
#[test]
fn a_confused_attack_that_flips_no_coins_keeps_the_old_path() {
    let (mut hit, mut missed) = (0, 0);
    for seed in 0..40 {
        let play = |used: bool| {
            let mut game = get_initialized_game_with_board(
                seed,
                0,
                3,
                vec![victini(CardId::B3025Victini).with_energy(vec![EnergyType::Fire, EnergyType::Colorless])],
                vec![sponge(400)],
            );
            let mut state = game.get_state_clone();
            state.apply_status_condition(0, 0, StatusCondition::Confused);
            state.victory_star_used_this_turn[0] = used;
            game.set_state(state);
            game.apply_action(&Action {
                actor: 0,
                action: attack_action(CardId::B3025Victini, 0),
                is_stack: false,
            });
            game.get_state_clone()
        };
        let (open, shut) = (play(false), play(true));
        assert!(open.pending_attack_coin_choice.is_none(), "seed {seed}: no pause");
        assert_eq!(
            open.get_active(1).get_remaining_hp(),
            shut.get_active(1).get_remaining_hp(),
            "seed {seed}: the same result as with Victory Star used"
        );
        assert_eq!(open.generate_possible_actions().1.len(), shut.generate_possible_actions().1.len(), "seed {seed}");
        if open.get_active(1).get_remaining_hp() == 400 {
            missed += 1;
        } else {
            hit += 1;
        }
    }
    assert!(hit > 5 && missed > 5, "{hit} hits, {missed} Confusion tails");
}
