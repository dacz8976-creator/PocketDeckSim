import json
import shutil
from pathlib import Path

batch = Path(__file__).resolve().parent
storage = batch.parent / 'CLOUD_STORAGE'
names = [f'20261009_{stamp}000_iOS.MP4' for stamp in ['193905', '194240', '194445', '195029', '195808']]
matches = {}
for path in sorted(storage.glob('*.apply.json')):
    data = json.loads(path.read_text(encoding='utf-8-sig'))
    for entry in data.get('entries', []):
        if entry['video'] in names:
            matches[entry['video']] = (path, data, entry)
assert set(matches) == set(names)
for name in names:
    path, data, entry = matches[name]
    packet = batch / name[:-4]
    shutil.copy2(path, packet / 'CLOUD_STORAGE_RECEIPT.json')
    print(json.dumps({'video': name, 'receipt': str(path), 'online_only': entry['after']['online_only'], 'pending_reason': entry.get('pending_reason'), 'local_bytes_reclaimed': data['local_bytes_reclaimed']}))
