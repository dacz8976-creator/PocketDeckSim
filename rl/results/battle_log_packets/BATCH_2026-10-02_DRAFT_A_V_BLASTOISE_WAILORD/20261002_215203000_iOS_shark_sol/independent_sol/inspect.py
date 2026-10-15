import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
p=Path(__file__).resolve().parent.parent
out=p/'independent_sol'
H=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
s=json.loads((p/'SUBMISSION.json').read_text('utf-8-sig'))
checks={k:H(p/k) for k in s['files']}
assert checks==s['files']
texts={k:(p/k).read_text('utf-8-sig') for k in s['files']}
data={k:json.loads(v) for k,v in texts.items() if k.endswith('.json')}
e=data['EXTRACTION_MANIFEST.json']; ids={r['evidence_id'] for r in e}
for r in e:
 assert H(r['full_frame_path'])==r['full_frame_sha256']
 assert Image.open(r['full_frame_path']).size==(1170,2532)
 for c in ['bottom_crop','top_crop']:
  assert H(r[c]['path'])==r[c]['sha256']
  b=r[c]['pixel_bounds_x0_y0_x1_y1']; assert Image.open(r[c]['path']).size==(b[2]-b[0],b[3]-b[1])
def walk(v):
 if isinstance(v,dict):
  for k,x in v.items():
   if k.endswith('evidence_ids') and isinstance(x,list):
    for a in x: assert a in ids,(k,a)
   walk(x)
 elif isinstance(v,list):
  for x in v:walk(x)
for k,v in data.items():walk(v)
turns=data['TURN_LEDGER.json']['turns']; assert [t['turn_number'] for t in turns]==list(range(1,13))
(out/'HASH_CHECK.json').write_text(json.dumps({'submission_sha256':H(p/'SUBMISSION.json'),'checked_submission_files':checks,'native_and_crops_checked':len(e)*3,'native_dimensions':[1170,2532],'evidence_ids_checked':True},indent=2))
print('19 frozen hashes match;137 native frames and274 crops match; nested evidence IDs valid.')
for t in turns:
 print('TURN',t['turn_number'],'KEYS',list(t) if t['turn_number']==2 else '')
 print('HAND',t.get('owner_hand_start'), 'DRAWS',t.get('draws_and_searches'))
 print('PLAYS',[(a.get('play_order'),a.get('kind'),a.get('card_name'),a.get('source_seconds'),a.get('evidence_ids')) for a in t.get('numbered_plays',[])])
 print('CANDIDATES',t.get('hand_evidence_selection'))
groups=[('T2',[43.5,45.5,48.5,56.9]),('T4',[70.2,71,73,76,96.5]),('T6',[128.5,130.5,133.5,140.5]),('T8',[164.8,165.5,167.5,170.5,171.5]),('T10',[193.8,195.5,197.5,200.5,206.5]),('T12',[226.2,227.5,229.5,232.5])]
for label,times in groups:
 rows=[next(r for r in e if r['requested_source_seconds']==a) for a in times]
 for c in ['bottom_crop','top_crop']:
  ims=[Image.open(r[c]['path']) for r in rows]
  for offset in range(0,len(ims),3):
   part=ims[offset:offset+3]; sheet=Image.new('RGB',(1170,sum(i.height+24 for i in part)),'white');d=ImageDraw.Draw(sheet);y=0
   for r,im in zip(rows[offset:offset+3],part):
    d.text((5,y),f"{label} {r['evidence_id']} {r['actual_frame_seconds_if_measured']} {c}",fill='black');sheet.paste(im,(0,y+24));y+=im.height+24
   sheet.save(out/f'{label}_{c}_{offset//3}.png')
