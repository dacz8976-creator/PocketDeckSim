from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw
p=Path('Recording_QA/RETROSPECTIVE_HANDS_2026-10-02/20260908_021327000/cue_audit');p.mkdir(exist_ok=True);frames=p/'reduced';frames.mkdir(exist_ok=True)
subprocess.run([r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffmpeg.exe','-hide_banner','-loglevel','error','-threads','2','-i',r'Reviewed\20260908_021327000_iOS.MP4','-vf','fps=1,scale=234:-1','-q:v','4','-y',str(frames/'%04d.jpg')],check=True)
fs=sorted(frames.glob('*.jpg'))
for s in range(0,len(fs),36):
 w,h=Image.open(fs[s]).size;out=Image.new('RGB',(w*6,(h+25)*6),'white');d=ImageDraw.Draw(out)
 for i,f in enumerate(fs[s:s+36]):
  x=i%6*w;y=i//6*(h+25);d.text((x+4,y+3),f'{s+i+.5:.1f}s',fill='black');out.paste(Image.open(f),(x,y+25))
 out.save(p/f'grid_{s//36+1:02}.jpg',quality=92)
(p/'SCAN_MANIFEST.json').write_text(json.dumps({'source':'20260908_021327000_iOS.MP4','sha256':'95df14af59472ec02a077b5a5804f1a44e6c02048179952934b68c56eee1e387','purpose':'Prompt and discard locator, not native hand evidence or outcome re-review','sampling':'ffmpeg fps=1; source-local approximate midpoint labels; PTS not independently measured','sample_count':len(fs),'native_evidence':False,'width':234,'source_duration_seconds':410.492,'covered_interval_seconds':[0,410.492],'limitations':'One sample per second does not examine every instant; brief events between samples can be missed.'},indent=2)+'\n')
print('Reduced samples',len(fs))
