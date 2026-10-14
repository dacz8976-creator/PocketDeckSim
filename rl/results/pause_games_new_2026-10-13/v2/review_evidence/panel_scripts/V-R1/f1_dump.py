import json, sys
P = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-13_REMAINING_SIX/20261013_015011000_iOS/TURN_LEDGER.json"
L = json.load(open(P, encoding='utf-8'))
print(type(L), list(L.keys()) if isinstance(L, dict) else len(L))
turns = L.get('turns') if isinstance(L, dict) else L
print('n turns', len(turns))
for t in turns:
    print('=' * 100)
    print('TURN', t.get('turn') or t.get('turn_number'), 'actor', t.get('actor') or t.get('side') or t.get('player'))
    print('keys', list(t.keys()))
    for bk in ('board_at_start', 'board_after'):
        b = t.get(bk) or {}
        for side in ('owner', 'opponent'):
            s = b.get(side) or {}
            print(f'--- {bk}.{side}: keys', list(s.keys()))
            print('   active:', json.dumps(s.get('active'), ensure_ascii=False)[:600])
            print('   bench:', json.dumps(s.get('bench_in_position_order'), ensure_ascii=False)[:1500])
            print('   energy_zone:', json.dumps(s.get('energy_zone'), ensure_ascii=False))
            for k in s:
                if k not in ('active', 'bench_in_position_order', 'energy_zone'):
                    print('   ', k, ':', json.dumps(s.get(k), ensure_ascii=False)[:400])
    for i, p in enumerate(t.get('plays_in_order') or []):
        print('  PLAY', i + 1, json.dumps(p, ensure_ascii=False)[:800])
    for k in t:
        if k not in ('board_at_start', 'board_after', 'plays_in_order'):
            print('  ', k, ':', json.dumps(t.get(k), ensure_ascii=False)[:600])
