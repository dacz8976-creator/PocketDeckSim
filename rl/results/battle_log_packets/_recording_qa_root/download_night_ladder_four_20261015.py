"""Bounded local hydration of the four owner-named night ladder sources."""
import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from free_reviewed_video_space import metadata

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / 'Recording_QA/BATCH_2026-10-15_NIGHT_LADDER_FOUR'
NAMES = ['20261016_015753000_iOS.MP4', '20261016_020517000_iOS.MP4',
         '20261016_020806000_iOS.MP4', '20261016_024253000_iOS.MP4']

def save(path, data):
    with path.open('x', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

BATCH.mkdir(exist_ok=True)
if not (BATCH / 'OWNER_CONTEXT.json').exists():
    save(BATCH / 'OWNER_CONTEXT.json', {'requested_utc': datetime.now(timezone.utc).isoformat(),
        'selected_sources': NAMES, 'scope': 'Four new owner-named ladder recordings only; download, full review, independent acceptance, live log/readback and archive.',
        'owner_filename_evidence': 'Attached Photo1 progress screenshot: all four uploads Done.',
        'owner_photo_path': 'C:/Users/dacz8/.codex/codex-remote-attachments/01a14162-ced4-7860-9ab6-dc3d660aacdc/92A663C5-8203-479B-9E00-FC1732EBA450/1-Photo-1.jpg',
        'artifact': 'https://claude.ai/artifact/GHSfGSCzNiWNj8SFPXV3R1', 'shared_writer': '/root', 'pause_games_supplement': False})
    with (ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='') as f:
        save(BATCH / 'INDEX_BEFORE.json', list(csv.DictReader(f)))
receipts = []
for name in NAMES:
    path = ROOT / name
    packet = BATCH / path.stem
    packet.mkdir(exist_ok=True)
    receipt = {'source_filename': name, 'checked_utc': datetime.now(timezone.utc).isoformat(),
        'exists_locally': path.exists(), 'visual_review_started': False, 'sha256': None, 'duration_seconds': None}
    if path.exists():
        receipt['before'] = metadata(path)
        if not receipt['before']['online_only'] and receipt['before']['allocated_bytes'] == receipt['before']['logical_bytes']:
            receipt['download_state'] = 'allocated locally; hash/duration binding still required'
        else:
            code = 'import sys;from pathlib import Path;sys.path.insert(0,sys.argv[1]);from hydrate_competitive_source import hydrate;hydrate(Path(sys.argv[2]));print("S_OK",flush=True)'
            try:
                result = subprocess.run([sys.executable, '-c', code, str(ROOT / 'Recording_QA'), str(path)], capture_output=True, text=True, timeout=45)
                receipt.update(hydration_exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr)
            except subprocess.TimeoutExpired:
                receipt['download_state'] = 'Cloud Files hydration timed out after45seconds; child stopped; no integrity or review claim'
        receipt['after'] = metadata(path)
    else:
        receipt['download_state'] = 'Named owner upload has not appeared in local folder yet'
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    save(packet / ('DOWNLOAD_CHECK.' + stamp + '.json'), receipt)
    receipts.append(receipt)
    print(json.dumps(receipt), flush=True)
save(BATCH / ('DOWNLOAD_STATUS.' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.json'), receipts)
