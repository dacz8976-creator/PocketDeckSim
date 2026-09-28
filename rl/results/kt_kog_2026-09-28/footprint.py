"""kt's footprint on kog, read first and committed alone (kt's registration, FOOTPRINT AND ROUTES, with amendments 1
and 2): for each code, the share of the 45 cells' paired games whose moves differ from the base's (kog3: the laptop's
composition runs, ../kog_composition_2026-09-27/table_kog3.jsonl and new17_kog3.jsonl). For kt3 and kta3 the number
fixes the route: under 15% the reserve route (a)-(e), otherwise the ordinary adoption rule. ktb3 and ktc3 are
reported for attribution. The same computation as koh's (../koh_2026-09-28/laptop_reading/footprint.py). Reads moves
only; no result, score or error is read. Usage: python3 footprint.py (from anywhere) > footprint.txt"""
import collections, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
KOG = os.path.join(HERE, "..", "kog_composition_2026-09-27")
BUILD = "ec7e1a8"
load = lambda p: {(g["a"], g["b"], g["i"]): g for g in map(json.loads, open(p, encoding="utf-8"))}
base = {**load(os.path.join(KOG, "table_kog3.jsonl")), **load(os.path.join(KOG, "new17_kog3.jsonl"))}
print(f"Base: kog3, {len(base)} paired games on the 45 cells. Build {BUILD}. Moves only.")
for code in ("kt3", "kta3", "ktb3", "ktc3"):
    files = [os.path.join(HERE, f"{BUILD}_{part}_{code}_500.jsonl") for part in ("table", "new17")]
    if not all(os.path.exists(f) for f in files):
        print(f"{code}: not run")
        continue
    new = {**load(files[0]), **load(files[1])}
    assert base.keys() == new.keys(), (code, len(base), len(new))
    assert all(base[k]["seed"] == new[k]["seed"] for k in base), f"{code}: different deals"
    assert {(g["bot_a"], g["bot_b"]) for g in new.values()} == {(code, code)}, f"{code} is not on both sides"
    diff = [k for k in base if base[k]["moves"] != new[k]["moves"]]
    fp = 100 * len(diff) / len(base)
    route = ("RESERVE route, clauses (a)-(e)" if fp < 15 else "ORDINARY adoption rule (15% or more)") \
        if code in ("kt3", "kta3") else "attribution only (a diagnostic)"
    print(f"\n{code}: FOOTPRINT {len(diff)} of {len(base)} paired games differ from kog3's moves = {fp:.2f}%")
    print(f"{code}: ROUTE (fixed on this number, before anything else is read): {route}")
    by = collections.Counter((a, b) for a, b, _ in diff)
    print(f"{code}: by cell (games differing of 500): "
          + (", ".join(f"{a} v {b} {n}" for (a, b), n in sorted(by.items())) or "none"))
