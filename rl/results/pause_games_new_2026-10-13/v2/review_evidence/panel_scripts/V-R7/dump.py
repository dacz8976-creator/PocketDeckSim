import json, sys, os
QA = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-13_REMAINING_SIX"
POS = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/positions_all.json"
game = sys.argv[1]  # e.g. 20261013_020824000
turns = [int(x) for x in sys.argv[2].split(",")]
mode = sys.argv[3] if len(sys.argv) > 3 else "both"
led = json.load(open(f"{QA}/{game}_iOS/TURN_LEDGER.json"))
if isinstance(led, dict):
    print("ledger keys:", list(led.keys()))
    rows = led.get("turns") or led.get("rows") or led.get("ledger")
else:
    rows = led
if mode in ("both", "led"):
    for r in rows:
        t = r.get("turn") or r.get("turn_number")
        if t in turns:
            print("=" * 30, "TURN", t)
            print(json.dumps(r, indent=1, ensure_ascii=False))
if mode in ("both", "pos"):
    pos = json.load(open(POS))
    short = "KW-26" + game[4:]
    for p in pos:
        for t in turns:
            if p.get("id") == f"{short}-t{t:02d}":
                print("#" * 30, p["id"])
                print(json.dumps(p, indent=1, ensure_ascii=False))
