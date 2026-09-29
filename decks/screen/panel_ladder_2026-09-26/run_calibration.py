#!/usr/bin/env python3
"""A3 calibration games: play every (Dustin deck, opponent list) pair in calibration_games.csv on the
official engine and write sim_results.csv for calibrate.py. Linux only (WSL or the cloud), like
run_screen.py; the engine is the manifest's available release, checked by hash.

usage: python3 run_calibration.py [--games 500] [--pilot P] [--meta-pilot P] [--seed 21107000000]
                                  [--only N] [--pairs-only] [--resume] [--out sim_results.csv] [--engine PATH]
                                  [--allow-pilot-mismatch] [--accept-unverified-resume]

Seeds: pair i (in the printed order, 0-based) plays games with Dustin's deck in slot 0 on seeds
seed + i*10,000 + g (g < games/2) and in slot 1 on seed + i*10,000 + 5,000 + g, with --seed-stream,
the same seat split as run_screen.py. The default block, 21,107,000,000 to 21,107,199,999, is reserved
for 20 pairs (200,000 seeds) and is outside every range in START_HERE's seed table. So a slot may play at
most 5,000 games (10,000 per pair) and a run at most 20 pairs; larger requests are refused, because their
seeds would run into the next slot, the next pair or another registered block. Who moves first is decided
by the engine from the seed, not by the slot, so the pooled row covers both. --pairs-only prints the pairs
and seeds and touches no engine (works on Windows too).

Pilots. The default is the project's working pilot on both sides, read from run_screen.py's --pilot and
--meta-pilot defaults and floor.py's FLOOR_PILOT (kog3 since the Sept 28 engine switch); the run is REFUSED if
those disagree or if --pilot/--meta-pilot name another bot, unless --allow-pilot-mismatch says that is deliberate
(for example to reproduce the kp3 that calibration_README.md registered on Sept 26).

Output and resume. Each finished pair is one row, appended and flushed at once, carrying what is needed to check it
later: engine and its hash, sha256 of the deck and the opponent file (line endings normalised), both pilots, game
counts per slot and both seeds, and schema "1". Nothing is appended to a file that already holds rows unless
--resume is given; --resume on a file that is missing, empty or holds only a header is refused (a mistyped --out
would otherwise replay every pair), so a fresh start is a run without --resume. --resume reuses a finished pair only after checking, against THIS run, the engine hash, both
files' contents, both pilots, the game count and the seeds. Any difference, a duplicated or overlapping record, a
second row for a pair, an unknown header, or a planned seed that another row already used, stops the run BEFORE the
engine is started or a row is written, and every problem found is listed. Rows without full provenance (older or
hand-edited files) are not reused unless --accept-unverified-resume is given, and then they are named as unverified;
a file with an older header cannot be appended to at all (start a new --out; calibrate.py can still score the old
one with --accept-unverified).

Also refused before any game: a file that does not end with a newline (a cut last row would be glued to the next);
a games file that names one pair under two spellings (./decks/x, decks//x, other case); a pilot name that is not plain
(letters, digits, underscore); a seed the engine cannot take or a block that leaves 0..2^64-1; --only below 1; a missing
deck or opponent file; a seat other than 'any' in a runner file; rows for other pairs, under this pilot, from another
engine build. Once running, the engine and both files are re-hashed before and after every pair and a pair whose inputs
moved is not recorded (earlier pairs stay); the output folder is locked so two runs cannot append the same pairs; the
output file is opened only when there is a pair to write, so an identical resume of a finished, read-only file changes
nothing. A seed block other than the default is announced (it must be in START_HERE's seed table). Seeds are shared
across pilots on purpose (paired comparisons), so only rows of the same pilot label count as a seed collision.
"""
import argparse
import csv
import hashlib
import os
import re
import subprocess
import sys
import time
from collections import defaultdict
try:
    import fcntl          # Linux only, like the runner; used to keep two runs off one output folder
except ImportError:       # pragma: no cover
    fcntl = None

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import calibrate  # noqa: E402  (shared record checks; standard library only)

GAMES_CSV = os.path.join(HERE, "calibration_games.csv")
FIELDS = ["deck_file", "opponent_file", "pilot", "games", "wins", "draws", "seat",
          "slot0_games", "slot0_wins", "slot0_draws", "slot1_games", "slot1_wins", "slot1_draws",
          "seed_slot0", "seed_slot1", "deck_pilot", "meta_pilot", "engine", "engine_sha256", "seconds",
          "schema", "deck_sha256", "opponent_sha256"]
PAIR_SPACING, SLOT_SPACING, RESERVED_SEEDS = calibrate.PAIR_SPACING, calibrate.SLOT_SPACING, calibrate.RESERVED_SEEDS


def pairs_from_csv(path):
    """The usable (deck, opponent) pairs, sorted, with how many ladder games each has. Refuses a file that names one pair
    twice under spellings the scorer would treat as one (./decks/x, decks//x, other case): the runner would play both into
    different seeds and could never resume its own output."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing = {"deck_file", "opponent_file", "usable"} - set(reader.fieldnames or [])
        if missing:
            raise SystemExit(f"REFUSED: {os.path.basename(path)} is missing columns {sorted(missing)}")
        rows = []
        for r in reader:
            if None in r or any(v is None for v in r.values()):
                raise SystemExit(f"REFUSED: {os.path.basename(path)} line {reader.line_num} has a different number of fields than the header")
            if r["usable"].strip() == "1":
                rows.append(r)
    seen = {}
    for r in rows:
        key = (r["deck_file"].strip(), r["opponent_file"].strip())
        seen[key] = seen.get(key, 0) + 1
    by_norm = defaultdict(list)
    for d, o in seen:
        by_norm[(calibrate.norm_path(d), calibrate.norm_path(o))].append((d, o))
    twice = [v for v in by_norm.values() if len(v) > 1]
    if twice:
        raise SystemExit(f"REFUSED: {os.path.basename(path)} names one pair under different spellings: "
                         + "; ".join(" and ".join(f"{d} vs {o}" for d, o in v) for v in twice)
                         + ". Make the spelling identical (or remove the duplicate) before any game is played.")
    return sorted(seen.items())


def run(engine, p0, p1, players, n, seed):
    out = subprocess.run([engine, "simulate", "--num", str(n), "--players", players, "--seed", str(seed),
                          "--seed-stream", "-p", p0, p1], capture_output=True, text=True, cwd=ROOT)
    text = out.stdout + out.stderr
    if "Player 0 won" not in text:
        raise SystemExit(f"engine refused {p0} vs {p1} (exit {out.returncode}):\n" + text[-600:])
    found = [re.search(pat, text) for pat in (r"Player 0 won: (\d+)", r"Player 1 won: (\d+)", r"Draws: (\d+)")]
    if not all(found):
        raise SystemExit(f"engine output could not be read (a count is missing) for {p0} vs {p1}:\n" + text[-600:])
    w0, w1, d = (int(m[1]) for m in found)
    if w0 + w1 + d != n:
        raise SystemExit(f"engine reported {w0}+{w1}+{d} results for {n} games:\n" + text[-600:])
    return w0, w1, d


# ---------------------------------------------------------------- checks before anything is run or written


def pilot_label(deck_pilot, meta_pilot):
    return deck_pilot if deck_pilot == meta_pilot else f"{deck_pilot}|{meta_pilot}"


def resolve_pilots(pilot, meta_pilot, allow_mismatch):
    """(pilot, meta_pilot, message). The intended pilot is the project's working pilot; anything else needs a flag."""
    for flag, name in (("--pilot", pilot), ("--meta-pilot", meta_pilot)):
        if name is not None and not calibrate.NAME_RE.fullmatch(name):
            raise SystemExit(f"REFUSED: {flag} {name!r} is not a pilot name (letters, digits and underscores only: no spaces, "
                             f"commas or pipes)")
    try:
        working, sources = calibrate.working_pilot()
    except ValueError as e:
        if not (allow_mismatch and pilot and meta_pilot):
            raise SystemExit(f"REFUSED: the intended pilot cannot be verified ({e}). Pass --pilot and --meta-pilot together "
                             f"with --allow-pilot-mismatch to run with the pilots you name regardless.")
        return pilot, meta_pilot, f"NOTE: the intended pilot could not be verified ({e}); running {pilot} / {meta_pilot} as asked"
    pilot, meta_pilot = pilot or working, meta_pilot or working
    where = "; ".join(f"{k} = {v}" for k, v in sources.items())
    if pilot != working or meta_pilot != working:
        msg = (f"{pilot} on Dustin's deck and {meta_pilot} on the opponent differ from the project's working pilot {working} "
               f"on both sides ({where})")
        if not allow_mismatch:
            raise SystemExit(f"REFUSED: {msg}. calibration_README.md still names kp3, which was the working pilot on Sept 26. "
                             f"If this pilot is intended, say so with --allow-pilot-mismatch.")
        return pilot, meta_pilot, f"NOTE (pilot mismatch, allowed): {msg}"
    return pilot, meta_pilot, f"pilot check: {working} on both sides, the project's working pilot ({where})"


def layout_errors(npairs, games, seed=0):
    errs = []
    end = seed + max(npairs, 1) * PAIR_SPACING - 1
    if seed < 0 or end > calibrate.U64:
        errs.append(f"--seed {seed:,} with {npairs} pairs needs seeds {seed:,} to {end:,}, "
                    f"outside what the engine takes (0 to {calibrate.U64:,})")
    lo, hi = DEFAULT_SEED, DEFAULT_SEED + RESERVED_SEEDS - 1
    if seed != DEFAULT_SEED and seed <= hi and end >= lo:
        errs.append(f"--seed {seed:,} (seeds {seed:,} to {end:,}) overlaps part of the reserved block ({lo:,} to {hi:,}) without being "
                    f"it: some games would share seeds with a run that already used them. Use the default seed, or a block that "
                    f"does not touch it and is registered in START_HERE's seed table")
    if games - games // 2 > SLOT_SPACING:
        errs.append(f"--games {games:,} overflows the reserved seed spacing: a slot may play at most {SLOT_SPACING:,} games "
                    f"(at most {2 * SLOT_SPACING:,} per pair); more would run slot 0's seeds into slot 1's and slot 1's into the "
                    f"next pair's block")
    if npairs * PAIR_SPACING > RESERVED_SEEDS:
        errs.append(f"{npairs} pairs need {npairs * PAIR_SPACING:,} seeds but one run reserves {RESERVED_SEEDS:,} "
                    f"({RESERVED_SEEDS // PAIR_SPACING} pairs); the last pairs would use seeds outside the reserved block and could "
                    f"collide with other registered blocks (use --only, or register a larger block first)")
    return errs


def plan_pairs(pairs, games, seed):
    half = games // 2
    return [dict(index=i, deck_file=d, opponent_file=o, ladder_games=k, games=games, slot0_games=half, slot1_games=games - half,
                 seed_slot0=seed + i * PAIR_SPACING, seed_slot1=seed + i * PAIR_SPACING + SLOT_SPACING)
            for i, ((d, o), k) in enumerate(pairs)]


def attach_hashes(plan, root):
    """Add the content hashes of both files to every planned pair; returns the problems (unreadable files)."""
    errs = []
    for pl in plan:
        for key, hkey in (("deck_file", "deck_sha256"), ("opponent_file", "opponent_sha256")):
            try:                           # read the way the engine call will: os.path.join(ROOT, path)
                pl[hkey] = calibrate.file_sha256(os.path.join(root, pl[key]))
            except OSError as e:
                errs.append(f"pair {pl['index']}: cannot read {pl[key]} ({e.strerror or e})")
    return errs


def inputs_unchanged(pl, engine, sha, when):
    """Re-hash the engine and both files of a pair. A pair is recorded only if what was hashed at the start is still what ran:
    an edit or a replaced binary while it played would otherwise be written down under the old hash."""
    problems = []
    for key, hkey in (("deck_file", "deck_sha256"), ("opponent_file", "opponent_sha256")):
        try:
            now = calibrate.file_sha256(os.path.join(ROOT, pl[key]))
        except OSError as e:
            problems.append(f"{pl[key]} cannot be read ({e.strerror or e})")
            continue
        if now != pl[hkey]:
            problems.append(f"{pl[key]} changed ({_show(pl[hkey])} -> {_show(now)})")
    with open(engine, "rb") as ef:
        if hashlib.sha256(ef.read()).hexdigest() != sha:
            problems.append("the engine binary changed")
    if problems:
        raise SystemExit(f"REFUSED: {'; '.join(problems)} {when} pair {pl['index']} was played; that pair was not recorded "
                         f"(pairs finished earlier are kept)")


def _show(x):
    """A value for a mismatch message: numbers with commas, long text cut at 16 characters with its full length, so a hash
    that was cut short or edited shows as such."""
    if isinstance(x, str):
        return x if len(x) <= 16 else f"{x[:16]}...({len(x)} characters)"
    return f"{x:,}"


def compare_record(r, pl, ident):
    """What a finished row says differently from this run's plan (fields the row does not record are not compared)."""
    p, o = r["prov"], r["opt"]
    checks = [("games", r["games"], pl["games"]), ("slot0_games", o["slot0_games"], pl["slot0_games"]),
              ("slot1_games", o["slot1_games"], pl["slot1_games"]), ("seed_slot0", o["seed_slot0"], pl["seed_slot0"]),
              ("seed_slot1", o["seed_slot1"], pl["seed_slot1"]), ("deck_pilot", p["deck_pilot"], ident["deck_pilot"]),
              ("meta_pilot", p["meta_pilot"], ident["meta_pilot"]), ("engine_sha256", p["engine_sha256"], ident["engine_sha256"]),
              ("deck_sha256", p["deck_sha256"], pl["deck_sha256"]), ("opponent_sha256", p["opponent_sha256"], pl["opponent_sha256"])]
    return [f"{name} is {_show(have)} in the file, this run would use {_show(want)}"
            for name, have, want in checks if have not in (None, "") and have != want]


def read_out_header(path):
    """The first line of an existing, non-empty output file; None if there is no such file."""
    if not os.path.isfile(path) or os.path.getsize(path) == 0:
        return None
    with open(path, encoding="utf-8", newline="") as f:
        return next(csv.reader(f), [])


def check_existing(out, header, plan, ident, resume, accept_unverified):
    """Everything to verify about an existing output file BEFORE any engine call or append.
    Returns (reuse {pair index: row}, warnings, problems)."""
    name = os.path.basename(out)
    with open(out, "rb") as fb:
        fb.seek(-1, os.SEEK_END)
        if fb.read(1) != b"\n":
            return {}, [], [f"{name} does not end with a newline, so its last row may be cut (an interrupted write, or an editor that "
                            f"trims the final newline); appending would glue the next row onto it. Restore the file or choose a new --out."]
    if header != FIELDS:
        bom = " It starts with a byte-order mark, as some Windows editors save files." if header and header[0].startswith("﻿") else ""
        first = next((f"column {i + 1} is {h.lstrip(chr(0xfeff))!r} where this runner writes {e!r}"
                      for i, (h, e) in enumerate(zip(header, FIELDS)) if h.lstrip(chr(0xfeff)) != e), None)
        return {}, [], [f"{name} has an older or different header ({len(header)} columns, this runner writes {len(FIELDS)}"
                        f"{'; ' + first if first else ''}); rows written under it would be misaligned, so nothing is appended "
                        f"to it.{bom} Start a new --out (calibrate.py can still score the old file with --accept-unverified)."]
    try:
        rows = calibrate.parse_sim_rows(out)
    except SystemExit as e:          # a bad row, a repeated header line, a cut number: refuse in the same form as every other problem
        return {}, [], [str(e.code)]
    if not rows:
        return {}, [], ([f"--resume was given but {name} holds no finished pair (a header only), so there is nothing to resume; "
                         f"to start it, leave out --resume"] if resume else [])
    if not resume:
        return {}, [], [f"{name} already holds {len(rows)} row{'s' if len(rows) != 1 else ''}; appending would write games twice. "
                        f"Pass --resume to continue it (each finished pair is then verified), or choose a new --out."]
    problems, warnings = [], []
    by_pilot = defaultdict(list)
    for r in rows:
        by_pilot[r["pilot"]].append(r)
    for pilot, rs in sorted(by_pilot.items()):
        errs, _ = calibrate.find_problems(rs, repo_root=None, accept_unverified=True)   # sets each row's level
        problems += [f"{name} (pilot {pilot}): {e}" for e in errs]
    for r in rows:
        if r["seat"] != "any":
            problems.append(f"{name} line {r['line']}: seat is {r['seat']!r}, but this runner writes only pooled ('any') rows; "
                            f"the file was edited or did not come from this runner")
    key_rows = defaultdict(list)
    for r in rows:
        key_rows[(calibrate.norm_path(r["deck"]), calibrate.norm_path(r["opp"]), r["pilot"])].append(r)
    planned_keys = set()
    reuse, has_row = {}, set()
    for pl in plan:
        i, label = pl["index"], ident["label"]
        k = (calibrate.norm_path(pl["deck_file"]), calibrate.norm_path(pl["opponent_file"]), label)
        planned_keys.add(k)
        what = f"pair {i} ({os.path.basename(pl['deck_file'])} vs {os.path.basename(pl['opponent_file'])})"
        rs = key_rows.get(k, [])
        if not rs:
            continue
        has_row.add(i)
        if len(rs) > 1:
            problems.append(f"{what}: {len(rs)} rows (lines {calibrate._lines(rs)}) for one pair; this runner writes exactly one")
            continue
        r = rs[0]
        diffs = compare_record(r, pl, ident)
        if diffs:
            problems += [f"{what}: {d}" for d in diffs]
            continue
        if r.get("level") != "verified":
            msg = f"{what}: line {r['line']} has no full provenance ({'; '.join(r['why'])}); its engine, file contents or seeds cannot be verified"
            if accept_unverified:
                warnings.append(msg + " (reused as UNVERIFIED because of --accept-unverified-resume)")
                reuse[i] = r
            else:
                problems.append(msg + "; pass --accept-unverified-resume to keep it as it is, or use a new --out")
            continue
        reuse[i] = r
    # Seeds are shared across pilots on purpose (paired comparisons play the same deals with another bot), so only rows of
    # THIS pilot label count here: another pair already using these seeds means the pair layout changed.
    used = [(iv, r["line"]) for r in rows if r["pilot"] == ident["label"] for iv in r["iv"]]
    for pl in plan:
        if pl["index"] in has_row:
            continue
        for lo, hi, tag in ((pl["seed_slot0"], pl["seed_slot0"] + pl["slot0_games"], "slot 0"),
                            (pl["seed_slot1"], pl["seed_slot1"] + pl["slot1_games"], "slot 1")):
            hit = [line for (a, b, _), line in used if a < hi and lo < b]
            if hit:
                problems.append(f"pair {pl['index']} ({os.path.basename(pl['deck_file'])} vs {os.path.basename(pl['opponent_file'])}): "
                                f"planned {tag} seeds {lo:,}..{hi - 1:,} overlap seeds already used by line {hit[0]} of {name}; "
                                f"the pair layout changed (or --seed did): use a fresh --seed block or a new --out")
                break
    stray = [r for r in rows if (calibrate.norm_path(r["deck"]), calibrate.norm_path(r["opp"]), r["pilot"]) not in planned_keys]
    plan_hash = {}
    for pl in plan:
        plan_hash[calibrate.norm_path(pl["deck_file"])] = pl["deck_sha256"]
        plan_hash[calibrate.norm_path(pl["opponent_file"])] = pl["opponent_sha256"]
    for r in stray:      # rows for other pairs under THIS pilot label would sit in the same scored set as this run's rows
        if r["pilot"] != ident["label"]:
            continue
        e = r["prov"].get("engine_sha256", "")
        if e and e != ident["engine_sha256"]:
            problems.append(f"{name} line {r['line']}: a row for another pair was played with engine {_show(e)}, this run uses "
                            f"{_show(ident['engine_sha256'])}; results from different engines cannot share one scored set "
                            f"(use a new --out)")
        for kind, path, want in (("deck", r["deck"], r["prov"].get("deck_sha256", "")),
                                 ("opponent", r["opp"], r["prov"].get("opponent_sha256", ""))):
            if not want:
                continue
            now = plan_hash.get(calibrate.norm_path(path))
            if now is None:
                try:
                    now = calibrate.file_sha256(os.path.join(ROOT, path))
                except OSError:
                    continue                         # the file is no longer here: nothing to compare it with
            if now != want:
                problems.append(f"{name} line {r['line']}: a row for another pair records the {kind} file {path} as {_show(want)}, "
                                f"but it is now {_show(now)}; one file with two contents cannot share one scored set (use a new --out)")
        if r.get("level") != "verified":
            msg = (f"{name} line {r['line']} (a pair not in this run) has no full provenance ({'; '.join(r['why'])}); "
                   f"the scorer would refuse the whole file with it in")
            if accept_unverified:
                warnings.append(msg + " (kept as UNVERIFIED because of --accept-unverified-resume)")
            else:
                problems.append(msg + "; pass --accept-unverified-resume to keep it, or use a new --out")
    if stray:
        warnings.append(f"{len(stray)} row{'s' if len(stray) != 1 else ''} in {name} belong to pairs or pilots not in this run "
                        f"(lines {calibrate._lines(stray)}); they are left as they are")
    return reuse, warnings, problems


# ---------------------------------------------------------------- main


def positive_int(text):
    try:
        v = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{text!r} is not a whole number")
    if v < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return v


def lock_folder(out):
    """Hold an exclusive lock on the output folder while a run checks and appends, so two runs (two terminals, two sessions)
    cannot both check, then both append the same pairs into the same seeds. Returns the descriptor to close, or None."""
    if fcntl is None:      # pragma: no cover
        return None
    fd = os.open(os.path.dirname(os.path.realpath(out)) or ".", os.O_RDONLY)   # the real folder, so a symlink cannot slip past the lock
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        os.close(fd)
        raise SystemExit(f"REFUSED: another calibration run holds the folder of {os.path.basename(out)}; wait for it to finish "
                         f"(two runs into one folder could append the same pairs twice)")
    return fd


DEFAULT_SEED = 21_107_000_000


def main(argv=None):
    """Run; a file that cannot be read or written ends in a REFUSED message (never a traceback) that says what, if anything,
    was already recorded."""
    state = {"appended": 0, "writing": False}
    try:
        return _main(argv, state)
    except BrokenPipeError:
        raise SystemExit(f"STOPPED: the output was closed (a pipe into head?), not a file problem; the {state['appended']} pair(s) "
                         f"recorded so far stay in the file and --resume continues from there")
    except (OSError, UnicodeDecodeError, csv.Error) as e:
        if state["writing"]:        # the failure came while a row was being written: the file may end in half a row
            tail = (f"a row may have been written only in part (the {state['appended']} pair(s) before it are complete): restore the "
                    f"file to its last complete line, or use a new --out; --resume refuses a file that does not end with a newline")
        elif state["appended"]:
            tail = f"the {state['appended']} pair(s) recorded before this stay in the file; nothing further was appended"
        else:
            tail = "nothing was run and nothing was appended"
        raise SystemExit(f"REFUSED: could not read or write a file ({type(e).__name__}: {e}); {tail}")


def _main(argv, state):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--games", type=int, default=500, help="games per pair, split across the two slots (at most 10,000)")
    ap.add_argument("--pilot", default=None, help="the bot on Dustin's deck (default: the project's working pilot)")
    ap.add_argument("--meta-pilot", default=None, help="the bot on the opponent's list (default: the project's working pilot)")
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED, help="first seed of the block")
    ap.add_argument("--only", type=positive_int, default=None, help="play only the first N pairs (smoke tests)")
    ap.add_argument("--pairs-only", action="store_true", help="print the pairs and seeds, play nothing")
    ap.add_argument("--resume", action="store_true", help="continue --out: verify and reuse finished pairs, play the rest")
    ap.add_argument("--allow-pilot-mismatch", action="store_true", help="run a pilot other than the working pilot, deliberately")
    ap.add_argument("--accept-unverified-resume", action="store_true",
                    help="reuse finished rows that lack full provenance (older or hand-edited), reported as unverified")
    ap.add_argument("--out", default=os.path.join(HERE, "sim_results.csv"))
    ap.add_argument("--engine", default=None, help="default: the manifest's available release")
    ap.add_argument("--games-csv", default=GAMES_CSV)
    a = ap.parse_args(argv)
    if a.games < 2:
        raise SystemExit("--games must be at least 2 (one per slot)")

    pairs = pairs_from_csv(a.games_csv)
    if a.only is not None:
        pairs = pairs[: a.only]
    if not pairs:
        raise SystemExit(f"REFUSED: no usable pairs in {os.path.basename(a.games_csv)}; there is nothing to play")
    a.pilot, a.meta_pilot, pilot_msg = resolve_pilots(a.pilot, a.meta_pilot, a.allow_pilot_mismatch)
    errs = layout_errors(len(pairs), a.games, a.seed)
    if errs:
        raise SystemExit(calibrate.format_problems("this run's plan", errs, "nothing was run"))
    label = pilot_label(a.pilot, a.meta_pilot)
    half = a.games // 2

    print(f"{len(pairs)} pairs, {a.games} games each ({half} with Dustin's deck in slot 0, {a.games - half} in slot 1), "
          f"{a.pilot} on Dustin's deck, {a.meta_pilot} on the opponent, seeds from {a.seed:,}")
    print(pilot_msg)
    if a.seed != DEFAULT_SEED:
        print(f"NOTE: seeds {a.seed:,} to {a.seed + len(pairs) * PAIR_SPACING - 1:,} are not the reserved block "
              f"({DEFAULT_SEED:,} to {DEFAULT_SEED + RESERVED_SEEDS - 1:,}); make sure they are registered in START_HERE's seed table.")
    for i, ((d, o), k) in enumerate(pairs):
        s0 = a.seed + i * PAIR_SPACING
        print(f"  pair {i:2d}: {d} vs {o}  ({k} ladder game{'s' if k > 1 else ''})  seeds {s0:,}+g and {s0 + SLOT_SPACING:,}+g")
    if a.pairs_only:
        return
    fd = lock_folder(a.out)
    try:
        execute(a, pairs, label, half, state)
    finally:
        if fd is not None:
            os.close(fd)


def execute(a, pairs, label, half, state):
    """Everything after the plan is printed: verify first, then play and append one pair at a time."""
    sys.path.insert(0, ROOT)
    from current_engine import resolve  # noqa: E402
    try:
        engine = str(resolve(project=ROOT, override=a.engine))
    except (OSError, ValueError) as e:
        raise SystemExit(f"REFUSED: {e} (this runs only the manifest's available release)")
    with open(engine, "rb") as ef:
        sha = hashlib.sha256(ef.read()).hexdigest()
    rel_engine = os.path.relpath(engine, ROOT)

    plan = plan_pairs(pairs, a.games, a.seed)
    problems = attach_hashes(plan, ROOT)
    ident = {"label": label, "deck_pilot": a.pilot, "meta_pilot": a.meta_pilot, "engine_sha256": sha}
    reuse, warnings = {}, []
    header = read_out_header(a.out)
    if a.resume and header is None:
        problems.append(f"--resume was given but {os.path.basename(a.out)} does not exist or is empty, so there is nothing to resume "
                        f"(a mistyped --out?); to start a new file, leave out --resume")
    if header is not None and not problems:
        reuse, warnings, more = check_existing(a.out, header, plan, ident, a.resume, a.accept_unverified_resume)
        problems += more
    if problems:
        raise SystemExit(calibrate.format_problems(os.path.basename(a.out), problems, "nothing was run and nothing was appended"))
    for w in warnings:
        print("WARNING: " + w)

    new_file = header is None
    played = 0
    f = w = None
    try:
        for pl in plan:
            i, d, o = pl["index"], pl["deck_file"], pl["opponent_file"]
            if i in reuse:
                r = reuse[i]
                how = "verified against this run's engine, deck and opponent contents, pilots, game count and seeds" \
                    if r["level"] == "verified" else "UNVERIFIED (accepted)"
                print(f"pair {i}: already in {os.path.basename(a.out)} (line {r['line']}), {how}; skipped")
                continue
            inputs_unchanged(pl, engine, sha, "before")
            if f is None:            # the file is opened only when there is something to write (a finished, read-only file stays untouched)
                f = open(a.out, "a", encoding="utf-8", newline="")
                w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
                if new_file:
                    state["writing"] = True
                    w.writeheader()
                    f.flush()
                    state["writing"] = False
            s0, s1 = pl["seed_slot0"], pl["seed_slot1"]
            t = time.time()
            w0, l0, d0 = run(engine, os.path.join(ROOT, d), os.path.join(ROOT, o), f"{a.pilot},{a.meta_pilot}", half, s0)
            l1, w1, d1 = run(engine, os.path.join(ROOT, o), os.path.join(ROOT, d), f"{a.meta_pilot},{a.pilot}", a.games - half, s1)
            secs = time.time() - t
            inputs_unchanged(pl, engine, sha, "while")
            row = dict(deck_file=d, opponent_file=o, pilot=label, games=a.games, wins=w0 + w1, draws=d0 + d1, seat="any",
                       slot0_games=half, slot0_wins=w0, slot0_draws=d0, slot1_games=a.games - half, slot1_wins=w1, slot1_draws=d1,
                       seed_slot0=s0, seed_slot1=s1, deck_pilot=a.pilot, meta_pilot=a.meta_pilot,
                       engine=rel_engine, engine_sha256=sha, seconds=f"{secs:.1f}",
                       schema=calibrate.PROVENANCE_SCHEMA, deck_sha256=pl["deck_sha256"], opponent_sha256=pl["opponent_sha256"])
            state["writing"] = True
            w.writerow(row)
            f.flush()
            state["writing"] = False
            played += 1
            state["appended"] += 1
            print(f"pair {i:2d}: {os.path.basename(d)} vs {os.path.basename(o)}: {w0 + w1}/{a.games} = "
                  f"{100 * (w0 + w1) / a.games:.1f}% (slot 0 {w0}/{half}, slot 1 {w1}/{a.games - half}, draws {d0 + d1})  {secs:.0f}s")
    finally:
        if f is not None:
            f.close()
    if played:
        print(f"wrote {a.out} ({played} pair{'s' if played != 1 else ''} played, {len(reuse)} reused)")
    else:
        print(f"nothing written: every pair ({len(reuse)}) was already in {os.path.basename(a.out)}, the file is unchanged")


if __name__ == "__main__":
    main()
