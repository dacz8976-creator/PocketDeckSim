use std::collections::BTreeSet;

use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::get_initialized_game,
    Game, State,
};

fn setup(seed: u64) -> Game<'static> {
    let mut game = get_initialized_game(seed);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    state.current_player = 0;
    state.turn_count = 3;
    state.hands = [vec![], vec![]];
    state.discard_piles = [vec![], vec![]];
    game.set_state(state);
    game
}

fn offered_play(state: &State, wanted: CardId) -> Option<Action> {
    let wanted = get_card_by_enum(wanted).get_id();
    state.generate_possible_actions().1.into_iter().find(|action| {
        matches!(&action.action, SimpleAction::Play { trainer_card } if trainer_card.id == wanted)
    })
}

fn play(game: &mut Game<'static>, wanted: CardId) {
    let action = offered_play(&game.get_state_clone(), wanted)
        .unwrap_or_else(|| panic!("{} should be offered", get_card_by_enum(wanted).get_name()));
    game.apply_action(&action);
}

fn evolution_target_actions(state: &State) -> Vec<Action> {
    state
        .generate_possible_actions()
        .1
        .into_iter()
        .filter(|action| {
            matches!(
                action.action,
                SimpleAction::ChooseRandomEvolutionTarget { .. }
            )
        })
        .collect()
}

#[test]
fn mythical_slab_keeps_any_stage_psychic_and_bottoms_a_non_psychic_basic() {
    let slab = get_card_by_enum(CardId::A1a065MythicalSlab);
    let psychic_stage_one = get_card_by_enum(CardId::A1116Kadabra);
    let non_psychic_basic = get_card_by_enum(CardId::A1033Charmander);

    let mut game = setup(0);
    let mut state = game.get_state_clone();
    state.hands[0] = vec![slab.clone()];
    state.decks[0].cards = vec![psychic_stage_one.clone(), non_psychic_basic.clone()];
    game.set_state(state);
    play(&mut game, CardId::A1a065MythicalSlab);
    let state = game.get_state_clone();
    assert_eq!(state.hands[0], vec![psychic_stage_one]);
    assert_eq!(state.decks[0].cards, vec![non_psychic_basic.clone()]);

    let mut game = setup(1);
    let mut state = game.get_state_clone();
    state.hands[0] = vec![slab];
    state.decks[0].cards = vec![
        non_psychic_basic.clone(),
        get_card_by_enum(CardId::A1001Bulbasaur),
    ];
    game.set_state(state);
    play(&mut game, CardId::A1a065MythicalSlab);
    let state = game.get_state_clone();
    assert!(state.hands[0].is_empty());
    assert_eq!(state.decks[0].cards.last(), Some(&non_psychic_basic));
}

#[test]
fn stadium_play_limit_is_separate_from_using_the_stadium() {
    let mut game = setup(0);
    let mut state = game.get_state_clone();
    state.hands[0] = vec![
        get_card_by_enum(CardId::B2a093Mesagoza),
        get_card_by_enum(CardId::B2153TrainingArea),
    ];
    state.decks[0].cards = vec![get_card_by_enum(CardId::PA001Potion)];
    game.set_state(state);

    play(&mut game, CardId::B2a093Mesagoza);
    let after_play = game.get_state_clone();
    let actions = after_play.generate_possible_actions().1;
    assert!(actions
        .iter()
        .any(|action| matches!(action.action, SimpleAction::UseStadium)));
    assert!(offered_play(&after_play, CardId::B2153TrainingArea).is_none());

    let use_action = actions
        .into_iter()
        .find(|action| matches!(action.action, SimpleAction::UseStadium))
        .expect("newly played Mesagoza should still be usable");
    game.apply_action(&use_action);
    assert!(offered_play(&game.get_state_clone(), CardId::B2153TrainingArea).is_none());
}

#[test]
fn hidden_deck_contents_do_not_block_searches_but_an_empty_deck_does() {
    let nonmatching = get_card_by_enum(CardId::PA001Potion);
    for id in [
        CardId::A3a067Gladion,
        CardId::A2151TeamGalacticGrunt,
        CardId::B3150Cabbie,
        CardId::B1a068Clemont,
        CardId::B1a069Serena,
        CardId::B3a071Juliana,
        CardId::B4145OrderPad,
    ] {
        let mut game = setup(0);
        let mut state = game.get_state_clone();
        state.hands[0] = vec![get_card_by_enum(id)];
        state.decks[0].cards = vec![nonmatching.clone()];
        game.set_state(state);
        assert!(
            offered_play(&game.get_state_clone(), id).is_some(),
            "{} should be legal against a nonempty hidden deck",
            get_card_by_enum(id).get_name()
        );

        let mut state = game.get_state_clone();
        state.decks[0].cards.clear();
        game.set_state(state);
        assert!(
            offered_play(&game.get_state_clone(), id).is_none(),
            "{} should be blocked by a visibly empty deck",
            get_card_by_enum(id).get_name()
        );
    }

    let mut game = setup(1);
    let mut state = game.get_state_clone();
    state.hands[0] = vec![
        get_card_by_enum(CardId::A2146PokemonCommunication),
        get_card_by_enum(CardId::A1001Bulbasaur),
    ];
    state.decks[0].cards = vec![nonmatching];
    game.set_state(state);
    assert!(offered_play(&game.get_state_clone(), CardId::A2146PokemonCommunication).is_some());
}

#[test]
fn every_confirmed_deck_taking_trainer_is_blocked_when_the_deck_is_empty() {
    for id in [
        CardId::A1a065MythicalSlab,
        CardId::A4a070TravelingMerchant,
        CardId::B1223May,
        CardId::B1226Lisia,
        CardId::B2a091Arven,
        CardId::B2150Sightseer,
        CardId::B3b067PuppyLovingGirl,
        CardId::B4145OrderPad,
        CardId::B4a069TeamRocketsResearcher,
    ] {
        let mut game = setup(0);
        let mut state = game.get_state_clone();
        state.hands[0] = vec![get_card_by_enum(id)];
        state.decks[0].cards.clear();
        game.set_state(state);
        assert!(
            offered_play(&game.get_state_clone(), id).is_none(),
            "{} should be blocked by an empty deck",
            get_card_by_enum(id).get_name()
        );
    }
}

#[test]
fn stadium_searches_follow_visible_nonempty_deck_legality() {
    for stadium in [CardId::B2a093Mesagoza, CardId::B3153FragrantForest] {
        let mut game = setup(0);
        let mut state = game.get_state_clone();
        state.set_active_stadium(get_card_by_enum(stadium));
        state.decks[0].cards = vec![get_card_by_enum(CardId::PA001Potion)];
        game.set_state(state);
        assert!(game
            .get_state_clone()
            .generate_possible_actions()
            .1
            .iter()
            .any(|action| matches!(action.action, SimpleAction::UseStadium)));

        let mut state = game.get_state_clone();
        state.decks[0].cards.clear();
        game.set_state(state);
        assert!(!game
            .get_state_clone()
            .generate_possible_actions()
            .1
            .iter()
            .any(|action| matches!(action.action, SimpleAction::UseStadium)));
    }

    let mut game = setup(0);
    let mut state = game.get_state_clone();
    state.set_active_stadium(get_card_by_enum(CardId::B3b069KidsRoom));
    state.hands[0] = vec![get_card_by_enum(CardId::A1001Bulbasaur)];
    state.decks[0].cards = vec![get_card_by_enum(CardId::A1033Charmander)];
    game.set_state(state);
    assert!(game
        .get_state_clone()
        .generate_possible_actions()
        .1
        .iter()
        .any(|action| matches!(action.action, SimpleAction::UseStadium)));

    let mut game = setup(0);
    let mut state = game.get_state_clone();
    state.set_active_stadium(get_card_by_enum(CardId::B4a072Arcade));
    state.hands[0] = vec![get_card_by_enum(CardId::A1001Bulbasaur)];
    state.decks[0].cards.clear();
    game.set_state(state);
    assert!(!game
        .get_state_clone()
        .generate_possible_actions()
        .1
        .iter()
        .any(|action| matches!(action.action, SimpleAction::UseStadium)));
}

#[test]
fn quick_grow_extract_lets_the_user_choose_the_target_before_random_evolution() {
    let mut game = setup(0);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A2b005Sprigatito),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    state.hands[0] = vec![get_card_by_enum(CardId::B1a067QuickGrowExtract)];
    state.decks[0].cards = vec![
        get_card_by_enum(CardId::A1002Ivysaur),
        get_card_by_enum(CardId::A2b006Floragato),
    ];
    game.set_state(state);

    play(&mut game, CardId::B1a067QuickGrowExtract);
    let choices = evolution_target_actions(&game.get_state_clone());
    assert_eq!(choices.len(), 2);
    assert_eq!(game.get_state_clone().get_active(0).get_name(), "Bulbasaur");

    let choose_bench = choices
        .into_iter()
        .find(|action| {
            matches!(
                action.action,
                SimpleAction::ChooseRandomEvolutionTarget { in_play_idx: 1, .. }
            )
        })
        .expect("Sprigatito should be a separate player choice");
    game.apply_action(&choose_bench);
    let state = game.get_state_clone();
    assert_eq!(state.get_active(0).get_name(), "Bulbasaur");
    assert_eq!(
        state.in_play_pokemon[0][1].as_ref().unwrap().get_name(),
        "Floragato"
    );
}

#[test]
fn wallace_uses_effective_max_hp_and_randomizes_only_after_target_choice() {
    let mut seen = BTreeSet::new();
    for seed in 0..64 {
        let mut game = setup(seed);
        let mut state = game.get_state_clone();
        state.set_board(
            vec![
                PlayedCard::from_id(CardId::A1074Staryu)
                    .with_tool(get_card_by_enum(CardId::A2147GiantCape)),
                PlayedCard::from_id(CardId::A1077Magikarp),
            ],
            vec![PlayedCard::from_id(CardId::A1033Charmander)],
        );
        state.hands[0] = vec![get_card_by_enum(CardId::B3b068Wallace)];
        state.decks[0].cards = vec![
            get_card_by_enum(CardId::A1078Gyarados),
            get_card_by_enum(CardId::A1a018GyaradosEx),
            get_card_by_enum(CardId::A1075Starmie),
        ];
        game.set_state(state);

        play(&mut game, CardId::B3b068Wallace);
        let choices = evolution_target_actions(&game.get_state_clone());
        assert_eq!(choices.len(), 1, "Giant Cape makes Staryu's maximum HP 70");
        assert!(matches!(
            &choices[0].action,
            SimpleAction::ChooseRandomEvolutionTarget { in_play_idx: 1, .. }
        ));
        game.apply_action(&choices[0]);
        let evolved = game.get_state_clone().in_play_pokemon[0][1]
            .as_ref()
            .unwrap()
            .card
            .get_id();
        seen.insert(evolved);
    }
    assert_eq!(
        seen.len(),
        2,
        "Wallace should sample both eligible Magikarp evolutions, never Starmie"
    );
}

#[test]
fn piers_discards_random_energy_without_replacement() {
    let mut survivors = BTreeSet::new();
    for seed in 0..64 {
        let mut game = setup(seed);
        let mut state = game.get_state_clone();
        state.in_play_pokemon[0][1] = Some(PlayedCard::from_id(CardId::B2100GalarianObstagoon));
        state.in_play_pokemon[1][0] = Some(
            PlayedCard::from_id(CardId::A1033Charmander).with_energy(vec![
                EnergyType::Fire,
                EnergyType::Water,
                EnergyType::Lightning,
            ]),
        );
        state.hands[0] = vec![get_card_by_enum(CardId::B2152Piers)];
        game.set_state(state);
        play(&mut game, CardId::B2152Piers);
        let state = game.get_state_clone();
        assert_eq!(state.get_active(1).attached_energy.len(), 1);
        assert_eq!(state.discard_energies[1].len(), 2);
        survivors.insert(state.get_active(1).attached_energy[0]);
    }
    assert!(
        survivors.len() > 1,
        "Piers must not always discard the last two Energy"
    );
}

#[test]
fn healing_trainers_offer_only_damaged_targets() {
    for (trainer, undamaged, damaged) in [
        (
            CardId::PA001Potion,
            CardId::A1001Bulbasaur,
            CardId::A1001Bulbasaur,
        ),
        (
            CardId::A1219Erika,
            CardId::A1001Bulbasaur,
            CardId::A1001Bulbasaur,
        ),
        (
            CardId::B1221Marlon,
            CardId::B1067Carracosta,
            CardId::B1069Jellicent,
        ),
        (
            CardId::A3155Lillie,
            CardId::A1003Venusaur,
            CardId::A1003Venusaur,
        ),
    ] {
        let mut game = setup(0);
        let mut state = game.get_state_clone();
        state.set_board(
            vec![
                PlayedCard::from_id(undamaged),
                PlayedCard::from_id(damaged).with_damage(10),
            ],
            vec![PlayedCard::from_id(CardId::A1033Charmander)],
        );
        state.hands[0] = vec![get_card_by_enum(trainer)];
        game.set_state(state);

        play(&mut game, trainer);
        let heal_targets = game
            .get_state_clone()
            .generate_possible_actions()
            .1
            .into_iter()
            .filter_map(|action| match action.action {
                SimpleAction::Heal { in_play_idx, .. } => Some(in_play_idx),
                _ => None,
            })
            .collect::<Vec<_>>();
        assert_eq!(
            heal_targets,
            vec![1],
            "{} must not offer an undamaged target",
            get_card_by_enum(trainer).get_name()
        );
    }
}
