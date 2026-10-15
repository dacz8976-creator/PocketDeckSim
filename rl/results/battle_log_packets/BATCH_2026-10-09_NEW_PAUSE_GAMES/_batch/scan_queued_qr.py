"""Bounded native QR intake, separate from full visual game acceptance."""
import json
import argparse
import subprocess
from pathlib import Path
batch=Path(__file__).resolve().parent;root=batch.parent.parent
python=r'C:\Users\dacz8\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
ffmpeg=r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffmpeg.exe'
decoder=root/'Recording_QA/BATCH_2026-10-06_NEW_PAUSE_GAMES/qr_support/decode_retained_qr.py'
ap=argparse.ArgumentParser();ap.add_argument('sources',nargs='*');args=ap.parse_args()
for stem in (args.sources or ['20261010_015821000_iOS','20261010_020258000_iOS','20261010_020908000_iOS']):
    packet=batch/stem;source=json.loads((packet/'SOURCE.json').read_text(encoding='utf-8'))
    out=packet/'qr_intake';out.mkdir(exist_ok=True)
    attempts=[]
    for sec in [1,2,5]:
        image=out/f't{sec:07.2f}.jpg';receipt=out/f'QR_DECODE_{sec:07.2f}.json'
        if receipt.exists():
            result=subprocess.CompletedProcess([],0,'Existing retained receipt','');break
        if not image.exists():
            subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-threads','2','-ss',str(sec),'-i',str(root/source['video_basename']),'-frames:v','1','-q:v','2',str(image)],check=True,timeout=40)
        result=subprocess.run([python,str(decoder),str(image),'--source-video',source['video_basename'],'--seconds',str(sec),
            '--source-sha256',source['sha256'],'--out',str(receipt)],capture_output=True,text=True,timeout=60)
        attempts.append({'seconds':sec,'native_frame':str(image),'exit_code':result.returncode,'stdout':result.stdout.strip(),'stderr':result.stderr[-700:]})
        if result.returncode==0:break
    (out/'INTAKE_RESULT.json').write_text(json.dumps({'source':source['video_basename'],'source_sha256':source['sha256'],
        'scope':'Automated early QR intake; game/deck binding requires whole-source visual review','attempts':attempts},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'source':stem,'decoded':result.returncode==0,'receipt':str(receipt) if result.returncode==0 else None}),flush=True)
