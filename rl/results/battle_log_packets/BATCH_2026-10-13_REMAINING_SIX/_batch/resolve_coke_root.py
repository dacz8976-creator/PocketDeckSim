import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

packet = Path(__file__).resolve().parent / '20261013_015011000_iOS'
p = packet / 'ROOT_SOURCE_CHECKS.json'
r = json.loads(p.read_text(encoding='utf-8-sig'))
check = json.loads((packet / 'independent_sol/CORRECTION_RECHECK.json').read_text(encoding='utf-8-sig'))
assert check['accepted'] is True and not check['required_repairs']
for name, sha in check['checked_input_sha256'].items():
    assert hashlib.sha256((packet / name).read_bytes()).hexdigest() == sha
for name, observed in [
    ('turn_evidence/t0066.00.jpg', 'Root directly viewed corrected first Research reveal: large Research with no earlier Research in hand. Second Research67, Helmet68 and Pop68.5 already directly checked. Revised packet preserves corrected arrival versus settled-hand distinctions.'),
    ('turn_evidence/t0167.50.jpg', 'Root directly viewed final clear turn3 hand Research2/Helmet/Pop/Glimmora5, both boards and unused Darkness before timeout modal. Revised ledger/evidence use167.5;168.5 explicitly blurred/error.'),
]:
    if not any(c['path'] == name for c in r['checks']):
        r['checks'].append({'path': name, 'sha256': hashlib.sha256((packet / name).read_bytes()).hexdigest(), 'observed': observed})
r['original_findings_preserved'] = r.get('pending_primary_repairs', [])
r['pending_primary_repairs'] = []
r['repair_resolution'] = 'Two independent timestamp findings resolved in revised eight-file freeze; separate checker accepted exact current hashes. Original draft observations and rejected bytes retained.'
r['updated_utc'] = datetime.now(timezone.utc).isoformat()
p.write_text(json.dumps(r, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Resolved root findings for coke')
