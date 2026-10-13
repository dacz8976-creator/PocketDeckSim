import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
base = r'C:\Users\dacz8\OneDrive\Desktop\Battle Logs\Recording_QA\BATCH_2026-10-09_NEW_PAUSE_GAMES'
for g in sorted(os.listdir(base)):
    f = os.path.join(base, g, 'DECK_USED.json')
    if not os.path.exists(f): continue
    d = json.load(open(f, encoding='utf-8'))
    print('==', g)
    for k in ('exact_list_status', 'game_version_binding_basis', 'conflicts_with_filmed_cards', 'limits', 'energy_configuration_from_log'):
        if k in d: print('  ', k, '=', json.dumps(d[k], ensure_ascii=False)[:600])
    u = os.path.join(base, g, 'UNCERTAINTIES.json')
    if os.path.exists(u):
        print('   UNCERTAINTIES', json.dumps(json.load(open(u, encoding='utf-8')), ensure_ascii=False)[:1500])
