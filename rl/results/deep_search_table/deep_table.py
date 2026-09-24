#!/usr/bin/env python3
"""Deeper-search table: the Limitless check's 28 pairings with k4 / k5 / k6 piloting BOTH sides.

Same decks, seeds and seat rule as the Sept 23 k3 table (results/limitless_check_2026-09-23.md):
seed = 72,000,000 + pairing index x 10,000 + i (i < games; pairings in alphabetical order), even i = first-named deck
in seat 0. So every k-level plays exactly the deals k3 played. Scored against the same Limitless numbers.

Resumable: re-running the same command skips finished games. Progress: STATUS.txt beside this file.
Nothing here trains anything or changes any engine, deck or earlier result.
"""
import argparse, hashlib, itertools, json, math, os, sys, time
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))           # the project folder
DECKS = os.path.join(ROOT, "Boss Folder", "competitive-deck-study-2026-09-08", "round-robin-checkpoint",
                     "reports", "research", "decks")
NAMES = ["altaria", "blaziken", "hydreigon", "lucario", "sceptile", "suicune", "vespiquen", "weezing"]
DECK_SHA = {"altaria": "435a2bebc567ca83", "blaziken": "fb08470e8801e93c", "hydreigon": "6ea0042236b48444",
            "lucario": "46a4820bc788b4fd", "sceptile": "7404c99e49161e68", "suicune": "7affe6530b8d096b",
            "vespiquen": "fc3a0ffd1997f202", "weezing": "c322fe64d6052bf9"}   # the auditor's fingerprints
MODULE_SHA = "0fee43ceaf9cf6bc15ed2319bb08c100397621a60703880cf26ace8f044a9101"  # add-on 0.7.2 engine module
SEED_BASE = 72_000_000
PAIRS = list(itertools.combinations(NAMES, 2))                                 # alphabetical, index = position
# Limitless (111 B4a tournaments, pulled Sept 23) W-L-T for the first-named deck, and k3 v k3 from the same file.
LIMITLESS = {("altaria", "blaziken"): (69, 23, 3), ("altaria", "hydreigon"): (74, 55, 6), ("altaria", "lucario"): (223, 84, 11),
    ("altaria", "sceptile"): (101, 105, 13), ("altaria", "suicune"): (76, 69, 5), ("altaria", "vespiquen"): (72, 117, 11),
    ("altaria", "weezing"): (33, 64, 5), ("blaziken", "hydreigon"): (33, 22, 6), ("blaziken", "lucario"): (63, 78, 3),
    ("blaziken", "sceptile"): (54, 10, 3), ("blaziken", "suicune"): (35, 22, 3), ("blaziken", "vespiquen"): (28, 6, 1),
    ("blaziken", "weezing"): (22, 23, 3), ("hydreigon", "lucario"): (78, 65, 6), ("hydreigon", "sceptile"): (30, 47, 3),
    ("hydreigon", "suicune"): (20, 39, 3), ("hydreigon", "vespiquen"): (35, 57, 3), ("hydreigon", "weezing"): (23, 26, 2),
    ("lucario", "sceptile"): (85, 141, 5), ("lucario", "suicune"): (91, 64, 3), ("lucario", "vespiquen"): (133, 57, 7),
    ("lucario", "weezing"): (74, 56, 6), ("sceptile", "suicune"): (49, 55, 3), ("sceptile", "vespiquen"): (41, 84, 2),
    ("sceptile", "weezing"): (51, 25, 4), ("suicune", "vespiquen"): (33, 92, 3), ("suicune", "weezing"): (50, 27, 4),
    ("vespiquen", "weezing"): (70, 13, 2)}
K3 = {("altaria", "blaziken"): 58.3, ("altaria", "hydreigon"): 57.0, ("altaria", "lucario"): 56.0, ("altaria", "sceptile"): 38.3,
    ("altaria", "suicune"): 39.0, ("altaria", "vespiquen"): 43.1, ("altaria", "weezing"): 37.5, ("blaziken", "hydreigon"): 65.5,
    ("blaziken", "lucario"): 46.9, ("blaziken", "sceptile"): 60.5, ("blaziken", "suicune"): 54.3, ("blaziken", "vespiquen"): 77.5,
    ("blaziken", "weezing"): 50.2, ("hydreigon", "lucario"): 30.2, ("hydreigon", "sceptile"): 29.2, ("hydreigon", "suicune"): 37.9,
    ("hydreigon", "vespiquen"): 29.9, ("hydreigon", "weezing"): 38.5, ("lucario", "sceptile"): 35.7, ("lucario", "suicune"): 52.4,
    ("lucario", "vespiquen"): 65.7, ("lucario", "weezing"): 52.1, ("sceptile", "suicune"): 57.0, ("sceptile", "vespiquen"): 66.1,
    ("sceptile", "weezing"): 73.2, ("suicune", "vespiquen"): 46.0, ("suicune", "weezing"): 62.7, ("vespiquen", "weezing"): 68.8}

_env = None


def deck_path(n):
    return os.path.join(DECKS, n + ".txt")


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def check_inputs():
    import pdl_rl_env
    mod = pdl_rl_env.__file__
    got = sha(mod)
    if got != MODULE_SHA:
        sys.exit(f"REFUSED: engine module {mod} has SHA-256 {got}, expected {MODULE_SHA} (add-on 0.7.2 on rules4)")
    for n in NAMES:
        g = sha(deck_path(n))
        if not g.startswith(DECK_SHA[n]):
            sys.exit(f"REFUSED: deck {n} has SHA-256 {g[:16]}, expected {DECK_SHA[n]} (the Sept 23 table's list)")


def init_worker():
    global _env
    from pdl_rl_env import RawEnv
    ids = sorted(set().union(*(set(RawEnv.deck_card_ids(deck_path(n))) for n in NAMES)))
    _env = RawEnv(ids, "v1")


def play(task):
    bot, p, i = task
    a, b = PAIRS[p]
    seed = SEED_BASE + p * 10_000 + i
    first_seat = 0 if i % 2 == 0 else 1
    da, db = (deck_path(a), deck_path(b)) if first_seat == 0 else (deck_path(b), deck_path(a))
    _env.reset(da, db, seed, [bot, bot])
    if not _env.done:
        raise RuntimeError(f"game did not finish: {bot} {a} v {b} seed {seed}")
    winner, points, turns = _env.result()
    score = 0.5 if winner == -1 else (1.0 if winner == first_seat else 0.0)
    return {"bot": bot, "pairing": p, "a": a, "b": b, "i": i, "seed": seed, "first_seat": first_seat,
            "winner_seat": winner, "points": list(points), "turns": turns, "score_first": score}


def load_done(path):
    done, rows = set(), []
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue          # a line cut off by an interruption; that game is replayed
                if (r["pairing"], r["i"]) not in done:
                    done.add((r["pairing"], r["i"]))
                    rows.append(r)
    return done, rows


def limitless_pct(key):
    w, l, t = LIMITLESS[key]
    n = w + l + t
    p = (w + 0.5 * t) / n
    return 100 * p, n, 196 * math.sqrt(p * (1 - p) / n)


def pearson(x, y):
    if len(x) < 3:
        return float("nan")
    mx, my = sum(x) / len(x), sum(y) / len(y)
    sx = math.sqrt(sum((v - mx) ** 2 for v in x))
    sy = math.sqrt(sum((v - my) ** 2 for v in y))
    if sx == 0 or sy == 0:
        return float("nan")
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


def score_table(sim, games_per):
    """sim: {pair: pct}. Same scoreboard as the Sept 23 check."""
    keys = [k for k in PAIRS if k in sim]
    lim = {k: limitless_pct(k) for k in keys}
    diffs = [sim[k] - lim[k][0] for k in keys]
    fav = sum(1 for k in keys if (sim[k] - 50) * (lim[k][0] - 50) > 0)
    clear = [k for k in keys if abs(lim[k][0] - 50) > lim[k][2]]
    clear_ok = sum(1 for k in clear if (sim[k] - 50) * (lim[k][0] - 50) > 0)
    beyond = 0
    for k in keys:
        pl, n, _ = lim[k]
        vs = (sim[k] / 100) * (1 - sim[k] / 100) / games_per[k]
        vl = (pl / 100) * (1 - pl / 100) / n
        if abs(sim[k] - pl) / 100 > 1.96 * math.sqrt(vs + vl):
            beyond += 1
    return {"pairings": len(keys), "correlation": pearson([sim[k] for k in keys], [lim[k][0] for k in keys]),
            "average_miss": sum(abs(d) for d in diffs) / len(diffs), "favorite_right": fav,
            "clear": len(clear), "clear_right": clear_ok, "beyond_chance": beyond}


def write_status(out_dir, bots, games, rates, started):
    lines = [f"Deeper-search table (k4 / k5 / k6 on both sides), updated {time.strftime('%Y-%m-%d %H:%M')}",
             f"28 pairings x {games} games per level, the Sept 23 k3 table's exact deals. Same command resumes.", ""]
    k3sc = score_table(K3, {k: 1000 for k in PAIRS})
    lines.append(f"k3 (Sept 23 table): correlation {k3sc['correlation']:.2f}, average miss {k3sc['average_miss']:.1f}, "
                 f"favorite right {k3sc['favorite_right']}/28, clear ones {k3sc['clear_right']}/{k3sc['clear']}, "
                 f"beyond chance {k3sc['beyond_chance']}")
    loaded = {bot: load_done(os.path.join(out_dir, f"{bot}_games.jsonl"))[1] for bot in bots}
    for bot in bots:
        rows = loaded[bot]
        n = len(rows)
        line = f"{bot}: {n:,} of {28 * games:,} games"
        if bot in rates:
            gps = rates[bot]
            left = 28 * games - n
            line += f" · {gps:.1f} games/sec · about {left / gps / 3600:.1f} h left" if gps > 0 and left else ""
        lines.append(line)
        per = {}
        for r in rows:
            per.setdefault(PAIRS[r["pairing"]], []).append(r["score_first"])
        full = {k: 100 * sum(v) / len(v) for k, v in per.items() if len(v) >= games}
        if full:
            sc = score_table(full, {k: games for k in full})
            k3sub = score_table({k: K3[k] for k in full}, {k: 1000 for k in full})
            lines.append(f"   on its {len(full)} finished pairings: correlation {sc['correlation']:.2f} (k3 on the same: "
                         f"{k3sub['correlation']:.2f}), average miss {sc['average_miss']:.1f} (k3 {k3sub['average_miss']:.1f}), "
                         f"favorite right {sc['favorite_right']}/{len(full)} (k3 {k3sub['favorite_right']}), "
                         f"clear ones {sc['clear_right']}/{sc['clear']} (k3 {k3sub['clear_right']}), "
                         f"beyond chance {sc['beyond_chance']} (k3 {k3sub['beyond_chance']})")
    lines += ["", "Per pairing (first deck's score): k3 | finished levels | Limitless (95%)"]
    for k in PAIRS:
        lp, n, hw = limitless_pct(k)
        parts = [f"k3 {K3[k]:5.1f}"]
        for bot in bots:
            s = [r["score_first"] for r in loaded[bot] if PAIRS[r["pairing"]] == k]
            if len(s) >= games:
                parts.append(f"{bot} {100 * sum(s) / len(s):5.1f}")
        lines.append(f"  {k[0]:>9} v {k[1]:<9} " + " | ".join(parts) + f" | Limitless {lp:5.1f} ± {hw:.1f} (n {n})")
    tmp = os.path.join(out_dir, "STATUS.txt.tmp")
    with open(tmp, "w") as f:
        f.write("\n".join(lines) + "\n")
    os.replace(tmp, os.path.join(out_dir, "STATUS.txt"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bots", default="k4,k5,k6")
    ap.add_argument("--games", type=int, default=1000)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", default=HERE)
    ap.add_argument("--only-pairing", type=int, default=None, help="check runs only")
    args = ap.parse_args()
    check_inputs()
    bots = args.bots.split(",")
    os.makedirs(args.out, exist_ok=True)
    rates, started = {}, time.time()
    write_status(args.out, bots, args.games, rates, started)
    with Pool(args.workers, initializer=init_worker) as pool:
        for bot in bots:
            path = os.path.join(args.out, f"{bot}_games.jsonl")
            done, _ = load_done(path)
            pairs = range(len(PAIRS)) if args.only_pairing is None else [args.only_pairing]
            tasks = [(bot, p, i) for p in pairs for i in range(args.games) if (p, i) not in done]
            print(f"{bot}: {len(tasks):,} games to play", flush=True)
            t0, n0, last = time.time(), 0, time.time()
            with open(path, "a") as f:
                for r in pool.imap_unordered(play, tasks, chunksize=4):
                    f.write(json.dumps(r) + "\n")
                    n0 += 1
                    if time.time() - last > 60:
                        f.flush()
                        rates[bot] = n0 / (time.time() - t0)
                        write_status(args.out, bots, args.games, rates, started)
                        last = time.time()
            rates[bot] = n0 / max(1e-9, time.time() - t0)
            write_status(args.out, bots, args.games, rates, started)
            print(f"{bot}: finished", flush=True)
    print("All levels finished. Results: STATUS.txt", flush=True)


if __name__ == "__main__":
    main()
