from pathlib import Path
import json,subprocess,hashlib
from PIL import Image
P=Path(__file__).parent
SRC=P.parents[2]/'Reviewed/20260909_023151000_iOS.MP4'
FF=r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffmpeg.exe'
receipt=[]
for t in [46.7,46.8,114.4,114.6,114.8]:
 q=P/'nativeframes'/f't{t:07.2f}.jpg';assert not q.exists()
 subprocess.run([FF,'-hide_banner','-loglevel','error','-threads','1','-ss',str(t),'-i',str(SRC),'-frames:v','1','-q:v','2','-threads','1',str(q)],check=True)
 assert Image.open(q).size==(1170,2532)
 receipt.append(dict(path=str(q),requested_source_seconds=t,actual_frame_pts=None,sha256=hashlib.sha256(q.read_bytes()).hexdigest()))
(P/'CAPTURE_RECEIPT_2.json').write_text(json.dumps(dict(source_sha256='3df25a8532bd7df253638e23c3a6cfd711e4b7607992463ca5663e8abbff367a',reason='T1 and T3 first captures still contained draw reveal/moving card; inspect dense postdraw/preplay window',native_seek_decodes=5,total_new_native=31,new_native_cap=60,additional_hash_reads=0,frames=receipt),indent=2),encoding='utf-8')
dest=P/'inspection_crops';dest.mkdir(exist_ok=True)
for q in (P/'nativeframes').glob('*.jpg'):
 im=Image.open(q);im.crop((0,2025,1170,2532)).save(dest/(q.stem+'_bottom.png'));im.crop((0,0,1170,500)).save(dest/(q.stem+'_top.png'))
