"""Bounded source-native QR and creation-time intake for the two added uploads."""
import json
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

BATCH = Path(__file__).resolve().parent
ROOT = BATCH.parent.parent
ffmpeg = r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffmpeg.exe'
probe = r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffprobe.exe'
decoder = ROOT / 'Recording_QA/BATCH_2026-10-06_NEW_PAUSE_GAMES/qr_support/decode_retained_qr.py'
for stem in ['20261012_210041000_iOS', '20261012_210823000_iOS']:
    packet = BATCH / stem
    source = json.loads((packet / 'SOURCE.json').read_text(encoding='utf-8'))
    original = ROOT / source['video_basename']
    metadata = json.loads(subprocess.check_output([probe, '-v', 'error', '-show_entries', 'format_tags=creation_time:stream_tags=creation_time', '-of', 'json', str(original)]))
    utc_text = metadata['format']['tags']['creation_time']
    started = datetime.fromisoformat(utc_text.replace('Z', '+00:00'))
    local = started.astimezone(timezone(timedelta(hours=-5), 'CDT'))
    times = {'source_video': source['video_basename'], 'creation_time_utc_from_container': utc_text,
             'container_video_audio_creation_times_agree': all(stream['tags']['creation_time'] == utc_text for stream in metadata['streams']),
             'local_recording_start': local.isoformat(), 'local_match_date': local.date().isoformat(), 'local_timezone': 'America/Chicago',
             'date_basis': 'ffprobe container and stream creation_time converted to owner local timezone'}
    (packet / 'SOURCE_TIME.json').write_text(json.dumps(times, indent=2) + '\n', encoding='utf-8')
    intake = packet / 'intake'
    intake.mkdir(exist_ok=True)
    frame = intake / 't0000.00.jpg'
    if not frame.exists():
        subprocess.run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-threads', '1', '-ss', '0', '-i', str(original), '-frames:v', '1', '-q:v', '2', str(frame)], check=True, timeout=45)
    receipt = packet / 'QR_DECODE.json'
    if not receipt.exists():
        result = subprocess.run([sys.executable, '-X', 'utf8', str(decoder), str(frame), '--source-video', source['video_basename'], '--seconds', '0', '--source-sha256', source['sha256'], '--out', str(receipt)], capture_output=True, text=True, encoding='utf-8', timeout=60)
        (packet / 'QR_INTAKE_RESULT.json').write_text(json.dumps({'source': source['video_basename'], 'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'source': stem, 'qr_decoded': result.returncode == 0, 'local_match_date': times['local_match_date']}), flush=True)
