"""Bounded read-only availability checks, without claiming source identity."""
import concurrent.futures
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parent.parent
batch = root / 'Recording_QA/BATCH_2026-10-09_NEW_PAUSE_GAMES'
names = json.loads((batch / 'OWNER_CONTEXT.json').read_text(encoding='utf-8'))['selected_sources']
def check(name):
    p = root / name
    before = p.stat()
    result = {'video': name, 'bytes': before.st_size, 'file_attributes': before.st_file_attributes,
              'checked_utc': datetime.now(timezone.utc).isoformat(), 'sha256': None, 'visual_review': 'not_started'}
    try:
        proc = subprocess.run([sys.executable, '-c', 'import sys; f=open(sys.argv[1],"rb"); print(f.read(32).hex())', str(p)],
                              capture_output=True, text=True, timeout=20)
        result.update(read_exit_code=proc.returncode, read_stdout=proc.stdout.strip(), read_stderr=proc.stderr.strip(),
                      first_bytes_readable=proc.returncode == 0 and bool(proc.stdout.strip()))
    except subprocess.TimeoutExpired:
        result.update(first_bytes_readable=False, error='20-second cloud-file read timeout; child terminated')
    folder = batch / p.stem
    folder.mkdir(exist_ok=True)
    (folder / 'AVAILABILITY.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result),flush=True)
    return result
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    results = list(pool.map(check,names))
(batch / 'SOURCE_AVAILABILITY.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
