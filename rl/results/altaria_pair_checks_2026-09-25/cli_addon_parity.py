#!/usr/bin/env python3
"""Compare the six frozen rules3 pilot cells against a supplied rules4 CLI/add-on pair.

This prepares the existing 12-game parity protocol. It never chooses a new deck pair,
seed, or player configuration. Run only after the expected rules4 engine and add-on
identities are available. Each CLI game exports one compact pdl-game-result/v1 record.

PocketDeckSim copy (Sept 24) of Astra's Sept 22 script. Changed only: repo root
detection, deck paths (same bytes, now under decks/research and decks/dustin),
two added Hydreigon v Lucario cells, seeds from --seed0 (default 21,000,300,000;
was 96,092,200-201), a --cases filter, and the default output folder (a new
timestamped folder next to this script; /tmp is also accepted for smoke tests).
The comparison and pass criterion are unchanged.
Altaria copy (Sept 25) for the Altaria detector network (rl/runs/diag-altaria-lucario/PRESET_READING.md):
decks Altaria v Lucario, seeds moved to Claude Code's 21,101,000,000 block (seeds 21,101,300,000-001):
the two Hydreigon v Lucario cells are replaced by Altaria v Lucario cells.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata
import json
import os
import re
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SEED0 = 21_101_300_000  # default --seed0 (Sept 22 used 96,092,200 and 96,092,201)
HERE = Path(__file__).resolve().parent
POOL = {
    "blaziken": ("decks/dustin/06-mega-blaziken-tournament-list.txt",
                 "69c521a33339a45633c5770b3e4acad5b8912f9367288a3044147e7fa45d5800"),
    "lucario": ("decks/research/lucario.txt",
                "46a4820bc788b4fd9ac1d9491e62bf7123c467441e7e30012e42e8a70c91e3f3"),
    "weezing": ("decks/research/weezing.txt",
                "c322fe64d6052bf9c55875ecf8bebcf9460e819df19d21fc8a20a04ff7a79e9b"),
    "altaria": ("decks/research/altaria.txt",
                "435a2bebc567ca8357696e400643fdc821cc36ae4765a7a16663fd4413a3bd7f"),
    "suicune": ("decks/research/suicune.txt",
                "7affe6530b8d096b2d81425380bbb92c303de84458bc2fd1ee0936c40f922633"),
}
CASES = (
    ("altaria-lucario-k2-k3", "altaria", "lucario", ("k2", "k3")),
    ("altaria-lucario-k3-k3", "altaria", "lucario", ("k3", "k3")),
    ("blaziken-lucario-k2-k3", "blaziken", "lucario", ("k2", "k3")),
    ("blaziken-lucario-k3-k3", "blaziken", "lucario", ("k3", "k3")),
    ("suicune-altaria-k2-k3", "suicune", "altaria", ("k2", "k3")),
    ("suicune-altaria-k3-k3", "suicune", "altaria", ("k3", "k3")),
    ("weezing-lucario-k2-k3", "weezing", "lucario", ("k2", "k3")),
    ("weezing-lucario-k3-k3", "weezing", "lucario", ("k3", "k3")),
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def find_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "project_manifest.json").is_file() and (parent / "lib" / "deckgym-database.json").is_file():
            return parent
    raise RuntimeError("could not locate project root")


def dist_version(module: Any) -> tuple[str, str]:
    names = importlib.metadata.packages_distributions().get(module.__name__, [])
    for name in names:
        try:
            return name, importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            pass
    for name in ("pdl_rl_env", "pdl-rl-env"):
        try:
            return name, importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            pass
    version = getattr(module, "__version__", None)
    if version:
        return "module.__version__", str(version)
    raise RuntimeError("add-on distribution version is unavailable")


def result_winner(value: Any) -> int:
    if value == "Tie":
        return -1
    if not isinstance(value, dict) or set(value) != {"Win"}:
        raise ValueError(f"unexpected state_winner: {value!r}")
    payload = value["Win"]
    if type(payload) is not int or payload not in (0, 1):
        raise ValueError(f"unexpected Win seat in state_winner: {value!r}")
    return payload


def load_cli_record(outdir: Path, seed: int, expected_version: str) -> dict[str, Any]:
    files = sorted(outdir.glob("*.json"))
    if len(files) != 1:
        raise RuntimeError(f"expected exactly one compact game JSON, found {len(files)}")
    record = json.loads(files[0].read_text(encoding="utf-8"))
    if record.get("schema") != "pdl-game-result/v1":
        raise RuntimeError(f"unexpected result schema: {record.get('schema')!r}")
    if record.get("completion") != "completed" or record.get("lifecycle_errors") != 0:
        raise RuntimeError(f"CLI game incomplete or had lifecycle errors: {record.get('completion')!r}")
    if record.get("engine_version") != expected_version:
        raise RuntimeError(f"CLI record engine version differs: {record.get('engine_version')!r}")
    if int(record.get("randomness", {}).get("game_seed", -1)) != seed:
        raise RuntimeError("CLI record seed differs from requested seed")
    return {
        "record_path": str(files[0]),
        "record_sha256": sha256_file(files[0]),
        "winner": result_winner(record.get("state_winner")),
        "points": [int(x) for x in record["final_points"]],
        "turns": int(record["final_turn"]),
        "record_engine_version": record["engine_version"],
        "seed": seed,
        "game_id": record.get("game_id"),
    }


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--engine", required=True, type=Path, help="rules4 candidate executable")
    parser.add_argument("--engine-sha256", required=True, help="expected rules4 executable SHA-256")
    parser.add_argument("--engine-version", required=True,
                        help="expected compact-record version, e.g. 0.1.0-pdl.rules4 (omit the 'deckgym ' prefix)")
    parser.add_argument("--addon-sha256", required=True, help="expected installed pdl_rl_env module SHA-256")
    parser.add_argument("--addon-version", required=True, help="expected installed add-on distribution version")
    parser.add_argument("--output", type=Path, default=HERE / f"cli-addon-parity-072-{stamp}",
                        help="new output directory inside this folder or /tmp (default: a new timestamped folder here)")
    parser.add_argument("--seed0", type=int, default=SEED0, help="first seed; each case plays seeds seed0, seed0+1, ... (default: %(default)s)")
    parser.add_argument("--seeds-per-case", type=int, default=2, help="seeds per case (default: %(default)s, as on Sept 22)")
    parser.add_argument("--cases", default=",".join(c[0] for c in CASES),
                        help="comma-separated case names (default: all %d cases)" % len(CASES))
    args = parser.parse_args()
    for key in ("engine_sha256", "addon_sha256"):
        if not re.fullmatch(r"[0-9a-fA-F]{64}", getattr(args, key)):
            parser.error(f"--{key.replace('_', '-')} must be a 64-character SHA-256")
    if args.output.exists():
        parser.error("--output must not already exist")
    if args.seeds_per_case < 1:
        parser.error("--seeds-per-case must be at least 1")
    names = [c[0] for c in CASES]
    args.cases = [c.strip() for c in args.cases.split(",") if c.strip()]
    unknown = [c for c in args.cases if c not in names]
    if unknown or not args.cases or len(set(args.cases)) != len(args.cases):
        parser.error(f"--cases must name distinct cases from: {', '.join(names)}")
    return args


def main() -> int:
    args = parse_args()
    root = find_root()
    packet_benchmarks = HERE
    cases = tuple(c for c in CASES if c[0] in args.cases)
    seeds = tuple(args.seed0 + i for i in range(args.seeds_per_case))
    engine = args.engine.expanduser().resolve(strict=True)
    output = args.output.expanduser().resolve()
    if not (output.is_relative_to(packet_benchmarks) or output.is_relative_to(Path("/tmp"))):
        raise RuntimeError("--output must be a new directory inside this folder or /tmp")
    if output in (packet_benchmarks, Path("/tmp")) or output.exists():
        raise RuntimeError("--output must be a new child directory")
    if not engine.is_file() or not os.access(engine, os.X_OK):
        raise RuntimeError(f"rules4 engine is not an executable file: {engine}")
    python_path = Path(sys.executable).resolve(strict=True)
    if sha256_file(engine).lower() != args.engine_sha256.lower():
        raise RuntimeError("rules4 executable SHA-256 does not match supplied identity")
    deck_paths: dict[str, Path] = {}
    deck_hashes: dict[str, str] = {}
    for name, (rel, expected) in POOL.items():
        path = (root / rel).resolve(strict=True)
        observed = sha256_file(path)
        if observed.lower() != expected:
            raise RuntimeError(f"frozen pool deck changed for {name}: {observed}")
        deck_paths[name] = path
        deck_hashes[name] = observed

    module = importlib.import_module("pdl_rl_env")
    if not callable(getattr(module, "engine_play", None)):
        raise RuntimeError("installed add-on has no callable engine_play")
    module_path = Path(module.__file__).resolve(strict=True)
    addon_name, addon_version = dist_version(module)
    module_hash = sha256_file(module_path)
    if module_hash.lower() != args.addon_sha256.lower() or addon_version != args.addon_version:
        raise RuntimeError("installed add-on module hash/version does not match supplied identity")
    args.engine_version = args.engine_version.strip()
    args.addon_version = args.addon_version.strip()
    if not args.engine_version or not args.addon_version:
        raise RuntimeError("expected engine version cannot be empty")

    before = {"engine_sha256": sha256_file(engine), "module_sha256": sha256_file(module_path),
              "decks": dict(deck_hashes)}
    script_path = Path(__file__).resolve()
    identity = {
        "protocol": "rules3 six-cell CLI/add-on parity protocol plus Altaria v Lucario cells, rules4 (PocketDeckSim)",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(root), "engine_path": str(engine), "engine_sha256": before["engine_sha256"],
        "engine_version_expected": args.engine_version,
        "python_path": str(python_path), "addon_name": addon_name, "addon_version": addon_version,
        "module_path": str(module_path), "module_sha256": before["module_sha256"],
        "decks": {name: {"path": str(deck_paths[name]), "sha256": deck_hashes[name]} for name in POOL},
        "cases": [{"case": case, "deck_order": [a, b], "players": list(players)} for case, a, b, players in cases],
        "seeds": list(seeds), "games_expected": len(cases) * len(seeds),
        "script_path": str(script_path), "script_sha256": sha256_file(script_path),
    }
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / "input_identity.json", identity)
    print(f"Seeds: {seeds[0]:,} to {seeds[-1]:,} for each of {len(cases)} cases ({len(cases) * len(seeds)} games). "
          f"Engine {before['engine_sha256'][:16]}, module {before['module_sha256'][:16]}. Output: {output}", file=sys.stderr, flush=True)
    rows: list[dict[str, Any]] = []
    all_match = True
    for case, deck0, deck1, players in cases:
        for seed in seeds:
            label = f"{case}__seed-{seed}"
            game_dir = output / "cli" / label
            game_dir.mkdir(parents=True, exist_ok=False)
            compact_dir = game_dir / "record"
            compact_dir.mkdir()
            command = [str(engine), "simulate", "--num", "1", "--players", ",".join(players),
                       "--seed", str(seed), "--results-output", str(compact_dir),
                       str(deck_paths[deck0]), str(deck_paths[deck1])]
            row: dict[str, Any] = {"case": case, "seed": seed, "deck_order": [deck0, deck1],
                                   "players": list(players), "command": command}
            try:
                proc = subprocess.run(command, cwd=str(root), capture_output=True, text=True, check=False)
                write_json(game_dir / "command.json", {"argv": command, "cwd": str(root),
                           "return_code": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr})
                if proc.returncode != 0:
                    raise RuntimeError(f"CLI exited {proc.returncode}: {proc.stderr[-2000:]}")
                cli = load_cli_record(compact_dir, seed, args.engine_version)
                addon_w, addon_points, addon_turns = module.engine_play(
                    str(deck_paths[deck0]), str(deck_paths[deck1]), int(seed), tuple(players))
                addon = {"winner": int(addon_w), "points": [int(x) for x in addon_points],
                         "turns": int(addon_turns)}
                row["cli"] = cli
                row["addon"] = addon
                row["matched"] = (cli["winner"], cli["points"], cli["turns"]) == (
                    addon["winner"], addon["points"], addon["turns"])
                all_match = all_match and row["matched"]
            except Exception as exc:
                row["matched"] = False
                row["error"] = f"{type(exc).__name__}: {exc}"
                row["traceback"] = traceback.format_exc(limit=5)
                all_match = False
            rows.append(row)
            with (output / "rows.jsonl").open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(row, sort_keys=True) + "\n")

    after = {"engine_sha256": sha256_file(engine), "module_sha256": sha256_file(module_path),
             "decks": {name: sha256_file(path) for name, path in deck_paths.items()}}
    unchanged = before == after
    summary = {"status": "passed" if all_match and unchanged and len(rows) == len(cases) * len(seeds) else "failed",
               "games_expected": len(cases) * len(seeds), "games_recorded": len(rows),
               "games_matched": sum(bool(row.get("matched")) for row in rows),
               "identity_unchanged": unchanged, "identity_before": before, "identity_after": after,
               "input_identity": "input_identity.json", "rows": rows}
    write_json(output / "summary.json", summary)
    print(json.dumps({k: v for k, v in summary.items() if k != "rows"}, indent=2))
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"REFUSED/FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(2)
