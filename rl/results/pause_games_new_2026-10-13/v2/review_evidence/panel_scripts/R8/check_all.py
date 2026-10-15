"""R8 scripted checks over the 92 positions of the 14 games against the RAW ledgers (independent re-derivation where possible).
writes check_all.txt (per position: DIFF lines and the plan side by side) and check_summary.json"""
import json, os, re, sys, collections
REPO = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim'
sys.path.insert(0, REPO + '/rl/results/pause_games_new_2026-10-12/harness')
import cardlib as C
R8 = '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/panel14/R8'
V2 = REPO + '/rl/results/pause_games_new_2026-10-13/v2'
games = [l.strip() for l in open(os.path.join(R8, 'games.txt')) if l.strip()]
POS = json.load(open(V2 + '/positions_all.json', encoding='utf-8'))
PL = {r['position_id']: r for r in json.load(open(V2 + '/position_list.json', encoding='utf-8'))}
REP = json.load(open(V2 + '/report_convert.json', encoding='utf-8'))
out = open(os.path.join(R8, 'check_all.txt'), 'w', encoding='utf-8')
summary = {}


def W(*a):
    print(*a, file=out)


def nn(x):
    return C.nname(x)


def cid(s):
    m = re.search(r'([A-Z][A-Za-z0-9\-]{0,4} \d{3})$', s)
    return m.group(1) if m else None


def cname(s):
    i = cid(s)
    return s[:-len(i)].strip() if i else s


def real(p):
    return isinstance(p, dict) and p.get('name') and str(p['name']).strip().lower() not in ('none', 'empty', 'null', 'n/a') and not p.get('empty')


def bpos(p):
    v = p.get('bench_position')
    if isinstance(v, int):
        return v
    s = str(v or '').lower()
    for w, n in (('left', 1), ('center', 2), ('middle', 2), ('right', 3)):
        if w in s:
            return n
    m = re.search(r'\d', s)
    return int(m.group(0)) if m else 99


def inst(side):
    side = side or {}
    a = side.get('active')
    o = [a] if real(a) else []
    b = [p for p in side.get('bench_in_position_order') or [] if real(p)]
    return o + sorted(b, key=bpos)


def ebt(p):
    v = (p.get('attached_energy') or {}).get('by_type')
    c = collections.Counter()
    if isinstance(v, dict):
        for t, n in v.items():
            if C.etype(t):
                c[C.etype(t)] += int(n or 0)
    elif isinstance(v, list):
        for x in v:
            if isinstance(x, dict):
                t = C.etype(x.get('type') or x.get('energy_type'))
                if t:
                    c[t] += int(x.get('count') or 1)
            elif C.etype(x):
                c[C.etype(x)] += 1
    return c


def tool(p):
    t = p.get('tool')
    return None if t is None or str(t).strip().lower() in ('none', 'null', '') else nn(t)


CONDS = {'asleep': 'Asleep', 'sleep': 'Asleep', 'paralyzed': 'Paralyzed', 'poisoned': 'Poisoned', 'poison': 'Poisoned', 'burned': 'Burned', 'confused': 'Confused'}


def deckfile(short):
    lines = open(os.path.join(V2, 'decks', f'KW{short}.txt'), encoding='utf-8').read().splitlines()
    en = [x.strip() for x in lines[0].split(':', 1)[1].split(',')]
    cards = collections.Counter()
    for l in lines[1:]:
        m = re.match(r'(\d+) (.+) ([A-Za-z0-9\-]+ \d{3})$', l.strip())
        cards[f'{nn(m.group(2))} {m.group(3)}'] += int(m.group(1))
    return en, cards


def hp_cap(card, tools, stadium):
    hp = card.get('hp') or 0
    if stadium and 'Starting Plains' in stadium and card.get('stage', 0) == 0:
        hp += 20
    for t in tools:
        tn = cname(t)
        if tn == 'Giant Cape':
            hp += 20
        if tn == 'Leaf Cape' and card.get('energy_type') == 'Grass':
            hp += 30
    return hp


tot_issue = collections.Counter()
for g in games:
    gname = os.path.basename(g)
    short = gname.replace('_iOS', '')[2:]
    led = json.load(open(os.path.join(g, 'TURN_LEDGER.json'), encoding='utf-8'))
    turns = led['turns']
    owner_rows = [t for t in turns if str(t.get('who_played', '')).startswith('owner')]
    en, deck = deckfile(short)
    deck_names = {cname(k) for k in deck}
    W('#' * 30, gname, '| deck energy', en, '| owner rows', [t['turn_number'] for t in owner_rows])
    poss = [p for p in POS if p['game'] == 'kw-' + short]
    have = {p['turn_count'] for p in poss}
    for k, t in enumerate(owner_rows):
        if t['turn_number'] not in have:
            why = [x for x in REP['left_out'] if x['game'] == short and x['turn'] == t['turn_number']]
            W(f'  LEFT OUT t{t["turn_number"]}: report says {why}')
    for p in poss:
        tn = p['turn_count']
        diffs = []
        t = next(x for x in turns if x['turn_number'] == tn and str(x.get('who_played', '')).startswith('owner'))
        k = owner_rows.index(t)
        b = t['board_at_start']
        prev_opp = next((x for x in turns if x['turn_number'] == tn - 1), None)
        # 1 identity
        if p['his_turn'] != k + 1:
            diffs.append(f'his_turn {p["his_turn"]} v {k + 1}')
        pts = [b['owner'].get('points'), b['opponent'].get('points')]
        if p['points'] != pts:
            diffs.append(f'points {p["points"]} v ledger {pts}')
        if p.get('decision_maker') != 'Dustin':
            diffs.append('decision_maker')
        # 2 hand
        hs = t.get('hand_at_start') or {}
        lh = [nn(c.get('name') if isinstance(c, dict) else c) for c in hs.get('cards_left_to_right') or []]
        ph = [cname(c) for c in p['me']['hand']]
        if ph != lh:
            diffs.append(f'hand {ph} v ledger {lh}')
        if hs.get('count') is not None and hs['count'] != len(ph):
            diffs.append(f'hand count {len(ph)} v ledger count {hs["count"]}')
        # 3 his board
        lb = inst(b['owner'])
        pb = p['me']['board']
        stad = b.get('stadium')
        stad = stad.get('name') if isinstance(stad, dict) else stad
        if len(lb) != len(pb):
            diffs.append(f'board size {len(pb)} v {len(lb)}')
        for i, (lp, pp) in enumerate(zip(lb, pb)):
            tag = f'me[{i}] {nn(lp["name"])}'
            if cname(pp['card']) != nn(lp['name']):
                diffs.append(f'{tag}: card {pp["card"]}')
            if pp['hp'] != lp.get('hp_now'):
                diffs.append(f'{tag}: hp {pp["hp"]} v {lp.get("hp_now")}')
            pe = collections.Counter(pp.get('energy') or [])
            if pe != ebt(lp):
                diffs.append(f'{tag}: energy {dict(pe)} v {dict(ebt(lp))} (raw {lp.get("attached_energy")})')
            pt = [cname(x) for x in pp.get('tools') or []]
            if (pt[0] if pt else None) != tool(lp):
                diffs.append(f'{tag}: tool {pt} v {tool(lp)}')
            pc = pp.get('conditions') or []
            lc = list(dict.fromkeys(CONDS.get(str(x).lower(), str(x)) for x in lp.get('special_conditions') or []))
            if sorted(pc) != sorted(lc):
                diffs.append(f'{tag}: conditions {pc} v {lc}')
            card = C.BYID.get(cid(pp['card']))
            if card is None:
                diffs.append(f'{tag}: printing {pp["card"]} not in DB')
            else:
                cap = hp_cap(card, pp.get('tools') or [], stad)
                if pp['hp'] > cap:
                    diffs.append(f'{tag}: hp {pp["hp"]} above max {cap}')
                if lp.get('hp_max') is not None and lp['hp_max'] != cap:
                    diffs.append(f'{tag}: ledger hp_max {lp["hp_max"]} v card max {cap} ({lp.get("hp_max_basis")})')
                # stack
                chain = C.chain_down(card['id'])
                beh = [cname(x) for x in pp.get('behind') or []]
                if beh != chain:
                    diffs.append(f'{tag}: behind {beh} v printed line {chain} (Rare Candy?)')
            for e in pe:
                if e not in en:
                    diffs.append(f'{tag}: energy type {e} not in deck energy {en}')
        # 5 opponent board
        lo = inst(b['opponent'])
        po = p['opp']['board']
        if len(lo) != len(po):
            diffs.append(f'opp board size {len(po)} v {len(lo)}')
        for i, (lp, pp) in enumerate(zip(lo, po)):
            tag = f'opp[{i}] {nn(lp["name"])}'
            if cname(pp['card']) != nn(lp['name']):
                diffs.append(f'{tag}: card {pp["card"]}')
            if pp['hp'] != lp.get('hp_now'):
                diffs.append(f'{tag}: hp {pp["hp"]} v {lp.get("hp_now")}')
            pe = collections.Counter(pp.get('energy') or [])
            if pe != ebt(lp):
                diffs.append(f'{tag}: energy {dict(pe)} v {dict(ebt(lp))}')
            pt = [cname(x) for x in pp.get('tools') or []]
            if (pt[0] if pt else None) != tool(lp):
                diffs.append(f'{tag}: tool {pt} v {tool(lp)}')
            pc = pp.get('conditions') or []
            lc = list(dict.fromkeys(CONDS.get(str(x).lower(), str(x)) for x in lp.get('special_conditions') or []))
            if sorted(pc) != sorted(lc):
                diffs.append(f'{tag}: conditions {pc} v {lc}')
            card = C.BYID.get(cid(pp['card']))
            if card is None:
                diffs.append(f'{tag}: printing not in DB')
                continue
            cap = hp_cap(card, pp.get('tools') or [], stad)
            if pp['hp'] > cap:
                diffs.append(f'{tag}: hp {pp["hp"]} above max {cap}')
            if lp.get('hp_max') is not None and lp['hp_max'] != cap:
                diffs.append(f'{tag}: ledger hp_max {lp["hp_max"]} v card max {cap} [{pp["card"]}] ({lp.get("hp_max_basis")})')
            funcs = C.functions(nn(lp['name']))
            pfun = [f for f in funcs if any(C.is_pokemon(C.BYID[i]) for i in f)]
            if len(pfun) > 1:
                amb = [a for a in p.get('opp_ambiguous') or [] if a['name'] == nn(lp['name']) and not a.get('under') and not a.get('where')]
                W(f'  OPP-PRINTING {tag}: used {pp["card"]}; functions {[f[0] for f in pfun]}; flagged={bool(amb)} variant={lp.get("variant")!r}')
            beh = [cname(x) for x in pp.get('behind') or []]
            if beh != C.chain_down(card['id']):
                diffs.append(f'{tag}: behind {beh} v printed line {C.chain_down(card["id"])}')
        oh = (t.get('opponent_hand_at_owner_turn_start') or {}).get('count')
        if p['opp']['hand_count'] != oh:
            diffs.append(f'opp hand {p["opp"]["hand_count"]} v ledger {oh}')
        # 6 stadium
        sd = b.get('stadium')
        sby = sd.get('played_by') if isinstance(sd, dict) else None
        sname = nn(sd.get('name') if isinstance(sd, dict) else sd) if sd and str(sd).strip().lower() not in ('none', 'null', 'empty', 'no stadium') else None
        ps = p.get('stadium')
        if (cname(ps['card']) if ps else None) != sname:
            diffs.append(f'stadium {ps} v ledger {sd!r}')
        elif ps:
            W(f'  STADIUM {ps} (ledger played_by={sby!r})')
        # 4 conservation (his side), by printing
        vis = collections.Counter(p['me']['hand'] + p['me']['discard'])
        for x in pb:
            vis[x['card']] += 1
            for y in (x.get('behind') or []) + (x.get('tools') or []):
                vis[y] += 1
        if ps and ps.get('owner') == 0:
            vis[ps['card']] += 1
        over = {c: n - deck.get(c, 0) for c, n in vis.items() if n > deck.get(c, 0)}
        if over:
            diffs.append(f'cards seen above the deck list: {over}')
        implied = 20 - sum(vis.values())
        if 'deck_count' in p['me'] and p['me']['deck_count'] != implied:
            diffs.append(f'deck_count {p["me"]["deck_count"]} v implied {implied}')
        # deck size from the ledger: draws remaining? (none in these ledgers); print implied
        # 4b knockouts == opponent points (no ex in his decks)
        if p['me'].get('knockouts') != pts[1]:
            diffs.append(f'knockouts {p["me"].get("knockouts")} v opponent points {pts[1]}')
        # 7 energy zone
        z = b['owner'].get('energy_zone') or {}
        zt = C.etype((z.get('this_turn') or {}).get('type'))
        zn = C.etype((z.get('next') or {}).get('type'))
        att = [C.etype((q.get('energy') or {}).get('type')) for q in t.get('plays_in_order') or [] if str(q.get('kind')) in ('energy_attachment', 'energy', 'attach_energy') and isinstance(q.get('energy'), dict)]
        za = (((t.get('board_after') or {}).get('owner') or {}).get('energy_zone') or {})
        zan = C.etype((za.get('next') or {}).get('type'))
        W(f'  ZONE pos now={p["me"]["energy_now"]} next={p["me"]["energy_next"]} | ledger this={zt} next={zn} attached={att} after.next={zan}')
        if zt and p['me']['energy_now'] != zt:
            diffs.append(f'energy_now {p["me"]["energy_now"]} v zone {zt}')
        if att and att[0] and p['me']['energy_now'] != att[0]:
            diffs.append(f'energy_now {p["me"]["energy_now"]} v attached {att[0]}')
        for e in (p['me']['energy_now'], p['me']['energy_next']):
            if e and e not in en:
                diffs.append(f'zone energy {e} not in deck energy {en}')
        # discard summary
        W(f'  DISCARD {sorted(collections.Counter(p["me"]["discard"]).items())} energy {dict(collections.Counter(p["me"]["discard_energy"]))} | implied deck {implied} | knockouts {p["me"].get("knockouts")}')
        W(f'  OPPDISC {p["opp"].get("discard")} energy {p["opp"].get("discard_energy")}')
        # 6b effects: opponent's previous attacks with lasting text; position's turn_effects and board effects
        effs = []
        for q in (prev_opp or {}).get('plays_in_order') or []:
            if 'attack' in str(q.get('kind')):
                cn = str(q.get('card_name') or '')
                res = str(q.get('result') or q.get('details') or '')
                att_names = [nn(cn.split(':')[0])] if ':' in cn else [nn(cn)]
                act = inst((prev_opp.get('board_at_start') or {}).get('opponent'))
                if act:
                    att_names.append(nn(act[0]['name']))
                texts = []
                for an in dict.fromkeys(att_names):
                    for c in C.BYNAME.get(an, []):
                        if not C.is_pokemon(c):
                            continue
                        for a in c.get('attacks') or []:
                            if a.get('title') and C.norm_text(a['title']) in C.norm_text(cn + ' ' + res) and a.get('effect'):
                                texts.append(f'{an} {a["title"]}: {a["effect"]}')
                effs.append(f'{cn} -> {res[:140]} || ' + ' / '.join(dict.fromkeys(texts)))
        W(f'  PREV-OPP-ATTACK {effs}')
        fx = [(x['card'], x.get('effects')) for x in pb + po if x.get('effects')]
        W(f'  TURN_EFFECTS {p.get("turn_effects")} BOARD-EFFECTS {fx}')
        # 9 flags
        W(f'  FLAGS usable={p["usable"]} approx={p["approximate"]} ({p["approximate_reason"]}) exact_list={p["exact_list"]} heldout={p["heldout"]} opp_amb={[(a["name"], a["used"], a["could_also_be"]) for a in p["opp_ambiguous"]]} switch2={PL[p["id"]]["switch2_flag"]} [{PL[p["id"]]["switch2_in_his_cards_here"]} | {PL[p["id"]]["switch2_opponent_board"]} | {PL[p["id"]]["switch2_opponent_possible"]}]')
        # 8 plan side by side
        W(f'  PLAN {p["his_plan"]} ended={p["his_plan_ended"]} trunc={p["plan_truncated_at"]} src={p["hand_source"]}')
        for i, q in enumerate(t.get('plays_in_order') or []):
            W(f'     L[{i}] {q.get("kind")} | {q.get("card_name")} | tgt={str(q.get("target"))[:50]} | {str(q.get("result") or q.get("details") or "")[:150]} | resp={q.get("response")}')
        if t.get('automatic_events_in_order'):
            W(f'     AUTO {json.dumps(t.get("automatic_events_in_order"), ensure_ascii=False)[:400]}')
        W(f'  NOTES {p["notes"][:600]}')
        head = f'== {p["id"]}: ' + ('OK' if not diffs else f'{len(diffs)} DIFF')
        W(head)
        for d in diffs:
            W('   DIFF ' + d)
        summary[p['id']] = diffs
out.close()
json.dump(summary, open(os.path.join(R8, 'check_summary.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('positions', len(summary), 'with diffs', sum(1 for v in summary.values() if v))
for k, v in summary.items():
    for d in v:
        print(k, '|', d)
