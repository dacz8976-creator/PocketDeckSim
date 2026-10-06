//! The Tool-placement rule for the play-outs (Oct 6; Fable via Dustin; rl/results/playout_tool_rule_2026-10-06/README.md):
//! in a play-out, a Tool is attached only where its printed effect can apply. Off by default (`_tools` turns it on);
//! km<N> itself is untouched, and so is kx<N>'s own move: only the play-outs' km<N> on both sides is wrapped.
//!
//! Decided by each Tool's text, read from the card database, never by a list of names. The text's conditions on "the
//! ... Pokémon this card is attached to" are read off its words:
//! - where it must be: "is in the Active Spot" / "is your Active Pokémon", or "is on your Bench";
//! - its stage ("Basic", "Stage 1", "Stage 2"), its type ("[W]", ...), its kind ("Ancient", "Future", "Ultra Beast"),
//!   "has a Retreat Cost of N or more" (N from the text), "previous Evolutions";
//! - a Tool that lowers or removes the Retreat Cost needs one to lower.
//!
//! Conditions of the moment (damage, Special Conditions, a Knock Out to come) can come true anywhere, so they don't limit
//! where it goes. A text with a condition word this reader doesn't know is an error (a test reads every Tool in the
//! database), and in play it limits nothing.
//!
//! The rule at a Tool's placement:
//! - km<N> chooses as always;
//! - if its choice has no effect and some placement has one, km<N> chooses again, with the same decision randomness,
//!   among the placements that have one;
//! - where no placement has an effect, km<N>'s choice stands.
//!
//! So a play-out in which km<N> never misplaces a Tool is km<N>'s exactly, and the interventions are counted.
use std::cell::Cell;
use std::rc::Rc;

use rand::rngs::StdRng;

use crate::actions::{Action, SimpleAction};
use crate::hooks::{is_ancient_pokemon, is_future_pokemon, is_ultra_beast};
use crate::models::{Card, EnergyType, PlayedCard};
use crate::observation::PlayerObservation;
use crate::players::Player;
use crate::{Deck, State};

/// Where a Tool's text needs the Pokémon to be.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ToolSpot {
    Active,
    Bench,
}

/// A Tool text's conditions on the Pokémon it is attached to (none: any Pokémon, anywhere).
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct ToolConditions {
    pub spot: Option<ToolSpot>,
    pub stage: Option<u8>,
    pub energy: Option<EnergyType>,
    /// "Ancient", "Future" or "Ultra Beast".
    pub class: Option<String>,
    /// The Pokémon's printed Retreat Cost must be at least this.
    pub min_retreat: Option<usize>,
    /// It must have earlier evolutions (Stage 1 or later).
    pub previous_evolution: bool,
}

const HOLDER: &str = "this card is attached to";

fn energy_of(symbol: &str) -> Option<EnergyType> {
    Some(match symbol {
        "[g]" => EnergyType::Grass,
        "[r]" => EnergyType::Fire,
        "[w]" => EnergyType::Water,
        "[l]" => EnergyType::Lightning,
        "[p]" => EnergyType::Psychic,
        "[f]" => EnergyType::Fighting,
        "[d]" => EnergyType::Darkness,
        "[m]" => EnergyType::Metal,
        "[c]" => EnergyType::Colorless,
        _ => return None,
    })
}

/// The conditions a Tool's text puts on the Pokémon it is attached to, read off its words.
pub fn tool_conditions(effect: &str) -> Result<ToolConditions, String> {
    let text = effect.to_lowercase();
    let mut c = ToolConditions::default();
    let mut from = 0;
    while let Some(i) = text[from..].find(HOLDER) {
        let at = from + i;
        from = at + HOLDER.len();
        let before = text[..at].trim_end();
        let after = text[at + HOLDER.len()..].trim_start();
        // The holder: "the <qualifiers> Pokémon" or "the <qualifiers> Ultra Beast" just before ("If this card is
        // attached to 1 of your Pokémon" names no holder).
        let noun = ["pokémon", "ultra beast"].into_iter().find(|n| before.ends_with(n));
        let Some(noun) = noun else { continue };
        let Some(the) = before.rfind("the ") else { continue };
        if noun == "ultra beast" {
            c.class = Some("Ultra Beast".to_string());
        }
        let qualifiers: Vec<&str> = before[the + 4..before.len() - noun.len()].split_whitespace().collect();
        let mut k = 0;
        while k < qualifiers.len() {
            match qualifiers[k] {
                "basic" => c.stage = Some(0),
                "stage" => {
                    let n = qualifiers.get(k + 1).and_then(|n| n.parse::<u8>().ok()).ok_or("a stage without a number")?;
                    c.stage = Some(n);
                    k += 1;
                }
                "ancient" => c.class = Some("Ancient".to_string()),
                "future" => c.class = Some("Future".to_string()),
                w => match energy_of(w) {
                    Some(e) => c.energy = Some(e),
                    None => return Err(format!("unknown condition word '{w}' in \"{effect}\"")),
                },
            }
            k += 1;
        }
        if after.starts_with("is in the active spot") || after.starts_with("is your active pokémon") {
            c.spot = Some(ToolSpot::Active);
        } else if after.starts_with("is on your bench") {
            c.spot = Some(ToolSpot::Bench);
        } else if let Some(rest) = after.strip_prefix("has a retreat cost of ") {
            let n = rest.split_whitespace().next().and_then(|n| n.parse::<usize>().ok()).ok_or("a Retreat Cost without a number")?;
            if rest.contains("or more") {
                c.min_retreat = Some(n);
            }
        } else if after.starts_with("has no retreat cost") {
            c.min_retreat = Some(1);
        }
        // "The Retreat Cost of the ... Pokémon this card is attached to is 1 less": there must be a cost to lower.
        if text[..the].trim_end().ends_with("retreat cost of") && after.starts_with("is") && after.contains("less") {
            c.min_retreat = Some(c.min_retreat.unwrap_or(0).max(1));
        }
    }
    if text.contains("its previous evolutions") {
        c.previous_evolution = true;
    }
    Ok(c)
}

/// Whether the conditions hold for `holder` at `in_play_idx` (0, the Active Spot).
pub fn conditions_hold(c: &ToolConditions, holder: &PlayedCard, in_play_idx: usize) -> bool {
    let Card::Pokemon(p) = &holder.card else { return false };
    let spot = match c.spot {
        Some(ToolSpot::Active) => in_play_idx == 0,
        Some(ToolSpot::Bench) => in_play_idx > 0,
        None => true,
    };
    let class = match c.class.as_deref() {
        Some("Ancient") => is_ancient_pokemon(&p.name),
        Some("Future") => is_future_pokemon(&p.name),
        Some("Ultra Beast") => is_ultra_beast(&p.name),
        _ => true,
    };
    spot
        && class
        && c.stage.map_or(true, |s| p.stage == s)
        && c.energy.map_or(true, |e| p.energy_type == e)
        && c.min_retreat.map_or(true, |n| p.retreat_cost.len() >= n)
        && (!c.previous_evolution || p.stage >= 1)
}

/// The Tool placements among `actions` where the Tool's effect can apply (a text this reader can't read limits nothing).
pub fn placements_with_effect(state: &State, actions: &[Action]) -> Vec<Action> {
    actions
        .iter()
        .filter(|a| match &a.action {
            SimpleAction::AttachTool { in_play_idx, tool_card: Card::Trainer(tool) } => {
                let holder = state.in_play_pokemon[a.actor].get(*in_play_idx).and_then(|p| p.as_ref());
                match (tool_conditions(&tool.effect), holder) {
                    (Ok(c), Some(h)) => conditions_hold(&c, h, *in_play_idx),
                    (Err(_), Some(_)) => true,
                    _ => false,
                }
            }
            _ => false,
        })
        .cloned()
        .collect()
}

/// km<N> in a play-out, with the rule at its Tool placements; `interventions` counts the placements it changed.
#[derive(Debug)]
pub struct ToolRulePlayer {
    pub inner: Box<dyn Player>,
    pub interventions: Rc<Cell<usize>>,
}

impl Player for ToolRulePlayer {
    fn decision_fn(&mut self, rng: &mut StdRng, observation: &PlayerObservation, possible_actions: &[Action]) -> Action {
        let start = rng.clone();
        let choice = self.inner.decision_fn(rng, observation, possible_actions);
        if matches!(choice.action, SimpleAction::AttachTool { .. }) {
            let effective = placements_with_effect(observation.visible_state(), possible_actions);
            if !effective.is_empty() && !effective.contains(&choice) {
                self.interventions.set(self.interventions.get() + 1);
                let mut again = start;
                return self.inner.decision_fn(&mut again, observation, &effective);
            }
        }
        choice
    }

    fn get_deck(&self) -> Deck {
        self.inner.get_deck()
    }

    fn decide_omniscient(&mut self, rng: &mut StdRng, state: &State, possible_actions: &[Action]) -> Action {
        self.inner.decide_omniscient(rng, state, possible_actions)
    }
}
