import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('stem')
parser.add_argument('--lead-evidence', nargs='+', required=True)
args = parser.parse_args()
packet = Path(__file__).resolve().parent / args.stem
source = json.loads((packet / 'SOURCE.json').read_text(encoding='utf-8-sig'))
verification = json.loads((packet / 'independent_sol/VERIFICATION.json').read_text(encoding='utf-8-sig'))
assert verification['decision'] == 'ACCEPT' and not verification['required_changes']
assert verification['source_sha256'] == source['sha256']
hashes = verification['primary_files_read_and_reconciled']
assert all(name in hashes for name in ['REVIEW.md', 'COVERAGE.md', 'FINDINGS.json'])
for name, digest in hashes.items():
    assert hashlib.sha256((packet / name).read_bytes()).hexdigest() == digest, name
assert all((packet / name).is_file() for name in args.lead_evidence)
acceptance = {
    'accepted': True,
    'decision': 'accepted_full_battle_review',
    'accepted_at_utc': datetime.now(timezone.utc).isoformat(),
    'lead': '/root',
    'source_filename': source['video_basename'],
    'source_sha256': source['sha256'],
    'source_bytes': source['bytes'],
    'duration_seconds': source['duration_seconds'],
    'first_pass_model': 'gpt-6-sol',
    'first_pass_reasoning_effort': 'high',
    'independent_model': verification.get('model', 'gpt-6-sol'),
    'independent_reasoning_effort': verification.get('reasoning_effort', 'high'),
    'primary_files_read_and_checked_by_lead': list(hashes),
    'independent_verification': 'independent_sol/VERIFICATION.json',
    'verified_primary_hashes': hashes,
    'lead_direct_visual_checks': args.lead_evidence,
    'full_source_and_turn_coverage_accepted': True,
    'classification_and_outcome_reconciled': True,
    'source_limits_preserved': True,
    'outcome': verification['outcome'],
    'external_log_routing': 'Computer battle excluded from Ladder and Pause Games',
    'archive_identity_and_registration': 'Required next; acceptance alone does not claim movement'
}
(packet / 'LEAD_ACCEPTANCE.json').write_text(json.dumps(acceptance, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'accepted': True, 'source': source['video_basename'], 'outcome': acceptance['outcome']}))
