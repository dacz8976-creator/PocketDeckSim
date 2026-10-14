"""Root-only reconciliation/registration; factual acceptance remains source-based."""
import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / 'Recording_QA/BATCH_2026-10-14_NEW_LADDER_FOUR'
CONFIG = {
    '20261014_142546000_iOS': {
        'observations': [
            ('native/t0010.0.jpg', 'Deck 12 visibly selected with Spinarak/Ariados grass core.'),
            ('native/t0227.0.jpg', 'Owner turn banner shows combined turn 7; first player own T4. Opponent has zero points.'),
            ('native/t0278.0.jpg', 'Whimsicott ex Active before first Grass Knot; opponent zero points, owner one point, Mega Sharpedo ex160 remaining HP.'),
            ('native/t0299.8.jpg', 'Victory versus まいちゃん; went first;7 turns;3-0;220 damage;Whimsicott ex Card of the Game.'),
        ],
        'section': 'd12', 'note_prefix': '1st | Whimsicott ex T4 | opp 0 pts',
        'opponent_deck': 'Mega Sharpedo ex / Magikarp / Mantyke',
        'note': '1st | Whimsicott ex T4 | opp 0 pts | vs まいちゃん | 2026-10-14 09:25:46 CDT | 20261014_142546000_iOS.MP4 | Victory 3-0 at 04:59.8; Grass Knot160 KOs Mega Sharpedo ex.',
        'clarification': 'The primary REVIEW.md has a nonmaterial clock typo: owner T2 interval ends at02:21 (141s), and opponent T2 begins at02:21, not02:41. COVERAGE.md source-second intervals are correct. Main attack ownT4/global7, points, opponent, result and mode are unaffected.',
    },
}

def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def save_new(path, data):
    if path.exists():
        raise RuntimeError('Existing receipt: ' + str(path))
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

p = argparse.ArgumentParser()
p.add_argument('packet', choices=CONFIG)
a = p.parse_args()
packet = BATCH / a.packet
c = CONFIG[a.packet]
source = load(packet / 'SOURCE.json')
summary = load(packet / 'SUMMARY.json')
manifest_path = packet / 'REVIEW_PACKET_HASHES.json'
manifest = load(manifest_path)
check_path = packet / 'independent_sol/CHECK_RESULT.json'
check = load(check_path)
assert check['accepted'] is True
assert check['source_filename'] == source['video_basename'] == summary['source_filename']
assert check['source_sha256'] == source['sha256'] == summary['source_sha256']
assert check['frozen_manifest_sha256'] == digest(manifest_path)
assert check['frozen_files_match'] is True and check['primary_unchanged'] is True
assert summary['battle_complete'] is True and summary['match_count'] == 1
assert summary['mode']['auto_option_seen'] is False
assert summary['exact_three_item_note_prefix'] == c['note_prefix']
for rel, sha in manifest['files'].items():
    target = (packet / rel).resolve()
    assert target.is_relative_to(packet.resolve()) and digest(target) == sha, rel
now = datetime.now(timezone.utc).isoformat()
save_new(packet / 'SOURCE_CHECKS.json', {
    'lead': '/root', 'checked_utc': now, 'source_filename': source['video_basename'], 'source_sha256': source['sha256'],
    'observations': [{'path': rel, 'sha256': digest(packet/rel), 'directly_viewed_by_root': True, 'finding': finding} for rel, finding in c['observations']],
    'coverage_reconciliation': 'Root read all turn/phase coverage and complete prose timeline; independent source checker sampled ordinary turns and decisive/source identity facts.',
})
clarification = packet / 'LEAD_CLARIFICATION.md'
assert not clarification.exists()
clarification.write_text('# Lead clarification\n\n' + c['clarification'] + '\n\nOriginal primary evidence remains frozen. This addendum and LEAD_ACCEPTANCE.json record the current accepted account.\n', encoding='utf-8')
save_new(packet / 'LEAD_ACCEPTANCE.json', {
    'accepted': True, 'decision': 'accepted_full_battle_review', 'lead': '/root', 'accepted_utc': now,
    'source_video': source['video_basename'], 'source_sha256': source['sha256'],
    'source_game_count': 1, 'all_source_games_accepted': True, 'battle_complete': True, 'archive_eligible': True,
    'scope': 'One complete source: setup, every recorded turn, terminal result; Ladder note first/second, main attacker own first attack turn and opponent points independently verified.',
    'independent_acceptance': str(check_path), 'independent_acceptance_sha256': digest(check_path),
    'independent_model_configuration': 'gpt-6.1-sol/high; fresh compact source checker',
    'accepted_input_sha256': manifest['files'], 'frozen_manifest_sha256': digest(manifest_path),
    'root_checks': 'SOURCE_CHECKS.json', 'clarification': c['clarification'],
})
save_new(packet / 'LADDER_ENTRY.json', {
    'source_filename': source['video_basename'], 'source_sha256': source['sha256'], 'section': c['section'],
    'opponent': summary['opponent_identifier'], 'opponent_deck': c['opponent_deck'], 'result': summary['outcome'],
    'note': c['note'], 'note_prefix': c['note_prefix'], 'match_creation_utc': source['source_creation_utc'],
    'artifact': 'https://claude.ai/artifact/GHSfGSCzNiWNj8SFPXV3R1', 'status': 'ready_for_live_save',
})
cmd = [sys.executable, '-X', 'utf8', str(ROOT / 'Review_Log/review_log.py'), 'record', '--video', source['video_basename'],
       '--reviewer', summary['reviewer'], '--status', 'full_battle_review_complete',
       '--scope', 'Whole one-game ladder source; all7turns and terminal victory; independent note-field/source checks and root acceptance',
       '--notes', 'Ladder log ready; first, Whimsicott ex ownT4/global7, opp0 before; win3-0. Primary clock typo corrected by frozen-source addendum. External save/readback remains separate.',
       '--recording-time', source['source_creation_utc']]
for name in ['SOURCE.json', 'REVIEW.md', 'COVERAGE.md', 'SUMMARY.json', 'UNCERTAINTIES.json', 'REVIEW_PACKET_HASHES.json', 'SOURCE_CHECKS.json', 'LEAD_CLARIFICATION.md', 'LEAD_ACCEPTANCE.json', 'LADDER_ENTRY.json', 'independent_sol/CHECK_RESULT.json']:
    cmd.extend(['--evidence', str(packet/name)])
r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
save_new(packet / 'REGISTRATION_RESULT.json', {'exit_code': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr, 'registered_utc': datetime.now(timezone.utc).isoformat()})
print(json.dumps({'packet': a.packet, 'exit_code': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr}, ensure_ascii=False), flush=True)
raise SystemExit(r.returncode)
