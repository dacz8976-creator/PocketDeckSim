"""Step 6: identity and integrity of the inputs (section 4): the three programs' sha256 on the disk, the 75 recorded
inputs, the game files' sha256 against what coverage_skip.txt and the score45 record name, the identity replays
(fresh runner at the development bases, i < 20) against kt's files game for game, the timing line, and the scan pages
(every legality_scan file read has its page, no RULE finding). Writes OUT/sr6_identity.txt."""
import sys, os, re, glob, json
sys.path.insert(0, "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kta_tables_2026-09-29/second_reader")
from sr_lib import *

lines = []
p = lines.append
REG = {"deckgym": "407976366fa2104ee1f2663c94fe31b1c503466defe9d6154b7e60659cb0991c",
       "legality_scan": "924751ba0926993eaee87ecc8fb8301ffd0b7eee8490bfb3369427794328f938",
       "tool_census": "d9799c96015f74b952889a7f7d9820bbc12d5d97e4d267ad8acc2b63cdcc720b"}
BIN = "/home/dacz8976/engine-kt-ec7e1a8/engine/target/release"
paths = {"deckgym": BIN + "/deckgym", "legality_scan": BIN + "/examples/legality_scan"}
tc = [x for x in glob.glob(BIN + "/**/tool_census", recursive=True) if os.path.isfile(x)]
paths["tool_census"] = tc[0] if tc else None
for n, pth in paths.items():
    h = sha(pth) if pth and os.path.exists(pth) else "MISSING"
    p(f"program {n}: {pth} sha256 {h} = registered: {h == REG[n]}")

# the 75 inputs recorded before the first game
rec = open(T + "/ec7e1a8_fresh_inputs.sha256", encoding="utf-8").read().splitlines()
ok = bad = 0
badl = []
for ln in rec:
    ln = ln.strip()
    if not ln:
        continue
    h, f = ln.split(None, 1)
    f = f.lstrip("*")
    fp = f if f.startswith("/") else os.path.join(REPO, f)
    if os.path.exists(fp) and sha(fp) == h:
        ok += 1
    else:
        bad += 1
        badl.append(f)
p(f"recorded inputs (ec7e1a8_fresh_inputs.sha256): {ok} equal now, {bad} differ or missing {badl[:5]}")

# game files: sha256 against coverage_skip.txt's and the score45 record's
named = {}
for ln in open(T + "/coverage_skip.txt", encoding="utf-8"):
    m = re.search(r"(\S+\.jsonl) \((\d+) games, sha256 ([0-9a-f]{64})\)", ln)
    if m:
        named[os.path.basename(m.group(1))] = m.group(3)
reps = json.load(open(T + "/score45_kta3_vs_kog3.txt.reps", encoding="utf-8"))
for f, h in reps["inputs"].items():
    if "composite" not in f:
        named.setdefault(f, h)
        assert named[f] == h
same = {f: sha(T + "/" + f) == h for f, h in named.items()}
p(f"game files hashed now against coverage_skip.txt / the score45 record: {sum(same.values())} of {len(same)} equal; differ: {[f for f, v in same.items() if not v] or 'none'}")

# identity replays
FIELDS = ("pairing", "a", "b", "i", "seed", "bot_a", "bot_b", "first_seat", "winner_seat", "points", "turns",
          "first_deck_score", "moves", "decisions", "openings")
K = KT + "/ec7e1a8_"
REPL = [
    ("kog3 table", "id_kog3_table_i20", "id_kog3_500", ab),
    ("kog3 new17", "id_kog3_new17_i20", "id_kog3_new17", ab),
    ("kog3 Scizor", "id_kog3_scizor_i20", "id_kog3_scz40", pairing),
    ("kog3 B2e", "id_kog3_b2e_i20", "id_kog3_b2e40", pairing),
    ("kog3 v-lucario_2", "id_kog3_var_v-lucario_2_i20", "id_kog3_var_v-lucario_240", pairing),
    ("kog3 v-suicune_2", "id_kog3_var_v-suicune_2_i20", "id_kog3_var_v-suicune_240", pairing),
    ("kog3 v-weezing_2", "id_kog3_var_v-weezing_2_i20", "id_kog3_var_v-weezing_240", pairing),
    ("kog3 l-charizardy", "id_kog3_var_l-charizardy_i20", "id_kog3_var_l-charizardy40", pairing),
    ("kog3 (d)", "id_kog3_d_i20", "d_kog3", pairing),
    ("kta3 table", "id_kta3_table_i20", "kta3_table", ab),
    ("kta3 new17", "id_kta3_new17_i20", "kta3_new17", ab),
    ("kta3 Scizor", "id_kta3_scizor_i20", "scizor_kta3", pairing),
    ("kta3 B2e", "id_kta3_b2e_i20", "b2e_kta3", pairing),
    ("kta3 v-lucario_2", "id_kta3_var_v-lucario_2_i20", "var_v-lucario_2_kta3", pairing),
    ("kta3 v-suicune_2", "id_kta3_var_v-suicune_2_i20", "var_v-suicune_2_kta3", pairing),
    ("kta3 v-weezing_2", "id_kta3_var_v-weezing_2_i20", "var_v-weezing_2_kta3", pairing),
    ("kta3 l-charizardy", "id_kta3_var_l-charizardy_i20", "var_l-charizardy_kta3", pairing),
    ("kta3 (d)", "id_kta3_d_i20", "d_kta3", pairing),
]
total = 0
alleq = True
for label, fresh, ref, key in REPL:
    A = by_key(rd(F + fresh + ".jsonl"), key)
    B = by_key(rd(K + ref + ".jsonl"), key)
    n = eq = 0
    bots = set()
    for k, c in A.items():
        for i, r in c.items():
            n += 1
            q = B.get(k, {}).get(i)
            bots.add((r["bot_a"], r["bot_b"]))
            if q is not None and all(r.get(f) == q.get(f) for f in FIELDS):
                eq += 1
    imax = max(i for c in A.values() for i in c)
    total += n
    alleq &= (n == eq)
    p(f"identity {label:<18}: {eq} of {n} equal on {len(FIELDS)} fields (i < {imax + 1}; bots {sorted(bots)})")
for arm in ("kog3", "kta3"):
    A = {(r["opp"], r["seat"], r["i"]): r for r in rd(F + f"id_ab_d07_{arm}.jsonl")}
    B = {(r["opp"], r["seat"], r["i"]): r for r in rd(K + f"ab_d07_{arm}.jsonl") if r["opp"] == "t-altaria"}
    eq = sum(1 for k, r in A.items() if k in B and all(r.get(f) == B[k].get(f) for f in B[k]))
    total += len(A)
    alleq &= (eq == len(A) == len(B))
    p(f"identity A/B tool {arm}, deck 07 v t-altaria, development block: {eq} of {len(A)} equal on every field of the reference row (reference rows {len(B)})")
p(f"IDENTITY: {total} games replayed; all equal: {alleq}")

# timing
for f in ("ec7e1a8_fresh_timing_1.txt", "ec7e1a8_fresh_timing_kog3_1.time", "ec7e1a8_fresh_timing_kta3_1.time"):
    p(f"timing file {f}: {open(T + '/' + f, encoding='utf-8').read().strip()}")

# scan pages
pages = sorted(glob.glob(F + "*.txt"))
rule = {os.path.basename(x): sum(1 for ln in open(x, encoding="utf-8", errors="replace") if re.search(r"\bRULE\b", ln)) for x in pages}
p(f"scan pages: {len(pages)}; pages with a RULE line: {[f for f, c in rule.items() if c] or 'none'}")
# legality_scan pages: every pairing line 'games with findings: 0' and the Findings block reads 'none'
scan = [x for x in pages if open(x, encoding="utf-8", errors="replace").readline().startswith("bot ")]
bad_pages = []
for x in scan:
    txt = open(x, encoding="utf-8", errors="replace").read().splitlines()
    nz = [ln for ln in txt if re.search(r"games with findings: (\d+)", ln) and int(re.search(r"games with findings: (\d+)", ln).group(1)) > 0]
    j = [k for k, ln in enumerate(txt) if ln.startswith("Findings")]
    block_none = bool(j) and txt[j[-1] + 1].strip() == "none"
    if nz or not block_none:
        bad_pages.append((os.path.basename(x), len(nz), block_none))
p(f"legality_scan pages: {len(scan)}; pages with a finding (any 'games with findings' > 0, or a Findings block other than 'none'): {bad_pages or 'none'}")
nopage = [os.path.basename(x) for x in glob.glob(F + "*.jsonl") if not os.path.exists(x[:-6] + ".txt")]
p(f"game files without a page beside them: {nopage or 'none'}")
open(OUT + "/sr6_identity.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines))
