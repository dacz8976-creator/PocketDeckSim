"""Run 4 report step: the knockout audit on the confirmation games, per matchup, next to k3.
Run after train_v4.py (run_training_v4.sh does it):  python audit_v4.py --run runs/<name>

For every confirmed checkpoint it replays that checkpoint's confirmation games (the network piloting one deck,
k3 the other, on the bars' seeds) and the bar games (k3 piloting both decks, same seeds), exactly, from their
saved moves. At every real decision the engine applies each legal option to copies of the TRUE game under 4
chance seeds (analysis only; the network never sees this). Per player-turn it counts:
  sure win on offer / not won that turn;  sure knockout on offer / not taken;
  attacks that hand the opponent sure points when another option didn't;
  checkup deaths: ended the turn when that hands the opponent sure points (poison/burn/etc. at the checkup)
    - loose: some other option avoided it on the spot (anything that doesn't end the turn does)
    - strict: a retreat was offered at some point that turn (retreating clears poison and burn)
    - strict and still winnable (network only): its score for the move it chose was above winnable_q
  and the two habits run 3 was measured on (Sept 20 checks): of the turns where an attack was on offer, the
  share where one was made; of the turns where a Basic could be benched, the share where one was
The comparison that matters is the network piloting deck A against k3 piloting deck A on the same seeds.
A report line, not a pass rule (Fable).
A finished result is reused only if its inputs are unchanged (checkpoint, recorded games, decks, settings, code,
add-on); otherwise it's redone and the old file is kept beside it. A game that doesn't replay exactly is left out
of the numbers, and the result is marked INCOMPLETE and redone next time instead of reused (Astra's review).
"""
import argparse
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import train_v4 as T  # noqa: E402

K = 4
_W = {}


def _init(ckpt_path, S):
    from pdl_rl_env import RawEnv
    T.set_decks(S)
    paths = list(T.DECKS["paths"].values())
    ids = sorted({i for p in paths for i in RawEnv.deck_card_ids(p)})
    env = RawEnv(ids, S["features"])
    env.reset(paths[0], paths[1], 1)
    env.set_audit(True, K)
    net = T.load_net(ckpt_path, env.obs_dim + env.action_dim)   # the one network being audited
    _W.update(env=env, net=net, S=S)


def kind(move):
    return move.split(" ")[0].replace("V:", "")


def k3dec(x):
    return {"actor": x["actor"], "turn": x["turn"], "moves": x["moves"], "outs": x["outcomes"], "chosen": x["chosen"], "q": None}


def replay(g):
    env, net = _W["env"], _W["net"]
    paths = T.DECKS["paths"]
    d0, d1 = g["decks"]
    decs = []
    if g["mode"] == "k3k3":
        env.reset(paths[d0], paths[d1], g["seed"], ["k3", "k3"])
        decs = [(x["actor"], k3dec(x)) for x in map(json.loads, env.bot_decisions())]
        res = env.result()
        return {"g": {k: g[k] for k in ("seed", "decks", "mode", "tag")}, "result": list(res), "decisions": decs,
                "ok": res[0] == g["winner"] and res[2] == g["turns"]}
    seat = g["bot_seat"]
    env.reset(paths[d0], paths[d1], g["seed"], [None, "k3"] if seat == 0 else ["k3", None])
    seen = 0
    for mv in g["moves"]:
        if env.done:
            break
        bd = env.bot_decisions()
        decs += [(x["actor"], k3dec(x)) for x in map(json.loads, bd[seen:])]
        seen = len(bd)
        p = env.current_player
        turn = json.loads(env.describe(p))["turn"]
        moves = env.legal_actions()
        outs = [list(o) for o in env.outcome_labels(K)]
        obs = np.frombuffer(env.observe(p), dtype="<f4")
        feats = np.frombuffer(env.action_features(), dtype="<f4").reshape(len(moves), env.action_dim)
        q = net.score_actions(obs, feats)
        decs.append((p, {"actor": p, "turn": turn, "moves": moves, "outs": outs, "chosen": mv, "q": [float(v) for v in q]}))
        env.step(mv)
    bd = env.bot_decisions()
    decs += [(x["actor"], k3dec(x)) for x in map(json.loads, bd[seen:])]
    res = env.result() if env.done else None
    ok = res is not None and res[0] == g["winner"] and res[2] == g["turns"]
    return {"g": {k: g[k] for k in ("seed", "decks", "mode", "tag", "bot_seat")}, "result": list(res) if res else None,
            "decisions": decs, "ok": ok}


def tally(games, winnable_q):
    """Keys: ("bot", "A>B") for the network piloting A; ("k3", "A>B") for k3 piloting A in the bar games;
    ("k3opp", "A>B") for k3 piloting B against the network."""
    stats = {}
    for gm in games:
        g, res = gm["g"], gm["result"]
        d = g["decks"]
        turns = {}
        for actor, x in gm["decisions"]:
            if len(x["moves"]) < 2:
                continue
            turns.setdefault((actor, x["turn"]), []).append(x)
        for (actor, turn), ds in turns.items():
            me, them = d[actor], d[1 - actor]
            if g["mode"] == "k3k3":
                who = "k3"
            else:
                who = "bot" if actor == g["bot_seat"] else "k3opp"
            key = f"{who}|{me}>{them}" if who != "k3opp" else f"k3opp|{them}>{me}"
            s = stats.setdefault(key, dict(turns=0, win_turns=0, win_missed=0, ko_turns=0, ko_missed=0,
                                           give_attack=0, checkup_loose=0, checkup_strict=0, checkup_strict_winnable=0,
                                           attack_turns=0, attack_made=0, bench_turns=0, bench_made=0))
            s["turns"] += 1
            # the two habits run 3 was measured on: playing out the turn, and benching.
            # Setup (turn 0) is excluded from both, as the run 2 / run 3 benching benchmark excludes it
            # (results/run3_checks/bench_run2_vs_run3.py): placing at setup is forced, so counting it as
            # successful benching flatters the rate and makes the comparison meaningless (Astra, Sept 20).
            # The 'turns' denominator for the giveaway and checkup rates keeps setup, as run 1 and run 2's
            # audits did, so those rates stay comparable with theirs.
            if turn > 0:
                offered = {kind(m) for x in ds for m in x["moves"]}
                taken = {kind(x["moves"][x["chosen"]]) for x in ds if x["chosen"] >= 0}
                if "Attack" in offered:
                    s["attack_turns"] += 1
                    s["attack_made"] += "Attack" in taken
                if "Place" in offered:
                    s["bench_turns"] += 1
                    s["bench_made"] += "Place" in taken
            win_avail = any(o[4] == K for x in ds for o in x["outs"])
            won_now = res is not None and res[0] == actor and res[2] == turn
            if win_avail:
                s["win_turns"] += 1
                s["win_missed"] += not won_now
            ko_avail = any(kind(m) == "Attack" and o[0] >= 1 for x in ds for m, o in zip(x["moves"], x["outs"]))
            took = any(x["outs"][x["chosen"]][1] >= 1 for x in ds if x["chosen"] >= 0)
            if ko_avail:
                s["ko_turns"] += 1
                s["ko_missed"] += (not took and not won_now)
            retreat_offered = any(kind(m) == "Retreat" for x in ds for m in x["moves"])
            for x in ds:
                c = x["chosen"]
                if c < 0 or x["outs"][c][2] < 1 or not any(o[3] == 0 for o in x["outs"]):
                    continue
                k = kind(x["moves"][c])
                if k == "Attack":
                    s["give_attack"] += 1
                elif k == "EndTurn":
                    s["checkup_loose"] += 1
                    if retreat_offered:
                        s["checkup_strict"] += 1
                        if x["q"] is not None and x["q"][c] > winnable_q:
                            s["checkup_strict_winnable"] += 1
    return stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--ckpt", default="", help="default: every confirmed checkpoint")
    ap.add_argument("--deck", default="", help="default: every network that was confirmed")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--redo", action="store_true")
    a = ap.parse_args()
    run_dir = Path(a.run) if Path(a.run).is_absolute() else HERE / a.run
    S = json.loads((run_dir / "settings.json").read_text())
    st = json.loads((run_dir / "state.json").read_text())
    # run 4 confirms one network at a time: (deck, checkpoint) pairs
    picks = [(cf["deck"], cf["name"]) for cf in st["confirmations"]]
    if a.ckpt:
        picks = [(d, n) for d, n in picks if n == a.ckpt]
    if a.deck:
        picks = [(d, n) for d, n in picks if d == a.deck]
    out_dir = HERE / "results/ko_audit"
    out_dir.mkdir(parents=True, exist_ok=True)
    T.check_decks_unchanged(run_dir, S)  # the recorded games were played with the run's own deck files
    lines_ = [line for line in (run_dir / "eval_games.jsonl").read_text().splitlines()
              if '"kind": "bar"' in line or '"kind": "confirmation"' in line]
    rows = [json.loads(line) for line in lines_]
    for deck, name in picks:
        out = out_dir / f"v4_{run_dir.name}_{deck}_{name}.json"
        conf_lines = [line for line, g in zip(lines_, rows)
                      if g.get("kind") == "confirmation" and g.get("ckpt") == name and g.get("deck") == deck]
        # that network's own pairings only
        deck_bar_lines = [line for line, g in zip(lines_, rows) if g.get("kind") == "bar" and deck in g["decks"]]
        inputs = T.report_inputs("audit", run_dir, S, name, ["audit_v4.py"], conf_lines + deck_bar_lines,
                                 nets={deck: name})
        inputs["deck"] = deck
        inputs["K"] = K
        if out.exists():
            old = json.loads(out.read_text())
            if old.get("inputs") == inputs and old.get("complete") and not a.redo:
                print(f"{out.name} exists with the same inputs; skipped (--redo to rerun)")
                continue
            why = "--redo" if a.redo else ("it was incomplete" if old.get("inputs") == inputs else "its inputs changed")
            kept = out.with_name(f"{out.stem}.superseded-{time.strftime('%Y%m%d-%H%M%S')}.json")
            out.replace(kept)
            print(f"{out.name}: redoing ({why}); the old result is kept as {kept.name}")
        conf = [json.loads(line) for line in conf_lines]
        deck_bars = [json.loads(line) for line in deck_bar_lines]
        with mp.get_context("spawn").Pool(a.workers, initializer=_init,
                                          initargs=(str(T.ckpt_path(run_dir, name, deck)), S)) as pool:
            games = pool.map(replay, conf + deck_bars, chunksize=4)
        failed = [g["g"] for g in games if not g["ok"]]
        bad = len(failed)
        stats = tally([g for g in games if g["ok"]], S["checkup_report"]["winnable_q"])  # failed replays left out
        per = lambda s, k: 1000 * s[k] / max(1, s["turns"])
        lines = ([f"INCOMPLETE: {bad:,} of {len(games):,} games did not replay exactly as recorded; they are left out of "
                  f"the numbers below, and this audit will be redone on the next run instead of reused."] if bad else []) + [
                 f"Knockout audit (run 4) — {run_dir.name}, the {deck} network's {name}: {len(conf):,} confirmation games "
                 f"and {len(deck_bars):,} bar games replayed; replay problems: {bad}", "",
                 "Per matchup: the network piloting the first deck (bot) vs k3 piloting the same deck on the same seeds (k3).",
                 "'attacked' / 'benched' = of the turns where that move was on offer, the share where it was made. "
                 "Setup (turn 0) is excluded from both, as the run 2/run 3 benching benchmark excludes it. "
                 "(k3 attacks 99% and benches 97%. Run 3's shared network: attacked 68%, benched 54%. "
                 "Run 2's Blaziken specialist, the like-for-like bar for the pilot: benched 63%.)",
                 "Giveaways and checkup deaths are rates per 1,000 player-turns. Checkup deaths: loose / strict (a "
                 "retreat was offered that turn) / strict and still winnable (network only).", "",
                 f"  {'matchup':<22}{'who':<5}{'turns':>7}{'sure win missed':>17}{'sure KO missed':>16}"
                 f"{'attacked':>10}{'benched':>9}{'giveaways':>11}{'checkup deaths':>24}"]
        for tag in sorted({k.split("|")[1] for k in stats}):
            for who in ("bot", "k3"):
                s = stats.get(f"{who}|{tag}")
                if not s:
                    continue
                cu = f"{per(s, 'checkup_loose'):.1f} / {per(s, 'checkup_strict'):.1f}" + (
                    f" / {per(s, 'checkup_strict_winnable'):.1f}" if who == "bot" else "")
                att = f"{s['attack_made'] / s['attack_turns']:.0%}" if s["attack_turns"] else "—"
                ben = f"{s['bench_made'] / s['bench_turns']:.0%}" if s["bench_turns"] else "—"
                lines.append(f"  {tag.replace('>', ' vs '):<22}{who:<5}{s['turns']:>7}"
                             f"{s['win_missed']:>9} of {s['win_turns']:<5}{s['ko_missed']:>8} of {s['ko_turns']:<5}"
                             f"{att:>10}{ben:>9}{per(s, 'give_attack'):>11.1f}  {cu:>24}")
        text = "\n".join(lines)
        print(text)
        out.write_text(json.dumps({"summary": text, "stats": stats, "replay_problems": bad, "complete": bad == 0,
                                   "failed_replays": failed[:50], "inputs": inputs,
                                   "winnable_q": S["checkup_report"]["winnable_q"]}, indent=1))


if __name__ == "__main__":
    main()
