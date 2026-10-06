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
use std::collections::BTreeSet;

use deckgym::actions::{Action, SimpleAction};
use deckgym::observation::{PlayerObservation, RevealedKnowledge};
use deckgym::card_ids::CardId;
use deckgym::database::get_card_by_enum;
use deckgym::models::{Card, PlayedCard};
use deckgym::players::playout_player::{
    effect_needs, effect_now, switch_bar, CardKind, DecisionReport, Knowledge, Need, PlayoutParams, PlayoutPlayer, PokemonFilter,
    Reading, Scope,
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


/// Every distinct Item, Supporter and Stadium text and every Ability text in the card database.
fn texts() -> Vec<(String, String)> {
    let mut seen = BTreeSet::new();
    let mut out = Vec::new();
    for card in CardId::iter().map(get_card_by_enum) {
        let (name, text) = match &card {
            Card::Trainer(t) if matches!(format!("{:?}", t.trainer_card_type).as_str(), "Item" | "Supporter" | "Stadium") => (t.name.clone(), t.effect.clone()),
            Card::Pokemon(p) => match &p.ability {
                Some(a) => (format!("{}'s {}", p.name, a.title), a.effect.clone()),
                None => continue,
            },
            _ => continue,
        };
        if seen.insert(text.clone()) {
            out.push((name, text));
        }
    }
    out
}

/// Every text is either read or named unread (never a panic), and the texts of the cards the quiz notes name are read.
#[test]
fn every_text_is_read_or_named_unread() {
    let all = texts();
    assert!(all.len() >= 250, "{} texts", all.len());
    let read = all.iter().filter(|(_, t)| effect_needs(t).is_ok()).count();
    eprintln!("{read} of {} texts read", all.len());
    for (name, text) in &all {
        if let Err(why) = effect_needs(text) {
            eprintln!("unread: {name}: {why}");
        }
    }
    for name in ["Indeedee ex's Watch Over", "Fragrant Forest", "Clemont's Backpack", "Poké Ball", "Potion", "Pokémon Center Lady", "Professor's Research"] {
        let (_, text) = all.iter().find(|(n, _)| n == name).unwrap_or_else(|| panic!("{name}"));
        assert!(effect_needs(text).is_ok(), "{name}: {:?}", effect_needs(text));
    }
}

fn text_of(name: &str) -> String {
    texts().into_iter().find(|(n, _)| n == name).unwrap_or_else(|| panic!("{name}")).1
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
