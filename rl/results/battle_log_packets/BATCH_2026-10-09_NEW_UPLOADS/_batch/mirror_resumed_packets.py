import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

batch = Path(__file__).resolve().parent
destination = Path(r'C:\Users\dacz8\Projects\Pocket Deck Lab\Boss Folder\new-uploads-2026-10-09')
assert destination.is_dir()
records = []

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

for stamp in ['195432', '222100', '222740']:
    packet = batch / f'20261009_{stamp}000_iOS'
    assert json.loads((packet / 'LEAD_ACCEPTANCE.json').read_text(encoding='utf-8-sig'))['accepted']
    assert list(packet.glob('MOVE_RECEIPT.*.json'))
    copied = []
    for source in sorted(packet.rglob('*')):
        if not source.is_file():
            continue
        target = destination / packet.name / source.relative_to(packet)
        target.parent.mkdir(parents=True, exist_ok=True)
        digest = sha(source)
        if target.exists():
            assert sha(target) == digest, f'Destination collision: {target}'
        else:
            shutil.copy2(source, target)
            assert sha(target) == digest
        copied.append({'relative_path': str(source.relative_to(packet)), 'sha256': digest})
    item = {'packet': packet.name, 'destination': str(destination / packet.name), 'verified_file_count': len(copied), 'files': copied}
    records.append(item)
    print(json.dumps({k: v for k, v in item.items() if k != 'files'}), flush=True)
(batch / 'RESUMED_BOSS_COPY_RECEIPT.json').write_text(json.dumps({'copied_at_utc': datetime.now(timezone.utc).isoformat(), 'packets': records}, indent=2) + '\n', encoding='utf-8')
