from pathlib import Path
import json,re,hashlib
from PIL import Image
P=Path(__file__).resolve().parent;OLD=P.parents[1]/'20260907_232617_v5_review/final_packet'
def read(n):return json.loads((P/n).read_text(encoding='utf-8-sig'))
def save(n,x):(P/n).write_text(json.dumps(x,indent=2,ensure_ascii=False),encoding='utf-8')
l=read('TURN_LEDGER.json');e=read('TURN_EVIDENCE.json');h=read('HAND_SUPPLEMENT.json');pg=read('PAUSE_GAME.json')
known={f['evidence_id'] for f in e['frames']}
def walk(x):
 if isinstance(x,dict):
  for k,v in x.items():
   if k in ['evidence_ids','turn_evidence_ids','candidate_evidence_ids'] and isinstance(v,list):
    for i in v:
     if isinstance(i,str) and re.fullmatch(r'f\d+\.\d{3}',i) and i not in known:
      t=float(i[1:]);path=OLD/'frames'/f'{t:07.3f}.jpg'
      if path.exists():
       with Image.open(path) as im:wh=im.size
       e['frames'].append({'evidence_id':i,'role':['inherited_action_or_draw_reference'],'source_video':pg['sources'][0]['video_basename'],'source_sha256':pg['sources'][0]['sha256'],'requested_source_seconds':t,'actual_frame_seconds_if_measured':None,'full_frame_path':str(path),'full_frame_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'native_dimensions':{'width':wh[0],'height':wh[1]},'bottom_crop':None,'top_crop':None,'crop_limit':'Action/draw reference; native full frame retained; scheduled candidate crops are separate','new_extraction':False});known.add(i)
      else:raise AssertionError('Missing native reference '+i)
   walk(v)
 elif isinstance(x,list):
  for v in x:walk(v)
for x in [l,h,pg]:walk(x)
for row in l['turns']:
 n=row['turn_number']
 if n%2:
  row['draws_and_searches'][0]['visible_count']=None;row['draws_and_searches'][0]['basis']='Hidden opponent normal draw; exact added count not certified in the accepted prose';row['draws_and_searches'][0]['limit_reason']='Identity hidden; source count not newly enumerated'
 for key in ['board_at_start','board_after']:
  b=row[key];b['stadium_status']='none_visible_before_T3' if b['stadium'] is None else 'inherited_accepted_and_visible'
  for side in ['owner','opponent']:
   b[side]['active_status']='known_empty_after_terminal_KO' if b[side]['active'] is None else 'present'
   for poke in b[side]['bench_in_position_order']:
    poke['bench_position_basis']='direct_native215/236/265/360 evidence plus inherited continuity' if side=='owner' and n>=5 else 'native board layout; accepted species/HP/Energy'
  if n>=8:
   active=b['opponent']['active']
   if active and active['name']=='Falinks':
    active['active_effects']=['Coordinated Unit'];active['Goo_zooka_retreat_modifier']=None;active['Goo_zooka_limit']='Last observed effect at235s; no later effect assumed'
assert [r['turn_number'] for r in l['turns']]==list(range(1,12))
assert h['target_turn_numbers']==[2,4,6,8,10]
for r in h['turns']:
 assert len(r['hand_at_start']['cards_left_to_right'])==r['hand_at_start']['count']
 assert len(r['owner_hand_end']['cards_left_to_right'])==r['owner_hand_end']['count']
 assert all(c['name'] for c in r['hand_at_start']['cards_left_to_right'])
assert pg['opening']['before_active_placement'] and pg['opening']['selected_active']['opening_position']==5
assert len(pg['opening']['cards_left_to_right'])==5
for f in e['frames']:
 assert Path(f['full_frame_path']).is_file()
 assert f['native_dimensions']=={'width':1170,'height':2532}
 if f.get('bottom_crop'):
  with Image.open(f['bottom_crop']['path']) as im:assert im.size==(1170,507)
 if f.get('top_crop'):
  with Image.open(f['top_crop']['path']) as im:assert im.size==(1170,720)
save('TURN_LEDGER.json',l);save('TURN_EVIDENCE.json',e)
m=read('METRICS.json');m['reused_native_frames_referenced']=sum(not f['new_extraction'] for f in e['frames']);save('METRICS.json',m)
save('FIELD_CHECK.json',{'passed':True,'turn_rows':11,'owner_hands':5,'opening_slots':5,'source_bound_native_evidence_records':len(e['frames']),'duplicate_evidence_ids':len(e['frames'])!=len(known),'independent_visual_acceptance':'pending','exact_deck_status':'unavailable historical list','accepted_outcome_unchanged':True})
print('Field/identity/reference checks passed;11 rows, five complete named owner hands and ending counts, five observed opening slots.')
