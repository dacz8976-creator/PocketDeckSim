"""Is the Hydreigon network's +40.8 more than pricing? Fable's decisive row, with its reading set before any row was
played (Sept 25, about 05:50 CDT). Inside WSL, from the rl folder:
    PDL_ADDON_DIR=<folder holding the diagnostic pdl_rl_env.abi3.so> \
    python results/hydreigon_network_readout/kp3_rows.py --run runs/diag-hydreigon-lucario [--games 2000] [--workers 8]

Why a diagnostic add-on: kp (public pricing) came after the verified 0.7.2 wheel, so the wheel can't pilot kp3. The
add-on source (rl/pdl_rl_env, identical on main and at c7cb688) is built against the engine at c7cb688 (kp3's
tier-1-sound state, the one its table ran on) into a scratch folder. The verified wheel, the run5 venv and run
identities are untouched; PDL_ADDON_DIR only puts the scratch build first on this script's path.
Before anything is read, the build must replay the run's own games exactly, on the first --identity-games deals:
  k3 v k3 = the bar rows (winner, turns); network Hydreigon v k3 Lucario = the confirmation rows (winner, turns and
  every move). Any mismatch stops the script before the kp3 rows are played.

Rows (row = who pilots Hydreigon | who pilots Lucario), all on the run's bar deals, Hydreigon's win %:
  k3|k3 and net|k3 are the run's own recorded games (bars and confirmation; the network is the confirmed
  hydreigon checkpoint in state.json); net|kp3, kp3|kp3 and kp3|k3 are played here. The network picks as
  eval_chunk does (rng seeded with the deal's seed).

READING, set before any row was played:
  Decisive: net|kp3 minus kp3|kp3, paired over the deals: how much better the network pilots Hydreigon than kp3
  does, against a Lucario that prices Darkness Claw. RUN5's 10-point line, reused:
    +10 or more -> the network plays Hydreigon better than kp3 even against a Lucario that sees Darkness Claw
                   coming: play beyond pricing, which B2c's divergence mining can name (a later step).
    under +10   -> most of the +40.8 is what kp3's pricing already gives Hydreigon plus what k3's blind Lucario
                   gives away; no further network work on this pair.
  Everything else is descriptive.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import sys  # noqa: E402

ADDON_DIR = os.environ.get("PDL_ADDON_DIR")
if not ADDON_DIR:
    raise SystemExit("set PDL_ADDON_DIR to the folder holding the diagnostic pdl_rl_env.abi3.so")
sys.path.insert(0, os.path.abspath(os.path.expanduser(ADDON_DIR)))
import pdl_rl_env  # noqa: E402

if not os.path.abspath(pdl_rl_env.__file__).startswith(os.path.abspath(os.path.expanduser(ADDON_DIR))):
    raise SystemExit(f"pdl_rl_env came from {pdl_rl_env.__file__}, not PDL_ADDON_DIR")

import argparse  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import multiprocessing as mp  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import readout as R  # noqa: E402  (imports train_v5 as R.T, which now uses the add-on imported above)

T = R.T
FOCUS, OPP = "hydreigon", "lucario"
LIMITLESS = (54.4, 8.0)   # Hydreigon v Lucario, results/limitless_check_2026-09-23.md
PLAYED = ("net|kp3", "kp3|kp3", "kp3|k3")
_W = {}


def _init(S, net_path):
    T.set_decks(S)
    env = T.make_env()
    _W.update(env=env, net=T.load_scorer(net_path, env.obs_dim + env.action_dim))


def play(task):
    """One deal. row 'H|L': H pilots Hydreigon, L pilots Lucario; 'net' = the confirmed Hydreigon network."""
    row, g = task
    env, net = _W["env"], _W["net"]
    d0, d1 = g["decks"]
    fseat = g["decks"].index(FOCUS)
    h, l = row.split("|")
    bots = [None, None]
    bots[fseat] = None if h == "net" else h
    bots[1 - fseat] = l
    rng = np.random.default_rng(g["seed"])   # as eval_chunk
    env.reset(T.DECKS["paths"][d0], T.DECKS["paths"][d1], g["seed"], bots=bots)
    moves = []
    while not env.done:
        if h != "net" or env.current_player != fseat:
            return {"row": row, "seed": g["seed"], "error": f"decision for seat {env.current_player}"}
        obs, feats = env.observe(fseat), env.action_features()
        i = T.pick(net.score_actions(obs, feats), rng)
        moves.append(i)
        env.step(i)
    w, pts, turns = env.result()
    return {"row": row, "seed": g["seed"], "decks": g["decks"], "winner": w, "points": list(pts), "turns": turns,
            "moves": moves}


def won(g):
    return float(g["winner"] == g["decks"].index(FOCUS))


def score(g):
    return 1.0 if won(g) else (0.5 if g["winner"] == -1 else 0.0)


def paired(label, a, b, seeds):
    d = np.array([won(a[s]) - won(b[s]) for s in seeds])
    n = len(d)
    half = 1.96 * d.std(ddof=1) / math.sqrt(n)
    only_a, only_b = int((d > 0).sum()), int((d < 0).sum())
    return 100 * d.mean(), (f"  {label:<58}{100 * d.mean():>+7.1f} ± {100 * half:<5.1f}"
                            f"{only_a:>7} / {only_b:<6}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--games", type=int, default=2000)
    ap.add_argument("--identity-games", type=int, default=200)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", default=str(HERE / "kp3_rows.txt"))
    a = ap.parse_args()
    t0 = time.time()
    run_dir = Path(a.run) if Path(a.run).is_absolute() else T.HERE / a.run
    S = json.loads((run_dir / "settings.json").read_text())
    st = json.loads((run_dir / "state.json").read_text())
    T.check_decks_unchanged(run_dir, S)
    pick = st["verdict"]["picks"][FOCUS]
    net_path = str(T.ckpt_path(run_dir, pick, FOCUS))
    rows = [json.loads(x) for x in (run_dir / "eval_games.jsonl").read_text().splitlines()
            if '"kind": "bar"' in x or '"kind": "confirmation"' in x]
    pair = sorted([FOCUS, OPP])
    bars = {g["seed"]: g for g in rows if g["kind"] == "bar" and sorted(g["decks"]) == pair}
    conf = {g["seed"]: g for g in rows if g["kind"] == "confirmation" and g.get("ckpt") == pick
            and g.get("deck") == FOCUS}
    seeds = sorted(bars)[:a.games]
    if any(s not in conf or conf[s]["decks"] != bars[s]["decks"] for s in seeds):
        raise SystemExit("the confirmation rows don't cover the bar deals one for one")
    deal = {s: {"seed": s, "decks": bars[s]["decks"]} for s in seeds}
    ids = seeds[:a.identity_games]

    L = [f"Hydreigon network v kp3 rows — {run_dir.name}   ({time.strftime('%Y-%m-%d %H:%M')})", "",
         f"Diagnostic add-on: {pdl_rl_env.__file__} sha256 {T.sha_file(pdl_rl_env.__file__)[:12]} (not the verified "
         f"0.7.2 wheel; built against the engine at c7cb688 for kp3). Network: {Path(net_path).name} "
         f"{T.sha_file(net_path)[:12]} (state.json's confirmed {FOCUS} checkpoint).", ""]
    with mp.get_context("spawn").Pool(a.workers, initializer=_init, initargs=(S, net_path)) as pool:
        # 1. identity: the build must replay the run's own games exactly
        got = pool.map(play, [("k3|k3", deal[s]) for s in ids] + [("net|k3", deal[s]) for s in ids], chunksize=4)
        bad = [r for r in got if "error" in r]
        idk = {r["seed"]: r for r in got if r["row"] == "k3|k3" and "error" not in r}
        idn = {r["seed"]: r for r in got if r["row"] == "net|k3" and "error" not in r}
        same_bar = sum(s in idk and (idk[s]["winner"], idk[s]["turns"]) == (bars[s]["winner"], bars[s]["turns"])
                       for s in ids)
        same_conf = sum(s in idn and (idn[s]["winner"], idn[s]["turns"], idn[s]["moves"])
                        == (conf[s]["winner"], conf[s]["turns"], conf[s]["moves"]) for s in ids)
        L += [f"Identity, first {len(ids)} deals: k3 v k3 equals the bar rows in {same_bar} of {len(ids)} (winner, turns);",
              f"  network v k3 equals the confirmation rows in {same_conf} of {len(ids)} (winner, turns, every move)."
              + (f" Errors: {len(bad)}." if bad else "")]
        if bad or same_bar != len(ids) or same_conf != len(ids):
            L.insert(0, "STOPPED: the diagnostic build does not replay the run's games; nothing below was played.")
            text = "\n".join(L) + "\n"
            print(text)
            R.free_name(Path(a.out)).write_text(text)
            raise SystemExit(1)
        # 2. the kp3 rows
        res = pool.map(play, [(row, deal[s]) for row in PLAYED for s in seeds], chunksize=4)
    bad = [r for r in res if "error" in r]
    if bad:
        raise SystemExit(f"{len(bad)} games asked the network for a Lucario decision or similar: {bad[0]}")
    G = {"k3|k3": bars, "net|k3": conf}
    for row in PLAYED:
        G[row] = {r["seed"]: r for r in res if r["row"] == row}

    L += ["", f"Deals: the run's bar deals, {len(seeds):,} (seed {seeds[0]:,} to {seeds[-1]:,}), bar seats.", "",
          f"  {'Hydreigon | Lucario pilots':<32}{'n':>6}{'won %':>8}{'draws':>7}{'score %':>9}   Limitless {LIMITLESS[0]} ± {LIMITLESS[1]}"]
    for row in ("k3|k3", "net|k3", "kp3|k3", "kp3|kp3", "net|kp3"):
        g = G[row]
        tag = " (recorded)" if row in ("k3|k3", "net|k3") else ""
        L.append(f"  {row + tag:<32}{len(seeds):>6}{100 * np.mean([won(g[s]) for s in seeds]):>8.1f}"
                 f"{sum(g[s]['winner'] == -1 for s in seeds):>7}{100 * np.mean([score(g[s]) for s in seeds]):>9.1f}")
    L += ["", f"Paired differences in Hydreigon's win % (95% interval = 1.96 x sd of the per-deal difference / sqrt n; "
              f"'won only' = deals won in the first row and not the second / the reverse):",
          f"  {'':<58}{'points':>7}{'':>8}{'won only':>14}"]
    dec, line = paired("DECISIVE net|kp3 - kp3|kp3 (network v kp3, Lucario sees)", G["net|kp3"], G["kp3|kp3"], seeds)
    L.append(line)
    for lab, x, y in (("net|k3 - k3|k3 (the run's margin, recomputed)", "net|k3", "k3|k3"),
                      ("kp3|k3 - k3|k3 (kp3's edge over k3, Lucario blind)", "kp3|k3", "k3|k3"),
                      ("net|k3 - kp3|k3 (network v kp3, Lucario blind)", "net|k3", "kp3|k3"),
                      ("net|k3 - net|kp3 (what Lucario's pricing takes from the net)", "net|k3", "net|kp3"),
                      ("kp3|k3 - kp3|kp3 (what it takes from kp3's Hydreigon)", "kp3|k3", "kp3|kp3")):
        L.append(paired(lab, G[x], G[y], seeds)[1])
    L += ["", "READING (set before any row was played; RUN5's 10-point line, reused):",
          f"  net|kp3 minus kp3|kp3 = {dec:+.1f} points: "
          + ("+10 or more -> the network plays Hydreigon better than kp3 even against a Lucario that sees Darkness "
             "Claw coming: play beyond pricing, which B2c's divergence mining can name (a later step)."
             if dec >= 10 else
             "under +10 -> most of the +40.8 is what kp3's pricing already gives Hydreigon plus what k3's blind "
             "Lucario gives away; no further network work on this pair."),
          "  Everything else above is descriptive.", "",
          f"Took {time.time() - t0:.0f} s with {a.workers} workers; played {2 * len(ids)} identity games and "
          f"{len(res):,} kp3-row games."]
    text = "\n".join(L) + "\n"
    print(text)
    out = R.free_name(Path(a.out))
    out.write_text(text)
    games = R.free_name(out.with_name(out.stem + "_games.jsonl"))
    with open(games, "w") as f:
        for r in res:
            f.write(json.dumps(r) + "\n")
    print(f"Written: {out}\n         {games}")


if __name__ == "__main__":
    main()
