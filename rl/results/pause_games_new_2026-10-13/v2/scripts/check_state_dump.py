#!/usr/bin/env python3
"""check_state_dump.py POSITIONS.json DECKS_DIR: do the positions reach the engine with the knock-out counts and Special Conditions as written?
Runs pg_pos_F_cond with `--dump-state` (main's pg_pos.rs prints, per position, the engine state's own_knockouts_this_game and every condition on each Pokemon) at seed 1 on all positions and compares
with the position's `me.knockouts` / `opp.knockouts` and the `conditions` of its board entries (board index = engine slot). Prints one line per mismatch and a summary; exit 1 on any mismatch."""
import json, os, subprocess, sys

pos_f, decks_dir = sys.argv[1:3]
BIN = os.environ.get('BIN', '/home/dacz8976/pgx/pg_pos_F_cond')
if any(k.startswith('DECKGYM_') for k in os.environ):
    sys.exit('a DECKGYM_ variable is set; refusing')
POS = json.load(open(pos_f, encoding='utf-8'))
DECKARGS = []
for f in sorted(os.listdir(decks_dir)):
    if f.startswith('KW') and f.endswith('.txt'):
        DECKARGS += ['--deck', f'{f[:-4]}={os.path.join(decks_dir, f)}']
r = subprocess.run(['nice', '-n', '19', BIN, '--positions', pos_f, *DECKARGS, '--seeds', '1', '--bot', 'km3', '--dump-state'], capture_output=True, text=True)
state = {}
for l in r.stdout.split('\n'):
    l = l.strip()
    if l.startswith('{'):
        d = json.loads(l)
        if d.get('kind') == 'state':
            state[d['id']] = d
bad = n_ko = n_cond = 0
for p in POS:
    s = state.get(p['id'])
    if s is None:
        print('NO STATE LINE', p['id'])
        bad += 1
        continue
    want_ko = [p['me'].get('knockouts') or 0, p['opp'].get('knockouts') or 0]
    got_ko = s['knockouts']
    if list(got_ko) != want_ko:
        print('KNOCKOUTS', p['id'], 'position', want_ko, 'engine', got_ko)
        bad += 1
    n_ko += 1 if any(want_ko) else 0
    for side in ('me', 'opp'):
        want = {i: sorted(b['conditions']) for i, b in enumerate(p[side]['board']) if b.get('conditions')}
        got = {int(k): sorted(v) for k, v in s['conditions'][side].items()}
        if want != got:
            print('CONDITIONS', p['id'], side, 'position', want, 'engine', got)
            bad += 1
        n_cond += 1 if want else 0
print(f'{len(POS)} positions, {len(state)} state lines; {n_ko} with a knock-out count above 0, {n_cond} sides with a condition; mismatches: {bad}')
sys.exit(1 if bad else 0)
