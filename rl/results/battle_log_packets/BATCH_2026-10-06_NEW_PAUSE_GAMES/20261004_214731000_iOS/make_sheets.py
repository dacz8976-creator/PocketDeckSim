from PIL import Image, ImageDraw
from pathlib import Path
import sys
p=Path(__file__).resolve().parent
mode=sys.argv[1]
if mode=='overview':
    fs=sorted((p/'overview/sample_frames').glob('*.jpg'))
else:
    fs=sorted((p/'turn_evidence').glob('t*.jpg'))
if len(sys.argv)>3:
    fs=[f for f in fs if float(sys.argv[2])<=float(f.stem[1:])<=float(sys.argv[3])]
    mode=f'{mode}_{sys.argv[2]}_{sys.argv[3]}'
for st in range(0,len(fs),9):
    s=Image.new('RGB',(1170,870*3),'white');d=ImageDraw.Draw(s)
    for i,f in enumerate(fs[st:st+9]):
        im=Image.open(f);im.thumbnail((390,844))
        s.paste(im,(i%3*390,i//3*870+26))
        t=f'{(st+i+0.5)*4:.2f}s' if mode=='overview' else f.stem
        d.text((i%3*390,i//3*870),t,fill='black')
    s.save(p/f'{mode}_{st//9+1:02}.jpg')
print(len(fs))
