from pathlib import Path
from PIL import Image,ImageDraw
import sys
p=Path(__file__).parent
kind=sys.argv[1] if len(sys.argv)>1 else 'seq'
files=sorted((p/('overview' if kind=='overview' else 'evidence')).glob(f'{kind if kind in ("seq","key") else "overview"}_*.jpg'))
kt=[float(x.strip().rstrip(',')) for x in (p/'key_times.csv').read_text().splitlines() if x.strip().rstrip(',')] if kind=='key' else []
stride=int(sys.argv[2]) if len(sys.argv)>2 else 1
files=files[::stride]
out=p/'sheets';out.mkdir(exist_ok=True)
for k in range(0,len(files),12):
    subset=files[k:k+12];w=390;h=844
    sheet=Image.new('RGB',(w*4,(h+28)*3),'white');d=ImageDraw.Draw(sheet)
    for j,f in enumerate(subset):
        idx=int(f.stem.split('_')[-1]);t=kt[idx-1] if kind=='key' and idx<=len(kt) else ((idx-1)*3+1.5 if kind=='seq' else (idx-.5)*12)
        x=j%4*w;y=j//4*(h+28)
        d.text((x+6,y+5),f'{f.stem} approx {t:.1f}s',fill='black')
        with Image.open(f) as im:sheet.paste(im.resize((w,h)),(x,y+28))
    dest=out/f'{kind}{stride}_{k//12+1:02d}.jpg';sheet.save(dest,quality=90)
    print(dest)
