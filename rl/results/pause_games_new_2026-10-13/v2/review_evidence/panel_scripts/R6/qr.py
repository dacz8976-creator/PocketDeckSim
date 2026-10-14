import json
base = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-13_REMAINING_SIX/"
for g in ["20261013_010837000_iOS", "20261013_014423000_iOS"]:
    print("=" * 60, g)
    q = json.load(open(base + g + "/QR_DECODE.json", encoding="utf-8"))
    print("keys:", list(q.keys()))
    cards = q.get("cards") or (q.get("decoded") or {}).get("cards") or []
    tot = 0
    for c in cards:
        print("  ", c.get("count"), c.get("name"), c.get("entity_kind"), c.get("entity_id"), c.get("printing_aliases"))
        tot += c.get("count") or 0
    print("total", tot)
    dec = q.get("decoded") or {}
    print("energy:", dec.get("energy"), "slot count:", q.get("card_slot_count"))
    for k in ("status", "binding", "notes", "limits", "roundtrip"):
        if k in q:
            print(k, json.dumps(q[k], ensure_ascii=False)[:600])
import os
for f in ["20261013_010837000_iOS/DECK_LOG_SNAPSHOT.json", "20261013_010837000_iOS/DECK_LOG_SNAPSHOT.live_20261013.json", "20261013_014423000_iOS/DECK_LOG_SNAPSHOT.live_20261013.json"]:
    print("=" * 60, f)
    s = json.load(open(base + f, encoding="utf-8"))
    print(json.dumps(s, ensure_ascii=False)[:2500])
