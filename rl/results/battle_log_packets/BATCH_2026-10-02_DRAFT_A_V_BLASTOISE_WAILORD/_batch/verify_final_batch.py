"""Verify accepted evidence, registration and archival without reading movies."""
import csv,json
from datetime import datetime,timezone
from pathlib import Path
from validate_packet import BATCH,read,sha,local,validate

ROOT=BATCH.parent.parent
AUTO=['205230','205731','210612','210952','211613']
MANUAL=['214254','215203','215825']
GUIDE=['GUIDE_UPDATE_SUPPLEMENT.json','GUIDE_UPDATE_SUPPLEMENT.md','SEEN_CARD_INVENTORY.json','SEEN_CARD_INVENTORY.md']
names={f'20261002_{t}000_iOS.MP4' for t in AUTO+MANUAL}
with (ROOT/'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig',newline='') as f:index=list(csv.DictReader(f))
assert [r for r in index if r['Video'] not in names]==read(BATCH/'INDEX_UNRELATED_BEFORE_FINAL_CHECKS.json')['rows'],'Unrelated index rows changed'
assert len(index)==137 and len([r for r in index if r['Video'] not in names])==129
events=[read(p) for p in (ROOT/'Review_Log/events').glob('*.json')]
media=read(ROOT/'MEDIA_LOCATIONS.json')['moved']
results=[]
for t in AUTO+MANUAL:
 name=f'20261002_{t}000_iOS.MP4';p=BATCH/(Path(name).stem+('_auto_sol' if t in AUTO else '_shark_sol'))
 source=read(p/'SOURCE.json');lead=read(p/'LEAD_ACCEPTANCE.json');completion=read(p/'COMPLETION_RECEIPT.json');guide=read(p/'GUIDE_UPDATE_ACCEPTANCE.json')
 assert lead['accepted'] and completion['accepted'] and guide['accepted'] and guide['guide_update_checked']
 assert source['video_basename']==name and source['classification']=='computer_battle'
 assert lead['full_reviewer']!=lead['independent_reviewer']
 assert lead['ranked_ladder_eligible'] is False and lead['human_pause_games_eligible'] is False
 assert lead['actual_destination']=='local_review_batch_and_BATTLE_REVIEW_INDEX' and lead['requested_log'] is None
 structural=validate(p,lead.get('submission_manifest','SUBMISSION.json'))
 assert structural['submission_manifest_sha256']==lead['submission_manifest_sha256']
 for receipt,check_key in [(lead,'independent_check'),(guide,'independent_check')]:
  check_path=local(p,receipt[check_key]);assert sha(check_path)==receipt['independent_check_sha256']
  check=read(check_path);assert check['accepted'] and not check['remaining_coverage_gaps'] and not check['unverified_material_claims']
  assert check['source_video']==name and check['source_sha256']==source['sha256']
  if norm:=check.get('format_normalization'):assert sha(local(p,norm['original_check']))==norm['original_check_sha256']
 guide_manifest=local(p,guide['checked_submission_manifest']);assert sha(guide_manifest)==guide['checked_submission_manifest_sha256']
 assert set(GUIDE)==set(guide['accepted_files'])
 for n,h in guide['accepted_files'].items():assert sha(local(p,n))==h,n
 if t=='205731':
  addition=read(p/'GUIDE_COMPLETION_RECEIPT.json');assert addition['accepted'] and addition['guide_acceptance_sha256']==sha(p/'GUIDE_UPDATE_ACCEPTANCE.json')
 else:assert completion['latest_guide_additions_accepted'] and completion['guide_acceptance_sha256']==sha(p/'GUIDE_UPDATE_ACCEPTANCE.json')
 move=read(p/f'MOVE_RECEIPT.{name}.json');assert move['identity_match'] and move['sha256_before']==move['sha256_after']==source['sha256'] and move['bytes']==source['bytes']
 assert not (ROOT/name).exists() and (ROOT/'Reviewed'/name).stat().st_size==source['bytes']
 mapping=[m for m in media if m['filename']==name];assert len(mapping)==1
 assert mapping[0]['sha256']==source['sha256'] and mapping[0]['bytes']==source['bytes']
 assert Path(mapping[0]['current_path']).resolve()==(ROOT/'Reviewed'/name).resolve(),'Media mapping path differs'
 current=[r for r in index if r['Video']==name];assert len(current)==1 and current[0]['Status']=='Reviewed'
 assert current[0]['Location'].replace('\\','/').endswith('Reviewed/'+name)
 assert all(n in current[0]['Review evidence'] for n in GUIDE)
 latest=max([e for e in events if e.get('video_basename')==name],key=lambda e:e['logged_at_utc'])
 assert latest['status']=='full_battle_review_complete' and latest['video_sha256']==source['sha256']
 assert all(any(Path(x).name==n for x in latest['evidence_paths']) for n in GUIDE)
 preserved=[]
 for folder,manifest in [('worker_submission','SUBMISSION.json'),('guide_submission_before_repair','GUIDE_UPDATE_SUBMISSION.json'),('guide_submission_before_timing_repair','GUIDE_UPDATE_SUBMISSION.json'),('guide_repair_before_binding_fix','GUIDE_UPDATE_SUBMISSION_AFTER_REPAIR.json')]:
  old=p/folder/manifest
  if old.exists():
   for n,h in read(old)['files'].items():assert sha(local(p/folder,n))==h,'Preserved original changed: '+n
   preserved.append(folder)
 inventory=read(p/'SEEN_CARD_INVENTORY.json')
 count_keys=['minimum_distinct_owner_cards_observed','total_minimum_distinct_owner_deck_cards_seen','observed_distinct_card_slot_lower_bound','minimum_distinct_cards_source_supported','minimum_total_distinct_owner_cards_seen']
 minimum=next((inventory[k] for k in count_keys if k in inventory),None)
 assert isinstance(minimum,int) and 0<minimum<=20,'Unrecognized seen-card lower bound'
 results.append({'source':name,'pilot':'Auto' if t in AUTO else 'Dustin','outcome':lead['outcome'],'turn_rows':structural['turn_rows'],'owner_turns':structural['owner_turns'],'native_frames':structural['native_frames_checked'],'native_lossless_crops':structural['lossless_native_crops_checked'],'minimum_distinct_owner_cards_seen':minimum,'accepted_core_manifest':lead['submission_manifest'],'accepted_guide_manifest':guide['checked_submission_manifest'],'preserved_prior_submissions':preserved,'movie_bytes':source['bytes'],'movie_sha256':source['sha256'],'archive_identity_verified':True,'latest_index_and_event_verified':True})
assert sum(r['turn_rows'] for r in results)==129
assert sum(r['owner_turns'] for r in results)==65
guide_source=read(BATCH/'GUIDE_UPDATE_RECEIPT.json')
out={'verified_utc':datetime.now(timezone.utc).isoformat(),'passed':True,'scope':'Only eight selected current computer comparison recordings','accepted_games':8,'accepted_latest_guide_supplements':8,'turn_rows':129,'owner_turns':65,'native_frames':sum(r['native_frames'] for r in results),'lossless_native_crops':sum(r['native_lossless_crops'] for r in results),'index_total_rows':137,'unrelated_index_rows_verified_unchanged':129,'online_game_entries_created':0,'movie_contents_read_by_this_verification':False,'original_movie_integrity_basis':'Verified before/after SHA256 archive receipts plus exact current filename and logical size; no movie rehydration','results':results}
(BATCH/'FINAL_BATCH_VERIFICATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k not in ['results']},ensure_ascii=False))
