"""Copy the ready written/evidence packet to the required Boss Folder."""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

B = Path(__file__).resolve().parent
boss = Path('C:/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder').resolve()
D = boss / B.name
check = json.loads((B / 'BATCH_COMPLETION_CHECK.json').read_text(encoding='utf-8-sig'))
assert check['all_requested_local_reviews_complete'] is True
assert D.parent == boss and not D.exists()
files = sorted(p for p in B.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
assert not any(p.suffix.lower() in ['.mp4', '.mov', '.m4v', '.mkv', '.avi'] for p in files)
shutil.copytree(B, D, ignore=shutil.ignore_patterns('__pycache__'))
copies = []
for p in files:
    rel = p.relative_to(B)
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    assert hashlib.sha256((D / rel).read_bytes()).hexdigest() == sha
    copies.append({'path': rel.as_posix(), 'bytes': p.stat().st_size, 'sha256': sha})
r = {'copied_utc': datetime.now(timezone.utc).isoformat(), 'source': str(B), 'destination': str(D), 'file_count': len(copies), 'all_copy_hashes_match': True, 'videos_copied': 0, 'files': copies}
p = B / 'MIRROR_RECEIPT.json'
p.write_text(json.dumps(r, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
shutil.copy2(p, D / p.name)
assert hashlib.sha256(p.read_bytes()).hexdigest() == hashlib.sha256((D / p.name).read_bytes()).hexdigest()
print(json.dumps({'mirrored_files': len(copies), 'copy_hashes_match': True, 'videos_copied': 0}))
