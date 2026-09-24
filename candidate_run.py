#!/usr/bin/env python3
"""Run one manifest-identified DeckGym candidate pairing with durable local evidence."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import uuid


SCHEMA = "pdl-candidate-run/v1"
DEFAULT_GAMES = 2
DEFAULT_PLAYERS = "k3,k3"
MAX_U64 = (1 << 64) - 1
MAX_U32 = (1 << 32) - 1


class Refused(ValueError):
    """An input or identity check failed before the engine was launched."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_file_or_none(path: Path) -> str | None:
    try:
        return sha256_file(path)
    except OSError:
        return None


def is_sha256(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-fA-F]{64}", value) is not None


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_object(data: bytes, path: Path, label: str) -> dict:
    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=unique_object)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise Refused(f"{label} is unreadable or invalid JSON: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise Refused(f"{label} must contain a JSON object: {path}")
    return value


def resolve_manifest_path(root: Path, value: object, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise Refused(f"available_release is missing {label}")
    relative = Path(value)
    if relative.is_absolute():
        raise Refused(f"manifest path {label} must be relative to the project root")
    resolved = (root / relative).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Refused(f"manifest path {label} escapes the project root: {value}") from exc
    return resolved


def positive_games(value: str) -> int:
    try:
        parsed = int(value, 10)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("games must be a positive integer") from exc
    if parsed < 1 or parsed > MAX_U32:
        raise argparse.ArgumentTypeError("games must be between 1 and 4294967295")
    return parsed


def u64_seed(value: str) -> int:
    try:
        parsed = int(value, 10)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("seed must be an unsigned 64-bit integer") from exc
    if parsed < 0 or parsed > MAX_U64:
        raise argparse.ArgumentTypeError("seed must be an unsigned 64-bit integer")
    return parsed


def validate_players(value: str) -> str:
    if not value or any(ord(character) < 32 for character in value):
        raise argparse.ArgumentTypeError("players must be a nonempty printable value")
    return value


def validate_source_manifest(data: bytes, path: Path) -> dict:
    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=unique_object)
    except (UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise Refused(f"source hash manifest is invalid JSON: {path}: {exc}") from exc
    if not isinstance(value, dict) or not value:
        raise Refused(f"source hash manifest must be a nonempty object: {path}")
    for name, digest in value.items():
        if not isinstance(name, str) or not name or not is_sha256(digest):
            raise Refused(f"source hash manifest has an invalid entry: {path}")
    return value


def require_regular_file(path: Path, label: str) -> Path:
    try:
        resolved = path.expanduser().resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise Refused(f"{label} does not exist: {path}") from exc
    if not resolved.is_file():
        raise Refused(f"{label} is not a regular file: {resolved}")
    return resolved


def parse_summary(text: str, games: int) -> dict:
    text = text.replace("\r\n", "\n")
    number = r"[-+]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][-+]?[0-9]+)?"
    count = r"(?:[0-9]{1,3}(?:,[0-9]{3})+|[0-9]+)"
    patterns = {
        "average_turns": rf"^Average number of turns per game:\s*({number})\s*$",
        "average_plys": rf"^Average number of plys per game:\s*({number})\s*$",
        "average_degrees": rf"^Average number of degrees per ply:\s*({number})\s*$",
        "player_0_wins": rf"^Player 0 won:\s*({count})(?:\s+.*)?$",
        "player_1_wins": rf"^Player 1 won:\s*({count})(?:\s+.*)?$",
        "draws": rf"^Draws:\s*({count})(?:\s+.*)?$",
    }
    result = {}
    for key, pattern in patterns.items():
        matches = re.findall(pattern, text, re.MULTILINE)
        if len(matches) != 1:
            raise Refused(f"engine output must contain exactly one {key} summary field")
        token = matches[0].replace(",", "")
        result[key] = int(token) if key.endswith("wins") or key == "draws" else float(token)
        if not math.isfinite(result[key]) or result[key] < 0:
            raise Refused(f"engine output has an invalid {key} value")
    total = result["player_0_wins"] + result["player_1_wins"] + result["draws"]
    if total != games:
        raise Refused(f"engine outcome counts sum to {total}, expected {games}")
    reported = re.findall(rf"^Ran ({count}) simulations\b", text, re.MULTILINE)
    if len(reported) != 1 or int(reported[0].replace(",", "")) != games:
        raise Refused(f"engine output does not report exactly {games} completed simulations")
    return result


def write_new_json(path: Path, value: object) -> None:
    payload = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
    with path.open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def write_new_bytes(path: Path, data: bytes) -> None:
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def safe_error(exc: BaseException) -> str:
    return f"{type(exc).__name__}: {exc}"


def build_plan(args: argparse.Namespace) -> dict:
    if args.seed > MAX_U64 - (args.games - 1):
        raise Refused("seed + games - 1 exceeds the unsigned 64-bit seed range")
    root = args.project_root.expanduser().resolve(strict=True)
    if not root.is_dir():
        raise Refused(f"project root is not a directory: {root}")
    manifest_path = root / "project_manifest.json"
    manifest_bytes = require_regular_file(manifest_path, "project manifest").read_bytes()
    manifest = load_object(manifest_bytes, manifest_path, "project manifest")
    release = manifest.get("available_release")
    if not isinstance(release, dict):
        raise Refused("project manifest has no available_release object")

    release_name = release.get("name")
    if not isinstance(release_name, str) or not release_name:
        raise Refused("available_release has no valid name")
    expected_binary = release.get("sha256")
    expected_source_manifest = release.get("source_sha256_manifest_sha256")
    if not is_sha256(expected_binary) or not is_sha256(expected_source_manifest):
        raise Refused("available_release must record binary and source-manifest SHA-256 values")

    binary_path = resolve_manifest_path(
        root, release.get("artifact", release.get("archive")), "artifact"
    )
    source_manifest_path = resolve_manifest_path(
        root, release.get("source_sha256_manifest"), "source_sha256_manifest"
    )
    catalog_path = resolve_manifest_path(root, manifest.get("card_catalog"), "card_catalog")
    for path, label in (
        (binary_path, "candidate binary"),
        (source_manifest_path, "source hash manifest"),
        (catalog_path, "card catalog"),
    ):
        require_regular_file(path, label)
    if not os.access(binary_path, os.X_OK):
        raise Refused(f"candidate binary is not executable: {binary_path}")

    binary_sha = sha256_file(binary_path)
    if binary_sha.lower() != expected_binary.lower():
        raise Refused(
            f"candidate binary SHA-256 mismatch: expected {expected_binary.lower()}, got {binary_sha}"
        )
    source_manifest_bytes = source_manifest_path.read_bytes()
    source_manifest_sha = sha256_bytes(source_manifest_bytes)
    if source_manifest_sha.lower() != expected_source_manifest.lower():
        raise Refused(
            "source hash manifest SHA-256 mismatch: "
            f"expected {expected_source_manifest.lower()}, got {source_manifest_sha}"
        )
    source_manifest = validate_source_manifest(source_manifest_bytes, source_manifest_path)
    embedded_database_sha = source_manifest.get("database.json")
    if not is_sha256(embedded_database_sha):
        raise Refused("source hash manifest has no valid database.json identity")

    deck_a = require_regular_file(args.deck_a, "deck A")
    deck_b = require_regular_file(args.deck_b, "deck B")
    deck_a_bytes = deck_a.read_bytes()
    deck_b_bytes = deck_b.read_bytes()
    catalog_sha = sha256_file(catalog_path)

    output = args.output.expanduser().resolve()
    results = (root / "results").resolve()
    if output == results or results in output.parents:
        raise Refused("output must not be inside the historical project results directory")
    if output.exists():
        raise Refused(f"output path already exists; refusing to overwrite it: {output}")

    return {
        "root": root,
        "output": output,
        "manifest_path": manifest_path,
        "manifest_bytes": manifest_bytes,
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "release_name": release_name,
        "binary_path": binary_path,
        "binary_sha256": binary_sha,
        "source_manifest_path": source_manifest_path,
        "source_manifest_bytes": source_manifest_bytes,
        "source_manifest_sha256": source_manifest_sha,
        "embedded_database_sha256": embedded_database_sha,
        "catalog_path": catalog_path,
        "catalog_sha256": catalog_sha,
        "deck_a": deck_a,
        "deck_b": deck_b,
        "deck_a_bytes": deck_a_bytes,
        "deck_b_bytes": deck_b_bytes,
    }


def run(args: argparse.Namespace) -> int:
    plan = build_plan(args)
    output = plan["output"]
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        output.mkdir()
    except FileExistsError as exc:
        raise Refused(f"output path appeared during setup; refusing to overwrite it: {output}") from exc

    inputs = output / "inputs"
    inputs.mkdir()
    deck_a_snapshot = inputs / "deck-a.txt"
    deck_b_snapshot = inputs / "deck-b.txt"
    write_new_bytes(deck_a_snapshot, plan["deck_a_bytes"])
    write_new_bytes(deck_b_snapshot, plan["deck_b_bytes"])
    write_new_bytes(inputs / "project_manifest.json", plan["manifest_bytes"])
    write_new_bytes(inputs / "source-sha256.json", plan["source_manifest_bytes"])

    command = [
        str(plan["binary_path"]),
        "simulate",
        "--players",
        args.players,
        "--num",
        str(args.games),
        "--seed",
        str(args.seed),
        "--seed-stream",
        str(deck_a_snapshot),
        str(deck_b_snapshot),
    ]
    started = utc_now()
    identity = {
        "schema": SCHEMA,
        "run_id": str(uuid.uuid4()),
        "started_utc": started,
        "project_root": str(plan["root"]),
        "output_directory": str(output),
        "requested": {
            "games": args.games,
            "players": args.players,
            "seed": args.seed,
            "seed_stream": True,
            "deck_a_origin": str(plan["deck_a"]),
            "deck_b_origin": str(plan["deck_b"]),
        },
        "engine_argv": command,
        "release": {
            "name": plan["release_name"],
            "binary_path": str(plan["binary_path"]),
            "binary_sha256": plan["binary_sha256"],
            "source_manifest_path": str(plan["source_manifest_path"]),
            "source_manifest_sha256": plan["source_manifest_sha256"],
            "embedded_database_sha256_from_source_manifest": plan["embedded_database_sha256"],
            "project_manifest_path": str(plan["manifest_path"]),
            "project_manifest_sha256": plan["manifest_sha256"],
        },
        "inputs": {
            "deck_a": {
                "origin": str(plan["deck_a"]),
                "snapshot": str(deck_a_snapshot.relative_to(output)),
                "sha256": sha256_bytes(plan["deck_a_bytes"]),
            },
            "deck_b": {
                "origin": str(plan["deck_b"]),
                "snapshot": str(deck_b_snapshot.relative_to(output)),
                "sha256": sha256_bytes(plan["deck_b_bytes"]),
            },
        },
        "project_catalog_reference": {
            "path": str(plan["catalog_path"]),
            "sha256": plan["catalog_sha256"],
            "meaning": "project card-resolution catalog; not proof of the binary's embedded database",
        },
        "scope": "development candidate smoke; not runtime activation or gameplay/performance qualification",
    }
    write_new_json(output / "identity.json", identity)

    stdout_path = output / "stdout.txt"
    stderr_path = output / "stderr.txt"
    exit_code = None
    launch_error = None
    start_clock = time.monotonic()
    with stdout_path.open("xb") as stdout_stream, stderr_path.open("xb") as stderr_stream:
        try:
            completed = subprocess.run(
                command,
                cwd=plan["root"],
                stdin=subprocess.DEVNULL,
                stdout=stdout_stream,
                stderr=stderr_stream,
                check=False,
            )
            exit_code = completed.returncode
        except OSError as exc:
            launch_error = safe_error(exc)
            stderr_stream.write((launch_error + "\n").encode("utf-8", errors="replace"))
        finally:
            stdout_stream.flush()
            stderr_stream.flush()
            os.fsync(stdout_stream.fileno())
            os.fsync(stderr_stream.fileno())

    failure = None
    summary = None
    if launch_error is not None:
        failure = "engine launch failed"
    elif exit_code != 0:
        failure = f"engine exited with status {exit_code}"
    else:
        combined = stdout_path.read_text(encoding="utf-8", errors="replace") + "\n" + stderr_path.read_text(
            encoding="utf-8", errors="replace"
        )
        try:
            summary = parse_summary(combined, args.games)
        except Refused as exc:
            failure = str(exc)

    after = {
        "binary_sha256": sha256_file_or_none(plan["binary_path"]),
        "source_manifest_sha256": sha256_file_or_none(plan["source_manifest_path"]),
        "catalog_sha256": sha256_file_or_none(plan["catalog_path"]),
        "deck_a_snapshot_sha256": sha256_file_or_none(deck_a_snapshot),
        "deck_b_snapshot_sha256": sha256_file_or_none(deck_b_snapshot),
    }
    expected_after = {
        "binary_sha256": plan["binary_sha256"],
        "source_manifest_sha256": plan["source_manifest_sha256"],
        "catalog_sha256": plan["catalog_sha256"],
        "deck_a_snapshot_sha256": sha256_bytes(plan["deck_a_bytes"]),
        "deck_b_snapshot_sha256": sha256_bytes(plan["deck_b_bytes"]),
    }
    if after != expected_after:
        failure = "a verified release/catalog or snapshotted deck input changed during the run"

    completion = {
        "schema": SCHEMA,
        "run_id": identity["run_id"],
        "status": "succeeded" if failure is None else "failed",
        "exit_code": exit_code,
        "failure": failure,
        "launch_error": launch_error,
        "started_utc": started,
        "finished_utc": utc_now(),
        "duration_seconds": round(time.monotonic() - start_clock, 6),
        "summary": summary,
        "stdout": {
            "path": "stdout.txt",
            "bytes": stdout_path.stat().st_size,
            "sha256": sha256_file(stdout_path),
        },
        "stderr": {
            "path": "stderr.txt",
            "bytes": stderr_path.stat().st_size,
            "sha256": sha256_file(stderr_path),
        },
        "post_run_hashes": after,
    }
    write_new_json(output / "completion.json", completion)
    if failure is not None:
        print(f"FAILED candidate run: {failure}; evidence: {output}", file=sys.stderr)
        return 1
    print(f"Completed candidate run {identity['run_id']}: {output}")
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("deck_a", type=Path, help="first complete deck file")
    result.add_argument("deck_b", type=Path, help="second complete deck file")
    result.add_argument("--output", type=Path, required=True, help="new output directory")
    result.add_argument("--games", type=positive_games, default=DEFAULT_GAMES)
    result.add_argument("--players", type=validate_players, default=DEFAULT_PLAYERS)
    result.add_argument("--seed", type=u64_seed, default=0)
    result.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="project containing project_manifest.json (defaults beside this script)",
    )
    return result


def main(argv: list[str] | None = None) -> int:
    try:
        return run(parser().parse_args(argv))
    except Refused as exc:
        print(f"REFUSED candidate run: {exc}", file=sys.stderr)
        return 2
    except (OSError, KeyError, TypeError) as exc:
        print(f"REFUSED candidate run: {safe_error(exc)}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
