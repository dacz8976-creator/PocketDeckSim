import csv, json
P = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/"
rows = list(csv.DictReader(open(P + "position_list.tsv", encoding="utf-8"), delimiter="\t"))
for r in rows:
    if "010706" in r["position_id"] or "015011" in r["position_id"]:
        print("====", r["position_id"])
        for k, v in r.items():
            if k in ("position_id",):
                continue
            print("  %s: %s" % (k, v))
# switch2 flags anywhere: which positions flagged and why
print("\n#### all switch2 yes:")
for r in rows:
    if r["switch2_flag"] not in ("no", ""):
        print(r["position_id"], "|", r["switch2_flag"], "|", r["switch2_in_his_deck"], "|", r["switch2_in_his_cards_here"], "|", r["switch2_opponent_board"], "|", r["switch2_opponent_possible"])
gm = json.load(open(P + "games_meta.json", encoding="utf-8"))
print("\n#### games_meta")
for k in gm if isinstance(gm, dict) else []:
    if "010706" in k or "015011" in k:
        print(k, json.dumps(gm[k], ensure_ascii=False))
if isinstance(gm, list):
    for g in gm:
        if "010706" in json.dumps(g) or "015011" in json.dumps(g):
            print(json.dumps(g, ensure_ascii=False))
