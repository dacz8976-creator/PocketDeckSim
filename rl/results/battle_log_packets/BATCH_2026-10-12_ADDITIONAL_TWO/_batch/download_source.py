"""Bounded cloud download request for one exact authorized source."""
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
NAMES = ['20261012_225319000_iOS.MP4', '20261012_230258000_iOS.MP4']
parser = argparse.ArgumentParser()
parser.add_argument('--child', action='store_true')
parser.add_argument('--video', choices=NAMES, default=NAMES[0])
args = parser.parse_args()
NAME = args.video
if args.child:
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    cloud = ctypes.WinDLL('CldApi', use_last_error=True)
    kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    kernel.CreateFileW.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    cloud.CfHydratePlaceholder.argtypes = [wintypes.HANDLE, ctypes.c_longlong, ctypes.c_longlong, wintypes.DWORD, wintypes.LPVOID]
    cloud.CfHydratePlaceholder.restype = wintypes.LONG
    print('Opening attribute-only handle', flush=True)
    handle = kernel.CreateFileW(str(ROOT / NAME), 0x80, 7, None, 3, 0, None)
    if handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        print('Requesting complete download', flush=True)
        result = cloud.CfHydratePlaceholder(handle, 0, -1, 0, None)
        if result:
            raise RuntimeError(f'Hydration HRESULT 0x{result & 0xffffffff:08X}')
        print('Download S_OK', flush=True)
    finally:
        kernel.CloseHandle(handle)
else:
    sys.path.insert(0, str(ROOT / 'Recording_QA'))
    from free_reviewed_video_space import metadata
    receipt = {'source': NAME, 'attempt_utc': datetime.now(timezone.utc).isoformat(),
               'operation': 'bounded attribute-handle Cloud Files download',
               'source_contents_modified': False, 'before': metadata(ROOT / NAME)}
    try:
        result = subprocess.run([sys.executable, __file__, '--child', '--video', NAME], capture_output=True, text=True, timeout=45)
        receipt.update(exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr)
    except subprocess.TimeoutExpired as error:
        output = error.stdout.decode(errors='replace') if isinstance(error.stdout, bytes) else error.stdout
        receipt.update(exit_code=None, stdout=output, error='Cloud request timed out after 45 seconds; only the task-owned request process was stopped.')
    receipt['after'] = metadata(ROOT / NAME)
    history = BATCH / Path(NAME).stem / 'source_access_history'
    history.mkdir(parents=True, exist_ok=True)
    target = history / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.json')
    target.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt), flush=True)
