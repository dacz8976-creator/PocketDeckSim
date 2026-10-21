"""Request the authorized OneDrive file through the Windows cloud-file API."""
import ctypes
import importlib.util
import json
import time
from ctypes import wintypes
from datetime import datetime, timezone
from pathlib import Path

BATCH = Path(__file__).resolve().parent
ROOT = BATCH.parents[1]
P = BATCH / "20260909_023151000"
source = ROOT / "Reviewed" / "20260909_023151000_iOS.MP4"
receipt_path = P / "WINDOWS_DELIVERY_REQUEST.json"
assert not receipt_path.exists(), "Do not repeat this delivery request automatically."
assert source.resolve().is_relative_to((ROOT / "Reviewed").resolve())
spec = importlib.util.spec_from_file_location("cloud_metadata", ROOT / "Recording_QA" / "free_reviewed_video_space.py")
metadata_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metadata_module)
before = metadata_module.metadata(source)
assert before["cloud_placeholder"] and before["in_sync"]
kernel = ctypes.WinDLL("kernel32", use_last_error=True)
cloud = ctypes.WinDLL("cldapi", use_last_error=True)
kernel.CreateFileW.argtypes = [wintypes.LPCWSTR,wintypes.DWORD,wintypes.DWORD,wintypes.LPVOID,wintypes.DWORD,wintypes.DWORD,wintypes.HANDLE]
kernel.CreateFileW.restype = wintypes.HANDLE
kernel.CloseHandle.argtypes = [wintypes.HANDLE]
kernel.CloseHandle.restype = wintypes.BOOL
cloud.CfHydratePlaceholder.argtypes = [wintypes.HANDLE,ctypes.c_longlong,ctypes.c_longlong,wintypes.DWORD,wintypes.LPVOID]
cloud.CfHydratePlaceholder.restype = wintypes.LONG
data = {
    "source":source.name,"current_path":str(source),"started_utc":datetime.now(timezone.utc).isoformat(),
    "status":"windows_delivery_request_in_progress","before":before,
    "documentation":"https://learn.microsoft.com/en-us/windows/win32/api/cfapi/nf-cfapi-cfhydrateplaceholder",
    "operation":"CfHydratePlaceholder for source bytes0 through EOF; no change to file contents, no hash reread",
    "python_movie_content_reads":0,"completed_failed_content_reads_before_request":2,
}
receipt_path.write_text(json.dumps(data,indent=2),encoding="utf-8")
start=time.monotonic()
# Attribute handle opens the placeholder itself, without a data read.
handle=kernel.CreateFileW(str(source),0x80,0x1|0x2|0x4,None,3,0x00200000,None)
if handle == ctypes.c_void_p(-1).value:
    data.update(status="native_handle_error",win_error=ctypes.get_last_error())
else:
    try:
        result=cloud.CfHydratePlaceholder(handle,0,-1,0,None)
        unsigned=result & 0xffffffff
        data.update(status="windows_delivery_completed" if result==0 else "windows_delivery_error",hresult=f"0x{unsigned:08X}")
        if (unsigned & 0xffff0000)==0x80070000:
            code=unsigned & 0xffff
            data.update(win_error=code,windows_error_text=ctypes.FormatError(code))
    finally:
        kernel.CloseHandle(handle)
data.update(finished_utc=datetime.now(timezone.utc).isoformat(),wall_seconds=round(time.monotonic()-start,2),after=metadata_module.metadata(source))
receipt_path.write_text(json.dumps(data,indent=2),encoding="utf-8")
print(json.dumps(data))
if data["status"]!="windows_delivery_completed":
    raise SystemExit(1)
