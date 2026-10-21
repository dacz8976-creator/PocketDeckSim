import json, os, glob, sys, collections, re
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import l2p_copy as L
BASE = '/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA'
SRC = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12'
POS = {p['id']: p for p in json.load(open(SRC + '/positions_all.json', encoding='utf-8'))}
want = sys.argv[1]
names_filter = set(sys.argv[2].split(',')) if len(sys.argv) > 2 and sys.argv[2] else None
show_plays = '--plays' in sys.argv
g = [x for x in glob.glob(BASE + '/BATCH_2026-10-*_NEW_PAUSE_GAMES/2026*_iOS') if want in x][0]
led = json.load(open(g + '/TURN_LEDGER.json', encoding='utf-8'))
short = os.path.basename(g).replace('_iOS', '')[2:]
def f(name):
    return names_filter is None or L.nname(name) in names_filter
for t in led['turns']:
    if not str(t.get('who_played', '')).startswith('owner'):
        continue
    tn = t['turn_number']
    pid = f'KW-{short}-t{tn:02d}'
    print(f'--- turn {tn} ({t.get("who_played")}) position {pid} {"PRESENT" if pid in POS else "absent"}')
    hs = t.get('hand_at_start') or {}
    for i, c in enumerate(hs.get('cards_left_to_right') or []):
        if isinstance(c, dict) and f(c.get('name')):
            print(f'   hand[{i}] {c.get("name")!r} variant={c.get("variant")!r} ' + ' '.join(f'{k}={c[k]!r}' for k in c if k in ('card_variant', 'printing', 'hp_max', 'id')))
        elif isinstance(c, str) and f(c):
            print(f'   hand[{i}] {c!r}')
    for side in ('board_at_start',):
        b = (t.get(side) or {}).get('owner') or {}
        for p in L.instances(b):
            if f(p.get('name')):
                print(f'   {side} owner {p.get("name")!r} variant={p.get("variant")!r} hp_now={p.get("hp_now")} hp_max={p.get("hp_max")} pos={p.get("bench_position")}')
        be = (t.get(side) or {}).get('board_effects') or (t.get(side) or {}).get('effects')
        if be:
            print(f'   {side} board_effects: {json.dumps(be, ensure_ascii=False)[:400]}')
    if show_plays:
        for p in t.get('plays_in_order') or []:
            print(f'   play {p.get("order")} {p.get("kind")} {p.get("card_name")!r} var={p.get("card_variant")!r} tgt={p.get("target")!r} res={str(p.get("result"))[:150]!r}')
    if pid in POS:
        P = POS[pid]
        print('   POS hand:', [c for c in P['me']['hand'] if f(c.rsplit(' ', 2)[0])])
        for i, bd in enumerate(P['me']['board']):
            if f(bd['card'].rsplit(' ', 2)[0]) or any(f(x.rsplit(' ', 2)[0]) for x in bd.get('behind', [])):
                print(f'   POS board[{i}]:', bd['card'], 'hp', bd['hp'], 'behind', bd.get('behind'))
        print('   POS plan:', P['his_plan'])
