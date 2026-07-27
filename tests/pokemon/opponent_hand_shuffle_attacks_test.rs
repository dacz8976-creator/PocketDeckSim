use deckgym::{
    actions::Action,
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
    Game,
};
use std::collections::HashSet;

fn hand(card_ids: &[CardId]) -> Vec<Card> {
    card_ids.iter().copied().map(get_card_by_enum).collect()
}

/// Board with `attacker` against a Mega Latios ex (180 HP, no weakness) damage sponge, and a
/// fixed opponent hand. Returns the game plus the opponent's deck size before the attack.
fn setup(
    seed: u64,
    attacker: PlayedCard,
    bench: Vec<PlayedCard>,
    opponent_hand: &[CardId],
) -> (Game<'static>, usize) {
    let mut board = vec![attacker];
    board.extend(bench);
    let mut game = get_initialized_game_with_board(
        seed,
        0,
        3,
        board,
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );
    let mut state = game.get_state_clone();
    state.hands[1] = hand(opponent_hand);
    state.discard_piles[1] = vec![];
    let opponent_deck_before = state.decks[1].cards.len();
    game.set_state(state);
    (game, opponent_deck_before)
}

fn use_attack(game: &mut Game<'static>, card_id: CardId) {
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(card_id, 0),
        is_stack: false,
    });
    game.play_until_stable();
}

const FIVE_CARDS: [CardId; 5] = [
    CardId::A1219Erika,
    CardId::A2b111PokeBall,
    CardId::A2147GiantCape,
    CardId::A2148RockyHelmet,
    CardId::A1001Bulbasaur,
];

// ---------------------------------------------------------------------------
// "Your opponent reveals a random card from their hand and shuffles it into their deck."
// Tsareena (A3b 005) Kick Down
// ---------------------------------------------------------------------------

#[test]
fn test_kick_down_shuffles_one_card_back_into_the_opponents_deck() {
    let (mut game, opponent_deck_before) = setup(
        0,
        PlayedCard::from_id(CardId::A3b005Tsareena).with_energy(vec![EnergyType::Grass]),
        vec![],
        &FIVE_CARDS,
    );
    use_attack(&mut game, CardId::A3b005Tsareena);

    let state = game.get_state_clone();
    assert_eq!(state.hands[1].len(), 4);
    assert_eq!(state.decks[1].cards.len(), opponent_deck_before + 1);
    assert!(
        state.discard_piles[1].is_empty(),
        "the card goes back to the deck, it is not discarded"
    );
    assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 50);
}

#[test]
fn test_kick_down_does_nothing_extra_with_an_empty_opponent_hand() {
    let (mut game, opponent_deck_before) = setup(
        0,
        PlayedCard::from_id(CardId::A3b005Tsareena).with_energy(vec![EnergyType::Grass]),
        vec![],
        &[],
    );
    use_attack(&mut game, CardId::A3b005Tsareena);

    let state = game.get_state_clone();
    assert!(state.hands[1].is_empty());
    assert_eq!(state.decks[1].cards.len(), opponent_deck_before);
    assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 50);
}

// ---------------------------------------------------------------------------
// "Your opponent reveals a random card from their hand and shuffles it into their deck.
//  Shuffle this Pokémon into your deck." — Liepard (B1a 048) Snatch and Flee
// ---------------------------------------------------------------------------

#[test]
fn test_snatch_and_flee_also_returns_liepard_to_its_own_deck() {
    let (mut game, opponent_deck_before) = setup(
        0,
        PlayedCard::from_id(CardId::B1a048Liepard).with_energy(vec![EnergyType::Darkness]),
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        &FIVE_CARDS,
    );
    let own_deck_before = game.get_state_clone().decks[0].cards.len();

    use_attack(&mut game, CardId::B1a048Liepard);

    let state = game.get_state_clone();
    assert_eq!(state.hands[1].len(), 4);
    assert_eq!(state.decks[1].cards.len(), opponent_deck_before + 1);
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        180 - 60,
        "damage is dealt before Liepard leaves play"
    );
    assert_eq!(
        state.get_active(0).get_name(),
        "Bulbasaur",
        "the Bench Pokémon is promoted after Liepard shuffles itself away"
    );
    assert_eq!(state.decks[0].cards.len(), own_deck_before + 1);
    assert!(
        state.decks[0]
            .cards
            .iter()
            .any(|card| card.get_name() == "Liepard"),
        "Liepard must be back in its owner's deck"
    );
    assert!(state.in_play_pokemon[0][1].is_none());
}

// ---------------------------------------------------------------------------
// "Flip a coin. If heads, look at a random card from your opponent's hand and shuffle it into
//  their deck." — Purrloin (B2 104 / B2 174) Whiny Voice
// ---------------------------------------------------------------------------

#[test]
fn test_whiny_voice_shuffles_a_card_back_only_on_heads() {
    for card_id in [CardId::B2104Purrloin, CardId::B2174Purrloin] {
        let mut seen = HashSet::new();
        for seed in 0..40 {
            let (mut game, opponent_deck_before) = setup(
                seed,
                PlayedCard::from_id(card_id).with_energy(vec![EnergyType::Darkness]),
                vec![],
                &FIVE_CARDS,
            );
            use_attack(&mut game, card_id);

            let state = game.get_state_clone();
            let moved = 5 - state.hands[1].len();
            assert_eq!(
                state.decks[1].cards.len(),
                opponent_deck_before + moved,
                "{card_id:?} seed {seed}: cards leaving the hand go into the deck"
            );
            assert!(state.discard_piles[1].is_empty());
            seen.insert(moved);
        }
        assert_eq!(
            seen,
            HashSet::from([0, 1]),
            "{card_id:?}: heads moves 1 card, tails moves none"
        );
    }
}

#[test]
fn test_whiny_voice_does_nothing_extra_with_an_empty_opponent_hand() {
    for seed in 0..10 {
        let (mut game, opponent_deck_before) = setup(
            seed,
            PlayedCard::from_id(CardId::B2104Purrloin).with_energy(vec![EnergyType::Darkness]),
            vec![],
            &[],
        );
        use_attack(&mut game, CardId::B2104Purrloin);

        let state = game.get_state_clone();
        assert!(state.hands[1].is_empty());
        assert_eq!(state.decks[1].cards.len(), opponent_deck_before);
    }
}

// ---------------------------------------------------------------------------
// "Flip 3 coins. For each heads, a card is chosen at random from your opponent's hand. Your
//  opponent reveals that card and shuffles it into their deck."
// Krookodile (A3a 041) Poaching Fangs
// ---------------------------------------------------------------------------

#[test]
fn test_poaching_fangs_shuffles_one_card_per_heads() {
    let mut seen = HashSet::new();
    for seed in 0..60 {
        let (mut game, opponent_deck_before) = setup(
            seed,
            PlayedCard::from_id(CardId::A3a041Krookodile).with_energy(vec![
                EnergyType::Darkness,
                EnergyType::Darkness,
                EnergyType::Colorless,
            ]),
            vec![],
            &FIVE_CARDS,
        );
        use_attack(&mut game, CardId::A3a041Krookodile);

        let state = game.get_state_clone();
        let moved = 5 - state.hands[1].len();
        assert!(moved <= 3, "seed {seed}: at most 3 coins can come up heads");
        assert_eq!(state.decks[1].cards.len(), opponent_deck_before + moved);
        assert!(state.discard_piles[1].is_empty());
        assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 90);
        seen.insert(moved);
    }
    assert!(seen.contains(&0), "all tails must move nothing");
    assert!(
        seen.iter().any(|moved| *moved >= 2),
        "multiple heads must move multiple cards: saw {seen:?}"
    );
}

#[test]
fn test_poaching_fangs_is_capped_by_the_opponents_hand_size() {
    for seed in 0..30 {
        let (mut game, opponent_deck_before) = setup(
            seed,
            PlayedCard::from_id(CardId::A3a041Krookodile).with_energy(vec![
                EnergyType::Darkness,
                EnergyType::Darkness,
                EnergyType::Colorless,
            ]),
            vec![],
            &[CardId::A1219Erika],
        );
        use_attack(&mut game, CardId::A3a041Krookodile);

        let state = game.get_state_clone();
        assert!(state.hands[1].len() <= 1);
        assert_eq!(
            state.decks[1].cards.len() - opponent_deck_before,
            1 - state.hands[1].len(),
            "seed {seed}: never move more cards than the opponent holds"
        );
    }
}
