"""Apply three frozen independent corrections, including dependent promotion boundary refs."""
import copy
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

B = Path(__file__).resolve().parent
P = B / '20261005_034953000_iOS'
check = json.loads((P / 'independent_sol/CHECK_RESULT.json').read_text(encoding='utf-8'))
assert check['accepted'] is False
assert {r['id'] for r in check['required_repairs']} == {'R1', 'R2', 'R3'}
backup = P / 'original_before_R1_R3'
assert not backup.exists() and not (P / 'LEAD_ACCEPTANCE.json').exists()
for name, digest in {**check['checked_input_sha256'], **check['supplemental_checked_input_sha256']}.items():
    assert hashlib.sha256((P / name).read_bytes()).hexdigest() == digest, name
backup.mkdir()
for name in check['checked_input_sha256']:
    shutil.copy2(P / name, backup / Path(name).name)
ledger = json.loads((P / 'TURN_LEDGER.json').read_text(encoding='utf-8'))
evidence = json.loads((P / 'TURN_EVIDENCE.json').read_text(encoding='utf-8'))
changes = []

for index, start, later, eid, later_id, state in [
    (1, 83, 83.8, 'f0083_00', 'f0083_80', 'generating'),
    (5, 149.5, 150.5, 'f0149_50', 'f0150_50', 'empty'),
    (9, 223, 223.5, 'f0223_00', 'f0223_50', 'generating'),
    (13, 333, 334, 'f0333_00', 'f0334_00', 'empty'),
    (15, 388, 389, 'f0388_00', 'f0389_00', 'empty')]:
    zone = ledger['turns'][index]['board_at_start']['owner']['energy_zone']
    before = copy.deepcopy(zone['this_turn'])
    assert before == {'type': 'Metal', 'count': 1, 'available': True}
    zone['this_turn'] = {'type': None, 'count': None, 'available': None} if state == 'generating' else {'type': 'none', 'count': 0, 'available': False}
    zone['current_status'] = 'generation_flare_settled_state_unverified' if state == 'generating' else 'observed_absent_at_selected_boundary'
    zone['basis'] = 'Large current orb is in a bright generation flare; settled type/count/availability cannot be established at the selected frame. Small next Metal preview is separate.' if state == 'generating' else 'Large current Energy slot visibly empty at selected intact-hand frame; small next Metal preview remains separate.'
    zone['limit_reason'] = 'Do not backfill the earlier selected boundary from later generated Energy.' if state == 'generating' else None
    zone['energy_generation_transition'] = {'source_local_window_seconds': [start, later], 'later_this_turn': before, 'evidence_ids': [eid, later_id], 'basis': 'Later retained frame supports generated Metal; exact generation instant not measured.'}
    changes.append({'repair_id': 'R1', 'turn': index + 1, 'selected_seconds': start, 'before': before, 'after': zone['this_turn'], 'later_generated_seconds': later})

r3 = ledger['turns'][2]
evolution, attachment, research, end = r3['plays_in_order']
assert research['card_name'] == "Professor's Research" and attachment['kind'] == 'energy_attachment'
research['order'] = 2
attachment.update(order=3, timestamp_seconds=108, input_interval_seconds=None,
                  displayed_action_window_seconds=[107, 109], resolution_seconds=109,
                  timestamp_basis='Current Metal is still available at107; first retained transfer108; attached on right Fraxure109. Opponent finger input is not exposed.',
                  evidence_ids=['f0107_00', 'f0108_00', 'f0109_00'],
                  limit_reason='Remote touch instant unknown; timestamps bound displayed transfer and resolution.')
r3['plays_in_order'] = [evolution, research, attachment, end]
r3['draws_and_searches'][1]['linked_play_order'] = 2
changes.append({'repair_id': 'R2', 'turn': 3, 'order': ['Fraxure evolution99', 'Research102 and hidden draws104', 'Metal transfer108/resolved109', 'End Turn109'], 'opponent_touch_claimed': False})

first = ledger['turns'][1]['plays_in_order'][2]
first.update(timestamp_seconds=88, input_interval_seconds=[87, 88],
             timestamp_basis='Native87 is pre-action; first retained transfer88. Selection is bounded87-88, not a measured touch instant.',
             evidence_ids=['f0087_00', 'f0088_00'])
promotion = ledger['turns'][10]['plays_in_order'][2]
promotion.update(timestamp_seconds=262, input_interval_seconds=[261, 262],
                 timestamp_basis='Native261 has empty Active and Melmetal on Bench. Promotion animation starts by262, reveal263 and placement264.',
                 evidence_ids=['f0261_00', 'f0262_00', 'f0263_00', 'f0264_00', 'f0266_00'],
                 nested_events_in_order=[{'kind': 'promotion_reveal', 'timestamp_seconds': 263, 'evidence_ids': ['f0263_00']}, {'kind': 'promotion_placed', 'timestamp_seconds': 264, 'evidence_ids': ['f0264_00']}, {'kind': 'settled_post_promotion_board', 'timestamp_seconds': 266, 'evidence_ids': ['f0266_00']}])
# The worker's stated post-promotion board was right in content but cited a pre-promotion frame.
after = ledger['turns'][10]['board_after']
assert after['owner']['active']['name'] == 'Melmetal ex' and after['source_seconds'] == 261
def rebind(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if key == 'evidence_ids' and item == ['f0261_00']:
                value[key] = ['f0266_00']
            else:
                rebind(item)
    elif isinstance(value, list):
        for item in value:
            rebind(item)
rebind(after)
after['source_seconds'] = 266
after['phase'] = 'Turn11 knockout and compulsory promotion resolved; settled boundary266 after next-turn label12 at265, before owner normal draw267.'
after['turn_number_displayed'] = None
after['turn_number_displayed_limit'] = 'No Current turn label at settled266; native265 separately displays next Current turn12, not concluded turn11.'
ledger['turns'][10]['timing'].update(end_seconds=265, end_after_resolution_seconds=266)
ledger['turns'][11]['timing']['start_seconds'] = 265
changes.append({'repair_id': 'R3', 'owner_attachment_selection_bound': [87, 88], 'promotion_selection_bound': [261, 262], 'promotion_reveal': 263, 'placed': 264, 'settled_board_reference': 266, 'next_turn_label': 12, 'next_turn_label_seconds': 265, 'board_content_changed': False})
observations = {
    'f0100_00': 'Fraxure evolution animation, not a Metal attachment.',
    'f0104_00': 'Research discard top and four opponent backs; current Metal remains available, right Fraxure unattached.',
    'f0107_00': 'Current Metal still available before transfer to right Fraxure.',
    'f0108_00': 'First retained Metal transfer to right Fraxure after Research.',
    'f0109_00': 'Right Fraxure has one Metal after Research and subsequent attachment.',
    'f0087_00': 'Pre-attachment owner state; current Metal available, Magnemite unattached.',
    'f0088_00': 'Owner Metal transfer toward Magnemite after pre-action87.',
    'f0261_00': 'After Magneton removal, owner Active empty; Melmetal still middle Bench, before forced promotion.',
    'f0262_00': 'Forced Melmetal promotion animation begins after pre-action261.',
    'f0263_00': 'Melmetal promotion reveal.',
    'f0264_00': 'Melmetal placed Active; animation suppresses some overlay icons.',
    'f0265_00': 'Readable Current turn12 transition after turn11 promotion; do not label this as displayed11.',
    'f0266_00': 'Settled post-promotion boundary before normal draw267: Melmetal Active170 with Steel Apron and three Metal; Doublade left90, middle/right empty; opponent Haxorus50, Happiny30/Munchlax50/Haxorus150 and 1-0 points.'}
for frame in evidence['frames']:
    if frame['evidence_id'] in observations:
        frame['observation'] = observations[frame['evidence_id']]

def save(name, value):
    (P / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
save('TURN_LEDGER.json', ledger)
save('TURN_EVIDENCE.json', evidence)
review = (P / 'REVIEW.md').read_text(encoding='utf-8')
review = review.replace('Attach one Metal Energy from Energy Zone (87s)', 'Attach one Metal Energy from Energy Zone (selection87-88, transfer88s)')
old = '2. energy_attachment -> opponent Bench right Fraxure: Attach one Metal Energy from Energy Zone (100s); 3. Professor\'s Research -> deck: Draw two concealed cards (102s)'
new = '2. Professor\'s Research -> deck: Draw two concealed cards (102s, fan four by104); 3. energy_attachment -> opponent Bench right Fraxure: Metal still available107, transfer108, attached109'
assert old in review
review = review.replace(old, new).replace('| 11 | opponent | 236-261 |', '| 11 | opponent | 236-265 |').replace('| 12 | owner | 262-295 |', '| 12 | owner | 265-295 |')
review = review.replace('no retreat payment (261s)', 'no retreat payment (selection261-262, reveal263, placed264s; settled boundary266s)')
review += '\nIndependent correction: intact selected hands83 and223 show generation flares with settled current Energy unverified. Selected149.5,333 and388 show an empty current slot. Next Metal remains separate, with later generated evidence83.8,150.5,223.5,334 and389. Opponent turn3 is evolution, Research, then Metal transfer. The turn11 settled post-promotion board now cites266, since261 still has an empty Active and Melmetal on Bench; native265 displays the next turn12. Original rejected inputs are retained in original_before_R1_R3.\n'
(P / 'REVIEW.md').write_text(review, encoding='utf-8')
coverage = (P / 'COVERAGE.md').read_text(encoding='utf-8').replace('236-261', '236-265').replace('262-295', '265-295')
coverage += '\nThe independent R1-R3 corrections use existing retained native evidence only. Selected intact hands remain unchanged; Energy generation, ordinary turn3 order, transfer/promotion input bounds and dependent settled board266 references are corrected together. Next-turn label12 at265 is separate from concluded turn11. No new source phase or terminal outcome is claimed.\n'
(P / 'COVERAGE.md').write_text(coverage, encoding='utf-8')
save('INDEPENDENT_CORRECTIONS.json', {'repaired_utc': datetime.now(timezone.utc).isoformat(), 'lead': '/root', 'source_sha256': check['source_sha256'], 'initial_independent_report': 'independent_sol/CHECK_RESULT.json', 'original_input_sha256': check['checked_input_sha256'], 'original_input_backup': backup.name, 'required_repairs_applied': ['R1', 'R2', 'R3'], 'changes': changes, 'retained_frame_files_changed': False, 'independent_recheck_required': True})
result = subprocess.run([sys.executable, str(B / 'validate_packet.py'), str(P)], capture_output=True, text=True, encoding='utf-8', check=True)
structure = json.loads(result.stdout)
assert structure['structural_pass'] is True
save('ROOT_REPAIR_STRUCTURE_CHECK.json', structure)
print(json.dumps({'required_repairs_applied': ['R1', 'R2', 'R3'], 'selected_hands_preserved': True, 'structural_pass': True, 'independent_recheck_required': True}))
