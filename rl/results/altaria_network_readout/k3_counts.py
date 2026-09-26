"""Companion to readout.py: k3's (or kp3's) own counts on the run's bar deals, so the network's counts have a paired
reference. results/hydreigon_network_readout/k3_counts.py with the deck and the audited attacks and abilities made
options (readout.py's preset options; default: the Altaria detector network's, PRESET_READING.md item 3). Inside WSL,
from the rl folder, with the run5 venv's python:
    nice -n 19 python results/altaria_network_readout/k3_counts.py --run runs/diag-altaria-lucario [--games 2000] [--workers 3]
    PDL_ADDON_DIR=/home/dacz8976/diag-kp-addon/module \
    nice -n 19 python results/altaria_network_readout/k3_counts.py --run runs/diag-altaria-lucario --bot kp3
    ... --preset hydreigon --run runs/diag-hydreigon-lucario [--bot kp3]   (the Hydreigon counts, unchanged)

For each bar deal (the bot pilots both sides; the run's own seeds and seats): the engine's own loop plays the game and
records the focus deck's choices (engine_play_record, as step1b_k3_replay_check.py); the game is then replayed
through the add-on with the bot on the other side, and each focus decision is classified with readout.py's own look()
and tally(). A replay counts only if its winner and turns equal the bar row's (k3), which also proves the engine's
loop played the same games the run recorded as its bars. Nothing is trained; no new seeds. It needs no network, but
like readout.py it refuses until state.json has its verdict (nothing is read before then; --check-only plays nothing
and works any time). --bot k3 refuses if PDL_ADDON_DIR is set: the k3 column is on the verified 0.7.2 wheel.

--bot kp3: the same count with kp3 piloting both sides, which needs the diagnostic add-on (PDL_ADDON_DIR, as
kp3_rows.py; it stops unless the module's sha256 is readout.DIAG_ADDON_SHA). There is no recorded kp3 game to compare
with, so a replay counts when it equals the engine loop's own game (winner and turns), as step1b checks.
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


def _init(S, focus, bot, A):
    T.set_decks(S)
    R._W.update(env=T.make_env(), focus=focus, bot=bot, audit=A)


def play(g):
    env, focus, bot, A = R._W["env"], R._W["focus"], R._W["bot"], R._W["audit"]
    fseat = g["decks"].index(focus)
    p0, p1 = (T.DECKS["paths"][d] for d in g["decks"])
    rec, _prints, _h, res = engine_play_record(p0, p1, g["seed"], (bot, bot), fseat)
    env.reset(p0, p1, g["seed"], bots=[None, bot] if fseat == 0 else [bot, None])
    recs = []
    i = 0
    while not env.done:
        if i >= len(rec) or env.current_player != fseat:
            return {"seed": g["seed"], "ok": False}
        recs.append(R.look(env, fseat, rec[i]))
        env.step(rec[i])
        i += 1
    w, _pts, turns = env.result()
    ref = (g["winner"], g["turns"]) if bot == "k3" else (res[0], res[2])
    ok = i == len(rec) and (w, turns) == tuple(ref)
    return {"seed": g["seed"], "decks": g["decks"], "ok": ok, "winner": w, "turns": turns, "count": R.tally(recs, A)}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--run", required=True)
    ap.add_argument("--games", type=int, default=2000)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--bot", default="k3", choices=("k3", "kp3"))
    ap.add_argument("--out", default=None, help="default: <bot>_counts.txt here")
    ap.add_argument("--check-only", action="store_true", help="resolve the names and check the run's files, then stop")
    R.add_preset_options(ap, counts=True)
    a = R.apply_preset(ap.parse_args(), counts=True)
    if a.bot == "k3" and os.environ.get("PDL_ADDON_DIR"):
        raise SystemExit("--bot k3 runs on the verified 0.7.2 wheel (the run's own add-on): unset PDL_ADDON_DIR")
    if a.bot != "k3":
        if not os.environ.get("PDL_ADDON_DIR"):
            raise SystemExit(f"--bot {a.bot} needs the diagnostic add-on: set PDL_ADDON_DIR (see kp3_rows.py)")
        import pdl_rl_env   # already imported above, from PDL_ADDON_DIR
        sha = T.sha_file(pdl_rl_env.__file__)
        if sha != R.DIAG_ADDON_SHA:
            raise SystemExit(f"{pdl_rl_env.__file__} has sha256 {sha}, not {R.DIAG_ADDON_SHA}: not the diagnostic "
                             "build this readout was set up with")
    a.out = a.out or str(HERE / f"{a.bot}_counts.txt")
    b = a.bot
    t0 = time.time()
    run_dir = Path(a.run) if Path(a.run).is_absolute() else T.HERE / a.run
    S = json.loads((run_dir / "settings.json").read_text())
    T.check_decks_unchanged(run_dir, S)
    A = R.resolve(S, a)
    legacy = a.reading == "hydreigon"   # the Hydreigon counts' text, unchanged
    print("\n".join(R.spec_lines(A)) + "\n")
    if a.check_only:
        print(f"--check-only: {run_dir.name}'s settings and deck files resolve; nothing played.")
        return
    # nothing is read before the run has its verdict (PRESET_READING: "Before anything is read"), as readout.py
    picks = (json.loads((run_dir / "state.json").read_text()).get("verdict") or {}).get("picks") or {}
    if set(picks) != set(S["pool"]):
        raise SystemExit("state.json has no confirmed checkpoint per network yet (verdict 'picks'); "
                         "run this after the run has finished its confirmations")
    focus, opp = A["deck"], A["opp"]
    pair = sorted([focus, opp])
    rows = [json.loads(x) for x in (run_dir / "eval_games.jsonl").read_text().splitlines() if '"kind": "bar"' in x]
    bars = {g["seed"]: g for g in rows if sorted(g["decks"]) == pair}
    formula = {s: [d0, d1] for s, d0, d1, *_ in T.bar_games(S) if sorted([d0, d1]) == pair}
    off = [s for s, g in bars.items() if formula.get(s) != g["decks"]]
    if off:
        raise SystemExit(f"{len(off)} bar rows don't match the settings' seed/seat formula (first: seed {off[0]})")
    seeds = sorted(bars)[:a.games]
    with mp.get_context("spawn").Pool(a.workers, initializer=_init, initargs=(S, focus, b, A)) as pool:
        res = pool.map(play, [bars[s] for s in seeds], chunksize=4)
    good = [r for r in res if r["ok"]]
    F, O = focus.capitalize(), opp.capitalize()
    ref = "the bar row" if b == "k3" else "the engine loop's own game"
    L = [f"{b}'s attack counts on the bar deals — {run_dir.name}   ({time.strftime('%Y-%m-%d %H:%M')})", "",
         f"Deals: the run's bar deals, first {len(seeds):,} (seed {seeds[0]:,} to {seeds[-1]:,}); {b} pilots both sides.",
         f"Replayed exactly (winner and turns equal {ref}): {len(good):,} of {len(res):,}. Only those are counted.",
         ""]
    c = R.total(good, A)
    if legacy:
        L += [f"Per turn of {b} piloting {F} where the attack was on offer: used / passed (use %). Same definitions as",
              "readout.py's table 2 (look() and tally() imported from it): 'KOs' = the opponent's Active had no more HP left",
              "than the attack's fixed damage; 'other' = offered earlier in the turn but not when it ended.", "",
              "  " + " " * 30 + "   KOs: used / passed    doesn't KO: used / passed   other"]
        for at in A["attacks"]:
            L.append(R.hr_line(f"{b} {F}: {at}", c["attacks"][at], 30))
        for ab in A["abilities"]:
            if ab["kind"] == "activated":
                k, owner = c["abilities"][ab["name"]], ab["owners"][0]
                L.append(f"  {ab['name']}, {b} {F} v {b} {O}: used on {k['used']} of the {k['turns']} turns it was usable on a "
                         f"{owner} with more than {ab['self_dmg']} HP left; uses that knocked out its own {owner}: "
                         f"{k['self_ko']}.")
        L.append("")
    else:
        L += [f"The audit's {b} counts (PRESET_READING item 3, descriptive): {b} piloting {F}, per turn of its own where",
              "   the move was on offer; the definitions are readout.py's section 2 (look() and tally() imported from it)."]
        L += R.ko_words(A, F, O) + [""]
        L += R.audit_lines([(f"{b} {F} v {b} {O} (the bars' deals)", c)], A)
        if b == "k3":
            # the knockout audit replays the same bar games for k3 (audit_v5.py, "k3|<focus>><opp>")
            au = R.ko_audit_file(run_dir, focus, picks[focus]) if focus in picks else None
            if au is not None and au.exists() and len(good) == len(res) == S["bar_per_pairing"]:
                k = json.loads(au.read_text())["stats"].get(f"k3|{focus}>{opp}") or {}
                h = c["habits"]
                mine = (h["attack_turns"], h["attack_made"], h["bench_turns"], h["bench_made"])
                theirs = tuple(k.get(x) for x in ("attack_turns", "attack_made", "bench_turns", "bench_made"))
                L.append(f"  Check: these attacking/benching counts {mine} {'equal' if mine == theirs else 'DIFFER FROM'} "
                         f"the knockout audit's k3 line {theirs} ({au.name}).")
        L.append("")
    L.append(f"Took {time.time() - t0:.0f} s with {a.workers} workers.")
    if len(good) < len(res):
        L.insert(0, f"INCOMPLETE: {len(res) - len(good)} bar deals did not replay exactly; they are left out.")
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
