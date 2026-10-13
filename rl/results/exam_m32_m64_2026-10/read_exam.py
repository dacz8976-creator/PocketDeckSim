#!/usr/bin/env python3
"""The held-out exam of m32 and m64: the reading, as fixed in PLAN.md before any game. Written Oct 13, before registration.

On the 528 (deck, opponent, deal, seat) pairs of the Oct 5 exam's deals, in game score (win 1, tie 1/2, loss 0), mean +- 1.96 sd/sqrt(n):
PRIMARY m32 - frozen, m64 - frozen and m64 - m32; also each against km3 (and the frozen kx3's own Oct 5 figure). Each pooled, per group
(setup first) and per deck, with how many games differ each way; pace (turns per game, the deck's first-attack own turn); time per kx3 game.
The pick (PLAN.md): m64 if it gains on the frozen kx3 and plays detectably better than m32; else m32 if it gains; else m64 if it gains (the
only setting with a shown gain, not shown better than m32); else the frozen kx3 stays.
Run from the repository root once both registrations are merged COMPLETE. `--selftest` checks the pick on fixed cases and runs the report on
stand-ins built from the Oct 5 exam's own kx3 and km3 games, which say nothing about the exam."""
import json, math, statistics as st, sys

R = "rl/results"
E = f"{R}/exam_m32_m64_2026-10"
EXAM = f"{R}/strength_2026-10-05_kx3_exam/games.jsonl"
PILOT = {"m32": "kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m32", "m64": "kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m64"}
# groups by km3's mean turns per game on these decks in the Oct 5 exam (../strength_2026-10-05_kx3_exam/GROUPS_AND_PACE.md), fixed now
GROUP = {"draft-D-entei-grimhound": "fast", "12-ariados-whimsicott-ogerpon": "fast", "15-jolteon-oricorio-raticate": "fast",
         "14-comfey-raticate-hypno": "fast", "02-arceus-crobat": "middle", "04-absol-hoopa-darkrai": "middle", "08-garchomp-toolbox": "middle",
         "13-a-ninetales-raticate": "setup", "11-archaludon-haxorus-dragonair": "setup", "draft-C-meowstic-hatterene-v2": "setup",
         "07-skarmory-stall": "setup"}
DECKS = list(GROUP)
GROUPS = ("setup", "middle", "fast")


def fail(msg):
    sys.exit(f"REFUSED: {msg}; nothing is read.")


def pair_key(g):
    return (g["deck"], g["opp"], g["deal"], g["seat"])


def load(path, arm):
    out = {}
    for l in open(path):
        if l.strip():
            g = json.loads(l)
            if g["arm"] == arm:
                if pair_key(g) in out:
                    fail(f"{path} holds {g['key']} twice")
                out[pair_key(g)] = g
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


def ci(diffs):
    """(mean, half-width) in points per 100 games."""
    n = len(diffs)
    m = st.mean(diffs)
    sd = st.stdev(diffs) if n > 1 else 0.0
    return 100 * m, 100 * 1.96 * sd / math.sqrt(n)


def above(c):
    return c[0] - c[1] > 0


def below(c):
    return c[0] + c[1] < 0


def bounds(c, nd=1):
    return f"{c[0] - c[1]:+.{nd}f} to {c[0] + c[1]:+.{nd}f}"


def pick(g32, g64, d):
    """PLAN.md's selection rule. g32 = m32 - frozen, g64 = m64 - frozen, d = m64 - m32, each (mean, half-width). Returns (pick, step)."""
    if above(g64) and above(d):
        return "m64", 1
    if above(g32):
        return "m32", 2
    if above(g64) and not below(d):
        return "m64", 3
    return "frozen", 4


WHY = {1: "m64 gains on the frozen kx3 and plays detectably better than m32",
       2: "m32 gains on the frozen kx3 and m64 is not detectably better than m32, so the cheaper setting is picked on cost alone, "
          "not because the two were shown equal",
       3: "m64 is the only setting with a gain shown on the frozen kx3; it is NOT shown better than m32 (m64 - m32 interval {d})",
       4: "neither setting shows a gain on the frozen kx3 on the held-out decks, so the frozen kx3 stays the deck tester as well as the "
          "screener, and the gain seen on the development decks is not confirmed here"}


def report(arms):
    keys = sorted(set.intersection(*(set(a) for a in arms.values())))
    if len(keys) != 528:
        fail(f"{len(keys)} pairs common to every arm, not 528")
    for name, a in arms.items():
        if any(a[k]["seed"] != arms["frozen"][k]["seed"] for k in keys):
            fail(f"{name}: a seed differs from the frozen kx3's on the same pair")
    L = [f"Pairs: {len(keys)} (11 held-out decks x 8 opponents x 3 deals x 2 seats); seeds identical across all arms on every pair.", ""]
    L.append("WIN RATE (score per 100 games) per arm: " + ", ".join(f"{a} {100 * st.mean(score(arms[a][k]) for k in keys):.1f}" for a in arms))
    L.append("")

    def diffs(a, b, ks):
        return [score(arms[a][k]) - score(arms[b][k]) for k in ks]

    def row(label, a, b, ks):
        x = diffs(a, b, ks)
        c = ci(x)
        return c, (f"{label}: {c[0]:+.1f} +- {c[1]:.1f} (n {len(ks)}; interval {bounds(c)}; "
                   f"{sum(v > 0 for v in x)} games better, {sum(v < 0 for v in x)} worse)")

    def comp(a, b, label):
        c, line = row("pooled", a, b, keys)
        L.append(f"== {label}")
        L.append("  " + line)
        for grp in GROUPS:
            L.append("  " + row(f"group {grp}", a, b, [k for k in keys if GROUP[k[0]] == grp])[1])
        for dk in DECKS:
            L.append("  " + row(f"deck {dk} ({GROUP[dk]})", a, b, [k for k in keys if k[0] == dk])[1])
        return c

    g32 = comp("m32", "frozen", "PRIMARY m32 - frozen kx3")
    g64 = comp("m64", "frozen", "PRIMARY m64 - frozen kx3")
    d = comp("m64", "m32", "PRIMARY m64 - m32 (the direct comparison)")
    if abs(g64[0] - g32[0] - d[0]) > 1e-9:   # the same pairs: m64 - frozen = (m32 - frozen) + (m64 - m32) exactly
        fail("the three PRIMARY comparisons are not on the same pairs")
    for s in ("m32", "m64", "frozen"):
        comp(s, "km3", f"{s} - km3 (the frozen kx3's Oct 5 figure was +21.3 +- 4.0)")
    L.append("")
    L.append("PACE (mean over the 528 games): turns per game; the deck's first-attack own turn (games with an attack)")
    for a in arms:
        fa = [x for x in (first_attack_own_turn(arms[a][k]) for k in keys) if x is not None]
        L.append(f"  {a}: turns {st.mean(arms[a][k]['turns'] for k in keys):.2f}, first attack own turn {st.mean(fa):.2f} ({len(fa)} games)")
    L.append("")
    L.append("TIME per game (wall_s): m32 and m64 in 4-core Managed Agents sandboxes at --threads 2 (measured); the frozen kx3 and km3 on the "
             "laptop on Oct 5, so any ratio against them is an estimate")
    for a in arms:
        w = [arms[a][k]["wall_s"] for k in keys]
        L.append(f"  {a}: mean {st.mean(w):.0f} s, median {st.median(w):.0f} s")
    ratio = st.mean(arms["m64"][k]["wall_s"] for k in keys) / st.mean(arms["m32"][k]["wall_s"] for k in keys)
    L.append(f"  m64 / m32 on the same pairs, both in sandboxes but each deck's on different workers (worker speed varies about +-15%): {ratio:.2f}")
    for dk in DECKS:
        ks = [k for k in keys if k[0] == dk]
        L.append(f"  deck {dk}: " + ", ".join(f"{a} {st.mean(arms[a][k]['wall_s'] for k in ks):.0f}" for a in ("m32", "m64", "frozen")))
    L.append("")
    L.append("LIMITS")
    for s, c in (("m32", g32), ("m64", g64)):
        L.append(f"  {s} - frozen {c[0]:+.1f} +- {c[1]:.1f}: " + ("a gain shown." if above(c) else
                 f"a loss shown: it plays worse than the frozen kx3 on these decks ({bounds(c)})." if below(c) else
                 f"no gain shown; its gain on these decks could be anywhere from {c[0] - c[1]:+.1f} to {c[0] + c[1]:+.1f}, including zero."))
    if d[0] - d[1] < 0 < d[0] + d[1]:
        L.append(f"  m64 - m32 {d[0]:+.1f} +- {d[1]:.1f}: on these decks m64 is somewhere between {d[1] - d[0]:.1f} points worse and "
                 f"{d[0] + d[1]:.1f} points better than m32 per 100 games; this exam can't tell them apart within that range.")
    else:
        L.append(f"  m64 - m32 {d[0]:+.1f} +- {d[1]:.1f} (interval {bounds(d)}).")
    sd = d[1] / 1.96 * math.sqrt(len(keys)) / 100
    need = math.ceil((1.96 * sd / 0.02) ** 2) if sd > 0 else 0
    per = math.ceil(need / 176)   # 88 matchups x 2 seats per deal
    L.append(f"  narrowing m64 - m32 to +-2 points would take about {need} pairs at this spread: about {per} deals per matchup in all "
             f"(both seats), {max(per - 3, 0)} more than this exam's 3.")
    L.append("  chance: if neither setting truly beats the frozen kx3, this rule recommends one at most about 5% of the time (two one-sided "
             "2.5% checks); if m32 and m64 truly play alike, it picks m64 about 1 time in 10 (simulated on the development games: 11%), "
             "mostly through step 3.")
    L.append("")
    p, step = pick(g32, g64, d)
    L.append(f"PICK (fixed in PLAN.md, step {step}): {p}: " + WHY[step].format(d=bounds(d, 2)) + ". "
             f"Intervals to two decimals: m32 - frozen {bounds(g32, 2)}; m64 - frozen {bounds(g64, 2)}; m64 - m32 {bounds(d, 2)}.")
    setup = [k for k in keys if GROUP[k[0]] == "setup"]
    rows = {lab: ci(diffs(a, b, setup)) for lab, a, b in (("m32 - frozen", "m32", "frozen"), ("m64 - frozen", "m64", "frozen"),
                                                         ("m64 - m32", "m64", "m32"))}
    line = "SETUP GROUP (stated with the pick; 192 pairs): " + "; ".join(f"{lab} {c[0]:+.1f} +- {c[1]:.1f}" for lab, c in rows.items()) + "."
    if p in ("m32", "m64"):
        c = rows[f"{p} - frozen"]
        line += (f" The picked setting shows a gain on the setup decks." if above(c) else
                 f" The picked setting ({p}) shows no gain on the setup decks, so the planning weakness there is not shown fixed.")
    L.append(line)
    return "\n".join(L), p


def selftest():
    # each case keeps m64 - frozen = (m32 - frozen) + (m64 - m32), as the same pairs force
    cases = [((4, 3), (7, 3.2), (3, 2.9), "m64", 1), ((4, 3), (6, 3.2), (2, 2.9), "m32", 2), ((4, 3), (3, 3.2), (-1, 2.9), "m32", 2),
             ((1, 3), (5, 3.2), (4, 2.9), "m64", 1), ((2, 3), (4, 3.2), (2, 2.9), "m64", 3), ((1, 3), (2, 3.2), (1, 2.9), "frozen", 4),
             ((-5, 3), (-4, 3.2), (1, 2.9), "frozen", 4), ((4, 3), (0, 3.2), (-4, 2.9), "m32", 2)]
    for g32, g64, d, want, wstep in cases:
        assert abs(g64[0] - g32[0] - d[0]) < 1e-9
        got = pick(g32, g64, d)
        assert got == (want, wstep), (g32, g64, d, got, want, wstep)
    print(f"pick: {len(cases)} of {len(cases)} fixed cases as PLAN.md says")
    kx3, km3 = load(EXAM, "X"), load(EXAM, "ref")
    setup_mix = {k: (km3[k] if GROUP[k[0]] == "setup" else kx3[k]) for k in kx3}
    stand = [("A (m32 = the frozen kx3's games, m64 = km3's)", {"m32": kx3, "m64": km3, "frozen": kx3, "km3": km3}, "frozen", True),
             ("B (frozen = km3's games, m64 = kx3's, m32 = kx3's except km3's on the setup decks)",
              {"m32": setup_mix, "m64": kx3, "frozen": km3, "km3": km3}, "m64", False),
             ("C (frozen = km3's games, m32 = m64 = kx3's)", {"m32": kx3, "m64": kx3, "frozen": km3, "km3": km3}, "m32", False)]
    print("STAND-INS ONLY: they exercise the code and say nothing about the exam")
    for label, arms, want, full in stand:
        text, p = report(arms)
        assert p == want, (label, p, want)
        print(f"\n--- stand-in {label}: pick {p}, as expected")
        print(text if full else "\n".join(text.splitlines()[-12:]))


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
        sys.exit(0)
    arms = {"frozen": load(EXAM, "X"), "km3": load(EXAM, "ref")}
    sys.path.insert(0, "rl/strength")
    from split_collect import content
    for s in ("m32", "m64"):
        path = f"{E}/reg_{s}/games.jsonl"
        arms[s] = load(path, "X")
        if len(arms[s]) != 528 or any(g["pilot_deck"] != PILOT[s] for g in arms[s].values()):
            fail(f"{path}: not 528 kx3 games all played by {PILOT[s]}")
        ref = load(path, "ref")   # the build check again: every km3 game equals the Oct 5 exam's, or the pairing is void
        bad = [k for k in arms["km3"] if k not in ref or content(ref[k]) != content(arms["km3"][k])]
        if bad or len(ref) != 528:
            fail(f"{path}: {len(ref)} km3 games, {len(bad)} differ from the Oct 5 exam's or are missing, e.g. {bad[:3]}")
    print(report({a: arms[a] for a in ("m32", "m64", "frozen", "km3")})[0])
