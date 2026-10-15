"""Retain embedded UTC recording clocks and convert to owner's local dates."""
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

BATCH=Path(__file__).resolve().parent
ROOT=BATCH.parent.parent
PROBE=r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffprobe.exe'
for packet in sorted(BATCH.iterdir()):
    source_path=packet/'SOURCE.json'
    if not source_path.is_file() or (packet/'RECORDING_METADATA.json').exists():
        continue
    source=json.loads(source_path.read_text(encoding='utf-8'))
    metadata=json.loads(subprocess.check_output([PROBE,'-v','error','-show_entries','format_tags=creation_time:stream_tags=creation_time','-of','json',source['source_path_at_review']],timeout=45))
    creation=metadata.get('format',{}).get('tags',{}).get('creation_time')
    local=datetime.fromisoformat(creation.replace('Z','+00:00')).astimezone(ZoneInfo('America/Chicago')) if creation else None
    receipt={'source_video':source['video_basename'],'source_sha256':source['sha256'],'captured_utc':datetime.now(timezone.utc).isoformat(),
        'raw_probe':metadata,'embedded_creation_time_utc':creation,'recording_time_america_chicago':local.isoformat() if local else None,
        'match_date_local':local.date().isoformat() if local else None,'basis':'Embedded movie creation_time establishes recording clock. Match date uses local recording date unless filmed evidence contradicts it.',
        'limits':['Source filename itself does not establish a local date; this companion preserves the frozen SOURCE.json.']}
    (packet/'RECORDING_METADATA.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(source['video_basename']+': '+str(receipt['match_date_local']),flush=True)
