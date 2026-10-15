import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('stem')
args = parser.parse_args()
assert args.stem in [f'20261009_{s}000_iOS' for s in ['195432', '222100', '222740']]
batch = Path(__file__).resolve().parent
root = batch.parent.parent
packet = batch / args.stem
source = json.loads((packet / 'SOURCE.json').read_text(encoding='utf-8-sig'))
acceptance = json.loads((packet / 'LEAD_ACCEPTANCE.json').read_text(encoding='utf-8-sig'))
assert acceptance['accepted']
for name, digest in acceptance['verified_primary_hashes'].items():
    assert hashlib.sha256((packet / name).read_bytes()).hexdigest() == digest
evidence_names = ['REVIEW.md', 'COVERAGE.md', 'FINDINGS.json', 'independent_sol/VERIFICATION.json', 'LEAD_ACCEPTANCE.json']
evidence_names += [p.name for p in packet.glob('LEAD_*.txt')]
command = [sys.executable, str(root / 'Review_Log/review_log.py'), 'record', '--video', source['video_basename'], '--reviewer', 'root-new-uploads-20261009', '--status', 'full_battle_review_complete', '--scope', f"Complete recorded computer battle, all available turns from setup through terminal result and source tail ({source['duration_seconds']:.6f} seconds). Full Sol review, separate independent Sol verification and targeted lead acceptance.", '--recording-time', source['container_creation_utc'], '--notes', 'Computer battle excluded from Ladder and human Pause Games. Auto status and source limitations retained. Independent source binding and actual final primary hashes verified. Prior access errors resolved; earlier accepted entries and unrelated active reviews preserved.']
for name in evidence_names:
    command.extend(['--evidence', str(packet / name)])
deadline = time.monotonic() + 600
attempt = 0
while True:
    attempt += 1
    run = subprocess.run(command, capture_output=True, text=True)
    if run.returncode == 0:
        output = {'exit_code': 0, 'attempts': attempt, 'event_path': run.stdout.strip(), 'source_filename': source['video_basename'], 'source_sha256': source['sha256']}
        (packet / 'REGISTRATION_RESULT.json').write_text(json.dumps(output, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(output), flush=True)
        if run.stderr.strip():
            print(run.stderr.strip(), flush=True)
        break
    if 'review log is locked:' not in run.stderr or time.monotonic() >= deadline:
        print(run.stdout, end='')
        print(run.stderr, end='', file=sys.stderr)
        raise SystemExit(run.returncode)
    if attempt == 1:
        print('Waiting for the active shared review-log writer; its lock is preserved.', flush=True)
    time.sleep(10)
