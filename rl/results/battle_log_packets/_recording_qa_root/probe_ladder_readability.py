"""Bound a tiny read of one requested upload; never claims video integrity."""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('video', choices=['20261014_143111000_iOS.MP4', '20261014_144627000_iOS.MP4', '20261014_145449000_iOS.MP4'])
a = p.parse_args()
code = 'import sys;from pathlib import Path;f=Path(sys.argv[1]).open("rb");print(f.read(32).hex(),flush=True)'
receipt = {'source': a.video, 'utc': datetime.now(timezone.utc).isoformat(), 'scope': '32-byte readability only; no review or integrity conclusion'}
try:
    r = subprocess.run([sys.executable, '-c', code, a.video], capture_output=True, text=True, timeout=20)
    receipt.update(exit_code=r.returncode, stdout=r.stdout, stderr=r.stderr)
except subprocess.TimeoutExpired:
    receipt['result'] = 'Read timed out after 20 seconds; child stopped'
out = Path(__file__).resolve().parent / 'BATCH_2026-10-14_NEW_LADDER_FOUR' / ('READABILITY.' + a.video + '.' + datetime.now(timezone.utc).strftime('%H%M%S') + '.json')
out.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
print(json.dumps(receipt), flush=True)
