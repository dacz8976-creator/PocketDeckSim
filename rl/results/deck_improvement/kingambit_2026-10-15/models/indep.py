"""Independent setup model for the Kingambit check (written from scratch; does not import sim2).
Solitaire, no opponent board. Pocket rules used: 20 cards, 5-card opening hand with the swap rule
(no Basic -> one random hand card swapped for a random Basic, deck reshuffled), both seats draw on own turn 1,
no evolution on own turn 1, Rare Candy not on own turn 1 and not on a Basic put down this turn, Bench of 3,
hand limit 10, one Supporter a turn, Mesagoza once a turn (coin, heads = random Pokemon from deck).
usage: python3 -B indep.py N policy   (policy: loose | eager | never | blank)"""
import sys, random, collections, json

OPP = {1: 4, 2: 11, 3: 17, 4: 21, 5: 12, 6: 7, 7: 3, 8: 1}  # opponent hand sizes (consistency step)
OPP_POOL = [k for k, v in OPP.items() for _ in range(v)]
BASICS = {'Paw', 'Glimmet', 'Grimer', 'Gigas'}
POKE = BASICS | {'King', 'Glimmora', 'Muk'}

def deck(changes):
    base = {'Grimer': 1, 'Muk': 1, 'Glimmet': 2, 'Glimmora': 2, 'Paw': 1, 'King': 1, 'Gigas': 1,
            'Ball': 2, 'Candy': 1, 'Pop': 2, 'Helmet': 1, 'Research': 2, 'Ilima': 1, 'Copycat': 1, 'Mesa': 1}
    for k, v in changes.items():
        base[k] = base.get(k, 0) + v
        if base[k] == 0:
            del base[k]
    d = [k for k, v in base.items() for _ in range(v)]
    assert len(d) == 20, (changes, len(d))
    assert max(base.values()) <= 2
    return d

def game(cards, rng, policy):
    dk = cards[:]
    rng.shuffle(dk)
    hand = dk[:5]; dk = dk[5:]
    if not any(c in BASICS for c in hand):
        i = rng.randrange(5)
        bas = [j for j, c in enumerate(dk) if c in BASICS]
        j = rng.choice(bas)
        hand[i], dk[j] = dk[j], hand[i]
        rng.shuffle(dk)
    # setup: Active = non-Pawniard Basic if any (Gigas > Glimmet > Grimer), bench Pawniard first, then the rest
    order = ['Gigas', 'Glimmet', 'Grimer']
    act = next((c for c in order if c in hand), 'Paw')
    hand.remove(act)
    res = {'paw_active': act == 'Paw'}
    board = [(act, 0)]  # (card, turn put down); turn 0 = setup
    def bench_basics(t):
        for want in ['Paw', 'Glimmet', 'Grimer', 'Glimmet', 'Gigas']:
            names = [c for c, _ in board]
            line_in = 'Paw' in names or 'King' in names
            spare = want in ('Gigas',) or (want == 'Glimmet' and 'Glimmet' in names + ['Glimmora' if 'Glimmora' in names else ''])
            cap = 4 if (want == 'Paw' or line_in or not spare) else 3  # keep a slot for Pawniard
            if len(board) >= cap:
                continue
            if want in hand:
                hand.remove(want); board.append((want, t))
    bench_basics(0)
    mesa_in_play = False
    first = {}
    def draw(n):
        for _ in range(n):
            if dk and len(hand) < 10:
                hand.append(dk.pop())
    def search(pred):
        idx = [i for i, c in enumerate(dk) if pred(c)]
        if idx:
            hand.append(dk.pop(rng.choice(idx)))
    for t in range(1, 6):
        draw(1)
        if 'Mesa' in hand and not mesa_in_play and policy != 'blank':
            hand.remove('Mesa'); mesa_in_play = True
        if mesa_in_play and rng.random() < 0.5 and len(hand) < 10:
            search(lambda c: c in POKE)
        def items():
            while 'Ball' in hand and policy != 'blank':
                hand.remove('Ball'); search(lambda c: c in BASICS)
            bench_basics(t)
        items()
        # evolutions before the Supporter only when legal now (keeps pieces out of a Copycat shuffle)
        def evolve():
            if t >= 2:
                names = [c for c, _ in board]
                for i, (c, tt) in enumerate(board):
                    if c == 'Paw' and tt < t and 'King' in hand and 'Candy' in hand and policy != 'blank_candy':
                        hand.remove('King'); hand.remove('Candy'); board[i] = ('King', t)
                for i, (c, tt) in enumerate(board):
                    if c == 'Glimmet' and tt < t and 'Glimmora' in hand:
                        hand.remove('Glimmora'); board[i] = ('Glimmora', t)
                for i, (c, tt) in enumerate(board):
                    if c == 'Grimer' and tt < t and 'Muk' in hand:
                        hand.remove('Muk'); board[i] = ('Muk', t)
        evolve()
        if policy != 'blank':
            king_needed = not any(c == 'King' for c, _ in board)
            pieces = any(c in hand for c in ('King', 'Candy', 'Paw', 'Glimmora', 'Muk'))
            opp = rng.choice(OPP_POOL)
            if 'Juliana' in hand and king_needed and 'King' not in hand:
                hand.remove('Juliana'); search(lambda c: c == 'King')
            elif policy == 'eager' and 'Copycat' in hand and not pieces and opp >= 3:
                hand.remove('Copycat'); dk.extend(hand); hand.clear(); rng.shuffle(dk); draw(opp)
            elif 'Research' in hand:
                hand.remove('Research'); draw(2)
            elif 'Copycat' in hand and policy in ('loose', 'eager'):
                hand.remove('Copycat'); dk.extend(hand); hand.clear(); rng.shuffle(dk); draw(opp)
            if mesa_in_play is False and 'Mesa' in hand:
                hand.remove('Mesa'); mesa_in_play = True
                if rng.random() < 0.5 and len(hand) < 10:
                    search(lambda c: c in POKE)
            items()
            evolve()
        names = [c for c, _ in board]
        for key, ok in (('King', 'King' in names), ('Paw', 'Paw' in names or 'King' in names),
                        ('Glimmora', 'Glimmora' in names), ('Muk', 'Muk' in names),
                        ('All3', 'King' in names and 'Glimmora' in names and 'Muk' in names),
                        ('MukGigas', 'Muk' in names and ('Gigas' in names or 'Gigas' in hand))):
            if ok and key not in first:
                first[key] = t
    res['first'] = first
    return res

LISTS = {
    'A': {},
    'B': {'Pop': -2, 'Candy': 1, 'Copycat': 1},
    'C': {'Pop': -2, 'Candy': 1, 'Copycat': 1, 'Ilima': -1, 'Red': 1},
    'Bplus': {'Pop': -2, 'Candy': 1, 'Copycat': 1, 'Ilima': -1, 'Juliana': 1},
    'Bjul': {'Pop': -2, 'Candy': 1, 'Juliana': 1},
    'Bsmall': {'Pop': -1, 'Candy': 1},
    'File': {'Pop': -1, 'Copycat': 1},
    'A_minus_Copycat_plus_Candy': {'Copycat': -1, 'Candy': 1},
    'C_alt_cut_Copycat': {'Pop': -2, 'Candy': 1, 'Red': 1},
}

def main():
    n = int(sys.argv[1]); policy = sys.argv[2]
    out = {}
    for name, ch in LISTS.items():
        cards = deck(ch)
        rng = random.Random(777000 + 1)
        cnt = collections.Counter(); pa = 0
        for _ in range(n):
            r = game(cards, rng, policy)
            pa += r['paw_active']
            for k, t in r['first'].items():
                for tt in range(t, 6):
                    cnt[(k, tt)] += 1
        row = {f'{k}_{t}': round(100 * cnt[(k, t)] / n, 1) for k in ('King', 'Paw', 'Glimmora', 'Muk', 'All3', 'MukGigas') for t in range(1, 6)}
        row['paw_active'] = round(100 * pa / n, 1)
        out[name] = row
        print(f"{name:28s} King t2-5 {row['King_2']}/{row['King_3']}/{row['King_4']}/{row['King_5']} | Paw t2 {row['Paw_2']} | Glimmora t3 {row['Glimmora_3']} | Muk t3 {row['Muk_3']} | All3 t4 {row['All3_4']} | Muk+Gigas t4 {row['MukGigas_4']} | PawActive {row['paw_active']}", flush=True)
    json.dump(out, open(f'/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/kingambit/check/indep_{policy}.json', 'w'), indent=1)

if __name__ == '__main__':
    main()
