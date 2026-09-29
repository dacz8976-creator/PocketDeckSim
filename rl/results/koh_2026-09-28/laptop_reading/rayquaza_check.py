"""koh's Rayquaza pre-set check (kph registration section 5 step 4; diagnostic, reported, never gating): the same 200
Rayquaza v Lucario deals (21,108,900,000+), kp3 on Lucario, koh3 or kpf3 on Rayquaza, replayed on the official engine
with trace_pilot.py --per-game (../laptop_runs/). Paired 95% intervals (bootstrap over deals, 20,000 draws, fixed seed)
for koh3 minus kpf3 on wins and on each use rate (Scorching Interruption, Mega Burst: own turns used / own turns
offered). Section 6's line: "the paired interval ... lies wholly below zero on wins or on either use rate" is a
finding (A or B reaches the discard lines), gating nothing.
Consistency first: each arm's totals must equal its existing trace page (kpf3: ../../kpf_2026-09-26/reading/
trace_rayquaza_v_lucario_kpf3.txt, the Sept 27 engine; koh3: the cloud's trace, rl/results/koh_2026-09-28/reading/ on
the branch, passed as argv[1]). Usage: python3 rayquaza_check.py <cloud koh3 trace page>"""
import json, os, random, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); RUNS = os.path.join(HERE, "..", "laptop_runs")
KPF_PAGE = os.path.join(HERE, "..", "..", "kpf_2026-09-26", "reading", "trace_rayquaza_v_lucario_kpf3.txt")
SI, MB = "attack:Gouging Fire:Scorching Interruption", "attack:Mega Rayquaza ex:Mega Burst"


def rows(bot):
    return {r["seed"]: r for r in map(json.loads, open(os.path.join(RUNS, f"trace_rayquaza_v_lucario_{bot}_pergame.jsonl")))}


def page_totals(path):
    t = open(path, encoding="utf-8").read()
    wins = int(re.search(r"seat 0 won (\d+)", t).group(1))
    out = {"wins": wins}
    for lab in (SI, MB):
        m = re.search(re.escape(lab[:50]) + r"\s+turns offered\s+(\d+), used\s+(\d+)", t)
        out[lab] = (int(m.group(1)), int(m.group(2)))
    return out


def totals(r):
    out = {"wins": sum(x["won"] for x in r.values())}
    for lab in (SI, MB):
        out[lab] = (sum(x["attacks"].get(lab, [0, 0])[0] for x in r.values()), sum(x["attacks"].get(lab, [0, 0])[1] for x in r.values()))
    return out


koh, kpf = rows("koh3"), rows("kpf3")
assert koh.keys() == kpf.keys() and len(koh) == 200, (len(koh), len(kpf))
ok = True
for name, r, page in (("kpf3", kpf, KPF_PAGE), ("koh3", koh, sys.argv[1])):
    a, b = totals(r), page_totals(page)
    same = a == b
    ok &= same
    print(f"consistency, {name}: replay {a['wins']} wins, SI {a[SI]}, MB {a[MB]} | page {b['wins']} wins, SI {b[SI]}, MB {b[MB]} -> {'equal' if same else 'DIFFERENT'}")
if not ok:
    raise SystemExit("the replays don't reproduce the trace pages; nothing read")
seeds = sorted(koh)
rng = random.Random(2810928)


def stat(sample):
    w = sum(koh[s]["won"] - kpf[s]["won"] for s in sample) / len(sample)
    rates = []
    for lab in (SI, MB):
        ko = [koh[s]["attacks"].get(lab, [0, 0]) for s in sample]; kf = [kpf[s]["attacks"].get(lab, [0, 0]) for s in sample]
        rk = sum(u for _, u in ko) / max(1, sum(o for o, _ in ko)); rf = sum(u for _, u in kf) / max(1, sum(o for o, _ in kf))
        rates.append(rk - rf)
    return [w] + rates


point = stat(seeds)
draws = [stat([seeds[rng.randrange(len(seeds))] for _ in seeds]) for _ in range(20000)]
names = ("wins per game", "Scorching Interruption use rate", "Mega Burst use rate")
below = []
print("\nkoh3 minus kpf3, paired over the 200 deals (bootstrap 95%):")
for j, n in enumerate(names):
    col = sorted(d[j] for d in draws)
    lo, hi = col[int(0.025 * len(col))], col[int(0.975 * len(col)) - 1]
    print(f"  {n:34} {point[j]:+.3f}  [{lo:+.3f}, {hi:+.3f}]{'  WHOLLY BELOW ZERO' if hi < 0 else ''}")
    below += [n] if hi < 0 else []
print("\nFinding (section 6, reported, gating nothing):",
      "the discard lines are reached: " + ", ".join(below) if below else "Rayquaza's gain is not reached (no interval wholly below zero)")
