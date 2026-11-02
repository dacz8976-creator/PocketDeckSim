// Ported from upstream deckgym-core #438 (tests/stadiums/abandoned_station_test.rs, 20d1857): its 2 tests (heads draws a card, tails nothing, and the use is once per turn; not offered with an empty deck) as upstream wrote them. Fork tests follow at the end: both players use the same Stadium, each once during their own turn and from their own deck; the exact forecast (one coin); a 10-card hand; an empty deck for either player (the fork's Stadium convention); Will; Luxury Coin on the player's own Abandoned Station (Keep and Reroll, both Gholdengo printings, real play and search) and not on the opponent's, with revert switch G9 on and off; the bots at its roots; and the printing's status. The Luxury Coin Stadium census is a lib test in actions/trainer_coin_plan.rs (every_stadium_that_flips_coins_takes_the_stadium_route).
//! Abandoned Station (C1 131): "Once during each player's turn, that player may use this effect.
//! Flip a coin. If heads, draw a card."

use deckgym::{
    actions::{try_forecast_action, with_luxury_coin_own_stadium_only, Action, SimpleAction},
    card_ids::CardId,
    card_validation::{get_implementation_status, implementation_limitations, ImplementationStatus},
    database::get_card_by_enum,
    models::{Card, PlayedCard},
    observation::canonical_actions,
    players::{create_players, PlayerCode},
    state::{LuxuryCoinDecision, TrainerCoinEffectRoute},
    test_support::{
        get_initialized_game, get_initialized_game_with_board, play_trainer, trainer_from_id,
    },
    Deck, Game, State,
};
use rand::{rngs::StdRng, SeedableRng};

fn game_with_station(seed: u64, deck_size: usize) -> deckgym::Game<'static> {
    let mut game = get_initialized_game(seed);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    state.current_player = 0;
    state.turn_count = 3;
    state.active_stadium = Some(get_card_by_enum(CardId::C1131AbandonedStation));
    state.decks[0].cards = (0..deck_size)
        .map(|_| get_card_by_enum(CardId::A1001Bulbasaur))
        .collect::<Vec<Card>>();
    state.hands[0] = vec![get_card_by_enum(CardId::A1033Charmander)];
    game.set_state(state);
    game
}

fn has_use_stadium(game: &deckgym::Game<'static>) -> bool {
    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    actions
        .iter()
        .any(|action| matches!(action.action, SimpleAction::UseStadium))
}

/// Abandoned Station: "Once during each player's turn, that player may use this effect. Flip a
/// coin. If heads, draw a card."
#[test]
fn test_abandoned_station_draws_a_card_on_heads_and_is_once_per_turn() {
    let mut saw_heads = false;
    let mut saw_tails = false;
    for seed in 0..30 {
        let mut game = game_with_station(seed, 10);
        assert!(has_use_stadium(&game));
        game.apply_action(&Action {
            actor: 0,
            action: SimpleAction::UseStadium,
            is_stack: false,
        });
        let state = game.get_state_clone();
        assert!(state.has_used_stadium[0]);
        match state.hands[0].len() {
            2 => saw_heads = true,
            1 => saw_tails = true,
            n => panic!("Seed {seed}: unexpected hand size {n}"),
        }
        assert!(!has_use_stadium(&game), "Seed {seed}: only once per turn");
    }
    assert!(saw_heads && saw_tails);
}

#[test]
fn test_abandoned_station_not_offered_with_empty_deck() {
    assert!(!has_use_stadium(&game_with_station(0, 0)));
}

// Fork tests.

fn use_stadium(actor: usize) -> Action {
    Action {
        actor,
        action: SimpleAction::UseStadium,
        is_stack: false,
    }
}

fn keep() -> Action {
    Action {
        actor: 0,
        action: SimpleAction::KeepTrainerCoinResults,
        is_stack: true,
    }
}

fn reroll(source: usize) -> Action {
    Action {
        actor: 0,
        action: SimpleAction::RerollTrainerCoins {
            luxury_coin_in_play_idx: source,
        },
        is_stack: true,
    }
}

fn end_turn(game: &mut Game<'static>, actor: usize) {
    game.apply_action(&Action {
        actor,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });
    game.play_until_stable();
}

fn has_will(state: &State) -> bool {
    serde_json::to_string(state).unwrap().contains("ForceFirstHeads")
}

fn card(id: CardId) -> Card {
    get_card_by_enum(id)
}

/// Player 0 to act on turn 3 with `own` against a Charmander. Abandoned Station is in play with
/// `owner` as the player who played it (None: a board set up without playing it); player 0's deck
/// is five Bulbasaur and player 1's five Squirtle; both hands and discard piles are empty.
fn station_game(seed: u64, own: Vec<PlayedCard>, owner: Option<usize>) -> Game<'static> {
    let mut game = get_initialized_game_with_board(
        seed,
        0,
        3,
        own,
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    let mut state = game.get_state_clone();
    state.active_stadium = Some(card(CardId::C1131AbandonedStation));
    state.active_stadium_owner = owner;
    state.decks[0].cards = vec![card(CardId::A1001Bulbasaur); 5];
    state.decks[1].cards = vec![card(CardId::A1053Squirtle); 5];
    state.hands = [vec![], vec![]];
    state.discard_piles = [vec![], vec![]];
    game.set_state(state);
    game
}

/// Bulbasaur Active with Gholdengo (Luxury Coin) on the Bench, in play slot 1.
fn with_gholdengo(gholdengo: CardId) -> Vec<PlayedCard> {
    vec![
        PlayedCard::from_id(CardId::A1001Bulbasaur),
        PlayedCard::from_id(gholdengo),
    ]
}

fn bulbasaur() -> Vec<PlayedCard> {
    vec![PlayedCard::from_id(CardId::A1001Bulbasaur)]
}

/// The exact forecast of `action` from `state`: its probabilities and each branch's successor.
fn branches(state: &State, action: &Action) -> (Vec<f64>, Vec<State>) {
    let (probabilities, mutations) = try_forecast_action(state, action)
        .expect("an exact forecast")
        .into_branches();
    let successors = mutations
        .into_iter()
        .map(|mutation| {
            let mut next = state.clone();
            mutation(&mut StdRng::seed_from_u64(0), &mut next, action);
            next
        })
        .collect();
    (probabilities, successors)
}

fn assert_close(actual: &[f64], expected: &[f64]) {
    assert_eq!(actual.len(), expected.len(), "{actual:?} v {expected:?}");
    for (a, e) in actual.iter().zip(expected) {
        assert!((a - e).abs() < 1e-12, "{actual:?} v {expected:?}");
    }
}

/// "Once during each player's turn, that player may use this effect": player 0 plays Abandoned
/// Station and uses it; player 1 uses the same Stadium during their turn; player 0 may use it
/// again during the next one. Each use is offered once during that player's turn, draws 0 or 1
/// card from the user's own deck (Bulbasaur for player 0, Squirtle for player 1), and leaves the
/// other player's flag, hand and deck alone.
#[test]
fn test_abandoned_station_each_player_uses_it_once_during_their_own_turn() {
    let mut draws = [0usize; 2];
    for seed in 0..16 {
        let mut game = station_game(seed, bulbasaur(), None);
        let mut state = game.get_state_clone();
        state.active_stadium = None;
        state.hands[0] = vec![card(CardId::C1131AbandonedStation)];
        game.set_state(state);
        assert!(!has_use_stadium(&game), "seed {seed}: no Stadium in play yet");
        play_trainer(&mut game, 0, trainer_from_id(CardId::C1131AbandonedStation));
        assert_eq!(game.get_state_clone().active_stadium_owner, Some(0));

        let mut use_once = |game: &mut Game<'static>, actor: usize, own_card: CardId| {
            let other = 1 - actor;
            let before = game.get_state_clone();
            assert_eq!(before.current_player, actor, "seed {seed}");
            assert!(!before.has_used_stadium[actor], "seed {seed}");
            assert!(has_use_stadium(game), "seed {seed}: player {actor} is offered the use");
            game.apply_action(&use_stadium(actor));
            let after = game.get_state_clone();
            let drawn = after.hands[actor].len() - before.hands[actor].len();
            assert!(drawn <= 1, "seed {seed}: one coin draws at most one card");
            assert_eq!(
                before.decks[actor].cards.len() - after.decks[actor].cards.len(),
                drawn,
                "seed {seed}"
            );
            if drawn == 1 {
                assert_eq!(after.hands[actor].last(), Some(&card(own_card)), "seed {seed}");
            }
            assert!(after.has_used_stadium[actor], "seed {seed}");
            assert_eq!(
                after.has_used_stadium[other], before.has_used_stadium[other],
                "seed {seed}"
            );
            assert_eq!(after.hands[other], before.hands[other], "seed {seed}");
            assert_eq!(after.decks[other].cards, before.decks[other].cards, "seed {seed}");
            assert!(!has_use_stadium(game), "seed {seed}: once during the turn");
            draws[drawn] += 1;
        };

        use_once(&mut game, 0, CardId::A1001Bulbasaur);
        end_turn(&mut game, 0);
        // Each flag is cleared when its player's next turn starts (State::end_turn_maintenance),
        // so player 0's still stands during player 1's turn and doesn't block player 1.
        assert_eq!(game.get_state_clone().has_used_stadium, [true, false]);
        use_once(&mut game, 1, CardId::A1053Squirtle);
        end_turn(&mut game, 1);
        assert_eq!(game.get_state_clone().has_used_stadium, [false, true]);
        use_once(&mut game, 0, CardId::A1001Bulbasaur);
    }
    assert!(draws[0] > 0 && draws[1] > 0, "heads and tails both seen: {draws:?}");
}

/// The exact forecast is one coin: 1/2 heads, which moves one card from the user's deck into the
/// hand, and 1/2 tails, which changes nothing else; both record the use for that player only.
#[test]
fn test_abandoned_station_forecast_is_one_coin_heads_draws_tails_nothing() {
    let game = station_game(0, bulbasaur(), None);
    let mut state = game.get_state_clone();
    let deck = vec![
        card(CardId::A1001Bulbasaur),
        card(CardId::A1033Charmander),
        card(CardId::A1053Squirtle),
    ];
    state.decks[0].cards = deck.clone();
    state.hands[0] = vec![card(CardId::A1094Pikachu)];
    let (probabilities, successors) = branches(&state, &use_stadium(0));
    assert_close(&probabilities, &[0.5, 0.5]);
    let heads = successors
        .iter()
        .find(|next| next.hands[0].len() == 2)
        .expect("a heads branch draws one card");
    let tails = successors
        .iter()
        .find(|next| next.hands[0].len() == 1)
        .expect("a tails branch draws nothing");
    let drawn = heads.hands[0][1].clone();
    assert!(deck.contains(&drawn));
    assert!(!heads.decks[0].cards.contains(&drawn));
    assert_eq!(heads.decks[0].cards.len(), 2);
    assert_eq!(tails.hands[0], state.hands[0]);
    assert_eq!(tails.decks[0].cards, deck);
    for next in [heads, tails] {
        assert_eq!(next.has_used_stadium, [true, false]);
        assert_eq!(next.hands[1], state.hands[1]);
        assert_eq!(next.decks[1].cards, state.decks[1].cards);
    }
}

/// A full hand: the fork's draw convention (`State::maybe_draw_card` stops at 10 cards, and a draw
/// effect stays offered) keeps the use on offer, and heads then draws nothing. Upstream also
/// offers it.
#[test]
fn test_abandoned_station_at_a_ten_card_hand_is_offered_and_heads_draws_nothing() {
    let mut game = station_game(0, bulbasaur(), None);
    let mut state = game.get_state_clone();
    state.hands[0] = vec![card(CardId::A1033Charmander); 10];
    game.set_state(state.clone());
    assert!(has_use_stadium(&game));
    let (probabilities, successors) = branches(&state, &use_stadium(0));
    assert_close(&probabilities, &[0.5, 0.5]);
    for next in successors {
        assert_eq!(next.hands[0].len(), 10);
        assert_eq!(next.decks[0].cards.len(), 5);
        assert!(next.has_used_stadium[0]);
    }
}

/// An empty deck: the fork's convention for a Stadium that takes from the deck (stadiums.rs:
/// Mesagoza, Fragrant Forest, Kid's Room and Arcade) is that its use isn't offered, here to either
/// player. One card left is enough, and heads draws it.
#[test]
fn test_abandoned_station_with_an_empty_deck_is_not_offered_to_either_player() {
    let mut game = station_game(0, bulbasaur(), None);
    let mut state = game.get_state_clone();
    state.decks[0].cards.clear();
    game.set_state(state.clone());
    assert!(!has_use_stadium(&game), "player 0, empty deck");

    state.current_player = 1;
    state.decks[0].cards = vec![card(CardId::A1001Bulbasaur); 5];
    state.decks[1].cards.clear();
    game.set_state(state.clone());
    assert!(!has_use_stadium(&game), "player 1, empty deck");

    state.decks[1].cards = vec![card(CardId::A1053Squirtle)];
    game.set_state(state.clone());
    assert!(has_use_stadium(&game), "player 1, one card left");
    let (probabilities, successors) = branches(&state, &use_stadium(1));
    assert_close(&probabilities, &[0.5, 0.5]);
    let heads = successors
        .iter()
        .find(|next| next.hands[1].len() == 1)
        .expect("heads draws the last card");
    assert!(heads.decks[1].cards.is_empty());
    assert_eq!(heads.hands[1], vec![card(CardId::A1053Squirtle)]);
    assert_eq!(heads.has_used_stadium, [false, true]);
}

/// Will: "The next time you flip any number of coins for the effect of an attack, Ability, or
/// Trainer card after using this card on this turn, the first coin flip will definitely be
/// heads." This fork applies Will to a Stadium's coins (UseStadium is Will-eligible in
/// apply_action.rs, as will_test's Mesagoza test shows), so after Will the use always draws and
/// uses Will; the exact forecast is the heads branch alone.
#[test]
fn test_will_forces_abandoned_stations_coin_to_heads() {
    let will_game = |seed: u64| {
        let mut game = station_game(seed, bulbasaur(), None);
        let mut state = game.get_state_clone();
        state.hands[0] = vec![card(CardId::A4156Will)];
        game.set_state(state);
        play_trainer(&mut game, 0, trainer_from_id(CardId::A4156Will));
        assert!(has_will(&game.get_state_clone()));
        game
    };
    for seed in 0..32 {
        let mut game = will_game(seed);
        game.apply_action(&use_stadium(0));
        let state = game.get_state_clone();
        assert_eq!(state.hands[0], vec![card(CardId::A1001Bulbasaur)], "seed {seed}");
        assert_eq!(state.decks[0].cards.len(), 4, "seed {seed}");
        assert!(!has_will(&state), "seed {seed}: Will is used on the coin");
    }
    let state = will_game(0).get_state_clone();
    let (probabilities, successors) = branches(&state, &use_stadium(0));
    assert_close(&probabilities, &[1.0]);
    assert_eq!(successors[0].hands[0].len(), 1);
    assert!(!has_will(&successors[0]));
}

/// Luxury Coin (Gholdengo, both printings): "Once during your turn, when you flip any coins for an
/// effect of your Trainer cards, you may ignore all results of those coin flips and begin flipping
/// those coins again." A Stadium is the Trainer card of the player who played it (TEXT_AUDIT.md
/// A6b), so using an Abandoned Station you played (or one with no recorded player, as for Arcade)
/// pauses on the coin, on the Stadium route, with the use recorded and nothing drawn yet; only
/// Keep and Reroll are offered. Keep draws on heads; Reroll uses Luxury Coin and draws on the new
/// heads. No panic: the Stadium is registered in `trainer_coin_plan::stadium_route`.
#[test]
fn test_abandoned_station_luxury_coin_keep_and_reroll_on_the_players_own_station() {
    for gholdengo in [CardId::B4a051Gholdengo, CardId::B4a109Gholdengo] {
        for played in [true, false] {
            let mut faces_seen = [false; 2];
            for seed in 0..12 {
                for rerolled in [false, true] {
                    let ctx = format!("{gholdengo:?}, played {played}, seed {seed}");
                    let mut game = station_game(seed, with_gholdengo(gholdengo), None);
                    if played {
                        let mut state = game.get_state_clone();
                        state.active_stadium = None;
                        state.hands[0] = vec![card(CardId::C1131AbandonedStation)];
                        game.set_state(state);
                        play_trainer(&mut game, 0, trainer_from_id(CardId::C1131AbandonedStation));
                        assert_eq!(game.get_state_clone().active_stadium_owner, Some(0), "{ctx}");
                    }
                    let before = game.get_state_clone();
                    game.apply_action(&use_stadium(0));
                    let paused = game.get_state_clone();
                    let pending = paused
                        .pending_trainer_coin_choice
                        .clone()
                        .unwrap_or_else(|| panic!("{ctx}: Luxury Coin pauses on the coin"));
                    assert_eq!(pending.flips.len(), 1, "{ctx}");
                    assert_eq!(pending.luxury_coin_in_play_idx, 1, "{ctx}");
                    let Some(TrainerCoinEffectRoute::Stadium { stadium, played_by }) =
                        pending.route.clone()
                    else {
                        panic!("{ctx}: the Stadium route");
                    };
                    assert_eq!(stadium.id, "C1 131", "{ctx}");
                    assert_eq!(played_by, before.active_stadium_owner, "{ctx}");
                    assert!(paused.has_used_stadium[0], "{ctx}");
                    assert_eq!(paused.hands[0], before.hands[0], "{ctx}: nothing drawn yet");
                    assert_eq!(paused.decks[0].cards, before.decks[0].cards, "{ctx}");
                    let (_, offered) = paused.generate_possible_actions();
                    assert_eq!(offered.len(), 2, "{ctx}");
                    assert!(offered.contains(&keep()) && offered.contains(&reroll(1)), "{ctx}");

                    game.apply_action(&if rerolled { reroll(1) } else { keep() });
                    let after = game.get_state_clone();
                    let record = game.luxury_coin_resolution_history().last().unwrap().clone();
                    assert_eq!(record.initial_faces, pending.flips, "{ctx}");
                    let heads = if rerolled {
                        assert_eq!(record.decision, LuxuryCoinDecision::Reroll, "{ctx}");
                        let faces = record.replacement_faces.clone().unwrap();
                        assert_eq!(faces.len(), 1, "{ctx}");
                        faces[0]
                    } else {
                        assert_eq!(record.decision, LuxuryCoinDecision::Keep, "{ctx}");
                        assert!(record.replacement_faces.is_none(), "{ctx}");
                        pending.flips[0]
                    };
                    faces_seen[usize::from(heads)] = true;
                    assert!(after.pending_trainer_coin_choice.is_none(), "{ctx}");
                    assert_eq!(after.luxury_coin_used_this_turn[0], rerolled, "{ctx}");
                    assert_eq!(
                        after.hands[0].len(),
                        before.hands[0].len() + usize::from(heads),
                        "{ctx}"
                    );
                    assert_eq!(
                        after.decks[0].cards.len() + usize::from(heads),
                        before.decks[0].cards.len(),
                        "{ctx}"
                    );
                    assert!(after.has_used_stadium[0], "{ctx}");
                    assert!(!has_use_stadium(&game), "{ctx}: once during the turn");
                }
            }
            assert!(faces_seen[0] && faces_seen[1], "{gholdengo:?}, played {played}");
        }
    }
}

/// The opponent's Abandoned Station is not one of your Trainer cards (TEXT_AUDIT.md A6b; G9 on, the
/// default): its coin is flipped with no offer, as on the opponent's Arcade, and Luxury Coin stays
/// unused. Revert switch G9 off (`with_luxury_coin_own_stadium_only(false, ..)`): Luxury Coin
/// covers any Stadium, so the coin pauses whoever played the Station (no one, player 0, player 1),
/// and Keep and Reroll resolve it, with no panic.
#[test]
fn test_abandoned_station_luxury_coin_not_on_the_opponents_station_and_g9_off() {
    let mut draws = [0usize; 2];
    for seed in 0..16 {
        let mut game = station_game(seed, with_gholdengo(CardId::B4a051Gholdengo), Some(1));
        game.apply_action(&use_stadium(0));
        let after = game.get_state_clone();
        assert!(after.pending_trainer_coin_choice.is_none(), "seed {seed}: no offer");
        assert!(!after.luxury_coin_used_this_turn[0], "seed {seed}");
        assert!(game.luxury_coin_resolution_history().is_empty(), "seed {seed}");
        assert!(after.has_used_stadium[0], "seed {seed}");
        draws[after.hands[0].len()] += 1;
    }
    assert!(draws[0] > 0 && draws[1] > 0, "{draws:?}");

    with_luxury_coin_own_stadium_only(false, || {
        for owner in [None, Some(0), Some(1)] {
            for rerolled in [false, true] {
                let ctx = format!("G9 off, owner {owner:?}, rerolled {rerolled}");
                let mut game = station_game(3, with_gholdengo(CardId::B4a109Gholdengo), owner);
                game.apply_action(&use_stadium(0));
                let paused = game.get_state_clone();
                let pending = paused
                    .pending_trainer_coin_choice
                    .clone()
                    .unwrap_or_else(|| panic!("{ctx}: the coin pauses"));
                assert_eq!(pending.flips.len(), 1, "{ctx}");
                let Some(TrainerCoinEffectRoute::Stadium { played_by, .. }) = pending.route else {
                    panic!("{ctx}: the Stadium route");
                };
                assert_eq!(played_by, owner, "{ctx}");
                game.apply_action(&if rerolled { reroll(1) } else { keep() });
                let after = game.get_state_clone();
                assert!(after.pending_trainer_coin_choice.is_none(), "{ctx}");
                assert_eq!(after.luxury_coin_used_this_turn[0], rerolled, "{ctx}");
                assert!(after.has_used_stadium[0], "{ctx}");
                assert!(after.hands[0].len() <= 1, "{ctx}");
            }
        }
    });
    with_luxury_coin_own_stadium_only(true, || {
        let mut game = station_game(3, with_gholdengo(CardId::B4a109Gholdengo), Some(1));
        game.apply_action(&use_stadium(0));
        let after = game.get_state_clone();
        assert!(after.pending_trainer_coin_choice.is_none(), "G9 on: no offer");
        assert!(!after.luxury_coin_used_this_turn[0]);
    });
}

/// The search sees the same thing exactly (`try_forecast_action`, through the Luxury Coin entry):
/// the use is two staged branches, 1/2 each, paused on heads or on tails with the use recorded
/// and nothing drawn; Keep is one branch (heads draws one card, tails none); a Reroll is a fresh
/// coin, 1/2 each, and uses Luxury Coin.
#[test]
fn test_abandoned_station_luxury_coin_search_is_exact() {
    let game = station_game(5, with_gholdengo(CardId::B4a051Gholdengo), Some(0));
    let state = game.get_state_clone();
    let (probabilities, paused) = branches(&state, &use_stadium(0));
    assert_close(&probabilities, &[0.5, 0.5]);
    let mut faces = Vec::new();
    for next in &paused {
        let pending = next
            .pending_trainer_coin_choice
            .as_ref()
            .expect("the search pauses on the coin too");
        assert_eq!(pending.flips.len(), 1);
        faces.push(pending.flips[0]);
        assert!(next.has_used_stadium[0]);
        assert_eq!(next.hands[0], state.hands[0]);
        assert_eq!(next.decks[0].cards, state.decks[0].cards);

        let (kept_probabilities, kept) = branches(next, &keep());
        assert_close(&kept_probabilities, &[1.0]);
        assert_eq!(kept[0].hands[0].len(), usize::from(pending.flips[0]));
        assert!(kept[0].pending_trainer_coin_choice.is_none());
        assert!(!kept[0].luxury_coin_used_this_turn[0]);

        let (rerolled_probabilities, rerolled) = branches(next, &reroll(1));
        assert_close(&rerolled_probabilities, &[0.5, 0.5]);
        let mut drawn: Vec<usize> = rerolled.iter().map(|after| after.hands[0].len()).collect();
        drawn.sort();
        assert_eq!(drawn, vec![0, 1]);
        for after in &rerolled {
            assert!(after.pending_trainer_coin_choice.is_none());
            assert!(after.luxury_coin_used_this_turn[0]);
        }
    }
    faces.sort();
    assert_eq!(faces, vec![false, true]);
}

/// Will with Luxury Coin: the paused coin is heads every time and Will is used; a Reroll is a fresh
/// coin that Will doesn't touch (some are tails), as for Misty and Sweet Honey.
#[test]
fn test_will_with_luxury_coin_forces_only_the_paused_abandoned_station_coin() {
    let mut saw_tails = false;
    for seed in 0..32 {
        let mut game = station_game(seed, with_gholdengo(CardId::B4a051Gholdengo), Some(0));
        let mut state = game.get_state_clone();
        state.hands[0] = vec![card(CardId::A4156Will)];
        game.set_state(state);
        play_trainer(&mut game, 0, trainer_from_id(CardId::A4156Will));
        assert!(has_will(&game.get_state_clone()), "seed {seed}");
        game.apply_action(&use_stadium(0));
        let paused = game.get_state_clone();
        assert_eq!(
            paused.pending_trainer_coin_choice.as_ref().unwrap().flips,
            vec![true],
            "seed {seed}"
        );
        assert!(!has_will(&paused), "seed {seed}: Will is used on the paused coin");
        game.apply_action(&reroll(1));
        let record = game.luxury_coin_resolution_history().last().unwrap().clone();
        let heads = record.replacement_faces.unwrap()[0];
        saw_tails |= !heads;
        assert_eq!(
            game.get_state_clone().hands[0].len(),
            usize::from(heads),
            "seed {seed}"
        );
    }
    assert!(saw_tails, "a Reroll is not forced");
}

/// The bots at every Abandoned Station root (km3 and WeightedRandomPlayer, through
/// `create_players`): the main phase with the use offered and, with Gholdengo, Keep or Reroll;
/// with and without Will. Each picks an offered action, without panic (km3's search forecasts the
/// use, through the Luxury Coin entry when Gholdengo is in play).
#[test]
fn test_bots_decide_at_every_abandoned_station_root() {
    let decide = |game: &Game<'static>, code: &PlayerCode| {
        let state = game.get_state_clone();
        let (actor, mut actions) = state.generate_possible_actions();
        canonical_actions(&mut actions);
        let codes = vec![code.clone(), code.clone()];
        let mut players = create_players(Deck::default(), Deck::default(), codes);
        let observation = game.observation(actor);
        let chosen =
            players[actor].decision_fn(&mut StdRng::seed_from_u64(7), &observation, &actions);
        assert!(actions.contains(&chosen), "{code:?} chose {chosen:?}");
        chosen
    };
    for code in [PlayerCode::KM { max_depth: 3 }, PlayerCode::W] {
        for (gholdengo, will) in [(false, false), (true, false), (false, true), (true, true)] {
            let ctx = format!("{code:?}, Gholdengo {gholdengo}, Will {will}");
            let own = if gholdengo {
                with_gholdengo(CardId::B4a051Gholdengo)
            } else {
                bulbasaur()
            };
            let mut game = station_game(3, own, Some(0));
            if will {
                let mut state = game.get_state_clone();
                state.hands[0] = vec![card(CardId::A4156Will)];
                game.set_state(state);
                play_trainer(&mut game, 0, trainer_from_id(CardId::A4156Will));
            }
            assert!(has_use_stadium(&game), "{ctx}");
            let _ = decide(&game, &code);
            game.apply_action(&use_stadium(0));
            if gholdengo {
                let chosen = decide(&game, &code);
                assert!(
                    matches!(
                        chosen.action,
                        SimpleAction::KeepTrainerCoinResults
                            | SimpleAction::RerollTrainerCoins { .. }
                    ),
                    "{ctx}"
                );
                game.apply_action(&chosen);
            }
            let state = game.get_state_clone();
            assert!(state.pending_trainer_coin_choice.is_none(), "{ctx}");
            assert!(state.has_used_stadium[0], "{ctx}");
        }
    }
}

/// Abandoned Station is Complete, with no limitation of its own (the empty-deck rule is the fork's
/// Stadium convention, tested above); Gholdengo's Luxury Coin line names it on both printings.
#[test]
fn test_abandoned_station_reports_complete() {
    assert_eq!(
        get_implementation_status(CardId::C1131AbandonedStation),
        ImplementationStatus::Complete
    );
    assert!(implementation_limitations(CardId::C1131AbandonedStation).is_empty());
    let named = "Luxury Coin is offered on Arcade, Mesagoza or Abandoned Station only when";
    for id in [CardId::B4a051Gholdengo, CardId::B4a109Gholdengo] {
        assert_eq!(
            get_implementation_status(id),
            ImplementationStatus::RulesUnverified,
            "{id:?}"
        );
        assert!(
            implementation_limitations(id)
                .iter()
                .any(|line| line.contains(named)),
            "{id:?}"
        );
    }
}
