from PIL import Image,ImageDraw
from pathlib import Path
p=Path(__file__).parent/'evidence'
files=sorted(p.glob('scan_[0-9]*.jpg'))
for k in range(0,len(files),8):
    subset=files[k:k+8]
    if len(subset)<8 and len(files)<96: continue
    dest=p/f'scan_sheet_{k//8+1:02d}.jpg'
    if dest.exists():continue
    out=Image.new('RGB',(470*4,1049*2),'white'); d=ImageDraw.Draw(out)
    for j,f in enumerate(subset):
        n=int(f.stem.split('_')[1]);t=(n-1)*3+1.5
        x=j%4*470;y=j//4*1049
        d.text((x+6,y+4),f'{t:.1f}s',fill='black')
        with Image.open(f) as im:out.paste(im,(x,y+32))
    out.save(dest,quality=90)
    print(dest)

