#!/usr/bin/env python3
"""A3 per-game calibration: does the simulator's win chance for the exact pair Dustin played
(his list against the opponent's archetype list) say anything about whether he won?

usage (Windows or Linux python 3, standard library only):
  python calibrate.py --sim sim_results.csv [--games calibration_games.csv] [--pilot kp3]
                      [--draws loss|half|drop] [--clip 0.02] [--boot 10000] [--seed 1]
                      [--json report.json] [--strict] [--quiet]

sim CSV (what the laptop writes, see calibration_README.md): columns deck_file, opponent_file,
pilot, games, wins; optional draws and seat. Paths are relative to the repo root as written in
calibration_games.csv (either slash, case ignored; a bare file name also matches, with a warning).
seat: blank or "any" = pooled over who moved first (the normal case); "first" / "second" = the
sim's win chance when Dustin's deck moved first / second, used only for the games whose
went_first is known in calibration_games.csv. Rows with the same key are summed, so a runner
may append chunks. Extra columns are ignored.

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
import csv
import json
import math
import os
import random
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_GAMES = os.path.join(HERE, "calibration_games.csv")
SEATS = ("any", "first", "second")


# ---------------------------------------------------------------- input


def norm_path(p):
    p = (p or "").strip().replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    return p.lower()


def to_int(row, col, path, line):
    v = (row.get(col) or "").strip()
    try:
        return int(float(v))
    except ValueError:
        raise SystemExit(f"{path} line {line}: column {col} is not a number: {v!r}")


def read_games(path):
    """The usable rows of calibration_games.csv (deck file present) as dicts."""
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    need = {"game_id", "deck_file", "opponent_file", "result", "usable"}
    missing = need - set(rows[0].keys() if rows else [])
    if missing:
        raise SystemExit(f"{path}: missing columns {sorted(missing)}")
    games, skipped = [], []
    for r in rows:
        if r["usable"].strip() != "1" or not r["deck_file"].strip():
            skipped.append(r)
            continue
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


def read_sim(path, draws_mode):
    """sim rows keyed by (deck, opponent, pilot, seat); values summed over duplicate keys."""
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        cols = set(reader.fieldnames or [])
        need = {"deck_file", "opponent_file", "pilot", "games", "wins"}
        if need - cols:
            raise SystemExit(f"{path}: missing columns {sorted(need - cols)} (has {sorted(cols)})")
        acc = defaultdict(lambda: [0, 0, 0])  # games, wins, draws
        for i, r in enumerate(reader, start=2):
            seat = (r.get("seat") or "").strip().lower() or "any"
            if seat == "pooled":
                seat = "any"
            if seat not in SEATS:
                raise SystemExit(f"{path} line {i}: seat must be blank, any, first or second, not {seat!r}")
            key = (norm_path(r["deck_file"]), norm_path(r["opponent_file"]), r["pilot"].strip(), seat)
            g, w = to_int(r, "games", path, i), to_int(r, "wins", path, i)
            d = to_int(r, "draws", path, i) if "draws" in cols and (r.get("draws") or "").strip() else 0
            if g <= 0 or w < 0 or d < 0 or w + d > g:
                raise SystemExit(f"{path} line {i}: games={g} wins={w} draws={d} do not make sense")
            acc[key][0] += g
            acc[key][1] += w
            acc[key][2] += d
    sim = {}
    for key, (g, w, d) in acc.items():
        if draws_mode == "loss":
            p = w / g
        elif draws_mode == "half":
            p = (w + 0.5 * d) / g
        else:  # drop
            if g - d <= 0:
                raise SystemExit(f"sim row {key}: every game was a draw, cannot drop draws")
            p = w / (g - d)
        sim[key] = {"p": p, "games": g, "wins": w, "draws": d}
    return sim


def pick_pilot(sim, wanted):
    pilots = sorted({k[2] for k in sim})
    if wanted:
        if wanted not in pilots:
            raise SystemExit(f"--pilot {wanted!r} is not in the sim file (it has {pilots})")
        return wanted
    if len(pilots) == 1:
        return pilots[0]
    raise SystemExit(f"the sim file has several pilots {pilots}; pass --pilot")


def join(games, sim, pilot, warn):
    """Attach a sim win chance to every game it can; return (matched, missing_pairs)."""
    by_base = defaultdict(list)
    for key in sim:
        if key[2] == pilot:
            by_base[(os.path.basename(key[0]), os.path.basename(key[1]), key[3])].append(key)
    warned = set()

    def lookup(deck, opp, seat):
        key = (norm_path(deck), norm_path(opp), pilot, seat)
        if key in sim:
            return sim[key]
        cands = by_base.get((os.path.basename(key[0]), os.path.basename(key[1]), seat), [])
        if len(cands) == 1:
            if cands[0] not in warned:
                warned.add(cands[0])
                warn(f"note: matched {deck} vs {opp} by file name to sim row {cands[0][0]} vs {cands[0][1]}")
            return sim[cands[0]]
        if len(cands) > 1:
            raise SystemExit(f"ambiguous sim rows for {deck} vs {opp}: {cands}")
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
                            sim_draws=row["draws"], seat_used=used_seat))
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


def print_report(games, skipped, matched, missing, pilot, res, out=print):
    n = res["n"]
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


def main(argv=None):
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
    a = ap.parse_args(argv)
    if not 0 < a.clip < 0.5:
        raise SystemExit("--clip must be between 0 and 0.5")

    games, skipped = read_games(a.games)
    if not games:
        raise SystemExit(f"{a.games}: no usable games")
    sim = read_sim(a.sim, a.draws)
    pilot = pick_pilot(sim, a.pilot)
    notes = []
    matched, missing = join(games, sim, pilot, notes.append)
    if a.strict and missing:
        raise SystemExit("missing sim rows for: " + "; ".join(f"{d} vs {o}" for d, o in sorted(missing)))
    if not matched:
        raise SystemExit("no game could be joined to a sim row (check the paths in the sim file)")
    res = score(matched, a.clip, a.boot, a.seed)
    res.update(pilot=pilot, draws=a.draws, sim_file=a.sim, games_file=a.games,
               usable_games=len(games), skipped_rows=len(skipped), missing_games=sum(missing.values()),
               missing_pairs=[f"{d} vs {o}" for d, o in sorted(missing)], notes=notes,
               games_scored=[{k: v for k, v in m.items()} for m in matched])
    if not a.quiet:
        for note in notes:
            print(note)
        print_report(games, skipped, matched, missing, pilot, res)
    else:
        b = res.get("boot_brier_diff", {})
        print(json.dumps({"n": res["n"], "brier_sim": res["brier_sim"], "brier_base": res["brier_base"],
                          "brier_diff": res["brier_diff_base_minus_sim"], "llr_bits": res["llr_bits"],
                          "diff_p05": b.get("p05"), "diff_p95": b.get("p95")}))
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2)
        if not a.quiet:
            print(f"\nwrote {a.json}")
    return res


if __name__ == "__main__":
    main()
