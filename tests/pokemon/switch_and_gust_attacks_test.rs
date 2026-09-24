use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board, get_test_game_with_board},
    Game, State,
};

// =================================================================================================
// Tapu Koko (A3 068 / A3 166) "Volt Switch": 70 damage, then "Switch this Pokémon with 1 of your
// Benched [L] Pokémon."
// =================================================================================================

fn volt_switch_game(card_id: CardId, own_bench: Vec<PlayedCard>) -> Game<'static> {
    let mut own_board = vec![PlayedCard::from_id(card_id).with_energy(vec![
        EnergyType::Lightning,
        EnergyType::Lightning,
        EnergyType::Lightning,
    ])];
    own_board.extend(own_bench);

    let mut game = get_test_game_with_board(
        own_board,
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(card_id, 0),
        is_stack: false,
    });
    game
}

#[test]
fn test_volt_switch_only_offers_lightning_benched_pokemon() {
    let mut game = volt_switch_game(
        CardId::A3068TapuKoko,
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::B2052Plusle),
        ],
    );

    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0);
    assert_eq!(
        choices.len(),
        1,
        "only the Lightning Plusle on bench slot 2 should be switchable"
    );
    assert!(matches!(
        choices[0].action,
        SimpleAction::Activate {
            player: 0,
            in_play_idx: 2
        }
    ));

    game.apply_action(&choices[0].clone());
    let state = game.get_state_clone();
    assert_eq!(state.get_active(0).get_name(), "Plusle");
    assert_eq!(
        state.in_play_pokemon[0][2].as_ref().unwrap().get_name(),
        "Tapu Koko"
    );
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        110,
        "Volt Switch still does its printed 70"
    );
}

/// Negative case: with no Benched [L] Pokémon at all, there is nothing to switch to and the attack
/// is just its printed damage.
#[test]
fn test_volt_switch_offers_nothing_without_a_lightning_bench() {
    let game = volt_switch_game(
        CardId::A3166TapuKoko,
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    let state = game.get_state_clone();
    assert_eq!(state.get_active(0).get_name(), "Tapu Koko");
    assert_eq!(state.get_active(1).get_remaining_hp(), 110);
    let (_, choices) = state.generate_possible_actions();
    assert!(
        !choices
            .iter()
            .any(|choice| matches!(choice.action, SimpleAction::Activate { .. })),
        "no Activate choices should be offered without a Benched [L] Pokémon"
    );
}

// =================================================================================================
// Eldegoss (B2 016) "Float Up" and Dunsparce (B3 130) "Bop 'n' Burrow": "You may shuffle this
// Pokémon and all attached cards into your deck."
// =================================================================================================

fn float_up_game(card_id: CardId, energy: Vec<EnergyType>) -> Game<'static> {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(card_id).with_energy(energy),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(card_id, 0),
        is_stack: false,
    });
    game
}

#[test]
fn test_float_up_can_shuffle_the_attacker_back_into_the_deck() {
    let mut game = float_up_game(CardId::B2016Eldegoss, vec![EnergyType::Grass]);

    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0);
    assert_eq!(
        choices.len(),
        2,
        "the effect is optional, so Noop is offered"
    );

    let shuffle = choices
        .iter()
        .find(|choice| {
            matches!(
                choice.action,
                SimpleAction::ShuffleInPlayPokemonIntoDeck { in_play_idx: 0 }
            )
        })
        .expect("shuffling the attacker into the deck should be an option")
        .clone();
    game.apply_action(&shuffle);

    // Finish the attack reaction before promoting. This keeps a removed attacker from being
    // confused with its eventual replacement in the Active Spot.
    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0);
    let reaction = choices
        .iter()
        .find(|choice| matches!(choice.action, SimpleAction::ResolveAttackRetaliation { .. }))
        .expect("attack retaliation should precede promotion")
        .clone();
    game.apply_action(&reaction);

    // The empty Active Spot then triggers a promotion from the Bench.
    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0);
    let promotion = choices
        .iter()
        .find(|choice| matches!(choice.action, SimpleAction::Promote { .. }))
        .expect("the benched Pokémon should be offered for promotion")
        .clone();
    game.apply_action(&promotion);

    let state = game.get_state_clone();
    assert_eq!(state.get_active(0).get_name(), "Bulbasaur");
    assert!(
        state.decks[0]
            .cards
            .iter()
            .any(|card| card.get_name() == "Eldegoss"),
        "Eldegoss should be back in its owner's deck"
    );
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        140,
        "Float Up still does its printed 40"
    );
}

/// Negative case: declining leaves the attacker exactly where it was.
#[test]
fn test_bop_n_burrow_can_be_declined() {
    let mut game = float_up_game(CardId::B3130Dunsparce, vec![EnergyType::Colorless]);

    let (_, choices) = game.get_state_clone().generate_possible_actions();
    let decline = choices
        .iter()
        .find(|choice| matches!(choice.action, SimpleAction::Noop))
        .expect("declining should be an option")
        .clone();
    game.apply_action(&decline);

    let state = game.get_state_clone();
    assert_eq!(state.get_active(0).get_name(), "Dunsparce");
    assert!(!state.decks[0]
        .cards
        .iter()
        .any(|card| card.get_name() == "Dunsparce"));
}

// =================================================================================================
// Fan Rotom (A2 142) "Spin Storm": "Flip a coin. If heads, put your opponent's Active Pokémon into
// their hand."
// =================================================================================================

fn spin_storm(seed: u64) -> State {
    let mut game = get_initialized_game_with_board(
        seed,
        0,
        3,
        vec![PlayedCard::from_id(CardId::A2142FanRotom)
            .with_energy(vec![EnergyType::Colorless, EnergyType::Colorless])],
        vec![
            PlayedCard::from_id(CardId::PB024MegaLatiosEx).with_energy(vec![EnergyType::Psychic]),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A2142FanRotom, 0),
        is_stack: false,
    });

    // A successful bounce leaves the opponent with a promotion to make.
    while !game.get_state_clone().move_generation_stack.is_empty() {
        let (_, choices) = game.get_state_clone().generate_possible_actions();
        game.apply_action(&choices[0].clone());
    }

    game.get_state_clone()
}

#[test]
fn test_spin_storm_returns_the_opponents_active_to_their_hand_on_heads() {
    let heads = (0..40)
        .map(spin_storm)
        .find(|state| {
            state.hands[1]
                .iter()
                .any(|card| card.get_name() == "Mega Latios ex")
        })
        .expect("heads should come up within 40 seeds");

    assert_eq!(
        heads.get_active(1).get_name(),
        "Charmander",
        "the opponent should have promoted from their Bench"
    );
    assert_eq!(
        heads.points[0], 0,
        "bouncing a Pokémon is not a knockout and scores nothing"
    );
    assert_eq!(
        heads.discard_energies[1],
        vec![EnergyType::Psychic],
        "the Energy attached to the bounced Pokémon is lost"
    );
}

/// Negative case: on tails the board is untouched.
#[test]
fn test_spin_storm_does_nothing_on_tails() {
    let tails = (0..40)
        .map(spin_storm)
        .find(|state| state.get_active(1).get_name() == "Mega Latios ex")
        .expect("tails should come up within 40 seeds");

    assert_eq!(tails.get_active(1).get_remaining_hp(), 180);
    assert!(tails.hands[1]
        .iter()
        .all(|card| card.get_name() != "Mega Latios ex"));
}

// =================================================================================================
// Chinchou (P-A 095) "Luring Glow": "Flip a coin. If heads, switch in 1 of your opponent's Benched
// Pokémon to the Active Spot." and Sandy Shocks (B3a 035) "Pull In and Pound": the same switch,
// followed by 50 damage to whoever ends up in the Active Spot.
// =================================================================================================

#[test]
fn test_luring_glow_lets_the_attacker_choose_the_new_active_on_heads() {
    let mut switched = 0;
    let mut untouched = 0;

    for seed in 0..40 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![
                PlayedCard::from_id(CardId::PA095Chinchou).with_energy(vec![EnergyType::Lightning])
            ],
            vec![
                PlayedCard::from_id(CardId::PB024MegaLatiosEx),
                PlayedCard::from_id(CardId::A1033Charmander),
            ],
        );
        game.apply_action(&Action {
            actor: 0,
            action: attack_action(CardId::PA095Chinchou, 0),
            is_stack: false,
        });

        let (actor, choices) = game.get_state_clone().generate_possible_actions();
        if choices
            .iter()
            .any(|choice| matches!(choice.action, SimpleAction::Activate { player: 1, .. }))
        {
            assert_eq!(
                actor, 0,
                "the *attacking* player picks the new Active Pokémon"
            );
            game.apply_action(&choices[0].clone());
            assert_eq!(
                game.get_state_clone().get_active(1).get_name(),
                "Charmander"
            );
            switched += 1;
        } else {
            assert_eq!(
                game.get_state_clone().get_active(1).get_name(),
                "Mega Latios ex"
            );
            untouched += 1;
        }
    }

    assert!(switched > 0, "Luring Glow never came up heads in 40 seeds");
    assert!(
        untouched > 0,
        "Luring Glow always came up heads in 40 seeds"
    );
}

#[test]
fn test_pull_in_and_pound_damages_the_newly_promoted_pokemon() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::B3a035SandyShocks).with_energy(vec![
                EnergyType::Fighting,
                EnergyType::Fighting,
                EnergyType::Colorless,
            ]),
        ],
        vec![
            PlayedCard::from_id(CardId::PB024MegaLatiosEx),
            PlayedCard::from_id(CardId::A1211Snorlax),
        ],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3a035SandyShocks, 0),
        is_stack: false,
    });

    // First the attacker picks who to drag into the Active Spot...
    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0);
    assert!(choices
        .iter()
        .all(|choice| matches!(choice.action, SimpleAction::Activate { player: 1, .. })));
    game.apply_action(&choices[0].clone());

    // ...then the 50 damage lands on whoever ended up there.
    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0);
    assert!(matches!(
        choices[0].action,
        SimpleAction::ApplyDamage { .. }
    ));
    game.apply_action(&choices[0].clone());

    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_name(), "Snorlax");
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        80,
        "Snorlax (150 HP, weak to Fighting) should take 50 + 20 once it is Active"
    );
    assert_eq!(
        state.in_play_pokemon[1][1].as_ref().unwrap().get_name(),
        "Mega Latios ex"
    );
    assert_eq!(
        state.in_play_pokemon[1][1]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        180,
        "the Pokémon that was switched out should take nothing"
    );
}

/// Negative case: "If you do" fails when the opponent has no Bench, so no damage is dealt at all.
#[test]
fn test_pull_in_and_pound_does_nothing_without_an_opponent_bench() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::B3a035SandyShocks).with_energy(vec![
                EnergyType::Fighting,
                EnergyType::Fighting,
                EnergyType::Colorless,
            ]),
        ],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3a035SandyShocks, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        180,
        "with nothing to switch in, Pull In and Pound does no damage"
    );
}
