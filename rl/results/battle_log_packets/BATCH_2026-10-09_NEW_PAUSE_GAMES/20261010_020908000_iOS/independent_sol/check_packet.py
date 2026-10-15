from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
from PIL import Image

P = Path(__file__).resolve().parent.parent
O = P / 'independent_sol'
def read(name):
    return json.loads((P / name).read_text(encoding='utf-8'))
def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

source = read('SOURCE.json')
media = Path(source['source_path_at_review'])
before = media.stat()
actual_sha = sha(media)
after = media.stat()
assert before.st_size == after.st_size == source['bytes']
assert before.st_mtime_ns == after.st_mtime_ns
assert actual_sha == source['sha256']

ledger = read('TURN_LEDGER.json')
backup = O / 'TURN_LEDGER.before_independent_timestamp_repair.json'
if not backup.exists():
    backup.write_bytes((P / 'TURN_LEDGER.json').read_bytes())
t4 = ledger['turns'][3]
stadium_draw = next(d for d in t4['draws_and_searches'] if d['kind'] == 'stadium_draw')
for card, time in zip(stadium_draw['cards_in_reveal_order'], [200, 201, 202]):
    card['timestamp_seconds'] = time
    card['evidence_ids'] = [f'F{time:07.2f}']
stadium_draw['timestamp_seconds'] = 200
stadium_draw['evidence_ids'] = ['F0200.00', 'F0201.00', 'F0202.00']
(P / 'TURN_LEDGER.json').write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

evidence = read('TURN_EVIDENCE.json')
for name in ['REVIEW.md', 'COVERAGE.md', 'TURN_EVIDENCE.json']:
    preserved = O / (name + '.before_independent_timestamp_repair')
    if not preserved.exists():
        preserved.write_bytes((P / name).read_bytes())
observations = {
    200: 'First Hiking Trail Stadium draw visibly reveals Poke Ball.',
    201: 'Second Hiking Trail Stadium draw visibly reveals Hiking Trail; Poke Ball is already in hand.',
    202: 'Third Hiking Trail Stadium draw visibly reveals Rare Candy; Poke Ball and Hiking Trail are already in hand.',
    204: 'All three Stadium draws have resolved into the owner hand; Poison damage checkup is now animating.'
}
for f in evidence['frames']:
    if f['requested_source_seconds'] in observations:
        f['observation'] = observations[f['requested_source_seconds']]
        f['suitability_or_limit'] = 'Independently inspected native source frame; requested seek time, not measured decoder PTS.'
(P / 'TURN_EVIDENCE.json').write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
review = (P / 'REVIEW.md').read_text(encoding='utf-8')
review = review.replace('Hiking Trail reveals Poke Ball, Hiking Trail, Rare Candy in order.', 'Hiking Trail reveals Poke Ball at200s, Hiking Trail at201s, Rare Candy at202s, in order (native seek frames independently checked).')
(P / 'REVIEW.md').write_text(review, encoding='utf-8')
coverage = (P / 'COVERAGE.md').read_text(encoding='utf-8')
coverage = coverage.replace('owner turn4, evolutions, Yes prompt, Water, end draw and checkups.', 'owner turn4, evolutions, Yes prompt, Water, end draws200/201/202s and checkups.')
(P / 'COVERAGE.md').write_text(coverage, encoding='utf-8')
frames = {f['evidence_id']: f for f in evidence['frames']}
assert len(ledger['turns']) == 7
assert [t['turn_number'] for t in ledger['turns']] == list(range(1, 8))
assert [t['who_played'] for t in ledger['turns']] == ['opponent','owner','opponent','owner','opponent','owner','opponent']
for turn in ledger['turns']:
    assert [a['order'] for a in turn['plays_in_order']] == list(range(1, len(turn['plays_in_order']) + 1))
    for phase in ['board_at_start', 'board_after']:
        board = turn[phase]
        for who in ['owner', 'opponent']:
            side = board[who]
            assert all(k in side for k in ['active', 'bench_in_position_order', 'energy_zone', 'points'])
            assert 'this_turn' in side['energy_zone'] and 'next' in side['energy_zone']
            for pokemon in [side['active']] + side['bench_in_position_order']:
                if pokemon is None:
                    continue
                assert all(k in pokemon for k in ['hp_now', 'hp_max', 'damage', 'attached_energy', 'tool', 'special_conditions', 'active_effects'])
                if isinstance(pokemon['hp_now'], (int, float)) and isinstance(pokemon['hp_max'], (int, float)):
                    assert pokemon['hp_max'] - pokemon['hp_now'] == pokemon['damage']
                energy = pokemon['attached_energy']
                if isinstance(energy['total'], int):
                    assert sum(energy['by_type'].values()) == energy['total']
    if turn['who_played'] == 'owner':
        assert turn['owner_hand_end']['count'] in [1, 3]
        assert turn['hand_reconciliation']

def check_ids(obj):
    if isinstance(obj, dict):
        for key, val in obj.items():
            if key.endswith('evidence_ids') and isinstance(val, list):
                for eid in val:
                    if isinstance(eid, str) and eid.startswith('F'):
                        assert eid in frames, eid
            check_ids(val)
    elif isinstance(obj, list):
        for val in obj:
            check_ids(val)
check_ids(ledger)
check_ids(read('PAUSE_GAME.json'))
for f in evidence['frames']:
    assert f['source_sha256'] == actual_sha
    assert f['source_video'] == source['video_basename']
    assert Image.open(P / f['full_frame_path']).size == (1170, 2532)
    for kind in ['bottom_crop', 'top_crop']:
        crop = f[kind]
        x0,y0,x1,y1 = crop['pixel_bounds_x0_y0_x1_y1']
        assert Image.open(P / crop['path']).size == (x1-x0,y1-y0)
deck = read('DECK_USED.json')
assert len(deck['cards_in_log_order']) == 20
assert sum(c['count'] for c in deck['counts_by_name_and_variant']) == 20
assert deck['energy_configuration'] == 'Water only'
assert deck['exact_list_status'] == 'verified_live_list_and_filmed_qr_game_binding'
qr = read('qr_intake/QR_DECODE_0001.00.json')
live_snapshot = json.loads((P.parent / 'LIVE_NEW_DECKS_VERIFIED.json').read_text(encoding='utf-8'))
live_deck = next(d for d in live_snapshot['decks'] if d['id'] == deck['deck_id'])
assert live_deck['code'] == qr['payload']
assert { (c['name'], c['variant']): c['count'] for c in deck['counts_by_name_and_variant'] } == { (name, variant): int(count) for count, name, variant in live_deck['rows'] }
assert qr['card_slot_count'] == 20 and qr['source_sha256'] == actual_sha

viewed_names = '''t0027.00_bottom.jpg t0029.00.jpg t0073.40_bottom.jpg t0074.40_bottom.jpg t0075.00.jpg t0174.80.jpg t0255.00.jpg t0080.00.jpg t0084.00.jpg t0094.00.jpg t0178.00.jpg t0187.00.jpg t0196.00.jpg t0200.00.jpg t0202.00.jpg t0204.00.jpg t0201.00.jpg t0216.00.jpg t0218.00.jpg t0225.00.jpg t0232.00.jpg t0243.00.jpg t0245.00.jpg t0258.00.jpg t0264.00.jpg t0270.00.jpg t0257.60.jpg t0274.00.jpg t0282.00.jpg t0300.00.jpg t0302.00.jpg t0306.00.jpg t0309.50.jpg t0315.00.jpg t0378.00.jpg t0382.00.jpg t0388.80.jpg t0076.40_bottom.jpg t0079.40_bottom.jpg t0176.80_bottom.jpg t0179.80_bottom.jpg t0255.60_bottom.jpg t0260.60_bottom.jpg t0220.00.jpg t0222.00.jpg t0228.00.jpg t0242.50.jpg t0257.20.jpg t0276.00.jpg t0278.00.jpg t0304.00.jpg t0318.00.jpg t0002.00.jpg t0003.00.jpg t0073.40_top.jpg t0174.80_top.jpg t0255.00_top.jpg'''.split()
manifest = {'reviewer': '/root/check_020908', 'scope': 'Fresh bounded independent native evidence checks, not a second full-battle review', 'source_sha256': actual_sha, 'actual_viewed': [{'path': 'turn_evidence/' + n, 'sha256': sha(P / 'turn_evidence' / n), 'dimensions': list(Image.open(P / 'turn_evidence' / n).size)} for n in viewed_names]}
(O / 'VIEWED_MANIFEST.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')
core = ['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
hashes = {name: sha(P / name) for name in core}
result = {
    'reviewer': '/root/check_020908', 'model': 'gpt-6.1-sol', 'checked_at_utc': datetime.now(timezone.utc).isoformat(),
    'accepted': True, 'status': 'accepted_with_recording_limits', 'source_sha256': actual_sha,
    'source_bytes': after.st_size, 'source_identity_independently_verified': True,
    'source_json_sha256': sha(P / 'SOURCE.json'), 'blockers': [], 'accepted_input_sha256': hashes,
    'checked_input_sha256': hashes, 'core_file_count': len(core), 'actual_viewed_manifest': 'VIEWED_MANIFEST.json',
    'actual_viewed_image_count': len(viewed_names), 'narrative': 'CHECK_REVIEW.md',
    'repair': {'scope': 'T4 per-card Stadium reveal timestamps and evidence references only', 'previous_ledger': 'TURN_LEDGER.before_independent_timestamp_repair.json', 'corrected_reveals': [{'name': c['name'], 'seconds': c['timestamp_seconds']} for c in stadium_draw['cards_in_reveal_order']]},
    'limits': ['No opened discard piles; hidden opponent hand identities remain unknown.', 'Draw-end seek times are approximate, decoder PTS was not independently measured.', 'Semantic deck variants do not establish exact artwork/rarity.', 'Timeout notice establishes terminal result, not disconnect intention.'],
    'shared_or_external_writes': False, 'source_moved': False
}
(O / 'CHECK_RESULT.json').write_text(json.dumps(result, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')
print(json.dumps({'accepted': True, 'source_sha256': actual_sha, 'core_files': len(core), 'viewed_images': len(viewed_names), 'frame_triplets_structurally_verified': len(frames)}, ensure_ascii=True))
