"""Gate 2's summary: the rule on v off at each position, every move kx3 would consider, paired on the same worlds and seeds.
  python3 rl/results/playout_tool_rule_2026-10-06/gate2/summarize.py   (from the repository root; writes gate2/summary.txt)"""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
out = []
P = out.append


def short(m, n=70):
    return m if len(m) <= n else m[: n - 3] + "..."


def stats(xs):
    n = len(xs)
    m = sum(xs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1)) if n > 1 else 0.0
    return m, sd / math.sqrt(n)


def choice(scores, z=2.0):  # kx3's own rule, as in engine/examples/playout_tool_rule.rs
    means = [sum(s) / len(s) for s in scores]
    best = 0
    for c in range(len(means)):
        if means[c] > means[best]:
            best = c
    if best == 0:
        return 0
    d, se = stats([a - b for a, b in zip(scores[best], scores[0])])
    return best if d > 0 and d > z * se else 0


allmoves = []
for part in ["continuation", "development"]:
    rows = [json.loads(l) for l in open(os.path.join(HERE, f"{part}.jsonl"))]
    P(f"== {part}: {len(rows)} positions, {rows[0]['rounds']} play-outs per move")
    for r in rows:
        acted = sum(m["rounds_acted"] for m in r["moves"])
        total = len(r["moves"]) * r["rounds"]
        P(f"\n{r['id']}  (the rule acted in {acted} of {total} play-outs, {sum(m['interventions'] for m in r['moves'])} placements changed)")
        P(f"  kx3's choice, rule off: {short(r['kx3_choice_off'])}")
        P(f"  kx3's choice, rule on:  {short(r['kx3_choice_on'])}" + ("   <- CHANGED" if r["kx3_choice_off"] != r["kx3_choice_on"] else ""))
        for i, m in enumerate(r["moves"]):
            off = [x[0] for x in m["rounds_detail"]["off"]]
            on = [x[0] for x in m["rounds_detail"]["on"]]
            sig = "*" if (m["lo"] > 0 or m["hi"] < 0) else " "
            P(f"  {'km3' if i == 0 else '   '} {short(m['move'], 60):60s} off {m['off']:.3f} on {m['on']:.3f}  on-off {m['on_minus_off']:+.3f} [{m['lo']:+.3f}, {m['hi']:+.3f}]{sig} acted {m['rounds_acted']:3d}/{len(on)}")
            allmoves.append((part, r["id"], m))
    P("")
P("== pooled over every move")
for part in ["continuation", "development"]:
    ms = [m for p, _, m in allmoves if p == part]
    acted = [m for m in ms if m["rounds_acted"] > 0]
    sig = [m for m in ms if m["lo"] > 0 or m["hi"] < 0]
    if acted:
        mean_abs = sum(abs(m["on_minus_off"]) for m in acted) / len(acted)
        mean = sum(m["on_minus_off"] for m in acted) / len(acted)
        P(f"{part}: {len(ms)} moves; the rule acted in some play-out of {len(acted)}; on - off over those: mean {mean:+.3f}, mean size {mean_abs:.3f}; "
          f"95% interval excluding 0: {len(sig)} (" + (", ".join("%+.3f" % m["on_minus_off"] for m in sig) or "none") + ")")
    else:
        P(f"{part}: {len(ms)} moves; the rule acted in no play-out")
open(os.path.join(HERE, "summary.txt"), "w").write("\n".join(out) + "\n")
print("\n".join(out))
