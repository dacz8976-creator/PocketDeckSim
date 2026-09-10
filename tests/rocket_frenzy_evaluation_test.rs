//! Public evaluation may estimate a future Rocket Frenzy from the unordered remaining-deck
//! multiset. Physical attack forecasting still resolves the concrete, observation-authorized
//! prefix. These fixtures are preserved k3 roots, not general strategy labels.

use deckgym::{
    actions::{try_forecast_action, Action, SimpleAction},
    card_ids::CardId,
    models::{Card, PlayedCard},
    observation::{canonical_actions, PlayerObservation, RevealedKnowledge},
    players::{
        public_clock_effect_value_function, public_effect_value_function, ExpectiMiniMaxPlayer,
        Player,
    },
    State,
};
use rand::{rngs::StdRng, SeedableRng};

const ROOT_612004: &str = include_str!("fixtures/rocket-frenzy-root-612004-25.json");
const ROOT_612005: &str = include_str!("fixtures/rocket-frenzy-root-612005-36.json");

fn saved_root(source: &str) -> (State, usize, u64) {
    let row: serde_json::Value = serde_json::from_str(source).unwrap();
    let state: State = serde_json::from_value(row["state"].clone()).unwrap();
    let actor = row["actor"].as_u64().unwrap() as usize;
    let search_seed = row["decision_randomness"]["search_seed"]
        .as_u64()
        .unwrap();
    assert_eq!(state.current_player, actor);
    (state, actor, search_seed)
}

fn k3(state: &State, actor: usize) -> ExpectiMiniMaxPlayer {
    ExpectiMiniMaxPlayer {
        deck: state.decks[actor].clone(),
        max_depth: 3,
        write_debug_trees: false,
        value_function: Box::new(public_clock_effect_value_function),
        opponent_ply: 0,
        consistent_horizon: false,
        soft_opponent: false,
    }
}

fn is_rocket_frenzy(action: &Action) -> bool {
    matches!(&action.action, SimpleAction::Attack(attack) if attack.title == "Rocket Frenzy")
}

fn is_team_rocket_pokemon(card: &Card) -> bool {
    matches!(card, Card::Pokemon(pokemon) if pokemon.name.contains("Team Rocket"))
}

fn with_qualifiers_first(mut state: State, actor: usize, qualifiers_first: bool) -> State {
    let cards = std::mem::take(&mut state.decks[actor].cards);
    let (qualifying, other): (Vec<_>, Vec<_>) = cards
        .into_iter()
        .partition(is_team_rocket_pokemon);
    state.decks[actor].cards = if qualifiers_first {
        qualifying.into_iter().chain(other).collect()
    } else {
        other.into_iter().chain(qualifying).collect()
    };
    state
}

fn rocket_frenzy_action(state: &State) -> Action {
    state
        .generate_possible_actions()
        .1
        .into_iter()
        .find(is_rocket_frenzy)
        .expect("saved Wobbuffet root should offer Rocket Frenzy")
}

fn forecast_damage(state: &State, action: &Action) -> u32 {
    let defender = 1 - action.actor;
    let before = state.get_active(defender).get_remaining_hp();
    let outcomes = try_forecast_action(state, action).expect("Rocket Frenzy is forecastable");
    let (probabilities, mutations) = outcomes.into_branches();
    assert_eq!(probabilities, vec![1.0]);
    assert_eq!(mutations.len(), 1);
    let mut result = state.clone();
    mutations.into_iter().next().unwrap()(
        &mut StdRng::seed_from_u64(47),
        &mut result,
        action,
    );
    before - result.get_active(defender).get_remaining_hp()
}

#[test]
fn saved_public_k3_roots_attack_instead_of_spending_x_speed() {
    for (label, source) in [("612004/25", ROOT_612004), ("612005/36", ROOT_612005)] {
        let (state, actor, search_seed) = saved_root(source);
        let observation = PlayerObservation::from_state(&state, actor, &Default::default());
        let (_, mut actions) = state.generate_possible_actions();
        canonical_actions(&mut actions);
        let chosen = k3(&state, actor).decision_fn(
            &mut StdRng::seed_from_u64(search_seed),
            &observation,
            &actions,
        );
        assert!(actions.contains(&chosen), "{label}: selected action must be legal");
        assert!(
            is_rocket_frenzy(&chosen),
            "{label}: expected Rocket Frenzy instead of the recorded X Speed, got {chosen:?}"
        );
    }
}

#[test]
fn public_future_value_is_invariant_to_remaining_deck_order() {
    let (state, actor, _) = saved_root(ROOT_612004);
    let high_prefix = with_qualifiers_first(state.clone(), actor, true);
    let low_prefix = with_qualifiers_first(state, actor, false);

    assert_ne!(high_prefix.decks[actor].cards, low_prefix.decks[actor].cards);
    let mut high_multiset = high_prefix.decks[actor].cards.clone();
    let mut low_multiset = low_prefix.decks[actor].cards.clone();
    high_multiset.sort_by_key(Card::get_id);
    low_multiset.sort_by_key(Card::get_id);
    assert_eq!(high_multiset, low_multiset);

    for (label, value) in [
        ("effect", public_effect_value_function as fn(&State, usize) -> f64),
        ("clock-effect", public_clock_effect_value_function),
    ] {
        assert_eq!(
            value(&high_prefix, actor),
            value(&low_prefix, actor),
            "{label} public leaf value must use unordered remaining-deck membership"
        );
    }
}

#[test]
fn concrete_forecast_still_uses_the_physical_prefix() {
    let (state, actor, _) = saved_root(ROOT_612004);
    let mut high_prefix = with_qualifiers_first(state.clone(), actor, true);
    let mut low_prefix = with_qualifiers_first(state, actor, false);
    high_prefix.in_play_pokemon[1 - actor][0] =
        Some(PlayedCard::from_id(CardId::B3b101MegaGyaradosEx));
    low_prefix.in_play_pokemon[1 - actor][0] =
        Some(PlayedCard::from_id(CardId::B3b101MegaGyaradosEx));

    let high_count = high_prefix.decks[actor]
        .cards
        .iter()
        .take(6)
        .filter(|card| is_team_rocket_pokemon(card))
        .count();
    let low_count = low_prefix.decks[actor]
        .cards
        .iter()
        .take(6)
        .filter(|card| is_team_rocket_pokemon(card))
        .count();
    assert_eq!((high_count, low_count), (5, 2));

    let high_action = rocket_frenzy_action(&high_prefix);
    let low_action = rocket_frenzy_action(&low_prefix);
    assert_eq!(forecast_damage(&high_prefix, &high_action), 150);
    assert_eq!(forecast_damage(&low_prefix, &low_action), 60);
}

#[test]
fn authorized_own_prefix_survives_determinization_and_drives_forecast_damage() {
    let (mut state, actor, _) = saved_root(ROOT_612004);
    state.in_play_pokemon[1 - actor][0] =
        Some(PlayedCard::from_id(CardId::B3b101MegaGyaradosEx));
    let high_order = with_qualifiers_first(state.clone(), actor, true);
    let low_order = with_qualifiers_first(state.clone(), actor, false);

    for (label, ordered, expected_damage) in [
        ("qualifiers-first", high_order, 150),
        ("nonqualifiers-first", low_order, 60),
    ] {
        let known_prefix = ordered.decks[actor].cards[..6].to_vec();
        let mut knowledge = RevealedKnowledge::default();
        knowledge.deck_top[actor] = known_prefix.clone();
        let observation = PlayerObservation::from_state(&state, actor, &knowledge);
        let search_state = observation.search_state(&mut StdRng::seed_from_u64(91));
        assert_eq!(
            &search_state.decks[actor].cards[..6],
            known_prefix.as_slice(),
            "{label}: authorized own top cards must not be shuffled away"
        );
        let action = rocket_frenzy_action(&search_state);
        assert_eq!(
            forecast_damage(&search_state, &action),
            expected_damage,
            "{label}: physical forecast must use the preserved concrete prefix"
        );
    }
}
