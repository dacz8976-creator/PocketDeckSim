"""Apply the independent check's bounded packaging and hand-phase repairs."""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

B = Path(__file__).resolve().parent
P = B / '20260909_023151000'
snapshot = P / 'before_packaging_repair'
assert not snapshot.exists(), 'Do not repeat this source-specific repair.'
load = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
submission = load(P / 'SUBMISSION.json')
for record in submission['submitted_files']:
    assert sha(Path(record['path'])) == record['sha256'], record['path']
hand = load(P / 'HAND_SUPPLEMENT.json')
source = load(P / 'SOURCE_REFERENCE.json')
assert [r['turn_number'] for r in hand['owner_turns']] == [1, 3, 5, 7, 9]
row = hand['owner_turns'][3]
assert row['before_end_hand']['cards_left_to_right'] == ['Helioptile']
assert row['before_end_hand']['evidence_ids'] == ['t0241.50']
snapshot.mkdir()
for name in ['SUBMISSION.json', 'HAND_SUPPLEMENT.json', 'SOURCE_REFERENCE.json']:
    shutil.copy2(P / name, snapshot / name)
row['before_end_evidence_ids'] = ['t0240.00', 't0241.50']
row['before_end_hand']['evidence_ids'] = ['t0240.00']
row['before_end_hand']['basis'] = 'direct visible single Helioptile in unzoomed pre-attack native view at requested 240s; Energy attachment animation is resolving'
row['before_end_hand']['limit_reason'] = 'Exact decoded PTS is unmeasured. The later 241.5s attack-selection overlay partly covers the hand and is secondary phase corroboration.'
row['before_end_candidate_limits'] = {'t0241.50': 'attack-selection overlay partly covers the sole hand card; use unzoomed t0240.00 for the primary count and identity'}
hand['target_rows'] = hand['owner_turns']
hand['target_turn_numbers'] = [1, 3, 5, 7, 9]
hand['capture_status'] = 'complete_with_recording_limits'
source['sha256'] = source['source_sha256']
for name, data in [('HAND_SUPPLEMENT.json', hand), ('SOURCE_REFERENCE.json', source)]:
    (P / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
records = [dict(r) for r in submission['submitted_files']]
for record in records:
    record['sha256'] = sha(Path(record['path']))
receipt = {'schema': 'source-bound-packaging-repair-v1', 'source': submission['source'],
           'source_sha256': submission['source_sha256'], 'repaired_utc': datetime.now(timezone.utc).isoformat(),
           'original_submission': str(snapshot / 'SUBMISSION.json'),
           'reason': 'Three minor packaging and hand-phase repairs requested by the independent Sol checker.',
           'changed_files': ['HAND_SUPPLEMENT.json', 'SOURCE_REFERENCE.json'],
           'root_inspected_native_ids': ['t0240.00', 't0241.50'],
           'new_native_frames': 0, 'card_names_counts_actions_boards_outcome_changed': False,
           'independent_acceptance_status': 'requires_same_independent_checker_confirmation',
           'submitted_files': records}
(P / 'SUBMISSION_AFTER_PACKAGING_REPAIR.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'changed_files': receipt['changed_files'], 'effective_hashes': len(records), 'new_native_frames': 0}))
