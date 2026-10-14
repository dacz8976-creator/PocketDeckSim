import json, os, re
R8 = '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/panel14/R8'
V2 = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2'
P = {p['id']: p for p in json.load(open(V2 + '/positions_all.json', encoding='utf-8'))}
NOTHING_FOUND = re.compile(r'no[\s-]*effect|no[\s-]*target|no eligible|nothing|no card', re.I)
games = [l.strip() for l in open(os.path.join(R8, 'games.txt')) if l.strip()]
for g in games:
    short = os.path.basename(g).replace('_iOS', '')[2:]
    led = json.load(open(os.path.join(R8, 'norm', os.path.basename(g), 'TURN_LEDGER.json'), encoding='utf-8'))
    for t in led['turns']:
        if not str(t.get('who_played', '')).startswith('owner'):
            continue
        for i, p in enumerate(t.get('plays_in_order') or []):
            cn = str(p.get('card_name') or '').replace('Poke Ball', 'Poké Ball')
            if cn == 'Poké Ball':
                res = str(p.get('result') or '')
                pid = f'KW-{short}-t{t["turn_number"]:02d}'
                plan = P.get(pid, {}).get('his_plan')
                n_balls = sum(1 for s in (plan or []) if s == 'Play:Poké Ball')
                print(f'{pid} [{i}] matched_nothing={bool(NOTHING_FOUND.search(res))} balls_in_plan={n_balls} | {res[:120]}')
