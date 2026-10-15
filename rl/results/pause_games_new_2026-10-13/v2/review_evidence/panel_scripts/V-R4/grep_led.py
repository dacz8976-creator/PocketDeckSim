import json, sys, re
paths = {
 '210823': "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-12_NEW_LONG_VIDEOS/20261012_210823000_iOS/TURN_LEDGER.json",
 '022530': "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-13_NEWEST_TWO/20261013_022530000_iOS/TURN_LEDGER.json",
}
g, pat = sys.argv[1], sys.argv[2]
led = json.load(open(paths[g], encoding='utf-8'))
rx = re.compile(pat.replace(',', '|'), re.I)

def walk(o, path):
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, f'{path}.{k}')
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, f'{path}[{i}]')
    else:
        s = str(o)
        if rx.search(s):
            print(path, '=>', s[:400])

for t in led['turns']:
    walk(t, f"T{t.get('turn_number')}:{t.get('who_played')}")
