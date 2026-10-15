"""Release only verified, completed, in-sync archive caches; preserve cloud files."""
import argparse
import csv
import ctypes
import json
import sys
from ctypes import wintypes
from datetime import datetime, timezone
from pathlib import Path

BATCH = Path(__file__).resolve().parent
ROOT = BATCH.parent.parent
sys.path.insert(0, str(ROOT / 'Recording_QA'))
import free_reviewed_video_space as storage

ALLOWED = ['20261012_004128000_iOS.MP4', '20261009_195432000_iOS.MP4',
           '20261009_222100000_iOS.MP4', '20261009_222740000_iOS.MP4']
ap = argparse.ArgumentParser()
ap.add_argument('video', choices=ALLOWED)
a = ap.parse_args()
path = (ROOT / 'Reviewed' / a.video).resolve()
assert path.parent == (ROOT / 'Reviewed').resolve()
rows = list(csv.DictReader((ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='')))
row = next(r for r in rows if r['Video'] == a.video)
assert row['Status'] == 'Reviewed' and row['Location'] == 'Reviewed/' + a.video
mapped = next(r for r in json.loads((ROOT / 'MEDIA_LOCATIONS.json').read_text(encoding='utf-8-sig'))['moved'] if r['filename'] == a.video)
receipt_path = Path(mapped['location_history'][-1]['receipt']).resolve()
assert receipt_path.is_relative_to(ROOT / 'Recording_QA')
move = json.loads(receipt_path.read_text(encoding='utf-8-sig'))
lead = json.loads((receipt_path.parent / 'LEAD_ACCEPTANCE.json').read_text(encoding='utf-8-sig'))
assert move['identity_match'] and move['sha256_before'] == move['sha256_after'] == mapped['sha256']
assert lead.get('accepted') is True
before = storage.metadata(path)
assert before['cloud_placeholder'] and before['in_sync'] and not before['pinned']
assert before['logical_bytes'] == move['bytes'] and path.stat().st_size == move['bytes']
record = {'operation': 'verified in-sync archived file cache release', 'video': a.video,
          'created_at_utc': datetime.now(timezone.utc).isoformat(), 'sha256_from_verified_move': mapped['sha256'],
          'move_receipt': str(receipt_path), 'before': before, 'files_deleted': 0,
          'method': 'CfOpenFileWithOplock EXCLUSIVE|WRITE_ACCESS, CfDehydratePlaceholder NONE',
          'documentation': ['https://learn.microsoft.com/en-us/previous-versions/mt827480(v=vs.85)',
              'https://learn.microsoft.com/en-us/windows/win32/api/cfapi/nf-cfapi-cfopenfilewithoplock']}
cloud = ctypes.WinDLL('CldApi', use_last_error=True)
cloud.CfOpenFileWithOplock.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE)]
cloud.CfOpenFileWithOplock.restype = wintypes.LONG
cloud.CfCloseHandle.argtypes = [wintypes.HANDLE]
cloud.CfCloseHandle.restype = None
cloud.CfDehydratePlaceholder.argtypes = [wintypes.HANDLE, ctypes.c_longlong, ctypes.c_longlong, wintypes.DWORD, wintypes.LPVOID]
cloud.CfDehydratePlaceholder.restype = wintypes.LONG
protected = wintypes.HANDLE()
try:
    result = cloud.CfOpenFileWithOplock(str(path), 0x1 | 0x2, ctypes.byref(protected))
    if result != 0:
        raise RuntimeError(f'Exclusive cloud handle unavailable: 0x{result & 0xffffffff:08X}')
    try:
        # No force flags, sync-state edits, root policy changes or deletion calls.
        result = cloud.CfDehydratePlaceholder(protected, 0, -1, 0, None)
        record['api_hresult'] = f'0x{result & 0xffffffff:08X}'
        if result != 0:
            raise RuntimeError('Cache release refused: ' + record['api_hresult'])
    finally:
        cloud.CfCloseHandle(protected)
except Exception as e:
    record['error'] = str(e)
after = storage.metadata(path)
assert path.is_file() and after['logical_bytes'] == before['logical_bytes']
record['after'] = after
record['bytes_reclaimed'] = before['allocated_bytes'] - after['allocated_bytes']
record['online_only_verified'] = after['online_only']
target = BATCH / ('CACHE_RELEASE.' + a.video + '.json')
target.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
print(json.dumps(record, indent=2), flush=True)
