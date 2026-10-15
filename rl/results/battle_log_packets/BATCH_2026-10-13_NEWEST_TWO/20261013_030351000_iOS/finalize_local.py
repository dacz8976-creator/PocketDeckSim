import json,re,hashlib
from pathlib import Path
p=Path(__file__).resolve().parent
files=['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
def wording(s):
 # Called only on prose-valued fields, never paths, IDs, hashes, URLs or deck codes.
 held=[]
 def hold(m):held.append(m.group());return '\x00'+str(len(held)-1)+'\x00'
 s=re.sub(r'\bT\d+\b|\bDacz8976\b',hold,s)
 s=re.sub(r'(?<=\d)(?=[A-Za-z])',' ',s)
 s=re.sub(r'(?<=[A-Za-z\u2019])(?=\d)',' ',s)
 s=re.sub(r'\b(at|from|deals|heal|heals|now|plus|printed|all|after|confirms|damage|total|remain|remaining|takes|gain|gains|stack|owner|opponent|interval|Size|Duration|date|defeat|Research|Metal|Fighting)(?=\d)',r'\1 ',s)
 s=s.replace('isOctober','is October').replace('allfive','all five').replace('→',' → ').replace('×',' × ')
 s=s.replace('containerUTC','container UTC')
 s=re.sub(r'[,;](?=[A-Za-z0-9])',lambda m:m.group()+' ',s)
 s=re.sub(r'\x00(\d+)\x00',lambda m:held[int(m.group(1))],s)
 s=re.sub(r' +',' ',s)
 return s
prose_keys={'result','basis','limit_reason','limit','limits','phase','observation','suitability_or_limit','hp_max_basis','variant','scope','log_list_version','game_version_binding_basis','date_basis','description','precision','scheduled_capture_limits','automatic_events_in_order','nested_events_in_order','scroll_coverage','semantic_notes','turn_number_basis','points_basis'}
def walk(d,prose=False):
 if isinstance(d,dict):return {k:walk(v,k in prose_keys) for k,v in d.items()}
 if isinstance(d,list):return [walk(v,prose) for v in d]
 if isinstance(d,str) and prose:return wording(d)
 return d
for name in files:
 f=p/name
 if f.suffix=='.json':f.write_text(json.dumps(walk(json.loads(f.read_text(encoding='utf-8'))),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 else:
  lines=[]
  for line in f.read_text(encoding='utf-8').splitlines():
   # Markdown code spans and link targets are protected while normal prose is spaced.
   pieces=re.split(r'(`[^`]*`|\]\([^)]*\)|(?<!\w)/root/[^ ;,]+|\b20261013_030351000_iOS\.MP4\b)',line)
   line=''.join(part if i%2 else wording(part) for i,part in enumerate(pieces))
   lines.append(line)
  f.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Final prose normalization complete, protected identifiers unchanged')
