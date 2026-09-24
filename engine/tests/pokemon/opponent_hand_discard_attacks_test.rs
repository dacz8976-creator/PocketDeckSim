use deckgym::{
    actions::Action,
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
    Game,
};
use std::collections::HashSet;

/// Mega Latios ex (180 HP, no weakness) is the damage sponge: it survives every attack in this
/// file, so `hp_before - hp_after` never silently caps at a knockout.
fn sponge() -> PlayedCard {
    PlayedCard::from_id(CardId::PB024MegaLatiosEx)
}

fn hand(card_ids: &[CardId]) -> Vec<Card> {
    card_ids.iter().copied().map(get_card_by_enum).collect()
}

fn setup(seed: u64, attacker: PlayedCard, opponent_hand: &[CardId]) -> (Game<'static>, Vec<Card>) {
    let mut game = get_initialized_game_with_board(seed, 0, 3, vec![attacker], vec![sponge()]);
    let mut state = game.get_state_clone();
    state.hands[1] = hand(opponent_hand);
    state.discard_piles[1] = vec![];
    let before = state.hands[1].clone();
    game.set_state(state);
    (game, before)
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
// "Discard a random card from your opponent's hand."
// Houndoom (A4 118 / P-A 096) Diving Swipe, Shiftry (B1 010) Nipping Cyclone
// ---------------------------------------------------------------------------

#[test]
fn test_discard_random_opponent_hand_card_removes_exactly_one_card() {
    let printings = [
        (CardId::A4118Houndoom, vec![EnergyType::Darkness; 3], 70),
        (CardId::PA096Houndoom, vec![EnergyType::Darkness; 3], 70),
        (CardId::B1010Shiftry, vec![EnergyType::Grass; 2], 70),
    ];
    for (card_id, energy, damage) in printings {
        let (mut game, before) = setup(
            7,
            PlayedCard::from_id(card_id).with_energy(energy),
            &[
                CardId::A1219Erika,
                CardId::A2b111PokeBall,
                CardId::A2147GiantCape,
            ],
        );
        use_attack(&mut game, card_id, 0);

        let state = game.get_state_clone();
        assert_eq!(
            state.hands[1].len(),
            2,
            "{card_id:?} should discard exactly 1 card from the opponent's hand"
        );
        assert_eq!(
            state.discard_piles[1].len(),
            1,
            "{card_id:?}: the discarded card must land in the opponent's discard pile"
        );
        let discarded = &state.discard_piles[1][0];
        assert!(
            before.contains(discarded),
            "{card_id:?}: discarded card must have come from the opponent's hand"
        );
        assert_eq!(
            state.get_active(1).get_remaining_hp(),
            180 - damage,
            "{card_id:?} should still deal its printed damage"
        );
    }
}

#[test]
fn test_discard_random_opponent_hand_card_does_nothing_extra_with_empty_hand() {
    let (mut game, _) = setup(
        7,
        PlayedCard::from_id(CardId::A4118Houndoom).with_energy(vec![EnergyType::Darkness; 3]),
        &[],
    );
    use_attack(&mut game, CardId::A4118Houndoom, 0);

    let state = game.get_state_clone();
    assert!(state.hands[1].is_empty());
    assert!(
        state.discard_piles[1].is_empty(),
        "nothing can be discarded from an empty hand"
    );
    assert_eq!(state.get_active(1).get_remaining_hp(), 110);
}

// ---------------------------------------------------------------------------
// "Discard a random Pokémon Tool card from your opponent's hand."
// Alolan Meowth (A3a 037 / A3a 073) Meddle
// ---------------------------------------------------------------------------

#[test]
fn test_meddle_discards_only_a_pokemon_tool() {
    for card_id in [CardId::A3a037AlolanMeowth, CardId::A3a073AlolanMeowth] {
        let (mut game, _) = setup(
            3,
            PlayedCard::from_id(card_id).with_energy(vec![EnergyType::Darkness]),
            &[
                CardId::A1219Erika,
                CardId::A2b111PokeBall,
                CardId::A2147GiantCape,
            ],
        );
        use_attack(&mut game, card_id, 0);

        let state = game.get_state_clone();
        assert_eq!(state.hands[1].len(), 2);
        assert_eq!(state.discard_piles[1].len(), 1);
        assert_eq!(
            state.discard_piles[1][0].get_name(),
            "Giant Cape",
            "{card_id:?} may only discard the Pokémon Tool card"
        );
    }
}

#[test]
fn test_meddle_does_nothing_when_opponent_has_no_tool() {
    let (mut game, _) = setup(
        3,
        PlayedCard::from_id(CardId::A3a037AlolanMeowth).with_energy(vec![EnergyType::Darkness]),
        &[CardId::A1219Erika, CardId::A2b111PokeBall],
    );
    use_attack(&mut game, CardId::A3a037AlolanMeowth, 0);

    let state = game.get_state_clone();
    assert_eq!(
        state.hands[1].len(),
        2,
        "Meddle must not touch a hand without Pokémon Tool cards"
    );
    assert!(state.discard_piles[1].is_empty());
}

// ---------------------------------------------------------------------------
// "Discard a random Item card from your opponent's hand."
// Alolan Raticate (A3 107) Scrounge-and-Scarf
// ---------------------------------------------------------------------------

#[test]
fn test_scrounge_and_scarf_discards_only_an_item() {
    let (mut game, _) = setup(
        11,
        PlayedCard::from_id(CardId::A3107AlolanRaticate).with_energy(vec![EnergyType::Darkness; 2]),
        &[
            CardId::A1219Erika,
            CardId::A2b111PokeBall,
            CardId::A2147GiantCape,
        ],
    );
    use_attack(&mut game, CardId::A3107AlolanRaticate, 0);

    let state = game.get_state_clone();
    assert_eq!(state.hands[1].len(), 2);
    assert_eq!(state.discard_piles[1].len(), 1);
    assert_eq!(state.discard_piles[1][0].get_name(), "Poké Ball");
    assert_eq!(state.get_active(1).get_remaining_hp(), 130);
}

#[test]
fn test_scrounge_and_scarf_does_nothing_when_opponent_has_no_item() {
    let (mut game, _) = setup(
        11,
        PlayedCard::from_id(CardId::A3107AlolanRaticate).with_energy(vec![EnergyType::Darkness; 2]),
        &[CardId::A1219Erika, CardId::A2147GiantCape],
    );
    use_attack(&mut game, CardId::A3107AlolanRaticate, 0);

    let state = game.get_state_clone();
    assert_eq!(state.hands[1].len(), 2);
    assert!(state.discard_piles[1].is_empty());
}

// ---------------------------------------------------------------------------
// "Flip a coin. If heads, discard a random card from your opponent's hand."
// Persian (A1 197 / B1 313) Shadow Claw
// ---------------------------------------------------------------------------

#[test]
fn test_shadow_claw_discards_only_on_heads() {
    for card_id in [CardId::A1197Persian, CardId::B1313Persian] {
        let mut seen_hand_sizes = HashSet::new();
        for seed in 0..40 {
            let (mut game, _) = setup(
                seed,
                PlayedCard::from_id(card_id).with_energy(vec![EnergyType::Colorless; 2]),
                &[
                    CardId::A1219Erika,
                    CardId::A2b111PokeBall,
                    CardId::A2147GiantCape,
                ],
            );
            use_attack(&mut game, card_id, 0);

            let state = game.get_state_clone();
            assert_eq!(
                state.hands[1].len() + state.discard_piles[1].len(),
                3,
                "{card_id:?}: cards leaving the hand must go to the discard pile"
            );
            assert_eq!(
                state.get_active(1).get_remaining_hp(),
                180 - 40,
                "{card_id:?}: damage is dealt on both coin outcomes"
            );
            seen_hand_sizes.insert(state.hands[1].len());
        }
        assert_eq!(
            seen_hand_sizes,
            HashSet::from([2, 3]),
            "{card_id:?}: heads discards one card, tails discards nothing"
        );
    }
}

#[test]
fn test_shadow_claw_does_nothing_extra_with_empty_hand() {
    for seed in 0..10 {
        let (mut game, _) = setup(
            seed,
            PlayedCard::from_id(CardId::A1197Persian).with_energy(vec![EnergyType::Colorless; 2]),
            &[],
        );
        use_attack(&mut game, CardId::A1197Persian, 0);

        let state = game.get_state_clone();
        assert!(state.hands[1].is_empty());
        assert!(state.discard_piles[1].is_empty());
    }
}
