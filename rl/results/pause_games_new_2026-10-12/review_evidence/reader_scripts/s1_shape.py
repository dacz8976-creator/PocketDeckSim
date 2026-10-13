import sys, json, collections
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *

print(len(GAMES), 'games;', len(POS), 'positions')
print('pos keys', list(POS[0].keys()))
print(json.dumps(POS[0], ensure_ascii=False)[:3000])
# key shapes across all ledgers
tk = collections.Counter(); bk = collections.Counter(); pk = collections.Counter(); playk = collections.Counter(); kinds = collections.Counter()
hk = collections.Counter(); ohk = collections.Counter(); ezk = collections.Counter()
for g in GAMES:
    L = led(g)
    for t in L['turns']:
        tk.update(t.keys())
        b = t.get('board_at_start') or {}
        bk.update(b.keys())
        for side in ('owner', 'opponent'):
            s = b.get(side) or {}
            for k in s.keys():
                bk['side.' + k] += 1
            act = s.get('active')
            if isinstance(act, dict):
                pk.update(act.keys())
            for p in s.get('bench_in_position_order') or []:
                if isinstance(p, dict):
                    pk.update('bench.' + k for k in p.keys())
        for p in t.get('plays_in_order') or []:
            playk.update(p.keys())
            kinds[(str(t.get('who_played'))[:5], p.get('kind'))] += 1
        hk.update((t.get('hand_at_start') or {}).keys())
        ohk.update((t.get('opponent_hand_at_owner_turn_start') or {}).keys())
print('turn keys', tk.most_common())
print('board keys', bk.most_common())
print('pokemon keys', pk.most_common())
print('play keys', playk.most_common())
print('kinds', sorted(kinds.items(), key=lambda x: -x[1]))
print('hand keys', hk.most_common())
print('opp hand keys', ohk.most_common())
