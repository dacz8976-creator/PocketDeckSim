import json
R8 = '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/panel14/R8'
V2 = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2'
A = {p['id']: p for p in json.load(open(V2 + '/positions_all.json', encoding='utf-8'))}
B = {p['id']: p for p in json.load(open(R8 + '/reconv/positions_all.json', encoding='utf-8')) if p['id'] in A or p['id'][3:9] in ('261012', '261013') and p['id'][10:16] in ('010706', '203719', '210041', '210823', '225319', '230258', '022530', '030351', '010003', '010837', '014423', '015011', '015659', '020824')}
print('committed', len(A), 'rerun (14 games)', len(B), 'only committed', sorted(set(A) - set(B)), 'only rerun', sorted(set(B) - set(A)))
nd = 0
for k in sorted(A):
    if k not in B:
        continue
    a, b = A[k], B[k]
    diffs = [f for f in sorted(set(a) | set(b)) if a.get(f) != b.get(f)]
    for side in ('me', 'opp'):
        if side in diffs:
            diffs.remove(side)
            diffs += [f'{side}.{x}' for x in sorted(set(a[side]) | set(b[side])) if a[side].get(x) != b[side].get(x)]
    if diffs:
        nd += 1
        print(k, diffs)
        for d in diffs:
            if d.startswith(('me.', 'opp.')):
                s, f = d.split('.')
                print('    committed:', json.dumps(a[s].get(f), ensure_ascii=False)[:300])
                print('    rerun    :', json.dumps(b[s].get(f), ensure_ascii=False)[:300])
            elif d == 'notes':
                print('    committed:', a['notes'][:400])
                print('    rerun    :', b['notes'][:400])
print('positions differing:', nd)
