from pathlib import Path
from PIL import Image,ImageDraw
p=Path(__file__).parent
kt=[float(x.strip().rstrip(',')) for x in (p/'key_times.csv').read_text().splitlines() if x.strip().rstrip(',')]
for label,start,end in [('a',110,124),('b',180,195),('c',270,280),('d',300,340),('e',394,415),('f',82,87)]:
    fs=[(i,p/'evidence'/f'key_{i:03d}.jpg') for i in range(start,min(end,len(kt))+1)]
    for k in range(0,len(fs),12):
        sheet=Image.new('RGB',(1600,2088),'white');d=ImageDraw.Draw(sheet)
        for j,(i,f) in enumerate(fs[k:k+12]):
            x=j%4*400;y=j//4*696
            d.text((x+5,y+5),f'{i}: {kt[i-1]:.3f}s',fill='black')
            with Image.open(f) as im:sheet.paste(im.crop((210,440,1010,1780)).resize((400,670)),(x,y+26))
        dest=p/'sheets'/f'action_{label}{k//12+1}.jpg';sheet.save(dest,quality=91);print(dest)
