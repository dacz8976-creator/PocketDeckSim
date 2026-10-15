import collections
import datetime
import hashlib
import json
import sys
from pathlib import Path
from PIL import Image

out = Path(__file__).resolve().parent
p = out.parent
load = lambda f: json.loads(f.read_text(encoding='utf-8-sig'))
digest = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
freeze = load(p / 'REVIEW_PACKET_HASHES.json')
source = load(p / 'SOURCE.json')
hashes_before = {name: digest(p / name) for name in freeze['files']}
issues = []
for name, actual in hashes_before.items():
    if actual != freeze['files'][name]:
        issues.append(f'Frozen hash mismatch: {name}')
source_path = Path(source['source_path_at_review'])
stat_before = source_path.stat()
source_hash = digest(source_path)
stat_after = source_path.stat()
if source_hash != source['sha256'] or (stat_before.st_size, stat_before.st_mtime_ns) != (stat_after.st_size, stat_after.st_mtime_ns):
    issues.append('Source hash or source stability mismatch')
docs = {name: load(p / name) for name in freeze['files'] if name.endswith('.json')}
ledger = docs['TURN_LEDGER.json']
evidence = docs['TURN_EVIDENCE.json']
frames = {f['evidence_id']: f for f in evidence['frames']}
for frame in frames.values():
    if frame['source_sha256'] != source_hash or frame['source_video'] != source['video_basename']:
        issues.append(f"Wrong source binding: {frame['evidence_id']}")
    if not 0 <= frame['requested_source_seconds'] <= source['duration_seconds']:
        issues.append(f"Timestamp outside source: {frame['evidence_id']}")
    with Image.open(p / frame['full_frame_path']) as im:
        size = im.size
    if list(size) != frame['native_dimensions'] or size != (1170, 2532):
        issues.append(f"Native dimensions mismatch: {frame['evidence_id']}")
    for key in ('bottom_crop', 'top_crop'):
        crop = frame[key]
        x0, y0, x1, y1 = crop['pixel_bounds_x0_y0_x1_y1']
        with Image.open(p / crop['path']) as im:
            if im.size != (x1-x0, y1-y0):
                issues.append(f"Crop dimensions mismatch: {frame['evidence_id']} {key}")
    if frame['bottom_crop']['pixel_bounds_x0_y0_x1_y1'] != [0, 2025, 1170, 2532]:
        issues.append(f"Bottom fifth mismatch: {frame['evidence_id']}")

def inspect(value, location):
    if isinstance(value, dict):
        for key, item in value.items():
            if key in ('evidence_ids', 'turn_evidence_ids') and item:
                for eid in item:
                    if eid not in frames:
                        issues.append(f'Missing evidence ID {eid} in {location}')
            if key in ('timestamp_seconds', 'requested_source_seconds') and isinstance(item, (float, int)):
                if not 0 <= item <= source['duration_seconds']:
                    issues.append(f'Timestamp outside source in {location}')
            inspect(item, location + '/' + key)
    elif isinstance(value, list):
        for i, item in enumerate(value):
            inspect(item, location + '/' + str(i))
for name, doc in docs.items():
    inspect(doc, name)

assert [t['turn_number'] for t in ledger['turns']] == list(range(1, 11))
for turn in ledger['turns']:
    assert turn['source_sha256'] == source_hash
    assert [a['order'] for a in turn['plays_in_order']] == list(range(1, len(turn['plays_in_order'])+1))
    for phase in ('board_at_start', 'board_after'):
        for side in ('owner', 'opponent'):
            board = turn[phase][side]
            assert board['energy_zone']['next']['count'] is None
            assert board['energy_zone']['next']['available'] is None
            for pokemon in [board['active']] + board['bench_in_position_order']:
                if pokemon:
                    assert pokemon['hp_max'] - pokemon['hp_now'] == pokemon['damage']
                    assert sum(pokemon['attached_energy']['by_type'].values()) == pokemon['attached_energy']['total']

qr = load(p / 'QR_DECODE.json')
runtime = p.parents[1] / 'BATCH_2026-10-12_ADDITIONAL_TWO/20261012_225319000_iOS/qr_runtime'
sys.path.insert(0, str(runtime))
import zxingcpp
with Image.open(p / 'turn_evidence/t0000.00.jpg') as im:
    payload = zxingcpp.read_barcodes(im)[0].text
assert payload == qr['payload'] == docs['DECK_USED.json']['filmed_qr']
catalog = load(p.parent / 'HISTORICAL_DECK_CATALOG.json')
matching = [d for d in catalog['decks'] if d['code'] == payload]
assert len(matching) == 1
assert collections.Counter(x['name'] for x in qr['slots']) == collections.Counter(x['name'] for x in docs['DECK_USED.json']['cards_in_log_order'])
assert len(docs['DECK_USED.json']['cards_in_log_order']) == sum(x['count'] for x in docs['DECK_USED.json']['counts_by_name_and_variant']) == 20
assert docs['DECK_USED.json']['fresh_live_verified'] is False
hashes_after = {name: digest(p / name) for name in freeze['files']}
if hashes_after != hashes_before:
    issues.append('Input files changed during independent check')

observed = [0, 30, 52, 59, 60, 68, 132, 141, 143, 144, 169, 185, 186, 193, 204, 207, 210, 219, 221, 223, 227, 246, 288, 297, 302, 309, 313, 316, 326]
result = {
    'reviewer': '/root/check_remaining_014423',
    'model': 'gpt-6.1-sol',
    'reasoning_effort': 'high',
    'checked_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'source_video': source['video_basename'],
    'source_sha256': source_hash,
    'source_hash_rechecked': True,
    'source_bytes': stat_after.st_size,
    'checked_input_sha256': hashes_after,
    'all_eight_frozen_files_stable': hashes_before == hashes_after == freeze['files'],
    'semantic_files_read': list(freeze['files']),
    'accepted': not issues,
    'required_repairs': issues,
    'review_scope': 'Independent bounded source acceptance of all eight frozen packet files. Retained source-native frames reused, not a second full visual pass.',
    'retained_native_seconds_visually_checked': observed,
    'checked_evidence_sha256': {f'N{x:07.2f}': digest(p / f'turn_evidence/t{x:07.2f}.jpg') for x in observed},
    'bounded_source_findings': [
        'Opening five at 30s are Poke Ball, Professors Research, Alolan Grimer, Copycat, Glimmora; selected Grimer is marked. Going first is visible.',
        'Poke Ball finds Pawniard at 52s. Research arrivals at 59 and 60s are Lucky Ice Pop then Regigigas. Final T1 hand at 68s contains four cards and matches arithmetic.',
        'Ordinary T3 retains five cards from 132 to 143s; Pawniard gains one Darkness, and 144s displays the unused-Supporter warning recorded in numbered End Turn nested details.',
        'T5 pre-play hand at 169s includes Heavy Helmet. Copycat reveals Glimmora then Glimmet at 185/186s, and 193s shows one ending card, Glimmora, with Glimmet benched and one Darkness.',
        'Generator coin at 204s is heads. At 207s benched Dedenne gains its first Lightning while Emolga has none; 210s then shows Emolga with one Lightning. Regigigas is 150 before attack and 50 at T7 with Heavy Helmet.',
        'Ordinary T7 begins with two Glimmora at 219s. First move lifts the held full-art card at 221s and evolves Glimmet by 223s, preserving one Darkness. At 227s Pawniard has two Darkness and ending hand is one ordinary-art Glimmora.',
        'T8 completed attachment at 246s shows benched Dedenne with two Lightning. T10 288s shows Emolga with two Lightning and active Dedenne at 80 HP, poisoned, with two Lightning. Retreat moves Dedenne to Bench1 and Emolga Active; the resulting board ledger retains one Lightning on former Active Dedenne.',
        'Emolga hits for 90 at 302s. Shattering Crystal tails at 309s, third point at 313s, Defeat at 316s and final326s results establish loss 0-3 after 10 turns, went first, damage30, versus RedGarados.',
        'Both-board semantic reconciliation covers all10 rows: HP, maximum HP, damage, tools, typed Energy, conditions, points and Stadium. Next-Energy numeric values remain unknown; type-only claims are retained.',
        'Native QR independently decoded and matches the unique deck code in the historical27-deck catalog and frozen exact20 semantic list with Darkness. Fresh live deck verification remains explicitly false.'
    ],
    'evidence_integrity': {'native_frame_records': len(frames), 'dimensions_and_crop_paths_checked': True, 'reference_ids_and_source_time_bounds_checked': True},
    'structural_validation_separate': {'path': '../STRUCTURAL_VALIDATION.json', 'structural_pass': load(p/'STRUCTURAL_VALIDATION.json')['structural_pass'], 'basis': 'Separately generated primary validator; does not establish visual semantics.'},
    'limits': [
        'This check is bounded and does not claim an independent whole-video pass. Whole-source coverage remains primary reviewer responsibility; coverage and all10 ledger rows were semantically read.',
        'Neither opened discard pile is available according to the full primary account; hidden opponent identities stay unknown.',
        'Exact decoded frame PTS and touch onset are not measured. Retained frames identify requested nearby source-local moments with qualified transition timing.',
        'Historical deck list and filmed QR are accepted with saved provenance. Current live-log access and external game write/readback are pending lead work.'
    ]
}
(out / 'CHECK_RESULT.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'accepted': result['accepted'], 'issues': issues, 'stable_eight': result['all_eight_frozen_files_stable'], 'frames': len(frames), 'qr_unique_historical_match': matching[0]['name']}))
