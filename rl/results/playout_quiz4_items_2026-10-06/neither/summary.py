"""Quiz 4, item 3: the continuation experiment at the "neither" positions, summarized from run/study.jsonl (the runner
playout_continuation, R = 128, LAB) and the positions' index (states/index.json: kx3's own decision in the game).
Scores are the pilot's (win 1, tie 1/2, loss 0); leads are paired over the same 128 worlds, with 95% intervals.
Run from the repository root:
  python3 rl/results/playout_quiz4_items_2026-10-06/neither/summary.py"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
lines = [json.loads(l) for l in open(HERE / "run" / "study.jsonl", encoding="utf-8")]
plans = {e["id"]: e for e in json.load(open(HERE / "plans.json", encoding="utf-8"))}
index = {e["id"]: e for e in json.load(open(HERE / "states" / "index.json", encoding="utf-8"))}


def iv(v):
    return f"{v['mean']:+.3f} [{v['lo']:+.3f}, {v['hi']:+.3f}]"


print("## The studies (each first move continued by km3, and by Dustin's plan for K own turns, then km3)")
print()
print("| entry | K | Dustin's first move: km3 / plan | the rival: km3 / plan | lead, km3's continuation | lead, the plan's | verdict |")
print("|---|---|---|---|---|---|---|")
for l in lines:
    if l["kind"] != "study":
        continue
    p, r = l["plans_first_move"], l["rival"]
    print(f"| {l['id']} | {l['k']} | {p['km3_continuation']['mean']:.3f} / {p['plan_continuation']['mean']:.3f} "
          f"| {plans[l['id']]['rival_is'].split(' (')[0]}: {r['km3_continuation']['mean']:.3f} / {r['plan_continuation']['mean']:.3f} "
          f"| {iv(l['lead_under_km3'])} | {iv(l['lead_under_plan'])} | {l['verdict'].split(':')[0]} |")
print()
print("## Dustin's plan against each rival's own line (his first move continued by his plan, minus the rival continued by")
print("km3: the line each bot would play), round by round in the same worlds; and how often his plan and km3's continuation")
print("of his first move end in the same final state")
print()
print("| entry | his plan | the rival's line | his plan minus the rival's line | his plan and km3's continuation: same final state |")
print("|---|---|---|---|---|")
for l in lines:
    if l["kind"] != "study":
        continue
    p, r = l["plans_first_move"], l["rival"]
    d = [a[0] - b[0] for a, b in zip(p["rounds_detail"]["plan"], r["rounds_detail"]["km3"])]
    n = len(d)
    m = sum(d) / n
    se = (sum((x - m) ** 2 for x in d) / (n - 1)) ** 0.5 / n ** 0.5
    print(f"| {l['id']} | {p['plan_continuation']['mean']:.3f} | {plans[l['id']]['rival_is'].split(' (')[0]}: {r['km3_continuation']['mean']:.3f} "
          f"| {m:+.3f} [{m - 1.96 * se:+.3f}, {m + 1.96 * se:+.3f}] | {p['same_final_state']} of {n} |")
print()
print("Checks: every round played (failed rounds: " + ", ".join(f"{l['id']} {l['failed_rounds']}" for l in lines if l["kind"] == "study")
      + "); the study's km3 scores equal kx3's own play-out scores at the same seed (run/study_stderr.txt).")
print()
print("## How often the plan's steps were played (of 128; after Dustin's first move, then after the rival)")
for l in lines:
    if l["kind"] != "study":
        continue
    for key in ("plans_first_move", "rival"):
        steps = "; ".join(f"t{s['game_turn']} {s['step']['do']} {s['played']}/{s['skipped']}/{s['unreached']}" for s in l[key]["steps"])
        print(f"- {l['id']}, {'Dustin' if key == 'plans_first_move' else 'rival'}: {steps} (played/skipped/unreached)")
print()
print("## Round 0's moves within the window")
for l in lines:
    if l["kind"] != "study":
        continue
    for key in ("plans_first_move", "rival"):
        print(f"- {l['id']}, {'Dustin' if key == 'plans_first_move' else 'rival'}, km3's continuation: " + " | ".join(l[key]["round_0_km3_trace"]))
        print(f"  {l['id']}, {'Dustin' if key == 'plans_first_move' else 'rival'}, the plan's: " + " | ".join(l[key]["round_0_plan_trace"]))
print()
print("## kx3 at each position: 128 rounds, LAB, the study's seed (every candidate's score under km3's continuation)")
for l in lines:
    if l["kind"] != "kx3":
        continue
    print(f"- {l['id']}: kx3 plays {l['chosen']}; {l['reason']}")
    for c in l["candidates"]:
        print(f"    {c['move']}: {c['score']:.3f} ({c['diff']:+.3f} over km3's move, SE {c['se']:.3f})")
print()
print("## kx3 in the game itself (16 rounds, its own knowledge mode; the game's observation and randomness)")
for id_, e in index.items():
    if "then" in e and e["then"]:
        continue
    k = e["kx3_in_the_game"]
    print(f"- {id_}: kx3 played {k['chosen']} (the kx3 arm's log says {k['kx3_arm_logged']}); {k['report']['reason']}")
    for c in k["report"]["candidates"]:
        se = f"{c['se']:.3f}" if c["se"] is not None else "-"
        print(f"    {c['move']}: {c['score']:.3f} ({c['diff']:+.3f}, SE {se})")
