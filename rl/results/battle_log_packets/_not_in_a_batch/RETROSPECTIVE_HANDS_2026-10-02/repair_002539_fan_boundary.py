"""Correct an ending fan count without moving the next turn's normal draw."""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

B = Path(__file__).resolve().parent
P = B / '20260929_002539000'
snapshot = P / 'before_fan_boundary_repair'
assert not snapshot.exists(), 'Do not repeat this source-specific repair.'
load = lambda path: json.loads(path.read_text(encoding='utf-8-sig'))
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
check = load(B / 'independent_ladder/20260929_002539000/CHECK_RESULT.json')
assert check.get('verdict', check.get('status')) in ['repair_required', 'needs_repair']
submission = load(P / 'SUBMISSION.json')
for record in submission['files']:
    assert sha(Path(record['path'])) == record['sha256'], record['path']
ledger = load(P / 'TURN_LEDGER.json')
row = ledger['turns'][9]
assert row['turn_number'] == 10 and row['opponent_hand_end']['count'] == 3
assert ledger['turns'][10]['hand_at_start']['count'] == 3
old_t11 = json.dumps(ledger['turns'][10], ensure_ascii=False, sort_keys=True)
md = (P / 'REVIEW_SUPPLEMENT.md').read_text(encoding='utf-8')
old_line = next(line for line in md.splitlines() if line.startswith('|10 owner '))
assert 'opponent end fan 3.' in old_line
snapshot.mkdir()
for name in ['SUBMISSION.json', 'TURN_LEDGER.json', 'REVIEW_SUPPLEMENT.md']:
    shutil.copy2(P / name, snapshot / name)
row['opponent_hand_end']['count'] = 2
row['opponent_hand_end']['basis'] = 'Direct native endpoint count of two concealed card backs in F0385.00, F0395.00 and R0396.00; the next normal draw belongs to turn11'
row['opponent_hand_end']['limit_reason'] = 'Faces concealed. The third back appears in the reduced turn11 normal-draw locator near nominal397s, so it is excluded from the turn10 ending count. Exact draw-completion PTS is not measured.'
assert json.dumps(ledger['turns'][10], ensure_ascii=False, sort_keys=True) == old_t11
new_line = old_line.replace('opponent end fan 3.', 'opponent end fan 2 (before turn11 normal draw).')
md = md.replace(old_line, new_line, 1)
md += '\nIndependent boundary correction: turn10 ends with two concealed opponent cards in all three cited native views. Turn11\'s post-normal-draw count of three is separately derived from that endpoint and the retained draw locator. Their identities and exact draw-completion PTS remain unknown.\n'
(P / 'TURN_LEDGER.json').write_text(json.dumps(ledger, ensure_ascii=False, indent=2), encoding='utf-8')
(P / 'REVIEW_SUPPLEMENT.md').write_text(md, encoding='utf-8')
records = [dict(r) for r in submission['files']]
for record in records:
    record['sha256'] = sha(Path(record['path']))
receipt = {'schema': 'source-bound-fan-boundary-repair-v1', 'game_id': P.name,
           'source_sha256': submission['source_sha256'], 'repaired_utc': datetime.now(timezone.utc).isoformat(),
           'original_submission': str(snapshot / 'SUBMISSION.json'),
           'changed_files': ['TURN_LEDGER.json', 'REVIEW_SUPPLEMENT.md'],
           'changed_field': 'turns[9].opponent_hand_end.count:3 to2, with phase provenance and MD mirror',
           'turn11_structured_row_unchanged': True, 'turn11_post_draw_count_preserved': 3,
           'root_inspected_native_ids': ['F0385.00', 'F0395.00'],
           'new_native_frames': 0, 'card_identities_actions_boards_energy_points_outcome_changed': False,
           'independent_acceptance_status': 'requires_same_independent_checker_confirmation',
           'files': records}
(P / 'SUBMISSION_AFTER_FAN_REPAIR.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'changed_files': receipt['changed_files'], 'effective_hashes': len(records), 'turn10_end_fan': 2, 'turn11_after_draw': 3}))
