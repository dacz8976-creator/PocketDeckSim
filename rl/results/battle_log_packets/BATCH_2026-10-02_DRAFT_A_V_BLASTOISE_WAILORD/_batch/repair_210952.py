import copy,hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
B=Path(__file__).resolve().parent;P=B/'20261002_210952000_iOS_auto_sol'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert read(P/'independent_sol/CHECK_RESULT.json')['accepted'] is False
assert read(P/'independent_sol/CHECK_GUIDE_UPDATE.json')['accepted'] is False
assert not(P/'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json').exists()
core=read(P/'SUBMISSION.json');guide=read(P/'GUIDE_UPDATE_SUBMISSION.json')
for folder,manifest_name,manifest in [('worker_submission','SUBMISSION.json',core),('guide_submission_before_repair','GUIDE_UPDATE_SUBMISSION.json',guide)]:
 dest=P/folder;assert not dest.exists();dest.mkdir()
 for name,expected in manifest['files'].items():
  assert sha(P/name)==expected,name
  shutil.copy2(P/name,dest/name)
 shutil.copy2(P/manifest_name,dest/manifest_name)
allframes=read(P/'EXTRACTION_MANIFEST.json')+read(P/'independent_sol/EXTRACTION_MANIFEST.json')
frames={f['evidence_id']:f for f in allframes}
ledger=read(P/'TURN_LEDGER.json')
def turn(n):return next(r for r in ledger['turns'] if r['turn_number']==n)
turn(18)['board_at_start']['owner']['energy_zone']['this_turn']={'type':None,'count':0,'available':False,'phase':'pending_generation'}
turn(18)['board_at_start']['owner']['energy_zone']['basis']='Native290.402 has an empty large current Energy slot and small Water preview. Generated Water appears later; do not place it at this start anchor.'
corrections=[(2,'supporter_draw',0,'independent_sol:F0035.50'),(2,'supporter_draw',1,'F0036.40'),(2,'search',0,'independent_sol:F0041.00'),(6,'supporter_draw',0,'F0093.00'),(6,'supporter_draw',1,'F0093.40')]
for number,kind,index,eid in corrections:
 d=next(d for d in turn(number)['draws_and_searches'] if d['kind']==kind)
 c=d['cards_in_reveal_order'][index];f=frames[eid]
 c['timestamp_seconds']=f['requested_source_seconds'];c['actual_frame_seconds_if_measured']=f['actual_frame_seconds_if_measured'];c['evidence_ids']=[eid]
 c['basis']='Directly readable named reveal in selected native frame; requested time and measured decoder PTS are separate.'
 d['evidence_ids']=[i for card in d['cards_in_reveal_order'] for i in card['evidence_ids']]
 d['timestamp_seconds']=d['cards_in_reveal_order'][0]['timestamp_seconds']
save(P/'TURN_LEDGER.json',ledger)
evidence=read(P/'TURN_EVIDENCE.json')
for eid,number,observation in [('independent_sol:F0035.50',2,'Research first reveal Alolan Ninetales ex'),('independent_sol:F0041.00',2,'Poke Ball search reveal Alolan Vulpix'),('independent_sol:F0253.50',15,'Visible written switch-in prompt and three highlighted Bench candidates; Auto enabled')]:
 f=copy.deepcopy(frames[eid]);f.update({'role':'independent_bounded_correction','turn_number':number,'who_played':'owner' if number==2 else 'opponent','observation':observation,'selected_for_start_hand':False,'before_first_play':None,'unzoomed':None,'suitability_or_limit':'Distinct independent extraction; original primary manifest is preserved.'})
 evidence['frames'].append(f)
save(P/'TURN_EVIDENCE.json',evidence)
review=(P/'REVIEW.md').read_text(encoding='utf-8')
old='Owner starts have generated Water available; several computer start anchors precede generation.'
assert old in review
review=review.replace(old,'Most selected owner starts show generated Water available. The turn18 start at measured290.402 instead has an empty large current slot, with Water only in the small preview; generation occurs later. Several computer start anchors also precede generation.')
note='\n\nIndependent bounded corrections: Research T2 reveals Ninetales at requested35.5/measured35.515, then Poke Ball at36.4; its Vulpix search reveal is41.0/measured41.015. Research T6 reveals Misty at93.0/measured93.015, then Sharpedo at93.4/measured93.415. Names, reveal order and end hands are unchanged. The T15 switch-in prompt is directly visible at253.503: "Please choose a Pokémon to switch in"; Auto selects the right Ninetales from the three highlighted Bench candidates. Original submissions and rejected independent receipts remain preserved.\n'
(P/'REVIEW.md').write_text(review+note,encoding='utf-8')
with (P/'TURN_TABLE.md').open('a',encoding='utf-8') as f:f.write(note)
supp=read(P/'GUIDE_UPDATE_SUPPLEMENT.json');choice=next(r for r in supp['owner_choices_during_opponent_turns'] if r['turn_number']==15)
prompt=frames['independent_sol:F0253.50'];text='Please choose a Pokémon to switch in'
choice['owner_forced_switch_prompt']=True;choice['prompt_text']=text
choice['options_shown']='Written switch-in prompt above three highlighted Bench Pokemon: Carvanha left, Sharpedo middle, Ninetales right. No separate menu is needed.'
choice['evidence_ids'].append(prompt['evidence_id'])
choice['prompt_evidence']={'evidence_id':prompt['evidence_id'],'requested_source_seconds':253.5,'actual_frame_seconds_if_measured':253.503,'full_frame_sha256':prompt['full_frame_sha256']}
event=choice['owner_choice_events'][0];event['options_shown']=choice['options_shown'];event['prompt_text']=text
event['source_seconds_bracket']=[253.503,256.405]
event['evidence'].append({'evidence_id':prompt['evidence_id'],'source_seconds':253.503})
supp['source_evidence'].append(copy.deepcopy(prompt))
supp['bounded_repair']={'author':'/root','based_on':'independent_sol/CHECK_GUIDE_UPDATE.json','original_guide_preserved':'guide_submission_before_repair','scope':'Visible T15 prompt only; selection, actor, candidate identities and inventory unchanged.'}
save(P/'GUIDE_UPDATE_SUPPLEMENT.json',supp)
md=(P/'GUIDE_UPDATE_SUPPLEMENT.md').read_text(encoding='utf-8')
md=md.replace('No separate option dialog or human touch is visible.','At measured253.503 the written prompt says "Please choose a Pokémon to switch in", with the three Bench candidates highlighted. No human touch is visible; Auto remains checked.')
md+='\nIndependent correction retains the explicit switch-in prompt in independent_sol:F0253.50. Original four-file guide submission remains preserved in guide_submission_before_repair.\n'
(P/'GUIDE_UPDATE_SUPPLEMENT.md').write_text(md,encoding='utf-8')
receipt={'repaired_utc':datetime.now(timezone.utc).isoformat(),'author':'/root','source_video':core['source_video'],'source_sha256':core['source_sha256'],'original_core_sha256':sha(P/'worker_submission/SUBMISSION.json'),'original_guide_sha256':sha(P/'guide_submission_before_repair/GUIDE_UPDATE_SUBMISSION.json'),'independent_core_rejection_sha256':sha(P/'independent_sol/CHECK_RESULT.json'),'independent_guide_rejection_sha256':sha(P/'independent_sol/CHECK_GUIDE_UPDATE.json'),'corrections':['T18 current Energy slot pending generation','T2/T6 exact named reveal/search anchors','T15 visible written promotion prompt'],'core_changed_files':['TURN_LEDGER.json','TURN_EVIDENCE.json','REVIEW.md','TURN_TABLE.md'],'guide_changed_files':['GUIDE_UPDATE_SUPPLEMENT.json','GUIDE_UPDATE_SUPPLEMENT.md'],'independent_extraction_manifest_sha256':sha(P/'independent_sol/EXTRACTION_MANIFEST.json'),'primary_extraction_manifest_unchanged':True,'original_results_names_and_action_order_unchanged':True,'independent_recheck_pending':True}
save(P/'REPAIR_RECEIPT.json',receipt)
effective=copy.deepcopy(core);effective['files']={name:sha(P/name) for name in core['files']};effective['files']['REPAIR_RECEIPT.json']=sha(P/'REPAIR_RECEIPT.json');effective['original_submission_preserved']='worker_submission/SUBMISSION.json';effective['repair_receipt']='REPAIR_RECEIPT.json'
save(P/'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json',effective)
effective_guide=copy.deepcopy(guide);effective_guide['files']={name:sha(P/name) for name in guide['files']};effective_guide['original_submission_preserved']='guide_submission_before_repair/GUIDE_UPDATE_SUBMISSION.json';effective_guide['repair_receipt']='REPAIR_RECEIPT.json'
save(P/'GUIDE_UPDATE_SUBMISSION_AFTER_REPAIR.json',effective_guide)
print(json.dumps({'effective_core_sha256':sha(P/'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json'),'effective_guide_sha256':sha(P/'GUIDE_UPDATE_SUBMISSION_AFTER_REPAIR.json'),'native_captures_union':len(allframes)}))
