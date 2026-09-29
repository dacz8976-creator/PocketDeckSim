#!/usr/bin/env python3
"""Error attribution for kog3's 14.0 on the 45 development cells (Sept 29). Read-only on the repo; no game or engine is run.
Usage (WSL, from anywhere):  nice -n 10 python3 -B attribute.py > attribution_numbers.txt   (also writes cells.csv here)

Per cell, kog3's squared miss against the Limitless development half is split into
  1. chance floor            Limitless binomial noise + simulator's 500-deal noise (exact, score.py's own tau-hat terms)
  2. real-side instability   how far the two halves of the Limitless events disagree beyond binomial noise (group level)
  3. list variation          how far one tested list change moves a cell (variation check), scaled for decks it did not test
  4. remainder               what is left: pilot, engine, and anything not named above
and the remainder is then compared with how far tested pilots have moved each cell.
Assumptions A1 to A8 are listed in README.md; the printout tags them where they apply (A2, A3, A4, A6, A7)."""
import csv, json, math, os, random, re, sys
from operator import itemgetter
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from loader import *  # noqa: E402,F401

rng = random.Random(29092026)
K = 45
q = lambda v, p: sorted(v)[min(len(v) - 1, max(0, int(p * (len(v) - 1) + 0.5)))]

# ---------------------------------------------------------------- A. base: kog3 against Limitless, and every pilot's 45-cell table
pairs, lim = load_limitless()
Lr = {k: (lim[k][0] + 0.5 * lim[k][2]) / sum(lim[k]) for k in pairs}
nL = {k: sum(lim[k]) for k in pairs}
RQ = [k for k in pairs if "rayquaza" in k]
AG = [k for k in pairs if "altaria_greninja" in k and "rayquaza" not in k]
PN = [k for k in pairs if k not in RQ and k not in AG]
GROUP = {k: ("rq" if k in RQ else "ag" if k in AG else "pn") for k in pairs}
GROUPS = {"rq": RQ, "ag": AG, "pn": PN}
GNAME = {"rq": "Rayquaza (9 cells)", "ag": "Altaria/Greninja (8 cells, not v Rayquaza)", "pn": "panel (28 cells)"}
cell_name = lambda k: f"{k[0]} v {k[1]}"

deals, rate, missing = {}, {}, []
for p in PILOTS:
    try:
        deals[p], _ = load_pilot(p, pairs)
        rate[p] = {k: sum(deals[p][k]) / 500 for k in pairs}
    except (FileNotFoundError, OSError) as ex:
        missing.append(p)
        print(f"NOTE: pilot {p} not loaded ({ex.__class__.__name__}: {os.path.basename(str(ex.filename))})")


def parts(p, k, L=None, S_=None):
    """(miss, miss^2, Limitless noise, simulator noise, excess) in points / points^2, tau-hat's own terms."""
    L = Lr[k] if L is None else L
    S_ = rate[p][k] if S_ is None else S_
    e = 100 * (S_ - L)
    vl = 1e4 * L * (1 - L) / nL[k]
    vs = 1e4 * S_ * (1 - S_) / 500
    return e, e * e, vl, vs, e * e - vl - vs


base = {k: parts("kog3", k) for k in pairs}
tot_e2 = sum(b[1] for b in base.values()); tot_vl = sum(b[2] for b in base.values())
tot_vs = sum(b[3] for b in base.values()); tot_exc = sum(b[4] for b in base.values())
nf = json.load(open(os.path.join(RES, "eval_power_2026-09-29", "analyst", "noise_floor.json")))["cells"]
for c in nf:
    k = tuple(c["k"].split("|"))
    assert abs(c["e"] - base[k][0]) < 0.06 and abs(c["exc"] - base[k][4]) < 0.6, (k, c["e"], base[k][0])
print("A. kog3 against Limitless, 45 development cells (points, points^2)")
print(f"   checked against eval_power_2026-09-29/analyst/noise_floor.json: all 45 cells agree")
print(f"   raw sum of squared misses {tot_e2:.0f} (mean {tot_e2 / K:.1f}, raw RMS {math.sqrt(tot_e2 / K):.2f})")
print(f"   chance floor: Limitless binomial noise {tot_vl:.0f} + simulator noise {tot_vs:.0f} = {tot_vl + tot_vs:.0f}"
      f"  = {100 * (tot_vl + tot_vs) / tot_e2:.1f}% of the raw sum")
print(f"   excess (what tau-hat calls real error squared, times 45) {tot_exc:.0f} = {100 * tot_exc / tot_e2:.1f}% of the raw sum; tau-hat {math.sqrt(tot_exc / K):.2f}")
for g in ("rq", "ag", "pn"):
    ex = sum(base[k][4] for k in GROUPS[g]); e2 = sum(base[k][1] for k in GROUPS[g])
    print(f"   {GNAME[g]:44} raw {e2:6.0f}  chance {sum(base[k][2] + base[k][3] for k in GROUPS[g]):5.0f}  excess {ex:6.0f} = {100 * ex / tot_exc:4.1f}% of all excess; group tau-hat {math.sqrt(max(0, ex / len(GROUPS[g]))):.1f}")
print(f"   pilots loaded: {', '.join(rate)}" + (f"; NOT loaded: {', '.join(missing)}" if missing else ""))

# ---------------------------------------------------------------- B. real-side instability: the two halves of the Limitless events
fz = load_frozen()
half = {}
for k in pairs:
    f = fz[k]
    w, l, t = lim[k]
    assert f["n_dev"] == sum(lim[k]) and abs(100 * f["dev"] - 100 * Lr[k]) < 0.06, k
    nh = f["n_pooled"] - f["n_dev"]
    ph = (f["pooled"] * f["n_pooled"] - f["dev"] * f["n_dev"]) / nh
    v = f["pooled"] * (1 - f["pooled"]) * (1 / f["n_dev"] + 1 / nh)
    d = f["dev"] - ph
    half[k] = dict(pd=f["dev"], nd=f["n_dev"], ph=ph, nh=nh, v=1e4 * v, d2=1e4 * d * d, z2=d * d / v)
omega2 = {}
for g in ("rq", "ag", "pn"):
    m = sum(half[k]["d2"] - half[k]["v"] for k in GROUPS[g]) / len(GROUPS[g])
    omega2[g] = max(0.0, m / 2)
boot_om = {g: [] for g in GROUPS}
for _ in range(4000):
    for g in GROUPS:
        ks = [rng.choice(GROUPS[g]) for _ in GROUPS[g]]
        m = sum(half[k]["d2"] - half[k]["v"] for k in ks) / len(ks)
        boot_om[g].append(max(0.0, m / 2))
print("\nB. real-side instability: dev half against the other half (pooled minus dev), same cells   [A2]")
print("   z^2 per cell = (dev - other)^2 / binomial variance of the difference; 1.0 is what binomial noise alone gives")
allz = [half[k]["z2"] for k in pairs]
print(f"   all 45 cells: mean z^2 {sum(allz) / K:.2f} (binomial alone expects 1.00, sd of the mean about {math.sqrt(2 / K):.2f})")
for g in ("rq", "ag", "pn"):
    zz = [half[k]["z2"] for k in GROUPS[g]]
    print(f"   {GNAME[g]:44} mean z^2 {sum(zz) / len(zz):5.2f}   extra half-variance omega^2 {omega2[g]:6.1f} pts^2 per cell "
          f"(90% {q(boot_om[g], .05):.0f} to {q(boot_om[g], .95):.0f}; sd {math.sqrt(omega2[g]):.1f} pts)")
INST = {k: omega2[GROUP[k]] for k in pairs}
tot_inst = sum(INST.values())
print(f"   allocated to cells (group value to every cell in the group): {tot_inst:.0f} pts^2 = {100 * tot_inst / tot_exc:.1f}% of the excess")
adev = sum(half[k]["pd"] * half[k]["nd"] for k in AG) / sum(half[k]["nd"] for k in AG)
aoth = sum(half[k]["ph"] * half[k]["nh"] for k in AG) / sum(half[k]["nh"] for k in AG)
print(f"   Altaria/Greninja's 8 cells pooled (match-weighted): dev {100 * adev:.1f}% ({sum(half[k]['nd'] for k in AG)} matches), other half {100 * aoth:.1f}% ({sum(half[k]['nh'] for k in AG)})")
sse_h = sum((rate['kog3'][k] - half[k]['ph']) ** 2 - half[k]['ph'] * (1 - half[k]['ph']) / half[k]['nh'] - rate['kog3'][k] * (1 - rate['kog3'][k]) / 500 for k in pairs)
print(f"   kog3's tau-hat against the OTHER half alone: {100 * math.sqrt(max(0, sse_h / K)):.2f} (against the dev half: {math.sqrt(tot_exc / K):.2f})   [descriptive only; nothing is decided from it]")

# ---------------------------------------------------------------- C. list variation: the variation check
T_ = GAUNT + "/tsv"
VERS = {"lucario": ["v-lucario_2", "v-lucario_swap1", "v-lucario_swap2"], "suicune": ["v-suicune_2", "v-suicune_swap1", "v-suicune_swap2"],
        "weezing": ["v-weezing_2", "v-weezing_swap1", "v-weezing_swap2"], "charizardy": ["l-charizardy", "v-charizardy_swap1", "v-charizardy_swap2"]}
main_old = {}   # the variation check's own main-list side: Sept 25 kp3 references (the engine the variation games were played on)
for f in ("kp3_500_worst5.jsonl", "kp3_500_rest.jsonl"):
    main_old.update(jl(RES + "/public_pricing_2026-09-25/" + f))
main_b2e = jl(RES + "/b2e_rows_2026-09-26/b2e_kp3_arch.jsonl")
main_kog = jl(KOG + "/table_kog3.jsonl")
kog_b2e_path = KOHC + "/b2e_kog3.jsonl"
main_kog_b2e = jl(kog_b2e_path) if os.path.exists(kog_b2e_path) else None


def var_rows(v, games, mains):
    rows = {int(r["pairing"]): r for r in csv.DictReader(open(f"{T_}/var_{v}.tsv", encoding="utf-8"), delimiter="\t")}
    per = {}
    for (p, i), g in games.items():
        m = mains[(p, i)]
        assert m["seed"] == g["seed"], (v, p, i)
        per.setdefault(p, []).append(100 * (g["first_deck_score"] - m["first_deck_score"]))
    out = {}
    for p, d in per.items():
        n = len(d); mean = sum(d) / n
        se = math.sqrt(sum((x - mean) ** 2 for x in d) / (n - 1) / n)
        side = rows[p]["variant_side"]
        out[p] = dict(first=mean, own=mean if side == "a" else -mean, se=se, side=side)
    return out


VAR = {}   # VAR[deck][version][pairing]
for deck, vs_ in VERS.items():
    VAR[deck] = {}
    for v in vs_:
        mains = main_b2e if deck == "charizardy" else main_old
        VAR[deck][v] = var_rows(v, jl(f"{GAUNT}/var_{v}_kp3.jsonl"), mains)
print("\nC. list variation: the variation check (kp3, three versions per deck: a second list and two single-Trainer swaps)")
print("   reproduces the README's own-side differences (deck average over its opponents, paired 95% half-width):")
for deck, vs_ in VERS.items():
    for v in vs_:
        o = VAR[deck][v]
        avg = sum(x["own"] for x in o.values()) / len(o)
        band = 1.96 * math.sqrt(sum(x["se"] ** 2 for x in o.values())) / len(o)
        print(f"     {v:20} {avg:+5.1f} +/- {band:.1f}   per cell " + " ".join(f"{o[p]['own']:+5.1f}" for p in sorted(o)))
NU = {}
print("   deck-level list swing: mean over (cell, version) of [change^2 - its paired variance], in pts^2 (then its square root)")
for deck, vs_ in VERS.items():
    al = [(x["own"], x["se"]) for v in vs_ for x in VAR[deck][v].values()]
    s2 = [(x["own"], x["se"]) for x in VAR[deck][vs_[0]].values()]
    sw = [(x["own"], x["se"]) for v in vs_[1:] for x in VAR[deck][v].values()]
    nu = lambda z: sum(a * a - s * s for a, s in z) / len(z)
    NU[deck] = max(0.0, nu(al))
    bs = sorted(nu([rng.choice(al) for _ in al]) for _ in range(4000))
    print(f"     {deck:11} all three versions {nu(al):5.1f} (rms {math.sqrt(max(0, nu(al))):.1f}; 90% over the {len(al)} cell-version changes {bs[200]:.0f} to {bs[3800]:.0f}); "
          f"second list alone {nu(s2):5.1f}; the two swaps alone {nu(sw):5.1f}; largest single change {max(abs(a) for a, _ in al):.1f}")
# second lists under kog3 (the working pilot), same deals as the kog3 table
print("   the same second lists under kog3 (the koh reading's runs; own-side deck average, and against kp3's paired change):")
KOGV = {}
for deck, v in (("lucario", "v-lucario_2"), ("suicune", "v-suicune_2"), ("weezing", "v-weezing_2"), ("charizardy", "l-charizardy")):
    mains = main_kog_b2e if deck == "charizardy" else main_kog
    if mains is None:
        print(f"     {v}: kog3 main for Charizard Y (koh cloud b2e_kog3) not available; skipped")
        continue
    o = var_rows(v, jl(f"{RES}/koh_2026-09-28/laptop_runs/var_{v}_kog3.jsonl"), mains)
    KOGV[deck] = o
    avg = sum(x["own"] for x in o.values()) / len(o)
    k3o = VAR[deck][v]
    print(f"     {v:14} kog3 own-side change {avg:+5.1f}; kp3 {sum(x['own'] for x in k3o.values()) / len(k3o):+5.1f}; per cell (kog3) " + " ".join(f"{o[p]['own']:+5.1f}" for p in sorted(o)))

# modal-list share of each deck's Limitless lists (rl/results/gauntlet_proposal_2026-09-26/README.md, section 5 and the "next two" note)
MODAL = {"lucario": 0.163, "altaria": 0.429, "sceptile": 0.709, "vespiquen": 0.296, "suicune": 0.090, "weezing": 0.158, "hydreigon": 0.583,
         "blaziken": 0.815, "rayquaza": 19 / 143, "altaria_greninja": 40 / 125, "charizardy": 0.151}
nu_bar = sum(NU.values()) / len(NU)
expo_bar = sum(1 - MODAL[d] for d in NU) / len(NU)
DECKS = PANEL + NEW
NUD, NUSRC = {}, {}
for d in DECKS:
    if d in NU:
        NUD[d], NUSRC[d] = NU[d], "measured"
    else:
        NUD[d], NUSRC[d] = nu_bar * (1 - MODAL[d]) / expo_bar, "assumed (A3)"
print(f"   A3: for a deck the check did not vary, the list swing is the four measured decks' mean ({nu_bar:.1f} pts^2) scaled by (1 - modal-list share) / {expo_bar:.2f}:")
for d in DECKS:
    print(f"     {d:17} modal list {100 * MODAL[d]:4.1f}% of its lists -> full swing {NUD[d]:5.1f} pts^2 ({NUSRC[d]})")
FACT = {"low": 0.25, "mid": 0.5, "high": 1.0}   # A4: the share of one tested list change's variance that the sim's list is off the field's mix
LFULL = {k: NUD[k[0]] + NUD[k[1]] for k in pairs}
print("   A4: the list part of a cell's miss^2 is taken as f x (sum of its two decks' full swings), f = 1/4 (low), 1/2 (mid), 1 (high)")
print(f"       totals over the 45 cells: low {FACT['low'] * sum(LFULL.values()):.0f}, mid {FACT['mid'] * sum(LFULL.values()):.0f}, high {FACT['high'] * sum(LFULL.values()):.0f} pts^2"
      f"  (= {100 * FACT['low'] * sum(LFULL.values()) / tot_exc:.1f}%, {100 * FACT['mid'] * sum(LFULL.values()) / tot_exc:.1f}%, {100 * FACT['high'] * sum(LFULL.values()) / tot_exc:.1f}% of the excess)")

# deck-level: can a tested list close the deck's own gap?   (kog3 deck average over its 7 panel opponents against Limitless dev)
print("\n   Can list choice close a deck's gap? kog3's 7-opponent average against Limitless (dev), and each tested version's shift (kp3 changes added to kog3):")
DECKGAP = {}
for deck in ("lucario", "suicune", "weezing"):
    cells = [k for k in D.PAIRS if deck in k]
    sim = sum((rate["kog3"][k] if k[0] == deck else 1 - rate["kog3"][k]) for k in cells) / len(cells)
    lm = sum((Lr[k] if k[0] == deck else 1 - Lr[k]) for k in cells) / len(cells)
    gap = 100 * (sim - lm)
    DECKGAP[deck] = gap
    shifts = {v: sum(x["own"] for x in VAR[deck][v].values()) / len(VAR[deck][v]) for v in VERS[deck]}
    txt = "; ".join(f"{v} {s:+.1f} -> gap {gap + s:+.1f}" for v, s in shifts.items())
    print(f"     {deck:9} sim {100 * sim:.1f} v Limitless {100 * lm:.1f}: gap {gap:+.1f} pts. {txt}")

# B2e: the archetype list against Dustin's file (a large list change by design)
tsv = {int(r["pairing"]): r for r in csv.DictReader(open(RES + "/b2e_card_check_2026-09-26/b2e_pairings.tsv", encoding="utf-8"), delimiter="\t")}
def b2e_cells(path):
    by = {}
    for line in open(path, encoding="utf-8"):
        g = json.loads(line)
        r = tsv[g["pairing"]]
        by.setdefault((r["held_key"], r["opponent"]), []).append(g["first_deck_score"])
    return by
B2E = {}
for pil in ("kp3", "k3"):
    arch = b2e_cells(f"{RES}/b2e_rows_2026-09-26/b2e_{pil}_arch.jsonl")
    dus = b2e_cells(f"{RES}/b2e_rows_2026-09-26/b2e_{pil}_dustin.jsonl")
    for (dk, opp), sa in arch.items():
        key = ("dustin_" + dk, opp)
        sd = dus[key]
        pa, pdx = sum(sa) / len(sa), sum(sd) / len(sd)
        va = sum((x - pa) ** 2 for x in sa) / (len(sa) - 1) / len(sa); vd = sum((x - pdx) ** 2 for x in sd) / (len(sd) - 1) / len(sd)
        B2E.setdefault(pil, {}).setdefault(dk, []).append((100 * (pa - pdx), 1e4 * (va + vd)))
print("\n   B2e: archetype list minus Dustin's file, per cell against the 8 panel decks (unpaired, 500 deals each); a large list change by design")
for pil in ("kp3", "k3"):
    tot_a = tot_n = 0; n_ = 0
    for dk, rows in B2E[pil].items():
        m = sum(d for d, _ in rows) / len(rows)
        ms = sum(d * d - v for d, v in rows) / len(rows)
        tot_a += sum(d * d - v for d, v in rows); n_ += len(rows)
        print(f"     {pil:3} {dk:14} panel-average list difference {m:+5.1f}; per-cell rms {math.sqrt(max(0, ms)):4.1f} (noise-corrected)")
    print(f"     {pil:3} all six archetypes: per-cell rms {math.sqrt(max(0, tot_a / n_)):.1f} over {n_} cells")
    rest_ = [(d, v) for dk, rows in B2E[pil].items() if dk != "hoopa_absol" for d, v in rows]
    print(f"     {pil:3} without Hoopa/Absol: per-cell rms {math.sqrt(max(0, sum(d * d - v for d, v in rest_) / len(rest_))):.1f} over {len(rest_)} cells")

# ---------------------------------------------------------------- D. pilot reach: every pilot's table, by group
PIL_ORDER = [p for p in ("k3", "kp3", "kpg3", "kog3", "kta3", "ktc3", "ktb3", "kt3", "kpf3", "kpr3", "koh3") if p in rate]
ex_p = {p: {k: parts(p, k)[4] for k in pairs} for p in PIL_ORDER}
print("\nD. pilot reach: each tested pilot's table on the 45 cells (excess = miss^2 minus both noise terms, pts^2 per cell; tau-hat in brackets)")
print(f"   {'pilot':6}{'all 45':>14}{'Rayquaza 9':>14}{'Alt/Gren 8':>14}{'panel 28':>14}   note")
NOTE = {"k3": "reference", "kp3": "Sept 26-27 base", "kpg3": "kp3 + discard-Energy credit", "kog3": "working pilot (kp3 + opening switch A + credit F)",
        "kta3": "kog + Tool cut (switch 1 alone)", "ktc3": "kog + switch 3", "ktb3": "kog + switch 2", "kt3": "kog + all three Tool switches",
        "kpf3": "kp3 + R' projection (discard-cost attacks)", "kpr3": "kp3 + readiness for the Active", "koh3": "kog + R' (kpf's projection with fixes A and B)"}
for p in PIL_ORDER:
    row = []
    for ks in (pairs, RQ, AG, PN):
        m = sum(ex_p[p][k] for k in ks) / len(ks)
        row.append(f"{m:7.1f} ({math.sqrt(max(0, m)):4.1f})")
    print(f"   {p:6}" + "".join(f"{r:>14}" for r in row) + f"   {NOTE.get(p, '')}")
KOGB = ["koh3", "kt3", "kta3", "ktb3", "ktc3"]   # pilots built on kog: comparable with kog3 in every cell
OTHERB = ["kpf3", "kpr3"]                        # built on kp3 (no opening switch A, no credit F): not comparable in Altaria's cells   [A6]
KOGB = [p for p in KOGB if p in rate]; OTHERB = [p for p in OTHERB if p in rate]


def env_set(k):
    return KOGB if "altaria" in k else KOGB + OTHERB


gain_koh = {k: ex_p["kog3"][k] - ex_p["koh3"][k] for k in pairs} if "koh3" in rate else None
best, envgain = {}, {}
for k in pairs:
    cand = env_set(k)
    b = min(cand, key=lambda p: ex_p[p][k])
    best[k] = b
    envgain[k] = max(0.0, ex_p["kog3"][k] - ex_p[b][k])

# ---------------------------------------------------------------- E. the split, cell by cell
cells_out = []
for k in pairs:
    e, e2, vl, vs, exc = base[k]
    lf = LFULL[k]
    row = dict(cell=cell_name(k), group=GROUP[k], nL=nL[k], L=100 * Lr[k], kog3=100 * rate["kog3"][k], miss=e, miss2=e2, lim_noise=vl, sim_noise=vs,
               chance=vl + vs, excess=exc, inst=INST[k], list_low=FACT["low"] * lf, list_mid=FACT["mid"] * lf, list_high=FACT["high"] * lf,
               z2_halves=half[k]["z2"], other_half=100 * half[k]["ph"], n_other=half[k]["nh"])
    row["rem_mid"] = exc - INST[k] - row["list_mid"]
    row["koh3"] = 100 * rate["koh3"][k] if gain_koh else float("nan")
    row["koh3_gain"] = gain_koh[k] if gain_koh else float("nan")
    row["best_pilot"] = best[k]; row["best_rate"] = 100 * rate[best[k]][k]; row["env_gain"] = envgain[k]
    pos = max(row["rem_mid"], 0.0)
    row["reach_koh"] = min(max(row["koh3_gain"], 0.0), pos) if gain_koh else float("nan")
    row["reach_env"] = min(envgain[k], pos)
    row["left_env"] = row["rem_mid"] - row["reach_env"]
    # list swing measured in this cell (kp3 own-side changes of the varied deck(s)), and the best tested change toward Limitless
    ms_, bt = [], None
    for deck in ("lucario", "suicune", "weezing"):
        if deck in k:
            p_ = D.PAIRS.index(k) if k in D.PAIRS else None
            if p_ is None:
                continue
            ch = [VAR[deck][v][p_]["first"] for v in VERS[deck] if p_ in VAR[deck][v]]
            ms_ += [VAR[deck][v][p_]["own"] for v in VERS[deck] if p_ in VAR[deck][v]]
            for x in ch:
                red = abs(e) - abs(e + x)
                bt = red if bt is None else max(bt, red)
    row["list_meas_rms"] = math.sqrt(sum(x * x for x in ms_) / len(ms_)) if ms_ else float("nan")
    row["list_best_toward"] = bt if bt is not None else float("nan")
    cells_out.append(row)

# ---------------------------------------------------------------- F. totals, with intervals from one joint bootstrap
B = 600
sums = {n: [] for n in ("exc", "rem_mid", "reach_koh", "reach_env", "left_env", "koh_net", "rq_net")}
pil_b = ["kog3"] + KOGB + OTHERB
exc_cell_b = {k: [] for k in pairs}
grp_b = {g: {"exc": [], "reach_koh": [], "reach_env": []} for g in GROUPS}
for _ in range(B):
    S_star = {p: {} for p in pil_b}
    Lstar = {}
    for k in pairs:
        idx = [rng.randrange(500) for _ in range(500)]
        ig = itemgetter(*idx)
        for p in pil_b:
            S_star[p][k] = sum(ig(deals[p][k])) / 500
        Lstar[k] = rng.binomialvariate(nL[k], Lr[k]) / nL[k]
    exs = {p: {k: parts(p, k, Lstar[k], S_star[p][k])[4] for k in pairs} for p in pil_b}
    tot = {"exc": 0, "rem_mid": 0, "reach_koh": 0, "reach_env": 0, "left_env": 0, "koh_net": 0, "rq_net": 0}
    gt = {g: {"exc": 0, "reach_koh": 0, "reach_env": 0} for g in GROUPS}
    for k in pairs:
        raw0 = exs["kog3"][k]
        # a parametric bootstrap that redraws Limitless around its own observed value adds the chance floor a second time to
        # (S - L)^2 while the subtracted noise terms stay one copy; take the expected copy back out so the draws centre on the excess
        e0 = raw0 - (base[k][2] + base[k][3])
        exc_cell_b[k].append(e0)
        rem = e0 - INST[k] - FACT["mid"] * LFULL[k]
        gk = raw0 - exs["koh3"][k] if gain_koh else 0.0   # a paired difference: the double count cancels
        ge = max(0.0, raw0 - min(exs[p][k] for p in env_set(k)))
        if GROUP[k] == "rq":
            tot["rq_net"] += gk
        rk = min(max(gk, 0.0), max(rem, 0.0)); re_ = min(ge, max(rem, 0.0))
        tot["exc"] += e0; tot["rem_mid"] += rem; tot["reach_koh"] += rk; tot["reach_env"] += re_; tot["left_env"] += rem - re_; tot["koh_net"] += gk
        g = GROUP[k]
        gt[g]["exc"] += e0; gt[g]["reach_koh"] += rk; gt[g]["reach_env"] += re_
    for n in tot:
        sums[n].append(tot[n])
    for g in GROUPS:
        for n in gt[g]:
            grp_b[g][n].append(gt[g][n])
for row, k in zip(cells_out, pairs):
    row["exc_lo"], row["exc_hi"] = q(exc_cell_b[k], .05), q(exc_cell_b[k], .95)

T = lambda name: (sum(r[name] for r in cells_out))
tot_list = {n: sum(r[f"list_{n}"] for r in cells_out) for n in FACT}
tot_rem = T("rem_mid"); tot_reach_koh = T("reach_koh"); tot_reach_env = T("reach_env"); tot_left = T("left_env")
ci = lambda name, scale=1.0: f"90% {q(sums[name], .05) * scale:.0f} to {q(sums[name], .95) * scale:.0f}"
print("\nE/F. THE SPLIT, totals over the 45 cells (pts^2; share of the excess in brackets). Intervals are 5th to 95th percentile of a joint bootstrap")
print(f"   (Limitless cells redrawn from Binomial, simulator resampled by deal, every pilot on the same deals; {B} draws), except where marked as an assumption range.")
print(f"   raw squared miss                          {tot_e2:7.0f}")
print(f"   1 chance floor (Limitless + simulator)     {tot_vl + tot_vs:7.0f}   = {100 * (tot_vl + tot_vs) / tot_e2:.0f}% of the raw sum")
print(f"   excess = tau-hat^2 x 45                    {tot_exc:7.0f}   (bootstrap {ci('exc')}; tau-hat {math.sqrt(tot_exc / K):.2f}, 90% {math.sqrt(q(sums['exc'], .05) / K):.1f} to {math.sqrt(q(sums['exc'], .95) / K):.1f})")
print(f"   2 real-side instability (halves)   [A2]   {tot_inst:7.0f}   ({100 * tot_inst / tot_exc:.0f}%) ; bootstrap over cells: " +
      ", ".join(f"{g} {sum(1 for _ in GROUPS[g]) * q(boot_om[g], .05):.0f}-{sum(1 for _ in GROUPS[g]) * q(boot_om[g], .95):.0f}" for g in GROUPS))
print(f"   3 list variation   [A3, A4]  low {tot_list['low']:.0f}, mid {tot_list['mid']:.0f}, high {tot_list['high']:.0f}   ({100 * tot_list['low'] / tot_exc:.0f}% / {100 * tot_list['mid'] / tot_exc:.0f}% / {100 * tot_list['high'] / tot_exc:.0f}%)  (assumption range, not a statistical interval)")
print(f"   4 remainder (mid list)                     {tot_rem:7.0f}   ({100 * tot_rem / tot_exc:.0f}%)   {ci('rem_mid')}")
print(f"       of which moved by a tested pilot:")
print(f"         koh3 (the whole pilot built on kog; net of what it made worse, all 45 cells): {T('koh3_gain'):7.0f} = {100 * T('koh3_gain') / tot_exc:.0f}% of the excess ({ci('koh_net')})")
print(f"         koh3, cells where it helped, capped at the cell's remainder:                 {tot_reach_koh:7.0f} ({100 * tot_reach_koh / tot_exc:.0f}% of the excess, {100 * tot_reach_koh / tot_rem:.0f}% of the remainder; {ci('reach_koh')})")
print(f"         best tested pilot per cell (upper bound; includes selection luck  [A6]):      {tot_reach_env:7.0f} ({100 * tot_reach_env / tot_exc:.0f}% of the excess, {100 * tot_reach_env / tot_rem:.0f}% of the remainder; {ci('reach_env')})")
print(f"       left where no tested pilot moved it (against the best-pilot bound):            {tot_left:7.0f} ({100 * tot_left / tot_exc:.0f}% of the excess, {100 * tot_left / tot_rem:.0f}% of the remainder; {ci('left_env')})")
print("   by group (pts^2; share of the group's excess in brackets):")
print(f"   {'group':44}{'excess':>8}{'chance':>8}{'instab.':>8}{'list mid':>9}{'remainder':>10}{'koh3 reach':>11}{'best reach':>11}{'left':>8}")
for g in ("rq", "ag", "pn"):
    rs = [r for r in cells_out if r["group"] == g]
    exg = sum(r["excess"] for r in rs)
    f = lambda name: sum(r[name] for r in rs)
    print(f"   {GNAME[g]:44}{exg:8.0f}{f('chance'):8.0f}{f('inst'):8.0f}{f('list_mid'):9.0f}{f('rem_mid'):10.0f}{f('reach_koh'):11.0f}{f('reach_env'):11.0f}{f('left_env'):8.0f}"
          f"   koh {q(grp_b[g]['reach_koh'], .05):.0f}-{q(grp_b[g]['reach_koh'], .95):.0f}; best {q(grp_b[g]['reach_env'], .05):.0f}-{q(grp_b[g]['reach_env'], .95):.0f}")

# tau-hat scale
mean = lambda x: x / K
print("\n   The same, on tau-hat's scale (square root of the per-cell mean; points):")
print(f"   now (kog3) {math.sqrt(mean(tot_exc)):.2f}")
fl = {n: math.sqrt(mean(tot_inst + tot_list[n])) for n in FACT}
print(f"   a perfect pilot and engine on these cells and lists would still read about {fl['low']:.1f} (low), {fl['mid']:.1f} (mid), {fl['high']:.1f} (high): instability + list variation only   [A2, A4]")
print(f"     of which instability alone {math.sqrt(mean(tot_inst)):.1f}, list variation alone {math.sqrt(mean(tot_list['low'])):.1f} / {math.sqrt(mean(tot_list['mid'])):.1f} / {math.sqrt(mean(tot_list['high'])):.1f}")
print(f"   koh3, as tested (whole pilot): {math.sqrt(mean(sum(ex_p['koh3'].values()))):.2f}" if gain_koh else "")
fl_data = math.sqrt(mean(tot_inst / 2 + tot_list['mid'])); fl_both = math.sqrt(mean(tot_inst / 2 + tot_list['low']))
print(f"   what would lower that floor (arithmetic on the same assumptions): folding the other half into the dev data halves the instability term -> floor {fl_data:.1f} (mid list);"
      f" and if list handling also cut the list term to the low value -> {fl_both:.1f}")
# the three tiers, in the order the evidence supports
rem_g = {g: sum(r["rem_mid"] for r in cells_out if r["group"] == g) for g in GROUPS}
reach_rq = sum(r["reach_koh"] for r in cells_out if r["group"] == "rq")
svv = next(r for r in cells_out if r["cell"] == "sceptile v vespiquen")
t1 = reach_rq; t2a = tot_inst; t2b = tot_list["mid"]
t3 = tot_exc - t1 - t2a - t2b
print("\n   THE THREE TIERS (pts^2; % of the excess):")
print(f"   1 a tested pilot fix reaches it (Rayquaza's 9 cells, koh3, capped at each cell's remainder): {t1:6.0f}  {100 * t1 / tot_exc:4.1f}%   (koh3 uncapped gain in those cells {sum(gain_koh[k] for k in RQ):.0f}; group bootstrap 90% {q(grp_b['rq']['reach_koh'], .05):.0f} to {q(grp_b['rq']['reach_koh'], .95):.0f} = {100 * q(grp_b['rq']['reach_koh'], .05) / tot_exc:.0f}% to {100 * q(grp_b['rq']['reach_koh'], .95) / tot_exc:.0f}%)")
print(f"   2 no pilot can touch it: the target moving (halves disagree) {t2a:6.0f}  {100 * t2a / tot_exc:4.1f}%   (Altaria/Greninja {INST[AG[0]] * len(AG):.0f}, Rayquaza {INST[RQ[0]] * len(RQ):.0f}, panel 0)")
print(f"                            list variation, mid                      {t2b:6.0f}  {100 * t2b / tot_exc:4.1f}%   (low {tot_list['low']:.0f} = {100 * tot_list['low'] / tot_exc:.1f}%, high {tot_list['high']:.0f} = {100 * tot_list['high'] / tot_exc:.1f}%)")
print(f"   3 not reached by any tested pilot and not explained by 2:        {t3:6.0f}  {100 * t3 / tot_exc:4.1f}%")
print(f"       Sceptile v Vespiquen {svv['rem_mid']:.0f}; Altaria/Greninja's remainder {rem_g['ag']:.0f}; the other 27 panel cells {rem_g['pn'] - svv['rem_mid']:.0f}; Rayquaza's leftover {rem_g['rq'] - reach_rq:.0f}")
six = [r for r in cells_out if r["exc_lo"] > 0]
print(f"   the {len(six)} cells whose own 90% excess interval stays above zero ({', '.join(r['cell'] for r in six)}) hold {sum(r['excess'] for r in six):.0f} = {100 * sum(r['excess'] for r in six) / tot_exc:.0f}% of the excess")
if gain_koh:
    non_rq = [k for k in pairs if k not in RQ]
    print(f"   koh3 outside Rayquaza's cells (36 cells): helped {sum(max(0, gain_koh[k]) for k in non_rq):+.0f}, hurt {sum(min(0, gain_koh[k]) for k in non_rq):+.0f}, net {sum(gain_koh[k] for k in non_rq):+.0f}")
bg = {}
for g in ("rq", "ag", "pn"):
    ex_g = {p: sum(ex_p[p][k] for k in GROUPS[g]) for p in PIL_ORDER if p not in ("k3", "kp3", "kpg3")}
    bp = min(ex_g, key=ex_g.get)
    bg[g] = (bp, ex_g[bp])
hy = sum(v[1] for v in bg.values())
print("   optimistic pilot-only bound (each group taken from the best tested whole pilot, ignoring what that pilot does to other groups): " +
      "; ".join(f"{g} {bg[g][0]} {bg[g][1]:.0f}" for g in bg) + f" -> total {hy:.0f}, tau-hat {math.sqrt(mean(hy)):.2f}")
after = tot_exc - tot_reach_env
print(f"   excess left after the best-pilot bound, cell by cell: {after:.0f} -> tau-hat {math.sqrt(max(0, mean(after))):.2f}")
after_k = tot_exc - T('koh3_gain')
print(f"   excess left after koh3's net reach: {after_k:.0f} -> tau-hat {math.sqrt(max(0, mean(after_k))):.2f}")
rq_net = sum(gain_koh[k] for k in RQ) if gain_koh else 0.0
after_r = tot_exc - rq_net
print(f"   koh3's Rayquaza cells with kog3 everywhere else (the pilot's demonstrated lever without its cost elsewhere): gain {rq_net:.0f} ({ci('rq_net')}) -> excess {after_r:.0f}, tau-hat {math.sqrt(max(0, mean(after_r))):.2f}")
print("   tau-hat by group against the dev half and against the other half (kog3; descriptive only):")
for g in ("rq", "ag", "pn"):
    ks = GROUPS[g]
    dv = sum(base[k][4] for k in ks) / len(ks)
    ot = sum((rate['kog3'][k] - half[k]['ph']) ** 2 * 1e4 - 1e4 * half[k]['ph'] * (1 - half[k]['ph']) / half[k]['nh'] - base[k][3] for k in ks) / len(ks)
    print(f"     {GNAME[g]:44} dev half {math.sqrt(max(0, dv)):5.1f}   other half {math.sqrt(max(0, ot)):5.1f}")

# ---------------------------------------------------------------- G. top 15 cells and the CSV
top = sorted(cells_out, key=lambda r: -r["miss2"])
print("\nG. TOP 15 CELLS BY SQUARED MISS (kog3 - Limitless, dev half); every column is pts^2 unless stated")
hdr = f"{'cell':32}{'nL':>4}{'kog3':>6}{'Lim':>6}{'miss':>7}{'miss^2':>8}{'chance':>7}{'instab':>7}{'list':>10}{'remaind':>8}{'koh3':>6}{'koh gain':>9}{'best':>6}{'best gain':>10}{'left':>7}"
print(hdr)
for r in top[:15]:
    print(f"{r['cell']:32}{r['nL']:4d}{r['kog3']:6.1f}{r['L']:6.1f}{r['miss']:+7.1f}{r['miss2']:8.0f}{r['chance']:7.0f}{r['inst']:7.0f}"
          f"{r['list_low']:4.0f}-{r['list_high']:<3.0f}{r['rem_mid']:8.0f}{r['koh3']:6.1f}{r['koh3_gain']:9.0f}{r['best_rate']:6.1f}{r['env_gain']:10.0f}{r['left_env']:7.0f}")
tt = top[:15]
print(f"{'top 15 together':32}{'':4}{'':6}{'':6}{'':7}{sum(r['miss2'] for r in tt):8.0f}{sum(r['chance'] for r in tt):7.0f}{sum(r['inst'] for r in tt):7.0f}"
      f"{sum(r['list_low'] for r in tt):4.0f}-{sum(r['list_high'] for r in tt):<3.0f}{sum(r['rem_mid'] for r in tt):8.0f}{'':6}{sum(r['koh3_gain'] for r in tt):9.0f}{'':6}{sum(r['env_gain'] for r in tt):10.0f}{sum(r['left_env'] for r in tt):7.0f}")
print(f"   the top 15 hold {100 * sum(r['miss2'] for r in tt) / tot_e2:.0f}% of the raw sum and {100 * sum(r['excess'] for r in tt) / tot_exc:.0f}% of the excess")
print("   extra columns per cell (90% interval of the cell's excess; other-half rate; halves z^2; measured list swing; best tested list change toward Limitless):")
nz = lambda x, fmt: "-" if x != x else format(x, fmt)
for r in top[:15]:
    print(f"   {r['cell']:32} excess {r['excess']:6.0f} (90% {r['exc_lo']:.0f} to {r['exc_hi']:.0f}); best pilot {r['best_pilot']}; other half {r['other_half']:.1f} (n {r['n_other']}), z^2 {r['z2_halves']:.1f}; "
          f"list swing measured {nz(r['list_meas_rms'], '.1f')} pts; best tested list moves the miss by {nz(r['list_best_toward'], '+.1f')}")

thin = [r for r in cells_out if r["nL"] < 25]
print(f"   thin cells (fewer than 25 real matches): {len(thin)} cells; raw miss^2 {sum(r['miss2'] for r in thin):.0f} of which chance {sum(r['chance'] for r in thin):.0f} ({100 * sum(r['chance'] for r in thin) / sum(r['miss2'] for r in thin):.0f}%); "
      f"excess {sum(r['excess'] for r in thin):.0f}; cells whose own 90% excess interval includes zero {sum(1 for r in thin if r['exc_lo'] <= 0)}")
print(f"   all 45: cells whose own 90% excess interval includes zero {sum(1 for r in cells_out if r['exc_lo'] <= 0)}; of the top 15 by squared miss {sum(1 for r in top[:15] if r['exc_lo'] <= 0)}")
sv = next(r for r in cells_out if r["cell"] == "sceptile v vespiquen")
print(f"   Sceptile v Vespiquen: kog3 {sv['kog3']:.1f}, Limitless dev {sv['L']:.1f} (n {sv['nL']}), other half {sv['other_half']:.1f} (n {sv['n_other']}); no tested pilot moved it: " +
      ", ".join(f"{p} {100 * rate[p][('sceptile', 'vespiquen')]:.1f}" for p in PIL_ORDER))

FIELDS = ["cell", "group", "nL", "L", "kog3", "miss", "miss2", "lim_noise", "sim_noise", "chance", "excess", "exc_lo", "exc_hi", "inst", "list_low", "list_mid", "list_high",
          "rem_mid", "koh3", "koh3_gain", "best_pilot", "best_rate", "env_gain", "reach_koh", "reach_env", "left_env", "z2_halves", "other_half", "n_other",
          "list_meas_rms", "list_best_toward"]
with open(os.path.join(HERE, "cells.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS)
    w.writeheader()
    for r in sorted(cells_out, key=lambda r: -r["miss2"]):
        w.writerow({k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items() if k in FIELDS})
print("\n   cells.csv written (all 45 cells, sorted by squared miss)")

# ---------------------------------------------------------------- H. other evidence on the pilot's reach and the target: deep search, option B, skill (B6), koh's cost
print("\nH. other evidence")
ds = open(RES + "/deep_search_table/STATUS.txt", encoding="utf-8").read().splitlines()
rows_ = []
for line in ds:
    m = re.match(r"\s*(\w+) v (\w+)\s+k3\s+([\d.]+) \| k4\s+([\d.]+) \| k5\s+([\d.]+) \| k6\s+([\d.]+) \| Limitless\s+([\d.]+) ± ([\d.]+) \(n (\d+)\)", line)
    if m:
        rows_.append((m.group(1), m.group(2), *[float(m.group(i)) for i in range(3, 8)], int(m.group(9))))
assert len(rows_) == 28
print("   deeper search (k4/k5/k6 on both sides; the Sept 23 table, 28 cells, old Limitless pull, 1000 deals): change from k3, points")
for name, col in (("k4", 3), ("k5", 4), ("k6", 5)):
    ch = [r[2 + col - 2] - r[2] for r in rows_]
    mse3 = sum((r[2] - r[6]) ** 2 for r in rows_) / 28; mse = sum((r[col + 0] - r[6]) ** 2 for r in rows_) / 28
    tow = sum(1 for r in rows_ if abs(r[col] - r[6]) < abs(r[2] - r[6]) - 1)
    away = sum(1 for r in rows_ if abs(r[col] - r[6]) > abs(r[2] - r[6]) + 1)
    print(f"     {name}: rms change {math.sqrt(sum(c * c for c in ch) / 28):.1f}, cells moved 5+ points {sum(1 for c in ch if abs(c) >= 5)}, toward Limitless by 1+ {tow}, away by 1+ {away}; raw MSE v Limitless {mse3:.0f} (k3) -> {mse:.0f}")
sv = next(r for r in rows_ if r[0] == "sceptile" and r[1] == "vespiquen")
print(f"     Sceptile v Vespiquen: k3 {sv[2]:.1f}, k4 {sv[3]:.1f}, k5 {sv[4]:.1f}, k6 {sv[5]:.1f}; Limitless {sv[6]:.1f}")
ob_before = {"altaria v blaziken": (56.0, 58.0, 74.2), "altaria v lucario": (56.6, 58.2, 71.9), "blaziken v sceptile": (59.6, 64.1, 82.8),
             "hydreigon v lucario": (30.6, 44.7, 54.4), "sceptile v vespiquen": (66.6, 62.4, 33.1)}
b0 = sum((L_ - a) ** 2 for a, b, L_ in ob_before.values()); b1 = sum((L_ - b) ** 2 for a, b, L_ in ob_before.values())
print(f"   option B (b3o3n1: guesses the hand and searches the reply) v k3, five cells, Sept 24 table and old Limitless: squared miss {b0:.0f} -> {b1:.0f} ({100 * (b0 - b1) / b0:.0f}% less);"
      f" Hydreigon v Lucario alone {(54.4 - 30.6) ** 2:.0f} -> {(54.4 - 44.7) ** 2:.0f}")
print(f"     per cell change: " + ", ".join(f"{c} {b - a:+.1f}" for c, (a, b, _) in ob_before.items()))

# B6 extension: the same skill proxy on the two new decks' matches (development events only)
sk = json.load(open(RES + "/limitless_skill_model_2026-09-25/model_summary.json"))
beta, blo, bhi = sk["beta"], sk["beta_ci95"][0], sk["beta_ci95"][1]
R6 = RES + "/limitless_skill_model_2026-09-25/"
skills = {}
for r in csv.DictReader(open(R6 + "development_player_skills.csv", encoding="utf-8")):
    skills[(r["event_id"], r["player"])] = float(r["skill"])
dn = {"Mega Altaria ex Greninja": "altaria_greninja", "Dragonair Mega Rayquaza ex": "rayquaza"}
acc = {v: [0, 0.0, 0.0] for v in dn.values()}
byp = {v: {} for v in dn.values()}
for r in csv.DictReader(open(R6 + "development_matches.csv", encoding="utf-8")):
    if not r["player1"] or not r["player2"] or r["winner"] == "-1":
        continue
    for side, other in (("1", "2"), ("2", "1")):
        name = r[f"deck{side}_name"]
        if name in dn and r[f"archetype{other}"] in PANEL:
            a = acc[dn[name]]
            a[0] += 1
            a[1] += skills.get((r["event_id"], r[f"player{side}"]), 0.0) - skills.get((r["event_id"], r[f"player{other}"]), 0.0)
            sc_ = 0.5 if r["winner"] == "0" else (1.0 if r["winner"] == r[f"player{side}"] else 0.0)
            pp_ = byp[dn[name]].setdefault(r[f"player{side}"], [0, 0.0])
            pp_[0] += 1; pp_[1] += sc_
print(f"   B6 skill proxy applied to the new decks (development matches against the 8 panel decks; B6's own beta {beta:.2f}, 95% {blo:.2f} to {bhi:.2f}; score change = 100 x 0.25 x beta x mean skill difference):")
for d, a in acc.items():
    ms = a[1] / a[0]
    print(f"     {d:17} {a[0]} matches, mean skill difference {ms:+.3f} -> {100 * .25 * beta * ms:+.2f} points (range {100 * .25 * blo * ms:+.2f} to {100 * .25 * bhi * ms:+.2f})")
    top3 = sorted(byp[d].items(), key=lambda kv: -kv[1][0])[:3]
    rest_n = sum(v[0] for p_, v in byp[d].items() if p_ not in dict(top3)); rest_s = sum(v[1] for p_, v in byp[d].items() if p_ not in dict(top3))
    all_s = sum(v[1] for v in byp[d].values())
    print(f"       {len(byp[d])} players; the three busiest play {sum(v[0] for _, v in top3)} of the {a[0]} matches ({100 * sum(v[0] for _, v in top3) / a[0]:.0f}%); "
          f"score {100 * all_s / a[0]:.1f}% with them, {100 * rest_s / rest_n:.1f}% without")

# how far past candidates moved cells (paired by deal against their own base)
print("   how far tested pilots moved the cells, against their own base (points per cell; delta-MSE per cell = mean over cells of new miss^2 minus base miss^2):")
BASEOF = {"kpf3": "kp3", "kpr3": "kp3", "kpg3": "kp3", "kog3": "kp3", "koh3": "kog3", "kt3": "kog3", "kta3": "kog3", "ktb3": "kog3", "ktc3": "kog3"}
for p, bp in BASEOF.items():
    if p not in rate or bp not in rate:
        continue
    mv = [100 * (rate[p][k] - rate[bp][k]) for k in pairs]
    dm = sum((100 * (rate[p][k] - Lr[k])) ** 2 - (100 * (rate[bp][k] - Lr[k])) ** 2 for k in pairs) / K
    print(f"     {p:5} v {bp:5}: cells moved by more than 5 points {sum(1 for m in mv if abs(m) > 5):2d} of 45, largest {max(abs(m) for m in mv):5.1f}, rms {math.sqrt(sum(m * m for m in mv) / K):4.1f}, cells not moved at all {sum(1 for m in mv if m == 0):2d}, delta-MSE {dm:+6.1f}")

# BO1 / BO3: the simulator plays single games; a third of the real matches are best-of-three   [A7]
NAMEMAP = {"Mega Altaria ex Greninja": "altaria_greninja", "Dragonair Mega Rayquaza ex": "rayquaza"}
labf = lambda r, s: NAMEMAP.get(r[f"deck{s}_name"]) or r[f"archetype{s}"]
b3 = {k: [0, 0] for k in pairs}
for r in csv.DictReader(open(R6 + "development_matches.csv", encoding="utf-8")):
    if not r["player1"] or not r["player2"] or r["winner"] == "-1":
        continue
    a_, b_ = labf(r, "1"), labf(r, "2")
    for k in ((a_, b_), (b_, a_)):
        if k in b3 and a_ != b_:
            b3[k][0] += 1
            b3[k][1] += 1 if r["mode"] == "BO3" else 0
            break
ser = lambda p: p * p * (3 - 2 * p)
fmt_pts2 = 0.0; fmt_rows = []
for k in pairs:
    x = b3[k][1] / b3[k][0]
    s_ = rate["kog3"][k]
    st = 100 * x * (ser(s_) - s_)
    fmt_pts2 += st * st
    fmt_rows.append((st, k, x))
print(f"   A7: format. {100 * sum(v[1] for v in b3.values()) / sum(v[0] for v in b3.values()):.0f}% of the development matches are best-of-three (BO3), the rest BO1; the simulator plays single games."
      f" If a series were three independent games at the simulator's rate, real cells would sit {math.sqrt(fmt_pts2 / K):.1f} points (rms) from the simulator's;"
      f" allowance {fmt_pts2:.0f} pts^2 = {100 * fmt_pts2 / tot_exc:.1f}% of the excess (not carved out of the split above).")
fmt_rows.sort(key=lambda t: -abs(t[0]))
print("     largest: " + ", ".join(f"{cell_name(k)} {s:+.1f} (BO3 share {100 * x:.0f}%)" for s, k, x in fmt_rows[:4]))

# what koh3 did to the cells it made worse
if gain_koh:
    worse = sorted(((gain_koh[k], k) for k in pairs))[:6]
    print("   koh3's biggest losses against kog3 (excess change, pts^2, negative = worse): " + "; ".join(f"{cell_name(k)} {g:+.0f}" for g, k in worse))
    for g in GROUPS:
        gg = sum(gain_koh[k] for k in GROUPS[g]); hp = sum(max(0, gain_koh[k]) for k in GROUPS[g]); ls = sum(min(0, gain_koh[k]) for k in GROUPS[g])
        print(f"     {GNAME[g]:44} net {gg:+6.0f} = helped {hp:+6.0f} and hurt {ls:+6.0f}")
