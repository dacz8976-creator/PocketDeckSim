"""Request a bounded media-header read for an owner-requested cloud recording."""
import argparse
import subprocess
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('video')
args = parser.parse_args()
root = Path(__file__).resolve().parent.parent
if Path(args.video).name != args.video or not args.video.startswith('20260930_'):
    raise SystemExit('Expected an exact September 30 source basename')
source = root / args.video
probe = Path(r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffprobe.exe')
try:
    result = subprocess.run([str(probe), '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', str(source)], capture_output=True, text=True, timeout=45)
    print(args.video + ': ' + (result.stdout.strip() if result.returncode == 0 else 'not readable yet: ' + result.stderr.strip()))
except subprocess.TimeoutExpired:
    print(args.video + ': OneDrive download still pending; bounded header reader stopped')
