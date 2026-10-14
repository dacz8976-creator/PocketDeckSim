import json,re
from pathlib import Path
p=Path(__file__).parent.resolve();out=(p/'turn_evidence').resolve()
assert out.parent==p and p.name=='20261004_213625000_iOS'
e=json.loads((p/'TURN_EVIDENCE.json').read_text());keep=set()
def walk(v):
 if isinstance(v,str) and re.fullmatch(r'F\d+\.\d\d',v):keep.add(v)
 elif isinstance(v,dict):
  for k,x in v.items():
   if k!='frames':walk(x)
 elif isinstance(v,list):
  for x in v:walk(x)
for fn in ['TURN_LEDGER.json','TURN_EVIDENCE.json','PAUSE_GAME.json','SUMMARY.json','ASTRA_QUESTION.json']:
 walk(json.loads((p/fn).read_text()))
for t in [0,2,4,6,8,10,15,20,25,30,31,32,33,34,37,40,41,42,43,44,47.5,49.5,52.5,75,76,77,78,80,81,82,89,91,93,97,124,125,126,128,130,131,134,135,136,137,138,189,190,191,192,193,194,195,197,198,199,219,222,223,224,240,241,243,244.5,245.5,247,250,259,260,265,269,270,276,282,284,307,308,309,310,311,312,314,315,319,322,324,326,327,328,329,330,331,332,333.5,334.5,335.5,336.5,338.5,341.5,351,352,353,354,355,356,357,358,359,360,363,366,370,371,372,375,376,377,378,379,380,381,384,387,388,389,390.5,391,391.5,391.6,391.8,392.2,392.5,392.6,393,393.5,394.6,395,396,397,397.6,398,399,400,401,401.5,402,402.2,402.5,403,404,405,406,407,408,409,410,410.5,411,412,413,414,414.5,415,415.5,416,417,418,419,420,427,430,440,441,442,443,444,445,446,448,449,450,451,454,457,459]:keep.add(f'F{t:07.2f}')
def frame(t):
 stem=f't{t:07.2f}'
 return {'evidence_id':f'F{t:07.2f}','source_video':e['source_video'],'requested_seek_seconds':t,'actual_frame_timestamp_seconds':None,'native_dimensions':[1170,2532],'full_frame':f'turn_evidence/{stem}.png','bottom_fifth':f'turn_evidence/{stem}_bottom.png','bottom_crop_xyxy':[0,2025,1170,2532],'top_crop':f'turn_evidence/{stem}_top.png','top_crop_xyxy':[0,0,1170,607],'status':'retained_native'}
e['frames']=[frame(float(f.stem[1:])) for f in sorted(out.glob('t*.png')) if '_' not in f.stem]
all_ids=[f['evidence_id'] for f in e['frames']];removed=[]
for f in e['frames']:
 if f['evidence_id'] in keep:continue
 for k in ['full_frame','bottom_fifth','top_crop']:
  path=(p/f[k]).resolve();assert path.parent==out and path.suffix=='.png';path.unlink()
 removed.append(f['evidence_id'])
e['frames']=[f for f in e['frames'] if f['evidence_id'] in keep]
(p/'TURN_EVIDENCE.json').write_text(json.dumps(e,indent=2)+'\n',encoding='utf-8')
(p/'EXTRACTION_RETENTION_RECEIPT.json').write_text(json.dumps({'original_extracted_ids':all_ids,'retained_ids':[f['evidence_id'] for f in e['frames']],'removed_redundant_native_ids':removed,'reason':'Keep all mandatory and referenced native captures plus dense consequential windows. Coarse overview sheets and reviewed-time account retained. Source unchanged.'},indent=2)+'\n',encoding='utf-8')
for fn in ['REVIEW.md','COVERAGE.md']:
 s=(p/fn).read_text().replace('Dacz 8976','Dacz8976').replace(',851427995bytes,460.651667seconds',', 851427995 bytes, 460.651667 seconds')
 lines=s.splitlines();ledger=json.loads((p/'TURN_LEDGER.json').read_text())
 for r in ledger['turns']:
  prefix=f"| {r['turn_number']} |"
  for i,line in enumerate(lines):
   if line.startswith(prefix):
    actions=[]
    for x in r['plays_in_order']:
     result=x['result']
     if x['kind']=='energy_attachment':result+=f" to {x['target']}"
     actions.append(f"{x['order']}. {x['card_name'] or x['kind'].replace('_',' ')}: {result} ({x['timestamp_seconds']} s)")
    lines[i]=f"| {r['turn_number']} | {r['who_played']} | {r['timing']['start_seconds']}-{r['timing']['end_after_resolution_seconds']} | {'; '.join(actions)} |"
 s='\n'.join(lines)+'\n'
 (p/fn).write_text(s,encoding='utf-8')
print(json.dumps({'retained_native_frames':len(e['frames']),'removed_redundant_frames':len(removed)}))
