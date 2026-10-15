"""Final storage verification reads metadata only, never archived video contents."""
import csv
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

BATCH = Path(__file__).resolve().parent
ROOT = BATCH.parent.parent
sys.path.insert(0, str(ROOT / 'Recording_QA'))
import free_reviewed_video_space as storage

NAMES = ['20261012_010706000_iOS.MP4', '20261012_203719000_iOS.MP4',
         '20261012_210041000_iOS.MP4', '20261012_210823000_iOS.MP4',
         '20261012_225319000_iOS.MP4', '20261012_230258000_iOS.MP4']
with (ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='') as handle:
    rows = {r['Video']: r for r in csv.DictReader(handle)}
entries = []
for name in NAMES:
    assert rows[name]['Status'] == 'Reviewed' and rows[name]['Location'].replace('\\', '/') == 'Reviewed/' + name
    path = ROOT / 'Reviewed' / name
    info = storage.metadata(path)
    assert info['in_sync'] and info['online_only'] and info['allocated_bytes'] == 0, name
    entries.append({'video': name, 'path': str(path), 'before': info, 'after': info,
                    'source_contents_read': False})
receipt = {'created_at_utc': datetime.now(timezone.utc).isoformat(),
           'operation': 'Final metadata-only storage verification', 'videos': 6,
           'online_only': 6, 'allocated_bytes_after': 0, 'files_deleted': 0,
           'verification': 'In-sync cloud placeholders, online-only state and actual allocated bytes; no content reads.',
           'entries': entries}
target = BATCH / 'ALL_SIX_STORAGE_CHECK.json'
assert not target.exists()
target.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
selected = set(NAMES[-2:])
for path in sorted((ROOT / 'Recording_QA/CLOUD_STORAGE').glob('*.apply.json'), reverse=True):
    candidate = json.loads(path.read_text(encoding='utf-8-sig'))
    if {e['video'] for e in candidate.get('entries', [])} == selected:
        assert all(e['after']['in_sync'] and e['after']['online_only'] and e['after']['allocated_bytes'] == 0 for e in candidate['entries'])
        assert not (BATCH / 'FINAL_STORAGE_CHECK.json').exists()
        shutil.copy2(path, BATCH / 'FINAL_STORAGE_CHECK.json')
        print('All six originals online only; final two release receipt: ' + path.name)
        break
else:
    raise RuntimeError('Missing successful two-source release receipt')
