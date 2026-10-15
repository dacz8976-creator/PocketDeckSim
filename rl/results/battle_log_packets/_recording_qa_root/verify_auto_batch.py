"""Check the final user-facing review packets and shared archive records."""
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parent.parent
batch = root / 'Recording_QA' / 'BATCH_2026-09-30'
def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

intake = read(batch / 'INTAKE.json')
baseline = read(batch / 'INDEX_BEFORE.json')
rows = list(csv.DictReader((root / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='')))
counts = Counter(r['Video'] for r in rows)
assert all(value == 1 for value in counts.values()), 'Duplicate index rows'
current = {r['Video']: r for r in rows}
for prior in baseline:
    assert current[prior['Video']] == prior, f"Unrelated index entry changed: {prior['Video']}"
events = [read(p) for p in (root / 'Review_Log' / 'events').glob('*.json')]
locations = read(root / 'MEDIA_LOCATIONS.json')
verified = []
for item in intake['sources']:
    name = item['video']
    packet = root / 'Recording_QA' / (Path(name).stem + '_auto_sol')
    source = read(packet / 'SOURCE.json')
    acceptance = read(packet / 'LEAD_ACCEPTANCE.json')
    receipt = read(packet / f'MOVE_RECEIPT.{name}.json')
    assert source['ladder_eligible'] is False and acceptance['ladder_eligible'] is False
    assert acceptance['accepted'] is True and acceptance['unreviewed_intervals'] == []
    assert source['sha256'] == item['sha256'] == receipt['sha256_before'] == receipt['sha256_after'] == acceptance['source_sha256']
    assert receipt['identity_match'] is True
    archived = root / 'Reviewed' / name
    assert archived.is_file() and archived.stat().st_size == source['bytes'] == item['bytes'] == receipt['bytes']
    assert not (root / name).exists(), f'Duplicate source remains: {name}'
    assert current[name]['Status'] == 'Reviewed' and current[name]['Location'] == 'Reviewed/' + name
    matching = [m for m in locations['moved'] if m['filename'] == name]
    assert len(matching) == 1 and matching[0]['sha256'] == source['sha256']
    assert Path(matching[0]['current_path']) == archived
    history = sorted((e for e in events if e.get('video_basename') == name), key=lambda e: e['logged_at_utc'])
    latest = history[-1]
    assert latest['status'] == 'full_battle_review_complete' and latest['video_sha256'] == source['sha256']
    archived_events = [e for e in history if e['event_id'] == receipt['review_event_id']]
    assert len(archived_events) == 1
    archived_event = archived_events[0]
    assert archived_event['status'] == 'full_battle_review_complete' and archived_event['video_sha256'] == source['sha256']
    preceding_id = archived_event['event_id']
    for follow_up in history[history.index(archived_event) + 1:]:
        assert follow_up['supersedes_event_id'] == preceding_id
        assert follow_up['status'] == 'full_battle_review_complete' and follow_up['video_sha256'] == source['sha256']
        preceding_id = follow_up['event_id']
    for filename in ['REVIEW.md', 'COVERAGE.md', 'SUMMARY.json', 'UNCERTAINTIES.json', 'LEAD_ACCEPTANCE.json']:
        assert (packet / filename).is_file()
    summary = read(packet / 'SUMMARY.json')
    uncertainty = read(packet / 'UNCERTAINTIES.json')
    assert summary.get('ladder_eligible') is False
    assert summary['current_status'] == 'full_battle_review_complete'
    assert summary['lead_acceptance'] == 'accepted' and summary['lead_acceptance_pending'] is False
    assert summary['source_archived'] is True and summary['global_registration_complete'] is True
    assert summary['archive_completion_event_id'] == receipt['review_event_id']
    assert summary.get('current_review_event_id', receipt['review_event_id']) == latest['event_id']
    for document in [summary, uncertainty]:
        for key in ['unreviewed_intervals', 'remaining_unreviewed_intervals', 'unreviewed_intervals_seconds', 'unreviewed_phases', 'uncovered_meaningful_phases']:
            assert not document.get(key), f'Incomplete coverage in {name}: {key}'
    verified.append({'video': name, 'sha256': source['sha256'], 'bytes': source['bytes'], 'reviewer': source['reviewer'], 'first_pass': acceptance['first_pass'], 'outcome': acceptance['outcome'], 'points': acceptance['final_points'], 'source_archived': True, 'ladder_eligible': False, 'archive_event_id': receipt['review_event_id'], 'current_review_event_id': latest['event_id']})
assert len(verified) == len(intake['sources']) and len(rows) == len(baseline) + len(verified)
assert locations['index_video_count'] == len(rows)
assert locations['awaiting_review_or_confirmation'] == sum(r['Status'] != 'Reviewed' for r in rows)
report = (root / 'BATTLE_TRANSCRIPTS_2026-09-30.md').read_text(encoding='utf-8-sig')
links = re.findall(r'\[[^\]\n]+\]\(([^)\n]+)\)', report)
for link in links:
    linked = (root / link).resolve()
    assert linked.is_relative_to(root.resolve()) and linked.is_file(), f'Broken or unsafe summary link: {link}'
assert len([link for link in links if link.endswith('/REVIEW.md')]) == len(verified)
assert f'{len(verified)} of {len(verified)} recordings' in report
results = read(batch / 'RESULTS.json')
assert results['total'] == results['completed'] == len(verified)
assert all(e['status'] == 'accepted_and_archived' and e['ladder_eligible'] is False for e in results['videos'])
corrections = batch / 'WORDING_CORRECTIONS_2026-09-30'
if (corrections / 'MANIFEST.json').is_file():
    manifest = read(corrections / 'MANIFEST.json')
    assert manifest['passed'] and manifest['packets_refreshed'] == len(verified)
    for entry in manifest['videos']:
        packet = root / 'Recording_QA' / (Path(entry['video']).stem + '_auto_sol')
        assert (packet / 'POST_ACCEPTANCE_CORRECTIONS.md').is_file()
        for changed in entry['modified_files']:
            assert hashlib.sha256((corrections / packet.name / changed['file']).read_bytes()).hexdigest() == changed['before_sha256']
            assert hashlib.sha256((packet / changed['file']).read_bytes()).hexdigest() == changed['after_sha256']
root_media = [p.name for p in root.iterdir() if p.is_file() and p.suffix.lower() in ['.mp4', '.mov', '.m4v', '.mkv', '.avi']]
assert all(name in current for name in root_media), 'New unindexed source arrivals require review'
result = {'passed': True, 'completed_today': len(verified), 'index_videos': len(rows), 'unchanged_prior_index_entries': len(baseline), 'remaining_prior_recording_limited_excerpts': sum(r['Status'] != 'Reviewed' for r in rows), 'ladder_entries_created': 0, 'archive_hash_check_basis': 'Each existing move receipt records SHA-256 freshly verified before and after its move; final reconciliation verifies bindings, receipts, file locations and sizes without redundant rehashing.', 'videos': verified}
result.update({'summary_links_verified': len(links), 'astra_checked_reports': sum(e.get('astra_consulted', False) for e in results['videos']), 'new_unindexed_arrivals': [], 'practice_results': {'wins': sum(e['outcome'] == 'owner_win' for e in results['videos']), 'losses': sum(e['outcome'] == 'owner_loss' for e in results['videos'])}})
(batch / 'VALIDATION.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(f"PASS: {len(verified)} complete packets and verified archive receipts; {len(baseline)} prior entries unchanged; {len(rows)} total index rows; no Ladder Log entries")
