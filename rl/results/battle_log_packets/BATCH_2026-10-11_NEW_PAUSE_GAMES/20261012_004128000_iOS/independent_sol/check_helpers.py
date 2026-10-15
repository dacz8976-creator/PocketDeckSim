import base64
import collections
import hashlib
import json
from pathlib import Path

P = Path(__file__).resolve().parent.parent
Q = json.loads((P / 'QR_DECODE.json').read_text(encoding='utf-8-sig'))
L = json.loads((P.parent / 'LIVE_DECK_SNAPSHOT.json').read_text(encoding='utf-8-sig'))
deck = next(d for d in L['decks'] if d['label'] == "Kingdra ex / Team Rocket's Weezing ex")
assert Q['payload'] == deck['code']
b = base64.b64decode(Q['payload'], validate=True)
i = 0
nt = b[i]; i += 1
trainers = []
for _ in range(nt):
    trainers.append(int.from_bytes(b[i:i+3], 'big') - 10000000); i += 3
npk = b[i]; i += 1
pokemon = []
for _ in range(npk):
    pokemon.append(int.from_bytes(b[i:i+3], 'big')); i += 3
ne = b[i]; i += 1
energy = list(b[i:i+ne]); i += ne
assert i == len(b) and nt + npk == 20 and energy == [3]
assert trainers == Q['decoded']['trainerIds'] and pokemon == Q['decoded']['pokemonIds']
normalize = lambda name: name.replace('\u2019', "'")
assert collections.Counter({normalize(c['name']): c['count'] for c in Q['cards']}) == collections.Counter({normalize(c['name']): c['quantity'] for c in deck['counts_by_name_and_variant']})
comparisons = []
for sec in [27, 121]:
    stem = f't{sec:07.2f}.jpg'
    old = hashlib.sha256((P/'turn_evidence'/stem).read_bytes()).hexdigest()
    fresh = hashlib.sha256((P/'independent_sol/source_check'/stem).read_bytes()).hexdigest()
    assert old == fresh
    comparisons.append({'source_seconds': sec, 'exact_jpeg_hash_match': True, 'sha256': fresh})
print(json.dumps({'payload_exact_live_match': True, 'independent_binary_decode': {'trainers':nt, 'pokemon':npk, 'energy':[3], 'complete_bytes_consumed':True}, 'semantic_counts_match_live': True, 'independent_native_seeks':comparisons, 'qr_image_reread_limit':'The selected runtime lacks cv2, so QR pixels were visually inspected but the independent check does not claim a fresh QR image decode.'}, indent=2))
