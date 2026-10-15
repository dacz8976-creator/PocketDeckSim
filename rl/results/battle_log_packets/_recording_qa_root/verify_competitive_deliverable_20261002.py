"""Check and retain the final usable report; never reopen original video bytes."""
from datetime import datetime, timezone
from pathlib import Path
import re
import subprocess
from intake_competitive_20261002 import ROOT, BATCH, read, save, packet_for
from start_competitive_packet import SELECTED
from free_reviewed_video_space import metadata

report = ROOT / 'WAILORD_COMPETITIVE_2026-10-01.md'
prose = report.read_text(encoding='utf-8')
assert '\u2014' not in prose
assert all(prose.count(name) == 1 for name in SELECTED)
for target in re.findall(r'\]\(([^)]+)\)', prose):
    if target.startswith('https://'):
        continue
    path = (ROOT / target).resolve()
    assert path.is_relative_to(ROOT.resolve()) and path.is_file(), target
assert not list(BATCH.rglob('*.MP4'))
for path in [report, ROOT / 'READ_ME_REVIEW_STATUS.md']:
    subprocess.run(['attrib', '+P', '-U', str(path)], capture_output=True, check=True)
subprocess.run(['attrib', '+P', '-U', str(BATCH / '*'), '/S', '/D'], capture_output=True, check=True)
for name in SELECTED:
    packet = packet_for(name)
    assert read(packet / 'SUMMARY.json')['external_log_saved']
    assert read(packet / 'EXTERNAL_LOG_RECEIPT.json')['verified_after_reload']
    assert metadata(ROOT / 'Reviewed' / name)['online_only']
    assert metadata(packet / 'REVIEW.md')['pinned']
    assert metadata(packet / 'COVERAGE.md')['pinned']
assert metadata(report)['pinned']
restore = read(BATCH / 'INTAKE_STORAGE_RESTORE.json')
for entry in restore['entries']:
    entry['after'] = metadata(Path(entry['path']))
restore['rechecked_at'] = datetime.now(timezone.utc).isoformat()
save(BATCH / 'INTAKE_STORAGE_RESTORE.json', restore)
save(BATCH / 'DELIVERABLE_QA.json', {
    'checked_at': datetime.now(timezone.utc).isoformat(),
    'report': report.name, 'local_links_valid': True,
    'all_five_reviewed_archived_logged_and_verified': True,
    'all_five_originals_online_only': True,
    'reports_and_evidence_pinned': True,
    'excluded_intake_storage_online_only': sum(e['after']['online_only'] for e in restore['entries']),
    'excluded_intake_storage_allocated_bytes': sum(e['after']['allocated_bytes'] for e in restore['entries']),
    'original_contents_reopened_for_this_check': False
})
print('Final report, links, five saved results and online-only originals verified.')
