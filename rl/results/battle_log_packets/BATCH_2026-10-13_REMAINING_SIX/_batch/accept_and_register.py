"""Lead-only registration after independently accepted final input hashes."""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BATCH = Path(__file__).resolve().parent
ROOT = BATCH.parent.parent
validator = ROOT / 'Recording_QA/BATCH_2026-10-11_NEW_PAUSE_GAMES/validate_packet.py'
parser = argparse.ArgumentParser()
parser.add_argument('packet', choices=['20261013_010003000_iOS', '20261013_010837000_iOS', '20261013_014423000_iOS', '20261013_015011000_iOS', '20261013_015659000_iOS', '20261013_020824000_iOS'])
args = parser.parse_args()
packet = BATCH / args.packet

def read(name):
    return json.loads((packet / name).read_text(encoding='utf-8-sig'))

def save(name, value):
    (packet / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

source = read('SOURCE.json')
assignment = read('ASSIGNMENT.json')
game = read('PAUSE_GAME.json')
assert not (packet / 'LEAD_ACCEPTANCE.json').exists(), 'Inspect existing lead disposition before changing it'
receipt_path = packet / 'independent_sol/CORRECTION_RECHECK.json'
if not receipt_path.exists():
    receipt_path = packet / 'independent_sol/CHECK_RESULT.json'
independent = json.loads(receipt_path.read_text(encoding='utf-8-sig'))
assert independent.get('accepted') is True, 'Independent acceptance required'
assert independent['source_sha256'] == source['sha256']
assert not any(independent.get(key) for key in ['required_repairs', 'required_repairs_remaining', 'blocking_findings', 'remaining_repairs'])
frozen = {**independent.get('accepted_input_sha256', {}), **independent.get('checked_input_sha256', {}), **independent.get('supplemental_checked_input_sha256', {})}
required = ['REVIEW.md', 'COVERAGE.md', 'SUMMARY.json', 'UNCERTAINTIES.json', 'PAUSE_GAME.json', 'DECK_USED.json', 'TURN_LEDGER.json', 'TURN_EVIDENCE.json']
assert set(required).issubset(frozen), 'All eight final files must be independently frozen'
for name, digest in frozen.items():
    assert hashlib.sha256((packet / name).read_bytes()).hexdigest() == digest, 'Accepted file changed: ' + name
validation = subprocess.run([sys.executable, '-X', 'utf8', str(validator), str(packet)], capture_output=True, text=True, encoding='utf-8', check=True)
structure = json.loads(validation.stdout)
assert structure['structural_pass'] is True and structure['turn_rows'] > 0
turn_count = structure['turn_rows']
summary = read('SUMMARY.json')
assert turn_count == summary.get('turn_count', summary.get('turns_played'))
save('ROOT_STRUCTURE_CHECK.json', structure)
assert game['capture_status'] in ['complete', 'complete_with_recording_limits']
root_checks = read('ROOT_SOURCE_CHECKS.json')
assert root_checks['source_sha256'] == source['sha256'] and len(root_checks['checks']) >= 8
assert not root_checks.get('pending_primary_repairs'), 'Root source findings must be reconciled'
source_time = read('SOURCE_TIME.json')
assert source_time.get('match_date_local', source_time.get('local_match_date')) == '2026-10-12'
deck = read('DECK_USED.json')
assert deck.get('is_template') is not True
assert (BATCH / 'HISTORICAL_DECK_CATALOG.json').exists()
shutil.copy2(packet / 'PAUSE_GAME.json', packet / 'PAUSE_GAME.before_lead_acceptance.json')
game.update(lead_checked=True, battle_review_status='full_battle_review_complete', lead_acceptance='LEAD_ACCEPTANCE.json')
save('PAUSE_GAME.json', game)
acceptance = {
    'accepted': True, 'decision': 'accepted_full_battle_review', 'lead': '/root',
    'accepted_utc': datetime.now(timezone.utc).isoformat(), 'source_game_count': 1, 'all_source_games_accepted': True,
    'source_video': source['video_basename'], 'source_sha256': source['sha256'],
    'scope': f'Entire supplied recording, one human battle, opening, all {turn_count} turns and terminal result',
    'capture_status': game['capture_status'], 'turn_rows': turn_count,
    'independent_acceptance': str(receipt_path), 'accepted_input_sha256': frozen,
    'basis': 'Whole-source Sol review, separately bounded Sol checks against source frames, and lead reconciliation of coverage, ordinary decisions, draws/searches, hand arithmetic, point progression, decisive sequences and terminal outcome. Structural integrity checked separately.',
    'administrative_fields_changed_after_independent_freeze': ['lead_checked', 'battle_review_status', 'lead_acceptance'],
    'source_limits': game.get('limits', []), 'outcome': game.get('outcome'),
    'deck_status': 'Filmed deck binding and exact dated historical live list are recorded in DECK_USED. Current browser access is blocked; no current live readback or save is claimed. A fresh saved-list readback remains a separate required external step.',
    'external_status': 'Prepared game import pending; browser stopped by URL policy check. No external save claimed.',
}
save('LEAD_ACCEPTANCE.json', acceptance)
command = [sys.executable, '-X', 'utf8', str(ROOT / 'Review_Log/review_log.py'), '--root', str(ROOT), 'record',
           '--video', source['video_basename'], '--reviewer', assignment['reviewer'], '--status', 'full_battle_review_complete',
           '--scope', f'Whole one-game recording; all {turn_count} turns and ending, required Pause Games capture supplement, independent source checks and lead acceptance']
for name in ['REVIEW.md', 'COVERAGE.md', 'LEAD_ACCEPTANCE.json', 'PAUSE_GAME.json', 'DECK_USED.json', 'TURN_LEDGER.json', 'TURN_EVIDENCE.json', str(receipt_path.relative_to(packet))]:
    command += ['--evidence', str(packet / name)]
command += ['--notes', 'Lead is sole shared writer. Deck provenance and any exact-list limits are independently checked and preserved in DECK_USED.json. Hidden/unrecorded information remains explicit. External import pending. Human game routed to Pause Games by owner context; specific queue is unverified. No Ladder entry.']
result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
save('REGISTRATION_RESULT.json', {'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr, 'recorded_utc': datetime.now(timezone.utc).isoformat()})
assert result.returncode == 0, result.stderr
print('Accepted and registered ' + source['video_basename'])
