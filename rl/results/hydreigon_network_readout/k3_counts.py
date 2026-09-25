"""Companion to readout.py: k3's own attack counts on the same bar deals, so the network's counts have a paired k3
reference (readout.py's k3 numbers come from other seeds, and it has none for Darkness Claw). Inside WSL, from rl:
    python results/hydreigon_network_readout/k3_counts.py --run runs/diag-hydreigon-lucario [--games 2000] [--workers 8]

For each bar deal (k3 pilots both sides; the run's own seeds and seats): the engine's own loop plays k3 v k3 and
records the focus deck's choices (engine_play_record, as step1b_k3_replay_check.py); the game is then replayed
through the add-on with k3 on the other side, and each focus decision is classified with readout.py's own look()
and tally(), once per attack name. A replay counts only if its winner and turns equal the bar row's, which also
proves the engine's loop played the same games the run recorded as its bars. Nothing is trained; no new seeds.

--bot kp3 (added after the k3 pass; the k3 path is unchanged): the same count with kp3 piloting both sides, which
needs the diagnostic add-on (PDL_ADDON_DIR, as kp3_rows.py). There is no recorded kp3 game to compare with, so a
replay counts when it equals the engine loop's own game (winner and turns), as step1b checks.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import sys  # noqa: E402

if os.environ.get("PDL_ADDON_DIR"):   # the diagnostic add-on for --bot kp3 (see kp3_rows.py)
    _dir = os.path.abspath(os.path.expanduser(os.environ["PDL_ADDON_DIR"]))
    sys.path.insert(0, _dir)
    import pdl_rl_env  # noqa: E402
    if not os.path.abspath(pdl_rl_env.__file__).startswith(_dir):
        raise SystemExit(f"pdl_rl_env came from {pdl_rl_env.__file__}, not PDL_ADDON_DIR")

import argparse  # noqa: E402
import json  # noqa: E402
import multiprocessing as mp  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import readout as R  # noqa: E402  (puts rl on the path and imports train_v5 as R.T)
from pdl_rl_env import engine_play_record  # noqa: E402

T = R.T
ATTACKS = ("Hyper Ray", "Darkness Claw")


def _init(S, focus, bot):
    T.set_decks(S)
    R._W.update(env=T.make_env(), focus=focus, bot=bot)


def play(g):
    env, focus, bot = R._W["env"], R._W["focus"], R._W["bot"]
    fseat = g["decks"].index(focus)
    p0, p1 = (T.DECKS["paths"][d] for d in g["decks"])
    rec, _prints, _h, res = engine_play_record(p0, p1, g["seed"], (bot, bot), fseat)
    env.reset(p0, p1, g["seed"], bots=[None, bot] if fseat == 0 else [bot, None])
    recs = {a: [] for a in ATTACKS}
    i = 0
    while not env.done:
        if i >= len(rec) or env.current_player != fseat:
            return {"seed": g["seed"], "ok": False}
        for a in ATTACKS:
            R._W["attack"] = a
            recs[a].append(R.look(env, fseat, rec[i]))
        env.step(rec[i])
        i += 1
    w, _pts, turns = env.result()
    ref = (g["winner"], g["turns"]) if bot == "k3" else (res[0], res[2])
    ok = i == len(rec) and (w, turns) == tuple(ref)
    return {"seed": g["seed"], "ok": ok, "count": {a: R.tally(recs[a]) for a in ATTACKS}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--games", type=int, default=2000)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--deck", default="hydreigon")
    ap.add_argument("--bot", default="k3", choices=("k3", "kp3"))
    ap.add_argument("--out", default=None, help="default: <bot>_counts.txt here")
    a = ap.parse_args()
    if a.bot != "k3" and not os.environ.get("PDL_ADDON_DIR"):
        raise SystemExit(f"--bot {a.bot} needs the diagnostic add-on: set PDL_ADDON_DIR (see kp3_rows.py)")
    a.out = a.out or str(HERE / f"{a.bot}_counts.txt")
    b = a.bot
    t0 = time.time()
    run_dir = Path(a.run) if Path(a.run).is_absolute() else T.HERE / a.run
    S = json.loads((run_dir / "settings.json").read_text())
    T.check_decks_unchanged(run_dir, S)
    names = list(S["pool"])
    opp = [d for d in names if d != a.deck][0]
    pair = sorted(names)
    rows = [json.loads(x) for x in (run_dir / "eval_games.jsonl").read_text().splitlines() if '"kind": "bar"' in x]
    bars = {g["seed"]: g for g in rows if sorted(g["decks"]) == pair}
    seeds = sorted(bars)[:a.games]
    with mp.get_context("spawn").Pool(a.workers, initializer=_init, initargs=(S, a.deck, b)) as pool:
        res = pool.map(play, [bars[s] for s in seeds], chunksize=4)
    good = [r for r in res if r["ok"]]
    F, O = a.deck.capitalize(), opp.capitalize()
    ref = "the bar row" if b == "k3" else "the engine loop's own game"
    L = [f"{b}'s attack counts on the bar deals — {run_dir.name}   ({time.strftime('%Y-%m-%d %H:%M')})", "",
         f"Deals: the run's bar deals, first {len(seeds):,} (seed {seeds[0]:,} to {seeds[-1]:,}); {b} pilots both sides.",
         f"Replayed exactly (winner and turns equal {ref}): {len(good):,} of {len(res):,}. Only those are counted.",
         "",
         f"Per turn of {b} piloting {F} where the attack was on offer: used / passed (use %). Same definitions as",
         "readout.py's table 2 (look() and tally() imported from it): 'KOs' = the opponent's Active had no more HP left",
         "than the attack's fixed damage; 'other' = offered earlier in the turn but not when it ended.", "",
         "  " + " " * 30 + "   KOs: used / passed    doesn't KO: used / passed   other"]
    for at in ATTACKS:
        c = dict.fromkeys(R.KEYS, 0)
        for r in good:
            for k in R.KEYS:
                c[k] += r["count"][at][k]
        L.append(R.hr_line(f"{b} {F}: {at}", c, 30))
    c = dict.fromkeys(R.KEYS, 0)
    for r in good:
        for k in R.KEYS:
            c[k] += r["count"][ATTACKS[0]][k]
    L += [f"  Roar in Unison, {b} {F} v {b} {O}: used on {c['roar_used']} of the {c['roar_turns']} turns it was usable on a "
          f"Hydreigon with more than 30 HP left; uses that knocked out its own Hydreigon: {c['roar_self_ko']}.", "",
          f"Took {time.time() - t0:.0f} s with {a.workers} workers."]
    if len(good) < len(res):
        L.insert(0, f"INCOMPLETE: {len(res) - len(good)} bar deals did not replay exactly; they are left out.")
    text = "\n".join(L) + "\n"
    print(text)
    out = R.free_name(Path(a.out))
    out.write_text(text)
    print(f"Written: {out}")


if __name__ == "__main__":
    main()
