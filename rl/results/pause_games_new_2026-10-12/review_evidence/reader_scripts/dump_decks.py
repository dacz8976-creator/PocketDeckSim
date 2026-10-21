import json, os, glob, sys
BASE = '/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA'
games = sorted(glob.glob(BASE + '/BATCH_2026-10-*_NEW_PAUSE_GAMES/2026*_iOS'))
want = sys.argv[1:]
for g in games:
    gn = os.path.basename(g)
    if want and not any(w in gn for w in want):
        continue
    p = os.path.join(g, 'DECK_USED.json')
    if not os.path.exists(p):
        print('====', gn, 'NO DECK_USED'); continue
    d = json.load(open(p, encoding='utf-8'))
    print('====', gn)
    def walk(v, path, depth=0):
        if isinstance(v, dict):
            for k, v2 in v.items():
                walk(v2, path + '.' + k, depth + 1)
        elif isinstance(v, list):
            if v and all(isinstance(x, dict) for x in v) and any('name' in x for x in v):
                print('  LIST', path, len(v))
                for x in v:
                    print('     ', json.dumps({k: x[k] for k in x if k not in ('variant_basis',)}, ensure_ascii=False)[:220])
            elif v and all(isinstance(x, str) for x in v) and len(v) > 3:
                print('  STRLIST', path, len(v), v[:25])
            else:
                if 'alias' in path.lower() or 'print' in path.lower():
                    print('  ', path, json.dumps(v, ensure_ascii=False)[:600])
        else:
            if 'alias' in path.lower() or 'print' in path.lower() or 'status' in path.lower():
                print('  ', path, json.dumps(v, ensure_ascii=False)[:300])
    walk(d, '')
