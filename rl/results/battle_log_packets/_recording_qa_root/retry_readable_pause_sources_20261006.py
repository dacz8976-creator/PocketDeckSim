"""Retry the now-local first two sources between serialized intake writes."""
import subprocess
import sys
import time
from pathlib import Path
from intake_pause_batch_20261006 import ROOT, BATCH, intake

deadline=time.monotonic()+600
for name in ['20261004_213625000_iOS.MP4','20261004_214518000_iOS.MP4']:
    while (ROOT/'Review_Log/.write.lock').exists() and time.monotonic()<deadline:
        time.sleep(0.2)
    if (ROOT/'Review_Log/.write.lock').exists():
        print(name+': serialization wait pending',flush=True)
        break
    intake(name)
