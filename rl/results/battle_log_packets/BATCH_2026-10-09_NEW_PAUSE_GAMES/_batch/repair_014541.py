import copy,json,shutil
from pathlib import Path
from PIL import Image
p=Path(__file__).resolve().parent/'20261010_014541000_iOS'
names=['PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json','REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json']
for n in names:
 f=p/n; b=p/(f.stem+'.before_independent_repairs'+f.suffix)
 if not b.exists():shutil.copy2(f,b)
def read(n):return json.loads((p/n).read_text(encoding='utf-8'))
def save(n,v):(p/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
e=read('TURN_EVIDENCE.json')
for sec,turn in [(223,6),(264,7),(293,8),(469,12),(470,12),(471,12),(490,12),(491,12),(492,12)]:
 eid=f'f_{sec:07.2f}'; dst=p/f'turn_evidence/t{sec:07.2f}.jpg'
 assert not any(x['evidence_id']==eid for x in e['frames'])
 shutil.copy2(p/f'independent_sol/t{sec:07.2f}.jpg',dst)
 with Image.open(dst) as im:
  w,h=im.size
  bottom=dst.with_name(dst.stem+'_bottom.jpg');top=dst.with_name(dst.stem+'_top.jpg')
  im.crop((0,2025,w,h)).save(bottom,quality=95);im.crop((0,0,w,780)).save(top,quality=95)
 f=copy.deepcopy(e['frames'][0]);f.update(evidence_id=eid,role='independent_repair_event',turn_number=turn,who_played='owner' if turn%2 else 'opponent',requested_source_seconds=float(sec),full_frame_path=str(dst.relative_to(p)),before_first_play=sec in [223,293],unzoomed=sec!=264,observation='Independent bounded native extraction; corrected ledger cites exact supported state.')
 f['bottom_crop']={'path':str(bottom.relative_to(p)),'pixel_bounds_x0_y0_x1_y1':[0,2025,w,h]}
 f['top_crop']={'path':str(top.relative_to(p)),'pixel_bounds_x0_y0_x1_y1':[0,0,w,780]}
 e['frames'].append(f)
save('TURN_EVIDENCE.json',e)
l=read('TURN_LEDGER.json')
def rebind(v,eid):
 if isinstance(v,dict):
  for k,x in v.items():
   if k=='evidence_ids':v[k]=[eid]
   else:rebind(x,eid)
 elif isinstance(v,list):
  for x in v:rebind(x,eid)
for n,sec in [(6,223),(8,293)]:
 t=l['turns'][n-1];rebind(t['board_at_start'],f'f_{sec:07.2f}');t['turn_evidence_ids'].append(f'f_{sec:07.2f}')
d=l['turns'][6]['draws_and_searches'][1];d['cards_in_reveal_order'][0]['evidence_ids']=['f_0264.00'];d['evidence_ids']=['f_0264.00','f_0265.00'];l['turns'][6]['turn_evidence_ids'].append('f_0264.00')
r=l['turns'][8]['plays_in_order'][1]['energy'];r['destination']='discard pile';r['source']='Horsea'
t=l['turns'][11];a,b=t['plays_in_order'][:2]
b.update(order=1,timestamp_seconds=469,evidence_ids=['f_0469.00','f_0470.00'])
a.update(order=2,target='Feebas, Bench position3',timestamp_seconds=471,evidence_ids=['f_0471.00','f_0472.00'],result='First Water attached to newly benched Feebas; Milotic remains at3Water')
a['energy']['destination']='Feebas';t['plays_in_order'][:2]=[b,a]
board=t['board_after'];board['phase']='Resolved terminal knockout, owner Active removed; no replacement because match ended'
board['owner']['active']=None;board['owner']['active_limit_reason']='Weezing ex and attached Small Balloon removed after terminal KO; match ended before replacement.'
for x in board['opponent']['bench_in_position_order']:
 if x['name'] in ['Milotic','Feebas']:
  count=3 if x['name']=='Milotic' else 1;x['attached_energy']={'total':count,'by_type':{'Water':count}}
rebind(board,'f_0492.00');board['opponent']['points_evidence_ids']=['f_0490.00','f_0492.00']
t['turn_evidence_ids']+=['f_0469.00','f_0470.00','f_0471.00','f_0490.00','f_0491.00','f_0492.00']
save('TURN_LEDGER.json',l)
g=read('PAUSE_GAME.json');g['opening']['cards_left_to_right'][4]['evidence_ids']+=['f_0055.00','f_0056.00'];g['opening']['selected_active']['evidence_ids']=['f_0055.00','f_0056.00'];g['outcome']['evidence_ids']=['f_0486.00','f_0490.00','f_0492.00','f_0501.00']
g['limits'][0]='Initial23-deck snapshot lacked this entry. Current live20 is a later QR candidate; visible Elegant Cape conflicts with it, so exact earlier game20 remains unverified.'
save('PAUSE_GAME.json',g)
f=p/'REVIEW.md';s=f.read_text(encoding='utf-8');s+='\nIndependent native corrections: T6 starts at223s before Feebas evolves; T8 start Energy is bound to293s. Research first reveals Elegant Cape264s, then Soothing Shore265s. T9 Horsea retreat discards its Water. T12 benches Feebas469s, attaches Water to Feebas471s, then Irida473.3s and Crystal Waltz483s. Milotic remains3Water; Feebas has1Water. All three opponent points are lit490s; resolved492s has no owner Active after Weezing/Small Balloon removal, Horsea50HP/1Water bench1 and Cape Koffing60HP/0Water bench3. These corrections supersede any earlier prose timing/state descriptions.\n';f.write_text(s,encoding='utf-8')
print('014541 precise independent repairs applied')
