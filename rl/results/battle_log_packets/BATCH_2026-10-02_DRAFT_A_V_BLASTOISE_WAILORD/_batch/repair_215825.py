import copy,json,shutil
from datetime import datetime,timezone
from pathlib import Path
from validate_packet import read,sha
B=Path(__file__).resolve().parent;P=B/'20261002_215825000_iOS_shark_sol'
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not read(P/'independent_sol/CHECK_RESULT.json')['accepted']
assert not(P/'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json').exists()
original=read(P/'SUBMISSION.json');dest=P/'worker_submission';assert not dest.exists();dest.mkdir()
for n,h in original['files'].items():
 assert sha(P/n)==h,n
 shutil.copy2(P/n,dest/n)
shutil.copy2(P/'SUBMISSION.json',dest/'SUBMISSION.json')
frames={f['evidence_id']:f for f in read(P/'EXTRACTION_MANIFEST.json')}
def anchor(obj,eid,inventory=False):
 f=frames[eid]
 if inventory:obj['requested_source_seconds']=f['requested_source_seconds'];obj['actual_frame_seconds']=f['actual_frame_seconds_if_measured']
 else:obj['timestamp_seconds']=f['requested_source_seconds'];obj['actual_frame_seconds_if_measured']=f['actual_frame_seconds_if_measured']
 obj['evidence_ids']=[eid]
ledger=read(P/'TURN_LEDGER.json');r=ledger['turns'][3];draw=r['draws_and_searches'][1]
ids=['F0097.20','F0098.00','F0099.00','F0100.00','F0101.00']
for card,eid in zip(draw['cards_in_reveal_order'],ids):anchor(card,eid)
anchor(draw,ids[0]);draw['evidence_ids']=ids;draw['basis']='First resolved center-card reveal97.2 through final center reveal101.0; causal Copycat action onset remains in plays_in_order.'
inventory=read(P/'SEEN_CARD_INVENTORY.json')
for name,index,eid in [('Mega Sharpedo ex',0,'F0101.00'),('Cyrus',0,'F0099.00'),('Elegant Cape',0,'F0097.20'),('Lucky Ice Pop',2,'F0098.00')]:
 card=next(c for c in inventory['inventory'] if c['name']==name);anchor(card['occurrences'][index],eid,True)
save(P/'SEEN_CARD_INVENTORY.json',inventory)
guide=read(P/'GUIDE_UPDATE_SUPPLEMENT.json')
def unknown_preview():return {'type':None,'count':None,'available':False,'phase':'not_settled_or_visible_at_selected_boundary','limit':'Do not assign a typed preview/count to animation or an empty preview slot; later native evidence is separate.'}
for number in [6,12,18]:
 zone=ledger['turns'][number-1]['board_at_start']['owner']['energy_zone']
 if number in [6,18]:
  zone['this_turn']={'type':'Water','count':1,'available':None,'phase':'generation_animation_readiness_indeterminate','limit':'A Water symbol is visible in the large current orb; readiness at this precise animated instant is not established.'}
 zone['next']=unknown_preview()
 zone['limit_reason']='Selected fresh start is an exact animation instant; current-slot visible contents, readiness and next preview remain separate.'
 eid={6:'F0144.50',12:'F0244.50',18:'F0339.50'}[number];f=frames[eid]
 zone['generation_followup']={'evidence_ids':[eid],'requested_source_seconds':f['requested_source_seconds'],'actual_frame_seconds_if_measured':f['actual_frame_seconds_if_measured'],'this_turn':{'type':'Water','count':1,'available':True,'phase':'later_availability_supported'},'basis':'T18 later unused-Energy warning establishes Water remains available, without claiming an unobscured orb view.' if number==18 else 'Later retained native shows current Water selectable/available; this is separate from selected start instant.'}
 if number==12:zone['generation_followup']['next']={'type':'Water','count':1,'available':False,'phase':'later_settled_preview'}
 row=next(x for x in guide['owner_turn_start_observations'] if x['turn_number']==number);row['fresh_both_boards']['owner']['energy_zone']=copy.deepcopy(zone)
guide['original_submission']='worker_submission/SUBMISSION.json';guide['canonical_submission']='SUBMISSION_AFTER_INDEPENDENT_REPAIR.json';save(P/'GUIDE_UPDATE_SUPPLEMENT.json',guide)
save(P/'TURN_LEDGER.json',ledger)
note='\n\nIndependent bounded corrections: T4 Copycat center reveals are Cape97.2, Ice Pop98.0, Cyrus99.0, Misty100.0, Sharpedo101.0, each bound to measured native PTS. Names/order, hand endpoints and physical-copy counts are unchanged. T6/T18 selected starts show Water1 in the current orb during generation animation; exact readiness and smaller preview are qualified. T12 selected start has empty current slot and no readable settled preview. Later native availability/preview evidence remains separate, with T18 unused-Energy warning339.5 as later proof. T8/T14 original pending labels were already correct. Original19-file submission and rejected receipt are preserved.\n'
for name in ['REVIEW.md','TURN_TABLE.md','GUIDE_UPDATE_SUPPLEMENT.md','SEEN_CARD_INVENTORY.md']:
 with (P/name).open('a',encoding='utf-8') as f:f.write(note)
receipt={'repaired_utc':datetime.now(timezone.utc).isoformat(),'author':'/root','source_video':original['source_video'],'source_sha256':original['source_sha256'],'original_submission_preserved':'worker_submission/SUBMISSION.json','original_submission_sha256':sha(dest/'SUBMISSION.json'),'independent_rejection_sha256':sha(P/'independent_sol/CHECK_RESULT.json'),'corrections':['Five T4 Copycat native center reveal references, parent draw event, four matching inventory occurrences','T6/T18 visible current Water1 with readiness indeterminate and no guessed preview','T12 unreadable selected-start preview; later generated/preview evidence kept separate','Guide duplicates updated and canonical manifest filename identifies repair'],'changed_files':['TURN_LEDGER.json','SEEN_CARD_INVENTORY.json','GUIDE_UPDATE_SUPPLEMENT.json','REVIEW.md','TURN_TABLE.md','GUIDE_UPDATE_SUPPLEMENT.md','SEEN_CARD_INVENTORY.md'],'primary_manifest_unchanged':True,'no_new_extraction':True,'card_names_order_counts_energy_targets_and_outcome_unchanged':True,'independent_recheck_pending':True};save(P/'REPAIR_RECEIPT.json',receipt)
effective=copy.deepcopy(original);effective['files']={n:sha(P/n) for n in original['files']};effective['files']['REPAIR_RECEIPT.json']=sha(P/'REPAIR_RECEIPT.json');effective['original_submission_preserved']='worker_submission/SUBMISSION.json';effective['repair_receipt']='REPAIR_RECEIPT.json';save(P/'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json',effective)
visual=read(P/'LEAD_VISUAL_CHECK.json');visual['evidence']+=['turn_evidence/t0097.20.jpg','turn_evidence/t0098.00.jpg','turn_evidence/t0099.00.jpg','turn_evidence/t0100.00.jpg','turn_evidence/t0101.00.jpg','turn_evidence/t0143.50.jpg','turn_evidence/t0187.50.jpg','turn_evidence/t0243.50.jpg','turn_evidence/t0269.50.jpg','turn_evidence/t0337.80.jpg','turn_evidence/t0144.50.jpg','turn_evidence/t0338.50.jpg'];visual['observations']+=' Root additionally directly viewed five centerCopycat reveals and five selectedstartEnergyorbs. T8/T12/T14 currentempty; T6/T18 currentWater1visible with animation/readinessqualified. Later338.5attackmodal obscuresorb, so availability is corroborated separately by actual unusedEnergywarning339.5, as independently checked.';save(P/'LEAD_VISUAL_CHECK.json',visual)
print(sha(P/'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json'))
