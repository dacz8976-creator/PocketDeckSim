use log::debug;
use std::cmp::min;

use crate::{
    actions::{
        abilities::DiscardSearchKind, apply_action_helpers::Mutations, apply_evolve,
        apply_place_card, outcomes::Outcomes,
    },
    combinatorics::generate_combinations,
    hooks::can_evolve_into,
    models::{Card, EnergyType, TrainerType},
    tools::is_tool_card,
    State,
};

pub(crate) fn pokemon_search_outcomes(
    acting_player: usize,
    state: &State,
    basic_only: bool,
) -> Outcomes {
    card_search_outcomes_with_filter(acting_player, state, move |card: &&Card| {
        if basic_only {
            card.is_basic()
        } else {
            matches!(card, Card::Pokemon(_))
        }
    })
}

pub(crate) fn pokemon_search_outcomes_by_type(
    state: &State,
    basic_only: bool,
    energy_type: EnergyType,
) -> Outcomes {
    pokemon_search_outcomes_by_type_for_player(state.current_player, state, basic_only, energy_type)
}

pub(crate) fn pokemon_search_outcomes_by_type_for_player(
    acting_player: usize,
    state: &State,
    basic_only: bool,
    energy_type: EnergyType,
) -> Outcomes {
    card_search_outcomes_with_filter(acting_player, state, move |card: &&Card| {
        let type_matches = card.get_type().map(|t| t == energy_type).unwrap_or(false);
        let basic_check = !basic_only || card.is_basic();
        type_matches && basic_check
    })
}

pub(crate) fn search_to_hand_by_evolves_from(state: &State, name: String) -> Outcomes {
    card_search_outcomes_with_filter(
        state.current_player,
        state,
        move |card: &&Card| matches!(card, Card::Pokemon(pokemon_card) if pokemon_card.evolves_from.as_deref() == Some(name.as_str())),
    )
}

pub(crate) fn item_search_outcomes(acting_player: usize, state: &State) -> Outcomes {
    card_search_outcomes_with_filter(
        acting_player,
        state,
        |card: &&Card| matches!(card, Card::Trainer(t) if t.trainer_card_type == TrainerType::Item),
    )
}

pub(crate) fn tool_search_outcomes(acting_player: usize, state: &State) -> Outcomes {
    card_search_outcomes_with_filter(acting_player, state, |card: &&Card| is_tool_card(card))
}

/// "Put `amount` random `card_kind` cards from your discard pile into your hand" (Galarian
/// Perrserker's Dig Up). The discard-pile mirror of `card_search_outcomes_with_filter_multiple`:
/// one equally likely branch per unordered combination the Ability could pull, so the search bots
/// price the real distribution. Takes fewer cards than asked for when the pile holds fewer, and
/// degrades to a no-op when it holds none — unlike the deck searches there is nothing to shuffle.
pub(crate) fn discard_search_outcomes(
    acting_player: usize,
    state: &State,
    card_kind: DiscardSearchKind,
    amount: u8,
) -> Outcomes {
    let eligible: Vec<Card> = state.discard_piles[acting_player]
        .iter()
        .filter(|card| card_kind.matches(card))
        .cloned()
        .collect();

    let draw_count = min(amount as usize, eligible.len());
    if draw_count == 0 {
        return Outcomes::single_fn(|_, _, _| {});
    }

    let combinations = generate_combinations(&eligible, draw_count);
    let num_outcomes = combinations.len();
    let probabilities = vec![1.0 / (num_outcomes as f64); num_outcomes];
    let mutations: Mutations = combinations
        .into_iter()
        .map(|combo| -> crate::actions::apply_action_helpers::Mutation {
            Box::new(move |_, state, action| {
                for card in &combo {
                    state.transfer_card_from_discard_to_hand(action.actor, card);
                }
            })
        })
        .collect();

    Outcomes::from_parts(probabilities, mutations)
}

pub(crate) fn gladion_search_outcomes(acting_player: usize, state: &State) -> Outcomes {
    card_search_outcomes_with_filter(acting_player, state, move |card: &&Card| {
        let name = card.get_name();
        name == "Type: Null" || name == "Silvally"
    })
}

pub(crate) fn supporter_search_outcomes(acting_player: usize, state: &State) -> Outcomes {
    card_search_outcomes_with_filter(
        acting_player,
        state,
        move |card: &&Card| matches!(card, Card::Trainer(trainer_card) if trainer_card.trainer_card_type == crate::models::TrainerType::Supporter),
    )
}

fn card_search_outcomes_with_filter<F>(
    acting_player: usize,
    state: &State,
    card_filter: F,
) -> Outcomes
where
    F: Fn(&&Card) -> bool + Clone + 'static,
{
    card_search_outcomes_with_filter_multiple(acting_player, state, 1, card_filter)
}

/// Draw up to `num_to_draw` cards from deck that match the filter, using unordered combinations
pub(crate) fn card_search_outcomes_with_filter_multiple<F>(
    acting_player: usize,
    state: &State,
    num_to_draw: usize,
    card_filter: F,
) -> Outcomes
where
    F: Fn(&&Card) -> bool + Clone + 'static,
{
    let eligible_pokemon: Vec<Card> = state.decks[acting_player]
        .cards
        .iter()
        .filter(|c| card_filter(c))
        .cloned()
        .collect();

    let num_eligible = eligible_pokemon.len();

    if num_eligible == 0 {
        // No eligible Pokemon in deck, just shuffle
        return Outcomes::single_fn(|rng, state, action| {
            state.decks[action.actor].shuffle(false, rng);
        });
    }

    let actual_draw_count = min(num_to_draw, num_eligible);

    // Generate all possible unordered combinations
    let draw_combinations = generate_combinations(&eligible_pokemon, actual_draw_count);
    let num_outcomes = draw_combinations.len();
    let probabilities = vec![1.0 / (num_outcomes as f64); num_outcomes];
    let mut outcomes: Mutations = vec![];

    for combo in draw_combinations {
        outcomes.push(Box::new(move |rng, state, _action| {
            // Transfer each Pokemon from the combination to hand
            for pokemon in &combo {
                state.transfer_card_from_deck_to_hand(acting_player, pokemon);
            }

            state.decks[acting_player].shuffle(false, rng);
        }));
    }

    Outcomes::from_parts(probabilities, outcomes)
}

/// Put one random card matching `card_filter` from `player`'s discard pile into their hand.
///
/// Like the deck searches above this returns one equally-likely branch per distinct candidate
/// rather than rolling the rng, so search bots price the retrieval instead of seeing a single
/// sampled result. Returns a no-op when the discard pile holds no candidate.
pub(crate) fn discard_search_outcomes_with_filter<F>(
    acting_player: usize,
    state: &State,
    card_filter: F,
) -> Outcomes
where
    F: Fn(&Card) -> bool + 'static,
{
    let candidates: Vec<Card> = state.discard_piles[acting_player]
        .iter()
        .filter(|card| card_filter(card))
        .cloned()
        .collect();

    if candidates.is_empty() {
        return Outcomes::single_fn(|_, _, _| {});
    }

    let num_outcomes = candidates.len();
    let probabilities = vec![1.0 / (num_outcomes as f64); num_outcomes];
    let mut outcomes: Mutations = vec![];
    for card in candidates {
        outcomes.push(Box::new(move |_, state, action| {
            if let Some(idx) = state.discard_piles[action.actor]
                .iter()
                .position(|c| c == &card)
            {
                state.discard_piles[action.actor].remove(idx);
                state.hands[action.actor].push(card.clone());
            }
        }));
    }

    Outcomes::from_parts(probabilities, outcomes)
}

/// Generates outcomes for the `RandomEvolutionFromDeck` abilities (Caterpie's Quick Growth,
/// Porygon2's Buggy Evolution): pick a random card from `player`'s deck that evolves from the
/// Pokémon at `in_play_idx` and evolve it. Returns a no-op (just shuffle) when no eligible
/// evolution exists in the deck.
///
/// The branch is chosen at forecast time but the board can still move between forecast and
/// mutation (Buggy Evolution forecasts *before* the Energy attach that triggers it, and that
/// attach can knock the holder out via Electromagnetic Wall), so each mutation re-checks that the
/// evolution is still legal before applying it.
pub(crate) fn random_evolution_from_deck_outcomes(
    player: usize,
    in_play_idx: usize,
    state: &State,
) -> Outcomes {
    let Some(target) = state.in_play_pokemon[player][in_play_idx].as_ref() else {
        return Outcomes::single_fn(move |rng, state, _action| {
            state.decks[player].shuffle(false, rng);
        });
    };
    let evolution_cards: Vec<Card> = state.decks[player]
        .cards
        .iter()
        .filter(|card| can_evolve_into(state, card, target))
        .cloned()
        .collect();

    if evolution_cards.is_empty() {
        return Outcomes::single_fn(move |rng, state, _action| {
            state.decks[player].shuffle(false, rng);
        });
    }

    let n = evolution_cards.len();
    let probabilities = vec![1.0 / n as f64; n];
    let mutations: Mutations = evolution_cards
        .into_iter()
        .map(
            |evo_card| -> crate::actions::apply_action_helpers::Mutation {
                Box::new(move |rng, state, _action| {
                    let still_legal = state.in_play_pokemon[player][in_play_idx]
                        .as_ref()
                        .is_some_and(|target| can_evolve_into(state, &evo_card, target))
                        && state.decks[player].cards.contains(&evo_card);
                    if still_legal {
                        apply_evolve(player, state, &evo_card, in_play_idx, true);
                    }
                    state.decks[player].shuffle(false, rng);
                })
            },
        )
        .collect();

    Outcomes::from_parts(probabilities, mutations)
}

pub(crate) fn search_and_bench_by_name(state: &State, card_name: String) -> Outcomes {
    search_and_bench_with_filter(
        state,
        move |card: &Card| card.get_name() == card_name,
        "Card should be in deck",
    )
}

/// "Put `count` random cards from among <names> from your deck onto your Bench" (Wishiwashi's Call
/// for Family, Tandemaus' Flock). The multi-name, multi-card generalization of
/// [`search_and_bench_by_name`]: one equally likely branch per unordered combination the attack
/// could pull, so the search bots price the real distribution rather than a pre-picked answer.
///
/// Takes fewer cards than asked for when the deck holds fewer, and stops early when the Bench fills
/// up. The deck is always shuffled afterwards, even when nothing was found.
pub(crate) fn search_and_bench_by_names(
    state: &State,
    names: Vec<String>,
    count: usize,
) -> Outcomes {
    let eligible: Vec<Card> = state.decks[state.current_player]
        .cards
        .iter()
        .filter(|card| names.iter().any(|name| card.get_name() == *name))
        .cloned()
        .collect();

    let draw_count = min(count, eligible.len());
    if draw_count == 0 {
        return Outcomes::single_fn(|rng, state, action| {
            state.decks[action.actor].shuffle(false, rng);
        });
    }

    let combinations = generate_combinations(&eligible, draw_count);
    let num_outcomes = combinations.len();
    let probabilities = vec![1.0 / (num_outcomes as f64); num_outcomes];
    let mutations: Mutations = combinations
        .into_iter()
        .map(|combo| -> crate::actions::apply_action_helpers::Mutation {
            Box::new(move |rng, state, action| {
                for card in &combo {
                    let Some(bench_idx) = state.in_play_pokemon[action.actor]
                        .iter()
                        .position(|slot| slot.is_none())
                    else {
                        debug!("No bench space left, stopping the search early");
                        break;
                    };
                    // The card must still be in the deck: the combination was drawn from it and
                    // nothing else has touched it in between.
                    apply_place_card(state, action.actor, card, bench_idx, true);
                }
                state.decks[action.actor].shuffle(false, rng);
            })
        })
        .collect();

    Outcomes::from_parts(probabilities, mutations)
}

pub(crate) fn search_and_bench_basic(state: &State) -> Outcomes {
    search_and_bench_with_filter(
        state,
        |card: &Card| card.is_basic(),
        "Basic card should be in deck",
    )
}

fn search_and_bench_with_filter<F>(
    state: &State,
    card_filter: F,
    missing_card_msg: &'static str,
) -> Outcomes
where
    F: Fn(&Card) -> bool + Clone + 'static,
{
    let num_cards_in_deck = state.decks[state.current_player]
        .cards
        .iter()
        .filter(|c| card_filter(c))
        .count();

    if num_cards_in_deck == 0 {
        Outcomes::single_fn({
            |rng, state, action| {
                // If there are no matching cards in the deck, just shuffle it
                state.decks[action.actor].shuffle(false, rng);
            }
        })
    } else {
        let probabilities = vec![1.0 / (num_cards_in_deck as f64); num_cards_in_deck];
        let mut outcomes: Mutations = vec![];

        for i in 0..num_cards_in_deck {
            let card_filter = card_filter.clone();
            outcomes.push(Box::new(move |rng, state, action| {
                let bench_space = state.in_play_pokemon[action.actor]
                    .iter()
                    .position(|x| x.is_none());
                if bench_space.is_none() {
                    debug!("No bench space available, shuffling deck without placing card");
                    state.decks[action.actor].shuffle(false, rng);
                    return;
                }

                let card = state.decks[action.actor]
                    .cards
                    .iter()
                    .filter(|c| card_filter(c))
                    .nth(i)
                    .cloned()
                    .expect(missing_card_msg);

                debug!(
                    "Fetched {card:?} from deck for player {} to place on bench",
                    action.actor
                );

                let bench_idx = bench_space.unwrap();
                apply_place_card(state, action.actor, &card, bench_idx, true);

                state.decks[action.actor].shuffle(false, rng);
            }));
        }
        Outcomes::from_parts(probabilities, outcomes)
    }
}

/// §47 — "Look at the top N cards of your deck, put all <matching> cards into your hand, shuffle
/// the rest back."
///
/// # ⚠ This shape was the single most expensive node in the engine
///
/// The obvious model — one outcome branch per C(deck, N) subset — is *correct* but ruinous: a
/// 17-card deck gives **C(17,4) = 2,380 branches**, and an expectiminimax search evaluates every
/// one of them at every node where the card is playable, at every depth. Three cards share this
/// shape (Sightseer, Traveling Merchant, Puppy-Loving Girl).
///
/// **This is what actually made `milotic-vaporeon` a cost outlier — not Vaporeon's Wash Out.**
/// §43-D attributed it to Wash Out's unbounded "as often as you like" branching. Ablation says
/// otherwise: disabling Wash Out outright leaves the deck at 20.3 s / 10 games (vs 20.2 s with it),
/// while removing Sightseer drops it to 3.2 s. The mechanism is *outcome* branching at a chance
/// node, not *action* branching — which is why every previous look at degrees-per-ply (5.25, barely
/// above the 5.01 field average) missed it.
///
/// # The collapse is exact, not a heuristic
///
/// The mutation only depends on WHICH matching cards were revealed; the non-matching ones are
/// shuffled back and are unobservable. So all subsets sharing a matching-set produce the identical
/// resulting state. Grouping them and summing their probabilities gives the *same* distribution
/// over successor states with far fewer branches — typically single digits. Nothing is
/// approximated and no play is removed.
pub(crate) fn top_n_reveal_outcomes<F>(
    acting_player: usize,
    state: &State,
    look_count: usize,
    matches_filter: F,
) -> Outcomes
where
    F: Fn(&Card) -> bool,
{
    let deck_cards: Vec<Card> = state.decks[acting_player].cards.to_vec();
    let look_count = min(look_count, deck_cards.len());
    if look_count == 0 {
        return Outcomes::single_fn(|_, _, _| {});
    }

    let combinations = generate_combinations(&deck_cards, look_count);
    let total = combinations.len() as f64;

    // Key on the matching cards only — that is the whole observable content of the reveal.
    let mut grouped: Vec<(Vec<Card>, f64)> = Vec::new();
    for subset in combinations {
        let mut taken: Vec<Card> = subset
            .into_iter()
            .filter(|card| matches_filter(card))
            .collect();
        taken.sort_by_key(|card| card.get_id());
        match grouped.iter_mut().find(|(existing, _)| *existing == taken) {
            Some((_, weight)) => *weight += 1.0,
            None => grouped.push((taken, 1.0)),
        }
    }

    debug!(
        "Top-{look_count} reveal: {} distinct outcome(s) collapsed from {total} subset(s)",
        grouped.len()
    );

    let mut probabilities = Vec::with_capacity(grouped.len());
    let mut outcomes: Mutations = Vec::with_capacity(grouped.len());
    for (taken, weight) in grouped {
        probabilities.push(weight / total);
        outcomes.push(Box::new(move |rng, state, _action| {
            for card in &taken {
                state.transfer_card_from_deck_to_hand(acting_player, card);
            }
            state.decks[acting_player].shuffle(false, rng);
        }));
    }
    Outcomes::from_parts(probabilities, outcomes)
}
