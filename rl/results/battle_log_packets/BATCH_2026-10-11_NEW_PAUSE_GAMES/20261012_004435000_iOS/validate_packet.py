from pathlib import Path
import json,re
from PIL import Image
p=Path(__file__).parent
required=['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
for f in required:assert (p/f).is_file() and (p/f).stat().st_size>100,f
data={f:json.loads((p/f).read_text(encoding='utf-8')) for f in required if f.endswith('.json')}
for f,d in data.items():assert d.get('is_template') is not True,f
le=data['TURN_LEDGER.json'];ev=data['TURN_EVIDENCE.json'];deck=data['DECK_USED.json'];pg=data['PAUSE_GAME.json']
assert len(le['turns'])==10 and [x['turn_number'] for x in le['turns']]==list(range(1,11))
assert len(deck['cards_in_log_order'])==deck['total_card_slots']==sum(x['count'] for x in deck['counts_by_name_and_variant'])==20
assert deck['filmed_QR_payload_matches_snapshot'] is True
assert pg['opening']['recorded_card_count']==len(pg['opening']['cards_left_to_right'])==5
known={x['evidence_id'] for x in ev['frames']}
for f in ev['frames']:
 path=p/f['full_frame_path'];assert path.is_file(),path
 with Image.open(path) as im:assert im.size==(1170,2532);im.verify()
 for key in ['bottom_crop','top_crop']:
  c=f[key]
  if c:
   path=p/c['path'];assert path.is_file(),path
   b=c['pixel_bounds_x0_y0_x1_y1'];assert 0<=b[0]<b[2]<=1170 and 0<=b[1]<b[3]<=2532
   with Image.open(path) as im:assert im.size==(b[2]-b[0],b[3]-b[1]);im.verify()
def walk(x):
 if isinstance(x,dict):
  for k,v in x.items():
   if k=='evidence_ids' and v:assert set(v)<=known,(k,set(v)-known)
   walk(v)
 elif isinstance(x,list):
  for v in x:walk(v)
walk(data)
for t in le['turns']:
 assert [x['order'] for x in t['plays_in_order']]==list(range(1,len(t['plays_in_order'])+1))
 for fld in ['owner_hand_start','owner_hand_end','owner_hand_before_end_action']:
  h=t[fld];assert len(h['cards_left_to_right'])==h['count']
 for fld in ['board_at_start','board_after']:
  for who in ['owner','opponent']:
   b=t[fld][who];assert b['points']==0 and len(b['bench_in_position_order'])==3
   for m in [b['active']]+[x for x in b['bench_in_position_order'] if x]:assert m['hp_now']+m['damage']==m['hp_max'] and sum(m['attached_energy']['by_type'].values())==m['attached_energy']['total']
  assert t[fld]['phase']
 if t['who_played']=='owner':
  assert t['opponent_hand_at_owner_turn_start']['count'] in [2,3,4,5]
  candidates=[f for f in ev['frames'] if f['turn_number']==t['turn_number'] and f['offset_after_draw_seconds'] is not None]
  assert any(f['selected_for_start_hand'] and f['before_first_play'] and f['unzoomed'] and f['bottom_crop'] and f['top_crop'] for f in candidates)
  for off in [1,3,6]:assert any(abs(f['offset_after_draw_seconds']-off)<=.5 for f in candidates),(t['turn_number'],off)
  before=t['owner_hand_before_end_action']['evidence_ids'][0];assert next(f for f in ev['frames'] if f['evidence_id']==before)['bottom_crop']
assert len(list((p/'overview_seek').glob('t[0-9][0-9][0-9].jpg')))==116
total=sum(f.stat().st_size for f in (p/'turn_evidence').glob('*.jpg'))
out={'status':'passed','required_files':required,'turn_rows':10,'deck_slots':20,'opening_slots':5,'native_frames':len(ev['frames']),'crop_pairs':sum(bool(f['bottom_crop']) for f in ev['frames']),'native_and_crop_bytes':total,'checks':['UTF-8 JSON parse; no templates','Exactly one row per displayed turn','Exact20card deck and QR match','Native dimensions, image integrity and crop bounds','All evidence IDs exist','Board HP/energy arithmetic','Owner hands/counts and scheduled offsets/preplay/end crops','116 retained reduced coverage samples'],'independent_acceptance':'pending'}
(p/'STRUCTURAL_CHECK.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out))
