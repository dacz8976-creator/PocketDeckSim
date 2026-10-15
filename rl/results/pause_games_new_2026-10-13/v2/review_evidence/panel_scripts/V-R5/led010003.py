import json, sys
P = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-13_REMAINING_SIX/20261013_010003000_iOS/TURN_LEDGER.json"
d = json.load(open(P, encoding="utf-8"))
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
for t in d["turns"]:
    tn = t["turn_number"]
    if tn not in (8, 9, 10, 11):
        continue
    print("=" * 30, "turn", tn, t["who_played"])
    for key in ("board_at_start", "board_after"):
        b = t.get(key) or {}
        print(" --", key, "stadium:", b.get("stadium"), "| phase:", b.get("phase"))
        for side in ("owner", "opponent"):
            for pos, m in mons(b.get(side)):
                print("   %s %s %s | %s | hp %s/%s | E %s | tool %s" % (side[:3], pos, m.get("instance_id"), m.get("variant"), m.get("hp_now"), m.get("hp_max"), (m.get("attached_energy") or {}).get("by_type"), m.get("tool")))
    print(" -- plays")
    for p in t.get("plays_in_order") or []:
        print("   ", json.dumps({k: v for k, v in p.items() if k not in ("evidence_ids", "source_video")}, ensure_ascii=False))
    print(" -- auto")
    for a in t.get("automatic_events_in_order") or []:
        print("   ", a)
