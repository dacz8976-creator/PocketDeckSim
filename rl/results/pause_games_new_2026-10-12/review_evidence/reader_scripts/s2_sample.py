import sys, json, collections
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
g = GBY[sys.argv[1]]
L = led(g)
print('top keys', list(L.keys()))
tn = int(sys.argv[2])
for t in L['turns']:
    if t['turn_number'] == tn:
        for k in ('who_played', 'hand_at_start', 'owner_hand_start', 'board_at_start', 'plays_in_order', 'opponent_hand_at_owner_turn_start', 'limits', 'draws_and_searches'):
            v = t.get(k)
            s = json.dumps(v, ensure_ascii=False, indent=1)
            print('====', k, len(s))
            print(s[:int(sys.argv[3]) if len(sys.argv) > 3 else 6000])
