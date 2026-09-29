#!/usr/bin/env python3
"""A3 per-game calibration: does the simulator's win chance for the exact pair Dustin played
(his list against the opponent's archetype list) say anything about whether he won?

usage (Windows or Linux python 3, standard library only):
  python calibrate.py --sim sim_results.csv [--games calibration_games.csv] [--pilot kp3]
                      [--draws loss|half|drop] [--clip 0.02] [--boot 10000] [--seed 1]
                      [--json report.json] [--strict] [--quiet] [--accept-unverified] [--repo-root DIR]

sim CSV (what run_calibration.py writes, see calibration_README.md): columns deck_file, opponent_file,
pilot, games, wins; optional draws and seat. Paths are relative to the repo root as written in
calibration_games.csv (either slash, case ignored; a bare file name also matches, with a warning, but only a row that has
no provenance: a row with provenance must match on the whole path).
seat: blank or "any" = pooled over who moved first (the normal case); "first" / "second" = the
sim's win chance when Dustin's deck moved first / second, used only for the games whose
went_first is known in calibration_games.csv. Rows with the same key are summed, so a runner
may append chunks. Extra columns are ignored.

Provenance (added Sept 29). run_calibration.py records, for every row, the engine hash, the sha256 of
the deck and opponent files (line endings normalised), both pilots, the game counts per slot and the
seeds. Before anything is scored the rows of the chosen pilot are checked as a set, and the scorer
REFUSES, naming every problem, if:
  - two rows for one pair share simulated seeds (the same games would be counted twice), or several
    rows for one pair carry no seeds (chunks cannot be told from repeats);
  - rows for one pair disagree on engine, deck or opponent contents, or pilots, or the rows come from
    more than one engine build;
  - slot game/win/draw counts do not add up, the pilot column contradicts deck_pilot/meta_pilot, or
    slot 0's seeds run into slot 1's;
  - a recorded deck or opponent hash no longer matches the file under --repo-root (files that are not
    there are reported, not failed);
  - a games/wins/draws/seed field is not a whole number (12.7, inf, nan), or a row is ragged.
A file, or rows, without this provenance (older runs, hand-made files) are NOT treated as verified: they
are refused unless --accept-unverified is given, and then the report, the JSON ("provenance") and the
--quiet line all say "unverified". The report also states whether the rows' pilot is the project's
working pilot (read from run_screen.py and floor.py) and says so loudly if it is not.

Details that decide "verified": a hash must be 64 hex characters (compared in lower case; 'TBD', 'n/a' or a cut hash is a
placeholder, not provenance), a pilot must be a plain name, a seed at most 2^64-1, slot wins + draws within the slot's games,
and a row the runner wrote keeps to its layout (5,000 seeds a slot, 10,000 a pair). One file recorded with two contents
anywhere in the rows is refused whether or not the files are present. The re-check finds a recorded path the way norm_path
matches it (either slash, './', '//', '..', case ignored: 'Decks/D0.txt' finds decks/d0.txt on a case-sensitive disk); two
files that differ only in case are refused as ambiguous. A verified row is matched to a game by the whole normalised path,
never by bare file name (that fallback is for hand-made rows only). A blank pilot column, a result other than W or L, a
non-numeric or absurd number, a ragged row, an unreadable or non-UTF-8 file, and --json pointing at an input all refuse
cleanly, and every refusal comes before any score is printed or --json is written. A byte-order mark is accepted.

What it reports, over the games that have a deck file and a sim row:
  - the Brier score of the sim's win chance: the average of (p - result)^2 with result 1 for a
    win and 0 for a loss; 0 is perfect, 0.25 is a coin, lower is better;
  - the Brier score of the constant base rate (Dustin's win rate over the same games), both
    in-sample and leave-one-out, and of the coin (0.5);
  - a skill score, 1 - Brier(sim) / Brier(base): 0 means no better than the base rate;
  - the log-likelihood ratio, sim against the base rate, in nats and bits (p clipped away from
    0 and 1 by --clip so one confident miss cannot dominate);
  - a paired bootstrap over games: the games are resampled with replacement, the per-game
    paired differences are recomputed, and 90% and 95% percentile intervals are printed with
    the share of resamples in which the sim came out ahead;
  - a reliability table (sim chance bins against the observed win rate) and every game.
A positive Brier difference (base minus sim) and a positive LLR mean the sim beat the base rate
on these games. Read calibration_README.md for what that does and does not mean at this size.
"""
import argparse
import ast
import csv
import hashlib
import json
import math
import os
import posixpath
import random
import re
import sys
from collections import defaultdict
from decimal import Decimal, InvalidOperation

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_GAMES = os.path.join(HERE, "calibration_games.csv")
SCREEN_DIR = os.path.dirname(HERE)                        # decks/screen: run_screen.py and floor.py name the working pilot
REPO_ROOT = os.path.dirname(os.path.dirname(SCREEN_DIR))
SEATS = ("any", "first", "second")

# What run_calibration.py records so that a row can be checked later (shared by both scripts). A row is "verified" only
# with this schema and every REQUIRED_PROVENANCE field; anything else is "unverified" and needs --accept-unverified.
PROVENANCE_SCHEMA = "1"
REQUIRED_PROVENANCE = ("engine_sha256", "deck_sha256", "opponent_sha256", "deck_pilot", "meta_pilot",
                       "seed_slot0", "seed_slot1", "slot0_games", "slot1_games",
                       "slot0_wins", "slot1_wins", "slot0_draws", "slot1_draws")
HASH_FIELDS = ("engine_sha256", "deck_sha256", "opponent_sha256")
SHA_RE = re.compile(r"[0-9a-f]{64}")     # hashes are compared in lower case; anything else is a placeholder, not provenance
NAME_RE = re.compile(r"[A-Za-z0-9_]+")   # a pilot name, as run_screen.py and floor.py write them
U64 = 2 ** 64 - 1                        # the largest seed the engine can be given
# The reserved seed layout (START_HERE's seed table): pair i owns 10,000 seeds from seed + i*10,000; slot 0 uses the first
# 5,000 of them and slot 1 the second 5,000; one run reserves 200,000 seeds, that is 20 pairs.
PAIR_SPACING = 10_000
SLOT_SPACING = 5_000
RESERVED_SEEDS = 200_000


# ---------------------------------------------------------------- input


def norm_path(p):
    """The key two spellings of one path share: either slash, './', '//', '/./', '..' and a trailing '/' collapsed, case ignored."""
    p = (p or "").strip().replace("\\", "/")
    return posixpath.normpath(p).lower() if p else p


def strict_int(text, what):
    """A whole number written as text ("500", "500.0", " 12 "); 12.7, inf, nan, empty or absurdly large (1e400, 5,000 digits)
    raise ValueError, never a silent cut, a traceback or a hang."""
    s = (text or "").strip()
    if len(s) > 60:
        raise ValueError(f"{what} is too long to be a number ({len(s)} characters)")
    try:
        d = Decimal(s)
    except InvalidOperation:
        raise ValueError(f"{what} is not a number: {s!r}")
    if not d.is_finite() or d != d.to_integral_value():
        raise ValueError(f"{what} is not a whole number: {s!r}")
    if d.adjusted() > 30:
        raise ValueError(f"{what} is too large to be a game count or a seed: {s!r}")
    return int(d)


def locate_file(root, rel):
    """The file a recorded path names under root, found the way norm_path matches paths (case ignored, so 'Decks/D0.txt' finds
    decks/d0.txt on a case-sensitive disk). Returns (path, None), (None, "missing") or (None, "ambiguous")."""
    rel = (rel or "").strip().replace("\\", "/")
    if not rel:
        return None, "missing"
    cur = "/" if rel.startswith("/") else root
    for part in [p for p in posixpath.normpath(rel).split("/") if p not in ("", ".")]:
        exact = os.path.join(cur, part)
        if os.path.exists(exact):
            cur = exact
            continue
        try:
            hits = [n for n in os.listdir(cur) if n.lower() == part.lower()]
        except OSError:
            return None, "missing"
        if not hits:
            return None, "missing"
        if len(hits) > 1:
            return None, "ambiguous"
        cur = os.path.join(cur, hits[0])
    return (cur, None) if os.path.isfile(cur) else (None, "missing")


def to_int(row, col, path, line):
    try:
        return strict_int(row.get(col), f"column {col}")
    except ValueError as e:
        raise SystemExit(f"{path} line {line}: {e}")


def file_sha256(path):
    """sha256 of a text file with line endings normalised to LF, so a Windows and a Linux checkout of one list agree."""
    with open(path, "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()


def working_pilot(screen_dir=None):
    """The pilot the project runs on both sides of its screens: (pilot, sources). Read from run_screen.py's --pilot and
    --meta-pilot defaults and floor.py's FLOOR_PILOT by parsing the Python (not by searching the text, so a commented-out line,
    a docstring example or an older assignment cannot confirm the wrong pilot); ValueError if one is unreadable, unparseable,
    not a plain pilot name, or they disagree."""
    d = screen_dir or SCREEN_DIR

    def parse(name):
        try:
            with open(os.path.join(d, name), encoding="utf-8-sig") as f:
                return ast.parse(f.read(), name)
        except OSError as e:
            raise ValueError(f"cannot read {name}: {e}")
        except (SyntaxError, ValueError) as e:
            raise ValueError(f"cannot parse {name}: {e}")

    screen, floor = parse("run_screen.py"), parse("floor.py")
    consts = {}                                 # module-level NAME = "text" in run_screen.py (the last one wins)
    for node in screen.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            consts.update({t.id: node.value.value for t in node.targets if isinstance(t, ast.Name)})

    def literal(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        return consts.get(node.id) if isinstance(node, ast.Name) else None

    found = {}
    for flag in ("--pilot", "--meta-pilot"):
        vals = []
        for node in ast.walk(screen):
            if isinstance(node, ast.Call) and getattr(node.func, "attr", None) == "add_argument" \
                    and any(isinstance(a, ast.Constant) and a.value == flag for a in node.args):
                vals += [literal(kw.value) for kw in node.keywords if kw.arg == "default" and literal(kw.value) is not None]
        if not vals:
            raise ValueError(f"run_screen.py has no default for {flag}")
        if len(set(vals)) > 1:
            raise ValueError(f"run_screen.py gives {flag} several different defaults: {sorted(set(vals))}")
        found[f"run_screen.py {flag}"] = vals[0]
    last, unreadable = None, None
    for node in floor.body:                     # the last module-level statement about FLOOR_PILOT wins, as it does when Python runs the file
        hit, value = False, None
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "FLOOR_PILOT" for t in node.targets):
            hit, value = True, node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "FLOOR_PILOT" \
                and node.value is not None:
            hit, value = True, node.value
        elif (isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name) and node.target.id == "FLOOR_PILOT") \
                or (isinstance(node, ast.Delete) and any(isinstance(t, ast.Name) and t.id == "FLOOR_PILOT" for t in node.targets)):
            last, unreadable = None, "an augmented assignment or a delete"
            continue
        if hit:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                last, unreadable = value.value, None
            else:
                last, unreadable = None, "a value that is not a plain string"
    if unreadable:
        raise ValueError(f"floor.py's last change to FLOOR_PILOT is {unreadable}, so its value cannot be read without running it")
    if last is None:
        raise ValueError("floor.py has no FLOOR_PILOT")
    found["floor.py FLOOR_PILOT"] = last
    for k, v in found.items():
        if not NAME_RE.fullmatch(v):
            raise ValueError(f"{k} = {v!r} is not a plain pilot name")
    if len(set(found.values())) != 1:
        raise ValueError("the screen and the floor disagree on the working pilot: " + ", ".join(f"{k} = {v}" for k, v in found.items()))
    return next(iter(found.values())), found


def read_games(path):
    """The usable rows of calibration_games.csv (deck file present) as dicts. A result other than W or L is refused, not
    scored as a loss."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        header = list(reader.fieldnames or [])
        rows = []
        for r in reader:
            if None in r or any(v is None for v in r.values()):
                raise SystemExit(f"{path} line {reader.line_num}: the row has a different number of fields than the header")
            rows.append((reader.line_num, r))
    need = {"game_id", "deck_file", "opponent_file", "result", "usable"}
    missing = need - set(header)
    if missing:
        raise SystemExit(f"{path}: missing columns {sorted(missing)}")
    games, skipped = [], []
    for line, r in rows:
        if r["usable"].strip() != "1" or not r["deck_file"].strip():
            skipped.append(r)
            continue
        if r["result"].strip().upper() not in ("W", "L"):
            raise SystemExit(f"{path} line {line}: the result is {r['result']!r}, not W or L; a blank or odd result would be "
                             f"scored as a loss")
        wf = (r.get("went_first") or "").strip()
        games.append({
            "game_id": r["game_id"],
            "date": r.get("date", ""),
            "deck_id": r.get("deck_id", ""),
            "deck_file": r["deck_file"].strip(),
            "opponent_file": r["opponent_file"].strip(),
            "opponent_key": r.get("opponent_key", ""),
            "list_match": r.get("list_match", ""),
            "went_first": {"1": "first", "0": "second"}.get(wf),
            "y": 1 if r["result"].strip().upper() == "W" else 0,
        })
    return games, skipped


OPTIONAL_INTS = ("seed_slot0", "seed_slot1", "slot0_games", "slot1_games",
                 "slot0_wins", "slot1_wins", "slot0_draws", "slot1_draws")
PROVENANCE_TEXT = ("schema", "engine", "engine_sha256", "deck_sha256", "opponent_sha256", "deck_pilot", "meta_pilot")


def parse_sim_rows(path):
    """Every row of a sim CSV as a dict (whole numbers checked, ragged rows refused). Nothing is combined here."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        cols = list(reader.fieldnames or [])
        need = {"deck_file", "opponent_file", "pilot", "games", "wins"}
        if need - set(cols):
            raise SystemExit(f"{path}: missing columns {sorted(need - set(cols))} (has {sorted(cols)})")
        rows = []
        for r in reader:
            i = reader.line_num          # the real line, not the row count: blank lines are skipped by the reader
            if None in r:
                raise SystemExit(f"{path} line {i}: {len(cols) + len(r[None])} fields under a header of {len(cols)} columns "
                                 f"(a row written under another file's header?)")
            if any(v is None for v in r.values()):
                raise SystemExit(f"{path} line {i}: fewer fields than the header's {len(cols)} columns (a cut or misaligned row?)")
            if (r.get("deck_file") or "").strip() == "deck_file" and (r.get("games") or "").strip() == "games":
                raise SystemExit(f"{path} line {i}: this line repeats the header (two files joined end to end?)")
            seat = (r.get("seat") or "").strip().lower() or "any"
            if seat == "pooled":
                seat = "any"
            if seat not in SEATS:
                raise SystemExit(f"{path} line {i}: seat must be blank, any, first or second, not {seat!r}")
            pilot = (r["pilot"] or "").strip()
            if not pilot:
                raise SystemExit(f"{path} line {i}: the pilot column is empty")
            g, w = to_int(r, "games", path, i), to_int(r, "wins", path, i)
            d = to_int(r, "draws", path, i) if "draws" in cols and (r.get("draws") or "").strip() else 0
            if g <= 0 or w < 0 or d < 0 or w + d > g:
                raise SystemExit(f"{path} line {i}: games={g} wins={w} draws={d} do not make sense")
            opt = {}
            for c in OPTIONAL_INTS:
                opt[c] = to_int(r, c, path, i) if (r.get(c) or "").strip() else None
                if opt[c] is not None and opt[c] < 0:
                    raise SystemExit(f"{path} line {i}: column {c} is negative")
                if c.startswith("seed") and opt[c] is not None and opt[c] > U64:
                    raise SystemExit(f"{path} line {i}: column {c} is above {U64:,}, the largest seed the engine takes")
            prov = {c: (r.get(c) or "").strip() for c in PROVENANCE_TEXT}
            for c in HASH_FIELDS:
                prov[c] = prov[c].lower()
            prov.update({c: "" if opt[c] is None else str(opt[c]) for c in OPTIONAL_INTS})
            iv = []  # the simulated seeds this row used, as half-open intervals
            if opt["seed_slot0"] is not None and opt["slot0_games"]:
                iv.append((opt["seed_slot0"], opt["seed_slot0"] + opt["slot0_games"], "slot 0"))
            if opt["seed_slot1"] is not None and opt["slot1_games"]:
                iv.append((opt["seed_slot1"], opt["seed_slot1"] + opt["slot1_games"], "slot 1"))
            rows.append({"line": i, "deck": (r["deck_file"] or "").strip(), "opp": (r["opponent_file"] or "").strip(),
                         "pilot": pilot, "seat": seat, "games": g, "wins": w, "draws": d, "prov": prov, "opt": opt, "iv": iv})
    return rows


def record_level(row):
    """("verified", []) or ("unverified", [why, ...]): only a row with the provenance schema and every required field is verified."""
    p = row["prov"]
    why = []
    if p.get("schema", "") != PROVENANCE_SCHEMA:
        why.append("no provenance schema (an older or hand-made row)" if not p.get("schema")
                   else f"unknown provenance schema {p['schema']!r}")
    missing = [f for f in REQUIRED_PROVENANCE if not p.get(f, "")]
    if missing:
        why.append("missing " + ", ".join(missing))
    for f in HASH_FIELDS:                                   # placeholders ('TBD', 'n/a', a cut hash) are not provenance
        if p.get(f, "") and not SHA_RE.fullmatch(p[f]):
            why.append(f"{f} {p[f][:16]!r} is not a 64-character sha256")
    for f in ("deck_pilot", "meta_pilot"):
        if p.get(f, "") and not NAME_RE.fullmatch(p[f]):
            why.append(f"{f} {p[f]!r} is not a pilot name")
    return ("unverified" if why else "verified"), why


def _overlap(a, b):
    return a[0] < b[1] and b[0] < a[1]


def _lines(rows, limit=10):
    return ", ".join(str(r["line"]) for r in rows[:limit]) + ("..." if len(rows) > limit else "")


def _short(x):
    return x[:12] + "..." if len(x) > 12 else x


def format_problems(source, errs, action, limit=25):
    body = [f"REFUSED: {len(errs)} problem{'s' if len(errs) != 1 else ''} in {source}; {action}:"]
    body += [f"  - {e}" for e in errs[:limit]]
    if len(errs) > limit:
        body.append(f"  ... and {len(errs) - limit} more")
    return "\n".join(body)


def find_problems(rows, repo_root=None, accept_unverified=False):
    """Everything wrong with these rows (ONE pilot's) taken as a set: (problems, summary). Sets each row's "level" and "why"."""
    errs, unverified = [], []
    for r in rows:
        r["level"], r["why"] = record_level(r)
        if r["level"] == "unverified":
            unverified.append(r)
        p, o, tag = r["prov"], r["opt"], f"line {r['line']}"
        for a, b, total, what in (("slot0_games", "slot1_games", r["games"], "games"), ("slot0_wins", "slot1_wins", r["wins"], "wins"),
                                  ("slot0_draws", "slot1_draws", r["draws"], "draws")):
            if o[a] is not None and o[b] is not None and o[a] + o[b] != total:
                errs.append(f"{tag}: {a} {o[a]} + {b} {o[b]} do not add up to {what} {total}")
        if p["deck_pilot"] and p["meta_pilot"]:
            want = p["deck_pilot"] if p["deck_pilot"] == p["meta_pilot"] else f"{p['deck_pilot']}|{p['meta_pilot']}"
            if want != r["pilot"]:
                errs.append(f"{tag}: the pilot column says {r['pilot']!r} but deck_pilot is {p['deck_pilot']!r} and meta_pilot "
                            f"{p['meta_pilot']!r} (that is {want!r})")
        if len(r["iv"]) == 2 and _overlap(r["iv"][0], r["iv"][1]):
            errs.append(f"{tag}: slot 0 seeds {r['iv'][0][0]:,}..{r['iv'][0][1] - 1:,} run into slot 1 seeds "
                        f"{r['iv'][1][0]:,}..{r['iv'][1][1] - 1:,} (a slot overflowed its reserved spacing)")
        for s in ("0", "1"):
            n_g, n_w, n_d = o[f"slot{s}_games"], o[f"slot{s}_wins"], o[f"slot{s}_draws"]
            if n_g is not None and (n_w or 0) + (n_d or 0) > n_g:
                errs.append(f"{tag}: slot {s} shows {n_w or 0} wins and {n_d or 0} draws in {n_g} games")
        if p.get("schema") == PROVENANCE_SCHEMA:            # rows the runner wrote keep to its layout: 5,000 seeds a slot, 10,000 a pair
            for s in ("0", "1"):
                if o[f"slot{s}_games"] is not None and o[f"slot{s}_games"] > SLOT_SPACING:
                    errs.append(f"{tag}: slot {s} played {o[f'slot{s}_games']:,} games, more than the {SLOT_SPACING:,} seeds reserved per slot")
            if o["seed_slot0"] is not None and o["seed_slot1"] is not None and o["slot1_games"] is not None \
                    and o["seed_slot1"] + o["slot1_games"] > o["seed_slot0"] + PAIR_SPACING:
                errs.append(f"{tag}: slot 1 seeds run past the pair's {PAIR_SPACING:,}-seed block (into the next pair's seeds)")
            if o["slot0_games"] is not None and o["slot1_games"] is not None \
                    and (o["slot0_games"], o["slot1_games"]) != (r["games"] // 2, r["games"] - r["games"] // 2):
                errs.append(f"{tag}: the slots hold {o['slot0_games']:,} and {o['slot1_games']:,} games, but the runner splits "
                            f"{r['games']:,} games as {r['games'] // 2:,} and {r['games'] - r['games'] // 2:,}")
            if o["seed_slot0"] is not None and o["seed_slot1"] is not None and o["seed_slot1"] != o["seed_slot0"] + SLOT_SPACING:
                errs.append(f"{tag}: slot 1 seeds start at {o['seed_slot1']:,}, not {SLOT_SPACING:,} after slot 0's "
                            f"({o['seed_slot0'] + SLOT_SPACING:,}), which is where every row the runner writes puts them")
            for s in ("0", "1"):
                if o[f"seed_slot{s}"] is not None and o[f"slot{s}_games"] and o[f"seed_slot{s}"] + o[f"slot{s}_games"] - 1 > U64:
                    errs.append(f"{tag}: slot {s} seeds run past {U64:,}, the largest seed the engine takes")

    groups = defaultdict(list)
    for r in rows:
        groups[(norm_path(r["deck"]), norm_path(r["opp"]), r["pilot"], r["seat"])].append(r)
    unseeded_repeats = []
    for rs in groups.values():
        if len(rs) < 2:
            continue
        name = f"{os.path.basename(rs[0]['deck'])} vs {os.path.basename(rs[0]['opp'])}"
        for f in ("engine_sha256", "deck_sha256", "opponent_sha256", "deck_pilot", "meta_pilot"):
            vals = [r["prov"].get(f, "") for r in rs]
            present = sorted({v for v in vals if v})
            if len(present) > 1:
                errs.append(f"{name} (lines {_lines(rs)}): rows disagree on {f} ({', '.join(_short(x) for x in present)}); "
                            f"rows from different runs cannot be combined")
            elif present and "" in vals:
                errs.append(f"{name} (lines {_lines(rs)}): {f} is recorded in some rows and blank in others; cannot tell "
                            f"whether they come from one run")
        seeded, unseeded = [r for r in rs if r["iv"]], [r for r in rs if not r["iv"]]
        first_seen = {}
        for r in unseeded:      # an exact repeat of a row that carries no seeds is a duplicate whatever anyone accepts
            sig = (r["games"], r["wins"], r["draws"], tuple(sorted(r["prov"].items())))
            if sig in first_seen:
                errs.append(f"{name}: lines {first_seen[sig]} and {r['line']} are identical and carry no seeds: the same row "
                            f"repeated would be counted twice (remove one, or give both seeds if they are different games)")
            else:
                first_seen[sig] = r["line"]
        if unseeded:
            unseeded_repeats.append(f"{name} (lines {_lines(rs)})")
            if not accept_unverified:
                errs.append(f"{name} (lines {_lines(rs)}): {len(rs)} rows for one pair and lines {_lines(unseeded)} carry no seeds, "
                            f"so chunks cannot be told from repeats of the same games (double counting); give every row "
                            f"seed_slot0/seed_slot1 and slot game counts, or pass --accept-unverified")
        reported = set()
        for x in range(len(seeded)):
            for y in range(x + 1, len(seeded)):
                for ia in seeded[x]["iv"]:
                    for ib in seeded[y]["iv"]:
                        pair = (seeded[x]["line"], seeded[y]["line"])
                        if _overlap(ia, ib) and pair not in reported:
                            reported.add(pair)
                            errs.append(f"{name}: lines {pair[0]} and {pair[1]} share simulated seeds {max(ia[0], ib[0]):,} to "
                                        f"{min(ia[1], ib[1]) - 1:,} (same pair, same pilot): the same games would be counted twice")

    by_engine = defaultdict(list)
    for r in rows:
        if r["prov"].get("engine_sha256"):
            by_engine[r["prov"]["engine_sha256"]].append(r)
    if len(by_engine) > 1:
        errs.append(f"the rows come from {len(by_engine)} different engine builds ("
                    + "; ".join(f"{_short(e)} at lines {_lines(rs, 5)}" for e, rs in sorted(by_engine.items()))
                    + "); results from different engines cannot be combined")

    by_file = defaultdict(lambda: defaultdict(list))        # one file recorded with two contents anywhere in the rows
    for r in rows:
        for path_key, hash_key in (("deck", "deck_sha256"), ("opp", "opponent_sha256")):
            if r["prov"].get(hash_key, ""):
                by_file[norm_path(r[path_key])][r["prov"][hash_key]].append(r)
    for path, hs in sorted(by_file.items()):
        if len(hs) > 1:
            every = sorted((r for lst in hs.values() for r in lst), key=lambda r: r["line"])
            errs.append(f"{path} is recorded with {len(hs)} different contents ({', '.join(_short(h) for h in sorted(hs))}) at lines "
                        f"{_lines(every)}; rows from different runs cannot be combined")

    rechecked, not_rechecked, seen = 0, [], set()
    if repo_root:
        for r in rows:
            for kind, path_key, hash_key in (("deck", "deck", "deck_sha256"), ("opponent", "opp", "opponent_sha256")):
                want, rel = r["prov"].get(hash_key, ""), r[path_key]
                if not SHA_RE.fullmatch(want) or (norm_path(rel), want) in seen:
                    continue                                 # a placeholder hash is already reported as unverified
                seen.add((norm_path(rel), want))
                full, why_not = locate_file(repo_root, rel)
                if full is None:
                    if why_not == "ambiguous":
                        errs.append(f"line {r['line']}: the {kind} path {rel} matches two files that differ only in case; "
                                    f"cannot tell which one was played")
                    elif rel not in not_rechecked:
                        not_rechecked.append(rel)
                    continue
                try:
                    have = file_sha256(full)
                except OSError as e:
                    errs.append(f"line {r['line']}: cannot read the {kind} file {rel} to re-check it ({e.strerror or e})")
                    continue
                if have != want:
                    errs.append(f"line {r['line']}: the {kind} file {rel} has changed since this row was written "
                                f"(recorded sha256 {_short(want)}, the file is now {_short(have)})")
                else:
                    rechecked += 1

    if unverified and not accept_unverified:
        reasons = sorted({w for r in unverified for w in r["why"]})
        errs.append(f"{len(unverified)} of {len(rows)} rows have no verifiable provenance (lines {_lines(unverified)}): "
                    + "; ".join(reasons) + ". Their engine, deck contents, pilots and seeds cannot be checked. To score them "
                    "as they are, say so with --accept-unverified (the report and the JSON will then label the scores unverified)")
    summary = {"level": "unverified" if unverified else "verified", "rows": len(rows),
               "verified_rows": len(rows) - len(unverified), "unverified_rows": len(unverified),
               "unverified_lines": [r["line"] for r in unverified],
               "unverified_reasons": sorted({w for r in unverified for w in r["why"]}),
               "accepted_unverified": bool(unverified and accept_unverified),
               "unseeded_repeats": unseeded_repeats,
               "engine_sha256": sorted(by_engine), "content_files_rechecked": rechecked, "content_not_rechecked": not_rechecked}
    return errs, summary


def check_records(rows, repo_root=None, accept_unverified=False, source="the sim file"):
    """find_problems, refusing (SystemExit naming every problem) before anything is scored; returns the summary."""
    errs, summary = find_problems(rows, repo_root, accept_unverified)
    if errs:
        raise SystemExit(format_problems(source, errs, "nothing was scored"))
    return summary


def sim_from_rows(rows, draws_mode):
    """sim rows keyed by (deck, opponent, pilot, seat); rows with one key are summed (call check_records first)."""
    acc = defaultdict(lambda: [0, 0, 0, True])  # games, wins, draws, every contributing row verified
    for r in rows:
        a = acc[(norm_path(r["deck"]), norm_path(r["opp"]), r["pilot"], r["seat"])]
        a[0] += r["games"]
        a[1] += r["wins"]
        a[2] += r["draws"]
        a[3] = a[3] and r.get("level") == "verified"
    sim = {}
    for key, (g, w, d, ok) in acc.items():
        if draws_mode == "loss":
            p = w / g
        elif draws_mode == "half":
            p = (w + 0.5 * d) / g
        else:  # drop
            if g - d <= 0:
                raise SystemExit(f"sim row {key}: every game was a draw, cannot drop draws")
            p = w / (g - d)
        sim[key] = {"p": p, "games": g, "wins": w, "draws": d, "verified": ok}
    return sim


def read_sim(path, draws_mode, wanted_pilot=None, accept_unverified=False, repo_root=None):
    """One pilot's sim rows, checked as a set and then combined per pair: (sim, pilot, provenance summary)."""
    every = parse_sim_rows(path)
    pilot = choose_pilot(sorted({r["pilot"] for r in every}), wanted_pilot)
    rows = [r for r in every if r["pilot"] == pilot]
    prov = check_records(rows, repo_root=repo_root, accept_unverified=accept_unverified, source=f"{path} (pilot {pilot})")
    prov["other_pilot_rows"] = len(every) - len(rows)      # not checked: they are not part of this score
    return sim_from_rows(rows, draws_mode), pilot, prov


def choose_pilot(pilots, wanted):
    if not pilots:
        raise SystemExit("the sim file has no rows")
    if wanted:
        if wanted not in pilots:
            raise SystemExit(f"--pilot {wanted!r} is not in the sim file (it has {pilots})")
        return wanted
    if len(pilots) == 1:
        return pilots[0]
    raise SystemExit(f"the sim file has several pilots {pilots}; pass --pilot")


def join(games, sim, pilot, warn, used=None):
    """Attach a sim win chance to every game it can; return (matched, missing_pairs). A bare file name may match a sim row only
    when that row has no provenance (a hand-made file): a verified row must match on the whole normalised path, because a
    file name alone can name a different deck. `used`, if given, collects the sim keys that were joined to a game."""
    by_base = defaultdict(list)
    for key in sim:
        if key[2] == pilot and not sim[key]["verified"]:
            by_base[(os.path.basename(key[0]), os.path.basename(key[1]), key[3])].append(key)
    warned = set()
    used = used if used is not None else set()

    def lookup(deck, opp, seat):
        key = (norm_path(deck), norm_path(opp), pilot, seat)
        if key in sim:
            used.add(key)
            return sim[key]
        cands = by_base.get((os.path.basename(key[0]), os.path.basename(key[1]), seat), [])
        if len(cands) == 1:
            if cands[0] not in warned:
                warned.add(cands[0])
                warn(f"note: matched {deck} vs {opp} by file name to sim row {cands[0][0]} vs {cands[0][1]}")
            used.add(cands[0])
            return sim[cands[0]]
        if len(cands) > 1:
            raise SystemExit(f"REFUSED: ambiguous sim rows for {deck} vs {opp}: "
                             + "; ".join(f"{k[0]} vs {k[1]}" for k in cands) + " (several rows share this file name; nothing was scored)")
        return None

    matched, missing = [], {}
    for g in games:
        row, used_seat = None, "any"
        if g["went_first"]:
            row = lookup(g["deck_file"], g["opponent_file"], g["went_first"])
            if row:
                used_seat = g["went_first"]
        if row is None:
            row = lookup(g["deck_file"], g["opponent_file"], "any")
        if row is None:
            missing.setdefault((g["deck_file"], g["opponent_file"]), 0)
            missing[(g["deck_file"], g["opponent_file"])] += 1
            continue
        matched.append(dict(g, p=row["p"], sim_games=row["games"], sim_wins=row["wins"],
                            sim_draws=row["draws"], sim_verified=row["verified"], seat_used=used_seat))
    return matched, missing


# ---------------------------------------------------------------- scoring


def clip(p, c):
    return min(max(p, c), 1.0 - c)


def brier(ps, ys):
    return sum((p - y) ** 2 for p, y in zip(ps, ys)) / len(ys)


def loglik(ps, ys, c):
    s = 0.0
    for p, y in zip(ps, ys):
        q = clip(p, c)
        s += math.log(q if y else 1.0 - q)
    return s


def percentile(sorted_vals, q):
    if not sorted_vals:
        return float("nan")
    k = (len(sorted_vals) - 1) * q
    f = math.floor(k)
    c = min(f + 1, len(sorted_vals) - 1)
    return sorted_vals[f] + (sorted_vals[c] - sorted_vals[f]) * (k - f)


def bootstrap(terms, boot, seed, agg):
    """Paired bootstrap of a statistic that is agg(terms over a resample of the games)."""
    n = len(terms)
    rng = random.Random(seed)
    stats = []
    for _ in range(boot):
        idx = [rng.randrange(n) for _ in range(n)]
        stats.append(agg([terms[i] for i in idx]))
    stats.sort()
    return {
        "p05": percentile(stats, 0.05), "p95": percentile(stats, 0.95),
        "p025": percentile(stats, 0.025), "p975": percentile(stats, 0.975),
        "share_positive": sum(1 for s in stats if s > 0) / boot,
        "share_zero": sum(1 for s in stats if s == 0) / boot,
    }


def score(matched, c, boot, seed):
    """All the numbers, as a dict. matched: list of dicts with p and y."""
    ps = [m["p"] for m in matched]
    ys = [m["y"] for m in matched]
    n = len(ys)
    wins = sum(ys)
    p0 = wins / n
    out = {
        "n": n, "wins": wins, "losses": n - wins, "base_rate": p0,
        "mean_sim_chance": sum(ps) / n,
        "brier_sim": brier(ps, ys),
        "brier_base": brier([p0] * n, ys),
        "brier_coin": 0.25,
        "clip": c,
    }
    out["skill_vs_base"] = 1.0 - out["brier_sim"] / out["brier_base"] if out["brier_base"] > 0 else float("nan")
    out["loglik_sim"] = loglik(ps, ys, c)
    out["loglik_base"] = loglik([p0] * n, ys, c)
    out["llr_nats"] = out["loglik_sim"] - out["loglik_base"]
    out["llr_bits"] = out["llr_nats"] / math.log(2)
    out["llr_per_game_bits"] = out["llr_bits"] / n

    # per-game paired terms against the fixed in-sample base rate
    d_brier = [(p0 - y) ** 2 - (p - y) ** 2 for p, y in zip(ps, ys)]
    d_ll = [math.log(clip(p, c) if y else 1 - clip(p, c)) - math.log(clip(p0, c) if y else 1 - clip(p0, c))
            for p, y in zip(ps, ys)]
    out["brier_diff_base_minus_sim"] = sum(d_brier) / n

    if n >= 2:
        loo = [(wins - y) / (n - 1) for y in ys]
        out["brier_base_loo"] = brier(loo, ys)
        out["skill_vs_base_loo"] = 1.0 - out["brier_sim"] / out["brier_base_loo"] if out["brier_base_loo"] > 0 else float("nan")
        out["llr_nats_loo"] = out["loglik_sim"] - loglik(loo, ys, c)
        out["llr_bits_loo"] = out["llr_nats_loo"] / math.log(2)
        d_brier_loo = [(q - y) ** 2 - (p - y) ** 2 for p, q, y in zip(ps, loo, ys)]
        d_ll_loo = [math.log(clip(p, c) if y else 1 - clip(p, c)) - math.log(clip(q, c) if y else 1 - clip(q, c))
                    for p, q, y in zip(ps, loo, ys)]
        mean = lambda t: sum(t) / len(t)
        out["boot"] = boot
        out["boot_seed"] = seed
        out["boot_brier_diff"] = bootstrap(d_brier, boot, seed, mean)
        out["boot_llr_bits"] = bootstrap(d_ll, boot, seed, lambda t: sum(t) / math.log(2))
        out["boot_brier_diff_loo"] = bootstrap(d_brier_loo, boot, seed, mean)
        out["boot_llr_bits_loo"] = bootstrap(d_ll_loo, boot, seed, lambda t: sum(t) / math.log(2))
        out["boot_brier_sim"] = bootstrap([(p - y) ** 2 for p, y in zip(ps, ys)], boot, seed, mean)

    # reliability table
    edges = [(0.0, 0.35), (0.35, 0.5), (0.5, 0.65), (0.65, 1.0001)]
    table = []
    for lo, hi in edges:
        sel = [(p, y) for p, y in zip(ps, ys) if lo <= p < hi]
        table.append({
            "bin": f"{lo:.2f}-{min(hi, 1.0):.2f}", "n": len(sel),
            "mean_sim": sum(p for p, _ in sel) / len(sel) if sel else None,
            "observed": sum(y for _, y in sel) / len(sel) if sel else None,
        })
    out["reliability"] = table
    return out


# ---------------------------------------------------------------- report


def fmt(x, d=3):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "n/a"
    return f"{x:.{d}f}"


def provenance_lines(res):
    """The banner every report starts with: what is known about where the sim rows came from, and which pilot they used."""
    prov, pilot, working = res["provenance"], res["pilot"], res.get("working_pilot")
    other = prov.get("other_pilot_rows", 0)
    scope = f"All {prov['rows']} sim rows of pilot {pilot}" + (f" ({other} rows of other pilots were not checked or scored)" if other else "")
    if prov["level"] == "verified":
        engines = ", ".join(_short(e) for e in prov["engine_sha256"])
        line = (f"PROVENANCE: verified. {scope} carry the provenance schema (engine hash {engines}, deck and opponent "
                f"content hashes, pilots, seeds); no duplicated or overlapping seeds; one engine build. "
                f"{prov['content_files_rechecked']} deck/opponent files re-checked against their recorded contents")
        if prov["content_not_rechecked"]:
            line += f", {len(prov['content_not_rechecked'])} not present here to re-check ({', '.join(prov['content_not_rechecked'][:4])})"
        lines = [line + "."]
        if prov["content_files_rechecked"] == 0:
            lines.append("  NOTE: no deck or opponent file could be re-checked here, so the recorded contents are taken on trust "
                         "(pass --repo-root to a checkout that holds them).")
    else:
        lines = [f"PROVENANCE: NOT VERIFIED (accepted with --accept-unverified). {prov['unverified_rows']} of {prov['rows']} sim rows "
                 f"lack verifiable provenance (lines {', '.join(str(x) for x in prov['unverified_lines'][:10])}"
                 f"{'...' if len(prov['unverified_lines']) > 10 else ''}): {'; '.join(prov['unverified_reasons'])}. "
                 f"Treat these scores as unverified: the engine, deck contents, pilots and seeds behind them cannot be checked."]
        if prov["unseeded_repeats"]:
            lines.append("  and these pairs have several rows without seeds, so repeated games cannot be ruled out: "
                         + "; ".join(prov["unseeded_repeats"]))
    if working is None:
        lines.append("PILOT: not checked (the working pilot could not be read from run_screen.py and floor.py).")
    elif pilot == working and prov["level"] != "verified":
        lines.append(f"PILOT (label only): the pilot column says {pilot}, the project's working pilot (run_screen.py and floor.py); "
                     f"these rows do not record which bot played which side, so that is not verified.")
    elif pilot == working:
        lines.append(f"PILOT: {pilot} on both sides, the project's working pilot (run_screen.py and floor.py).")
    else:
        lines.append(f"PILOT MISMATCH: these sim rows were played with {pilot}, but the project's working pilot is {working} "
                     f"(run_screen.py and floor.py). The scores describe {pilot}, not {working}.")
    return lines


def print_report(games, skipped, matched, missing, pilot, res, out=print):
    n = res["n"]
    for line in provenance_lines(res):
        out(line)
    out("")
    out(f"Per-game calibration (A3): pilot {pilot}, {n} games scored "
        f"({len(games)} usable in calibration_games.csv, {len(skipped)} rows skipped for no deck file, "
        f"{sum(missing.values())} games with no sim row)")
    if missing:
        out("  pairs with no sim row:")
        for (d, o), k in sorted(missing.items()):
            out(f"    {d} vs {o}  ({k} game{'s' if k > 1 else ''})")
    out("")
    out(f"Dustin's record on the scored games: {res['wins']}-{res['losses']} (base rate {res['base_rate']:.3f}); "
        f"the sim's average win chance for the same games: {res['mean_sim_chance']:.3f}")
    out("")
    out("Brier score (lower is better; 0.25 is a coin):")
    out(f"  sim win chance            {fmt(res['brier_sim'])}")
    out(f"  base rate (in-sample)     {fmt(res['brier_base'])}")
    out(f"  base rate (leave-one-out) {fmt(res.get('brier_base_loo'))}")
    out(f"  coin (0.5)                {fmt(res['brier_coin'])}")
    out(f"  skill score vs base rate  {fmt(res['skill_vs_base'])} in-sample, {fmt(res.get('skill_vs_base_loo'))} leave-one-out "
        f"(1 = perfect, 0 = no better than the base rate, negative = worse)")
    out("")
    out(f"Log-likelihood ratio, sim against the base rate (chances clipped to [{res['clip']}, {1 - res['clip']}]):")
    out(f"  {fmt(res['llr_nats'])} nats = {fmt(res['llr_bits'])} bits in total, {fmt(res['llr_per_game_bits'])} bits per game "
        f"(leave-one-out base rate: {fmt(res.get('llr_bits_loo'))} bits)")
    out("  positive = the sim's chances made Dustin's actual results more likely than the base rate did")
    out("")
    if "boot_brier_diff" in res:
        b = res["boot_brier_diff"]
        out(f"Paired bootstrap over the {n} games ({res['boot']} resamples, seed {res['boot_seed']}):")
        out(f"  Brier difference, base rate minus sim: {fmt(res['brier_diff_base_minus_sim'])}; "
            f"90% interval {fmt(b['p05'])} to {fmt(b['p95'])}, 95% {fmt(b['p025'])} to {fmt(b['p975'])}; "
            f"sim ahead in {100 * b['share_positive']:.1f}% of resamples")
        b = res["boot_brier_diff_loo"]
        out(f"    against the leave-one-out base rate: 90% {fmt(b['p05'])} to {fmt(b['p95'])}, "
            f"sim ahead in {100 * b['share_positive']:.1f}%")
        b = res["boot_llr_bits"]
        out(f"  LLR in bits: 90% interval {fmt(b['p05'], 2)} to {fmt(b['p95'], 2)}, 95% {fmt(b['p025'], 2)} to {fmt(b['p975'], 2)}; "
            f"positive in {100 * b['share_positive']:.1f}% of resamples")
        b = res["boot_brier_sim"]
        out(f"  Brier of the sim alone: 90% interval {fmt(b['p05'])} to {fmt(b['p95'])}")
        out("  An interval that contains 0 means these games cannot tell the sim from the base rate.")
        out("")
    out("Reliability (sim chance bin: games, average sim chance, observed win rate):")
    for t in res["reliability"]:
        if t["n"]:
            out(f"  {t['bin']:10s} {t['n']:3d} games   sim {t['mean_sim']:.3f}   observed {t['observed']:.3f}")
        else:
            out(f"  {t['bin']:10s}   0 games")
    out("")
    out("Every scored game (date, Dustin's deck, opponent list, sim chance [sim games], result):")
    for m in matched:
        seat = "" if m["seat_used"] == "any" else f" (moved {m['seat_used']})"
        out(f"  {m['date']}  {os.path.basename(m['deck_file']):45s} {m['opponent_key']:11s} "
            f"{m['p']:.3f} [{m['sim_games']}]{seat}  {'W' if m['y'] else 'L'}  {m['list_match']}")


def _json_safe(x):
    """NaN and infinity become null, so the JSON is valid (strict) whatever the scores were."""
    if isinstance(x, float) and (math.isnan(x) or math.isinf(x)):
        return None
    if isinstance(x, dict):
        return {k: _json_safe(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_json_safe(v) for v in x]
    return x


def main(argv=None):
    try:
        return _main(argv)
    except BrokenPipeError:
        # the reader of stdout went away (a pipe into head): the score was computed, so stop quietly, not with a false refusal
        try:
            os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        except (OSError, ValueError, AttributeError):
            pass
        raise SystemExit(1)
    except (OSError, UnicodeDecodeError, csv.Error) as e:
        raise SystemExit(f"REFUSED: could not read or write a file ({type(e).__name__}: {e}); no report was produced")


def _main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sim", required=True, help="CSV of simulated win chances per pair")
    ap.add_argument("--games", default=DEFAULT_GAMES, help="calibration_games.csv (default: next to this script)")
    ap.add_argument("--pilot", default=None, help="which pilot's rows to use when the sim file has several")
    ap.add_argument("--draws", choices=("loss", "half", "drop"), default="loss",
                    help="how a sim draw counts for Dustin's deck: a loss (default), half a win, or dropped")
    ap.add_argument("--clip", type=float, default=0.02, help="clip chances to [clip, 1-clip] for the log-likelihood")
    ap.add_argument("--boot", type=int, default=10000, help="bootstrap resamples")
    ap.add_argument("--seed", type=int, default=1, help="bootstrap seed")
    ap.add_argument("--json", default=None, help="also write every number here")
    ap.add_argument("--strict", action="store_true", help="fail if any usable game has no sim row")
    ap.add_argument("--quiet", action="store_true", help="print only the JSON summary line")
    ap.add_argument("--accept-unverified", action="store_true",
                    help="score rows that lack provenance (older or hand-made files) anyway; the report and JSON label them unverified")
    ap.add_argument("--repo-root", default=REPO_ROOT,
                    help="where the deck and opponent files named in the sim file live, to re-check their recorded contents "
                         "(default: this repo; files that are not there are reported, not failed)")
    a = ap.parse_args(argv)
    if not 0 < a.clip < 0.5:
        raise SystemExit("--clip must be between 0 and 0.5")
    if a.boot < 1:
        raise SystemExit("--boot must be at least 1")
    if a.json:
        target = os.path.realpath(a.json)
        if not os.path.isdir(os.path.dirname(target)):
            raise SystemExit(f"REFUSED: the folder for --json {a.json} does not exist")
        if os.path.isdir(target):
            raise SystemExit(f"REFUSED: --json {a.json} is a folder")
        if os.path.exists(target):
            for inp in (a.sim, a.games):
                if target == os.path.realpath(inp) or (os.path.exists(inp) and os.path.samefile(target, inp)):
                    raise SystemExit(f"REFUSED: --json {a.json} is the same file as --sim or --games; it would overwrite the evidence")
            with open(target, "rb") as jf:
                head = jf.read(1)
            if head not in (b"", b"{"):
                raise SystemExit(f"REFUSED: --json {a.json} already exists and is not a JSON report; it would be overwritten "
                                 f"(a deck, a list or a results file?)")

    games, skipped = read_games(a.games)
    if not games:
        raise SystemExit(f"{a.games}: no usable games")
    sim, pilot, prov = read_sim(a.sim, a.draws, a.pilot, a.accept_unverified, a.repo_root)
    notes = []
    try:
        working = working_pilot()[0]
    except ValueError as e:
        working = None
        notes.append(f"note: the working pilot could not be read ({e})")
    used = set()
    matched, missing = join(games, sim, pilot, notes.append, used)
    if a.strict and missing:
        raise SystemExit("missing sim rows for: " + "; ".join(f"{d} vs {o}" for d, o in sorted(missing)))
    if not matched:
        raise SystemExit("no game could be joined to a sim row (check the paths in the sim file)")
    unused = sorted(f"{k[0]} vs {k[1]}" + ("" if k[3] == "any" else f" ({k[3]})") for k in sim if k not in used)
    if unused:
        notes.append(f"note: {len(unused)} sim row group{'s' if len(unused) != 1 else ''} joined to no game and did not count: "
                     + "; ".join(unused[:6]) + ("..." if len(unused) > 6 else ""))
    res = score(matched, a.clip, a.boot, a.seed)
    res.update(pilot=pilot, draws=a.draws, sim_file=a.sim, games_file=a.games,
               usable_games=len(games), skipped_rows=len(skipped), missing_games=sum(missing.values()),
               missing_pairs=[f"{d} vs {o}" for d, o in sorted(missing)], notes=notes, unused_sim_pairs=unused,
               provenance=prov, working_pilot=working,
               pilot_is_working_pilot=None if working is None else pilot == working,
               games_scored=[{k: v for k, v in m.items()} for m in matched])
    if a.json:      # written before anything is printed, so a bad --json path cannot leave a half report behind
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(_json_safe(res), f, indent=2, allow_nan=False)
    if not a.quiet:
        for note in notes:
            print(note)
        print_report(games, skipped, matched, missing, pilot, res)
        if a.json:
            print(f"\nwrote {a.json}")
    else:
        b = res.get("boot_brier_diff", {})
        print(json.dumps(_json_safe({"n": res["n"], "brier_sim": res["brier_sim"], "brier_base": res["brier_base"],
                                     "brier_diff": res["brier_diff_base_minus_sim"], "llr_bits": res["llr_bits"],
                                     "diff_p05": b.get("p05"), "diff_p95": b.get("p95"),
                                     "provenance": prov["level"], "pilot": pilot,
                                     "pilot_is_working_pilot": res["pilot_is_working_pilot"],
                                     "content_files_rechecked": prov["content_files_rechecked"],
                                     "content_files_not_rechecked": len(prov["content_not_rechecked"]),
                                     "name_matched_pairs": sum(1 for n in notes if n.startswith("note: matched")),
                                     "unused_sim_pairs": len(unused), "missing_games": sum(missing.values()),
                                     "missing_pairs": len(missing)}), allow_nan=False))
    return res


if __name__ == "__main__":
    main()
