"""Correct the first turn-four Research reveal using newly inspected native evidence."""
import copy, hashlib, json, shutil
from pathlib import Path
from PIL import Image
P=Path(__file__).resolve().parent/'20261005_031138000_iOS'
backup=P/'submitted_before_independent_corrections';backup.mkdir(exist_ok=True)
files=['TURN_LEDGER.json','TURN_EVIDENCE.json','REVIEW.md']
for name in files:
    if not (backup/name).exists(): shutil.copy2(P/name,backup/name)
ledger=json.loads((P/'TURN_LEDGER.json').read_text(encoding='utf-8'))
evidence=json.loads((P/'TURN_EVIDENCE.json').read_text(encoding='utf-8'))
old=next(f for f in evidence['frames'] if f['evidence_id']=='f0124.00')
new=copy.deepcopy(old)
target=P/'turn_evidence/t0125.00.jpg';shutil.copy2(P/'root_corrections/t0125.00.jpg',target)
im=Image.open(target)
im.crop((0,2025,1170,2532)).save(target.with_name('t0125.00_bottom.png'))
im.crop((0,130,1170,660)).save(target.with_name('t0125.00_top.png'))
new.update(evidence_id='f0125.00',requested_source_seconds=125,full_frame_path='turn_evidence/t0125.00.jpg',role='draw_or_search_reveal',observation='First Research reveal Hatterene is face-up and named; previously cited124s still has an incoming card back.')
new['bottom_crop']['path']='turn_evidence/t0125.00_bottom.png';new['top_crop']['path']='turn_evidence/t0125.00_top.png'
old['observation']='Incoming Research draw card back; no first-card identity visible yet.'
old['suitability_or_limit']='Not suitable as a named Hatterene reveal; use125s.'
evidence['frames'].append(new)
t=ledger['turns'][3];r=t['draws_and_searches'][1]
r.update(timestamp_seconds=125,evidence_ids=['f0125.00','f0126.00'])
r['cards_in_reveal_order'][0].update(timestamp_seconds=125,evidence_ids=['f0125.00'])
for action in t['plays_in_order']:
    if action.get('card_name')=="Professor's Research":
        action['result']=action.get('result','').replace('124','125')
t['turn_evidence_ids']=list(dict.fromkeys(t['turn_evidence_ids']+['f0125.00']))
review=(P/'REVIEW.md').read_text(encoding='utf-8').replace('Hatterene first at124','Hatterene first at125').replace('Research124/126','Research125/126')
review+='\nIndependent reveal-evidence correction: first turn4 Research draw is named Hatterene at125s, not the still face-down124s frame. Native125s full frame and top/bottom crops retained. Original submission is preserved.\n'
for name,value in [('TURN_LEDGER.json',ledger),('TURN_EVIDENCE.json',evidence)]: (P/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(P/'REVIEW.md').write_text(review,encoding='utf-8')
(P/'INDEPENDENT_CORRECTIONS.json').write_text(json.dumps({'repair':'First Research Hatterene reveal source frame124 corrected to125; actual reveal order unchanged.','prior_submission':'submitted_before_independent_corrections','source_video':t['source_video'],'inspected_native_frame':'root_corrections/t0125.00.jpg','current_sha256':{n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in files}},indent=2)+'\n',encoding='utf-8')
print('Corrected first Research reveal with named native125s evidence.')
