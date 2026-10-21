"""Fresh bounded download request using an attribute-only placeholder handle."""
import argparse
import ctypes
import json
import subprocess
import sys
from ctypes import wintypes
from datetime import datetime, timezone
from pathlib import Path

BATCH = Path(__file__).resolve().parent
ROOT = BATCH.parent.parent
NAMES = ['20261012_003458000_iOS.MP4', '20261012_004435000_iOS.MP4']
ap = argparse.ArgumentParser()
ap.add_argument('--child', choices=NAMES)
a = ap.parse_args()
if a.child:
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    cloud = ctypes.WinDLL('CldApi', use_last_error=True)
    kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    kernel.CreateFileW.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    cloud.CfHydratePlaceholder.argtypes = [wintypes.HANDLE, ctypes.c_longlong, ctypes.c_longlong, wintypes.DWORD, wintypes.LPVOID]
    cloud.CfHydratePlaceholder.restype = wintypes.LONG
    print('Opening attribute handle', flush=True)
    handle = kernel.CreateFileW(str(ROOT / a.child), 0x80, 7, None, 3, 0, None)
    if handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        print('Requesting complete local bytes', flush=True)
        result = cloud.CfHydratePlaceholder(handle, 0, -1, 0, None)
        if result != 0:
            raise RuntimeError(f'Cloud hydration failed: HRESULT 0x{result & 0xffffffff:08X}')
        print('S_OK', flush=True)
    finally:
        kernel.CloseHandle(handle)
else:
    results = []
    for name in NAMES:
        p = ROOT / name
        if not p.exists():
            continue
        receipt = {'source_video': name, 'attempt_utc': datetime.now(timezone.utc).isoformat(),
                   'operation': 'full Cloud Files hydration with FILE_READ_ATTRIBUTES handle',
                   'source_contents_modified': False, 'source_sha256': None,
                   'documentation': 'https://learn.microsoft.com/en-us/windows/win32/api/cfapi/nf-cfapi-cfhydrateplaceholder'}
        try:
            r = subprocess.run([sys.executable, __file__, '--child', name], capture_output=True, text=True, timeout=45)
            receipt.update(exit_code=r.returncode, stdout=r.stdout.strip(), stderr=r.stderr.strip())
        except subprocess.TimeoutExpired as e:
            output = e.stdout.decode(errors='replace') if isinstance(e.stdout, bytes) else e.stdout
            receipt.update(exit_code=None, stdout=output, error='Timed out after45 seconds; child terminated.')
        folder = BATCH / p.stem / 'source_access_history'
        folder.mkdir(exist_ok=True)
        target = folder / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.json')
        target.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
        results.append(receipt)
        print(json.dumps(receipt), flush=True)
    (BATCH / 'LATEST_DOWNLOAD_RETRY.json').write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8')
