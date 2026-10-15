import subprocess,sys
from pathlib import Path
from PIL import Image,ImageDraw
root=Path(__file__).parent
video=root.parents[2]/'20261014_145449000_iOS.MP4'
out=root/'evidence';out.mkdir(exist_ok=True)
mode=sys.argv[1]
times=list(map(float,sys.argv[2:]))
files=[]
for t in times:
    p=out/f'{mode}_{t:07.2f}.jpg'
    cmd=['C:/Program Files/MiniTool Screen Recorder/FFmpeg/ffmpeg.exe','-hide_banner','-loglevel','error','-threads','1','-ss',str(t),'-i',str(video),'-frames:v','1']
    if mode!='native':cmd+=['-vf','scale=320:-1']
    cmd+=['-q:v','2','-threads','1',str(p)]
    if not p.exists():subprocess.run(cmd,check=True)
    files.append(p)
if mode!='native':
    for start in range(0,len(files),12):
        subset=files[start:start+12]
        with Image.open(subset[0]) as im:w,h=im.size
        sheet=Image.new('RGB',(4*w,3*(h+28)),'white');draw=ImageDraw.Draw(sheet)
        for j,p in enumerate(subset):
            x,y=j%4*w,j//4*(h+28);draw.text((x+3,y+3),p.stem,fill='black')
            with Image.open(p) as im:sheet.paste(im,(x,y+28))
        dest=out/f'{mode}_sheet_{start//12+1:02d}.jpg';sheet.save(dest,quality=90);print(dest,flush=True)
