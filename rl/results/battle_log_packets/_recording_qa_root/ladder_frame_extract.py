"""Bounded ffmpeg extraction for this batch; sheets supplement native evidence."""
import argparse
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw

FFMPEG = 'C:/Program Files/MiniTool Screen Recorder/FFmpeg/ffmpeg.exe'
p = argparse.ArgumentParser()
p.add_argument('video')
p.add_argument('output')
p.add_argument('--times', nargs='+', type=float)
p.add_argument('--step', type=float, default=15)
p.add_argument('--width', type=int, default=320)
a = p.parse_args()
out = Path(a.output)
out.mkdir(parents=True, exist_ok=True)
if a.times:
    for t in a.times:
        dest = out / f't{t:07.2f}.jpg'
        if not dest.exists():
            subprocess.run([FFMPEG, '-hide_banner', '-loglevel', 'error', '-threads', '1', '-ss', str(t), '-i', a.video,
                '-an', '-frames:v', '1', '-q:v', '2', '-threads', '1', str(dest)], check=True)
        print(str(dest), flush=True)
else:
    assert a.step > 0 and a.width >= 200
    import json
    import math
    probe='C:/Program Files/MiniTool Screen Recorder/FFmpeg/ffprobe.exe'
    duration=float(json.loads(subprocess.run([probe,'-v','error','-show_entries','format=duration','-of','json',a.video],capture_output=True,text=True,check=True).stdout)['format']['duration'])
    for i in range(math.ceil(duration/a.step)):
        t=min((i+0.5)*a.step,max(0,duration-0.15))
        dest=out/f'overview_{i+1:04d}.jpg'
        if not dest.exists():
            subprocess.run([FFMPEG,'-hide_banner','-loglevel','error','-threads','1','-ss',str(t),'-i',a.video,
                '-an','-frames:v','1','-vf',f'scale={a.width}:-1','-q:v','3','-threads','1',str(dest)],check=True)
    files = sorted(out.glob('overview_*.jpg'))
    for start in range(0, len(files), 12):
        subset = files[start:start+12]
        with Image.open(subset[0]) as im:
            w, h = im.size
        sheet = Image.new('RGB', (w*4, (h+28)*3), 'white')
        draw = ImageDraw.Draw(sheet)
        for j, f in enumerate(subset):
            approx = min((start+j+0.5)*a.step,max(0,duration-0.15))
            x, y = j%4*w, j//4*(h+28)
            draw.text((x+4,y+4), f'Approx {approx:.1f}s', fill='black')
            with Image.open(f) as im:
                sheet.paste(im,(x,y+28))
        dest=out/f'contact_{start//12+1:02d}.jpg'
        sheet.save(dest,quality=88)
        print(str(dest),flush=True)
