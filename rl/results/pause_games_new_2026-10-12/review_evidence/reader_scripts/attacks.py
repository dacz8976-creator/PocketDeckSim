import json, os, glob, sys, collections, re
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import l2p_copy as L
SRC = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12'
BASE = '/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA'
POS = json.load(open(SRC + '/positions_all.json', encoding='utf-8'))
gdirs = {os.path.basename(g).replace('_iOS', '')[2:]: g for g in glob.glob(BASE + '/BATCH_2026-10-*_NEW_PAUSE_GAMES/2026*_iOS')}
ledcache = {}
alltitles = set()
for c in L.CARDS:
    for a in c.get('attacks', []):
        alltitles.add(a['title'])
n = 0
for P in POS:
    short = P['game'][3:]
    if short not in ledcache:
        ledcache[short] = {t['turn_number']: t for t in json.load(open(gdirs[short] + '/TURN_LEDGER.json', encoding='utf-8'))['turns']}
    t = ledcache[short][P['turn_count']]
    atk = [p for p in (t.get('plays_in_order') or []) if L.nk(p.get('kind')) == 'attack']
    pa = [s for s in P['his_plan'] if s.startswith('Attack:')]
    if not pa or not atk:
        continue
    title = pa[0][7:]
    txt = ' '.join(str(atk[0].get(k) or '') for k in ('card_name', 'card_variant', 'result')).replace('’', "'")
    ok = title.lower() in txt.lower()
    named = [x for x in alltitles if len(x) > 3 and x.lower() in str(atk[0].get('result') or '').replace('’', "'").lower()]
    if not ok:
        n += 1
        print(f"{P['id']}: plan {pa[0]!r}; ledger attack card {atk[0].get('card_name')!r} var {atk[0].get('card_variant')!r} result {str(atk[0].get('result'))[:110]!r}; titles in result {named}; notes: {'last printed attack' in P['notes']}")
print('mismatches', n)
