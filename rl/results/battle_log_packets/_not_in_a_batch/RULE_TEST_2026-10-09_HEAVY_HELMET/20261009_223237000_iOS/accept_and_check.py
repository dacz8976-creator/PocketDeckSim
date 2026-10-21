import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

packet = Path(__file__).resolve().parent
root = packet.parents[2]
video = '20261009_223237000_iOS.MP4'
source = json.loads((packet / 'SOURCE.json').read_text(encoding='utf-8-sig'))
verification = json.loads((packet / 'independent_sol/VERIFICATION.json').read_text(encoding='utf-8-sig'))
assert verification.get('decision', '').upper() == 'ACCEPT', verification
assert verification.get('source_sha256') == source['sha256']
for name, accepted_hash in verification['primary_files_read_and_reconciled'].items():
    assert hashlib.sha256((packet / name).read_bytes()).hexdigest() == accepted_hash, name
for name in ['REVIEW.md', 'COVERAGE.md', 'FINDINGS.json', 'independent_sol/VERIFICATION.md']:
    assert (packet / name).is_file(), name
    if name.endswith('.md'):
        assert '\u2014' not in (packet / name).read_text(encoding='utf-8-sig'), name

acceptance = {
    'accepted': True,
    'accepted_utc': datetime.now(timezone.utc).isoformat(),
    'lead_reviewer': 'root-hitback-heavyhelmet-20261009',
    'source_video': video,
    'source_sha256': source['sha256'],
    'completion_status': 'full_battle_review_complete',
    'scope': 'Entire 308.721667-second computer rules-test battle: setup, all 15 turns, positive control, primary hit-back test, later repeats and terminal result',
    'coverage_checked': True,
    'first_pass': {'reviewer': '/root/helmet_full_review', 'model': 'gpt-6.1-sol', 'reasoning_effort': 'high'},
    'independent_review': {'reviewer': '/root/helmet_independent', 'model': 'gpt-6.1-sol', 'reasoning_effort': 'high', 'decision': 'ACCEPT', 'scope': 'Bounded independent source checks and full-packet reconciliation'},
    'lead_direct_source_checks': ['frames/overview_042.jpg', 'frames/overview_043.jpg', 'frames/overview_044.jpg', 'independent_sol/exact_77.5s.jpg', 'independent_sol/exact_185s.jpg', 'independent_sol/exact_190s.jpg', 'wailmer_cost_native.jpg', 'dense/sec_309.jpg'],
    'lead_notes': 'Same Helmet stays attached to retreat-3 Wailmer. Normal attack control100 to90 and hit-back90 to80 establish10 damage in both. Target80 to20 confirms Wave Splash60. Three Water attack cost confirmed by native Water silhouettes. Three Wave Splash attacks and two Wondrous Waves attacks sum to displayed380. Terminal Victory,15 turns,3-0 independently checked. Computer routing and Auto OFF during primary test qualified. Other defensive/return cards and hidden information remain untested.',
    'remaining_coverage_gaps': [],
    'unverified_material_claims': [],
    'ladder_eligible': False,
    'pause_games_eligible': False,
    'simulator_changes_authorized': False,
    'accepted_evidence': ['SOURCE.json', 'REVIEW.md', 'COVERAGE.md', 'FINDINGS.json', 'independent_sol/VERIFICATION.md', 'independent_sol/VERIFICATION.json', 'LEAD_ACCEPTANCE.json'],
}
(packet / 'LEAD_ACCEPTANCE.json').write_text(json.dumps(acceptance, indent=2) + '\n', encoding='utf-8')
source['classification'] = 'owner-designated computer rules-test battle; Solo menu, AI label and visible Auto control'
(packet / 'SOURCE.json').write_text(json.dumps(source, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'accepted': True, 'source_sha256': source['sha256'], 'turns': 15, 'result': '3-0', 'damage': 380}))
