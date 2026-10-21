import json
from pathlib import Path
B=Path(__file__).parent
p=json.loads((B/'EXTRACTION_PLAN.json').read_text())
p['new_native_cap']=69
p.setdefault('checkpoints',[]).append({'approved_by':'root','new_cap':69,'prior_count':64,'exact_requested_seconds':[394,467,554,429.5,679],'reason':'Actual attachment-target windows T10/T12/T14, Supporter warning response boundary, and unoccluded menu classification; endpoints and earlier generated-Energy views cannot establish these inputs.'})
(B/'EXTRACTION_PLAN.json').write_text(json.dumps(p,indent=2))
