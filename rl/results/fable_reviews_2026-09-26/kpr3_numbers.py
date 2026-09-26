#!/usr/bin/env python3
"""Independent recount of the kpr3 readout: file structure, identity replays by fingerprint, footprint against kp3,
fit to the Sept 23 Limitless table and to scoreboard v2, paired dMSE bootstrap, veto candidates. Read-only."""
import json, math, random, re, sys
from pathlib import Path

B = Path("/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/75cb92d0-6f2d-44b8-a636-513a8f7ee71a/scratchpad/reviews/branch")
R = B / "ref"
MAIN = Path("/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results")


def load(*paths):
    games = {}
    for p in paths:
        for line in open(p, encoding="utf-8"):
            if line.strip():
                g = json.loads(line)
                k = (g["pairing"], g["i"])
                if k in games:
                    print(f"  DUPLICATE key {k} in {p.name}")
                games[k] = g
    return games


def compare(name, new, ref, fields=("moves", "first_deck_score", "winner_seat", "points", "turns", "seed", "a", "b", "first_seat")):
    same = diff = missing = 0
    bad_fields = {}
    for k, g in new.items():
        r = ref.get(k)
        if r is None:
            missing += 1
            continue
        ok = True
        for f in fields:
            if g.get(f) != r.get(f):
                ok = False
                bad_fields[f] = bad_fields.get(f, 0) + 1
        if ok:
            same += 1
        else:
            diff += 1
    print(f"  {name}: {same} identical of {len(new)} ({diff} differ, {missing} not in reference){'  fields: ' + str(bad_fields) if bad_fields else ''}")
    return same, diff, missing


print("=== structure of kpr3_500.jsonl ===")
kpr = load(B / "kpr3_500.jsonl")
pairings = sorted({p for p, _ in kpr})
print(f"  games {len(kpr)}, pairings {len(pairings)} ({pairings[0]}..{pairings[-1]}), i range {min(i for _, i in kpr)}..{max(i for _, i in kpr)}")
bots = {(g["bot_a"], g["bot_b"]) for g in kpr.values()}
print(f"  bot pairs: {bots}")
bad_seed = sum(1 for (p, i), g in kpr.items() if g["seed"] != 72_000_000 + p * 10_000 + i)
bad_seat = sum(1 for (p, i), g in kpr.items() if g["first_seat"] != (i % 2))
print(f"  seed formula violations: {bad_seed}; first_seat != i%2: {bad_seat}")
cells_kpr = sorted({(g["a"], g["b"]) for g in kpr.values()})
print(f"  cells: {len(cells_kpr)}")

print("\n=== identity replays, by every field including the move fingerprint ===")
kp3_ref = load(R / "kp3_500_worst5.jsonl", R / "kp3_500_rest.jsonl")
k3_ref = load(R / "k3_500.jsonl")
kq3_ref = load(R / "kq3_500.jsonl")
kd3_ref = load(R / "kd3_500.jsonl")
id_kp3 = load(B / "identity_kp3_500.jsonl")
id_k3 = load(R / "identity_k3_500.jsonl")
id_kq3 = load(R / "identity_kq3_500.jsonl")
id_kd3 = load(R / "identity_kd3_40.jsonl")
print("  (full replay at 53638a7, bot code = 1981bb4's)")
compare("kp3 identity_kp3_500 vs kp3 table", id_kp3, kp3_ref)
compare("k3  identity_k3_500 vs k3 table", id_k3, k3_ref)
compare("kq3 identity_kq3_500 vs kq3 table", id_kq3, kq3_ref)
compare("kd3 identity_kd3_40 vs kd3 table", id_kd3, kd3_ref)
print("  (subset at the table's own build e09fb46, bot code = 14c7d9b's)")
for bot, ref in (("k3", k3_ref), ("kp3", kp3_ref), ("kq3", kq3_ref)):
    sub = load(R / f"table_commit_identity_{bot}_40.jsonl")
    imax = max(i for _, i in sub)
    print(f"    {bot}: {len(sub)} games, i max {imax}, pairings {len({p for p, _ in sub})}")
    compare(f"{bot} table_commit_identity_{bot}_40 vs {bot} table", sub, ref)
part = load(R / "identity_k3_9a35f54_partial.jsonl")
compare("k3 identity_k3_9a35f54_partial vs k3 table", part, k3_ref)
print(f"  kd3 coverage at the table's build: none (kd3 subset only at 53638a7); games covered at e09fb46 per bot = 1120 of 14000 = {1120/14000:.1%}")

print("\n=== footprint: kpr3 v kpr3 against kp3 v kp3 on the same deals ===")
diff_games = sum(1 for k, g in kpr.items() if g["moves"] != kp3_ref[k]["moves"])
print(f"  games whose move fingerprint differs: {diff_games} of {len(kpr)} = {diff_games/len(kpr):.1%}")
by_cell = {}
for k, g in kpr.items():
    c = (g["a"], g["b"])
    s = by_cell.setdefault(c, [0, 0])
    s[1] += 1
    if g["moves"] != kp3_ref[k]["moves"]:
        s[0] += 1
lo = min(by_cell.items(), key=lambda kv: kv[1][0] / kv[1][1])
hi = max(by_cell.items(), key=lambda kv: kv[1][0] / kv[1][1])
print(f"  least-changed cell {lo[0]}: {lo[1][0]} of {lo[1][1]}; most-changed {hi[0]}: {hi[1][0]} of {hi[1][1]}")
diff_outcome = sum(1 for k, g in kpr.items() if g["first_deck_score"] != kp3_ref[k]["first_deck_score"])
print(f"  games whose result differs: {diff_outcome} of {len(kpr)} = {diff_outcome/len(kpr):.1%}")
# also for reference: kd3 v kp3 footprint, and kq3
diff_kd = sum(1 for k, g in kd3_ref.items() if g["moves"] != kp3_ref[k]["moves"])
diff_kq = sum(1 for k, g in kq3_ref.items() if g["moves"] != kp3_ref[k]["moves"])
print(f"  for scale: kd3 differs from kp3 in {diff_kd/len(kd3_ref):.1%} of games, kq3 in {diff_kq/len(kq3_ref):.1%}")

print("\n=== Limitless cells ===")
sept23 = {}
text = (R / "limitless_check_2026-09-23.md").read_text(encoding="utf-8").split("### Rules4, every pairing")[1].split("## Part 2")[0]
for line in text.splitlines():
    m = re.match(r"\|\s*(\w+) v (\w+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+) ± ([\d.]+)\s*\|", line)
    if m:
        sept23[(m.group(1), m.group(2))] = dict(score=float(m.group(4)), band=float(m.group(5)), n=None)
print(f"  Sept 23 table: {len(sept23)} cells parsed")
v2raw = json.loads((MAIN / "scoreboard_v2_2026-09-25/limitless_v2_dev.json").read_text(encoding="utf-8"))["cells"]
v2 = {}
for key, (w, l, t) in v2raw.items():
    a, b = key.split("|")
    n = w + l + t
    p = (w + t / 2) / n
    v2[(a, b)] = dict(score=100 * p, band=100 * 1.96 * math.sqrt(p * (1 - p) / n), n=n)
print(f"  v2: {len(v2)} cells, matches {sum(c['n'] for c in v2.values())}")
QUAR = {("altaria", "sceptile")}


def cell_scores(games):
    out = {}
    for g in games.values():
        s = out.setdefault((g["a"], g["b"]), [])
        s.append(g["first_deck_score"])
    return out


S_kp3 = cell_scores(kp3_ref)
S_kpr = cell_scores(kpr)
S_k3 = cell_scores(k3_ref)


def fit(name, S, lim, cells):
    misses = [100 * sum(S[c]) / len(S[c]) - lim[c]["score"] for c in cells]
    mse = sum(m * m for m in misses) / len(misses)
    mae = sum(abs(m) for m in misses) / len(misses)
    return mae, mse


for label, lim in (("Sept 23", sept23), ("v2", v2)):
    for cellset_name, cells in (("28 cells", sorted(lim)), ("27-cell decision set", sorted(c for c in lim if c not in QUAR))):
        print(f"  {label}, {cellset_name}:")
        for bot, S in (("k3", S_k3), ("kp3", S_kp3), ("kpr3", S_kpr)):
            mae, mse = fit(bot, S, lim, cells)
            print(f"    {bot:5} mean |miss| {mae:.2f}  mean squared miss {mse:.1f}")

print("\n=== per-cell: kp3, kpr3, change, Limitless Sept 23 / v2, miss growth (veto candidates: > 6), v2 band ===")
print(f"  {'cell':24} {'kp3':>6} {'kpr3':>6} {'chg':>6}  {'L23':>6} {'m23kp3':>7} {'m23kpr':>7} {'grow23':>7} | {'Lv2':>6} {'mv2kp3':>7} {'mv2kpr':>7} {'growv2':>7} {'bandv2':>6} {'n':>4}")
grow_flags = []
for c in sorted(sept23):
    kp = 100 * sum(S_kp3[c]) / len(S_kp3[c])
    kr = 100 * sum(S_kpr[c]) / len(S_kpr[c])
    L23, Lv2 = sept23[c]["score"], v2[c]["score"]
    g23 = abs(kr - L23) - abs(kp - L23)
    gv2 = abs(kr - Lv2) - abs(kp - Lv2)
    flag = ""
    if g23 > 6:
        flag += " VETO23"
    if gv2 > 6:
        flag += " VETOv2" + ("(band>15, excluded)" if v2[c]["band"] > 15.0 else "")
    if c in QUAR:
        flag += " quarantined"
    if flag:
        grow_flags.append((c, flag))
    print(f"  {c[0]+' v '+c[1]:24} {kp:6.1f} {kr:6.1f} {kr-kp:+6.1f}  {L23:6.1f} {kp-L23:+7.1f} {kr-L23:+7.1f} {g23:+7.1f} | {Lv2:6.1f} {kp-Lv2:+7.1f} {kr-Lv2:+7.1f} {gv2:+7.1f} {v2[c]['band']:6.1f} {v2[c]['n']:4}{flag}")

print("\n=== deck averages and deck-gap growth (veto candidates: > 2) ===")
decks = sorted({d for c in sept23 for d in c})


def deck_avg(S, lim, deck, cells):
    vals, lvals = [], []
    for c in cells:
        if deck in c:
            s = 100 * sum(S[c]) / len(S[c])
            l = lim[c]["score"]
            if c[0] != deck:
                s, l = 100 - s, 100 - l
            vals.append(s)
            lvals.append(l)
    return sum(vals) / len(vals), sum(lvals) / len(lvals)


for label, lim, cells in (("Sept 23, 28 cells", sept23, sorted(sept23)), ("v2, 27 cells", v2, sorted(c for c in v2 if c not in QUAR))):
    print(f"  {label}:")
    for d in decks:
        kp, L = deck_avg(S_kp3, lim, d, cells)
        kr, _ = deck_avg(S_kpr, lim, d, cells)
        grow = abs(kr - L) - abs(kp - L)
        print(f"    {d:10} L {L:5.1f}  kp3 {kp:5.1f} (gap {kp-L:+5.1f})  kpr3 {kr:5.1f} (gap {kr-L:+5.1f})  growth {grow:+5.1f}{'  VETO CANDIDATE' if grow > 2 else ''}")

print("\n=== paired per-deck change kpr3 - kp3 (pooled over the deck's 7 cells, 95%) ===")
for d in decks:
    diffs = []
    for k, g in kpr.items():
        if d in (g["a"], g["b"]):
            s_new = g["first_deck_score"] if g["a"] == d else 1 - g["first_deck_score"]
            r = kp3_ref[k]
            s_old = r["first_deck_score"] if r["a"] == d else 1 - r["first_deck_score"]
            diffs.append(s_new - s_old)
    m = sum(diffs) / len(diffs)
    sd = math.sqrt(sum((x - m) ** 2 for x in diffs) / (len(diffs) - 1))
    print(f"  {d:10} {100*m:+.1f} ± {100*1.96*sd/math.sqrt(len(diffs)):.1f}  (n {len(diffs)})")

print("\n=== paired dMSE bootstrap, kpr3 - kp3 (deals resampled within each cell, paired; Limitless redrawn Binomial(n, L)) ===")
random.seed(20260926)


def dmse_boot(lim, cells, reps=4000):
    # per cell: paired per-deal scores
    per = {}
    for c in cells:
        keys = sorted(k for k, g in kpr.items() if (g["a"], g["b"]) == c)
        per[c] = ([kp3_ref[k]["first_deck_score"] for k in keys], [kpr[k]["first_deck_score"] for k in keys])
    point = 0.0
    for c in cells:
        old, new = per[c]
        L = lim[c]["score"]
        so, sn = 100 * sum(old) / len(old), 100 * sum(new) / len(new)
        point += (sn - L) ** 2 - (so - L) ** 2
    point /= len(cells)
    draws = []
    for _ in range(reps):
        tot = 0.0
        for c in cells:
            old, new = per[c]
            n = len(old)
            idx = [random.randrange(n) for _ in range(n)]
            so = 100 * sum(old[i] for i in idx) / n
            sn = 100 * sum(new[i] for i in idx) / n
            Ln = lim[c]["n"]
            if Ln:
                p = lim[c]["score"] / 100
                L = 100 * sum(1 for _ in range(Ln) if random.random() < p) / Ln
            else:
                # Sept 23 table: n not parsed; use the band to back out n
                band = lim[c]["band"] / 100
                p = lim[c]["score"] / 100
                Ln_est = max(1, round(1.96 ** 2 * p * (1 - p) / band ** 2)) if band > 0 else 1000
                L = 100 * sum(1 for _ in range(Ln_est) if random.random() < p) / Ln_est
            tot += (sn - L) ** 2 - (so - L) ** 2
        draws.append(tot / len(cells))
    draws.sort()
    return point, draws[int(0.025 * reps)], draws[int(0.975 * reps) - 1]


for label, lim in (("v2, 27-cell decision set", v2), ("Sept 23, 27 cells", sept23)):
    cells = sorted(c for c in lim if c not in QUAR)
    pt, lo, hi = dmse_boot(lim, cells, reps=2000)
    print(f"  {label}: dMSE {pt:+.1f}, 95% ({lo:+.1f}, {hi:+.1f}) -> {'whole interval below zero: ADOPTABLE by metric' if hi < 0 else 'NOT below zero'}")

print("\n=== real error tau-hat on v2 (27 cells): sqrt(mean[(S-L)^2 - SE_L^2 - SE_S^2]) ===")
for bot, S in (("k3", S_k3), ("kp3", S_kp3), ("kpr3", S_kpr)):
    acc = 0.0
    cells = sorted(c for c in v2 if c not in QUAR)
    for c in cells:
        s = sum(S[c]) / len(S[c])
        n_s = len(S[c])
        se_s = 100 * math.sqrt(s * (1 - s) / n_s)
        p = v2[c]["score"] / 100
        se_l = 100 * math.sqrt(p * (1 - p) / v2[c]["n"])
        acc += (100 * s - v2[c]["score"]) ** 2 - se_l ** 2 - se_s ** 2
    acc /= len(cells)
    print(f"  {bot:5} tau-hat {math.sqrt(max(acc, 0)):.2f}")

print("\n=== flags summary ===")
for c, f in grow_flags:
    print(f"  {c[0]} v {c[1]}:{f}")
