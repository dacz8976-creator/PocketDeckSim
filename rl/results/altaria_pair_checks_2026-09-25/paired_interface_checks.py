#!/usr/bin/env python3
"""Bounded paired RawEnv interface checks for a selected Run 5 candidate pair.

C1 replays recorded k3 decisions through RawEnv.step and checks each decision
fingerprint plus terminal identity. C2 checks hidden-information invariance and
visible-own-hand positive controls on balanced random and one-k3 games.
This driver never trains. Outputs are written only to a new --output directory.

PocketDeckSim copy (Sept 24) of Astra's Sept 22 Weezing v Lucario script, for
Hydreigon v Lucario. Changed only: repo root detection, identity read from
project_manifest.json, seed flags (defaults in Claude Code's 21,000,000,000 block),
default decks and default output folder. Checks and pass criteria are unchanged.

Altaria copy (Sept 25) for the Altaria detector network (rl/runs/diag-altaria-lucario/PRESET_READING.md):
decks Altaria v Lucario, seeds moved to Claude Code's 21,101,000,000 block (C1 21,101,000,000, C2 21,101,100,000),
and the engine identity read from the manifest's rules4 entry in historical_releases: the add-on 0.7.2
is rules4, and available_release moved to main-7fc6ccb on Sept 25.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata
import json
import random
import sys
import traceback
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

C1_SEED0 = 21_101_000_000  # default --c1-seed (was 18,500,000 on Sept 22)
C2_SEED0 = 21_101_100_000  # default --c2-seed (was 28,500,000 on Sept 22)
U64 = (1 << 64) - 1
DECK_A = ("decks/research/altaria.txt", "435a2bebc567ca8357696e400643fdc821cc36ae4765a7a16663fd4413a3bd7f")
DECK_B = ("decks/research/lucario.txt", "46a4820bc788b4fd9ac1d9491e62bf7123c467441e7e30012e42e8a70c91e3f3")
HERE = Path(__file__).resolve().parent


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def dump_line(fp, value: Any) -> None:
    fp.write(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str) + "\n")
    fp.flush()


def find_project_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "project_manifest.json").is_file() and (parent / "lib" / "deckgym-database.json").is_file():
            return parent
    raise RuntimeError("cannot locate project root from this script path")


def result_key(value: Any) -> tuple[int, int, int, int]:
    winner, points, turns = value
    return (int(winner), int(points[0]), int(points[1]), int(turns))


def module_metadata(addon: Any, root: Path) -> dict[str, Any]:
    module_path = Path(addon.__file__).resolve()
    version = getattr(addon, "__version__", None)
    dist_name = None
    discovered = importlib.metadata.packages_distributions().get(addon.__name__, [])
    candidates = list(dict.fromkeys([*discovered, "pdl-rl-env", "pdl_rl_env"]))
    for candidate in candidates:
        try:
            version = importlib.metadata.version(candidate)
            dist_name = candidate
            break
        except importlib.metadata.PackageNotFoundError:
            continue
    # PocketDeckSim: identity comes from project_manifest.json (available_release + addon_wheel).
    # The rules4 source archive stayed in Pocket Deck Lab, so its hash is recorded, not checked.
    release_path = root / "project_manifest.json"
    project = json.loads(release_path.read_text(encoding="utf-8"))
    release = next((r for r in project.get("historical_releases") or [] if r.get("name") == "rules4"), {})
    wheel = project.get("addon_wheel") or {}
    required = ("name", "artifact", "sha256", "source_sha256_manifest", "source_sha256_manifest_sha256")
    missing = [key for key in required if not release.get(key)]
    if not wheel.get("installed_module_sha256"):
        missing.append("addon_wheel.installed_module_sha256")
    if missing:
        raise RuntimeError(f"release identity has empty/missing fields: {missing}")
    manifest_path = root / release["source_sha256_manifest"]
    engine_path = root / release["artifact"]
    for label, path, expected in (
        ("engine artifact", engine_path, release["sha256"]),
        ("source manifest", manifest_path, release["source_sha256_manifest_sha256"]),
        ("add-on module", module_path, wheel["installed_module_sha256"]),
    ):
        if not path.is_file():
            raise RuntimeError(f"{label} missing: {path}")
        observed = sha256_file(path)
        if observed.lower() != str(expected).lower():
            raise RuntimeError(f"{label} SHA-256 mismatch: expected {expected}, observed {observed}")
    if version is None:
        raise RuntimeError("add-on package version is unavailable")
    return {
        "module_name": addon.__name__,
        "module_path": str(module_path),
        "module_sha256": sha256_file(module_path),
        "distribution": dist_name,
        "version": version,
        "features_requested": None,
        "module_sha256_recorded": wheel.get("installed_module_sha256"),
        "addon_wheel": wheel.get("path"),
        "engine_release": release.get("name"),
        "engine_artifact_path": str(engine_path),
        "engine_artifact_sha256_recorded": release.get("sha256"),
        "engine_artifact_sha256_observed": sha256_file(engine_path),
        "source_archive": release.get("source_archive_location"),
        "source_archive_sha256": release.get("source_archive_sha256"),
        "source_manifest": release.get("source_sha256_manifest"),
        "source_manifest_sha256_recorded": release.get("source_sha256_manifest_sha256"),
        "source_manifest_sha256_observed": sha256_file(manifest_path),
        "source_archive_path": None,
        "source_archive_sha256_observed": None,  # archive not in this repo; not checked
        "release_identity_path": str(release_path),
        "release_identity_sha256": sha256_file(release_path) if release_path.is_file() else None,
    }


def replay_once(raw: Any, deck_paths: tuple[Path, Path], seed: int, seat: int,
                actions: list[int], expected_prints: list[Any], opponent: str) -> dict[str, Any]:
    bots: list[str | None] = [None, None]
    bots[1 - seat] = opponent
    raw.reset(str(deck_paths[0]), str(deck_paths[1]), int(seed), bots)
    compared = 0
    mismatches: list[dict[str, Any]] = []
    stop_reason = None
    for i, expected in enumerate(expected_prints):
        if raw.done:
            stop_reason = "game ended before recorded decision"
            break
        actor = raw.current_player
        if actor != seat:
            stop_reason = f"expected recorded seat {seat}, got actor {actor}"
            break
        observed = tuple(int(x) for x in raw.decision_fingerprint())
        expected_tuple = tuple(int(x) for x in expected)
        compared += 1
        if observed != expected_tuple:
            mismatches.append({"decision": i, "expected_fingerprint": expected_tuple,
                               "observed_fingerprint": observed})
            stop_reason = "decision fingerprint mismatch"
            break
        n_actions = len(raw.legal_actions())
        if i >= len(actions) or int(actions[i]) < 0 or int(actions[i]) >= n_actions:
            stop_reason = f"recorded action index {actions[i] if i < len(actions) else None} is not legal"
            break
        raw.step(int(actions[i]))
    if stop_reason is None and compared != len(actions):
        stop_reason = f"recorded action/fingerprint lengths differ: {len(actions)} vs {len(expected_prints)}"
    if stop_reason is None and not raw.done:
        stop_reason = "game did not finish after recorded decisions"
    return {
        "matched": stop_reason is None,
        "decisions_compared": compared,
        "mismatches": mismatches,
        "stop_reason": stop_reason,
        "final_state_hash": int(raw.final_state_hash()) if raw.done else None,
        "result": result_key(raw.result()) if raw.done else None,
    }


def run_c1(raw: Any, engine_play_record: Any, deck_a: Path, deck_b: Path,
           count: int, out_dir: Path, seed0: int = C1_SEED0) -> dict[str, Any]:
    tally: Counter[str] = Counter()
    seed_rows = []
    with (out_dir / "c1_games.jsonl").open("x", encoding="utf-8") as fp:
        for i in range(count):
            seed = seed0 + i
            pair = (deck_a, deck_b) if seed % 2 == 0 else (deck_b, deck_a)
            for seat in (0, 1):
                row: dict[str, Any] = {
                    "seed": seed, "recorded_seat": seat,
                    "deck_order": [str(x) for x in pair],
                    "deck_hashes": [sha256_file(x) for x in pair],
                }
                try:
                    rec, prints, ref_hash, ref_result = engine_play_record(
                        str(pair[0]), str(pair[1]), seed, ("k3", "k3"), seat)
                    replay = replay_once(raw, pair, seed, seat, list(rec), list(prints), "k3")
                    replay["reference_final_state_hash"] = int(ref_hash)
                    replay["reference_result"] = result_key(ref_result)
                    replay["terminal_match"] = (
                        replay["matched"]
                        and replay["final_state_hash"] == int(ref_hash)
                        and replay["result"] == result_key(ref_result)
                    )
                    row["k3_replay"] = replay
                    if replay["terminal_match"]:
                        tally["k3_exact_match"] += 1
                    else:
                        tally["k3_failure"] += 1
                    control = replay_once(raw, pair, seed, seat, list(rec), list(prints), "k2")
                    control["reference_final_state_hash"] = int(ref_hash)
                    control["reference_result"] = result_key(ref_result)
                    control["exact_match"] = (
                        control["matched"]
                        and control["final_state_hash"] == int(ref_hash)
                        and control["result"] == result_key(ref_result)
                    )
                    row["k2_negative_control"] = control
                    tally["k2_exact_match"] += int(control["exact_match"])
                    tally["decisions_compared"] += int(replay["decisions_compared"])
                    tally["fingerprint_mismatches"] += len(replay["mismatches"])
                except Exception as exc:  # record failures; never turn missing data into a pass
                    row["error"] = f"{type(exc).__name__}: {exc}"
                    row["traceback"] = traceback.format_exc(limit=5)
                    tally["k3_failure"] += 1
                dump_line(fp, row)
                seed_rows.append(row)
            if (i + 1) % 10 == 0 or i + 1 == count:
                print(f"C1 progress: {i + 1}/{count} seeds, {tally['k3_exact_match']}/{(i + 1) * 2} exact k3 replays", file=sys.stderr, flush=True)
    expected_games = count * 2
    passed = (
        expected_games > 0
        and tally["k3_exact_match"] == expected_games
        and tally["k2_exact_match"] < expected_games
        and tally["decisions_compared"] > 0
        and tally["fingerprint_mismatches"] == 0
        and tally["k3_failure"] == 0
    )
    return {"pass": passed, "distinct_seeds": count, "k3_replays_expected": expected_games,
            "k3_replays_exact": tally["k3_exact_match"], "k3_failures": tally["k3_failure"],
            "k2_negative_control_exact_matches": tally["k2_exact_match"],
            "decisions_compared": tally["decisions_compared"],
            "fingerprint_mismatches": tally["fingerprint_mismatches"],
            "games": seed_rows}


def empty_probe_counts() -> dict[str, int]:
    return {"checked": 0, "same": 0, "changed": 0, "none": 0, "errors": 0}


def record_probe(counter: dict[str, int], value: Any) -> None:
    if value is None:
        counter["none"] += 1
    elif bool(value):
        counter["same"] += 1
        counter["checked"] += 1
    else:
        counter["changed"] += 1
        counter["checked"] += 1


def probe_key(scenario: str, visibility: str, probe: str) -> str:
    return f"{scenario}.{visibility}.{probe}"


def run_c2(raw: Any, deck_a: Path, deck_b: Path, games: int, features: str,
           out_dir: Path, seed0: int = C2_SEED0) -> dict[str, Any]:
    half = games // 2
    totals = {probe_key(s, v, p): empty_probe_counts()
              for s in ("random", "one_k3")
              for v in ("hidden", "own_hand_control")
              for p in ("observation_and_action_features", "legal_moves")}
    game_passes = 0
    probe_decisions = 0
    with (out_dir / "c2_games.jsonl").open("x", encoding="utf-8") as games_fp, \
         (out_dir / "c2_decisions.jsonl").open("x", encoding="utf-8") as dec_fp:
        for gi in range(games):
            scenario = "random" if gi < half else "one_k3"
            local_i = gi if scenario == "random" else gi - half
            seed = seed0 + gi
            if scenario == "random":
                pair = (deck_a, deck_b) if seed % 2 == 0 else (deck_b, deck_a)
                human_seat = None
            else:
                flip = (local_i // 2) % 2
                pair = (deck_b, deck_a) if flip else (deck_a, deck_b)
                human_seat = local_i % 2
            bots: list[str | None] = [None, None]
            if human_seat is not None:
                bots[1 - human_seat] = "k3"
            row: dict[str, Any] = {
                "game_index": gi, "scenario": scenario, "seed": seed,
                "deck_order": [str(x) for x in pair],
                "deck_hashes": [sha256_file(x) for x in pair],
                "human_seat": human_seat, "features": features,
                "decisions": 0, "probe_counts": {}, "error": None,
            }
            decision_rows: list[dict[str, Any]] = []
            rng = random.Random(seed)
            try:
                raw.reset(str(pair[0]), str(pair[1]), int(seed), bots)
                while not raw.done:
                    actor = raw.current_player
                    if actor is None:
                        raise RuntimeError("nonterminal environment has no acting player")
                    if human_seat is not None and actor != human_seat:
                        raise RuntimeError(f"k3 environment exposed non-human seat {actor}")
                    if not raw.legal_actions():
                        raise RuntimeError("nonterminal decision has no legal actions")
                    probe_seed = (seed ^ ((row["decisions"] + 1) * 0x9E3779B97F4A7C15)) & U64
                    values: dict[str, Any] = {}
                    for visibility, control in (("hidden", False), ("own_hand_control", True)):
                        for probe, method in (("observation_and_action_features", raw.hidden_info_probe),
                                              ("legal_moves", raw.hidden_move_probe)):
                            key = probe_key(scenario, visibility, probe)
                            try:
                                value = method(int(probe_seed), control)
                            except Exception:
                                totals[key]["errors"] += 1
                                raise
                            values[key] = value
                            record_probe(totals[key], value)
                    decision = {"game_index": gi, "decision_index": row["decisions"],
                                "actor": int(actor), "probe_seed": int(probe_seed),
                                "probes": values, "legal_action_count": len(raw.legal_actions())}
                    decision_rows.append(decision)
                    dump_line(dec_fp, decision)
                    row["decisions"] += 1
                    probe_decisions += 1
                    raw.step(rng.randrange(len(raw.legal_actions())))
                row["result"] = result_key(raw.result())
                row["final_state_hash"] = int(raw.final_state_hash())
                row["probe_counts"] = {k: {"checked": sum(v is not None for v in [d["probes"].get(k) for d in decision_rows]),
                                           "same": sum(d["probes"].get(k) is True for d in decision_rows),
                                           "changed": sum(d["probes"].get(k) is False for d in decision_rows),
                                           "none": sum(d["probes"].get(k) is None for d in decision_rows)}
                                       for k in totals if k.startswith(scenario + ".")}
                row["pass"] = row["decisions"] > 0
                game_passes += int(row["pass"])
            except Exception as exc:
                row["error"] = f"{type(exc).__name__}: {exc}"
                row["traceback"] = traceback.format_exc(limit=5)
                row["pass"] = False
            dump_line(games_fp, row)
            if (gi + 1) % 10 == 0 or gi + 1 == games:
                print(f"C2 progress: {gi + 1}/{games} games, {game_passes} completed", file=sys.stderr, flush=True)
    hidden_keys = [probe_key(s, "hidden", p) for s in ("random", "one_k3")
                   for p in ("observation_and_action_features", "legal_moves")]
    control_keys = [probe_key(s, "own_hand_control", p) for s in ("random", "one_k3")
                    for p in ("observation_and_action_features", "legal_moves")]
    no_hidden_changes = all(totals[k]["changed"] == 0 and totals[k]["checked"] > 0 for k in hidden_keys)
    controls_sensed = all(totals[k]["changed"] > 0 and totals[k]["checked"] > 0 for k in control_keys)
    passed = (games > 0 and games % 2 == 0 and game_passes == games and probe_decisions > 0
              and no_hidden_changes and controls_sensed)
    return {"pass": passed, "games_expected": games, "games_completed_with_decisions": game_passes,
            "random_games_expected": half, "one_k3_games_expected": half,
            "probe_decisions": probe_decisions, "hidden_invariance_pass": no_hidden_changes,
            "own_hand_controls_detect_changes": controls_sensed, "counts": totals}


def parse_args() -> argparse.Namespace:
    root = find_project_root()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--deck-a", type=Path, default=root / DECK_A[0], help="first candidate deck list (default: %(default)s)")
    parser.add_argument("--deck-b", type=Path, default=root / DECK_B[0], help="second candidate deck list (default: %(default)s)")
    parser.add_argument("--output", type=Path, default=HERE / f"altaria-lucario-interface-072-{stamp}",
                        help="new output directory; must not already exist (default: a new timestamped folder next to this script)")
    parser.add_argument("--features", default="v2.2", choices=("v1", "v2.1", "v2.2"))
    parser.add_argument("--replay-seeds", type=int, default=50, help="distinct C1 seeds (50 gives 100 recorded-seat replays)")
    parser.add_argument("--hidden-games", type=int, default=100, help="even C2 total: half random, half one-k3")
    parser.add_argument("--c1-seed", type=int, default=C1_SEED0, help="first C1 game seed (default: %(default)s)")
    parser.add_argument("--c2-seed", type=int, default=C2_SEED0, help="first C2 game seed (default: %(default)s)")
    args = parser.parse_args()
    if args.replay_seeds < 1:
        parser.error("--replay-seeds must be at least 1")
    if args.hidden_games < 2 or args.hidden_games % 2:
        parser.error("--hidden-games must be an even number of at least 2")
    if not args.deck_a.is_file() or not args.deck_b.is_file():
        parser.error("both deck paths must be existing files")
    for path, (rel, expected) in ((args.deck_a, DECK_A), (args.deck_b, DECK_B)):
        if path.resolve() == (root / rel).resolve() and sha256_file(path) != expected:
            parser.error(f"{rel} has changed: its SHA-256 is no longer {expected}")
    if args.output.exists():
        parser.error("--output must be a new directory; existing paths are never overwritten")
    return args


def main() -> int:
    args = parse_args()
    root = find_project_root()
    deck_a = args.deck_a.resolve()
    deck_b = args.deck_b.resolve()
    try:
        addon = importlib.import_module("pdl_rl_env")
        RawEnv = addon.RawEnv
        from pdl_rl_env import engine_play_record
        vocab = sorted(set(RawEnv.deck_card_ids(str(deck_a))) | set(RawEnv.deck_card_ids(str(deck_b))))
        raw = RawEnv(vocab, args.features)
    except Exception as exc:
        print(f"Cannot initialize requested add-on: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    script_path = Path(__file__).resolve()
    try:
        meta = module_metadata(addon, root)
    except Exception as exc:
        print(f"Cannot verify add-on/release identity: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    meta["features_requested"] = args.features
    meta["features_active"] = raw.features
    meta["script_path"] = str(script_path)
    meta["script_sha256"] = sha256_file(script_path)
    meta["python_version"] = sys.version
    meta["project_root"] = str(root)
    meta["deck_a"] = {"path": str(deck_a), "sha256": sha256_file(deck_a)}
    meta["deck_b"] = {"path": str(deck_b), "sha256": sha256_file(deck_b)}
    meta["vocab_ids"] = vocab
    meta["raw_env_action_dim"] = int(raw.action_dim)
    meta["raw_env_observation_dim"] = int(raw.obs_dim)
    meta["seeds"] = {"c1_start": args.c1_seed, "c2_start": args.c2_seed,
                      "c1_count": args.replay_seeds, "c2_count": args.hidden_games}
    initial_hashes = {"deck_a": meta["deck_a"]["sha256"], "deck_b": meta["deck_b"]["sha256"],
                      "module": meta["module_sha256"]}
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "input_identity.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(f"Decks: {deck_a.name} {meta['deck_a']['sha256'][:16]}, {deck_b.name} {meta['deck_b']['sha256'][:16]}; "
          f"module {meta['module_sha256'][:16]}; engine {meta['engine_artifact_sha256_observed'][:16]}", file=sys.stderr, flush=True)
    print(f"Seeds: C1 {args.c1_seed:,} to {args.c1_seed + args.replay_seeds - 1:,}; "
          f"C2 {args.c2_seed:,} to {args.c2_seed + args.hidden_games - 1:,}. Output: {args.output}", file=sys.stderr, flush=True)
    c1 = run_c1(raw, engine_play_record, deck_a, deck_b, args.replay_seeds, args.output, args.c1_seed)
    c2 = run_c2(raw, deck_a, deck_b, args.hidden_games, args.features, args.output, args.c2_seed)
    after_hashes = {"deck_a": sha256_file(deck_a), "deck_b": sha256_file(deck_b),
                    "module": sha256_file(Path(meta["module_path"]))}
    unchanged = after_hashes == initial_hashes
    summary = {"features": args.features, "input_identity": "input_identity.json", "c1": c1, "c2": c2,
               "post_check_identity": {"sha256": after_hashes, "unchanged": unchanged},
               "pass": bool(c1["pass"] and c2["pass"] and unchanged),
               "scope": "C1/C2 only; no training; v2.2 skip/forecast diagnostics are separate"}
    summary.pop("c1", None)  # Per-game rows remain in c1_games.jsonl; keep summary compact.
    summary["c1"] = {k: v for k, v in c1.items() if k != "games"}
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if summary["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())



