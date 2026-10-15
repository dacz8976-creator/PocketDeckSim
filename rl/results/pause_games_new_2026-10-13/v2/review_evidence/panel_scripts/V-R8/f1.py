import json, re, sys
sys.path.insert(0, "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/harness")
Q = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/"
P = Q + "BATCH_2026-10-13_NEWEST_TWO/20261013_022530000_iOS/"
led = json.load(open(P + "TURN_LEDGER.json", encoding="utf-8"))
s = json.dumps(led, ensure_ascii=False)
for m in re.finditer(r'.{0,200}(Dratini|Slam|Beat).{0,200}', s):
    t = m.group(0)
    if 'Dratini' in t or 'Slam' in t or 'Beat ' in t:
        print('...', t)
        print()
import deckspec, cardlib as C
dk = json.load(open(P + "DECK_USED.json", encoding="utf-8"))
qr, log = deckspec.find_lists(dk)
print('qr lists', [p for p, _ in qr], 'log lists', [p for p, _ in log])
sp = deckspec.read_deck(dk, {})
for e in sp.entries:
    print('  ', e)
print('functions Dratini', C.functions('Dratini'))
for i in ['A1 183', 'A3b 051', 'B2b 051', 'B4 116']:
    print(i, C.BYID.get(i))
