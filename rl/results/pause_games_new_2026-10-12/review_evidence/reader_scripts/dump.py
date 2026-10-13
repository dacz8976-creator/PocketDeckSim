import json, sys
g, tn = sys.argv[1], int(sys.argv[2])
fields = sys.argv[3].split(',') if len(sys.argv) > 3 else None
base = r'C:\Users\dacz8\OneDrive\Desktop\Battle Logs\Recording_QA\BATCH_2026-10-09_NEW_PAUSE_GAMES'
d = json.load(open(base + '\\' + g + '\\TURN_LEDGER.json', encoding='utf-8'))
for t in d['turns']:
    if t['turn_number'] == tn:
        for k, v in t.items():
            if fields and k not in fields:
                continue
            print('==', k)
            print(json.dumps(v, ensure_ascii=False, indent=1))
