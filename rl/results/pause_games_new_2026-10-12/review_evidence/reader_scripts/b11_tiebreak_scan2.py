import sys, json, os, glob, re, importlib.util
H = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/harness/ledger_to_positions.py'
spec = importlib.util.spec_from_file_location('l2p', H)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
P = json.load(open('/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/positions_all.json', encoding='utf-8'))
pids = {p['id'] for p in P}
base = '/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/'
def norm(s):
    return re.sub(r'[^a-z]', '', str(s).replace('’', "'").lower())
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
                if len(by_hp) < 2:
                    continue
                vt = str(p.get('variant') or '').split(';')[0]
                t2 = [c for c in by_hp if any(vt.startswith(a.get('title', '~')) for a in c.get('attacks', []))]
                if t2:
                    continue
                chosen = m.opp_card(name, hp, p.get('variant'))
                nv = norm(p.get('variant') or '')
                fits = []
                for c in by_hp:
                    ttl = [a.get('title') for a in c.get('attacks', [])]
                    ab = c.get('ability')
                    if isinstance(ab, dict) and ab.get('title'):
                        ttl.append(ab['title'])
                    if ttl and all(norm(x) in nv for x in ttl if x) and nv:
                        fits.append(m.cid(c))
                sigs = {}
                for c in by_hp:
                    ab = c.get('ability')
                    sigs.setdefault(tuple(a.get('title') for a in c.get('attacks', [])) + ((ab.get('title') if isinstance(ab, dict) else None),), []).append(c['id'])
                if len(sigs) < 2:
                    continue
                verdict = 'n/a (text names nothing)' if not fits else ('OK' if chosen in fits else 'WRONG')
                print(pid, '|', name, hp, '|', repr(p.get('variant')), '| chosen', chosen, '| text fits', fits, '|', verdict, '|', sigs)
