import hashlib
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

root = Path('/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs')
batch = root / 'Recording_QA/BATCH_2026-10-09_NEW_UPLOADS'
names = [f'20261009_{stamp}000_iOS.MP4' for stamp in ['195432', '222100', '222740']]
results = []
for name in names:
    path = root / name
    packet = batch / path.stem
    before = (path.stat().st_size, path.stat().st_mtime_ns)
    time.sleep(1)
    assert before == (path.stat().st_size, path.stat().st_mtime_ns), name
    meta = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-print_format', 'json', '-show_format', '-show_streams', str(path)], timeout=45))
    stream = next(s for s in meta['streams'] if s['codec_type'] == 'video')
    digest = hashlib.sha256()
    with path.open('rb') as media:
        for chunk in iter(lambda: media.read(1024 * 1024), b''):
            digest.update(chunk)
    assert before == (path.stat().st_size, path.stat().st_mtime_ns), name
    windows_path = 'C:\\Users\\dacz8\\OneDrive\\Desktop\\Battle Logs\\' + name
    source = {'video_basename': name, 'sha256': digest.hexdigest(), 'bytes': before[0], 'duration_seconds': float(meta['format']['duration']), 'width': stream['width'], 'height': stream['height'], 'avg_frame_rate': stream.get('avg_frame_rate'), 'container_creation_utc': meta['format'].get('tags', {}).get('creation_time'), 'source_path_at_review': windows_path, 'current_path': windows_path, 'recording_relationships': [], 'classification': 'pending visual classification', 'owner_request': 'Continue the three newly uploaded videos after source access restored', 'intake_utc': datetime.now(timezone.utc).isoformat(), 'prior_source_access_error': 'INTAKE_ERROR.json retained as historical evidence'}
    assert not (packet / 'SOURCE.json').exists(), f'Existing source binding: {name}'
    (packet / 'SOURCE.json').write_text(json.dumps(source, indent=2) + '\n')
    (packet / 'PROBE.json').write_text(json.dumps(meta, indent=2) + '\n')
    frames = packet / 'intake_frames'
    frames.mkdir(exist_ok=True)
    times = [0, min(20, source['duration_seconds'] / 4), source['duration_seconds'] / 2, source['duration_seconds'] - 1]
    for index, timestamp in enumerate(times):
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-ss', str(timestamp), '-i', str(path), '-frames:v', '1', '-q:v', '3', str(frames / f'{index}_{timestamp:.3f}s.jpg')], check=True, timeout=45)
    results.append(source)
    print(json.dumps(source), flush=True)
(batch / 'RESUMED_INTAKE.json').write_text(json.dumps(results, indent=2) + '\n')
