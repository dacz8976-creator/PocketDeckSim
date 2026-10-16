from pathlib import Path
from PIL import Image, ImageDraw
p=Path(__file__).parent/'orientation'
files=sorted(p.glob('dense_[0-9][0-9][0-9][0-9].jpg'))
for start in range(0,len(files),8):
    subset=files[start:start+8]
    if len(subset)<8 and len(files)<190: continue
    dest=p/f'dense_sheet_{start//8+1:03d}.jpg'
    sheet=Image.new('RGB',(468*4,(1013+28)*2),'white');d=ImageDraw.Draw(sheet)
    for j,f in enumerate(subset):
        n=int(f.stem.split('_')[-1]); x=j%4*468;y=j//4*1041
        d.text((x+5,y+5),f'{2*n-1:.1f}s',fill='black')
        with Image.open(f) as im:sheet.paste(im,(x,y+28))
    sheet.save(dest,quality=90)
print(len(files))
