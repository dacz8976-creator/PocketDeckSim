"""Release only the four verified, in-sync original video caches."""
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / 'Recording_QA/BATCH_2026-10-14_OFFLINE_LADDER_FOUR'
sys.path.insert(0, str(ROOT / 'Recording_QA'))
import free_reviewed_video_space as storage


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


cloud = ctypes.WinDLL('CldApi', use_last_error=True)
cloud.CfOpenFileWithOplock.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE)]
cloud.CfOpenFileWithOplock.restype = wintypes.LONG
cloud.CfCloseHandle.argtypes = [wintypes.HANDLE]
cloud.CfCloseHandle.restype = None
cloud.CfDehydratePlaceholder.argtypes = [wintypes.HANDLE, ctypes.c_longlong, ctypes.c_longlong,
                                        wintypes.DWORD, wintypes.LPVOID]
cloud.CfDehydratePlaceholder.restype = wintypes.LONG
records = []
for source in load(BATCH / 'SOURCE_INVENTORY.json'):
    name = source['video_basename']
    packet = Path(source['packet']).resolve()
    assert packet.is_relative_to(BATCH.resolve())
    path = (ROOT / 'Reviewed' / name).resolve()
    assert path.parent == (ROOT / 'Reviewed').resolve()
    move = load(packet / 'SYNC_RECOVERY_MOVE_RECEIPT.json')
    assert move['identity_match'] and move['sha256_after'] == source['sha256']
    before = storage.metadata(path)
    assert before['cloud_placeholder'] and before['in_sync'] and not before['pinned']
    assert before['logical_bytes'] == source['bytes']
    record = {'filename': name, 'path': str(path), 'source_sha256': source['sha256'],
         'before': before, 'files_deleted': 0, 'video_contents_read': False,
         'method': 'CfOpenFileWithOplock EXCLUSIVE|WRITE_ACCESS; CfDehydratePlaceholder NONE'}
    if not before['online_only']:
        protected = wintypes.HANDLE()
        result = cloud.CfOpenFileWithOplock(str(path), 0x1 | 0x2, ctypes.byref(protected))
        record['open_hresult'] = f'0x{result & 0xffffffff:08X}'
        if result == 0:
            try:
                result = cloud.CfDehydratePlaceholder(protected, 0, -1, 0, None)
                record['dehydrate_hresult'] = f'0x{result & 0xffffffff:08X}'
            finally:
                cloud.CfCloseHandle(protected)
    after = storage.metadata(path)
    assert path.is_file() and after['logical_bytes'] == before['logical_bytes']
    record['after'] = after
    record['online_only_verified'] = after['online_only'] and after['in_sync']
    record['local_bytes_reclaimed'] = before['allocated_bytes'] - after['allocated_bytes']
    records.append(record)
result = {'checked_utc': datetime.now(timezone.utc).isoformat(), 'records': records,
     'all_four_in_sync_online_only': all(r['online_only_verified'] for r in records),
     'local_bytes_reclaimed': sum(r['local_bytes_reclaimed'] for r in records),
     'files_deleted': 0, 'video_contents_read': False}
(BATCH / 'SYNC_RECOVERY_CACHE_RELEASE.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, indent=2), flush=True)
