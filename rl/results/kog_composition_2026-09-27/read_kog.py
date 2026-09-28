"""kog's composition check, read in READING_PLAN.md's order (fixed before any laptop game).
  1. identity (identity_check.txt, written by the runner);
  2-3. score45.py --rules v2, kog3 against kp3 with kog3's mixed rows: the table, the vetoes;
  4. accuracy against the better component: score45.py with kpg3 as current, kog3 as new: the tau margin
     (kpg3 minus kog3) 90% lower bound at -1.0 or above passes; kog3 against koa3 reported the same way;
  5. where the parts meet: Altaria v Blaziken and Rayquaza v Altaria, kog3 beside kp3, koa3 and kpg3.
Usage: python3 read_kog.py > READING_numbers.txt"""
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.abspath(os.path.join(HERE, ".."))
K = os.path.join(RES, "kpf_2026-09-26", "reading")
KOA = os.path.join(RES, "koa_2026-09-26", "reading")
S45 = os.path.join(K, "score45.py")
KOG = [os.path.join(HERE, "table_kog3.jsonl"), os.path.join(HERE, "new17_kog3.jsonl")]
BASES = {"kp3": [os.path.join(K, "table_kp3.jsonl"), os.path.join(K, "new17_kp3.jsonl")],
         "kpg3": [os.path.join(K, "table_kpg3.jsonl"), os.path.join(K, "new17_kpg3.jsonl")],
         "koa3": [os.path.join(KOA, "table_koa3.jsonl"), os.path.join(KOA, "new17_koa3.jsonl")]}
MIXED = [os.path.join(HERE, f"mixed_{s}_kog3_{d}.jsonl") for s in ("table", "new17") for d in ("first", "second")]
KEYS = ("real error [", ": real error", "dMSE", "real error, current minus new", "cell veto", "deck veto", "ADOPTION")


def score(old, mixed):
    cmd = [sys.executable, S45, "--rules", "v2", "--old-games", *BASES[old], "--new-games", *KOG, "--old", old, "--new", "kog3"]
    if mixed:
        cmd += ["--mixed", *MIXED]
    out = subprocess.run(cmd, capture_output=True, text=True, cwd=K)
    text = out.stdout + out.stderr
    open(os.path.join(HERE, f"score45_kog3_vs_{old}.txt"), "w", encoding="utf-8").write(text)
    return text


def show(text, n=40):
    for line in text.splitlines()[:400]:
        if any(k in line for k in KEYS):
            print("   " + line.strip()[:250])


print("1. Identity:")
for line in open(os.path.join(HERE, "identity_check.txt"), encoding="utf-8"):
    print("   " + line.strip())
print("2-3. The 45 cells, kog3 against kp3 (the pilot in force), rules v2 with kog3's mixed rows (score45_kog3_vs_kp3.txt):")
show(score("kp3", True))
print("4. Accuracy against the components (no mixed rows; only the margin is read):")
for old in ("kpg3", "koa3"):
    t = score(old, False)
    m = re.findall(r"real error, current minus new: ([+-]?[\d.]+) points, 90% interval ([+-]?[\d.]+) to ([+-]?[\d.]+)", t)
    for (pt, lo, hi), label in zip(m, ("all 45 cells", "decision set (Altaria v Sceptile quarantined)")):
        verdict = ("PASSES (lower bound at -1.0 or above)" if float(lo) >= -1.0 else "FAILS (lower bound below -1.0)") \
            if old == "kpg3" else "reported"
        print(f"   {label}: margin ({old} minus kog3) {float(pt):+.2f}, 90% interval {float(lo):+.2f} to {float(hi):+.2f}: {verdict}")
print("5. Where the parts meet (first-named deck's score, 500 deals each):")
load = lambda paths: {(g["a"], g["b"], g["i"]): g["first_deck_score"] for p in paths for g in map(json.loads, open(p))}
rows = {"kp3": load(BASES["kp3"]), "koa3": load(BASES["koa3"]), "kpg3": load(BASES["kpg3"]), "kog3": load(KOG)}
for a, b in (("altaria", "blaziken"), ("rayquaza", "altaria")):
    print(f"   {a} v {b}: " + ", ".join(f"{bot} {100 * sum(r[(a, b, i)] for i in range(500)) / 500:.1f}" for bot, r in rows.items()))
