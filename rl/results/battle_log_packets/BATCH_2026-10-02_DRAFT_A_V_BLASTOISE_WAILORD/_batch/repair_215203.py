import copy,json,shutil
from datetime import datetime,timezone
from pathlib import Path
from validate_packet import read,sha
B=Path(__file__).resolve().parent;P=B/'20261002_215203000_iOS_shark_sol'
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not read(P/'independent_sol/CHECK_RESULT.json')['accepted']
assert not(P/'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json').exists()
original=read(P/'SUBMISSION.json');dest=P/'worker_submission';assert not dest.exists();dest.mkdir()
for n,h in original['files'].items():
 assert sha(P/n)==h,n
 shutil.copy2(P/n,dest/n)
shutil.copy2(P/'SUBMISSION.json',dest/'SUBMISSION.json')
frames={f['evidence_id']:f for f in read(P/'independent_sol/EXTRACTION_MANIFEST.json')}
ledger=read(P/'TURN_LEDGER.json');research=ledger['turns'][0]['plays_in_order'][0];research['hand_count_after']=5
for number,name,eid in [(1,"Professor's Research",'independent_sol:F0035.50'),(7,'Poké Ball','independent_sol:F0157.50')]:
 r=ledger['turns'][number-1];play=next(x for x in r['plays_in_order'] if x['card_name']==name);f=frames[eid]
 play['timestamp_seconds']=f['requested_source_seconds'];play['actual_frame_seconds_if_measured']=f['actual_frame_seconds_if_measured'];play['evidence_ids'].insert(0,eid)
 play['named_card_face_anchor']={'evidence_id':eid,'requested_source_seconds':f['requested_source_seconds'],'actual_frame_seconds_if_measured':f['actual_frame_seconds_if_measured'],'basis':'Directly readable named played card at measured native instant; earlier retained frames can establish preface/action continuity.'}
 play['limit_reason']='Named face anchor is exact selected native PTS; action input onset remains approximate. Concealed Research draws/search identity remain unknown.'
save(P/'TURN_LEDGER.json',ledger)
evidence=read(P/'TURN_EVIDENCE.json')
for number,eid,observation in [(1,'independent_sol:F0035.50','Direct opponent Research played-card face, with concealed draw names kept null'),(7,'independent_sol:F0157.50','Direct opponent Poke Ball played-card face; hidden searched identity remains null')]:
 f=copy.deepcopy(frames[eid]);f.update({'role':'independent_bounded_named_card_correction','turn_number':number,'who_played':'opponent','observation':observation,'selected_for_start_hand':False,'before_first_play':None,'unzoomed':False,'suitability_or_limit':'Named card center display; not owner start-hand evidence. Original primary capture manifest is preserved.'});evidence['frames'].append(f)
save(P/'TURN_EVIDENCE.json',evidence)
note='\n\nIndependent bounded corrections: T1 Research completed-action hand count is5 after two concealed draws;3 is the intermediate post-consumption/pre-draw phase, followed by Frigibax leaving4. Direct played-card face anchors are independent_sol:F0035.50, measured35.5067 Research, and independent_sol:F0157.50, measured157.505 T7 Poke Ball. Earlier native references remain continuity evidence and are not presented as readable faces. Hidden drawn/searched identities remain unknown. Four tiny independent captures are retained separately, with only these two selected for correction. Original19-file first pass and rejected receipt remain preserved.\n'
for name in ['REVIEW.md','TURN_TABLE.md']:
 with (P/name).open('a',encoding='utf-8') as f:f.write(note)
receipt={'repaired_utc':datetime.now(timezone.utc).isoformat(),'author':'/root','source_video':original['source_video'],'source_sha256':original['source_sha256'],'original_submission_preserved':'worker_submission/SUBMISSION.json','original_submission_sha256':sha(dest/'SUBMISSION.json'),'independent_rejection_sha256':sha(P/'independent_sol/CHECK_RESULT.json'),'corrections':['T1 Research completed hand count3to5','T1 Research measured native centerface35.5067','T7 Ball measured native centerface157.505'],'changed_files':['TURN_LEDGER.json','TURN_EVIDENCE.json','REVIEW.md','TURN_TABLE.md'],'primary_manifest_unchanged':True,'independent_extraction_manifest_sha256':sha(P/'independent_sol/EXTRACTION_MANIFEST.json'),'retained_native_frames_union':141,'guide_and_inventory_semantics_unchanged':True,'results_hidden_identities_and_move_order_unchanged':True,'independent_recheck_pending':True};save(P/'REPAIR_RECEIPT.json',receipt)
effective=copy.deepcopy(original);effective['files']={n:sha(P/n) for n in original['files']};effective['files']['REPAIR_RECEIPT.json']=sha(P/'REPAIR_RECEIPT.json');effective['original_submission_preserved']='worker_submission/SUBMISSION.json';effective['repair_receipt']='REPAIR_RECEIPT.json';save(P/'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json',effective)
visual=read(P/'LEAD_VISUAL_CHECK.json');visual['evidence']+=['independent_sol/turn_evidence/t0035.50.jpg','independent_sol/turn_evidence/t0157.50.jpg'];visual['observations']+=' Root directly inspected new source-bound center Research35.5 and PokeBall157.5 face frames. Correct Research completed handcount5 reconciles two concealed draws then Frigibax4; identities remain unknown.';save(P/'LEAD_VISUAL_CHECK.json',visual)
print(sha(P/'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json'))
