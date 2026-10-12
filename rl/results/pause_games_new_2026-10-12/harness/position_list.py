#!/usr/bin/env python3
"""The position list for a bot comparison (nothing is run): one row per position with the game, turn, Dustin's move, km3's first move and whether they match,
the deck and opponent names, and a flag for rules switch 2 (main-c045ede): does his deck, the opponent's cards seen in the game, or the position itself hold a
card the switch changed. Flagged rows are the ones a kx3 (or any bot) run must be read on the official engine for.
usage: position_list.py POSITIONS.json KM3_SUMMARY.json GAMES_META.json OUT_PREFIX
Reads the ledgers and PAUSE_GAME.json through games_meta.json's 'folder' and the engine database (engine/database.json) for the card lists."""
import json, os, re, sys, collections

POS = json.load(open(sys.argv[1], encoding='utf-8'))
SUM = {r['id']: r for r in json.load(open(sys.argv[2], encoding='utf-8'))}
META = json.load(open(sys.argv[3], encoding='utf-8'))
OUT = sys.argv[4]
Q = '/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/'
DB = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/engine/database.json'


def nname(n):
    if n is None:
        return ''
    n = str(n).strip().replace('Poke Ball', 'Poké Ball').replace('’', "'")
    return re.sub(r'\s*[\(\[].*[\)\]]$', '', n)


# ---- the switch's list (rl/engine-2026-10-12/README.md, results/engine_switch_rules2_2026-10/PLAN.md section 0), by card name with the rule group
db = json.load(open(DB, encoding='utf-8'))
inner = [c.get('Pokemon') or c.get('Trainer') or c.get('Energy') or c for c in (db if isinstance(db, list) else db.get('cards', list(db.values())))]


def names_where(pred):
    return {nname(c['name']) for c in inner if pred(c)}


AFFECTED = collections.defaultdict(set)   # card name -> set of rule groups
def add(group, names):
    for n in names:
        AFFECTED[n].add(group)

ATTACK_SITES = ['Wild Swing', 'Wellspring Dance', 'Tornado Shot', 'Double Splash', 'Triple Bombardment', 'Mischievous Ring', 'Litter']
for a in ATTACK_SITES:
    add('coin-ability trigger attack (' + a + ')', names_where(lambda c, a=a: any(x.get('title') == a for x in c.get('attacks', []))))
add('coin-ability trigger attack (Mega Kangaskhan ex second punch)', {'Mega Kangaskhan ex'})
add('coin ability defender (Meowth, Togekiss, Bastiodon, Hisuian Goodra)', {'Meowth', 'Togekiss', 'Bastiodon', 'Hisuian Goodra'})
add('Guts', names_where(lambda c: isinstance(c.get('ability'), dict) and c['ability'].get('title') == 'Guts'))
add('Perish Body', names_where(lambda c: isinstance(c.get('ability'), dict) and c['ability'].get('title') == 'Perish Body'))
add('Victory Star', names_where(lambda c: isinstance(c.get('ability'), dict) and c['ability'].get('title') == 'Victory Star'))
add('Will (works for Confused attacker / block coin)', {'Will'})
add('Trap Territory / Ariados retreat cost', {'Ariados'})
add('Luxury Coin', names_where(lambda c: 'hp' not in c and 'Luxury Coin' in c['name']))
add('Fossil (Item card; no Fossil under Item lock)', names_where(lambda c: 'hp' not in c and ('Fossil' in str(c.get('trainer_card_type')) or 'Fossil' in c['name'] or c['name'] == 'Old Amber')))
add('return damage takes Weakness (Cursed Jewel / Spike Armor / Bristling Spikes / Needle Lariat / Shell Trap)', {'Mega Sableye ex', 'Alolan Sandslash', 'Togedemaru', 'Chesnaught', 'Turtonator'})
add('Bounded Field doubles the hit back', {'Bounded Field'})
ATTACK_TITLES = {a: 'attack ' + a for a in ATTACK_SITES}


def groups(names):
    out = {}
    for n in names:
        if n in AFFECTED:
            out[n] = sorted(AFFECTED[n])
    return out


def kind_short(g):
    return g.split(' (')[0]


# ---- per game: deck names, the opponent's cards and attack titles seen anywhere in the ledger, captions
def deck_names(short):
    p = '/home/dacz8976/pgd_vr/all/KW' + short + '.txt'
    out = set()
    for l in open(p, encoding='utf-8'):
        m = re.match(r'(\d+) (.+?) [A-Za-z0-9\-]+ \d{3}\s*$', l)
        if m:
            out.add(nname(m.group(2)))
    return out


GAME = {}
for g, m in META.items():
    folder = Q + m['folder']
    short = g.replace('kw-', '')
    if not os.path.exists('/home/dacz8976/pgd_vr/all/KW' + short + '.txt'):
        continue
    led = json.load(open(folder + '/TURN_LEDGER.json', encoding='utf-8'))
    pg = json.load(open(folder + '/PAUSE_GAME.json', encoding='utf-8'))
    oc = pg.get('outcome') or {}
    oc = oc if isinstance(oc, dict) else {'result': str(oc)}
    opp_name = oc.get('opponent') if isinstance(oc.get('opponent'), str) else pg.get('opponent')
    seen, titles = set(), set()
    for t in led['turns']:
        mine = str(t.get('who_played', '')).startswith('owner')
        for key in ('board_at_start', 'board_after'):
            side = ((t.get(key) or {}).get('opponent')) or {}
            for p in [side.get('active')] + list(side.get('bench_in_position_order') or []):
                if p and p.get('name') and nname(p['name']).lower() not in ('none', 'empty'):
                    seen.add(nname(p['name']))
                    for x in (p.get('evolution_stack') or {}).get('cards_bottom_to_top', []) if isinstance(p.get('evolution_stack'), dict) else []:
                        seen.add(nname(x if isinstance(x, str) else x.get('name')))
                    if p.get('tool') and str(p['tool']).lower() not in ('none', 'null'):
                        seen.add(nname(p['tool']))
        if not mine:
            for p in t.get('plays_in_order') or []:
                if p.get('card_name'):
                    seen.add(nname(p['card_name']))
                txt = json.dumps(p, ensure_ascii=False)
                for a in ATTACK_SITES:
                    if a in txt:
                        titles.add(a)
    GAME[short] = dict(deck_name=pg.get('deck_name'), opponent=opp_name, result=oc.get('result') or oc.get('owner'), method=oc.get('method'),
                       my_names=deck_names(short), opp_seen=seen, opp_titles=titles)


def verdict(r):
    k = r['same_first'] / r['n']
    return 'agree' if k >= 10 / 12 else ('differ' if k <= 2 / 12 else 'split')


rows = []
for p in POS:
    s = SUM.get(p['id'])
    if s is None:
        continue
    short = p['game'].replace('kw-', '')
    G = GAME[short]
    sn = lambda c: re.sub(r' [A-Za-z0-9\-]+ \d{3}$', '', c)
    pos_hand = {sn(c) for c in p['me']['hand']}
    pos_board = {sn(b['card']) for b in p['me']['board']} | {sn(b['card']) for b in p['opp']['board']}
    deck_hits = groups(G['my_names'])
    opp_hits = groups(G['opp_seen'])
    opp_title_hits = sorted(G['opp_titles'])
    here_hits = groups(pos_hand | pos_board)
    flag_deck = bool(deck_hits)
    flag_opp = bool(opp_hits) or bool(opp_title_hits)
    flag_here = bool(here_hits)
    his = s['his']
    km_first = max(s['first'].items(), key=lambda kv: kv[1]) if s['first'] else ('', 0)
    rows.append(dict(
        position_id=p['id'], game_id=short, game_turn=p['turn_count'], his_turn=p['his_turn'],
        deck_name=G['deck_name'], opponent_name=G['opponent'], result=f"{G['result']}{(' by ' + G['method']) if G['method'] else ''}",
        his_first_move=(his[0] if his else ''), his_plan=' > '.join(his) if s['comparable'] else '(none: the game ended before he played)',
        km3_first_move=km_first[0], km3_first_count=f"{km_first[1]}/{s['n']}", km3_first_distribution=', '.join(f'{k} x{v}' for k, v in sorted(s['first'].items(), key=lambda kv: -kv[1])),
        first_match=(verdict(s) if s['comparable'] else 'no plan recorded'), same_plan_seeds=f"{s['same_plan']}/{s['n']}", km3_modal_plan=' > '.join(s['modal']),
        approximate=True, plan_truncated=p.get('plan_truncated_at') is not None,
        switch2_flag=('yes' if (flag_deck or flag_opp or flag_here) else 'no'),
        switch2_in_his_deck='; '.join(f"{n} [{', '.join(kind_short(x) for x in g)}]" for n, g in sorted(deck_hits.items())),
        switch2_in_opponent_cards_seen_in_game='; '.join([f"{n} [{', '.join(kind_short(x) for x in g)}]" for n, g in sorted(opp_hits.items())] + [f'attack {t} used' for t in opp_title_hits]),
        switch2_on_the_table_at_this_position='; '.join(f"{n} [{', '.join(kind_short(x) for x in g)}]" for n, g in sorted(here_hits.items())),
        engine_note=('read on the official engine main-c045ede' if (flag_deck or flag_opp or flag_here) else 'no switch-2 card seen: the 8626a35 harness and c045ede should agree'),
    ))

json.dump(rows, open(OUT + '.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
cols = list(rows[0].keys())
with open(OUT + '.tsv', 'w', encoding='utf-8', newline='') as f:
    f.write('\t'.join(cols) + '\n')
    for r in rows:
        f.write('\t'.join(str(r[c]).replace('\t', ' ').replace('\n', ' ') for c in cols) + '\n')
n = len(rows)
fl = sum(1 for r in rows if r['switch2_flag'] == 'yes')
print(n, 'positions;', fl, 'flagged for switch 2;', n - fl, 'not')
by_game = collections.OrderedDict()
for r in rows:
    by_game.setdefault(r['game_id'], []).append(r)
for g, rs in by_game.items():
    d = rs[0]['switch2_in_his_deck']
    o = rs[0]['switch2_in_opponent_cards_seen_in_game']
    print(f"{g}: {len(rs)} positions, {sum(1 for r in rs if r['switch2_flag'] == 'yes')} flagged | deck: {d or '-'} | opp seen: {o or '-'}")
