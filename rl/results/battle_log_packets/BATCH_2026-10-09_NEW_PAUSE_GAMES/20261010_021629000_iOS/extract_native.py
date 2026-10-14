from pathlib import Path
from PIL import Image,ImageDraw
import subprocess,json,sys
p=Path(__file__).parent;out=p/'turn_evidence';out.mkdir(exist_ok=True)
v=p.parents[2]/'20261010_021629000_iOS.MP4';f=r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffmpeg.exe'
times=[28,60,62,64,66,67,69,72,74,78,106,108,110,111,113,116,118,126,134,136,140,142,146,148,150,152,182,184,186,187,189,192,198,206,218,250,252,254,255,257,260,262,264,266,268,270,314,316,318,319,321,324,326,328,330,334,342,346,354,388,390,391,392,393,396,398,400,402,410,418,438,440,441,442,443,444,446,448,450,454,462,510,512,514,515,517,520,522,526,530,538,542,550,558,656,658,660,661,663,666,668,670,674,678,684,724,725,726,727,728,729,732,734,738,746,782,783,784,785,786,788,790,794,802,846,847,848,849,850,851,852,854,862,882,892]
if len(sys.argv)>1: times=[float(x) for x in sys.argv[1:]]
for t in times:
 target=out/f't{t:07.2f}.jpg'
 if not target.exists(): subprocess.run([f,'-hide_banner','-loglevel','error','-threads','2','-ss',str(t),'-i',str(v),'-frames:v','1','-q:v','2','-y',str(target)],check=True)
 im=Image.open(target);w,h=im.size
 im.crop((0,int(h*.8),w,h)).save(out/f't{t:07.2f}_hand.jpg',quality=95)
 im.crop((0,0,w,850)).save(out/f't{t:07.2f}_top.jpg',quality=95)
for n in range(0,len(times),9):
 sheet=Image.new('RGB',(1755,855),'white');d=ImageDraw.Draw(sheet)
 for j,t in enumerate(times[n:n+9]):
  im=Image.open(out/f't{t:07.2f}_hand.jpg').resize((585,254));x=j%3*585;y=j//3*285
  sheet.paste(im,(x,y+30));d.text((x+5,y+5),str(t),fill='black')
 sheet.save(out/f'{"extra" if len(sys.argv)>1 else "hand"}_sheet_{n//9+1:02}.jpg',quality=95)
(out/('EXTRA_REQUESTED_SEEKS.json' if len(sys.argv)>1 else 'REQUESTED_SEEKS.json')).write_text(json.dumps(times))
print('finished native',len(times))
