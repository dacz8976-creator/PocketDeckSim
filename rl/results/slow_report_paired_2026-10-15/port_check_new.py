import sys, json, collections
sys.path.insert(0, '/home/dacz8976/pgfix/rl/strength')
import slow_report_paired as PAIRED
info, name_of, is_tool = PAIRED.load_card_data('/home/dacz8976/pgfix')
P = '/home/dacz8976/pgfix/rl/results/slow_reports/2026-10-12_13-a-ninetales-raticate/games.jsonl'
rows = [json.loads(l) for l in open(P)]
tot = collections.defaultdict(collections.Counter)
for g in rows:
    key = (g['opp'], g['arm'])
    r = PAIRED.charged_idle_turns(g, info)
    t = tot[key]
    t['games'] += 1; t['own_turns'] += r['own_turns']; t['NOATK'] += r['idle']; t['NOATK_ex'] += r['idle_ex']; t['atk'] += r['attacked']; t['warn'] += r['warnings']
    f = PAIRED.first_point(g, info)
    t['scored'] += f['scored']; t['open_ko'] += f['opening_ko']
for k in sorted(tot, key=lambda k: (k[1], k[0])):
    print(k, dict(tot[k]))
