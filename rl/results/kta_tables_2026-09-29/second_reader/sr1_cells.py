"""Step 1: the footprint (5.1), the route, the integrity line on the 45 cells, clause (c) (5.2 (c)), and the mixed-row
composites handed to score45 (a zero-footprint cell's mixed rows are kog3's games: 5.5 last bullet / 5.2 (c)).
Writes: OUT/sr1_cells.txt and SCR/sr_mixed_first.jsonl, SCR/sr_mixed_second.jsonl."""
import sys, json
sys.path.insert(0, "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kta_tables_2026-09-29/second_reader")
from sr_lib import *

lines = []
p = lines.append

O = by_key(rd(F + "kog3_table.jsonl") + rd(F + "kog3_new17.jsonl"), ab)
N = by_key(rd(F + "kta3_table.jsonl") + rd(F + "kta3_new17.jsonl"), ab)
assert set(O) == set(N) == set(CELLS45), (set(O) ^ set(CELLS45))

# ---- pairing checks and the footprint
diff = {}
res_changed = 0
for k in CELLS45:
    assert set(O[k]) == set(N[k]) == set(range(500)), k
    for i in range(500):
        o, n = O[k][i], N[k][i]
        assert (o["bot_a"], o["bot_b"]) == ("kog3", "kog3") and (n["bot_a"], n["bot_b"]) == ("kta3", "kta3")
        for f in ("seed", "first_seat", "a_file", "b_file", "pairing"):
            assert o[f] == n[f], (k, i, f)
        assert o["first_seat"] == i % 2, (k, i)  # even i puts the first-named deck in seat 0 (3.2)
    diff[k] = [i for i in range(500) if O[k][i]["moves"] != N[k][i]["moves"]]
    res_changed += sum(1 for i in diff[k] if sc(O[k][i]) != sc(N[k][i]))
# seeds: 23,000,000,000 + pairing x 10,000 + i (table), 23,001,000,000 + pairing x 10,000 + i (new cells 8-24)
for k in CELLS45:
    base = 23000000000 if k in TABLE28 else 23001000000
    for i in range(500):
        r = O[k][i]
        assert r["seed"] == base + r["pairing"] * 10000 + i, (k, i, r["seed"])
tot = sum(len(v) for v in diff.values())
changed_cells = [k for k in CELLS45 if diff[k]]
route = "reserve (5.2)" if 100 * tot < 15 * 22500 else "ordinary rule (5.3)"
p(f"FOOTPRINT kta3 v kog3, 45 cells, paired by (a, b, i), seeds and seats checked equal: {tot} of 22500 = {100*tot/22500:.4f}% -> {route}")
p(f"  games among those whose result (first_deck_score) changed: {res_changed}")
p(f"  cells with a changed game: {len(changed_cells)} of 45")
for k in changed_cells:
    p(f"    {k[0]} v {k[1]}: {len(diff[k])}")
bad = [k for k in changed_cells if not (set(k) & REACH_DECKS)]
reach = [k for k in CELLS45 if set(k) & REACH_DECKS]
p(f"  INTEGRITY (section 4 line): cells a switch-1 list reaches: {len(reach)}; changed cells outside them: {bad or 'none'}")
p(f"  changed cells == reach cells: {set(changed_cells) == set(reach)}")

# ---- mixed rows as run
MF = by_key(rd(F + "mixed_table_kta3_first.jsonl") + rd(F + "mixed_new17_kta3_first.jsonl"), ab)
MS = by_key(rd(F + "mixed_table_kta3_second.jsonl") + rd(F + "mixed_new17_kta3_second.jsonl"), ab)
SF = by_key(rd(F + "mixed_table_kta3_first_s40.jsonl") + rd(F + "mixed_new17_kta3_first_s40.jsonl"), ab)
SS = by_key(rd(F + "mixed_table_kta3_second_s40.jsonl") + rd(F + "mixed_new17_kta3_second_s40.jsonl"), ab)
p(f"MIXED ROWS run at 500 deals: first {len(MF)} cells, second {len(MS)} cells; equal to the changed cells: {set(MF) == set(MS) == set(changed_cells)}")
p(f"i<40 samples: first {len(SF)} cells, second {len(SS)} cells; equal to the zero-footprint cells: {set(SF) == set(SS) == (set(CELLS45) - set(changed_cells))}")
for k in MF:
    assert set(MF[k]) == set(MS[k]) == set(range(500)), k
    for i in range(500):
        assert (MF[k][i]["bot_a"], MF[k][i]["bot_b"]) == ("kta3", "kog3") and (MS[k][i]["bot_a"], MS[k][i]["bot_b"]) == ("kog3", "kta3")
        for f in ("seed", "first_seat", "a_file", "b_file"):
            assert MF[k][i][f] == O[k][i][f] == MS[k][i][f], (k, i, f)
s40_diff = 0
s40_n = 0
for M, bots in ((SF, ("kta3", "kog3")), (SS, ("kog3", "kta3"))):
    for k in M:
        assert set(M[k]) == set(range(40)), (k, sorted(M[k])[:3])
        for i in range(40):
            r = M[k][i]
            assert (r["bot_a"], r["bot_b"]) == bots
            for f in ("seed", "first_seat", "a_file", "b_file"):
                assert r[f] == O[k][i][f]
            s40_n += 1
            if r["moves"] != O[k][i]["moves"] or sc(r) != sc(O[k][i]):
                s40_diff += 1
p(f"INTEGRITY (N5/K5): i<40 sample games in zero-footprint cells that differ from kog3's (moves or score): {s40_diff} of {s40_n}")
mf_diff = sum(1 for k in MF for i in range(500) if MF[k][i]["moves"] != O[k][i]["moves"])
ms_diff = sum(1 for k in MS for i in range(500) if MS[k][i]["moves"] != O[k][i]["moves"])
# mixed-row differences outside the deals where both-sides differ (informative only)
out_f = sum(1 for k in MF for i in range(500) if MF[k][i]["moves"] != O[k][i]["moves"] and i not in diff[k])
out_s = sum(1 for k in MS for i in range(500) if MS[k][i]["moves"] != O[k][i]["moves"] and i not in diff[k])
p(f"mixed-row games that differ from kog3's (moves): first {mf_diff}, second {ms_diff}, total {mf_diff + ms_diff} (of them on deals where the both-sides games did not differ: {out_f} and {out_s})")

# ---- composites for score45 (my own build): the runner's mixed games where run; kog3's games relabelled elsewhere
def relabel(r, bots):
    x = dict(r)
    x["bot_a"], x["bot_b"] = bots
    return x

for name, M, bots in (("first", MF, ("kta3", "kog3")), ("second", MS, ("kog3", "kta3"))):
    n = 0
    with open(f"{SCR}/sr_mixed_{name}.jsonl", "w", encoding="utf-8") as f:
        for k in CELLS45:
            for i in range(500):
                r = M[k][i] if k in M else relabel(O[k][i], bots)
                f.write(json.dumps(r, sort_keys=True) + "\n")
                n += 1
    p(f"composite {name}: {n} games -> {SCR}/sr_mixed_{name}.jsonl")

# compare with the first reader's composites, record by record (after building mine)
for name, M, bots in (("first", MF, ("kta3", "kog3")), ("second", MS, ("kog3", "kta3"))):
    theirs = by_key(rd(f"{T}/score45_inputs/ec7e1a8_fresh_kta3_mixed_{name}_composite.jsonl"), ab)
    mine = by_key(rd(f"{SCR}/sr_mixed_{name}.jsonl"), ab)
    # theirs keep a subset of fields (the ones score45 reads, plus moves) and add 'mixed_source'; compare on theirs
    kept = set(theirs[CELLS45[0]][0]) - {"mixed_source"}
    ndiff = sum(1 for k in CELLS45 for i in range(500)
                if any(theirs[k][i].get(f) != mine[k][i].get(f) for f in kept))
    p(f"first reader's {name} composite: {sum(len(c) for c in theirs.values())} games, fields {sorted(kept)}; "
      f"records unequal to mine on those fields: {ndiff}")

# ---- clause (c): per meta deck, pooled over its cells with a changed game, both directions (own side)
p("CLAUSE (c): own side (kta3 on that deck only v kog3 on both), pooled over the deck's cells with a changed game")
c_fail = []
c_total_changed = 0
own = {}
for k in changed_cells:
    own[(k, k[0])] = (paired(O[k], MF[k], +1), sum(1 for i in range(500) if MF[k][i]["moves"] != O[k][i]["moves"]))
    own[(k, k[1])] = (paired(O[k], MS[k], -1), sum(1 for i in range(500) if MS[k][i]["moves"] != O[k][i]["moves"]))
for d in DECKS10:
    parts = [(v, c) for (k, dd), (v, c) in own.items() if dd == d]
    if not parts:
        p(f"  {d:>17}: no cell with a changed game")
        continue
    m, h, n = pool([v for v, _ in parts])
    ch = sum(c for _, c in parts)
    c_total_changed += ch
    worse = m + h < 0
    if worse:
        c_fail.append(d)
    p(f"  {d:>17}: own side {m:+.3f} +/- {h:.3f} over {len(parts)} cells ({n} deals; {ch} mixed-row games changed){'  WORSE' if worse else ''}")
p(f"  (c) decks worse: {c_fail or 'none'}; mixed-row games changed, both directions: {c_total_changed}")
p("  per cell side (reported):")
for (k, d), (v, c) in own.items():
    m, h, _ = pool([v])
    p(f"    {k[0]} v {k[1]}, {d}'s side: {m:+.2f} +/- {h:.2f} ({c} changed)")

open(OUT + "/sr1_cells.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines))
