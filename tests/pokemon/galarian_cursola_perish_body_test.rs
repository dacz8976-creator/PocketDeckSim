use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
    State,
};

/// Player 0's Pikachu uses Gnaw (20 damage) on player 1's Galarian Cursola, which is left with
/// `cursola_hp` HP. Both players keep a Benched Pokémon so that neither knockout ends the game.
fn gnaw_galarian_cursola(seed: u64, cursola_hp: u32) -> State {
    let mut game = get_initialized_game_with_board(
        seed,
        0,
        3,
        vec![
            PlayedCard::from_id(CardId::A1094Pikachu).with_energy(vec![EnergyType::Lightning]),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
        vec![
            PlayedCard::from_id(CardId::A4a035GalarianCursola).with_remaining_hp(cursola_hp),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A1094Pikachu, 0),
        is_stack: false,
    });

    game.get_state_clone()
}

/// Galarian Cursola (A4a 035) "Perish Body": "If this Pokémon is in the Active Spot and is Knocked
/// Out by damage from an attack from your opponent's Pokémon, flip a coin. If heads, the Attacking
/// Pokémon is Knocked Out."
///
/// The coin never saves Cursola — it only decides whether the attacker goes down with it.
#[test]
fn test_perish_body_flips_a_real_coin_for_the_attacker() {
    let mut attacker_knocked_out = 0;
    let mut attacker_survived = 0;

    for seed in 0..40 {
        let state = gnaw_galarian_cursola(seed, 20);
        assert!(
            state.in_play_pokemon[1][0].is_none(),
            "seed {seed}: Perish Body must never prevent Cursola's own knockout"
        );
        if state.in_play_pokemon[0][0].is_none() {
            attacker_knocked_out += 1;
        } else {
            attacker_survived += 1;
        }
    }

    assert!(
        attacker_knocked_out > 0,
        "the Attacking Pokémon was never Knocked Out in 40 seeds — the Perish Body coin is not firing"
    );
    assert!(
        attacker_survived > 0,
        "the Attacking Pokémon was always Knocked Out in 40 seeds — the coin is not being flipped"
    );
}

/// A Perish Body heads is a double knockout: each player scores their own point, both Active Spots
/// empty out, and both players are asked to promote.
#[test]
fn test_perish_body_double_knockout_awards_both_players_a_point() {
    let heads = (0..40)
        .map(|seed| gnaw_galarian_cursola(seed, 20))
        .find(|state| state.in_play_pokemon[0][0].is_none())
        .expect("some seed should flip heads");

    assert_eq!(
        heads.points[0], 1,
        "player 0 should still score the point for knocking out Cursola"
    );
    assert_eq!(
        heads.points[1], 1,
        "player 1 should score the point for the Attacking Pokémon that Perish Body knocked out"
    );
    assert!(heads.winner.is_none(), "neither player is at 3 points yet");

    for player in 0..2 {
        assert!(
            heads.in_play_pokemon[player][0].is_none(),
            "player {player}'s Active Spot should be empty after the double knockout"
        );
    }
}

/// Negative test: Perish Body is conditioned on Cursola actually being Knocked Out. At full HP
/// Gnaw is not lethal, so no coin is flipped and the attacker is never in danger.
#[test]
fn test_perish_body_does_not_fire_on_non_lethal_damage() {
    for seed in 0..40 {
        let state = gnaw_galarian_cursola(seed, 80);
        assert_eq!(
            state.in_play_pokemon[1][0]
                .as_ref()
                .expect("Cursola survives a non-lethal Gnaw")
                .get_remaining_hp(),
            60
        );
        assert!(
            state.in_play_pokemon[0][0].is_some(),
            "seed {seed}: a surviving Cursola must not knock out the attacker"
        );
        assert_eq!(state.points[1], 0, "seed {seed}");
    }
}

/// Negative test: the knockout has to come from "damage from an attack". A Cursola that faints to
/// Poison during Pokémon Checkup takes nobody with it.
#[test]
fn test_perish_body_does_not_fire_on_a_non_attack_knockout() {
    for seed in 0..8 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![
                PlayedCard::from_id(CardId::A1094Pikachu),
                PlayedCard::from_id(CardId::A1001Bulbasaur),
            ],
            vec![
                PlayedCard::from_id(CardId::A4a035GalarianCursola).with_remaining_hp(10),
                PlayedCard::from_id(CardId::A1033Charmander),
            ],
        );

        let mut state = game.get_state_clone();
        state.apply_status_condition(1, 0, deckgym::models::StatusCondition::Poisoned);
        game.set_state(state);

        game.apply_action(&Action {
            actor: 0,
            action: SimpleAction::EndTurn,
            is_stack: false,
        });

        let state = game.get_state_clone();
        assert!(
            state.in_play_pokemon[1][0].is_none(),
            "seed {seed}: Poison should have knocked Cursola out"
        );
        assert!(
            state.in_play_pokemon[0][0].is_some(),
            "seed {seed}: a Poison knockout is not an attack, so Perish Body must not fire"
        );
        assert_eq!(state.points[1], 0, "seed {seed}");
    }
}

/// Perish Body is passive — it is never offered as a `UseAbility` action.
#[test]
fn test_perish_body_is_passive() {
    let game = get_initialized_game_with_board(
        0,
        1,
        3,
        vec![PlayedCard::from_id(CardId::A1094Pikachu)],
        vec![PlayedCard::from_id(CardId::A4a035GalarianCursola)],
    );

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    assert!(!actions
        .iter()
        .any(|a| matches!(a.action, SimpleAction::UseAbility { .. })));
}
