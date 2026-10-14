import json
P = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-12_NEW_LONG_VIDEOS/20261012_010706000_iOS/TURN_LEDGER.json"
L = json.load(open(P, encoding='utf-8'))
for t in L['turns']:
    if t.get('turn_number') in (9, 10, 11):
        print('=' * 60, 'TURN', t.get('turn_number'), t.get('who_played'))
        for bk in ('board_at_start', 'board_after'):
            s = (t.get(bk) or {}).get('owner') or {}
            a = s.get('active') or {}
            print(bk, 'ACTIVE', a.get('name'), a.get('hp_now'), json.dumps(a.get('attached_energy'), ensure_ascii=False), a.get('tool'))
            for b in s.get('bench_in_position_order') or []:
                print('   BENCH', json.dumps({k: b.get(k) for k in ('name', 'bench_position', 'position', 'hp_now', 'attached_energy', 'tool', 'pokemon')}, ensure_ascii=False)[:300])
        if t.get('turn_number') == 9:
            for p in t.get('plays_in_order') or []:
                print('PLAY', json.dumps(p, ensure_ascii=False)[:900])
