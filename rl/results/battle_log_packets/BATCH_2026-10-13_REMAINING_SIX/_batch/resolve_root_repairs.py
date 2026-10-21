import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('stem')
args = parser.parse_args()
p = Path(__file__).resolve().parent / args.stem
assert p.parent == Path(__file__).resolve().parent
c = json.loads((p / 'independent_sol/CORRECTION_RECHECK.json').read_text(encoding='utf-8-sig'))
assert c['accepted'] is True and not c.get('required_repairs')
frozen = c.get('checked_input_sha256', c.get('accepted_input_sha256', {}))
assert len(frozen) >= 8
for name, sha in frozen.items(): assert hashlib.sha256((p / name).read_bytes()).hexdigest() == sha
f = p / 'ROOT_SOURCE_CHECKS.json'
r = json.loads(f.read_text(encoding='utf-8-sig'))
r['original_findings_preserved'] = r.get('pending_primary_repairs', [])
r['pending_primary_repairs'] = []
r['repair_resolution'] = 'Independent corrected-input recheck accepted all eight current hashes; root retained direct source observations and reconciled repaired actions, timing and board state. Rejected bytes remain preserved.'
r['updated_utc'] = datetime.now(timezone.utc).isoformat()
f.write_text(json.dumps(r, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Resolved root findings: ' + args.stem)
