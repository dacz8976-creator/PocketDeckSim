import hashlib
import json
from pathlib import Path
b=Path(__file__).resolve().parent
paths=list(b.glob('*/QR_DECODE.json'))+list(b.glob('*/QR_DECODE_RECEIPT.json'))+list(b.glob('*/qr_intake/QR_DECODE_*.json'))
out=[]
for p in sorted(paths):
    q=json.loads(p.read_text(encoding='utf-8'))
    key=json.dumps([sorted((c['entity_kind'],c['entity_id'],c['count']) for c in q['cards']),sorted(q['decoded']['energyTypes'])],separators=(',',':'))
    fingerprint=hashlib.sha256(key.encode()).hexdigest()
    entry={'source':q['source_video'],'seconds':q['source_seconds'],'canonical_deck_fingerprint':fingerprint,'QR_receipt':str(p.resolve()),
        'pokemon':[(c['name'],c['entity_id'],c['count']) for c in q['cards'] if c['entity_kind']=='pokemon'],
        'energy':[e['name'] for e in q['decoded']['energy']],'payload_sha256':q['payload_ascii_sha256']}
    out.append(entry)
    print(json.dumps(entry,ensure_ascii=True),flush=True)
(b/'QR_INTAKE_CATALOG.json').write_text(json.dumps({'scope':'Source-bound decoded deck identities; game binding and filmed labels await whole source Sol review',
    'unique_semantic_lists':len(set(x['canonical_deck_fingerprint'] for x in out)),'receipts':out},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
