import json, sys
QA = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-13_REMAINING_SIX"
game = sys.argv[1]
led = json.load(open(f"{QA}/{game}_iOS/TURN_LEDGER.json"))
print("top keys", list(led.keys()))
for k in led:
    if k != "turns":
        print(k, json.dumps(led[k], ensure_ascii=False)[:1500])
for t in led["turns"]:
    print("T", t["turn_number"], t["who_played"], "hand_arith:", json.dumps(t.get("hand_arithmetic"), ensure_ascii=False)[:700])
    b = t.get("board_at_start") or {}
    o = b.get("opponent") or {}
    act = o.get("active") or {}
    print("    opp board start: active", act.get("name"), act.get("hp_now"), "bench", [(x.get("name"), x.get("bench_position")) for x in o.get("bench_in_position_order") or []], "| stadium", b.get("stadium"))
    for k in t:
        if "opponent" in k.lower() and k != "opponent_hand_at_owner_turn_start":
            print("    ", k, json.dumps(t[k], ensure_ascii=False)[:400])
