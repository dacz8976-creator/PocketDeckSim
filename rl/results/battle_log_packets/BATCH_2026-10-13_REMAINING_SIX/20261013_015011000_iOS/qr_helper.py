import json,hashlib,base64,collections,sys
from pathlib import Path
from PIL import Image,ImageDraw
p=Path(__file__).resolve().parent
def sheets(paths,out,label):
 out.mkdir(exist_ok=True)
 for k in range(0,len(paths),9):
  s=Image.new('RGB',(1170,2610),'white');d=ImageDraw.Draw(s)
  for i,f in enumerate(paths[k:k+9]):
   x=i%3*390;y=i//3*870
   with Image.open(f) as im: s.paste(im.resize((390,844)),(x,y+26))
   d.text((x+4,y+5),label(f),fill='black')
  s.save(out/f'sheet_{k//9+1:02}.jpg',quality=90)
if sys.argv[1]=='sheets':
 fs=sorted((p/'turn_evidence').glob('t*.jpg'))
 sheets(fs,p/'native_sheets',lambda f:f.stem[1:]+'s')
elif sys.argv[1]=='overview':
 fs=sorted((p/'overview/sample_frames').glob('*.jpg'))
 sheets(fs,p/'overview_current',lambda f:f'{(int(f.stem)-.5)*6:.2f}s')
elif sys.argv[1]=='qr':
 sys.path.insert(0,str(p.parents[1]/'BATCH_2026-10-12_ADDITIONAL_TWO/20261012_225319000_iOS/qr_runtime'))
 import zxingcpp
 f=p/'turn_evidence/t0001.00.jpg';payload=zxingcpp.read_barcodes(Image.open(f))[0].text
 b=base64.b64decode(payload);i=0;groups=[]
 for kind in ['trainer','pokemon']:
  n=b[i];i+=1;ids=[]
  for _ in range(n):
   ids.append(int.from_bytes(b[i:i+3],'big')-(10000000 if kind=='trainer' else 0));i+=3
  groups.append((kind,ids))
 n=b[i];i+=1;en=list(b[i:i+n]);i+=n;assert i==len(b)
 cat=json.loads(Path('C:/Users/dacz8/Projects/Pocket Deck Lab/s216_card_catalog_v1.json').read_text(encoding='utf-8'))['aliases']
 cards=[];slots=[]
 for kind,ids in groups:
  for eid,cnt in collections.Counter(ids).items():
   aa=[a for a in cat if a['entity_key'].split(':')[0]==kind and int(a['entity_key'].split(':')[1])==eid];names=sorted(set(a['raw_name'] for a in aa))
   name=names[0] if len(names)==1 else None
   item=dict(entity_kind=kind,entity_id=eid,count=cnt,name=name,name_candidates=names,printing_limit='QR does not establish artwork or rarity')
   cards.append(item)
  for eid in ids:
   a=next(c for c in cards if c['entity_kind']==kind and c['entity_id']==eid);slots.append(dict(name=a['name'],entity_kind=kind,entity_id=eid))
 s=json.loads((p/'SOURCE.json').read_text(encoding='utf-8-sig'))
 q=dict(source_video=s['video_basename'],source_sha256=s['sha256'],source_seconds=1,retained_image=str(f),retained_image_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),native_dimensions=[1170,2532],payload=payload,card_slot_count=len(slots),cards=cards,slots=slots,energy_types=en,energy=['Darkness' if x==7 else str(x) for x in en],all_entities_resolved=all(x['name'] for x in cards),decoded_byte_count=i,read_method='zxingcpp native frame',limits=['Filmed QR is separate from fresh live Pause Games snapshot.'])
 (p/'QR_DECODE.json').write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(q,ensure_ascii=False,indent=2))

