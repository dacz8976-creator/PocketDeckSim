#!/usr/bin/env python3
"""Second reader's independent recomputation of koa's reading (REGISTRATION.md sections 4, 5, 7, 8).
Written from the raw per-game files only; does not import or copy read_koa.py or footprint.py."""
import csv, json, math, os, sys
from collections import Counter, defaultdict

R = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
KOA = f"{R}/rl/results/koa_2026-09-26"
RD = f"{KOA}/reading"
KPF = f"{R}/rl/results/kpf_2026-09-26/reading"
B2E = f"{R}/rl/results/b2e_card_check_2026-09-26"


def load(path):
    out = {}
    n = 0
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        g = json.loads(line)
        k = (g["pairing"], g["i"])
        if k in out:
            raise SystemExit(f"duplicate key {k} in {path}")
        out[k] = g
        n += 1
    return out


def P(*a):
    print(*a)
    sys.stdout.flush()


PLAY = ("moves", "decisions", "winner_seat", "points", "first_deck_score", "openings", "seed", "first_seat", "a", "b")


def cmp(A, B, fields=PLAY):
    """Count keys in A present in B, and per-field equality."""
    common = sorted(set(A) & set(B))
    eq = Counter()
    alleq = 0
    for k in common:
        ok = True
        for f in fields:
            if A[k].get(f) == B[k].get(f):
                eq[f] += 1
            else:
                ok = False
        alleq += ok
    return len(common), eq, alleq


t_koa = load(f"{RD}/table_koa3.jsonl")
t_kp3 = load(f"{KPF}/table_kp3.jsonl")
P(f"files: table_koa3 {len(t_koa)} games; kpf table_kp3 {len(t_kp3)} games")
P("bots in table_koa3:", Counter((g['bot_a'], g['bot_b']) for g in t_koa.values()))
P("bots in table_kp3:", Counter((g['bot_a'], g['bot_b']) for g in t_kp3.values()))
P("keys identical:", set(t_koa) == set(t_kp3), "| pairings", sorted({k[0] for k in t_koa})[:3], "...", max(k[0] for k in t_koa), "| i range", min(k[1] for k in t_koa), max(k[1] for k in t_koa))
bad_seed = [k for k in t_koa if t_koa[k]["seed"] != t_kp3[k]["seed"] or t_koa[k]["seed"] != 72_000_000 + k[0] * 10_000 + k[1]]
P("seed mismatches (vs kp3 file or vs 72,000,000 + p*10,000 + i):", len(bad_seed))
bad_fs = [k for k in t_koa if t_koa[k]["first_seat"] != t_kp3[k]["first_seat"] or t_koa[k]["first_seat"] != (0 if k[1] % 2 == 0 else 1)]
P("first_seat mismatches (vs kp3, vs even-i = seat 0):", len(bad_fs))

# ---------- (0) the kp3 reference is the official engine's ----------
P("\n== 0a. kp3 reference check: kpf table_kp3 v other kp3 files at the repaired engine")
for name, path in [("koa build 9af40c8 identity_kp3_500", f"{KOA}/identity_kp3_500.jsonl"),
                   ("official 83e17ae pin_identity_kp3_500", f"{R}/rl/results/engine_switch_2026-09-26/pin_identity_kp3_500.jsonl")]:
    if os.path.exists(path):
        X = load(path)
        n, eq, alleq = cmp(t_kp3, X, ("moves", "decisions", "winner_seat", "points", "openings", "seed"))
        P(f"   kpf table_kp3 v {name}: {n} common; all fields equal {alleq}; per field {dict(eq)}")

# ---------- (1) koa3 official v cloud identity_koa3_40 ----------
P("\n== 1. koa3 at the official build (table_koa3) v the cloud's identity_koa3_40 (9af40c8)")
idk = load(f"{KOA}/identity_koa3_40.jsonl")
P(f"   identity_koa3_40: {len(idk)} games; pairings {len({k[0] for k in idk})}; i < {max(k[1] for k in idk) + 1}; bots {Counter((g['bot_a'], g['bot_b']) for g in idk.values())}")
n, eq, alleq = cmp(idk, t_koa)
P(f"   common {n}; all fields equal in {alleq}; per field {dict(eq)}")
missing = set(idk) - set(t_koa)
P(f"   identity keys missing from table_koa3: {len(missing)}")

# ---------- (2) footprint ----------
P("\n== 2. footprint: table_koa3 v table_kp3, same deals")
changed_moves = [k for k in t_koa if t_koa[k]["moves"] != t_kp3[k]["moves"]]
changed_dec = [k for k in t_koa if t_koa[k]["decisions"] != t_kp3[k]["decisions"]]
changed_any = [k for k in t_koa if any(t_koa[k][f] != t_kp3[k][f] for f in ("moves", "decisions", "winner_seat", "points", "first_deck_score", "openings"))]
changed_res = [k for k in t_koa if (t_koa[k]["winner_seat"], t_koa[k]["points"]) != (t_kp3[k]["winner_seat"], t_kp3[k]["points"])]
changed_score = [k for k in t_koa if t_koa[k]["first_deck_score"] != t_kp3[k]["first_deck_score"]]
P(f"   moves differ: {len(changed_moves)} of {len(t_koa)} = {100 * len(changed_moves) / len(t_koa):.3f}%")
P(f"   decisions differ: {len(changed_dec)}; any play/result field differs: {len(changed_any)}; winner/points differ: {len(changed_res)}; deck-a score differs: {len(changed_score)}")
P(f"   15% trigger = {0.15 * len(t_koa):.0f} games -> route: {'RESERVE' if len(changed_moves) < 0.15 * len(t_koa) else 'ORDINARY'}")
byp = Counter(k[0] for k in changed_moves)
names = {}
for k, g in t_koa.items():
    names[k[0]] = f"{g['a']} v {g['b']}"
P("   by pairing (changed / 500):")
for p in sorted(byp):
    P(f"     {p:2d} {names[p]:24s} {byp[p]}")
non_alt = [p for p in byp if "altaria" not in names[p]]
P(f"   non-Altaria pairings with any moves difference: {non_alt}")
alt_pairs = sorted(p for p in names if "altaria" in names[p])
P(f"   Altaria pairings: {alt_pairs}; Altaria is deck a in all: {all(names[p].startswith('altaria v') for p in alt_pairs)}")

# ---------- (3) leak test + opening transitions ----------
P("\n== 3. leak test (section 8) and opening transitions")
op_changed = {k for k in t_koa if t_koa[k]["openings"] != t_kp3[k]["openings"]}
leak = [k for k in changed_any if k not in op_changed]
P(f"   games with an opening changed: {len(op_changed)}")
P(f"   games that differ in any field with both openings unchanged (LEAK): {len(leak)} {leak[:5]}")
silent = [k for k in op_changed if t_koa[k]["moves"] == t_kp3[k]["moves"]]
P(f"   games with an opening changed but identical moves hash (should be 0): {len(silent)}")
trans = Counter()
side_changed = Counter()
for k in op_changed:
    for s, deck in ((0, t_koa[k]["a"]), (1, t_koa[k]["b"])):
        o, n_ = t_kp3[k]["openings"][s], t_koa[k]["openings"][s]
        if o != n_:
            trans[(deck, o, n_)] += 1
            side_changed[deck] += 1
P(f"   decks whose opening changed: {dict(side_changed)}")
for (d, o, n_), c in trans.most_common():
    P(f"     {d}: {o} -> {n_}: {c} ({100 * c / 3500:.2f}% of Altaria's 3,500 games)")
alt_share = 100 * side_changed.get("altaria", 0) / 3500
P(f"   Altaria's changed-opening share: {side_changed.get('altaria', 0)} / 3500 = {alt_share:.2f}% (registered range 22.6 to 25.4) -> {'inside' if 22.6 <= alt_share <= 25.4 else 'OUTSIDE'}")
P(f"   Altaria openings under kp3 (3500): {Counter(t_kp3[k]['openings'][0] for k in t_kp3 if k[0] in alt_pairs)}")
P(f"   Altaria openings under koa3 (3500): {Counter(t_koa[k]['openings'][0] for k in t_koa if k[0] in alt_pairs)}")
P(f"   changed-opening games with a changed deck-a score: {sum(1 for k in op_changed if t_koa[k]['first_deck_score'] != t_kp3[k]['first_deck_score'])}")

# ---------- table cell scores (Altaria's seven cells before/after) ----------
P("\n== table cells (deck a's score, %), kp3 -> koa3, Altaria's pairings")
def cell(T, p):
    v = [g["first_deck_score"] for k, g in T.items() if k[0] == p]
    return 100 * sum(v) / len(v), len(v)
for p in alt_pairs:
    a, n1 = cell(t_kp3, p); b, n2 = cell(t_koa, p)
    P(f"     {names[p]:24s} kp3 {a:.1f} -> koa3 {b:.1f} (n {n1}/{n2}); change {b - a:+.1f}")
other_moved = [p for p in names if p not in alt_pairs and abs(cell(t_kp3, p)[0] - cell(t_koa, p)[0]) > 1e-12]
P(f"   non-Altaria cells whose score moved: {other_moved}")

# ---------- (4) mixed rows ----------
P("\n== 4. mixed rows")
m1 = load(f"{RD}/mixed_koa3_first.jsonl")
m2 = load(f"{RD}/mixed_koa3_second.jsonl")
P(f"   mixed_koa3_first: {len(m1)} games, bots {Counter((g['bot_a'], g['bot_b']) for g in m1.values())}, pairings {sorted({k[0] for k in m1})}")
P(f"   mixed_koa3_second: {len(m2)} games, bots {Counter((g['bot_a'], g['bot_b']) for g in m2.values())}, pairings {sorted({k[0] for k in m2})}")
for nm, M in (("first", m1), ("second", m2)):
    bs = [k for k in M if M[k]["seed"] != t_kp3[k]["seed"]]
    P(f"   {nm}: seeds differing from kp3's table on the same key: {len(bs)}; keys missing from kp3 table: {len(set(M) - set(t_kp3))}")

# opponents' side: second file must be exact identity of kp3's table
n, eq, alleq = cmp(m2, t_kp3, ("moves", "decisions", "winner_seat", "points", "first_deck_score", "openings", "seed", "first_seat"))
P(f"   opponents' rows (koa3 on the opponent): {n} games; identical to kp3's table on every play/result field: {alleq}; per field {dict(eq)}")
opp_d = []
for p in alt_pairs:
    ks = [k for k in m2 if k[0] == p]
    d = [-100 * (m2[k]["first_deck_score"] - t_kp3[k]["first_deck_score"]) for k in ks]
    opp_d.append(d)
P(f"   opponents' own-side change per cell: {[round(sum(d) / len(d), 3) for d in opp_d]}")

# first file: leak check within mixed rows, and identity with table_koa3
op1 = {k for k in m1 if m1[k]["openings"] != t_kp3[k]["openings"]}
ch1 = {k for k in m1 if any(m1[k][f] != t_kp3[k][f] for f in ("moves", "decisions", "winner_seat", "points", "first_deck_score", "openings"))}
P(f"   mixed first: openings changed {len(op1)}; games differing from kp3 {len(ch1)}; differ with openings unchanged (leak) {len(ch1 - op1)}; opponent's opening changed {sum(1 for k in op1 if m1[k]['openings'][1] != t_kp3[k]['openings'][1])}")
n, eq, alleq = cmp(m1, t_koa, ("moves", "decisions", "winner_seat", "points", "first_deck_score", "openings", "seed"))
P(f"   mixed first v table_koa3 (koa3 on both sides) on pairings 0-6: {n} common; all equal {alleq}; per field {dict(eq)}")


def mv(d, ddof=1):
    n = len(d); m = sum(d) / n
    return m, sum((x - m) ** 2 for x in d) / max(n - ddof, 1) / n


P("   Altaria's own side: mixed_koa3_first minus kp3's table, same deals (points per game)")
own = []
for p in alt_pairs:
    ks = sorted(k for k in m1 if k[0] == p)
    d = [100 * (m1[k]["first_deck_score"] - t_kp3[k]["first_deck_score"]) for k in ks]
    own.append(d)
    m, v = mv(d)
    _, v0 = mv(d, 0)
    nz = sum(1 for x in d if x != 0)
    P(f"     {names[p]:24s} {m:+.2f} +/- {1.96 * math.sqrt(v):.2f} (n {len(d)}; ddof0 +/- {1.96 * math.sqrt(v0):.2f}; nonzero deals {nz}; wins gained {sum(1 for x in d if x > 0)}, lost {sum(1 for x in d if x < 0)})")
mvs = [mv(d) for d in own]
pm = sum(m for m, _ in mvs) / len(mvs)
ph = 1.96 * math.sqrt(sum(v for _, v in mvs)) / len(mvs)
P(f"   POOLED (stratified mean of 7 cell means): {pm:+.3f} +/- {ph:.3f} -> lower bound {pm - ph:+.3f}; {'above zero beyond noise' if pm - ph > 0 else 'NOT beyond noise'}")
flat = [x for d in own for x in d]
m_, v_ = mv(flat)
P(f"   (unstratified check: {m_:+.3f} +/- {1.96 * math.sqrt(v_):.3f} over {len(flat)} deals)")
dec = [d for p, d in zip(alt_pairs, own) if "sceptile" not in names[p]]
mvs6 = [mv(d) for d in dec]
P(f"   decision set (6 cells, Sceptile quarantined): {sum(m for m, _ in mvs6) / 6:+.3f} +/- {1.96 * math.sqrt(sum(v for _, v in mvs6)) / 6:.3f}")

# diagnostics kob3/kor3 (reported only)
P("\n== diagnostics (reported only; not part of koa's decision)")
for b in ("kob3", "kor3"):
    f1 = f"{RD}/mixed_{b}_first.jsonl"; f2 = f"{RD}/mixed_{b}_second.jsonl"
    if not os.path.exists(f1):
        continue
    X = load(f1); Y = load(f2)
    parts = []
    for p in alt_pairs:
        ks = sorted(k for k in X if k[0] == p)
        parts.append([100 * (X[k]["first_deck_score"] - t_kp3[k]["first_deck_score"]) for k in ks])
    mm = [mv(d) for d in parts]
    P(f"   {b} Altaria own side pooled: {sum(m for m, _ in mm) / 7:+.3f} +/- {1.96 * math.sqrt(sum(v for _, v in mm)) / 7:.3f}")
    n, eq, alleq = cmp(Y, t_kp3, ("moves", "decisions", "winner_seat", "points", "openings"))
    P(f"   {b} second (on Altaria's opponents): {n} games, identical to kp3's table {alleq} (per field {dict(eq)})")
    tr = Counter((t_kp3[k]["openings"][0], X[k]["openings"][0]) for k in X if X[k]["openings"][0] != t_kp3[k]["openings"][0])
    P(f"   {b} Altaria transitions: {dict(tr)}")
kb = load(f"{RD}/mixed_kob3_first.jsonl"); kr = load(f"{RD}/mixed_kor3_first.jsonl")
n, eq, alleq = cmp(kb, kr, ("moves", "decisions", "winner_seat", "points", "openings"))
P(f"   kob3_first v kor3_first: {n} common; identical {alleq} (per field {dict(eq)})")

# ---------- (6) held-out B2e ----------
P("\n== 6. held-out check, B2e pairings 0-47")
tsv = list(csv.DictReader(open(f"{B2E}/b2e_pairings.tsv", encoding="utf-8"), delimiter="\t"))
rows = {int(r["pairing"]): r for r in tsv}
bk = load(f"{RD}/b2e_koa3.jsonl")
bp = load(f"{KPF}/b2e_kp3.jsonl")
P(f"   b2e_koa3: {len(bk)} games, pairings {min(k[0] for k in bk)}-{max(k[0] for k in bk)}, bots {Counter((g['bot_a'], g['bot_b']) for g in bk.values())}")
P(f"   b2e_kp3 (kpf reading): {len(bp)} games, pairings {min(k[0] for k in bp)}-{max(k[0] for k in bp)}, bots {Counter((g['bot_a'], g['bot_b']) for g in bp.values())}")
keys48 = sorted(k for k in bk if k[0] <= 47)
P(f"   koa3 keys 0-47: {len(keys48)}; present in kp3 file: {sum(1 for k in keys48 if k in bp)}")
seedbad = [k for k in keys48 if bk[k]["seed"] != bp[k]["seed"] or bk[k]["seed"] != int(rows[k[0]]["seed_first"]) + k[1]]
P(f"   seed mismatches (vs kp3, vs tsv seed_first + i): {len(seedbad)}")
namebad = [k for k in keys48 if (bk[k]["a"], bk[k]["b"]) != (rows[k[0]]["held_key"], rows[k[0]]["opponent"]) or (bp[k]["a"], bp[k]["b"]) != (bk[k]["a"], bk[k]["b"])]
P(f"   deck-name mismatches with the tsv: {len(namebad)}")
bch = [k for k in keys48 if any(bk[k][f] != bp[k][f] for f in ("moves", "decisions", "winner_seat", "points", "first_deck_score", "openings"))]
bop = {k for k in keys48 if bk[k]["openings"] != bp[k]["openings"]}
P(f"   B2e games differing from kp3: {len(bch)}; openings changed {len(bop)}; differ with openings unchanged (leak) {len([k for k in bch if k not in bop])}")
P(f"   B2e opening changes by side: held deck {sum(1 for k in bop if bk[k]['openings'][0] != bp[k]['openings'][0])}, panel deck {sum(1 for k in bop if bk[k]['openings'][1] != bp[k]['openings'][1])}; by opponent {dict(Counter(bk[k]['b'] for k in bop))}")
P(f"   B2e changed pairings' opponents: {dict(Counter(rows[k[0]]['opponent'] for k in bch))}")

lim = defaultdict(dict)
for r in csv.DictReader(open(f"{B2E}/limitless_cells.csv", encoding="utf-8")):
    lim[r["dataset"]][(r["archetype"], r["opponent"])] = (float(r["score_pct"]) if int(r["n"]) else None, int(r["n"]))
arches = sorted({a for a, _ in lim["pooled"]})
P(f"   Limitless archetypes: {arches}")


def panel(T):
    by = defaultdict(list)
    for k in keys48:
        g = T[k]
        by[(rows[k[0]]["held_key"], rows[k[0]]["opponent"])].append(g["first_deck_score"])
    out = defaultdict(dict)
    for (h, o), s in by.items():
        out[h][o] = 100 * sum(s) / len(s)
    return out


pk, pa = panel(bp), panel(bk)
for h in sorted(pk):
    arch = [a for a in arches if a == h or a.startswith(h + "_") or a.startswith(h)]
    a_ = arch[0] if len(arch) == 1 else None
    opps = sorted(pk[h])
    s0 = sum(pk[h].values()) / len(opps); s1 = sum(pa[h].values()) / len(opps)
    cells = [(o, lim["pooled"].get((a_, o), (None, 0))) for o in opps]
    have = [(o, v) for o, (v, n) in cells if v is not None]
    L = sum(v for _, v in have) / len(have)
    devs = [lim["development"].get((a_, o), (None, 0))[0] for o, _ in have]
    Ld = sum(x for x in devs if x is not None) / len([x for x in devs if x is not None])
    fur = abs(s1 - L) - abs(s0 - L)
    P(f"     {h:18s} ({a_}; {len(opps)} opponents, {len(have)} pooled cells with n>0) kp3 {s0:.2f} -> koa3 {s1:.2f} (change {s1 - s0:+.2f}); L pooled {L:.2f} (dev {Ld:.2f}); further by {fur:+.2f} -> {'VETO FIRES' if fur > 2 else 'no veto'}")
    P(f"        per-opponent change: " + ", ".join(f"{o} {pa[h][o] - pk[h][o]:+.1f}" for o in opps))
