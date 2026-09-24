use deckgym::{
    card_ids::CardId,
    card_validation::{
        get_implementation_status, implementation_limitations, ImplementationStatus,
    },
    database::get_card_by_enum,
    Deck,
};
use std::{
    collections::{BTreeMap, BTreeSet},
    fs,
    path::Path,
};

#[derive(Debug)]
struct Finding {
    id: String,
    name: String,
    reason: &'static str,
    limitations: &'static [&'static str],
    sources: BTreeSet<String>,
}

#[derive(Default)]
struct SupportReport {
    blocking: BTreeMap<String, Finding>,
    experimental: BTreeMap<String, Finding>,
    invalid_inputs: Vec<String>,
}

impl SupportReport {
    fn inspect_deck(&mut self, source: String, deck: &Deck) {
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

    fn inspect_card_id(&mut self, source: &str, card_id: CardId) {
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

    fn enforce(self, operation: &str) -> Result<(), String> {
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
}

fn join_sources(sources: &BTreeSet<String>) -> String {
    sources.iter().cloned().collect::<Vec<_>>().join(", ")
}

fn load_deck(path: &str, label: &str) -> Result<Deck, String> {
    let contents = fs::read_to_string(path)
        .map_err(|error| format!("Card-support preflight could not read {label}: {error}"))?;
    validate_energy_lines(&contents, label)?;
    Deck::from_string(&contents)
        .map_err(|error| format!("Card-support preflight could not parse {label}: {error}"))
}

fn regular_files(folder: &str) -> Result<Vec<String>, String> {
    let entries = fs::read_dir(folder).map_err(|error| {
        format!("Card-support preflight could not read folder {folder}: {error}")
    })?;
    let mut paths = Vec::new();
    for entry in entries {
        let entry = entry.map_err(|error| {
            format!("Card-support preflight could not read an entry in folder {folder}: {error}")
        })?;
        let file_type = entry.file_type().map_err(|error| {
            format!(
                "Card-support preflight could not inspect folder entry {}: {error}",
                entry.path().display()
            )
        })?;
        let path = entry.path();
        if file_type.is_file() {
            paths.push(path.to_string_lossy().into_owned());
        }
    }
    paths.sort();
    Ok(paths)
}

fn inspect_simulated_folder_decks(report: &mut SupportReport, folder: &str) -> Result<(), String> {
    let paths = regular_files(folder)?;
    if paths.is_empty() {
        report
            .invalid_inputs
            .push(format!("opponent folder ({folder}) contains no deck files"));
        return Ok(());
    }

    for path in paths {
        let label = format!("opponent deck ({path})");
        match load_deck(&path, &label) {
            Ok(deck) => {
                if let Some(problem) = full_deck_problem(&deck) {
                    report.invalid_inputs.push(format!("{label}: {problem}"));
                }
                report.inspect_deck(label, &deck);
            }
            Err(error) => report.invalid_inputs.push(error),
        }
    }
    Ok(())
}

fn validate_energy_lines(contents: &str, label: &str) -> Result<(), String> {
    const ENERGY_TYPES: &[&str] = &[
        "Grass",
        "Fire",
        "Water",
        "Lightning",
        "Psychic",
        "Fighting",
        "Darkness",
        "Metal",
        "Dragon",
        "Colorless",
    ];

    for (index, line) in contents.lines().enumerate() {
        let Some(energy_list) = line.trim().strip_prefix("Energy:") else {
            continue;
        };
        for energy in energy_list.split(',').map(str::trim) {
            if !energy.is_empty() && !ENERGY_TYPES.contains(&energy) {
                return Err(format!(
                    "Card-support preflight could not parse {label}: invalid energy type '{energy}' on line {}",
                    index + 1
                ));
            }
        }
    }
    Ok(())
}

fn full_deck_problem(deck: &Deck) -> Option<String> {
    if deck.is_valid() {
        return None;
    }
    if deck.cards.len() != 20 {
        return Some(format!(
            "expected exactly 20 cards, found {}",
            deck.cards.len()
        ));
    }
    if !deck.cards.iter().any(|card| card.is_basic()) {
        return Some("must contain at least one Basic Pokémon".to_string());
    }
    duplicate_limit_problem(deck).or_else(|| Some("failed full-deck validation".to_string()))
}

fn duplicate_limit_problem(deck: &Deck) -> Option<String> {
    let mut counts = BTreeMap::new();
    for card in &deck.cards {
        let name = card.get_name();
        let count = counts.entry(name.clone()).or_insert(0usize);
        *count += 1;
        if *count > 2 {
            return Some(format!(
                "contains more than two copies of {name} (found {count})"
            ));
        }
    }
    None
}

pub(crate) fn simulation(deck_a_path: &str, deck_b_or_folder: &str) -> Result<(), String> {
    let mut report = SupportReport::default();
    let deck_a = load_deck(deck_a_path, "deck A")?;
    if let Some(problem) = full_deck_problem(&deck_a) {
        report
            .invalid_inputs
            .push(format!("deck A ({deck_a_path}): {problem}"));
    }
    report.inspect_deck(format!("deck A ({deck_a_path})"), &deck_a);

    if Path::new(deck_b_or_folder).is_dir() {
        inspect_simulated_folder_decks(&mut report, deck_b_or_folder)?;
    } else {
        let deck_b = load_deck(deck_b_or_folder, "deck B")?;
        if let Some(problem) = full_deck_problem(&deck_b) {
            report
                .invalid_inputs
                .push(format!("deck B ({deck_b_or_folder}): {problem}"));
        }
        report.inspect_deck(format!("deck B ({deck_b_or_folder})"), &deck_b);
    }

    report.enforce("simulation")
}

fn parse_candidate_card_id(raw: &str) -> Result<CardId, String> {
    let raw = raw.trim();
    if !raw.is_ascii() {
        return Err(format!(
            "Invalid card ID '{raw}' in candidate cards: IDs must use ASCII characters"
        ));
    }
    let compact = raw.replace(' ', "");
    if compact.len() < 3 {
        return Err(format!("Invalid card ID '{raw}' in candidate cards"));
    }
    let (prefix, number) = if let Some(index) = raw.find(' ') {
        let (prefix, number) = raw.split_at(index);
        (prefix.trim(), number.trim())
    } else {
        let split = compact.len() - 3;
        (&compact[..split], &compact[split..])
    };
    let id = format!("{} {:0>3}", prefix, number);
    CardId::from_card_id(&id).ok_or_else(|| format!("Invalid card ID '{raw}' in candidate cards"))
}

pub(crate) fn optimization(
    incomplete_deck_path: &str,
    candidate_cards: &str,
    enemy_decks_folder: &str,
) -> Result<(), String> {
    let mut report = SupportReport::default();
    let incomplete = load_deck(incomplete_deck_path, "incomplete deck")?;
    let incomplete_label = format!("incomplete deck ({incomplete_deck_path})");
    if incomplete.cards.len() > 20 {
        report.invalid_inputs.push(format!(
            "{incomplete_label}: expected at most 20 cards, found {}",
            incomplete.cards.len()
        ));
    }
    if let Some(problem) = duplicate_limit_problem(&incomplete) {
        report
            .invalid_inputs
            .push(format!("{incomplete_label}: {problem}"));
    }
    report.inspect_deck(incomplete_label, &incomplete);

    for raw in candidate_cards.split(',') {
        let card_id = parse_candidate_card_id(raw)?;
        report.inspect_card_id("candidate card pool", card_id);
    }

    inspect_simulated_folder_decks(&mut report, enemy_decks_folder)?;
    report.enforce("optimization")
}
