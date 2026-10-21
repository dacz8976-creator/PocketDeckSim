from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
p=Path(__file__).resolve().parent.parent
out=p/'independent_sol'
groups={
'early_draw_search':[41,42,43,44.5,45,47,47.5,49,51,53,55,57,59,61,63,65,125,126,127,128,129,130,131,133,135,137,139,141,143,145,147],
'ordinary_and_copycat':[474,476,479,533,535,538,710,712,715,718,721,724],
'first_crystal':[333,334,335,336,338,340,341,342,344,346],
}
manifest={}
for key,times in groups.items():
 ims=[]
 for t in times:
  f=p/'turn_evidence'/f't{t:07.2f}.jpg'
  im=Image.open(f).crop((0,1980,1170,2532)) if key!='first_crystal' else Image.open(f).crop((50,450,1120,1900))
  im.thumbnail((585,550 if key=='first_crystal' else 276))
  ims.append((t,im))
  manifest[str(f.relative_to(p))]=hashlib.sha256(f.read_bytes()).hexdigest()
 for i in range(0,len(ims),9):
  w,h=ims[0][1].size
  sheet=Image.new('RGB',(w*3,(h+24)*3),'white');d=ImageDraw.Draw(sheet)
  for j,(t,im) in enumerate(ims[i:i+9]):
   x=j%3*w;y=j//3*(h+24);sheet.paste(im,(x,y+24));d.text((x+3,y+3),str(t),fill='black')
  sheet.save(out/f'{key}_{i//9+1}.jpg',quality=94)
(out/'CHECKED_FRAME_HASHES.json').write_text(json.dumps(manifest,indent=2))
