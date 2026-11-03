use deckgym::{
    actions::{try_forecast_action, Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{get_initialized_game, get_initialized_game_with_board},
    Game, State,
};
use rand::{rngs::StdRng, SeedableRng};

#[test]
fn test_darkrai_ex_nightmare_aura() {
    // Darkrai ex's Nightmare Aura: Whenever you attach a Darkness Energy from your Energy Zone to this Pokémon, do 20 damage to your opponent's Active Pokémon.

    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();

    // Set up Darkrai ex vs Bulbasaur
    state.set_board(
        vec![PlayedCard::from_id(CardId::A2110DarkraiEx)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    state.current_player = 0;
    game.set_state(state);

    // Attach Darkness energy from Energy Zone to Darkrai ex
    let attach_action = Action {
        actor: 0,
        action: SimpleAction::Attach {
            attachments: vec![(1, EnergyType::Darkness, 0)],
            is_turn_energy: true,
        },
        is_stack: false,
    };

    game.apply_action(&attach_action);
    let state = game.get_state_clone();

    // Check that Darkrai ex has the energy attached
    assert_eq!(
        state.get_active(0).attached_energy.len(),
        1,
        "Darkrai ex should have 1 energy attached"
    );

    // Check that opponent's active took 20 damage
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        50,
        "Opponent's active should have taken 20 damage (70 - 20 = 50)"
    );
}

#[test]
fn test_darkrai_ex_nightmare_aura_only_darkness() {
    // Test that non-Darkness energy doesn't trigger the ability

    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();

    state.set_board(
        vec![PlayedCard::from_id(CardId::A2110DarkraiEx)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    state.current_player = 0;
    game.set_state(state);

    // Attach Fire energy from Energy Zone to Darkrai ex
    let attach_action = Action {
        actor: 0,
        action: SimpleAction::Attach {
            attachments: vec![(1, EnergyType::Fire, 0)],
            is_turn_energy: true,
        },
        is_stack: false,
    };

    game.apply_action(&attach_action);
    let state = game.get_state_clone();

    // Check that opponent's active did NOT take damage
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        70,
        "Opponent's active should not have taken damage from non-Darkness energy"
    );
}

#[test]
fn test_darkrai_ex_nightmare_aura_also_fires_on_an_effect_attach_from_the_zone() {
    // R8-10b (Dustin, Nov 1, 2026): a Darkness Energy that an effect attaches from the Energy Zone
    // (is_turn_energy = false: not the turn's Energy) fires Nightmare Aura too, as the text reads.

    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();

    state.set_board(
        vec![PlayedCard::from_id(CardId::A2110DarkraiEx)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    state.current_player = 0;
    game.set_state(state);

    // Attach Darkness energy from Energy Zone by an effect (is_turn_energy = false)
    let attach_action = Action {
        actor: 0,
        action: SimpleAction::Attach {
            attachments: vec![(1, EnergyType::Darkness, 0)],
            is_turn_energy: false,
        },
        is_stack: false,
    };

    game.apply_action(&attach_action);
    let state = game.get_state_clone();

    // Check that opponent's active took 20 damage
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        50,
        "Opponent's active should have taken 20 damage from an effect's Energy Zone attach (70 - 20 = 50)"
    );
}

#[test]
fn test_darkrai_ex_nightmare_aura_ko_triggers_promotion() {
    // If Nightmare Aura KOs the opponent's Active and they have a bench,
    // promotion should be queued.

    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();

    // Darkrai ex vs Bulbasaur at 20 HP with a benched Pokemon
    state.set_board(
        vec![PlayedCard::from_id(CardId::A2110DarkraiEx)],
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur).with_remaining_hp(20),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
    );
    state.current_player = 0;
    game.set_state(state);

    // Attach Darkness energy from Energy Zone to Darkrai ex
    let attach_action = Action {
        actor: 0,
        action: SimpleAction::Attach {
            attachments: vec![(1, EnergyType::Darkness, 0)],
            is_turn_energy: true,
        },
        is_stack: false,
    };

    game.apply_action(&attach_action);
    let state = game.get_state_clone();

    // Promotion should be queued for the opponent (player 1)
    let (actor, actions) = state.generate_possible_actions();
    let has_promotion = actor == 1
        && actions
            .iter()
            .any(|a| matches!(a.action, SimpleAction::Promote { .. }));

    assert!(
        has_promotion,
        "Expected promotion to be queued after Darkrai Aura KOs active"
    );
}

// ---------------------------------------------------------------------------------------------
// Fork additions (R8-10b): Nightmare Aura fires on every [D] Energy attached from the Energy Zone to
// Darkrai ex, an effect's attach included, not only on the turn's Energy (Dustin's decision, Nov 1,
// 2026). Sableye's Jeweled Gift is the only effect that can attach a [D] from the Zone to it.
// ---------------------------------------------------------------------------------------------

/// Every Darkrai ex printing. Nightmare Aura: "Whenever you attach a [D] Energy from your Energy Zone
/// to this Pokémon, do 20 damage to your opponent's Active Pokémon."
const DARKRAI_EX_PRINTINGS: [CardId; 6] = [
    CardId::A2110DarkraiEx,
    CardId::A2187DarkraiEx,
    CardId::A2202DarkraiEx,
    CardId::A4b245DarkraiEx,
    CardId::A4b378DarkraiEx,
    CardId::PA042DarkraiEx,
];

/// Both Sableye printings. Jeweled Gift ([C]): "Take a random Energy from among [G], [R], [W], [L],
/// [P], [F], [D], and [M] Energy from your Energy Zone and attach it to 1 of your Benched Pokémon."
const SABLEYE_PRINTINGS: [CardId; 2] = [CardId::B3a040Sableye, CardId::PB070Sableye];

const BASIC_ENERGY_TYPES: [EnergyType; 8] = [
    EnergyType::Grass,
    EnergyType::Fire,
    EnergyType::Water,
    EnergyType::Lightning,
    EnergyType::Psychic,
    EnergyType::Fighting,
    EnergyType::Darkness,
    EnergyType::Metal,
];

/// Player 1's board in the damage tests: an Active Wailord ex (250 HP).
fn wailord_ex() -> Vec<PlayedCard> {
    vec![PlayedCard::from_id(CardId::B4197WailordEx)]
}

/// Player 0 to act on turn 3: an Active `sableye` with the [C] Energy Jeweled Gift needs and `bench`
/// on the Bench, against player 1's `opponent` board.
fn sableye_game(
    sableye: PlayedCard,
    bench: Vec<PlayedCard>,
    opponent: Vec<PlayedCard>,
) -> Game<'static> {
    let mut board = vec![sableye.with_energy(vec![EnergyType::Colorless])];
    board.extend(bench);
    get_initialized_game_with_board(0, 0, 3, board, opponent)
}

/// The first legal action that `pick` accepts; `actor` must be the player to act.
fn legal_action(state: &State, actor: usize, pick: impl Fn(&SimpleAction) -> bool) -> Action {
    let (to_act, actions) = state.generate_possible_actions();
    assert_eq!(to_act, actor, "player {actor} is to act");
    actions
        .into_iter()
        .find(|action| pick(&action.action))
        .expect("the action is legal")
}

/// Player 0's Sableye uses Jeweled Gift, taken from the legal actions, and each of the attack's
/// forecast branches is applied: one per printed Energy type, each queuing player 0's choice of
/// Benched Pokémon for an Energy of that type. Returns each branch's Energy type and state, with the
/// attach still to choose.
fn jeweled_gift_branches(game: &Game<'static>) -> Vec<(EnergyType, State)> {
    let initial = game.get_state_clone();
    let jeweled_gift = legal_action(&initial, 0, |action| {
        matches!(action, SimpleAction::Attack(attack) if attack.title == "Jeweled Gift")
    });
    let (_, branches) = try_forecast_action(&initial, &jeweled_gift)
        .expect("Jeweled Gift's forecast should be exactly priced")
        .into_branches();
    assert_eq!(branches.len(), 8, "one branch per printed Energy type");
    branches
        .into_iter()
        .map(|branch| {
            let mut state = initial.clone();
            branch(&mut StdRng::seed_from_u64(0), &mut state, &jeweled_gift);
            let queued = legal_action(&state, 0, |action| {
                matches!(
                    action,
                    SimpleAction::Attach {
                        is_turn_energy: false,
                        ..
                    }
                )
            });
            let SimpleAction::Attach { attachments, .. } = queued.action else {
                unreachable!("the queued choice is an Attach");
            };
            (attachments[0].1, state)
        })
        .collect()
}

/// The state of Jeweled Gift's [D] branch (see `jeweled_gift_branches`).
fn jeweled_gift_d_branch(game: &Game<'static>) -> State {
    jeweled_gift_branches(game)
        .into_iter()
        .find(|(energy, _)| *energy == EnergyType::Darkness)
        .map(|(_, state)| state)
        .expect("Jeweled Gift has a [D] branch")
}

/// In `state`, player 0 takes the legal attach from the Energy Zone to their Pokémon at
/// `in_play_idx`: the turn's Energy (`is_turn_energy`) or the Energy an effect queued. Returns the
/// state after it.
fn attach_from_zone(
    game: &mut Game<'static>,
    state: State,
    is_turn_energy: bool,
    in_play_idx: usize,
) -> State {
    let attach = legal_action(&state, 0, |action| {
        matches!(
            action,
            SimpleAction::Attach { attachments, is_turn_energy: turn }
                if *turn == is_turn_energy
                    && attachments.len() == 1
                    && attachments[0].2 == in_play_idx
        )
    });
    game.set_state(state);
    game.apply_action(&attach);
    game.get_state_clone()
}

/// Jeweled Gift's [D] branch, given to a Benched Darkrai ex, fires Nightmare Aura: 20 to player 1's
/// Active Wailord ex (250 to 230). The other 7 branches give Darkrai ex their Energy and do nothing.
/// Both Sableye printings, every Darkrai ex printing.
#[test]
fn test_jeweled_gift_d_energy_onto_a_benched_darkrai_ex_fires_nightmare_aura() {
    for sableye in SABLEYE_PRINTINGS {
        for darkrai in DARKRAI_EX_PRINTINGS {
            let mut game = sableye_game(
                PlayedCard::from_id(sableye),
                vec![PlayedCard::from_id(darkrai)],
                wailord_ex(),
            );
            let branches = jeweled_gift_branches(&game);
            assert!(BASIC_ENERGY_TYPES
                .iter()
                .all(|energy| branches.iter().any(|(given, _)| given == energy)));
            for (energy, state) in branches {
                let state = attach_from_zone(&mut game, state, false, 1);
                let darkrai_ex = state.in_play_pokemon[0][1]
                    .as_ref()
                    .expect("Darkrai ex stays on the Bench");
                assert_eq!(darkrai_ex.attached_energy, vec![energy]);
                let expected = if energy == EnergyType::Darkness {
                    230
                } else {
                    250
                };
                assert_eq!(
                    state.get_active(1).get_remaining_hp(),
                    expected,
                    "{sableye:?}'s Jeweled Gift gives {darkrai:?} {energy:?}"
                );
            }
        }
    }
}

/// Nightmare Aura fires only on a [D] given to Darkrai ex itself. With a Benched Darkrai ex and a
/// Benched Darkrai (B2b 040, which has no Nightmare Aura), Jeweled Gift's [D] given to Darkrai ex does
/// 20 and the same [D] given to Darkrai does nothing; so does the turn's [D] Energy given to Darkrai.
#[test]
fn test_a_d_energy_attached_to_a_pokemon_that_is_not_darkrai_ex_does_nothing() {
    let bench = || {
        vec![
            PlayedCard::from_id(CardId::A2110DarkraiEx),
            PlayedCard::from_id(CardId::B2b040Darkrai),
        ]
    };
    for sableye in SABLEYE_PRINTINGS {
        let mut game = sableye_game(PlayedCard::from_id(sableye), bench(), wailord_ex());
        let d_branch = jeweled_gift_d_branch(&game);
        for (in_play_idx, expected) in [(1, 230), (2, 250)] {
            let state = attach_from_zone(&mut game, d_branch.clone(), false, in_play_idx);
            let given = state.in_play_pokemon[0][in_play_idx]
                .as_ref()
                .expect("the Benched Pokémon stays in play");
            assert_eq!(given.attached_energy, vec![EnergyType::Darkness]);
            assert_eq!(
                state.get_active(1).get_remaining_hp(),
                expected,
                "{sableye:?}'s Jeweled Gift gives {} a [D]",
                given.get_name()
            );
        }
    }

    let mut game = sableye_game(
        PlayedCard::from_id(CardId::B3a040Sableye),
        bench(),
        wailord_ex(),
    );
    let mut state = game.get_state_clone();
    state.energy_zone[0].current = Some(EnergyType::Darkness);
    let state = attach_from_zone(&mut game, state, true, 2);
    assert_eq!(state.get_active(1).get_remaining_hp(), 250);
}

/// The turn's [D] Energy still fires Nightmare Aura exactly once, and Jeweled Gift's [D] later in the
/// same turn fires it once more: player 0 attaches the turn's [D] Energy to the Benched Darkrai ex
/// (250 to 230), then Sableye's Jeweled Gift gives it a second [D] (230 to 210). Both Sableye
/// printings, every Darkrai ex printing.
#[test]
fn test_the_turns_d_energy_and_jeweled_gifts_d_each_fire_nightmare_aura_once() {
    for sableye in SABLEYE_PRINTINGS {
        for darkrai in DARKRAI_EX_PRINTINGS {
            let mut game = sableye_game(
                PlayedCard::from_id(sableye),
                vec![PlayedCard::from_id(darkrai)],
                wailord_ex(),
            );
            let mut state = game.get_state_clone();
            state.energy_zone[0].current = Some(EnergyType::Darkness);
            let state = attach_from_zone(&mut game, state, true, 1);
            assert_eq!(state.energy_zone[0].current, None, "the turn's Energy is used");
            assert_eq!(
                state.get_active(1).get_remaining_hp(),
                230,
                "the turn's [D] Energy given to {darkrai:?}"
            );

            let d_branch = jeweled_gift_d_branch(&game);
            let state = attach_from_zone(&mut game, d_branch, false, 1);
            let darkrai_ex = state.in_play_pokemon[0][1]
                .as_ref()
                .expect("Darkrai ex stays on the Bench");
            assert_eq!(
                darkrai_ex.attached_energy,
                vec![EnergyType::Darkness, EnergyType::Darkness]
            );
            assert_eq!(
                state.get_active(1).get_remaining_hp(),
                210,
                "{sableye:?}'s Jeweled Gift gives {darkrai:?} a second [D]"
            );
        }
    }
}

/// Nightmare Aura's 20, fired inside Jeweled Gift, Knocks Out player 1's Snorlax (20 HP left, holding
/// Rescue Scarf) with Ceruledge on their Bench. As with Flame Aura inside an attack
/// (charizard_flame_aura_test.rs; rules/README #9, rules/04 §7), it is an Ability Knock Out: it scores,
/// but it is not "by damage from an attack". Rescue Scarf ("If the Pokémon this card is attached to is
/// Knocked Out by damage from an attack from your opponent's Pokémon, put it into your hand instead of
/// the discard pile.") leaves Snorlax in the discard pile; Lucky Mittens on Sableye ("Whenever your
/// opponent's Pokémon is Knocked Out by damage from an attack used by the Pokémon this card is attached
/// to, draw a card.") draws nothing; and on player 1's next turn nothing of theirs counts as Knocked
/// Out by damage from an attack during the last turn (the flag Revenge attacks read).
#[test]
fn test_a_nightmare_aura_knock_out_inside_jeweled_gift_is_an_ability_knock_out() {
    for sableye in SABLEYE_PRINTINGS {
        for darkrai in [CardId::A2110DarkraiEx, CardId::PA042DarkraiEx] {
            let mut game = sableye_game(
                PlayedCard::from_id(sableye)
                    .with_tool(get_card_by_enum(CardId::B1220LuckyMittens)),
                vec![PlayedCard::from_id(darkrai)],
                vec![
                    PlayedCard::from_id(CardId::A1211Snorlax)
                        .with_remaining_hp(20)
                        .with_tool(get_card_by_enum(CardId::A4155RescueScarf)),
                    PlayedCard::from_id(CardId::C1028Ceruledge),
                ],
            );
            let hand_before = game.get_state_clone().hands[0].len();
            let d_branch = jeweled_gift_d_branch(&game);
            assert!(
                d_branch
                    .move_generation_stack
                    .iter()
                    .any(|(_, choices)| choices.iter().any(|choice| matches!(
                        choice,
                        SimpleAction::ResolveAttackRetaliation { .. }
                    ))),
                "Jeweled Gift's ResolveAttackRetaliation choice is pending when its attach is applied"
            );
            attach_from_zone(&mut game, d_branch, false, 1);
            // The attack's Knock Out wave, then player 1's promotion.
            game.play_until_stable();

            let state = game.get_state_clone();
            let case = format!("{sableye:?} with {darkrai:?}");
            assert_eq!(state.points, [1, 0], "{case}: the Knock Out scores");
            assert_eq!(state.get_active(1).get_name(), "Ceruledge", "{case}");
            assert!(
                !state.hands[1]
                    .iter()
                    .any(|card| card.get_name() == "Snorlax"),
                "{case}: no Rescue Scarf"
            );
            assert!(
                state.discard_piles[1]
                    .iter()
                    .any(|card| card.get_name() == "Snorlax"),
                "{case}"
            );
            assert_eq!(
                state.hands[0].len(),
                hand_before,
                "{case}: no Lucky Mittens draw"
            );

            let end_turn = legal_action(&state, 0, |action| matches!(action, SimpleAction::EndTurn));
            game.apply_action(&end_turn);
            // The Pokémon Checkup and player 1's draw.
            game.play_until_stable();
            let state = game.get_state_clone();
            assert_eq!(state.current_player, 1, "{case}");
            assert!(
                !state.get_knocked_out_by_opponent_attack_last_turn(),
                "{case}: no Revenge flag for player 1"
            );
        }
    }
}
