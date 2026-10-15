from pathlib import Path
import re,json,hashlib
from datetime import datetime,timezone
p=Path(__file__).parent
f=p/'REVIEW.md';x=f.read_text()
for a,b in [('Dacz 8976','Dacz8976'),('draft_before_t 6_correction','draft_before_t6_correction'),('Native t 0','Native t0'),('T 2','T2'),('T 4','T4'),('T 5','T5'),('T 6','T6'),('T 8','T8')]:x=x.replace(a,b)
x=re.sub(r',(?=\S)',', ',x)
for sec in ['326','336','338','340']:x=x.replace(f'({sec}s)',f'({sec} s)')
f.write_text(x,encoding='utf-8')
names=['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
source=json.loads((p/'SOURCE.json').read_text())
record={'frozen_utc':datetime.now(timezone.utc).isoformat(),'source_video':source['video_basename'],'source_sha256':source['sha256'],'reviewer':'/root/pause_20261012_225319000_iOS','files':{n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in names},'status':'submitted_for_independent_acceptance','correction_history':'Rejected first draft preserved at draft_before_t6_correction. T6 attachment and retreat payment corrected before this freeze.'}
(p/'REVIEW_PACKET_HASHES.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,indent=2))
