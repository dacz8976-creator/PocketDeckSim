"""Request a complete cloud download for one exact selected source."""
import argparse
import ctypes
import importlib.util
import json
import subprocess
import sys
from ctypes import wintypes
from datetime import datetime, timezone
from pathlib import Path

BATCH = Path(__file__).resolve().parent
ROOT = BATCH.parent.parent
NAMES = ['20261013_022530000_iOS.MP4', '20261013_030351000_iOS.MP4']
parser = argparse.ArgumentParser()
parser.add_argument('--video', choices=NAMES, required=True)
parser.add_argument('--child', action='store_true')
parser.add_argument('--check-only', action='store_true')
parser.add_argument('--missing-range', action='store_true')
parser.add_argument('--offset', type=int, default=0)
parser.add_argument('--length', type=int, default=-1)
args = parser.parse_args()
path = ROOT / args.video
assert path.resolve().parent == ROOT.resolve() and path.exists()
if args.child:
    assert args.offset >= 0
    assert args.length == -1 or (0 < args.length <= 64 * 1024 * 1024 and args.offset + args.length <= path.stat().st_size)
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    cloud = ctypes.WinDLL('CldApi', use_last_error=True)
    kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    kernel.CreateFileW.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    cloud.CfHydratePlaceholder.argtypes = [wintypes.HANDLE, ctypes.c_longlong, ctypes.c_longlong, wintypes.DWORD, wintypes.LPVOID]
    cloud.CfHydratePlaceholder.restype = wintypes.LONG
    handle = kernel.CreateFileW(str(path), 0x80, 7, None, 3, 0, None)
    if handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        print(f'Requesting download: {path.name}, offset {args.offset}, length {args.length}', flush=True)
        hr = cloud.CfHydratePlaceholder(handle, args.offset, args.length, 0, None)
        if hr:
            raise RuntimeError(f'Download HRESULT 0x{hr & 0xffffffff:08X}')
        print('Download request succeeded', flush=True)
    finally:
        kernel.CloseHandle(handle)
else:
    spec = importlib.util.spec_from_file_location('range_metadata', ROOT / 'Recording_QA/BATCH_2026-10-12_ADDITIONAL_TWO/check_download_ranges.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    record = {'created_utc': datetime.now(timezone.utc).isoformat(), 'source': path.name,
              'source_contents_modified': False, 'before': mod.ranges(path)}
    if not args.check_only and record['before']['missing_bytes']:
        subprocess.run(['attrib', '+P', '-U', str(path)], check=True, capture_output=True)
        command = [sys.executable, '-X', 'utf8', __file__, '--child', '--video', path.name]
        if args.missing_range:
            first_gap = record['before']['missing_ranges'][0]
            length = min(first_gap['length'], 64 * 1024 * 1024)
            record.update(requested_offset=first_gap['offset'], requested_length=length)
            command += ['--offset', str(first_gap['offset']), '--length', str(length)]
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=300)
            record.update(exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr)
        except subprocess.TimeoutExpired as error:
            record.update(exit_code=None, timeout_seconds=300,
                          stdout=error.stdout.decode(errors='replace') if isinstance(error.stdout, bytes) else error.stdout,
                          note='Only the task-owned download request process was stopped; background cloud download may continue.')
    record['after'] = mod.ranges(path)
    history = BATCH / path.stem / 'source_access_history'
    history.mkdir(parents=True, exist_ok=True)
    target = history / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.json')
    target.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(record), flush=True)
