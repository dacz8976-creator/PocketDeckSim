"""dump_rows.py GAME_SUBSTR TURN[,TURN...] [keys]: print raw ledger rows (compact) of one of the 14 packets"""
import json, os, sys
R8 = '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/panel14/R8'
games = [l.strip() for l in open(os.path.join(R8, 'games.txt')) if l.strip()]
g = next(x for x in games if sys.argv[1] in x)
turns = [int(x) for x in sys.argv[2].split(',')]
keys = sys.argv[3].split(',') if len(sys.argv) > 3 else None
led = json.load(open(os.path.join(g, 'TURN_LEDGER.json'), encoding='utf-8'))


def side(s):
    out = []
    if not s:
        return 'None'
    for k, v in s.items():
        if k in ('active', 'bench_in_position_order'):
            continue
        out.append(f'{k}={json.dumps(v, ensure_ascii=False)}')
    lines = ['    ' + ' '.join(out)]
    for p in [s.get('active')] + list(s.get('bench_in_position_order') or []):
        if not isinstance(p, dict):
            lines.append(f'    - {p!r}')
            continue
        q = {k: v for k, v in p.items() if k not in ('evidence_ids', 'limit_reason', 'status', 'hp_max_basis')}
        lines.append('    - ' + json.dumps(q, ensure_ascii=False))
    return '\n'.join(lines)


for t in led['turns']:
    if t.get('turn_number') not in turns:
        continue
    print('=' * 20, 'turn', t.get('turn_number'), t.get('who_played'))
    for k, v in t.items():
        if keys and k not in keys:
            continue
        if k in ('board_at_start', 'board_after'):
            print(f' {k}:')
            for sd in ('owner', 'opponent'):
                print(f'  {sd}:')
                print(side((v or {}).get(sd)))
            for kk, vv in (v or {}).items():
                if kk not in ('owner', 'opponent'):
                    print(f'  {kk}: {json.dumps(vv, ensure_ascii=False)}')
        elif k == 'plays_in_order':
            print(' plays:')
            for i, p in enumerate(v or []):
                print(f'  [{i}] ' + json.dumps(p, ensure_ascii=False))
        else:
            print(f' {k}: {json.dumps(v, ensure_ascii=False)}')
