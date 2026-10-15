import json, os, sys
R8 = '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/panel14/R8'
games = [l.strip() for l in open(os.path.join(R8, 'games.txt')) if l.strip()]
out = open(os.path.join(R8, 'diff_norm.txt'), 'w', encoding='utf-8')


def P(*a):
    print(*a, file=out)


def walk(a, b, path, diffs):
    if type(a) != type(b):
        diffs.append((path, a, b)); return
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b), key=str):
            if k not in a:
                diffs.append((path + '.' + str(k), '<absent>', b[k]))
            elif k not in b:
                diffs.append((path + '.' + str(k), a[k], '<absent>'))
            else:
                walk(a[k], b[k], path + '.' + str(k), diffs)
    elif isinstance(a, list):
        if len(a) != len(b):
            diffs.append((path + f' len {len(a)}->{len(b)}', None, None))
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, f'{path}[{i}]', diffs)
        if len(b) > len(a):
            for i in range(len(a), len(b)):
                diffs.append((f'{path}[{i}]', '<absent>', b[i]))
    else:
        if a != b:
            diffs.append((path, a, b))


for g in games:
    name = os.path.basename(g)
    raw = json.load(open(os.path.join(g, 'TURN_LEDGER.json'), encoding='utf-8'))
    nrm = json.load(open(os.path.join(R8, 'norm', name, 'TURN_LEDGER.json'), encoding='utf-8'))
    P('=' * 30, name)
    for tr, tn in zip(raw['turns'], nrm['turns']):
        d = []
        walk(tr, tn, '', d)
        if not d:
            continue
        P(f"-- turn {tr.get('turn_number')} ({tr.get('who_played')})")
        # group per play
        plays_changed = sorted({int(p.split('[')[1].split(']')[0]) for p, _, _ in d if p.startswith('.plays_in_order[')})
        for i in plays_changed:
            a, b = tr['plays_in_order'][i], tn['plays_in_order'][i]
            P(f"  play {i}: kind={a.get('kind')!r} card={a.get('card_name')!r}")
            P(f"     raw target={a.get('target')!r} result={a.get('result')!r}")
            P(f"     raw details={a.get('details')!r} energy={a.get('energy')!r}")
            P(f"     NEW target={b.get('target')!r}")
            if b.get('result') != a.get('result'):
                P(f"     NEW result={b.get('result')!r}")
            if b.get('energy') != a.get('energy'):
                P(f"     NEW energy={b.get('energy')!r}")
        for p, x, y in d:
            if not p.startswith('.plays_in_order['):
                P(f"  OTHER {p}: {json.dumps(x, ensure_ascii=False)[:300]} -> {json.dumps(y, ensure_ascii=False)[:600]}")
    # deck
    dr = json.load(open(os.path.join(g, 'DECK_USED.json'), encoding='utf-8'))
    dn = json.load(open(os.path.join(R8, 'norm', name, 'DECK_USED.json'), encoding='utf-8'))
    d = []
    walk(dr, dn, 'DECK', d)
    if d:
        P('  DECK_USED changes:')
        for p, x, y in d:
            P(f"    {p}: {json.dumps(x, ensure_ascii=False)[:200]} -> {json.dumps(y, ensure_ascii=False)[:400]}")
out.close()
print(open(os.path.join(R8, 'diff_norm.txt'), encoding='utf-8').read())
