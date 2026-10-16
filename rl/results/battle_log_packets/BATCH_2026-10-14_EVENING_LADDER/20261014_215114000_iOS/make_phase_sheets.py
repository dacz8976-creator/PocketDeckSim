from pathlib import Path
from PIL import Image,ImageDraw
p=Path('Recording_QA/BATCH_2026-10-14_EVENING_LADDER/20261014_215114000_iOS')
for k,start in enumerate(range(32,441,24),1):
    ts=list(range(start,min(start+24,441),4))
    fs=[p/'evidence'/f't{t:07.2f}.jpg' for t in ts]
    if not all(f.exists() and f.stat().st_size>0 for f in fs):continue
    out=p/'orientation'/f'phase_{k:02}.jpg'
    if out.exists():continue
    im=Image.new('RGB',(1350,2008),'white');d=ImageDraw.Draw(im)
    for j,(f,t) in enumerate(zip(fs,ts)):
        with Image.open(f) as q:q=q.resize((450,974));im.paste(q,((j%3)*450,(j//3)*1004+30))
        d.text(((j%3)*450+10,(j//3)*1004+8),str(t)+'s',fill='black')
    im.save(out,quality=91)
    print(out)

