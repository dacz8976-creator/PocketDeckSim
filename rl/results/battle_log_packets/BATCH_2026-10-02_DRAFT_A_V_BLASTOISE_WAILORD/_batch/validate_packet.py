"""Check frozen packet integrity and the Pause Games capture contract.

These structural checks supplement independent source inspection; they never
establish that a visible card or outcome was read correctly.
"""
import argparse
import hashlib
import json
import traceback
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

BATCH = Path(__file__).resolve().parent
CORE = ['SOURCE.json', 'ASSIGNMENT.json', 'REVIEW.md', 'COVERAGE.md',
        'SUMMARY.json', 'UNCERTAINTIES.json', 'PAUSE_GAME.json', 'DECK_USED.json',
        'TURN_LEDGER.json', 'TURN_EVIDENCE.json', 'TURN_TABLE.md', 'METRICS.json']

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def local(packet, reference):
    path = Path(reference)
    if not path.is_absolute():
        path = packet / path
    path = path.resolve()
    assert path.is_relative_to(packet.resolve()) and path.is_file(), reference
    return path

def validate(packet, manifest_name='SUBMISSION.json'):
    packet = packet.resolve()
    assert packet.parent == BATCH and packet.is_dir()
    manifest_path = local(packet, manifest_name)
    submission = read(manifest_path)
    files = submission['files']
    assert isinstance(files, dict), 'Expected filename-to-SHA256 submission map'
    assert set(CORE).issubset(files), 'Core files missing from frozen submission'
    assert submission['complete_first_pass'] is True
    for name, expected in files.items():
        assert sha(local(packet, name)) == expected, 'Frozen file changed: ' + name
    source = read(packet/'SOURCE.json')
    assignment = read(packet/'ASSIGNMENT.json')
    assert submission['source_video'] == source['video_basename'] == assignment['video_basename']
    assert submission['source_sha256'] == source['sha256'] == assignment['source_sha256']
    assert assignment['ranked_ladder_eligible'] is False
    assert source['classification'] == 'computer_battle' and source['excluded_from_ladder'] is True
    game = read(packet/'PAUSE_GAME.json')
    deck = read(packet/'DECK_USED.json')
    ledger = read(packet/'TURN_LEDGER.json')
    evidence = read(packet/'TURN_EVIDENCE.json')
    for obj in [game, deck, ledger, evidence]:
        assert obj.get('is_template') is False, 'Unreplaced capture template'
    assert game['capture_status'] in ['complete', 'complete_with_recording_limits']
    opening = game['opening']
    assert opening['expected_card_slots'] == 5
    assert len(opening['cards_left_to_right']) == 5, 'Opening must retain five slots'
    assert opening['selected_active']['name'] or opening.get('limit_reason')
    shared_deck = read(BATCH/'OWNER_DECK_SNAPSHOT.json')
    assert shared_deck['actual_card_count'] == 20
    assert deck['actual_card_count'] == 20 and len(deck['cards_in_log_order']) == 20
    assert deck['cards_in_log_order'] == shared_deck['cards_in_log_order'], 'Per-game deck differs from frozen log snapshot'
    assert deck['counts_by_name_and_variant'] == shared_deck['counts_by_name_and_variant']
    assert deck['source_url'] == shared_deck['source_url']
    assert deck['capture_source_text_or_image'], 'Deck source capture reference required'
    rows = ledger['turns']
    assert rows and [r['turn_number'] for r in rows] == list(range(1, len(rows)+1))
    manifest = read(packet/'EXTRACTION_MANIFEST.json')
    # Independently captured evidence stays in separately frozen manifests.
    independent_manifests = sorted(packet.glob('independent_*/EXTRACTION_MANIFEST.json'))
    for independent_manifest in independent_manifests:
        manifest.extend(read(independent_manifest))
    by_id = {r['evidence_id']: r for r in manifest}
    assert len(by_id) == len(manifest), 'Duplicate native evidence IDs'
    for frame in evidence['frames']:
        assert frame['evidence_id'] in by_id, 'Capture refers to missing native evidence'
        native = by_id[frame['evidence_id']]
        assert frame['source_video'] == source['video_basename'] and frame['source_sha256'] == source['sha256']
        assert local(packet, frame['full_frame_path']) == local(packet, native['full_frame_path'])
    streams = [s for s in source['streams'] if 'width' in s and 'height' in s]
    assert len(streams) == 1
    dimensions = (streams[0]['width'], streams[0]['height'])
    for frame in manifest:
        assert frame['source_video'] == source['video_basename']
        assert frame['source_sha256'] == source['sha256']
        assert 0 <= frame['requested_source_seconds'] < source['duration_seconds']
        assert frame['actual_frame_seconds_if_measured'] is not None
        full = local(packet, frame['full_frame_path'])
        assert sha(full) == frame['full_frame_sha256']
        with Image.open(full) as image:
            assert image.size == dimensions
            for role in ['bottom_crop', 'top_crop']:
                crop = frame[role]
                bounds = crop['pixel_bounds_x0_y0_x1_y1']
                cp = local(packet, crop['path'])
                assert crop['parent_sha256'] == frame['full_frame_sha256']
                assert crop['lossless'] is True and sha(cp) == crop['sha256']
                if role == 'bottom_crop':
                    assert bounds == [0, int(image.height*.8), image.width, image.height]
                with Image.open(cp) as cropped:
                    assert cropped.size == (bounds[2]-bounds[0], bounds[3]-bounds[1])
                    assert image.crop(bounds).tobytes() == cropped.tobytes()
        local(packet, frame['decode_log'])
    required = ['who_played', 'source_video', 'timing', 'hand_at_start',
                'owner_hand_start', 'draws_and_searches', 'plays_in_order',
                'board_at_start', 'board_after', 'opponent_hand_at_owner_turn_start']
    for row in rows:
        assert all(key in row for key in required), 'Required turn field missing'
        assert row['source_video'] == source['video_basename']
        actor = row['who_played'].lower()
        assert actor.startswith('owner') or actor in ['opponent', 'computer opponent'], 'Ambiguous player label'
        assert [p['order'] for p in row['plays_in_order']] == list(range(1, len(row['plays_in_order'])+1))
        for boundary in ['board_at_start', 'board_after']:
            board = row[boundary]
            assert all(k in board for k in ['owner', 'opponent', 'stadium', 'turn_number_displayed'])
            for who in ['owner', 'opponent']:
                state = board[who]
                assert all(k in state for k in ['active', 'bench_in_position_order', 'energy_zone', 'points'])
                assert all(k in state['energy_zone'] for k in ['this_turn', 'next'])
                pokemon = ([state['active']] if state['active'] else []) + (state['bench_in_position_order'] or [])
                for mon in pokemon:
                    if mon.get('name') is None and mon.get('status') == 'observed_empty':
                        continue
                    if mon.get('empty') is True:
                        assert mon.get('name') is None and mon.get('basis') and mon.get('evidence_ids')
                        continue
                    assert all(k in mon for k in ['name', 'hp_now', 'hp_max', 'damage', 'attached_energy', 'tool', 'special_conditions', 'active_effects'])
                    hp, maximum, damage = mon['hp_now'], mon['hp_max'], mon['damage']
                    if hp is not None and maximum is not None:
                        assert 0 <= hp <= maximum
                        if damage is not None:
                            assert damage == maximum-hp, 'Inconsistent HP/damage'
                    energy = mon['attached_energy']
                    if energy['total'] is not None and energy['by_type'] is not None:
                        assert energy['total'] == sum(energy['by_type'].values())
    result = {
        'checked_utc': datetime.now(timezone.utc).isoformat(),
        'source_video': source['video_basename'], 'source_sha256': source['sha256'],
        'passed': True, 'submission_manifest': manifest_name,
        'submission_manifest_sha256': sha(manifest_path),
        'frozen_core_files': len(files), 'turn_rows': len(rows),
        'owner_turns': sum(r['who_played'].lower().startswith('owner') for r in rows),
        'native_frames_checked': len(manifest), 'lossless_native_crops_checked': len(manifest)*2,
        'movie_contents_read': False,
        'limits': 'Structural integrity is separate from independent semantic/source acceptance.'
    }
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('packet')
    parser.add_argument('--manifest', default='SUBMISSION.json')
    args = parser.parse_args()
    path = Path(args.packet)
    try:
        result = validate(path, args.manifest)
    except Exception as error:
        result = {'passed': False, 'error_type': type(error).__name__, 'error': str(error), 'traceback': traceback.format_exc(), 'movie_contents_read': False}
    (path/'ROOT_STRUCTURAL_CHECK.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result['passed'] else 1)
