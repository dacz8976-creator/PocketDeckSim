import sys, json, os, glob, importlib.util
H = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/harness/ledger_to_positions.py'
spec = importlib.util.spec_from_file_location('l2p', H)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
P = json.load(open('/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/positions_all.json', encoding='utf-8'))
pids = {p['id'] for p in P}
base = '/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/'
hits = []
for b in ('BATCH_2026-10-06_NEW_PAUSE_GAMES', 'BATCH_2026-10-09_NEW_PAUSE_GAMES', 'BATCH_2026-10-11_NEW_PAUSE_GAMES'):
    for gd in sorted(glob.glob(base + b + '/*/TURN_LEDGER.json')):
        g = os.path.basename(os.path.dirname(gd))
        short = g.replace('_iOS', '')[2:]
        led = json.load(open(gd, encoding='utf-8'))
        for t in led['turns']:
            if not str(t.get('who_played', '')).startswith('owner'):
                continue
            pid = f"KW-{short}-t{t['turn_number']:02d}"
            if pid not in pids:
                continue
            for p in m.instances(((t.get('board_at_start') or {}).get('opponent')) or {}):
                name = m.nname(p['name'])
                cand = [c for c in m.BYNAME.get(name, []) if 'hp' in c] or m.BYNAME.get(name, [])
                hp = p.get('hp_max')
                by_hp = [c for c in cand if hp is not None and c.get('hp') == hp] or cand
                sigs = {tuple(a.get('title') for a in c.get('attacks', [])) + (((c.get('ability') or {}).get('title') if isinstance(c.get('ability'), dict) else None),) for c in by_hp}
                if len(sigs) <= 1:
                    continue
                vt = str(p.get('variant') or '').split(';')[0]
                t2 = [c for c in by_hp if any(vt.startswith(a.get('title', '~')) for a in c.get('attacks', []))]
                chosen = m.opp_card(name, hp, p.get('variant'))
                hits.append((pid, name, hp, p.get('variant'), chosen, 'tie-break matched' if t2 else 'NO MATCH -> first', sorted(sigs, key=str)))
for h in hits:
    print(h)
print(len(hits), 'opponent instances with >1 distinct printing at the same HP')
