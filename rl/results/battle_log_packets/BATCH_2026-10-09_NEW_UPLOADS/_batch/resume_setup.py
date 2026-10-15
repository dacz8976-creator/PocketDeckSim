import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

batch = Path(__file__).resolve().parent
root = batch.parent.parent
rows = list(csv.DictReader((root / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='')))
baseline = batch / 'RESUME_INDEX_BASELINE.json'
assert not baseline.exists()
baseline.write_text(json.dumps({'row_count': len(rows), 'videos': [r['Video'] for r in rows], 'rows_sha256': hashlib.sha256(json.dumps(rows, sort_keys=True, ensure_ascii=False).encode()).hexdigest()}, indent=2) + '\n', encoding='utf-8')
for stamp in ['195432', '222100', '222740']:
    name = f'20261009_{stamp}000_iOS.MP4'
    packet = batch / name[:-4]
    source = json.loads((packet / 'SOURCE.json').read_text(encoding='utf-8-sig'))
    assignment = {'source': name, 'source_sha256': source['sha256'], 'model': 'gpt-6-sol', 'reasoning_effort': 'high', 'scope': 'Full visual review of entire source, all recorded matches/turns through terminal result; independent bounded Sol verification and lead acceptance before archival', 'first_pass': f'/root/resumed_review_{stamp}', 'registration_reviewer': 'root-new-uploads-20261009', 'classification': 'Worker must determine from source before external routing'}
    (packet / 'RESUMED_ASSIGNMENT.json').write_text(json.dumps(assignment, indent=2) + '\n', encoding='utf-8')
    run = subprocess.run([sys.executable, str(root / 'Review_Log/review_log.py'), 'record', '--video', name, '--reviewer', 'root-new-uploads-20261009', '--status', 'in_progress', '--scope', assignment['scope'], '--recording-time', source['container_creation_utc'], '--evidence', str(packet / 'SOURCE.json'), '--notes', 'Owner requested retry after source access restored. Fresh compact Sol full review, separate independent Sol verification, lead integration. Existing accepted reviews and paused older backlog excluded.'], capture_output=True, text=True)
    print(run.stdout, end='')
    assert run.returncode == 0, run.stderr
print(f'Preserved baseline of {len(rows)} existing index rows')
