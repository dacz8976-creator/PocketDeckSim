from pathlib import Path
from PIL import Image,ImageDraw
p=Path(r'Recording_QA/BATCH_2026-10-06_NEW_PAUSE_GAMES/20261005_123812000_iOS'); paths=list((p/'turn_evidence').glob('t*.jpg'))
for f in paths:
 im=Image.open(f);im.crop((0,2025,1170,2532)).save(f.with_name(f.stem+'_hand.png'));im.crop((0,0,1170,520)).save(f.with_name(f.stem+'_top.png'))
for name,times in [('early',[43,44,46,47,48,50,53,54,56,58,59,61]),('draw3',[108,109,110,111,112,114,117,125]),('draw5',[181,182,183,184,185,186,187,188,189,190,191,194])]:
 sheet=Image.new('RGB',(1170,540*len(times)),'white');d=ImageDraw.Draw(sheet)
 for i,t in enumerate(times):
  f=p/'turn_evidence'/f't{t:07.2f}_hand.png'
  if not f.exists():continue
  d.text((5,i*540+3),str(t)+'s',fill='black');sheet.paste(Image.open(f),(0,i*540+25))
 sheet.save(p/'overview'/f'{name}_hands.jpg',quality=90)
