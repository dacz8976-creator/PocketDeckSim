"""opp_track.py GAME NAME: every appearance of an opponent Pokemon of that name in the ledger (row, key, slot, variant, hp, ids) and what each position used"""
import json, os, sys, re
R8 = '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/panel14/R8'
V2 = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2'
games = [l.strip() for l in open(os.path.join(R8, 'games.txt')) if l.strip()]
g = next(x for x in games if sys.argv[1] in x)
name = sys.argv[2]
side = sys.argv[3] if len(sys.argv) > 3 else 'opponent'
led = json.load(open(os.path.join(g, 'TURN_LEDGER.json'), encoding='utf-8'))
for t in led['turns']:
    for key in ('board_at_start', 'board_after'):
        s = ((t.get(key) or {}).get(side) or {})
        for slot, p in [('A', s.get('active'))] + [(f'B', q) for q in s.get('bench_in_position_order') or []]:
            if isinstance(p, dict) and name.lower() in str(p.get('name', '')).lower():
                print(f"t{t['turn_number']} {t['who_played'][:5]} {key[:12]} {slot}{p.get('bench_position')} {p.get('name')} | var={p.get('variant')!r} hp={p.get('hp_now')}/{p.get('hp_max')} id={p.get('instance_id')} E={p.get('attached_energy', {}).get('by_type')} tool={p.get('tool')} cond={p.get('special_conditions')}")
    for p in t.get('plays_in_order') or []:
        if name.lower() in json.dumps(p, ensure_ascii=False).lower():
            print(f"   t{t['turn_number']} PLAY {p.get('kind')} {p.get('card_name')} tgt={p.get('target')} | {str(p.get('result') or p.get('details'))[:200]}")
P = json.load(open(V2 + '/positions_all.json', encoding='utf-8'))
short = os.path.basename(g).replace('_iOS', '')[2:]
for p in P:
    if p['game'] == 'kw-' + short:
        bd = p['opp' if side == 'opponent' else 'me']['board']
        print(p['id'], [(i, x['card'], x['hp'], x.get('tools'), x.get('behind')) for i, x in enumerate(bd) if name.lower() in x['card'].lower()])
