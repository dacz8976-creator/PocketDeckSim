// Ported from upstream deckgym-core #433 (tests/trainers/c1_sweet_honey_test.rs, e7cc5ce) as #439 left it (7aa4ef0): its 2 tests. test_sweet_honey_heals_20_per_heads_until_tails is adapted to this fork's order: the Play offers a ChooseSweetHoneyTarget on the one damaged Pokémon and the coins are flipped when it resolves (upstream flips first, then offers a Heal of 20 per heads on any of the player's Pokémon), with no cap on the heads (upstream's geometric_until_tails(8)); its board, seeds and assertions are upstream's. test_sweet_honey_needs_a_damaged_pokemon (#439) is as upstream wrote it. Fork tests follow at the end: neither printing playable without a damaged Pokémon; damaged targets only and nothing flipped before the choice, on both printings; an unoffered target refused before the coins, with the gameplay RNG fingerprinted after it; the Play drawing nothing from that RNG, on both printings; no cap; the exact search forecast and its match with real play; Will; Heal Block; Luxury Coin (both Gholdengo printings, real play and search, Will, a spent coin); serialization, redaction and adoption, malformed states included; the bots at every Sweet Honey root; and the printings' status.
//! Sweet Honey (C1 119, C1 152): "Choose 1 of your Pokémon, and then flip a coin until you get
//! tails. For each heads, heal 20 damage from that Pokémon."

use std::panic::{catch_unwind, AssertUnwindSafe};

use deckgym::{
    actions::{try_forecast_action, Action, SimpleAction, UnpricedForecastKind},
    card_ids::CardId,
    card_validation::{get_implementation_status, implementation_limitations, ImplementationStatus},
    database::get_card_by_enum,
    models::{Card, PlayedCard},
    observation::{canonical_actions, PlayerObservation, RevealedKnowledge, INFORMATION_MODEL},
    players::{create_players, Player, PlayerCode},
    state::{MistySourceRoute, TrainerCoinEffectRoute},
    test_support::{
        get_initialized_game_with_board, get_test_game_with_board, play_trainer, trainer_from_id,
    },
    Deck, Game, State,
};
use rand::{rngs::StdRng, SeedableRng};

/// Sweet Honey: "Choose 1 of your Pokémon, and then flip a coin until you get tails. For each
/// heads, heal 20 damage from that Pokémon."
#[test]
fn test_sweet_honey_heals_20_per_heads_until_tails() {
    let mut healed_amounts = std::collections::BTreeSet::new();
    for seed in 0..60u64 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![PlayedCard::from_id(CardId::A1001Bulbasaur).with_remaining_hp(10)],
            vec![PlayedCard::from_id(CardId::A1033Charmander)],
        );
        let honey = trainer_from_id(CardId::C1119SweetHoney);
        let mut state = game.get_state_clone();
        state.hands[0] = vec![Card::Trainer(honey.clone())];
        game.set_state(state);

        play_trainer(&mut game, 0, honey);

        // Ours: the Pokémon is chosen first, and the coins are flipped when the choice resolves.
        let state = game.get_state_clone();
        let (_, actions) = state.generate_possible_actions();
        assert_eq!(actions, vec![target(0)]);
        game.apply_action(&actions[0]);
        let state = game.get_state_clone();
        let healed = state.get_active(0).get_remaining_hp() - 10;
        assert_eq!(healed % 20, 0);
        assert!(state.hands[0].is_empty(), "Sweet Honey leaves the hand");
        healed_amounts.insert(healed);
    }
    assert!(
        healed_amounts.contains(&0),
        "tails first should heal nothing"
    );
    assert!(healed_amounts.contains(&20));
    assert!(healed_amounts.contains(&40));
}

/// Like Potion, Sweet Honey needs a damaged Pokémon to target.
#[test]
fn test_sweet_honey_needs_a_damaged_pokemon() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    let mut state = game.get_state_clone();
    state.hands[0] = vec![Card::Trainer(trainer_from_id(CardId::C1119SweetHoney))];
    game.set_state(state);
    let state = game.get_state_clone();
    let (_, actions) = state.generate_possible_actions();
    assert!(!actions
        .iter()
        .any(|a| matches!(a.action, SimpleAction::Play { .. })));

    // A damaged Benched Pokémon is enough to play it.
    let mut state = game.get_state_clone();
    state.in_play_pokemon[0][1] =
        Some(PlayedCard::from_id(CardId::A1033Charmander).with_remaining_hp(10));
    game.set_state(state);
    let state = game.get_state_clone();
    let (_, actions) = state.generate_possible_actions();
    assert!(actions
        .iter()
        .any(|a| matches!(a.action, SimpleAction::Play { .. })));
}

// Fork tests.

fn play(id: CardId) -> Action {
    Action {
        actor: 0,
        action: SimpleAction::Play {
            trainer_card: trainer_from_id(id),
        },
        is_stack: false,
    }
}

fn target(in_play_idx: usize) -> Action {
    Action {
        actor: 0,
        action: SimpleAction::ChooseSweetHoneyTarget { in_play_idx },
        is_stack: true,
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

/// Player 0 to act on turn 3 with `own` against a Bulbasaur, `hand` in hand, both discard piles
/// empty.
fn honey_game(seed: u64, own: Vec<PlayedCard>, hand: &[CardId]) -> Game<'static> {
    let mut game = get_initialized_game_with_board(
        seed,
        0,
        3,
        own,
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    let mut state = game.get_state_clone();
    state.hands = [hand.iter().map(|id| get_card_by_enum(*id)).collect(), vec![]];
    state.discard_piles = [vec![], vec![]];
    game.set_state(state);
    game
}

/// A game from `state` whose gameplay RNG is seeded with `seed` (for the many-seed tests).
fn reseeded(state: &State, seed: u64) -> Game<'static> {
    Game::from_state(state.clone(), Vec::<Box<dyn Player>>::new(), seed)
}

/// `state` as Game adopts it (`Game::from_state` runs `State::sanitize_pending_choice_state`).
fn adopt(state: State) -> State {
    reseeded(&state, 0).get_state_clone()
}

/// An undamaged Bulbasaur Active, a Charmander with 30 damage and a Squirtle with 50 on the Bench.
fn mixed_board() -> Vec<PlayedCard> {
    vec![
        PlayedCard::from_id(CardId::A1001Bulbasaur),
        PlayedCard::from_id(CardId::A1033Charmander).with_damage(30),
        PlayedCard::from_id(CardId::A1053Squirtle).with_damage(50),
    ]
}

/// A Wailord ex at 500 HP with 480 damage: up to 24 heads heal exactly 20 each.
fn sponge() -> PlayedCard {
    PlayedCard::new(get_card_by_enum(CardId::B4197WailordEx), 480, 500, vec![], false, vec![])
}

fn remaining_hp(state: &State, in_play_idx: usize) -> u32 {
    state.in_play_pokemon[0][in_play_idx]
        .as_ref()
        .unwrap()
        .get_remaining_hp()
}

fn hp(game: &Game<'static>, in_play_idx: usize) -> u32 {
    remaining_hp(&game.get_state_clone(), in_play_idx)
}

fn has_will(state: &State) -> bool {
    serde_json::to_string(state).unwrap().contains("ForceFirstHeads")
}

fn legal(game: &Game<'static>, wanted: impl Fn(&SimpleAction) -> bool) -> Action {
    game.get_state_clone()
        .generate_possible_actions()
        .1
        .into_iter()
        .find(|action| wanted(&action.action))
        .expect("expected a legal action")
}

fn plays(name: &'static str) -> impl Fn(&SimpleAction) -> bool {
    move |action| matches!(action, SimpleAction::Play { trainer_card } if trainer_card.name == name)
}

fn heads(faces: &[bool]) -> u32 {
    faces.iter().filter(|face| **face).count() as u32
}

/// Upstream's `test_sweet_honey_needs_a_damaged_pokemon` on both printings (upstream's holds C1
/// 119 only): on its board, no Play with every Pokémon undamaged, and a Play once the Benched
/// Charmander is damaged.
#[test]
fn test_neither_printing_is_playable_without_a_damaged_pokemon() {
    let offers_play = |game: &Game<'static>| {
        game.get_state_clone()
            .generate_possible_actions()
            .1
            .iter()
            .any(|action| plays("Sweet Honey")(&action.action))
    };
    for honey in [CardId::C1119SweetHoney, CardId::C1152SweetHoney] {
        let mut game = get_test_game_with_board(
            vec![
                PlayedCard::from_id(CardId::A1001Bulbasaur),
                PlayedCard::from_id(CardId::A1033Charmander),
            ],
            vec![PlayedCard::from_id(CardId::A1033Charmander)],
        );
        let mut state = game.get_state_clone();
        state.hands[0] = vec![get_card_by_enum(honey)];
        game.set_state(state);
        assert!(!offers_play(&game), "{honey:?}: no damaged Pokémon");

        let mut state = game.get_state_clone();
        state.in_play_pokemon[0][1] =
            Some(PlayedCard::from_id(CardId::A1033Charmander).with_remaining_hp(10));
        game.set_state(state);
        assert!(offers_play(&game), "{honey:?}: a damaged Benched Pokémon");
    }
}

/// Right after the Play, on either printing: Sweet Honey is in the discard pile, its target phase
/// sits in the shared pre-coin slot with a Sweet Honey route, no coin choice is pending, nothing is
/// healed, and the only choices are the damaged Pokémon (the Charmander and Squirtle, not the
/// undamaged Bulbasaur), the same in every game.
#[test]
fn test_sweet_honey_offers_only_damaged_pokemon_before_any_coin() {
    for honey in [CardId::C1119SweetHoney, CardId::C1152SweetHoney] {
        for seed in 0..16 {
            let mut game = honey_game(seed, mixed_board(), &[honey]);
            let before = game.get_state_clone();
            game.apply_action(&legal(&game, plays("Sweet Honey")));
            let state = game.get_state_clone();
            let pending = state.pending_misty_target_choice.as_ref().expect("target phase");
            assert!(
                matches!(&pending.route, Some(MistySourceRoute::SweetHoney { sweet_honey })
                    if sweet_honey.id == trainer_from_id(honey).id),
                "{honey:?}: {pending:?}"
            );
            assert!(state.pending_trainer_coin_choice.is_none());
            let (actor, actions) = state.generate_possible_actions();
            assert_eq!(actor, 0);
            assert_eq!(actions, vec![target(1), target(2)], "{honey:?}, seed {seed}");
            for slot in 0..3 {
                assert_eq!(remaining_hp(&state, slot), remaining_hp(&before, slot));
            }
            assert!(state.hands[0].is_empty());
            assert_eq!(state.discard_piles[0], vec![get_card_by_enum(honey)]);
        }
    }
}

/// Plays a Red Card for player 0 against an opponent with an empty hand and 60 distinct cards in
/// the deck: the order they are shuffled into and the cards drawn fingerprint the gameplay RNG
/// `game` was left with, as in `misty_coin_plan_trace_test.rs`.
fn red_card_print(mut game: Game<'static>) -> (Vec<Card>, Vec<Card>) {
    use strum::IntoEnumIterator;

    let red_card = get_card_by_enum(CardId::PA006RedCard);
    let mut state = game.get_state_clone();
    state.hands[0].push(red_card.clone());
    state.hands[1].clear();
    state.decks[1].cards = CardId::iter().take(60).map(get_card_by_enum).collect();
    game.set_state(state);
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::Play {
            trainer_card: red_card.as_trainer(),
        },
        is_stack: false,
    });
    let state = game.get_state_clone();
    (state.decks[1].cards.clone(), state.hands[1].clone())
}

/// The twin of `misty_precoin_target_test.rs`'s rejected target: an undamaged (unoffered) target,
/// an empty slot and Misty's own target action are refused, and the gameplay RNG is untouched: the
/// real choice then heals what it heals without the attempts, and a Red Card played after it
/// shuffles and draws the same in both games (the heal alone often matches after a different draw).
#[test]
fn test_sweet_honey_unoffered_target_is_rejected_before_the_coins() {
    let seed = 91;
    let mut rejected = honey_game(seed, mixed_board(), &[CardId::C1119SweetHoney]);
    let state = rejected.get_state_clone();
    rejected.apply_action(&play(CardId::C1119SweetHoney));
    let misty_target = Action {
        actor: 0,
        action: SimpleAction::ChooseMistyTarget { in_play_idx: 1 },
        is_stack: true,
    };
    for invalid in [target(0), target(3), misty_target] {
        let result = catch_unwind(AssertUnwindSafe(|| rejected.apply_action(&invalid)));
        assert!(result.is_err(), "{invalid:?} must be refused");
    }
    rejected.apply_action(&target(2));

    let mut control = honey_game(seed, mixed_board(), &[CardId::C1119SweetHoney]);
    control.set_state(state);
    control.apply_action(&play(CardId::C1119SweetHoney));
    control.apply_action(&target(2));
    assert_eq!(
        format!("{:?}", rejected.get_state_clone()),
        format!("{:?}", control.get_state_clone()),
        "the real choice must heal as it does without the rejected attempts"
    );
    assert_eq!(
        red_card_print(rejected),
        red_card_print(control),
        "a rejected target must not advance the gameplay RNG"
    );
}

/// The Play flips no coin, on either printing: the staged target phase, adopted into a game seeded
/// the same, heals the chosen Squirtle exactly as the whole line does, and a Red Card played after
/// each shuffles and draws the same (the heal alone often matches after a different draw). The twin
/// of `misty_precoin_target_test.rs`'s same-seed check.
#[test]
fn test_sweet_honeys_play_draws_nothing_from_the_gameplay_rng() {
    let squirtle = |action: &SimpleAction| {
        matches!(action, SimpleAction::ChooseSweetHoneyTarget { in_play_idx: 2 })
    };
    for honey in [CardId::C1119SweetHoney, CardId::C1152SweetHoney] {
        let base = honey_game(0, mixed_board(), &[honey]).get_state_clone();
        let mut healed = std::collections::BTreeSet::new();
        for seed in 0..64 {
            let mut whole = reseeded(&base, seed);
            whole.apply_action(&legal(&whole, plays("Sweet Honey")));
            let staged = whole.get_state_clone();
            whole.apply_action(&legal(&whole, squirtle));
            healed.insert(hp(&whole, 2) - 10);

            let mut adopted = reseeded(&staged, seed);
            adopted.apply_action(&legal(&adopted, squirtle));
            assert_eq!(
                adopted.get_state_clone().in_play_pokemon,
                whole.get_state_clone().in_play_pokemon,
                "{honey:?}, seed {seed}: the Play must not flip a coin"
            );
            assert_eq!(
                red_card_print(adopted),
                red_card_print(whole),
                "{honey:?}, seed {seed}: the Play must not draw from the gameplay RNG"
            );
        }
        assert!(
            healed.contains(&0) && healed.len() > 1,
            "{honey:?}: the coins follow the target; healed {healed:?}"
        );
    }
}

/// No heads cap: on a target with 480 damage, more than 8 heads (upstream's cap) occur across
/// 4096 games, and the heal never exceeds the damage.
#[test]
fn test_sweet_honey_has_no_heads_cap() {
    let base = honey_game(0, vec![sponge()], &[CardId::C1119SweetHoney]).get_state_clone();
    let mut most = 0;
    for seed in 0..4096 {
        let mut game = reseeded(&base, seed);
        game.apply_action(&play(CardId::C1119SweetHoney));
        game.apply_action(&target(0));
        let healed = hp(&game, 0) - 20;
        assert!(healed % 20 == 0 && healed <= 480, "seed {seed}: healed {healed}");
        most = most.max(healed);
    }
    assert!(most > 160, "more than 8 heads must be possible; most healed {most}");
}

/// `action`'s exact forecast from `state`: each branch's probability and the state it leaves.
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

/// Real play's heal frequencies over 4096 games match `probabilities` over `heals`.
fn assert_real_play_matches(base: &State, setup: &[Action], heals: &[u32], probabilities: &[f64]) {
    let mut counts = vec![0usize; heals.len()];
    for seed in 0..4096 {
        let mut game = reseeded(base, seed);
        let before = hp(&game, 0);
        for action in setup {
            game.apply_action(action);
        }
        game.apply_action(&target(0));
        let healed = hp(&game, 0) - before;
        let index = heals
            .iter()
            .position(|heal| *heal == healed)
            .unwrap_or_else(|| panic!("seed {seed}: healed {healed}, not one of {heals:?}"));
        counts[index] += 1;
    }
    for ((count, probability), heal) in counts.iter().zip(probabilities).zip(heals) {
        let frequency = *count as f64 / 4096.0;
        assert!(
            (frequency - probability).abs() < 0.03,
            "heal {heal}: frequency {frequency} v probability {probability}"
        );
    }
}

/// Search, without Luxury Coin: the Play is one exact branch that only stages the target, and the
/// target is priced exactly. A Charmander with 50 damage heals 0, 20 or 40 on 0, 1 or 2 heads, and
/// all 50 on 3 or more, one class of 1/8; real play draws heals at those frequencies.
#[test]
fn test_sweet_honey_forecast_is_exact_and_matches_real_play() {
    let base = honey_game(
        0,
        vec![PlayedCard::from_id(CardId::A1033Charmander).with_damage(50)],
        &[CardId::C1119SweetHoney],
    )
    .get_state_clone();
    let (probabilities, mut staged) = branches(&base, &play(CardId::C1119SweetHoney));
    assert_eq!(probabilities, vec![1.0]);
    let staged = staged.remove(0);
    assert!(staged.pending_misty_target_choice.is_some());
    assert_eq!(remaining_hp(&staged, 0), 10);

    let (probabilities, successors) = branches(&staged, &target(0));
    let heals = successors
        .iter()
        .map(|next| {
            assert!(next.pending_misty_target_choice.is_none());
            assert!(next.move_generation_stack.is_empty());
            remaining_hp(next, 0) - 10
        })
        .collect::<Vec<_>>();
    assert_eq!(probabilities, vec![0.5, 0.25, 0.125, 0.125]);
    assert_eq!(heals, vec![0, 20, 40, 50]);
    assert_real_play_matches(&base, &[play(CardId::C1119SweetHoney)], &heals, &probabilities);
}

/// Will: "the first coin flip will definitely be heads". Played before Sweet Honey, it waits
/// through the Play (which flips nothing) and forces the target's first coin: every heal is at
/// least 20, Will is used once, and later coins stay random. The exact forecast drops the
/// zero-heads branch and renormalises the rest, and real play matches it.
#[test]
fn test_will_forces_sweet_honeys_first_coin_at_the_target() {
    let base = honey_game(
        0,
        vec![PlayedCard::from_id(CardId::A1033Charmander).with_damage(50)],
        &[CardId::A4156Will, CardId::C1119SweetHoney],
    )
    .get_state_clone();
    let mut saw_more_than_one = false;
    for seed in 0..128 {
        let mut game = reseeded(&base, seed);
        game.apply_action(&legal(&game, plays("Will")));
        game.apply_action(&legal(&game, plays("Sweet Honey")));
        assert!(has_will(&game.get_state_clone()), "the Play flips no coin");
        game.apply_action(&target(0));
        let healed = hp(&game, 0) - 10;
        assert!(healed >= 20, "seed {seed}: Will must force the first coin to heads");
        assert!(!has_will(&game.get_state_clone()), "Will is used once");
        saw_more_than_one |= healed > 20;
    }
    assert!(saw_more_than_one, "later coins must stay random");

    let mut game = reseeded(&base, 0);
    game.apply_action(&play(CardId::A4156Will));
    game.apply_action(&play(CardId::C1119SweetHoney));
    let (probabilities, successors) = branches(&game.get_state_clone(), &target(0));
    let heals = successors
        .iter()
        .map(|next| {
            assert!(!has_will(next));
            remaining_hp(next, 0) - 10
        })
        .collect::<Vec<_>>();
    assert_eq!(probabilities, vec![0.5, 0.25, 0.25]);
    assert_eq!(heals, vec![20, 40, 50]);
    assert_real_play_matches(
        &base,
        &[play(CardId::A4156Will), play(CardId::C1119SweetHoney)],
        &heals,
        &probabilities,
    );
}

/// Heal Block (Claydol A3a 031, "Pokémon (both yours and your opponent's) can't be healed."), on
/// either side: Sweet Honey is still played on a damaged Pokémon, as Potion is, and the target is
/// offered. Its coins are still flipped, so Will is used and, with Gholdengo, Luxury Coin is
/// offered, but nothing is healed: the forecast is one branch.
#[test]
fn test_sweet_honey_under_heal_block_flips_and_heals_nothing() {
    for claydol_side in [0, 1] {
        for gholdengo in [false, true] {
            let ctx = format!("Claydol {claydol_side}, Gholdengo {gholdengo}");
            let mut boards = [
                vec![PlayedCard::from_id(CardId::A1033Charmander).with_damage(50)],
                vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
            ];
            boards[claydol_side].push(PlayedCard::from_id(CardId::A3a031Claydol));
            if gholdengo {
                boards[0].push(PlayedCard::from_id(CardId::B4a051Gholdengo));
            }
            let [ours, theirs] = boards;
            let mut game = get_initialized_game_with_board(0, 0, 3, ours, theirs);
            let mut state = game.get_state_clone();
            state.hands[0] = vec![
                get_card_by_enum(CardId::A4156Will),
                get_card_by_enum(CardId::C1119SweetHoney),
            ];
            game.set_state(state);
            game.apply_action(&legal(&game, plays("Will")));
            game.apply_action(&legal(&game, plays("Sweet Honey")));
            let staged = game.get_state_clone();
            assert_eq!(staged.generate_possible_actions().1, vec![target(0)], "{ctx}");
            if !gholdengo {
                let (probabilities, successors) = branches(&staged, &target(0));
                assert_eq!(probabilities, vec![1.0], "{ctx}");
                assert_eq!(remaining_hp(&successors[0], 0), 10, "{ctx}");
                assert!(!has_will(&successors[0]), "{ctx}");
            }
            game.apply_action(&target(0));
            if gholdengo {
                let paused = game.get_state_clone();
                let pending = paused.pending_trainer_coin_choice.as_ref().expect(&ctx);
                assert!(pending.flips[0], "{ctx}: Will forced the first coin");
                game.apply_action(&keep());
            }
            let state = game.get_state_clone();
            assert_eq!(remaining_hp(&state, 0), 10, "{ctx}");
            assert!(!has_will(&state), "{ctx}: Will is used on the coins");
            assert!(state.move_generation_stack.is_empty(), "{ctx}");
        }
    }
}

/// Luxury Coin, both Gholdengo printings: the Play stages the target (no panic, no coin choice
/// yet); the target fixes the Wailord ex and pauses on the complete batch with nothing healed;
/// Keep heals 20 per heads of that batch, Reroll per heads of a fresh one (spending Luxury Coin
/// and recording both batches); the Play's cost is paid once.
#[test]
fn test_luxury_coin_covers_sweet_honey_with_its_target_fixed() {
    for gholdengo in [CardId::B4a051Gholdengo, CardId::B4a109Gholdengo] {
        for seed in 0..32 {
            for use_reroll in [false, true] {
                let ctx = format!("{gholdengo:?}, seed {seed}, reroll {use_reroll}");
                let mut game = honey_game(
                    seed,
                    vec![
                        PlayedCard::from_id(CardId::A1001Bulbasaur),
                        sponge(),
                        PlayedCard::from_id(gholdengo),
                    ],
                    &[CardId::C1119SweetHoney],
                );
                game.apply_action(&legal(&game, plays("Sweet Honey")));
                let staged = game.get_state_clone();
                assert!(staged.pending_misty_target_choice.is_some(), "{ctx}");
                assert!(staged.pending_trainer_coin_choice.is_none(), "{ctx}");
                assert_eq!(staged.generate_possible_actions().1, vec![target(1)], "{ctx}");

                game.apply_action(&target(1));
                let paused = game.get_state_clone();
                assert!(paused.pending_misty_target_choice.is_none(), "{ctx}");
                let pending = paused.pending_trainer_coin_choice.as_ref().expect(&ctx);
                assert_eq!(pending.misty_target_in_play_idx, Some(1), "{ctx}");
                assert!(
                    matches!(&pending.route, Some(TrainerCoinEffectRoute::Direct { trainer })
                        if trainer.name == "Sweet Honey"),
                    "{ctx}"
                );
                assert_eq!(pending.luxury_coin_in_play_idx, 2, "{ctx}");
                assert_eq!(remaining_hp(&paused, 1), 20, "{ctx}: nothing healed yet");
                let initial = pending.flips.clone();
                assert_eq!(initial.last(), Some(&false), "{ctx}: flipped until tails");

                let healed_heads = if use_reroll {
                    game.apply_action(&reroll(2));
                    let state = game.get_state_clone();
                    assert!(state.luxury_coin_used_this_turn[0], "{ctx}");
                    let record = game.luxury_coin_resolution_history().last().unwrap().clone();
                    assert_eq!(record.initial_faces, initial, "{ctx}");
                    heads(record.replacement_faces.as_ref().unwrap())
                } else {
                    game.apply_action(&keep());
                    heads(&initial)
                };
                let state = game.get_state_clone();
                assert_eq!(remaining_hp(&state, 1), 20 + 20 * healed_heads, "{ctx}");
                assert_eq!(remaining_hp(&state, 0), 70, "{ctx}");
                assert_eq!(
                    state.discard_piles[0],
                    vec![get_card_by_enum(CardId::C1119SweetHoney)],
                    "{ctx}: the Play's cost is paid once"
                );
                assert!(state.pending_trainer_coin_choice.is_none(), "{ctx}");
                assert!(state.move_generation_stack.is_empty(), "{ctx}");
            }
        }
    }
}

/// Luxury Coin in search: the Play is one exact branch; the target's batch and a Reroll's are
/// explicitly unpriced (infinitely many observable face sequences, as for Misty), and Keep is
/// priced exactly on the batch shown.
#[test]
fn test_luxury_coin_search_prices_the_keep_and_leaves_the_batches_unpriced() {
    for seed in 0..8 {
        let mut game = honey_game(
            seed,
            vec![
                PlayedCard::from_id(CardId::A1001Bulbasaur),
                sponge(),
                PlayedCard::from_id(CardId::B4a051Gholdengo),
            ],
            &[CardId::C1119SweetHoney],
        );
        let base = game.get_state_clone();
        let (probabilities, staged) = branches(&base, &play(CardId::C1119SweetHoney));
        assert_eq!(probabilities, vec![1.0]);
        assert!(staged[0].pending_misty_target_choice.is_some());
        let unpriced = |state: &State, action: &Action| match try_forecast_action(state, action) {
            Ok(_) => panic!("{action:?} must stay unpriced"),
            Err(error) => assert!(matches!(
                error.kind,
                UnpricedForecastKind::TrainerCoinObservableGeometric { .. }
            )),
        };
        unpriced(&staged[0], &target(1));

        game.apply_action(&play(CardId::C1119SweetHoney));
        game.apply_action(&target(1));
        let paused = game.get_state_clone();
        let shown = heads(&paused.pending_trainer_coin_choice.as_ref().unwrap().flips);
        let (probabilities, kept) = branches(&paused, &keep());
        assert_eq!(probabilities, vec![1.0]);
        assert_eq!(remaining_hp(&kept[0], 1), 20 + 20 * shown);
        assert!(kept[0].pending_trainer_coin_choice.is_none());
        unpriced(&paused, &reroll(2));
    }
}

/// With Luxury Coin already used this turn, Sweet Honey takes the plain path: no coin choice, the
/// heal lands at once, and there is still no cap.
#[test]
fn test_spent_luxury_coin_leaves_sweet_honey_on_the_uncapped_plain_path() {
    let mut base = honey_game(
        0,
        vec![sponge(), PlayedCard::from_id(CardId::B4a051Gholdengo)],
        &[CardId::C1119SweetHoney],
    )
    .get_state_clone();
    base.luxury_coin_used_this_turn[0] = true;
    let mut most = 0;
    for seed in 0..4096 {
        let mut game = reseeded(&base, seed);
        game.apply_action(&play(CardId::C1119SweetHoney));
        game.apply_action(&target(0));
        let state = game.get_state_clone();
        assert!(state.pending_trainer_coin_choice.is_none(), "seed {seed}");
        most = most.max(remaining_hp(&state, 0) - 20);
    }
    assert!(most > 160, "spent Luxury Coin must not cap the heads; most healed {most}");
}

/// Will with Luxury Coin: the initial batch starts with heads every time and uses Will; a Reroll is
/// a fresh batch that Will doesn't touch (some start with tails), as for Misty.
#[test]
fn test_will_with_luxury_coin_forces_only_the_initial_batch() {
    let mut saw_tails_first = false;
    for seed in 0..64 {
        let mut game = honey_game(
            seed,
            vec![
                PlayedCard::from_id(CardId::A1001Bulbasaur),
                sponge(),
                PlayedCard::from_id(CardId::B4a051Gholdengo),
            ],
            &[CardId::A4156Will, CardId::C1119SweetHoney],
        );
        game.apply_action(&legal(&game, plays("Will")));
        game.apply_action(&legal(&game, plays("Sweet Honey")));
        assert!(has_will(&game.get_state_clone()), "seed {seed}");
        game.apply_action(&target(1));
        let paused = game.get_state_clone();
        assert!(paused.pending_trainer_coin_choice.as_ref().unwrap().flips[0], "seed {seed}");
        assert!(!has_will(&paused), "seed {seed}");
        game.apply_action(&reroll(2));
        let record = game.luxury_coin_resolution_history().last().unwrap().clone();
        saw_tails_first |= !record.replacement_faces.unwrap()[0];
    }
    assert!(saw_tails_first, "a Reroll is not forced");
}

/// The target phase and the paused batch survive a serde round trip and Game adoption with their
/// target; the opponent sees both without the route; and a redacted opponent search state, once
/// adopted, can't resume either (the slot is dropped and its frame popped). INFORMATION_MODEL stays
/// v8.
#[test]
fn test_sweet_honey_pending_states_round_trip_and_are_redacted_for_the_opponent() {
    let mut game = honey_game(
        7,
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            sponge(),
            PlayedCard::from_id(CardId::B4a051Gholdengo),
        ],
        &[CardId::C1152SweetHoney],
    );
    game.apply_action(&play(CardId::C1152SweetHoney));
    let staged = game.get_state_clone();
    game.apply_action(&target(1));
    let paused = game.get_state_clone();
    for (name, referee) in [("target phase", &staged), ("coin pause", &paused)] {
        let json = serde_json::to_string(referee).unwrap();
        let restored: State = serde_json::from_str(&json).unwrap();
        assert_eq!(&restored, referee, "{name}");
        let adopted = adopt(restored);
        assert_eq!(&adopted, referee, "{name}: a valid referee state is kept whole");

        let actor = PlayerObservation::from_state(referee, 0, &RevealedKnowledge::default());
        let opponent = PlayerObservation::from_state(referee, 1, &RevealedKnowledge::default());
        assert_eq!(opponent.information_model, "closed-counts-unpriced-v8");
        assert_eq!(INFORMATION_MODEL, "closed-counts-unpriced-v8");
        let has_route = |observation: &PlayerObservation| {
            let state = observation.visible_state();
            match name {
                "target phase" => state.pending_misty_target_choice.as_ref().unwrap().route.is_some(),
                _ => state.pending_trainer_coin_choice.as_ref().unwrap().route.is_some(),
            }
        };
        assert!(has_route(&actor) && !has_route(&opponent), "{name}");

        let adopted = adopt(opponent.search_state(&mut StdRng::seed_from_u64(2)));
        assert!(adopted.pending_misty_target_choice.is_none(), "{name}");
        assert!(adopted.pending_trainer_coin_choice.is_none(), "{name}");
        assert!(adopted.move_generation_stack.is_empty(), "{name}: the frame is popped");
    }
    assert_eq!(
        paused.pending_trainer_coin_choice.as_ref().unwrap().misty_target_in_play_idx,
        Some(1)
    );
}

/// Adoption (`State::sanitize_pending_choice_state`) drops every malformed Sweet Honey state and
/// pops its frame: a target frame offering an undamaged Pokémon, an empty slot or Misty's target
/// action; a Sweet Honey route on another card's Play; Misty's route with Sweet Honey's frame; and
/// a paused batch whose fixed target is undamaged, empty or missing, or whose route is Penny.
#[test]
fn test_adoption_drops_malformed_sweet_honey_states() {
    let mut game = honey_game(
        5,
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            sponge(),
            PlayedCard::from_id(CardId::B4a051Gholdengo),
        ],
        &[CardId::C1119SweetHoney],
    );
    game.apply_action(&play(CardId::C1119SweetHoney));
    let staged = game.get_state_clone();
    game.apply_action(&target(1));
    let paused = game.get_state_clone();
    assert_eq!(adopt(staged.clone()), staged);
    assert_eq!(adopt(paused.clone()), paused);

    let with_frame = |choice: SimpleAction| {
        let mut state = staged.clone();
        state.move_generation_stack.last_mut().unwrap().1 = vec![choice];
        state
    };
    let misty = trainer_from_id(CardId::A1220Misty);
    let mut misty_route = with_frame(SimpleAction::ChooseSweetHoneyTarget { in_play_idx: 1 });
    let pending = misty_route.pending_misty_target_choice.as_mut().unwrap();
    pending.original_action = SimpleAction::Play {
        trainer_card: misty.clone(),
    };
    pending.route = Some(MistySourceRoute::Direct { misty });
    let mut other_card = staged.clone();
    other_card.pending_misty_target_choice.as_mut().unwrap().original_action = SimpleAction::Play {
        trainer_card: trainer_from_id(CardId::PA001Potion),
    };
    for (name, state) in [
        ("undamaged target", with_frame(SimpleAction::ChooseSweetHoneyTarget { in_play_idx: 0 })),
        ("empty slot", with_frame(SimpleAction::ChooseSweetHoneyTarget { in_play_idx: 3 })),
        ("Misty's action", with_frame(SimpleAction::ChooseMistyTarget { in_play_idx: 1 })),
        ("another card's Play", other_card),
        ("Misty's route", misty_route),
    ] {
        let state = adopt(state);
        assert!(state.pending_misty_target_choice.is_none(), "{name}");
        assert!(state.move_generation_stack.is_empty(), "{name}: the frame is popped");
    }

    let with_target = |index: Option<usize>| {
        let mut state = paused.clone();
        state.pending_trainer_coin_choice.as_mut().unwrap().misty_target_in_play_idx = index;
        state
    };
    let mut penny_route = paused.clone();
    let pending = penny_route.pending_trainer_coin_choice.as_mut().unwrap();
    pending.original_action = SimpleAction::Play {
        trainer_card: trainer_from_id(CardId::A3b069Penny),
    };
    pending.route = Some(TrainerCoinEffectRoute::Penny {
        copied: trainer_from_id(CardId::C1119SweetHoney),
        shuffle_owner: 1,
    });
    for (name, state) in [
        ("undamaged target", with_target(Some(0))),
        ("empty target", with_target(Some(3))),
        ("no target", with_target(None)),
        ("Penny route", penny_route),
    ] {
        let state = adopt(state);
        assert!(state.pending_trainer_coin_choice.is_none(), "{name}");
        assert!(state.move_generation_stack.is_empty(), "{name}: the frame is popped");
    }
}

/// The bots at every Sweet Honey root (km3 and WeightedRandomPlayer, through `create_players`):
/// the main phase with Sweet Honey in hand, its target with two damaged Pokémon, and, with
/// Gholdengo, Keep or Reroll; with and without Will. Each picks an offered action, without panic.
#[test]
fn test_bots_decide_at_every_sweet_honey_root() {
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
            let mut own = mixed_board();
            if gholdengo {
                own.push(PlayedCard::from_id(CardId::B4a051Gholdengo));
            }
            let hand: &[CardId] = if will {
                &[CardId::A4156Will, CardId::C1119SweetHoney]
            } else {
                &[CardId::C1119SweetHoney]
            };
            let mut game = honey_game(3, own, hand);
            if will {
                game.apply_action(&legal(&game, plays("Will")));
            }
            let _ = decide(&game, &code);
            game.apply_action(&legal(&game, plays("Sweet Honey")));
            let chosen = decide(&game, &code);
            assert!(matches!(chosen.action, SimpleAction::ChooseSweetHoneyTarget { .. }), "{ctx}");
            game.apply_action(&chosen);
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
            assert!(state.pending_misty_target_choice.is_none(), "{ctx}");
            assert!(state.pending_trainer_coin_choice.is_none(), "{ctx}");
        }
    }
}

/// Both printings are Complete, with no limitation of their own; Gholdengo's unpriced-batch
/// limitation names Sweet Honey on both its printings.
#[test]
fn test_sweet_honey_printings_report_complete() {
    for id in [CardId::C1119SweetHoney, CardId::C1152SweetHoney] {
        assert_eq!(get_implementation_status(id), ImplementationStatus::Complete, "{id:?}");
        assert!(implementation_limitations(id).is_empty(), "{id:?}");
    }
    let unpriced = "(Misty, Sweet Honey, Team Rocket Grunt, and Team Rocket's Researcher)";
    for id in [CardId::B4a051Gholdengo, CardId::B4a109Gholdengo] {
        assert!(
            implementation_limitations(id)
                .iter()
                .any(|line| line.contains(unpriced)),
            "{id:?}"
        );
    }
}
