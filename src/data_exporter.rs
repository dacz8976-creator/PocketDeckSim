use crate::actions::Action;
use crate::game::{
    DecisionRandomness, GameRandomness, LuxuryCoinResolutionRecord, PrivateRevealRecord,
    PublicRevealRecord,
};
use crate::simulation_event_handler::SimulationEventHandler;
use crate::state::{GameOutcome, State};
use log::warn;
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;
use uuid::Uuid;

/// Struct to hold the exported data point (state, action pair)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExportedDataPoint {
    pub game_id: String,
    pub ply: u32,
    pub actor: usize,
    pub state: State,
    pub playable_actions: Vec<Action>,
    pub chosen_action: Action,
    #[serde(default)]
    pub randomness: Option<GameRandomness>,
    #[serde(default)]
    pub decision_randomness: Option<DecisionRandomness>,
    #[serde(default)]
    pub information_model: Option<String>,
    #[serde(default)]
    pub unpriced_branches: Vec<crate::observation::UnpricedBranch>,
    /// Successful checks at hypothetical search leaves, not whole-root loss claims.
    /// None means no collection occurred; Some with zero counts means collection found none.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub public_reply_evidence: Option<crate::public_reply_evidence::PublicReplyEvidence>,
    /// Privileged referee result for card effects that reveal concealed information. Policy
    /// observations never receive this field.
    #[serde(default)]
    pub private_reveals: Vec<PrivateRevealRecord>,
    #[serde(default)]
    pub public_reveals: Vec<PublicRevealRecord>,
    #[serde(default)]
    pub luxury_coin_resolutions: Vec<LuxuryCoinResolutionRecord>,
}

/// Event handler that exports (state, action) pairs to JSON files
pub struct DataExporter {
    output_folder: PathBuf,
    ply_counter: u32,
    current_game_id: Option<Uuid>,
    randomness: Option<GameRandomness>,
    decision_randomness: Option<DecisionRandomness>,
    information_model: Option<String>,
    unpriced_branches: Vec<crate::observation::UnpricedBranch>,
    public_reply_evidence: Option<crate::public_reply_evidence::PublicReplyEvidence>,
    /// Held until action resolution so all reveal results are attached before one write.
    /// The next-action and game-end flushes also support manual event-handler callers.
    pending_data_point: Option<ExportedDataPoint>,
}

impl DataExporter {
    pub fn new(output_folder: PathBuf) -> Self {
        Self {
            output_folder,
            ply_counter: 0,
            current_game_id: None,
            randomness: None,
            decision_randomness: None,
            information_model: None,
            unpriced_branches: Vec::new(),
            public_reply_evidence: None,
            pending_data_point: None,
        }
    }

    fn flush_pending(&mut self) {
        let Some(data_point) = self.pending_data_point.take() else {
            return;
        };
        let game_folder = self.output_folder.join(&data_point.game_id);
        let file_path = game_folder.join(format!("ply_{:04}.json", data_point.ply));
        match serde_json::to_string_pretty(&data_point) {
            Ok(json) => {
                if let Err(error) = fs::write(&file_path, json) {
                    warn!("Failed to write ply file {:?}: {}", file_path, error);
                }
            }
            Err(error) => warn!(
                "Failed to serialize data point for ply {}: {}",
                data_point.ply, error
            ),
        }
    }
}

impl SimulationEventHandler for DataExporter {
    fn wants_public_reply_evidence(&self) -> bool { true }

    fn on_public_reply_evidence(
        &mut self,
        game_id: Uuid,
        evidence: Option<&crate::public_reply_evidence::PublicReplyEvidence>,
    ) {
        if self.current_game_id != Some(game_id) {
            warn!("Ignoring public reply evidence for unexpected game {game_id}");
            return;
        }
        self.public_reply_evidence = evidence.cloned();
    }

    fn on_decision_information(
        &mut self,
        _: Uuid,
        model: &str,
        unpriced: &[crate::observation::UnpricedBranch],
    ) {
        self.information_model = Some(model.into());
        self.unpriced_branches = unpriced.to_vec();
    }

    fn on_game_randomness(&mut self, _: Uuid, randomness: &GameRandomness) {
        self.randomness = Some(randomness.clone());
    }

    fn on_decision_randomness(&mut self, _: Uuid, randomness: Option<&DecisionRandomness>) {
        self.decision_randomness = randomness.cloned();
    }

    fn on_game_start(&mut self, game_id: Uuid) {
        self.flush_pending();
        self.current_game_id = Some(game_id);
        self.public_reply_evidence = None;
        self.ply_counter = 0;

        // Create folder for this game
        let game_folder = self.output_folder.join(game_id.to_string());
        if let Err(e) = fs::create_dir_all(&game_folder) {
            warn!("Failed to create game folder {:?}: {}", game_folder, e);
        }
    }

    fn on_action(
        &mut self,
        game_id: Uuid,
        state_before_action: &State,
        actor: usize,
        playable_actions: &[Action],
        action: &Action,
    ) {
        self.flush_pending();

        // Create data point
        let data_point = ExportedDataPoint {
            game_id: game_id.to_string(),
            ply: self.ply_counter,
            actor,
            state: state_before_action.clone(),
            playable_actions: playable_actions.to_vec(),
            chosen_action: action.clone(),
            randomness: self.randomness.clone(),
            decision_randomness: self.decision_randomness.take(),
            information_model: self.information_model.clone(),
            unpriced_branches: std::mem::take(&mut self.unpriced_branches),
            public_reply_evidence: self.public_reply_evidence.take(),
            private_reveals: Vec::new(),
            public_reveals: Vec::new(),
            luxury_coin_resolutions: Vec::new(),
        };

        self.pending_data_point = Some(data_point);
        self.ply_counter += 1;
    }

    fn on_private_reveals(&mut self, game_id: Uuid, reveals: &[PrivateRevealRecord]) {
        if reveals.is_empty() {
            return;
        }
        if self.current_game_id != Some(game_id) {
            warn!("Ignoring private reveals for unexpected game {game_id}");
            return;
        }
        let Some(data_point) = self.pending_data_point.as_mut() else {
            warn!("Ignoring private reveals without a pending exported ply");
            return;
        };
        data_point.private_reveals.extend_from_slice(reveals);
    }

    fn on_public_reveals(&mut self, game_id: Uuid, reveals: &[PublicRevealRecord]) {
        if reveals.is_empty() {
            return;
        }
        if self.current_game_id != Some(game_id) {
            warn!("Ignoring public reveals for unexpected game {game_id}");
            return;
        }
        let Some(data_point) = self.pending_data_point.as_mut() else {
            warn!("Ignoring public reveals without a pending exported ply");
            return;
        };
        data_point.public_reveals.extend_from_slice(reveals);
    }

    fn on_luxury_coin_resolutions(
        &mut self,
        game_id: Uuid,
        records: &[LuxuryCoinResolutionRecord],
    ) {
        if records.is_empty() {
            return;
        }
        if self.current_game_id != Some(game_id) {
            warn!("Ignoring Luxury Coin records for unexpected game {game_id}");
            return;
        }
        let Some(data_point) = self.pending_data_point.as_mut() else {
            warn!("Ignoring Luxury Coin records without a pending exported ply");
            return;
        };
        data_point
            .luxury_coin_resolutions
            .extend_from_slice(records);
    }

    fn on_action_resolved(&mut self, game_id: Uuid) {
        if self.current_game_id == Some(game_id) {
            self.flush_pending();
        }
    }

    fn on_game_end(&mut self, _game_id: Uuid, _state: State, _result: Option<GameOutcome>) {
        self.flush_pending();
        // Reset for next game
        self.ply_counter = 0;
        self.current_game_id = None;
        self.public_reply_evidence = None;
        self.randomness = None;
        self.decision_randomness = None;
        self.pending_data_point = None;
    }

    fn on_simulation_end(&mut self) {
        self.flush_pending();
        warn!(
            "Data export complete. Data written to: {:?}",
            self.output_folder
        );
    }

    fn merge(&mut self, _other: &dyn SimulationEventHandler) {
        // DataExporter doesn't need to merge data since each thread
        // writes to separate game folders. No aggregation needed.
    }
}

#[cfg(test)]
mod private_reveal_export_tests {
    use super::*;
    use crate::{actions::SimpleAction, card_ids::CardId, database::get_card_by_enum};

    #[test]
    fn reveal_export_fields_round_trip_and_default_for_old_traces() {
        let game_id = Uuid::new_v4();
        let output = std::env::temp_dir().join(format!("deckgym-private-reveal-{game_id}"));
        let mut exporter = DataExporter::new(output.clone());
        exporter.on_game_start(game_id);
        let action = Action {
            actor: 0,
            action: SimpleAction::Noop,
            is_stack: false,
        };
        exporter.on_action(game_id, &State::default(), 0, &[action.clone()], &action);
        let record = PrivateRevealRecord {
            viewer: 0,
            zone_owner: 1,
            cause: "Spy Ops".into(),
            scope: "random_hand_card".into(),
            cards: vec![get_card_by_enum(CardId::PA001Potion)],
        };
        exporter.on_private_reveals(game_id, &[record.clone()]);
        let public_record = PublicRevealRecord {
            zone_owner: 0,
            cause: "Rocket Frenzy".into(),
            scope: "deck_prefix_then_shuffle".into(),
            cards: vec![get_card_by_enum(CardId::PB088TeamRocketsScyther)],
        };
        exporter.on_public_reveals(game_id, &[public_record.clone()]);
        let pending_path = output.join(game_id.to_string()).join("ply_0000.json");
        assert!(
            !pending_path.exists(),
            "do not publish a ply before its results are complete"
        );
        exporter.on_action_resolved(game_id);
        assert!(
            pending_path.exists(),
            "a completed action must be available immediately"
        );
        exporter.on_game_end(game_id, State::default(), None);

        let path = output.join(game_id.to_string()).join("ply_0000.json");
        let json = fs::read_to_string(&path).unwrap();
        let exported: ExportedDataPoint = serde_json::from_str(&json).unwrap();
        assert_eq!(exported.private_reveals, vec![record]);
        assert_eq!(exported.public_reveals, vec![public_record]);

        let mut cause_legacy: serde_json::Value = serde_json::from_str(&json).unwrap();
        cause_legacy["public_reveals"][0]
            .as_object_mut()
            .unwrap()
            .remove("cause");
        let cause_legacy: ExportedDataPoint = serde_json::from_value(cause_legacy).unwrap();
        assert_eq!(cause_legacy.public_reveals[0].cause, "");

        let mut old: serde_json::Value = serde_json::from_str(&json).unwrap();
        old.as_object_mut().unwrap().remove("private_reveals");
        old.as_object_mut().unwrap().remove("public_reveals");
        let old: ExportedDataPoint = serde_json::from_value(old).unwrap();
        assert!(old.private_reveals.is_empty());
        assert!(old.public_reveals.is_empty());
    }
}
