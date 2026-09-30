"""Item 1 (footprint and route), item 3 (clause (c)), the 45-cell half of item 8 (integrity), and the mixed-row
composites handed to score45 (item 2). Written from the registration: step 1 (footprint on `moves`, paired by
(a, b, i), under 15% = reserve route), Amendment 1 (b) item 2 (km3 against kta3's references), step 4 reserve (c)
(own side, pooled per deck over its cells, as score.py does), block item 7 / step 5 (a cell whose km3 games equal
kta3's on every deal has mixed rows equal to kta3's: zero-footprint cells' mixed rows read as kta3's games).
Writes OUT/sr1_cells.txt and SCR/sr_mixed_{first,second}.jsonl."""
import sys, json, re
sys.path.insert(0, "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/km_tables_2026-09-30/second_reader")
from sr_lib import *

lines = []
p = lines.append

O = by_key(rd(KT + "/ec7e1a8_kta3_table.jsonl") + rd(KT + "/ec7e1a8_kta3_new17.jsonl"), ab)
N = by_key(rd(B + "km3_table.jsonl") + rd(B + "km3_new17.jsonl"), ab)
assert set(O) == set(N) == set(CELLS45), set(O) ^ set(CELLS45)

# ---------- pairing checks (bots, seed formula, seats, files) and the footprint
diff, dec_diff, res_changed = {}, 0, 0
for k in CELLS45:
    assert set(O[k]) == set(N[k]) == set(range(500)), k
    src, base = ("table", TABLE_BASE) if k in TABLE28 else ("new", NEW_BASE)
    pr = TABLE28.index(k) if src == "table" else NEW_PAIRING[k]
    for i in range(500):
        o, n = O[k][i], N[k][i]
        assert (o["bot_a"], o["bot_b"]) == ("kta3", "kta3") and (n["bot_a"], n["bot_b"]) == ("km3", "km3"), (k, i)
        for f in ("seed", "first_seat", "pairing", "a_file", "b_file"):
            assert o.get(f) == n.get(f), (k, i, f)
        assert o["pairing"] == pr and o["seed"] == base + pr * 10000 + i, (k, i, o["seed"])
        assert o["first_seat"] == i % 2, (k, i)
    diff[k] = [i for i in range(500) if O[k][i]["moves"] != N[k][i]["moves"]]
    dec_diff += sum(1 for i in range(500) if O[k][i]["decisions"] != N[k][i]["decisions"])
    res_changed += sum(1 for i in diff[k] if sc(O[k][i]) != sc(N[k][i]))
tot = sum(len(v) for v in diff.values())
reserve = 100 * tot < 15 * 22500          # integers: the 15% trigger, exact
p(f"FOOTPRINT km3 v kta3's references, 45 cells, paired by (a, b, i); bots, seeds (base + pairing x 10,000 + i), seats (i % 2) and files checked: "
  f"{tot} of 22500 = {100 * tot / 22500:.6f}%")
p(f"  ROUTE from the integers: 100 x {tot} = {100 * tot} {'<' if reserve else '>='} 15 x 22500 = {15 * 22500} -> {'RESERVE route (under 15%)' if reserve else 'ORDINARY rule (15% or more)'}")
p(f"  games whose result (first_deck_score) changed among them: {res_changed}; games whose decisions fingerprint differs: {dec_diff} (reported)")
changed = [k for k in CELLS45 if diff[k]]
p(f"  cells with a changed game: {len(changed)} of 45")
for k in changed:
    p(f"    {k[0]} v {k[1]}: {len(diff[k])}")
# compare with footprint.txt's by-cell list
ft = open(K + "/footprint.txt", encoding="utf-8").read()
m = re.search(r"by cell \(games differing of 500\): (.*)", ft)
theirs = {tuple(x.rsplit(" ", 1)[0].split(" v ")): int(x.rsplit(" ", 1)[1]) for x in m.group(1).strip().split(", ")}
mine = {k: len(diff[k]) for k in changed}
m2 = re.search(r"FOOTPRINT: (\d+) of (\d+)", ft)
p(f"  footprint.txt: {m2.group(1)} of {m2.group(2)}; by-cell counts equal to mine: {theirs == mine}")
# ---------- integrity: every changed game lies in the 17 cells holding a panel Altaria or Lucario list
outside = [k for k in changed if k not in NAMED17]
p(f"INTEGRITY (45 cells): cells holding a panel Altaria or Lucario list: {len(NAMED17)}; changed cells outside them: {outside or 'none'};"
  f" changed cells == the 17 named cells: {set(changed) == set(NAMED17)}")

# ---------- the mixed rows as run
MF = by_key(rd(B + "mixed_table_km3_first.jsonl") + rd(B + "mixed_new17_km3_first.jsonl"), ab)
MS = by_key(rd(B + "mixed_table_km3_second.jsonl") + rd(B + "mixed_new17_km3_second.jsonl"), ab)
p(f"MIXED ROWS as run: first {len(MF)} cells, second {len(MS)} cells; both equal to the changed cells: {set(MF) == set(MS) == set(changed)}")
for k in MF:
    assert set(MF[k]) == set(MS[k]) == set(range(500)), k
    for i in range(500):
        assert (MF[k][i]["bot_a"], MF[k][i]["bot_b"]) == ("km3", "kta3"), (k, i)
        assert (MS[k][i]["bot_a"], MS[k][i]["bot_b"]) == ("kta3", "km3"), (k, i)
        for f in ("seed", "first_seat", "pairing", "a_file", "b_file"):
            assert MF[k][i].get(f) == O[k][i].get(f) == MS[k][i].get(f), (k, i, f)
mf_d = sum(1 for k in MF for i in range(500) if MF[k][i]["moves"] != O[k][i]["moves"])
ms_d = sum(1 for k in MS for i in range(500) if MS[k][i]["moves"] != O[k][i]["moves"])
out_f = sum(1 for k in MF for i in range(500) if MF[k][i]["moves"] != O[k][i]["moves"] and i not in diff[k])
out_s = sum(1 for k in MS for i in range(500) if MS[k][i]["moves"] != O[k][i]["moves"] and i not in diff[k])
p(f"  mixed-row games whose moves differ from kta3's: first {mf_d}, second {ms_d}, total {mf_d + ms_d};"
  f" of them on deals where the both-sides games did not differ: {out_f} and {out_s} (reported: one side changed can differ where both did not)")

# ---------- composites for score45: the runner's mixed games where run; kta3's reference games relabelled elsewhere
def relabel(r, bots):
    x = dict(r)
    x["bot_a"], x["bot_b"] = bots
    return x

for name, M, bots in (("first", MF, ("km3", "kta3")), ("second", MS, ("kta3", "km3"))):
    n = 0
    with open(f"{SCR}/sr_mixed_{name}.jsonl", "w", encoding="utf-8") as f:
        for k in CELLS45:
            for i in range(500):
                r = M[k][i] if k in M else relabel(O[k][i], bots)
                f.write(json.dumps(r, sort_keys=True) + "\n")
                n += 1
    p(f"composite {name}: {n} games ({sum(1 for k in CELLS45 if k in M)} cells run, {sum(1 for k in CELLS45 if k not in M)} cells as kta3's games relabelled {bots[0]}/{bots[1]})")

# compare with the first reader's composites, record by record (after mine are built)
for name in ("first", "second"):
    theirs = by_key(rd(f"{K}/score45_inputs/1f6319e_km3_mixed_{name}_composite.jsonl"), ab)
    mine_c = by_key(rd(f"{SCR}/sr_mixed_{name}.jsonl"), ab)
    kept = set(theirs[CELLS45[0]][0]) - {"mixed_source"}
    nd = sum(1 for k in CELLS45 for i in range(500) if any(theirs[k][i].get(f) != mine_c[k][i].get(f) for f in kept))
    p(f"  first reader's {name} composite: {sum(len(c) for c in theirs.values())} games; fields {sorted(kept)}; records unequal to mine: {nd}")

# ---------- clause (c): per meta deck, own side, pooled over its cells with a changed game, both directions
p("CLAUSE (c): own side (km3 on that deck only, kta3 on the other, v kta3 on both), pooled per deck over its cells with a changed game")
own = {}
for k in changed:
    own[(k, k[0])] = (paired(O[k], MF[k], +1), sum(1 for i in range(500) if MF[k][i]["moves"] != O[k][i]["moves"]))
    own[(k, k[1])] = (paired(O[k], MS[k], -1), sum(1 for i in range(500) if MS[k][i]["moves"] != O[k][i]["moves"]))
worse = []
for d in DECKS10:
    parts = [(v, c) for (k, dd), (v, c) in own.items() if dd == d]
    if not parts:
        p(f"  {d:>17}: no cell with a changed game")
        continue
    mm, h, n = pool([v for v, _ in parts])
    ch = sum(c for _, c in parts)
    w = mm + h < 0
    if w:
        worse.append(d)
    p(f"  {d:>17}: {mm:+.4f} +/- {h:.4f} ({mm - h:+.4f} to {mm + h:+.4f}) over {len(parts)} cells, {n} deals, {ch} mixed games changed{'  WORSE' if w else ''}")
p(f"  (c) decks worse beyond paired noise: {worse or 'none'} -> {'FAIL' if worse else 'PASS'}")
p("  per cell side (reported):")
for (k, d), (v, c) in own.items():
    mm, h, _ = pool([v])
    p(f"    {k[0]} v {k[1]}, {d}'s side: {mm:+.2f} +/- {h:.2f} ({c} changed)")

write("sr1_cells.txt", lines)
