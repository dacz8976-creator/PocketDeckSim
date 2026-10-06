import json, os, re
B = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-06_NEW_PAUSE_GAMES"
S = os.path.dirname(os.path.abspath(__file__))
cov = json.load(open(S + "/cov.json", encoding="utf-8"))
opp_by_game = {}
for n, r in cov["opponent_cards"].items():
    for g in r["games"]:
        opp_by_game.setdefault(g, []).append(n)

CANDS = [("20261004_213625000_iOS", 5), ("20261004_213625000_iOS", 11), ("20261004_214731000_iOS", 6), ("20261005_003547000_iOS", 9),
         ("20261005_031138000_iOS", 6), ("20261005_032023000_iOS", 8), ("20261005_032023000_iOS", 12), ("20261005_032857000_iOS", 4),
         ("20261005_034229000_iOS", 5), ("20261005_034229000_iOS", 7), ("20261005_034953000_iOS", 6), ("20261005_183108000_iOS", 9),
         ("20261006_012140000_iOS", 6), ("20261006_020518000_iOS", 11), ("20261006_020518000_iOS", 15), ("20261006_020518000_iOS", 17),
         ("20261005_123812000_iOS", 7), ("20261004_214731000_iOS", 8)]
for g, tn in CANDS:
    L = json.load(open(f"{B}/{g}/TURN_LEDGER.json", encoding="utf-8"))
    t = next(x for x in L["turns"] if x["turn_number"] == tn)
    ts = [p.get("timestamp_seconds") for p in (t.get("plays_in_order") or []) if p.get("timestamp_seconds") is not None]
    h = t.get("hand_at_start") or {}
    names = [c.get("name") if isinstance(c, dict) else c for c in (h.get("cards_left_to_right") or [])]
    oh = t.get("opponent_hand_at_owner_turn_start") or {}
    print(f"{g[:15]} t{tn}: seconds {min(ts) if ts else None}-{max(ts) if ts else None}; hand {h.get('status')} {names}; opp hand count {oh.get('count')}")
    print("    opp cards seen in game:", sorted(n for n in opp_by_game.get(g[:15], []) if n))
