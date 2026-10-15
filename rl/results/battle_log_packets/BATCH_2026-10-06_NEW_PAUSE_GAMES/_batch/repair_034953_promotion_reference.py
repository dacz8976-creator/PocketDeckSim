"""Complete the remaining promotion reference in the frozen R3 repair."""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

B = Path(__file__).resolve().parent
P = B / '20261005_034953000_iOS'
receipt = P / 'independent_sol/CORRECTION_RECHECK.json'
check = json.loads(receipt.read_text(encoding='utf-8'))
assert check['accepted'] is False and not (P / 'LEAD_ACCEPTANCE.json').exists()
for name, digest in check.get('checked_input_sha256', {}).items():
    assert hashlib.sha256((P / name).read_bytes()).hexdigest() == digest, name
prior = P / 'independent_sol/CORRECTION_RECHECK.before_promotion_dependency.json'
assert not prior.exists()
shutil.copy2(receipt, prior)
shutil.copy2(P / 'TURN_LEDGER.json', P / 'TURN_LEDGER.before_promotion_dependency.json')
ledger = json.loads((P / 'TURN_LEDGER.json').read_text(encoding='utf-8'))
event = ledger['turns'][10]['automatic_events_in_order'][2]
assert event['kind'] == 'promotion' and event['evidence_ids'] == ['f0261_00']
event.update(evidence_ids=['f0261_00', 'f0262_00', 'f0263_00', 'f0264_00', 'f0266_00'], source_local_window_seconds=[261,266], basis='261 is the empty-Active pre-promotion bound.262 animation,263 reveal,264 placement,266 settled board establish the Melmetal promotion.')
(P / 'TURN_LEDGER.json').write_text(json.dumps(ledger, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
record = {'repair_id':'R3', 'dependency':'turn11 automatic promotion event reference', 'applied_by':'/root', 'applied_utc':datetime.now(timezone.utc).isoformat(), 'previous_recheck':str(prior), 'native_evidence_reused':True, 'independent_recheck_required':True}
(P / 'PROMOTION_REFERENCE_CORRECTION.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print('Corrected sole remaining automatic promotion reference; independent recheck required')
