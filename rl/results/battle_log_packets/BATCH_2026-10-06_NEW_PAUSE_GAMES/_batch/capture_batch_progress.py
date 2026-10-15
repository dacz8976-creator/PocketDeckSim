"""Report the actual persisted state without inferring review from intake."""
import json
from datetime import datetime, timezone
from pathlib import Path
b=Path(__file__).resolve().parent
selected=json.loads((b/'OWNER_CONTEXT.json').read_text(encoding='utf-8'))['selected_sources']
rows=[]
for name in selected:
    p=b/Path(name).stem
    def read(file):
        q=p/file
        return json.loads(q.read_text(encoding='utf-8-sig')) if q.exists() else {}
    source=read('SOURCE.json');summary=read('SUMMARY.json');lead=read('LEAD_ACCEPTANCE.json')
    game=read('PAUSE_GAME.json')
    validation=read('VALIDATION.json') or read('STRUCTURAL_VALIDATION.json') or read('STRUCTURAL_RECEIPT.json') or read('VALIDATION_RECEIPT.json') or read('STRUCTURAL_CHECK.json')
    submitted=bool((p/'REVIEW.md').exists() and (p/'COVERAGE.md').exists() and game.get('is_template') is False and validation.get('structural_pass') is True and not validation.get('issues'))
    status='lead_accepted' if lead.get('accepted') else 'submitted_pending_acceptance' if submitted else 'source_bound_review_pending' if source else 'source_access_pending'
    if list(p.glob('MOVE_RECEIPT.*.json')):status='accepted_registered_archived'
    rows.append({'source_video':name,'sha256':source.get('sha256'),'duration_seconds':source.get('duration_seconds'),'packet':str(p),'persisted_status':status,
        'review_summary':summary,'external_saved':bool(read('EXTERNAL_RECEIPT.json').get('saved'))})
doc={'updated_utc':datetime.now(timezone.utc).isoformat(),'source_count':len(rows),'source_bound_count':sum(bool(r['sha256']) for r in rows),'sources':rows,
    'status_definition':'Source identity/intake is separate from full visual review, independent acceptance, registration, external save and archival.'}
(b/'BATCH_PROGRESS.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({s:sum(r['persisted_status']==s for r in rows) for s in sorted({r['persisted_status'] for r in rows})}))
