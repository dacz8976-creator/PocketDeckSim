"""km's footprint, read first and committed alone (../REGISTRATION_DRAFT.md, section 5, step 1; section 4.0, "Reading
code"; Amendment 1 (Sept 30), (b) items 2-4: km3 against kta3). A copy of ../../koh_2026-09-28/laptop_reading/footprint.py
with km's names: the base is kta3's two 45-cell reference files as km_config.json names them (Amendment 1 (b) item 3:
ec7e1a8_kta3_table.jsonl and ec7e1a8_kta3_new17.jsonl, each checked here against the config's sha256), asserted
("kta3","kta3"); the new side is km3's, asserted ("km3","km3"); the codes come from the config. The share of paired
games on the 45 cells whose moves differ from kta3's. Under 15% the reserve route applies; otherwise the ordinary rule.
The route is fixed on this number. run_km.sh part R gives it a scratch folder holding copies of its <B>_km3_table.jsonl
and <B>_km3_new17.jsonl under the names below. Reads moves only; no result, score or error is read.
Usage: python3 footprint_km.py <dir with table_km3.jsonl, new17_km3.jsonl> [--config km_config.json]"""
import collections, hashlib, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import km_config  # noqa: E402
S = sys.argv[1]
CFG = km_config.load(sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == "--config" else None)
BASE, CAND = CFG["comparison"]["baseline"], CFG["comparison"]["candidate"]
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
load = lambda p: {(g["a"], g["b"], g["i"]): g for g in map(json.loads, open(p, encoding="utf-8"))}


def ref(group):
    r = CFG["refs"][group]
    p = os.path.join(ROOT, r["path"])
    got = hashlib.sha256(open(p, "rb").read()).hexdigest()
    assert got == r["sha256"], f"{r['path']} has sha256 {got}, not km_config.json's {r['sha256']}"
    return p


base = {**load(ref("table")), **load(ref("new17"))}
new = {**load(os.path.join(S, f"table_{CAND}.jsonl")), **load(os.path.join(S, f"new17_{CAND}.jsonl"))}
assert base.keys() == new.keys(), (len(base), len(new))
assert all(base[k]["seed"] == new[k]["seed"] for k in base), "different deals"
assert {(g["bot_a"], g["bot_b"]) for g in base.values()} == {(BASE, BASE)}, f"the base files are not {BASE} on both sides"
assert {(g["bot_a"], g["bot_b"]) for g in new.values()} == {(CAND, CAND)}, f"km's files are not {CAND} on both sides"
diff = [k for k in base if base[k]["moves"] != new[k]["moves"]]
fp = 100 * len(diff) / len(base)
print(f"FOOTPRINT: {len(diff)} of {len(base)} paired games on the 45 cells differ from {BASE}'s moves = {fp:.2f}%")
print(f"ROUTE (fixed on this number, before anything else is read): "
      f"{'RESERVE route, clauses (a)-(e)' if fp < 15 else 'ORDINARY adoption rule (15% or more)'}")
by = collections.Counter((a, b) for a, b, _ in diff)
print("by cell (games differing of 500): " + ", ".join(f"{a} v {b} {n}" for (a, b), n in sorted(by.items())))
