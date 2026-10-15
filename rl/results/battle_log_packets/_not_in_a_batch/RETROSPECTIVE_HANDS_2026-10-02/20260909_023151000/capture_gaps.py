from pathlib import Path
import json,subprocess,hashlib
from PIL import Image
P=Path(__file__).parent
SRC=P.parents[2]/'Reviewed/20260909_023151000_iOS.MP4'
FF=r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffmpeg.exe'
SHA='3df25a8532bd7df253638e23c3a6cfd711e4b7607992463ca5663e8abbff367a'
times=[23.5,46.2,46.5,48.5,51.5,59.5,114.2,115,117,120,128.5,181.2,182,184,187,197.5,234.2,235,237,240,241.5,329.4,330,332,335,331.5]
dest=P/'nativeframes';dest.mkdir(exist_ok=True)
receipt=[]
for t in times:
 q=dest/f't{t:07.2f}.jpg'
 if q.exists():raise RuntimeError('Refusing duplicate decode '+str(q))
 subprocess.run([FF,'-hide_banner','-loglevel','error','-threads','1','-ss',str(t),'-i',str(SRC),'-frames:v','1','-q:v','2','-threads','1',str(q)],check=True)
 assert Image.open(q).size==(1170,2532)
 receipt.append(dict(path=str(q),requested_source_seconds=t,actual_frame_pts=None,sha256=hashlib.sha256(q.read_bytes()).hexdigest(),native_dimensions=[1170,2532]))
 print(t,flush=True)
(P/'CAPTURE_RECEIPT_1.json').write_text(json.dumps(dict(source=str(SRC),source_sha256=SHA,verification_reused='ROOT_SOURCE_VERIFICATION.json',additional_hash_reads=0,native_seek_decodes=len(times),new_native_initial_cap=60,frames=receipt),indent=2),encoding='utf-8')
