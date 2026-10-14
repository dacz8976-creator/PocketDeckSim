from pathlib import Path
from PIL import Image,ImageDraw
p=Path(r'C:/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/RETROSPECTIVE_HANDS_2026-10-02/20260907_232617000');f=p.parents[1]/'20260907_232617_v5_review/final_packet/frames'
files=sorted(f.glob('*.jpg'))
for b in range(0,len(files),80):
 sh=Image.new('RGB',(1440,3328),'white');d=ImageDraw.Draw(sh)
 for i,path in enumerate(files[b:b+80]):
  im=Image.open(path);im.thumbnail((144,312));x=(i%10)*144;y=(i//10)*416;d.text((x,y),path.stem,fill='black');sh.paste(im,(x,y+20))
 sh.save(p/f'discard_locator_{b}.jpg',quality=85)
