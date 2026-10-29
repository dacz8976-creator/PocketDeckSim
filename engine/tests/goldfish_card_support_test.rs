//! The goldfish example (examples/goldfish.rs, the brew pages) refuses a list or panel deck that holds a
//! card the engine cannot play, through the card-support preflight of `deckgym simulate`
//! (deckgym::card_support), and with --allow-unsupported-cards lists the card and goes on.
//!
//! The card is C1 019 Volcanion, a Basic whose only attack, Dynamite Steam ("Flip 2 coins. This attack
//! does 110 damage for each heads."), has no entry in EFFECT_MECHANIC_MAP (the map has the 2-coin texts
//! for 20 to 100 damage, not 110), so card_status gives MissingAttack (release lane, d0792568). If it is
//! implemented one day, swap in another blocked printing.
//!
//! `cargo test` builds the examples before it runs the tests, so the program is the goldfish beside this
//! test's executable (target/<profile>/examples). Run alone, build it first:
//! `cargo build --release --example goldfish`.

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
            "deckgym-goldfish-card-support-{label}-{}-{}",
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

/// The supported deck with its Red Card replaced by C1 019 Volcanion (MissingAttack); still a legal
/// 20-card deck, so only the card-support check can refuse it.
fn deck_with_missing_attack_card() -> String {
    let original = "1 Red Card P-A 006";
    assert!(supported_deck().contains(original));
    supported_deck().replacen(original, "1 Volcanion C1 019", 1)
}

/// target/<profile>/deps/<this test> -> target/<profile>/examples/goldfish (or the newest hashed copy).
fn goldfish_program() -> PathBuf {
    let exe = std::env::current_exe().expect("test executable path");
    let examples = exe
        .parent()
        .and_then(Path::parent)
        .expect("target profile folder")
        .join("examples");
    let program = examples.join(format!("goldfish{}", std::env::consts::EXE_SUFFIX));
    if program.is_file() {
        return program;
    }
    let hashed = fs::read_dir(&examples).ok().and_then(|entries| {
        entries
            .flatten()
            .map(|entry| entry.path())
            .filter(|path| {
                path.is_file()
                    && path.extension().is_none()
                    && path
                        .file_name()
                        .is_some_and(|name| name.to_string_lossy().starts_with("goldfish-"))
            })
            .max_by_key(|path| fs::metadata(path).and_then(|m| m.modified()).ok())
    });
    hashed.unwrap_or_else(|| {
        panic!(
            "no goldfish program in {}: run the whole suite (cargo test builds the examples) or cargo build --release --example goldfish",
            examples.display()
        )
    })
}

fn run(list: &Path, panel: &Path, coverage: &Path, extra: &[&str]) -> Output {
    let mut args = vec![
        "--deck".to_string(),
        list.display().to_string(),
        "--panel".to_string(),
        panel.display().to_string(),
        "--bot".to_string(),
        "r".to_string(),
        "--opp-bot".to_string(),
        "r".to_string(),
        "--games".to_string(),
        "0".to_string(),
        "--coverage".to_string(),
        coverage.display().to_string(),
    ];
    args.extend(extra.iter().map(|arg| arg.to_string()));
    Command::new(goldfish_program())
        .args(&args)
        .output()
        .expect("goldfish should launch")
}

#[test]
fn goldfish_refuses_a_list_or_panel_deck_with_a_missing_attack_card_before_writing_anything() {
    for blocked_side in ["list", "panel"] {
        let fixture = FixtureDir::new(blocked_side);
        let (list_contents, panel_contents) = if blocked_side == "list" {
            (deck_with_missing_attack_card(), supported_deck().to_string())
        } else {
            (supported_deck().to_string(), deck_with_missing_attack_card())
        };
        let list = fixture.write("list.txt", &list_contents);
        let panel = fixture.path().join("panel");
        fs::create_dir(&panel).unwrap();
        fs::write(panel.join("opponent.txt"), panel_contents).unwrap();
        let coverage = fixture.path().join("must-not-exist.json");

        let output = run(&list, &panel, &coverage, &[]);
        let stderr = String::from_utf8_lossy(&output.stderr);
        assert_eq!(output.status.code(), Some(2), "{blocked_side}: {stderr}");
        assert!(
            stderr.contains("Card-support preflight failed; goldfish did not start."),
            "{stderr}"
        );
        assert!(
            stderr.contains("C1 019 — Volcanion — Attack effect not implemented"),
            "{stderr}"
        );
        let used_by = if blocked_side == "list" {
            "Used by: list ("
        } else {
            "Used by: panel deck ("
        };
        assert!(stderr.contains(used_by), "{stderr}");
        assert!(stderr.contains("--allow-unsupported-cards"), "{stderr}");
        assert!(!stderr.contains("panicked at"), "{stderr}");
        assert!(!coverage.exists(), "{blocked_side}: the coverage file was written");
    }
}

#[test]
fn goldfish_with_the_opt_out_lists_the_unsupported_card_and_runs() {
    let fixture = FixtureDir::new("allowed");
    let list = fixture.write("list.txt", &deck_with_missing_attack_card());
    let panel = fixture.path().join("panel");
    fs::create_dir(&panel).unwrap();
    fs::write(panel.join("opponent.txt"), supported_deck()).unwrap();
    let coverage = fixture.path().join("coverage.json");

    let output = run(&list, &panel, &coverage, &["--allow-unsupported-cards"]);
    let stderr = String::from_utf8_lossy(&output.stderr);
    assert!(output.status.success(), "{stderr}");
    assert!(stderr.contains("--allow-unsupported-cards was given"), "{stderr}");
    assert!(
        stderr.contains("C1 019 — Volcanion — Attack effect not implemented"),
        "{stderr}"
    );
    assert!(stderr.contains("Used by: list ("), "{stderr}");
    assert!(!stderr.contains("preflight failed"), "{stderr}");
    assert!(coverage.exists());
}
