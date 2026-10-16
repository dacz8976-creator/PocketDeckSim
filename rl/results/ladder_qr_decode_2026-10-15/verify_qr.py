"""Check the four QR_DECODE.json receipts (as committed in rl/results/battle_log_packets/) against the Kingambit deck list, with the deck journal's own functions.

  python3 rl/results/ladder_qr_decode_2026-10-15/verify_qr.py        (from the repository root)
"""
import collections, json, os, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'rl', 'deck_journal'))
sys.path.insert(0, os.path.join(REPO, 'lib'))
os.chdir(REPO)
import journal  # noqa: E402

PACKETS = 'rl/results/battle_log_packets/'
GAMES = {
    '201201': 'BATCH_2026-10-15_LADDER_TWO/20261015_201201000_iOS',
    '201850': 'BATCH_2026-10-15_LADDER_TWO/20261015_201850000_iOS',
    '205332': 'BATCH_2026-10-15_LATE_LADDER_TWO/20261015_205332000_iOS',
    '210617': 'BATCH_2026-10-15_LATE_LADDER_TWO/20261015_210617000_iOS',
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
print('the four payload strings are identical:', len(set(payloads.values())) == 1)
