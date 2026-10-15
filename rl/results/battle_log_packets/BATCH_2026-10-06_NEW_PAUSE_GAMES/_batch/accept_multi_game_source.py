"""Accept every game and source interlude before a single multi-game source registration."""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from batch_packet_scope import game_packets

B = Path(__file__).resolve().parent
ROOT = B.parent.parent
ap = argparse.ArgumentParser()
ap.add_argument('packet')
ap.add_argument('--check-only', action='store_true')
args = ap.parse_args()
P = (B / args.packet).resolve()
assert P.parent == B and P.is_dir()

def read(p, name):
    return json.loads((p / name).read_text(encoding='utf-8-sig'))

def save(p, name, value):
    (p / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

source = read(P, 'SOURCE.json')
assignment = read(P, 'ASSIGNMENT.json')
packets = game_packets(P)
assert len(packets) > 1
checked = []
# Check all independent receipts before changing any game disposition.
for p in packets:
    assert not (p / 'LEAD_ACCEPTANCE.json').exists(), 'Existing lead disposition: inspect before updating'
    binding = read(p, 'SOURCE.json')
    assert binding['sha256'] == source['sha256'] and binding['video_basename'] == source['video_basename']
    receipt = p / 'independent_sol/CORRECTION_RECHECK.json'
    if not receipt.exists():
        receipt = p / 'independent_sol/CHECK_RESULT.json'
    independent = json.loads(receipt.read_text(encoding='utf-8'))
    accepted = independent.get('accepted') is True or ('accepted' not in independent and independent.get('status') in ('accepted', 'accepted_with_recording_limits'))
    assert accepted and not any(independent.get(k) for k in ('required_repairs', 'required_repairs_remaining', 'remaining_repairs')), str(p) + ' independent acceptance required'
    assert independent['source_sha256'] == source['sha256']
    for name, digest in {**independent.get('checked_input_sha256', {}), **independent.get('supplemental_checked_input_sha256', {})}.items():
        assert hashlib.sha256((p / name).read_bytes()).hexdigest() == digest, 'Accepted input changed: ' + str(p / name)
    result = subprocess.run([sys.executable, str(B / 'validate_packet.py'), str(p)], capture_output=True, text=True, encoding='utf-8', check=True)
    structure = json.loads(result.stdout)
    assert structure['structural_pass'] is True
    game = read(p, 'PAUSE_GAME.json')
    assert game['capture_status'] in ('complete', 'complete_with_recording_limits')
    if structure['turn_rows'] == 0:
        summary = read(p, 'SUMMARY.json')
        assert summary.get('turn_count') == 0 and independent.get('zero_turn_terminal_verified') is True
    checked.append((p, receipt, structure, game, independent))
summary = read(P, 'SUMMARY.json')
assert summary.get('source_game_count', summary.get('game_count')) == len(packets)
assert summary.get('whole_source_reviewed') is True
assert len(summary.get('games', [])) == len(packets)
assert checked[0][4].get('all_source_segments_verified') is True
total_turns = sum(item[2]['turn_rows'] for item in checked)
if args.check_only:
    print(json.dumps({'preflight_pass': True, 'game_count': len(packets), 'source_total_turn_rows': total_turns}))
    sys.exit(0)
evidence_paths = []
for number, (p, receipt, structure, game, _) in enumerate(checked, 1):
    save(p, 'ROOT_STRUCTURE_CHECK.json', structure)
    shutil.copy2(p / 'PAUSE_GAME.json', p / 'PAUSE_GAME.before_lead_acceptance.json')
    game.update(lead_checked=True, battle_review_status='full_battle_review_complete', lead_acceptance='LEAD_ACCEPTANCE.json')
    save(p, 'PAUSE_GAME.json', game)
    acceptance = {
        'accepted': True, 'decision': 'accepted_full_battle_review', 'lead': '/root',
        'accepted_utc': datetime.now(timezone.utc).isoformat(),
        'source_video': source['video_basename'], 'source_sha256': source['sha256'],
        'scope': f'Game {number} of {len(packets)} in the fully reviewed source; all games and intervening deck edits checked before source registration.',
        'game_number_in_source': number, 'source_game_count': len(packets),
        'all_source_games_accepted': True,
        'game_packet_paths': [str(q) for q in packets],
        'source_total_turn_rows': total_turns,
        'capture_status': game['capture_status'], 'turn_rows': structure['turn_rows'],
        'independent_acceptance': str(receipt),
        'basis': 'Full Sol accounts of every game and source interlude; separate bounded independent checks including ordinary turns, captures, draws/searches, both boards and decisive result. All repairs verified. Root reconciled reports and inspected source evidence.',
        'source_limits': game.get('limits', []), 'outcome': game.get('outcome'),
        'external_status': 'Prepared for Pause Games; no live deck or game save claimed; exact deck limits retained.',
        'archive_authorization': 'All games and interludes complete; archive only after verified source CLI registration.'}
    save(p, 'LEAD_ACCEPTANCE.json', acceptance)
    evidence_paths += [p / name for name in ['REVIEW.md', 'COVERAGE.md', 'LEAD_ACCEPTANCE.json', 'PAUSE_GAME.json', 'DECK_USED.json', 'TURN_LEDGER.json', 'TURN_EVIDENCE.json']]
    evidence_paths.append(receipt)
evidence_paths.append(P / 'RELATED_GAME_PACKETS.json')
cmd = [sys.executable, str(ROOT / 'Review_Log/review_log.py'), '--root', str(ROOT), 'record', '--video', source['video_basename'], '--reviewer', assignment['reviewer'], '--status', 'full_battle_review_complete', '--scope', f'Whole source: {len(packets)} games, {total_turns} total turns, setup, intervening deck edits and source ending; every game independently checked and root accepted']
for evidence in evidence_paths:
    cmd += ['--evidence', str(evidence)]
cmd += ['--notes', 'Root is sole shared writer. Every game and intervening source phase has a complete first pass and independent acceptance. Exact deck limits retained. External saving pending; no Ladder entry.']
result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
registration = {'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr, 'recorded_utc': datetime.now(timezone.utc).isoformat(), 'source_game_count': len(packets), 'source_total_turn_rows': total_turns, 'source_registration_packet': str(P)}
for p in packets:
    save(p, 'REGISTRATION_RESULT.json', registration)
assert result.returncode == 0, result.stderr
print('Accepted and registered ' + source['video_basename'] + f' ({len(packets)} games, {total_turns} turns)')
