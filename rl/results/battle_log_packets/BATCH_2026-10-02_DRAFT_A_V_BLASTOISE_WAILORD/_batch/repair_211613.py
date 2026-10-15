import copy,json,shutil
from datetime import datetime,timezone
from pathlib import Path
from validate_packet import read,sha
B=Path(__file__).resolve().parent;P=B/'20261002_211613000_iOS_auto_sol'
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not read(P/'independent_sol/CHECK_RESULT.json')['accepted']
assert not(P/'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json').exists()
original=read(P/'SUBMISSION.json');dest=P/'worker_submission';assert not dest.exists();dest.mkdir()
for n,h in original['files'].items():
 assert sha(P/n)==h,n
 shutil.copy2(P/n,dest/n)
shutil.copy2(P/'SUBMISSION.json',dest/'SUBMISSION.json')
ledger=read(P/'TURN_LEDGER.json');r=ledger['turns'][7]
r['timing']['end_after_resolution_seconds']=164.0;r['timing']['source_interval_seconds'][1]=164.0
r['board_after']['phase']='After actions, before T8 turn-end expiry: restriction icon still visible at162.502. Separate retained164.002 frame establishes post-expiry T9 handoff.'
effect=copy.deepcopy(r['board_at_start']['opponent']['board_effects'][0]);effect['evidence_ids']=['F0162.50'];effect['basis']='Direct prohibition icon still visible at162.502; expiry confirmed separately at164.002 next-turn handoff.'
r['board_after']['opponent']['board_effects']=[effect]
r['automatic_events_in_order'][0]['evidence_ids']=['F0164.00','F0167.20']
r['automatic_events_in_order'][0]['basis']='Logical end-T8 expiry is confirmed by native164.002 displayed turn9 with icon absent;162.502 is still pre-expiry.'
r['post_expiry_confirmation']={'evidence_id':'F0164.00','requested_source_seconds':164.0,'actual_frame_seconds_if_measured':164.002,'turn_number_displayed':9,'binding_snow_icon_present':False,'phase':'Next-turn handoff before owner normal draw; physical Pokemon/HP/Energy remain unchanged from162.5.'}
r['turn_evidence_ids'].append('F0164.00');save(P/'TURN_LEDGER.json',ledger)
evidence=read(P/'TURN_EVIDENCE.json')
for frame in evidence['frames']:
 if frame['evidence_id']=='F0162.50':
  frame['role']=[x for x in frame['role'] if x!='board_after_resolution']+['board_after_actions_before_expiry'];frame['observation']='T8 actions complete; prohibition icon still visible before turn-end handoff.'
 if frame['evidence_id']=='F0164.00':
  frame['role'].append('previous_turn_post_expiry_confirmation');frame['observation']='Displayed current turn9; prohibition icon absent, confirming end-T8 expiry before normal owner draw.'
save(P/'TURN_EVIDENCE.json',evidence)
review=(P/'REVIEW.md').read_text(encoding='utf-8');review=review.replace('## Turn 8: opponent (157–162.5 seconds)','## Turn 8: opponent (157–164.0 seconds)')
review=review.replace('"evidence_ids": ["F0162.50", "F0167.20"]','"evidence_ids": ["F0164.00", "F0167.20"]')
assert 'Resolved ending boards at 162.5:' in review
review=review.replace('Resolved ending boards at 162.5:','Boards after actions at162.5, before turn-end expiry: the prohibition icon is still present. Native164.002 shows displayed turn9 and the icon absent, establishing the post-expiry endpoint. Physical Pokemon, HP and attached Energy are unchanged across this handoff:')
note='\n\nIndependent T8 boundary correction:162.502 remains pre-expiry;164.002 is the retained next-turn confirmation of end-T8 Binding Snow expiry. The current board snapshot keeps its truthful162.5 timestamp and visible restriction; automatic expiry has separate164.0 evidence. No card identities, actions, inventory counts or result changed. Original first pass and rejected receipt are preserved.\n'
(P/'REVIEW.md').write_text(review+note,encoding='utf-8')
with (P/'TURN_TABLE.md').open('a',encoding='utf-8') as f:f.write(note)
receipt={'repaired_utc':datetime.now(timezone.utc).isoformat(),'author':'/root','source_video':original['source_video'],'source_sha256':original['source_sha256'],'original_submission_preserved':'worker_submission/SUBMISSION.json','original_submission_sha256':sha(dest/'SUBMISSION.json'),'independent_rejection_sha256':sha(P/'independent_sol/CHECK_RESULT.json'),'corrections':['T8 pre-expiry board phase and visible restriction retained at162.502','End-T8 expiry separately anchored to retained164.002 displayed T9 without restriction','Native frame roles and narrative distinguish pre-expiry and post-expiry instants'],'changed_files':['TURN_LEDGER.json','TURN_EVIDENCE.json','REVIEW.md','TURN_TABLE.md'],'guide_and_inventory_semantics_unchanged':True,'primary_manifest_unchanged':True,'no_new_extraction':True,'independent_recheck_pending':True};save(P/'REPAIR_RECEIPT.json',receipt)
effective=copy.deepcopy(original);effective['files']={n:sha(P/n) for n in original['files']};effective['files']['REPAIR_RECEIPT.json']=sha(P/'REPAIR_RECEIPT.json');effective['original_submission_preserved']='worker_submission/SUBMISSION.json';effective['repair_receipt']='REPAIR_RECEIPT.json';save(P/'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json',effective)
visual=read(P/'LEAD_VISUAL_CHECK.json');visual['evidence']+=['turn_evidence/t0162.50.jpg','turn_evidence/t0164.00.jpg'];visual['observations']+=' Root directly compared162.5 icon-present/opponent phase with164.0 displayed turn9/icon absent, confirming separate pre-expiry snapshot and post-expiry evidence.';save(P/'LEAD_VISUAL_CHECK.json',visual)
print(sha(P/'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json'))
