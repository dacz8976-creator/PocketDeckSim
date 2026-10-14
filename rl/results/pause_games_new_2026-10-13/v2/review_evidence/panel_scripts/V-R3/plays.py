import json, sys
B = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/"
games = {
    "210041": B + "BATCH_2026-10-12_NEW_LONG_VIDEOS/20261012_210041000_iOS/TURN_LEDGER.json",
    "230258": B + "BATCH_2026-10-12_ADDITIONAL_TWO/20261012_230258000_iOS/TURN_LEDGER.json",
    "210823": B + "BATCH_2026-10-12_NEW_LONG_VIDEOS/20261012_210823000_iOS/TURN_LEDGER.json",
}
which = sys.argv[1]
turns = [int(x) for x in sys.argv[2].split(",")]
keys = sys.argv[3].split(",") if len(sys.argv) > 3 else ["plays_in_order", "automatic_events_in_order"]
L = json.load(open(games[which], encoding="utf-8"))
for r in L["turns"]:
    if r["turn_number"] in turns:
        print("=== turn", r["turn_number"], r["who_played"])
        for k in keys:
            print("--", k)
            print(json.dumps(r.get(k), indent=1, ensure_ascii=False))
