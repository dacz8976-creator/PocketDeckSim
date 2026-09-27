"""Second reader's independent checks on koa's reading (registration compliance). Reads files only; plays nothing."""
import csv, json, math, os, sys
from collections import Counter, defaultdict

R = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
O = R + "/rl/results/koa_2026-09-26/reading"
KPF = R + "/rl/results/kpf_2026-09-26/reading"
NAMES = ['altaria', 'blaziken', 'hydreigon', 'lucario', 'sceptile', 'suicune', 'vespiquen', 'weezing']
import itertools
PAIRS = list(itertools.combinations(NAMES, 2))
ALT = [p for p, (a, b) in enumerate(PAIRS) if 'altaria' in (a, b)]


def load(f):
    return {(g["pairing"], g["i"]): g for g in map(json.loads, open(f, encoding="utf-8"))}


kp3 = load(KPF + "/table_kp3.jsonl")
koa = load(O + "/table_koa3.jsonl")
pin = load(R + "/rl/results/engine_switch_2026-09-26/pin_identity_kp3_500.jsonl")
print("== table")
print("n", len(kp3), len(koa), "pairings in PAIRS order match file a/b:",
      all((koa[k]["a"], koa[k]["b"]) == PAIRS[k[0]] for k in koa))
print("seeds equal:", sum(koa[k]["seed"] == kp3[k]["seed"] for k in kp3), "first_seat equal:",
      sum(koa[k]["first_seat"] == kp3[k]["first_seat"] for k in kp3))
print("seed formula 72e6+p*1e4+i:", all(koa[k]["seed"] == 72_000_000 + k[0] * 10_000 + k[1] for k in koa))
print("bots koa file:", Counter((g["bot_a"], g["bot_b"]) for g in koa.values()))
print("kpf kp3 == pin (official build) kp3 on moves/decisions/points/winner:",
      sum(all(kp3[k][f] == pin[k][f] for f in ("moves", "decisions", "points", "winner_seat", "seed")) for k in kp3))
print("openings field present in all koa table games:", all("openings" in g and len(g["openings"]) == 2 for g in koa.values()))
dm = [k for k in kp3 if koa[k]["moves"] != kp3[k]["moves"]]
dd = [k for k in kp3 if koa[k]["decisions"] != kp3[k]["decisions"]]
o0 = [k for k in kp3 if koa[k]["openings"][0] != kp3[k]["openings"][0]]
o1 = [k for k in kp3 if koa[k]["openings"][1] != kp3[k]["openings"][1]]
print("moves differ", len(dm), "decisions differ", len(dd), "first-deck opening changed", len(o0), "second-deck opening changed", len(o1))
print("moves-differ set == decisions-differ set:", set(dm) == set(dd))
leak = [k for k in dm if koa[k]["openings"] == kp3[k]["openings"]]
leak_d = [k for k in dd if koa[k]["openings"] == kp3[k]["openings"]]
print("leak (moves differ, both openings same):", len(leak), "; on decisions:", len(leak_d))
print("opening changed but moves same:", len([k for k in set(o0) | set(o1) if koa[k]["moves"] == kp3[k]["moves"]]))
alt_games = [k for k in kp3 if k[0] in ALT]
alt_changed = [k for k in alt_games if koa[k]["openings"][0] != kp3[k]["openings"][0]]
print(f"Altaria openings changed: {len(alt_changed)} of {len(alt_games)} = {100*len(alt_changed)/len(alt_games):.2f}% (range 22.6-25.4)")
tr = Counter((kp3[k]["openings"][0], koa[k]["openings"][0]) for k in alt_changed)
for (a, b), n in tr.most_common():
    print(f"   {a} -> {b}: {n} = {100*n/len(alt_games):.2f}% of Altaria's openings")
print("changed games outside Altaria pairings:", len([k for k in dm if k[0] not in ALT]))
fp = 100 * len(dm) / 14000
se = math.sqrt(fp / 100 * (1 - fp / 100) / 14000) * 100
print(f"footprint {fp:.2f}% (sampling 95% about {fp-1.96*se:.2f}-{fp+1.96*se:.2f}); registered 6.0% range 790-890 games -> {len(dm)}")

print("== mixed rows")
for side in ("first", "second"):
    m = load(O + f"/mixed_koa3_{side}.jsonl")
    ks = sorted(m)
    print(side, "n", len(m), "pairings", sorted({k[0] for k in m}), "bots", Counter((g["bot_a"], g["bot_b"]) for g in m.values()))
    print("   seeds == table seeds:", all(m[k]["seed"] == kp3[k]["seed"] and m[k]["first_seat"] == kp3[k]["first_seat"] for k in ks))
    d = [k for k in ks if m[k]["moves"] != kp3[k]["moves"]]
    lk = [k for k in d if m[k]["openings"] == kp3[k]["openings"]]
    c0 = sum(m[k]["openings"][0] != kp3[k]["openings"][0] for k in ks)
    c1 = sum(m[k]["openings"][1] != kp3[k]["openings"][1] for k in ks)
    print(f"   differ from kp3 table: {len(d)}; leak {len(lk)}; opening changes deck a {c0}, deck b {c1}")
    # mixed first: koa on Altaria; changed games should equal the table's Altaria-opening-changed games (same deals)?
    if side == "first":
        same_set = set(k for k in ks if m[k]["openings"][0] != kp3[k]["openings"][0]) == set(alt_changed)
        print("   Altaria opening changes in mixed-first equal those in koa's table (same deals):", same_set)
        # own-side change, pooled
        per = {}
        allds = []
        for p in ALT:
            ds = [m[(p, i)]["first_deck_score"] - kp3[(p, i)]["first_deck_score"] for i in range(500)]
            mu = sum(ds) / 500
            var = sum((x - mu) ** 2 for x in ds) / 499 / 500
            per[p] = (100 * mu, 100 * 1.96 * math.sqrt(var))
            allds += ds
        for p, (mu, h) in per.items():
            print(f"     {PAIRS[p][0]} v {PAIRS[p][1]}: {mu:+.2f} +/- {h:.2f} (95%)  lo {mu-h:+.2f}")
        mean7 = sum(v[0] for v in per.values()) / 7
        se7 = math.sqrt(sum((v[1] / 1.96) ** 2 for v in per.values())) / 7
        print(f"   pooled mean of 7 rows {mean7:+.3f}, 95% +/- {1.96*se7:.3f}, 90% +/- {1.645*se7:.3f}; z {mean7/se7:.2f}")
        mu = sum(allds) / len(allds); var = sum((x - mu) ** 2 for x in allds) / (len(allds) - 1) / len(allds)
        print(f"   pooled over 3500 deals {100*mu:+.3f} +/- {100*1.96*math.sqrt(var):.3f}")
        # Lucario row
        pl = PAIRS.index(('altaria', 'lucario'))
        print(f"   Altaria v Lucario row: {per[pl][0]:+.2f} +/- {per[pl][1]:.2f}; below zero beyond noise? {per[pl][0] + per[pl][1] < 0}")

print("== diagnostics kob3/kor3 Altaria rows")
kob1, kor1 = load(O + "/mixed_kob3_first.jsonl"), load(O + "/mixed_kor3_first.jsonl")
kob2, kor2 = load(O + "/mixed_kob3_second.jsonl"), load(O + "/mixed_kor3_second.jsonl")
print("kob3_first == kor3_first moves:", sum(kob1[k]["moves"] == kor1[k]["moves"] for k in kob1), "of", len(kob1))
tb = Counter((kp3[k]["openings"][0], kob1[k]["openings"][0]) for k in kob1 if kob1[k]["openings"][0] != kp3[k]["openings"][0])
print("kob3 Altaria transitions:", dict(tb), "share", sum(tb.values()) / 3500)
for nm, f2 in (("kob3", kob2), ("kor3", kor2)):
    byopp = defaultdict(lambda: [0, 0, 0])
    for k, g in f2.items():
        opp = PAIRS[k[0]][1]
        byopp[opp][0] += 1
        byopp[opp][1] += g["moves"] != kp3[k]["moves"]
        byopp[opp][2] += g["openings"][1] != kp3[k]["openings"][1]
    print(nm, "on the opponent v kp3 Altaria (n, games differ, opponent opening changed):", dict(byopp))

print("== B2e")
b2k = load(KPF + "/b2e_kp3.jsonl")
b2a = load(O + "/b2e_koa3.jsonl")
print("koa b2e n", len(b2a), "pairings", min(k[0] for k in b2a), "-", max(k[0] for k in b2a), "; kp3 b2e n", len(b2k), "pairings",
      min(k[0] for k in b2k), "-", max(k[0] for k in b2k))
tsv = {int(r["pairing"]): r for r in csv.DictReader(open(R + "/rl/results/b2e_card_check_2026-09-26/b2e_pairings.tsv"), delimiter="\t")}
print("seeds equal on 0-47:", all(b2a[k]["seed"] == b2k[k]["seed"] for k in b2a), "; seed == tsv seed_first + i:",
      all(b2a[k]["seed"] == int(tsv[k[0]]["seed_first"]) + k[1] for k in b2a))
old = load(R + "/rl/results/b2e_rows_2026-09-26/b2e_kp3_arch.jsonl")
print("old B2e kp3 rows (7fc6ccb) n", len(old), "seeds equal to kpf b2e:", all(old[k]["seed"] == b2k[k]["seed"] for k in old if k in b2k))
chg_old = [k for k in old if k in b2k and old[k]["moves"] != b2k[k]["moves"]]
print("kp3 B2e games changed by the engine switch (0-47):", len(chg_old))
diffp = Counter()
leakb = 0
held_open = 0
for k in b2a:
    if b2a[k]["moves"] != b2k[k]["moves"]:
        diffp[(tsv[k[0]]["held_key"], tsv[k[0]]["opponent"])] += 1
        if b2a[k]["openings"] == b2k[k]["openings"]:
            leakb += 1
    if b2a[k]["openings"][0] != b2k[k]["openings"][0]:
        held_open += 1
print("B2e games differing by (held, opponent):", dict(diffp))
print("B2e leak (differ with both openings same):", leakb, "; held deck opening changes:", held_open)
# held-out veto, matched cell sets
lim = defaultdict(dict)
for r in csv.DictReader(open(R + "/rl/results/b2e_card_check_2026-09-26/limitless_cells.csv")):
    if int(r["n"]):
        lim[r["dataset"]][(r["archetype"], r["opponent"])] = float(r["score_pct"])
names = sorted({a for a, _ in lim["pooled"]})


def panel(d):
    by = defaultdict(list)
    for k, g in d.items():
        if k[0] < 48:
            by[(tsv[k[0]]["held_key"], tsv[k[0]]["opponent"])].append(g["first_deck_score"])
    out = defaultdict(dict)
    for (h, o), s in by.items():
        out[h][o] = 100 * sum(s) / len(s)
    return out


A, B = panel(b2k), panel(b2a)
for h in sorted(A):
    arch = next((n for n in names if n == h), None) or next((n for n in names if n.startswith(h)), None)
    cells = [o for o in A[h] if (arch, o) in lim["pooled"]]
    L = sum(lim["pooled"][(arch, o)] for o in cells) / len(cells)
    x_all, y_all = sum(A[h].values()) / len(A[h]), sum(B[h].values()) / len(B[h])
    x_m, y_m = sum(A[h][o] for o in cells) / len(cells), sum(B[h][o] for o in cells) / len(cells)
    print(f"  {h} ({arch}): cells with Limitless {len(cells)}/8; all-8: {x_all:.1f}->{y_all:.1f} further {abs(y_all-L)-abs(x_all-L):+.2f};"
          f" matched: {x_m:.1f}->{y_m:.1f} L {L:.1f} further {abs(y_m-L)-abs(x_m-L):+.2f}; Altaria cell {A[h]['altaria']:.1f}->{B[h]['altaria']:.1f}")
