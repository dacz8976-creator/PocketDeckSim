"""What each habit costs in the 8 positions' play-outs (Oct 5): the continuation study's worlds, the pilot's side played by
km3 as usual and by km3 with one Trainer withheld for 10 own turns (the accepted plan continuation with an `avoid` rule
and no steps). Paired per round. Each run's km3 arm must equal the study's (run 2), round for round. Run from the
repository root: python3 rl/results/playout_trainer_habits_2026-10-05/withhold.py > .../withhold.txt
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
STUDY = {json.loads(l)["id"]: json.loads(l) for l in open(HERE.parent / "playout_continuation_2026-10-05/run/study.jsonl", encoding="utf-8")}


def stats(xs):
    n = len(xs)
    m = sum(xs) / n
    se = (sum((x - m) ** 2 for x in xs) / (n - 1)) ** 0.5 / n ** 0.5
    return m, m - 1.96 * se, m + 1.96 * se


for card, slug in (("Copycat", "copycat"), ("Elegant Cape", "elegant_cape"), ("Irida", "irida")):
    path = HERE / f"withhold_{slug}.jsonl"
    if not path.exists():
        continue
    print(f"## {card} withheld from the pilot's side (draft A) for 10 own turns")
    print("| # | Position | first move | km3 | withheld | withheld - km3 [95%] | the rival: km3 | withheld | withheld - km3 [95%] |")
    print("|---|---|---|---|---|---|---|---|---|")
    same = True
    for i, line in enumerate(open(path, encoding="utf-8"), 1):
        d = json.loads(line)
        row = []
        for key in ("plans_first_move", "rival"):
            m = d[key]
            km = [r[0] for r in m["rounds_detail"]["km3"]]
            wh = [r[0] for r in m["rounds_detail"]["plan"]]
            same &= m["rounds_detail"]["km3"] == STUDY[d["id"]][key]["rounds_detail"]["km3"]
            diff = stats([w - k for w, k in zip(wh, km)])
            row.append(f"{sum(km) / len(km):.3f} | {sum(wh) / len(wh):.3f} | {diff[0]:+.3f} [{diff[1]:+.3f}, {diff[2]:+.3f}]")
        label = d["plans_first_move"]["round_0_plan_trace"][0].split(": ", 1)[1] if d["plans_first_move"]["round_0_plan_trace"] else ""
        print(f"| {i} | {d['id']} | {label} | {row[0]} | {row[1]} |")
    print(f"\nThe km3 arm equals the continuation study's, round for round, at every position: {same}\n")
