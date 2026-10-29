// The card lookup and the refusal message are the library's (deckgym::card_support), shared with
// the goldfish example and rl/strength; this module adds the CLI's own input checks.
use deckgym::{card_ids::CardId, card_support::SupportReport, Deck};
use std::{collections::BTreeMap, fs, path::Path};

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
