import csv,json
from datetime import datetime,timezone
from pathlib import Path
b=Path(__file__).resolve().parent;root=b.parent.parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
names=read(b/'OWNER_CONTEXT.json')['selected_sources']
index={x['Video']:x for x in csv.DictReader((root/'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig',newline=''))}
rows=[]
for name in names:
 p=b/Path(name).stem;c=p/'independent_sol/CHECK_RESULT.json';live=p/'LIVE_GAME_SAVE_VERIFICATION.json'
 liveproof=read(live) if live.exists() else {}
 checkproof=read(c) if c.exists() else {}
 independentok=checkproof.get('accepted') is True or ('accepted' not in checkproof and checkproof.get('status') in ['accepted','accepted_with_recording_limits'])
 row={'video':name,'source_bound':(p/'SOURCE.json').exists(),'index_status':index.get(name,{}).get('Status'),'review_written':(p/'REVIEW.md').exists(),'independent_accepted':independentok,'lead_accepted':(p/'LEAD_ACCEPTANCE.json').exists(),'archived':(root/'Reviewed'/name).exists(),'external_verified':liveproof.get('reloaded') is True and (liveproof.get('saved') is True or (liveproof.get('matching_entries')==1 and liveproof.get('note_exact_match') is True))}
 if (p/'PAUSE_GAME.json').exists():
  g=read(p/'PAUSE_GAME.json')
  if not g.get('is_template',True):row['outcome']=g.get('outcome');row['deck_status']=read(p/'DECK_USED.json').get('exact_list_status')
 if (p/'TURN_LEDGER.json').exists():
  l=read(p/'TURN_LEDGER.json');row['turn_rows']=len(l.get('turns',[]))
 rows.append(row)
result={'checked_utc':datetime.now(timezone.utc).isoformat(),'scope':'Frozen newest8 uploads; older active assignments excluded','source_bound_count':sum(x['source_bound'] for x in rows),'reviewed_archived_count':sum(x['archived'] for x in rows),'live_verified_count':sum(x['external_verified'] for x in rows),'videos':rows}
(b/'BATCH_STATUS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='videos'}))
