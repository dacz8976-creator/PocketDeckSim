from pathlib import Path
from PIL import Image,ImageDraw
p=Path(r'C:/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/RETROSPECTIVE_HANDS_2026-10-02/20260907_232617000')
f=p.parents[1]/'20260907_232617_v5_review/final_packet/frames'
ts=[40,47,52,100,104,134,138,162,170,210,215,237,240,260,265,317,320,355,360,407,410,440]
for b in range(0,len(ts),6):
 sh=Image.new('RGB',(1170,283*len(ts[b:b+6])),'white');d=ImageDraw.Draw(sh)
 for i,t in enumerate(ts[b:b+6]):
  im=Image.open(f/f'{t:07.3f}.jpg');im.thumbnail((1170,2532))
  d.text((0,i*283),f'{t}s native boundary zone/detail strips. TOP left; BOTTOM right',fill='black')
  sh.paste(im.crop((0,200,350,450)),(0,i*283+30));sh.paste(im.crop((800,2050,1170,2300)),(370,i*283+30));sh.paste(im.crop((100,1600,430,1850)),(750,i*283+30))
 sh.save(p/f'zones_{b}.png')
