import json, os, sys
base = sys.argv[1]
games = json.load(open(os.path.join(base, 'games.json'), encoding='utf-8'))
rev = [g for g in games if g['reviews']]
k = 5
os.makedirs(os.path.join(base, 'extract'), exist_ok=True)
for i in range(k):
    part = rev[i::k]
    rows = []
    for g in part:
        extra = []
        for d in g['review_dirs']:
            for name in ('SUMMARY.json', 'LADDER_ENTRY.json'):
                p = os.path.join(d, name)
                if os.path.exists(p):
                    extra.append(p)
        rows.append({'game_key': g['game_key'], 'utc': g['utc'], 'my_deck': g['deck_name'] or g['deck_id'], 'result': g['result'],
                     'ladder_opp_text': g['opp'], 'ladder_note': g['note'], 'review_files': g['reviews'], 'structured_files': extra})
    json.dump(rows, open(os.path.join(base, 'extract', f'batch_{i+1}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    size = sum(os.path.getsize(p) for r in rows for p in r['review_files'])
    print(f'batch_{i+1}: {len(rows)} games, review bytes {size}')
print('no-review games:', sum(1 for g in games if not g['reviews']))
