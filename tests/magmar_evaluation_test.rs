//! Luckycad 08:20 shows Magmar's 60-damage preview against a Poisoned target.
//! Compare public leaf scores with synthetic plain-damage controls and independently
//! check physical resolution. These are constructed positions, not full video replays.

use deckgym::{
    actions::Action,
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard, StatusCondition},
    observation::{PlayerObservation, RevealedKnowledge},
    players::{
        baseline_value_function, public_baseline_value_function,
        public_clock_effect_value_function, public_clock_value_function,
        public_damage_value_function, public_development_value_function,
        public_effect_value_function, public_pokemon_value_function,
    },
    test_support::{attack_action, get_initialized_game_with_board},
    State,
};
use rand::{rngs::StdRng, SeedableRng};

fn legal_condition_sets() -> Vec<Vec<StatusCondition>> {
    use StatusCondition::*;
    let mut sets = Vec::new();
    // Poison and Burn coexist; Asleep, Confused and Paralyzed are mutually exclusive.
    for poison in [false, true] {
        for burn in [false, true] {
            for rotated in [None, Some(Asleep), Some(Confused), Some(Paralyzed)] {
                let mut conditions = Vec::new();
                if poison { conditions.push(Poisoned); }
                if burn { conditions.push(Burned); }
                if let Some(condition) = rotated { conditions.push(condition); }
                sets.push(conditions);
            }
        }
    }
    sets
}

fn magmar(plain_damage: Option<u32>) -> PlayedCard {
    let mut card = PlayedCard::from_id(CardId::B4a006TeamRocketsMagmar)
        .with_energy(vec![EnergyType::Psychic]);
    if let Some(damage) = plain_damage {
        if let Card::Pokemon(ref mut pokemon) = card.card {
            pokemon.attacks[0].fixed_damage = damage;
            pokemon.attacks[0].effect = None;
        }
    }
    card
}

fn target(conditions: &[StatusCondition]) -> PlayedCard {
    let mut card = PlayedCard::from_id(CardId::PB024MegaLatiosEx);
    for &condition in conditions {
        card = card.with_status_condition(condition);
    }
    card
}

fn position(conditions: &[StatusCondition], plain_damage: Option<u32>, actor: usize) -> State {
    let mut state = State::default();
    state.turn_count = 3;
    // Keep current_player fixed to catch accidentally reading it instead of the
    // evaluated slot's owner when estimating the opposing Magmar's threat.
    state.current_player = 0;
    if actor == 0 {
        state.set_board(vec![magmar(plain_damage)], vec![target(conditions)]);
    } else {
        state.set_board(vec![target(conditions)], vec![magmar(plain_damage)]);
    }
    state
}

#[test]
fn magmar_physical_damage_matches_all_legal_condition_combinations() {
    for conditions in legal_condition_sets() {
        let defender = target(&conditions);
        let before = defender.get_remaining_hp();
        let mut game = get_initialized_game_with_board(47, 0, 3,
            vec![magmar(None)], vec![defender]);
        game.apply_action(&Action { actor: 0,
            action: attack_action(CardId::B4a006TeamRocketsMagmar, 0), is_stack: false });
        let after = game.get_state_clone().get_active(1).get_remaining_hp();
        assert_eq!(before - after, 10 + 50 * conditions.len() as u32, "{conditions:?}");
    }
}

#[test]
fn effect_aware_leaves_value_magmar_at_its_conditional_damage_for_either_owner() {
    let functions: [(&str, fn(&State, usize) -> f64); 3] = [
        ("f", public_effect_value_function),
        ("g", public_development_value_function),
        ("k", public_clock_effect_value_function),
    ];
    for conditions in legal_condition_sets() {
        let expected = 10 + 50 * conditions.len() as u32;
        for actor in [0, 1] {
            let actual = position(&conditions, None, actor);
            let control = position(&conditions, Some(expected), actor);
            for (name, value) in functions {
                for perspective in [0, 1] {
                    assert_eq!(value(&actual, perspective), value(&control, perspective),
                        "tier {name}, actor {actor}, perspective {perspective}, {conditions:?}");
                }
            }
        }
    }
}

#[test]
fn printed_damage_baselines_keep_their_historical_magmar_evaluation() {
    let functions: [(&str, fn(&State, usize) -> f64); 5] = [
        ("e", baseline_value_function),
        ("p", public_baseline_value_function),
        ("d", public_damage_value_function),
        ("t", public_clock_value_function),
        ("v", public_pokemon_value_function),
    ];
    for conditions in legal_condition_sets() {
        for actor in [0, 1] {
            let actual = position(&conditions, None, actor);
            let printed = position(&conditions, Some(10), actor);
            for (name, value) in functions {
                for perspective in [0, 1] {
                    assert_eq!(value(&actual, perspective), value(&printed, perspective), "tier {name}, actor {actor}, perspective {perspective}, {conditions:?}");
                }
            }
        }
    }
}

#[test]
fn magmar_public_evaluation_is_invariant_to_unseen_cards_and_own_deck_order() {
    let mut base = position(&[StatusCondition::Poisoned], None, 0);
    base.decks[0].cards = vec![get_card_by_enum(CardId::PA001Potion),
        get_card_by_enum(CardId::PA002XSpeed), get_card_by_enum(CardId::PA005PokeBall)];
    base.decks[1].cards = base.decks[0].cards.clone();
    base.hands[1] = vec![get_card_by_enum(CardId::PA007ProfessorsResearch)];
    let knowledge = RevealedKnowledge::default();
    let observed = PlayerObservation::from_state(&base, 0, &knowledge);
    for shift in 0..3 {
        let mut changed = base.clone();
        changed.decks[0].cards.rotate_left(shift);
        changed.decks[1].cards.fill(get_card_by_enum(CardId::A1003Venusaur));
        changed.hands[1].fill(get_card_by_enum(CardId::PA006RedCard));
        let alternative = PlayerObservation::from_state(&changed, 0, &knowledge);
        assert_eq!(observed, alternative);
        for seed in [7, 47, 91] {
            let a = observed.search_state(&mut StdRng::seed_from_u64(seed));
            let b = alternative.search_state(&mut StdRng::seed_from_u64(seed));
            for value in [public_effect_value_function as fn(&State, usize) -> f64,
                          public_development_value_function, public_clock_effect_value_function] {
                assert_eq!(value(&a, 0), value(&b, 0));
            }
        }
    }
}
