import json, io, sys, os
R = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/"
for p in (R + "lib/deckgym-database.json", R + "deckgym-database.json"):
    if os.path.exists(p):
        print("DB", p)
        db = json.load(io.open(p, encoding="utf-8"))
        break
pat = sys.argv[1:]
for e in db:
    k, v = next(iter(e.items()))
    s = json.dumps(v, ensure_ascii=False)
    if all(x.lower() in s.lower() for x in pat):
        print(k, s[:600])
