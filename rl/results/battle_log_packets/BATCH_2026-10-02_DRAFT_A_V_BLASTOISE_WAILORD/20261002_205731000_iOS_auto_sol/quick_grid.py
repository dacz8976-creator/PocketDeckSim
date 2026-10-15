from pathlib import Path
from PIL import Image,ImageDraw
P=Path(r'Recording_QA/BATCH_2026-10-02_DRAFT_A_V_BLASTOISE_WAILORD/20261002_205731000_iOS_auto_sol')
for start in range(0,180,20):
 grid=Image.new('RGB',(1170,2104),'white');d=ImageDraw.Draw(grid)
 for j in range(20):
  q=P/'locator_scan'/'frames'/f'{start+j+1:06d}.jpg'
  if not q.exists():break
  x=j%5*234;y=j//5*526;d.text((x+3,y+3),f'{start+j}s',fill='black')
  with Image.open(q)as im:grid.paste(im,(x,y+20))
 grid.save(P/f'early_grid_{start:03d}.jpg',quality=90)
