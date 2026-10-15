"""Check packet integrity and template completion, separately from visual acceptance."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image

p=argparse.ArgumentParser();p.add_argument('packet');a=p.parse_args()
packet=Path(a.packet).resolve();issues=[]
required=['SOURCE.json','REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
documents={}
for name in required:
    path=packet/name
    if not path.is_file():
        issues.append('missing '+name);continue
    if path.suffix=='.json':
        try:documents[name]=json.loads(path.read_text(encoding='utf-8-sig'))
        except Exception as e:issues.append(name+': invalid JSON '+str(e))
for name,doc in documents.items():
    if doc.get('is_template') is True:issues.append(name+': still marked template')
    def scan(value, trail=''):
        if isinstance(value,dict):
            for key,item in value.items():scan(item,trail+'.'+key)
        elif isinstance(value,list):
            for i,item in enumerate(value):scan(item,trail+f'[{i}]')
        elif value in ('not_reviewed','not_captured'):
            issues.append(name+trail+': scaffold status remains')
        elif isinstance(value,str) and any(bad in value for bad in ('PokÃ©','PokÃƒ','Professorâ€','PokÃ©mon')):
            issues.append(name+trail+': authored card-name encoding is corrupted')
    scan(doc)
source=documents.get('SOURCE.json',{})
turns=documents.get('TURN_LEDGER.json',{}).get('turns',[])
numbers=[t.get('turn_number') for t in turns]
if turns and (len(numbers)!=len(set(numbers)) or numbers!=sorted(numbers)):
    issues.append('turn numbers duplicate or out of order')
for turn in turns:
    n=turn.get('turn_number')
    if turn.get('source_video')!=source.get('video_basename'):issues.append(f'turn {n}: source differs')
    orders=[play.get('order') for play in turn.get('plays_in_order',[])]
    if orders!=list(range(1,len(orders)+1)):issues.append(f'turn {n}: nonsequential voluntary plays')
    for key,value in turn.get('timing',{}).items():
        if isinstance(value,(int,float)) and (value<0 or value>source.get('duration_seconds',float('inf'))):
            issues.append(f'turn {n}: {key} outside source')
deck=documents.get('DECK_USED.json',{})
cards=deck.get('cards_in_log_order')
if isinstance(cards,list) and cards and len(cards)!=20:issues.append('deck log snapshot does not have twenty slots')
counts=deck.get('counts_by_name_and_variant')
if isinstance(counts,list) and counts and sum(c.get('count',0) for c in counts)!=20:issues.append('deck counts do not total twenty')
qr=packet/'QR_DECODE.json'
if not qr.exists():qr=packet/'QR_DECODE_RECEIPT.json'
if qr.exists():
    q=json.loads(qr.read_text(encoding='utf-8'))
    if q.get('source_sha256')!=source.get('sha256'):issues.append('QR source hash differs')
    if q.get('card_slot_count')!=20:issues.append('QR does not have twenty card slots')
    retained=Path(q['retained_image'])
    if not retained.is_file() or hashlib.sha256(retained.read_bytes()).hexdigest()!=q.get('retained_image_sha256'):
        issues.append('QR retained image missing or changed')
evidence=documents.get('TURN_EVIDENCE.json',{})
frames=evidence.get('frames',[])
ids=[f.get('evidence_id') for f in frames]
if len(ids)!=len(set(ids)):issues.append('duplicate frame evidence IDs')
for frame in frames:
    eid=frame.get('evidence_id','unknown')
    if frame.get('source_video')!=source.get('video_basename'):issues.append(eid+': frame source differs')
    if frame.get('source_sha256',evidence.get('source_sha256'))!=source.get('sha256'):issues.append(eid+': frame source hash differs')
    image_path=packet/str(frame.get('full_frame_path',frame.get('full_frame','')))
    if not image_path.is_file():issues.append(eid+': native full frame missing');continue
    with Image.open(image_path) as im:actual=im.size
    declared=frame.get('native_dimensions',{})
    declared_size=tuple(declared) if isinstance(declared,list) else (declared.get('width'),declared.get('height'))
    if actual!=declared_size:issues.append(eid+': native dimensions differ')
    for key in ['bottom_crop','top_crop']:
        crop=frame.get(key,{}) or {}
        if isinstance(crop,dict):
            bounds=crop.get('pixel_bounds_x0_y0_x1_y1');crop_name=crop.get('path','')
            if key=='bottom_crop' and not crop_name:
                crop_name=frame.get('bottom_fifth','');bounds=frame.get('bottom_crop_xyxy')
        else:
            crop_name=crop;bounds=frame.get('top_crop_xyxy')
        crop_path=packet/str(crop_name)
        if not crop_path.is_file() or not bounds or len(bounds)!=4:
            issues.append(eid+': '+key+' missing');continue
        x0,y0,x1,y1=bounds
        if not (0<=x0<x1<=actual[0] and 0<=y0<y1<=actual[1]):issues.append(eid+': '+key+' bounds invalid')
        with Image.open(crop_path) as im:crop_size=im.size
        if crop_size!=(x1-x0,y1-y0):issues.append(eid+': '+key+' dimensions differ from bounds')
valid_ids=set(ids)
def check_references(value,trail):
    if isinstance(value,dict):
        for key,item in value.items():
            if key=='evidence_ids' and isinstance(item,list):
                for ref in item:
                    if ref not in valid_ids:issues.append(trail+'.evidence_ids: unknown frame '+str(ref))
            else:check_references(item,trail+'.'+key)
    elif isinstance(value,list):
        for i,item in enumerate(value):check_references(item,trail+f'[{i}]')
for name in ['TURN_LEDGER.json','PAUSE_GAME.json']:check_references(documents.get(name,{}),name)
print(json.dumps({'packet':str(packet),'structural_pass':not issues,'turn_rows':len(turns),'issues':issues,
    'visual_acceptance':False,'limit':'Integrity/template checks do not establish battle coverage or semantic correctness.'},indent=2))
raise SystemExit(1 if issues else 0)
