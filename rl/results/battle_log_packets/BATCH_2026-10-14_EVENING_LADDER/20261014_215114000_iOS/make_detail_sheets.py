from pathlib import Path
from PIL import Image,ImageDraw
p=Path('Recording_QA/BATCH_2026-10-14_EVENING_LADDER/20261014_215114000_iOS')
groups=[[12,17,19,24,26,28],[38,42,46,50,58,66],[70,90,94,106,109,130],[134,138,150,153,182,185],[189,194,198,201,214,222],[226,230,254,258,270,274],[282,286,290,330,345,346],[347,353,354,355,358,362],[366,370,374,378,381,383],[385,386,390,402,406,410],[414,418,422,426,430,434],[436,437,438,441,445,447]]
for k,ts in enumerate(groups,1):
    fs=[p/'evidence'/f't{t:07.2f}.jpg' for t in ts]
    if not all(f.exists() and f.stat().st_size>0 for f in fs):continue
    out=p/'orientation'/f'detail_{k:02}.jpg'
    if out.exists():continue
    im=Image.new('RGB',(1350,2008),'white');d=ImageDraw.Draw(im)
    for j,(f,t) in enumerate(zip(fs,ts)):
        with Image.open(f) as q:q=q.resize((450,974));im.paste(q,((j%3)*450,(j//3)*1004+30))
        d.text(((j%3)*450+10,(j//3)*1004+8),str(t)+'s',fill='black')
    im.save(out,quality=91)
    print(out)
