//! The Tool-placement rule for the play-outs (Oct 6; Fable via Dustin; rl/results/playout_tool_rule_2026-10-06). Written
//! before the rule: every Tool text in the card database is read, and its conditions on the Pokémon it is attached to come
//! from the text; a Tool goes only where its effect can apply, and where no placement has one km3's choice stands; with
//! the rule off the play-outs are km3's (and kx3's) exactly, and with it on a play-out in which the rule never acts is
//! unchanged; the code spells the rule, and every code without it is unchanged.
//!
//! The same rule as a within-noise tie-break at kx3's own decision (Oct 6, the amended follow-up; written before the
//! tie-break; it replaces a candidate filter, because a planning bot must keep legal preparation moves evaluable): with
//! `_tools`, every placement stays in kx3's pool with its play-outs; only when no move clears the z bar, and km3's proposed
//! placement has no printed effect now while another placement has one, kx3 plays the placement with an effect that km3
//! prefers (the play-out rule's choice, same randomness), named "tie-break: Tool effect" in the trace. km3's placement is
//! kept when its play-outs lead that placement beyond the noise. With `_tools` off nothing changes.
use std::cell::Cell;
use std::rc::Rc;

use deckgym::actions::{Action, SimpleAction};
use deckgym::card_ids::CardId;
use deckgym::database::get_card_by_enum;
use deckgym::models::{Card, EnergyType, PlayedCard};
use deckgym::observation::{PlayerObservation, RevealedKnowledge};
use deckgym::players::playout_player::{
    kept_by_playouts, placements_with_effect, tie_break_placements, tool_conditions, Knowledge, PlayoutParams, PlayoutPlayer,
    Step, ToolRulePlayer, ToolSpot,
};
use deckgym::players::Player;
use deckgym::test_support::get_test_game_with_board;
use deckgym::{Deck, State};
use rand::{rngs::StdRng, SeedableRng};
use strum::IntoEnumIterator;

const POSITIONS: &str = "../rl/results/playout_continuation_2026-10-05/states";

/// Every Tool card of the database, one per distinct text.
fn tools() -> Vec<Card> {
    let mut seen = std::collections::BTreeSet::new();
    CardId::iter()
        .map(get_card_by_enum)
        .filter(|c| matches!(c, Card::Trainer(t) if format!("{:?}", t.trainer_card_type) == "Tool" && seen.insert(t.effect.clone())))
        .collect()
}

fn tool(name: &str) -> Card {
    CardId::iter().map(get_card_by_enum).find(|c| matches!(c, Card::Trainer(t) if t.name == name)).unwrap_or_else(|| panic!("{name}"))
}

fn effect(card: &Card) -> String {
    match card {
        Card::Trainer(t) => t.effect.clone(),
        _ => unreachable!(),
    }
}

/// Every Tool text the database holds is read: no condition word the rule doesn't know.
#[test]
fn every_tool_text_in_the_database_is_read() {
    let all = tools();
    assert!(all.len() >= 26, "{} Tool texts", all.len());
    for card in &all {
        tool_conditions(&effect(card)).unwrap_or_else(|e| panic!("{}: {e}", card.get_name()));
    }
}

/// The conditions come from the text: where the Pokémon must be, its stage, type, kind, Retreat Cost, earlier evolutions.
#[test]
fn the_conditions_come_from_the_text() {
    let c = |name: &str| tool_conditions(&effect(&tool(name))).unwrap();
    assert_eq!(c("Protective Poncho").spot, Some(ToolSpot::Bench));
    assert_eq!(c("Rocky Helmet").spot, Some(ToolSpot::Active));
    assert_eq!(c("Poison Barb").spot, Some(ToolSpot::Active));
    assert_eq!(c("Leftovers").spot, Some(ToolSpot::Active));
    assert_eq!(c("Elegant Cape").stage, Some(1));
    assert_eq!(c("Big Air Balloon").stage, Some(2));
    assert_eq!(c("Small Balloon").stage, Some(0));
    assert_eq!(c("Leaf Cape").energy, Some(EnergyType::Grass));
    assert_eq!(c("Steel Apron").energy, Some(EnergyType::Metal));
    let cord = c("Electrical Cord");
    assert_eq!((cord.energy, cord.spot), (Some(EnergyType::Lightning), Some(ToolSpot::Active)));
    let needle = c("Deceptive Needle");
    assert_eq!((needle.energy, needle.spot), (Some(EnergyType::Darkness), Some(ToolSpot::Active)));
    assert_eq!(c("Heavy Helmet").min_retreat, Some(3));
    let boat = c("Inflatable Boat");
    assert_eq!((boat.energy, boat.min_retreat), (Some(EnergyType::Water), Some(1)));
    assert_eq!(c("Small Balloon").min_retreat, Some(1));
    assert_eq!(c("Big Air Balloon").min_retreat, Some(1));
    assert!(c("Memory Light").previous_evolution);
    assert_eq!(c("Beastite").class.as_deref(), Some("Ultra Beast"));
    assert_eq!(c("Ancient Booster Energy Capsule").class.as_deref(), Some("Ancient"));
    assert_eq!(c("Future Booster Energy Capsule").class.as_deref(), Some("Future"));
    for free in ["Giant Cape", "Lum Berry", "Sitrus Berry", "Lucky Egg", "Rescue Scarf", "Lucky Mittens", "Clear Veil"] {
        assert_eq!(c(free), Default::default(), "{free} applies to any Pokémon anywhere");
    }
}

/// A board: the Active Alolan Ninetales ex (Stage 1, [W], Retreat Cost 2); the Bench Alolan Vulpix and Carvanha (Basics,
/// [W], Retreat Cost 1) and a Mega Sharpedo ex (Stage 1, [W], Retreat Cost 0).
fn board() -> State {
    let game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::B2029AlolanNinetalesEx),
            PlayedCard::from_id(CardId::B2028AlolanVulpix),
            PlayedCard::from_id(CardId::B4034Carvanha),
            PlayedCard::from_id(CardId::B4035MegaSharpedoEx),
        ],
        vec![PlayedCard::from_id(CardId::A1115Abra)],
    );
    game.get_state_clone()
}

fn frame(name: &str) -> Vec<Action> {
    let card = tool(name);
    (0..4).map(|i| Action { actor: 0, action: SimpleAction::AttachTool { in_play_idx: i, tool_card: card.clone() }, is_stack: true }).collect()
}

fn slots(actions: &[Action]) -> Vec<usize> {
    actions
        .iter()
        .map(|a| match a.action {
            SimpleAction::AttachTool { in_play_idx, .. } => in_play_idx,
            _ => unreachable!(),
        })
        .collect()
}

/// A Tool goes only where its effect can apply; with no such place, none is offered (and km3's choice stands).
#[test]
fn a_tool_goes_only_where_its_effect_can_apply() {
    let state = board();
    let effective = |name: &str| slots(&placements_with_effect(&state, &frame(name)));
    assert_eq!(effective("Elegant Cape"), vec![0, 3], "only on a Stage 1");
    assert_eq!(effective("Protective Poncho"), vec![1, 2, 3], "never on the Active");
    assert_eq!(effective("Rocky Helmet"), vec![0], "only on the Active");
    assert_eq!(effective("Giant Cape"), vec![0, 1, 2, 3]);
    assert_eq!(effective("Inflatable Boat"), vec![0, 1, 2], "a Retreat Cost to reduce");
    assert!(effective("Leaf Cape").is_empty(), "no [G] Pokémon");
}

/// A stand-in for km3 that picks the Tool's place in `prefer` if offered, else the first move offered.
#[derive(Debug)]
struct Prefers(usize);

impl Player for Prefers {
    fn decision_fn(&mut self, _: &mut StdRng, _: &PlayerObservation, actions: &[Action]) -> Action {
        actions.iter().find(|a| matches!(a.action, SimpleAction::AttachTool { in_play_idx, .. } if in_play_idx == self.0)).unwrap_or(&actions[0]).clone()
    }
    fn get_deck(&self) -> Deck {
        Deck::default()
    }
    fn decide_omniscient(&mut self, _: &mut StdRng, _: &State, actions: &[Action]) -> Action {
        actions[0].clone()
    }
}

/// km3's choice stands when it has an effect, or when no placement has one; otherwise km3 chooses again among the
/// placements that have one, and the intervention is counted.
#[test]
fn km3s_choice_stands_unless_it_has_no_effect_and_another_has() {
    let state = board();
    let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
    let choose = |prefer: usize, name: &str| {
        let interventions = Rc::new(Cell::new(0));
        let mut rule = ToolRulePlayer { inner: Box::new(Prefers(prefer)), interventions: interventions.clone() };
        let chosen = rule.decision_fn(&mut StdRng::seed_from_u64(1), &observation, &frame(name));
        (slots(&[chosen])[0], interventions.get())
    };
    assert_eq!(choose(3, "Elegant Cape"), (3, 0), "on a Stage 1: km3's choice");
    assert_eq!(choose(1, "Elegant Cape"), (0, 1), "on a Basic: chosen again among the Stage 1s");
    assert_eq!(choose(0, "Protective Poncho"), (1, 1), "on the Active: chosen again among the Bench");
    assert_eq!(choose(2, "Leaf Cape"), (2, 0), "no placement has an effect: km3's choice");
    // A decision that isn't a Tool's placement is km3's, untouched.
    let other = vec![Action { actor: 0, action: SimpleAction::EndTurn, is_stack: false }];
    let interventions = Rc::new(Cell::new(0));
    let mut rule = ToolRulePlayer { inner: Box::new(Prefers(0)), interventions: interventions.clone() };
    assert_eq!(rule.decision_fn(&mut StdRng::seed_from_u64(1), &observation, &other), other[0]);
    assert_eq!(interventions.get(), 0);
}

/// The code spells the rule (`_tools`), and every code without it is as before.
#[test]
fn the_code_spells_the_rule() {
    assert_eq!(PlayoutParams::new(3).code(), "kx3_r16_c12_z2_real_t0_poolwide");
    assert!(!PlayoutParams::new(3).tools);
    let on = PlayoutParams::parse("3_tools").unwrap();
    assert!(on.tools);
    assert_eq!(on.code(), "kx3_r16_c12_z2_real_t0_poolwide_tools");
    assert_eq!(PlayoutParams::parse(&on.code()[2..]).unwrap(), on);
}

fn deck(path: &str) -> Deck {
    Deck::from_file(path).unwrap()
}

fn position(id: &str) -> State {
    serde_json::from_str(&std::fs::read_to_string(format!("{POSITIONS}/{id}.json")).unwrap()).unwrap()
}

fn pilot(rounds: usize, tools: bool) -> PlayoutPlayer {
    let params = PlayoutParams { rollouts: rounds, cap: 12, z: 50.0, knowledge: Knowledge::Lab, tools, ..PlayoutParams::new(3) };
    PlayoutPlayer::with_extra_lists(
        deck("../decks/brews/drafts_2026-10-01/draft-A-shark-tempo.txt"),
        deck("../decks/computer/blastoise-wailord-deluxe.txt"),
        params,
        Vec::new(),
    )
}

/// With the rule off the play-outs are kx3's own (its `evaluate` scores at the same decision randomness); with it on, a
/// play-out in which it never acts ends in the same final state. At B-214254-t06 draft A's one Elegant Cape is already
/// on the Active Mega, so the rule never acts at all.
#[test]
fn with_the_rule_off_the_play_outs_are_kx3s_and_unacted_play_outs_are_unchanged() {
    let state = position("B-214254-t06");
    let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
    let actions = state.generate_possible_actions().1;
    let report = pilot(6, false).evaluate(&mut StdRng::seed_from_u64(20_000_000_201), &observation, &actions);
    let moves: Vec<Action> = report.candidates.iter().map(|c| c.action.clone()).collect();
    let study = pilot(6, false).tool_rule_study(&mut StdRng::seed_from_u64(20_000_000_201), &observation, &moves, 6);
    assert_eq!(study.failed_rounds, 0);
    for (m, c) in study.moves.iter().zip(&report.candidates) {
        let mean = m.off.iter().map(|o| o.score).sum::<f64>() / m.off.len() as f64;
        assert_eq!(mean, c.score, "{}", c.label);
        assert!(m.interventions.iter().all(|&n| n == 0), "{}", c.label);
        assert_eq!(m.on, m.off, "{}", c.label);
    }
}

/// At B-205731-t02 (draft A's turn 2, its one Elegant Cape still in the deck) km3 puts the Cape on a Basic in some
/// play-outs, but never while a Stage 1 Pokémon is in play to take it: the rule leaves km3's choice, and every round ends
/// as with the rule off. The study is deterministic.
#[test]
fn where_no_placement_has_an_effect_the_play_outs_are_unchanged() {
    let state = position("B-205731-t02");
    let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
    let water: Step = serde_json::from_str(r#"{"do": "energy", "to": ["Carvanha"], "at": "active"}"#).unwrap();
    let legal = state.generate_possible_actions().1;
    let first = legal.iter().find(|a| water.matches(&state, 0, a)).unwrap().clone();
    let run = || pilot(8, true).tool_rule_study(&mut StdRng::seed_from_u64(20_000_000_202), &observation, &[first.clone()], 8);
    let (a, b) = (run(), run());
    let m = &a.moves[0];
    assert!(m.interventions.iter().all(|&n| n == 0), "{:?}", m.interventions);
    assert_eq!(m.on, m.off);
    assert_eq!(a.moves[0].on, b.moves[0].on);
}

/// Records the Tool placements of the player it wraps, with whether a Benched Pokémon was there to take one.
#[derive(Debug)]
struct Recorder {
    inner: ToolRulePlayer,
    placed: Rc<std::cell::RefCell<Vec<(String, usize, bool)>>>,
}

impl Player for Recorder {
    fn decision_fn(&mut self, rng: &mut StdRng, observation: &PlayerObservation, actions: &[Action]) -> Action {
        let a = self.inner.decision_fn(rng, observation, actions);
        if let SimpleAction::AttachTool { in_play_idx, tool_card } = &a.action {
            let state = observation.visible_state();
            let bench = state.in_play_pokemon[a.actor].iter().skip(1).any(|p| p.is_some());
            self.placed.borrow_mut().push((tool_card.get_name(), *in_play_idx, bench));
        }
        a
    }
    fn get_deck(&self) -> Deck {
        self.inner.get_deck()
    }
    fn decide_omniscient(&mut self, rng: &mut StdRng, state: &State, actions: &[Action]) -> Action {
        self.inner.decide_omniscient(rng, state, actions)
    }
}

/// Where km3 would misplace a Tool, the rule acts. In the development run's km3 game
/// `05-indeedee-stoutland|t-altaria|0|0|ref` (seed 24,450,000,000, the deck in seat 0) km3 put Protective Poncho on its
/// Active Indeedee ex with a Bench to take it; with the rule, every Poncho of that seat goes to the Bench when there is
/// one, and the rule's interventions are counted.
#[test]
fn where_km3_would_misplace_a_tool_the_rule_acts() {
    use deckgym::players::{create_players, PlayerCode};
    let (d0, d1) = (deck("../decks/dustin/05-indeedee-stoutland.txt"), deck("../decks/screen/opponents/t-altaria.txt"));
    let code = PlayerCode::KM { max_depth: 3 };
    let mut players = create_players(d0, d1, vec![code.clone(), code]);
    let km = players.remove(0);
    let interventions = Rc::new(Cell::new(0));
    let placed = Rc::new(std::cell::RefCell::new(Vec::new()));
    players.insert(0, Box::new(Recorder { inner: ToolRulePlayer { inner: km, interventions: interventions.clone() }, placed: placed.clone() }));
    let mut game = deckgym::Game::new(players, 24_450_000_000);
    while !game.is_game_over() {
        game.play_tick();
    }
    let placed = placed.borrow();
    assert!(interventions.get() > 0, "{placed:?}");
    for (name, slot, bench) in placed.iter() {
        if name == "Protective Poncho" && *bench {
            assert!(*slot > 0, "{placed:?}");
        }
    }
}

/// The tie-break's premise on its own: km3's proposal is a placement without an effect now and another placement has one.
/// Then it names the placements with one and why km3's has none; otherwise nothing.
#[test]
fn the_tie_break_applies_only_when_km3_proposes_a_placement_without_effect() {
    let state = board();
    let premise = |name: &str, proposal: usize| {
        let actions = frame(name);
        tie_break_placements(&state, &actions, &actions[proposal]).map(|(effective, why)| (slots(&effective), why))
    };
    assert_eq!(premise("Elegant Cape", 3), None, "km3's placement has an effect");
    assert_eq!(premise("Leaf Cape", 2), None, "no placement has an effect");
    let (effective, why) = premise("Elegant Cape", 1).unwrap();
    assert_eq!(effective, vec![0, 3]);
    assert!(why.contains("Elegant Cape") && why.contains("Stage 1"), "{why}");
    let (effective, why) = premise("Protective Poncho", 0).unwrap();
    assert_eq!(effective, vec![1, 2, 3]);
    assert!(why.contains("Protective Poncho") && why.contains("Bench"), "{why}");
    let mut mixed = frame("Protective Poncho");
    mixed.push(Action { actor: 0, action: SimpleAction::EndTurn, is_stack: false });
    assert_eq!(tie_break_placements(&state, &mixed, &mixed[4]), None, "a proposal that isn't a placement");
}

/// km3's placement without effect is kept only when its play-outs lead the placement with an effect beyond the noise: by
/// more than z standard errors of the paired difference (`diff` is that placement's lead over km3's).
#[test]
fn km3s_placement_is_kept_only_by_a_lead_beyond_the_noise() {
    assert!(kept_by_playouts(-0.20, 0.05, 2.0), "km3's placement leads by 4 standard errors: kept");
    assert!(!kept_by_playouts(-0.05, 0.05, 2.0), "a lead of 1 standard error is noise: the tie-break applies");
    assert!(!kept_by_playouts(0.05, 0.05, 2.0), "the placement with an effect leads: the tie-break applies");
    assert!(!kept_by_playouts(-0.30, f64::INFINITY, 2.0), "with fewer than 2 rounds there is no lead beyond the noise");
}

/// The first decision of `actor` in the km3 game (`deck0` v `deck1`, `seed`) that places `name`, with a check on the
/// state: the state and its legal moves.
fn placement_decision(deck0: &str, deck1: &str, seed: u64, actor: usize, name: &str, ok: impl Fn(&State) -> bool) -> (State, Vec<Action>) {
    use deckgym::players::{create_players, PlayerCode};
    let code = PlayerCode::KM { max_depth: 3 };
    let mut game = deckgym::Game::new(create_players(deck(deck0), deck(deck1), vec![code.clone(), code]), seed);
    while !game.is_game_over() {
        let state = game.get_state_clone();
        let (who, actions) = state.generate_possible_actions();
        let places = actions.iter().all(|a| matches!(&a.action, SimpleAction::AttachTool { tool_card, .. } if tool_card.get_name() == name));
        if who == actor && actions.len() > 1 && places && ok(&state) {
            return (state, actions);
        }
        game.play_tick();
    }
    panic!("no {name} placement for player {actor}");
}

const DECK05: &str = "../decks/dustin/05-indeedee-stoutland.txt";
const ALTARIA: &str = "../decks/screen/opponents/t-altaria.txt";

fn pilot_for(list: &str, opponent: &str, tools: bool, z: f64) -> PlayoutPlayer {
    let params = PlayoutParams { rollouts: 2, cap: 12, z, knowledge: Knowledge::Lab, tools, ..PlayoutParams::new(3) };
    PlayoutPlayer::with_extra_lists(deck(list), deck(opponent), params, Vec::new())
}

/// Deck 05's first Protective Poncho in the development run's km3 game `05-indeedee-stoutland|t-altaria|0|0|ref`
/// (seed 24,450,000,000), with Pokémon on the Bench: km3 proposes the Active.
fn poncho_decision() -> (State, Vec<Action>) {
    placement_decision(DECK05, ALTARIA, 24_450_000_000, 0, "Protective Poncho", |s| s.in_play_pokemon[0].iter().skip(1).any(|p| p.is_some()))
}

/// Every distinct legal placement, sorted.
fn offered(actions: &[Action]) -> Vec<usize> {
    let mut v = slots(actions);
    v.sort();
    v.dedup();
    v
}

/// With `_tools` off, kx3's pool at that decision is every distinct legal placement, km3's first, nothing dropped, and
/// no tie-break.
#[test]
fn with_the_parameter_off_kx3s_pool_is_unfiltered() {
    let (state, actions) = poncho_decision();
    let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
    let report = pilot_for(DECK05, ALTARIA, false, 50.0).evaluate(&mut StdRng::seed_from_u64(20_000_000_203), &observation, &actions);
    assert_eq!(slots(&[report.candidates[0].action.clone()]), vec![0], "the premise: km3 proposes the Active");
    let mut pooled = slots(&report.candidates.iter().map(|c| c.action.clone()).collect::<Vec<_>>());
    pooled.sort();
    assert_eq!(pooled, offered(&actions));
    assert!(report.dropped.is_empty(), "{:?}", report.dropped);
    assert_eq!(report.chosen, 0, "z 50: km3's move");
    assert!(!report.reason.contains("tie-break"), "{}", report.reason);
}

/// With `_tools` on, every placement stays in the pool and is played out; with z 50 no move clears the bar, so the
/// tie-break plays the Poncho on the Bench: km3's choice among the placements with an effect (the play-out rule's, same
/// randomness), named in the reason.
#[test]
fn with_the_parameter_on_every_placement_stays_and_the_tie_break_chooses_one_with_effect() {
    use deckgym::players::{create_players, PlayerCode};
    let (state, actions) = poncho_decision();
    let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
    let seed = 20_000_000_204;
    let report = pilot_for(DECK05, ALTARIA, true, 50.0).evaluate(&mut StdRng::seed_from_u64(seed), &observation, &actions);
    let mut pooled = slots(&report.candidates.iter().map(|c| c.action.clone()).collect::<Vec<_>>());
    assert_eq!(pooled[0], 0, "km3's proposal leads the pool");
    pooled.sort();
    assert_eq!(pooled, offered(&actions), "nothing leaves the pool");
    assert!(report.dropped.is_empty(), "{:?}", report.dropped);
    assert!(report.rounds > 0 && report.candidates.iter().all(|c| c.score.is_finite()), "every placement is played out");
    assert!(report.reason.starts_with("tie-break: Tool effect"), "{}", report.reason);
    let km = create_players(deck(DECK05), deck(ALTARIA), vec![PlayerCode::KM { max_depth: 3 }, PlayerCode::KM { max_depth: 3 }]).remove(0);
    let mut rule = ToolRulePlayer { inner: km, interventions: Rc::new(Cell::new(0)) };
    let preferred = rule.decision_fn(&mut StdRng::seed_from_u64(seed), &observation, &actions);
    assert!(slots(&[preferred.clone()])[0] > 0);
    assert_eq!(report.candidates[report.chosen].action, preferred);
}

/// Where no placement has an effect (deck 09's Elegant Cape with only Basics in play, the development run's km3 game
/// `09-mega-manectric-heliolisk|t-altaria|1|0|ref`, seed 24,400,000,001), the pool is the same with `_tools` on, and
/// there is no tie-break.
#[test]
fn where_no_placement_has_an_effect_there_is_no_tie_break() {
    let deck09 = "../decks/dustin/09-mega-manectric-heliolisk.txt";
    let (state, actions) = placement_decision(deck09, ALTARIA, 24_400_000_001, 0, "Elegant Cape", |_| true);
    assert!(placements_with_effect(&state, &actions).is_empty(), "the premise: no Stage 1 in play");
    let observation = PlayerObservation::from_state(&state, 0, &RevealedKnowledge::default());
    let pool = |tools: bool| {
        let r = pilot_for(deck09, ALTARIA, tools, 50.0).evaluate(&mut StdRng::seed_from_u64(20_000_000_205), &observation, &actions);
        assert!(!r.reason.contains("tie-break"), "{}", r.reason);
        (r.candidates.iter().map(|c| c.action.clone()).collect::<Vec<_>>(), r.dropped.len(), r.chosen)
    };
    assert_eq!(pool(true), pool(false));
}
