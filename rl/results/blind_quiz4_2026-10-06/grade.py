"""Grade Quiz 4: Dustin's answers v the private key (which plan was kx3's and which km3's)."""
import json, glob, os, collections
SP = "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/"
sel = {x["q"]: x for x in json.load(open(SP + "quiz4_selection_PRIVATE.json"))}
key = json.load(open("/home/dacz8976/quiz4_private/answer_key_q4.json"))
ans = {}
for f in sorted(glob.glob(SP + "quiz4_page/answers_read/answers/*.json")):
    d = json.load(open(f)); ans[os.path.basename(f)[:-5]] = d.get("data", d)
def keyed(q):
    k = key.get(q) if isinstance(key, dict) else None
    if k is None and isinstance(key, dict):
        for v in key.values():
            if isinstance(v, dict) and v.get("q") == q: k = v
    return k
tally = collections.Counter(); grp = collections.defaultdict(collections.Counter)
for q in sorted(sel):
    s, a = sel[q], ans.get(q, {})
    k = keyed(q) or {}
    who_a = (k.get("plan_A") or {}).get("bot") or s["plan_A"]
    if who_a != s["plan_A"]: print("KEY/SELECTION DISAGREE on", q)
    c = a.get("choice", "?")
    pick = {"Plan A": who_a, "Plan B": ("km3" if who_a == "kx3" else "kx3")}.get(c, c)
    tally[pick] += 1; grp[s["group"]][pick] += 1
    print(f"{q} {s['group']:5s} {s['deck'][:24]:24s} o{s['own_turn']} | A={who_a:3s} | answer: {c:15s} -> {pick:15s} ({a.get('confidence','')}) | games: kx3 {s['kx_result']}, km3 {s['km3_result']}")
    print(f"     why picked: {s['why']}")
    if a.get("note"): print(f"     note: {a['note']}")
print("\nTotals:", dict(tally))
for g, t in grp.items(): print(g, dict(t))
print("key top-level type:", type(key).__name__, "keys sample:", list(key)[:5] if isinstance(key, dict) else len(key))
