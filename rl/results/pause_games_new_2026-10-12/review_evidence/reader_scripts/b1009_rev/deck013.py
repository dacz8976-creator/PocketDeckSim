import json, sys
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open(r'C:\Users\dacz8\OneDrive\Desktop\Battle Logs\Recording_QA\BATCH_2026-10-09_NEW_PAUSE_GAMES\20261010_013009000_iOS\DECK_USED.json', encoding='utf-8'))
print(json.dumps(d.get('counts_by_name_and_variant'), ensure_ascii=False))
print(json.dumps(d.get('filmed_qr_snapshot'), ensure_ascii=False)[:3000])
