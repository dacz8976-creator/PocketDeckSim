import hashlib
import json
import shutil
from pathlib import Path

batch = Path(__file__).resolve().parent
destination = Path(r'C:\Users\dacz8\Projects\Pocket Deck Lab\Boss Folder\new-uploads-2026-10-09')
records = []
for source_name, target_name in [('RESUMED_BATCH_SUMMARY.txt', 'RESUMED_BATCH_SUMMARY.txt'), ('BATCH_STATUS.json', 'RESUMED_BATCH_STATUS.json'), ('RESUMED_BOSS_COPY_RECEIPT.json', 'RESUMED_BOSS_COPY_RECEIPT.json'), ('BATCH_STORAGE_RESULT.json', 'BATCH_STORAGE_RESULT.json'), ('ONEDRIVE_RETRY.json', 'RESUMED_ONEDRIVE_RETRY.json')]:
    source = batch / source_name
    target = destination / target_name
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if target.exists():
        assert hashlib.sha256(target.read_bytes()).hexdigest() == digest, f'Destination collision: {target}'
    else:
        shutil.copy2(source, target)
        assert hashlib.sha256(target.read_bytes()).hexdigest() == digest
    records.append({'source': str(source), 'destination': str(target), 'sha256': digest})
(batch / 'RESUMED_BOSS_REPORT_RECEIPT.json').write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'verified_report_files': len(records), 'destination': str(destination)}))
