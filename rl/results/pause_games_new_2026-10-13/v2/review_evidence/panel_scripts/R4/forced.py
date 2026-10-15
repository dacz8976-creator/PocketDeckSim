import json, os
V2 = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/"
s = json.load(open(V2 + "runs_forced/forced_summary.json", encoding="utf-8"))
for x in s:
    if x['id'].startswith(('KW-261012_210823000', 'KW-261013_022530000')):
        print("=" * 80)
        print(x['id'], "force=", x['force'], "note=", x['note'])
        for r in x['rows']:
            print("   ", json.dumps(r, ensure_ascii=False))
        print("  first_dev", json.dumps(x['first_deviation'], ensure_ascii=False))
# per-position forced record for t08, seed 1
for pid in ('KW-261012_210823000-t08', 'KW-261012_210823000-t04', 'KW-261012_210823000-t02'):
    f = V2 + "runs_forced/forced_%s.json" % pid
    if os.path.exists(f):
        recs = json.load(open(f, encoding="utf-8"))
        if recs:
            print("#" * 60, pid)
            print(json.dumps(recs[0], ensure_ascii=False)[:3000])
