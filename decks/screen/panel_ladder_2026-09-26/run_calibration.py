#!/usr/bin/env python3
"""A3 calibration games: play every (Dustin deck, opponent list) pair in calibration_games.csv on the
official engine and write sim_results.csv for calibrate.py. Linux only (WSL or the cloud), like
run_screen.py; the engine is the manifest's available release, checked by hash.

usage: python3 run_calibration.py [--games 500] [--pilot kp3] [--meta-pilot kp3] [--seed 21107000000]
                                  [--only N] [--pairs-only] [--resume] [--out sim_results.csv] [--engine PATH]

Seeds: pair i (in the printed order, 0-based) plays games with Dustin's deck in slot 0 on seeds
seed + i*10,000 + g (g < games/2) and in slot 1 on seed + i*10,000 + 5,000 + g, with --seed-stream,
the same seat split as run_screen.py. The default block, 21,107,000,000 to 21,107,149,999 for 15
pairs (reserved to 21,107,199,999), is outside every range in START_HERE's seed table. Who moves
first is decided by the engine from the seed, not by the slot, so the pooled row covers both.
The output is appended one pair at a time, so a stopped run keeps what it finished; --resume skips
the pairs already in the file. --pairs-only prints the pairs and seeds and touches no engine
(works on Windows too).
"""
import argparse
import csv
import hashlib
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
GAMES_CSV = os.path.join(HERE, "calibration_games.csv")
FIELDS = ["deck_file", "opponent_file", "pilot", "games", "wins", "draws", "seat",
          "slot0_games", "slot0_wins", "slot0_draws", "slot1_games", "slot1_wins", "slot1_draws",
          "seed_slot0", "seed_slot1", "deck_pilot", "meta_pilot", "engine", "engine_sha256", "seconds"]


def pairs_from_csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        rows = [r for r in csv.DictReader(f) if r["usable"].strip() == "1"]
    seen = {}
    for r in rows:
        key = (r["deck_file"].strip(), r["opponent_file"].strip())
        seen[key] = seen.get(key, 0) + 1
    return sorted(seen.items())


def run(engine, p0, p1, players, n, seed):
    out = subprocess.run([engine, "simulate", "--num", str(n), "--players", players, "--seed", str(seed),
                          "--seed-stream", "-p", p0, p1], capture_output=True, text=True, cwd=ROOT)
    text = out.stdout + out.stderr
    if "Player 0 won" not in text:
        raise SystemExit(f"engine refused {p0} vs {p1} (exit {out.returncode}):\n" + text[-600:])
    w0 = int(re.search(r"Player 0 won: (\d+)", text)[1])
    w1 = int(re.search(r"Player 1 won: (\d+)", text)[1])
    d = int(re.search(r"Draws: (\d+)", text)[1])
    if w0 + w1 + d != n:
        raise SystemExit(f"engine reported {w0}+{w1}+{d} results for {n} games:\n" + text[-600:])
    return w0, w1, d


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--games", type=int, default=500, help="games per pair, split across the two slots")
    ap.add_argument("--pilot", default="kp3", help="the bot on Dustin's deck")
    ap.add_argument("--meta-pilot", default="kp3", help="the bot on the opponent's list")
    ap.add_argument("--seed", type=int, default=21_107_000_000, help="first seed of the block")
    ap.add_argument("--only", type=int, default=None, help="play only the first N pairs (smoke tests)")
    ap.add_argument("--pairs-only", action="store_true", help="print the pairs and seeds, play nothing")
    ap.add_argument("--resume", action="store_true", help="skip pairs already in --out")
    ap.add_argument("--out", default=os.path.join(HERE, "sim_results.csv"))
    ap.add_argument("--engine", default=None, help="default: the manifest's available release")
    ap.add_argument("--games-csv", default=GAMES_CSV)
    a = ap.parse_args()
    if a.games < 2:
        raise SystemExit("--games must be at least 2 (one per slot)")

    pairs = pairs_from_csv(a.games_csv)
    if a.only is not None:
        pairs = pairs[: a.only]
    label = a.pilot if a.pilot == a.meta_pilot else f"{a.pilot}|{a.meta_pilot}"
    half = a.games // 2

    print(f"{len(pairs)} pairs, {a.games} games each ({half} with Dustin's deck in slot 0, {a.games - half} in slot 1), "
          f"{a.pilot} on Dustin's deck, {a.meta_pilot} on the opponent, seeds from {a.seed:,}")
    for i, ((d, o), k) in enumerate(pairs):
        s0 = a.seed + i * 10_000
        print(f"  pair {i:2d}: {d} vs {o}  ({k} ladder game{'s' if k > 1 else ''})  seeds {s0:,}+g and {s0 + 5_000:,}+g")
    if a.pairs_only:
        return

    sys.path.insert(0, ROOT)
    from current_engine import resolve  # noqa: E402
    try:
        engine = str(resolve(project=ROOT, override=a.engine))
    except (OSError, ValueError) as e:
        raise SystemExit(f"REFUSED: {e} (this runs only the manifest's available release)")
    sha = hashlib.sha256(open(engine, "rb").read()).hexdigest()
    rel_engine = os.path.relpath(engine, ROOT)

    done = set()
    if a.resume and os.path.isfile(a.out):
        with open(a.out, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                done.add((r["deck_file"], r["opponent_file"], r["pilot"]))
    new_file = not os.path.isfile(a.out) or os.path.getsize(a.out) == 0
    with open(a.out, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        if new_file:
            w.writeheader()
            f.flush()
        for i, ((d, o), k) in enumerate(pairs):
            if (d, o, label) in done:
                print(f"pair {i}: already in {os.path.basename(a.out)}, skipped")
                continue
            s0 = a.seed + i * 10_000
            s1 = s0 + 5_000
            t = time.time()
            w0, l0, d0 = run(engine, os.path.join(ROOT, d), os.path.join(ROOT, o), f"{a.pilot},{a.meta_pilot}", half, s0)
            l1, w1, d1 = run(engine, os.path.join(ROOT, o), os.path.join(ROOT, d), f"{a.meta_pilot},{a.pilot}", a.games - half, s1)
            secs = time.time() - t
            row = dict(deck_file=d, opponent_file=o, pilot=label, games=a.games, wins=w0 + w1, draws=d0 + d1, seat="any",
                       slot0_games=half, slot0_wins=w0, slot0_draws=d0, slot1_games=a.games - half, slot1_wins=w1, slot1_draws=d1,
                       seed_slot0=s0, seed_slot1=s1, deck_pilot=a.pilot, meta_pilot=a.meta_pilot,
                       engine=rel_engine, engine_sha256=sha, seconds=f"{secs:.1f}")
            w.writerow(row)
            f.flush()
            print(f"pair {i:2d}: {os.path.basename(d)} vs {os.path.basename(o)}: {w0 + w1}/{a.games} = "
                  f"{100 * (w0 + w1) / a.games:.1f}% (slot 0 {w0}/{half}, slot 1 {w1}/{a.games - half}, draws {d0 + d1})  {secs:.0f}s")
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
