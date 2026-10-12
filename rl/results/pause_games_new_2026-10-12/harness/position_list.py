#!/usr/bin/env python3
"""The position list for a bot comparison (nothing is run): one row per position with the game, turn, Dustin's move, the old km3 read's first move and whether they matched,
the deck and opponent names, and the rules switch 2 flag, now BY PRINTING: a card is flagged when its function (cardlib.py) is one the switch changed, whatever its name.
usage: position_list.py POSITIONS.json OLD_POSITIONS.json OLD_KM3_SUMMARY.json GAMES_META.json DECKS_DIR OUT_PREFIX
(the old files are the first version's: its km3 read stays in the list, marked `superseded` for every position whose content changed, `stands` for the others)

The switch's list (rl/engine-2026-10-12/README.md, results/engine_switch_rules2_2026-10/PLAN.md section 0), by what the cards are:
- attacks that now flip Meowth's / Togekiss's / Bastiodon's / Hisuian Goodra's coin when their damage lands: Wild Swing, Wellspring Dance, Tornado Shot, Double Splash,
  Triple Bombardment, Mischievous Ring, Litter, and Mega Kangaskhan ex's second punch; and the coin Abilities they meet: Carefree Steps (Meowth B2 124), Celestial Blessing
  (Togekiss), Guarded Grill (Bastiodon), Securely Sheltered (Hisuian Goodra); Guts, Perish Body; Will; Victory Star (Victini); Trap Territory (Ariados); Luxury Coin; Fossils
  (Item cards, no Fossil under an Item lock); the attacks whose hit back now takes Weakness: Cursed Jewel, Spike Armor, Bristling Spikes, Needle Lariat, Shell Trap; Bounded Field."""
import collections, json, os, re, sys

import cardlib as C

Q = '/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/'

ATTACK_SITES = ['Wild Swing', 'Wellspring Dance', 'Tornado Shot', 'Double Splash', 'Triple Bombardment', 'Mischievous Ring', 'Litter']
RETURN_DAMAGE = ['Cursed Jewel', 'Spike Armor', 'Bristling Spikes', 'Needle Lariat', 'Shell Trap']
ABILITIES = ['Guts', 'Perish Body', 'Victory Star', 'Trap Territory', 'Carefree Steps', 'Celestial Blessing', 'Guarded Grill', 'Securely Sheltered']
TRAINERS = {'Will': 'Will', 'Bounded Field': 'Bounded Field'}


def build_affected():
    out = collections.defaultdict(set)
    for c in C.CARDS:
        i = c['id']
        for a in c.get('attacks') or []:
            t = a.get('title')
            if t in ATTACK_SITES:
                out[i].add(f'coin-ability trigger attack ({t})')
            if t in RETURN_DAMAGE:
                out[i].add(f'hit back takes Weakness ({t})')
        ab = C.ability_title(c)
        if ab in ABILITIES:
            out[i].add(f'Ability {ab}')
        if not C.is_pokemon(c):
            n = C.nname(c['name'])
            if n in TRAINERS:
                out[i].add(TRAINERS[n])
            if 'Luxury Coin' in n:
                out[i].add('Luxury Coin')
            if 'Fossil' in str(c.get('trainer_card_type')) or 'Fossil' in n or n == 'Old Amber':
                out[i].add('Fossil (Item card)')
        elif C.nname(c['name']) == 'Mega Kangaskhan ex':
            out[i].add('coin-ability trigger attack (Mega Kangaskhan ex second punch)')
    return {k: sorted(v) for k, v in out.items()}


AFFECTED_IDS = build_affected()
AFFECTED_SIGS = collections.defaultdict(set)     # function -> reasons (every printing of a function is affected the same way)
for _i, _r in AFFECTED_IDS.items():
    AFFECTED_SIGS[C.SIG[_i]].update(_r)
AFFECTED_NAMES = collections.defaultdict(set)
for _i, _r in AFFECTED_IDS.items():
    AFFECTED_NAMES[C.nname(C.BYID[_i]['name'])].update(_r)


def card_id(s):
    m = re.search(r'([A-Z][A-Za-z0-9\-]{0,4} \d{3})$', s)
    return m.group(1) if m else None


def flag_cards(strings):
    """{card string: reasons} for the cards (as 'Name ID') whose function is on the switch's list"""
    out = {}
    for s in strings:
        i = card_id(s)
        if i in C.SIG and C.SIG[i] in AFFECTED_SIGS:
            out[s] = sorted(AFFECTED_SIGS[C.SIG[i]])
    return out


def fmt(d):
    return '; '.join(f'{k} [{", ".join(v)}]' for k, v in sorted(d.items()))


def position_cards(p):
    """his cards and the opponent's board cards of a position, as 'Name ID' strings"""
    mine, theirs = [], []
    mine += p['me']['hand'] + p['me']['discard']
    for b in p['me']['board']:
        mine += [b['card']] + b.get('behind', []) + b.get('tools', [])
    if p.get('stadium'):
        mine.append(p['stadium']['card'])
    for b in p['opp']['board']:
        theirs += [b['card']] + b.get('behind', []) + b.get('tools', [])
    return mine, theirs


def same_content(a, b):
    """is the new position the old one? (his cards, boards, discard, Energy, Stadium, effects and plan; notes and flags do not count)"""
    keys = [('me', 'hand'), ('me', 'discard'), ('me', 'board'), ('me', 'energy_now'), ('me', 'energy_next'), ('opp', 'board'), ('opp', 'hand_count')]
    for k1, k2 in keys:
        x, y = a[k1][k2], b[k1][k2]
        if k2 in ('hand', 'discard'):
            x, y = sorted(x), sorted(y)
        if x != y:
            return False, f'{k1}.{k2} differs'
    for k in ('points', 'stadium', 'his_plan', 'turn_count'):
        if a.get(k) != b.get(k):
            return False, f'{k} differs'
    return True, ''


def main():
    pos_f, old_f, km3_f, meta_f, decks_dir, out = sys.argv[1:7]
    POS = json.load(open(pos_f, encoding='utf-8'))
    OLD = {p['id']: p for p in json.load(open(old_f, encoding='utf-8'))}
    KM3 = {r['id']: r for r in json.load(open(km3_f, encoding='utf-8'))}
    META = json.load(open(meta_f, encoding='utf-8'))
    games = {}
    for g, m in META.items():
        short = g.replace('kw-', '')
        deck_path = os.path.join(decks_dir, f'KW{short}.txt')
        if not os.path.exists(deck_path):
            continue
        folder = Q + m['folder']
        led = json.load(open(folder + '/TURN_LEDGER.json', encoding='utf-8'))
        pg = json.load(open(folder + '/PAUSE_GAME.json', encoding='utf-8'))
        oc = pg.get('outcome') or {}
        oc = oc if isinstance(oc, dict) else {'result': str(oc)}
        opp_name = oc.get('opponent') if isinstance(oc.get('opponent'), str) else pg.get('opponent')
        deck_cards = []
        for l in open(deck_path, encoding='utf-8'):
            mm = re.match(r'(\d+) (.+) ([A-Za-z0-9\-]+ \d{3})\s*$', l)
            if mm:
                deck_cards.append(f'{mm.group(2)} {mm.group(3)}')
        seen = set()
        for t in led['turns']:
            for key in ('board_at_start', 'board_after'):
                side = ((t.get(key) or {}).get('opponent')) or {}
                for p in [side.get('active')] + list(side.get('bench_in_position_order') or []):
                    if p and p.get('name') and C.nname(p['name']).lower() not in ('none', 'empty'):
                        seen.add(C.nname(p['name']))
            if not str(t.get('who_played', '')).startswith('owner'):
                for p in t.get('plays_in_order') or []:
                    if p.get('card_name'):
                        seen.add(C.nname(p['card_name']).split(':')[0])
                    txt = json.dumps(p, ensure_ascii=False)
                    for a in ATTACK_SITES + RETURN_DAMAGE:
                        if a in txt:
                            seen.add('attack:' + a)
        games[short] = dict(deck_name=pg.get('deck_name'), opponent=opp_name, result=oc.get('result') or oc.get('owner'), method=oc.get('method'), deck_cards=deck_cards, opp_seen=seen)
    rows = []
    for p in POS:
        short = p['game'].replace('kw-', '')
        G = games[short]
        mine, theirs = position_cards(p)
        deck_hits = flag_cards(G['deck_cards'])
        here_mine = flag_cards(mine)
        here_opp = flag_cards(theirs)
        possible = {}
        for amb in p.get('opp_ambiguous') or []:
            for alt in amb.get('could_also_be') or []:
                f = flag_cards([f'{amb["name"]} {alt}'])
                possible.update(f)
        seen_possible = {n: sorted(AFFECTED_NAMES[n]) for n in G['opp_seen'] if n in AFFECTED_NAMES and not any(s.startswith(n + ' ') for s in here_opp)}
        seen_attacks = sorted(n[7:] for n in G['opp_seen'] if n.startswith('attack:'))
        flag = 'yes' if (deck_hits or here_mine or here_opp) else ('possible' if (possible or seen_possible or seen_attacks) else 'no')
        s = KM3.get(p['id'])
        old = OLD.get(p['id'])
        if old is None:
            km3_read, why = 'none (new position)', 'a position the first version did not have'
        else:
            same, why = same_content(p, old)
            km3_read = 'stands (position unchanged)' if same else f'superseded ({why})'
        his = p['his_plan']
        km_first = max(s['first'].items(), key=lambda kv: kv[1]) if s and s['first'] else ('', 0)
        rows.append(dict(
            position_id=p['id'], game_id=short, game_turn=p['turn_count'], his_turn=p['his_turn'],
            deck_name=G['deck_name'], opponent_name=G['opponent'], result=f"{G['result']}{(' by ' + G['method']) if G['method'] else ''}",
            usable='yes' if p.get('usable', True) else 'no', usable_reason=p.get('usable_reason') or '',
            his_first_move=(his[0] if his else ('EndTurn' if p.get('his_plan_ended') else '')), his_plan=' > '.join(his) if (his or p.get('his_plan_ended')) else '(none: the game ended before he played)',
            km3_read=km3_read, km3_first_move=km_first[0] if s else '', km3_first_count=(f"{km_first[1]}/{s['n']}" if s else ''),
            km3_first_match=(s and ('agree' if s['same_first'] / s['n'] >= 10 / 12 else ('differ' if s['same_first'] / s['n'] <= 2 / 12 else 'split'))) if s and s['comparable'] else ('' if not s else 'no plan recorded'),
            km3_modal_plan=' > '.join(s['modal']) if s else '',
            switch2_flag=flag,
            switch2_in_his_deck=fmt(deck_hits), switch2_in_his_cards_here=fmt(here_mine), switch2_opponent_board=fmt(here_opp),
            switch2_opponent_possible=fmt(possible) + ('; ' if possible and (seen_possible or seen_attacks) else '') + '; '.join([f'{n} (seen by name) [{", ".join(r)}]' for n, r in sorted(seen_possible.items())] + [f'attack {a} used' for a in seen_attacks]),
            his_cards_not_settled='; '.join(sorted(set(re.findall(r'([^;]+?): (?:which of|the ledger does not tell)[^;]*', p['notes'])))),
            opponent_cards_not_settled='; '.join(f"{a['name']}{' under ' + a['under'] if a.get('under') else ''} (used {a['used']}, could be {', '.join(a['could_also_be'])})" for a in p.get('opp_ambiguous') or []),
            engine_note={'yes': 'read on the official engine main-c045ede', 'possible': 'read on the official engine main-c045ede if the opponent card is the flagged one', 'no': 'no switch-2 card here: the older and the official engine should agree'}[flag],
        ))
    json.dump(rows, open(out + '.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    cols = list(rows[0].keys())
    with open(out + '.tsv', 'w', encoding='utf-8', newline='') as f:
        f.write('\t'.join(cols) + '\n')
        for r in rows:
            f.write('\t'.join(str(r[c]).replace('\t', ' ').replace('\n', ' ') for c in cols) + '\n')
    cnt = collections.Counter(r['switch2_flag'] for r in rows)
    rd = collections.Counter(r['km3_read'].split(' ')[0] for r in rows)
    print(len(rows), 'positions; switch 2:', dict(cnt), '; km3 read:', dict(rd), '; unusable:', sum(1 for r in rows if r['usable'] == 'no'))
    by_game = collections.OrderedDict()
    for r in rows:
        by_game.setdefault(r['game_id'], []).append(r)
    for g, rs in by_game.items():
        print(f"{g}: {len(rs)} positions | flag {dict(collections.Counter(r['switch2_flag'] for r in rs))} | deck: {rs[0]['switch2_in_his_deck'] or '-'}")


if __name__ == '__main__':
    main()
