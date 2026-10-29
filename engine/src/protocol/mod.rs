//! Upstream bot protocol v1 (JSON lines) plus opt-in `pdl_*` extensions. See docs/pdl-protocol-extensions.md.
pub mod bot;
pub mod view;

use crate::{actions::Action, observation::PlayerObservation, Deck, State};
use serde::{Deserialize, Serialize};

pub const PROTOCOL_VERSION: u32 = 1;

/// What one applied action did, as far as a public observer can tell.
#[derive(Debug, Clone, Copy, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
pub struct PublicEvent {
    pub actor: usize,
    pub was_choice: bool,
    /// The game RNG advanced during the action.
    pub chance: bool,
    pub cards_left_deck: [usize; 2],
}

/// engine -> bot
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct HelloMsg {
    #[serde(rename = "type")]
    pub kind: String,
    pub protocol: u32,
}

impl HelloMsg {
    pub fn new() -> Self {
        HelloMsg { kind: "hello".into(), protocol: PROTOCOL_VERSION }
    }
}

impl Default for HelloMsg {
    fn default() -> Self {
        Self::new()
    }
}

/// bot -> engine. Every key optional; unknown keys are ignored.
#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
pub struct HelloReply {
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub name: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub agent_snapshot: Option<bool>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub pdl_observation: Option<bool>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub pdl_events: Option<bool>,
}

/// engine -> bot
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct NewGameMsg {
    #[serde(rename = "type")]
    pub kind: String,
    pub game_id: String,
    pub you: usize,
    pub deck: Vec<String>,
    pub deck_definition: Option<Deck>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ActionMsg {
    pub i: usize,
    pub text: String,
    pub action: crate::actions::SimpleAction,
}

/// `pdl_events`: what happened since this bot's previous decide.
#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct SinceLast {
    pub opponent_choices: u64,
    pub chance_events: u64,
    pub cards_left_deck_mine: usize,
    pub cards_left_deck_opponent: usize,
}

/// engine -> bot
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct DecideMsg {
    #[serde(rename = "type")]
    pub kind: String,
    pub ply: u64,
    pub state: view::ViewState,
    pub actions: Vec<ActionMsg>,
    pub actor: usize,
    pub agent_snapshot: Option<State>,
    pub legal_actions: Option<Vec<Action>>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub pdl_observation: Option<PlayerObservation>,
    /// Present (maybe null) exactly when `pdl_observation` is.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub pdl_search_seed: Option<Option<u64>>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub pdl_since_last: Option<SinceLast>,
}

/// bot -> engine
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct DecideReply {
    pub i: usize,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub note: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub scores: Option<Vec<f64>>,
}
