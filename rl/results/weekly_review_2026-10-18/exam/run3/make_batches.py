#!/usr/bin/env python3
"""The build's batches: whole games in time order, cut into N batches of about equal points (mechanical). Metadata only."""
import collections, json, sys
E2 = '/home/dacz8976/exam_v2'
N = int(sys.argv[1]) if len(sys.argv) > 1 else 10
sel = json.load(open(f'{E2}/select/selection.json', encoding='utf-8'))['candidates']
games = collections.OrderedDict()
for c in sorted(sel, key=lambda c: (c['game'], c['global_turn'])):
    games.setdefault(c['game'], []).append(c)
total = len(sel)
batches, cur, acc = [], [], 0
for g, cs in games.items():
    cur.append(g)
    acc += len(cs)
    if acc >= total * (len(batches) + 1) / N and len(batches) < N - 1:
        batches.append(cur)
        cur = []
if cur:
    batches.append(cur)
out = []
for i, gs in enumerate(batches, 1):
    out.append({'batch': i, 'games': [{'game': g, 'folder': games[g][0]['folder'], 'deck': games[g][0]['deck'],
                                        'clips': games[g][0]['clips_in_game'],
                                        'points': [{'point_id': c['point_id'], 'global_turn': c['global_turn'], 'clip': c['clip']} for c in games[g]]}
                                       for g in gs]})
json.dump({'what': 'exam v2 build batches (whole games, time order)', 'batches': out}, open(f'{E2}/build/batches.json', 'w'), indent=1, ensure_ascii=False)
for b in out:
    print(b['batch'], 'games', len(b['games']), 'points', sum(len(g['points']) for g in b['games']),
          'multi-clip', sum(g['clips'] > 1 for g in b['games']))
d = json.load(open(f'{E2}/decks/DECKS.json', encoding='utf-8'))['decks']
print('multi-Energy decks:', {k: v['energy'] for k, v in d.items() if ',' in v['energy']})
