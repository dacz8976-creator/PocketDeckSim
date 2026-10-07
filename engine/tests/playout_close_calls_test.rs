//! Adaptive play-outs for close calls (Oct 7; Fable via Dustin; rl/results/playout_close_calls_2026-10-07/README.md):
//! `_m<R_max>`. After the R rounds, when a candidate is within z standard errors of the best one (paired), the best, every
//! such candidate and km3's move are played out in blocks of 16 more rounds, from the same worlds and seeds a larger R
//! would use (the common random numbers extended), until no candidate is within the noise of the best or R_max rounds are
//! played; the decision is then made among the candidates still in play. Candidates identical in every round so far are
//! not a close call. Written before the code:
//! - the code spells the parameter, and refuses an R_max not above R or a time budget with it;
//! - a decision without a close call is the decision without the parameter, field for field;
//! - an extended candidate's play-outs are exactly those of a plain run with as many rounds (the same worlds and seeds);
//!   a candidate left out of the extension keeps its R rounds, as without the parameter;
//! - km3's move and the best candidate after R rounds are always among the extended ones, the reason says how many rounds
//!   were played for how many candidates, and the choice is one of them.
use std::collections::BTreeSet;

use deckgym::actions::Action;
use deckgym::observation::{PlayerObservation, RevealedKnowledge};
use deckgym::players::playout_player::{DecisionReport, Knowledge, PlayoutParams, PlayoutPlayer};
use deckgym::players::{create_players, parse_player_code};
use deckgym::test_support::load_test_decks;
use deckgym::{Game, State};
use rand::{rngs::StdRng, SeedableRng};

/// Every field of a decision's report but its time, as text.
fn fingerprint(r: &DecisionReport) -> String {
    let candidates: Vec<String> =
        r.candidates.iter().map(|c| format!("{:?} {} {} {} {} {}", c.action, c.score, c.diff, c.se, c.attacks_this_turn, c.rounds)).collect();
    format!("{:?} | km {} chosen {} | {} | rounds {} failed {}", candidates, r.km3, r.chosen, r.reason, r.rounds, r.failed_rounds)
}

/// The code spells the extension (`_m<R_max>`, last), and every code without it is as before.
#[test]
fn the_code_spells_the_extension() {
    assert_eq!(PlayoutParams::new(3).max_rounds, None);
    let p = PlayoutParams::parse("3_m64").unwrap();
    assert_eq!(p.max_rounds, Some(64));
    assert_eq!(p.code(), "kx3_r16_c12_z2_real_t0_poolwide_m64");
    assert_eq!(PlayoutParams::parse(&p.code()[2..]).unwrap(), p);
    let more = PlayoutParams::parse("3_r16_c12_z2_real_t0_poolmeta_zs3_m48").unwrap();
    assert_eq!(more.code(), "kx3_r16_c12_z2_real_t0_poolmeta_zs3_m48");
    for bad in ["kx3_m", "kx3_mx", "kx3_m16", "kx3_r16_m8", "kx3_r32_m32", "kx3_t30_m64"] {
        assert!(parse_player_code(bad).is_err(), "{bad} should not parse");
    }
    assert!(parse_player_code("kx3_r8_m20").is_ok());
}

/// Decisions of player 0 from turn 3 on with at least three distinct moves, one per game: km3 plays test-deck games from
/// the seeds given.
fn decisions(seeds: &[u64]) -> Vec<(u64, State)> {
    let km3 = || parse_player_code("km3").unwrap();
    let mut out = Vec::new();
    for &seed in seeds {
        let (deck_a, deck_b) = load_test_decks();
        let mut game = Game::new(create_players(deck_a, deck_b, vec![km3(), km3()]), seed);
        while !game.is_game_over() {
            let state = game.get_state_clone();
            let (actor, actions) = state.generate_possible_actions();
            let distinct: BTreeSet<String> = actions.iter().map(|a| format!("{:?}", a.action)).collect();
            if actor == 0 && state.turn_count >= 3 && distinct.len() >= 3 {
                out.push((seed, state));
                break;
            }
            game.play_tick();
        }
    }
    out
}

fn pilot(rollouts: usize, max_rounds: Option<usize>) -> PlayoutPlayer {
    let (deck_a, deck_b) = load_test_decks();
    let params = PlayoutParams { rollouts, cap: 6, z: 2.0, max_rounds, knowledge: Knowledge::Lab, ..PlayoutParams::new(3) };
    PlayoutPlayer::with_extra_lists(deck_a, deck_b, params, Vec::new())
}

fn decide(p: &mut PlayoutPlayer, seed: u64, state: &State) -> DecisionReport {
    let observation = PlayerObservation::from_state(state, 0, &RevealedKnowledge::default());
    let actions: Vec<Action> = state.generate_possible_actions().1;
    p.evaluate(&mut StdRng::seed_from_u64(seed), &observation, &actions)
}

const SEEDS: [u64; 8] = [
    20_000_000_240, 20_000_000_241, 20_000_000_242, 20_000_000_243, 20_000_000_244, 20_000_000_245, 20_000_000_246,
    20_000_000_247,
];

/// With R = 4 and R_max = 20: a decision without a close call is the plain decision field for field; with one, km3's move
/// and the best after 4 rounds are extended to 20 rounds, each extended candidate's play-outs are a plain 20-round run's
/// (scores, and differences from km3's move, alike), the others keep their 4 rounds as in the plain run, the reason says so,
/// and the choice is an extended candidate. Both kinds of decision come up.
#[test]
fn close_calls_are_played_out_further_on_the_same_worlds() {
    let (mut extended, mut clear) = (0, 0);
    for (seed, state) in decisions(&SEEDS) {
        let plain = decide(&mut pilot(4, None), seed, &state);
        let ext = decide(&mut pilot(4, Some(20)), seed, &state);
        assert_eq!(plain.failed_rounds + ext.failed_rounds, 0, "seed {seed}");
        let moves = |r: &DecisionReport| r.candidates.iter().map(|c| c.action.clone()).collect::<Vec<_>>();
        assert_eq!(moves(&plain), moves(&ext), "seed {seed}: the same candidates");
        if ext.candidates.iter().all(|c| c.rounds == 4) {
            clear += 1;
            assert_eq!(fingerprint(&plain), fingerprint(&ext), "seed {seed}: no close call, the plain decision");
            continue;
        }
        extended += 1;
        let full = decide(&mut pilot(20, None), seed, &state);
        let best4 = (0..plain.candidates.len()).fold(0, |b, c| if plain.candidates[c].score > plain.candidates[b].score { c } else { b });
        assert_eq!(ext.candidates[ext.km3].rounds, 20, "seed {seed}: km3's move extended");
        assert_eq!(ext.candidates[best4].rounds, 20, "seed {seed}: the best after 4 rounds extended");
        for (c, e) in ext.candidates.iter().enumerate() {
            match e.rounds {
                20 => {
                    assert_eq!(e.score, full.candidates[c].score, "seed {seed}: {} on the same 20 worlds", e.label);
                    assert_eq!(e.diff, full.candidates[c].diff, "seed {seed}: {}", e.label);
                    assert_eq!(e.attacks_this_turn, full.candidates[c].attacks_this_turn, "seed {seed}: {}", e.label);
                }
                4 => {
                    assert_eq!(e.score, plain.candidates[c].score, "seed {seed}: {} keeps its 4 rounds", e.label);
                    assert_eq!(e.diff, plain.candidates[c].diff, "seed {seed}: {}", e.label);
                }
                n => panic!("seed {seed}: {} played {n} rounds", e.label),
            }
        }
        assert_eq!(ext.candidates[ext.chosen].rounds, 20, "seed {seed}: the choice is an extended candidate");
        let n = ext.candidates.iter().filter(|c| c.rounds == 20).count();
        assert!(ext.reason.contains(&format!("close call: play-outs extended from 4 to 20 rounds for {n} candidates")), "seed {seed}: {}", ext.reason);
        assert_eq!(ext.rounds, 20, "seed {seed}");
    }
    eprintln!("decisions: {extended} extended, {clear} without a close call");
    assert!(extended >= 1 && clear >= 1, "{extended} extended, {clear} without a close call");
}

/// The extension goes in blocks of 16 and drops a candidate once the best leads it beyond the noise: with R_max = 68 every
/// candidate has played 4 rounds and then a whole number of blocks; km3's move and the choice have played the most; and
/// the decision is deterministic.
#[test]
fn the_extension_goes_in_blocks_of_16_and_is_deterministic() {
    for (seed, state) in decisions(&SEEDS[..4]) {
        let a = decide(&mut pilot(4, Some(68)), seed, &state);
        let b = decide(&mut pilot(4, Some(68)), seed, &state);
        assert_eq!(fingerprint(&a), fingerprint(&b), "seed {seed}");
        for c in &a.candidates {
            assert!([4, 20, 36, 52, 68].contains(&c.rounds), "seed {seed}: {} played {} rounds", c.label, c.rounds);
        }
        assert_eq!(a.candidates[a.km3].rounds, a.rounds, "seed {seed}");
        assert_eq!(a.candidates[a.chosen].rounds, a.rounds, "seed {seed}");
    }
}
