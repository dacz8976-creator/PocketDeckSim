import json, sys
paths = {
 '210823': "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-12_NEW_LONG_VIDEOS/20261012_210823000_iOS/TURN_LEDGER.json",
 '022530': "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-13_NEWEST_TWO/20261013_022530000_iOS/TURN_LEDGER.json",
}
g = sys.argv[1]
turns = [int(x) for x in sys.argv[2].split(',')]
keys = sys.argv[3].split(',') if len(sys.argv) > 3 else ['plays_in_order']
led = json.load(open(paths[g], encoding='utf-8'))
for t in led['turns']:
    if t.get('turn_number') in turns:
        print('=' * 20, 'turn', t.get('turn_number'), t.get('who_played'))
        for k in keys:
            print('---', k)
            print(json.dumps(t.get(k), ensure_ascii=False, indent=1))
