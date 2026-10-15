"""Verify delivered local records without reading archived video contents."""
from pathlib import Path
import csv,json
from datetime import datetime,timezone
b=Path(__file__).resolve().parent;r=b.parent.parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
ctx=read(b/'OWNER_CONTEXT.json')
rows=list(csv.DictReader((r/'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig',newline='')))
loc=read(r/'MEDIA_LOCATIONS.json')
checked=[];issues=[];concurrent_updates=[]
for video in ctx['selected_sources']:
 p=b/Path(video).stem
 source=read(p/'SOURCE.json')
 index=[x for x in rows if x['Video']==video]
 assert len(index)==1,video
 move=read(p/('MOVE_RECEIPT.'+video+'.json')) if (p/('MOVE_RECEIPT.'+video+'.json')).exists() else {}
 lead=read(p/'LEAD_ACCEPTANCE.json') if (p/'LEAD_ACCEPTANCE.json').exists() else {}
 external=read(p/'LIVE_GAME_SAVE_VERIFICATION.json') if (p/'LIVE_GAME_SAVE_VERIFICATION.json').exists() else {}
 mapping=[x for x in loc.get('moved',[]) if x['filename']==video]
 checks={'index_reviewed':index[0]['Status']=='Reviewed','index_location':index[0]['Location']=='Reviewed/'+video,
 'original_exists':(r/'Reviewed'/video).is_file(),'original_size':(r/'Reviewed'/video).stat().st_size==source['bytes'] if (r/'Reviewed'/video).is_file() else False,
 'lead_accepted':lead.get('accepted') is True,'archive_identity':move.get('identity_match') is True and move.get('sha256_before')==source['sha256']==move.get('sha256_after'),
 'current_mapping':len(mapping)==1 and Path(mapping[0]['current_path'])==r/'Reviewed'/video,
 'external_reload':external.get('reloaded') is True and (external.get('count')==1 or external.get('matching_entries')==1)}
 checked.append({'source':video,'checks':checks,'source_sha256':source['sha256']})
 issues.extend(video+': '+k for k,v in checks.items() if not v)
for previous in ctx['excluded_existing_assignments']:
 current=[x for x in rows if x['Video']==previous['Video']]
 if len(current)!=1:issues.append('Other assignment index row missing/duplicate: '+previous['Video']);continue
 if current[0]!=previous:
  other=r/'Recording_QA/BATCH_2026-10-09_NEW_UPLOADS'/Path(previous['Video']).stem/'LEAD_ACCEPTANCE.json'
  accepted=read(other) if other.exists() else {}
  attributed=accepted.get('accepted') is True and str(other) in current[0]['Review evidence']
  concurrent_updates.append({'source':previous['Video'],'current_status':current[0]['Status'],'separate_batch_acceptance':str(other),'attributed_to_existing_assignment':attributed})
  if not attributed:issues.append('Unattributed change to other assignment: '+previous['Video'])
report={'checked_utc':datetime.now(timezone.utc).isoformat(),'complete':not issues,'sources':checked,'issues':issues,'concurrent_updates':concurrent_updates,'original_video_contents_read':False,'basis':'Initial frozen SOURCE plus pre/post move SHA receipts, file metadata, shared index/map and live-reload receipts. Other assignments compared with intake rows; concurrent completions attributed to their separate accepted batch and preserved.'}
(b/'FINAL_LOCAL_AUDIT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'complete':not issues,'source_count':len(checked),'issues':issues}))
