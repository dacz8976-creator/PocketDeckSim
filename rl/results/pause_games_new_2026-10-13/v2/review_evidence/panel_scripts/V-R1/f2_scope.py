import json, re, collections
V2 = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/"
QA = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/"
meta = json.load(open(V2 + 'games_meta.json', encoding='utf-8'))
pos = json.load(open(V2 + 'positions_all.json', encoding='utf-8'))
bygame = collections.defaultdict(list)
for p in pos:
    bygame[p['game']].append(p)
ET = ('Grass', 'Fire', 'Water', 'Lightning', 'Psychic', 'Fighting', 'Darkness', 'Metal', 'Colorless', 'Dragon')
for g, m in meta.items():
    L = json.load(open(QA + m['folder'] + '/TURN_LEDGER.json', encoding='utf-8'))
    opp_this = collections.Counter()
    opp_next_seen = collections.Counter()
    opp_attach = collections.Counter()
    hidden_at_owner_start = 0
    own_turns = 0
    owner_zone_types = collections.Counter()
    for t in L['turns']:
        who = str(t.get('who_played'))
        b = t.get('board_at_start') or {}
        oz = ((b.get('opponent') or {}).get('energy_zone') or {})
        mz = ((b.get('owner') or {}).get('energy_zone') or {})
        if who.startswith('owner'):
            own_turns += 1
            ot = (oz.get('this_turn') or {}).get('type')
            on = (oz.get('next') or {}).get('type')
            if not ot and not on:
                hidden_at_owner_start += 1
        else:
            ot = (oz.get('this_turn') or {}).get('type')
            if ot:
                opp_this[ot] += 1
            for p in t.get('plays_in_order') or []:
                if str(p.get('kind')).lower().startswith('energy') and isinstance(p.get('energy'), dict) and p['energy'].get('type'):
                    opp_attach[p['energy']['type']] += 1
        for bk in ('board_at_start', 'board_after'):
            oz2 = (((t.get(bk) or {}).get('opponent') or {}).get('energy_zone') or {})
            on2 = (oz2.get('next') or {}).get('type')
            if on2:
                opp_next_seen[on2] += 1
            mz2 = (((t.get(bk) or {}).get('owner') or {}).get('energy_zone') or {})
            for k in ('this_turn', 'next'):
                ty = (mz2.get(k) or {}).get('type')
                if ty:
                    owner_zone_types[ty] += 1
    pv = collections.Counter(p['opp'].get('energy_next') for p in bygame.get(g, []))
    print(g, '| positions', len(bygame.get(g, [])), '| owner turns', own_turns, '| opp zone hidden at his start', hidden_at_owner_start)
    print('    opp this_turn on opp rows', dict(opp_this), '| opp next icon seen', dict(opp_next_seen), '| opp attach types', dict(opp_attach))
    print('    his zone types', dict(owner_zone_types), '| POSITIONS opp.energy_next', dict(pv))
