use deckgym::{
    actions::{try_forecast_action, Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    effects::CardEffect,
    models::{Card, EnergyType, PlayedCard},
    observation::PlayerObservation,
    players::public_reply::{assess_observation, PublicReplyAssessment, UnsupportedReason},
    state::GameOutcome,
    Deck, State,
};
use rand::{rngs::StdRng, SeedableRng};

#[derive(Clone)]
struct FamilyCase {
    id: CardId,
    title: &'static str,
    energy: Vec<EnergyType>,
    damage: u32,
    counterattack: u32,
}

fn family() -> Vec<FamilyCase> {
    vec![
        FamilyCase {
            id: CardId::A3039AlolanSandslash,
            title: "Spike Armor",
            energy: vec![EnergyType::Water],
            damage: 20,
            counterattack: 40,
        },
        FamilyCase {
            id: CardId::A3b048Togedemaru,
            title: "Bristling Spikes",
            energy: vec![EnergyType::Metal, EnergyType::Metal],
            damage: 30,
            counterattack: 30,
        },
        FamilyCase {
            id: CardId::B1047Turtonator,
            title: "Shell Trap",
            energy: vec![EnergyType::Fire, EnergyType::Fire],
            damage: 40,
            counterattack: 20,
        },
        FamilyCase {
            id: CardId::B2010Chesnaught,
            title: "Needle Lariat",
            energy: vec![
                EnergyType::Grass,
                EnergyType::Grass,
                EnergyType::Grass,
                EnergyType::Grass,
            ],
            damage: 80,
            counterattack: 80,
        },
        FamilyCase {
            id: CardId::B3b041MegaSableyeEx,
            title: "Cursed Jewel",
            energy: vec![EnergyType::Darkness, EnergyType::Darkness],
            damage: 80,
            counterattack: 40,
        },
        FamilyCase {
            id: CardId::B3b081MegaSableyeEx,
            title: "Cursed Jewel",
            energy: vec![EnergyType::Darkness, EnergyType::Darkness],
            damage: 80,
            counterattack: 40,
        },
        FamilyCase {
            id: CardId::B3b088MegaSableyeEx,
            title: "Cursed Jewel",
            energy: vec![EnergyType::Darkness, EnergyType::Darkness],
            damage: 80,
            counterattack: 40,
        },
        FamilyCase {
            id: CardId::PA090Togedemaru,
            title: "Bristling Spikes",
            energy: vec![EnergyType::Metal, EnergyType::Metal],
            damage: 30,
            counterattack: 30,
        },
    ]
}

fn state_with_board(
    actor: usize,
    attacker: PlayedCard,
    target: PlayedCard,
    target_bench: Vec<PlayedCard>,
    attacker_points: u8,
) -> State {
    let mut state = State::new(&Deck::default(), &Deck::default());
    state.turn_count = 13;
    state.current_player = actor;
    let mut target_side = vec![target];
    target_side.extend(target_bench);
    if actor == 0 {
        state.set_board(vec![attacker], target_side);
    } else {
        state.set_board(target_side, vec![attacker]);
    }
    state.points[actor] = attacker_points;
    state
}

fn state_for_case(
    actor: usize,
    case: &FamilyCase,
    target: PlayedCard,
    target_bench: Vec<PlayedCard>,
    attacker_points: u8,
) -> State {
    state_with_board(
        actor,
        PlayedCard::from_id(case.id).with_energy(case.energy.clone()),
        target,
        target_bench,
        attacker_points,
    )
}

fn assess(state: &State, observer: usize) -> PublicReplyAssessment {
    assess_observation(&PlayerObservation::from_state(
        state,
        observer,
        &Default::default(),
    ))
}

fn proven_action(state: &State, observer: usize) -> Action {
    let verdict = assess(state, observer);
    let PublicReplyAssessment::ProvenImmediateWin {
        action,
        positive_branches,
        probability_sum,
    } = verdict
    else {
        panic!("expected a certified reply, got {verdict:?}");
    };
    assert_eq!(positive_branches, 1);
    assert_eq!(probability_sum, 1.0);
    action
}

fn assert_no_witness(state: &State, observer: usize) {
    assert!(
        matches!(
            assess(state, observer),
            PublicReplyAssessment::NoCertifiedWitness { .. }
        ),
        "admitted board should remain unknown without a terminal witness"
    );
}

fn apply_only_branch(state: &State, action: &Action) -> State {
    let (probabilities, mut mutations) = try_forecast_action(state, action)
        .expect("registered deterministic attack must forecast")
        .into_branches();
    assert_eq!(probabilities, vec![1.0]);
    assert_eq!(mutations.len(), 1);
    let mut result = state.clone();
    mutations.pop().expect("one branch was asserted")(
        &mut StdRng::seed_from_u64(77),
        &mut result,
        action,
    );
    result
}

fn assert_counterattack_armed(state: &State, player: usize, amount: u32) {
    let serialized = serde_json::to_value(state).expect("state should serialize");
    let effects = serialized["in_play_pokemon"][player][0]["effects"]
        .as_array()
        .expect("active effects should be an array");
    assert!(
        effects.iter().any(
            |entry| entry == &serde_json::json!([{"Counterattack": {"amount": amount}}, 1])
        ),
        "expected Counterattack {{ amount: {amount} }} for duration 1: {effects:?}"
    );
}

#[test]
fn every_exact_self_counterattack_print_certifies_in_both_seats() {
    for case in family() {
        for actor in [0, 1] {
            let state = state_for_case(
                actor,
                &case,
                PlayedCard::from_id(CardId::A1076StarmieEx)
                    .with_remaining_hp(case.damage),
                vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
                1,
            );
            let action = proven_action(&state, 1 - actor);
            assert!(matches!(
                &action.action,
                SimpleAction::Attack(attack) if attack.title == case.title
            ));

            let generic = apply_only_branch(&state, &action);
            assert_eq!(generic.winner, Some(GameOutcome::Win(actor)));
            assert_eq!(generic.points[actor], 3);
            assert!(generic.move_generation_stack.is_empty());
            assert_counterattack_armed(&generic, actor, case.counterattack);
        }
    }
}

#[test]
fn lethal_boundaries_promotion_and_protection_remain_distinct() {
    let cursed = family()
        .into_iter()
        .find(|case| case.id == CardId::B3b041MegaSableyeEx)
        .expect("Cursed Jewel case is listed");

    let exact = state_for_case(
        1,
        &cursed,
        PlayedCard::from_id(CardId::A1076StarmieEx).with_remaining_hp(80),
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        1,
    );
    proven_action(&exact, 0);

    let one_short = state_for_case(
        1,
        &cursed,
        PlayedCard::from_id(CardId::A1076StarmieEx).with_remaining_hp(81),
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        1,
    );
    assert_no_witness(&one_short, 0);

    let promotion_required = state_for_case(
        1,
        &cursed,
        PlayedCard::from_id(CardId::A1076StarmieEx).with_remaining_hp(80),
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        0,
    );
    let verdict = assess(&promotion_required, 0);
    assert!(matches!(
        verdict,
        PublicReplyAssessment::NoCertifiedWitness { ref unsupported }
            if unsupported.iter().any(|entry| {
                matches!(&entry.action.action, SimpleAction::Attack(attack) if attack.title == "Cursed Jewel")
                    && entry.reason == UnsupportedReason::UnresolvedContinuation
            })
    ));

    let mut protected = exact;
    protected
        .in_play_pokemon[0][0].as_mut().unwrap()
        .add_effect(CardEffect::PreventAllDamageAndEffects, 1);
    assert_no_witness(&protected, 0);
}

#[test]
fn canonical_cape_and_weakness_use_the_existing_damage_path() {
    let cursed = family()
        .into_iter()
        .find(|case| case.id == CardId::B3b041MegaSableyeEx)
        .expect("Cursed Jewel case is listed");
    let cape = get_card_by_enum(CardId::A2147GiantCape);

    for remaining_hp in [80, 81] {
        let target = PlayedCard::from_id(CardId::A1001Bulbasaur)
            .with_tool(cape.clone())
            .with_remaining_hp(remaining_hp);
        let state = state_for_case(
            1,
            &cursed,
            target,
            vec![PlayedCard::from_id(CardId::A1005Caterpie)],
            2,
        );
        if remaining_hp == 80 {
            proven_action(&state, 0);
        } else {
            assert_no_witness(&state, 0);
        }
    }

    for remaining_hp in [100, 101] {
        let weakness = state_for_case(
            1,
            &cursed,
            PlayedCard::from_id(CardId::A1129MewtwoEx).with_remaining_hp(remaining_hp),
            vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
            1,
        );
        if remaining_hp == 100 {
            let action = proven_action(&weakness, 0);
            let generic = apply_only_branch(&weakness, &action);
            assert_eq!(generic.winner, Some(GameOutcome::Win(1)));
            assert_eq!(generic.points, [0, 3]);
        } else {
            assert_no_witness(&weakness, 0);
        }
    }
}

#[test]
fn attached_energy_is_required_and_hidden_substitutions_do_not_matter() {
    let cursed = family()
        .into_iter()
        .find(|case| case.id == CardId::B3b041MegaSableyeEx)
        .expect("Cursed Jewel case is listed");
    let mut state = state_for_case(
        1,
        &cursed,
        PlayedCard::from_id(CardId::A1076StarmieEx).with_remaining_hp(80),
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        1,
    );

    for alternate in [false, true] {
        state.hands[0] = if alternate {
            vec![get_card_by_enum(CardId::A1005Caterpie), Card::Unknown]
        } else {
            vec![Card::Unknown, get_card_by_enum(CardId::PA001Potion)]
        };
        state.hands[1] = if alternate {
            vec![Card::Unknown, get_card_by_enum(CardId::A1033Charmander)]
        } else {
            vec![get_card_by_enum(CardId::PA001Potion), Card::Unknown]
        };
        state.decks[0].cards = if alternate {
            vec![get_card_by_enum(CardId::A1033Charmander), Card::Unknown]
        } else {
            vec![Card::Unknown, get_card_by_enum(CardId::A1005Caterpie)]
        };
        state.decks[1].cards = if alternate {
            vec![Card::Unknown, get_card_by_enum(CardId::A1001Bulbasaur)]
        } else {
            vec![get_card_by_enum(CardId::A1005Caterpie), Card::Unknown]
        };
        let action = proven_action(&state, 0);
        assert!(matches!(
            &action.action,
            SimpleAction::Attack(attack) if attack.title == "Cursed Jewel"
        ));
    }

    state.in_play_pokemon[1][0].as_mut().unwrap().attached_energy = vec![EnergyType::Darkness];
    assert_no_witness(&state, 0);
}

#[test]
fn armed_counterattacks_and_existing_hook_classes_still_abstain() {
    let cursed = family()
        .into_iter()
        .find(|case| case.id == CardId::B3b041MegaSableyeEx)
        .expect("Cursed Jewel case is listed");
    let base = state_for_case(
        1,
        &cursed,
        PlayedCard::from_id(CardId::A1076StarmieEx).with_remaining_hp(80),
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        1,
    );

    for player in [0, 1] {
        let mut armed = base.clone();
        armed
            .in_play_pokemon[player][0].as_mut().unwrap()
            .add_effect(CardEffect::Counterattack { amount: 40 }, 1);
        assert!(matches!(
            assess(&armed, 0),
            PublicReplyAssessment::NotApplicable {
                reason: UnsupportedReason::UnsupportedHook
            }
        ));
    }

    let mut helmet = base.clone();
    helmet.in_play_pokemon[0][0].as_mut().unwrap().attached_tools.push(get_card_by_enum(
        CardId::A2148RockyHelmet,
    ));
    assert!(matches!(
        assess(&helmet, 0),
        PublicReplyAssessment::NotApplicable {
            reason: UnsupportedReason::UnsupportedHook
        }
    ));

    let mut passive = base.clone();
    passive.in_play_pokemon[0][0] = Some(
        PlayedCard::from_id(CardId::A1a056Druddigon).with_remaining_hp(80),
    );
    assert!(matches!(
        assess(&passive, 0),
        PublicReplyAssessment::NotApplicable {
            reason: UnsupportedReason::UnsupportedHook
        }
    ));

    let mut stadium = base;
    stadium.set_active_stadium(get_card_by_enum(CardId::B2153TrainingArea));
    assert!(matches!(
        assess(&stadium, 0),
        PublicReplyAssessment::NotApplicable {
            reason: UnsupportedReason::UnsupportedHook
        }
    ));
}
