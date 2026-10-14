import json, os
R8 = '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/panel14/R8'
V2 = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2'
P = {p['id']: p for p in json.load(open(V2 + '/positions_all.json', encoding='utf-8'))}
games = [l.strip() for l in open(os.path.join(R8, 'games.txt')) if l.strip()]
for g in games:
    short = os.path.basename(g).replace('_iOS', '')[2:]
    led = json.load(open(os.path.join(g, 'TURN_LEDGER.json'), encoding='utf-8'))
    for t in led['turns']:
        if not str(t.get('who_played', '')).startswith('owner'):
            continue
        oh = t.get('opponent_hand_at_owner_turn_start') or {}
        pid = f'KW-{short}-t{t["turn_number"]:02d}'
        pc = P.get(pid, {}).get('opp', {}).get('hand_count')
        extra = {k: t.get(k) for k in ('opponent_hand_count', 'hand_arithmetic') if t.get(k) is not None}
        if oh.get('count') is None or extra or oh.get('inferred_count') is not None:
            print(pid, 'pos', pc, '| count', oh.get('count'), 'range', oh.get('supported_range'), 'inferred', oh.get('inferred_count'), '| basis', str(oh.get('basis'))[:60], '| limit', str(oh.get('limit_reason'))[:150], '|', json.dumps(extra, ensure_ascii=False)[:200])
