import concurrent.futures
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

batch = Path(__file__).resolve().parent
root = batch.parent.parent
names = [f'20261009_{s}000_iOS.MP4' for s in ['195432', '222100', '222740']]

def probe(name):
    code = 'import pathlib,sys; p=pathlib.Path(sys.argv[1]); f=p.open("rb"); print(f.read(64).hex()); f.close()'
    try:
        run = subprocess.run([sys.executable, '-c', code, str(root / name)], capture_output=True, text=True, timeout=20)
        return {'video': name, 'readable_first_64_bytes': run.returncode == 0 and len(run.stdout.strip()) == 128, 'exit_code': run.returncode, 'output': run.stdout.strip(), 'error': run.stderr.strip()}
    except subprocess.TimeoutExpired:
        return {'video': name, 'readable_first_64_bytes': False, 'error': 'Read did not complete within 20 seconds after OneDrive startup'}

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    results = list(pool.map(probe, names))
report = {'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'note': 'Bounded read check after starting OneDrive; a successful header read alone is not complete source verification.', 'results': results}
(batch / 'ONEDRIVE_RETRY.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report, indent=2))
