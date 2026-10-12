import json, os, sys, re
sys.stdout.reconfigure(encoding='utf-8')
base = r'C:\Users\dacz8\OneDrive\Desktop\Battle Logs\Recording_QA\BATCH_2026-10-09_NEW_PAUSE_GAMES'
P = {p['id']: p for p in json.load(open(r'C:\Users\dacz8\Projects\Pocket Deck Sim\PocketDeckSim\rl\results\pause_games_new_2026-10-12\positions_all.json', encoding='utf-8'))}
STAD = ('Arena of Antiquity', 'Hiking Trail', 'Soothing Shore')
for g in sorted(os.listdir(base)):
    if not g.endswith('_iOS'): continue
    d = json.load(open(os.path.join(base, g, 'TURN_LEDGER.json'), encoding='utf-8'))
    short = g.replace('_iOS', '')[2:]
    last = None
    for t in d['turns']:
        who = 'owner' if str(t.get('who_played','')).startswith('owner') else 'opp'
        if who == 'owner':
            pid = f"KW-{short}-t{t['turn_number']:02d}"
            p = P.get(pid)
            st = t['board_at_start'].get('stadium')
            if p is not None:
                print(pid, 'ledger stadium', st, '| last played by', last, '| position', p['stadium'])
        for pl in t.get('plays_in_order') or []:
            cn = str(pl.get('card_name') or '').replace('\u2019', "'")
            if cn in STAD and 'attempt' not in str(pl.get('kind')).lower():
                last = (who, cn, t['turn_number'])
