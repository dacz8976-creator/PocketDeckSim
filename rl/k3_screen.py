"""Which matchups have room to measure a trained bot? k3 pilots both sides.
Run from the project root:
    python rl/k3_screen.py --games 100 --workers 8

Every deck in decks/dustin/ and decks/brews/ against every Limitless deck in the Sept 8 study
folder, half the games from each seat. This is a SCREEN, not a ranking: the project's rule is
that the simulator can't rank decks (it gets the favored side wrong about a third of the time).
What it's good for: finding matchups that are roughly even under k3 (35-65%), where a trained
bot has room to show it plays better or worse than k3, and avoiding hopeless ones.
"""
import argparse
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ROOT = HERE.parent  # the repo root (on the laptop this file sat two folders down)
META = ROOT / "decks/research"
SEED0 = 50_000_000
NOTE = ("READ THIS AS: which matchups leave room to measure a trained pilot (k3 roughly even, 35-65%).\n"
        "NOT a ranking of which decks are good: the simulator can't rank decks (project rule), and k3 piloting\n"
        "both sides is not how people play. About +/-10 points at 100 games.\n")


def play(task):
    from pdl_rl_env import engine_play
    mine, meta, seed, seat = task
    decks = (mine, meta) if seat == 0 else (meta, mine)
    try:
        w, pts, turns = engine_play(decks[0], decks[1], seed, ("k3", "k3"))
    except Exception as e:  # a deck the engine can't play
        return (mine, meta, seat, "error", str(e)[:120])
    res = "draw" if w == -1 else ("win" if w == seat else "loss")
    return (mine, meta, seat, res, turns)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=100, help="games per matchup (half per seat)")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--root", default=str(ROOT))
    a = ap.parse_args()
    root = Path(a.root)
    sub = root / "decks" if (root / "decks/dustin").exists() else root  # project layout or a flat copy
    mine = sorted((sub / "dustin").glob("*.txt")) + sorted((sub / "brews").glob("*.txt"))
    meta_dir = META if a.root == str(ROOT) else root / "meta"
    metas = sorted(meta_dir.glob("*.txt"))
    tasks = [(str(m), str(o), SEED0 + i, i % 2) for m in mine for o in metas for i in range(a.games)]
    t0 = time.time()
    with mp.get_context("spawn").Pool(a.workers) as pool:
        rows = pool.map(play, tasks, chunksize=10)
    table = {}
    for m, o, seat, res, extra in rows:
        key = (Path(m).stem, Path(o).stem)
        t = table.setdefault(key, {"win": 0, "loss": 0, "draw": 0, "error": 0, "seat0_wins": 0, "seat1_wins": 0,
                                   "err_msg": ""})
        t[res] += 1
        if res == "win":
            t[f"seat{seat}_wins"] += 1
        if res == "error":
            t["err_msg"] = extra
    out = {"note": NOTE, "games_per_matchup": a.games, "seconds": round(time.time() - t0), "matchups": []}
    for (m, o), t in sorted(table.items()):
        n = t["win"] + t["loss"] + t["draw"]
        out["matchups"].append(dict(t, deck=m, meta=o, games=n, win_rate=t["win"] / n if n else None))
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/k3_screen.json").write_text(json.dumps(out, indent=1))
    decks = sorted({r["deck"] for r in out["matchups"]})
    metas_s = sorted({r["meta"] for r in out["matchups"]})
    print(NOTE)
    print(f"k3 vs k3 win rate of each deck (rows) against each Limitless deck (columns), {a.games} games each")
    print(f"{'deck':<42}" + "".join(f"{x[:9]:>10}" for x in metas_s))
    for d in decks:
        cells = []
        for o in metas_s:
            r = next(x for x in out["matchups"] if x["deck"] == d and x["meta"] == o)
            cells.append(f"{'ERR':>10}" if r["win_rate"] is None else f"{r['win_rate']:>10.0%}")
        print(f"{d[:42]:<42}" + "".join(cells))


if __name__ == "__main__":
    main()
