from pathlib import Path
import json,subprocess,hashlib
from PIL import Image
P=Path(__file__).parent;SRC=P.parents[2]/'Reviewed/20260909_023151000_iOS.MP4';FF=r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffmpeg.exe'
receipt=[]
for t in [95,110,177.5,230.5,325.5]:
 q=P/'nativeframes'/f't{t:07.2f}.jpg';assert not q.exists()
 subprocess.run([FF,'-hide_banner','-loglevel','error','-threads','1','-ss',str(t),'-i',str(SRC),'-frames:v','1','-q:v','2','-threads','1',str(q)],check=True)
 assert Image.open(q).size==(1170,2532)
 receipt.append(dict(path=str(q),requested_source_seconds=t,actual_frame_pts=None,sha256=hashlib.sha256(q.read_bytes()).hexdigest()))
(P/'CAPTURE_RECEIPT_3.json').write_text(json.dumps(dict(source_sha256='3df25a8532bd7df253638e23c3a6cfd711e4b7607992463ca5663e8abbff367a',reason='Settled T2/T4/T6/T8 native endpoints and concealed opponent Ball interval; retained resolution anchors sometimes precede final HP or promotion',native_seek_decodes=5,total_new_native=36,new_native_cap=60,additional_hash_reads=0,frames=receipt),indent=2),encoding='utf-8')
