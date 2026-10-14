"""Ensure one explicitly selected review source is locally readable via Windows Cloud Files."""
import argparse
import ctypes
import json
from ctypes import wintypes
from pathlib import Path
from intake_competitive_20261002 import ROOT,VIDEOS

def hydrate(path):
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    cloud=ctypes.WinDLL('CldApi',use_last_error=True)
    kernel.CreateFileW.argtypes=[wintypes.LPCWSTR,wintypes.DWORD,wintypes.DWORD,wintypes.LPVOID,wintypes.DWORD,wintypes.DWORD,wintypes.HANDLE]
    kernel.CreateFileW.restype=wintypes.HANDLE
    kernel.CloseHandle.argtypes=[wintypes.HANDLE]
    kernel.CloseHandle.restype=wintypes.BOOL
    cloud.CfHydratePlaceholder.argtypes=[wintypes.HANDLE,ctypes.c_longlong,ctypes.c_longlong,wintypes.DWORD,wintypes.LPVOID]
    cloud.CfHydratePlaceholder.restype=wintypes.LONG
    handle=kernel.CreateFileW(str(path),1,7,None,3,0,None)
    if handle==ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        result=cloud.CfHydratePlaceholder(handle,0,-1,0,None)
        if result != 0:
            raise RuntimeError(f'Cloud hydration did not succeed: HRESULT 0x{result & 0xffffffff:08X}')
    finally:
        kernel.CloseHandle(handle)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('video',choices=VIDEOS)
    args=parser.parse_args()
    path=(ROOT/args.video).resolve()
    assert path.parent==ROOT.resolve() and path.is_file()
    print('Ensuring local bytes: '+args.video,flush=True)
    hydrate(path)
    print(json.dumps({'video':args.video,'hydration_result':'S_OK','source_contents_modified':False}),flush=True)

if __name__=='__main__':main()
