"""Bounded local frame extraction for the September 30 review batch."""
import argparse
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw

p = argparse.ArgumentParser()
p.add_argument('video')
p.add_argument('output')
p.add_argument('--step', type=float, default=3)
p.add_argument('--start', type=float, default=0)
p.add_argument('--end', type=float)
p.add_argument('--width', type=int, default=390)
p.add_argument('--decode-threads', type=int, default=4)
p.add_argument('--times', nargs='+', type=float)
a = p.parse_args()
ffmpeg = r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffmpeg.exe'
out = Path(a.output).resolve()
out.mkdir(parents=True, exist_ok=True)
if a.times:
    for t in a.times:
        target = out / f't{t:07.2f}.jpg'
        subprocess.run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-threads', str(a.decode_threads), '-ss', str(t), '-i', a.video, '-frames:v', '1', '-q:v', '2', '-y', str(target)], check=True)
        print(target)
else:
    frames = out / 'sample_frames'
    frames.mkdir(exist_ok=True)
    command = [ffmpeg, '-hide_banner', '-loglevel', 'error', '-threads', str(a.decode_threads), '-ss', str(a.start), '-i', a.video]
    if a.end is not None:
        command += ['-t', str(a.end - a.start)]
    command += ['-vf', f'fps=1/{a.step},scale={a.width}:-1', '-q:v', '3', '-y', str(frames / '%05d.jpg')]
    subprocess.run(command, check=True)
    paths = sorted(frames.glob('*.jpg'))
    for start in range(0, len(paths), 9):
        with Image.open(paths[start]) as first:
            h = first.height
        sheet = Image.new('RGB', (a.width * 3, (h + 26) * 3), 'white')
        draw = ImageDraw.Draw(sheet)
        for slot, path in enumerate(paths[start:start + 9]):
            x = (slot % 3) * a.width
            y = (slot // 3) * (h + 26)
            t = a.start + (start + slot + 0.5) * a.step
            draw.text((x + 4, y + 5), f'{t:.2f}s', fill='black')
            with Image.open(path) as im:
                sheet.paste(im, (x, y + 26))
        target = out / f'sheet_{start // 9 + 1:02d}.jpg'
        sheet.save(target, quality=88)
        print(target)
    print(f'Sampled {len(paths)} frames at step={a.step}; labels use fps midpoint sampling.')
