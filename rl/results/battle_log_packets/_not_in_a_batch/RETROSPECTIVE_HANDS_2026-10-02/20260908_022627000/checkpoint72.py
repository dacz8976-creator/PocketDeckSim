import json
from pathlib import Path
B=Path(__file__).parent
p=json.loads((B/'EXTRACTION_PLAN.json').read_text())
p['new_native_cap']=72
p.setdefault('checkpoints',[]).append({'approved_by':'root','new_cap':72,'prior_count':69,'exact_requested_seconds':[403,444,559],'reason':'Earlier five views resolve warning/menu but three Energy views predate attachment. Re-inspected nominal 1fps locators narrow actual transitions to T10 401-407, T12 441-446 and T14 555-560. Preserve source turn attribution and bounded timing if input is not in selected frame.'})
(B/'EXTRACTION_PLAN.json').write_text(json.dumps(p,indent=2))
