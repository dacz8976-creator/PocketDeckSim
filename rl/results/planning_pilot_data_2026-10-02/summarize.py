"""The planning pilot's data (Oct 2): summary statistics of a pilot_data run.
Reads the rows (gzipped TSV) and the games (JSONL), and writes summary.txt and feature_stats.tsv next to this script.
- Rows and games, rows by kind of decision (own turn, setup, the move chosen).
- The outcome balance: wins, losses and ties by seat, by who went first, by list.
- The class check of the pool: each list's mean turn of its first attack and its mean game length (pool.tsv's classes).
- The feature ranges: min, max, mean, standard deviation, share non-zero and number of distinct values of every feature,
  and the features that are constant or nearly so ("dead").
- km's check: games whose rows' km terms didn't add up to km's value.
Usage: python3 summarize.py <rows.tsv.gz> <games.jsonl> [<run_stdout.txt>]"""
import csv, gzip, json, math, sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
rows_path, games_path = sys.argv[1], sys.argv[2]
stdout_path = sys.argv[3] if len(sys.argv) > 3 else None
META = ["pairing", "i", "seed", "tick", "seat", "deck", "opp_deck", "n_offered", "chosen_kind", "own_turn"]
LABELS = ["result", "final_points_mine", "final_points_opp", "final_turn", "game_ticks"]

games = [json.loads(l) for l in open(games_path, encoding="utf-8")]
pool = {l.split("\t")[0]: l.split("\t")[2] for l in (HERE / "pool.tsv").read_text(encoding="utf-8").splitlines()[1:]}
out = []
say = out.append

# The games.
n = len(games)
winners = Counter(g["winner"] for g in games)
first_wins = sum(1 for g in games if g["winner"] == g["first_player"])
say(f"games: {n}; seat 0 won {winners[0]}, seat 1 won {winners[1]}, ties {winners[-1]}; "
    f"the player going first won {first_wins} ({first_wins / max(1, n - winners[-1]):.1%} of decided games)")
say(f"km's check (the terms add up to km's value): games with a mismatch {sum(1 for g in games if g['km_check_bad'])}, "
    f"mismatched rows {sum(g['km_check_bad'] for g in games)}")
turns = [g["turns"] for g in games]
say(f"game length: mean {sum(turns) / n:.1f} turns (min {min(turns)}, max {max(turns)}); "
    f"mean {sum(g['ticks'] for g in games) / n:.1f} ticks")

# Per list: results, first attack turn, length.
per = defaultdict(lambda: {"games": 0, "wins": 0, "ties": 0, "first_attack": [], "no_attack": 0, "turns": []})
for g in games:
    for seat, deck in enumerate(g["decks"]):
        p = per[deck]
        p["games"] += 1
        p["wins"] += g["winner"] == seat
        p["ties"] += g["winner"] == -1
        p["turns"].append(g["turns"])
        t = g["first_attack_turn"][seat]
        if t is None:
            p["no_attack"] += 1
        else:
            p["first_attack"].append(t)
say("\nper list (class from pool.tsv): games, win rate, mean turn of its first attack (games with none), mean game length")
order = sorted(per, key=lambda d: (pool.get(d, "?"), sum(per[d]["first_attack"]) / max(1, len(per[d]["first_attack"]))))
for d in order:
    p = per[d]
    fa = p["first_attack"]
    say(f"  {pool.get(d, '?'):5} {d:38} {p['games']:5}  {p['wins'] / p['games']:.1%}  first attack {sum(fa) / max(1, len(fa)):.2f} "
        f"({p['no_attack']} none)  length {sum(p['turns']) / len(p['turns']):.1f}")
by_class = defaultdict(list)
for d in per:
    by_class[pool.get(d, "?")].extend(per[d]["first_attack"])
say("  by class, mean first attack turn: " + ", ".join(f"{c} {sum(v) / len(v):.2f}" for c, v in sorted(by_class.items())))

# The rows.
with gzip.open(rows_path, "rt", encoding="utf-8") as f:
    reader = csv.reader(f, delimiter="\t")
    header = next(reader)
    feats = [h for h in header if h not in META and h not in LABELS]
    idx = {h: k for k, h in enumerate(header)}
    stats = {h: {"n": 0, "sum": 0.0, "sq": 0.0, "min": math.inf, "max": -math.inf, "nonzero": 0, "distinct": set()} for h in feats}
    rows, kinds, own, setup, results = 0, Counter(), Counter(), Counter(), Counter()
    for r in reader:
        rows += 1
        kinds[r[idx["chosen_kind"]]] += 1
        own[r[idx["own_turn"]]] += 1
        setup[r[idx["setup"]]] += 1
        results[r[idx["result"]]] += 1
        for h in feats:
            v = float(r[idx[h]])
            s = stats[h]
            s["n"] += 1
            s["sum"] += v
            s["sq"] += v * v
            s["min"] = min(s["min"], v)
            s["max"] = max(s["max"], v)
            s["nonzero"] += v != 0
            if len(s["distinct"]) < 1000:
                s["distinct"].add(v)
say(f"\nrows: {rows} ({rows / n:.1f} a game); own turn {own['1']}, the opponent's turn {own['0']} (promotions and the like); "
    f"setup {setup['1']}")
say(f"rows by result for the mover: win {results['1']}, loss {results['0']}, tie {results['0.5']}")
say("rows by the move chosen: " + ", ".join(f"{k} {v}" for k, v in kinds.most_common()))
say(f"features: {len(feats)} (meta {len(META)}, labels {len(LABELS)})")

lines = ["feature\tmin\tmax\tmean\tsd\tnonzero_share\tdistinct"]
dead = []
for h in feats:
    s = stats[h]
    mean = s["sum"] / s["n"]
    sd = math.sqrt(max(0.0, s["sq"] / s["n"] - mean * mean))
    distinct = len(s["distinct"])
    lines.append(f"{h}\t{s['min']:g}\t{s['max']:g}\t{mean:.4g}\t{sd:.4g}\t{s['nonzero'] / s['n']:.4f}\t"
                 f"{distinct if distinct < 1000 else '1000+'}")
    if distinct <= 1:
        dead.append(f"{h} (constant {s['min']:g})")
    elif min(s["nonzero"], s["n"] - s["nonzero"]) / s["n"] < 0.001:
        dead.append(f"{h} (all but {min(s['nonzero'], s['n'] - s['nonzero'])} rows the same)")
(HERE / "feature_stats.tsv").write_text("\n".join(lines) + "\n", encoding="utf-8")
say(f"dead or nearly constant features ({len(dead)}): " + ("; ".join(dead) if dead else "none"))

if stdout_path:
    total = [l for l in open(stdout_path, encoding="utf-8") if l.startswith("total:")]
    say("\nthroughput: " + (total[-1].strip() if total else "not found"))
(HERE / "summary.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))
