"""Metadata-only check of the selected two archived originals."""
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BATCH = Path(__file__).resolve().parent
ROOT = BATCH.parent.parent
sys.path.insert(0, str(ROOT / 'Recording_QA'))
import free_reviewed_video_space as storage
NAMES = ['20261013_022530000_iOS.MP4', '20261013_030351000_iOS.MP4']
with (ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='') as f:
    rows = {r['Video']: r for r in csv.DictReader(f)}
entries = []
for name in NAMES:
    assert rows[name]['Status'] == 'Reviewed' and rows[name]['Location'].replace('\\', '/') == 'Reviewed/' + name
    path = ROOT / 'Reviewed' / name
    info = storage.metadata(path)
    entries.append({'video': name, 'path': str(path), 'before': info, 'after': info, 'source_contents_read': False})
ready = all(e['after']['in_sync'] and e['after']['online_only'] and e['after']['allocated_bytes'] == 0 for e in entries)
receipt = {'created_at_utc': datetime.now(timezone.utc).isoformat(), 'operation': 'Metadata-only final storage check', 'videos': 2, 'online_only': sum(e['after']['online_only'] for e in entries), 'allocated_bytes_after': sum(e['after']['allocated_bytes'] for e in entries), 'files_deleted': 0, 'complete': ready, 'entries': entries}
target = BATCH / ('FINAL_STORAGE_CHECK.json' if ready else 'STORAGE_PENDING.json')
if ready:
    assert not target.exists(), 'Final storage receipt already exists'
target.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'complete': ready, 'online_only': receipt['online_only'], 'allocated_bytes': receipt['allocated_bytes_after'], 'states': [{'video': e['video'], 'in_sync': e['after']['in_sync'], 'online_only': e['after']['online_only']} for e in entries]}))
