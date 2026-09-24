//! Minimal engine fixtures for six outcomes directly visible in the SweetGameBuddy recording.
//!
//! These are independent mid-game states, not a replay. Card IDs select catalog-equivalent
//! mechanics by name, HP, attack, and Ability; they do not identify the artwork printing on video.

use deckgym::{
    actions::Action,
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, init_random_players},
    Game, State,
};

fn fixture_game(
    seed: u64,
    own_board: Vec<PlayedCard>,
    opponent_board: Vec<PlayedCard>,
    points: [u8; 2],
) -> Game<'static> {
    // Scaffold: the recording does not reveal full decks, hands, or deck order. These fixtures
    // supply only the board fields needed to exercise the observed attack result.
    let mut state = State::default();
    state.set_board(own_board, opponent_board);
    state.current_player = 0;
    state.turn_count = 3;
    state.points = points;
    Game::from_state(state, init_random_players(), seed)
}

fn attack(game: &mut Game<'_>, card_id: CardId) {
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(card_id, 0),
        is_stack: false,
    });
}

fn four_grass_energy() -> Vec<EnergyType> {
    vec![
        EnergyType::Grass,
        EnergyType::Grass,
        EnergyType::Grass,
        EnergyType::Grass,
    ]
}

fn observed_exeggutor(current_hp: u32) -> PlayedCard {
    // Frames 87–102 establish the 130-HP printing with Giant Cape (+20 maximum HP) and 20
    // retained damage, hence 130 current HP. Later fixtures carry that Tool and damage forward.
    PlayedCard::from_id(CardId::A1a002Exeggutor)
        .with_energy(four_grass_energy())
        .with_tool(get_card_by_enum(CardId::A2147GiantCape))
        .with_remaining_hp(current_hp)
}

fn assert_observed_exeggutor_checkpoint(card: &PlayedCard, current_hp: u32) {
    assert_eq!(card.get_remaining_hp(), current_hp);
    assert!(card
        .attached_tools
        .iter()
        .any(|tool| tool.get_name() == "Giant Cape"));
}

#[test]
fn observed_sudowoodo_deals_40_with_one_benched_fighting_coach() {
    // Frame 171.6: Fighting Headbutt displays 40 against an Ivysaur at 30 HP. The board visibly
    // contains one benched Lucario with Fighting Coach. A bench Charmander is fixture scaffolding
    // so the post-KO promotion state remains inspectable.
    let attacker = || {
        vec![
            PlayedCard::from_id(CardId::A2a036Sudowoodo).with_energy(vec![EnergyType::Fighting]),
            PlayedCard::from_id(CardId::A2092Lucario),
        ]
    };

    // Nonlethal control: the same target card/type and modifier board at its healthy 90 HP must
    // retain exactly 50 HP, proving 40 rather than merely enough damage for the observed KO.
    let mut exact_damage = fixture_game(
        0,
        attacker(),
        vec![PlayedCard::from_id(CardId::A1002Ivysaur)],
        [0, 0],
    );
    attack(&mut exact_damage, CardId::A2a036Sudowoodo);
    assert_eq!(
        exact_damage
            .get_state_clone()
            .get_active(1)
            .get_remaining_hp(),
        50
    );

    let mut game = fixture_game(
        0,
        attacker(),
        vec![
            PlayedCard::from_id(CardId::A1002Ivysaur).with_remaining_hp(30),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
        [0, 0],
    );

    attack(&mut game, CardId::A2a036Sudowoodo);
    let state = game.get_state_clone();

    assert_eq!(state.points, [1, 0]);
    assert!(state.in_play_pokemon[1][0].is_none());
    assert!(state.discard_piles[1]
        .iter()
        .any(|card| card.get_name() == "Ivysaur"));
}

#[test]
fn observed_psychic_deals_120_to_sudowoodo_and_rocky_helmet_returns_20() {
    // Frames 207–216: Psychic displays 120 with Weakness, Sudowoodo is Knocked Out, and Rocky
    // Helmet leaves Exeggutor at 110 HP. Sudowoodo's one Energy is visible earlier in the sequence.
    let sudowoodo_with_helmet = |base_hp| {
        PlayedCard::new(
            get_card_by_enum(CardId::A2a036Sudowoodo),
            0,
            base_hp,
            vec![EnergyType::Fighting],
            false,
            vec![],
        )
        .with_tool(get_card_by_enum(CardId::A2148RockyHelmet))
    };

    // Raised-HP scaffold: same Sudowoodo type, one Energy, Weakness, and Rocky Helmet. Ending at
    // 80 from 200 proves exact 120 while preserving the observed KO case below.
    let mut exact_damage = fixture_game(
        0,
        vec![observed_exeggutor(130)],
        vec![sudowoodo_with_helmet(200)],
        [0, 0],
    );
    assert_observed_exeggutor_checkpoint(exact_damage.get_state_clone().get_active(0), 130);
    attack(&mut exact_damage, CardId::A1a002Exeggutor);
    let exact_state = exact_damage.get_state_clone();
    assert_eq!(exact_state.get_active(1).get_remaining_hp(), 80);
    assert_eq!(exact_state.get_active(0).get_remaining_hp(), 110);

    let mut game = fixture_game(
        0,
        vec![observed_exeggutor(130)],
        vec![
            sudowoodo_with_helmet(80),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
        [0, 1],
    );

    assert_observed_exeggutor_checkpoint(game.get_state_clone().get_active(0), 130);
    attack(&mut game, CardId::A1a002Exeggutor);
    let state = game.get_state_clone();

    assert_eq!(state.points, [1, 1]);
    assert!(state.in_play_pokemon[1][0].is_none());
    assert_eq!(state.get_active(0).get_remaining_hp(), 110);
}

#[test]
fn observed_psychic_deals_80_to_energyless_lucario_and_helmet_returns_20() {
    // Frames 247–254: the Active Lucario has no visible Energy, remains at 20 HP after Psychic,
    // and Rocky Helmet changes Exeggutor from the observed 110 HP checkpoint to 90 HP.
    let mut game = fixture_game(
        0,
        vec![observed_exeggutor(110)],
        vec![PlayedCard::from_id(CardId::A2092Lucario)
            .with_tool(get_card_by_enum(CardId::A2148RockyHelmet))],
        [1, 1],
    );

    assert_observed_exeggutor_checkpoint(game.get_state_clone().get_active(0), 110);
    attack(&mut game, CardId::A1a002Exeggutor);
    let state = game.get_state_clone();

    assert_eq!(state.get_active(1).get_remaining_hp(), 20);
    assert_eq!(state.get_active(0).get_remaining_hp(), 90);
    assert_eq!(state.points, [1, 1]);
}

#[test]
fn observed_later_psychic_knocks_out_damaged_lucario_and_helmet_still_returns_20() {
    // Frames 290–301: the later Psychic Knocks Out the 20-HP Lucario, Rocky Helmet still deals
    // 20, Exeggutor falls from 90 to 70 HP, and the lower player reaches 2 points.
    let mut game = fixture_game(
        0,
        vec![observed_exeggutor(90)],
        vec![
            PlayedCard::from_id(CardId::A2092Lucario)
                .with_remaining_hp(20)
                .with_tool(get_card_by_enum(CardId::A2148RockyHelmet)),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
        [1, 1],
    );

    assert_observed_exeggutor_checkpoint(game.get_state_clone().get_active(0), 90);
    attack(&mut game, CardId::A1a002Exeggutor);
    let state = game.get_state_clone();

    assert_eq!(state.points, [2, 1]);
    assert!(state.in_play_pokemon[1][0].is_none());
    assert_eq!(state.get_active(0).get_remaining_hp(), 70);
}

#[test]
fn observed_head_smash_deals_150_with_fighting_coach_and_recoils_only_after_ko() {
    // Frames 330 and 332: Head Smash displays 150 with one benched Fighting Coach, Exeggutor is
    // Knocked Out from 70 HP, then Rampardos changes from 150 to 100 HP.
    let rampardos =
        || PlayedCard::from_id(CardId::A2089Rampardos).with_energy(vec![EnergyType::Fighting]);
    let mut observed = fixture_game(
        0,
        vec![rampardos(), PlayedCard::from_id(CardId::A2092Lucario)],
        vec![
            observed_exeggutor(70),
            PlayedCard::from_id(CardId::A1a003CelebiEx),
        ],
        [1, 2],
    );

    assert_observed_exeggutor_checkpoint(observed.get_state_clone().get_active(1), 70);
    attack(&mut observed, CardId::A2089Rampardos);
    let state = observed.get_state_clone();
    assert_eq!(state.points, [2, 2]);
    assert!(state.in_play_pokemon[1][0].is_none());
    assert_eq!(state.get_active(0).get_remaining_hp(), 100);
    assert!(state.discard_piles[1]
        .iter()
        .any(|card| card.get_name() == "Giant Cape"));

    // Negative-control scaffold: the same 150-damage attack against a synthetic 200-HP target
    // does not Knock Out that target, so the conditional 50 recoil must not occur.
    let synthetic_target = PlayedCard::new(
        get_card_by_enum(CardId::A1001Bulbasaur),
        0,
        200,
        vec![],
        false,
        vec![],
    );
    let mut surviving = fixture_game(
        0,
        vec![rampardos(), PlayedCard::from_id(CardId::A2092Lucario)],
        vec![synthetic_target],
        [0, 0],
    );
    attack(&mut surviving, CardId::A2089Rampardos);
    let state = surviving.get_state_clone();
    assert_eq!(state.get_active(1).get_remaining_hp(), 50);
    assert_eq!(state.get_active(0).get_remaining_hp(), 150);
}

#[test]
fn observed_powerful_bloom_two_head_outcome_deals_120_with_weakness_and_final_point() {
    // Frame 370 establishes four flips with a final 2-head/2-tail count. We locate a deterministic
    // fixture seed by observing 100 raw damage on a neutral synthetic target. This selects the
    // engine's two-head forecast class; it does not claim to recover the recording's seed or the
    // order of its four faces.
    let celebi = || PlayedCard::from_id(CardId::A1a003CelebiEx).with_energy(four_grass_energy());
    let selected_seed = (0..256)
        .find(|seed| {
            let neutral_target = PlayedCard::new(
                get_card_by_enum(CardId::A1001Bulbasaur),
                0,
                300,
                vec![],
                false,
                vec![],
            );
            let mut probe = fixture_game(*seed, vec![celebi()], vec![neutral_target], [0, 0]);
            attack(&mut probe, CardId::A1a003CelebiEx);
            probe.get_state_clone().get_active(1).get_remaining_hp() == 200
        })
        .expect("the four-flip binomial forecast should contain a two-head result");

    // Raised-HP scaffold: the same Rampardos card/type and selected two-head forecast outcome
    // must leave exactly 80 HP from 200, proving 100 raw plus 20 Grass Weakness = 120 total.
    let synthetic_rampardos = PlayedCard::new(
        get_card_by_enum(CardId::A2089Rampardos),
        0,
        200,
        vec![],
        false,
        vec![],
    );
    let mut exact_damage = fixture_game(
        selected_seed,
        vec![celebi()],
        vec![synthetic_rampardos],
        [0, 0],
    );
    attack(&mut exact_damage, CardId::A1a003CelebiEx);
    assert_eq!(
        exact_damage
            .get_state_clone()
            .get_active(1)
            .get_remaining_hp(),
        80
    );

    // Frames 374–378: 100 raw damage plus Rampardos's 20 Grass Weakness displays as 120,
    // Knocks Out the observed 100-HP Rampardos, and awards the lower player's third point.
    let mut observed = fixture_game(
        selected_seed,
        vec![celebi()],
        vec![
            PlayedCard::from_id(CardId::A2089Rampardos).with_remaining_hp(100),
            PlayedCard::from_id(CardId::A2a036Sudowoodo),
        ],
        [2, 2],
    );
    attack(&mut observed, CardId::A1a003CelebiEx);
    let state = observed.get_state_clone();

    assert_eq!(state.points, [3, 2]);
    assert!(state.in_play_pokemon[1][0].is_none());
}
