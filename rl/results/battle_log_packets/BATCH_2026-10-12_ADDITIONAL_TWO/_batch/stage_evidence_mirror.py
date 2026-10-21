"""Preserve accepted written evidence while the archive rename finishes syncing."""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

BATCH = Path(__file__).resolve().parent
BOSS = Path('C:/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder').resolve()
destination = BOSS / BATCH.name
assert destination.parent == BOSS and not destination.exists()
for name in ['20261012_225319000_iOS', '20261012_230258000_iOS']:
    accepted = json.loads((BATCH / name / 'LEAD_ACCEPTANCE.json').read_text(encoding='utf-8-sig'))
    assert accepted['accepted'] and accepted['all_source_games_accepted']
    moved = json.loads((BATCH / name / ('MOVE_RECEIPT.' + name + '.MP4.json')).read_text(encoding='utf-8-sig'))
    assert moved['identity_match'] and moved['sha256_before'] == moved['sha256_after']
live = json.loads((BATCH / 'LIVE_SAVE_VERIFICATION_230258.json').read_text(encoding='utf-8-sig'))
assert live['reloaded'] and live['total_games'] == 45 and live['prior_44_games_unchanged']
files = [p for p in BATCH.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
assert not any(p.suffix.lower() in ['.mp4', '.mov', '.m4v', '.mkv', '.avi'] for p in files)
shutil.copytree(BATCH, destination, ignore=shutil.ignore_patterns('__pycache__'))
copies = []
for path in sorted(files):
    relative = path.relative_to(BATCH)
    expected = hashlib.sha256(path.read_bytes()).hexdigest()
    assert hashlib.sha256((destination / relative).read_bytes()).hexdigest() == expected
    copies.append({'path': relative.as_posix(), 'bytes': path.stat().st_size, 'sha256': expected})
receipt = {'copied_utc': datetime.now(timezone.utc).isoformat(), 'source': str(BATCH),
           'destination': str(destination), 'file_count': len(copies),
           'all_copy_hashes_match': True, 'videos_copied': 0,
           'scope': 'Accepted reviews and live-save evidence backed up; final cloud cache release remains pending.',
           'files': copies}
target = BATCH / 'MIRROR_STAGING_RECEIPT.json'
assert not target.exists()
target.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
shutil.copy2(target, destination / target.name)
assert target.read_bytes() == (destination / target.name).read_bytes()
print(json.dumps({'backed_up_files': len(copies), 'all_copy_hashes_match': True, 'final_storage_pending': True}))
