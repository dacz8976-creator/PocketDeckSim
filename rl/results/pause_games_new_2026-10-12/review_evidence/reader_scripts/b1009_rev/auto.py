import sys
sys.stdout.reconfigure(encoding='utf-8')
import json, sys, os, re, collections
DB = r'C:\Users\dacz8\Projects\Pocket Deck Sim\PocketDeckSim\engine\database.json'
db = json.load(open(DB, encoding='utf-8'))
cards = db if isinstance(db, list) else db.get('cards', list(db.values()))
BYID = {}
for c in cards:
    inner = c.get('Pokemon') or c.get('Trainer') or c.get('Energy') or c
    BYID[f"{inner.get('name','').replace(chr(8217), chr(39))} {inner.get('id')}"] = inner
def nname(n):
    if n is None: return None
    n = str(n).strip().replace('Poke Ball', 'Poké Ball').replace('\u2019', "'")
    return re.sub(r'\s*[\(\[].*[\)\]]$', '', n)
def titles(cid):
    c = BYID.get(cid)
    if not c: return None
    out = [a.get('title') for a in c.get('attacks', []) or []]
    ab = c.get('ability')
    if isinstance(ab, dict): out.insert(0, ab.get('title'))
    return out
def norm(s): return re.sub(r'[^a-z]', '', str(s).lower())
base = r'C:\Users\dacz8\OneDrive\Desktop\Battle Logs\Recording_QA\BATCH_2026-10-09_NEW_PAUSE_GAMES'
P = json.load(open(r'C:\Users\dacz8\Projects\Pocket Deck Sim\PocketDeckSim\rl\results\pause_games_new_2026-10-12\positions_all.json', encoding='utf-8'))
def inst(side):
    out = []
    a = side.get('active')
    if a and isinstance(a, dict) and a.get('name') and str(a['name']).lower() not in ('none','empty'): out.append(a)
    bench = [p for p in side.get('bench_in_position_order') or [] if isinstance(p, dict) and p.get('name') and str(p['name']).lower() not in ('none','empty') and not p.get('empty')]
    def bp(p):
        v = p.get('bench_position')
        if isinstance(v, int): return v
        m = re.search(r'\d', str(v)); return int(m.group(0)) if m else 99
    bench.sort(key=bp)
    return out + bench
def eb(p):
    v = (p.get('attached_energy') or {}).get('by_type')
    c = collections.Counter()
    if isinstance(v, dict):
        for k, n in v.items(): c[str(k).capitalize()] += int(n or 0)
    elif isinstance(v, list):
        for x in v:
            if isinstance(x, dict): c[str(x.get('type') or x.get('energy_type')).capitalize()] += int(x.get('count') or 1)
            else: c[str(x).capitalize()] += 1
    return c
for g in sorted(os.listdir(base)):
    if not g.endswith('_iOS'): continue
    d = json.load(open(os.path.join(base, g, 'TURN_LEDGER.json'), encoding='utf-8'))
    short = g.replace('_iOS', '')[2:]
    for t in d['turns']:
        if not str(t.get('who_played','')).startswith('owner'): continue
        pid = f"KW-{short}-t{t['turn_number']:02d}"
        pos = next((p for p in P if p['id'] == pid), None)
        if pos is None:
            print(pid, 'NO POSITION'); continue
        issues = []
        h = [nname(c.get('name') if isinstance(c, dict) else c) for c in (t.get('hand_at_start') or {}).get('cards_left_to_right') or []]
        rawh = [(c.get('name') if isinstance(c, dict) else c) for c in (t.get('hand_at_start') or {}).get('cards_left_to_right') or []]
        ph = [x.rsplit(' ', 2)[0] for x in pos['me']['hand']]
        if h != ph: issues.append(f'HAND ledger={h} pos={ph}')
        for raw, cid in zip(rawh, pos['me']['hand']):
            m = re.search(r'\((.*)\)', str(raw))
            if m:
                tt = titles(cid) or []
                if not any(norm(x) and norm(x) in norm(m.group(1)) for x in tt): issues.append(f'HAND PRINTING {raw!r} -> {cid} {tt}')
        hs = t.get('hand_at_start') or {}
        if hs.get('status') not in ('observed', 'visually_reviewed', None) or hs.get('limit_reason'):
            issues.append(f"HAND status={hs.get('status')} limit={hs.get('limit_reason')}")
        b = t['board_at_start']
        for side, key in (('owner', 'me'), ('opponent', 'opp')):
            L = inst(b[side]); B = pos[key]['board']
            if len(L) != len(B): issues.append(f'{side} BOARD COUNT ledger={len(L)} pos={len(B)}')
            for lp, bp_ in zip(L, B):
                nm = nname(lp['name']); cn = bp_['card'].rsplit(' ', 2)[0]
                if nm != cn: issues.append(f"{side} NAME {nm} vs {bp_['card']}")
                if lp.get('hp_now') != bp_['hp']: issues.append(f"{side} HP {nm} {lp.get('hp_now')} vs {bp_['hp']}")
                c = BYID.get(bp_['card'])
                if c and lp.get('hp_max') not in (None, c.get('hp')): issues.append(f"{side} HPMAX {nm} ledger {lp.get('hp_max')} card {c.get('hp')} ({bp_['card']})")
                if eb(lp) != collections.Counter(bp_.get('energy', [])): issues.append(f"{side} ENERGY {nm} {dict(eb(lp))} vs {bp_.get('energy')}")
                tool = lp.get('tool'); tool = None if not tool or str(tool).lower() in ('none','null') else nname(tool)
                ptool = [x.rsplit(' ', 2)[0] for x in bp_.get('tools', [])]
                if (tool or None) != (ptool[0] if ptool else None): issues.append(f"{side} TOOL {nm} {tool} vs {ptool}")
                vt = str(lp.get('variant') or '')
                tt = titles(bp_['card']) or []
                words = [w for w in re.split(r'[/;,]', vt)]
                if vt and not re.match(r'^[A-Za-z0-9\-]+ \d{3}', vt):
                    ok = any(norm(x) and norm(x) in norm(vt) for x in tt)
                    if not ok: issues.append(f"{side} PRINTING? {nm} ledger variant {vt!r} -> {bp_['card']} {tt}")
                elif vt:
                    m = re.match(r'^([A-Za-z0-9\-]+ \d{3})', vt)
                    if m and not bp_['card'].endswith(m.group(1)): issues.append(f"{side} PRINTING ID {nm} ledger {m.group(1)} -> {bp_['card']}")
                if lp.get('special_conditions'): issues.append(f"{side} COND {nm} {lp.get('special_conditions')}")
                if lp.get('status') not in ('observed', 'visually_reviewed', None) or (lp.get('limit_reason') and 'artwork' not in str(lp.get('limit_reason'))):
                    issues.append(f"{side} PK status {nm} {lp.get('status')} limit={lp.get('limit_reason')}")
            pts = b[side].get('points')
            if pts != pos['points'][0 if side == 'owner' else 1]: issues.append(f'{side} POINTS {pts} vs {pos["points"]}')
        oh = (t.get('opponent_hand_at_owner_turn_start') or {}).get('count')
        if oh != pos['opp']['hand_count']: issues.append(f"OPP HAND {oh} vs {pos['opp']['hand_count']}")
        st = b.get('stadium'); st = st.get('name') if isinstance(st, dict) else st
        st = None if not st or str(st).strip().lower() in ('none','null','empty','no stadium') else nname(st)
        pst = pos['stadium']['card'].rsplit(' ', 2)[0] if pos['stadium'] else None
        if st != pst: issues.append(f'STADIUM {st} vs {pos["stadium"]}')
        z = b['owner'].get('energy_zone') or {}
        tz = (z.get('this_turn') or {}).get('type'); nz = (z.get('next') or {}).get('type')
        if str(tz).capitalize() != str(pos['me']['energy_now']) : issues.append(f"ENERGY_NOW ledger={tz} pos={pos['me']['energy_now']}")
        if str(nz).capitalize() != str(pos['me']['energy_next']) : issues.append(f"ENERGY_NEXT ledger={nz} pos={pos['me']['energy_next']}")
        kinds = [(p.get('kind'), p.get('card_name'), p.get('response')) for p in t.get('plays_in_order') or []]
        odd = [k for k in kinds if str(k[0]).lower() in ('card_play_attempt', 'prompt_response') or 'cancel' in str(k).lower()]
        if odd: issues.append(f'PLAY ODD {odd}')
        print(pid, 'turn_count', pos['turn_count'], '==' if pos['turn_count'] == t['turn_number'] else '!=', 'plan', pos['his_plan'], 'trunc', pos['plan_truncated_at'])
        print('   plays', [(p.get('kind'), p.get('card_name'), p.get('target')) for p in t.get('plays_in_order') or []])
        for i in issues: print('   !', i)
