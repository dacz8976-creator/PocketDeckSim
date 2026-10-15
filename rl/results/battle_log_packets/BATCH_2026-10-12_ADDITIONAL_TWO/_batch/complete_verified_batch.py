"""Reconcile the two accepted sources and mirror their written evidence."""
import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

BATCH = Path(__file__).resolve().parent
ROOT = BATCH.parent.parent
BOSS = Path('C:/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder').resolve()
NAMES = ['20261012_225319000_iOS', '20261012_230258000_iOS']

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

assert not (BATCH / 'BATCH_COMPLETION_CHECK.json').exists(), 'Inspect the existing receipt before repeating finalization.'
now = datetime.now(timezone.utc).isoformat()
before = {r['Video']: r for r in read(BATCH / 'INDEX_BEFORE.json')}
with (ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='') as handle:
    current = {r['Video']: r for r in csv.DictReader(handle)}
selected = {n + '.MP4' for n in NAMES}
assert all(current.get(n) == row for n, row in before.items() if n not in selected)
assert not (set(current) - set(before) - selected)
locations = read(ROOT / 'MEDIA_LOCATIONS.json')['moved']
storage = read(BATCH / 'FINAL_STORAGE_CHECK.json')
assert {e['video'] for e in storage['entries']} == selected
assert all(e['after']['in_sync'] and e['after']['online_only'] and e['after']['allocated_bytes'] == 0 for e in storage['entries'])
live = read(BATCH / 'LIVE_SAVE_VERIFICATION_230258.json')
assert live['reloaded'] and live['prior_44_games_unchanged'] and live['all_decks_unchanged']
assert live['total_games'] == 45 and live['deck_count'] == 26
assert live['wins'] == 25 and live['losses'] == 20 and live['concession_wins'] == 15
all_storage = read(BATCH / 'ALL_SIX_STORAGE_CHECK.json')
assert len(all_storage['entries']) == 6
assert all(e['after']['in_sync'] and e['after']['online_only'] and e['after']['allocated_bytes'] == 0 for e in all_storage['entries'])
earlier = read(ROOT / 'Recording_QA/BATCH_2026-10-12_NEW_LONG_VIDEOS/BATCH_COMPLETION_CHECK.json')
assert earlier['external_saved'] and earlier['all_requested_local_reviews_complete']
accepted = []
writes = []
for name in NAMES:
    packet = BATCH / name
    source = read(packet / 'SOURCE.json')
    summary = read(packet / 'SUMMARY.json')
    game = read(packet / 'PAUSE_GAME.json')
    lead = read(packet / 'LEAD_ACCEPTANCE.json')
    move = read(packet / ('MOVE_RECEIPT.' + name + '.MP4.json'))
    ledger = read(packet / 'TURN_LEDGER.json')['turns']
    assert lead['accepted'] and lead['all_source_games_accepted'] and lead['source_game_count'] == 1
    assert lead['source_sha256'] == source['sha256']
    assert move['identity_match'] and move['sha256_before'] == move['sha256_after'] == source['sha256']
    registration = read(packet / 'REGISTRATION_RESULT.json')
    assert registration['exit_code'] == 0
    event_path = Path(registration['stdout'].strip())
    assert event_path.resolve().parent == (ROOT / 'Review_Log/events').resolve()
    assert move['review_event_id'] in event_path.name
    event = read(event_path)
    assert event['status'] == 'full_battle_review_complete'
    assert event['video_basename'] == source['video_basename'] and event['video_sha256'] == source['sha256']
    assert current[name + '.MP4']['Status'] == 'Reviewed'
    assert current[name + '.MP4']['Location'].replace('\\', '/') == 'Reviewed/' + name + '.MP4'
    assert (ROOT / 'Reviewed' / (name + '.MP4')).stat().st_size == source['bytes']
    assert not (ROOT / (name + '.MP4')).exists()
    matches = [e for e in locations if e['filename'] == name + '.MP4']
    assert len(matches) == 1 and matches[0]['sha256'] == source['sha256']
    assert len(ledger) == summary['turn_count'] == lead['turn_rows']
    assert [row['turn_number'] for row in ledger] == list(range(1, len(ledger) + 1))
    for filename, expected in lead['accepted_input_sha256'].items():
        bound = 'PAUSE_GAME.before_lead_acceptance.json' if filename == 'PAUSE_GAME.json' else filename
        assert digest(packet / bound) == expected, (name, filename)
    assert game['lead_checked'] and game['capture_status'] in ['complete', 'complete_with_recording_limits']
    rows = [r for r in live['all_game_texts'] if name + '.MP4' in r]
    assert len(rows) == 1 and 'Loss' in rows[0]
    status = {'verified_utc': now, 'source': source['video_basename'], 'source_sha256': source['sha256'],
              'game_id': game['game_id'], 'external_saved': True, 'fresh_reload_verified': True,
              'artifact_url': live['artifact_url'], 'saved_row': rows[0],
              'verification_receipt': '../LIVE_SAVE_VERIFICATION_230258.json',
              'ratings': 'Not supplied by owner; left blank.'}
    writes.append((packet / 'EXTERNAL_SAVE_STATUS.json', status))
    snapshot = read(BATCH / 'LIVE_DECK_SNAPSHOT.json')
    assert snapshot['slot_count'] == 20
    matching_deck = [d for d in live['all_decks'] if d['name'] == snapshot['deck_label']]
    assert len(matching_deck) == 1 and matching_deck[0]['code'] == snapshot['qr_payload']
    snapshot.update(retrieved_utc=live['verified_utc'], game_id=game['game_id'],
                    source_video=source['video_basename'], source_sha256=source['sha256'],
                    live_readback_receipt='../LIVE_SAVE_VERIFICATION_230258.json',
                    supplement='Append-only live saved-list readback; accepted DECK_USED.json is preserved.')
    assert not (packet / 'DECK_LOG_SNAPSHOT.json').exists()
    writes.append((packet / 'DECK_LOG_SNAPSHOT.json', snapshot))
    accepted.append({'source': source['video_basename'], 'sha256': source['sha256'],
                     'game_id': game['game_id'], 'opponent': summary['opponent'],
                     'owner_result': 'loss', 'turns': len(ledger), 'complete': True,
                     'registration_event': move['review_event_id'], 'archive_hash_verified': True,
                     'external_saved': True, 'storage_online_only': True,
                     'packet': str(packet)})
assert sum(r['turns'] for r in accepted) == 23
for path, value in writes:
    save(path, value)
completion = {'checked_utc': now, 'all_requested_reviews_complete': True, 'sources': accepted,
              'counts': {'sources': 2, 'games': 2, 'wins': 0, 'losses': 2, 'turns': 23},
              'all_source_games_covered': True, 'unrelated_index_rows_unchanged': True,
              'external_saved': True, 'fresh_live_counts': {'games': 45, 'wins': 25, 'losses': 20, 'concession_wins': 15, 'decks': 26},
              'storage_online_only_count': 2, 'storage_allocated_bytes': 0,
              'storage_receipt': 'FINAL_STORAGE_CHECK.json',
              'source_contents_not_read_for_final_reconciliation': True,
              'accepted_packet_semantics_unchanged': True}
save(BATCH / 'BATCH_COMPLETION_CHECK.json', completion)
save(BATCH / 'ALL_SIX_COMPLETION.json', {'checked_utc': now, 'all_six_complete': True,
     'sources': 6, 'games': 6, 'wins': 3, 'losses': 3, 'opponent_concessions': 2, 'turns': 91,
     'earlier_four_receipt': '../BATCH_2026-10-12_NEW_LONG_VIDEOS/BATCH_COMPLETION_CHECK.json',
     'additional_two_receipt': 'BATCH_COMPLETION_CHECK.json', 'external_saved': True,
     'storage_online_only': 6, 'storage_allocated_bytes': 0, 'storage_receipt': 'ALL_SIX_STORAGE_CHECK.json',
     'fresh_live_counts': completion['fresh_live_counts']})
shutil.copy2(BATCH / 'README.md', BATCH / 'README.md.before_batch_completion')
table = ['| Recording | Opponent | Result | Turns |', '|---|---|---|---:|']
for entry in accepted:
    stem = Path(entry['source']).stem
    table.append(f"| [{entry['source']}]({stem}/REVIEW.md) | {entry['opponent']} | Loss | {entry['turns']} |")
(BATCH / 'README.md').write_text('# Two further October 12 recordings\n\nBoth recordings are fully reviewed, separately independently accepted, lead accepted, registered and archived with matching pre/post move hashes. Both losses are saved in Pause Games and verified after reload.\n\n' + '\n'.join(table) + '\n\nJob is an owner-concession loss at 0-2. Giorno is a 2-3 points loss after Starmie ex knocks out Alolan Muk; the earlier empty-deck notice did not end the battle.\n\nThe current Pause Games total is 45 games, 25 wins, 20 losses, 15 wins by opponent concession and 26 decks. All previous game entries and all 26 deck lists are preserved. Each filmed QR establishes the same exact 20-card Darkness list. Native opening, draw, hand and board evidence and one row per turn are retained. Hidden cards, unopened discard contents, exact frame PTS, artwork and rarity remain explicit limits.\n\nTogether with the earlier four-source batch, all six requested videos are complete: 3 wins, 3 losses, two opponent concessions and 91 recorded turns. No older paused backlog was reopened.\n\nAll six archived originals are verified in sync and online only with zero allocated bytes. No video was deleted. Written reviews and retained evidence are mirrored into Pocket Deck Lab/Boss Folder/BATCH_2026-10-12_ADDITIONAL_TWO. See BATCH_COMPLETION_CHECK.json, ALL_SIX_COMPLETION.json, FINAL_STORAGE_CHECK.json, LIVE_SAVE_VERIFICATION_230258.json and MIRROR_RECEIPT.json for completion evidence.\n', encoding='utf-8')
shutil.copy2(BATCH / 'REVIEW_ROLES.json', BATCH / 'REVIEW_ROLES.json.before_batch_completion')
roles = read(BATCH / 'REVIEW_ROLES.json')
roles['updated_utc'] = now
for entry in roles['sources']:
    entry['current_status'] = 'accepted_registered_archived_live_verified_and_online_only'
save(BATCH / 'REVIEW_ROLES.json', roles)
destination = BOSS / BATCH.name
assert destination.parent == BOSS
if destination.exists():
    staging_path = BATCH / 'MIRROR_STAGING_RECEIPT.json'
    assert staging_path.exists() and digest(staging_path) == digest(destination / staging_path.name)
    staging = read(staging_path)
    assert Path(staging['destination']).resolve() == destination.resolve() and staging['all_copy_hashes_match']
    for entry in staging['files']:
        assert digest(destination / entry['path']) == entry['sha256'], 'A staged mirror was changed outside this finalization.'
files = [p for p in BATCH.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
assert not any(p.suffix.lower() in ['.mp4', '.mov', '.m4v', '.mkv', '.avi'] for p in files)
shutil.copytree(BATCH, destination, dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__'))
copies = []
for path in sorted(files):
    relative = path.relative_to(BATCH)
    expected = digest(path)
    assert digest(destination / relative) == expected
    copies.append({'path': relative.as_posix(), 'bytes': path.stat().st_size, 'sha256': expected})
receipt = {'copied_utc': datetime.now(timezone.utc).isoformat(), 'source': str(BATCH),
           'destination': str(destination), 'file_count': len(copies),
           'all_copy_hashes_match': True, 'videos_copied': 0, 'files': copies}
save(BATCH / 'MIRROR_RECEIPT.json', receipt)
shutil.copy2(BATCH / 'MIRROR_RECEIPT.json', destination / 'MIRROR_RECEIPT.json')
assert digest(BATCH / 'MIRROR_RECEIPT.json') == digest(destination / 'MIRROR_RECEIPT.json')
print(json.dumps({'all_six_complete': True, 'live_games': 45, 'mirror_files': len(copies), 'all_copy_hashes_match': True}))
