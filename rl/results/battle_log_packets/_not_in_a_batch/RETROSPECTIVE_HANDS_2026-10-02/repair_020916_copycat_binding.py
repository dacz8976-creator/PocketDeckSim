"""Bind a concealed Copycat refill count to the independently captured settled fan."""
import copy
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

B = Path(__file__).resolve().parent
P = B / '20260929_020916000'
C = B / 'independent_ladder/20260929_020916000'
snapshot = P / 'before_copycat_binding_repair'
assert not snapshot.exists(), 'Do not repeat this source-specific repair automatically.'
freeze = json.loads((P / 'SUBMISSION_AFTER_ASTRA_REPAIR.json').read_text(encoding='utf-8-sig'))
for name, expected in freeze['file_sha256'].items():
    assert hashlib.sha256((P / name).read_bytes()).hexdigest() == expected, name
added = json.loads((C / 'ADDED_NATIVE_EVIDENCE.json').read_text(encoding='utf-8-sig'))
for file in added['files']:
    assert hashlib.sha256(Path(file['path']).read_bytes()).hexdigest() == file['sha256']
snapshot.mkdir()
changed_names = ['TURN_LEDGER.json', 'REVIEW_SUPPLEMENT.json', 'TURN_EVIDENCE.json', 'REVIEW_SUPPLEMENT.md']
for name in changed_names + ['SUBMISSION_AFTER_ASTRA_REPAIR.json']:
    shutil.copy2(P / name, snapshot / name)
eid = added['evidence_id']
for name, key in [('TURN_LEDGER.json', 'turns'), ('REVIEW_SUPPLEMENT.json', 'rows')]:
    data = json.loads((P / name).read_text(encoding='utf-8-sig'))
    row = data[key][1]
    refill = row['draws_and_searches'][1]
    assert row['turn_number'] == 2 and refill['caused_by'] == 'Copycat'
    assert refill['hand_count_after'] == 5 and len(refill['cards_in_reveal_order']) == 5
    for slot, card in enumerate(refill['cards_in_reveal_order'], 1):
        assert card['name'] is None
        card.update(reveal_position=None, hidden_draw_count_slot=slot, timestamp_seconds=None,
                    evidence_ids=[eid], basis='concealed count placeholder; settled five backs directly visible in IC0090.50',
                    limit_reason='Card identity, physical copy and actual reveal order/time are unobserved; this slot is bookkeeping, not a reveal position.')
    refill.update(timestamp_seconds=None, play_anchor_requested_seconds=79.5,
                  settled_count_measured_pts_seconds=added['measured_pts_seconds'],
                  evidence_ids=['F0079.50', eid],
                  hand_count_basis='Before0 is inferred after Copycat shuffles the prior concealed hand; after5 is directly counted in settled native IC0090.50. F0079.50 is the played Copycat and prior three backs, not five draws.',
                  limit_reason='Concealed identities and actual reveal order/times remain unknown; native90.5117 is a settled post-refill view, not an exact draw-completion time.')
    row['turn_evidence_ids'] = list(dict.fromkeys(row.get('turn_evidence_ids', []) + [eid]))
    (P / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
evidence = json.loads((P / 'TURN_EVIDENCE.json').read_text(encoding='utf-8-sig'))
assert eid not in {f['evidence_id'] for f in evidence['frames']}
files = {f['role']: f for f in added['files']}
frame = {'evidence_id': eid, 'source_video': added['source_video'], 'source_sha256': added['source_sha256'],
         'requested_source_seconds': added['requested_source_seconds'],
         'actual_frame_seconds_if_measured': added['measured_pts_seconds'], 'timestamp_basis': added['timestamp_basis'],
         'full_frame_path': files['full']['path'], 'full_frame_sha256': files['full']['sha256'],
         'native_dimensions': {'width': 1170, 'height': 2532}, 'decode_log': added['decode_log'],
         'role': 'opponent settled Copycat refill count', 'turn_number': 2, 'who_played': 'opponent',
         'selected_for_start_hand': False, 'before_first_play': False,
         'observation': 'Five concealed opponent card backs after Copycat; five owner face cards. No opponent identities or reveal order assigned.',
         'independent_addition_receipt': str(C / 'ADDED_NATIVE_EVIDENCE.json')}
for role in ['top', 'bottom']:
    frame[role + '_crop'] = {'path': files[role]['path'], 'pixel_bounds_x0_y0_x1_y1': files[role]['bounds'],
                            'sha256': files[role]['sha256'], 'parent_sha256': files['full']['sha256'], 'lossless': True}
evidence['frames'].append(frame)
(P / 'TURN_EVIDENCE.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8')
note = '\nIndependent Copycat reference correction: turn 2\'s F0079.50 is the played Copycat and preceding three backs. IC0090.50 (measured PTS90.5117) directly shows five concealed backs after the refill. Individual identities, physical copies and reveal order/times remain unknown; five placeholder entries count hidden draws only. The post-shuffle zero is a card-effect inference.\n'
with (P / 'REVIEW_SUPPLEMENT.md').open('a', encoding='utf-8') as file:
    file.write(note)
receipt = {'schema': 'retrospective-copycat-reference-repair-v1', 'source': added['source_video'],
           'repaired_utc': datetime.now(timezone.utc).isoformat(), 'preceding_effective_submission': str(snapshot / 'SUBMISSION_AFTER_ASTRA_REPAIR.json'),
           'changed_files': changed_names, 'new_independent_native_frames': 1, 'primary_native_frames_unchanged': 85,
           'added_native_receipt': str(C / 'ADDED_NATIVE_EVIDENCE.json'), 'cards_counts_actions_boards_outcome_changed': False,
           'file_sha256': {name: hashlib.sha256((P / name).read_bytes()).hexdigest() for name in freeze['file_sha256']},
           'independent_acceptance_status': 'same full independent Sol checker confirmation required'}
(P / 'SUBMISSION_AFTER_COPYCAT_REPAIR.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
print(json.dumps({'changed_files': changed_names, 'added_native': eid, 'count': 5, 'identities_and_reveal_order': 'unknown'}))
