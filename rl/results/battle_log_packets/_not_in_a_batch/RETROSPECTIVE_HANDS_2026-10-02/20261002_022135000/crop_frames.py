from pathlib import Path
from PIL import Image,ImageDraw
p=Path('Recording_QA/RETROSPECTIVE_HANDS_2026-10-02/20261002_022135000/turn_evidence')
files=sorted(p.glob('t*.jpg'))
for f in files:
 if '_bottom' in f.stem or '_top' in f.stem:continue
 im=Image.open(f)
 im.crop((0,2025,1170,2532)).save(f.with_name(f.stem+'_bottom.png'))
 im.crop((0,0,1170,820)).save(f.with_name(f.stem+'_top.png'))
for k in range(0,len(files),6):
 fs=files[k:k+6];sheet=Image.new('RGB',(1170,537*len(fs)),'white');d=ImageDraw.Draw(sheet)
 for j,f in enumerate(fs):
  d.text((5,j*537),f.name,fill='black');sheet.paste(Image.open(f).crop((0,2025,1170,2532)),(0,j*537+30))
 sheet.save(p/f'contact_bottom_{k:02}.jpg')
