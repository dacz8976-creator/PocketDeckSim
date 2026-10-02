"""Draft A: the Oct 2 page (floor.py 8e5395e6, fallback attacker) v the re-run (floor.py 76327865, ATTACKERS)."""
import hashlib, json, os, sys
D = "rl/results/floor_drafts_2026-10-02"
OLD, NEW = D, os.path.join(D, "draft-A_attackers-sharpedo")
stem = "draft-A-shark-tempo"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


for x in (".md", "_coverage.json", "_games.jsonl"):
    a, b = os.path.join(OLD, stem + x), os.path.join(NEW, stem + x)
    eq = open(a, "rb").read() == open(b, "rb").read()
    print(f"{'BYTE-EQUAL' if eq else 'DIFFERS'} {stem}{x}: Oct 2 {sha(a)} / re-run {sha(b)}")

# the page, line by line
ol = open(os.path.join(OLD, stem + ".md"), encoding="utf-8").read().split("\n")
nl = open(os.path.join(NEW, stem + ".md"), encoding="utf-8").read().split("\n")
print(f"page lines: Oct 2 {len(ol)}, re-run {len(nl)}")
for i in range(max(len(ol), len(nl))):
    o = ol[i] if i < len(ol) else None
    n = nl[i] if i < len(nl) else None
    if o != n:
        print(f"line {i + 1} differs:\n  Oct 2:  {o}\n  re-run: {n}")

# the games file, record by record
og = [json.loads(l) for l in open(os.path.join(OLD, stem + "_games.jsonl"), encoding="utf-8")]
ng = [json.loads(l) for l in open(os.path.join(NEW, stem + "_games.jsonl"), encoding="utf-8")]
print(f"games: Oct 2 {len(og)} records, re-run {len(ng)}")
keys_o = set().union(*(r.keys() for r in og))
keys_n = set().union(*(r.keys() for r in ng))
print(f"fields: {sorted(keys_o)}; same field set: {keys_o == keys_n}")
diff_fields = {}
nrec = 0
for r1, r2 in zip(og, ng):
    d = [k for k in sorted(keys_o | keys_n) if r1.get(k) != r2.get(k)]
    if d:
        nrec += 1
    for k in d:
        diff_fields[k] = diff_fields.get(k, 0) + 1
print(f"records with any difference: {nrec} of {len(og)}; per field: {diff_fields}")
ATT = {"could", "did", "conceded"}
same_rest = all({k: v for k, v in r1.items() if k not in ATT} == {k: v for k, v in r2.items() if k not in ATT} for r1, r2 in zip(og, ng))
print(f"every record equal once could / did / conceded are left out: {same_rest}")
# the line text with those three fields left out, byte for byte, in the same key order
def strip(line):
    r = json.loads(line)
    return json.dumps({k: v for k, v in r.items() if k not in ATT})
so = [strip(l) for l in open(os.path.join(OLD, stem + "_games.jsonl"), encoding="utf-8")]
sn = [strip(l) for l in open(os.path.join(NEW, stem + "_games.jsonl"), encoding="utf-8")]
print(f"the files with could / did / conceded removed are equal text: {so == sn}")
print(f"won, per record, equal: {[r['won'] for r in og] == [r['won'] for r in ng]}; flagged equal: {[r['flagged'] for r in og] == [r['flagged'] for r in ng]}")
