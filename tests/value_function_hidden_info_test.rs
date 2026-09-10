//! §40 — Does the value function read the OPPONENT's hidden information?
//!
//! §38 concluded: "the value function reads only opponent hand_size / deck_size (COUNTS),
//! never hand or deck CONTENTS." That is true of the feature list and FALSE of the function.
//! `calculate_active_pokemon_online_score` scans `state.decks[player]` and
//! `state.hands[player]` for evolutions of that player's Active, and it is called for the
//! opponent as well as for the searching player — at a coefficient of 500.0.
//!
//! These tests pin the leak, pin its fix, and — per the §37-R rule — prove the harness can
//! see a KNOWN-NONZERO case before any "no change" result below is allowed to mean anything.
//! `test_harness_detects_a_public_change` is that control.

use deckgym::card_ids::CardId;
use deckgym::database::get_card_by_enum;
use deckgym::models::{EnergyType, PlayedCard};
use deckgym::players::value_functions::{baseline_value_function, public_baseline_value_function};
use deckgym::test_support::get_initialized_game_with_board;
use deckgym::State;

/// Board with a plain attacker on both sides. Perspective is always player 0,
/// so player 1 is "the opponent" whose hidden zones are under test.
fn board() -> State {
    let mine = PlayedCard::from_id(CardId::A1094Pikachu)
        .with_energy(vec![EnergyType::Lightning, EnergyType::Lightning]);
    let theirs = PlayedCard::from_id(CardId::A1001Bulbasaur).with_energy(vec![EnergyType::Grass]);
    get_initialized_game_with_board(0, 0, 3, vec![mine], vec![theirs]).get_state_clone()
}

/// Replace every card in `player`'s deck with `filler`, keeping the deck the SAME LENGTH.
/// Any score change is therefore attributable to deck CONTENTS, never to `deck_size`.
fn with_deck_of(player: usize, filler: CardId) -> State {
    let mut state = board();
    let n = state.decks[player].cards.len();
    state.decks[player].cards = vec![get_card_by_enum(filler); n];
    assert_eq!(
        state.decks[player].cards.len(),
        n,
        "deck size must not change"
    );
    state
}

/// Same, for the hand.
fn with_hand_of(player: usize, filler: CardId) -> State {
    let mut state = board();
    let n = state.hands[player].len();
    state.hands[player] = vec![get_card_by_enum(filler); n];
    assert_eq!(state.hands[player].len(), n, "hand size must not change");
    state
}

/// CONTROL. A change the value function is entitled to see must move the score, under BOTH
/// value functions. If this fails, every "no change" assertion below is meaningless.
#[test]
fn test_harness_detects_a_public_change() {
    let base = board();

    // Damage on the opponent's Active is fully public information.
    let mut damaged = board();
    damaged.in_play_pokemon[1][0] = Some(
        PlayedCard::from_id(CardId::A1001Bulbasaur)
            .with_energy(vec![EnergyType::Grass])
            .with_damage(30),
    );

    for (name, vf) in [
        (
            "baseline",
            baseline_value_function as fn(&State, usize) -> f64,
        ),
        ("public", public_baseline_value_function),
    ] {
        let before = vf(&base, 0);
        let after = vf(&damaged, 0);
        assert!(
            (after - before).abs() > f64::EPSILON,
            "CONTROL FAILED for {name}: a public board change did not move the value \
             function ({before} -> {after}). No conclusion in this file is valid."
        );
    }
}

/// Documents the DEFECT, so it cannot be silently reintroduced or silently "fixed" without
/// someone noticing that `e<N>`'s behaviour changed. `baseline_value_function` is deliberately
/// left leaky: every historical ranking in this lab was produced with it, and changing it in
/// place would retroactively alter what those numbers mean.
#[test]
fn test_baseline_value_function_still_leaks_opponent_hidden_zones() {
    let deck_evo = baseline_value_function(&with_deck_of(1, CardId::A1003Venusaur), 0);
    let deck_plain = baseline_value_function(&with_deck_of(1, CardId::A1094Pikachu), 0);
    assert_ne!(
        deck_evo, deck_plain,
        "expected the historical leak via the opponent's DECK to still be present in \
         baseline_value_function; if this now passes, `e<N>` is no longer comparable to \
         every ranking in this lab and that must be stated explicitly"
    );

    let hand_evo = baseline_value_function(&with_hand_of(1, CardId::A1003Venusaur), 0);
    let hand_plain = baseline_value_function(&with_hand_of(1, CardId::A1094Pikachu), 0);
    assert_ne!(
        hand_evo, hand_plain,
        "expected the historical leak via the opponent's HAND to still be present in \
         baseline_value_function"
    );
}

/// THE FIX. Swapping the CONTENTS of the opponent's deck, size held constant, must not
/// change how player 0 evaluates the position.
#[test]
fn test_public_value_function_hides_opponent_deck_contents() {
    let evo = public_baseline_value_function(&with_deck_of(1, CardId::A1003Venusaur), 0);
    let plain = public_baseline_value_function(&with_deck_of(1, CardId::A1094Pikachu), 0);
    assert_eq!(
        evo, plain,
        "LEAK: evaluation changed when only the OPPONENT's deck CONTENTS changed \
         (deck size held constant): {evo} vs {plain}"
    );
}

/// Same question for the opponent's hand.
#[test]
fn test_public_value_function_hides_opponent_hand_contents() {
    let evo = public_baseline_value_function(&with_hand_of(1, CardId::A1003Venusaur), 0);
    let plain = public_baseline_value_function(&with_hand_of(1, CardId::A1094Pikachu), 0);
    assert_eq!(
        evo, plain,
        "LEAK: evaluation changed when only the OPPONENT's hand CONTENTS changed \
         (hand size held constant): {evo} vs {plain}"
    );
}

/// The fix must be surgical. A player's OWN deck and hand are legitimately visible to them,
/// so the public value function must still read them — otherwise we would have replaced a
/// leak with a blindfold.
#[test]
fn test_public_value_function_still_sees_own_zones() {
    let a = public_baseline_value_function(&with_deck_of(0, CardId::A1095Raichu), 0);
    let b = public_baseline_value_function(&with_deck_of(0, CardId::A1001Bulbasaur), 0);
    assert!(
        (a - b).abs() > f64::EPSILON,
        "expected a player's OWN deck contents to remain visible to them, got {a} vs {b}"
    );
}

/// The two functions must actually differ on the leaky input — otherwise `p<N>` would be a
/// relabelling of `e<N>` and the whole `e` vs `p` comparison would measure nothing.
#[test]
fn test_the_two_value_functions_disagree_where_it_matters() {
    let leaky_state = with_deck_of(1, CardId::A1003Venusaur);
    let leaky = baseline_value_function(&leaky_state, 0);
    let public = public_baseline_value_function(&leaky_state, 0);
    assert_ne!(
        leaky, public,
        "baseline and public value functions agree on a state whose only unusual feature is \
         the opponent's hidden deck — the fix is not doing anything"
    );
}
