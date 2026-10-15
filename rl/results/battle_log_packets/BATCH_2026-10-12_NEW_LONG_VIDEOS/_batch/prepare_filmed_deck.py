"""Prepare the exact source-bound list; no external write or game acceptance."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

BATCH = Path(__file__).resolve().parent
names = ['20261012_010706000_iOS', '20261012_203719000_iOS', '20261012_210041000_iOS', '20261012_210823000_iOS']
qs = [json.loads((BATCH / n / 'QR_DECODE.json').read_text(encoding='utf-8')) for n in names]
assert len({q['payload'] for q in qs}) == 1
for name, q in zip(names, qs):
    source = json.loads((BATCH / name / 'SOURCE.json').read_text(encoding='utf-8'))
    assert q['source_sha256'] == source['sha256']
    assert q['card_slot_count'] == 20 and q['decoded']['roundtrip'] is True
    assert hashlib.sha256(Path(q['retained_image']).read_bytes()).hexdigest() == q['retained_image_sha256']
    assert q['all_entities_resolved'] is True
cards = sorted(qs[0]['cards'], key=lambda c: c['entity_kind'] != 'pokemon')
definition = {
    'id': 'filmed-qr-' + qs[0]['payload_ascii_sha256'][:12],
    'name': 'Glimmora / Alolan Muk / Kingambit / Regigigas',
    'energy': 'Darkness',
    'tag': 'FILMED QR',
    'deck_code': qs[0]['payload'],
    'cards': [{'n': c['count'], 'name': c['name'], 'kind': 'Pokémon' if c['entity_kind'] == 'pokemon' else 'Trainer', 'id': c['printing_aliases'][0]} for c in cards],
    'cards_in_log_order': [{'name': c['name'], 'variant': c['printing_aliases'][0]} for c in cards for _ in range(c['count'])],
    'counts_by_name_and_variant': [{'name': c['name'], 'variant': c['printing_aliases'][0], 'count': c['count']} for c in cards],
    'provenance': 'All four source-native QR codes at 0 seconds decode to the same exact 20 semantic card slots and Darkness Energy. Reference labels do not identify filmed artwork or rarity.',
    'sources': [{'video': q['source_video'], 'source_sha256': q['source_sha256'], 'source_seconds': q['source_seconds'], 'image_sha256': q['retained_image_sha256']} for q in qs],
    'game_binding_status': 'awaiting full review and independent acceptance',
    'external_saved': False,
}
assert len(definition['cards_in_log_order']) == sum(c['count'] for c in definition['counts_by_name_and_variant']) == 20
record = {'prepared_utc': datetime.now(timezone.utc).isoformat(), 'destination': 'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd', 'deck': definition,
          'live_list_status': 'Absent from the rendered current deck choices and Decks view. No Add Deck control is exposed in the artifact UI.',
          'live_snapshot_status': 'No verified live snapshot for this new list yet. Preserve this limit separately from the exact filmed QR list.'}
(BATCH / 'PREPARED_FILMED_DECK.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'name': definition['name'], 'semantic_card_slots': 20, 'source_qr_payloads_match': True, 'source_count': len(qs), 'external_saved': False}))
