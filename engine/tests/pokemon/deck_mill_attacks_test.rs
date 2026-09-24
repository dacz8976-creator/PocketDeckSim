use deckgym::{
    actions::Action,
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
    Game,
};
use std::collections::HashSet;

fn game_with_attacker(seed: u64, attacker: PlayedCard) -> Game<'static> {
    get_initialized_game_with_board(
        seed,
        0,
        3,
        vec![attacker],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    )
}

fn use_attack(game: &mut Game<'static>, card_id: CardId, index: usize) {
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(card_id, index),
        is_stack: false,
    });
    game.play_until_stable();
}

// ---------------------------------------------------------------------------
// "Discard the top 3 cards of your deck." — Rhyperior (A2 082 / A2 169) Mountain Swing
// ---------------------------------------------------------------------------

#[test]
fn test_mountain_swing_discards_top_three_of_own_deck() {
    for card_id in [CardId::A2082Rhyperior, CardId::A2169Rhyperior] {
        let mut game = game_with_attacker(
            0,
            PlayedCard::from_id(card_id).with_energy(vec![
                EnergyType::Fighting,
                EnergyType::Fighting,
                EnergyType::Fighting,
                EnergyType::Colorless,
            ]),
        );
        let before = game.get_state_clone();
        let deck_before: Vec<_> = before.decks[0].cards.iter().take(3).cloned().collect();
        let deck_len_before = before.decks[0].cards.len();
        let discard_len_before = before.discard_piles[0].len();
        let opponent_deck_len_before = before.decks[1].cards.len();
        assert!(deck_len_before >= 3, "test needs a deck with >= 3 cards");

        use_attack(&mut game, card_id, 0);

        let state = game.get_state_clone();
        assert_eq!(state.decks[0].cards.len(), deck_len_before - 3);
        assert_eq!(state.discard_piles[0].len(), discard_len_before + 3);
        assert_eq!(
            state.discard_piles[0][discard_len_before..],
            deck_before[..],
            "{card_id:?}: the top 3 cards must be the ones discarded, in order"
        );
        assert_eq!(
            state.decks[1].cards.len(),
            opponent_deck_len_before,
            "{card_id:?}: only your own deck is milled"
        );
        assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 150);
    }
}

#[test]
fn test_mountain_swing_still_attacks_with_an_empty_deck() {
    let mut game = game_with_attacker(
        0,
        PlayedCard::from_id(CardId::A2082Rhyperior).with_energy(vec![
            EnergyType::Fighting,
            EnergyType::Fighting,
            EnergyType::Fighting,
            EnergyType::Colorless,
        ]),
    );
    let mut state = game.get_state_clone();
    state.decks[0].cards.clear();
    state.discard_piles[0] = vec![];
    game.set_state(state);

    use_attack(&mut game, CardId::A2082Rhyperior, 0);

    let state = game.get_state_clone();
    assert!(state.discard_piles[0].is_empty());
    assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 150);
}

// ---------------------------------------------------------------------------
// "Discard the top 5 cards of each player's deck."
// Ultra Necrozma ex (P-A 081) Shoegaze
// ---------------------------------------------------------------------------

#[test]
fn test_shoegaze_mills_five_from_both_decks() {
    let mut game = game_with_attacker(
        0,
        PlayedCard::from_id(CardId::PA081UltraNecrozmaEx).with_energy(vec![
            EnergyType::Psychic,
            EnergyType::Psychic,
            EnergyType::Metal,
            EnergyType::Metal,
        ]),
    );
    let before = game.get_state_clone();
    let own_deck_before = before.decks[0].cards.len();
    let opponent_deck_before = before.decks[1].cards.len();
    let own_discard_before = before.discard_piles[0].len();
    let opponent_discard_before = before.discard_piles[1].len();

    use_attack(&mut game, CardId::PA081UltraNecrozmaEx, 1);

    let state = game.get_state_clone();
    assert_eq!(state.decks[0].cards.len(), own_deck_before - 5);
    assert_eq!(state.decks[1].cards.len(), opponent_deck_before - 5);
    assert_eq!(state.discard_piles[0].len(), own_discard_before + 5);
    assert_eq!(state.discard_piles[1].len(), opponent_discard_before + 5);
    assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 120);
}

// ---------------------------------------------------------------------------
// "Flip a coin until you get tails. For each heads, discard the top card of your
// opponent's deck." — Coalossal (B3 094) Mountain Crush
// ---------------------------------------------------------------------------

#[test]
fn test_mountain_crush_mills_opponent_once_per_heads() {
    let mut milled_counts = HashSet::new();
    for seed in 0..40 {
        let mut game = game_with_attacker(
            seed,
            PlayedCard::from_id(CardId::B3094Coalossal).with_energy(vec![
                EnergyType::Fighting,
                EnergyType::Fighting,
                EnergyType::Colorless,
            ]),
        );
        let before = game.get_state_clone();
        let opponent_deck_before = before.decks[1].cards.len();
        let opponent_discard_before = before.discard_piles[1].len();
        let own_deck_before = before.decks[0].cards.len();

        use_attack(&mut game, CardId::B3094Coalossal, 0);

        let state = game.get_state_clone();
        let milled = opponent_deck_before - state.decks[1].cards.len();
        assert_eq!(
            state.discard_piles[1].len(),
            opponent_discard_before + milled,
            "seed {seed}: milled cards must land in the opponent's discard pile"
        );
        assert_eq!(
            state.decks[0].cards.len(),
            own_deck_before,
            "seed {seed}: Mountain Crush only mills the opponent"
        );
        assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 90);
        milled_counts.insert(milled);
    }
    assert!(
        milled_counts.contains(&0),
        "an immediate tails must mill nothing"
    );
    assert!(
        milled_counts.iter().any(|count| *count >= 2),
        "consecutive heads must mill more than one card: saw {milled_counts:?}"
    );
}
