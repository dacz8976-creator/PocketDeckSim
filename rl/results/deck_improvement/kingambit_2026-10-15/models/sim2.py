"""Setup simulation for deck 01 (Kingambit) and candidate lists. Solitaire: no opponent board, no Knock Outs,
no disruption; the opponent enters only through its hand size (for Copycat), sampled from Dustin's pause-game
positions. Fixed seed. Policy is stated in POLICY below and applied identically to every list.
usage: python3 sim.py N_PER_SEAT out.json
"""
import random, json, sys, collections

SEED = 20000000151
POS = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/positions_all.json"

BASIC = {'Pawniard', 'PawniardPB', 'Glimmet', 'Grimer', 'Regigigas'}
EVO_FROM = {'Glimmora': 'Glimmet', 'Muk': 'Grimer', 'Bisharp': 'Pawniard*'}
PAWN = {'Pawniard', 'PawniardPB'}
LISIA_OK = {'Pawniard'}  # Basics with 50 HP or less in these lists: only Pawniard B3a 041 (50). PawniardPB is 60.
POKEMON = BASIC | {'Glimmora', 'Muk', 'Bisharp', 'Kingambit'}

def opp_hand_pool():
    d = json.load(open(POS, encoding='utf-8'))
    v = [p['opp']['hand_count'] for p in d if 1 <= p['his_turn'] <= 6]
    return v

class G:
    __slots__ = ('deck', 'hand', 'board', 'mesa', 't', 'rng', 'opp', 'stadium_played', 'mesa_used', 'policy')

def line_of(name):
    if name in PAWN or name in ('Bisharp', 'Kingambit'):
        return 'K'
    if name in ('Glimmet', 'Glimmora'):
        return 'G'
    if name in ('Grimer', 'Muk'):
        return 'M'
    return 'R'

def has_on_board(g, names):
    return any(m[0] in names for m in g.board)

def value(g, c):
    """How much the setup plan wants this Pokemon card right now (used for May / Pokemon Communication)."""
    kg_in_play = has_on_board(g, ('Kingambit',))
    if c in PAWN:
        return 10 if not has_on_board(g, PAWN | {'Bisharp', 'Kingambit'}) else 1
    if c == 'Kingambit':
        return 10 if not kg_in_play and g.hand.count('Kingambit') <= 1 else 1
    if c == 'Bisharp':
        return 6 if not kg_in_play and not has_on_board(g, ('Bisharp',)) else 1
    if c == 'Glimmet':
        return 7 if not has_on_board(g, ('Glimmet', 'Glimmora')) else 3
    if c == 'Glimmora':
        return 7 if has_on_board(g, ('Glimmet',)) and not has_on_board(g, ('Glimmora',)) else 2
    if c == 'Grimer':
        return 7 if not has_on_board(g, ('Grimer', 'Muk')) else 0
    if c == 'Muk':
        return 7 if has_on_board(g, ('Grimer',)) and not has_on_board(g, ('Muk',)) else 2
    if c == 'Regigigas':
        return 2
    return 0

def draw(g, n=1):
    for _ in range(n):
        if g.deck and len(g.hand) < 10:
            g.hand.append(g.deck.pop())

def take_random(g, pred):
    idx = [i for i, c in enumerate(g.deck) if pred(c)]
    if not idx or len(g.hand) >= 10:
        return None
    i = g.rng.choice(idx)
    c = g.deck.pop(i)
    g.hand.append(c)
    return c

def missing_cores(g):
    """Core lines with no Pokemon on board whose Basic is still obtainable (in deck)."""
    n = 0
    if not has_on_board(g, PAWN | {'Bisharp', 'Kingambit'}) and any(c in PAWN for c in g.deck):
        n += 1
    if not has_on_board(g, ('Glimmet', 'Glimmora')) and 'Glimmet' in g.deck:
        n += 1
    if not has_on_board(g, ('Grimer', 'Muk')) and 'Grimer' in g.deck:
        n += 1
    return n

def place_basics(g, setup=False):
    changed = False
    while True:
        basics = [c for c in g.hand if c in BASIC]
        if not basics or len(g.board) >= 4:
            return changed
        def prio(c):
            if c in PAWN and not has_on_board(g, PAWN | {'Bisharp', 'Kingambit'}):
                return 0
            if c == 'Glimmet' and not has_on_board(g, ('Glimmet', 'Glimmora')):
                return 1
            if c == 'Grimer' and not has_on_board(g, ('Grimer', 'Muk')):
                return 2
            if c == 'Glimmet':
                return 3
            if c in PAWN:
                return 4
            return 5  # Regigigas
        c = min(basics, key=prio)
        core = prio(c) <= 2
        if not core and g.board:
            # keep a slot for each core line still missing whose Basic is in the deck
            if 4 - len(g.board) <= missing_cores(g):
                return changed
        g.hand.remove(c)
        g.board.append([c, g.t, -1, 0])  # name, turn placed (0 = setup), turn evolved, energy
        changed = True

def evolve(g):
    if g.t < 2:
        return False
    changed = False
    t = g.t
    for m in g.board:
        ok = m[1] < t and m[2] < t
        if not ok:
            continue
        n = m[0]
        if n == 'Bisharp' and 'Kingambit' in g.hand:
            g.hand.remove('Kingambit'); m[0] = 'Kingambit'; m[2] = t; changed = True
        elif n in PAWN:
            if 'Kingambit' in g.hand and 'Rare Candy' in g.hand and not has_on_board(g, ('Kingambit',)):
                g.hand.remove('Kingambit'); g.hand.remove('Rare Candy'); m[0] = 'Kingambit'; m[2] = t; changed = True
            elif 'Bisharp' in g.hand and not has_on_board(g, ('Bisharp', 'Kingambit')):
                g.hand.remove('Bisharp'); m[0] = 'Bisharp'; m[2] = t; changed = True
        elif n == 'Glimmet' and 'Glimmora' in g.hand:
            g.hand.remove('Glimmora'); m[0] = 'Glimmora'; m[2] = t; changed = True
        elif n == 'Grimer' and 'Muk' in g.hand:
            g.hand.remove('Muk'); m[0] = 'Muk'; m[2] = t; changed = True
    return changed

def items(g):
    changed = False
    if not g.stadium_played and not g.mesa and 'Mesagoza' in g.hand:
        g.hand.remove('Mesagoza'); g.mesa = True; g.stadium_played = True; changed = True
    if g.mesa and not g.mesa_used:
        g.mesa_used = True
        if g.rng.random() < 0.5:
            take_random(g, lambda c: c in POKEMON)
        changed = True
    while 'Poke Ball' in g.hand and any(c in BASIC for c in g.deck):
        g.hand.remove('Poke Ball')
        take_random(g, lambda c: c in BASIC)
        changed = True
    if 'Comm' in g.hand:
        spares = [c for c in g.hand if c in POKEMON and value(g, c) <= 2]
        wanted = [c for c in g.deck if c in POKEMON and value(g, c) >= 6]
        if spares and wanted:
            sp = min(spares, key=lambda c: value(g, c))
            g.hand.remove('Comm'); g.hand.remove(sp)
            take_random(g, lambda c: c in POKEMON)
            g.deck.append(sp); g.rng.shuffle(g.deck)
            changed = True
    return changed

def settle(g):
    while True:
        a = items(g); b = place_basics(g); c = evolve(g)
        if not (a or b or c):
            return

def kg_line_pieces_in_hand(g):
    if has_on_board(g, ('Kingambit',)):
        return 0
    return sum(1 for c in g.hand if c in ('Kingambit', 'Rare Candy', 'Bisharp'))

def keepers(g):
    k = kg_line_pieces_in_hand(g)
    for c in g.hand:
        if c == 'Glimmora' and has_on_board(g, ('Glimmet',)) and not has_on_board(g, ('Glimmora',)):
            k += 1
        if c == 'Muk' and has_on_board(g, ('Grimer',)) and not has_on_board(g, ('Muk',)):
            k += 1
    return k

def supporter(g):
    h = g.hand
    pawn_line = has_on_board(g, PAWN | {'Bisharp', 'Kingambit'}) or any(c in PAWN for c in h)
    kg_have = has_on_board(g, ('Kingambit',)) or 'Kingambit' in h
    if 'Lisia' in h and not pawn_line and any(c in LISIA_OK for c in g.deck):
        h.remove('Lisia')
        for _ in range(2):
            take_random(g, lambda c: c in LISIA_OK)
        return 'Lisia'
    if 'Juliana' in h and not kg_have and 'Kingambit' in g.deck:
        h.remove('Juliana')
        take_random(g, lambda c: c == 'Kingambit')
        return 'Juliana'
    if 'May' in h and any(c in POKEMON and value(g, c) >= 6 for c in g.deck):
        h.remove('May')
        got = 0
        for _ in range(2):
            if take_random(g, lambda c: c in POKEMON):
                got += 1
        for _ in range(got):
            pk = [c for c in h if c in POKEMON]
            if not pk:
                break
            c = min(pk, key=lambda c: value(g, c))
            h.remove(c); g.deck.append(c)
        g.rng.shuffle(g.deck)
        return 'May'
    N = g.rng.choice(g.opp)
    hsz = len(h) - 1  # hand after the Copycat leaves it
    kp = keepers(g)
    has_pr = 'PR' in h and bool(g.deck)
    cop = False
    if 'Copycat' in h:
        one_away = (has_on_board(g, PAWN) and not has_on_board(g, ('Kingambit',))
                    and (('Kingambit' in h) != ('Rare Candy' in h)))
        if g.policy == 'never':
            cop = False
        elif g.policy == 'smart' and one_away:
            cop = False  # Pawniard down and one of Kingambit / Rare Candy in hand: keep it
        elif g.policy in ('eager', 'smart') and kp == 0 and N >= 3:
            cop = True  # Copycat even over Professor's Research when the hand holds nothing to keep
        elif has_pr:
            cop = False  # Professor's Research first, Copycat kept for a smaller hand
        elif g.policy in ('loose', 'eager', 'smart'):
            cop = True  # always play a Supporter when one is in hand, whatever the hand holds
        else:
            if kp == 0:
                cop = N >= 2 and N >= hsz - 1
            else:
                cop = (N - hsz) >= 3
    if cop:
        h.remove('Copycat')
        g.deck.extend(h); h.clear(); g.rng.shuffle(g.deck)
        draw(g, N)
        return 'Copycat'
    if has_pr:
        h.remove('PR'); draw(g, 2)
        return 'PR'
    return None

def attach(g, seat):
    if seat == 'first' and g.t == 1:
        return
    line = [m for m in g.board if (m[0] in PAWN or m[0] in ('Bisharp', 'Kingambit')) and m[3] < 2]
    if line:
        line.sort(key=lambda m: (m[0] != 'Kingambit', m[0] != 'Bisharp', -m[3], m[1]))
        line[0][3] += 1

def play_game(deck_list, seat, rng, opp, policy, T=5):
    g = G(); g.rng = rng; g.opp = opp; g.policy = policy
    deck = list(deck_list); rng.shuffle(deck)
    hand = deck[:5]; rest = deck[5:]
    if not any(c in BASIC for c in hand):
        i = rng.randrange(5)
        bi = [j for j, c in enumerate(rest) if c in BASIC]
        j = rng.choice(bi)
        hand[i], rest[j] = rest[j], hand[i]
        rng.shuffle(rest)
    g.deck = rest; g.hand = hand; g.board = []; g.mesa = False; g.t = 0
    rec = {}
    basics = [c for c in hand if c in BASIC]
    rec['PAW_ACTIVE'] = int(all(c in PAWN for c in basics))
    # setup: Active (non-Pawniard preferred), then Bench by the same priority/reservation
    act = sorted(basics, key=lambda c: (c in PAWN, c != 'Regigigas', c != 'Glimmet'))[0]
    hand.remove(act); g.board.append([act, 0, -1, 0])
    place_basics(g, setup=True)
    for t in range(1, T + 1):
        g.t = t; g.stadium_played = False; g.mesa_used = False
        draw(g)
        settle(g)
        s = supporter(g)
        settle(g)
        attach(g, seat)
        names = [m[0] for m in g.board]
        rec[f'PAW_{t}'] = int(any(n in PAWN or n in ('Bisharp', 'Kingambit') for n in names))
        rec[f'KG_{t}'] = int('Kingambit' in names)
        rec[f'BLADE_{t}'] = int(any(m[0] == 'Kingambit' and m[3] >= 2 for m in g.board))
        rec[f'GLM_{t}'] = int('Glimmora' in names)
        rec[f'MUK_{t}'] = int('Muk' in names)
        rec[f'ALL3_{t}'] = int('Kingambit' in names and 'Glimmora' in names and 'Muk' in names)
        gig = 'Regigigas' in names or 'Regigigas' in g.hand
        rec[f'GIGAS_{t}'] = int(gig)
        rec[f'MUKGIGAS_{t}'] = int(gig and 'Muk' in names)
        rec[f'PAWdeck_{t}'] = int(any(c in PAWN for c in g.deck)) if not rec[f'PAW_{t}'] and not any(c in PAWN for c in g.hand) else 0
        rec[f'KGdeck_{t}'] = int('Kingambit' not in names and 'Kingambit' not in g.hand)
        rec[f'RCdeck_{t}'] = int('Kingambit' not in names and 'Rare Candy' not in g.hand and 'Bisharp' not in g.hand
                                 and not ('Bisharp' in names))
        if t == 4 and 'Kingambit' not in names:
            pawn_ok = any((m[0] in PAWN and m[1] < 4) or m[0] == 'Bisharp' for m in g.board)
            kg = 'Kingambit' in g.hand
            rc = 'Rare Candy' in g.hand or 'Bisharp' in names
            if not pawn_ok:
                why = 'no Pawniard in play since an earlier turn' + ('' if (kg and rc) else ' (+ pieces missing)')
            elif not kg and not rc:
                why = 'Pawniard ready; Kingambit and Rare Candy both not in hand'
            elif not kg:
                why = 'Pawniard ready; Kingambit not in hand'
            else:
                why = 'Pawniard ready; Rare Candy not in hand'
            rec['why4'] = why
    return rec

CORE = {'Grimer': 1, 'Muk': 1, 'Glimmet': 2, 'Glimmora': 2, 'Pawniard': 1, 'Kingambit': 1, 'Regigigas': 1,
        'Poke Ball': 2, 'Rare Candy': 1, 'LIP': 1, 'HH': 1, 'PR': 2, 'Ilima': 1, 'Copycat': 2, 'Mesagoza': 1}

def mk(changes, base=CORE):
    d = dict(base)
    for k, v in changes.items():
        d[k] = d.get(k, 0) + v
        assert 0 <= d[k] <= 2, (k, d[k])
    names = collections.Counter()
    for k, v in d.items():
        names['Pawniard' if k in PAWN else k] += v
    assert all(v <= 2 for k, v in names.items() if k != 'Blank'), names
    assert sum(d.values()) == 20, changes
    return [k for k, v in d.items() for _ in range(v)]

PLAYED = dict(CORE); PLAYED['LIP'] = 2; PLAYED['Copycat'] = 1

BLANKED = dict(CORE)
for _k in ('Poke Ball', 'PR', 'Copycat', 'Mesagoza'):
    BLANKED['Blank'] = BLANKED.get('Blank', 0) + BLANKED.pop(_k)
TEST = [
    ('V0 validation: search/draw blanked (compare exact.py deck01)', {}, BLANKED, 'careful'),
    ('S0 deck01 policy careful', {}, CORE, 'careful'),
    ('S1 deck01 policy loose', {}, CORE, 'loose'),
    ('S2 deck01 policy eager', {}, CORE, 'eager'),
    ('S3 deck01 policy never Copycat', {}, CORE, 'never'),
    ('S4 deck01 policy smart (eager, but keep a lone Kingambit or Rare Candy when Pawniard is down)', {}, CORE, 'smart'),
    ('S5 played list policy smart', {}, PLAYED, 'smart'),
    ('S6 played list policy never Copycat', {}, PLAYED, 'never'),
]
LISTS = [
    ('L0 deck01 file', {}, CORE, 'eager'),
    ('L0 deck01 file, careful Copycat', {}, CORE, 'careful'),
    ('L1 played list (QR): 2 LIP 1 Copycat', {}, PLAYED, 'eager'),
    ('L1 played list, careful Copycat', {}, PLAYED, 'careful'),
    ('A1 +Rare Candy -Heavy Helmet', {'Rare Candy': 1, 'HH': -1}, CORE, 'eager'),
    ('A2 +Rare Candy -Mesagoza', {'Rare Candy': 1, 'Mesagoza': -1}, CORE, 'eager'),
    ('A3 +Rare Candy -Copycat', {'Rare Candy': 1, 'Copycat': -1}, CORE, 'eager'),
    ('A4 +Kingambit -Heavy Helmet', {'Kingambit': 1, 'HH': -1}, CORE, 'eager'),
    ('A5 +Pawniard -Regigigas', {'Pawniard': 1, 'Regigigas': -1}, CORE, 'eager'),
    ('A6 +Pawniard -Heavy Helmet', {'Pawniard': 1, 'HH': -1}, CORE, 'eager'),
    ('A7 +Bisharp -Heavy Helmet', {'Bisharp': 1, 'HH': -1}, CORE, 'eager'),
    ('A8 +Juliana -Copycat', {'Juliana': 1, 'Copycat': -1}, CORE, 'eager'),
    ('A9 +Lisia -Copycat', {'Lisia': 1, 'Copycat': -1}, CORE, 'eager'),
    ('A10 +Pokemon Communication -Heavy Helmet', {'Comm': 1, 'HH': -1}, CORE, 'eager'),
    ('A11 +May -Copycat', {'May': 1, 'Copycat': -1}, CORE, 'eager'),
    ('A12 -Mesagoza +Lucky Ice Pop (Mesagoza value)', {'Mesagoza': -1, 'LIP': 1}, CORE, 'eager'),
    ('P1 +Rare Candy +Juliana -Heavy Helmet -Copycat', {'Rare Candy': 1, 'Juliana': 1, 'HH': -1, 'Copycat': -1}, CORE, 'eager'),
    ('P2 +Rare Candy +Juliana -2 Copycat', {'Rare Candy': 1, 'Juliana': 1, 'Copycat': -2}, CORE, 'eager'),
    ('P3 +Rare Candy +Pawniard -Regigigas -Ilima', {'Rare Candy': 1, 'Pawniard': 1, 'Regigigas': -1, 'Ilima': -1}, CORE, 'eager'),
    ('P4 +Rare Candy +Juliana +Pawniard -Regigigas -Ilima -Copycat', {'Rare Candy': 1, 'Juliana': 1, 'Pawniard': 1, 'Regigigas': -1, 'Ilima': -1, 'Copycat': -1}, CORE, 'eager'),
    ('P5 +2 Juliana +Rare Candy -2 Copycat -Heavy Helmet', {'Juliana': 2, 'Rare Candy': 1, 'Copycat': -2, 'HH': -1}, CORE, 'eager'),
    ('P6 +Bisharp +Rare Candy -Heavy Helmet -Mesagoza', {'Bisharp': 1, 'Rare Candy': 1, 'HH': -1, 'Mesagoza': -1}, CORE, 'eager'),
    ('P7 +Kingambit +Rare Candy -Heavy Helmet -Copycat', {'Kingambit': 1, 'Rare Candy': 1, 'HH': -1, 'Copycat': -1}, CORE, 'eager'),
    ('P8 +Rare Candy +Juliana -Regigigas -Ilima (keeps HH, 2 Copycat)', {'Rare Candy': 1, 'Juliana': 1, 'Regigigas': -1, 'Ilima': -1}, CORE, 'eager'),
    ('Q1 played list +Rare Candy +Juliana -Copycat -Lucky Ice Pop', {'Rare Candy': 1, 'Juliana': 1, 'Copycat': -1, 'LIP': -1}, PLAYED, 'eager'),
    ('Q2 played list +Rare Candy -Lucky Ice Pop', {'Rare Candy': 1, 'LIP': -1}, PLAYED, 'eager'),
    ('Q3 played list +Rare Candy +Juliana -2 Lucky Ice Pop', {'Rare Candy': 1, 'Juliana': 1, 'LIP': -2}, PLAYED, 'eager'),
    ('B1 +Juliana -Heavy Helmet', {'Juliana': 1, 'HH': -1}, CORE, 'eager'),
    ('B2 +Lisia -Heavy Helmet', {'Lisia': 1, 'HH': -1}, CORE, 'eager'),
    ('B3 +Kingambit +Rare Candy -Heavy Helmet -Lucky Ice Pop', {'Kingambit': 1, 'Rare Candy': 1, 'HH': -1, 'LIP': -1}, CORE, 'eager'),
    ('B4 +Pawniard +Rare Candy -Heavy Helmet -Lucky Ice Pop', {'Pawniard': 1, 'Rare Candy': 1, 'HH': -1, 'LIP': -1}, CORE, 'eager'),
    ('B5 +Bisharp +Rare Candy -Heavy Helmet -Lucky Ice Pop', {'Bisharp': 1, 'Rare Candy': 1, 'HH': -1, 'LIP': -1}, CORE, 'eager'),
    ('B6 +Rare Candy +Juliana +Pawniard -Heavy Helmet -Lucky Ice Pop -Ilima', {'Rare Candy': 1, 'Juliana': 1, 'Pawniard': 1, 'HH': -1, 'LIP': -1, 'Ilima': -1}, CORE, 'eager'),
    ('B7 +Rare Candy +Juliana +Pokemon Communication -Heavy Helmet -Lucky Ice Pop -Ilima', {'Rare Candy': 1, 'Juliana': 1, 'Comm': 1, 'HH': -1, 'LIP': -1, 'Ilima': -1}, CORE, 'eager'),
    ('P9 +Rare Candy +Juliana -Heavy Helmet -Mesagoza', {'Rare Candy': 1, 'Juliana': 1, 'HH': -1, 'Mesagoza': -1}, CORE, 'eager'),
    ('P10 +Rare Candy +Juliana -Heavy Helmet -Lucky Ice Pop', {'Rare Candy': 1, 'Juliana': 1, 'HH': -1, 'LIP': -1}, CORE, 'eager'),
    ('P11 +Rare Candy +Juliana +Pawniard -Heavy Helmet -Lucky Ice Pop -Mesagoza', {'Rare Candy': 1, 'Juliana': 1, 'Pawniard': 1, 'HH': -1, 'LIP': -1, 'Mesagoza': -1}, CORE, 'eager'),
]

def main():
    n = int(sys.argv[1]); out = sys.argv[2]
    only = sys.argv[3] if len(sys.argv) > 3 else None
    opp = opp_hand_pool()
    res = {'opp_hand_pool': {'n': len(opp), 'mean': sum(opp) / len(opp), 'dist': dict(collections.Counter(opp))}}
    for name, ch, base, pol in (TEST + LISTS if only else LISTS):
        if only and not any(name.startswith(o + ' ') for o in only.split(',')):
            continue
        dl = mk(ch, base)
        res[name] = {'list': dict(collections.Counter(dl)), 'policy': pol}
        for seat in ('first', 'second'):
            rng = random.Random(SEED)
            acc = collections.Counter(); why = collections.Counter()
            for _ in range(n):
                r = play_game(dl, seat, rng, opp, pol)
                for k, v in r.items():
                    if k == 'why4':
                        why[v] += 1
                    else:
                        acc[k] += v
            res[name][seat] = {k: round(v / n, 4) for k, v in sorted(acc.items())}
            res[name][seat + '_why_no_KG_by_4'] = {k: round(v / n, 4) for k, v in why.most_common()}
        f = res[name]['first']; s = res[name]['second']
        print(name, '| first KG2-5', [f[f'KG_{t}'] for t in (2, 3, 4, 5)], 'second', [s[f'KG_{t}'] for t in (2, 3, 4, 5)], flush=True)
    json.dump(res, open(out, 'w'), indent=1)

if __name__ == '__main__':
    main()
