import json, sys, os, glob, collections
for batch in ['BATCH_2026-10-06_NEW_PAUSE_GAMES','BATCH_2026-10-09_NEW_PAUSE_GAMES','BATCH_2026-10-11_NEW_PAUSE_GAMES']:
    base = r'C:\Users\dacz8\OneDrive\Desktop\Battle Logs\Recording_QA' + '\\' + batch
    for g in sorted(os.listdir(base)):
        f = os.path.join(base, g, 'DECK_USED.json')
        if not os.path.exists(f):
            continue
        d = json.load(open(f, encoding='utf-8'))
        lst = d.get('cards_in_log_order') or d.get('counts_by_name_and_variant')
        vs = collections.defaultdict(collections.Counter)
        def walk(v):
            if isinstance(v, list):
                for x in v:
                    if isinstance(x, dict) and x.get('name'):
                        vs[x['name']][str(x.get('variant'))] += (x.get('count') if isinstance(x.get('count'), int) else 1)
        walk(lst)
        multi = {n: dict(c) for n, c in vs.items() if len(c) > 1}
        print(batch[6:16], g, 'keys=', [k for k in d.keys() if 'card' in k.lower() or 'count' in k.lower() or 'qr' in k.lower()], 'MULTI=', multi)
