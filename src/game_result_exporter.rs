//! Compact, terminal-only simulation result export.
//!
//! This handler is intentionally separate from `DataExporter`: it records one complete result
//! after `on_game_end` and never clones or serializes a per-ply `State`.

use log::warn;
use serde::{Deserialize, Serialize};
use std::{
    any::Any,
    fs::{self, OpenOptions},
    io::{self, Write},
    path::{Path, PathBuf},
};
use uuid::Uuid;

use crate::{
    actions::Action,
    game::GameRandomness,
    models::EnergyType,
    simulation_event_handler::SimulationEventHandler,
    state::GameOutcome,
    Deck, State,
};

pub const GAME_RESULT_SCHEMA: &str = "pdl-game-result/v1";

/// Ordered deck identity as supplied to the simulation.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ExportedDeck {
    pub card_ids: Vec<String>,
    pub energy_types: Vec<EnergyType>,
}

impl ExportedDeck {
    fn from_deck(deck: &Deck) -> Self {
        Self {
            card_ids: deck.cards.iter().map(|card| card.get_id()).collect(),
            energy_types: deck.energy_types.clone(),
        }
    }
}

/// Seat-ordered inputs required to interpret a result without a trace snapshot.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ExportedMatchup {
    pub decks: [ExportedDeck; 2],
    pub player_codes: [String; 2],
}

impl ExportedMatchup {
    pub fn from_decks(
        deck_a: &Deck,
        deck_b: &Deck,
        player_codes: Vec<String>,
    ) -> Result<Self, String> {
        let player_codes: [String; 2] = player_codes.try_into().map_err(|labels: Vec<String>| {
            format!(
                "game result matchup requires exactly 2 player-code labels, received {}",
                labels.len()
            )
        })?;
        Ok(Self {
            decks: [ExportedDeck::from_deck(deck_a), ExportedDeck::from_deck(deck_b)],
            player_codes,
        })
    }
}

/// Whether the result callback and final referee state form a usable completed result.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum GameCompletion {
    Completed,
    Incomplete,
    Inconsistent,
}

/// One compact, terminal callback record. `randomness: None` is explicit and must not be treated
/// by consumers as a seeded/replay-bound result.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ExportedGameResult {
    pub schema: String,
    pub game_id: String,
    pub engine_version: String,
    pub randomness: Option<GameRandomness>,
    pub outcome: Option<GameOutcome>,
    pub state_winner: Option<GameOutcome>,
    pub completion: GameCompletion,
    pub lifecycle_errors: usize,
    pub plies: u32,
    pub actions_by_player: [u32; 2],
    pub final_turn: u8,
    pub final_points: [u8; 2],
    pub matchup: ExportedMatchup,
}

#[derive(Debug, Clone)]
struct ActiveGame {
    game_id: Uuid,
    randomness: Option<GameRandomness>,
    plies: u32,
    actions_by_player: [u32; 2],
    failure_count_at_start: usize,
}

/// Results-only event handler. A simulation creates one instance per game and merges their
/// failure counts into the main instance after all games finish.
pub struct GameResultExporter {
    output_folder: PathBuf,
    matchup: ExportedMatchup,
    active: Option<ActiveGame>,
    failure_count: usize,
}

impl GameResultExporter {
    pub fn new(output_folder: PathBuf, matchup: ExportedMatchup) -> Self {
        Self {
            output_folder,
            matchup,
            active: None,
            failure_count: 0,
        }
    }

    pub fn failure_count(&self) -> usize {
        self.failure_count
    }

    fn record_failure(&mut self, message: impl std::fmt::Display) {
        self.failure_count = self.failure_count.saturating_add(1);
        warn!("Game result export failure: {message}");
    }

    fn publish(&self, result: &ExportedGameResult) -> io::Result<()> {
        fs::create_dir_all(&self.output_folder)?;
        let final_path = self
            .output_folder
            .join(format!("game_{}.json", result.game_id));
        let temp_path = temporary_path(&self.output_folder, &result.game_id);

        let mut bytes = serde_json::to_vec_pretty(result)
            .map_err(|error| io::Error::new(io::ErrorKind::InvalidData, error.to_string()))?;
        bytes.push(b'\n');

        // A failed `create_new` means this process never owned the path, so it must not clean it.
        let mut file = OpenOptions::new()
            .write(true)
            .create_new(true)
            .open(&temp_path)?;
        let write_result = file.write_all(&bytes).and_then(|()| file.sync_all());
        drop(file);
        if let Err(error) = write_result {
            let _ = fs::remove_file(&temp_path);
            return Err(error);
        }

        // Linking a complete same-directory temporary to a new name is atomic and refuses to
        // replace an existing result. Readers therefore see either no file or complete JSON.
        if let Err(error) = fs::hard_link(&temp_path, &final_path) {
            let _ = fs::remove_file(&temp_path);
            return Err(error);
        }
        fs::remove_file(&temp_path)
    }
}

fn temporary_path(folder: &Path, game_id: &str) -> PathBuf {
    folder.join(format!(
        ".game_{game_id}.{}.{}.tmp",
        std::process::id(),
        Uuid::new_v4()
    ))
}

fn completion(outcome: Option<GameOutcome>, final_winner: Option<GameOutcome>) -> GameCompletion {
    match (outcome, final_winner) {
        (Some(GameOutcome::Win(seat)), Some(GameOutcome::Win(final_seat)))
            if seat < 2 && seat == final_seat =>
        {
            GameCompletion::Completed
        }
        (Some(GameOutcome::Tie), Some(GameOutcome::Tie)) => GameCompletion::Completed,
        (None, None) => GameCompletion::Incomplete,
        _ => GameCompletion::Inconsistent,
    }
}

impl SimulationEventHandler for GameResultExporter {
    fn on_game_start(&mut self, game_id: Uuid) {
        if let Some(previous) = self.active.take() {
            self.record_failure(format!(
                "game {game_id} started while game {} was still active",
                previous.game_id
            ));
        }
        self.active = Some(ActiveGame {
            game_id,
            randomness: None,
            plies: 0,
            actions_by_player: [0, 0],
            failure_count_at_start: self.failure_count,
        });
    }

    fn on_game_randomness(&mut self, game_id: Uuid, randomness: &GameRandomness) {
        let Some(active_game_id) = self.active.as_ref().map(|active| active.game_id) else {
            self.record_failure(format!("randomness arrived without an active game: {game_id}"));
            return;
        };
        if active_game_id != game_id {
            self.record_failure(format!(
                "randomness for unexpected game {game_id}; active game is {}",
                active_game_id
            ));
            return;
        }
        if self
            .active
            .as_ref()
            .expect("the matching active game was just checked")
            .randomness
            .is_some()
        {
            self.record_failure(format!("duplicate randomness for game {game_id}"));
            return;
        }
        self.active
            .as_mut()
            .expect("the matching active game was just checked")
            .randomness = Some(randomness.clone());
    }

    fn on_action(
        &mut self,
        game_id: Uuid,
        _state_before_action: &State,
        actor: usize,
        _playable_actions: &[Action],
        _action: &Action,
    ) {
        let Some(active_game_id) = self.active.as_ref().map(|active| active.game_id) else {
            self.record_failure(format!("action arrived without an active game: {game_id}"));
            return;
        };
        if active_game_id != game_id {
            self.record_failure(format!(
                "action for unexpected game {game_id}; active game is {}",
                active_game_id
            ));
            return;
        }
        if actor >= 2 {
            self.record_failure(format!("action for game {game_id} has invalid actor {actor}"));
            return;
        }
        let active = self
            .active
            .as_mut()
            .expect("the matching active game was just checked");
        active.plies = active.plies.saturating_add(1);
        active.actions_by_player[actor] = active.actions_by_player[actor].saturating_add(1);
    }

    fn on_game_end(&mut self, game_id: Uuid, state: State, outcome: Option<GameOutcome>) {
        let Some(active_game_id) = self.active.as_ref().map(|active| active.game_id) else {
            self.record_failure(format!("game end arrived without an active game: {game_id}"));
            return;
        };
        if active_game_id != game_id {
            self.record_failure(format!(
                "game end for unexpected game {game_id}; active game is {}",
                active_game_id
            ));
            return;
        }
        let active = self
            .active
            .take()
            .expect("the matching active game was just checked");
        let state_winner = state.winner;
        let completion = completion(outcome, state_winner);
        if active.randomness.is_none() {
            self.record_failure(format!(
                "game {game_id} ended without exactly one bound randomness event"
            ));
        }
        if completion != GameCompletion::Completed {
            self.record_failure(format!(
                "game {game_id} ended with {completion:?} result/state agreement"
            ));
        }
        let lifecycle_errors = self
            .failure_count
            .saturating_sub(active.failure_count_at_start);
        let record = ExportedGameResult {
            schema: GAME_RESULT_SCHEMA.to_string(),
            game_id: game_id.to_string(),
            engine_version: env!("CARGO_PKG_VERSION").to_string(),
            randomness: active.randomness,
            outcome,
            state_winner,
            completion,
            lifecycle_errors,
            plies: active.plies,
            actions_by_player: active.actions_by_player,
            final_turn: state.turn_count,
            final_points: state.points,
            matchup: self.matchup.clone(),
        };
        if let Err(error) = self.publish(&record) {
            self.record_failure(format!("could not publish game {game_id}: {error}"));
        }
    }

    fn on_simulation_end(&mut self) {
        if let Some(active) = self.active.take() {
            self.record_failure(format!(
                "simulation ended before game {} supplied on_game_end",
                active.game_id
            ));
        }
    }

    fn merge(&mut self, other: &dyn SimulationEventHandler) {
        let Some(other) = (other as &dyn Any).downcast_ref::<GameResultExporter>() else {
            self.record_failure("attempted to merge an incompatible event handler");
            return;
        };
        self.failure_count = self.failure_count.saturating_add(other.failure_count);
        if other.active.is_some() {
            self.record_failure("merged a game handler that never supplied on_game_end");
        }
    }
}
