//! Quiz 4's items for the play-out pilot (Oct 6; Fable via Dustin; rl/results/playout_quiz4_items_2026-10-06/README.md),
//! each its own parameter, written before the code.
//!
//! Item 1, "attack when you can" (`_za<z>`): when km3's move is an attack and kx3's best candidate is not, the switch needs
//! a lead beyond z_attack standard errors instead of z; a switch to another attack, or from a move that isn't an attack,
//! keeps the bar z. Every switch away from km3's attack names both scores in the reason (the trace's), and so does every
//! switch the stricter bar stops. With the parameter off nothing changes.
//!
//! Item 2, no-effect actions (`_noeffect`): whether an action's printed effect can do anything now, read from the card's
//! text (every Trainer and Ability text in the database is read or named unread; the needs come from the words), and a
//! within-noise tie-break at kx3's own decision, the Tool tie-break's shape: nothing leaves the pool; only when no move
//! clears the bar and km3's move can do nothing now while another candidate does something, kx3 plays km3's choice among
//! those ("tie-break: no effect now"), unless km3's move leads it beyond the noise. With the parameter off nothing changes.
//!
//! Item 1, narrowed (Oct 7; Fable via Dustin: `_za` as built is not shipped, it stops moves that attack later in the turn):
//! the skip bar (`_zs<z>`). Every play-out records whether the pilot's side attacked before its turn ended. A switch from
//! km3's attack to a move that isn't one needs a lead beyond z_skip standard errors only when that move's own line leaves
//! the turn without an attack (in more than half of its play-outs); a line that attacks later in the turn keeps the bar z.
//! The reason names the count either way. With the parameter off nothing changes.
//!
//! Item 3, the continuation experiment at the quiz's three "neither" positions (Q06, Q07, Q11): Dustin's plans are scripted
//! by intent (rl/results/playout_quiz4_items_2026-10-06/neither/plans.json), and Q06's begins with an Ability, so a plan
//! step can name whose Ability is used; the plan is played as he wrote it.
use std::collections::BTreeSet;

use deckgym::actions::{Action, SimpleAction};
use deckgym::observation::{PlayerObservation, RevealedKnowledge};
use deckgym::card_ids::CardId;
use deckgym::database::get_card_by_enum;
use deckgym::models::{Card, PlayedCard};
use deckgym::players::playout_player::{
    effect_needs, effect_now, skip_bar, switch_bar, CardKind, DecisionReport, Knowledge, Need, Plan, PlayoutParams, PlayoutPlayer,
    PokemonFilter, Reading, Scope, Step,
};
use deckgym::test_support::get_test_game_with_board;
use strum::IntoEnumIterator;
use deckgym::players::{create_players, parse_player_code, PlayerCode};
use deckgym::test_support::load_test_decks;
use deckgym::{Game, State};
use rand::{rngs::StdRng, SeedableRng};

fn is_attack(a: &Action) -> bool {
    matches!(a.action, SimpleAction::Attack(_))
}

/// Every field of a decision's report but its time, as text.
fn fingerprint(r: &DecisionReport) -> String {
    let candidates: Vec<String> = r.candidates.iter().map(|c| format!("{:?} {} {} {}", c.action, c.score, c.diff, c.se)).collect();
    format!("{:?} | km {} chosen {} | {} | rounds {}", candidates, r.km3, r.chosen, r.reason, r.rounds)
}

/// The code spells the attack bar (`_za<z>`, after `_tools`), and every code without it is as before.
#[test]
fn the_code_spells_the_attack_bar() {
    assert_eq!(PlayoutParams::new(3).z_attack, None);
    assert_eq!(PlayoutParams::new(3).code(), "kx3_r16_c12_z2_real_t0_poolwide");
    let p = PlayoutParams::parse("3_za3").unwrap();
    assert_eq!(p.z_attack, Some(3.0));
    assert_eq!(p.code(), "kx3_r16_c12_z2_real_t0_poolwide_za3");
    assert_eq!(PlayoutParams::parse(&p.code()[2..]).unwrap(), p);
    let both = PlayoutParams::parse("3_r16_c12_z2_real_t0_poolmeta_tools_za2.5").unwrap();
    assert_eq!(both.code(), "kx3_r16_c12_z2_real_t0_poolmeta_tools_za2.5");
    let PlayerCode::KX { params } = parse_player_code("kx3_za3").unwrap() else { panic!() };
    assert_eq!(params.z_attack, Some(3.0));
    for bad in ["kx3_za", "kx3_za-1", "kx3_zax"] {
        assert!(parse_player_code(bad).is_err(), "{bad} should not parse");
    }
}

/// The bar: z_attack only from km3's attack to a move that isn't one; z otherwise, and always z with the parameter off.
#[test]
fn the_attack_bar_applies_only_away_from_an_attack() {
    let (deck_a, deck_b) = load_test_decks();
    let km3 = || parse_player_code("km3").unwrap();
    let mut game = Game::new(create_players(deck_a, deck_b, vec![km3(), km3()]), 20_000_000_210);
    let mut attack = None;
    while attack.is_none() && !game.is_game_over() {
        let (_, actions) = game.get_state_clone().generate_possible_actions();
        attack = actions.iter().find(|a| is_attack(a)).cloned();
        game.play_tick();
    }
    let attack = attack.expect("an attack came up");
    let end = Action { actor: attack.actor, action: SimpleAction::EndTurn, is_stack: false };
    assert_eq!(switch_bar(&attack, &end, 2.0, Some(3.0)), 3.0, "away from an attack");
    assert_eq!(switch_bar(&attack, &attack, 2.0, Some(3.0)), 2.0, "to an attack");
    assert_eq!(switch_bar(&end, &attack, 2.0, Some(3.0)), 2.0, "from a move that isn't an attack");
    assert_eq!(switch_bar(&attack, &end, 2.0, None), 2.0, "the parameter off");
}

/// Decisions where km3 proposes an attack among at least three distinct moves: km3 plays test-deck games from the seeds
/// given, and the first such decision of player 0 from turn 3 on is taken from each.
fn attack_decisions(seeds: &[u64]) -> Vec<(u64, State)> {
    let km3 = || parse_player_code("km3").unwrap();
    let mut out = Vec::new();
    for &seed in seeds {
        let (deck_a, deck_b) = load_test_decks();
        let mut game = Game::new(create_players(deck_a.clone(), deck_b.clone(), vec![km3(), km3()]), seed);
        let mut proposer = create_players(deck_a, deck_b, vec![km3(), km3()]).remove(0);
        while !game.is_game_over() {
            let state = game.get_state_clone();
            let (actor, actions) = state.generate_possible_actions();
            let distinct: BTreeSet<String> = actions.iter().map(|a| format!("{:?}", a.action)).collect();
            if actor == 0 && state.turn_count >= 3 && distinct.len() >= 3 && actions.iter().any(is_attack) {
                let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
                if is_attack(&proposer.decision_fn(&mut StdRng::seed_from_u64(seed), &observation, &actions)) {
                    out.push((seed, state));
                    break;
                }
            }
            game.play_tick();
        }
    }
    out
}

fn small(z: f64, z_attack: Option<f64>) -> PlayoutPlayer {
    let (deck_a, deck_b) = load_test_decks();
    let params = PlayoutParams { rollouts: 8, cap: 6, z, z_attack, knowledge: Knowledge::Lab, ..PlayoutParams::new(3) };
    PlayoutPlayer::with_extra_lists(deck_a, deck_b, params, Vec::new())
}

/// With the bar at z itself, every decision is the one without the parameter (identity).
#[test]
fn an_attack_bar_equal_to_z_changes_nothing() {
    for (seed, state) in attack_decisions(&[20_000_000_211, 20_000_000_212, 20_000_000_213]) {
        let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
        let actions = state.generate_possible_actions().1;
        let off = small(0.5, None).evaluate(&mut StdRng::seed_from_u64(seed), &observation, &actions);
        let same = small(0.5, Some(0.5)).evaluate(&mut StdRng::seed_from_u64(seed), &observation, &actions);
        assert_eq!(off.chosen, same.chosen, "seed {seed}");
        assert_eq!(fingerprint(&off).split(" | ").next(), fingerprint(&same).split(" | ").next(), "seed {seed}: the same play-outs");
    }
}

/// With no bar (z 0) kx3 takes the best play-out score; with an unreachable attack bar it never leaves km3's attack for a
/// move that isn't an attack, and the reason names the bar with both scores. At least one of these test-deck decisions is
/// such a stopped switch.
#[test]
fn the_attack_bar_keeps_km3s_attack_against_a_smaller_lead() {
    let decisions = attack_decisions(&[20_000_000_211, 20_000_000_212, 20_000_000_213, 20_000_000_214, 20_000_000_215, 20_000_000_216]);
    assert!(decisions.len() >= 4, "{} decisions", decisions.len());
    let mut stopped = 0;
    for (seed, state) in decisions {
        let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
        let actions = state.generate_possible_actions().1;
        let open = small(0.0, None).evaluate(&mut StdRng::seed_from_u64(seed), &observation, &actions);
        let barred = small(0.0, Some(1e9)).evaluate(&mut StdRng::seed_from_u64(seed), &observation, &actions);
        assert!(is_attack(&open.candidates[open.km3].action), "seed {seed}: km3 proposes an attack");
        assert!(is_attack(&barred.candidates[barred.chosen].action), "seed {seed}: {}", barred.reason);
        if is_attack(&open.candidates[open.chosen].action) {
            assert_eq!(barred.chosen, open.chosen, "seed {seed}");
        } else {
            stopped += 1;
            assert_eq!(barred.chosen, barred.km3, "seed {seed}: km3's attack kept");
            assert!(barred.reason.contains("attack bar") && barred.reason.contains(&format!("{:.3}", open.candidates[open.km3].score)),
                    "seed {seed}: {}", barred.reason);
        }
    }
    assert!(stopped >= 1, "no stopped switch among these decisions");
}

// Item 1, narrowed: the skip bar (`_zs<z>`).

/// The code spells the skip bar (`_zs<z>`, last); it can't be named with the attack bar; every code without it is as before.
#[test]
fn the_code_spells_the_skip_bar() {
    assert_eq!(PlayoutParams::new(3).z_skip, None);
    let p = PlayoutParams::parse("3_zs3").unwrap();
    assert_eq!(p.z_skip, Some(3.0));
    assert_eq!(p.code(), "kx3_r16_c12_z2_real_t0_poolwide_zs3");
    assert_eq!(PlayoutParams::parse(&p.code()[2..]).unwrap(), p);
    let more = PlayoutParams::parse("3_r16_c12_z2_real_t0_poolmeta_noeffect_zs2.5").unwrap();
    assert_eq!(more.code(), "kx3_r16_c12_z2_real_t0_poolmeta_noeffect_zs2.5");
    for bad in ["kx3_zs", "kx3_zs-1", "kx3_zsx", "kx3_za3_zs3"] {
        assert!(parse_player_code(bad).is_err(), "{bad} should not parse");
    }
}

/// The skip bar: z_skip only from km3's attack to a move that isn't one whose line attacks this turn in fewer than half of
/// its play-outs; z otherwise, and always z with the parameter off.
#[test]
fn the_skip_bar_applies_only_away_from_an_attack_to_a_line_without_one() {
    let (deck_a, deck_b) = load_test_decks();
    let km3 = || parse_player_code("km3").unwrap();
    let mut game = Game::new(create_players(deck_a, deck_b, vec![km3(), km3()]), 20_000_000_210);
    let mut attack = None;
    while attack.is_none() && !game.is_game_over() {
        let (_, actions) = game.get_state_clone().generate_possible_actions();
        attack = actions.iter().find(|a| is_attack(a)).cloned();
        game.play_tick();
    }
    let attack = attack.expect("an attack came up");
    let other = Action { actor: attack.actor, action: SimpleAction::EndTurn, is_stack: false };
    assert_eq!(skip_bar(&attack, &other, 0, 8, 2.0, Some(3.0)), 3.0, "no attack this turn in its line");
    assert_eq!(skip_bar(&attack, &other, 3, 8, 2.0, Some(3.0)), 3.0, "an attack in 3 of 8 play-outs: mostly none");
    assert_eq!(skip_bar(&attack, &other, 4, 8, 2.0, Some(3.0)), 2.0, "half: not a skip");
    assert_eq!(skip_bar(&attack, &other, 8, 8, 2.0, Some(3.0)), 2.0, "attacks later in the turn");
    assert_eq!(skip_bar(&attack, &attack, 0, 8, 2.0, Some(3.0)), 2.0, "to an attack");
    assert_eq!(skip_bar(&other, &attack, 0, 8, 2.0, Some(3.0)), 2.0, "from a move that isn't an attack");
    assert_eq!(skip_bar(&attack, &other, 0, 8, 2.0, None), 2.0, "the parameter off");
}

fn small_skip(z: f64, z_skip: Option<f64>) -> PlayoutPlayer {
    let (deck_a, deck_b) = load_test_decks();
    let params = PlayoutParams { rollouts: 8, cap: 6, z, z_skip, knowledge: Knowledge::Lab, ..PlayoutParams::new(3) };
    PlayoutPlayer::with_extra_lists(deck_a, deck_b, params, Vec::new())
}

const SKIP_SEEDS: [u64; 12] = [
    20_000_000_211, 20_000_000_212, 20_000_000_213, 20_000_000_214, 20_000_000_215, 20_000_000_216,
    20_000_000_230, 20_000_000_231, 20_000_000_232, 20_000_000_233, 20_000_000_234, 20_000_000_235,
];

/// Every play-out counts whether the pilot's side attacked before its turn ended: an attack itself always has, End Turn
/// never has, and some other move's line attacks later in the turn. The play-outs themselves are the same with the skip
/// bar on or off.
#[test]
fn the_play_outs_count_the_attacks_of_the_turn() {
    let mut later = 0;
    for (seed, state) in attack_decisions(&SKIP_SEEDS[..6]) {
        let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
        let actions = state.generate_possible_actions().1;
        let r = small_skip(2.0, None).evaluate(&mut StdRng::seed_from_u64(seed), &observation, &actions);
        assert!(r.rounds > 0, "seed {seed}");
        for c in &r.candidates {
            assert!(c.attacks_this_turn <= r.rounds, "seed {seed}: {}", c.label);
            if is_attack(&c.action) {
                assert_eq!(c.attacks_this_turn, r.rounds, "seed {seed}: {}", c.label);
            } else if matches!(c.action.action, SimpleAction::EndTurn) {
                assert_eq!(c.attacks_this_turn, 0, "seed {seed}");
            } else if c.attacks_this_turn > 0 {
                later += 1;
            }
        }
        let on = small_skip(2.0, Some(3.0)).evaluate(&mut StdRng::seed_from_u64(seed), &observation, &actions);
        assert_eq!(fingerprint(&r).split(" | ").next(), fingerprint(&on).split(" | ").next(), "seed {seed}: the same play-outs");
    }
    assert!(later >= 1, "no move's line attacked later in the turn");
}

/// The skip bar is the attack bar only where the best move's line leaves the turn without an attack; where it attacks
/// later in the turn the switch stands as without the bar. The reason names the count either way.
#[test]
fn the_skip_bar_stops_only_switches_that_skip_the_attack() {
    let (mut stopped, mut stood) = (0, 0);
    for (seed, state) in attack_decisions(&SKIP_SEEDS) {
        let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
        let actions = state.generate_possible_actions().1;
        let open = small_skip(0.0, None).evaluate(&mut StdRng::seed_from_u64(seed), &observation, &actions);
        let barred = small_skip(0.0, Some(1e9)).evaluate(&mut StdRng::seed_from_u64(seed), &observation, &actions);
        assert!(is_attack(&open.candidates[open.km3].action), "seed {seed}: km3 proposes an attack");
        let best = &open.candidates[open.chosen];
        if open.chosen == open.km3 || is_attack(&best.action) {
            assert_eq!(barred.chosen, open.chosen, "seed {seed}");
        } else if best.attacks_this_turn * 2 < open.rounds {
            stopped += 1;
            assert_eq!(barred.chosen, barred.km3, "seed {seed}: km3's attack kept");
            assert!(barred.reason.contains("no attack this turn"), "seed {seed}: {}", barred.reason);
        } else {
            stood += 1;
            assert_eq!(barred.chosen, open.chosen, "seed {seed}: {}", barred.reason);
            assert!(barred.reason.contains(&format!("attacks this turn in {} of {}", best.attacks_this_turn, open.rounds)),
                    "seed {seed}: {}", barred.reason);
        }
    }
    eprintln!("switches away from km3's attack: {stopped} stopped (no attack this turn), {stood} standing (an attack later)");
    assert!(stopped + stood >= 1, "no switch away from km3's attack among these decisions");
}

/// A switch away from km3's attack that clears the bar names both scores too.
#[test]
fn a_switch_away_from_an_attack_names_both_scores() {
    for (seed, state) in attack_decisions(&[20_000_000_211, 20_000_000_212, 20_000_000_213, 20_000_000_214, 20_000_000_215, 20_000_000_216]) {
        let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
        let actions = state.generate_possible_actions().1;
        let r = small(0.0, Some(0.0)).evaluate(&mut StdRng::seed_from_u64(seed), &observation, &actions);
        if !is_attack(&r.candidates[r.chosen].action) {
            let (km, chosen) = (r.candidates[r.km3].score, r.candidates[r.chosen].score);
            assert!(r.reason.contains("away from km's attack") && r.reason.contains(&format!("{km:.3}")) && r.reason.contains(&format!("{chosen:.3}")),
                    "seed {seed}: {}", r.reason);
        }
    }
}


/// Every distinct Item, Supporter and Stadium text and every Ability text in the card database (Abilities named "X's T"),
/// with its kind.
fn texts_with_kind() -> Vec<(String, String, String)> {
    let mut seen = BTreeSet::new();
    let mut out = Vec::new();
    for card in CardId::iter().map(get_card_by_enum) {
        let (name, text, kind) = match &card {
            Card::Trainer(t) if matches!(format!("{:?}", t.trainer_card_type).as_str(), "Item" | "Supporter" | "Stadium") => {
                (t.name.clone(), t.effect.clone(), format!("{:?}", t.trainer_card_type))
            }
            Card::Pokemon(p) => match &p.ability {
                Some(a) => (format!("{}'s {}", p.name, a.title), a.effect.clone(), "Ability".to_string()),
                None => continue,
            },
            _ => continue,
        };
        if seen.insert(text.clone()) {
            out.push((name, text, kind));
        }
    }
    out
}

/// Whether a text can be chosen as a move: an Item or Supporter played, a Stadium used "once during each player's turn",
/// an Ability used "once during your turn" or "as often as you like" (the others work by themselves and are never a move;
/// playing a Stadium card always does something).
fn usable(kind: &str, text: &str) -> bool {
    let t = text.to_lowercase();
    match kind {
        "Item" | "Supporter" => true,
        "Stadium" => t.contains("once during each player's turn"),
        _ => t.contains("once during your turn") || t.starts_with("as often as you like"),
    }
}

/// Every text is either read or named unread (never a panic); most texts that can be a move are read; and the texts of
/// the cards the quiz notes name are read.
#[test]
fn every_text_is_read_or_named_unread() {
    let all = texts_with_kind();
    assert!(all.len() >= 250, "{} texts", all.len());
    let moves: Vec<_> = all.iter().filter(|(_, t, k)| usable(k, t)).map(|(n, t, _)| (n.clone(), t.clone())).collect();
    let read = moves.iter().filter(|(_, t)| effect_needs(t).is_ok()).count();
    eprintln!("{read} of the {} texts that can be a move are read ({} texts in all)", moves.len(), all.len());
    for (name, text) in &moves {
        if let Err(why) = effect_needs(text) {
            eprintln!("unread: {name}: {why}");
        }
    }
    assert!(read * 10 >= moves.len() * 9, "{read} of {}", moves.len());
    for name in ["Indeedee ex's Watch Over", "Fragrant Forest", "Clemont's Backpack", "Poké Ball", "Potion", "Pokémon Center Lady", "Professor's Research"] {
        let text = text_of(name);
        assert!(effect_needs(&text).is_ok(), "{name}: {:?}", effect_needs(&text));
    }
}

/// A card's text by its name ("X's T" for an Ability), from any printing.
fn text_of(name: &str) -> String {
    CardId::iter()
        .map(get_card_by_enum)
        .find_map(|c| match &c {
            Card::Trainer(t) if t.name == name => Some(t.effect.clone()),
            Card::Pokemon(p) => p.ability.as_ref().filter(|a| format!("{}'s {}", p.name, a.title) == name).map(|a| a.effect.clone()),
            _ => None,
        })
        .unwrap_or_else(|| panic!("{name}"))
}

/// The needs come from the words.
#[test]
fn the_needs_come_from_the_text() {
    let needs = |name: &str| effect_needs(&text_of(name)).unwrap();
    let any = PokemonFilter::default();
    assert_eq!(needs("Indeedee ex's Watch Over"), Reading::Needs(vec![Need::Damaged(Scope::Active, any.clone())]));
    assert_eq!(needs("Potion"), Reading::Needs(vec![Need::Damaged(Scope::Any, any.clone())]));
    assert_eq!(needs("Pokémon Center Lady"), Reading::Needs(vec![Need::Damaged(Scope::Any, any.clone()), Need::Condition(Scope::Any, any.clone())]));
    let basic_grass = PokemonFilter { stage: Some(0), energy: Some(deckgym::models::EnergyType::Grass), ..Default::default() };
    assert_eq!(needs("Fragrant Forest"), Reading::Needs(vec![Need::InDeck(CardKind::Pokemon(basic_grass))]));
    let magneton_or_heliolisk = PokemonFilter { names: vec!["magneton".into(), "heliolisk".into()], ..Default::default() };
    assert_eq!(needs("Clemont's Backpack"), Reading::Needs(vec![Need::InPlay(Scope::Any, magneton_or_heliolisk)]));
    assert_eq!(needs("Poké Ball"), Reading::Needs(vec![Need::InDeck(CardKind::Pokemon(PokemonFilter { stage: Some(0), ..Default::default() }))]));
    assert_eq!(needs("Professor's Research"), Reading::Needs(vec![Need::DeckNotEmpty]));
    assert_eq!(needs("X Speed"), Reading::Needs(vec![Need::InPlay(Scope::Active, PokemonFilter { min_retreat: Some(1), ..Default::default() })]));
    assert_eq!(needs("Sabrina"), Reading::Needs(vec![Need::OpponentBench(any.clone())]));
    assert_eq!(needs("Red Card"), Reading::Always);
    let w = PokemonFilter { energy_attached: Some(Some(deckgym::models::EnergyType::Water)), ..Default::default() };
    assert_eq!(needs("Irida"), Reading::Needs(vec![Need::Damaged(Scope::Any, w)]));
    // Supporters the engine offers whatever the board: what they need comes from the words too (Guzma's and Elesa's
    // Tools, Hala's and Iris's Pokémon, Drayden's Draco Meteor), not "always".
    assert_eq!(needs("Guzma"), Reading::Needs(vec![Need::ToolsInPlay { yours: false, theirs: true }]));
    assert_eq!(needs("Elesa"), Reading::Needs(vec![Need::ToolsInPlay { yours: true, theirs: true }]));
    let named = |ns: &[&str]| PokemonFilter { names: ns.iter().map(|n| n.to_string()).collect(), ..Default::default() };
    assert_eq!(needs("Hala"), Reading::Needs(vec![Need::InPlay(Scope::Any, named(&["hariyama", "crabominable"]))]));
    assert_eq!(needs("Iris"), Reading::Needs(vec![Need::InPlay(Scope::Any, named(&["haxorus"]))]));
    let draco = PokemonFilter { attack: Some("draco meteor".into()), ..Default::default() };
    assert_eq!(needs("Drayden"), Reading::Needs(vec![Need::InPlay(Scope::Any, draco)]));
}

/// Guzma does nothing while no Pokémon of the opponent's holds a Tool, and something once one does; Elesa counts either
/// side's.
#[test]
fn the_tool_supporters_read_the_board() {
    let game = get_test_game_with_board(vec![PlayedCard::from_id(CardId::B1121IndeedeeEx)], vec![PlayedCard::from_id(CardId::A1115Abra)]);
    let mut state = game.get_state_clone();
    let play = |id: CardId| match get_card_by_enum(id) {
        Card::Trainer(t) => Action { actor: 0, action: SimpleAction::Play { trainer_card: t }, is_stack: false },
        _ => unreachable!(),
    };
    let (guzma, elesa) = (play(CardId::A3151Guzma), play(CardId::B3b066Elesa));
    assert_eq!(effect_now(&state, &guzma, &[]), Some(false), "no Tool in play");
    assert_eq!(effect_now(&state, &elesa, &[]), Some(false), "no Tool in play");
    let helmet = get_card_by_enum(CardId::B1219HeavyHelmet);
    state.in_play_pokemon[0][0].as_mut().unwrap().attached_tools.push(helmet.clone());
    assert_eq!(effect_now(&state, &guzma, &[]), Some(false), "only your own Tool");
    assert_eq!(effect_now(&state, &elesa, &[]), Some(true), "your own Tool");
    state.in_play_pokemon[1][0].as_mut().unwrap().attached_tools.push(helmet);
    assert_eq!(effect_now(&state, &guzma, &[]), Some(true), "the opponent's Tool");
}

/// On a board: Watch Over does nothing with the Active at full HP, and something once it is damaged; Clemont's Backpack
/// does nothing with no Magneton or Heliolisk in play; Fragrant Forest does nothing with no Basic [G] Pokémon left in the
/// deck; a Pokémon placed or an attack always does something.
#[test]
fn effect_now_reads_the_board() {
    let game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B1121IndeedeeEx), PlayedCard::from_id(CardId::B1121IndeedeeEx)],
        vec![PlayedCard::from_id(CardId::A1115Abra)],
    );
    let mut state = game.get_state_clone();
    let watch_over = Action { actor: 0, action: SimpleAction::UseAbility { in_play_idx: 1 }, is_stack: false };
    assert_eq!(effect_now(&state, &watch_over, &[]), Some(false), "full HP");
    state.in_play_pokemon[0][0] = Some(PlayedCard::from_id(CardId::B1121IndeedeeEx).with_damage(30));
    assert_eq!(effect_now(&state, &watch_over, &[]), Some(true), "damaged");
    let backpack = match get_card_by_enum(CardId::B1a066ClemontsBackpack) {
        Card::Trainer(t) => t,
        _ => unreachable!(),
    };
    let play = Action { actor: 0, action: SimpleAction::Play { trainer_card: backpack }, is_stack: false };
    assert_eq!(effect_now(&state, &play, &[]), Some(false), "no Magneton or Heliolisk in play");
    let end = Action { actor: 0, action: SimpleAction::EndTurn, is_stack: false };
    assert_eq!(effect_now(&state, &end, &[]), Some(true));
}

/// The code spells the no-effect rule (`_noeffect`, after `_tools`, before `_za`), and every code without it is as before.
#[test]
fn the_code_spells_the_no_effect_rule() {
    assert!(!PlayoutParams::new(3).noeffect);
    let p = PlayoutParams::parse("3_noeffect").unwrap();
    assert!(p.noeffect);
    assert_eq!(p.code(), "kx3_r16_c12_z2_real_t0_poolwide_noeffect");
    assert_eq!(PlayoutParams::parse(&p.code()[2..]).unwrap(), p);
    assert_eq!(PlayoutParams::parse("3_tools_noeffect_za3").unwrap().code(), "kx3_r16_c12_z2_real_t0_poolwide_tools_noeffect_za3");
}

/// A decision where km3 proposes Indeedee ex's Watch Over with its Active at full HP: deck 05 v t-altaria, km3 on both
/// sides, the first such decision of player 0.
fn idle_watch_over(seed: u64) -> Option<State> {
    let list = deckgym::Deck::from_file("../decks/dustin/05-indeedee-stoutland.txt").unwrap();
    let opp = deckgym::Deck::from_file("../decks/screen/opponents/t-altaria.txt").unwrap();
    let km3 = || parse_player_code("km3").unwrap();
    let mut game = Game::new(create_players(list.clone(), opp.clone(), vec![km3(), km3()]), seed);
    let mut proposer = create_players(list, opp, vec![km3(), km3()]).remove(0);
    while !game.is_game_over() {
        let state = game.get_state_clone();
        let (actor, actions) = state.generate_possible_actions();
        let distinct: BTreeSet<String> = actions.iter().map(|a| format!("{:?}", a.action)).collect();
        if actor == 0 && distinct.len() >= 3 {
            let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
            let a = proposer.decision_fn(&mut StdRng::seed_from_u64(seed), &observation, &actions);
            if matches!(a.action, SimpleAction::UseAbility { .. }) && effect_now(&state, &a, &state.decks[0].cards) == Some(false) {
                return Some(state);
            }
        }
        game.play_tick();
    }
    None
}

fn pilot05(noeffect: bool, z: f64) -> PlayoutPlayer {
    let list = deckgym::Deck::from_file("../decks/dustin/05-indeedee-stoutland.txt").unwrap();
    let opp = deckgym::Deck::from_file("../decks/screen/opponents/t-altaria.txt").unwrap();
    let params = PlayoutParams { rollouts: 4, cap: 12, z, noeffect, knowledge: Knowledge::Lab, ..PlayoutParams::new(3) };
    PlayoutPlayer::with_extra_lists(list, opp, params, Vec::new())
}

/// With `_noeffect` and nothing clearing the bar, kx3 doesn't spend Watch Over at full HP: it plays km3's choice among the
/// moves that do something, every move still played out; with the parameter off it plays km3's Watch Over.
#[test]
fn the_tie_break_turns_away_from_an_action_that_does_nothing() {
    let (seed, state) = [20_000_000_220u64, 20_000_000_221, 20_000_000_222, 20_000_000_223]
        .iter()
        .find_map(|&s| idle_watch_over(s).map(|st| (s, st)))
        .expect("a Watch Over at full HP came up");
    let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
    let actions = state.generate_possible_actions().1;
    let off = pilot05(false, 50.0).evaluate(&mut StdRng::seed_from_u64(seed), &observation, &actions);
    assert_eq!(off.chosen, 0, "{}", off.reason);
    assert!(matches!(off.candidates[0].action.action, SimpleAction::UseAbility { .. }));
    let on = pilot05(true, 50.0).evaluate(&mut StdRng::seed_from_u64(seed), &observation, &actions);
    assert_eq!(on.candidates.len(), off.candidates.len(), "nothing leaves the pool");
    assert!(on.dropped.is_empty());
    assert!(on.reason.starts_with("tie-break: no effect now"), "{}", on.reason);
    let chosen = &on.candidates[on.chosen].action;
    assert_eq!(effect_now(&state, chosen, &state.decks[0].cards), Some(true), "{chosen:?}");
}

// Item 3: the continuation experiment at the "neither" positions.

const NEITHER: &str = "../rl/results/playout_quiz4_items_2026-10-06/neither";

/// A position rebuilt from the development run (trainer_habits positions; checked there against the run's log).
fn neither(id: &str) -> State {
    serde_json::from_str(&std::fs::read_to_string(format!("{NEITHER}/states/{id}.json")).unwrap()).unwrap()
}

/// An entry of the experiment's plans file, as the runner reads it.
fn neither_entry(id: &str) -> serde_json::Value {
    let entries: Vec<serde_json::Value> = serde_json::from_str(&std::fs::read_to_string(format!("{NEITHER}/plans.json")).unwrap()).unwrap();
    entries.into_iter().find(|e| e["id"] == id).unwrap()
}

/// A step names the Pokémon whose Ability is used: at Q06 the Benched Indeedee ex's Watch Over is the one legal Ability
/// (the Active's was used this turn), so a step naming Indeedee ex on the Bench, or anywhere, names it; one naming the
/// Active, or Lillipup (no Ability), names no legal move; and no other move is an Ability step.
#[test]
fn an_ability_step_names_whose_ability_is_used() {
    let state = neither("Q06");
    let (me, legal) = state.generate_possible_actions();
    let found = |json: &str| -> Vec<Action> {
        let step: Step = serde_json::from_str(json).unwrap();
        legal.iter().filter(|a| step.matches(&state, me, a)).cloned().collect()
    };
    let bench = found(r#"{"do": "ability", "of": ["Indeedee ex"], "at": "bench"}"#);
    assert_eq!(bench.len(), 1, "{bench:?}");
    assert!(matches!(bench[0].action, SimpleAction::UseAbility { in_play_idx: 2 }), "{bench:?}");
    assert_eq!(found(r#"{"do": "ability", "of": ["Indeedee ex"]}"#), bench);
    assert!(found(r#"{"do": "ability", "of": ["Indeedee ex"], "at": "active"}"#).is_empty());
    assert!(found(r#"{"do": "ability", "of": ["Lillipup"]}"#).is_empty());
    let any = found(r#"{"do": "ability", "of": ["Indeedee ex", "Lillipup"]}"#);
    assert_eq!(any, bench);
    assert!(serde_json::from_str::<Step>(r#"{"do": "ability", "of": ["Indeedee ex"], "where": "bench"}"#).is_err(), "a misspelt field");
}

/// Dustin's Q06 plan, from the plans file, is played as he wrote it in every round: the Benched Indeedee ex's Watch Over
/// (the first move), retreat into Lillipup, the turn's Psychic to it, Tackle. After kx3's move (the turn's Psychic to the
/// Benched Indeedee ex) the Watch Over and the retreat are still played, but the Energy is spent, so Lillipup can't
/// Tackle: both steps are skipped, and km3 decides in their place.
#[test]
fn dustins_q06_plan_is_played_as_written() {
    let state = neither("Q06");
    let entry = neither_entry("Q06");
    let plan: Plan = serde_json::from_value(entry["plan"].clone()).unwrap();
    let (me, legal) = state.generate_possible_actions();
    let one = |step: &serde_json::Value| -> Action {
        let step: Step = serde_json::from_value(step.clone()).unwrap();
        let found: Vec<&Action> = legal.iter().filter(|a| step.matches(&state, me, a)).collect();
        assert_eq!(found.len(), 1, "{step:?}");
        found[0].clone()
    };
    let moves = [one(&entry["first_move"]), one(&entry["rival"])];
    let list = deckgym::Deck::from_file("../decks/dustin/05-indeedee-stoutland.txt").unwrap();
    let opp = deckgym::Deck::from_file("../decks/screen/opponents/t-lucario.txt").unwrap();
    let params = PlayoutParams { rollouts: 4, cap: 12, z: 2.0, knowledge: Knowledge::Lab, ..PlayoutParams::new(3) };
    let mut pilot = PlayoutPlayer::with_extra_lists(list, opp, params, Vec::new());
    let observation = PlayerObservation::from_state(&state, me, &RevealedKnowledge::default());
    let report = pilot.continuation_study(&mut StdRng::seed_from_u64(20_000_000_224), &observation, &moves, &plan, 1, 4);
    assert_eq!(report.failed_rounds, 0);
    let (planned, rival) = (&report.moves[0], &report.moves[1]);
    assert_eq!(planned.counts.fired[0], vec![4, 4, 4, 4], "{:?}", planned.counts);
    assert_eq!(rival.counts.fired[0], vec![4, 4, 0, 0], "{:?}", rival.counts);
    assert_eq!(rival.counts.skipped[0], vec![0, 0, 4, 4], "{:?}", rival.counts);
    assert_eq!(planned.plan_trace[0], "t4 first move: use the Benched Indeedee ex's Ability", "{:?}", planned.plan_trace);
    for line in ["t4 plan: retreat into the Benched Lillipup", "t4 plan: the turn's Psychic to the Active Lillipup", "t4 plan: attack Tackle"] {
        assert!(planned.plan_trace.iter().any(|l| l == line), "{line}: {:?}", planned.plan_trace);
    }
}
