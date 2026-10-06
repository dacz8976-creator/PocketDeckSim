#!/usr/bin/env python3
"""Gate 3's reading (fixed before any game): the Tool rule on v off, paired on the development run's own deals.

  python3 rl/results/playout_tool_rule_2026-10-06/gate3/pair_with_dev.py RUN_DIR [RUN_DIR ...]   (from the repository root)

Each RUN_DIR is a gate-3 strength run (pilot kx3_r16_c12_z2_real_t0_poolmeta_tools, reference km3) whose seeds reproduce
the development run's deals (rl/results/strength_2026-10-03_kx3_dev, "the dev run"). Its X arm is kx3 with the rule on;
the dev run's X arm, on the same key (deck, opponent, deal, seat), is kx3 with the rule off.

1. The build check: every reference (km3 v km3) game must equal the dev run's game for game and decision for decision
   (timings aside), and so must any X game of a replay run with the rule off. If one differs, the pairing is void: say so.
2. Per deck and pooled: on - off in game score (win 1, tie 1/2, loss 0), mean +- 1.96 sd / sqrt(n), n paired games; how
   many of the pairs differ at all (any logged decision); and, for context, kx3 - km3 with the rule on (this run) and
   off (the dev run) on the same keys.
"""
import json, math, os, sys
from collections import defaultdict

DEV = "rl/results/strength_2026-10-03_kx3_dev/games.jsonl"


def load(p):
    return {x["key"]: x for x in (json.loads(l) for l in open(p, encoding="utf-8") if l.strip())}


def facts(x):
    return (x["seed"], x["first"], x["winner"], x["points"], x["turns"], x["plies"], x["moves_deck"]["n"], x["moves_opp"]["n"],
            [{k: v for k, v in d.items() if k != "ms"} for d in (x.get("log") or [])])


def score(x):
    return {"deck": 1.0, "tie": 0.5, "opp": 0.0}[x["winner"]]


def ci(ds):
    n = len(ds)
    if n == 0:
        return "n 0"
    m = sum(ds) / n
    sd = math.sqrt(sum((d - m) ** 2 for d in ds) / (n - 1)) if n > 1 else float("nan")
    h = 1.96 * sd / math.sqrt(n) if n > 1 else float("nan")
    return f"{100 * m:+.1f} +- {100 * h:.1f} points (n {n})"


def main():
    dev = load(DEV)
    runs = sys.argv[1:]
    if not runs:
        sys.exit(__doc__)
    ref_same = ref_diff = 0
    rows = defaultdict(list)  # deck -> [(opp, on - off, differs, on - km3, off - km3)]
    void = False
    for r in runs:
        man = json.load(open(os.path.join(r, "manifest.json"), encoding="utf-8"))
        tools = man["pilot"].endswith("_tools")
        games = load(os.path.join(r, "games.jsonl"))
        for k, g in sorted(games.items()):
            if k not in dev:
                print("NOT A DEV-RUN DEAL:", k)
                void = True
                continue
            if g["arm"] == "ref" or not tools:
                if facts(g) == facts(dev[k]):
                    ref_same += 1
                else:
                    ref_diff += 1
                    print("DIFFERS FROM THE DEV RUN:", k)
        for k, g in sorted(games.items()):
            if g["arm"] != "X" or not tools or k not in dev:
                continue
            kr = k[: -len("X")] + "ref"
            on, off = score(g), score(dev[k])
            km_on = score(games[kr]) if kr in games else None
            km_off = score(dev[kr])
            rows[g["deck"]].append((g["opp"], on - off, facts(g) != facts(dev[k]), None if km_on is None else on - km_on, off - km_off))
    print(f"build check: {ref_same} games replay the dev run exactly, {ref_diff} differ")
    if ref_diff or void:
        print("THE PAIRING IS VOID: this build does not replay the dev run; on - off can't be read against it")
        return
    pooled, per_deck_means = [], []
    for deck, rs in rows.items():
        ds = [x[1] for x in rs]
        pooled += ds
        per_deck_means.append(sum(ds) / len(ds))
        print(f"\n{deck}: rule on - off {ci(ds)}; pairs that differ at all {sum(x[2] for x in rs)} of {len(rs)}")
        print(f"  for context, on the same deals: kx3 - km3 with the rule on {ci([x[3] for x in rs if x[3] is not None])}, off {ci([x[4] for x in rs])}")
        by_opp = defaultdict(list)
        for x in rs:
            by_opp[x[0]].append(x)
        for o, xs in by_opp.items():
            print(f"  v {o}: games gained with the rule on, net {sum(x[1] for x in xs):+.1f} of {len(xs)} pairs ({sum(x[2] for x in xs)} differ at all)")
    if pooled:
        print(f"\npooled: rule on - off {ci(pooled)}; every deck weighted equally {100 * sum(per_deck_means) / len(per_deck_means):+.1f} points")


if __name__ == "__main__":
    main()
