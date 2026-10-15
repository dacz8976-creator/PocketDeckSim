import csv
import hashlib
import json
from pathlib import Path

batch = Path(__file__).resolve().parent
root = batch.parent.parent
baseline = json.loads((batch / 'INDEX_BASELINE.json').read_text(encoding='utf-8-sig'))
rows = list(csv.DictReader((root / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='')))
locations = json.loads((root / 'MEDIA_LOCATIONS.json').read_text(encoding='utf-8-sig'))
old = [row for row in rows if row['Video'] in baseline['videos']]
assert len(old) == baseline['row_count']
digest = hashlib.sha256(json.dumps(old, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
assert digest == baseline['rows_sha256'], 'Existing index rows changed'
results = []
resume_baseline_path = batch / 'RESUME_INDEX_BASELINE.json'
resume_unchanged = None
if resume_baseline_path.exists():
    resume_baseline = json.loads(resume_baseline_path.read_text(encoding='utf-8-sig'))
    resume_old = [row for row in rows if row['Video'] in resume_baseline['videos']]
    assert len(resume_old) == resume_baseline['row_count']
    assert hashlib.sha256(json.dumps(resume_old, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == resume_baseline['rows_sha256'], 'Existing rows changed during resumed reviews'
    resume_unchanged = len(resume_old)
for stamp in ['193905', '194240', '194445', '195029', '195432', '195808', '222100', '222740']:
    name = f'20261009_{stamp}000_iOS.MP4'
    packet = batch / name[:-4]
    item = {'video': name, 'packet': str(packet), 'status': 'pending'}
    if (packet / 'INTAKE_ERROR.json').exists() and not (packet / 'SOURCE.json').exists():
        item['status'] = 'source_access_blocked'
        item['error'] = json.loads((packet / 'INTAKE_ERROR.json').read_text(encoding='utf-8-sig'))
    elif (packet / 'SOURCE.json').exists():
        item['status'] = 'source_verified_review_pending'
    if (packet / 'LEAD_ACCEPTANCE.json').exists():
        acceptance = json.loads((packet / 'LEAD_ACCEPTANCE.json').read_text(encoding='utf-8-sig'))
        item['accepted'] = acceptance.get('accepted')
        item['outcome'] = acceptance.get('outcome')
    receipts = list(packet.glob('MOVE_RECEIPT.*.json'))
    if receipts:
        receipt = json.loads(receipts[0].read_text(encoding='utf-8-sig'))
        binding = json.loads((packet / 'SOURCE.json').read_text(encoding='utf-8-sig'))
        assert item.get('accepted') is True
        assert receipt['identity_match'] and receipt['sha256_before'] == receipt['sha256_after'] == binding['sha256']
        row = [r for r in rows if r['Video'] == name]
        assert len(row) == 1 and row[0]['Status'] == 'Reviewed' and row[0]['Location'] == f'Reviewed/{name}'
        assert (root / 'Reviewed' / name).exists() and not (root / name).exists()
        location = [entry for entry in locations['moved'] if entry['filename'] == name]
        assert len(location) == 1 and location[0]['sha256'] == binding['sha256']
        assert Path(location[0]['current_path']) == root / 'Reviewed' / name
        item['status'] = 'accepted_registered_archived'
    results.append(item)
output = {'existing_index_rows_unchanged': len(old), 'existing_index_rows_before_retry_unchanged': resume_unchanged, 'results': results}
(batch / 'BATCH_STATUS.json').write_text(json.dumps(output, indent=2) + '\n', encoding='utf-8')
print(json.dumps(output, indent=2))
