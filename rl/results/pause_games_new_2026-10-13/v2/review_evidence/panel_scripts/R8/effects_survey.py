"""distinct effects the ledgers show at the START of his turns (active_effects on Pokemon, board_effects, shared_effects), with turns; plus deck counts and play kinds"""
import json, os, collections
R8 = '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/panel14/R8'
games = [l.strip() for l in open(os.path.join(R8, 'games.txt')) if l.strip()]
kinds = collections.Counter()
for g in games:
    nm = os.path.basename(g)[2:15]
    led = json.load(open(os.path.join(g, 'TURN_LEDGER.json'), encoding='utf-8'))
    seen = collections.OrderedDict()
    for t in led['turns']:
        for p in t.get('plays_in_order') or []:
            kinds[str(p.get('kind'))] += 1
        if not str(t.get('who_played', '')).startswith('owner'):
            continue
        b = t.get('board_at_start') or {}
        for sd in ('owner', 'opponent'):
            s = b.get(sd) or {}
            for e in s.get('board_effects') or []:
                e = e if isinstance(e, dict) else {'text': e}
                key = (sd, 'BOARD', json.dumps({k: v for k, v in e.items() if k not in ('evidence_ids', 'basis')}, ensure_ascii=False))
                seen.setdefault(key, []).append(t['turn_number'])
            for p in [s.get('active')] + list(s.get('bench_in_position_order') or []):
                if not isinstance(p, dict):
                    continue
                for e in p.get('active_effects') or []:
                    ee = e if isinstance(e, dict) else {'text': e}
                    if ee.get('name') in ('Seal of Antiquity', 'Power of Alchemy'):
                        continue
                    key = (sd, p.get('name'), json.dumps({k: v for k, v in ee.items() if k not in ('evidence_ids', 'basis')}, ensure_ascii=False))
                    seen.setdefault(key, []).append(t['turn_number'])
        for e in b.get('shared_effects') or []:
            key = ('shared', '', json.dumps(e, ensure_ascii=False))
            seen.setdefault(key, []).append(t['turn_number'])
    print('=' * 10, nm)
    for (sd, who, txt), ts in seen.items():
        print(f'  {sd} {who} t{ts}: {txt[:330]}')
print('PLAY KINDS', dict(kinds))

