import json, re, glob, os
Q = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/"
NOTHING_FOUND = re.compile(r'no[\s-]*effect|no[\s-]*target|no eligible|nothing|no card', re.I)
V = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/positions_all.json"
pos = {p['id']: p for p in json.load(open(V, encoding='utf-8'))}
for g in sorted(glob.glob(Q + "BATCH_2026-10-1[23]_*/2026101*_iOS/TURN_LEDGER.json")):
    gid = os.path.basename(os.path.dirname(g))
    led = json.load(open(g, encoding="utf-8"))
    for t in led['turns']:
        if not str(t.get('who_played', '')).startswith('owner'):
            continue
        for i, p in enumerate(t.get('plays_in_order') or []):
            if 'ball' in str(p.get('card_name') or '').lower():
                res = str(p.get('result') or '') + ' || ' + str(p.get('details') or '')
                found = re.search(r'\b(find|found|finds|search\w*|take|takes|reveal\w*)\b', res, re.I)
                nf = bool(NOTHING_FOUND.search(str(p.get('result') or '')))
                flag = ''
                if re.search(r'\bno\b', res, re.I):
                    flag = '  <-- has "no"'
                pid = 'KW-' + gid[2:15] + '-t%02d' % t.get('turn_number')
                plan = pos.get(pid, {}).get('his_plan')
                print(gid, 't', t.get('turn_number'), 'play', i, 'NF=' + str(nf), repr(res)[:200], flag)
                if flag or nf:
                    print('      plan:', plan)
                    # following search events
                    for ev in t.get('automatic_events_in_order') or []:
                        s = json.dumps(ev, ensure_ascii=False)
                        if 'search' in s.lower() or 'ball' in s.lower():
                            print('      EV', s[:300])
