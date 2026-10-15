"""Root reconciliation. Does not read archived video contents or write externally."""
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

BATCH = Path(__file__).resolve().parent
ROOT = BATCH.parent.parent
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p, d): p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
selected = read(BATCH / 'OWNER_CONTEXT.json')['selected_sources']
before = {r['Video']: r for r in read(BATCH / 'INDEX_BEFORE.json')}
with (ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='') as f:
    current = {r['Video']: r for r in csv.DictReader(f)}
assert all(current.get(n) == r for n, r in before.items() if n not in selected)
assert not (set(current) - set(before) - set(selected))
locations = read(ROOT / 'MEDIA_LOCATIONS.json')['moved']
storage_path = BATCH / 'FINAL_STORAGE_CHECK.json'
if not storage_path.exists(): storage_path = BATCH / 'STORAGE_PENDING.json'
storage = read(storage_path)
assert {e['video'] for e in storage['entries']} == set(selected)
storage_by_name = {e['video']:e['after'] for e in storage['entries']}
if storage['complete']:
    assert all(e['after']['in_sync'] and e['after']['online_only'] and e['after']['allocated_bytes'] == 0 for e in storage['entries'])
prepared = read(BATCH / 'PAUSE_GAMES_BATCH_IMPORT.json')
assert prepared['external_saved'] is False and prepared['sent_to_claude'] is False
assert {g['source_video'] for g in prepared['game_documents']} == set(selected)
now = datetime.now(timezone.utc).isoformat()
accepted = []
for name in selected:
    packet = BATCH / Path(name).stem
    source = read(packet / 'SOURCE.json')
    summary = read(packet / 'SUMMARY.json')
    game = read(packet / 'PAUSE_GAME.json')
    lead = read(packet / 'LEAD_ACCEPTANCE.json')
    move = read(packet / ('MOVE_RECEIPT.' + name + '.json'))
    assert lead['accepted'] and lead['all_source_games_accepted'] and lead['source_game_count'] == 1
    assert lead['source_sha256'] == source['sha256'] == move['sha256_before'] == move['sha256_after'] and move['identity_match']
    reg = read(packet / 'REGISTRATION_RESULT.json')
    assert reg['exit_code'] == 0
    event_path = Path(reg['stdout'].strip()).resolve()
    assert event_path.parent == (ROOT / 'Review_Log/events').resolve() and move['review_event_id'] in event_path.name
    event = read(event_path)
    assert event['status'] == 'full_battle_review_complete' and event['video_basename'] == name and event['video_sha256'] == source['sha256']
    assert current[name]['Status'] == 'Reviewed' and current[name]['Location'].replace('\\', '/') == 'Reviewed/' + name
    assert not (ROOT / name).exists() and (ROOT / 'Reviewed' / name).stat().st_size == source['bytes']
    mapped = [e for e in locations if e['filename'] == name]
    assert len(mapped) == 1 and mapped[0]['sha256'] == source['sha256']
    turns = read(packet / 'TURN_LEDGER.json')['turns']
    count = summary.get('turn_count', summary.get('turns_played'))
    assert len(turns) == count == lead['turn_rows']
    assert [r['turn_number'] for r in turns] == list(range(1, count + 1))
    for filename, expected in lead['accepted_input_sha256'].items():
        bound = 'PAUSE_GAME.before_lead_acceptance.json' if filename == 'PAUSE_GAME.json' else filename
        assert sha(packet / bound) == expected, (name, filename)
    old_game = read(packet / 'PAUSE_GAME.before_lead_acceptance.json')
    for key in set(game) | set(old_game):
        if key not in ['lead_checked', 'battle_review_status', 'lead_acceptance']:
            assert game.get(key) == old_game.get(key)
    assert summary['classification'] in ['human', 'human_battle', 'human_event_battle'] and summary['auto_option_visible'] is False
    outcome = summary.get('result', summary.get('outcome'))
    assert outcome in ['win', 'loss']
    status = {'checked_utc': now, 'source_video': name, 'source_sha256': source['sha256'], 'game_id': game['game_id'], 'external_saved': False, 'fresh_reload_verified': False, 'artifact_url': prepared['existing_artifact'], 'blocker_receipt': '../EXTERNAL_ACCESS_BLOCK.json', 'prepared_import': '../PAUSE_GAMES_BATCH_IMPORT.json', 'status': 'Accepted local review; external save and fresh deck/game readback pending browser policy stop.'}
    save(packet / 'EXTERNAL_SAVE_STATUS.json', status)
    doc = next(g for g in prepared['game_documents'] if g['source_video'] == name)
    accepted.append({'source': name, 'sha256': source['sha256'], 'game_id': game['game_id'], 'opponent': summary['opponent'], 'result': outcome, 'result_method': doc['result_method'], 'turns': count, 'registration_event': move['review_event_id'], 'archive_hash_verified': True, 'external_saved': False, 'storage_online_only': storage_by_name[name]['online_only'], 'storage_in_sync': storage_by_name[name]['in_sync'], 'storage_allocated_bytes': storage_by_name[name]['allocated_bytes'], 'packet': str(packet)})
counts = {'sources': len(selected), 'games': len(accepted), 'wins': sum(e['result'] == 'win' for e in accepted), 'losses': sum(e['result'] == 'loss' for e in accepted), 'opponent_concessions': sum(e['result_method'] == 'opponent_concession' for e in accepted), 'turns': sum(e['turns'] for e in accepted)}
completion = {'checked_utc': now, 'all_requested_local_reviews_complete': True, 'entire_requested_work_complete': False, 'sources': accepted, 'counts': counts, 'all_source_games_covered': True, 'unrelated_index_rows_unchanged': True, 'external_saved': False, 'fresh_live_counts': None, 'external_blocker': 'Computer Use stopped because Chrome current URL could not be verified for policy enforcement.', 'external_import_prepared': True, 'storage_complete': storage['complete'], 'storage_online_only_count': storage['online_only'], 'storage_allocated_bytes': storage['allocated_bytes_after'], 'storage_receipt': storage_path.name, 'storage_pending_reason': None if storage['complete'] else 'OneDrive has not confirmed sync; originals retained locally rather than releasing unsynced contents.', 'source_contents_not_read_for_final_reconciliation': True, 'accepted_packet_semantics_unchanged': True}
assert not (BATCH / 'BATCH_COMPLETION_CHECK.json').exists()
save(BATCH / 'BATCH_COMPLETION_CHECK.json', completion)
roles = read(BATCH / 'REVIEW_ROLES.json')
roles['updated_utc'] = now
for r in roles['sources']: r['status'] = 'accepted_registered_archived_external_pending' + ('_online_only' if storage_by_name[r['source']]['online_only'] else '_storage_sync_pending')
save(BATCH / 'REVIEW_ROLES.json', roles)
storage_sentence = 'All six originals are in sync, online only and use zero local allocated video bytes.' if storage['complete'] else f"OneDrive has not confirmed sync for every archived original. {storage['online_only']} of six are online only; remaining local video allocation is {storage['allocated_bytes_after']:,} bytes. The originals stay local until sync is verified, as required by the storage preference."
lines = ['# Six remaining October 13 recordings', '', 'All six supplied recordings have full-source reviews, separate independent acceptance, root source checks and completion registration. Original hashes match before and after archival into Reviewed. ' + storage_sentence, '', '| Recording | Opponent | Result | Turns |', '|---|---|---|---:|']
for e in accepted:
    stem = Path(e['source']).stem
    label = {'opponent_concession':'Win, opponent conceded','opponent_return_timeout':'Win, opponent failed to return','owner_concession':'Loss, owner conceded','points':e['result'].capitalize() + ' on points'}[e['result_method']]
    lines.append(f"| [{e['source']}]({stem}/REVIEW.md) | {e['opponent']} | {label} | {e['turns']} |")
lines += ['', 'Source metadata establishes October 12 Chicago evening; original October 13 UTC filenames are preserved. Each packet contains five-card opening evidence, draw and hand captures, numbered plays, both boards and one structured row per recorded turn. Hidden cards, unopened discards, unsupported future Energy counts and printing remain explicit recording limits.', '', 'A bounded Astra check directly identified Protective Poncho in the GaboDobleT recording and confirmed that its attachment preceded the Fighting Energy. Its Bench condition and corrected turn order are included in the independently accepted report.', '', 'Pause Games entries are prepared in PAUSE_GAMES_BATCH_IMPORT.json and CLAUDE_IMPORT_REQUEST.txt. They have not been saved or verified live: Computer Use stopped because it could not verify the current Chrome URL for policy enforcement. Historical exact deck snapshots retain their actual retrieval date and are not represented as fresh readbacks.', '', 'The completed newest pair and older backlog are excluded. See BATCH_COMPLETION_CHECK.json, ' + storage_path.name + ' and the per-source acceptance and move receipts. Written reviews and retained evidence are intended for the required Pocket Deck Lab/Boss Folder mirror; MIRROR_RECEIPT.json confirms its completion separately.']
(BATCH / 'README.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(json.dumps({'local_reviews_complete': True, 'external_saved': False, 'counts': counts}))
