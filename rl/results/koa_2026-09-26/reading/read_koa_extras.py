"""koa's reported-beside runs and diagnostics (READING.md "Still to be reported beside"), all at the official engine
(main-83e17ae), each against kp3 on the same deals. None of these changes koa's verdict, except that a veto on koa's two
new cells (Rayquaza v Altaria, Altaria/Greninja v Altaria) would block the takeover (Dustin, Sept 27: "forty-five for
no-harm").
  1. The 17 new cells (new17_koa3 v kpf's new17_kp3): which cells change; score45.py with rules v2 for the 45-cell view.
  2. Dustin's six B2e files (pairings 48-95; b2e_dustin_koa3 v kpf's b2e_kp3): each file's average, reported only.
  3. The variant-list check (registration section 7 (d)): LaNora's list, koa3 arm minus kp3 arm, same deals, pooled over
     its 8 rows (7 table opponents + the table's own Altaria list on amendment 2's block). Predicted up.
  4. kob3 and kor3's discriminating rows (registration section 7, "B and R"): the diagnostic deck's own side against kp3's
     table games; "the Darkrai half proves real" = Hydreigon up beyond pooled noise under kob, or Suicune down under kor.
     Identity check: where the diagnostic sits on a deck its switch doesn't touch, every game must equal kp3's.
Usage: python3 read_koa_extras.py > extras_numbers.txt"""
import json, math, os, subprocess, sys
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(RES, "table_readings_2026-09-24"))
import score as S  # noqa: E402
KPF = os.path.join(RES, "kpf_2026-09-26", "reading")
PAIRS = S.D.PAIRS[:28]


def load(path, key=("pairing", "i")):
    return {tuple(g[k] for k in key): g for g in map(json.loads, open(path, encoding="utf-8"))}


def own(rows, base, keys, flip):
    """Paired own-side diffs: rows and base are dicts keyed like keys; flip reads the second-named deck's side."""
    b = {i: {"s": base[k]["first_deck_score"], "seed": base[k]["seed"]} for i, k in enumerate(keys)}
    o = {i: {"s": rows[k]["first_deck_score"], "seed": rows[k]["seed"]} for i, k in enumerate(keys)}
    return S.diffs(b, o, flip)


def fmt(mv):
    m, v = mv
    return f"{m:+.2f} +/- {1.96 * math.sqrt(v):.2f}"


# 1. the 17 new cells
kp = load(os.path.join(KPF, "new17_kp3.jsonl"), ("a", "b", "i"))
ko = load(os.path.join(HERE, "new17_koa3.jsonl"), ("a", "b", "i"))
assert kp.keys() == ko.keys(), "new17 key sets differ"
cells = sorted({(a, b) for a, b, _ in kp})
print(f"1. The 17 new cells, koa3 v kp3, same deals ({len(kp)} games):")
for a, b in cells:
    ks = [(a, b, i) for i in range(500)]
    same = sum(ko[k]["decisions"] == kp[k]["decisions"] and ko[k]["moves"] == kp[k]["moves"] for k in ks)
    s0 = 100 * sum(kp[k]["first_deck_score"] for k in ks) / 500
    s1 = 100 * sum(ko[k]["first_deck_score"] for k in ks) / 500
    tag = "identical" if same == 500 else f"{500 - same} games differ; {a} score {s0:.1f} -> {s1:.1f}"
    print(f"   {a} v {b}: {tag}")
cmd = [sys.executable, os.path.join(KPF, "score45.py"), "--rules", "v2",
       "--old-games", os.path.join(KPF, "table_kp3.jsonl"), os.path.join(KPF, "new17_kp3.jsonl"),
       "--new-games", os.path.join(HERE, "table_koa3.jsonl"), os.path.join(HERE, "new17_koa3.jsonl"),
       "--old", "kp3", "--new", "koa3",
       "--mixed", os.path.join(HERE, "mixed_koa3_first.jsonl"), os.path.join(HERE, "mixed_koa3_second.jsonl")]
out = subprocess.run(cmd, capture_output=True, text=True, cwd=KPF)
open(os.path.join(HERE, "score45_koa3_vs_kp3.txt"), "w", encoding="utf-8").write(out.stdout + out.stderr)
print("   score45.py, rules v2 (full output: score45_koa3_vs_kp3.txt):")
for line in out.stdout.splitlines():
    if any(t in line for t in ("real error [", "real error, current minus new", "dMSE", "cell veto", "deck veto", "ADOPTION",
                               ": real error")) or ("altaria" in line.lower() and ("rayquaza" in line.lower() or "greninja" in line.lower()) and "->" in line):
        print("     " + line.strip()[:240])

# 2. Dustin's six B2e files
import csv  # noqa: E402
tsv = {int(r["pairing"]): r for r in csv.DictReader(open(os.path.join(RES, "b2e_card_check_2026-09-26", "b2e_pairings.tsv"),
                                                        encoding="utf-8"), delimiter="\t")}
kb = {k: g for k, g in load(os.path.join(KPF, "b2e_kp3.jsonl")).items() if k[0] >= 48}
ob = load(os.path.join(HERE, "b2e_dustin_koa3.jsonl"))
assert kb.keys() == ob.keys(), (len(kb), len(ob))
by = defaultdict(list)
for k in kb:
    by[tsv[k[0]]["held_key"]].append(k)
print(f"2. Dustin's B2e files (pairings 48-95, {len(kb)} games), koa3 v kp3, reported only:")
for hk, ks in sorted(by.items()):
    ch = sum(ob[k]["moves"] != kb[k]["moves"] for k in ks)
    s0 = 100 * sum(kb[k]["first_deck_score"] for k in ks) / len(ks)
    s1 = 100 * sum(ob[k]["first_deck_score"] for k in ks) / len(ks)
    alt = [k for k in ks if tsv[k[0]]["opponent"] == "altaria"]
    extra = ""
    if alt:
        extra = f"; v Altaria {100 * sum(kb[k]['first_deck_score'] for k in alt) / len(alt):.1f} -> " \
                f"{100 * sum(ob[k]['first_deck_score'] for k in alt) / len(alt):.1f}"
    print(f"   {hk}: {s0:.1f} -> {s1:.1f} over {len(ks)} games ({ch} changed){extra}")

# 3. the variant-list check
parts, per = [], []
for name, tag in (("variant", "7 table opponents"), ("variant_self", "the table's own Altaria list")):
    k3 = load(os.path.join(HERE, f"{name}_kp3.jsonl"))
    ka = load(os.path.join(HERE, f"{name}_koa3.jsonl"))
    assert k3.keys() == ka.keys()
    for p in sorted({p for p, _ in k3}):
        ks = [(p, i) for i in range(500)]
        d = own(ka, k3, ks, False)
        parts.append(d)
        per.append((f"{k3[ks[0]]['a']} v {k3[ks[0]]['b']}", S.mean_var(d), sum(ka[k]["moves"] != k3[k]["moves"] for k in ks)))
m, h, n = S.side_change(parts)
print(f"3. Variant list (LaNora's Altaria), koa3 minus kp3 on its own side, pooled over {len(per)} rows ({n} deals): "
      f"{m:+.2f} +/- {h:.2f} ({'up beyond noise' if m - h > 0 else 'down beyond noise' if m + h < 0 else 'within noise'})")
for c, mv, ch in per:
    print(f"   {c}: {fmt(mv)} ({ch} games changed)")

# 4. kob3 and kor3's discriminating rows
kp3 = load(os.path.join(KPF, "table_kp3.jsonl"))
TOUCH = {"kob3": {"altaria", "hydreigon", "vespiquen", "weezing"}, "kor3": {"altaria", "suicune", "vespiquen", "weezing"}}
print("4. Diagnostics, the deck's own side (diagnostic on the deck, kp3 on the other) v kp3's table games, same deals:")
for spec in ("kob3:hydreigon", "kob3:vespiquen", "kob3:weezing", "kor3:suicune", "kor3:vespiquen", "kor3:weezing"):
    bot, deck = spec.split(":")
    first = load(os.path.join(HERE, f"diag_{bot}_{deck}_first.jsonl"))
    second = load(os.path.join(HERE, f"diag_{bot}_{deck}_second.jsonl"))
    ps = [p for p, (a, b) in enumerate(PAIRS) if deck in (a, b)]
    parts, rows_txt, ident, ident_n = [], [], 0, 0
    for p in ps:
        a, b = PAIRS[p]
        ks = [(p, i) for i in range(500)]
        mine, theirs, flip = (first, second, False) if a == deck else (second, first, True)
        d = own(mine, kp3, ks, flip)
        parts.append(d)
        opp = b if a == deck else a
        rows_txt.append(f"v {opp} {fmt(S.mean_var(d))}")
        if opp not in TOUCH[bot]:
            ident_n += 500
            ident += sum(theirs[k]["moves"] == kp3[k]["moves"] for k in ks)
    m, h, n = S.side_change(parts)
    verdict = "up beyond noise" if m - h > 0 else "down beyond noise" if m + h < 0 else "within noise"
    print(f"   {bot} on {deck}: {m:+.2f} +/- {h:.2f} pooled over {len(ps)} rows ({verdict})")
    print(f"      " + "; ".join(rows_txt))
    print(f"      identity where {bot} sits on an untouched deck: {ident} of {ident_n} games equal kp3's")
