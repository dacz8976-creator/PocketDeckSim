import sys, json
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
conv = {p['game'][3:] for p in POS}
for g in GAMES:
    d = deck(g)
    s = short_of(g)
    n = sum(1 for p in POS if p['game'][3:] == s)
    print(s, 'positions', n, '| status:', d.get('exact_list_status') or d.get('source_deck_status'), '| conflicts:', json.dumps(d.get('conflicts_with_filmed_cards'), ensure_ascii=False)[:220])
