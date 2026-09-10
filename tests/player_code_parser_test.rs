use deckgym::players::{parse_player_code, PlayerCode};
use std::{
    path::PathBuf,
    process::{Command, Output},
};

#[test]
fn exact_multi_letter_codes_are_case_insensitive_and_precede_prefixes() {
    for code in ["et", "ET", "eT"] {
        assert_eq!(parse_player_code(code), Ok(PlayerCode::ET), "{code}");
    }
    for code in ["er", "ER", "eR"] {
        assert_eq!(parse_player_code(code), Ok(PlayerCode::ER), "{code}");
    }
    for code in ["aa", "AA", "aA"] {
        assert_eq!(parse_player_code(code), Ok(PlayerCode::AA), "{code}");
    }

    assert_eq!(parse_player_code("e"), Ok(PlayerCode::E { max_depth: 3 }));
    assert_eq!(parse_player_code("E4"), Ok(PlayerCode::E { max_depth: 4 }));
}

#[test]
fn malformed_prefixed_and_extended_codes_are_rejected() {
    for code in ["et2", "er2", "efoo", "e-1", "e2x", "aa2", ""] {
        assert!(parse_player_code(code).is_err(), "{code:?} unexpectedly parsed");
    }
}

fn cli(players: &str) -> Output {
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let deck_a = root.join("tests/fixtures/result-deck-a.txt");
    let deck_b = root.join("tests/fixtures/result-deck-b.txt");
    Command::new(env!("CARGO_BIN_EXE_deckgym"))
        .arg("simulate")
        .arg(deck_a)
        .arg(deck_b)
        .args(["--players", players, "--num", "1", "--seed", "714001"])
        .output()
        .unwrap()
}

#[test]
fn cli_accepts_mixed_case_end_turn_codes_and_rejects_malformed_e_codes() {
    let accepted = cli("ET,eT");
    assert!(
        accepted.status.success(),
        "stdout:\n{}\nstderr:\n{}",
        String::from_utf8_lossy(&accepted.stdout),
        String::from_utf8_lossy(&accepted.stderr)
    );

    let rejected = cli("et2,et");
    assert!(!rejected.status.success());
    assert!(
        String::from_utf8_lossy(&rejected.stderr).contains("Invalid player code: et2"),
        "stderr:\n{}",
        String::from_utf8_lossy(&rejected.stderr)
    );
}
