import hashlib
import json
import shutil
from pathlib import Path

batch = Path(__file__).resolve().parent
destination = Path(r'C:\Users\dacz8\Projects\Pocket Deck Lab\Boss Folder\new-uploads-2026-10-09')
assert destination.is_dir()
records = []
for name in ['BATCH_SUMMARY.txt', 'BATCH_STATUS.json', 'BOSS_FOLDER_COPY_RECEIPT.json', 'ONEDRIVE_RETRY.json', 'INTAKE_ERRORS.json']:
    source = batch / name
    target = destination / name
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if target.exists():
        assert hashlib.sha256(target.read_bytes()).hexdigest() == digest, f'Destination collision: {target}'
    else:
        shutil.copy2(source, target)
        assert hashlib.sha256(target.read_bytes()).hexdigest() == digest
    records.append({'source': str(source), 'destination': str(target), 'sha256': digest})
(batch / 'BOSS_BATCH_REPORT_RECEIPT.json').write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'verified_report_files': len(records), 'destination': str(destination)}))
