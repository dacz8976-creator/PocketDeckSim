"""Check the six QR_DECODE.json receipts (as committed in rl/results/battle_log_packets/) against the Kingambit deck list, with the deck journal's own functions.

  python3 rl/results/ladder_qr_decode_2026-10-16/verify_qr.py        (from the repository root)
"""
import collections, json, os, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'rl', 'deck_journal'))
sys.path.insert(0, os.path.join(REPO, 'lib'))
os.chdir(REPO)
import journal  # noqa: E402

PACKETS = 'rl/results/battle_log_packets/'
GAMES = {
    '015753': 'BATCH_2026-10-15_NIGHT_LADDER_FOUR/20261016_015753000_iOS',
    '020517': 'BATCH_2026-10-15_NIGHT_LADDER_FOUR/20261016_020517000_iOS',
    '020806': 'BATCH_2026-10-15_NIGHT_LADDER_FOUR/20261016_020806000_iOS',
    '024253': 'BATCH_2026-10-15_NIGHT_LADDER_FOUR/20261016_024253000_iOS',
    '030833': 'BATCH_2026-10-15_FINAL_LADDER_TWO/20261016_030833000_iOS',
    '031512': 'BATCH_2026-10-15_FINAL_LADDER_TWO/20261016_031512000_iOS',
}
text = open('decks/dustin/01-kingambit-as-played.txt', encoding='utf-8').read()
energy, pairs = journal.parse_list(text)
want = journal.code_cards(energy, pairs)
print('deck file decks/dustin/01-kingambit-as-played.txt: list id', journal.list_id(journal.lines_of(text)), '| cards', len(want['cards']), '| energy codes', want['energy'])
payloads = {}
for g, pk in GAMES.items():
    d = PACKETS + pk
    rec = json.load(open(os.path.join(d, 'QR_DECODE.json'), encoding='utf-8'))
    payloads[g] = journal.packet_payload(d)
    got = journal.decode_payload(payloads[g])
    print(g, '| schema', rec['schema'], '| source sha', rec['source_sha256'][:12], '| second', rec['source_seconds'], '| image', rec['retained_image'].split('\\')[-2] + '/' + rec['retained_image'].split('\\')[-1],
          '| read by', rec['read_method'], '| same cards and Energy as the deck file:', got == want, '| all entities resolved:', rec['all_entities_resolved'], '| encoder round trip:', rec['decoded'].get('roundtrip'))
    if got != want:
        a, b = collections.Counter(got['cards']), collections.Counter(want['cards'])
        print('   only in the code:', dict(a - b), '| only in the deck file:', dict(b - a), '| energy', got['energy'], want['energy'])
print('the six payload strings are identical:', len(set(payloads.values())) == 1)
