from pathlib import Path
import json,hashlib
p=Path(__file__).resolve().parent.parent
names=['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
files={};out={'files':{},'diagnostics':[]}
for n in names:
 f=p/n
 if not f.exists():out['diagnostics'].append('Missing '+n);continue
 raw=f.read_bytes();text=raw.decode('utf-8-sig');files[n]=json.loads(text) if n.endswith('.json') else text
 out['files'][n]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'em_dash_count':text.count('\u2014')}
for n,d in files.items():
 if isinstance(d,dict) and d.get('is_template'):out['diagnostics'].append('Template remains '+n)
ledger=files.get('TURN_LEDGER.json',{})
rows=ledger.get('turns',ledger.get('rows',[]))
out['ledger_top_keys']=list(ledger)
out['turns']=[{'turn':r.get('turn_number'),'player':r.get('player',r.get('who_played')),'timing':r.get('timing',r.get('source_local_timing')),'hand':r.get('hand_at_start'),'draws':r.get('draws_and_searches'),'plays':r.get('plays_in_order'),'end_hand':r.get('owner_hand_end')} for r in rows]
out['row_count']=len(rows)
evidence=files.get('TURN_EVIDENCE.json',{});frames=evidence.get('frames',[])
ids={f.get('evidence_id') for f in frames};missing=[]
for fr in frames:
 for key in ['full_frame_path','bottom_crop','top_crop']:
  x=fr.get(key);x=x.get('path') if isinstance(x,dict) else x
  if x and not (p/x).exists():missing.append(x)
out['missing_frame_paths']=missing
out['frame_count']=len(frames)
out['source_binding']=json.loads((p/'SOURCE.json').read_text(encoding='utf-8-sig'))
out['deck']=files.get('DECK_USED.json')
out['summary']=files.get('SUMMARY.json')
(p/'independent_sol/FINAL_FILE_INSPECTION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k not in ['turns','deck','source_binding']},ensure_ascii=True,indent=2))
