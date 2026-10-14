"""Reconcile and report the owner-requested evening Auto AI batch."""
import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / 'Recording_QA' / 'BATCH_2026-09-30_EVENING'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def check_gaps(document, name):
    gap_keys = {'unreviewed_intervals', 'unreviewed_battle_intervals', 'remaining_unreviewed_intervals', 'unreviewed_intervals_seconds', 'unreviewed_phases', 'uncovered_meaningful_phases', 'coverage_gaps', 'blocking_coverage_gaps', 'remaining_coverage_gaps', 'remaining_battle_coverage_gaps', 'uncovered_intervals', 'material_unresolved_events', 'consequential_unresolved_mechanics', 'consequential_unresolved_events'}
    if isinstance(document, dict):
        for key, value in document.items():
            if key in gap_keys:
                assert not value, f'Coverage/material gap: {name} {key}'
            check_gaps(value, name)
    elif isinstance(document, list):
        for value in document:
            check_gaps(value, name)

def main():
    intake = read(BATCH / 'INTAKE.json')
    baseline = read(BATCH / 'INDEX_BEFORE.json')
    rows = list(csv.DictReader((ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='')))
    counts = Counter(r['Video'] for r in rows)
    assert all(n == 1 for n in counts.values()), 'Duplicate review-index rows'
    current = {r['Video']: r for r in rows}
    for old in baseline:
        assert current[old['Video']] == old, f"Unrelated index row changed: {old['Video']}"
    events = [read(p) for p in (ROOT / 'Review_Log' / 'events').glob('*.json')]
    locations = read(ROOT / 'MEDIA_LOCATIONS.json')
    entries = []
    for item in intake['sources']:
        name = item['video']
        packet = ROOT / 'Recording_QA' / (Path(name).stem + '_auto_sol')
        entry = {'video': name, 'status': item['status'], 'ladder_eligible': False}
        acceptance_path = packet / 'LEAD_ACCEPTANCE.json'
        receipt_path = packet / f'MOVE_RECEIPT.{name}.json'
        if acceptance_path.exists() and receipt_path.exists():
            a, receipt, source, summary, uncertainty = (read(p) for p in [acceptance_path, receipt_path, packet / 'SOURCE.json', packet / 'SUMMARY.json', packet / 'UNCERTAINTIES.json'])
            assert a['accepted'] and a['ladder_eligible'] is False and source['ladder_eligible'] is False
            assert a['unreviewed_intervals'] == []
            assert source['sha256'] == item['sha256'] == a['source_sha256'] == receipt['sha256_before'] == receipt['sha256_after']
            assert receipt['identity_match'] and source['bytes'] == item['bytes'] == receipt['bytes']
            archive = ROOT / 'Reviewed' / name
            assert archive.is_file() and archive.stat().st_size == source['bytes'] and not (ROOT / name).exists()
            assert current[name]['Status'] == 'Reviewed' and current[name]['Location'] == 'Reviewed/' + name
            matches = [m for m in locations['moved'] if m['filename'] == name]
            assert len(matches) == 1 and matches[0]['sha256'] == source['sha256'] and Path(matches[0]['current_path']) == archive
            history = sorted((e for e in events if e.get('video_basename') == name), key=lambda e: e['logged_at_utc'])
            assert history[-1]['status'] == 'full_battle_review_complete' and history[-1]['video_sha256'] == source['sha256']
            assert any(e['event_id'] == receipt['review_event_id'] and e['status'] == 'full_battle_review_complete' for e in history)
            assert summary['current_status'] == 'full_battle_review_complete' and summary['lead_acceptance'] == 'accepted' and summary['source_archived'] and summary['global_registration_complete']
            for document in [summary, uncertainty]:
                check_gaps(document, name)
            for filename in ['SOURCE.json', 'REVIEW.md', 'COVERAGE.md', 'UNCERTAINTIES.json', 'SUMMARY.json', 'LEAD_ACCEPTANCE.json']:
                assert (packet / filename).is_file()
            entry.update(a)
            entry['status'] = 'accepted_and_archived'
        entries.append(entry)
    complete = [e for e in entries if e['status'] == 'accepted_and_archived']
    expected = intake['expected_recordings']
    wins = sum(e['outcome'] == 'owner_win' for e in complete)
    losses = sum(e['outcome'] == 'owner_loss' for e in complete)
    results = {'expected': expected, 'discovered': len(entries), 'completed': len(complete), 'not_yet_visible': max(0, expected - len(entries)), 'practice_wins': wins, 'practice_losses': losses, 'ladder_entries_created': 0, 'videos': entries}
    (BATCH / 'RESULTS.json').write_text(json.dumps(results, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    opening = f'All {expected} requested recordings are reviewed, lead-accepted and archived.' if len(complete) == expected else f'{len(complete)} of {expected} requested recordings are reviewed, lead-accepted and archived. {len(entries)} sources have appeared in Battle Logs.'
    lines = ['# September 30 evening Auto AI battle reviews', '', opening, '', f'These owner-declared Auto AI games are excluded from Ladder Log. Completed practice results: {wins} wins and {losses} losses. Every accepted packet contains a complete visual account, turn coverage, retained evidence, source identity, explicit uncertainties and bounded independent lead checks.', '', 'Filename timestamps begin 20261001; the upload and request were September 30 in America/Chicago. The filename clock basis is unverified.', '', '| Source recording | Visible owner core | Practice result | Review |', '|---|---|---|---|']
    for entry in entries:
        if entry['status'] == 'accepted_and_archived':
            points = entry['final_points']
            result = entry.get('result_display') or (('Win' if entry['outcome'] == 'owner_win' else 'Loss') + f" {points['owner']}-{points['opponent']}")
            link = 'Recording_QA/' + Path(entry['video']).stem + '_auto_sol/REVIEW.md'
            lines.append(f"| `{entry['video']}` | {entry['owner_visible_core']} | {result} vs {entry['opponent']} | [Complete review]({link}) |")
        else:
            lines.append(f"| `{entry['video']}` | Pending | {entry['status'].replace('_', ' ')} | Pending |")
    if results['not_yet_visible']:
        lines += ['', f"{results['not_yet_visible']} requested recordings have not yet appeared in Battle Logs. Their filenames, footage and results have not been reviewed."]
    if complete:
        lines += ['', '## Useful observations', '']
        for e in complete:
            finding = re.sub(r'(?<=[A-Za-z])(?=\+?\d)|(?<=\d)(?=[A-Za-z])', ' ', e['useful_finding'])
            lines.append(f"- `{e['video']}`: {finding}")
    lines += ['', '## Verification', '', 'Each archived original keeps its filename and bytes. Source bindings and matching SHA-256 before and after the move are saved in the packet receipts. Shared completion events, index rows and current media locations agree. Verification after storage release reads metadata rather than redownloading originals. Local storage release follows OneDrive sync; written reviews and retained evidence stay local.', '', 'Results-screen damage can include overkill. Point-circle displays stop at three; individual reviews distinguish the shown circles from actual award messages. Unknown hidden cards and untested rule interactions remain unknown.', '']
    (ROOT / 'BATTLE_TRANSCRIPTS_2026-09-30_EVENING.md').write_text('\n'.join(lines), encoding='utf-8')
    validation = {'passed_for_completed_packets': True, 'batch_complete': len(complete) == expected, 'completed_packets_verified': len(complete), 'unchanged_prior_index_entries': len(baseline), 'index_videos': len(rows), 'ladder_entries_created': 0, 'not_yet_visible': results['not_yet_visible'], 'archive_identity_basis': 'Matching source bindings and freshly hashed pre/post-move receipts; metadata-only reconciliation afterward'}
    if complete:
        assert locations['index_video_count'] == len(rows)
        assert locations['awaiting_review_or_confirmation'] == sum(r['Status'] != 'Reviewed' for r in rows)
    (BATCH / 'VALIDATION.json').write_text(json.dumps(validation, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(validation))

if __name__ == '__main__':
    main()
