"""The decisive comparison, played against kp3: PRESET_READING.md item 2 for the Altaria detector network (default), or
the Hydreigon run's kp3 rows unchanged with --preset hydreigon. This is results/hydreigon_network_readout/kp3_rows.py
with the decks, the Limitless value and the reading's wording made options (readout.py's preset options). Inside WSL,
from the rl folder, with the run5 venv's python:
    PDL_ADDON_DIR=/home/dacz8976/diag-kp-addon/module \
    nice -n 19 python results/altaria_network_readout/kp3_rows.py --run runs/diag-altaria-lucario [--games 2000] [--workers 3]

Why a diagnostic add-on: kp (public pricing) came after the verified 0.7.2 wheel, so the wheel can't pilot kp3. The
add-on source (rl/pdl_rl_env, identical on main and at c7cb688) is built against the engine at c7cb688 (kp3's
tier-1-sound state, the one its table ran on) into a scratch folder. The verified wheel, the run5 venv and run
identities are untouched; PDL_ADDON_DIR only puts the scratch build first on this script's path, and the script stops
unless the imported module's sha256 is the one the Hydreigon readout used (readout.DIAG_ADDON_SHA, c048388b...;
READING.md there). There is no option to accept another build.
Before anything is read, the build must replay the run's own games exactly, on the first --identity-games deals:
  k3 v k3 = the bar rows (winner, turns); network v k3 = the confirmation rows (winner, turns and every move).
  Any mismatch stops the script before the kp3 rows are played.
--precheck plays only the k3 v k3 half of that gate and stops. It needs no network, so it can run before the run has
its verdict (an early warning that the diagnostic build replays this pair's bars); it prints match counts only.

Rows (row = who pilots the focus deck | who pilots the other), all on the run's bar deals, the focus deck's win %:
  k3|k3 and net|k3 are the run's own recorded games (bars and confirmation; the network is the confirmed focus
  checkpoint in state.json); net|kp3, kp3|kp3 and kp3|k3 are played here. The network picks as eval_chunk does
  (rng seeded with the deal's seed). In net|kp3 the network's play is also counted with readout.py's audit
  (PRESET_READING item 3, the network against kp3), which reads the game and never changes it.

READING (altaria), PRESET_READING.md item 2, fixed before training: D = (network Altaria v kp3 Lucario) - (kp3 Altaria
v kp3 Lucario), Altaria's win %, paired over the run's 2,000 bar deals, bar seats.
  D is taken from the exact counts (deals won only with the network minus only with kp3, over the deals), so exactly
  +10.00 counts as "+10 or more".
    +10 or more -> the network plays Altaria better than kp3 even against a Lucario that prices its hidden-text cards.
                   Its habits are then audited (step 3) to name the difference. That difference is a candidate cause
                   of Altaria's gap and a B5 feature candidate, registered and read on its own.
    under +10   -> learning finds no large Altaria piloting gain in this matchup. Altaria's gap is then unlikely to be
                   a piloting blind spot that play can reveal. The leads that remain are card or rules implementation
                   (a card check of the Altaria list's texts in the engine) and the population, neither tested by
                   this run.
  Also printed: the run's own RUN5 line (PRESET item 1: the network's confirmed margin over k3, +10 or more = a gain).
READING (hydreigon), set before any row was played (Sept 25, about 05:50 CDT): net|kp3 minus kp3|kp3, RUN5's
10-point line reused; +10 or more -> play beyond pricing; under +10 -> most of the +40.8 is pricing plus what k3's
blind Lucario gives away.
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
PLAYED = ("net|kp3", "kp3|kp3", "kp3|k3")
# the diagnostic build the Hydreigon readout used (results/hydreigon_network_readout/READING.md); fixed, no option
ADDON_SHA = R.DIAG_ADDON_SHA
_W = {}


def _init(S, net_path, focus, A):
    T.set_decks(S)
    env = T.make_env()
    net = T.load_scorer(net_path, env.obs_dim + env.action_dim) if net_path else None
    _W.update(env=env, net=net, focus=focus, audit=A)
    R._W.update(audit=A)   # readout.look() reads the audit spec from there


def play(task):
    """One deal. row 'F|O': F pilots the focus deck, O the other; 'net' = the confirmed focus network."""
    row, g = task
    env, net, focus, A = _W["env"], _W["net"], _W["focus"], _W["audit"]
    d0, d1 = g["decks"]
    fseat = g["decks"].index(focus)
    h, l = row.split("|")
    bots = [None, None]
    bots[fseat] = None if h == "net" else h
    bots[1 - fseat] = l
    rng = np.random.default_rng(g["seed"])   # as eval_chunk
    env.reset(T.DECKS["paths"][d0], T.DECKS["paths"][d1], g["seed"], bots=bots)
    moves, recs = [], []
    while not env.done:
        if h != "net" or env.current_player != fseat:
            return {"row": row, "seed": g["seed"], "error": f"decision for seat {env.current_player}"}
        obs, feats = env.observe(fseat), env.action_features()
        i = T.pick(net.score_actions(obs, feats), rng)
        recs.append(R.look(env, fseat, i))   # reads the position; the game is untouched
        moves.append(i)
        env.step(i)
    w, pts, turns = env.result()
    out = {"row": row, "seed": g["seed"], "decks": g["decks"], "winner": w, "points": list(pts), "turns": turns,
           "moves": moves}
    if h == "net":
        out["count"] = R.tally(recs, A)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--run", required=True)
    ap.add_argument("--games", type=int, default=2000)
    ap.add_argument("--identity-games", type=int, default=R.IDENTITY_DEALS,
                    help=f"deals in the identity gate (default {R.IDENTITY_DEALS}, the Hydreigon readout's; fewer is not "
                         "the pre-set reading)")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--out", default=str(HERE / "kp3_rows.txt"))
    ap.add_argument("--precheck", action="store_true",
                    help="only the k3 v k3 identity replay on the bars, then stop (no network; works before the verdict)")
    R.add_preset_options(ap)
    a = R.apply_preset(ap.parse_args())
    t0 = time.time()
    addon_sha = T.sha_file(pdl_rl_env.__file__)
    if addon_sha != ADDON_SHA:
        raise SystemExit(f"{pdl_rl_env.__file__} has sha256 {addon_sha}, not {ADDON_SHA}: not the diagnostic build "
                         "this readout was set up with")
    if a.identity_games < 1:
        raise SystemExit("--identity-games must be at least 1: the kp3 rows are played only after the identity gate")
    run_dir = Path(a.run) if Path(a.run).is_absolute() else T.HERE / a.run
    S = json.loads((run_dir / "settings.json").read_text())
    T.check_decks_unchanged(run_dir, S)
    A = R.resolve(S, a)
    FOCUS, OPP = A["deck"], A["opp"]
    F, O = FOCUS.capitalize(), OPP.capitalize()
    legacy = a.reading == "hydreigon"   # the Hydreigon rows' text, unchanged
    print("\n".join(R.spec_lines(A)) + "\n")
    pair = sorted([FOCUS, OPP])

    if a.precheck:
        rows = [json.loads(x) for x in (run_dir / "eval_games.jsonl").read_text().splitlines() if '"kind": "bar"' in x]
        bars = {g["seed"]: g for g in rows if sorted(g["decks"]) == pair}
        ids = sorted(bars)[:a.identity_games]
        with mp.get_context("spawn").Pool(a.workers, initializer=_init, initargs=(S, None, FOCUS, A)) as pool:
            got = pool.map(play, [("k3|k3", {"seed": s, "decks": bars[s]["decks"]}) for s in ids], chunksize=4)
        bad = [r for r in got if "error" in r]
        same = sum("error" not in r and (r["winner"], r["turns"]) == (bars[r["seed"]]["winner"], bars[r["seed"]]["turns"])
                   for r in got)
        print(f"Precheck ({run_dir.name}): the diagnostic build {pdl_rl_env.__file__} ({addon_sha[:12]}) replays the "
              f"k3 v k3 bar rows exactly (winner, turns) on {same} of {len(ids)} deals"
              + (f"; errors {len(bad)}" if bad else "") + f" (of {len(bars):,} bar rows). "
              f"{'Same games' if same == len(ids) else 'NOT the same games: the kp3 rows would stop at their identity gate'}."
              f" Took {time.time() - t0:.0f} s.")
        return

    st = json.loads((run_dir / "state.json").read_text())
    picks = (st.get("verdict") or {}).get("picks")
    if not picks or FOCUS not in picks:
        raise SystemExit("state.json has no confirmed checkpoint per network yet (verdict 'picks'); "
                         "run this after the run has finished its confirmations")
    pick = picks[FOCUS]
    margin = next(c["margin"] for c in st["confirmations"] if c["deck"] == FOCUS and c["name"] == pick)
    net_path = str(T.ckpt_path(run_dir, pick, FOCUS))
    rows = [json.loads(x) for x in (run_dir / "eval_games.jsonl").read_text().splitlines()
            if '"kind": "bar"' in x or '"kind": "confirmation"' in x]
    bars = {g["seed"]: g for g in rows if g["kind"] == "bar" and sorted(g["decks"]) == pair}
    conf = {g["seed"]: g for g in rows if g["kind"] == "confirmation" and g.get("ckpt") == pick
            and g.get("deck") == FOCUS}
    seeds = sorted(bars)[:a.games]
    if any(s not in conf or conf[s]["decks"] != bars[s]["decks"] for s in seeds):
        raise SystemExit("the confirmation rows don't cover the bar deals one for one")
    deal = {s: {"seed": s, "decks": bars[s]["decks"]} for s in seeds}
    ids = seeds[:a.identity_games]

    L = [f"{F} network v kp3 rows — {run_dir.name}   ({time.strftime('%Y-%m-%d %H:%M')})", "",
         f"Diagnostic add-on: {pdl_rl_env.__file__} sha256 {addon_sha[:12]} (not the verified "
         f"0.7.2 wheel; built against the engine at c7cb688 for kp3). Network: {Path(net_path).name} "
         f"{T.sha_file(net_path)[:12]} (state.json's confirmed {FOCUS} checkpoint).", ""]
    if not legacy:
        L += [R.preset_line(a)] + R.spec_lines(A) + [""]
    with mp.get_context("spawn").Pool(a.workers, initializer=_init, initargs=(S, net_path, FOCUS, A)) as pool:
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
        raise SystemExit(f"{len(bad)} games asked the network for a {O} decision or similar: {bad[0]}")
    G = {"k3|k3": bars, "net|k3": conf}
    for row in PLAYED:
        G[row] = {r["seed"]: r for r in res if r["row"] == row}
    won = lambda g: float(g["winner"] == g["decks"].index(FOCUS))  # noqa: E731
    score = lambda g: 1.0 if won(g) else (0.5 if g["winner"] == -1 else 0.0)  # noqa: E731

    def paired(label, x, y):
        d = np.array([won(x[s]) - won(y[s]) for s in seeds])
        n = len(d)
        half = 1.96 * d.std(ddof=1) / math.sqrt(n)
        only_a, only_b = int((d > 0).sum()), int((d < 0).sum())
        # the difference from the exact counts (deals won only in the first row minus only in the second, over n)
        return 100 * (only_a - only_b) / n, (f"  {label:<58}{100 * d.mean():>+7.1f} ± {100 * half:<5.1f}"
                                             f"{only_a:>7} / {only_b:<6}")

    lim = f"   Limitless {a.limitless[0]} ± {a.limitless[1]}" if a.limitless else ""
    L += ["", f"Deals: the run's bar deals, {len(seeds):,} (seed {seeds[0]:,} to {seeds[-1]:,}), bar seats.", "",
          f"  {F + ' | ' + O + ' pilots':<32}{'n':>6}{'won %':>8}{'draws':>7}{'score %':>9}{lim}"]
    for row in ("k3|k3", "net|k3", "kp3|k3", "kp3|kp3", "net|kp3"):
        g = G[row]
        tag = " (recorded)" if row in ("k3|k3", "net|k3") else ""
        L.append(f"  {row + tag:<32}{len(seeds):>6}{100 * np.mean([won(g[s]) for s in seeds]):>8.1f}"
                 f"{sum(g[s]['winner'] == -1 for s in seeds):>7}{100 * np.mean([score(g[s]) for s in seeds]):>9.1f}")
    L += ["", f"Paired differences in {F}'s win % (95% interval = 1.96 x sd of the per-deal difference / sqrt n; "
              f"'won only' = deals won in the first row and not the second / the reverse):",
          f"  {'':<58}{'points':>7}{'':>8}{'won only':>14}"]
    dec, line = paired(f"DECISIVE net|kp3 - kp3|kp3 (network v kp3, {O} sees)", G["net|kp3"], G["kp3|kp3"])
    L.append(line)
    for lab, x, y in (("net|k3 - k3|k3 (the run's margin, recomputed)", "net|k3", "k3|k3"),
                      (f"kp3|k3 - k3|k3 (kp3's edge over k3, {O} blind)", "kp3|k3", "k3|k3"),
                      (f"net|k3 - kp3|k3 (network v kp3, {O} blind)", "net|k3", "kp3|k3"),
                      (f"net|k3 - net|kp3 (what {O}'s pricing takes from the net)", "net|k3", "net|kp3"),
                      (f"kp3|k3 - kp3|kp3 (what it takes from kp3's {F})", "kp3|k3", "kp3|kp3")):
        L.append(paired(lab, G[x], G[y])[1])
    if legacy:
        L += ["", "READING (set before any row was played; RUN5's 10-point line, reused):",
              f"  net|kp3 minus kp3|kp3 = {dec:+.1f} points: "
              + ("+10 or more -> the network plays Hydreigon better than kp3 even against a Lucario that sees Darkness "
                 "Claw coming: play beyond pricing, which B2c's divergence mining can name (a later step)."
                 if dec >= 10 else
                 "under +10 -> most of the +40.8 is what kp3's pricing already gives Hydreigon plus what k3's blind "
                 "Lucario gives away; no further network work on this pair."),
              "  Everything else above is descriptive.", ""]
    else:
        c_net = R.total([r for r in res if r["row"] == "net|kp3"], A)
        full = len(seeds) == S["bar_per_pairing"] and len(ids) >= R.IDENTITY_DEALS
        L += ["", f"The audit, the network against kp3 (PRESET_READING item 3, descriptive): the {F} network's play in "
                  f"net|kp3, live,", "  per turn of its own where the move was on offer; the definitions are readout.py's "
                  "section 2."] + R.ko_words(A, F, O) + [""]
        L += R.audit_lines([(f"network {F} v kp3 {O} (live)", c_net)], A)
        L += ["", "READING (PRESET_READING.md item 2, fixed before training; applied as written):"]
        if not full:
            L.append(f"  NOT THE PRE-SET READING: {len(seeds):,} of the run's {S['bar_per_pairing']:,} bar deals were "
                     f"played, with an identity gate of {len(ids):,} deals; the reading is for all of them, after a "
                     f"gate of at least {R.IDENTITY_DEALS}.")
        L += [f"  D = (network {F} v kp3 {O}) - (kp3 {F} v kp3 {O}) = {dec:+.2f} points ({F}'s win %, paired over "
              f"{len(seeds):,} bar deals, bar seats; from the exact counts on the DECISIVE line above, where its 95% "
              "interval is).",
              "  " + (f"D at +10 or more: the network plays {F} better than kp3 even against a {O} that prices its "
                      "hidden-text cards. Its habits are then audited (step 3) to name the difference. That difference is "
                      f"a candidate cause of {F}'s gap and a B5 feature candidate, registered and read on its own."
                      if R.at_least_10(dec) else
                      f"D under +10: learning finds no large {F} piloting gain in this matchup. {F}'s gap is then "
                      "unlikely to be a piloting blind spot that play can reveal. The leads that remain are card or rules "
                      f"implementation (a card check of the {F} list's texts in the engine) and the population, neither "
                      "tested by this run."),
              f"  Item 1, the run's own RUN5 line: the {F} network's confirmed margin over k3 is {100 * margin:+.1f} points "
              f"(state.json; recomputed above as net|k3 - k3|k3). +10 or more counts as a gain: "
              f"{'yes' if R.at_least_10(100 * margin) else 'no'}.",
              "  Everything else above is descriptive.", ""]
    L.append(f"Took {time.time() - t0:.0f} s with {a.workers} workers; played {2 * len(ids)} identity games and "
             f"{len(res):,} kp3-row games.")
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
