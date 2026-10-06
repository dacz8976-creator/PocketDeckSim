"""The exam's reading addendum (READING_ADDENDUM.md, fixed before the result was read): fast v setup groups and pace.

Groups: the 11 held-out decks ranked by the mean turns of the reference arm (km3 on the deck v the panel) in this exam;
the 4 shortest = fast, the 4 longest = setup, the middle 3 unlabelled; deck 07 (Skarmory stall) is setup by Dustin's
word whatever its rank (the next-longest then moves to the middle). Per group and per deck, paired (kx3 arm minus km3
arm, same deck, opponent, deal, seat): score gain, turns per game, and the deck's first-attack own turn (a game with no
attack counts at its last own turn). Also the development run by its own groups. Run from the repository root.
"""
import json, math, statistics as st, collections, sys

def load(p):
    return {(x["arm"], x["deck"], x["opp"], x["seed"], x["seat"]): x for x in (json.loads(l) for l in open(p) if l.strip())}

SC = {"deck": 1.0, "tie": 0.5, "opp": 0.0}
def first_attack(g):
    log = g.get("log") or []
    own = [d.get("o", 0) for d in log]
    att = [d.get("o", 0) for d in log if str(d.get("a", "")).startswith("Attack:")]
    return min(att) if att else (max(own) if own else 0)

def ci(v):
    n = len(v); m = st.mean(v); h = 1.96 * st.stdev(v) / math.sqrt(n) if n > 1 else float("nan")
    return m, h, n

def table(games, groups, title, pct=True):
    keys = sorted(k[1:] for k in games if k[0] == "X")
    rows = collections.defaultdict(lambda: {"s": [], "t": [], "f": []})
    for k in keys:
        x, r = games[("X",) + k], games[("ref",) + k]
        for grp in ["all", groups.get(k[0], "middle"), k[0]]:
            rows[grp]["s"].append(SC[x["winner"]] - SC[r["winner"]])
            rows[grp]["t"].append(x["turns"] - r["turns"])
            rows[grp]["f"].append(first_attack(x) - first_attack(r))
    print(f"\n### {title}\n")
    print("| group or deck | paired games | score gain (points) | turns per game, kx3 − km3 | first-attack own turn, kx3 − km3 |")
    print("|---|---|---|---|---|")
    order = ["all", "fast", "setup", "middle"] + sorted(k for k in rows if k not in ("all", "fast", "setup", "middle"))
    for grp in order:
        if grp not in rows: continue
        d = rows[grp]; s, t, f = ci(d["s"]), ci(d["t"]), ci(d["f"])
        label = grp if grp in ("all", "fast", "setup", "middle") else f"{grp} ({groups.get(grp, 'middle')})"
        print(f"| {label} | {s[2]} | {100*s[0]:+.1f} ± {100*s[1]:.1f} | {t[0]:+.2f} ± {t[1]:.2f} | {f[0]:+.2f} ± {f[1]:.2f} |")

ex = load("rl/results/strength_2026-10-05_kx3_exam/games.jsonl")
decks = sorted({k[1] for k in ex})
ref_turns = {d: st.mean(g["turns"] for k, g in ex.items() if k[0] == "ref" and k[1] == d) for d in decks}
ranked = sorted(decks, key=lambda d: ref_turns[d])
setup = ["07-skarmory-stall"] + [d for d in reversed(ranked) if d != "07-skarmory-stall"][:3]
fast = [d for d in ranked if d not in setup][:4]
groups = {d: ("setup" if d in setup else "fast" if d in fast else "middle") for d in decks}
print("Reference-arm (km3) mean turns per deck, shortest first:")
for d in ranked: print(f"- {d}: {ref_turns[d]:.2f} turns -> {groups[d]}")
table(ex, groups, "The exam (held-out decks, fresh deals)")

dev = load("rl/results/strength_2026-10-03_kx3_dev/games.jsonl")
dgroups = {"09-mega-manectric-heliolisk": "fast", "06-mega-blaziken-tournament-list": "fast", "10-xatu-oricorio-tr-weezing": "fast",
           "03-wailord-indeedee-wall": "setup", "01-muk-glimmora-kingambit-regigigas": "setup", "05-indeedee-stoutland": "setup"}
table(dev, dgroups, "The development run, by its own groups (draft A in the middle row)")
