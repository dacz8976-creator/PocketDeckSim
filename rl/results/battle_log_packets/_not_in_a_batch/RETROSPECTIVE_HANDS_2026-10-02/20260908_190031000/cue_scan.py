from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;p=P/'cue_audit';p.mkdir(exist_ok=True);frames=p/'reduced';frames.mkdir(exist_ok=True)
src=Path('C:/Users/dacz8/OneDrive/Desktop/Battle Logs/Reviewed/20260908_190031000_iOS.MP4')
subprocess.run([r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffmpeg.exe','-hide_banner','-loglevel','error','-threads','2','-i',str(src),'-vf','fps=1,scale=234:-1','-q:v','4','-y',str(frames/'%04d.jpg')],check=True)
fs=sorted(frames.glob('*.jpg'))
for s in range(0,len(fs),36):
 w,h=Image.open(fs[s]).size;out=Image.new('RGB',(w*6,(h+25)*6),'white');d=ImageDraw.Draw(out)
 for i,f in enumerate(fs[s:s+36]):
  x=i%6*w;y=i//6*(h+25);d.text((x+4,y+3),f'{s+i+.5:.1f}s',fill='black');out.paste(Image.open(f),(x,y+25))
 out.save(p/f'grid_{s//36+1:02}.jpg',quality=92)
(p/'SCAN_MANIFEST.json').write_text(json.dumps({'source':src.name,'sha256':'2f68b969662a26fd6a79844ad00d7a3eb97ebde0bf790a25c273ff34d7d8cbf5','purpose':'Prompt, discard and draw locator; not native hand evidence or new result review','sample_count':len(fs),'sampling_rate_fps':1,'native_evidence':False,'dimensions':[234,506],'source_duration_seconds':168.41,'covered_interval_seconds':[0,168.41],'timestamp_precision':'Approximate source-local midpoint labels, PTS not independently measured','limitations':'One sample per second does not examine every instant; brief events between samples can be missed.'},indent=2)+'\n')
print('Reduced samples',len(fs))
