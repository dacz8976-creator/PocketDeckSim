import json, glob, sys
D = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/runs_km3/"
for f in sorted(glob.glob(D + 'out_KW-*' + sys.argv[1] + '*.jsonl')):
    for l in open(f, encoding='utf-8'):
        d = json.loads(l)
        if d.get('kind') == 'position':
            s = d['summary']
            print(d['id'], 'problems', d.get('problems'))
            for side in ('me', 'opp'):
                print('  ', side, [(b['card'], b['id'], b['hp'], b.get('tools'), b.get('behind')) for b in s[side]['board']])
