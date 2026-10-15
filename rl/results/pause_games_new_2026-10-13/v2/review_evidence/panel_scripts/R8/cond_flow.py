"""cond_flow.py GAME: per row, conditions on both Actives at start and after, with auto events / attack results mentioning sleep/poison/burn/paraly/confus/wake/checkup"""
import json, os, re, sys
R8 = '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/panel14/R8'
V2 = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2'
P = {p['id']: p for p in json.load(open(V2 + '/positions_all.json', encoding='utf-8'))}
games = [l.strip() for l in open(os.path.join(R8, 'games.txt')) if l.strip()]
KW = re.compile(r'sleep|asleep|poison|burn|paraly|confus|wake|woke|checkup|cure', re.I)
for g in games:
    if sys.argv[1] not in g:
        continue
    short = os.path.basename(g).replace('_iOS', '')[2:]
    led = json.load(open(os.path.join(g, 'TURN_LEDGER.json'), encoding='utf-8'))
    for t in led['turns']:
        def act(key, side):
            a = (((t.get(key) or {}).get(side) or {}).get('active') or {})
            return f"{a.get('name')}{a.get('special_conditions') or ''}"
        print(f"t{t['turn_number']} {t['who_played'][:5]} start: me={act('board_at_start','owner')} opp={act('board_at_start','opponent')} | after: me={act('board_after','owner')} opp={act('board_after','opponent')}")
        for p in t.get('plays_in_order') or []:
            s = str(p.get('result') or p.get('details') or '')
            if KW.search(s):
                print(f"     [{p.get('kind')}] {s[:180]}")
        for e in t.get('automatic_events_in_order') or []:
            s = e if isinstance(e, str) else json.dumps(e, ensure_ascii=False)
            if KW.search(s):
                print(f"     AUTO {s[:220]}")
        pid = f'KW-{short}-t{t["turn_number"]:02d}'
        if pid in P:
            pp = P[pid]
            print(f"     POS me0={pp['me']['board'][0]['card']} {pp['me']['board'][0].get('conditions')} opp0={pp['opp']['board'][0]['card']} {pp['opp']['board'][0].get('conditions')}")
