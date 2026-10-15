"""Source-bound intake for the owner's new competitive-video request."""
import argparse
import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / 'Recording_QA' / 'BATCH_2026-10-02_COMPETITIVE'
VIDEOS = ['20261002_011527000_iOS.MP4', '20261002_012229000_iOS.MP4', '20261002_020315000_iOS.MP4', '20261002_020920000_iOS.MP4', '20261002_021402000_iOS.MP4', '20261002_023418000_iOS.MP4', '20261002_022135000_iOS.MP4']
PROBE = r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffprobe.exe'
FFMPEG = r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffmpeg.exe'
DESTINATION = 'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd'

def save(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def packet_for(name):
    return ROOT / 'Recording_QA' / (Path(name).stem + '_competitive_sol')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--video', choices=VIDEOS)
    args = parser.parse_args()
    BATCH.mkdir(exist_ok=True)
    baseline = BATCH / 'INDEX_BEFORE.json'
    if not baseline.exists():
        save(baseline, list(csv.DictReader((ROOT/'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline=''))))
    for name in ([args.video] if args.video else VIDEOS):
        video = ROOT / name
        packet = packet_for(name)
        packet.mkdir(exist_ok=True)
        binding = packet / 'SOURCE.json'
        if not binding.exists():
            before = video.stat()
            print('Binding ' + name, flush=True)
            digest = hashlib.sha256()
            with video.open('rb') as handle:
                while chunk := handle.read(8*1024*1024):
                    digest.update(chunk)
            probe = json.loads(subprocess.check_output([PROBE,'-v','error','-show_entries','format=duration:stream=width,height,codec_name','-of','json',str(video)], timeout=300))
            after = video.stat()
            assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns), 'Upload changed during intake'
            save(binding, {'video_basename':name,'sha256':digest.hexdigest(),'bytes':before.st_size,'duration_seconds':float(probe['format']['duration']),'streams':probe['streams'],'source_path_at_review':str(video),'recording_relationships':[],'owner_testimony':'I am uploading five new ones. These were competitive battles to be logged here.','requested_log':DESTINATION,'scope_confirmation':'Pending identification of the five competitive recordings among six new root files','recording_date_basis':'Filename 20261002; local synced modification date 2026-10-01; exact filename clock basis unverified','intake_utc':datetime.now(timezone.utc).isoformat()})
        source = read(binding)
        evidence = packet / 'intake'
        evidence.mkdir(exist_ok=True)
        times = [0, min(35,source['duration_seconds']/3), max(0,source['duration_seconds']-3)]
        images=[]
        for t in times:
            path=evidence/f't{t:07.2f}.jpg'
            if not path.exists():
                subprocess.run([FFMPEG,'-hide_banner','-loglevel','error','-threads','2','-ss',str(t),'-i',str(video),'-frames:v','1','-vf','scale=390:-1','-q:v','3','-y',str(path)],check=True,timeout=90)
            images.append(path)
        with Image.open(images[0]) as im:
            height=im.height
        sheet=Image.new('RGB',(1170,height+30),'white')
        draw=ImageDraw.Draw(sheet)
        for i,path in enumerate(images):
            draw.text((i*390+4,5),f'{times[i]:.2f}s',fill='black')
            with Image.open(path) as im: sheet.paste(im,(i*390,30))
        sheet.save(packet/'INTAKE_CONTACT.jpg',quality=88)
        print(json.dumps({'video':name,'bytes':source['bytes'],'sha256':source['sha256'],'duration':source['duration_seconds'],'contact':str(packet/'INTAKE_CONTACT.jpg')}),flush=True)

if __name__=='__main__':
    main()
