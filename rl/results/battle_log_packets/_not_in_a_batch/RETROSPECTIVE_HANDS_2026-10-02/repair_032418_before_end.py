"""Correct one hand-phase reference while retaining the producer's frozen packet."""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

B = Path(__file__).resolve().parent
P = B / '20260909_032418000'
snapshot = P / 'before_hand_phase_repair'
assert not snapshot.exists(), 'This source-specific repair is not repeatable automatically.'
submission = json.loads((P / 'SUBMISSION.json').read_text(encoding='utf-8-sig'))
for record in submission['submitted_files']:
    assert hashlib.sha256(Path(record['path']).read_bytes()).hexdigest() == record['sha256']
hand = json.loads((P / 'HAND_SUPPLEMENT.json').read_text(encoding='utf-8-sig'))
row = hand['owner_turns'][4]
assert row['turn_number'] == 9 and row['before_end_hand']['count'] == 0
assert row['before_end_hand']['evidence_ids'] == ['t0314.00']
snapshot.mkdir()
for name in ['HAND_SUPPLEMENT.json', 'SUBMISSION.json']:
    shutil.copy2(P / name, snapshot / name)
row['before_end_evidence_ids'] = ['r0302.00', 't0305.00']
row['before_end_hand']['evidence_ids'] = ['r0302.00']
row['before_end_hand']['basis'] = 'direct visible empty hand in unzoomed pre-attack native frame at requested302s; Energy attachment is resolving'
row['after_attack_hand_corroboration'] = {'count': 0, 'cards_left_to_right': [], 'evidence_ids': ['t0314.00'],
                                         'basis': 'same empty hand after attack; this does not establish the before-attack phase'}
row['before_end_candidate_limits'] = {'t0305.00': 'pre-attack card/attack selection overlay; r0302.00 supplies the unzoomed empty hand'}
(P / 'HAND_SUPPLEMENT.json').write_text(json.dumps(hand, ensure_ascii=False, indent=2), encoding='utf-8')
records = [dict(record) for record in submission['submitted_files']]
for record in records:
    record['sha256'] = hashlib.sha256(Path(record['path']).read_bytes()).hexdigest()
repair = {'schema': 'source-bound-hand-phase-repair-v1', 'source': '20260909_032418000_iOS.MP4',
          'repaired_utc': datetime.now(timezone.utc).isoformat(), 'original_submission': str(snapshot / 'SUBMISSION.json'),
          'reason': 'Independent Sol noted a post-attack reference in the before-end hand field.',
          'changed_files': ['HAND_SUPPLEMENT.json'], 'new_native_frames': 0,
          'root_inspected_native_ids': ['r0300.00', 'r0302.00', 't0305.00'],
          'observations': '300s is a coin overlay.302s is an unzoomed empty hand during Energy attachment before attack.305s is attack selection with an overlay.314s remains after-attack corroboration.',
          'card_names_counts_actions_boards_outcome_changed': False,
          'independent_acceptance_status': 'repair_requires_same_independent_checker_confirmation',
          'submitted_files': records}
(P / 'SUBMISSION_AFTER_PHASE_REPAIR.json').write_text(json.dumps(repair, indent=2), encoding='utf-8')
print(json.dumps({'changed_files': repair['changed_files'], 'new_native_frames': 0, 'turn': 9, 'pre_attack_hand_count': 0}))
