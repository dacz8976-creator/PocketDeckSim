"""How much does the pilot change Dustin's Raticate brews? k3 against kp3 piloting decks 13, 14 and 15 (each runs Team
Rocket's Raticate ex, whose Thieving Incisors k3 leaves unpriced under its opponent-hand text rule; kp prices it), with
the opponent k3; plus a third row, kp3 on both sides (Fable's addition: does the number move again when the meta side
prices too, the screen question (iii)). Diagnostic only. Inside WSL, from the rl folder:
    PDL_ADDON_DIR=<folder holding the diagnostic pdl_rl_env.abi3.so> \
    python results/brew_pilot_check_2026-09-25/brew_pilot.py [--deals 200] [--workers 8]

Needs kp3, so it runs on the scratch diagnostic add-on (engine at c7cb688; see
results/hydreigon_network_readout/READING.md for its conditions). The engine's own CLI at c7cb688 would give win rates
but its per-game output keeps only a hash of the moves, so it can't count Thieving Incisors or Copycat; the add-on can.
All rows run on that one build, so the comparison is within one engine. For each deal the engine's own loop plays the game and records the brew's choices
(engine_play_record); the game is replayed through the add-on (the opponent's k3 re-deciding) to classify the brew's
decisions, and counts only if the replay equals the engine loop's game (winner and turns).

Counted per brew turn: Thieving Incisors on offer (a UseAbility of a Team Rocket's Raticate ex) and used; Copycat on
offer and played (kp also prices Copycat's text, so the two are kept apart).

Seeds: 21,030,000,000 + brew x 1,000,000 + opponent x 10,000 + i, i < --deals, the brew in seat 0 on even i. The same
deals for all three rows (paired).

READING, set before any game was played (Sept 25, about 06:10 CDT; the third row added about 06:15, still before any
game): descriptive only. Rows are (brew pilot | opponent pilot): k3|k3, kp3|k3, kp3|kp3, on the same deals.
  kp3|k3 minus k3|k3: how much k3's text rule (and anything else kp prices) understates the brew against k3 opponents;
  the Thieving Incisors and Copycat rates say where it comes from.
  kp3|kp3 minus kp3|k3: whether the number moves again when the meta side prices too.
Nothing here is a table or a deck ranking.

Options added after the Raticate run (06:30; its defaults and results unchanged): --brews all (every deck in
decks/dustin), --rows (e.g. "k3|k3,kp3|k3"), --seed0. The all-decks run's reading, set before its first game: the
same "pilot" difference per brew, descriptive only; it says which of Dustin's brews' simulator numbers depend on the
pilot, and by how much, not how good any brew is.

Added about 09:20 for the A2 screen re-run (RUN5, the plan revised Sept 25): --brews also takes repo-relative deck
paths (e.g. decks/brews/brew-07-hoopa-darkrai-sableye.txt) and the token "all"; a 'both' column (kp3|kp3 - k3|k3);
and a closing screen summary against decks/screen/results.md's bar. The opponents are decks/research, identical card
for card to decks/screen/opponents (checked). READING for that re-run, set before its first game: the screen's own
anchors must hold with kp3 on both sides for the screen to be usable again: the two Payback decks (brew-06, brew-06b;
0-3 each on the ladder) under 20%, Skarmory stall (07; 3-1) at 45% or more, brew-05b (3-3) at 20% or more. The bar
(under 20% = broken) is unchanged; brews whose side of the bar differs between k3|k3 and kp3|kp3 are listed.
Descriptive otherwise; not a ranking. Dustin decides the A2 hold on it.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import sys  # noqa: E402

ADDON_DIR = os.environ.get("PDL_ADDON_DIR")
if not ADDON_DIR:
    raise SystemExit("set PDL_ADDON_DIR to the folder holding the diagnostic pdl_rl_env.abi3.so (kp3 is needed)")
_dir = os.path.abspath(os.path.expanduser(ADDON_DIR))
sys.path.insert(0, _dir)
import pdl_rl_env  # noqa: E402

if not os.path.abspath(pdl_rl_env.__file__).startswith(_dir):
    raise SystemExit(f"pdl_rl_env came from {pdl_rl_env.__file__}, not PDL_ADDON_DIR")

import argparse  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import multiprocessing as mp  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
RL = HERE.parents[1]
ROOT = RL.parent
sys.path.insert(0, str(RL))
from pdl_env import PocketEnv  # noqa: E402
from pdl_rl_env import engine_play_record  # noqa: E402

BREWS = ["13-a-ninetales-raticate", "14-comfey-raticate-hypno", "15-jolteon-oricorio-raticate"]
OPPS = ["altaria", "blaziken", "hydreigon", "lucario", "sceptile", "suicune", "vespiquen", "weezing"]
ROWS = ("k3|k3", "kp3|k3", "kp3|kp3")   # brew pilot | opponent pilot
SEED0 = 21_030_000_000
_W = {}


def bpath(b):
    return str(ROOT / b) if "/" in b else str(ROOT / "decks/dustin" / f"{b}.txt")


def label(b):
    return Path(b).stem if "/" in b else b


def opath(o):
    return str(ROOT / "decks/research" / f"{o}.txt")


def _init(brews, seed0):
    BREWS[:] = brews
    global SEED0
    SEED0 = seed0
    env = PocketEnv(vocab_deck_paths=[bpath(b) for b in BREWS] + [opath(o) for o in OPPS], features="v2.2")
    env.reset(bpath(BREWS[0]), opath(OPPS[0]), 1)
    _W["env"] = env


def look(env, p, mv):
    acts = [json.loads(a) for a in env.raw.legal_actions_json()]
    me = json.loads(env.raw.describe(p))["me"]["board"]
    ti = [i for i, a in enumerate(acts) if isinstance(a, dict) and "UseAbility" in a
          and "Raticate" in ((me[a["UseAbility"]["in_play_idx"]] or {}).get("name") or "")]
    cc = [i for i, a in enumerate(acts) if isinstance(a, dict) and "Play" in a and "Copycat" in json.dumps(a["Play"])]
    return {"turn": json.loads(env.raw.describe(p))["turn"], "ti_on": bool(ti), "ti": mv in ti,
            "cc_on": bool(cc), "cc": mv in cc}


def play(task):
    b, o, i, row = task
    pilot, opp_pilot = row.split("|")
    seed = SEED0 + b * 1_000_000 + o * 10_000 + i
    brew_seat = i % 2
    paths = [bpath(BREWS[b]), opath(OPPS[o])] if brew_seat == 0 else [opath(OPPS[o]), bpath(BREWS[b])]
    codes = (pilot, opp_pilot) if brew_seat == 0 else (opp_pilot, pilot)
    try:
        rec, _prints, _h, res = engine_play_record(paths[0], paths[1], seed, codes, brew_seat)
    except Exception as e:  # a card the engine can't load or play: reported, never hidden
        return {"b": b, "o": o, "i": i, "row": row, "ok": False, "error": repr(e)[:200]}
    env = _W["env"]
    env.reset(paths[0], paths[1], seed, bots=[None, opp_pilot] if brew_seat == 0 else [opp_pilot, None])
    recs, n = [], 0
    while not env.done:
        if n >= len(rec) or env.current_player != brew_seat:
            return {"b": b, "o": o, "i": i, "row": row, "ok": False, "error": "replay diverged"}
        recs.append(look(env, brew_seat, rec[n]))
        env.step(rec[n])
        n += 1
    w, _pts, turns = env.result()
    turns_ = {}
    for r in recs:
        turns_.setdefault(r["turn"], []).append(r)
    c = {"ti_on": 0, "ti": 0, "cc_on": 0, "cc": 0}
    for ds in turns_.values():
        c["ti_on"] += any(r["ti_on"] for r in ds)
        c["ti"] += any(r["ti"] for r in ds)
        c["cc_on"] += any(r["cc_on"] for r in ds)
        c["cc"] += any(r["cc"] for r in ds)
    return {"b": b, "o": o, "i": i, "row": row, "ok": n == len(rec) and (w, turns) == (res[0], res[2]),
            "won": float(w == brew_seat), "draw": w == -1, "count": c}


def main():
    global ROWS, SEED0
    ap = argparse.ArgumentParser()
    ap.add_argument("--deals", type=int, default=200)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", default=str(HERE / "brew_pilot.txt"))
    ap.add_argument("--brews", default=None, help="comma list of decks/dustin names, or 'all'; default the three Raticate brews")
    ap.add_argument("--rows", default=",".join(ROWS), help="comma list of brew|opponent pilot rows; k3|k3 must be one")
    ap.add_argument("--seed0", type=int, default=SEED0)
    a = ap.parse_args()
    if a.brews:
        picked = []
        for tok in a.brews.split(","):
            picked += sorted(p.stem for p in (ROOT / "decks/dustin").glob("*.txt")) if tok == "all" else [tok]
        BREWS[:] = list(dict.fromkeys(picked))
    ROWS = tuple(a.rows.split(","))
    SEED0 = a.seed0
    if "k3|k3" not in ROWS or any(r.split("|")[0] not in ("k3", "kp3") or r.split("|")[1] not in ("k3", "kp3") for r in ROWS):
        raise SystemExit(f"--rows {a.rows}: each row is <k3|kp3>|<k3|kp3>, and k3|k3 must be one of them")
    missing = [b for b in BREWS if not Path(bpath(b)).exists()]
    if missing:
        raise SystemExit(f"no such deck (a name in decks/dustin, or a repo-relative path): {missing}")
    t0 = time.time()
    tasks = [(b, o, i, r) for b in range(len(BREWS)) for o in range(len(OPPS)) for i in range(a.deals) for r in ROWS]
    with mp.get_context("spawn").Pool(a.workers, initializer=_init, initargs=(list(BREWS), SEED0)) as pool:
        res = pool.map(play, tasks, chunksize=4)
    by = {(r["b"], r["o"], r["i"], r["row"]): r for r in res}
    errors = [r for r in res if not r["ok"]]
    sha = hashlib.sha256(Path(pdl_rl_env.__file__).read_bytes()).hexdigest()
    what = "Raticate brews" if len(BREWS) == 3 and BREWS[0].startswith("13-") else f"{len(BREWS)} brews"
    L = [f"Brew pilot check: Dustin's {what} under k3 and kp3   ({time.strftime('%Y-%m-%d %H:%M')})", "",
         f"Diagnostic add-on {pdl_rl_env.__file__} sha256 {sha} (engine at c7cb688; not the verified 0.7.2 wheel).",
         f"{a.deals} paired deals per matchup, seeds {SEED0:,} + brew x 1,000,000 + opponent x 10,000 + i. Games that did "
         f"not replay exactly or raised an error: {len(errors)} of {len(res):,}; a deal counts only when all {len(ROWS)} "
         f"rows' games are clean.", "",
         "Rows are brew pilot | opponent pilot. The brew's win % in each row; three paired differences (95% interval):",
         "  'pilot' = kp3|k3 - k3|k3 (what k3 understates, against k3 opponents);",
         "  'meta'  = kp3|kp3 - kp3|k3 (does it move again when the meta side prices too);",
         "  'both'  = kp3|kp3 - k3|k3 (kp3 on both sides against k3 on both sides).",
         "Per brew turn where Thieving Incisors (TI) / Copycat was on offer: turns the brew used it / turns on offer.", ""]
    hdr = (f"  {'brew v opponent':<34}{'n':>5}{'k3|k3':>7}{'kp3|k3':>8}{'kp3|kp3':>9}{'pilot':>14}{'meta':>14}{'both':>14}"
           f"   {'TI k3|k3':>13}{'TI kp3|k3':>13}{'TI kp3|kp3':>13}   {'Copycat k3|k3':>14}{'Copycat kp3|k3':>15}")
    L.append(hdr)

    def agg(keys):
        good = [k for k in keys if all(by.get((*k, r), {}).get("ok") for r in ROWS)]
        if not good:
            return None
        w = {r: np.array([by[(*k, r)]["won"] for k in good]) for r in ROWS}

        def diff(x, y):
            if x not in w or y not in w:
                return float("nan"), float("nan")
            d = w[x] - w[y]
            return 100 * d.mean(), (1.96 * 100 * d.std(ddof=1) / math.sqrt(len(d)) if len(d) > 1 else float("nan"))
        cs = {r: {x: sum(by[(*k, r)]["count"][x] for k in good) for x in ("ti_on", "ti", "cc_on", "cc")} for r in ROWS}
        f = lambda c, u, on: f"{c[u]}/{c[on]}" + (f" {100 * c[u] / c[on]:.0f}%" if c[on] else "")  # noqa: E731
        every = ("k3|k3", "kp3|k3", "kp3|kp3")
        return (len(good), {r: 100 * w[r].mean() if r in w else float("nan") for r in every},
                diff("kp3|k3", "k3|k3"), diff("kp3|kp3", "kp3|k3"), diff("kp3|kp3", "k3|k3"),
                [f(cs[r], "ti", "ti_on") if r in cs else "—" for r in every],
                [f(cs[r], "cc", "cc_on") if r in cs else "—" for r in every[:2]])

    def row(label, v):
        if v is None:
            return f"  {label:<34}  no clean deals"
        n, won, (p, ph), (m, mh), (bo, bh), ti, cc = v
        return (f"  {label:<34}{n:>5}{won['k3|k3']:>7.1f}{won['kp3|k3']:>8.1f}{won['kp3|kp3']:>9.1f}"
                f"{p:>+8.1f} ±{ph:<4.1f}{m:>+8.1f} ±{mh:<4.1f}{bo:>+8.1f} ±{bh:<4.1f}"
                f"   {ti[0]:>13}{ti[1]:>13}{ti[2]:>13}   {cc[0]:>14}{cc[1]:>15}")

    totals = {}
    for b, brew in enumerate(BREWS):
        for o, opp in enumerate(OPPS):
            L.append(row(f"{label(brew)[:21]} v {opp}", agg([(b, o, i) for i in range(a.deals)])))
        totals[brew] = agg([(b, o, i) for o in range(len(OPPS)) for i in range(a.deals)])
        L += [row(f"{label(brew)[:21]} v all eight", totals[brew]), ""]
    if "kp3|kp3" in ROWS:
        L += ["Screen summary (decks/screen/results.md's bar: under 20% against the panel = broken), panel win %:",
              f"  {'brew':<40}{'k3|k3':>8}{'kp3|kp3':>9}{'both':>14}   side of the bar"]
        for brew, v in totals.items():
            if v is None:
                continue
            k, kp, (bo, bh) = v[1]["k3|k3"], v[1]["kp3|kp3"], v[4]
            side = lambda x: "under 20" if x < 20 else "20+"  # noqa: E731
            flip = "" if side(k) == side(kp) else "   FLIPS"
            L.append(f"  {label(brew)[:40]:<40}{k:>8.1f}{kp:>9.1f}{bo:>+8.1f} ±{bh:<4.1f}   {side(k)} -> {side(kp)}{flip}")
        L.append("")
    if errors:
        kinds = {}
        for r in errors:
            kinds[r.get("error", "not exact")] = kinds.get(r.get("error", "not exact"), 0) + 1
        L += ["Unclean games by reason: " + "; ".join(f"{k} x{v}" for k, v in sorted(kinds.items(), key=lambda x: -x[1])[:5]), ""]
    L.append(f"Took {time.time() - t0:.0f} s with {a.workers} workers; {len(res):,} games.")
    text = "\n".join(L) + "\n"
    print(text)
    out = Path(a.out)
    if out.exists():
        out = out.with_name(f"{out.stem}_{time.strftime('%Y%m%d-%H%M%S')}{out.suffix}")
    out.write_text(text)
    print(f"Written: {out}")


if __name__ == "__main__":
    main()
