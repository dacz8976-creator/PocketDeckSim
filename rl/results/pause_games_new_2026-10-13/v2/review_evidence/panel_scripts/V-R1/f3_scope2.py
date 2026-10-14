import json, collections, os
V2 = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/"
QA = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/"
meta = json.load(open(V2 + 'games_meta.json', encoding='utf-8'))
pos = {p['id']: p for p in json.load(open(V2 + 'positions_all.json', encoding='utf-8'))}
for pid in ('KW-261012_010706000-t09', 'KW-261012_203719000-t07', 'KW-261012_210823000-t08', 'KW-261012_230258000-t11', 'KW-261013_010003000-t09'):
    g = 'kw-' + pid[3:].rsplit('-t', 1)[0]
    tn = int(pid.rsplit('-t', 1)[1])
    L = json.load(open(QA + meta[g]['folder'] + '/TURN_LEDGER.json', encoding='utf-8'))
    row = [t for t in L['turns'] if t.get('turn_number') == tn][0]
    print('#' * 10, pid, 'board', [b['card'] for b in pos[pid]['me']['board']])
    for p in row.get('plays_in_order') or []:
        if str(p.get('kind')).lower().startswith('attack'):
            print('   LEDGER attack:', json.dumps({k: p.get(k) for k in ('card_name', 'target', 'result', 'details', 'nested_events_in_order', 'prompt_text', 'response')}, ensure_ascii=False)[:700])
    f = V2 + 'runs_forced/forced_' + pid + '.json'
    if os.path.exists(f):
        R = json.load(open(f, encoding='utf-8'))
        c = collections.Counter()
        legal = None
        for r in R:
            last = r['steps'][-1]
            c[last.get('next_choice_km3')] += 1
            legal = last.get('legal')
        print('   forced: last legal', legal, '| km3 next', dict(c))
