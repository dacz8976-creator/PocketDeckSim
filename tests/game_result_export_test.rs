use std::{collections::BTreeMap, fs, path::{Path, PathBuf}, process::Command};
use serde_json::Value;
use uuid::Uuid;
use deckgym::{players::PlayerCode, ParallelConfig, SimulationConfig};

struct Workspace(PathBuf);
impl Workspace {
    fn new() -> Self {
        let path = std::env::temp_dir().join(format!("pdl-game-result-test-{}", Uuid::new_v4()));
        fs::create_dir(&path).unwrap();
        fs::write(path.join("a.txt"), include_str!("fixtures/result-deck-a.txt")).unwrap();
        fs::write(path.join("b.txt"), include_str!("fixtures/result-deck-b.txt")).unwrap();
        Self(path)
    }
}
impl Drop for Workspace {
    fn drop(&mut self) { let _ = fs::remove_dir_all(&self.0); }
}

fn run(root: &Path, name: &str, games: u32, seed: u64, parallel: bool, stream: bool, traces: bool, players: &str) -> PathBuf {
    let results = root.join(name);
    let mut command = Command::new(env!("CARGO_BIN_EXE_deckgym"));
    command.arg("simulate").args(["--players", players, "--num", &games.to_string(), "--seed", &seed.to_string()])
        .arg("--results-output").arg(&results);
    if stream { command.arg("--seed-stream"); }
    if parallel { command.args(["--parallel", "--threads", "2"]); }
    if traces { command.arg("--data-output").arg(root.join(format!("{name}-traces"))); }
    let output = command.arg(root.join("a.txt")).arg(root.join("b.txt")).output().unwrap();
    assert!(output.status.success(), "{}", String::from_utf8_lossy(&output.stderr));
    results
}

fn read_results(folder: &Path) -> Vec<Value> {
    let files: Vec<_> = fs::read_dir(folder).unwrap().map(|x| x.unwrap().path()).collect();
    assert!(!files.is_empty());
    files.into_iter().map(|path| {
        assert!(path.is_file(), "results-only output must not create ply directories");
        let value: Value = serde_json::from_slice(&fs::read(&path).unwrap()).unwrap();
        let id = value["game_id"].as_str().unwrap();
        Uuid::parse_str(id).unwrap();
        assert_eq!(path.file_name().unwrap().to_str().unwrap(), format!("game_{id}.json"));
        assert_eq!(value["schema"], "pdl-game-result/v1");
        assert_eq!(value["engine_version"], env!("CARGO_PKG_VERSION"));
        assert_eq!(value["completion"], "completed");
        assert_eq!(value["state_winner"], value["outcome"]);
        assert_eq!(value["lifecycle_errors"], 0);
        let actions = value["actions_by_player"].as_array().unwrap();
        assert_eq!(value["plies"].as_u64().unwrap(), actions.iter().map(|x| x.as_u64().unwrap()).sum::<u64>());
        value
    }).collect()
}

fn by_seed(folder: &Path) -> BTreeMap<u64, Value> {
    let mut result = BTreeMap::new();
    for mut value in read_results(folder) {
        let seed = value["randomness"]["game_seed"].as_u64().unwrap();
        value.as_object_mut().unwrap().remove("game_id");
        assert!(result.insert(seed, value).is_none(), "streamed seeds must stay distinct");
    }
    result
}

#[test]
fn results_only_records_real_turn_cap_ties_with_matchup_and_seed() {
    let root = Workspace::new();
    let folder = root.0.join("ties");
    let a = deckgym::Deck::from_string(include_str!("fixtures/result-deck-a.txt")).unwrap();
    let b = deckgym::Deck::from_string(include_str!("fixtures/result-deck-b.txt")).unwrap();
    deckgym::simulate::simulate_with_results(
        root.0.join("a.txt").to_str().unwrap(),
        root.0.join("b.txt").to_str().unwrap(),
        SimulationConfig {
            num_games: 2,
            players: Some(vec![PlayerCode::ET, PlayerCode::ET]),
            seed: Some(991001),
            seed_stream: true,
            data_output: None,
        },
        ParallelConfig {
            enabled: false,
            num_threads: None,
        },
        Some(folder.to_str().unwrap().to_string()),
    )
    .unwrap();
    let rows = by_seed(&folder);
    assert_eq!(rows.keys().copied().collect::<Vec<_>>(), vec![991001, 991002]);
    for row in rows.values() {
        assert_eq!(row["outcome"], "Tie");
        assert_eq!(row["final_turn"], 31);
        assert_eq!(row["final_points"], serde_json::json!([0, 0]));
        assert!(row["plies"].as_u64().unwrap() > 0);
        let decks = &row["matchup"]["decks"];
        for (seat, deck) in [&a, &b].iter().enumerate() {
            let ids: Vec<_> = deck.cards.iter().map(|card| card.get_id()).collect();
            assert_eq!(decks[seat]["card_ids"], serde_json::to_value(ids).unwrap());
        }
        assert_eq!(decks[0]["energy_types"], serde_json::json!(["Psychic"]));
        assert_eq!(decks[1]["energy_types"], serde_json::json!(["Grass"]));
        assert_eq!(row["matchup"]["player_codes"].as_array().unwrap().len(), 2);
    }
}

#[test]
fn final_records_bind_all_legacy_plies_when_both_outputs_are_requested() {
    let root = Workspace::new();
    let folder = run(&root.0, "both", 2, 992001, false, true, true, "r,r");
    let rows = read_results(&folder);
    assert_eq!(rows.len(), 2);
    for row in rows {
        let game = root.0.join("both-traces").join(row["game_id"].as_str().unwrap());
        let plies: Vec<_> = fs::read_dir(game).unwrap().map(|x| x.unwrap().path()).collect();
        assert_eq!(plies.len() as u64, row["plies"].as_u64().unwrap());
        for path in plies {
            let ply: Value = serde_json::from_slice(&fs::read(path).unwrap()).unwrap();
            assert_eq!(ply["game_id"], row["game_id"]);
            assert_eq!(ply["randomness"], row["randomness"]);
        }
    }
}

#[test]
fn batched_single_and_parallel_results_match_by_effective_seed() {
    let root = Workspace::new();
    let serial = by_seed(&run(&root.0, "serial", 4, 993001, false, true, false, "r,r"));
    let parallel = by_seed(&run(&root.0, "parallel", 4, 993001, true, true, false, "r,r"));
    assert_eq!(serial, parallel);
    for seed in 993001..993005 {
        let single = by_seed(&run(&root.0, &format!("single-{seed}"), 1, seed, false, true, false, "r,r"));
        assert_eq!(single[&seed], serial[&seed]);
    }
}

#[test]
fn repeated_seed_mode_keeps_separate_games_and_stream_wrap_reports_effective_seed() {
    let root = Workspace::new();
    let rows = read_results(&run(&root.0, "repeat", 3, 994001, true, false, false, "r,r"));
    assert_eq!(rows.len(), 3);
    let mut ids = std::collections::HashSet::new();
    for row in rows {
        assert!(ids.insert(row["game_id"].as_str().unwrap().to_owned()));
        assert_eq!(row["randomness"]["game_seed"], 994001);
    }
    let wrapped = by_seed(&run(&root.0, "wrapped", 2, u64::MAX, false, true, false, "r,r"));
    assert_eq!(wrapped.keys().copied().collect::<Vec<_>>(), vec![0, u64::MAX]);
}

#[test]
fn unavailable_result_destination_fails_the_cli_without_overwriting_existing_data() {
    let root = Workspace::new();
    let path = root.0.join("occupied");
    fs::write(&path, b"preserve this file").unwrap();
    let output = Command::new(env!("CARGO_BIN_EXE_deckgym"))
        .args(["simulate", "--players", "r,r", "--num", "1", "--seed", "995001"])
        .arg("--results-output").arg(&path).arg(root.0.join("a.txt")).arg(root.0.join("b.txt"))
        .output().unwrap();
    assert!(!output.status.success());
    assert_eq!(fs::read(path).unwrap(), b"preserve this file");
}

use deckgym::{
    actions::{Action, SimpleAction},
    game::GameRandomness,
    game_result_exporter::{ExportedMatchup, GameResultExporter},
    simulation_event_handler::SimulationEventHandler,
    state::GameOutcome,
    State,
};

fn matchup() -> ExportedMatchup {
    let a = deckgym::Deck::from_string(include_str!("fixtures/result-deck-a.txt")).unwrap();
    let b = deckgym::Deck::from_string(include_str!("fixtures/result-deck-b.txt")).unwrap();
    ExportedMatchup::from_decks(&a, &b, vec!["Random".into(), "Random".into()]).unwrap()
}
fn randomness(seed: u64) -> GameRandomness {
    GameRandomness { scheme: "handler-fixture".into(), game_seed: seed, player_search_seeds: [seed, seed ^ 1] }
}
fn start(exporter: &mut GameResultExporter, id: Uuid, seed: u64) {
    exporter.on_game_start(id);
    exporter.on_game_randomness(id, &randomness(seed));
}
fn finish(exporter: &mut GameResultExporter, id: Uuid, callback: Option<GameOutcome>, winner: Option<GameOutcome>) {
    let mut state = State::default();
    state.winner = winner;
    exporter.on_game_end(id, state, callback);
}
fn result_path(folder: &Path, id: Uuid) -> PathBuf { folder.join(format!("game_{id}.json")) }
fn load(folder: &Path, id: Uuid) -> Value {
    serde_json::from_slice(&fs::read(result_path(folder, id)).unwrap()).unwrap()
}

#[test]
fn callback_and_final_state_disagreements_are_explicit_and_never_count_as_draws() {
    let root = Workspace::new();
    let cases = [
        (Some(GameOutcome::Win(0)), Some(GameOutcome::Win(0)), "completed"),
        (Some(GameOutcome::Win(1)), Some(GameOutcome::Win(1)), "completed"),
        (Some(GameOutcome::Tie), Some(GameOutcome::Tie), "completed"),
        (None, None, "incomplete"),
        (Some(GameOutcome::Win(0)), Some(GameOutcome::Win(1)), "inconsistent"),
        (Some(GameOutcome::Tie), None, "inconsistent"),
        (None, Some(GameOutcome::Tie), "inconsistent"),
        (Some(GameOutcome::Win(2)), Some(GameOutcome::Win(2)), "inconsistent"),
    ];
    for (index, (callback, winner, expected)) in cases.into_iter().enumerate() {
        let folder = root.0.join(format!("case-{index}"));
        let mut exporter = GameResultExporter::new(folder.clone(), matchup());
        let id = Uuid::new_v4();
        start(&mut exporter, id, index as u64);
        finish(&mut exporter, id, callback, winner);
        let row = load(&folder, id);
        assert_eq!(row["completion"], expected);
        assert_eq!(row["outcome"], serde_json::to_value(callback).unwrap());
        assert_eq!(row["state_winner"], serde_json::to_value(winner).unwrap());
        assert_eq!(exporter.failure_count() == 0, expected == "completed");
        assert_eq!(row["lifecycle_errors"].as_u64().unwrap() == 0, expected == "completed");
    }
}

#[test]
fn unexpected_ids_duplicate_metadata_and_invalid_actors_are_not_silent_success() {
    let root = Workspace::new();
    let folder = root.0.join("lifecycle");
    let mut exporter = GameResultExporter::new(folder.clone(), matchup());
    let id = Uuid::new_v4();
    start(&mut exporter, id, 10);
    exporter.on_game_randomness(id, &randomness(99));
    finish(&mut exporter, Uuid::new_v4(), Some(GameOutcome::Win(0)), Some(GameOutcome::Win(0)));
    let action = Action { actor: 2, action: SimpleAction::Noop, is_stack: false };
    exporter.on_action(id, &State::default(), 2, &[action.clone()], &action);
    finish(&mut exporter, id, Some(GameOutcome::Win(0)), Some(GameOutcome::Win(0)));
    let before = fs::read(result_path(&folder, id)).unwrap();
    let row: Value = serde_json::from_slice(&before).unwrap();
    assert_eq!(row["randomness"]["game_seed"], 10);
    assert_eq!(row["plies"], 0);
    assert!(row["lifecycle_errors"].as_u64().unwrap() >= 3);
    finish(&mut exporter, id, Some(GameOutcome::Tie), Some(GameOutcome::Tie));
    assert_eq!(fs::read(result_path(&folder, id)).unwrap(), before);
    assert!(exporter.failure_count() >= 4);
    assert_eq!(fs::read_dir(folder).unwrap().count(), 1);
}

#[test]
fn handler_reuse_does_not_carry_previous_seed_into_a_game_missing_randomness() {
    let root = Workspace::new();
    let folder = root.0.join("reuse");
    let mut exporter = GameResultExporter::new(folder.clone(), matchup());
    let first = Uuid::new_v4();
    start(&mut exporter, first, 30);
    finish(&mut exporter, first, Some(GameOutcome::Win(0)), Some(GameOutcome::Win(0)));
    let second = Uuid::new_v4();
    exporter.on_game_start(second);
    finish(&mut exporter, second, Some(GameOutcome::Tie), Some(GameOutcome::Tie));
    assert_eq!(load(&folder, first)["randomness"]["game_seed"], 30);
    assert!(load(&folder, second)["randomness"].is_null());
    assert_eq!(load(&folder, second)["lifecycle_errors"], 1);
    assert_eq!(exporter.failure_count(), 1);
}

#[test]
fn missing_game_end_produces_no_result_and_is_reported_through_merge() {
    let root = Workspace::new();
    let folder = root.0.join("orphan");
    let mut child = GameResultExporter::new(folder.clone(), matchup());
    start(&mut child, Uuid::new_v4(), 40);
    let mut parent = GameResultExporter::new(folder.clone(), matchup());
    parent.merge(&child);
    assert_eq!(parent.failure_count(), 1);
    child.on_simulation_end();
    parent.on_simulation_end();
    assert_eq!(child.failure_count(), 1);
    assert!(!folder.exists(), "simulation end must not invent an end-of-game record");
}

#[test]
fn result_collision_is_not_overwritten_and_worker_write_failure_reaches_parent() {
    let root = Workspace::new();
    let folder = root.0.join("collision");
    let id = Uuid::new_v4();
    let mut first = GameResultExporter::new(folder.clone(), matchup());
    start(&mut first, id, 50);
    finish(&mut first, id, Some(GameOutcome::Win(0)), Some(GameOutcome::Win(0)));
    let before = fs::read(result_path(&folder, id)).unwrap();
    let mut second = GameResultExporter::new(folder.clone(), matchup());
    start(&mut second, id, 51);
    finish(&mut second, id, Some(GameOutcome::Win(1)), Some(GameOutcome::Win(1)));
    assert_eq!(second.failure_count(), 1);
    assert_eq!(fs::read(result_path(&folder, id)).unwrap(), before);
    assert_eq!(fs::read_dir(&folder).unwrap().count(), 1, "owned temporary should be removed");
    let mut parent = GameResultExporter::new(folder, matchup());
    parent.merge(&second);
    assert_eq!(parent.failure_count(), 1);
}

#[test]
fn starting_a_new_game_reports_the_orphan_without_fabricating_its_result() {
    let root = Workspace::new();
    let folder = root.0.join("replace");
    let mut exporter = GameResultExporter::new(folder.clone(), matchup());
    let orphan = Uuid::new_v4();
    start(&mut exporter, orphan, 60);
    let next = Uuid::new_v4();
    start(&mut exporter, next, 61);
    finish(&mut exporter, next, Some(GameOutcome::Win(1)), Some(GameOutcome::Win(1)));
    assert!(!result_path(&folder, orphan).exists());
    assert_eq!(load(&folder, next)["randomness"]["game_seed"], 61);
    assert_eq!(load(&folder, next)["lifecycle_errors"], 0);
    assert_eq!(exporter.failure_count(), 1);
}

#[test]
fn opponent_folder_results_keep_each_matchup_distinct_despite_reused_seed_ranges() {
    let root = Workspace::new();
    let opponents = root.0.join("opponents");
    fs::create_dir(&opponents).unwrap();
    fs::copy(root.0.join("a.txt"), opponents.join("one.txt")).unwrap();
    fs::copy(root.0.join("b.txt"), opponents.join("two.txt")).unwrap();
    let folder = root.0.join("folder-results");
    let output = Command::new(env!("CARGO_BIN_EXE_deckgym"))
        .args(["simulate", "--players", "r,r", "--num", "4", "--seed", "996001", "--seed-stream"])
        .arg("--results-output").arg(&folder).arg(root.0.join("a.txt")).arg(opponents)
        .output().unwrap();
    assert!(output.status.success(), "{}", String::from_utf8_lossy(&output.stderr));
    let rows = read_results(&folder);
    assert_eq!(rows.len(), 4);
    let mut groups: BTreeMap<String, Vec<u64>> = BTreeMap::new();
    for row in rows {
        let identity = serde_json::to_string(&row["matchup"]["decks"][1]).unwrap();
        groups.entry(identity).or_default().push(row["randomness"]["game_seed"].as_u64().unwrap());
    }
    assert_eq!(groups.len(), 2);
    for seeds in groups.values_mut() {
        seeds.sort();
        assert_eq!(seeds, &vec![996001, 996002]);
    }
}
