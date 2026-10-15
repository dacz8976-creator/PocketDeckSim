import json,sys,subprocess,time
from pathlib import Path
from PIL import Image
B=Path(__file__).resolve().parent
receipt=json.loads((B/'ROOT_SOURCE_VERIFICATION.json').read_text(encoding='utf-8-sig'))
assert receipt['status']=='verified_sha256_match',receipt['status']
video=receipt['current_path']
out=B/'turn_evidence';out.mkdir(exist_ok=True)
times=[float(x) for x in sys.argv[1:]]
existing=list(out.glob('t*.jpg'))
assert len(existing)+sum(not (out/f't{t:07.2f}.jpg').exists() for t in times)<=86,'cap 86 requires checkpoint'
ff=r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffmpeg.exe'
manifest=json.loads((B/'EXTRACTION_MANIFEST.json').read_text()) if (B/'EXTRACTION_MANIFEST.json').exists() else []
for t in times:
    path=out/f't{t:07.2f}.jpg'
    if path.exists():continue
    subprocess.run([ff,'-hide_banner','-loglevel','error','-threads','2','-ss',str(t),'-i',video,'-frames:v','1','-q:v','2','-y',str(path)],check=True)
    with Image.open(path) as im:
        w,h=im.size
        bottom=[0,int(h*.8),w,h];top=[0,0,w,550]
        im.crop(bottom).save(out/f'b{t:07.2f}.jpg',quality=95)
        im.crop(top).save(out/f'p{t:07.2f}.jpg',quality=95)
    manifest.append({'evidence_id':f'F{t:07.2f}','source_video':receipt['source'],'source_sha256':receipt['expected_sha256'],'requested_source_seconds':t,'actual_frame_seconds_if_measured':None,'full_frame_path':str(path),'native_dimensions':{'width':w,'height':h},'bottom_crop':{'path':str(out/f'b{t:07.2f}.jpg'),'pixel_bounds_x0_y0_x1_y1':bottom},'top_crop':{'path':str(out/f'p{t:07.2f}.jpg'),'pixel_bounds_x0_y0_x1_y1':top}})
    (B/'EXTRACTION_MANIFEST.json').write_text(json.dumps(manifest,indent=2))
print('new retained native total',len(manifest))
