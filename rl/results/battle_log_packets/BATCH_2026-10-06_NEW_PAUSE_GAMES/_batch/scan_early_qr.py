"""Bounded automated QR intake only, never a battle review or game binding."""
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
b=Path(__file__).resolve().parent; root=b.parent.parent
sys.path.insert(0,str(b/'qr_support/deps'))
import cv2
import zxingcpp
spec=importlib.util.spec_from_file_location('retained_qr',b/'qr_support/decode_retained_qr.py')
decoder=importlib.util.module_from_spec(spec);spec.loader.exec_module(decoder)
selected=json.loads((b/'OWNER_CONTEXT.json').read_text(encoding='utf-8'))['selected_sources']
ffmpeg=r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffmpeg.exe'
for name in selected:
    p=b/Path(name).stem
    if (p/'QR_DECODE.json').exists() or (p/'QR_DECODE_RECEIPT.json').exists():continue
    # Completed no-QR source is already inspected; retain its established source limit.
    if (p/'REVIEW.md').exists():continue
    source=json.loads((p/'SOURCE.json').read_text(encoding='utf-8'))
    out=p/'qr_intake';out.mkdir(exist_ok=True)
    if (out/'INTAKE_RESULT.json').exists():continue
    attempts=[]; found=None
    for sec in [1,2,5,8]:
        image=out/f't{sec:07.2f}.png'
        if not image.exists():
            subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-threads','2','-ss',str(sec),'-i',str(root/name),'-frames:v','1',str(image)],check=True,timeout=60)
        codes=list(dict.fromkeys(x.text for x in zxingcpp.read_barcodes(cv2.imread(str(image)))))
        attempts.append({'source_seconds':sec,'image':str(image),'detected_codes':len(codes)})
        if len(codes)!=1:continue
        try: decoded=decoder.decode_payload(codes[0])
        except Exception as e:
            attempts[-1]['payload_error']=str(e);continue
        if len(decoded['trainerIds'])+len(decoded['pokemonIds'])!=20:continue
        receipt=out/f'QR_DECODE_{sec:07.2f}.json'
        if not receipt.exists():
            subprocess.run([sys.executable,str(b/'qr_support/decode_retained_qr.py'),str(image),'--source-video',name,'--seconds',str(sec),'--source-sha256',source['sha256'],'--out',str(receipt)],check=True,timeout=60,capture_output=True)
        found=str(receipt);break
    result={'source_video':name,'source_sha256':source['sha256'],'scan_utc':datetime.now(timezone.utc).isoformat(),'attempts':attempts,'decoded_receipt':found,
        'scope':'Automated source-bound early QR intake only. Full Sol source review must establish displayed deck label, continuity, classification and game binding. No QR detected in these candidates does not establish absence throughout footage.'}
    (out/'INTAKE_RESULT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'source':name,'decoded':bool(found),'receipt':found}),flush=True)
