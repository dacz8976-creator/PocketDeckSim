import json,subprocess,sys
from datetime import datetime,timezone
from validate_packet import BATCH,CORE,read,sha,local

p=BATCH/'20261002_205731000_iOS_auto_sol'
out=p/'GUIDE_COMPLETION_RECEIPT.json'
assert not out.exists()
s=read(p/'SOURCE.json');g=read(p/'GUIDE_UPDATE_ACCEPTANCE.json');c=read(p/'COMPLETION_RECEIPT.json')
assert c['accepted'] and g['accepted'] and g['guide_update_checked']
assert c['source_sha256']==g['source_sha256']==s['sha256']
for name,expected in read(p/'SUBMISSION.json')['files'].items():assert sha(p/name)==expected
for name,expected in g['accepted_files'].items():assert sha(p/name)==expected
check=local(p,g['independent_check']);assert sha(check)==g['independent_check_sha256']
cmd=[sys.executable,str(BATCH.parent.parent/'Review_Log/review_log.py'),'--root',str(BATCH.parent.parent),'record','--video',s['video_basename'],'--reviewer','/root guide addendum','--status','full_battle_review_complete','--scope','Full accepted18-turn computer battle plus independently checked October2 evening guide addendum for this current eight-game batch: fresh boards, opponent-turn owner promotion, seen-card copies and per-turn Auto actor.','--notes','Supplement preserves original full review, first-pass submission, lead acceptance and archive receipt. Timing clarification preserves prior supplement files and uses null exact times for composite end-state observations. Local batch/index only, no human Pause Games or Ladder entry. Stored source hash reused, no archived video rehash.','--imported-saved-record','--known-sha256',s['sha256']]
for name in list(dict.fromkeys(CORE+['LEAD_ACCEPTANCE.json','COMPLETION_RECEIPT.json','ROUTING.json','GUIDE_UPDATE_ACCEPTANCE.json',g['independent_check']]+list(g['accepted_files']))):cmd+=['--evidence',str(local(p,name))]
result=subprocess.run(cmd,check=True,capture_output=True,text=True,encoding='utf-8')
events=[read(f) for f in (BATCH.parent.parent/'Review_Log/events').glob('*.json')]
latest=max((e for e in events if e.get('video_basename')==s['video_basename']),key=lambda e:e['logged_at_utc'])
assert latest['status']=='full_battle_review_complete' and latest['video_sha256']==s['sha256']
receipt={'accepted':True,'guide_update_checked':True,'registered_utc':datetime.now(timezone.utc).isoformat(),'source_video':s['video_basename'],'source_sha256':s['sha256'],'guide_acceptance_sha256':sha(p/'GUIDE_UPDATE_ACCEPTANCE.json'),'supplement_event_id':latest['event_id'],'original_core_completion_event_id':c['completion_event_id'],'core_completion_receipt_preserved':True,'archived_movie_not_reread':True,'actual_destination':'local_review_batch_and_BATTLE_REVIEW_INDEX','external_game_entry_requested':False}
out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Accepted guide addendum registered locally: '+s['video_basename'])
