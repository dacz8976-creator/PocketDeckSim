use super::*;
use deckgym::actions::{try_forecast_action, SimpleAction};
use deckgym::card_ids::CardId;
use deckgym::database::get_card_by_enum;
use deckgym::models::PlayedCard;
use deckgym::observation::RevealedKnowledge;

fn state(ours: Vec<PlayedCard>, theirs: Vec<PlayedCard>) -> State {
    let mut s = State::new(&Deck::default(), &Deck::default());
    s.current_player = 0;
    s.turn_count = 3;
    s.set_board(ours, theirs);
    s
}

fn apply_exact(s: &mut State, a: &Action) {
    assert!(s.generate_possible_actions().1.contains(a));
    let (p, effects) = try_forecast_action(s, a).unwrap().into_branches();
    assert_eq!(p, vec![1.0]);
    let mut next = s.clone();
    effects.into_iter().next().unwrap()(&mut StdRng::seed_from_u64(9), &mut next, a);
    *s = next;
}

fn assert_distinct_public_choices(s: &State, label: &str) -> Vec<Action> {
    let (actor, choices) = s.generate_possible_actions();
    assert_eq!(actor, 0);
    assert_eq!(choices.len(), 2, "{label}");
    let obs = PlayerObservation::from_state(s, 0, &RevealedKnowledge::default());
    let visible = obs.visible_state().generate_possible_actions().1;
    assert_eq!(visible.len(), choices.len());
    assert!(choices.iter().all(|choice| visible.contains(choice)));
    let env = RawEnv::new(vec![], "v2.2").unwrap();
    let mut encoded = Vec::new();
    for a in &choices {
        let (tokens, _) = action_tokens(a);
        assert!(tokens.iter().any(|token| token == &format!("V:{label}")), "{tokens:?}");
        let mut row = vec![0.0; env.act_len()];
        env.encode_action(a, &mut row);
        assert!(row[..HASH_BUCKETS].iter().any(|x| *x > 0.0));
        encoded.push(row);
    }
    assert_ne!(encoded[0], encoded[1], "{label} alternatives need distinct encoded rows");
    choices
}

#[test]
fn new_energy_choices_are_visible_distinct_and_priced_after_selection() {
    let mut retreat = state(
        vec![
            PlayedCard::from_id(CardId::B3a054GougingFire)
                .with_energy(vec![EnergyType::Fire, EnergyType::Fire, EnergyType::Lightning]),
            PlayedCard::from_id(CardId::B3a053WalkingWake),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    apply_exact(&mut retreat, &Action {
        actor: 0, action: SimpleAction::Retreat(1), is_stack: false,
    });
    let retreat_choices = assert_distinct_public_choices(&retreat, "ChooseRetreatEnergy");
    let obs = PlayerObservation::from_state(&retreat, 0, &RevealedKnowledge::default());
    let (_, rows, _) = v2::features(&obs, &retreat_choices, true);
    assert!(rows.iter().all(|row| row[0] == 1.0));

    let mut attack = state(
        vec![PlayedCard::from_id(CardId::B3a054GougingFire)
            .with_energy(vec![EnergyType::Fire, EnergyType::Fire, EnergyType::Lightning])],
        vec![
            PlayedCard::from_id(CardId::A1033Charmander).with_damage(50),
            PlayedCard::from_id(CardId::PB024MegaLatiosEx),
        ],
    );
    apply_exact(&mut attack, &Action {
        actor: 0, action: deckgym::test_support::attack_action(CardId::B3a054GougingFire, 0), is_stack: false,
    });
    let attack_choices = assert_distinct_public_choices(&attack, "ChooseAttackEnergyDiscard");
    let obs = PlayerObservation::from_state(&attack, 0, &RevealedKnowledge::default());
    let (_, rows, _) = v2::features(&obs, &attack_choices, true);
    assert!(rows.iter().all(|row| row[0] == 1.0));
    assert!(rows.iter().all(|row| row[1] > 0.0));
}

#[test]
fn random_evolution_target_is_encoded_and_hidden_deck_refusal_is_scoped() {
    let mut evolve = state(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A2b005Sprigatito),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    let extract = get_card_by_enum(CardId::B1a067QuickGrowExtract);
    evolve.hands[0] = vec![extract.clone()];
    evolve.decks[0].cards = vec![
        get_card_by_enum(CardId::A1002Ivysaur),
        get_card_by_enum(CardId::A2b006Floragato),
    ];
    let Card::Trainer(trainer_card) = extract else { panic!("expected trainer") };
    apply_exact(&mut evolve, &Action {
        actor: 0, action: SimpleAction::Play { trainer_card }, is_stack: false,
    });
    let targets = assert_distinct_public_choices(&evolve, "ChooseRandomEvolutionTarget");
    let obs = PlayerObservation::from_state(&evolve, 0, &RevealedKnowledge::default());
    let (_, rows, _) = v2::features(&obs, &targets, true);
    assert!(rows.iter().all(|row| row[0] == 1.0), "known own deck supports each real target");
    let mut unknown = evolve.clone();
    unknown.decks[0].cards.fill(Card::Unknown);
    let unknown_obs = PlayerObservation::from_state(&unknown, 0, &RevealedKnowledge::default());
    let (_, rows, _) = v2::features(&unknown_obs, &targets, true);
    assert!(rows.iter().all(|row| row[0] == 0.0), "unknown evolution card stays unpriced");
    let diagnostics = v2::diagnostics(&unknown_obs, &targets, false);
    assert!(diagnostics.iter().all(|item| item.contains("hidden_refusal")));
}
