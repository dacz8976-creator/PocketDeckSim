import json, sys
QA = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-13_REMAINING_SIX"
game = sys.argv[1]
lo, hi = (int(x) for x in sys.argv[2].split("-"))
led = json.load(open(f"{QA}/{game}_iOS/TURN_LEDGER.json"))
HANDKEYS = None
for t in led["turns"]:
    tn = t.get("turn_number")
    if not (lo <= tn <= hi):
        continue
    print("=" * 20, "TURN", tn, t.get("who_played"), "timing", (t.get("timing") or {}).get("turn_start_seconds"))
    for k, v in t.items():
        kl = k.lower()
        if "opponent" in kl and "hand" in kl or kl in ("opponent_hand_count",) or ("hand" in kl and "count" in kl):
            print("  ", k, "=", json.dumps(v, ensure_ascii=False)[:600])
    for k in ("hand_reconciliation", "opponent_hand_reconciliation"):
        if k in t:
            print("  ", k, "=", t[k])
    for d in t.get("draws_and_searches") or []:
        print("   DRAW", d.get("kind"), d.get("caused_by"), d.get("count"), [c.get("name") for c in d.get("cards_in_reveal_order") or []], d.get("basis"), d.get("limit_reason"))
    for p in t.get("plays_in_order") or []:
        print("   PLAY", p.get("order"), p.get("kind"), "|", p.get("card_name"), "|", p.get("details"), "|", p.get("result"), "|", p.get("target"), "| hc_after", p.get("hand_count_after"), "|", p.get("timestamp_seconds"), p.get("evidence_ids"))
        for ne in p.get("nested_events_in_order") or []:
            print("       nested", json.dumps(ne, ensure_ascii=False)[:300])
    for e in t.get("automatic_events_in_order") or []:
        print("   AUTO", json.dumps(e, ensure_ascii=False)[:300])
    for k in ("limits",):
        if t.get(k):
            print("   LIMITS", json.dumps(t[k], ensure_ascii=False)[:800])
    # other keys
    others = [k for k in t.keys() if k not in ("plays_in_order", "board_at_start", "board_after", "draws_and_searches", "automatic_events_in_order", "hand_at_start", "owner_hand_start", "owner_hand_end", "owner_hand_before_end_action", "timing", "limits")]
    print("   keys:", others)
