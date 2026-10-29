//! The card-support preflight: before a program plays any game, every card of the decks it was
//! given is looked up in `card_validation`. A card the engine cannot play (CardNotFound or a
//! Missing* status) blocks the run; a RulesUnverified card is allowed, and its known limitations
//! are printed. `deckgym simulate` and `deckgym optimize` (src/cli_preflight.rs), the goldfish
//! example and the slow report's program (rl/strength) all refuse through this one report, so
//! there is one list of what blocks a run. It reads only the card database: no RNG, and nothing a
//! game depends on.

use crate::{
    card_ids::CardId,
    card_validation::{
        get_implementation_status, implementation_limitations, ImplementationStatus,
    },
    database::get_card_by_enum,
    Deck,
};
use std::collections::{BTreeMap, BTreeSet};

/// The opt-out of the programs that refuse through `refuse_unsupported_cards` (goldfish, and
/// `strength run` / `strength selfcheck` in rl/strength). `deckgym simulate` and `deckgym
/// optimize` have none.
pub const ALLOW_UNSUPPORTED_CARDS_FLAG: &str = "--allow-unsupported-cards";

#[derive(Debug)]
struct Finding {
    id: String,
    name: String,
    reason: &'static str,
    limitations: &'static [&'static str],
    sources: BTreeSet<String>,
}

/// What the preflight found, by card id, with the decks (sources) that hold each card.
#[derive(Default)]
pub struct SupportReport {
    blocking: BTreeMap<String, Finding>,
    experimental: BTreeMap<String, Finding>,
    /// Problems with the inputs themselves (a deck file that does not parse, a deck of the wrong
    /// size). The card lookup adds none; `deckgym simulate` and `optimize` add theirs, and they
    /// are refused in the same message.
    pub invalid_inputs: Vec<String>,
}

impl SupportReport {
    pub fn inspect_deck(&mut self, source: String, deck: &Deck) {
        for card in &deck.cards {
            let id = card.get_id();
            let Some(card_id) = CardId::from_card_id(&id) else {
                Self::record(
                    &mut self.blocking,
                    id,
                    card.get_name(),
                    ImplementationStatus::CardNotFound.description(),
                    &[],
                    &source,
                );
                continue;
            };
            self.inspect_card_id(source.as_str(), card_id);
        }
    }

    pub fn inspect_card_id(&mut self, source: &str, card_id: CardId) {
        let card = get_card_by_enum(card_id);
        let status = get_implementation_status(card_id);
        match status {
            ImplementationStatus::Complete => {}
            ImplementationStatus::RulesUnverified => Self::record(
                &mut self.experimental,
                card.get_id(),
                card.get_name(),
                status.description(),
                implementation_limitations(card_id),
                source,
            ),
            ImplementationStatus::CardNotFound
            | ImplementationStatus::MissingAttack
            | ImplementationStatus::MissingAbility
            | ImplementationStatus::MissingTrainer
            | ImplementationStatus::MissingTool => Self::record(
                &mut self.blocking,
                card.get_id(),
                card.get_name(),
                status.description(),
                &[],
                source,
            ),
        }
    }

    fn record(
        findings: &mut BTreeMap<String, Finding>,
        id: String,
        name: String,
        reason: &'static str,
        limitations: &'static [&'static str],
        source: &str,
    ) {
        findings
            .entry(id.clone())
            .or_insert_with(|| Finding {
                id,
                name,
                reason,
                limitations,
                sources: BTreeSet::new(),
            })
            .sources
            .insert(source.to_string());
    }

    /// Refuses (Err, the whole message) when an input is invalid or a card is unsupported;
    /// otherwise prints the experimental cards and their limitations to stderr and allows the run.
    pub fn enforce(self, operation: &str) -> Result<(), String> {
        if !self.invalid_inputs.is_empty() || !self.blocking.is_empty() {
            let mut message = format!("Card-support preflight failed; {operation} did not start.");
            if !self.invalid_inputs.is_empty() {
                message.push_str("\nInvalid deck inputs:");
                for invalid in &self.invalid_inputs {
                    message.push_str(&format!("\n  - {invalid}"));
                }
            }
            if !self.blocking.is_empty() {
                message.push_str("\nUnsupported cards:");
            }
            for finding in self.blocking.values() {
                message.push_str(&format!(
                    "\n  - {} — {} — {}\n    Used by: {}",
                    finding.id,
                    finding.name,
                    finding.reason,
                    join_sources(&finding.sources)
                ));
            }
            return Err(message);
        }

        if !self.experimental.is_empty() {
            eprintln!(
                "Card-support preflight: allowing experimental cards with known limitations:"
            );
            for finding in self.experimental.values() {
                eprintln!("  - {} — {}", finding.id, finding.name);
                eprintln!("    Used by: {}", join_sources(&finding.sources));
                for limitation in finding.limitations {
                    eprintln!("    Limitation: {limitation}");
                }
            }
        }
        Ok(())
    }

    /// `enforce`, except that with `allow_unsupported_cards` the unsupported cards are listed on
    /// stderr (id, name, reason, the decks that hold them) and the run is allowed, so it never
    /// runs silently on them. Invalid inputs still refuse.
    pub fn enforce_unless_allowed(
        self,
        operation: &str,
        allow_unsupported_cards: bool,
    ) -> Result<(), String> {
        if !allow_unsupported_cards || !self.invalid_inputs.is_empty() || self.blocking.is_empty() {
            return self.enforce(operation);
        }
        eprintln!(
            "Card-support preflight: {ALLOW_UNSUPPORTED_CARDS_FLAG} was given, so {operation} starts with unsupported cards; a game that reaches one can panic or play it wrongly:"
        );
        for finding in self.blocking.values() {
            eprintln!("  - {} — {} — {}", finding.id, finding.name, finding.reason);
            eprintln!("    Used by: {}", join_sources(&finding.sources));
        }
        Self {
            blocking: BTreeMap::new(),
            ..self
        }
        .enforce(operation)
    }
}

fn join_sources(sources: &BTreeSet<String>) -> String {
    sources.iter().cloned().collect::<Vec<_>>().join(", ")
}

/// The refusal of the programs that take decks without the CLI's own input checks (the goldfish
/// example and rl/strength): each deck is inspected under its label, and a deck holding a
/// CardNotFound or Missing* card refuses the run, in `enforce`'s words plus how to opt out, unless
/// `allow_unsupported_cards`. The caller prints the Err and exits with code 2, as `deckgym
/// simulate` does.
pub fn refuse_unsupported_cards<'a>(
    operation: &str,
    decks: impl IntoIterator<Item = (String, &'a Deck)>,
    allow_unsupported_cards: bool,
) -> Result<(), String> {
    let mut report = SupportReport::default();
    for (source, deck) in decks {
        report.inspect_deck(source, deck);
    }
    report
        .enforce_unless_allowed(operation, allow_unsupported_cards)
        .map_err(|message| {
            format!(
                "{message}\n{ALLOW_UNSUPPORTED_CARDS_FLAG} starts it anyway, after listing these cards on stderr."
            )
        })
}
