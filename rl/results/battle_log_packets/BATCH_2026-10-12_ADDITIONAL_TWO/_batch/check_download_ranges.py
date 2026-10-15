"""Read-only Cloud Files range metadata. Does not read video data."""
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

BATCH = Path(__file__).resolve().parent
ROOT = BATCH.parent.parent
sys.path.insert(0, str(ROOT / 'Recording_QA'))
from free_reviewed_video_space import metadata

kernel = ctypes.WinDLL('kernel32', use_last_error=True)
cloud = ctypes.WinDLL('cldapi', use_last_error=True)
kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
kernel.CreateFileW.restype = wintypes.HANDLE
kernel.CloseHandle.argtypes = [wintypes.HANDLE]
cloud.CfGetPlaceholderRangeInfo.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_longlong, ctypes.c_longlong, wintypes.LPVOID, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
cloud.CfGetPlaceholderRangeInfo.restype = wintypes.LONG

class FileRange(ctypes.Structure):
    _fields_ = [('offset', ctypes.c_longlong), ('length', ctypes.c_longlong)]

def ranges(path):
    state = metadata(path)
    handle = kernel.CreateFileW(str(path), 0x80, 7, None, 3, 0, None)
    if handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        buffer = ctypes.create_string_buffer(65536)
        returned = wintypes.DWORD()
        hr = cloud.CfGetPlaceholderRangeInfo(handle, 1, 0, -1, buffer, len(buffer), ctypes.byref(returned))
        if hr:
            raise RuntimeError(f'Range metadata HRESULT 0x{hr & 0xffffffff:08X}')
        assert returned.value <= len(buffer) and returned.value % ctypes.sizeof(FileRange) == 0
        entries = (FileRange * (returned.value // ctypes.sizeof(FileRange))).from_buffer(buffer)
        present = sorted((max(0, r.offset), min(state['logical_bytes'], r.offset + r.length)) for r in entries)
        gaps = []
        cursor = 0
        for start, end in present:
            if start > cursor:
                gaps.append({'offset': cursor, 'length': start - cursor})
            cursor = max(cursor, end)
        if cursor < state['logical_bytes']:
            gaps.append({'offset': cursor, 'length': state['logical_bytes'] - cursor})
        return {'source': path.name, 'metadata': state, 'present_ranges': [{'offset': a, 'length': b-a} for a,b in present], 'missing_ranges': gaps, 'missing_bytes': sum(g['length'] for g in gaps)}
    finally:
        kernel.CloseHandle(handle)

if __name__ == '__main__':
    names = ['20261012_225319000_iOS.MP4', '20261012_230258000_iOS.MP4']
    result = {'checked_utc': datetime.now(timezone.utc).isoformat(), 'source_contents_read': False,
              'documentation': 'https://learn.microsoft.com/en-us/windows/win32/api/cfapi/nf-cfapi-cfgetplaceholderrangeinfo',
              'entries': [ranges(ROOT / name) for name in names]}
    out = BATCH / ('DOWNLOAD_RANGES.' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SfZ') + '.json')
    out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2), flush=True)
