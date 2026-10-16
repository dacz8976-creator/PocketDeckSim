"""Metadata-only checkpoint for the four still-unavailable requested sources."""
import hashlib, json, shutil, tomllib
from datetime import datetime, timezone
from pathlib import Path
from free_reviewed_video_space import metadata

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / 'Recording_QA/BATCH_2026-10-14_NEWER_LADDER_FOUR'
BOSS = Path('C:/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder') / BATCH.name
NAMES = ['20261014_232438000_iOS.MP4', '20261014_233402000_iOS.MP4', '20261014_234511000_iOS.MP4', '20261014_234728000_iOS.MP4']
now = datetime.now(timezone.utc).isoformat()
rows = [{'source_filename': name, 'metadata': metadata(ROOT / name)} for name in NAMES]
assert all(row['metadata']['allocated_bytes'] == 0 for row in rows), 'Availability changed; perform readable intake instead'
automation_path = Path('C:/Users/dacz8/.codex/automations/retry-four-ladder-uploads/automation.toml')
automation = tomllib.loads(automation_path.read_text(encoding='utf-8'))
assert automation['status'] == 'ACTIVE' and automation['kind'] == 'heartbeat'
status = {'checked_utc': now, 'owner_authorization': 'Yes, include all six', 'owner_followup': 'Either wait or try again later.', 'requested_games_this_batch': 4, 'reviewable_games': 0, 'reviewed_games': 0, 'sources_claimed': 0, 'source_rows': rows, 'pending_reason': 'All four canonical sources are OneDrive cloud placeholders with zero locally allocated bytes. Bounded read and hydration attempts timed out. No readable matching local copies were found.', 'next_action': 'Scheduled hourly retry in this thread, limited to four runs; proceed only after readable media, stable metadata, SHA-256 and duration.', 'automation_id': automation['id'], 'automation_status': automation['status'], 'automation_created_utc': datetime.fromtimestamp(automation['created_at'] / 1000, timezone.utc).isoformat(), 'related_completed_batch': 'BATCH_2026-10-14_LATE_LADDER_TWO', 'older_backlog_reopened': False, 'media_deleted': False}
(BATCH / 'BATCH_STATUS.json').write_text(json.dumps(status, indent=2) + '\n', encoding='utf-8')
(BATCH / 'README.md').write_text('# Pending October 14 ladder uploads\n\nThe owner authorized all six new recordings. The original two are complete in BATCH_2026-10-14_LATE_LADDER_TWO. These four remain unavailable for visual review:\n\n' + ''.join('- `' + name + '`\n' for name in NAMES) + '\nAll four still have zero allocated local bytes. Bounded read and hydration attempts timed out. No source hash, duration, game result or full-review claim is made. The owner asked to wait or try later; the active heartbeat `retry-four-ladder-uploads` checks hourly for up to four runs in the same thread. Review only after stable readable source identity is established. Preserve originals and skip existing active or accepted assignments. Do not restart the older paused backlog.\n\nSee BATCH_STATUS.json and per-source AVAILABILITY/HYDRATION_RETRY receipts.\n', encoding='utf-8')
files = []
for path in sorted(BATCH.rglob('*')):
    if not path.is_file() or path.name == 'MIRROR_RECEIPT.json': continue
    assert path.suffix.lower() not in ['.mp4', '.mov', '.mkv']
    rel = path.relative_to(BATCH)
    dest = BOSS / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if dest.exists() and hashlib.sha256(dest.read_bytes()).hexdigest() != digest:
        assert path.name in ['README.md', 'BATCH_STATUS.json'], dest
        shutil.copy2(dest, dest.with_name(dest.name + '.before_' + datetime.now(timezone.utc).strftime('%H%M%S')))
    shutil.copy2(path, dest)
    assert hashlib.sha256(dest.read_bytes()).hexdigest() == digest
    files.append({'path': rel.as_posix(), 'sha256': digest})
receipt = {'created_utc': now, 'destination': str(BOSS), 'all_hashes_verified': True, 'videos_copied': 0, 'files': files}
(BATCH / 'MIRROR_RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
shutil.copy2(BATCH / 'MIRROR_RECEIPT.json', BOSS / 'MIRROR_RECEIPT.json')
print(json.dumps({'pending_sources': len(rows), 'reviewable': 0, 'retry': automation['id'], 'mirrored_files': len(files)}))
