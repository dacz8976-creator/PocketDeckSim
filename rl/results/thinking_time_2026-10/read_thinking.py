#!/usr/bin/env python3
"""The thinking-time test's reading, as fixed in PLAN.md before any game: for each setting S (m32, m16), S - frozen in game score (win 1, tie 1/2,
loss 0) on the same (deck, opponent, deal, seat), mean +- 1.96 sd/sqrt(n) over the 480 pairs; also S - candidate and candidate - frozen on the same
pairs; pooled, every deck weighted equally, per group and per deck; pace (turns per game, the deck's first-attack own turn); time per kx3 game.
Reading: the cheapest setting (m16, then m32, then the candidate m64) whose S - frozen interval is entirely above zero is the recommended deck tester.
Run from the repository root; prints the report (READING.md is written from it)."""
import json, math, statistics as st
from collections import defaultdict

R = "rl/results"
DECKS = ["09-mega-manectric-heliolisk", "06-mega-blaziken-tournament-list", "10-xatu-oricorio-tr-weezing",
         "01-muk-glimmora-kingambit-regigigas", "05-indeedee-stoutland", "draft-A-shark-tempo"]
GROUP = {DECKS[0]: "fast", DECKS[1]: "fast", DECKS[2]: "fast", DECKS[3]: "setup", DECKS[4]: "setup", DECKS[5]: "middle"}


def load(paths, arm="X"):
    out = {}
    for p in paths:
        for l in open(p):
            if l.strip():
                g = json.loads(l)
                if g["arm"] == arm and g["deck"] in GROUP:
                    out[g["key"]] = g
    return out


def score(g):
    return {"deck": 1.0, "tie": 0.5, "opp": 0.0}[g["winner"]]


def first_attack_own_turn(g):
    first = g.get("first") == "deck"
    for e in g.get("log") or []:
        if isinstance(e, dict) and str(e.get("a", "")).startswith("Attack"):
            t = e["t"]
            return (t + 1) // 2 if first else t // 2
    return None


T = f"{R}/thinking_time_2026-10"
arms = {
    "frozen": load([f"{R}/strength_2026-10-03_kx3_dev/games.jsonl"]),
    "candidate": load([f"{R}/strength_2026-10-08_kx3_combined/games.jsonl"]),
    "m32": load([f"{T}/reg_m32_a/games.jsonl", f"{T}/reg_m32_b/games.jsonl"]),
    "m16": load([f"{T}/reg_m16_a/games.jsonl", f"{T}/reg_m16_b/games.jsonl"]),
}
keys = sorted(set(arms["m32"]) & set(arms["m16"]) & set(arms["frozen"]) & set(arms["candidate"]))
assert len(keys) == 480, len(keys)
for a, d in arms.items():
    seeds = {k: d[k]["seed"] for k in keys}
    assert seeds == {k: arms["frozen"][k]["seed"] for k in keys}, a


def ci(diffs):
    n = len(diffs)
    m = st.mean(diffs)
    sd = st.stdev(diffs) if n > 1 else 0.0
    return 100 * m, 100 * 1.96 * sd / math.sqrt(n)


def row(label, ks, a, b):
    m, h = ci([score(arms[a][k]) - score(arms[b][k]) for k in ks])
    return f"{label}: {m:+.1f} +- {h:.1f} (n {len(ks)})"


def deck_equal(a, b):
    per = [st.mean([score(arms[a][k]) - score(arms[b][k]) for k in keys if arms[a][k]["deck"] == d]) for d in DECKS]
    return 100 * st.mean(per)


lines = [f"Pairs: {len(keys)} (6 decks x 8 opponents x 5 deals x 2 seats); seeds identical across all four arms on every key.", ""]
lines.append("WIN RATE (score per 100 games) per arm: " + ", ".join(f"{a} {100 * st.mean(score(arms[a][k]) for k in keys):.1f}" for a in arms))
lines.append("")
for s in ("m16", "m32", "candidate"):
    lines.append(f"== {s} - frozen (PRIMARY for m16 and m32)")
    lines.append("  " + row("pooled", keys, s, "frozen") + f"; every deck weighted equally {deck_equal(s, 'frozen'):+.1f}")
    for grp in ("fast", "setup", "middle"):
        lines.append("  " + row(f"group {grp}", [k for k in keys if GROUP[arms[s][k]['deck']] == grp], s, "frozen"))
    for d in DECKS:
        lines.append("  " + row(f"deck {d}", [k for k in keys if arms[s][k]["deck"] == d], s, "frozen"))
for s in ("m16", "m32"):
    lines.append(f"== {s} - candidate (what the cheaper setting loses)")
    lines.append("  " + row("pooled", keys, s, "candidate"))
    for grp in ("fast", "setup", "middle"):
        lines.append("  " + row(f"group {grp}", [k for k in keys if GROUP[arms[s][k]['deck']] == grp], s, "candidate"))
lines.append("== m32 - m16")
lines.append("  " + row("pooled", keys, "m32", "m16"))
lines.append("")
lines.append("PACE (mean over the 480 games): turns per game; the deck's first-attack own turn (games with an attack)")
for a in arms:
    turns = st.mean(arms[a][k]["turns"] for k in keys)
    fa = [first_attack_own_turn(arms[a][k]) for k in keys]
    fa = [x for x in fa if x is not None]
    lines.append(f"  {a}: turns {turns:.2f}, first attack own turn {st.mean(fa):.2f} ({len(fa)} games)")
lines.append("")
lines.append("TIME per kx3 game (wall_s): frozen and candidate on the laptop; m32 and m16 in 4-core Managed Agents sandboxes at --threads 2")
for a in arms:
    w = [arms[a][k]["wall_s"] for k in keys]
    lines.append(f"  {a}: mean {st.mean(w):.0f} s, median {st.median(w):.0f} s" + (f"; laptop-equivalent estimate (/2.7) {st.mean(w) / 2.7:.0f} s" if a in ("m32", "m16") else ""))
for d in DECKS:
    lines.append(f"  deck {d}: " + ", ".join(f"{a} {st.mean(arms[a][k]['wall_s'] for k in keys if arms[a][k]['deck'] == d):.0f}" for a in arms))
lines.append("")
rec = None
for s in ("m16", "m32", "candidate"):
    m, h = ci([score(arms[s][k]) - score(arms["frozen"][k]) for k in keys])
    if m - h > 0:
        rec = s
        break
lines.append("READING (fixed in PLAN.md): the cheapest setting whose S - frozen interval is entirely above zero: "
             + (rec if rec else "none of the three (the candidate's own interval on these 480 pairs is not above zero either)"))
print("\n".join(lines))
