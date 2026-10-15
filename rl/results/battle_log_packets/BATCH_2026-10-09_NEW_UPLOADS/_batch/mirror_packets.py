import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

batch = Path(__file__).resolve().parent
destination = Path(r'C:\Users\dacz8\Projects\Pocket Deck Lab\Boss Folder\new-uploads-2026-10-09')
destination.mkdir(parents=True, exist_ok=True)

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

records = []
for packet in sorted(batch.glob('20261009_*_iOS')):
    if not (packet / 'LEAD_ACCEPTANCE.json').exists():
        continue
    acceptance = json.loads((packet / 'LEAD_ACCEPTANCE.json').read_text(encoding='utf-8-sig'))
    assert acceptance['accepted'] is True
    assert list(packet.glob('MOVE_RECEIPT.*.json')), packet
    copied = []
    for source in sorted(packet.rglob('*')):
        if not source.is_file():
            continue
        target = destination / packet.name / source.relative_to(packet)
        target.parent.mkdir(parents=True, exist_ok=True)
        source_hash = sha(source)
        if target.exists():
            assert sha(target) == source_hash, f'Destination collision: {target}'
        else:
            shutil.copy2(source, target)
            assert sha(target) == source_hash, target
        copied.append({'relative_path': str(source.relative_to(packet)), 'sha256': source_hash})
    records.append({'packet': packet.name, 'destination': str(destination / packet.name), 'verified_file_count': len(copied), 'files': copied})
receipt = {'copied_at_utc': datetime.now(timezone.utc).isoformat(), 'packets': records}
(batch / 'BOSS_FOLDER_COPY_RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
for record in records:
    print(json.dumps({k: v for k, v in record.items() if k != 'files'}))
