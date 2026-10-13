import json, sys
B = '/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-06_NEW_PAUSE_GAMES/'
D = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/decks/'
for g in sys.argv[1:]:
    d = json.load(open(B + g + '/DECK_USED.json', encoding='utf-8'))
    print('=====', g)
    for k, v in d.items():
        if isinstance(v, list) and v and isinstance(v[0], dict) and ('name' in v[0]):
            print(' ', k, len(v))
            for x in v:
                print('    ', json.dumps({kk: vv for kk, vv in x.items() if kk in ('name', 'variant', 'count', 'entity_id', 'printing', 'printing_aliases', 'set_number', 'id')}, ensure_ascii=False))
        elif isinstance(v, dict):
            for k2, v2 in v.items():
                if isinstance(v2, list) and v2 and isinstance(v2[0], dict) and 'name' in v2[0]:
                    print(' ', k + '.' + k2, len(v2))
                    for x in v2:
                        print('    ', json.dumps({kk: vv for kk, vv in x.items() if kk in ('name', 'variant', 'count', 'entity_id', 'printing', 'printing_aliases')}, ensure_ascii=False))
    short = g.replace('_iOS', '')[2:]
    print('  deck file:', open(D + f'KW{short}.txt', encoding='utf-8').read().replace('\n', ' | '))
