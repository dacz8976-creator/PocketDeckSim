"""Read and hash only an explicitly requested local OneDrive upload."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from free_reviewed_video_space import metadata

ROOT = Path(__file__).resolve().parent.parent
NAMES = ['20261016_015753000_iOS.MP4', '20261016_020806000_iOS.MP4', '20261016_031512000_iOS.MP4']
p = argparse.ArgumentParser()
p.add_argument('video', choices=NAMES)
args = p.parse_args()
path = ROOT / args.video
before = path.stat()
before_meta = metadata(path)
h = hashlib.sha256()
count = 0
print(json.dumps({'source': args.video, 'before': before_meta, 'operation': 'Normal local file read and SHA256'}), flush=True)
with path.open('rb') as f:
    while True:
        block = f.read(4 * 1024 * 1024)
        if not block:
            break
        h.update(block)
        count += len(block)
        if count % (128 * 1024 * 1024) == 0:
            print(json.dumps({'source': args.video, 'bytes_read': count, 'total_bytes': before.st_size}), flush=True)
after = path.stat()
assert count == before.st_size
assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)
stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
data = {'source': args.video, 'sha256': h.hexdigest(), 'bytes_read': count,
        'stable_size_mtime': True, 'verified_utc': stamp, 'before': before_meta, 'after': metadata(path)}
out = ROOT / 'Recording_QA/LOCAL_DOWNLOAD_RESUME_20261015' / (args.video + '.READABLE.' + stamp + '.json')
with out.open('x', encoding='utf-8') as f:
    json.dump(data, f, indent=2)
print(json.dumps(data), flush=True)
