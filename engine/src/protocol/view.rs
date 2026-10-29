//! Port of upstream's `ViewState` (replay/view.rs) built from a `PlayerObservation` only.
use crate::{
    models::{Card, EnergyType, StatusCondition},
    observation::PlayerObservation,
    state::{EnergyZone, GameOutcome, PlayedCard},
};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct SlotView {
    pub card: String,
    pub hp: u32,
    pub max_hp: u32,
    pub energy: Vec<EnergyType>,
    pub tools: Vec<String>,
    pub status: Vec<StatusCondition>,
    pub played_this_turn: bool,
}

impl SlotView {
    fn from_played_card(card: &PlayedCard) -> Self {
        let mut status = Vec::new();
        if card.is_poisoned() {
            status.push(StatusCondition::Poisoned);
        }
        if card.is_paralyzed() {
            status.push(StatusCondition::Paralyzed);
        }
        if card.is_asleep() {
            status.push(StatusCondition::Asleep);
        }
        if card.is_burned() {
            status.push(StatusCondition::Burned);
        }
        if card.is_confused() {
            status.push(StatusCondition::Confused);
        }
        SlotView {
            card: card.get_id(),
            hp: card.get_remaining_hp(),
            max_hp: card.get_effective_total_hp(),
            energy: card.attached_energy.clone(),
            tools: card.attached_tools.iter().map(Card::get_id).collect(),
            status,
            played_this_turn: card.played_this_turn,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct PlayerView {
    /// `None` for the opponent: only `hand_count` is visible.
    pub hand: Option<Vec<String>>,
    pub hand_count: usize,
    pub deck_count: usize,
    pub discard: Vec<String>,
    pub discard_energies: Vec<EnergyType>,
    pub energy_zone: EnergyZone,
    /// 0 = active, 1..=3 = bench.
    pub in_play: [Option<SlotView>; 4],
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ViewState {
    pub turn: u8,
    pub current_player: usize,
    pub points: [u8; 2],
    pub winner: Option<GameOutcome>,
    pub players: [PlayerView; 2],
    pub stadium: Option<String>,
}

impl ViewState {
    pub fn for_observation(obs: &PlayerObservation) -> ViewState {
        let me = obs.actor;
        let v = obs.visible_state();
        let players = std::array::from_fn(|p| {
            let hand_ids: Vec<String> = v.hands[p].iter().map(Card::get_id).collect();
            PlayerView {
                hand_count: hand_ids.len(),
                hand: if p == me { Some(hand_ids) } else { None },
                deck_count: if p == me {
                    obs.known_own_deck.len()
                } else {
                    v.decks[p].cards.len()
                },
                discard: v.discard_piles[p].iter().map(Card::get_id).collect(),
                discard_energies: v.discard_energies[p].clone(),
                energy_zone: v.energy_zone[p],
                in_play: std::array::from_fn(|i| {
                    v.in_play_pokemon[p][i]
                        .as_ref()
                        .map(SlotView::from_played_card)
                }),
            }
        });
        ViewState {
            turn: v.turn_count,
            current_player: v.current_player,
            points: v.points,
            winner: v.winner,
            players,
            stadium: v.active_stadium.as_ref().map(Card::get_id),
        }
    }
}
