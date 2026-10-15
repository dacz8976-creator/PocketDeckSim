"""Apply Astra's two identical provenance wording corrections without changing facts."""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

B = Path(__file__).resolve().parent
P = B / '20260929_020916000'
snapshot = P / 'before_astra_wording_repair'
assert not snapshot.exists(), 'Do not repeat this source-specific repair automatically.'
submission = json.loads((P / 'SUBMISSION.json').read_text(encoding='utf-8-sig'))
for name, expected in submission['file_sha256'].items():
    assert hashlib.sha256((P / name).read_bytes()).hexdigest() == expected, name
snapshot.mkdir()
for name in ['TURN_LEDGER.json', 'REVIEW_SUPPLEMENT.json', 'SUBMISSION.json']:
    shutil.copy2(P / name, snapshot / name)
replacement = ('derived paid retreat: direct two-Fire pre-switch state at 414.008 PTS and zero-Fire '
               'benched endpoint at 418.010 PTS plus printed retreat cost 2; native switch animation '
               'at 415.008-417.010 PTS; selection/payment touch hidden')
changed = []
for name, key in [('TURN_LEDGER.json', 'turns'), ('REVIEW_SUPPLEMENT.json', 'rows')]:
    data = json.loads((P / name).read_text(encoding='utf-8-sig'))
    row = data[key][7]
    assert row['turn_number'] == 8
    play = row['plays_in_order'][3]
    assert 'Fire2input414' in play['basis']
    changed.append({'file': name, 'json_path': f'$.{key}[7].plays_in_order[3].basis', 'old': play['basis'], 'new': replacement})
    play['basis'] = replacement
    (P / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
effective = {name: hashlib.sha256((P / name).read_bytes()).hexdigest() for name in submission['file_sha256']}
receipt = {'schema': 'retrospective-astra-wording-repair-v1', 'source': '20260929_020916000_iOS.MP4',
           'repaired_utc': datetime.now(timezone.utc).isoformat(), 'original_submission': str(snapshot / 'SUBMISSION.json'),
           'astra_check': str(B / 'astra_checks/20260929_020916000/ASTRA_CHECK.json'),
           'changed_fields': changed, 'source_facts_actions_counts_boards_outcome_changed': False,
           'new_native_frames': 0, 'file_sha256': effective,
           'independent_acceptance_status': 'different Sol full check still required'}
(P / 'SUBMISSION_AFTER_ASTRA_REPAIR.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
print(json.dumps({'changed_fields': len(changed), 'facts_changed': False, 'new_native_frames': 0}))
