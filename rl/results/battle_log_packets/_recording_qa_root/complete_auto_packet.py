"""Register and archive an owner-declared Auto AI packet after lead acceptance."""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from refresh_accepted_packet import refresh_accepted_packet

p = argparse.ArgumentParser()
p.add_argument('video')
p.add_argument('--validate-only', action='store_true', help='Check the packet without registering or moving it')
a = p.parse_args()
root = Path(__file__).resolve().parent.parent
if Path(a.video).name != a.video or not a.video.startswith(('20260930_', '20261001_')):
    raise SystemExit('Expected an exact approved Auto AI batch source basename')
packet = root / 'Recording_QA' / (Path(a.video).stem + '_auto_sol')
required = ['SOURCE.json', 'REVIEW.md', 'COVERAGE.md', 'UNCERTAINTIES.json', 'SUMMARY.json', 'LEAD_ACCEPTANCE.json']
for filename in required:
    if not (packet / filename).is_file():
        raise SystemExit(f'Missing required packet file: {filename}')
binding = json.loads((packet / 'SOURCE.json').read_text(encoding='utf-8-sig'))
acceptance = json.loads((packet / 'LEAD_ACCEPTANCE.json').read_text(encoding='utf-8-sig'))
if acceptance.get('accepted') is not True:
    raise SystemExit('Explicit lead acceptance required')
if binding.get('ladder_eligible') is not False or acceptance.get('ladder_eligible') is not False:
    raise SystemExit('Explicit ladder exclusion required')
if acceptance.get('source_sha256') != binding['sha256']:
    raise SystemExit('Acceptance/source identity mismatch')
for ref in acceptance.get('lead_evidence', []):
    target = packet / ref
    if not target.resolve().is_relative_to(packet.resolve()) or not target.is_file():
        raise SystemExit(f'Missing or unsafe lead evidence: {ref}')
for filename in ['REVIEW.md', 'COVERAGE.md']:
    prose = (packet / filename).read_text(encoding='utf-8-sig')
    refs = set(re.findall(r'`([^`\n]+\.(?:jpg|png))`', prose))
    refs.update(re.findall(r'(?<![A-Za-z0-9_])((?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.*?-]+\.(?:jpg|png))(?![A-Za-z0-9_])', prose))
    for ref in refs:
        if '*' in ref or '?' in ref:
            matches = list(packet.glob(ref))
            if not matches or not all(path.is_file() and path.resolve().is_relative_to(packet.resolve()) for path in matches):
                raise SystemExit(f'Missing or unsafe evidence set: {ref}')
            continue
        if not (packet / ref).is_file():
            matches = list(packet.rglob(ref)) if '/' not in ref and '\\' not in ref else []
            if len(matches) != 1:
                raise SystemExit(f'Missing or ambiguous explicitly referenced evidence: {ref}')
if a.validate_only:
    print(f'Packet evidence valid: {a.video}')
    raise SystemExit(0)
command = [sys.executable, str(root / 'Review_Log' / 'review_log.py'), '--root', str(root), 'record', '--video', a.video, '--reviewer', binding['reviewer'], '--status', 'full_battle_review_complete', '--scope', acceptance['scope'], '--notes', 'Complete independent Sol first pass reconciled and accepted by root lead. Owner-declared Auto AI games are excluded from Ladder Log. See bound owner testimony and packet for source-grounded unknowns.']
for filename in ['REVIEW.md', 'COVERAGE.md', 'LEAD_ACCEPTANCE.json']:
    command += ['--evidence', str(packet / filename)]
for filename in ['INDEPENDENT_CHECK.md', 'ROOT_SPOT_CHECK.md', 'ASTRA_CHECK.md', 'LEAD_CLARIFICATION.md']:
    if (packet / filename).is_file():
        command += ['--evidence', str(packet / filename)]
subprocess.run(command, check=True)
shell = shutil.which('pwsh')
if not shell:
    raise SystemExit('PowerShell 7 required by the existing finalizer')
subprocess.run([shell, '-NoProfile', '-File', str(root / 'Recording_QA' / 'finalize_accepted_review.ps1'), '-Video', a.video, '-Packet', str(packet.relative_to(root))], check=True)
receipt_name = f'MOVE_RECEIPT.{a.video}.json'
receipt = json.loads((packet / receipt_name).read_text(encoding='utf-8-sig'))
if receipt['sha256_after'] != binding['sha256'] or not receipt['identity_match']:
    raise SystemExit('Archive identity verification failed')
review_path = packet / 'REVIEW.md'
review = review_path.read_text(encoding='utf-8-sig')
title, rest = review.split('\n', 1)
stamp = '\n\n**Current status: completed full-battle review accepted by the lead; original archived unchanged in `Reviewed`. Excluded from Ladder Log.**\n'
completion = '\n\n## Lead completion\n\nAccepted as a completed full-battle review after the source checks documented in `LEAD_ACCEPTANCE.json`. The unchanged original is archived in `Reviewed`; matching before/after SHA-256 is recorded in `' + receipt_name + '`. No Ladder Log entry was created.\n'
review_path.write_text(title + stamp + rest + completion, encoding='utf-8')
refresh_accepted_packet(packet)
print(f'Completed and verified: {a.video}')
