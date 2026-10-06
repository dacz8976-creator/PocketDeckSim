//! Quiz 4's items for the play-out pilot (Oct 6; Fable via Dustin; rl/results/playout_quiz4_items_2026-10-06/README.md),
//! each its own parameter, written before the code.
//!
//! Item 1, "attack when you can" (`_za<z>`): when km3's move is an attack and kx3's best candidate is not, the switch needs
//! a lead beyond z_attack standard errors instead of z; a switch to another attack, or from a move that isn't an attack,
//! keeps the bar z. Every switch away from km3's attack names both scores in the reason (the trace's), and so does every
//! switch the stricter bar stops. With the parameter off nothing changes.
use std::collections::BTreeSet;

use deckgym::actions::{Action, SimpleAction};
use deckgym::observation::{PlayerObservation, RevealedKnowledge};
use deckgym::players::playout_player::{switch_bar, DecisionReport, Knowledge, PlayoutParams, PlayoutPlayer};
use deckgym::players::{create_players, parse_player_code, PlayerCode};
use deckgym::test_support::load_test_decks;
use deckgym::{Game, State};
use rand::{rngs::StdRng, SeedableRng};

fn is_attack(a: &Action) -> bool {
    matches!(a.action, SimpleAction::Attack(_))
}

/// Every field of a decision's report but its time, as text.
fn fingerprint(r: &DecisionReport) -> String {
    let candidates: Vec<String> = r.candidates.iter().map(|c| format!("{:?} {} {} {}", c.action, c.score, c.diff, c.se)).collect();
    format!("{:?} | km {} chosen {} | {} | rounds {}", candidates, r.km3, r.chosen, r.reason, r.rounds)
}

/// The code spells the attack bar (`_za<z>`, after `_tools`), and every code without it is as before.
#[test]
fn the_code_spells_the_attack_bar() {
    assert_eq!(PlayoutParams::new(3).z_attack, None);
    assert_eq!(PlayoutParams::new(3).code(), "kx3_r16_c12_z2_real_t0_poolwide");
    let p = PlayoutParams::parse("3_za3").unwrap();
    assert_eq!(p.z_attack, Some(3.0));
    assert_eq!(p.code(), "kx3_r16_c12_z2_real_t0_poolwide_za3");
    assert_eq!(PlayoutParams::parse(&p.code()[2..]).unwrap(), p);
    let both = PlayoutParams::parse("3_r16_c12_z2_real_t0_poolmeta_tools_za2.5").unwrap();
    assert_eq!(both.code(), "kx3_r16_c12_z2_real_t0_poolmeta_tools_za2.5");
    let PlayerCode::KX { params } = parse_player_code("kx3_za3").unwrap() else { panic!() };
    assert_eq!(params.z_attack, Some(3.0));
    for bad in ["kx3_za", "kx3_za-1", "kx3_zax"] {
        assert!(parse_player_code(bad).is_err(), "{bad} should not parse");
    }
}

/// The bar: z_attack only from km3's attack to a move that isn't one; z otherwise, and always z with the parameter off.
#[test]
fn the_attack_bar_applies_only_away_from_an_attack() {
    let (deck_a, deck_b) = load_test_decks();
    let km3 = || parse_player_code("km3").unwrap();
    let mut game = Game::new(create_players(deck_a, deck_b, vec![km3(), km3()]), 20_000_000_210);
    let mut attack = None;
    while attack.is_none() && !game.is_game_over() {
        let (_, actions) = game.get_state_clone().generate_possible_actions();
        attack = actions.iter().find(|a| is_attack(a)).cloned();
        game.play_tick();
    }
    let attack = attack.expect("an attack came up");
    let end = Action { actor: attack.actor, action: SimpleAction::EndTurn, is_stack: false };
    assert_eq!(switch_bar(&attack, &end, 2.0, Some(3.0)), 3.0, "away from an attack");
    assert_eq!(switch_bar(&attack, &attack, 2.0, Some(3.0)), 2.0, "to an attack");
    assert_eq!(switch_bar(&end, &attack, 2.0, Some(3.0)), 2.0, "from a move that isn't an attack");
    assert_eq!(switch_bar(&attack, &end, 2.0, None), 2.0, "the parameter off");
}

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

fn small(z: f64, z_attack: Option<f64>) -> PlayoutPlayer {
    let (deck_a, deck_b) = load_test_decks();
    let params = PlayoutParams { rollouts: 8, cap: 6, z, z_attack, knowledge: Knowledge::Lab, ..PlayoutParams::new(3) };
    PlayoutPlayer::with_extra_lists(deck_a, deck_b, params, Vec::new())
}

/// With the bar at z itself, every decision is the one without the parameter (identity).
#[test]
fn an_attack_bar_equal_to_z_changes_nothing() {
    for (seed, state) in attack_decisions(&[20_000_000_211, 20_000_000_212, 20_000_000_213]) {
        let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
        let actions = state.generate_possible_actions().1;
        let off = small(0.5, None).evaluate(&mut StdRng::seed_from_u64(seed), &observation, &actions);
        let same = small(0.5, Some(0.5)).evaluate(&mut StdRng::seed_from_u64(seed), &observation, &actions);
        assert_eq!(off.chosen, same.chosen, "seed {seed}");
        assert_eq!(fingerprint(&off).split(" | ").next(), fingerprint(&same).split(" | ").next(), "seed {seed}: the same play-outs");
    }
}

/// With no bar (z 0) kx3 takes the best play-out score; with an unreachable attack bar it never leaves km3's attack for a
/// move that isn't an attack, and the reason names the bar with both scores. At least one of these test-deck decisions is
/// such a stopped switch.
#[test]
fn the_attack_bar_keeps_km3s_attack_against_a_smaller_lead() {
    let decisions = attack_decisions(&[20_000_000_211, 20_000_000_212, 20_000_000_213, 20_000_000_214, 20_000_000_215, 20_000_000_216]);
    assert!(decisions.len() >= 4, "{} decisions", decisions.len());
    let mut stopped = 0;
    for (seed, state) in decisions {
        let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
        let actions = state.generate_possible_actions().1;
        let open = small(0.0, None).evaluate(&mut StdRng::seed_from_u64(seed), &observation, &actions);
        let barred = small(0.0, Some(1e9)).evaluate(&mut StdRng::seed_from_u64(seed), &observation, &actions);
        assert!(is_attack(&open.candidates[open.km3].action), "seed {seed}: km3 proposes an attack");
        assert!(is_attack(&barred.candidates[barred.chosen].action), "seed {seed}: {}", barred.reason);
        if is_attack(&open.candidates[open.chosen].action) {
            assert_eq!(barred.chosen, open.chosen, "seed {seed}");
        } else {
            stopped += 1;
            assert_eq!(barred.chosen, barred.km3, "seed {seed}: km3's attack kept");
            assert!(barred.reason.contains("attack bar") && barred.reason.contains(&format!("{:.3}", open.candidates[open.km3].score)),
                    "seed {seed}: {}", barred.reason);
        }
    }
    assert!(stopped >= 1, "no stopped switch among these decisions");
}

/// A switch away from km3's attack that clears the bar names both scores too.
#[test]
fn a_switch_away_from_an_attack_names_both_scores() {
    for (seed, state) in attack_decisions(&[20_000_000_211, 20_000_000_212, 20_000_000_213, 20_000_000_214, 20_000_000_215, 20_000_000_216]) {
        let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
        let actions = state.generate_possible_actions().1;
        let r = small(0.0, Some(0.0)).evaluate(&mut StdRng::seed_from_u64(seed), &observation, &actions);
        if !is_attack(&r.candidates[r.chosen].action) {
            let (km, chosen) = (r.candidates[r.km3].score, r.candidates[r.chosen].score);
            assert!(r.reason.contains("away from km's attack") && r.reason.contains(&format!("{km:.3}")) && r.reason.contains(&format!("{chosen:.3}")),
                    "seed {seed}: {}", r.reason);
        }
    }
}
