import json, sys
d = json.load(open(sys.argv[1], encoding='utf-8'))
print(type(d).__name__, list(d.keys()) if isinstance(d, dict) else len(d))
for k, v in d.items():
    if k != 'turns':
        s = json.dumps(v, ensure_ascii=False)
        print('==', k, s[:1500])
print('turns', len(d['turns']))
for t in d['turns']:
    print(t.get('turn_number'), t.get('who_played'), list(t.keys()))
