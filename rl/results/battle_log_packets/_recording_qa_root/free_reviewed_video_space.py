"""Use OneDrive's documented online-only state for completed archived videos.

Metadata queries never read video contents. No deletion operation is used.
"""
import argparse
import csv
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = ROOT / 'Reviewed'
PLACEHOLDER = 0x1
IN_SYNC = 0x8
OFFLINE = 0x1000
PINNED = 0x80000
UNPINNED = 0x100000


class FindData(ctypes.Structure):
    _fields_ = [('attributes', wintypes.DWORD),
                ('creation', wintypes.FILETIME), ('access', wintypes.FILETIME),
                ('write', wintypes.FILETIME), ('size_high', wintypes.DWORD),
                ('size_low', wintypes.DWORD), ('reserved0', wintypes.DWORD),
                ('reserved1', wintypes.DWORD), ('name', wintypes.WCHAR * 260),
                ('alternate_name', wintypes.WCHAR * 14)]


kernel = ctypes.WinDLL('kernel32', use_last_error=True)
cloud = ctypes.WinDLL('cldapi', use_last_error=True)
native = ctypes.WinDLL('ntdll')
# Windows can disguise cloud placeholders as ordinary files for legacy processes.
# Expose them in this process so the sync and disk-state checks are accurate.
native.RtlSetProcessPlaceholderCompatibilityMode.argtypes = [ctypes.c_byte]
native.RtlSetProcessPlaceholderCompatibilityMode.restype = ctypes.c_byte
if native.RtlSetProcessPlaceholderCompatibilityMode(2) < 0:
    raise RuntimeError('Could not expose OneDrive placeholder metadata')
kernel.FindFirstFileW.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(FindData)]
kernel.FindFirstFileW.restype = wintypes.HANDLE
kernel.FindClose.argtypes = [wintypes.HANDLE]
kernel.FindClose.restype = wintypes.BOOL
kernel.GetCompressedFileSizeW.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(wintypes.DWORD)]
kernel.GetCompressedFileSizeW.restype = wintypes.DWORD
cloud.CfGetPlaceholderStateFromFindData.argtypes = [ctypes.POINTER(FindData)]
cloud.CfGetPlaceholderStateFromFindData.restype = wintypes.DWORD


def metadata(path):
    data = FindData()
    handle = kernel.FindFirstFileW(str(path), ctypes.byref(data))
    if handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    kernel.FindClose(handle)
    state = cloud.CfGetPlaceholderStateFromFindData(ctypes.byref(data))
    if state == 0xffffffff:
        raise RuntimeError(f'Invalid cloud placeholder state: {path.name}')
    high = wintypes.DWORD()
    ctypes.set_last_error(0)
    low = kernel.GetCompressedFileSizeW(str(path), ctypes.byref(high))
    error = ctypes.get_last_error()
    if low == 0xffffffff and error:
        raise ctypes.WinError(error)
    allocated = (high.value << 32) | low
    return {'logical_bytes': (data.size_high << 32) | data.size_low,
            'allocated_bytes': allocated, 'attributes': data.attributes,
            'placeholder_state': state, 'cloud_placeholder': bool(state & PLACEHOLDER),
            'in_sync': bool(state & IN_SYNC), 'pinned': bool(data.attributes & PINNED),
            'unpinned': bool(data.attributes & UNPINNED),
            'online_only': bool(data.attributes & OFFLINE) and allocated == 0}


def main():
    p = argparse.ArgumentParser()
    selection = p.add_mutually_exclusive_group()
    selection.add_argument('--video', help='One exact completed video basename; otherwise all Reviewed videos')
    selection.add_argument('--videos', nargs='+', help='Exact completed video basenames for a bounded batch')
    p.add_argument('--apply', action='store_true', help='Request OneDrive online-only state')
    p.add_argument('--wait-seconds', type=float, default=20, help='Bounded verification wait, at most 45 seconds')
    args = p.parse_args()
    if not 0 <= args.wait_seconds <= 45:
        p.error('wait-seconds must be between zero and 45')
    sync_roots = [Path(os.environ[key]).resolve() for key in ['OneDrive', 'OneDriveConsumer', 'OneDriveCommercial'] if os.environ.get(key)]
    if not any(ARCHIVE.resolve().is_relative_to(sync_root) for sync_root in sync_roots):
        raise RuntimeError('Reviewed is not inside a configured OneDrive sync root')
    rows = list(csv.DictReader((ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='')))
    approved = {r['Video']: r for r in rows if r['Status'] == 'Reviewed' and r['Location'].replace('\\', '/') == 'Reviewed/' + r['Video']}
    selected = [args.video] if args.video else args.videos
    if selected:
        if len(set(selected)) != len(selected) or any(Path(name).name != name or name not in approved for name in selected):
            p.error('Expected unique exact, completed, archived video basenames')
        files = [ARCHIVE / name for name in selected]
    else:
        files = sorted(path for path in ARCHIVE.iterdir() if path.is_file() and path.suffix.lower() in ['.mp4', '.mov', '.m4v', '.mkv', '.avi'])
        if any(path.name not in approved for path in files):
            raise RuntimeError('Archive contains a video without a completed index record')
    entries = []
    for path in files:
        if path.resolve().parent != ARCHIVE.resolve():
            raise RuntimeError('Target outside Reviewed')
        before = metadata(path)
        entry = {'video': path.name, 'path': str(path), 'before': before, 'requested_online_only': False}
        if args.apply and not before['online_only']:
            if not before['cloud_placeholder'] or not before['in_sync']:
                entry['pending_reason'] = 'Waiting for OneDrive to finish uploading/syncing; local contents retained'
            else:
                attrib = str(Path(os.environ['SystemRoot']) / 'System32' / 'attrib.exe')
                # A previously online-only video can be cached again after inspection.
                # Clear its existing preference first so OneDrive receives a fresh change.
                if before['unpinned']:
                    reset = subprocess.run([attrib, '-U', '-P', str(path)], capture_output=True, text=True)
                    if reset.returncode:
                        raise RuntimeError(f'OneDrive state reset failed: {path.name}: {reset.stderr or reset.stdout}')
                    entry['existing_unpinned_preference_refreshed'] = True
                    time.sleep(1)
                changed = subprocess.run([attrib, '+U', '-P', str(path)], capture_output=True, text=True)
                if changed.returncode:
                    raise RuntimeError(f'OneDrive state request failed: {path.name}: {changed.stderr or changed.stdout}')
                entry['requested_online_only'] = True
        entries.append(entry)
    deadline = time.monotonic() + (args.wait_seconds if args.apply else 0)
    while True:
        for entry in entries:
            entry['after'] = metadata(Path(entry['path']))
            if entry['after']['logical_bytes'] != entry['before']['logical_bytes']:
                raise RuntimeError('Logical video size changed')
        if all(entry['after']['online_only'] for entry in entries) or time.monotonic() >= deadline:
            break
        time.sleep(min(1, max(0, deadline - time.monotonic())))
    before_bytes = sum(e['before']['allocated_bytes'] for e in entries)
    after_bytes = sum(e['after']['allocated_bytes'] for e in entries)
    result = {'operation': 'OneDrive online-only request' if args.apply else 'Read-only storage inventory',
              'created_at_utc': datetime.now(timezone.utc).isoformat(),
              'videos': len(entries), 'online_only': sum(e['after']['online_only'] for e in entries),
              'allocated_bytes_before': before_bytes, 'allocated_bytes_after': after_bytes,
              'local_bytes_reclaimed': before_bytes - after_bytes, 'files_deleted': 0,
              'method': 'Microsoft-documented attrib +U -P; only in-sync cloud placeholders are changed',
              'verification': 'Cloud placeholder metadata and actual allocated disk bytes; video contents are never read',
              'documentation': 'https://learn.microsoft.com/en-us/sharepoint/files-on-demand-windows',
              'entries': entries}
    directory = ROOT / 'Recording_QA' / 'CLOUD_STORAGE'
    directory.mkdir(exist_ok=True)
    name = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + ('.apply.json' if args.apply else '.inventory.json')
    (directory / name).write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in result.items() if key != 'entries'}, indent=2), flush=True)
    pending = [e['video'] for e in entries if not e['after']['online_only']]
    if pending:
        print(f'Still local: {len(pending)}; details in {directory / name}', flush=True)


if __name__ == '__main__':
    main()
