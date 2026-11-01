// Ported from upstream deckgym-core #433 (tests/pokemon/c1_grass_fire_test.rs, as of e7cc5ce): the Sawsbuck, Amoonguss, Volcanion, Ceruledge and Venusaur tests, without the Raboot, Ribombee and Vespiquen tests (later R8 commits), with fork tests added at the end (Rally Back through real Knock Outs; the printings' status).
use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    card_validation::{get_implementation_status, implementation_limitations, ImplementationStatus},
    models::{EnergyType, PlayedCard, StatusCondition},
    test_support::{attack_action, get_initialized_game_with_board, get_test_game_with_board},
    Game,
};

fn attack(game: &mut deckgym::Game<'static>, card_id: CardId) {
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(card_id, 0),
        is_stack: false,
    });
    game.play_until_stable();
}

/// Sawsbuck - Leaf Litter Tackle: 100 damage, then discard a [G] Energy from this Pokémon.
#[test]
fn test_sawsbuck_leaf_litter_tackle_discards_a_grass_energy() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::C1010Sawsbuck).with_energy(vec![
            EnergyType::Grass,
            EnergyType::Fire,
            EnergyType::Fire,
        ])],
        vec![PlayedCard::from_id(CardId::B4197WailordEx)],
    );
    attack(&mut game, CardId::C1010Sawsbuck);

    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_remaining_hp(), 150);
    assert_eq!(
        state.get_active(0).attached_energy,
        vec![EnergyType::Fire, EnergyType::Fire]
    );
    assert_eq!(state.discard_energies[0], vec![EnergyType::Grass]);
}
/// Amoonguss - Astonish: a random card from the opponent's hand is shuffled into their deck.
#[test]
fn test_amoonguss_astonish_shuffles_a_random_hand_card_back() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::C1012Amoonguss)
            .with_energy(vec![EnergyType::Grass, EnergyType::Colorless])],
        vec![PlayedCard::from_id(CardId::A1211Snorlax)],
    );
    let state = game.get_state_clone();
    let hand_before = state.hands[1].len();
    let deck_before = state.decks[1].cards.len();

    attack(&mut game, CardId::C1012Amoonguss);

    let state = game.get_state_clone();
    assert_eq!(state.hands[1].len(), hand_before - 1);
    assert_eq!(state.decks[1].cards.len(), deck_before + 1);
}
/// Volcanion - Dynamite Steam: flip 2 coins, 110 damage for each heads.
#[test]
fn test_volcanion_dynamite_steam_damage_scales_with_heads() {
    let mut seen = std::collections::BTreeSet::new();
    for seed in 0..40 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![
                PlayedCard::from_id(CardId::C1019Volcanion).with_energy(vec![
                    EnergyType::Fire,
                    EnergyType::Fire,
                    EnergyType::Fire,
                    EnergyType::Colorless,
                ]),
            ],
            vec![PlayedCard::from_id(CardId::B4197WailordEx)],
        );
        attack(&mut game, CardId::C1019Volcanion);
        let state = game.get_state_clone();
        seen.insert(250 - state.get_active(1).get_remaining_hp());
    }
    assert_eq!(seen, [0, 110, 220].into_iter().collect());
}
/// Ceruledge - Rally Back: +70 damage if one of our Pokémon was Knocked Out by an attack last turn.
#[test]
fn test_ceruledge_rally_back_adds_damage_after_a_knockout_last_turn() {
    for (knocked_out, expected_damage) in [(true, 140), (false, 70)] {
        let mut game = get_test_game_with_board(
            vec![
                PlayedCard::from_id(CardId::C1028Ceruledge).with_energy(vec![
                    EnergyType::Fire,
                    EnergyType::Fire,
                    EnergyType::Colorless,
                ]),
            ],
            vec![PlayedCard::from_id(CardId::B4197WailordEx)],
        );
        let mut state = game.get_state_clone();
        state.set_knocked_out_by_opponent_attack_last_turn(knocked_out);
        game.set_state(state);
        attack(&mut game, CardId::C1028Ceruledge);

        let state = game.get_state_clone();
        assert_eq!(
            250 - state.get_active(1).get_remaining_hp(),
            expected_damage
        );
    }
}

/// Venusaur - Sunny Heal: once during your turn, you may heal 30 damage from your Active Pokémon.
#[test]
fn test_venusaur_sunny_heal_heals_active_once_per_turn() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur).with_damage(50),
            PlayedCard::from_id(CardId::C1003Venusaur),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    let ability = Action {
        actor: 0,
        action: SimpleAction::UseAbility { in_play_idx: 1 },
        is_stack: false,
    };
    assert!(game
        .get_state_clone()
        .generate_possible_actions()
        .1
        .contains(&ability));
    game.apply_action(&ability);
    game.play_until_stable();

    let state = game.get_state_clone();
    assert_eq!(state.get_active(0).get_remaining_hp(), 70 - 50 + 30);
    assert!(!state.generate_possible_actions().1.contains(&ability));
}

// ---------------------------------------------------------------------------------------------
// Fork additions.
// ---------------------------------------------------------------------------------------------

fn ready_ceruledge() -> PlayedCard {
    PlayedCard::from_id(CardId::C1028Ceruledge).with_energy(vec![
        EnergyType::Fire,
        EnergyType::Fire,
        EnergyType::Colorless,
    ])
}

fn end_turn(game: &mut Game<'static>, actor: usize) {
    game.apply_action(&Action {
        actor,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });
    // The Pokémon Checkup, any promotion, and the next player's draw.
    game.play_until_stable();
}

/// Full flow for Rally Back, with no flag set by hand: the opponent (player 1) Knocks Out player 0's
/// Active Snorlax with Mega Latios ex's Sonic Impulse (160), player 0 promotes their only Benched
/// Pokémon, a ready Ceruledge, and player 1 ends the turn, so the Pokémon Checkup shifts the
/// knockout flag.
fn ceruledge_after_a_knock_out_by_an_attack() -> Game<'static> {
    let mut game = get_initialized_game_with_board(
        0,
        1,
        4,
        vec![PlayedCard::from_id(CardId::A1211Snorlax), ready_ceruledge()],
        vec![
            PlayedCard::from_id(CardId::PB024MegaLatiosEx).with_energy(vec![
                EnergyType::Water,
                EnergyType::Water,
                EnergyType::Psychic,
            ]),
        ],
    );
    game.apply_action(&Action {
        actor: 1,
        action: attack_action(CardId::PB024MegaLatiosEx, 0),
        is_stack: false,
    });

    let (actor, actions) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0, "player 0 should be promoting after the knockout");
    assert_eq!(actions.len(), 1);
    game.apply_action(&actions[0]);

    let (actor, actions) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 1, "player 1 should be ending their turn");
    assert_eq!(actions.len(), 1);
    game.apply_action(&actions[0]);
    game.play_until_stable();

    let state = game.get_state_clone();
    assert_eq!(state.current_player, 0);
    assert_eq!(state.get_active(0).get_name(), "Ceruledge");
    game
}

/// Ceruledge - Rally Back: "If any of your Pokémon were Knocked Out by damage from an attack during
/// your opponent's last turn, this attack does 70 more damage." After a real Knock Out by the
/// opponent's attack: 70 + 70.
#[test]
fn test_ceruledge_rally_back_after_a_knock_out_by_the_opponents_attack() {
    let mut game = ceruledge_after_a_knock_out_by_an_attack();
    attack(&mut game, CardId::C1028Ceruledge);

    // Mega Latios ex (180 HP, no Weakness): 180 - 140 = 40.
    assert_eq!(game.get_state_clone().get_active(1).get_remaining_hp(), 40);
}

/// Rally Back reads only the opponent's last turn: Ceruledge waits a turn after the Knock Out, the
/// opponent's next turn knocks out nothing, and Rally Back does its printed 70.
#[test]
fn test_ceruledge_rally_back_ignores_a_knock_out_two_turns_ago() {
    let mut game = ceruledge_after_a_knock_out_by_an_attack();
    end_turn(&mut game, 0);
    end_turn(&mut game, 1);
    assert_eq!(game.get_state_clone().current_player, 0);

    attack(&mut game, CardId::C1028Ceruledge);
    assert_eq!(game.get_state_clone().get_active(1).get_remaining_hp(), 110);
}

/// A Knock Out that is not by damage from an attack does not count: player 0's Poisoned Snorlax
/// (10 HP left) is Knocked Out at the Pokémon Checkup that ends player 1's turn, and Rally Back
/// does its printed 70.
#[test]
fn test_ceruledge_rally_back_ignores_a_knock_out_by_poison() {
    let mut game = get_initialized_game_with_board(
        0,
        1,
        4,
        vec![
            PlayedCard::from_id(CardId::A1211Snorlax)
                .with_remaining_hp(10)
                .with_status_condition(StatusCondition::Poisoned),
            ready_ceruledge(),
        ],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );
    end_turn(&mut game, 1);

    let state = game.get_state_clone();
    assert_eq!(state.current_player, 0);
    assert_eq!(state.points, [0, 1], "the Poison Knock Out scored for player 1");
    assert_eq!(state.get_active(0).get_name(), "Ceruledge");

    attack(&mut game, CardId::C1028Ceruledge);
    assert_eq!(game.get_state_clone().get_active(1).get_remaining_hp(), 110);
}

/// The printings R8-04a maps, the alt-art Venusaur and Ceruledge and Charizard's two
/// (charizard_flame_aura_test.rs) included: each is Complete, with no known limitation.
#[test]
fn test_mapped_c1_printings_report_complete() {
    for id in [
        CardId::C1003Venusaur,
        CardId::C1132Venusaur,
        CardId::C1010Sawsbuck,
        CardId::C1012Amoonguss,
        CardId::C1018Charizard,
        CardId::C1136Charizard,
        CardId::C1019Volcanion,
        CardId::C1028Ceruledge,
        CardId::C1138Ceruledge,
    ] {
        assert_eq!(
            get_implementation_status(id),
            ImplementationStatus::Complete,
            "{id:?}"
        );
        assert!(implementation_limitations(id).is_empty(), "{id:?}");
    }
}
