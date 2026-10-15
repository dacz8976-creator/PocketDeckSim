"""Reconcile final source-bound reviews and save the owner's October 1 summary."""
import csv
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from batch_rules_20261001 import ROOT, BATCH, VIDEOS, read, save
from complete_rules_packet import validate
from free_reviewed_video_space import metadata

def main():
    rows = list(csv.DictReader((ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='')))
    by_name = {row['Video']: row for row in rows}
    assert len(by_name) == len(rows), 'Duplicate index source'
    baseline = read(BATCH / 'INDEX_BEFORE.json')
    for old in baseline:
        assert by_name[old['Video']] == old, f"Previous row changed: {old['Video']}"
    assert len(rows) == len(baseline) + len(VIDEOS)
    events = [read(path) for path in (ROOT / 'Review_Log' / 'events').glob('*.json')]
    locations = {item['filename']: item for item in read(ROOT / 'MEDIA_LOCATIONS.json')['moved']}
    records = []
    storage = []
    for name in VIDEOS:
        packet, source, lead, status = validate(name)
        receipt = read(packet / f'MOVE_RECEIPT.{name}.json')
        summary = read(packet / 'SUMMARY.json')
        latest = sorted((event for event in events if event.get('video_basename') == name), key=lambda event: event['logged_at_utc'])[-1]
        assert latest['status'] == status and latest['event_id'] == receipt['review_event_id']
        assert latest['video_sha256'] == receipt['sha256_before'] == receipt['sha256_after'] == source['sha256'] == locations[name]['sha256']
        assert receipt['identity_match'] and receipt['review_status'] == status
        assert by_name[name]['Status'] == 'Reviewed' and by_name[name]['Location'] == f'Reviewed/{name}'
        assert summary['current_status'] == status and summary['lead_acceptance'] == 'accepted' and summary['source_archived'] is True
        archived = ROOT / 'Reviewed' / name
        assert not (ROOT / name).exists() and archived.is_file() and archived.stat().st_size == source['bytes']
        assert summary['ladder_eligible'] is False
        storage.append({'video': name, **metadata(archived)})
        records.append({'video': name, 'sha256': source['sha256'], 'bytes': source['bytes'], 'duration_seconds': source['duration_seconds'], 'completion_status': status, 'scope': lead['scope'], 'outcome_description': lead['outcome_description'], 'key_findings': lead['key_findings'], 'limitations': lead['limitations'], 'review_path': f'Recording_QA/{packet.name}/REVIEW.md', 'event_id': latest['event_id']})
    assert len({record['sha256'] for record in records}) == len(VIDEOS)
    # Discover no additional unindexed recordings silently left outside the current request.
    unexpected = [path.name for path in ROOT.glob('*.MP4') if path.name not in by_name]
    assert not unexpected, f'New unindexed uploads appeared: {unexpected}'
    now = datetime.now(timezone.utc).isoformat()
    storage_result = {'checked_at_utc': now, 'verification': 'Metadata only; no archived original contents read', 'videos': len(VIDEOS), 'online_only': sum(item['online_only'] for item in storage), 'still_local': sum(not item['online_only'] for item in storage), 'allocated_bytes': sum(item['allocated_bytes'] for item in storage), 'files_deleted': 0, 'entries': storage}
    save(BATCH / 'STORAGE_STATUS.json', storage_result)
    result = {'checked_at_utc': now, 'batch_complete': True, 'completed_recordings': len(records), 'unchanged_previous_index_rows': len(baseline), 'packet_references_valid': True, 'source_hashes_unique': len(records), 'archive_identity_verified_by_matching_pre_post_move_receipts': True, 'ladder_entries_created': 0, 'records': records}
    save(BATCH / 'RESULTS.json', result)
    report = ['# October 1 rules-test video reviews', '', f'All {len(VIDEOS)} newly uploaded recordings have been fully reviewed by fresh Sol workers, independently checked and accepted by the lead, registered, and archived unchanged. The owner identified these as rules tests. No Ladder Log entry was created.', '', 'Each review separates visible findings from inference, hidden information and interactions the footage did not test. Intentional setup choices are interpreted as test choices.', '', '| Recording | Reviewed scope and ending | Full review |', '|---|---|---|']
    report[6:6] = ['Astra checked the Will and damage-order conclusions, the unclear second Misty target, and the lethal Destructive Inferno sequence. See the [bounded Astra check](Recording_QA/BATCH_2026-10-01_RULES/ASTRA_CHECK.md). Will\'s guarantee was not reapplied to the observed Victory Star replacement and did not force the separate Confusion check. Bounded Field\'s Mega exception concerns the attacker. The second Misty target remains unknown, with zero Energy confirmed. Destructive Inferno coins continued after lethal damage, but the observed removal of all two Energy cannot distinguish the attack effect from knockout cleanup. Dragon-type Gabite\'s attack did not provide a matching-weakness test.', '']
    for record in records:
        scope = record['scope'].replace('|', '/')
        ending = record['outcome_description'].replace('|', '/')
        report.append(f"| `{record['video']}` | {scope}. {ending} | [Review]({record['review_path']}) |")
    report += ['', '## Supported observations', '']
    for record in records:
        report += [f"### {record['video']}", '']
        report += [f'- {finding}' for finding in record['key_findings']]
        report += ['', 'Limits: ' + ' '.join(record['limitations']), '']
    report += ['## Verification and storage', '', f"All {len(VIDEOS)} source bindings match the registered completion events, archive locations and before/after SHA-256 move receipts. All {len(baseline)} previous index rows remain unchanged. File names and video contents are preserved. The written reviews and retained evidence are kept locally.", '', f"OneDrive metadata checked at {now}: {storage_result['online_only']} of {len(VIDEOS)} archived originals are online-only. {storage_result['still_local']} retain local data ({storage_result['allocated_bytes'] / 1_000_000_000:.2f} GB) while OneDrive sync or space release remains pending. No video was deleted.", '', 'Source filenames use October 1; their exact clock and timezone basis was not established.', '']
    report_path = ROOT / 'BATTLE_RULE_TESTS_2026-10-01.md'
    prose = '\n'.join(report)
    for cramped, spaced in [('Charged1H', 'Charged 1H'), ('another1H', 'another 1H'), ('for80', 'for 80'), ('for40', 'for 40'), (';14 turns', '; 14 turns'), (';120 displayed', '; 120 displayed')]:
        prose = prose.replace(cramped, spaced)
    assert '\u2014' not in prose
    report_path.write_text(prose, encoding='utf-8')
    for record in records:
        assert (ROOT / record['review_path']).is_file()
    assert (BATCH / 'ASTRA_CHECK.md').is_file()
    readme = ROOT / 'READ_ME_REVIEW_STATUS.md'
    text = readme.read_text(encoding='utf-8-sig')
    start = 'Updated after the October 1 rules-test batch.'
    paragraph = start + f" All {len(VIDEOS)} new recordings are reviewed by fresh Sol workers, independently checked and lead-accepted, registered and archived with matching source hashes. These are owner-requested rules tests and are excluded from Ladder Log. See the [October 1 findings and full reviews](BATTLE_RULE_TESTS_2026-10-01.md). {storage_result['online_only']} of {len(VIDEOS)} originals are online-only; {storage_result['still_local']} still retain local data while OneDrive sync or space release is pending. Originals are preserved."
    if start in text:
        text = re.sub(re.escape(start) + r'[^\n]*', lambda match: paragraph, text, count=1)
    else:
        title, rest = text.split('\n', 1)
        text = title + '\n\n' + paragraph + '\n' + rest
    latest_by_name = {}
    for event in sorted(events, key=lambda event: (event.get('logged_at_utc', event.get('timestamp_utc', '')), event.get('event_id', ''))):
        # Legacy pause events used timestamp_utc/video; preserve them unchanged.
        basename = event.get('video_basename', event.get('video'))
        assert isinstance(basename, str) and basename, 'Review event has no source filename'
        latest_by_name[basename] = event
    complete_full = sum(event['status'] == 'full_battle_review_complete' for event in latest_by_name.values())
    complete_rule = sum(event['status'] == 'rule_test_review_complete' for event in latest_by_name.values())
    old_counts = r'The \[review index\]\(BATTLE_REVIEW_INDEX.csv\) contains \d+ videos: \d+ accepted full-battle reviews and (?:eight|\d+) completed rule tests in `Reviewed`, plus seven recording-limited excerpts in the main folder\.'
    current_counts = f'The [review index](BATTLE_REVIEW_INDEX.csv) contains {len(rows)} videos: {complete_full} accepted full-battle reviews and {complete_rule} completed rule tests in `Reviewed`, plus seven recording-limited excerpts in the main folder.'
    text, replaced = re.subn(old_counts, current_counts, text, count=1)
    assert replaced == 1, 'Current index count paragraph not found'
    readme.write_text(text, encoding='utf-8')
    validation = {key: value for key, value in result.items() if key != 'records'}
    validation.update({'summary_links_valid': True, 'index_rows': len(rows), 'full_battle_reviews': complete_full, 'rule_test_reviews': complete_rule, 'online_only': storage_result['online_only'], 'storage_pending': storage_result['still_local']})
    save(BATCH / 'FINAL_CHECKS.json', validation)
    print(json.dumps(validation), flush=True)

if __name__ == '__main__':
    main()
