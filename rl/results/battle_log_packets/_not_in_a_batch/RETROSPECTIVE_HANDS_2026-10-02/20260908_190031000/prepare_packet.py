from pathlib import Path
import json,re,copy
P=Path(__file__).resolve().parent
T=P.parents[2]/'Review_Log'/'templates'/'pause_games'
O=Path('C:/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder/video-review-coordinator-2026-09-09/previously-finished-audit/first-altaria')
S=json.loads((O/'SOURCE.json').read_text(encoding='utf-8'))
def save(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
source={'video_basename':S['filename'],'sha256':S['sha256'],'source_json':'SOURCE_REFERENCE.json'}
def template(n):
 d=json.loads((T/(n+'.template.json')).read_text(encoding='utf-8-sig'));d.update(is_template=False,game_id='20260908_190031000',sources=[source],capture_status='incomplete_review');return d
ref={'source':S['filename'],'sha256':S['sha256'],'logical_bytes':S['bytes'],'duration_seconds':S['duration_seconds'],'current_path':str(Path('Reviewed')/S['filename']),'frozen_binding_path':str(O/'SOURCE.json'),'current_source_verification_status':'waiting_for_once_only_read','accepted_review':str(O/'REVIEW.md'),'retained_evidence_status':'All47audit images585x1266; reduced locator only, not native hand evidence','main_status':'Reviewed','scope':'Historical field supplement; no old packet or result changes'}
save('SOURCE_REFERENCE.json',ref)
old=(O/'REVIEW.md').read_text(encoding='utf-8');rows=[]
for m in re.finditer(r'^### .*?turn (\d+)\b.*?(?=^### |^## |\Z)',old,re.M|re.S):rows.append({'turn_number':int(m.group(1)),'accepted_source_line':old[:m.start()].count('\n')+1,'verbatim_accepted_section':m.group(0).rstrip(),'basis':'inherited accepted prose, not completed new source observation'})
save('INHERITED_TURNS.json',{'source':S['filename'],'accepted_review':str(O/'REVIEW.md'),'rows':rows,'scope':'Accepted turn account preserved as scaffolding; added fields require source inspection'})
l=template('TURN_LEDGER');row=l['turns'][0];l['turns']=[]
for i in range(1,5):
 r=copy.deepcopy(row);r.update(turn_number=i,who_played='owner' if i%2==0 else 'opponent',source_video=S['filename'],inherited_accepted_turn=rows[i-1],limits=['Native added fields are awaiting source read and inspection.']);l['turns'].append(r)
save('TURN_LEDGER.json',l)
for n in ['PAUSE_GAME','DECK_USED','TURN_EVIDENCE']:save(n+'.json',template(n))
save('HAND_SUPPLEMENT.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':'20260908_190031000','sources':[source],'target_rows':2,'target_turn_numbers':[2,4],'capture_status':'incomplete_review','rows':[],'limits':['Native hand fields awaiting source delivery.']})
save('UNCERTAINTIES.json',{'capture_status':'incomplete_review','review_gaps':['Native setup and turn capture pending once-only source read.'],'recording_limits':['Hidden opponent unplayed cards','Exact historical20-card log list unavailable in captured batch log'],'old_packet_unchanged':True})
print('Prepared source reference and four turn scaffolds; no source observation claimed.')
