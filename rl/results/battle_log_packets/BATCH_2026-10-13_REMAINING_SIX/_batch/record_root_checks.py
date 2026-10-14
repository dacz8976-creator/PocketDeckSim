import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('notes_file')
args = parser.parse_args()
B = Path(__file__).resolve().parent
notes = json.loads((B / args.notes_file).read_text(encoding='utf-8-sig'))
p = B / notes['packet']
assert p.parent == B
s = json.loads((p / 'SOURCE.json').read_text(encoding='utf-8-sig'))
target = p / 'ROOT_SOURCE_CHECKS.json'
r = json.loads(target.read_text(encoding='utf-8-sig')) if target.exists() else {'lead':'/root','source_sha256':s['sha256'],'full_second_pass':False,'checks':[],'pending_primary_repairs':[]}
assert r['source_sha256'] == s['sha256']
for n in notes['checks']:
    assert not any(c['path'] == n['path'] for c in r['checks']), 'Already recorded: ' + n['path']
    f = p / n['path']
    assert f.resolve().is_relative_to(p.resolve())
    r['checks'].append({**n,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
if 'pending_primary_repairs' in notes: r['pending_primary_repairs'] = notes['pending_primary_repairs']
r['updated_utc'] = datetime.now(timezone.utc).isoformat()
target.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Recorded direct source observations for '+notes['packet'])
