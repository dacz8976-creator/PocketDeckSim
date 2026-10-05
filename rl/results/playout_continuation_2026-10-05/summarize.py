"""The continuation experiment's summary (Oct 5): reads <folder>/study.jsonl (and <folder>/kx3.jsonl and
<folder>/variant_t18_k1.jsonl if present; the folder is run, the default, or run1) and prints, per
position, both first moves' scores under km3's continuation and under the plan's, the paired leads with 95% intervals,
the verdict, how often each scripted step was played, skipped or never reached, round 0's move logs, and kx3's line
(checked against the study: the two moves' km3 scores must be their kx3 scores, since both use the same worlds and seeds).
Run from the repository root: python3 rl/results/playout_continuation_2026-10-05/summarize.py [run | run1]
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = HERE / (sys.argv[1] if len(sys.argv) > 1 else "run")
study = [json.loads(l) for l in open(RUN / "study.jsonl", encoding="utf-8")]
if (RUN / "variant_t18_k1.jsonl").exists():
    for l in open(RUN / "variant_t18_k1.jsonl", encoding="utf-8"):
        v = json.loads(l)
        v["id"] += " (variant: K = 1)"
        study.append(v)
study = [s for s in study if s["kind"] == "study"]
kx3 = {}
if (RUN / "kx3.jsonl").exists():
    for l in open(RUN / "kx3.jsonl", encoding="utf-8"):
        d = json.loads(l)
        kx3[d["id"]] = d


def ci(v):
    return f"{v['mean']:+.3f} [{v['lo']:+.3f}, {v['hi']:+.3f}]"


def first_line(m):
    t = m["round_0_plan_trace"]
    return t[0].split(": ", 1)[1] if t else m["move"][:60]


print("| # | Position | K | R | Plan's first move: km3 / plan | Rival: km3 / plan | Lead, km3's continuation | Lead, the plan's | Change | Verdict |")
print("|---|---|---|---|---|---|---|---|---|---|")
for i, s in enumerate(study, 1):
    p, r = s["plans_first_move"], s["rival"]
    print(
        f"| {i} | {s['id']} | {s['k']} | {s['rounds']} | {first_line(p)}: {p['km3_continuation']['mean']:.3f} / "
        f"{p['plan_continuation']['mean']:.3f} | {first_line(r)} ({s['rival_is']}): {r['km3_continuation']['mean']:.3f} / "
        f"{r['plan_continuation']['mean']:.3f} | {ci(s['lead_under_km3'])} | {ci(s['lead_under_plan'])} | "
        f"{ci(s['lead_change'])} | {s['verdict'].split(':')[0]} |"
    )
print()
print("Plan minus km3's continuation, per first move (the same first move, the two continuations):")
for s in study:
    p, r = s["plans_first_move"], s["rival"]
    print(f"  {s['id']}: the plan's first move {ci(p['plan_minus_km3'])}; the rival {ci(r['plan_minus_km3'])}")
for s in study:
    print()
    print(f"== {s['id']} (K = {s['k']}, {s['rounds']} rounds, {s['failed_rounds']} failed, {s['ms'] / 1000:.0f} s; {s['knowledge'][:60]}...)")
    print(f"   verdict: {s['verdict']}")
    for key, title in (("plans_first_move", "the plan's first move"), ("rival", "the rival")):
        m = s[key]
        print(f"   -- {title}: {first_line(m)}")
        print(f"      plan's moves {m['plan_moves']} (promotions {m['promotions']}), km3's fill-ins {m['km3_fills']}, "
              f"plan's attack for km3's turn end {m['plan_attack_replaced_km3s_end']}, rounds ending as km3's did {m['same_final_state']}")
        for st in m["steps"]:
            step = dict(st["step"])
            what = step.pop("do")
            print(f"      turn {st['game_turn']:>2} {what:<12} {json.dumps(step, ensure_ascii=False):<70} "
                  f"played {st['played']:>3}  skipped {st['skipped']:>3}  unreached {st['unreached']:>3}")
        print("      round 0, the plan's continuation: " + " | ".join(m["round_0_plan_trace"]))
        print("      round 0, km3's continuation:      " + " | ".join(m["round_0_km3_trace"])
              + ("" if m["round_0_km3_trace_is_km3s_play_out"] else "  (NOT km3's play-out)"))
    k = kx3.get(s["id"])
    if k:
        scores = {c["move"]: c["score"] for c in k["candidates"]}
        checks = []
        for key in ("plans_first_move", "rival"):
            m = s[key]
            got = scores.get(m["move"])
            checks.append("missing" if got is None else ("same" if abs(got - m["km3_continuation"]["mean"]) < 1e-12 else f"DIFFERENT ({got})"))
        print(f"   kx3 ({k['code']}, seed {k['seed']}, {k['rounds']} rounds, {k['ms'] / 1000:.0f} s): chose {k['chosen'][:70]}; "
              f"{k['reason']}; the two moves' km3 scores in kx3's report: {checks[0]}, {checks[1]}")
        for c in sorted(k["candidates"], key=lambda c: -c["score"]):
            print(f"      {c['score']:.3f}  {c['diff']:+.3f} (se {c['se']:.3f})  {c['move'][:90]}")
