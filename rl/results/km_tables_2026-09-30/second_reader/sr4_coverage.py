"""Items 5 and 7, and the coverage half of item 8. Written from block item 7 and step 5 (Dustin's condition: a
pairing's mixed rows are skipped only when every corresponding deal of km3's both-sides games and kta3's matches on
the complete move fingerprint, both decks, the seed and the seats; winners never used), Amendment 1 (b) item 2
(kta3's references), step 5's rows and tests (whole 95% interval below zero is harm; B2e's held-out accuracy veto:
more than 2 points further from Limitless than under kta3, counting only through mixed rows), step 5b item 4 (the
held-out direction) and step 5's reach (a row is reached when either list carries Training Area B2 153 or Arena of
Antiquity B3 154; each has one printing, lib/card.py).
Condition, per pairing: every deal i < 500 present on both sides and equal on moves, a, b, a_file, b_file, seed,
first_seat. A skipped pairing's mixed rows are kta3's games (own side exactly 0).
Writes OUT/sr4_coverage.txt."""
import sys, re, csv
sys.path.insert(0, "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/km_tables_2026-09-30/second_reader")
from sr_lib import *

lines = []
p = lines.append

# ---------- coverage_skip.txt's named skips and runs (per line and summary lists)
named, cur = {}, None
for ln in open(K + "/coverage_skip.txt", encoding="utf-8"):
    m = re.match(r"COVERAGE SHORTCUT, (\S+)", ln)
    if m:
        cur = m.group(1)
        named[cur] = {"skip_lines": set(), "run_lines": set(), "skip_list": None, "run_list": None}
        continue
    m = re.match(r"(SKIP|RUN) (\S+) (\d+):", ln)
    if m:
        assert m.group(2) == cur, (m.group(2), cur)
        named[cur]["skip_lines" if m.group(1) == "SKIP" else "run_lines"].add(int(m.group(3)))
        continue
    m = re.match(r"Skipped pairings \((\d+)\): (.*)", ln)
    if m:
        s = m.group(2).strip()
        named[cur]["skip_list"] = set() if s == "none" else {int(x) for x in s.split(",")}
        assert len(named[cur]["skip_list"]) == int(m.group(1))
        continue
    m = re.match(r"Pairings whose mixed rows run \((\d+)\): (.*)", ln)
    if m:
        s = m.group(2).strip()
        named[cur]["run_list"] = set() if s == "none" else {int(x) for x in s.split(",")}
        assert len(named[cur]["run_list"]) == int(m.group(1))

VARS = ["v-lucario_2", "v-suicune_2", "v-weezing_2", "l-charizardy"]
GROUPS = {"table": (KT + "/ec7e1a8_kta3_table.jsonl", B + "km3_table.jsonl"),
          "new17": (KT + "/ec7e1a8_kta3_new17.jsonl", B + "km3_new17.jsonl"),
          "b2e": (KT + "/ec7e1a8_b2e_kta3.jsonl", B + "b2e_km3.jsonl"),
          "scizor": (KT + "/ec7e1a8_scizor_kta3.jsonl", B + "scizor_km3.jsonl")}
for v in VARS:
    GROUPS["var_" + v] = (KT + f"/ec7e1a8_var_{v}_kta3.jsonl", B + f"var_{v}_km3.jsonl")


def deck_path(r, side):
    f = r.get(side + "_file")
    return f if f else f"decks/research/{r[side]}.txt"


_carry = {}
def carries(path):
    if path not in _carry:
        txt = open(REPO + "/" + path.lstrip("./").replace("../", ""), encoding="utf-8").read()
        _carry[path] = bool(re.search(r"\bB2 153\b|\bB3 154\b", txt))
    return _carry[path]


G, mine_skip, changed_pairings, reach = {}, {}, {}, {}
p("COVERAGE SHORTCUT re-verified deal by deal (moves, a, b, a_file, b_file, seed, first_seat; winners not used), km3 v kta3's references")
for g, (fo, fn) in GROUPS.items():
    O = by_key(rd(fo), pairing)
    N = by_key(rd(fn), pairing)
    assert set(O) == set(N), g
    G[g] = (O, N)
    skip, run = set(), set()
    nd = 0
    changed_pairings[g] = {}
    reach[g] = set()
    for pr in sorted(O):
        assert set(O[pr]) == set(N[pr]) == set(range(500)), (g, pr, len(O[pr]), len(N[pr]))
        assert all((O[pr][i]["bot_a"], O[pr][i]["bot_b"]) == ("kta3", "kta3") and (N[pr][i]["bot_a"], N[pr][i]["bot_b"]) == ("km3", "km3") for i in range(500)), (g, pr)
        bad = [i for i in range(500) if any(O[pr][i].get(f) != N[pr][i].get(f) for f in COV_FIELDS)]
        # nothing but moves may differ (same deal, decks, seats)
        assert all(O[pr][i].get(f) == N[pr][i].get(f) for i in range(500) for f in COV_FIELDS if f != "moves"), (g, pr)
        (run if bad else skip).add(pr)
        nd += len(bad)
        if bad:
            changed_pairings[g][pr] = bad
        r0 = O[pr][0]
        if carries(deck_path(r0, "a")) or carries(deck_path(r0, "b")):
            reach[g].add(pr)
    mine_skip[g] = skip
    nm = named.get(g)
    agree = nm is not None and nm["skip_list"] == nm["skip_lines"] == skip and nm["run_list"] == nm["run_lines"] == run
    p(f"  {g:>18}: {len(O)} pairings; {nd} both-sides games differ; mine skip {len(skip)} / run {len(run)} {sorted(run)};"
      f" coverage_skip.txt names the same skips and runs (per line and summary): {agree}")
    if not agree and nm is not None:
        p(f"      theirs skip {sorted(nm['skip_list'])} run {sorted(nm['run_list'])}")
    # the condition is exact: every skipped pairing has every one of its 500 deals equal on all seven fields
    assert all(all(O[pr][i].get(f) == N[pr][i].get(f) for f in COV_FIELDS) for pr in skip for i in range(500))
p(f"  skipped pairings verified: {sum(len(s) for s in mine_skip.values())}, each on all 500 deals and all seven fields (every skip checked)")

# ---------- integrity (coverage): every changed pairing is one a Stadium list reaches
viol = {g: sorted(set(changed_pairings[g]) - reach[g]) for g in GROUPS}
p(f"INTEGRITY (coverage): pairings reached (either list carries B2 153 or B3 154): "
  + "; ".join(f"{g} {len(reach[g])}" for g in GROUPS))
p(f"  changed pairings outside the reach: {viol}; clean: {not any(viol.values())}")
p(f"  reached pairings with no changed game (reported): " + "; ".join(f"{g} {sorted(reach[g] - set(changed_pairings[g]))}" for g in GROUPS if reach[g] - set(changed_pairings[g])))

# ---------- the own-side mixed rows as run
MIX = {"b2e": [(B + "mixed_b2e_km3_first.jsonl", "a")],
       "scizor": [(B + "mixed_scizor_km3_first.jsonl", "a")],
       "var_v-lucario_2": [(B + "var_v-lucario_2_km3_mixed_a.jsonl", "a"), (B + "var_v-lucario_2_km3_mixed_b.jsonl", "b")],
       "var_v-suicune_2": [(B + "var_v-suicune_2_km3_mixed_b.jsonl", "b")],
       "var_v-weezing_2": [(B + "var_v-weezing_2_km3_mixed_b.jsonl", "b")],
       "var_l-charizardy": [(B + "var_l-charizardy_km3_mixed_a.jsonl", "a")]}
SIDE = {"b2e": {pr: "a" for pr in range(96)}, "scizor": {pr: "a" for pr in range(8)}}
for v in VARS:
    SIDE["var_" + v] = {int(r["pairing"]): r["variant_side"] for r in tsv(R + f"/gauntlet_runs_2026-09-26/tsv/var_{v}.tsv")}
    for pr, s in SIDE["var_" + v].items():
        assert G["var_" + v][0][pr][0][s] == v, (v, pr, s)
M = {}
for g, parts in MIX.items():
    M[g] = {}
    O = G[g][0]
    for f, side in parts:
        c = by_key(rd(f), pairing)
        bots = ("km3", "kta3") if side == "a" else ("kta3", "km3")
        for pr, cc in c.items():
            assert pr not in M[g] and SIDE[g][pr] == side, (g, pr)
            assert set(cc) == set(range(500)), (g, pr)
            for i in range(500):
                assert (cc[i]["bot_a"], cc[i]["bot_b"]) == bots, (g, pr, i)
                for fld in ("seed", "first_seat", "a_file", "b_file", "a", "b"):
                    assert cc[i].get(fld) == O[pr][i].get(fld), (g, pr, i, fld)
            M[g][pr] = cc
    must = set(G[g][0]) - mine_skip[g]
    p(f"  mixed rows {g}: pairings {sorted(M[g])}; exactly the pairings that must run: {set(M[g]) == must}; km3 on the own (held/variant) side: True")
    mix_out = sum(1 for pr in M[g] for i in range(500) if M[g][pr][i]["moves"] != O[pr][i]["moves"] and i not in changed_pairings[g].get(pr, []))
    p(f"     mixed games differing from kta3's on deals where the both-sides games did not differ: {mix_out} (reported)")


def own_rows(g, prs):
    out, nchg = [], 0
    O = G[g][0]
    for pr in prs:
        sign = +1 if SIDE[g][pr] == "a" else -1
        if pr in mine_skip[g]:
            out.append([0.0] * 500)
        else:
            out.append(paired(O[pr], M[g][pr], sign))
            nchg += sum(1 for i in range(500) if M[g][pr][i]["moves"] != O[pr][i]["moves"])
    return out, nchg


def sim_avg(g, prs, which):
    D = G[g][which]
    v = []
    for pr in prs:
        s = sum(sc(r) for r in D[pr].values()) / 500
        v.append(s if SIDE[g][pr] == "a" else 1 - s)
    return 100 * sum(v) / len(v)


LC = [r for r in csv.DictReader(open(R + "/b2e_card_check_2026-09-26/limitless_cells.csv", encoding="utf-8", newline="")) if r["dataset"] == "pooled"]


def lim_fig(key):
    arch = {"manectric": "manectric_heliolisk", "raticate": "raticate_ninetales", "whimsicott": "whimsicott_ariados"}.get(key.replace("dustin_", ""), key.replace("dustin_", ""))
    rs = [r for r in LC if r["archetype"] == arch and r["opponent"] in NAMES]
    if len(rs) != 8:
        return None
    vals = [(int(r["W"]) + 0.5 * int(r["T"])) / (int(r["W"]) + int(r["L"]) + int(r["T"])) for r in rs]
    return 100 * sum(vals) / 8


held = {}
for r in tsv(R + "/b2e_card_check_2026-09-26/b2e_pairings.tsv"):
    held.setdefault((r["block"], r["held_key"]), []).append(int(r["pairing"]))
p("B2E (0-47 held-out count; 48-95 Dustin's, reported). Own side = km3 on the held deck (side a), kta3 on the panel list:")
harm_h, veto, hod = [], [], []
for (blk, key), prs in held.items():
    assert len(prs) == 8
    rows_, nchg = own_rows("b2e", prs)
    m, h, n = pool(rows_)
    so, sn = sim_avg("b2e", prs, 0), sim_avg("b2e", prs, 1)
    lf = lim_fig(key)
    ch = None if lf is None else abs(sn - lf) - abs(so - lf)
    harm = m + h < 0
    if blk == "A_archetype":
        if harm:
            harm_h.append(key)
        if harm and ch is not None and ch > 2:
            veto.append(key)
        hod.append((key, ch))
    p(f"  {blk:>11} {key:<24} own side {m:+.4f} +/- {h:.4f} over 8 rows ({nchg} own-side mixed games changed){' HARM' if harm else ''};"
      f" both sides kta3 {so:.2f} -> km3 {sn:.2f}; Limitless {'n/a' if lf is None else f'{lf:.2f}'}; change in miss {'n/a' if ch is None else f'{ch:+.3f}'}")
p(f"  B2e held-out own-side harm: {harm_h or 'none'}; held-out accuracy veto (> 2 further AND own side worse): {veto or 'none'};"
  f" largest held-out change in miss {max(c for _, c in hod):+.3f}")
closer = sum(1 for _, c in hod if c < 0)
further = sum(1 for _, c in hod if c > 0)
same = sum(1 for _, c in hod if c == 0)
p(f"HELD-OUT DIRECTION (six archetypes, gates nothing): {closer} closer, {further} further, {same} unchanged; mean change in miss {sum(c for _, c in hod) / 6:+.4f}"
  f" ({', '.join(f'{k} {c:+.3f}' for k, c in hod)})")

# Scizor
rows_, nchg = own_rows("scizor", range(8))
m, h, n = pool(rows_)
so, sn = sim_avg("scizor", range(8), 0), sim_avg("scizor", range(8), 1)
sciz_harm = m + h < 0
p(f"SCIZOR: own side {m:+.4f} +/- {h:.4f} ({m - h:+.4f} to {m + h:+.4f}) over 8 rows ({nchg} own-side mixed games changed; both-sides changed "
  f"{sum(len(v) for v in changed_pairings['scizor'].values())}){' HARM' if m + h < 0 else ' -> no harm'}; Scizor both sides kta3 {so:.2f} -> km3 {sn:.2f}")

p("SECOND LISTS (own side = km3 on the list, kta3 on the other deck):")
sl_harm = []
for v in VARS:
    g = "var_" + v
    prs = sorted(SIDE[g])
    assert set(prs) == set(G[g][0])
    rows_, nchg = own_rows(g, prs)
    m, h, n = pool(rows_)
    so, sn = sim_avg(g, prs, 0), sim_avg(g, prs, 1)
    if m + h < 0:
        sl_harm.append(v)
    p(f"  {v:<13} own side {m:+.4f} +/- {h:.4f} ({m - h:+.4f} to {m + h:+.4f}) over {len(prs)} rows ({nchg} changed; both-sides changed "
      f"{sum(len(x) for x in changed_pairings[g].values())} in {len(changed_pairings[g])} pairings){' HARM' if m + h < 0 else ' -> no harm'};"
      f" list average kta3 {so:.2f} -> km3 {sn:.2f}")
p(f"  second lists with own-side harm: {sl_harm or 'none'}")
p(f"COVERAGE (step 5): {'PASS' if not (harm_h or veto or sl_harm or sciz_harm) else 'FAIL'} (B2e held-out harm {harm_h or 'none'}, veto {veto or 'none'}; Scizor harm {sciz_harm}; second lists {sl_harm or 'none'})")
write("sr4_coverage.txt", lines)
