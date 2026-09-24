use deckgym::{
    actions::Action,
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
};

/// Builds a board where player 0's Raichu is about to knock out player 1's Glimmora, runs the
/// attack, and returns `(points_scored_by_player_0, glimmora_still_in_play)`.
fn knock_out_glimmora(seed: u64) -> (u8, bool) {
    let mut game = get_initialized_game_with_board(
        seed,
        0,
        3,
        vec![
            PlayedCard::from_id(CardId::A1095Raichu).with_energy(vec![
                EnergyType::Lightning,
                EnergyType::Lightning,
                EnergyType::Lightning,
            ]),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
        vec![
            // 10 HP left: any attack finishes it, so the point-denial coin always gets flipped.
            PlayedCard::from_id(CardId::B3a045Glimmora).with_remaining_hp(10),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A1095Raichu, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    (state.points[0], state.in_play_pokemon[1][0].is_some())
}

/// Glimmora (B3a 045) "Shattering Crystal": when it is Knocked Out, flip a coin; if heads, the
/// opponent gets no points for it.
///
/// The knockout itself is never prevented — only the score is. This is what separates it from
/// Ursaluna's Guts, which stops the knockout outright.
#[test]
fn test_glimmora_is_always_knocked_out_regardless_of_the_coin() {
    for seed in 0..12 {
        let (_, still_in_play) = knock_out_glimmora(seed);
        assert!(
            !still_in_play,
            "seed {seed}: Shattering Crystal denies points, it must never prevent the knockout"
        );
    }
}

/// Across enough seeds both sides of the coin must show up: sometimes the opponent scores the
/// point, sometimes it is denied. A one-sided result means the coin is not being flipped.
#[test]
fn test_glimmora_point_denial_produces_both_outcomes() {
    let mut denied = 0;
    let mut scored = 0;

    for seed in 0..40 {
        let (points, _) = knock_out_glimmora(seed);
        match points {
            0 => denied += 1,
            1 => scored += 1,
            other => panic!("seed {seed}: unexpected point total {other} for a non-ex knockout"),
        }
    }

    assert!(
        denied > 0,
        "never denied a point in 40 seeds — the Shattering Crystal coin is not firing"
    );
    assert!(
        scored > 0,
        "never scored a point in 40 seeds — points are being denied unconditionally"
    );
}
