"""koh's reading, steps 5 and 6 of kph's registration (../../kph_2026-09-27/REGISTRATION.md, with amendments 1-3),
on the base kog3 at the official engine. The route is the ordinary adoption rule (footprint 93.44%, d3664e3).
  5. The 45 cells: score45.py --rules v2, kog3 (current) against koh3 (new), with koh3's mixed rows: paired dMSE with
     the whole 95% interval below zero; vetoes only through mixed rows (own side worse beyond paired noise), never on a
     cell whose band is wider than about +-15. The by-event interval is printed beside (standing column).
  6. Before any verdict is final:
     - B2e's held-out archetypes (pairings 0-47): one moving more than 2 points further from its Limitless pooled
       equal-weight average (kpg's heldout_check rule) is a veto, counted through mixed rows (then to be run).
       Dustin's files (48-95) reported beside.
     - The Scizor row (amendment 2): veto if Scizor's own-side average over its 8 rows falls by more than 2 points and
       its paired 95% interval (1.96 x sqrt(sum of per-cell variances of the mean difference) / 8) lies wholly below
       zero; own side = koh3 on Scizor, kog3 on the panel, against kog3 on both. The other direction reported.
     - The second lists (amendment 2): veto if the list's opponent average under koh3 ends more than 2 points further
       from its archetype's figure than under kog3, counted only when the list's own side in the mixed rows is worse
       beyond the variation check's paired 95% interval. Figures: the development half's average over the same
       opponents for Lucario, Suicune and Weezing (scoreboard v2/v3's cells); for Charizard Y, B2e's held-out pooled
       figure for charizardy_entei.
  Amendment 4 (Dustin, Sept 28 evening: "coverage rows count for the mixed-row veto and are reported for accuracy")
  supersedes the two-part tests above: Scizor's and the second lists' accuracy is reported only; for them and for B2e's
  held-out decks, the own side in the mixed rows worse beyond paired noise (the 95% interval wholly below zero) is a
  veto. B2e's "more than 2 further" stands; without own-side harm it is an investigation item (rule v2). B2e's rows
  are the laptop's (laptop_runs/b2e_koh3, cross-checked game for game against the cloud's copy when both exist); its
  mixed rows are laptop_runs/mixed_b2e_koh3_first (koh3 on the held deck, kog3 on the panel), 48-95 reported.
Usage: python3 read_koh.py <dir with the cloud's koh files> > READING_numbers.txt"""
import csv, json, math, os, subprocess, sys
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.abspath(os.path.join(HERE, "..", ".."))
CLOUD = sys.argv[1]; RUNS = os.path.join(HERE, "..", "laptop_runs"); KOG = os.path.join(RES, "kog_composition_2026-09-27")
K = os.path.join(RES, "kpf_2026-09-26", "reading"); B2E = os.path.join(RES, "b2e_card_check_2026-09-26")
T = os.path.join(RES, "gauntlet_runs_2026-09-26", "tsv")
load = lambda p: {(g["pairing"], g["i"]): g for g in map(json.loads, open(p, encoding="utf-8"))}

# 5. The 45 cells.
cmd = [sys.executable, os.path.join(K, "score45.py"), "--rules", "v2",
       "--old-games", os.path.join(KOG, "table_kog3.jsonl"), os.path.join(KOG, "new17_kog3.jsonl"),
       "--new-games", os.path.join(CLOUD, "table_koh3.jsonl"), os.path.join(CLOUD, "new17_koh3.jsonl"),
       "--old", "kog3", "--new", "koh3", "--mixed"] + [os.path.join(CLOUD, f"mixed_{s}_koh3_{d}.jsonl")
                                                     for s in ("table", "new17") for d in ("first", "second")]
P45 = os.path.join(HERE, "score45_koh3_vs_kog3.txt")
if os.environ.get("KOH_REUSE_45"):
    # The 45 cells' inputs are unchanged since the committed page (087528f): reuse it rather than re-score (Sept 29,
    # to put B2e's read ahead of a slow re-score under load).
    stdout, tag = open(P45, encoding="utf-8").read(), ", reused: the committed page, inputs unchanged"
else:
    out = subprocess.run(cmd, capture_output=True, text=True, cwd=K)
    open(P45, "w", encoding="utf-8").write(out.stdout + out.stderr)
    if out.returncode:
        sys.exit(f"score45.py FAILED (exit {out.returncode}); nothing read:\n{out.stderr[-600:]}")
    stdout, tag = out.stdout, ""
print(f"5. The 45 cells, koh3 against kog3, rules v2 with koh3's mixed rows (score45_koh3_vs_kog3.txt{tag}):")
for line in stdout.splitlines():
    if any(t in line for t in ("real error ", "dMSE", "cell veto", "deck veto", "ADOPTION", "COUNTS:", "AWAITS",
                               "never counts:", "investigation item")):
        if "PASS (a)" not in line and not line.startswith("Veto rule"):
            print("   " + line.strip()[:400])

# 6a. B2e's held-out archetypes.
tsv = {int(r["pairing"]): r for r in csv.DictReader(open(os.path.join(B2E, "b2e_pairings.tsv"), encoding="utf-8"), delimiter="\t")}
lim = defaultdict(dict)
for r in csv.DictReader(open(os.path.join(B2E, "limitless_cells.csv"), encoding="utf-8")):
    if int(r["n"]):
        lim[r["dataset"]][(r["archetype"], r["opponent"])] = float(r["score_pct"])
names = sorted({k for k, _ in lim["pooled"]})


def panel(path):
    by = defaultdict(list)
    for g in map(json.loads, open(path, encoding="utf-8")):
        r = tsv[g["pairing"]]
        by[(r["block"], r["held_key"], r["opponent"])].append(g["first_deck_score"])
    res = defaultdict(dict)
    for (block, k, o), s in by.items():
        res[(block, k)][o] = 100 * sum(s) / len(s)
    return res


print("\n6a. B2e's held-out archetypes (panel average, equal-weight over 8; Limitless pooled):")
bk, bc = os.path.join(RUNS, "b2e_koh3.jsonl"), os.path.join(CLOUD, "b2e_koh3.jsonl")
if not os.path.exists(bk):
    bk = bc
FURTHER = {}
if not os.path.exists(bk):
    print("   b2e_koh3.jsonl not in yet")
else:
    print(f"   rows: {os.path.relpath(bk, HERE)}")
    if bk != bc and os.path.exists(bc):
        x_, y_ = load(bk), load(bc)
        f_ = ("moves", "winner_seat", "points", "seed")
        same_ = x_.keys() == y_.keys() and all(x_[k][f] == y_[k][f] for k in x_ for f in f_)
        print(f"   cross-check against the cloud's b2e_koh3: {'identical' if same_ else 'DIFFERENT'} on {', '.join(f_)} "
              f"({len(x_)} and {len(y_)} games)")
        assert same_, "the laptop's and the cloud's b2e_koh3 differ: stop and write it down"
    a, b = panel(os.path.join(CLOUD, "b2e_kog3.jsonl")), panel(bk)
    assert all(a[k].keys() == b[k].keys() and len(a[k]) == 8 for k in a) and \
        sum(1 for _ in open(bk, encoding="utf-8")) == 96 * 500, "b2e_koh3 incomplete"
    for (block, k) in sorted(a):
        x, y = sum(a[(block, k)].values()) / 8, sum(b[(block, k)].values()) / 8
        base = k.replace("dustin_", "")
        arch = next((n for n in names if n == base), None) or next((n for n in names if n.startswith(base)), None)
        cells = [o for o in a[(block, k)] if (arch, o) in lim["pooled"]]
        L = sum(lim["pooled"][(arch, o)] for o in cells) / len(cells)
        fur = abs(y - L) - abs(x - L)
        FURTHER[k] = (block, fur)
        tag = ("more than 2 further: a veto only with own-side harm (6d)" if fur > 2 else "no") \
            if block.startswith("A") else "reported only"
        print(f"   {block} {k:28} kog3 {x:5.1f} -> koh3 {y:5.1f}; Limitless {L:5.1f}; further by {fur:+.1f}: {tag}")


def paired(base_rows, new_rows, own):
    """Mean own-side change (points) and the variation check's 95% half-width, over the rows' cells."""
    assert all(base_rows[k]["seed"] == g["seed"] for k, g in new_rows.items()), "mixed rows are not the base's deals"
    cells = defaultdict(list)
    for key, g in new_rows.items():
        cells[key[0]].append(100 * (own(g) - own(base_rows[key])))
    K_ = len(cells)
    means = [sum(v) / len(v) for v in cells.values()]
    var = [(sum((d - m) ** 2 for d in v) / (len(v) - 1)) / len(v) for v, m in zip(cells.values(), means)]
    return sum(means) / K_, 1.96 * math.sqrt(sum(var)) / K_, K_


# 6b. The Scizor row.
print("\n6b. The Scizor row (amendment 2's rows, amendment 4's test):")
sk, sg = load(os.path.join(RUNS, "scizor_koh3.jsonl")), load(os.path.join(RUNS, "scizor_kog3.jsonl"))
m1 = load(os.path.join(RUNS, "mixed_scizor_koh3_first.jsonl")); m2 = load(os.path.join(RUNS, "mixed_scizor_koh3_second.jsonl"))
assert {k[0] for k in m1} == {k[0] for k in m2} == set(range(8)) and len(m1) == len(m2) == 4000, "Scizor mixed rows incomplete"
fds = lambda g: g["first_deck_score"]
m, h, n = paired(sg, m1, fds)
veto = m + h < 0
print(f"   own side (koh3 on Scizor v kog3 on both): {m:+.2f} +/- {h:.2f} over {n} rows -> "
      f"{'VETO (own side worse beyond paired noise; amendment 4)' if veto else 'no harm'}")
m, h, n = paired(sg, m2, lambda g: 1 - g["first_deck_score"])
print(f"   the other direction (koh3 on the panel list, kog3 on Scizor), the panel's side: {m:+.2f} +/- {h:.2f} (reported)")
print(f"   Scizor's panel average, both sides: kog3 {100 * sum(map(fds, sg.values())) / len(sg):.1f} -> koh3 {100 * sum(map(fds, sk.values())) / len(sk):.1f} (reported)")

# 6c. The second lists.
print("\n6c. The second lists (amendment 2's rows, amendment 4's test; accuracy reported):")
v2 = json.load(open(os.path.join(RES, "scoreboard_v2_2026-09-25", "limitless_v2_dev.json"), encoding="utf-8"))["cells"]
for v in ("v-lucario_2", "v-suicune_2", "v-weezing_2", "l-charizardy"):
    rows = {int(r["pairing"]): r for r in csv.DictReader(open(os.path.join(T, f"var_{v}.tsv"), encoding="utf-8"), delimiter="\t")}
    side = {p: r["variant_side"] for p, r in rows.items()}
    own = lambda g: g["first_deck_score"] if side[g["pairing"]] == "a" else 1 - g["first_deck_score"]
    gk, gg = load(os.path.join(RUNS, f"var_{v}_koh3.jsonl")), load(os.path.join(RUNS, f"var_{v}_kog3.jsonl"))
    avg = lambda rs: 100 * sum(own(g) for g in rs.values()) / len(rs)
    deck = rows[next(iter(rows))]["deck"]
    if deck == "charizardy":
        cells = [(o, lim["pooled"].get(("charizardy_entei", o))) for o in {r["opponent"] for r in rows.values()}]
        L = sum(x for _, x in cells if x is not None) / sum(1 for _, x in cells if x is not None); src = "B2e pooled, charizardy_entei"
    else:
        vals = []
        for p, r in rows.items():
            # the version stands in for its deck on its side; the other deck is 'opponent' (side a) or 'held_key' (side b)
            a_, b_ =(deck, r["opponent"]) if r["variant_side"] == "a" else (r["held_key"], deck)
            key = f"{min(a_, b_)}|{max(a_, b_)}"
            w, l, t = v2[key]
            s = (w + 0.5 * t) / (w + l + t)
            vals.append(100 * (s if min(a_, b_) == deck else 1 - s))
        L = sum(vals) / len(vals); src = "development half, the same opponents"
    x, y = avg(gg), avg(gk)
    fur = abs(y - L) - abs(x - L)
    mix = {}
    for s in ("a", "b"):
        p = os.path.join(RUNS, f"var_{v}_mixed_{s}.jsonl")
        if os.path.exists(p):
            mix.update(load(p))
    miss = sorted(set(rows) - {k[0] for k in mix})
    if miss:
        sys.exit(f"{v}: mixed rows missing for pairings {miss}; wait for the laptop runs")
    m, h, n = paired(gg, mix, own)
    counts = m + h < 0
    print(f"   {v:13} opponent average kog3 {x:5.1f} -> koh3 {y:5.1f}; figure {L:5.1f} ({src}); further by {fur:+.1f} "
          f"(reported); own side (mixed) {m:+.2f} +/- {h:.2f} over {n} -> "
          f"{'VETO (own side worse beyond paired noise; amendment 4)' if counts else 'no harm'}")

# 6d. B2e's own-side mixed rows (amendment 4): koh3 on the held deck, kog3 on the panel, against kog3 on both.
print("\n6d. B2e's own side in the mixed rows (koh3 on the held deck, kog3 on the panel; amendment 4):")
mb = os.path.join(RUNS, "mixed_b2e_koh3_first.jsonl")
if not os.path.exists(mb) or not FURTHER:
    print("   mixed_b2e_koh3_first.jsonl (or b2e_koh3) not in yet")
else:
    base_b2e, mix_b2e = load(os.path.join(CLOUD, "b2e_kog3.jsonl")), load(mb)
    assert len(mix_b2e) == 96 * 500 and {k[0] for k in mix_b2e} == set(range(96)), "B2e mixed rows incomplete"
    assert {(g["bot_a"], g["bot_b"]) for g in mix_b2e.values()} == {("koh3", "kog3")}, "B2e mixed rows: wrong pilots"
    vetoes = []
    for key in sorted({tsv[p]["held_key"] for p in range(96)}, key=lambda k: min(p for p in range(96) if tsv[p]["held_key"] == k)):
        rows = {kk: g for kk, g in mix_b2e.items() if tsv[kk[0]]["held_key"] == key}
        m, h, n = paired(base_b2e, rows, fds)
        block, fur = FURTHER[key]
        harm = m + h < 0
        if block.startswith("A"):
            tag = "VETO (own side worse beyond paired noise)" if harm else \
                ("investigation item (more than 2 further, own side not worse)" if fur > 2 else "no harm")
            vetoes += [key] if harm else []
        else:
            tag = "reported (Dustin's file)" + ("; own side worse beyond paired noise" if harm else "")
        print(f"   {block} {key:28} own side {m:+.2f} +/- {h:.2f} over {n} rows; further by {fur:+.1f} -> {tag}")
    print(f"   B2e held-out veto: {'none' if not vetoes else ', '.join(vetoes)}")
