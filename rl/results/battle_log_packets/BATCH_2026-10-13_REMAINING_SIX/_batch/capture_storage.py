"""Check cloud metadata only; never rehydrate an archived original."""
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

B = Path(__file__).resolve().parent
R = B.parent.parent
sys.path.insert(0, str(R / 'Recording_QA'))
import free_reviewed_video_space as storage
names = json.loads((B / 'OWNER_CONTEXT.json').read_text(encoding='utf-8-sig'))['selected_sources']
with (R / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='') as f: rows = {r['Video']: r for r in csv.DictReader(f)}
entries = []
for n in names:
    assert rows[n]['Status'] == 'Reviewed' and rows[n]['Location'].replace('\\', '/') == 'Reviewed/' + n
    info = storage.metadata(R / 'Reviewed' / n)
    entries.append({'video': n, 'path': str(R / 'Reviewed' / n), 'before': info, 'after': info, 'source_contents_read': False})
ready = all(e['after']['in_sync'] and e['after']['online_only'] and e['after']['allocated_bytes'] == 0 for e in entries)
r = {'created_at_utc': datetime.now(timezone.utc).isoformat(), 'operation': 'Metadata-only final storage check', 'videos': len(names), 'online_only': sum(e['after']['online_only'] for e in entries), 'allocated_bytes_after': sum(e['after']['allocated_bytes'] for e in entries), 'files_deleted': 0, 'complete': ready, 'entries': entries}
p = B / ('FINAL_STORAGE_CHECK.json' if ready else 'STORAGE_PENDING.json')
assert not p.exists() or not ready, 'Final receipt already exists'
p.write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'complete': ready, 'online_only': r['online_only'], 'allocated_bytes': r['allocated_bytes_after']}))
