import json
from pathlib import Path
p=Path(__file__).resolve().parent.parent
d=json.loads((p/'TURN_LEDGER.json').read_text(encoding='utf-8'))
def walk(x,path):
    if isinstance(x,dict):
        for k,v in x.items(): walk(v,path+'/'+k)
    elif isinstance(x,list):
        for i,v in enumerate(x): walk(v,path+'/'+str(i))
    elif isinstance(x,str) and any(s in x.lower() for s in ['binding','cannot attach','energy zone attachment','attach energy from','active attachment']):
        print(path+': '+x)
for t in d['turns']:
    if t['turn_number']>=10:
        walk(t,'T'+str(t['turn_number']))
