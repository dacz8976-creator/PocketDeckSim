"""Prepare one source-bound new deck, preserving its initial live absence."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

BATCH = Path(__file__).resolve().parent
NAMES = ['20261013_022530000_iOS', '20261013_030351000_iOS']
def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))
decoded = read(BATCH / NAMES[1] / 'QR_DECODE.json')
payload = decoded['payload']
qr_paths = {NAMES[0]: 'independent_sol/QR_CHECK.json', NAMES[1]: 'QR_DECODE.json'}
other = read(BATCH / NAMES[0] / qr_paths[NAMES[0]])
assert other['payload'] == payload
assert decoded['decoded']['roundtrip'] is True and decoded['card_slot_count'] == 20
baseline = read(BATCH / 'LIVE_BASELINE.json')
assert not any(d['code'] == payload for d in baseline['all_decks'])
cards = []
for card in sorted(decoded['cards'], key=lambda c: 0 if c['entity_kind'] == 'pokemon' else 1):
    assert card['resolution'] == 'resolved_semantic_entity'
    cards.append({'n': card['count'], 'name': card['name'],
                  'kind': 'Pokémon' if card['entity_kind'] == 'pokemon' else 'Trainer',
                  'id': card['printing_aliases'][0]})
assert sum(c['n'] for c in cards) == 20
sources = []
for name in NAMES:
    source = read(BATCH / name / 'SOURCE.json')
    qr = read(BATCH / name / qr_paths[name])
    assert qr['source_sha256'] == source['sha256']
    sources.append({'video': source['video_basename'], 'sha256': source['sha256'],
                    'qr_receipt': name + '/' + qr_paths[name],
                    'payload_identical': qr['payload'] == payload})
result = {'prepared_utc': datetime.now(timezone.utc).isoformat(),
          'destination': baseline['artifact_url'], 'external_saved': False,
          'initial_live_catalog_count': baseline['deck_count'],
          'initial_live_status': 'Identical payload absent from every expanded live deck.',
          'deck': {'id': 'filmed-qr-' + hashlib.sha256(payload.encode('ascii')).hexdigest()[:12],
                   'name': 'Haxorus / Dragonair / Druddigon', 'energy': 'Fighting + Metal',
                   'tag': 'Filmed QR', 'deck_code': payload, 'cards': cards,
                   'sources': sources, 'semantic_versions_only': True,
                   'printing_note': 'References identify representative playable versions. Exact filmed artwork and rarity remain unverified.',
                   'game_binding_status': 'Both native QR payloads match; full-source acceptance remains pending.'}}
target = BATCH / 'PREPARED_FILMED_DECK.json'
assert not target.exists()
target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'deck_id': result['deck']['id'], 'slots': 20, 'energy': result['deck']['energy'], 'sources': 2, 'external_saved': False}))
