from pathlib import Path
from PIL import Image,ImageDraw
p=Path(r'C:/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/20261001_210403000_iOS_rule_sol')
for t in ['0034.00','0049.00','0079.00','0126.00','0130.00','0152.00','0284.00','0329.00','0377.00']:
 f=p/'native'/f't{t}.jpg'
 if f.exists():
  im=Image.open(f);im.crop((100,780,1090,2140)).save(p/'native'/f'crop_{t}.jpg',quality=92)
