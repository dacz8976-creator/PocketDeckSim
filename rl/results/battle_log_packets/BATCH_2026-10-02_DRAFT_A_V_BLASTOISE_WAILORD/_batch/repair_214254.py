import copy,json,shutil
from datetime import datetime,timezone
from pathlib import Path
from validate_packet import read,sha
B=Path(__file__).resolve().parent;P=B/'20261002_214254000_iOS_shark_sol'
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert read(P/'independent_sol/CHECK_RESULT.json')['accepted'] is False
assert not(P/'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json').exists()
original=read(P/'SUBMISSION.json');dest=P/'worker_submission'
if not dest.exists():
 dest.mkdir()
 for n,h in original['files'].items():
  assert sha(P/n)==h,n
  shutil.copy2(P/n,dest/n)
 shutil.copy2(P/'SUBMISSION.json',dest/'SUBMISSION.json')
else:
 assert sha(dest/'SUBMISSION.json')==sha(P/'SUBMISSION.json')
 for n,h in original['files'].items():assert sha(dest/n)==h,n
 for n in ['TURN_LEDGER.json','REVIEW.md','TURN_TABLE.md','SEEN_CARD_INVENTORY.json','SEEN_CARD_INVENTORY.md']:shutil.copy2(dest/n,P/n)
frames={f['evidence_id']:f for f in read(P/'EXTRACTION_MANIFEST.json')}
def anchor(obj,eid):
 f=frames[eid];obj['timestamp_seconds']=f['requested_source_seconds'];obj['decoded_pts_seconds']=f['actual_frame_seconds_if_measured'];obj['evidence_ids']=[eid]
ledger=read(P/'TURN_LEDGER.json');r=ledger['turns'][17];draw=r['draws_and_searches'][1]
for card,eid in zip(draw['cards_in_reveal_order'],['F0427.40','F0428.40','F0429.40','F0430.40']):anchor(card,eid)
anchor(draw,'F0427.40');draw['evidence_ids']=[c['evidence_ids'][0] for c in draw['cards_in_reveal_order']];draw['linked_play_order']=1
old=r['plays_in_order'];new=[old[1],old[2],old[0],old[3]]
for number,play in enumerate(new,1):play['order']=number
anchor(new[0],'F0427.40');new[0]['limit_reason']='Copycat is first voluntary action, with held card at420.4 and commitment visible around421-422 in the continuous locator. The retained427.4 native anchor proves the first resolved reveal, not exact touch timing.'
anchor(new[1],'F0432.40');new[1]['prompt_text']='The conditions for using this Item card have not been met'
anchor(new[2],'F0433.40');new[2]['evidence_ids'].append('F0434.40');new[2]['basis']='Native433.408 attachment glow and emptied current Energy slot after failed Ball; native434.410 corroborates fourth Water.'
r['plays_in_order']=new
r['observed_course']='Copycat first shuffles3 and reveals Misty, Poke Ball, Cyrus, Lapras; Poke Ball attempt rejected and retained; ordinary fourth Water then attaches to Active rainbow Ninetales; Binding80.'
for number,eid in [(4,'F0118.40'),(8,'F0185.40')]:
 end=ledger['turns'][number-1]['owner_hand_end'];end['evidence_ids']=[eid];end['basis']='Retained native before-ending action establishes membership and count; no hand-changing action follows before turn end.'
save(P/'TURN_LEDGER.json',ledger)
review=(P/'REVIEW.md').read_text(encoding='utf-8')
oldtext='Owner turn 18 draws Cyrus, gives Active rainbow Ninetales its fourth Water, then uses Copycat.'
assert oldtext in review
review=review.replace(oldtext,'Owner turn 18 draws Cyrus and first uses Copycat.')
oldtext='A Poke Ball attempt receives the conditions-not-met rejection and remains in hand, with no search or discard.'
assert oldtext in review
review=review.replace(oldtext,oldtext+' The ordinary fourth Water then attaches to Active rainbow Ninetales, after the rejected Ball attempt.')
note='\n\nIndependent correction: T18 native Copycat reveals are Misty427.4, Poke Ball428.4, Cyrus429.4 and Lapras430.4. Action order is Copycat, failed Ball at432.4, normal fourth Water at433.4, then Binding Snow. Exact touchscreen input timing remains approximate; native decoder PTS is retained separately. T4/T8 ending hand IDs are now explicit. Frozen first-pass files and the rejected independent receipt remain preserved.\n'
(P/'REVIEW.md').write_text(review+note,encoding='utf-8')
table=(P/'TURN_TABLE.md').read_text(encoding='utf-8');oldtext='Fourth Water to Active Ninetales; Copycat shuffles 3 and draws Misty, Poke Ball, Cyrus, Lapras. Poke Ball attempt rejected, retained. Binding 80.'
assert oldtext in table
table=table.replace(oldtext,r['observed_course']);(P/'TURN_TABLE.md').write_text(table+note,encoding='utf-8')
inventory=read(P/'SEEN_CARD_INVENTORY.json');ball=next(c for c in inventory['cards'] if c['name']=='Poké Ball');anchor(ball['observations'][1],'F0428.40');save(P/'SEEN_CARD_INVENTORY.json',inventory)
md=(P/'SEEN_CARD_INVENTORY.md').read_text(encoding='utf-8');assert '429.4s Copycat draw T18' in md;(P/'SEEN_CARD_INVENTORY.md').write_text(md.replace('429.4s Copycat draw T18','428.4s Copycat draw T18'),encoding='utf-8')
receipt={'repaired_utc':datetime.now(timezone.utc).isoformat(),'author':'/root','source_video':original['source_video'],'source_sha256':original['source_sha256'],'original_submission_preserved':'worker_submission/SUBMISSION.json','original_submission_sha256':sha(dest/'SUBMISSION.json'),'independent_rejection_sha256':sha(P/'independent_sol/CHECK_RESULT.json'),'corrections':['T18 four individual Copycat reveal anchors and Ball inventory anchor','T18 Copycat/Ball/ordinary Water/attack order and exact visible Ball rejection banner','T4/T8 existing before-end hand evidence IDs made explicit'],'changed_files':['TURN_LEDGER.json','REVIEW.md','TURN_TABLE.md','SEEN_CARD_INVENTORY.json','SEEN_CARD_INVENTORY.md'],'primary_manifest_unchanged':True,'no_new_extraction':True,'names_results_end_hand_and_copy_counts_unchanged':True,'independent_recheck_pending':True}
save(P/'REPAIR_RECEIPT.json',receipt)
effective=copy.deepcopy(original);effective['files']={n:sha(P/n) for n in original['files']};effective['files']['REPAIR_RECEIPT.json']=sha(P/'REPAIR_RECEIPT.json');effective['original_submission_preserved']='worker_submission/SUBMISSION.json';effective['repair_receipt']='REPAIR_RECEIPT.json';save(P/'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json',effective)
visual=read(P/'LEAD_VISUAL_CHECK.json');visual['evidence']+=['turn_evidence/t0427.40.jpg','turn_evidence/t0428.40.jpg','turn_evidence/t0429.40.jpg','turn_evidence/t0430.40.jpg','turn_evidence/t0432.40.jpg','turn_evidence/t0433.40.jpg'];visual['observations']+=' Root additionally directly inspected all four native Copycat center reveals, the failed Ball banner at432.4 and subsequent Water attachment glow/emptied current slot at433.4. Correct chronology is Copycat, failed Ball, normal Water, attack.';save(P/'LEAD_VISUAL_CHECK.json',visual)
print(sha(P/'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json'))
