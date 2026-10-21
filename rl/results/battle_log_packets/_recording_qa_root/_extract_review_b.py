import argparse
from pathlib import Path

import cv2
from PIL import Image, ImageDraw, ImageFont


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('video')
    parser.add_argument('output')
    parser.add_argument('--interval', type=float, default=3.0)
    parser.add_argument('--start', type=float, default=0.0)
    parser.add_argument('--end', type=float, default=None)
    args = parser.parse_args()

    out = Path(args.output)
    frames_dir = out / 'frames'
    frames_dir.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        raise SystemExit('Cannot open video')
    fps = cap.get(cv2.CAP_PROP_FPS)
    count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    duration = count / fps
    end = min(duration - 0.1, args.end if args.end is not None else duration - 0.1)
    timestamps = [round(args.start + i * args.interval, 3) for i in range(int((end - args.start) / args.interval) + 1)]
    if end - timestamps[-1] > 0.25:
        timestamps.append(round(end, 3))
    images = []
    for t in timestamps:
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, frame = cap.read()
        if not ok:
            continue
        path = frames_dir / f'{t:07.2f}.jpg'
        cv2.imwrite(str(path), frame, [cv2.IMWRITE_JPEG_QUALITY, 88])
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        im = Image.fromarray(rgb)
        im.thumbnail((390, 844))
        images.append((t, im.copy()))
    cap.release()
    for page_start in range(0, len(images), 9):
        page = Image.new('RGB', (1170, 9 * 866 // 3), 'white')
        draw = ImageDraw.Draw(page)
        for index, (t, im) in enumerate(images[page_start:page_start + 9]):
            x = index % 3 * 390
            y = index // 3 * 866
            page.paste(im, (x, y + 22))
            draw.text((x + 4, y + 3), f'{t:.1f}s', fill='black')
        page.save(out / f'sheet_{page_start // 9 + 1:02d}.jpg', quality=90)
    print(f'fps={fps:.3f} frames={count:.0f} duration={duration:.3f} seconds; saved={len(images)}')


if __name__ == '__main__':
    main()
