"""Record successful CLI-bound downloads, preserving earlier cloud-access failures."""
import json
from datetime import datetime, timezone
from pathlib import Path

batch = Path(__file__).resolve().parent
root = batch.parent.parent
names = ['20261012_003458000_iOS.MP4', '20261012_004435000_iOS.MP4']
sources = []
for name in names:
    binding = json.loads((batch / Path(name).stem / 'SOURCE.json').read_text(encoding='utf-8-sig'))
    current = root / name
    if not current.exists():
        current = root / 'Reviewed' / name
    assert current.is_file() and current.stat().st_size == binding['bytes']
    assert binding['video_basename'] == name and len(binding['sha256']) == 64
    assert binding['source_identity_basis'] == 'CLI SHA-256 and stable size/mtime during intake'
    sources.append({'source_video': name, 'bytes': binding['bytes'], 'sha256': binding['sha256'],
                    'duration_seconds': binding['duration_seconds'], 'intake_utc': binding['intake_utc'],
                    'identity_verified_event_id': binding['identity_verified_event_id'],
                    'identity_basis': binding['source_identity_basis'], 'binding': str(batch / Path(name).stem / 'SOURCE.json')})
receipt = {'verified_utc': datetime.now(timezone.utc).isoformat(), 'requested_retry_sources': 2,
           'successful_downloads': 2, 'remaining_download_blockers': [], 'browser_sign_in_needed': False,
           'originals_modified': False, 'sources': sources,
           'earlier_failed_attempts': 'Preserved in per-source source_access_history and batch retry receipts.'}
(batch / 'RESUME_DOWNLOAD_SUCCESS.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
print(json.dumps(receipt, indent=2))
