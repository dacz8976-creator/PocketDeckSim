//! Optional, bounded evidence for public-reply certificates used during one decision.
//!
//! These records describe certificate occurrences inside search. They are not full states,
//! authenticated proofs, complete replays, or claims about the selected root outcome.

use std::cell::RefCell;

use serde::{Deserialize, Serialize};

use crate::{
    actions::Action,
    observation::current_root_action,
    state::{PlayedCard, State},
};

pub const PUBLIC_REPLY_EVIDENCE_SCHEMA: &str = "pdl-public-reply-evidence/v1";
const MAX_DISTINCT_RECORDS: usize = 128;

fn default_schema() -> String {
    PUBLIC_REPLY_EVIDENCE_SCHEMA.to_owned()
}

fn default_occurrences() -> usize {
    1
}

/// Evidence collected for one decision scope.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct PublicReplyEvidence {
    #[serde(default = "default_schema")]
    pub schema: String,
    #[serde(default)]
    pub records: Vec<PublicReplyRecord>,
    #[serde(default)]
    pub total_occurrences: usize,
    #[serde(default)]
    pub dropped_occurrences: usize,
}

impl Default for PublicReplyEvidence {
    fn default() -> Self {
        Self {
            schema: default_schema(),
            records: Vec::new(),
            total_occurrences: 0,
            dropped_occurrences: 0,
        }
    }
}

/// One distinct certificate occurrence, aggregated within the collection scope.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct PublicReplyRecord {
    #[serde(default)]
    pub root_action: Option<Action>,
    #[serde(default)]
    pub selected: bool,
    pub observer: usize,
    pub witness_action: Action,
    pub positive_branches: usize,
    pub probability_sum: f64,
    #[serde(with = "leaf_value_serde")]
    pub applied_leaf_value: f64,
    pub context: PublicReplyContext,
    #[serde(default = "default_occurrences")]
    pub occurrences: usize,
}

mod leaf_value_serde {
    use std::fmt;

    use serde::{de, Deserializer, Serializer};

    pub fn serialize<S>(value: &f64, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        if value.is_nan() {
            serializer.serialize_str("NaN")
        } else if *value == f64::INFINITY {
            serializer.serialize_str("+Infinity")
        } else if *value == f64::NEG_INFINITY {
            serializer.serialize_str("-Infinity")
        } else {
            serializer.serialize_f64(*value)
        }
    }

    pub fn deserialize<'de, D>(deserializer: D) -> Result<f64, D::Error>
    where
        D: Deserializer<'de>,
    {
        struct LeafValueVisitor;

        impl<'de> de::Visitor<'de> for LeafValueVisitor {
            type Value = f64;

            fn expecting(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
                formatter.write_str("a finite number or NaN, +Infinity, or -Infinity")
            }

            fn visit_f64<E>(self, value: f64) -> Result<Self::Value, E>
            where
                E: de::Error,
            {
                if value.is_finite() {
                    Ok(value)
                } else {
                    Err(E::custom("nonfinite numeric leaf utility must use its string spelling"))
                }
            }

            fn visit_i64<E>(self, value: i64) -> Result<Self::Value, E>
            where
                E: de::Error,
            {
                Ok(value as f64)
            }

            fn visit_u64<E>(self, value: u64) -> Result<Self::Value, E>
            where
                E: de::Error,
            {
                Ok(value as f64)
            }

            fn visit_str<E>(self, value: &str) -> Result<Self::Value, E>
            where
                E: de::Error,
            {
                match value {
                    "NaN" => Ok(f64::NAN),
                    "+Infinity" => Ok(f64::INFINITY),
                    "-Infinity" => Ok(f64::NEG_INFINITY),
                    _ => Err(E::unknown_variant(
                        value,
                        &["NaN", "+Infinity", "-Infinity"],
                    )),
                }
            }
        }

        deserializer.deserialize_any(LeafValueVisitor)
    }
}

/// Public-board context immediately before the successful certificate assessment.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct PublicReplyContext {
    pub turn_count: u8,
    pub current_player: usize,
    pub points: [u8; 2],
    pub in_play_pokemon: [[Option<PlayedCard>; 4]; 2],
}

impl PublicReplyContext {
    fn from_state(state: &State) -> Self {
        Self {
            turn_count: state.turn_count,
            current_player: state.current_player,
            points: state.points,
            in_play_pokemon: state.in_play_pokemon.clone(),
        }
    }
}

thread_local! {
    // None is an explicitly disabled nested scope. Recording always targets only the last frame,
    // so enabled inner scopes capture their own evidence and disabled inner scopes mask an outer
    // collector.
    static COLLECTORS: RefCell<Vec<Option<PublicReplyEvidence>>> = const { RefCell::new(Vec::new()) };
}

struct CollectorScope {
    active: bool,
}

impl CollectorScope {
    fn push(enabled: bool) -> Self {
        COLLECTORS.with(|collectors| {
            collectors
                .borrow_mut()
                .push(enabled.then(PublicReplyEvidence::default));
        });
        Self { active: true }
    }

    fn finish(mut self) -> Option<PublicReplyEvidence> {
        let evidence = COLLECTORS.with(|collectors| {
            collectors
                .borrow_mut()
                .pop()
                .expect("public-reply collector scope must be balanced")
        });
        self.active = false;
        evidence
    }
}

impl Drop for CollectorScope {
    fn drop(&mut self) {
        if self.active {
            COLLECTORS.with(|collectors| {
                collectors.borrow_mut().pop();
            });
        }
    }
}

/// Run `f` with an optional collector. The returned evidence belongs only to this innermost
/// scope. A disabled nested scope deliberately masks any enabled outer scope.
pub fn collect_public_reply_evidence<T>(
    enabled: bool,
    f: impl FnOnce() -> T,
) -> (T, Option<PublicReplyEvidence>) {
    if !enabled && COLLECTORS.with(|collectors| collectors.borrow().is_empty()) {
        return (f(), None);
    }
    let scope = CollectorScope::push(enabled);
    let value = f();
    let evidence = scope.finish();
    (value, evidence)
}

/// Record one trusted successful public-reply certificate.
///
/// The certificate verifier is the authority for calling this function. Keeping it crate-private
/// prevents external callers from presenting arbitrary state as certified evidence.
pub(crate) fn record_public_reply(
    state: &State,
    observer: usize,
    witness_action: &Action,
    positive_branches: usize,
    probability_sum: f64,
    applied_leaf_value: f64,
) {
    COLLECTORS.with(|collectors| {
        let mut collectors = collectors.borrow_mut();
        let Some(Some(evidence)) = collectors.last_mut() else {
            return;
        };
        let Some(root_action) = current_root_action() else {
            return;
        };

        // Everything below this gate may clone public board state. Disabled collection therefore
        // has no board-cloning cost and cannot expose context through a dormant outer collector.
        let record = PublicReplyRecord {
            root_action: Some(root_action),
            selected: false,
            observer,
            witness_action: witness_action.clone(),
            positive_branches,
            probability_sum,
            applied_leaf_value,
            context: PublicReplyContext::from_state(state),
            occurrences: 1,
        };

        add_record(evidence, record);
    });
}

fn add_record(evidence: &mut PublicReplyEvidence, record: PublicReplyRecord) {
    evidence.total_occurrences = evidence.total_occurrences.saturating_add(1);
    if let Some(existing) = evidence
        .records
        .iter_mut()
        .find(|existing| records_match(existing, &record))
    {
        existing.occurrences = existing.occurrences.saturating_add(1);
    } else if evidence.records.len() < MAX_DISTINCT_RECORDS {
        evidence.records.push(record);
    } else {
        evidence.dropped_occurrences = evidence.dropped_occurrences.saturating_add(1);
    }
}

fn records_match(left: &PublicReplyRecord, right: &PublicReplyRecord) -> bool {
    left.root_action == right.root_action
        && left.observer == right.observer
        && left.witness_action == right.witness_action
        && left.positive_branches == right.positive_branches
        && left.probability_sum.to_bits() == right.probability_sum.to_bits()
        && left.applied_leaf_value.to_bits() == right.applied_leaf_value.to_bits()
        && left.context == right.context
}

/// Mark every record attributed to `selected` and clear prior selection marks.
pub fn mark_selected(evidence: &mut PublicReplyEvidence, selected: &Action) {
    for record in &mut evidence.records {
        record.selected = record.root_action.as_ref() == Some(selected);
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{
        actions::SimpleAction,
        observation::with_root_action,
    };

    fn action(actor: usize, action: SimpleAction) -> Action {
        Action {
            actor,
            action,
            is_stack: false,
        }
    }

    fn witness() -> Action {
        action(1, SimpleAction::EndTurn)
    }

    fn record_unchecked(state: &State, value: f64) {
        record_public_reply(state, 0, &witness(), 1, 1.0, value);
    }

    fn record(state: &State, value: f64) {
        with_root_action(&action(0, SimpleAction::EndTurn), || {
            record_unchecked(state, value)
        });
    }

    fn sample_record(value: f64) -> PublicReplyRecord {
        PublicReplyRecord {
            root_action: None,
            selected: false,
            observer: 0,
            witness_action: witness(),
            positive_branches: 1,
            probability_sum: 1.0,
            applied_leaf_value: value,
            context: PublicReplyContext::from_state(&State::default()),
            occurrences: 1,
        }
    }

    #[test]
    fn innermost_scope_captures_and_disabled_scope_masks_outer() {
        let state = State::default();
        let (value, evidence) = collect_public_reply_evidence(false, || 17);
        assert_eq!(value, 17);
        assert!(evidence.is_none());

        let ((), outer) = collect_public_reply_evidence(true, || {
            record(&state, 5.0);
            let ((), inner) = collect_public_reply_evidence(true, || record(&state, 7.0));
            assert_eq!(inner.unwrap().records[0].applied_leaf_value, 7.0);
            let ((), disabled) = collect_public_reply_evidence(false, || record(&state, 9.0));
            assert!(disabled.is_none());
            record(&state, 5.0);
        });
        let outer = outer.unwrap();
        assert_eq!(outer.total_occurrences, 2);
        assert_eq!(outer.records.len(), 1);
        assert_eq!(outer.records[0].occurrences, 2);
        assert_eq!(outer.records[0].applied_leaf_value, 5.0);
    }

    #[test]
    fn panic_cleans_up_scope() {
        let result = std::panic::catch_unwind(|| {
            collect_public_reply_evidence(true, || panic!("intentional collector panic"));
        });
        assert!(result.is_err());

        record(&State::default(), 3.0);
        let ((), evidence) = collect_public_reply_evidence(true, || {
            record(&State::default(), 4.0)
        });
        assert_eq!(evidence.unwrap().total_occurrences, 1);
    }

    #[test]
    fn unscoped_occurrence_is_not_exported() {
        let ((), evidence) = collect_public_reply_evidence(true, || {
            record_unchecked(&State::default(), 4.0)
        });
        let evidence = evidence.unwrap();
        assert_eq!(evidence.total_occurrences, 0);
        assert!(evidence.records.is_empty());
    }

    #[test]
    fn collectors_are_thread_local() {
        let state = State::default();
        let ((), main_evidence) = collect_public_reply_evidence(true, || {
            let thread = std::thread::spawn(|| {
                collect_public_reply_evidence(true, || record(&State::default(), 12.0)).1
            });
            record(&state, 11.0);
            let thread_evidence = thread.join().unwrap().unwrap();
            assert_eq!(thread_evidence.records[0].applied_leaf_value, 12.0);
        });
        let main_evidence = main_evidence.unwrap();
        assert_eq!(main_evidence.total_occurrences, 1);
        assert_eq!(main_evidence.records[0].applied_leaf_value, 11.0);
    }

    #[test]
    fn cap_drops_only_new_records_and_still_counts_repeats() {
        let state = State::default();
        let ((), evidence) = collect_public_reply_evidence(true, || {
            for value in 0..=MAX_DISTINCT_RECORDS {
                record(&state, value as f64);
            }
            record(&state, 0.0);
        });
        let evidence = evidence.unwrap();
        assert_eq!(evidence.records.len(), MAX_DISTINCT_RECORDS);
        assert_eq!(evidence.total_occurrences, MAX_DISTINCT_RECORDS + 2);
        assert_eq!(evidence.dropped_occurrences, 1);
        assert_eq!(evidence.records[0].occurrences, 2);
    }

    #[test]
    fn occurrence_counters_saturate_without_wrapping_or_panicking() {
        let mut repeated = PublicReplyEvidence {
            total_occurrences: usize::MAX,
            records: vec![PublicReplyRecord {
                occurrences: usize::MAX,
                ..sample_record(1.0)
            }],
            ..PublicReplyEvidence::default()
        };
        add_record(&mut repeated, sample_record(1.0));
        assert_eq!(repeated.total_occurrences, usize::MAX);
        assert_eq!(repeated.records[0].occurrences, usize::MAX);

        let mut full = PublicReplyEvidence {
            total_occurrences: usize::MAX,
            dropped_occurrences: usize::MAX,
            records: vec![sample_record(2.0); MAX_DISTINCT_RECORDS],
            ..PublicReplyEvidence::default()
        };
        add_record(&mut full, sample_record(3.0));
        assert_eq!(full.total_occurrences, usize::MAX);
        assert_eq!(full.dropped_occurrences, usize::MAX);
        assert_eq!(full.records.len(), MAX_DISTINCT_RECORDS);
    }

    #[test]
    fn leaf_values_round_trip_as_numbers_or_fixed_nonfinite_strings() {
        for (value, expected_json) in [
            (42.5, serde_json::json!(42.5)),
            (f64::NAN, serde_json::json!("NaN")),
            (f64::INFINITY, serde_json::json!("+Infinity")),
            (f64::NEG_INFINITY, serde_json::json!("-Infinity")),
        ] {
            let record = sample_record(value);
            let encoded = serde_json::to_value(&record).unwrap();
            assert_eq!(encoded["applied_leaf_value"], expected_json);
            let decoded: PublicReplyRecord = serde_json::from_value(encoded).unwrap();
            if value.is_nan() {
                assert!(decoded.applied_leaf_value.is_nan());
            } else {
                assert_eq!(decoded.applied_leaf_value, value);
            }
        }

        let invalid = serde_json::to_value(sample_record(1.0)).unwrap();
        let mut invalid = invalid.as_object().unwrap().clone();
        invalid.insert("applied_leaf_value".into(), serde_json::json!("Infinity"));
        assert!(serde_json::from_value::<PublicReplyRecord>(serde_json::Value::Object(invalid))
            .is_err());
    }

    #[test]
    fn root_actions_aggregate_separately_and_selection_is_replaceable() {
        let state = State::default();
        let root_a = action(0, SimpleAction::EndTurn);
        let root_b = action(0, SimpleAction::Noop);
        let ((), evidence) = collect_public_reply_evidence(true, || {
            with_root_action(&root_a, || {
                record_unchecked(&state, 20.0);
                record_unchecked(&state, 20.0);
            });
            with_root_action(&root_b, || record_unchecked(&state, 20.0));
        });
        let mut evidence = evidence.unwrap();
        assert_eq!(evidence.records.len(), 2);
        assert_eq!(evidence.total_occurrences, 3);

        mark_selected(&mut evidence, &root_b);
        assert!(evidence
            .records
            .iter()
            .any(|record| record.root_action.as_ref() == Some(&root_b) && record.selected));
        assert!(!evidence
            .records
            .iter()
            .any(|record| record.root_action.as_ref() == Some(&root_a) && record.selected));

        mark_selected(&mut evidence, &root_a);
        assert!(evidence
            .records
            .iter()
            .filter(|record| record.selected)
            .all(|record| record.root_action.as_ref() == Some(&root_a)));
    }
}
