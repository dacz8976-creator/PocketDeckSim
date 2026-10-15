import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

out = Path(__file__).resolve().parent
p = out.parent
def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
previous = read(out/'CHECK_RESULT.json')
freeze = read(p/'REVIEW_PACKET_HASHES.json')
receipt = read(p/'REPAIR_RECEIPT.json')
current = {name: sha(p/name) for name in freeze['review_components']}
assert current == freeze['review_components'] == receipt['new_components']
assert freeze['source_sha256'] == previous['source_sha256']
for name, digest in previous['checked_input_sha256'].items():
    assert sha(out/'rejected_inputs'/name) == digest
changed = [name for name in current if current[name] != previous['checked_input_sha256'][name]]
assert set(changed) == {'REVIEW.md', 'TURN_LEDGER.json', 'TURN_EVIDENCE.json'}
ledger = read(p/'TURN_LEDGER.json')
evidence = read(p/'TURN_EVIDENCE.json')
frames = {x['evidence_id']: x for x in evidence['frames']}
draw = ledger['turns'][6]['draws_and_searches'][1]
assert draw['timestamp_seconds'] == 286 and draw['evidence_ids'] == ['f0286_00']
card = draw['cards_in_reveal_order'][0]
assert card['timestamp_seconds'] == 286 and card['evidence_ids'] == ['f0286_00'] and card['name'] == 'Alolan Grimer'
final = ledger['turns'][10]
assert len(final['plays_in_order']) == 2
play = final['plays_in_order'][1]
assert play['order'] == 2 and play['kind'] == 'energy_attachment'
assert play['energy']['type'] == 'Darkness' and play['energy']['count'] == 1
assert 'Alolan Muk' in play['target']
muk = next(x for x in final['board_after']['owner']['bench_in_position_order'] if x['name'] == 'Alolan Muk')
assert muk['attached_energy'] == {'total': 2, 'by_type': {'Darkness': 1, 'Colorless': 1}}
assert final['board_after']['owner']['energy_zone']['this_turn']['count'] == 0
assert final['board_after']['owner']['energy_zone']['this_turn']['available'] is False
assert final['owner_hand_end']['count'] == 5
native = []
for evidence_id in ['f0286_00', 'f0449_25', 'f0449_50', 'f0449_75', 'f0451_00', 'f0453_00']:
    f = frames[evidence_id]
    path = p/f['full_frame_path']
    assert path.exists() and Image.open(path).size == (1170,2532)
    assert sha(path) == f['image_sha256']
    native.append({'evidence_id': evidence_id, 'source_seconds': f['requested_source_seconds'], 'path': f['full_frame_path'], 'sha256': sha(path), 'native_dimensions': [1170,2532]})
prose = (p/'REVIEW.md').read_text(encoding='utf-8-sig')
assert 'Alolan Grimer search arrival is bound to native 286 s' in prose
assert 'Energy attachment at 449.25 s' in prose
assert 'Muk ends with Darkness 1 and Colorless 1, total 2' in prose
assert current == {name: sha(p/name) for name in current}
result = {
    'schema': 'battle-logs/bounded-independent-acceptance-v1',
    'reviewer': '/root/check_remaining_010003', 'model': 'gpt-6.1-sol', 'reasoning_effort': 'high',
    'checked_utc': datetime.now(timezone.utc).isoformat(),
    'source_video': freeze['source_video'], 'source_sha256': freeze['source_sha256'],
    'accepted': True, 'checked_input_sha256': current, 'primary_freeze_match': True,
    'required_repairs': [],
    'scope': 'Narrow separate correction recheck of R1 and R2 against native evidence, repaired prose/ledger/evidence, and all eight new stable frozen hashes. Earlier bounded findings remain in CHECK_RESULT.json. No second entire-video pass.',
    'previous_check': 'CHECK_RESULT.json',
    'original_rejection_preserved': True,
    'changed_components': changed,
    'native_findings': [
        {'repair_id': 'T7_SEARCH_ARRIVAL_REFERENCE', 'resolved': True, 'finding': 'Alolan Grimer individual arrival and group now both use 286 s and f0286_00. Native 286 retained from prior check shows the added fifth card, correctly separated from the pre-arrival 284 s view.'},
        {'repair_id': 'T11_MISSING_ENERGY_ATTACHMENT', 'resolved': True, 'finding': 'New native 449.25/449.50 shows Darkness orb on Bench Alolan Muk; 449.75 shows resolution. Stable 451/453 shows Darkness 1 plus Colorless 1, total 2, and consumed current Energy Zone. Repaired action 2 follows Ice Pop and precedes Regigigas menu inspection. Hand remains five. No extra attack resolves.'}
    ],
    'selected_native_evidence': native,
    'structural_validation_is_separate': True,
    'fresh_live_readback': False,
    'external_limit': 'Acceptance is local and retains historical exact deck provenance and blocked fresh live access. It does not assert a new external save.',
    'remaining_material_findings': []
}
(out/'CORRECTION_RECHECK.json').write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
print(json.dumps({'accepted': True, 'required_repairs': [], 'primary_freeze_match': True, 'original_rejection_preserved': True, 'changed_components': changed}))
