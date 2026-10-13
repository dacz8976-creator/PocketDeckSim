import sys, os, json, glob, collections
sys.dont_write_bytecode = True
sys.path.insert(0, '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/harness')
import ledger_to_positions as L
QA = '/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/'
R = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/'
P = json.load(open(R + 'positions_all.json', encoding='utf-8'))
byid = {}
for c in L.CARDS:
    byid[str(c.get('id'))] = c
def sig(c):
    return (json.dumps(c.get('attacks'), sort_keys=True, ensure_ascii=False), json.dumps(c.get('ability'), sort_keys=True, ensure_ascii=False), c.get('hp'))
for b in ['BATCH_2026-10-06_NEW_PAUSE_GAMES', 'BATCH_2026-10-09_NEW_PAUSE_GAMES', 'BATCH_2026-10-11_NEW_PAUSE_GAMES']:
    for g in sorted(glob.glob(QA + b + '/*/')):
        if not (os.path.exists(g + 'TURN_LEDGER.json') and os.path.exists(g + 'DECK_USED.json')):
            continue
        d = json.load(open(g + 'DECK_USED.json', encoding='utf-8'))
        cards, energy, src = L.load_deck(d)
        if not cards:
            print(os.path.basename(g.rstrip('/')), 'no deck')
            continue
        byname = collections.defaultdict(collections.Counter)
        for n, v in cards:
            byname[n][v] += 1
        short = os.path.basename(g.rstrip('/')).replace('_iOS', '')[2:]
        for n, vs in byname.items():
            if len(vs) > 1:
                sigs = {v: sig(byid.get(v.split(' ', 0)[0] if False else v, {})) for v in vs if v}
                # look up by id string 'A3 096'
                distinct = len({sig(byid[v]) if v in byid else ('missing', v) for v in vs if v}) > 1
                dfile = R + 'decks/KW' + short + '.txt'
                dline = [l.strip() for l in open(dfile, encoding='utf-8')] if os.path.exists(dfile) else None
                dline = [l for l in (dline or []) if n in l]
                npos = [p['id'] for p in P if p['deck'] == 'KW' + short]
                print(short, 'src', src, n, dict(vs), 'distinct' if distinct else 'same', 'deckfile', dline, 'positions', len(npos))
print('ids sample', list(byid)[:3])
