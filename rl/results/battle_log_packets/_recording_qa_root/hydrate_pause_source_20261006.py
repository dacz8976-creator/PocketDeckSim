"""Hydrate one owner-requested upload without changing its content."""
import argparse
import json
from pathlib import Path
from datetime import datetime, timezone
from hydrate_competitive_source import hydrate

ROOT=Path(__file__).resolve().parent.parent
BATCH=ROOT/'Recording_QA/BATCH_2026-10-06_NEW_PAUSE_GAMES'
selected=json.loads((BATCH/'OWNER_CONTEXT.json').read_text(encoding='utf-8'))['selected_sources']
p=argparse.ArgumentParser();p.add_argument('video',choices=selected);a=p.parse_args()
source=(ROOT/a.video).resolve()
assert source.parent==ROOT.resolve() and source.is_file()
receipt={'source':a.video,'attempt_utc':datetime.now(timezone.utc).isoformat(),'operation':'Windows Cloud Files hydrate','source_contents_modified':False}
print('Hydrating '+a.video,flush=True)
try:
    hydrate(source)
    receipt['result']='S_OK'
except Exception as e:
    receipt['result']='failed';receipt['error']=str(e)
(BATCH/('HYDRATION.'+a.video+'.json')).write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt),flush=True)
