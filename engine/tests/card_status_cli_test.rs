use std::process::Command;

/// The sets upstream #430 added (Dual Fusion C1, SP1, promo P-C) and their printing counts. Their
/// designs are implemented release by release, so these tests check that the cards are listed but
/// pin neither which of them are still incomplete nor how many.
const NEW_SETS: [(&str, usize); 3] = [("C1", 217), ("SP1", 30), ("P-C", 13)];

fn set_of(card: &serde_json::Value) -> &str {
    let id = card["id"].as_str().expect("every card has a string id");
    id.split_once(' ').map_or(id, |(set, _)| set)
}

fn in_new_set(card: &serde_json::Value) -> bool {
    let set = set_of(card);
    NEW_SETS.iter().any(|&(new_set, _)| new_set == set)
}

fn inventory(args: &[&str]) -> serde_json::Value {
    let output = Command::new(env!("CARGO_BIN_EXE_card_status"))
        .arg("--json")
        .args(args)
        .output()
        .expect("card_status should launch");
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    serde_json::from_slice(&output.stdout).expect("stdout should be one valid JSON document")
}

#[test]
fn inventory_includes_new_printings_and_explicit_rule_boundaries() {
    let all = inventory(&[]);
    assert_eq!(all["schema_version"], 1);
    assert_eq!(all["engine_version"], env!("CARGO_PKG_VERSION"));
    let cards = all["cards"].as_array().unwrap();
    // 4,317 before the Dual Fusion data, plus its 260 printings.
    assert_eq!(cards.len(), 4577);
    for (set, count) in NEW_SETS {
        assert_eq!(
            cards.iter().filter(|card| set_of(card) == set).count(),
            count,
            "{set} printings listed"
        );
    }
    for id in [
        "B3 025", "P-B 049", "B4 115", "B4a 051", "B4a 069", "B4a 109",
    ] {
        let card = cards.iter().find(|card| card["id"] == id).unwrap();
        assert_eq!(card["status"], "RulesUnverified");
        assert!(!card["limitations"].as_array().unwrap().is_empty());
    }
    assert!(cards
        .iter()
        .any(|card| card["id"] == "B4a 002" && card["status"] == "Complete"));
    for id in ["B4a 021", "B4a 062", "B4a 064", "B4a 071"] {
        assert!(cards
            .iter()
            .any(|card| card["id"] == id && card["status"] == "Complete"));
    }
    assert!(cards
        .iter()
        .any(|card| card["id"] == "P-B 091" && card["status"] == "Complete"));
    // Every card outside the new sets is Complete or RulesUnverified.
    assert!(cards
        .iter()
        .filter(|card| !in_new_set(card))
        .all(|card| matches!(
            card["status"].as_str(),
            Some("Complete" | "RulesUnverified")
        )));
}

#[test]
fn incomplete_inventory_does_not_hide_unverified_cards() {
    let incomplete = inventory(&["--incomplete-only"]);
    let cards = incomplete["cards"].as_array().unwrap();
    // Outside the new sets, every incomplete card is RulesUnverified.
    assert!(cards
        .iter()
        .filter(|card| !in_new_set(card))
        .all(|card| card["status"] == "RulesUnverified"));
    assert!(cards.iter().any(|card| card["id"] == "B4 115"));
    assert!(cards.iter().any(|card| card["id"] == "B4a 051"));
    assert_eq!(
        inventory(&["--first-incomplete"])["cards"]
            .as_array()
            .unwrap()
            .len(),
        1
    );
}
