import json
from pathlib import Path
B=Path(__file__).parent
p=B/'EXTRACTION_PLAN.json';d=json.loads(p.read_text());d['new_native_cap']=64
ts=[106,210,118,120,126,144,304,339.3,339.8,340.5,391,549]
d['source_action_checkpoint']={'status':'approved_by_lead','seconds':ts,'purpose':'Exact named Research/Copycat reveal bridges; ownerT3 target/retreat, opponentT4/10/14 attachments, ownerT7 Energy, and blueTool identity/maxHP.'}
for s in ts:d['rows'].append(dict(requested_source_seconds=float(s),purpose=d['source_action_checkpoint']['purpose'],status='planned',actual_frame_seconds_if_measured=None))
d['planned_new_native_count']=64
p.write_text(json.dumps(d,indent=2),encoding='utf-8')
