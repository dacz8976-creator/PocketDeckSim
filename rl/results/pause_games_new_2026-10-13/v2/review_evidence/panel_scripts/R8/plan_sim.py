"""simulate each position's his_plan on the board by index (engine-like: Place fills first empty slot, Retreat swaps 0 and i, Evolve renames) and print every indexed step with
the ledger play it should correspond to (matched by order of plan-producing plays), flagging when the Pokemon at the index is not named in that play's text"""
import json, os, re, sys
sys.path.insert(0, '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/harness')
import cardlib as C
R8 = '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/panel14/R8'
V2 = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2'
P = json.load(open(V2 + '/positions_all.json', encoding='utf-8'))
games = {os.path.basename(l.strip()).replace('_iOS', '')[2:]: l.strip() for l in open(os.path.join(R8, 'games.txt')) if l.strip()}


def cname(s):
    m = re.search(r'([A-Z][A-Za-z0-9\-]{0,4} \d{3})$', s)
    return s[:-len(m.group(1))].strip() if m else s


for p in P:
    short = p['game'][3:]
    led = json.load(open(os.path.join(games[short], 'TURN_LEDGER.json'), encoding='utf-8'))
    t = next(x for x in led['turns'] if x['turn_number'] == p['turn_count'] and str(x.get('who_played')).startswith('owner'))
    plays = [q for q in t.get('plays_in_order') or [] if str(q.get('kind')) not in ('end_turn', 'end_turn_request', 'prompt_response', 'menu_open', 'concession', 'promotion', 'replacement_choice')]
    slots = [cname(b['card']) for b in p['me']['board']] + [None] * (4 - len(p['me']['board']))
    out = []
    flag = False
    for s in p['his_plan']:
        m = re.match(r'(\w+):(.*)$', s)
        kind, arg = (m.group(1), m.group(2)) if m else (s, '')
        idx = None
        mi = re.search(r'@(\d)', arg)
        if mi:
            idx = int(mi.group(1))
        info = ''
        if kind == 'Place':
            j = next((k for k in range(1, 4) if slots[k] is None), None)
            if j is not None:
                slots[j] = arg
            info = f'-> slot {j}'
        elif kind == 'Retreat':
            i = int(arg)
            info = f'swap {slots[0]} <-> {slots[i]}'
            slots[0], slots[i] = slots[i], slots[0]
        elif kind == 'Evolve' and idx is not None:
            info = f'{slots[idx]} -> {arg.split("@")[0]}'
            slots[idx] = arg.split('@')[0]
        elif idx is not None:
            info = f'on {slots[idx]}'
        out.append(f'      {s:40s} {info}')
    print(p['id'], '| board', [cname(b['card']) for b in p['me']['board']])
    for o in out:
        print(o)
    for q in t.get('plays_in_order') or []:
        print(f"         L {q.get('kind')} | {q.get('card_name')} | tgt={str(q.get('target'))[:45]} | {str(q.get('result') or q.get('details') or '')[:110]}")
