//! The play-out chooser (`kx<N>`, engine/src/players/playout_player.rs; branch claude/playout-pilot, Oct 2). Written
//! before the player: the parse of its code, an immediate win taken, km3's move kept within the noise, the drops of the
//! candidate cap reported, no information leak (the same observation over different hidden cards gives the same
//! evaluation and the same move, also through `Game`), and determinism (same seeds, same moves).
//! Added with the fixes of round 1 (Oct 3), to prove what the README claims: REALISTIC reads no list (two pilots built
//! with different opponent lists report alike; a hidden card from outside the opponent's list changes no choice); LAB on
//! a pool pairing uses the exact list, and LAB against a list outside the pool is REALISTIC exactly; a path under
//! decks/brews is refused for KX_EXTRA_LISTS (the variable itself: playout_pilot_extra_lists_test.rs); with a time budget
//! no switch before 8 rounds; an omniscient call keeps km's move and is counted.
//! Round 2 (Oct 3): a copy of a brew's or one of Dustin's lists is refused by its cards wherever it lives, decks/dustin
//! paths and resolved paths too, and unreadable protected folders; the time-budget test runs in a 2-thread pool, so it
//! checks the same thing on any machine. Every pilot here is built without the environment's extra lists.
use std::collections::BTreeMap;

use deckgym::actions::{Action, SimpleAction};
use deckgym::card_ids::CardId;
use deckgym::database::get_card_by_enum;
use deckgym::models::{EnergyType, PlayedCard};
use deckgym::observation::{PlayerObservation, RevealedKnowledge};
use deckgym::players::playout_player::{
    parse_extra_lists, parse_extra_lists_against, protected_lists, DecisionReport, Knowledge, PlayoutParams, PlayoutPlayer,
};
use deckgym::players::{create_players, parse_player_code, Player, PlayerCode};
use deckgym::test_support::{get_test_game_with_board, load_test_decks};
use deckgym::{Deck, Game, State};
use rand::{rngs::StdRng, SeedableRng};

/// Small play-out settings for tests: 4 play-outs per candidate, at most 4 candidates.
fn small(knowledge: Knowledge, z: f64) -> PlayoutParams {
    PlayoutParams { rollouts: 4, cap: 4, z, knowledge, ..PlayoutParams::new(3) }
}

fn pilot(params: PlayoutParams) -> PlayoutPlayer {
    let (deck_a, deck_b) = load_test_decks();
    fresh(deck_a, deck_b, params)
}

/// A pilot with no extra lists, whatever the shell's KX_EXTRA_LISTS says.
fn fresh(deck: Deck, opponent_list: Deck, params: PlayoutParams) -> PlayoutPlayer {
    PlayoutPlayer::with_extra_lists(deck, opponent_list, params, Vec::new())
}

/// km3's own choice for `actor` at `state`, with the decision randomness the pilot is given.
fn km3_choice(state: &State, actor: usize, seed: u64) -> Action {
    let (deck_a, deck_b) = load_test_decks();
    let mut km3 = create_players(deck_a, deck_b, vec![parse_player_code("km3").unwrap(), parse_player_code("km3").unwrap()])
        .remove(actor);
    let observation = PlayerObservation::from_state(state, actor, &RevealedKnowledge::default());
    let actions = state.generate_possible_actions().1;
    km3.decision_fn(&mut StdRng::seed_from_u64(seed), &observation, &actions)
}

/// A battle position (turn 3 or later) where player 0 decides among three or more distinct moves: km3 plays a test-deck
/// game from `seed` until one comes.
fn midgame(seed: u64) -> State {
    let (deck_a, deck_b) = load_test_decks();
    midgame_with(deck_a, deck_b, seed)
}

/// A pool list by its file under decks/screen/opponents (the tests run in engine/).
fn pool_deck(name: &str) -> Deck {
    Deck::from_file(&format!("../decks/screen/opponents/{name}.txt")).unwrap()
}

/// Every field of a decision's report but its time, as text.
fn fingerprint(r: &DecisionReport) -> String {
    let candidates: Vec<String> =
        r.candidates.iter().map(|c| format!("{:?} {} {} {}", c.action, c.score, c.diff, c.se)).collect();
    let dropped: Vec<String> = r.dropped.iter().map(|d| format!("{} / {}", d.label, d.reason)).collect();
    format!(
        "{} | t{} s{} | {:?} | {:?} | km {} chosen {} | {} | rounds {} failed {} | {:?}",
        r.knowledge, r.turn, r.actor, candidates, dropped, r.km3, r.chosen, r.reason, r.rounds, r.failed_rounds, r.lists
    )
}

/// The same, without the knowledge label.
fn fingerprint_without_label(r: &DecisionReport) -> String {
    fingerprint(r).replacen(&r.knowledge, "", 1)
}

/// `midgame` for any two lists, player 0 on `deck_a`.
fn midgame_with(deck_a: Deck, deck_b: Deck, seed: u64) -> State {
    let km3 = || parse_player_code("km3").unwrap();
    let mut game = Game::new(create_players(deck_a, deck_b, vec![km3(), km3()]), seed);
    loop {
        assert!(!game.is_game_over(), "seed {seed}: the game ended before a position came");
        let state = game.get_state_clone();
        let (actor, actions) = state.generate_possible_actions();
        let distinct: std::collections::BTreeSet<String> = actions.iter().map(|a| format!("{:?}", a.action)).collect();
        if actor == 0 && state.turn_count >= 3 && state.current_player == 0 && distinct.len() >= 3 {
            return state;
        }
        game.play_tick();
    }
}

#[test]
fn the_code_parses_with_defaults_and_parameters_and_leaves_the_other_codes_alone() {
    let PlayerCode::KX { params } = parse_player_code("kx3").unwrap() else { panic!("kx3 is not KX") };
    assert_eq!(params, PlayoutParams::new(3));
    assert_eq!((params.rollouts, params.cap, params.z, params.knowledge, params.budget_ms, params.trace),
               (16, 12, 2.0, Knowledge::Realistic, 0, false));
    let PlayerCode::KX { params } = parse_player_code("KX3_r8_c5_z1.5_lab_t30_trace").unwrap() else { panic!() };
    assert_eq!((params.depth, params.rollouts, params.cap, params.z, params.knowledge, params.budget_ms, params.trace),
               (3, 8, 5, 1.5, Knowledge::Lab, 30_000, true));
    for bad in ["kx", "kx3_q1", "kx3_r0", "kx3_c1", "kxx3", "kx3_"] {
        assert!(parse_player_code(bad).is_err(), "{bad} should not parse");
    }
    assert_eq!(parse_player_code("km3").unwrap(), PlayerCode::KM { max_depth: 3 });
    assert_eq!(parse_player_code("k3").unwrap(), PlayerCode::K { max_depth: 3 });
}

/// Mega Absol ex with Darkness Claw paid for, against the opponent's only Pokémon, Abra: the attack knocks it out and
/// wins. With the noise threshold at 0 the pilot must find it: every play-out after the attack is a win.
#[test]
fn an_immediate_win_is_taken() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B1151MegaAbsolEx).with_energy(vec![EnergyType::Darkness, EnergyType::Darkness])],
        vec![PlayedCard::from_id(CardId::A1115Abra)],
    );
    let mut state = game.get_state_clone();
    state.move_generation_stack.clear();
    game.set_state(state);
    let state = game.get_state_clone();
    let actions = state.generate_possible_actions().1;
    assert!(actions.len() >= 2, "the position offers alternatives: {actions:?}");
    for knowledge in [Knowledge::Lab, Knowledge::Realistic] {
        let mut p = pilot(small(knowledge, 0.0));
        let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
        let report = p.evaluate(&mut StdRng::seed_from_u64(5), &observation, &actions);
        let chosen = &report.candidates[report.chosen].action;
        assert!(matches!(&chosen.action, SimpleAction::Attack(a) if a.title == "Darkness Claw"), "{knowledge:?}: chose {chosen:?}");
        assert_eq!(report.candidates[report.chosen].score, 1.0, "{knowledge:?}: every play-out after the knockout is a win");
    }
}

/// With an unreachable noise threshold the pilot always keeps km3's move; with the threshold at 0 it keeps the move with
/// the best play-out score (km3's on a tie).
#[test]
fn within_the_noise_km3s_move_is_kept() {
    for seed in [3u64, 11] {
        let state = midgame(seed);
        let actions = state.generate_possible_actions().1;
        let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
        let km3 = km3_choice(&state, 0, 9);
        let report = pilot(small(Knowledge::Lab, 1e9)).evaluate(&mut StdRng::seed_from_u64(9), &observation, &actions);
        assert_eq!(report.candidates[report.km3].action, km3, "seed {seed}: the report's km3 move is km3's");
        assert_eq!(report.chosen, report.km3, "seed {seed}: kept km3's move: {}", report.reason);
        let open = pilot(small(Knowledge::Lab, 0.0)).evaluate(&mut StdRng::seed_from_u64(9), &observation, &actions);
        let best = open.candidates.iter().map(|c| c.score).fold(f64::MIN, f64::max);
        assert_eq!(open.candidates[open.chosen].score, best, "seed {seed}: with no threshold, the best play-out score");
        if open.candidates[open.km3].score == best {
            assert_eq!(open.chosen, open.km3, "seed {seed}: a tie keeps km3's move");
        }
    }
}

/// The candidate cap: km3's move is always kept, and every dropped move is named with its reason.
#[test]
fn a_capped_candidate_list_keeps_km3s_move_and_names_the_drops() {
    let state = midgame(3);
    let actions = state.generate_possible_actions().1;
    let distinct: std::collections::BTreeSet<String> = actions.iter().map(|a| format!("{:?}", a.action)).collect();
    let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
    let report = pilot(PlayoutParams { cap: 2, ..small(Knowledge::Lab, 2.0) })
        .evaluate(&mut StdRng::seed_from_u64(9), &observation, &actions);
    assert_eq!(report.candidates.len(), 2);
    assert_eq!(report.candidates[report.km3].action, km3_choice(&state, 0, 9));
    assert_eq!(report.candidates.len() + report.dropped.len(), distinct.len(), "every distinct move is a candidate or a drop");
    assert!(report.dropped.iter().all(|d| !d.reason.is_empty()));
}

/// Swap a card between the opponent's hand and deck, and reverse both decks: the hidden cards change, the observation
/// doesn't.
fn other_hidden_cards(state: &State) -> State {
    let mut other = state.clone();
    let opponent = 1;
    if let (Some(h), Some(d)) = (other.hands[opponent].first().cloned(), other.decks[opponent].cards.iter().position(|c| {
        Some(c) != other.hands[opponent].first()
    })) {
        let deck_card = other.decks[opponent].cards[d].clone();
        other.decks[opponent].cards[d] = h;
        other.hands[opponent][0] = deck_card;
    }
    other.decks[0].cards.reverse();
    other.decks[1].cards.reverse();
    other
}

#[test]
fn the_choice_cannot_depend_on_the_opponents_hand_or_either_decks_order() {
    let state = midgame(3);
    let other = other_hidden_cards(&state);
    assert!(other.hands[1] != state.hands[1] || other.decks[1].cards != state.decks[1].cards, "the hidden cards differ");
    let (obs_a, obs_b) = (
        PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default()),
        PlayerObservation::from_state(&other, 0, &RevealedKnowledge::default()),
    );
    assert_eq!(obs_a, obs_b, "the same observation");
    let actions = state.generate_possible_actions().1;
    for knowledge in [Knowledge::Lab, Knowledge::Realistic] {
        let a = pilot(small(knowledge, 2.0)).evaluate(&mut StdRng::seed_from_u64(21), &obs_a, &actions);
        let b = pilot(small(knowledge, 2.0)).evaluate(&mut StdRng::seed_from_u64(21), &obs_b, &actions);
        let scores = |r: &deckgym::players::playout_player::DecisionReport| {
            r.candidates.iter().map(|c| (format!("{:?}", c.action), c.score, c.diff)).collect::<Vec<_>>()
        };
        assert_eq!(scores(&a), scores(&b), "{knowledge:?}: the same play-out results");
        assert_eq!(a.chosen, b.chosen, "{knowledge:?}: the same choice");
        // Through Game: the game hands the pilot only its observation.
        let code = PlayerCode::KX { params: small(knowledge, 2.0) };
        let (deck_a, deck_b) = load_test_decks();
        let play = |s: &State| {
            let players = create_players(deck_a.clone(), deck_b.clone(), vec![code.clone(), parse_player_code("km3").unwrap()]);
            let mut game = Game::from_state(s.clone(), players, 77);
            game.play_tick()
        };
        assert_eq!(play(&state), play(&other), "{knowledge:?}: the same move through Game");
    }
}

#[test]
fn the_same_seeds_give_the_same_moves() {
    let state = midgame(11);
    let code = PlayerCode::KX { params: small(Knowledge::Realistic, 2.0) };
    let run = || {
        let (deck_a, deck_b) = load_test_decks();
        let players = create_players(deck_a, deck_b, vec![code.clone(), parse_player_code("km3").unwrap()]);
        let mut game = Game::from_state(state.clone(), players, 1234);
        let mut moves = Vec::new();
        while moves.len() < 12 && !game.is_game_over() {
            moves.push(format!("{:?}", game.play_tick()));
        }
        moves
    };
    assert_eq!(run(), run());
}

/// A whole short game through `Game::new` (setup included), to the end, without a panic.
#[test]
fn a_whole_game_plays_to_the_end() {
    let (deck_a, deck_b) = load_test_decks();
    let code = PlayerCode::KX { params: PlayoutParams { rollouts: 2, cap: 3, ..PlayoutParams::new(3) } };
    let mut game = Game::new(create_players(deck_a, deck_b, vec![code, parse_player_code("km3").unwrap()]), 31);
    while !game.is_game_over() {
        game.play_tick();
    }
}

/// REALISTIC reads no list: two pilots built with different opponent lists (the real one, and a pool list cut to 19
/// cards, so even the length differs) give the same report, field for field, at the same observation and seed.
#[test]
fn realistic_reads_no_opponent_list() {
    for seed in [3u64, 11] {
        let state = midgame(seed);
        let actions = state.generate_possible_actions().1;
        let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
        let (deck_a, deck_b) = load_test_decks();
        let mut short = pool_deck("t-suicune");
        short.cards.pop();
        assert_ne!(short.cards.len(), deck_b.cards.len());
        let real = fresh(deck_a.clone(), deck_b, small(Knowledge::Realistic, 2.0))
            .evaluate(&mut StdRng::seed_from_u64(21), &observation, &actions);
        let other = fresh(deck_a, short, small(Knowledge::Realistic, 2.0))
            .evaluate(&mut StdRng::seed_from_u64(21), &observation, &actions);
        assert!(real.rounds > 0, "seed {seed}: play-outs ran: {}", real.reason);
        assert_eq!(fingerprint(&real), fingerprint(&other), "seed {seed}");
    }
}

/// LAB on a pool pairing (t-altaria v t-suicune): labelled LAB, and every round drew the exact list.
#[test]
fn lab_on_a_pool_pairing_uses_the_exact_list() {
    let state = midgame_with(pool_deck("t-altaria"), pool_deck("t-suicune"), 3);
    let actions = state.generate_possible_actions().1;
    let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
    let mut lab = fresh(pool_deck("t-altaria"), pool_deck("t-suicune"), small(Knowledge::Lab, 2.0));
    assert!(lab.knowledge_label().starts_with("LAB (laboratory condition"), "{}", lab.knowledge_label());
    let report = lab.evaluate(&mut StdRng::seed_from_u64(21), &observation, &actions);
    assert_eq!(report.rounds, 4);
    assert_eq!(report.lists, BTreeMap::from([("the exact list (LAB)".to_string(), 4)]));
    // REALISTIC at the same position draws from the pool instead.
    let real = fresh(pool_deck("t-altaria"), pool_deck("t-suicune"), small(Knowledge::Realistic, 2.0))
        .evaluate(&mut StdRng::seed_from_u64(21), &observation, &actions);
    assert!(real.lists.keys().all(|k| !k.contains("LAB")), "{:?}", real.lists);
}

/// LAB against a list outside the pool (the test decks) is REALISTIC exactly, and its label says so.
#[test]
fn lab_against_a_list_outside_the_pool_is_realistic_exactly() {
    let state = midgame(3);
    let actions = state.generate_possible_actions().1;
    let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
    let mut lab = pilot(small(Knowledge::Lab, 2.0));
    assert!(lab.knowledge_label().starts_with("REALISTIC (LAB asked"), "{}", lab.knowledge_label());
    let a = lab.evaluate(&mut StdRng::seed_from_u64(21), &observation, &actions);
    let b = pilot(small(Knowledge::Realistic, 2.0)).evaluate(&mut StdRng::seed_from_u64(21), &observation, &actions);
    assert_eq!(fingerprint_without_label(&a), fingerprint_without_label(&b));
}

/// One of the opponent's hidden hand cards replaced by a card from outside their list (Bulbasaur; weezing-arbok holds
/// none): the observation is the same, and so is the REALISTIC choice through `Game`.
#[test]
fn a_hidden_card_from_outside_the_opponents_list_changes_no_choice() {
    for seed in [3u64, 11] {
        let state = midgame(seed);
        assert!(!state.hands[1].is_empty(), "seed {seed}: the opponent holds a hand");
        let mut other = state.clone();
        let foreign = get_card_by_enum(CardId::A1001Bulbasaur);
        let (_, deck_b) = load_test_decks();
        assert!(!deck_b.cards.contains(&foreign));
        other.hands[1][0] = foreign;
        assert_eq!(
            PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default()),
            PlayerObservation::from_state(&other, 0, &RevealedKnowledge::default()),
            "seed {seed}: the same observation"
        );
        let code = PlayerCode::KX { params: small(Knowledge::Realistic, 2.0) };
        let play = |s: &State| {
            let (deck_a, deck_b) = load_test_decks();
            let players = create_players(deck_a, deck_b, vec![code.clone(), parse_player_code("km3").unwrap()]);
            Game::from_state(s.clone(), players, 77).play_tick()
        };
        assert_eq!(play(&state), play(&other), "seed {seed}: the same move through Game");
    }
}

/// LAB on a pool pairing cannot depend on the hidden cards either: the no-leak swap, through `Game`.
#[test]
fn the_lab_choice_on_a_pool_pairing_cannot_depend_on_hidden_cards() {
    let state = midgame_with(pool_deck("t-altaria"), pool_deck("t-suicune"), 3);
    let other = other_hidden_cards(&state);
    assert!(other.hands[1] != state.hands[1] || other.decks[1].cards != state.decks[1].cards, "the hidden cards differ");
    assert_eq!(
        PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default()),
        PlayerObservation::from_state(&other, 0, &RevealedKnowledge::default())
    );
    let code = PlayerCode::KX { params: small(Knowledge::Lab, 2.0) };
    let play = |s: &State| {
        let players = create_players(pool_deck("t-altaria"), pool_deck("t-suicune"), vec![code.clone(), parse_player_code("km3").unwrap()]);
        Game::from_state(s.clone(), players, 77).play_tick()
    };
    assert_eq!(play(&state), play(&other));
}

/// KX_EXTRA_LISTS refuses a path under decks/brews (also written the Windows way, and before reading it), and reads a
/// list elsewhere with its hash.
#[test]
fn an_extra_list_under_decks_brews_is_refused() {
    for spec in [
        "mine=../decks/brews/brew-01-arceus-crobat-xatu.txt",
        "mine=..\\decks\\brews\\brew-01-arceus-crobat-xatu.txt",
        "mine=../decks/brews/no-such-file.txt",
        "ok=../decks/screen/opponents/t-suicune.txt;mine=../decks/BREWS/brew-01-arceus-crobat-xatu.txt",
        "mine=../decks/screen/../brews/brew-01-arceus-crobat-xatu.txt",
    ] {
        let refused = parse_extra_lists(spec).expect_err(spec);
        assert!(refused.contains("decks/brews"), "{spec}: {refused}");
    }
    let lists = parse_extra_lists(" computer = ../decks/screen/opponents/t-suicune.txt ; ").unwrap();
    assert_eq!(lists.len(), 1);
    assert_eq!((lists[0].name.as_str(), lists[0].fnv1a64.len()), ("computer", 16));
    assert_eq!(lists[0].deck.cards, pool_deck("t-suicune").cards);
    for bad in ["computer", "=x.txt", "a=../decks/screen/opponents/t-suicune.txt;a=../decks/screen/opponents/t-altaria.txt", "a=no-such-file.txt"] {
        assert!(parse_extra_lists(bad).is_err(), "{bad} should be refused");
    }
}

/// With a time budget, no move replaces km's before 8 rounds. In a 2-thread pool a batch is 2 rounds, and the 1 ms budget
/// ends after the first, so every decision here has 2 rounds whatever the machine's cores. km's move is kept at every
/// position, and at least one has a rival leading, so the reason "fewer than the 8" is always checked. The positions: the
/// immediate-win board (km3 takes the win itself), middle-game positions of the test decks (REALISTIC; their opponent is
/// outside the pool, filler since round 3) and of the pool pairing t-altaria v t-suicune (LAB), which round 3 leaves alone.
#[test]
fn with_a_time_budget_no_switch_before_8_rounds() {
    let threads = rayon::ThreadPoolBuilder::new().num_threads(2).build().unwrap();
    let immediate_win = {
        let mut game = get_test_game_with_board(
            vec![PlayedCard::from_id(CardId::B1151MegaAbsolEx).with_energy(vec![EnergyType::Darkness, EnergyType::Darkness])],
            vec![PlayedCard::from_id(CardId::A1115Abra)],
        );
        let mut state = game.get_state_clone();
        state.move_generation_stack.clear();
        game.set_state(state);
        game.get_state_clone()
    };
    let mut led = 0;
    let test_decks = |state: State| (state, load_test_decks(), Knowledge::Realistic);
    let pool_pairing = |seed: u64| {
        (midgame_with(pool_deck("t-altaria"), pool_deck("t-suicune"), seed), (pool_deck("t-altaria"), pool_deck("t-suicune")), Knowledge::Lab)
    };
    for (state, (deck, opponent), knowledge) in
        [test_decks(immediate_win), test_decks(midgame(3)), test_decks(midgame(11)), pool_pairing(3), pool_pairing(5)]
    {
        let actions = state.generate_possible_actions().1;
        let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
        let params = PlayoutParams { rollouts: 16, budget_ms: 1, ..small(knowledge, 0.0) };
        let report =
            threads.install(|| fresh(deck, opponent, params).evaluate(&mut StdRng::seed_from_u64(9), &observation, &actions));
        assert_eq!(report.rounds, 2, "{}", report.reason);
        assert_eq!(report.chosen, report.km3, "{}", report.reason);
        let best = report.candidates.iter().map(|c| c.score).fold(f64::MIN, f64::max);
        if report.candidates[report.km3].score < best {
            assert!(report.reason.contains("fewer than the 8"), "{}", report.reason);
            led += 1;
        }
        eprintln!("time-budget position: km {} best {best} rounds {}: {}", report.candidates[report.km3].score, report.rounds, report.reason);
    }
    assert!(led > 0, "no position had a rival leading, so the reason went unchecked");
}

/// The diagnostic entry with a full state keeps km's move, with no play-outs, and is counted (and traced with `_trace`).
#[test]
fn an_omniscient_call_keeps_kms_move_and_is_counted() {
    let state = midgame(3);
    let actions = state.generate_possible_actions().1;
    let mut p = pilot(small(Knowledge::Realistic, 0.0));
    let chosen = p.decide_omniscient(&mut StdRng::seed_from_u64(9), &state, &actions);
    let (deck_a, deck_b) = load_test_decks();
    let mut km3 = create_players(deck_a, deck_b, vec![parse_player_code("km3").unwrap(), parse_player_code("km3").unwrap()]).remove(0);
    assert_eq!(chosen, km3.decide_omniscient(&mut StdRng::seed_from_u64(9), &state, &actions));
    assert_eq!((p.omniscient, p.decisions), (1, 0));
}

/// A temporary folder of this test process's own.
fn scratch(name: &str) -> std::path::PathBuf {
    let dir = std::env::temp_dir().join(format!("kx_test_{}_{name}", std::process::id()));
    std::fs::create_dir_all(&dir).unwrap();
    dir
}

/// Dustin's own lists are refused by path too (decks/dustin), as given, once resolved, and written the Windows way.
#[test]
fn an_extra_list_under_decks_dustin_is_refused() {
    for spec in [
        "his=../decks/dustin/02-arceus-crobat.txt",
        "his=../decks/screen/../dustin/02-arceus-crobat.txt",
        "his=..\\decks\\Dustin\\02-arceus-crobat.txt",
    ] {
        let refused = parse_extra_lists(spec).expect_err(spec);
        assert!(refused.contains("decks/dustin"), "{spec}: {refused}");
    }
}

/// A copy of a brew's list or one of Dustin's, anywhere else (a test folder here; the position runner's decks/ folder in
/// use), is refused by its cards: as copied, with its lines reordered, and with its Energy line dropped.
#[test]
fn a_copy_of_a_brew_or_dustins_list_is_refused_by_its_cards() {
    let dir = scratch("copies");
    for (source, copy) in [
        ("../decks/brews/brew-08-entei-rainbow-cave.txt", "brew08.txt"),
        ("../decks/brews/drafts_2026-10-01/draft-A-shark-tempo.txt", "draftA.txt"),
        ("../decks/dustin/03-wailord-indeedee-wall.txt", "deck03.txt"),
    ] {
        let text = std::fs::read_to_string(source).unwrap();
        let reordered: String = {
            let mut lines: Vec<&str> = text.lines().filter(|l| !l.trim().is_empty()).collect();
            lines.reverse();
            lines.join("\n")
        };
        let no_energy: String = text.lines().filter(|l| !l.starts_with("Energy:")).collect::<Vec<_>>().join("\n");
        for (prefix, body) in [("", text.clone()), ("reordered_", reordered), ("no_energy_", no_energy)] {
            let path = dir.join(format!("{prefix}{copy}"));
            std::fs::write(&path, body).unwrap();
            let spec = format!("computer={}", path.display());
            let refused = parse_extra_lists(&spec).expect_err(&spec);
            assert!(
                refused.contains("holds the same cards as") && refused.contains(source.trim_start_matches("../")),
                "{spec}: {refused}"
            );
        }
    }
    // A list that is no copy is read, with what it was checked against.
    let lists = parse_extra_lists("computer=../decks/screen/opponents/t-suicune.txt").unwrap();
    assert!(lists[0].checked_against.contains("lists under decks/brews and decks/dustin"), "{}", lists[0].checked_against);
    // Every .txt in the two folders reads as a list (none is skipped).
    fn txt_files(d: &std::path::Path) -> usize {
        std::fs::read_dir(d)
            .unwrap()
            .map(|e| e.unwrap().path())
            .map(|p| if p.is_dir() { txt_files(&p) } else { p.extension().is_some_and(|x| x == "txt") as usize })
            .sum()
    }
    let repo = std::path::Path::new("..");
    assert_eq!(
        protected_lists(repo).unwrap().len(),
        txt_files(&repo.join("decks/brews")) + txt_files(&repo.join("decks/dustin"))
    );
}

/// No protected folders to check against (a folder that isn't the repository): refused, with the reason.
#[test]
fn extra_lists_are_refused_when_the_protected_folders_cant_be_read() {
    let empty = scratch("not_a_repository");
    let refused = parse_extra_lists_against("computer=../decks/screen/opponents/t-suicune.txt", &empty).unwrap_err();
    assert!(refused.contains("can't read") && refused.contains("decks"), "{refused}");
    // An empty variable needs no repository.
    assert!(parse_extra_lists_against("", &empty).unwrap().is_empty());
}
