import io,json,subprocess,shutil,sys
from pathlib import Path
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
SRC=P.parents[2]/'20261012_003458000_iOS.MP4'
FF=r'C:/Program Files/MiniTool Screen Recorder/FFmpeg/ffmpeg.exe'
def gate():
    if shutil.disk_usage(P).free<100*1024*1024:raise RuntimeError('free space gate')
def frame(t,native=False):
    gate();cmd=[FF,'-v','error','-threads','1','-ss',str(t),'-i',str(SRC),'-frames:v','1','-threads','1']
    if not native:cmd+=['-vf','scale=234:506']
    cmd+=['-f','image2pipe','-vcodec','mjpeg','-q:v','3','pipe:1']
    data=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True).stdout
    return Image.open(io.BytesIO(data)).convert('RGB')
mode=sys.argv[1]
times=[float(x) for x in sys.argv[2:]] if len(sys.argv)>2 else list(range(0,364,4))
d=P/('turn_evidence' if mode=='native' else mode);d.mkdir(exist_ok=True)
for t in times:
    stem=f'{t:07.3f}'.replace('.','p');path=d/(stem+'.jpg')
    if not path.exists():
        im=frame(t,mode=='native');gate();im.save(path,quality=85)
        if mode=='native':
            im.crop((0,2025,1170,2532)).save(d/(stem+'_bottom.jpg'),quality=85)
            im.crop((0,0,1170,600)).save(d/(stem+'_top.jpg'),quality=85)
    print(t,flush=True)
if mode!='native':
    for k in range(0,len(times),24):
        batch=times[k:k+24];contact=Image.new('RGB',(234*6,530*4),'#202020');draw=ImageDraw.Draw(contact)
        for j,t in enumerate(batch):
            stem=f'{t:07.3f}'.replace('.','p');im=Image.open(d/(stem+'.jpg'));x=(j%6)*234;y=(j//6)*530
            contact.paste(im,(x,y+24));draw.text((x+3,y+4),str(t)+' sec',fill='white')
        gate();contact.save(d/f'contact_{k//24}.jpg',quality=88)
