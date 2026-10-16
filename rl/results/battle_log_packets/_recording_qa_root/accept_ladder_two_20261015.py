"""Register a lead-accepted October 15 packet after independent source checks."""
import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / 'Recording_QA/BATCH_2026-10-15_LADDER_TWO'
SELECTED = ['20261015_201201000_iOS', '20261015_201850000_iOS']

def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

parser = argparse.ArgumentParser()
parser.add_argument('packet', choices=SELECTED)
args = parser.parse_args()
packet = BATCH / args.packet

def load(name):
    return json.loads((packet / name).read_text(encoding='utf-8-sig'))

def save(name, value):
    with (packet / name).open('x', encoding='utf-8') as f:
        f.write(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

source = load('SOURCE.json')
summary = load('SUMMARY.json')
manifest = load('REVIEW_PACKET_HASHES.json')
check = load('independent_sol/CHECK_RESULT.json')
decision = load('ROOT_DECISION.json')
assert check['accepted'] is True and decision['accepted'] is True
assert check['source_filename'] == summary['source_filename'] == decision['source_filename'] == source['video_basename']
assert check['source_sha256'] == summary['source_sha256'] == decision['source_sha256'] == source['sha256']
assert check['frozen_manifest_sha256'] == digest(packet / 'REVIEW_PACKET_HASHES.json')
assert check['frozen_files_match'] and check['primary_unchanged']
assert summary['battle_complete'] and summary['match_count'] == 1
assert decision['auto_option_seen'] is False
assert decision['note_prefix'] == summary['exact_three_item_note_prefix']
assert decision['full_timeline_and_coverage_read'] is True
for rel, sha in manifest['files'].items():
    path = (packet / rel).resolve()
    assert path.is_relative_to(packet.resolve()) and digest(path) == sha, rel
observations = decision['direct_source_observations']
assert observations and all(o['directly_viewed_by_root'] is True for o in observations)
for observation in observations:
    path = (packet / observation['path']).resolve()
    assert path.is_relative_to(packet.resolve())
    observation['sha256'] = digest(path)
now = datetime.now(timezone.utc).isoformat()
save('SOURCE_CHECKS.json', {'lead': '/root', 'checked_utc': now, 'source_filename': source['video_basename'],
    'source_sha256': source['sha256'], 'observations': observations,
    'coverage_reconciliation': 'Lead read full timeline and turn/phase coverage. A separate Sol reviewer checked ordinary turns and decisive evidence against retained source frames.'})
save('LEAD_ACCEPTANCE.json', {'accepted': True, 'decision': 'accepted_full_battle_review', 'lead': '/root',
    'accepted_utc': now, 'source_video': source['video_basename'], 'source_sha256': source['sha256'],
    'source_game_count': 1, 'all_source_games_accepted': True, 'battle_complete': True, 'archive_eligible': True,
    'scope': decision['scope'], 'independent_acceptance': str(packet / 'independent_sol/CHECK_RESULT.json'),
    'independent_acceptance_sha256': digest(packet / 'independent_sol/CHECK_RESULT.json'),
    'accepted_input_sha256': manifest['files'], 'frozen_manifest_sha256': digest(packet / 'REVIEW_PACKET_HASHES.json'),
    'root_checks': 'SOURCE_CHECKS.json', 'clarifications': decision.get('clarifications', [])})
save('LADDER_ENTRY.json', {'source_filename': source['video_basename'], 'source_sha256': source['sha256'],
    'section': decision['section'], 'opponent': decision['opponent'], 'opponent_deck': decision['opponent_deck'],
    'result': decision['result'], 'note': decision['note'], 'note_prefix': decision['note_prefix'],
    'match_creation_utc': source['source_creation_utc'], 'artifact': 'https://claude.ai/artifact/GHSfGSCzNiWNj8SFPXV3R1',
    'status': 'ready_for_live_save'})
command = [sys.executable, '-X', 'utf8', str(ROOT / 'Review_Log/review_log.py'), 'record', '--video', source['video_basename'],
    '--reviewer', load('ASSIGNMENT.json')['reviewer'], '--status', 'full_battle_review_complete',
    '--scope', decision['scope'], '--notes', decision['registration_notes'], '--recording-time', source['source_creation_utc']]
evidence = ['SOURCE.json', 'REVIEW.md', 'COVERAGE.md', 'SUMMARY.json', 'UNCERTAINTIES.json', 'REVIEW_PACKET_HASHES.json',
    'ROOT_DECISION.json', 'SOURCE_CHECKS.json', 'LEAD_ACCEPTANCE.json', 'LADDER_ENTRY.json', 'independent_sol/CHECK_RESULT.json']
if (packet / 'LEAD_CLARIFICATION.md').exists():
    evidence.append('LEAD_CLARIFICATION.md')
for name in evidence:
    command.extend(['--evidence', str(packet / name)])
result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', timeout=60)
save('REGISTRATION_RESULT.json', {'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr,
    'registered_utc': datetime.now(timezone.utc).isoformat()})
print(json.dumps({'packet': args.packet, 'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}))
raise SystemExit(result.returncode)
