//! Adaptive play-outs for close calls (Oct 7; Fable via Dustin; rl/results/playout_close_calls_2026-10-07/README.md):
//! `_m<R_max>`. After the R rounds, when the decision is a close call, the best candidate, every candidate close to it and
//! km3's move play out rounds R to R_max, from the same worlds and seeds a larger R would use (the common random numbers
//! extended), and the decision is made at the end, among them, on their rounds; the others keep their R rounds. Written
//! before the code:
//! - the code spells the parameter, and refuses an R_max not above R or a time budget with it;
//! - a decision without a close call is the decision without the parameter, field for field;
//! - an extended candidate's play-outs are exactly those of a plain run with as many rounds (the same worlds and seeds);
//!   a candidate left out of the extension keeps its R rounds, as without the parameter;
//! - km3's move and the best candidate after R rounds are always among the extended ones, the reason says how many rounds
//!   were played for how many candidates, and the choice is one of them.
//!
//! Combined with the skip bar (Oct 7; Fable via Dustin, from the laptop's review of 7d3639d0; written before the fix):
//! - (a) closeness is tested against the bar that will decide: km3's move is close to a best that is another move when
//!   the best's lead is within the bar for that switch (z_skip from km3's attack to a line that skips it, `_zs<z>`;
//!   z_attack with `_za<z>`; else z), whatever the other candidates do; any other move is close when the best leads it
//!   by no more than z standard errors;
//! - (b) the extended candidates all play to R_max and the decision is made once, at the end: no stop at the first block
//!   where the best clears the bar, and no candidate dropped on the way;
//! - (c) dropped (the Oct 7 addendum, Fable via Dustin): a move tied with km3's in every round so far is extended like
//!   any other move close to the best, since rare draws or events can separate them later; a move tied with km3's through
//!   16 rounds is extended and wins at R_max (B-210952-t16);
//! - `_tools _zs3 _m64` together: at km3's attacks the extension and the skip bar act as above; at a Tool placement the
//!   Tool tie-break comes after the extension's decision and looks at every candidate, so it may play a placement left at
//!   R rounds.
use std::cell::Cell;
use std::collections::BTreeSet;
use std::rc::Rc;

use deckgym::actions::{Action, SimpleAction};
use deckgym::observation::{PlayerObservation, RevealedKnowledge};
use deckgym::players::playout_player::{
    close_call, skip_bar, tie_break_placements, DecisionReport, Knowledge, PlayoutParams, PlayoutPlayer, ToolRulePlayer,
};
use deckgym::players::{create_players, parse_player_code, Player, PlayerCode};
use deckgym::test_support::load_test_decks;
use deckgym::{Deck, Game, State};
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
/// and the choice is an extended candidate; a move tied with km3's in each of the 4 rounds is extended whenever km3's move
/// is close to a best that is another move (the tied move is then exactly as close). Both kinds of decision come up.
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
        let lead4 = &plain.candidates[best4];
        for (c, p) in plain.candidates.iter().enumerate() {
            if c != plain.km3 && p.diff == 0.0 && p.se == 0.0 && best4 != plain.km3 && lead4.diff <= 2.0 * lead4.se {
                assert_eq!(ext.candidates[c].rounds, 20, "seed {seed}: {} ties km3's move in every round, extended as it is", p.label);
            }
        }
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

/// The extension isn't stopped early: with R = 4 and R_max = 40 (not 4 plus a whole number of blocks of 16) every
/// candidate has played 4 rounds or 40, km3's move and the choice 40 whenever there was a close call; the decision is the
/// usual rule on the extended candidates' 40 rounds (their best replaces km3's move only beyond z standard errors); and
/// it is deterministic.
#[test]
fn extended_candidates_play_to_r_max_and_the_decision_is_made_at_the_end() {
    let mut extended = 0;
    for (seed, state) in decisions(&SEEDS[..4]) {
        let a = decide(&mut pilot(4, Some(40)), seed, &state);
        let b = decide(&mut pilot(4, Some(40)), seed, &state);
        assert_eq!(fingerprint(&a), fingerprint(&b), "seed {seed}");
        assert_eq!(a.failed_rounds, 0, "seed {seed}");
        for c in &a.candidates {
            assert!([4, 40].contains(&c.rounds), "seed {seed}: {} played {} rounds", c.label, c.rounds);
        }
        if a.rounds == 4 {
            continue;
        }
        extended += 1;
        assert_eq!(a.rounds, 40, "seed {seed}");
        assert_eq!(a.candidates[a.km3].rounds, 40, "seed {seed}");
        assert_eq!(a.candidates[a.chosen].rounds, 40, "seed {seed}");
        let best = (0..a.candidates.len())
            .filter(|&c| a.candidates[c].rounds == 40)
            .fold(a.km3, |b, c| if a.candidates[c].score > a.candidates[b].score { c } else { b });
        let lead = &a.candidates[best];
        let switch = best != a.km3 && lead.diff > 0.0 && lead.diff > 2.0 * lead.se;
        assert_eq!(a.chosen, if switch { best } else { a.km3 }, "seed {seed}: {}", a.reason);
    }
    eprintln!("decisions extended: {extended} of 4");
    assert!(extended >= 1, "no close call among these decisions");
}

// (a), and the dropped (c), on rounds given directly.

fn is_attack(a: &Action) -> bool {
    matches!(a.action, SimpleAction::Attack(_))
}

/// An attack of the test decks (the first that comes up in km3's game from seed 20,000,000,250), and three moves that
/// aren't attacks: End Turn, and retreats to Bench spots 1 and 2.
fn moves() -> (Action, Action, Action, Action) {
    let (deck_a, deck_b) = load_test_decks();
    let km3 = || parse_player_code("km3").unwrap();
    let mut game = Game::new(create_players(deck_a, deck_b, vec![km3(), km3()]), 20_000_000_250);
    let mut attack = None;
    while attack.is_none() && !game.is_game_over() {
        let (_, actions) = game.get_state_clone().generate_possible_actions();
        attack = actions.iter().find(|a| is_attack(a)).cloned();
        game.play_tick();
    }
    let attack = attack.expect("an attack came up");
    let other = |action| Action { actor: attack.actor, action, is_stack: false };
    (attack.clone(), other(SimpleAction::EndTurn), other(SimpleAction::Retreat(1)), other(SimpleAction::Retreat(2)))
}

/// A candidate's rounds: its scores, and whether its line attacked this turn (the same in every round).
fn rounds(scores: &[f64], attacked: bool) -> Vec<(f64, bool)> {
    scores.iter().map(|&s| (s, attacked)).collect()
}

/// (a) km3's attack is close to a best whose line skips it when the best's lead is within the skip bar, not z: End Turn
/// leading km3's attack by 0.5 at 2.65 standard errors is a close call with `_zs3` (and with `_za3`), whatever a third
/// move does; it is clear with the bar z, and clear when the same lead is a line that attacks later in the turn or the
/// lead is past the skip bar (3.4 standard errors). Another move is close when the best leads it by no more than z
/// standard errors, with the skip bar or without.
#[test]
fn a_close_call_is_tested_against_the_bar_that_decides() {
    let (attack, end, retreat1, retreat2) = moves();
    let z = PlayoutParams { z: 2.0, ..PlayoutParams::new(3) };
    let zs = PlayoutParams { z_skip: Some(3.0), ..z.clone() };
    let za = PlayoutParams { z_attack: Some(3.0), ..z.clone() };
    let none: Vec<usize> = Vec::new();
    let km = rounds(&[0.0; 8], true);
    let lead = [1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0];
    let two = vec![attack.clone(), end.clone()];
    let skip = vec![km.clone(), rounds(&lead, false)];
    assert_eq!(close_call(&skip, &two, &zs), vec![0, 1], "2.65 standard errors, within the skip bar 3: a close call");
    assert_eq!(close_call(&skip, &two, &za), vec![0, 1], "within the attack bar 3: a close call");
    assert_eq!(close_call(&skip, &two, &z), none, "past z 2, the bar without them: clear");
    let later = vec![attack.clone(), retreat1.clone()];
    assert_eq!(close_call(&vec![km.clone(), rounds(&lead, true)], &later, &zs), none, "a line that attacks later: the bar is z");
    let past = [1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0];
    assert_eq!(close_call(&vec![km.clone(), rounds(&past, false)], &two, &zs), none, "3.4 standard errors, past the skip bar");
    // A third move the best leads by 2.05 standard errors isn't close, and changes nothing.
    let three = vec![attack.clone(), end.clone(), retreat2.clone()];
    let far = vec![km.clone(), rounds(&lead, false), rounds(&[0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0], true)];
    assert_eq!(close_call(&far, &three, &zs), vec![0, 1], "km3's attack and the best, for themselves");
    assert_eq!(close_call(&far, &three, &z), none);
    // A third move the best leads by 1 standard error is close, with the skip bar or without.
    let near = vec![km.clone(), rounds(&lead, false), rounds(&[1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0], true)];
    assert_eq!(close_call(&near, &three, &z), vec![0, 1, 2]);
    assert_eq!(close_call(&near, &three, &zs), vec![0, 1, 2]);
}

/// (c) dropped: a move tied with km3's in every round is extended, as close to the best as km3's move is; a move equal to
/// the best in every round is no close call (as in the first version).
#[test]
fn a_move_tied_with_km3s_in_every_round_is_still_extended() {
    let (attack, end, retreat1, retreat2) = moves();
    let z = PlayoutParams { z: 2.0, ..PlayoutParams::new(3) };
    let km = [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0];
    let per = vec![rounds(&km, false), rounds(&[1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], false), rounds(&km, true)];
    let candidates = vec![end.clone(), retreat1.clone(), attack.clone()];
    assert_eq!(close_call(&per, &candidates, &z), vec![0, 1, 2], "the best leads both by 1 standard error; the attack, tied with km3's move, too");
    let lead = [1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0];
    let per = vec![rounds(&[0.0; 8], false), rounds(&lead, false), rounds(&lead, false)];
    assert_eq!(close_call(&per, &[end, retreat1, retreat2], &z), Vec::<usize>::new(), "equal to the best: no close call");
}

/// (c) dropped: a move tied with km3's through the first 16 rounds is extended and can win at R_max. The continuation
/// position B-210952-t16 (Shark tempo v Blastoise-Wailord, the position's seed 24,200,001,005), with `_tools _zs3` (LAB,
/// cap 12, z 2): after 16 rounds km3's bench of the Alolan Vulpix and nine other moves score 0 in every round, and Binding
/// Snow leads by +0.094 (1.9 standard errors). The turn's Water to the Active is one of the tied moves. With R_max 64 it
/// is extended with the rest, leads km3's move over the 64 rounds by +0.125 (3.0 standard errors), more than Binding
/// Snow, and is played.
#[test]
fn a_move_tied_with_km3s_through_16_rounds_is_extended_and_can_win() {
    let path = "../rl/results/playout_continuation_2026-10-05/states/B-210952-t16.json";
    let state: State = serde_json::from_str(&std::fs::read_to_string(path).unwrap()).unwrap();
    let (me, actions) = state.generate_possible_actions();
    let observation = PlayerObservation::from_state(&state, me, &RevealedKnowledge::default());
    let run = |max_rounds: Option<usize>| {
        let params = PlayoutParams {
            rollouts: 16,
            cap: 12,
            z: 2.0,
            knowledge: Knowledge::Lab,
            tools: true,
            z_skip: Some(3.0),
            max_rounds,
            ..PlayoutParams::new(3)
        };
        let (shark, blastoise) = (deck("../decks/brews/drafts_2026-10-01/draft-A-shark-tempo.txt"), deck("../decks/computer/blastoise-wailord-deluxe.txt"));
        PlayoutPlayer::with_extra_lists(shark, blastoise, params, Vec::new())
            .evaluate(&mut StdRng::seed_from_u64(24_200_001_005), &observation, &actions)
    };
    let r16 = run(None);
    let water = r16
        .candidates
        .iter()
        .position(|c| c.label.starts_with("Attach { attachments: [(1, Water, 0)], is_turn_energy: true"))
        .expect("the turn's Water to the Active is a candidate");
    let w = &r16.candidates[water];
    assert!(water != r16.km3 && w.diff == 0.0 && w.se == 0.0, "tied with km3's move in all 16 rounds: {} {} {}", w.label, w.diff, w.se);
    assert_eq!(r16.chosen, r16.km3, "{}", r16.reason);
    let ext = run(Some(64));
    assert_eq!(ext.failed_rounds, 0);
    assert_eq!(ext.candidates[water].rounds, 64, "the tied move is extended: {}", ext.reason);
    assert_eq!(ext.chosen, water, "and wins at R_max: {}", ext.reason);
    assert!(ext.reason.contains("close call: play-outs extended from 16 to 64 rounds"), "{}", ext.reason);
}

// `_tools _zs3 _m64` together.

/// Decisions where km3 proposes an attack among at least three distinct moves: km3 plays test-deck games from the seeds
/// given, and the first such decision of player 0 from turn 3 on is taken from each.
fn attack_decisions(seeds: &[u64]) -> Vec<(u64, State)> {
    let km3 = || parse_player_code("km3").unwrap();
    let mut out = Vec::new();
    for &seed in seeds {
        let (deck_a, deck_b) = load_test_decks();
        let mut game = Game::new(create_players(deck_a.clone(), deck_b.clone(), vec![km3(), km3()]), seed);
        let mut proposer = create_players(deck_a, deck_b, vec![km3(), km3()]).remove(0);
        while !game.is_game_over() {
            let state = game.get_state_clone();
            let (actor, actions) = state.generate_possible_actions();
            let distinct: BTreeSet<String> = actions.iter().map(|a| format!("{:?}", a.action)).collect();
            if actor == 0 && state.turn_count >= 3 && distinct.len() >= 3 && actions.iter().any(is_attack) {
                let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
                if is_attack(&proposer.decision_fn(&mut StdRng::seed_from_u64(seed), &observation, &actions)) {
                    out.push((seed, state));
                    break;
                }
            }
            game.play_tick();
        }
    }
    out
}

/// The combined code's pilot on the test decks, at a small R: LAB, cap 6, z 2, the Tool rule, the skip bar 3.
fn combined(rollouts: usize, max_rounds: Option<usize>) -> PlayoutPlayer {
    let (deck_a, deck_b) = load_test_decks();
    let params = PlayoutParams {
        rollouts,
        cap: 6,
        z: 2.0,
        knowledge: Knowledge::Lab,
        tools: true,
        z_skip: Some(3.0),
        max_rounds,
        ..PlayoutParams::new(3)
    };
    PlayoutPlayer::with_extra_lists(deck_a, deck_b, params, Vec::new())
}

/// km3's attacks from seeds 20,000,000,301, 324, 325 and 266 (a scan of 250-329 with R = 8 before the fix found them): at
/// 301 and 324 the best after 8 rounds skips km3's attack (its line attacks this turn in 0 of 8 play-outs) with a lead of
/// 2.05 standard errors, past z 2 but within the skip bar 3 (the review's gap); at 325 the best attacks later in the turn
/// with the same lead, so it switches at z; at 266 End Turn leads by 1.5 standard errors.
const COMBINED_SEEDS: [u64; 4] = [20_000_000_301, 20_000_000_324, 20_000_000_325, 20_000_000_266];

/// `_tools _zs3 _m64` together at km3's attacks, with R = 8 and R_max = 64: the code spells all three; whenever the best
/// after 8 rounds leads km3's attack within the bar that decides (the skip bar for a line that skips the attack), km3's
/// attack and the best are extended, so the review's gap is extended at 301 and 324; a move tied with km3's in each of the
/// 8 rounds is extended whenever the best leads km3's attack by no more than z standard errors; every extended candidate
/// plays 64 rounds, the same worlds as a plain 64-round run; the decision is the
/// skip bar's on the extended candidates' 64 rounds; and without a close call it is the plain decision.
#[test]
fn the_tools_rule_the_skip_bar_and_close_calls_combine() {
    let code = PlayoutParams::parse("3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m64").unwrap();
    assert!(code.tools && code.z_skip == Some(3.0) && code.max_rounds == Some(64), "{code:?}");
    assert_eq!(code.code(), "kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m64");
    assert_eq!(PlayoutParams::parse(&code.code()[2..]).unwrap(), code);
    let (mut gaps, mut extended) = (0, 0);
    for (seed, state) in attack_decisions(&COMBINED_SEEDS) {
        let plain = decide(&mut combined(8, None), seed, &state);
        let comb = decide(&mut combined(8, Some(64)), seed, &state);
        assert_eq!(plain.failed_rounds + comb.failed_rounds, 0, "seed {seed}");
        assert!(is_attack(&plain.candidates[plain.km3].action), "seed {seed}: km3 proposes an attack");
        let moves = |r: &DecisionReport| r.candidates.iter().map(|c| c.action.clone()).collect::<Vec<_>>();
        assert_eq!(moves(&plain), moves(&comb), "seed {seed}: the same candidates");
        for c in &comb.candidates {
            assert!([8, 64].contains(&c.rounds), "seed {seed}: {} played {} rounds", c.label, c.rounds);
        }
        // (a) The best after 8 rounds, and the bar its switch would need.
        let best8 = (0..plain.candidates.len()).fold(plain.km3, |b, c| if plain.candidates[c].score > plain.candidates[b].score { c } else { b });
        let lead = &plain.candidates[best8];
        let bar8 = skip_bar(&plain.candidates[plain.km3].action, &lead.action, lead.attacks_this_turn, plain.rounds, 2.0, Some(3.0));
        if best8 != plain.km3 && lead.diff <= bar8 * lead.se {
            assert_eq!(comb.candidates[comb.km3].rounds, 64, "seed {seed}: km3's attack extended ({})", plain.reason);
            assert_eq!(comb.candidates[best8].rounds, 64, "seed {seed}: the best extended ({})", plain.reason);
            if lead.diff > 2.0 * lead.se {
                gaps += 1;
            }
        }
        // (c) dropped: a move tied with km3's attack is another move, close to the best at z.
        for (c, p) in plain.candidates.iter().enumerate() {
            if c != plain.km3 && p.diff == 0.0 && p.se == 0.0 && best8 != plain.km3 && lead.diff <= 2.0 * lead.se {
                assert_eq!(comb.candidates[c].rounds, 64, "seed {seed}: {} ties km3's attack in every round, extended", p.label);
            }
        }
        if comb.rounds == 8 {
            assert_eq!(fingerprint(&plain), fingerprint(&comb), "seed {seed}: no close call, the plain decision");
            continue;
        }
        extended += 1;
        // (b) Every extended candidate on the same 64 worlds as a plain run; the others keep their 8 rounds.
        let full = decide(&mut combined(64, None), seed, &state);
        for (c, e) in comb.candidates.iter().enumerate() {
            let (same, why) = if e.rounds == 64 { (&full.candidates[c], "the same 64 worlds") } else { (&plain.candidates[c], "its 8 rounds") };
            assert_eq!((e.score, e.diff, e.attacks_this_turn), (same.score, same.diff, same.attacks_this_turn), "seed {seed}: {} on {why}", e.label);
        }
        // The decision at the end: the skip bar on the extended candidates' 64 rounds.
        let live: Vec<usize> = (0..comb.candidates.len()).filter(|&c| comb.candidates[c].rounds == 64).collect();
        let best = live.iter().copied().fold(comb.km3, |b, c| if comb.candidates[c].score > comb.candidates[b].score { c } else { b });
        let l = &comb.candidates[best];
        let bar = skip_bar(&comb.candidates[comb.km3].action, &l.action, l.attacks_this_turn, l.rounds, 2.0, Some(3.0));
        let switch = best != comb.km3 && l.diff > 0.0 && l.diff > bar * l.se;
        assert_eq!(comb.chosen, if switch { best } else { comb.km3 }, "seed {seed}: {}", comb.reason);
        if !switch && best != comb.km3 && l.diff > 2.0 * l.se {
            assert!(comb.reason.contains("the skip bar"), "seed {seed}: {}", comb.reason);
        }
        let n = live.len();
        assert!(comb.reason.contains(&format!("close call: play-outs extended from 8 to 64 rounds for {n} candidates")), "seed {seed}: {}", comb.reason);
        eprintln!("seed {seed}: after 8 rounds: {}; at the end: {}", plain.reason, comb.reason);
    }
    eprintln!("km3's attacks: {extended} extended, {gaps} in the gap (past z, within the skip bar)");
    assert!(gaps >= 2, "the review's gap came up {gaps} times");
}

fn deck(path: &str) -> Deck {
    Deck::from_file(path).unwrap()
}

const DECK05: &str = "../decks/dustin/05-indeedee-stoutland.txt";
const ALTARIA: &str = "../decks/screen/opponents/t-altaria.txt";

/// Deck 05's first Protective Poncho in the development run's km3 game `05-indeedee-stoutland|t-altaria|0|0|ref` (seed
/// 24,450,000,000), with Pokémon on the Bench: km3 proposes the Active, where the Poncho does nothing (the Tool tests'
/// decision).
fn poncho_decision() -> (State, Vec<Action>) {
    let code = PlayerCode::KM { max_depth: 3 };
    let mut game = Game::new(create_players(deck(DECK05), deck(ALTARIA), vec![code.clone(), code]), 24_450_000_000);
    while !game.is_game_over() {
        let state = game.get_state_clone();
        let (who, actions) = state.generate_possible_actions();
        let places = actions
            .iter()
            .all(|a| matches!(&a.action, SimpleAction::AttachTool { tool_card, .. } if tool_card.get_name() == "Protective Poncho"));
        if who == 0 && actions.len() > 1 && places && state.in_play_pokemon[0].iter().skip(1).any(|p| p.is_some()) {
            return (state, actions);
        }
        game.play_tick();
    }
    panic!("no Protective Poncho placement");
}

/// `_tools _zs3 _m64` at a Tool placement, with R = 8 (LAB, cap 12, z 2): every candidate plays 8 rounds or 64; the
/// decision is first made on the extended candidates' rounds; only when no move clears the bar does the Tool tie-break
/// play the placement with an effect km3 prefers (the play-out rule's choice, same randomness), unless km3's placement
/// leads it beyond the noise. The tie-break looks at every candidate, so its placement may be one left at 8 rounds.
#[test]
fn at_a_tool_placement_the_tie_break_comes_after_the_extension() {
    let (state, actions) = poncho_decision();
    let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
    let seed = 20_000_000_251;
    let params = PlayoutParams {
        rollouts: 8,
        cap: 12,
        z: 2.0,
        knowledge: Knowledge::Lab,
        tools: true,
        z_skip: Some(3.0),
        max_rounds: Some(64),
        ..PlayoutParams::new(3)
    };
    let r = PlayoutPlayer::with_extra_lists(deck(DECK05), deck(ALTARIA), params, Vec::new())
        .evaluate(&mut StdRng::seed_from_u64(seed), &observation, &actions);
    assert!(tie_break_placements(&state, &actions, &r.candidates[r.km3].action).is_some(), "the premise: km3's Poncho on the Active");
    assert_eq!(r.failed_rounds, 0);
    for c in &r.candidates {
        assert!([8, 64].contains(&c.rounds), "{} played {} rounds", c.label, c.rounds);
    }
    if r.rounds == 64 {
        let n = r.candidates.iter().filter(|c| c.rounds == 64).count();
        assert!(r.reason.contains(&format!("close call: play-outs extended from 8 to 64 rounds for {n} candidates")), "{}", r.reason);
    }
    let best = (0..r.candidates.len())
        .filter(|&c| r.candidates[c].rounds == r.rounds)
        .fold(r.km3, |b, c| if r.candidates[c].score > r.candidates[b].score { c } else { b });
    let l = &r.candidates[best];
    if best != r.km3 && l.diff > 0.0 && l.diff > 2.0 * l.se {
        assert_eq!(r.chosen, best, "{}", r.reason);
        assert!(!r.reason.contains("tie-break"), "{}", r.reason);
        eprintln!("the best clears the bar: {}", r.reason);
        return;
    }
    let km = create_players(deck(DECK05), deck(ALTARIA), vec![PlayerCode::KM { max_depth: 3 }, PlayerCode::KM { max_depth: 3 }]).remove(0);
    let mut rule = ToolRulePlayer { inner: km, interventions: Rc::new(Cell::new(0)) };
    let preferred = rule.decision_fn(&mut StdRng::seed_from_u64(seed), &observation, &actions);
    let t = r.candidates.iter().position(|c| c.action == preferred).expect("the placement with an effect is a candidate");
    let p = &r.candidates[t];
    if p.diff < 0.0 && -p.diff > 2.0 * p.se {
        assert_eq!(r.chosen, r.km3, "{}", r.reason);
        assert!(r.reason.contains("play-outs lead the placement with one"), "{}", r.reason);
    } else {
        assert_eq!(r.chosen, t, "{}", r.reason);
        assert!(r.reason.starts_with("tie-break: Tool effect"), "{}", r.reason);
    }
    eprintln!("the tie-break's placement, {}, played {} of {} rounds: {}", p.label, p.rounds, r.rounds, r.reason);
}
