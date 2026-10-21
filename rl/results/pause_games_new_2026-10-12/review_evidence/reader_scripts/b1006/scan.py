"""read-only scan of the Oct 6 batch positions: energy fields vs ledger, active/board effects the position drops, deck-file Energy line vs DECK_USED"""
import sys, json, os, re
sys.dont_write_bytecode = True
H = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/harness'
sys.path.insert(0, H)
import ledger_to_positions as L  # noqa
B = '/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-06_NEW_PAUSE_GAMES/'
P = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/positions_all.json'
D = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/decks/'
ALL = json.load(open(P, encoding='utf-8'))
for g in sorted(os.listdir(B)):
    if not g.endswith('_iOS'):
        continue
    short = g.replace('_iOS', '')[2:]
    ps = [x for x in ALL if x['game'][3:] == short]
    if not ps:
        continue
    led = json.load(open(B + g + '/TURN_LEDGER.json', encoding='utf-8'))
    T = {t['turn_number']: t for t in led['turns']}
    du = json.load(open(B + g + '/DECK_USED.json', encoding='utf-8'))
    ekeys = {}
    def walk(o, path=''):
        if isinstance(o, dict):
            for k, v in o.items():
                if 'energy' in k.lower():
                    ekeys[path + k] = v
                walk(v, path + k + '.')
    walk(du)
    deck_e = open(D + f'KW{short}.txt', encoding='utf-8').readline().strip()
    print('=====', short, '| deck file', deck_e, '| DECK_USED energy keys', json.dumps(ekeys, ensure_ascii=False)[:300])
    seen_types = set()
    for t in led['turns']:
        if str(t.get('who_played', '')).startswith('owner'):
            for p in t.get('plays_in_order') or []:
                e = p.get('energy') or {}
                if p.get('kind') in ('energy_attachment', 'energy') and L.etype(e.get('type')):
                    seen_types.add(L.etype(e.get('type')))
    print('   his attached types in ledger:', sorted(seen_types))
    for p in ps:
        t = T[p['turn_count']]
        b = t['board_at_start']
        z = b['owner'].get('energy_zone') or {}
        oz = b['opponent'].get('energy_zone') or {}
        lt, ln = (z.get('this_turn') or {}).get('type'), (z.get('next') or {}).get('type')
        on = (oz.get('next') or {}).get('type')
        flag = []
        if L.etype(ln) is None:
            flag.append(f'ledger next unreadable ({ln}) -> position {p["me"]["energy_next"]}')
        elif L.etype(ln) != p['me']['energy_next']:
            flag.append(f'NEXT MISMATCH ledger {ln} pos {p["me"]["energy_next"]}')
        if L.etype(lt) is None and p['me']['energy_now'] is not None:
            flag.append(f'ledger this_turn unreadable ({lt}) -> position {p["me"]["energy_now"]}')
        elif L.etype(lt) and L.etype(lt) != p['me']['energy_now']:
            flag.append(f'NOW MISMATCH ledger {lt} pos {p["me"]["energy_now"]}')
        if L.etype(on) is None:
            flag.append(f'opp next unreadable ({on}) -> position {p["opp"]["energy_next"]}')
        elif L.etype(on) != p['opp']['energy_next']:
            flag.append(f'OPP NEXT MISMATCH ledger {on} pos {p["opp"]["energy_next"]}')
        effs = []
        for sk in ('owner', 'opponent'):
            s = b[sk]
            if s.get('board_effects'):
                effs.append(f'{sk}.board_effects={json.dumps(s["board_effects"], ensure_ascii=False)[:200]}')
            for q in L.instances(s):
                if q.get('active_effects'):
                    effs.append(f'{sk}.{q["name"]}.active_effects={json.dumps(q["active_effects"], ensure_ascii=False)[:200]}')
                if q.get('special_conditions'):
                    effs.append(f'{sk}.{q["name"]}.conditions={q["special_conditions"]}')
        if b.get('shared_effects'):
            effs.append(f'shared={json.dumps(b["shared_effects"], ensure_ascii=False)[:200]}')
        print(' ', p['id'], 'now', p['me']['energy_now'], 'next', p['me']['energy_next'], 'opp_next', p['opp']['energy_next'], '| ledger', lt, ln, on, '|', '; '.join(flag))
        for e in effs:
            print('      EFFECT', e)
        if p.get('turn_effects'):
            print('      pos turn_effects', p['turn_effects'])
