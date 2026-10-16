from pathlib import Path
from PIL import Image, ImageDraw
import sys
import re
p=Path(__file__).parent/'evidence'
pattern=sys.argv[1] if len(sys.argv)>1 else 'dense_*.jpg'
kind='dense' if pattern.startswith('dense') else 'native'
fs=sorted(p.glob(pattern))
if kind=='dense':
    fs=[f for f in fs if re.fullmatch(r'dense_\d{4}',f.stem)]
for start in range(0,len(fs),9):
    subset=fs[start:start+9]
    s=Image.new('RGB',(1170,2628),'white'); d=ImageDraw.Draw(s)
    for i,f in enumerate(subset):
        im=Image.open(f); im.thumbnail((390,844))
        x,y=i%3*390,i//3*876
        label=f'{42+(start+i)*3:.1f}s nominal' if kind=='dense' else f.stem
        d.text((x+4,y+4),label,fill='black'); s.paste(im,(x,y+30))
    s.save(p/f'{kind}_sheet_{start//9+1:02d}.jpg',quality=88)
print(len(fs))
