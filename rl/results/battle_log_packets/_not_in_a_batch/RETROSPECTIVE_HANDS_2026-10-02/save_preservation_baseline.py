import hashlib, json
from pathlib import Path

BATCH = Path(__file__).resolve().parent
target = BATCH/'PRESERVATION_BASELINE.json'
if target.exists():
    raise SystemExit('Baseline already exists; preserve it.')
data = json.loads((BATCH/'EVIDENCE_AVAILABILITY.json').read_text(encoding='utf-8'))
out=[]
for game in data:
    folder = Path(game['accepted_review']).parent
    for name in ['REVIEW.md','COVERAGE.md','SOURCE.json','SOURCE_IDENTITY.json','LEAD_ACCEPTANCE.json','SUMMARY.json','EXTERNAL_LOG_RECEIPT.json']:
        path=folder/name
        if path.exists():
            out.append({'source':game['source'],'path':str(path),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
target.write_text(json.dumps(out,indent=2),encoding='utf-8')
print('Preserved accepted packet identities:',len(out))
