import hashlib
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

root = Path('/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs')
batch = root / 'Recording_QA/BATCH_2026-10-09_NEW_UPLOADS'
names = [f'20261009_{stamp}000_iOS.MP4' for stamp in ['193905','194240','194445','195029','195808','222740']]
before = {n: ((root/n).stat().st_size, (root/n).stat().st_mtime_ns) for n in names}
time.sleep(2)
for n in names:
    assert before[n] == ((root/n).stat().st_size, (root/n).stat().st_mtime_ns), f'Upload still writing: {n}'
out = []
errors = []
for name in names:
    p = root / name
    packet = batch / p.stem
    packet.mkdir(parents=True, exist_ok=True)
    if (packet/'SOURCE.json').exists():
        existing = json.loads((packet/'SOURCE.json').read_text())
        assert existing['bytes'] == p.stat().st_size, name
        out.append(existing)
        print(json.dumps({'video_basename':name,'existing_verified_intake_reused':True}),flush=True)
        continue
    try:
        meta = json.loads(subprocess.check_output(['ffprobe','-v','error','-print_format','json','-show_format','-show_streams',str(p)], stderr=subprocess.STDOUT, timeout=45))
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        msg = getattr(exc,'output',None)
        if isinstance(msg,bytes): msg=msg.decode(errors='replace')
        errors.append({'video_basename':name,'stage':'ffprobe','error':str(exc),'detail':msg})
        (packet/'INTAKE_ERROR.json').write_text(json.dumps(errors[-1],indent=2)+'\n')
        print(json.dumps(errors[-1]),flush=True)
        continue
    stream = next(s for s in meta['streams'] if s['codec_type']=='video')
    digest = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''):
            digest.update(b)
    assert before[name] == (p.stat().st_size, p.stat().st_mtime_ns), name
    win_path = 'C:\\Users\\dacz8\\OneDrive\\Desktop\\Battle Logs\\' + name
    source = {'video_basename':name,'sha256':digest.hexdigest(),'bytes':p.stat().st_size,
              'duration_seconds':float(meta['format']['duration']),'width':stream['width'],'height':stream['height'],
              'avg_frame_rate':stream.get('avg_frame_rate'),'container_creation_utc':meta['format'].get('tags',{}).get('creation_time'),
              'source_path_at_review':win_path,'current_path':win_path,'recording_relationships':[],
              'classification':'intake pending visual classification','owner_request':'Process these new uploads with usual full-review workflow',
              'intake_utc':datetime.now(timezone.utc).isoformat()}
    (packet/'SOURCE.json').write_text(json.dumps(source,indent=2)+'\n')
    (packet/'PROBE.json').write_text(json.dumps(meta,indent=2)+'\n')
    initial = packet / 'intake_frames'
    initial.mkdir(exist_ok=True)
    times = [0.0,min(20.0,source['duration_seconds']/4),source['duration_seconds']/2,max(0,source['duration_seconds']-1)]
    for i,t in enumerate(times):
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-ss',str(t),'-i',str(p),'-frames:v','1','-q:v','3',str(initial/f'{i}_{t:.3f}s.jpg')],check=True)
    out.append(source)
    print(json.dumps({k:source[k] for k in ['video_basename','duration_seconds','sha256','bytes']}),flush=True)
(batch/'INTAKE.json').write_text(json.dumps(out,indent=2)+'\n')
(batch/'INTAKE_ERRORS.json').write_text(json.dumps(errors,indent=2)+'\n')


