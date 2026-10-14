import subprocess
from pathlib import Path
from PIL import Image,ImageDraw
p=Path(__file__).parent
out=p/'dense_seeks'; out.mkdir(exist_ok=True)
ff=r'C:/Program Files/MiniTool Screen Recorder/FFmpeg/ffmpeg.exe'
for t in range(114,489,3):
    f=out/f't{t:07.2f}.jpg'
    subprocess.run([ff,'-hide_banner','-loglevel','error','-threads','2','-ss',str(t),'-i',str(p.parents[2]/'20261010_014541000_iOS.MP4'),'-frames:v','1','-vf','scale=585:-1','-q:v','2','-y',str(f)],check=True)
    if (t-114)%27==24:
        fs=sorted(out.glob('t*.jpg'))[-9:]; s=Image.new('RGB',(1755,3900),'white'); d=ImageDraw.Draw(s)
        for i,g in enumerate(fs):
            s.paste(Image.open(g),(i%3*585,i//3*1300+26)); d.text((i%3*585+5,i//3*1300+5),g.stem,fill='black')
        s.save(out/f'sheet_{t:03}.jpg',quality=88); print(t,flush=True)
