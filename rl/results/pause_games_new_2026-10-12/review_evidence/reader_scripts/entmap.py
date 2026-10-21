import json, os, glob, re, collections, sys
BASE = '/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA'
PR = re.compile(r'\b([A-Z][A-Za-z0-9]*(?:-[A-Z])? \d{3})\b')
EM = collections.defaultdict(lambda: collections.Counter())
NAMES = collections.defaultdict(set)
files = []
for b in glob.glob(BASE + '/BATCH_2026-10-*_NEW_PAUSE_GAMES'):
    for root, dirs, fs in os.walk(b):
        for f in fs:
            if f.endswith('.json') and 'TURN_LEDGER' not in f:
                files.append(os.path.join(root, f))
def walk(v, src):
    if isinstance(v, dict):
        eid = v.get('entity_id', v.get('semantic_entity_id'))
        if v.get('name') and isinstance(eid, int):
            NAMES[eid].add(v['name'])
            for k in ('variant', 'printing_aliases', 'variant_aliases', 'semantic_variant_references', 'printings', 'printing'):
                x = v.get(k)
                xs = [x] if isinstance(x, str) else (x if isinstance(x, list) else [])
                for y in xs:
                    if isinstance(y, str):
                        for p in PR.findall(y):
                            EM[eid][p] += 1
        for v2 in v.values():
            walk(v2, src)
    elif isinstance(v, list):
        for x in v:
            walk(x, src)
for f in files:
    try:
        d = json.load(open(f, encoding='utf-8-sig'))
    except Exception as e:
        continue
    walk(d, f)
out = {eid: {'names': sorted(NAMES[eid]), 'printings': dict(EM[eid])} for eid in NAMES}
json.dump(out, open(os.path.dirname(os.path.abspath(__file__)) + '/entmap.json', 'w'), indent=1, ensure_ascii=False)
want = [int(x) for x in sys.argv[1:]]
for eid in sorted(out):
    if not want or eid in want:
        print(eid, out[eid])
