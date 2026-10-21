"""Bounded hydration/readability retry for this batch, preserving originals."""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BATCH = Path(__file__).resolve().parent
ROOT = BATCH.parent.parent
selected = json.loads((BATCH / 'OWNER_CONTEXT.json').read_text(encoding='utf-8'))['selected_sources']
ap = argparse.ArgumentParser()
ap.add_argument('--hydrate', choices=selected)
args = ap.parse_args()
if args.hydrate:
    sys.path.insert(0, str(ROOT / 'Recording_QA'))
    from hydrate_competitive_source import hydrate
    hydrate(ROOT / args.hydrate)
    print('S_OK', flush=True)
else:
    receipts = []
    for name in selected:
        packet = BATCH / Path(name).stem
        if (packet / 'SOURCE.json').exists():
            continue
        source = ROOT / name
        receipt = {'source': name, 'attempt_utc': datetime.now(timezone.utc).isoformat(),
                   'source_bytes': source.stat().st_size, 'operation': 'bounded Cloud Files hydration',
                   'source_contents_modified': False, 'sha256': None}
        try:
            result = subprocess.run([sys.executable, __file__, '--hydrate', name], capture_output=True,
                                    text=True, timeout=45)
            receipt.update(exit_code=result.returncode, stdout=result.stdout.strip(), stderr=result.stderr.strip())
        except subprocess.TimeoutExpired:
            receipt.update(exit_code=None, error='Hydration child timed out after45 seconds and was terminated.')
        packet.mkdir(exist_ok=True)
        history = packet / 'source_access_history'
        history.mkdir(exist_ok=True)
        (history / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.json')).write_text(
            json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
        receipts.append(receipt)
        print(json.dumps(receipt), flush=True)
    (BATCH / 'SOURCE_ACCESS_RETRY.json').write_text(json.dumps(receipts, indent=2) + '\n', encoding='utf-8')
