"""Request one bounded missing cloud range, preserving source bytes and receipts."""
import argparse
import ctypes
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from check_download_ranges import ROOT, BATCH, ranges, kernel, cloud
from ctypes import wintypes

p = argparse.ArgumentParser()
p.add_argument('--video', required=True, choices=['20261012_225319000_iOS.MP4', '20261012_230258000_iOS.MP4'])
p.add_argument('--child', action='store_true')
p.add_argument('--offset', type=int)
p.add_argument('--length', type=int)
a = p.parse_args()
if a.child:
    assert a.offset is not None and a.length is not None and a.offset >= 0 and 0 < a.length <= 64 * 1024 * 1024
    handle = kernel.CreateFileW(str(ROOT / a.video), 0x80, 7, None, 3, 0, None)
    if handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        cloud.CfHydratePlaceholder.argtypes = [wintypes.HANDLE, ctypes.c_longlong, ctypes.c_longlong, wintypes.DWORD, wintypes.LPVOID]
        cloud.CfHydratePlaceholder.restype = wintypes.LONG
        print(f'Requesting missing range {a.offset}+{a.length}', flush=True)
        hr = cloud.CfHydratePlaceholder(handle, a.offset, a.length, 0, None)
        if hr:
            raise RuntimeError(f'Hydration HRESULT 0x{hr & 0xffffffff:08X}')
        print('Range download S_OK', flush=True)
    finally:
        kernel.CloseHandle(handle)
else:
    before = ranges(ROOT / a.video)
    if not before['missing_ranges']:
        print(json.dumps({'source': a.video, 'all_ranges_present': True}))
        sys.exit(0)
    first = before['missing_ranges'][0]
    length = min(first['length'], 64 * 1024 * 1024)
    receipt = {'attempt_utc': datetime.now(timezone.utc).isoformat(), 'source': a.video, 'operation': 'one 64 MiB or smaller missing-range download', 'source_contents_modified': False, 'before': before, 'requested_offset': first['offset'], 'requested_length': length,
               'documentation': 'https://learn.microsoft.com/en-us/windows/win32/api/cfapi/nf-cfapi-cfhydrateplaceholder'}
    try:
        r = subprocess.run([sys.executable, __file__, '--child', '--video', a.video, '--offset', str(first['offset']), '--length', str(length)], capture_output=True, text=True, timeout=300)
        receipt.update(exit_code=r.returncode, stdout=r.stdout, stderr=r.stderr)
    except subprocess.TimeoutExpired as e:
        receipt.update(exit_code=None, error='Task-owned download request timed out after 300 seconds', stdout=e.stdout.decode(errors='replace') if isinstance(e.stdout, bytes) else e.stdout)
    receipt['after'] = ranges(ROOT / a.video)
    history = BATCH / Path(a.video).stem / 'source_access_history'
    history.mkdir(parents=True, exist_ok=True)
    out = history / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.missing_range.json')
    out.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt, indent=2), flush=True)
