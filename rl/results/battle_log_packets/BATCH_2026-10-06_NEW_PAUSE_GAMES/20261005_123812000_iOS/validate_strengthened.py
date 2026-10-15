import json, hashlib, subprocess, sys
from pathlib import Path
P=Path(__file__).parent
def read(n):return json.loads((P/n).read_text(encoding='utf-8-sig'))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
src=read('SOURCE.json');ld=read('TURN_LEDGER.json');ev=read('TURN_EVIDENCE.json');pa=read('PAUSE_GAME.json');deck=read('DECK_USED.json')
issues=[];checks=[]
def check(ok,claim):
    checks.append(dict(check=claim,pass_check=bool(ok)))
    if not ok:issues.append(claim)
check(len(ld['turns'])==9 and [x['turn_number'] for x in ld['turns']]==list(range(1,10)),'Exactly nine consecutive rows including four opponent turns')
check(pa['opening']['recorded_card_count']==5 and len(pa['opening']['cards_left_to_right'])==5 and pa['opening']['before_active_placement'],'Five-card native opening before placement')
ids={x['evidence_id']:x for x in ev['frames']}
expected={1:['Nidoking','Poison Barb','Deceptive Needle'],3:['Nidoking','Poison Barb','Darkrai ex'],5:['Nidoking','Darkrai ex','Poke Ball'],7:['Nidoking','Darkrai ex',"Professor's Research"],9:['Nidoking','Darkrai ex','Heavy Helmet','Poke Ball']}
fancount={1:4,3:4,5:4,7:3,9:4}
for row in ld['turns']:
 n=row['turn_number'];check([p['order'] for p in row['plays_in_order']]==list(range(1,len(row['plays_in_order'])+1)),f'Turn{n} sequential voluntary order')
 if n%2:
  selected=[f for f in ev['frames'] if f['turn_number']==n and f['selected_for_start_hand']]
  candidates=[f for f in ev['frames'] if f['turn_number']==n and f['role']=='scheduled_draw_candidate']
  check(len(selected)==1 and selected[0]['unzoomed'] and selected[0]['before_first_play'] and row['owner_hand_start']['cards_left_to_right']==expected[n],f'Turn{n} selected intact named native preplay hand')
  check(len(candidates)==3 and all(abs(f['offset_after_draw_seconds']-offset)<=.6 for f,offset in zip(sorted(candidates,key=lambda f:f['requested_source_seconds']),[1,3,6])),f'Turn{n} retained approximate draw+1/+3/+6')
  check(row['opponent_hand_at_owner_turn_start']['count']==fancount[n],f'Turn{n} native opponent fan count')
  check(row['plays_in_order'][-1]['hand_count_after']==row['owner_hand_end']['count'],f'Turn{n} end hand arithmetic reconciles')
  check(any(f['role']=='before_end_action' and f['turn_number']==n for f in ev['frames']),f'Turn{n} before-end hand retained')
 for key in ['board_at_start','board_after']:
  for who in ['owner','opponent']:
   side=row[key][who];check(len(side['bench_in_position_order'])==3 and all('tool' in m and 'attached_energy' in m and 'special_conditions' in m for m in [side['active']]+side['bench_in_position_order']),f'Turn{n}/{key}/{who} full positional board, typed Energy, Tool/conditions')
   for m in [side['active']]+side['bench_in_position_order']:
    if m['name']!='none':check(m['attached_energy']['total']==sum(m['attached_energy']['by_type'].values()) and m['damage']==m['hp_max']-m['hp_now'],f'Turn{n}/{key}/{who}/{m["name"]} Energy/HP arithmetic')
check(all(ld['turns'][n-1]['board_at_start']['owner']['energy_zone']['this_turn']['count']==0 for n in [1,3,7]),'Early selected T1/T3/T7 current Energy absence preserved separately from Darkness next')
check(ld['turns'][8]['board_at_start']['owner']['energy_zone']['this_turn']['type']=='unknown','T9 generation glow current remains unknown')
check(ld['turns'][5]['board_after']['opponent']['bench_in_position_order'][2]['attached_energy']['by_type']=={'Psychic':3},'First Fantasia assigns three Psychic to right Diancie')
check(ld['turns'][7]['board_after']['opponent']['bench_in_position_order'][1]['attached_energy']['by_type']=={'Psychic':4},'Second Fantasia leaves four Psychic on center Diancie')
check(ld['turns'][6]['plays_in_order'][1]['energy']['retreat_payment_by_type']=={'Darkness':1} and ld['turns'][6]['plays_in_order'][2]['energy']['destination']=='right Bench Nidoran♂','Retreat payment precedes new bench attachment')
research=ld['turns'][6]['draws_and_searches'][1]['cards_in_reveal_order']
check([x['name'] for x in research]==['Heavy Helmet','Nihilego'] and research[0]['timestamp_seconds']<research[1]['timestamp_seconds'],'Owner Research named reveal order')
check(not ld['turns'][8]['draws_and_searches'][1]['cards_in_reveal_order'] and ld['turns'][8]['plays_in_order'][0]['hand_count_after']==3,'No-effect final Poke Ball consumes card and finds zero')
check(pa['outcome']['method']=='owner_concession' and pa['outcome']['last_visible_earned_points']=={'owner':1,'opponent':2},'Filmed concession loss linked separately from earned score1-2')
qr=json.loads((P/'qr_intake/QR_DECODE_0002.00.json').read_text(encoding='utf-8'))
check(qr['source_sha256']==src['sha256'] and qr['card_slot_count']==20 and digest(Path(qr['retained_image']))==qr['retained_image_sha256'],'Frozen retained QR hash/source and exact20 intact')
check(sum(c['count'] for c in deck['counts_by_name_and_variant'])==20 and next(c['count'] for c in deck['counts_by_name_and_variant'] if c['name']=='Darkrai ex')==2,'Distinct two-Darkrai exact semantic20 revision')
check(deck['cards_in_log_order'] is None and 'pending' in deck['exact_list_status'],'Missing live exact deck snapshot remains explicit')
check(all(not d['full_pile_established'] for d in ev['discard_snapshots']),'No top preview mislabeled full discard')
required=['SOURCE.json','REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
for name in required:
 text=(P/name).read_text(encoding='utf-8-sig');check(not any(bad in text for bad in ['PokÃ','Professorâ€']),'UTF8 authored strings '+name)
r=subprocess.run([sys.executable,str(P.parent/'validate_packet.py'),str(P)],capture_output=True,text=True,encoding='utf-8')
(P/'STRUCTURAL_VALIDATION.json').write_text(r.stdout,encoding='utf-8')
check(r.returncode==0,'Shared frame/file/crop/reference/template validator')
receipt=dict(schema='pause-games/strengthened-local-validation-v1',source_video=src['video_basename'],source_sha256=src['sha256'],local_pass=not issues,checks=checks,issues=issues,required_file_sha256={n:digest(P/n) for n in required},native_frame_count=len(ev['frames']),visual_acceptance=False,independent_acceptance=False,external_registration=False,limits=['Consistency and integrity are reviewer-authored; root independent source review remains required.','Exact live log list pending root registration.'])
(P/'VALIDATION_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(local_pass=not issues,checks=len(checks),issues=issues,native_frames=len(ev['frames'])),indent=2));sys.exit(1 if issues else 0)
