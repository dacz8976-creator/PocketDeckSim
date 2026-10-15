import json
BASE = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/"
G = {
 "010706": ("BATCH_2026-10-12_NEW_LONG_VIDEOS/20261012_010706000_iOS", 9),
 "203719": ("BATCH_2026-10-12_NEW_LONG_VIDEOS/20261012_203719000_iOS", 7),
 "210823": ("BATCH_2026-10-12_NEW_LONG_VIDEOS/20261012_210823000_iOS", 8),
 "230258": ("BATCH_2026-10-12_ADDITIONAL_TWO/20261012_230258000_iOS", 11),
}
def mons(side):
    out = []
    if not side:
        return out
    a = side.get("active")
    if a:
        out.append(("A", a))
    for b in side.get("bench_in_position_order") or []:
        out.append(("B%s" % b.get("bench_position"), b))
    return out
for g, (folder, tn) in G.items():
    d = json.load(open(BASE + folder + "/TURN_LEDGER.json", encoding="utf-8"))
    for t in d["turns"]:
        if t["turn_number"] != tn:
            continue
        print("=" * 20, g, "turn", tn)
        for key in ("board_at_start", "board_after"):
            b = t.get(key) or {}
            print(" --", key)
            for pos, m in mons(b.get("owner")):
                print("   own %s %s | hp %s/%s | E %s" % (pos, m.get("name"), m.get("hp_now"), m.get("hp_max"), (m.get("attached_energy") or {}).get("by_type")))
        for p in t.get("plays_in_order") or []:
            if (p.get("kind") or "").lower() in ("attack",) or "Giga" in json.dumps(p, ensure_ascii=False):
                print("   PLAY", json.dumps({k: p.get(k) for k in ("order", "kind", "card_name", "target", "result", "nested_events_in_order", "response", "prompt_text")}, ensure_ascii=False))
        for a in t.get("automatic_events_in_order") or []:
            if "Colorless" in json.dumps(a, ensure_ascii=False) or "Giga" in json.dumps(a, ensure_ascii=False):
                print("   AUTO", a)
