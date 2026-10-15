"""Verify the one-battle, two-source rules review and refresh its entry point."""
import csv
import re
import shutil
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from intake_carefree_snipes_20261002 import ROOT, BATCH, VIDEOS, read, save
from complete_rules_packet import validate
from free_reviewed_video_space import metadata


def storage_for(names):
    entries = [{'video': name, **metadata(ROOT / 'Reviewed' / name)} for name in names]
    return {
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'videos': len(names),
        'online_only': sum(e['online_only'] for e in entries),
        'allocated_bytes': sum(e['allocated_bytes'] for e in entries),
        'entries': entries,
        'files_deleted': 0,
        'originals_modified': False,
        'verification': 'Metadata only; archived originals were not reopened or rehashed',
    }


def storage_sentence(storage, number_word):
    if storage['online_only'] == storage['videos']:
        return f'All {number_word} originals are confirmed online-only. Review packets and evidence remain pinned locally.'
    return f"{storage['online_only']} of {storage['videos']} originals are confirmed online-only; {storage['allocated_bytes']/1e9:.2f} GB remains locally allocated while OneDrive sync or space release is pending. Review packets and evidence remain pinned locally."


def main():
    rows = list(csv.DictReader((ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='')))
    by_name = {row['Video']: row for row in rows}
    assert len(by_name) == len(rows)
    baseline = read(BATCH / 'INDEX_BEFORE.json')
    assert all(by_name[row['Video']] == row for row in baseline), 'Unrelated baseline row changed'
    assert set(by_name) - {row['Video'] for row in baseline} == set(VIDEOS)
    events = [read(path) for path in (ROOT / 'Review_Log' / 'events').glob('*.json')]
    for event in events:
        event.setdefault('video_basename', event.get('video'))
        event.setdefault('logged_at_utc', event.get('timestamp_utc'))
    locations = read(ROOT / 'MEDIA_LOCATIONS.json')['moved']
    results = []
    for name in VIDEOS:
        packet, source, lead, completion_status = validate(name)
        assignment = read(packet / 'ASSIGNMENT.json')
        summary = read(packet / 'SUMMARY.json')
        receipt = read(packet / f'MOVE_RECEIPT.{name}.json')
        current = ROOT / 'Reviewed' / name
        assert completion_status == 'rule_test_review_complete'
        assert source['sha256'] == assignment['sha256'] == receipt['sha256_before'] == receipt['sha256_after']
        assert receipt['identity_match'] and source['bytes'] == receipt['bytes'] == current.stat().st_size
        assert current.is_file() and not (ROOT / name).exists()
        assert not source['pause_games_eligible'] and not summary['pause_games_eligible']
        assert not lead['ladder_eligible'] and not lead['pause_games_eligible']
        latest = max((event for event in events if event['video_basename'] == name), key=lambda event: event['logged_at_utc'])
        assert latest['status'] == completion_status and latest['video_sha256'] == source['sha256']
        assert latest['event_id'] == receipt['review_event_id']
        assert by_name[name]['Status'] == 'Reviewed' and by_name[name]['Location'].replace('\\', '/') == 'Reviewed/' + name
        location = [entry for entry in locations if entry['filename'] == name]
        assert len(location) == 1 and Path(location[0]['current_path']).resolve() == current.resolve()
        assert location[0]['sha256'] == source['sha256']
        assert summary['source_archived'] and summary['global_registration_complete']
        for filename in ['REVIEW.md', 'COVERAGE.md', 'SUMMARY.json', 'UNCERTAINTIES.json']:
            assert (packet / 'worker_submission' / filename).is_file()
        assert not list(packet.rglob('*.MP4')) and not (packet / 'EXTERNAL_LOG_RECEIPT.json').exists()
        results.append({
            'video': name, 'source_sha256': source['sha256'], 'source_bytes': source['bytes'],
            'duration_seconds': source['duration_seconds'], 'review_status': completion_status,
            'review': str((packet / 'REVIEW.md').relative_to(ROOT)).replace('\\', '/'),
            'coverage': str((packet / 'COVERAGE.md').relative_to(ROOT)).replace('\\', '/'),
            'accepted': True, 'registered': True, 'archived_hash_verified': True,
            'pause_games_eligible': False, 'ladder_eligible': False,
        })
    assert (BATCH / 'TEST_REVIEW.md').is_file() and (BATCH / 'ASTRA_CAREFREE_CHECK.md').is_file()
    raw_combined = BATCH / 'worker_submission' / 'TEST_REVIEW.md'
    raw_combined.parent.mkdir(exist_ok=True)
    if not raw_combined.exists():
        shutil.copyfile(BATCH / 'TEST_REVIEW.md', raw_combined)
    combined_text = (BATCH / 'TEST_REVIEW.md').read_text(encoding='utf-8-sig')
    combined_text = combined_text.replace('Proposed completion: `rule_test_review_complete`.', 'Registered completion: `rule_test_review_complete`.')
    stamp = '**Current status: both source reviews independently accepted, registered as rule_test_review_complete and archived unchanged. One computer test battle; no Pause Games or Ladder Log entry.**'
    if stamp not in combined_text:
        title, rest = combined_text.split('\n', 1)
        combined_text = title + '\n\n' + stamp + '\n' + rest
    (BATCH / 'TEST_REVIEW.md').write_text(combined_text, encoding='utf-8')
    for name in VIDEOS:
        packet = ROOT / 'Recording_QA' / (Path(name).stem + '_rule_sol')
        path = packet / 'REVIEW.md'
        prose = path.read_text(encoding='utf-8-sig')
        prose = prose.replace('Proposed completion: `rule_test_review_complete`.', 'Registered completion: `rule_test_review_complete`.')
        prose = prose.replace('No shared battle records, source files or simulator files were changed.', 'The worker changed no shared battle records, source files or simulator files. The coordinator subsequently registered and archived the accepted reviews.')
        path.write_text(prose, encoding='utf-8')
    statuses = Counter(row['Status'] for row in rows)
    rule_names = {event['video_basename'] for event in events if event['status'] == 'rule_test_review_complete'}
    archive_names = {path.name for path in (ROOT / 'Reviewed').iterdir() if path.is_file() and path.suffix.lower() == '.mp4'}
    assert archive_names == {row['Video'] for row in rows if row['Status'] == 'Reviewed'}
    assert len(rows) == 129 and statuses['Reviewed'] == 121 and len(rule_names) == 10
    storage = storage_for(VIDEOS)
    checks = {
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'baseline_rows_preserved': len(baseline), 'indexed_videos': len(rows),
        'accepted_full_reviews': statuses['Reviewed'] - len(rule_names), 'completed_rule_tests': len(rule_names),
        'archived_videos': len(archive_names), 'pending_indexed_videos': len(rows) - statuses['Reviewed'],
        'recordings_reviewed': 2, 'battles': 1, 'all_coverage_lead_event_hash_location_checks_passed': True,
        'raw_first_passes_preserved': True, 'pause_games_entries': 0, 'ladder_log_entries': 0,
        'simulator_changes': False, 'repair_pinning': False, 'fixture_ingestion': False, 'training': False,
        'storage': storage,
    }
    save(BATCH / 'RESULTS.json', {'recordings': 2, 'battles': 1, 'intent': 'rules_testing',
        'observation': 'Tongue Whip targeted benched Meowth; Carefree Steps flipped heads and prevented30, preserving50HP',
        'source_of_code_comparison': 'Owner-provided prediction; current engine or build not inspected',
        'pause_games_entries': 0, 'ladder_log_entries': 0, 'results': results})
    save(BATCH / 'STORAGE_STATUS.json', storage)
    save(BATCH / 'FINAL_CHECKS.json', checks)
    part2 = 'Recording_QA/20261002_161342000_iOS_rule_sol/evidence/'
    head = '''# Carefree Steps snipe rule test, October 2, 2026

**A snipe targeting benched Meowth triggered Carefree Steps. Heads prevented the damage, and Meowth stayed at 50 HP.** Tongue Whip is the filmed example: its printed attack deals 30 damage to one opposing Benched Pokemon. Linear Attack was supplied as another example of the same class, not a separate required test.

The two recordings are reviewed and archived unchanged as **one interrupted computer test battle**. They are excluded from Pause Games and Ladder Log. A fresh Sol high worker reviewed all available footage; the lead checked ordinary turns, the cut, the decisive sequence and the ending. Astra independently checked the ability and prevention sequence.

| Source | Available footage | Role | Review |
|---|---|---|---|
'''
    lines = []
    for result, role in zip(results, ['Setup through turn 7; recording cuts', 'Same public turn-7 board through the test and Victory']):
        lines.append(f"| {result['video']} | {result['duration_seconds']:.2f} seconds | {role} | [Full available-source review]({result['review']}) |")
    evidence_text = f'''

## Recorded test

Times below are local to the second recording, 20261002_161342000_iOS.MP4.

- [86 seconds]({part2}t0086.00.jpg): Tongue Whip targets benched Meowth at 50 HP; the attack specifies 30 damage to one opposing Benched Pokemon.
- [87 seconds]({part2}t0087.00.jpg): the ability banner explicitly names Carefree Steps.
- [89 seconds]({part2}t0089.00.jpg): the prevention coin prompt appears.
- [91 seconds]({part2}t0091.00.jpg): the coin explicitly lands heads.
- [94 seconds]({part2}t0094.00.jpg): Meowth shows a shield and remains at 50 HP.

[Astra's targeted check](Recording_QA/BATCH_2026-10-02_CAREFREE_SNIPES/ASTRA_CAREFREE_CHECK.md) agrees this is Carefree Steps, not Victory Star. This establishes the intended interaction in the filmed snipe example. It supports repair B's stated behavior over the quoted no-coin behavior for this case. The simulator description and code references came from the owner; this review did not inspect or verify a current engine, build or pinned repair. Tails behavior and other individual snipe variants are not established by this heads example.

## Recording cut and battle context

Both sides' public board, HP, score and Rainbow Cave agree across the recording cut. The first recording ends during the start of turn 7; the second begins on that same public board. A hand difference is visible, so the missing interval and its actions remain unrecorded. No draw or elapsed duration is invented. The raw frozen intake relationship is retained; the verified public-board relationship is documented in the accepted reviews.

The ending explicitly shows Victory against the computer's Mega Blaziken ex & Typhlosion ex Deck (Deluxe Pack: Mega): 3-1, went first, 15 turns, 360 damage. This outcome provides context only and has no competitive-log entry. Auto was off for the rules-test interaction and switched on later; exact visible intervals and the remaining battle sequence are documented in the source reviews. The blue icon on Meowth is its damage-prevention effect, not a recorded Sleep condition.

[Combined time-coded account](Recording_QA/BATCH_2026-10-02_CAREFREE_SNIPES/TEST_REVIEW.md) links the two parts and covers their available turns and state changes.

## Preservation and verification

Both before/after archive hashes match their frozen source identities. All 127 baseline index rows are preserved exactly. Current inventory is 129 videos: 111 accepted full-battle reviews and 10 completed rule-test recordings in Reviewed, plus eight indexed pending items. The two new rule-test recordings are one battle. The older backlog remains paused. No simulator change, repair pinning, fixture ingestion or training occurred.

{storage_sentence(storage, 'two')}

[Verification records](Recording_QA/BATCH_2026-10-02_CAREFREE_SNIPES/FINAL_CHECKS.json) retain completion events, source proofs and storage status. Raw worker reports and extracted evidence remain available locally.
'''
    report = head + '\n'.join(lines) + evidence_text
    assert '\u2014' not in report
    for ref in re.findall(r'\]\(([^)]+)\)', report):
        assert (ROOT / ref).is_file(), ref
    (ROOT / 'CAREFREE_STEPS_RULE_TEST_2026-10-02.md').write_text(report, encoding='utf-8')
    status_path = ROOT / 'READ_ME_REVIEW_STATUS.md'
    text = status_path.read_text(encoding='utf-8-sig')
    update = f'Updated after the October 2 Carefree Steps snipe test. Both recordings are reviewed as one interrupted computer battle, independently accepted, registered as completed rule tests and archived with matching hashes. Carefree Steps flips heads for Tongue Whip against benched Meowth and prevents the 30 damage; Meowth stays at 50 HP. No Pause Games or Ladder Log entry. See [the test findings and full reviews](CAREFREE_STEPS_RULE_TEST_2026-10-02.md). {storage_sentence(storage, "two")}'
    if 'Updated after the October 2 Carefree Steps' not in text:
        title, rest = text.split('\n', 1)
        text = title + '\n\n' + update + '\n' + rest
    else:
        text = re.sub(r'Updated after the October 2 Carefree Steps[^\n]*', lambda _: update, text)
    text = text.replace('contains 127 videos: 111 accepted full-battle reviews and 8 completed rule tests', 'contains 129 videos: 111 accepted full-battle reviews and 10 completed rule tests')
    shark_names = ['20261002_114458000_iOS.MP4', '20261002_115323000_iOS.MP4', '20261002_132311000_iOS.MP4', '20261002_143309000_iOS.MP4', '20261002_143837000_iOS.MP4']
    shark_storage = storage_for(shark_names)
    shark_batch = ROOT / 'Recording_QA' / 'BATCH_2026-10-02_SHARK_TEMPO'
    save(shark_batch / 'STORAGE_STATUS.json', shark_storage)
    shark_checks = read(shark_batch / 'FINAL_CHECKS.json')
    shark_checks['storage'] = shark_storage
    shark_checks['storage_rechecked_at'] = shark_storage['checked_at']
    save(shark_batch / 'FINAL_CHECKS.json', shark_checks)
    shark_results = read(shark_batch / 'RESULTS.json')
    by_shark = {entry['video']: entry for entry in shark_storage['entries']}
    for result in shark_results['results']:
        result['storage'] = {key: value for key, value in by_shark[result['video']].items() if key != 'video'}
    save(shark_batch / 'RESULTS.json', shark_results)
    shark_path = ROOT / 'SHARK_TEMPO_COMPETITIVE_2026-10-02.md'
    shark_report = shark_path.read_text(encoding='utf-8-sig')
    old_storage = '1 of 5 originals are confirmed online-only; 3.22 GB remains locally allocated while OneDrive sync or space release is pending. Review packets and evidence remain pinned locally.'
    shark_report = shark_report.replace(old_storage, storage_sentence(shark_storage, 'five'))
    shark_path.write_text(shark_report, encoding='utf-8')
    text = text.replace(old_storage, storage_sentence(shark_storage, 'five'))
    status_path.write_text(text, encoding='utf-8')
    for packet in [BATCH, *[ROOT / 'Recording_QA' / (Path(name).stem + '_rule_sol') for name in VIDEOS]]:
        assert packet.resolve().is_relative_to((ROOT / 'Recording_QA').resolve()) and not list(packet.rglob('*.MP4'))
        subprocess.run(['attrib', '+P', '-U', str(packet / '*'), '/S', '/D'], check=True, capture_output=True, text=True)
    print(f'Confirmed: two completed source reviews, one test battle, 127 baseline rows preserved, 129 indexed; {storage["online_only"]}/2 test originals and {shark_storage["online_only"]}/5 Shark originals online-only.')


if __name__ == '__main__':
    main()
