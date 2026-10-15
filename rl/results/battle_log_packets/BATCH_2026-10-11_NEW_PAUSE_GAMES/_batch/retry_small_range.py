"""Try a small Cloud Files range without loading an entire cloud video."""
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
selected = json.loads((BATCH / 'OWNER_CONTEXT.json').read_text(encoding='utf-8'))['selected_sources']
ap = argparse.ArgumentParser()
ap.add_argument('video', choices=selected)
ap.add_argument('--child', action='store_true')
a = ap.parse_args()
if a.child:
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    cloud = ctypes.WinDLL('CldApi', use_last_error=True)
    kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    kernel.CreateFileW.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    cloud.CfHydratePlaceholder.argtypes = [wintypes.HANDLE, ctypes.c_longlong, ctypes.c_longlong, wintypes.DWORD, wintypes.LPVOID]
    cloud.CfHydratePlaceholder.restype = wintypes.LONG
    handle = kernel.CreateFileW(str(ROOT / a.video), 1, 7, None, 3, 0, None)
    if handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        result = cloud.CfHydratePlaceholder(handle, 0, 1024 * 1024, 0, None)
        if result != 0:
            raise RuntimeError(f'Cloud range hydration failed: HRESULT 0x{result & 0xffffffff:08X}')
    finally:
        kernel.CloseHandle(handle)
    with (ROOT / a.video).open('rb') as source:
        header = source.read(32)
    print(json.dumps({'range_hydration': 'S_OK', 'first32_read': len(header) == 32}), flush=True)
else:
    receipt = {'source': a.video, 'attempt_utc': datetime.now(timezone.utc).isoformat(),
               'operation': 'hydrate first1MiB only, then read32 bytes', 'source_contents_modified': False, 'sha256': None}
    try:
        r = subprocess.run([sys.executable, __file__, a.video, '--child'], capture_output=True, text=True, timeout=30)
        receipt.update(exit_code=r.returncode, stdout=r.stdout.strip(), stderr=r.stderr.strip())
    except subprocess.TimeoutExpired:
        receipt.update(exit_code=None, error='Small-range hydration timed out after30 seconds; child terminated.')
    packet = BATCH / Path(a.video).stem
    target = packet / 'SMALL_RANGE_RETRY.json'
    target.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt), flush=True)
