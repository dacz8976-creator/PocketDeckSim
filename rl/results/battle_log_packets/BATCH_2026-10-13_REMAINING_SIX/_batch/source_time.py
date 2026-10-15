"""Root metadata dates for exactly the six frozen sources, no source mutations."""
import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
BATCH = Path(__file__).resolve().parent
ROOT = BATCH.parent.parent
context = json.loads((BATCH / 'OWNER_CONTEXT.json').read_text(encoding='utf-8'))
for name in context['selected_sources']:
    packet = BATCH / Path(name).stem
    target = packet / 'SOURCE_TIME.json'
    assert not target.exists(), 'Do not overwrite source-time provenance'
    source = json.loads((packet / 'SOURCE.json').read_text(encoding='utf-8'))
    raw = json.loads(subprocess.check_output(['C:/Program Files/MiniTool Screen Recorder/FFmpeg/ffprobe.exe', '-v', 'error', '-show_entries', 'format_tags=creation_time:stream_tags=creation_time', '-of', 'json', str(ROOT / name)]))
    utc = raw['format']['tags']['creation_time']
    local = datetime.fromisoformat(utc.replace('Z', '+00:00')).astimezone(timezone(timedelta(hours=-5)))
    assert local.date().isoformat() == '2026-10-12'
    data = {'source_video': name, 'source_sha256': source['sha256'], 'probed_utc': datetime.now(timezone.utc).isoformat(), 'probe_output': raw, 'creation_time_utc': utc, 'creation_time_local': local.isoformat(), 'match_date_local': local.date().isoformat(), 'timezone': 'America/Chicago', 'utc_offset': '-05:00', 'basis': 'Container and stream creation metadata converted to Chicago daylight time; worker must corroborate visible phone clock and report any discrepancy. Filename uses UTC recording date, preserved unchanged.'}
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(name + ' -> ' + local.isoformat())
