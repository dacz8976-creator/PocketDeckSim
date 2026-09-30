"""Step 4: coverage (5.5), the shortcut's skips re-verified against Dustin's exact condition (top block item 3), the
own-side no-harm tests (B2e held-out, Scizor, the four second lists), the held-out direction (RUN5, Sept 29), and the
coverage half of the integrity line (section 2's reach lists).
Condition, per pairing: every deal i < 500 present on both sides, and equal on moves, a, b, a_file, b_file, seed,
first_seat. Winners are never read for it. A skipped pairing's mixed rows are kog3's games (own side exactly 0).
Writes OUT/sr4_coverage.txt."""
import sys, re, csv, math
sys.path.insert(0, "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kta_tables_2026-09-29/second_reader")
from sr_lib import *

lines = []
p = lines.append

# ---------- the first reader's (runner's) named skips, parsed from coverage_skip.txt
named = {}
cur = None
for ln in open(T + "/coverage_skip.txt", encoding="utf-8"):
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

GROUPS = {
    "table": (F + "kog3_table.jsonl", F + "kta3_table.jsonl"),
    "new17": (F + "kog3_new17.jsonl", F + "kta3_new17.jsonl"),
    "scizor": (F + "scizor_kog3.jsonl", F + "scizor_kta3.jsonl"),
    "b2e": (F + "b2e_kog3.jsonl", F + "b2e_kta3.jsonl"),
}
VARS = ["v-lucario_2", "v-suicune_2", "v-weezing_2", "l-charizardy"]
for v in VARS:
    GROUPS["var_" + v] = (F + f"var_{v}_kog3.jsonl", F + f"var_{v}_kta3.jsonl")

G = {}
mine_skip = {}
changed_pairings = {}
p("COVERAGE SHORTCUT, re-verified deal by deal (moves, a, b, a_file, b_file, seed, first_seat; winners not used)")
for g, (fo, fn) in GROUPS.items():
    O = by_key(rd(fo), pairing)
    N = by_key(rd(fn), pairing)
    assert set(O) == set(N), g
    G[g] = (O, N)
    skip, run = set(), set()
    ndiff_games = 0
    changed_pairings[g] = {}
    for pr in sorted(O):
        assert set(O[pr]) == set(N[pr]) == set(range(500)), (g, pr, len(O[pr]), len(N[pr]))
        assert all((O[pr][i]["bot_a"], O[pr][i]["bot_b"]) == ("kog3", "kog3") and (N[pr][i]["bot_a"], N[pr][i]["bot_b"]) == ("kta3", "kta3") for i in range(500))
        bad = [i for i in range(500) if any(O[pr][i][f] != N[pr][i][f] for f in COV_FIELDS)]
        # the fields other than moves must never differ (same deal, same decks, same seats)
        assert all(O[pr][i][f] == N[pr][i][f] for i in range(500) for f in COV_FIELDS if f != "moves"), (g, pr)
        (run if bad else skip).add(pr)
        ndiff_games += len(bad)
        if bad:
            changed_pairings[g][pr] = bad
    mine_skip[g] = skip
    nm = named.get(g)
    agree = nm is not None and nm["skip_list"] == nm["skip_lines"] == skip and nm["run_list"] == nm["run_lines"] == run
    p(f"  {g:>18}: {len(O)} pairings; {ndiff_games} both-sides games differ; mine skip {len(skip)} / run {len(run)} {sorted(run)};"
      f" coverage_skip.txt names the same skips and runs: {agree}")
    if not agree and nm is not None:
        p(f"      theirs skip {sorted(nm['skip_list'])} run {sorted(nm['run_list'])}")

# ---------- mixed rows as run: exactly the non-skipped pairings, 500 deals, the right side, the same deals
MIX = {
    "b2e": (F + "mixed_b2e_kta3_first.jsonl", "a"),
    "scizor": (F + "mixed_scizor_kta3_first.jsonl", "a"),
    "var_v-lucario_2": (F + "var_v-lucario_2_kta3_mixed_a.jsonl", "a"),
    "var_v-weezing_2": (F + "var_v-weezing_2_kta3_mixed_b.jsonl", "b"),
    "var_l-charizardy": (F + "var_l-charizardy_kta3_mixed_a.jsonl", "a"),
}
M = {}
for g, (f, side) in MIX.items():
    M[g] = by_key(rd(f), pairing)
    O = G[g][0]
    bots = ("kta3", "kog3") if side == "a" else ("kog3", "kta3")
    for pr, c in M[g].items():
        assert set(c) == set(range(500)), (g, pr)
        for i in range(500):
            assert (c[i]["bot_a"], c[i]["bot_b"]) == bots, (g, pr, i)
            for fld in ("seed", "first_seat", "a_file", "b_file", "a", "b"):
                assert c[i][fld] == O[pr][i][fld], (g, pr, i, fld)
    ok = set(M[g]) == (set(G[g][0]) - mine_skip[g]) if g != "scizor" else set(M[g]) == set(range(8))
    p(f"  mixed rows {g}: pairings {sorted(M[g])} (kta3 on side {side}); exactly the pairings that must run: {ok}")
p(f"  var_v-suicune_2: no pairing must run (mine: {sorted(set(G['var_v-suicune_2'][0]) - mine_skip['var_v-suicune_2'])}); no mixed file exists: consistent")
ms = by_key(rd(F + "mixed_scizor_kta3_second.jsonl"), pairing)

# ---------- integrity (section 2's coverage reach): Scizor rows 0-7; B2e pairings with pairing % 8 == 4 (v Suicune);
# second lists' rows v Suicune: v-lucario_2 19, v-weezing_2 26, l-charizardy 44; v-suicune_2 none.
REACH = {"scizor": set(range(8)), "b2e": {x for x in range(96) if x % 8 == 4},
         "var_v-lucario_2": {19}, "var_v-weezing_2": {26}, "var_l-charizardy": {44}, "var_v-suicune_2": set()}
viol = {g: sorted(set(changed_pairings[g]) - REACH[g]) for g in REACH}
p(f"INTEGRITY (coverage): changed pairings outside section 2's reach: {viol}; all clean: {not any(viol.values())}")
b2e_panel_check = all(G['b2e'][0][pr][0]['b'] == 'suicune' for pr in REACH['b2e'])
p(f"  (B2e pairings 4, 12, ..., 92 are the held decks v the panel's Suicune: {b2e_panel_check})")

# ---------- own-side tests
def own_rows(g, prs, side_of):
    """per pairing, the own side's per-deal change: the mixed row where run, 500 zeros (kog3's games) where skipped."""
    out = []
    nchg = 0
    O = G[g][0]
    for pr in prs:
        side = side_of(pr)
        sign = +1 if side == "a" else -1
        if pr in mine_skip[g]:
            out.append([0.0] * 500)
        else:
            out.append(paired(O[pr], M[g][pr], sign))
            nchg += sum(1 for i in range(500) if M[g][pr][i]["moves"] != O[pr][i]["moves"])
    return out, nchg


def sim_avg(g, prs, side_of, which):
    D = G[g][which]
    v = []
    for pr in prs:
        s = sum(sc(r) for r in D[pr].values()) / 500
        v.append(s if side_of(pr) == "a" else 1 - s)
    return 100 * sum(v) / len(v)

# Limitless pooled equal-weight figures for the held-out archetypes (b2e_card_check limitless_cells.csv, pooled rows)
LC = [r for r in csv.DictReader(open(R + "/b2e_card_check_2026-09-26/limitless_cells.csv", encoding="utf-8", newline="")) if r["dataset"] == "pooled"]
def lim_fig(key):
    arch = {"manectric": "manectric_heliolisk", "raticate": "raticate_ninetales", "whimsicott": "whimsicott_ariados"}.get(key.replace("dustin_", ""), key.replace("dustin_", ""))
    rs = [r for r in LC if r["archetype"] == arch and r["opponent"] in NAMES]  # the 8 panel cells, not the summary rows
    assert len(rs) == 8, (key, arch, len(rs))
    vals = []
    for r in rs:
        W, L_, Tt = int(r["W"]), int(r["L"]), int(r["T"])
        vals.append((W + 0.5 * Tt) / (W + L_ + Tt))
    return 100 * sum(vals) / 8, [float(r["score_pct"]) for r in rs]

pairs_b2e = tsv(T + "/pairs/fresh_b2e.tsv")
held = {}
for r in pairs_b2e:
    held.setdefault((r["block"], r["held_key"]), []).append(int(r["pairing"]))
p("B2e held-out (0-47 count; 48-95 Dustin's, reported). Own side = kta3 on the held deck (side a), kog3 on the panel:")
veto = []
hod = []
for (blk, key), prs in held.items():
    assert len(prs) == 8
    rows_, nchg = own_rows("b2e", prs, lambda pr: "a")
    m, h, n = pool(rows_)
    so, sn = sim_avg("b2e", prs, lambda pr: "a", 0), sim_avg("b2e", prs, lambda pr: "a", 1)
    lf, raw = lim_fig(key)
    ch = abs(sn - lf) - abs(so - lf)
    harm = m + h < 0
    if harm and blk == "A_archetype":
        veto.append(key)
    if blk == "A_archetype":
        hod.append((key, ch))
    p(f"  {blk:>11} {key:<24} own side {m:+.3f} +/- {h:.3f} over 8 rows ({nchg} changed){' HARM' if harm else ''};"
      f" both sides kog3 {so:.2f} -> kta3 {sn:.2f}; Limitless {lf:.2f} (csv score_pct mean {sum(raw)/8:.2f}); change in miss {ch:+.3f}")
p(f"  B2e held-out veto (own-side harm on 0-47): {veto or 'none'}")
closer = sum(1 for _, c in hod if c < 0)
further = sum(1 for _, c in hod if c > 0)
same = sum(1 for _, c in hod if c == 0)
p(f"HELD-OUT DIRECTION (six archetypes, gates nothing): {closer} closer, {further} further, {same} unchanged; mean change in miss {sum(c for _, c in hod)/6:+.4f}")

# Scizor: own side = kta3 on Scizor (side a)
rows_, nchg = own_rows("scizor", range(8), lambda pr: "a")
m, h, n = pool(rows_)
so, sn = sim_avg("scizor", range(8), lambda pr: "a", 0), sim_avg("scizor", range(8), lambda pr: "a", 1)
other = [paired(G["scizor"][0][pr], ms[pr], -1) for pr in range(8)]
assert all((ms[pr][i]["bot_a"], ms[pr][i]["bot_b"]) == ("kog3", "kta3") for pr in range(8) for i in range(500))
mo, ho, _ = pool(other)
p(f"SCIZOR: own side {m:+.3f} +/- {h:.3f} over 8 rows ({nchg} own-side mixed games changed; both-sides changed {sum(len(v) for v in changed_pairings['scizor'].values())}){' HARM' if m + h < 0 else ' -> no harm'};"
  f" Scizor both sides kog3 {so:.2f} -> kta3 {sn:.2f}; other direction (panel's side, reported) {mo:+.3f} +/- {ho:.3f}")

# the four second lists: own side = kta3 on the list, on the side the pairs file names
p("SECOND LISTS (own side = kta3 on the list, kog3 on the other deck):")
sl_harm = []
for v in VARS:
    g = "var_" + v
    pf = tsv(T + f"/pairs/fresh_var_{v}.tsv")
    side = {int(r["pairing"]): r["variant_side"] for r in pf}
    prs = sorted(side)
    assert set(prs) == set(G[g][0]), (g, prs)
    for pr in prs:
        nm_ = G[g][0][pr][0]["a" if side[pr] == "a" else "b"]
        assert nm_ == v, (g, pr, nm_)
    rows_, nchg = own_rows(g, prs, side.get)
    m, h, n = pool(rows_)
    so, sn = sim_avg(g, prs, side.get, 0), sim_avg(g, prs, side.get, 1)
    if m + h < 0:
        sl_harm.append(v)
    p(f"  {v:<13} own side {m:+.3f} +/- {h:.3f} over {len(prs)} rows ({nchg} changed; both-sides changed {sum(len(x) for x in changed_pairings[g].values())} in {len(changed_pairings[g])} pairings){' HARM' if m + h < 0 else ' -> no harm'};"
      f" the list's average kog3 {so:.2f} -> kta3 {sn:.2f}")
p(f"  second lists with own-side harm: {sl_harm or 'none'}")

open(OUT + "/sr4_coverage.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines))
