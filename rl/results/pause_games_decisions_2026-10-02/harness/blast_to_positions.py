#!/usr/bin/env python3
"""Draft A v the fixed computer deck (Mega Blastoise ex & Wailord ex): Codex's TURN_LEDGER.json of each of the eight recordings -> constructed-board positions
at the start of every owner turn (harness schema, see examples_positions.json). Both lists are exact (owner list == repo draft A; opponent list from OPPONENT_DECK.json).
A turn is LEFT OUT (and counted, with the reason) when its hand is not fully named, a card name cannot be mapped, or the points are not given.
usage: blast_to_positions.py OUT.json REPORT.json"""
import json, os, re, sys, collections

B = '/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-02_DRAFT_A_V_BLASTOISE_WAILORD/'
MINE = {'Carvanha': 'Carvanha B4 034', 'Mega Sharpedo ex': 'Mega Sharpedo ex B4 035', 'Alolan Vulpix': 'Alolan Vulpix B2 028',
        'Alolan Ninetales ex': 'Alolan Ninetales ex B2 029', 'Lapras': 'Lapras A3 044', 'Misty': 'Misty A1 220',
        "Professor's Research": "Professor's Research P-A 007", 'Poké Ball': 'Poké Ball P-A 005', 'Copycat': 'Copycat B1 225', 'Cyrus': 'Cyrus A2 150',
        'Irida': 'Irida A2a 072', 'Elegant Cape': 'Elegant Cape B3b 065', 'Lucky Ice Pop': 'Lucky Ice Pop B2 145'}
ATTACK = {'Carvanha': 'Sharp Fang', 'Alolan Vulpix': 'Gnaw', 'Alolan Ninetales ex': 'Binding Snow', 'Mega Sharpedo ex': 'Turbo Shark', 'Lapras': 'Surf'}
CHAIN_MINE = {'Mega Sharpedo ex': ['Carvanha'], 'Alolan Ninetales ex': ['Alolan Vulpix']}
# the opponent's printings are not known (OPPONENT_DECK.json: set ids not inferred): chosen by the HP the ledger shows, then by the set the cards come from
OPP_BY_HP = {('Squirtle', 70): 'Squirtle B1a 017', ('Squirtle', 60): 'Squirtle A1 053', ('Wartortle', 90): 'Wartortle B1a 018', ('Wartortle', 80): 'Wartortle A1 054',
             ('Mega Blastoise ex', 230): 'Mega Blastoise ex B1a 020', ('Wailmer', 100): 'Wailmer B4 036', ('Wailord ex', 250): 'Wailord ex B4 037',
             ('Meowth', 50): 'Meowth B2 124', ('Frigibax', 60): 'Frigibax B2a 034', ('Arctibax', 90): 'Arctibax B2a 035', ('Baxcalibur', 140): 'Baxcalibur B2a 036'}
OPP_DEFAULT = {'Squirtle': 'Squirtle B1a 017', 'Wartortle': 'Wartortle B1a 018', 'Mega Blastoise ex': 'Mega Blastoise ex B1a 020', 'Wailmer': 'Wailmer B4 036',
               'Wailord ex': 'Wailord ex B4 037', 'Meowth': 'Meowth B2 124', 'Frigibax': 'Frigibax B2a 034', 'Arctibax': 'Arctibax B2a 035', 'Baxcalibur': 'Baxcalibur B2a 036'}
CHAIN_OPP = {'Wartortle': ['Squirtle'], 'Mega Blastoise ex': ['Squirtle', 'Wartortle'], 'Arctibax': ['Frigibax'], 'Baxcalibur': ['Frigibax', 'Arctibax'], 'Wailord ex': ['Wailmer']}
SHORE = 'Soothing Shore B4 154'


def nname(n):
    if n is None:
        return None
    n = str(n).strip().replace('Poke Ball', 'Poké Ball').replace('’', "'")
    n = re.sub(r'\s*[\(\[].*[\)\]]$', '', n)
    return n


def opp_id(name, hp_max):
    return OPP_BY_HP.get((name, hp_max)) or OPP_DEFAULT.get(name)


def stack_names(p):
    """names under the top card, bottom first, from whichever field this ledger variant uses; None if the ledger gives nothing"""
    es = p.get('evolution_stack')
    if isinstance(es, dict) and es.get('cards_bottom_to_top'):
        names = [nname(x if isinstance(x, str) else x.get('name')) for x in es['cards_bottom_to_top']]
        return names[:-1] if names and names[-1] == nname(p.get('name')) else names
    if isinstance(p.get('evolution_stack_under_top'), list):
        return [nname(x if isinstance(x, str) else x.get('name')) for x in p['evolution_stack_under_top']]
    if isinstance(p.get('evolution_stack_bottom_to_top'), list):
        names = [nname(x.get('name') if isinstance(x, dict) else x) for x in p['evolution_stack_bottom_to_top']]
        return names[:-1] if names and names[-1] == nname(p.get('name')) else names
    return None


def instances(side):
    out = []
    act = side.get('active')
    if act and act.get('name') and not act.get('empty'):
        out.append(act)
    bench = [p for p in (side.get('bench_in_position_order') or []) if p and p.get('name') and not p.get('empty')]
    bench.sort(key=lambda p: (p.get('bench_position') if p.get('bench_position') is not None else 99))
    return out + bench


def iid(p):
    return p.get('instance_id') or p.get('physical_instance')


def make_pk(p, mine, notes):
    name = nname(p['name'])
    hp_max = p.get('hp_max')
    cid = MINE.get(name) if mine else opp_id(name, hp_max)
    if cid is None:
        raise KeyError(f'no card id for {name} ({hp_max})')
    d = {'card': cid, 'hp': p['hp_now']}
    by = ((p.get('attached_energy') or {}).get('by_type')) or {}
    en = []
    for t, n in by.items():
        en += [t] * int(n or 0)
    if en:
        d['energy'] = en
    tool = p.get('tool')
    tools = []
    if tool and str(tool).lower() not in ('none', 'null'):
        tn = nname(tool)
        if mine and tn in MINE:
            tools = [MINE[tn]]
        else:
            raise KeyError(f'unknown tool {tool}')
    if tools:
        d['tools'] = tools
    under = stack_names(p)
    chain = (CHAIN_MINE if mine else CHAIN_OPP).get(name, [])
    if under is None:
        under = chain
        if chain:
            notes.append(f'{name} stack forced by the evolution rules (no Rare Candy in either list)')
    elif under != chain and chain:
        notes.append(f'{name}: ledger stack {under} differs from the rule-forced {chain}; the ledger is used')
    if under:
        if mine:
            d['behind'] = [MINE[u] for u in under]
        else:
            d['behind'] = [OPP_DEFAULT[u] for u in under]
    return d


def tokens_for(p):
    return {t for t in (iid(p), p.get('instance_id'), p.get('physical_instance')) if t}


class Resolver:
    """maps a play's target text to an index in the current owner board list (a list of dicts with name/ids/pos words)"""

    def __init__(self, items):
        self.items = items  # list of {'name', 'ids': set, 'pos': ..}

    def find(self, text, name_hint=None):
        if text is None:
            return None
        t = str(text)
        tl = t.lower()
        # 1. an instance token (O1, O-N1, owner_lapras1, oV2 ...) contained in the text
        hits = []
        for i, it in enumerate(self.items):
            for tok in it['ids']:
                if re.search(r'(?<![A-Za-z0-9])' + re.escape(str(tok)) + r'(?![A-Za-z0-9])', t):
                    hits.append(i)
                    break
        if len(hits) == 1:
            return hits[0]
        # a bare instance token that matches nobody: the Pokemon benched earlier this turn whose play named no id
        if not hits and re.fullmatch(r'[A-Za-z0-9_\-]+', t):
            fresh = [i for i, it in enumerate(self.items) if not it['ids']]
            if len(fresh) == 1:
                self.items[fresh[0]]['ids'].add(t)
                return fresh[0]
        # 2. 'Active' / bench words with a name
        cand = list(range(len(self.items)))
        if name_hint:
            c2 = [i for i in cand if self.items[i]['name'].lower().startswith(name_hint.lower().split()[0])]
            if c2:
                cand = c2
        nm = [i for i in cand if any(w in tl for w in (self.items[i]['name'].lower(), self.items[i]['name'].lower().replace('alolan ', '').replace(' ex', '')))]
        if len(nm) == 1:
            return nm[0]
        if nm:
            cand = nm
        if 'active' in tl and 0 in cand:
            return 0
        m = re.search(r'bench\s*(\d)', tl)
        if m:
            k = int(m.group(1))
            if 0 < k < len(self.items) + 1:
                # screen bench position k = the k-th bench slot; compacted list index = the position among occupied slots
                pos = [i for i in cand if self.items[i].get('bench_position') == k]
                if len(pos) == 1:
                    return pos[0]
        for word, k in (('left', 1), ('middle', 2), ('center', 2), ('right', 3)):
            if word in tl:
                pos = [i for i in cand if self.items[i].get('bench_position') == k]
                if len(pos) == 1:
                    return pos[0]
        if len(cand) == 1:
            return cand[0]
        return None


def build_items(side):
    items = []
    for p in instances(side):
        items.append({'name': nname(p['name']), 'ids': tokens_for(p), 'bench_position': p.get('bench_position')})
    return items


BASICS = {'Carvanha', 'Alolan Vulpix', 'Lapras'}
TOKEN_RE = re.compile(r'(?<![A-Za-z0-9])(?:O-[A-Za-z0-9]+|O\d+|o[A-Z]\d+|owner_[a-z]+\d+)(?![A-Za-z0-9])')


def parse_attack_title(play, active_name):
    return ATTACK.get(active_name) or 'Attack'


def convert_game(gdir, short, actor_game):
    d = json.load(open(B + gdir + '/TURN_LEDGER.json', encoding='utf-8'))
    turns = d['turns']
    owner_idx = [i for i, t in enumerate(turns) if str(t.get('who_played', '')).startswith('owner')]
    first_player = turns[owner_idx[0]]['turn_number'] == 1
    positions, skipped, notes_all = [], [], []
    disc, disc_energy = [], []
    prev_after = None
    stem = gdir.replace('_iOS_auto_sol', '').replace('_iOS_shark_sol', '')
    for k, ti in enumerate(owner_idx):
        t = turns[ti]
        tn = t['turn_number']
        notes = []
        b = t['board_at_start']
        own_inst, opp_inst = instances(b['owner']), instances(b['opponent'])
        # ---- discard bookkeeping from the previous owner turn's plays and any knock-out between then and now
        if k > 0:
            pt = turns[owner_idx[k - 1]]
            for p in pt.get('plays_in_order') or []:
                kind, card, res = p.get('kind'), nname(p.get('card_name')), str(p.get('result') or '')
                if kind in ('card_play', 'item', 'supporter') and card in MINE and card not in ('Elegant Cape',) and card not in BASICS:
                    if card == 'Lucky Ice Pop' and re.search(r'heads', res, re.I) and re.search(r'return', res, re.I):
                        continue
                    disc.append(MINE[card])
                if kind == 'no_effect_attempt':
                    pass
                if kind == 'retreat':
                    m = re.search(r'pay\s*(\d+)\s*Water', res, re.I)
                    if m:
                        disc_energy += ['Water'] * int(m.group(1))
            # knocked-out Pokemon of his: present after the previous turn, gone now
            after = instances(pt.get('board_after', {}).get('owner') or {})
            now_ids = {iid(p) for p in own_inst if iid(p)}
            for p in after:
                if iid(p) and iid(p) not in now_ids:
                    nm = nname(p['name'])
                    st = stack_names(p) or CHAIN_MINE.get(nm, [])
                    disc += [MINE[nm]] + [MINE[s] for s in st]
                    tool = p.get('tool')
                    if tool and str(tool).lower() not in ('none', 'null'):
                        disc.append(MINE[nname(tool)])
                    by = ((p.get('attached_energy') or {}).get('by_type')) or {}
                    for tt, n in by.items():
                        disc_energy += [tt] * int(n or 0)
                    notes.append(f'knocked out between turns: {nm}')
        # ---- the hand
        hs = t.get('hand_at_start') or {}
        raw = hs.get('cards_left_to_right') or []
        names = [nname(c.get('name') if isinstance(c, dict) else c) for c in raw]
        if not raw or any(n is None or n not in MINE for n in names) or (hs.get('count') is not None and hs['count'] != len(names)):
            skipped.append({'game': short, 'turn': tn, 'reason': f'hand not fully named or unmapped: {names} count={hs.get("count")}'})
            continue
        hand = [MINE[n] for n in names]
        # ---- boards
        try:
            me_board = [make_pk(p, True, notes) for p in own_inst]
            opp_board = [make_pk(p, False, notes) for p in opp_inst]
        except KeyError as e:
            skipped.append({'game': short, 'turn': tn, 'reason': f'board: {e}'})
            continue
        pts_me, pts_opp = b['owner'].get('points'), b['opponent'].get('points')
        if pts_me is None or pts_opp is None:
            skipped.append({'game': short, 'turn': tn, 'reason': f'points missing ({pts_me},{pts_opp})'})
            continue
        oh = t.get('opponent_hand_at_owner_turn_start') or {}
        opp_hand = oh.get('count')
        if opp_hand is None and oh.get('supported_range'):
            opp_hand = oh['supported_range'][0]
            notes.append(f"opponent hand range {oh['supported_range']}: the lower end is used")
        if opp_hand is None:
            skipped.append({'game': short, 'turn': tn, 'reason': 'opponent hand count missing'})
            continue
        st = b.get('stadium')
        stadium = {'card': SHORE, 'owner': 1} if st and str(st).lower() not in ('none', 'null') else None
        # ---- his plan, with indices resolved against the board as it changes during the turn
        plan, unresolved, trace = [], [], []
        items = build_items(b['owner'])
        oitems = build_items(b['opponent'])
        resolver = Resolver(items)
        for p in t.get('plays_in_order') or []:
            kind, card, res, tg = p.get('kind'), nname(p.get('card_name')), str(p.get('result') or ''), p.get('target')
            if kind == 'bench' or (kind in ('card_play', 'item', 'supporter') and card in BASICS):
                plan.append(f'Place:{card}')
                ids = set(TOKEN_RE.findall(str(tg))) or ({str(tg)} if tg and re.fullmatch(r'[A-Za-z0-9_\-]+', str(tg)) else set())
                m = re.search(r'bench\s*(\d)', str(tg).lower())
                bp = int(m.group(1)) if m else next((k2 for w, k2 in (('left', 1), ('middle', 2), ('center', 2), ('right', 3)) if w in str(tg).lower()), None)
                items.append({'name': card, 'ids': ids, 'bench_position': bp})
                resolver = Resolver(items)
            elif kind in ('card_play', 'item', 'supporter') and card in MINE and card != 'Elegant Cape':
                plan.append(f'Play:{card}')
                if card == 'Misty':
                    i = resolver.find(tg)
                    plan.append(f'MistyTarget@{i}' if i is not None else 'MistyTarget@?')
                    if i is None:
                        unresolved.append(f'Misty target {tg!r}')
                if card == 'Cyrus':
                    j = Resolver(oitems).find(tg)
                    plan.append(f'Activate:1@{j}' if j is not None else 'Activate:1@?')
                    if j is None:
                        unresolved.append(f'Cyrus target {tg!r}')
            elif kind == 'no_effect_attempt' and card in MINE:
                plan.append(f'Play:{card}')
                plan.append('(the Poké Ball had no target: no search, the card stayed in hand)')
            elif kind in ('tool', 'tool_attachment'):
                plan.append('Play:Elegant Cape')
                i = resolver.find(tg, 'Mega Sharpedo')
                plan.append(f'Tool:Elegant Cape@{i}' if i is not None else 'Tool:Elegant Cape@?')
                if i is None:
                    unresolved.append(f'tool target {tg!r}')
            elif kind == 'evolution':
                i = resolver.find(tg, {'Mega Sharpedo ex': 'Carvanha', 'Alolan Ninetales ex': 'Alolan Vulpix'}.get(card))
                plan.append(f'Evolve:{card}@{i}' if i is not None else f'Evolve:{card}@?')
                if i is None:
                    unresolved.append(f'evolution target {tg!r}')
                else:
                    items[i]['name'] = card
                    resolver = Resolver(items)
            elif kind == 'energy_attachment':
                i = resolver.find(tg)
                trace.append((str(tg), items[i]['name'] if i is not None else None))
                fx = bool(re.search(r'turbo', res, re.I))
                label = f'Attach:1Water@{i if i is not None else "?"} {"fx" if fx else "zone"}'
                plan.append(label)
                if i is None:
                    unresolved.append(f'attach target {tg!r}')
            elif kind == 'retreat':
                # the new Active: an instance token or a name in the target/result text
                i = None
                for cand_text in (str(tg), res):
                    i2 = resolver.find(cand_text)
                    if i2 is not None and i2 != 0:
                        i = i2
                        break
                if i is None:
                    m = re.search(r'promote\s+(\S+)', res)
                    if m:
                        i = resolver.find(m.group(1))
                plan.append(f'Retreat:{i}' if i is not None else 'Retreat:?')
                if i is None:
                    unresolved.append(f'retreat target {tg!r} / {res!r}')
                else:
                    items[0], items[i] = items[i], items[0]
                    resolver = Resolver(items)
            elif kind == 'attack':
                act = items[0]['name'] if items else None
                plan.append(f'Attack:{parse_attack_title(p, act)}')
            # prompt_response, end_turn, attack_selection: nothing played
        # ---- assemble
        pid = f'B-{short}-t{tn:02d}'
        pos = {
            'id': pid, 'game': 'cmp-' + stem, 'his_turn': k + 1, 'deck': 'A', 'turn_count': tn, 'points': [pts_me, pts_opp],
            'me': {'hand': hand, 'discard': list(disc), 'discard_energy': list(disc_energy), 'board': me_board,
                   'energy_now': None if (first_player and tn == 1) else 'Water', 'energy_next': 'Water'},
            'opp': {'hand_count': opp_hand, 'discard_n': 0, 'discard_energy': [], 'board': opp_board, 'energy_next': 'Water'},
            'stadium': stadium, 'turn_effects': [], 'his_plan': plan, 'hand_source': 'codex', 'decision_maker': actor_game,
            'exact_list': True, 'milestones': [], 'unresolved': unresolved,
            'notes': ('; '.join(sorted(set(notes))) + '. ' if notes else '') + 'The opponent\'s discard is not tracked (0); the opponent\'s printings are not known (chosen by the HP shown).',
            'plan_known_prefix': None, '_trace': trace,
        }
        if unresolved:
            # keep only the steps before the first unresolved one
            for si, s in enumerate(plan):
                if '?' in s:
                    pos['plan_known_prefix'] = si
                    break
        positions.append(pos)
    return positions, skipped


RESULT = {'205230': 'won 3-0', '205731': 'won 3-2', '210612': 'won 3-0', '210952': 'lost 2-3', '211613': 'won 3-0', '214254': 'won 3-0', '215203': 'won 3-0', '215825': 'won 3-0'}
LIST_SOURCE = ("exact: his list = OWNER_DECK_SNAPSHOT.json (checked card for card against decks/brews/drafts_2026-10-01/draft-A-shark-tempo.txt); "
               "the computer's list = OPPONENT_DECK.json (all 13 names Complete in the pinned engine's card_status)")
MAXHP = {'Carvanha': 50, 'Mega Sharpedo ex': 190, 'Alolan Vulpix': 60, 'Alolan Ninetales ex': 150, 'Lapras': 110}


def tag_milestones(ps):
    """Mechanical rules (not a reading of the game): see README. ps = one game's positions in turn order."""
    for i, p in enumerate(ps):
        tags = []
        plan = [s for s in p['his_plan'] if not s.startswith('(')]
        names = {b['card'].rsplit(' ', 2)[0]: b for b in p['me']['board']}
        sharp_damaged = any(b['card'].startswith('Mega Sharpedo ex') and b['hp'] < 190 + (30 if b.get('tools') else 0) for b in p['me']['board'])
        sharp_active = p['me']['board'][0]['card'].startswith('Mega Sharpedo ex')
        if any(s.startswith('Evolve:Mega Sharpedo ex') or s.startswith('Evolve:Alolan Ninetales ex') for s in plan) or \
           any(re.match(r'Attach:1Water@([1-9])\d* zone', s) for s in plan):
            tags.append('preparing an attacker')
        if (sharp_active and any(s.startswith('Retreat') for s in plan)) or (sharp_damaged and any(s in ('Play:Lucky Ice Pop', 'Play:Irida') for s in plan)):
            tags.append('managing a sacrifice')
        if any('knocked out between turns' in n for n in p['notes'].split('; ')):
            tags.append('adapting when the plan fails')
        if i == len(ps) - 1 and RESULT[p['id'].split('-')[1]].startswith('won') and any(s.startswith('Attack:') for s in plan):
            tags.append('recognising an immediate win')
        p['milestones'] = tags


def main():
    games = sorted(g for g in os.listdir(B) if g.startswith('2026100') and os.path.isdir(B + g))
    allpos, allskip = [], []
    for g in games:
        short = g[9:15]
        actor = 'Auto' if g.endswith('_auto_sol') else 'Dustin'
        pos, skip = convert_game(g, short, actor)
        for p in pos:
            p['list_source'] = LIST_SOURCE
            p['pilot_result'] = RESULT[short]
            p.pop('plan_known_prefix', None)
            p.pop('_trace', None)
            if p['unresolved']:
                allskip.append({'game': short, 'turn': p['turn_count'], 'reason': 'unresolved plan targets (plan kept)', 'detail': p['unresolved']})
            p.pop('unresolved', None)
        tag_milestones(pos)
        allpos += pos
        allskip += skip
        print(g, actor, 'positions', len(pos), 'skipped', len(skip))
    json.dump(allpos, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump({'positions': len(allpos), 'left_out': [s for s in allskip if 'unresolved' not in s['reason']], 'plans_with_unresolved_targets': [s for s in allskip if 'unresolved' in s['reason']]},
              open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('total', len(allpos), 'positions;', sum(1 for s in allskip if 'unresolved' not in s['reason']), 'turns left out;', sum(1 for s in allskip if 'unresolved' in s['reason']), 'plans with unresolved targets')


if __name__ == '__main__':
    main()

