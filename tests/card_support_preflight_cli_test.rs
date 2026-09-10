use std::{
    fs,
    path::{Path, PathBuf},
    process::{Command, Output},
    sync::atomic::{AtomicUsize, Ordering},
};

static NEXT_FIXTURE: AtomicUsize = AtomicUsize::new(0);

struct FixtureDir(PathBuf);

impl FixtureDir {
    fn new(label: &str) -> Self {
        let path = std::env::temp_dir().join(format!(
            "deckgym-card-support-preflight-{label}-{}-{}",
            std::process::id(),
            NEXT_FIXTURE.fetch_add(1, Ordering::Relaxed)
        ));
        fs::create_dir_all(&path).unwrap();
        Self(path)
    }

    fn path(&self) -> &Path {
        &self.0
    }

    fn write(&self, name: &str, contents: &str) -> PathBuf {
        let path = self.0.join(name);
        fs::write(&path, contents).unwrap();
        path
    }
}

impl Drop for FixtureDir {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.0);
    }
}

fn supported_deck() -> &'static str {
    include_str!("../example_decks/venusaur-exeggutor.txt")
}

fn deck_replacing_red_card(replacement: &str) -> String {
    let original = "1 Red Card P-A 006";
    assert!(supported_deck().contains(original));
    supported_deck().replacen(original, replacement, 1)
}

fn run(args: &[String]) -> Output {
    Command::new(env!("CARGO_BIN_EXE_deckgym"))
        .args(args)
        .output()
        .expect("deckgym CLI should launch")
}

fn simulate_args(deck_a: &Path, deck_b: &Path, output: &Path) -> Vec<String> {
    vec![
        "simulate".into(),
        deck_a.display().to_string(),
        deck_b.display().to_string(),
        "--num".into(),
        "0".into(),
        "--data-output".into(),
        output.display().to_string(),
    ]
}

fn nineteen_card_deck() -> String {
    supported_deck().replacen("1 Red Card P-A 006", "", 1)
}

fn malformed_energy_deck() -> String {
    supported_deck().replacen("Pokémon: 10", "Energy: Plasma\nPokémon: 10", 1)
}

fn optimize_args(incomplete: &Path, candidates: &str, opponents: &Path) -> Vec<String> {
    vec![
        "optimize".into(),
        incomplete.display().to_string(),
        candidates.into(),
        opponents.display().to_string(),
        "--num".into(),
        "0".into(),
    ]
}

#[test]
fn simulate_rejects_an_unknown_card_id_before_creating_data_output() {
    let fixture = FixtureDir::new("unknown-card");
    let deck_a = fixture.write("supported.txt", supported_deck());
    let deck_b = fixture.write(
        "invalid-id.txt",
        &deck_replacing_red_card("1 Imaginary Card B9 999"),
    );
    let data_output = fixture.path().join("must-not-exist");

    let output = run(&simulate_args(&deck_a, &deck_b, &data_output));
    let stderr = String::from_utf8_lossy(&output.stderr);
    assert_eq!(output.status.code(), Some(2), "{stderr}");
    assert!(stderr.contains("deck B"), "{stderr}");
    assert!(stderr.contains("B9 999"), "{stderr}");
    assert!(!data_output.exists());
}

#[test]
fn folder_simulation_rejects_an_unknown_card_instead_of_skipping_the_file() {
    let fixture = FixtureDir::new("folder");
    let deck_a = fixture.write("supported.txt", supported_deck());
    let opponents = fixture.path().join("opponents");
    fs::create_dir(&opponents).unwrap();
    fs::write(opponents.join("supported.txt"), supported_deck()).unwrap();
    fs::write(
        opponents.join("invalid-id.txt"),
        deck_replacing_red_card("1 Imaginary Card B9 999"),
    )
    .unwrap();
    let data_output = fixture.path().join("must-not-exist");

    let output = run(&simulate_args(&deck_a, &opponents, &data_output));
    let stderr = String::from_utf8_lossy(&output.stderr);
    assert_eq!(output.status.code(), Some(2), "{stderr}");
    assert!(stderr.contains("B9 999"), "{stderr}");
    assert!(stderr.contains("opponent deck"), "{stderr}");
    assert!(stderr.contains("invalid-id.txt"), "{stderr}");
    assert!(!data_output.exists());
}

#[test]
fn file_simulation_rejects_invalid_full_decks() {
    for (label, invalid_deck, expected) in [
        (
            "nineteen",
            nineteen_card_deck(),
            "exactly 20 cards, found 19",
        ),
        (
            "three-copies",
            deck_replacing_red_card("1 Bulbasaur A1 001"),
            "more than two copies of Bulbasaur",
        ),
    ] {
        let fixture = FixtureDir::new(&format!("invalid-pair-{label}"));
        let deck_a = fixture.write("supported.txt", supported_deck());
        let deck_b = fixture.write("invalid.txt", &invalid_deck);
        let data_output = fixture.path().join("must-not-exist");

        let output = run(&simulate_args(&deck_a, &deck_b, &data_output));
        let stderr = String::from_utf8_lossy(&output.stderr);
        assert_eq!(output.status.code(), Some(2), "{stderr}");
        assert!(stderr.contains("Invalid deck inputs"), "{stderr}");
        assert!(stderr.contains("deck B"), "{stderr}");
        assert!(stderr.contains(expected), "{stderr}");
        assert!(!data_output.exists());
    }
}

#[test]
fn both_folder_commands_reject_every_malformed_or_non_twenty_card_file() {
    for (command, invalid_name, invalid_contents, expected) in [
        (
            "simulate",
            "bad-energy.txt",
            malformed_energy_deck(),
            "invalid energy type 'Plasma'",
        ),
        (
            "simulate",
            "nineteen.txt",
            nineteen_card_deck(),
            "exactly 20 cards, found 19",
        ),
        (
            "optimize",
            "bad-energy.txt",
            malformed_energy_deck(),
            "invalid energy type 'Plasma'",
        ),
        (
            "optimize",
            "nineteen.txt",
            nineteen_card_deck(),
            "exactly 20 cards, found 19",
        ),
    ] {
        let fixture = FixtureDir::new(&format!("{command}-{invalid_name}"));
        let deck_a = fixture.write("deck-a.txt", supported_deck());
        let incomplete = fixture.write("incomplete.txt", &nineteen_card_deck());
        let opponents = fixture.path().join("opponents");
        fs::create_dir(&opponents).unwrap();
        fs::write(opponents.join(invalid_name), invalid_contents).unwrap();
        let data_output = fixture.path().join("must-not-exist");

        let args = if command == "simulate" {
            simulate_args(&deck_a, &opponents, &data_output)
        } else {
            optimize_args(&incomplete, "P-A 006", &opponents)
        };
        let output = run(&args);
        let stderr = String::from_utf8_lossy(&output.stderr);
        assert_eq!(output.status.code(), Some(2), "{stderr}");
        assert!(stderr.contains(invalid_name), "{stderr}");
        assert!(stderr.contains(expected), "{stderr}");
        assert!(!stderr.contains("panicked at"), "{stderr}");
        assert!(!data_output.exists());
    }
}

#[test]
fn both_folder_commands_reject_an_empty_opponent_folder() {
    for command in ["simulate", "optimize"] {
        let fixture = FixtureDir::new(&format!("empty-{command}"));
        let deck_a = fixture.write("deck-a.txt", supported_deck());
        let incomplete = fixture.write("incomplete.txt", &nineteen_card_deck());
        let opponents = fixture.path().join("empty-opponents");
        fs::create_dir(&opponents).unwrap();
        let data_output = fixture.path().join("must-not-exist");

        let args = if command == "simulate" {
            simulate_args(&deck_a, &opponents, &data_output)
        } else {
            optimize_args(&incomplete, "P-A 006", &opponents)
        };
        let output = run(&args);
        let stderr = String::from_utf8_lossy(&output.stderr);
        assert_eq!(output.status.code(), Some(2), "{stderr}");
        assert!(stderr.contains("contains no deck files"), "{stderr}");
        assert!(!data_output.exists());
    }
}

#[test]
fn optimize_rejects_an_unknown_candidate_before_running() {
    let fixture = FixtureDir::new("optimize-unknown-candidate");
    let incomplete = fixture.write("incomplete.txt", &nineteen_card_deck());
    let opponents = fixture.path().join("opponents");
    fs::create_dir(&opponents).unwrap();
    fs::write(opponents.join("supported.txt"), supported_deck()).unwrap();

    let output = run(&[
        "optimize".into(),
        incomplete.display().to_string(),
        "B9 999".into(),
        opponents.display().to_string(),
        "--num".into(),
        "0".into(),
    ]);
    let stderr = String::from_utf8_lossy(&output.stderr);
    assert_eq!(output.status.code(), Some(2), "{stderr}");
    assert!(stderr.contains("Invalid card ID 'B9 999'"), "{stderr}");
    assert!(!stderr.contains("panicked at"), "{stderr}");
}

#[test]
fn optimize_rejects_oversized_and_duplicate_incomplete_decks_before_running() {
    let cases = [
        (
            "oversized",
            format!("{}1 Potion P-A 001\n", supported_deck()),
            "at most 20 cards, found 21",
        ),
        (
            "duplicate",
            format!("{}1 Bulbasaur A1 001\n", nineteen_card_deck()),
            "more than two copies of Bulbasaur",
        ),
    ];

    for (label, incomplete_contents, expected) in cases {
        let fixture = FixtureDir::new(label);
        let incomplete = fixture.write("incomplete.txt", &incomplete_contents);
        let opponents = fixture.path().join("opponents");
        fs::create_dir(&opponents).unwrap();
        fs::write(opponents.join("supported.txt"), supported_deck()).unwrap();

        let output = run(&optimize_args(&incomplete, "P-A 006", &opponents));
        let stderr = String::from_utf8_lossy(&output.stderr);
        assert_eq!(output.status.code(), Some(2), "{stderr}");
        assert!(stderr.contains(expected), "{stderr}");
    }
}

#[test]
fn optimize_rejects_non_ascii_candidate_ids_without_panicking() {
    let fixture = FixtureDir::new("unicode-candidate");
    let incomplete = fixture.write("incomplete.txt", &nineteen_card_deck());
    let opponents = fixture.path().join("opponents");
    fs::create_dir(&opponents).unwrap();
    fs::write(opponents.join("supported.txt"), supported_deck()).unwrap();

    let output = run(&optimize_args(&incomplete, "B4a ０６９", &opponents));
    let stderr = String::from_utf8_lossy(&output.stderr);
    assert_eq!(output.status.code(), Some(2), "{stderr}");
    assert!(stderr.contains("IDs must use ASCII characters"), "{stderr}");
    assert!(!stderr.contains("panicked at"), "{stderr}");
}

#[test]
fn rules_unverified_cards_are_allowed_with_explicit_experimental_limitations() {
    let fixture = FixtureDir::new("experimental");
    let deck_a = fixture.write(
        "experimental.txt",
        &deck_replacing_red_card("1 Revavroom B4 115"),
    );
    let deck_b = fixture.write(
        "researcher.txt",
        &deck_replacing_red_card("1 Team Rocket's Researcher B4a 069"),
    );

    let output = run(&[
        "simulate".into(),
        deck_a.display().to_string(),
        deck_b.display().to_string(),
        "--num".into(),
        "1".into(),
        "--seed".into(),
        "17".into(),
        "--players".into(),
        "r,r".into(),
    ]);
    let stderr = String::from_utf8_lossy(&output.stderr);
    assert!(output.status.success(), "{stderr}");
    assert!(stderr.contains("allowing experimental cards"), "{stderr}");
    assert!(stderr.contains("B4 115"), "{stderr}");
    assert!(stderr.contains("Revavroom"), "{stderr}");
    assert!(stderr.contains("Owner-approved assumption"), "{stderr}");
    assert!(stderr.contains("B4a 069"), "{stderr}");
    assert!(stderr.contains("Team Rocket's Researcher"), "{stderr}");
    assert!(stderr.contains("not capped at a 10-card hand"), "{stderr}");
    assert!(!stderr.contains("preflight failed"), "{stderr}");
}
