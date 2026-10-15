from pathlib import Path
import json, subprocess, hashlib
from PIL import Image
P=Path(__file__).parent
SRC=P.parents[2]/'Reviewed/20260909_023151000_iOS.MP4'
FF=r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffmpeg.exe'
receipt=[]
for t in [47.7,49.7,52.7,111.2]:
 q=P/'nativeframes'/f't{t:07.2f}.jpg'; assert not q.exists()
 subprocess.run([FF,'-hide_banner','-loglevel','error','-threads','1','-ss',str(t),'-i',str(SRC),'-frames:v','1','-q:v','2','-threads','1',str(q)],check=True)
 assert Image.open(q).size==(1170,2532)
 receipt.append(dict(path=str(q),requested_source_seconds=t,actual_frame_pts=None,sha256=hashlib.sha256(q.read_bytes()).hexdigest()))
(P/'CAPTURE_RECEIPT_4.json').write_text(json.dumps(dict(source_sha256='3df25a8532bd7df253638e23c3a6cfd711e4b7607992463ca5663e8abbff367a',reason='True T1 draw-join end was 46.7 rather than reduced reveal cue: capture actual +1/+3/+6 offsets; T2 final HP after110 attack animation',native_seek_decodes=4,total_new_native=40,new_native_cap=60,additional_hash_reads=0,frames=receipt),indent=2),encoding='utf-8')
