#!/usr/bin/env python3
"""check_deck_assumption.py POSITIONS.json DECKS_DIR QA: for each game whose DECK_USED.json holds no list (the list was built from its QR and snapshot), compare the list with every card of his the ledger shows:
a card named in his hand or on his board that the list does not hold, or more copies at once (hand + board) than the list holds. Run on a verified game too, as the control.
Prints one line per game; exit 0 always (it is a report, not a test)."""
import collections, glob, json, os, re, sys

pos_f, decks_dir, qa = sys.argv[1:4]
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'pause_games_new_2026-10-12', 'harness'))
import cardlib as C  # noqa: E402

BATCHES = ('BATCH_2026-10-12_NEW_LONG_VIDEOS', 'BATCH_2026-10-12_ADDITIONAL_TWO', 'BATCH_2026-10-13_NEWEST_TWO', 'BATCH_2026-10-13_REMAINING_SIX')
games = {}
for b in BATCHES:
    for d in glob.glob(os.path.join(qa, b, '2026*')):
        games[os.path.basename(d).replace('_iOS', '')[2:]] = d
def has_list(d):
    j = json.load(open(os.path.join(d, 'DECK_USED.json'), encoding='utf-8'))
    return any(isinstance(v, list) and len(v) == 20 for v in j.values())


assumed = {g for g, d in games.items() if not has_list(d)}      # the packets with no 20-card list in DECK_USED.json: normalize_ledger.py built one from the QR and the live log snapshot
POS = json.load(open(pos_f, encoding='utf-8'))
for g in sorted(games):
    deck = collections.Counter()
    for line in open(os.path.join(decks_dir, f'KW{g}.txt'), encoding='utf-8'):
        m = re.match(r'(\d+) (.+) ([A-Za-z0-9\-]+ \d{3})\s*$', line)
        if m:
            deck[C.nname(m.group(2))] += int(m.group(1))
    seen_names, over = set(), {}
    for p in (x for x in POS if x['game'] == 'kw-' + g):
        now = collections.Counter()
        for h in p['me']['hand']:
            now[h.rsplit(' ', 2)[0]] += 1
        for b in p['me']['board']:
            now[b['card'].rsplit(' ', 2)[0]] += 1
            for x in b.get('behind', []) + b.get('tools', []):
                now[x.rsplit(' ', 2)[0]] += 1
        seen_names |= set(now)
    # the converter takes its cards from the list it was given, so a card the list lacks never reaches a position: look at the ledger's own names instead
    led = json.load(open(os.path.join(games[g], 'TURN_LEDGER.json'), encoding='utf-8'))
    ledger_names, max_at_once = set(), collections.Counter()
    for t in led['turns']:
        if not str(t.get('who_played', '')).startswith('owner'):
            continue
        hand = collections.Counter()
        for c in (t.get('hand_at_start') or {}).get('cards_left_to_right') or []:
            n = C.nname(c.get('name') if isinstance(c, dict) else c)
            hand[n] += 1
            ledger_names.add(n)
        for p in t.get('plays_in_order') or []:
            n = C.nname(p.get('card_name'))
            if n and C.BYNAME.get(n):
                ledger_names.add(n)
        for n, k in hand.items():
            max_at_once[n] = max(max_at_once[n], k)
    missing = sorted(n for n in ledger_names if n not in deck and C.BYNAME.get(n) and not any(n.startswith(x) for x in ()))
    # cards the list lacks that the ledger shows him holding or playing (his own cards; the opponent's plays are in other rows)
    too_many = sorted(f'{n} x{k} in hand, list holds {deck[n]}' for n, k in max_at_once.items() if deck and k > deck.get(n, 0))
    tag = 'FROM-QR ' if g in assumed else 'listed  '
    print(f'{tag} {g}: list {sum(deck.values())} cards | his hands/plays name {len(ledger_names)} cards; not in the list: {missing or "none"}; more at once than the list holds: {too_many or "none"}')
