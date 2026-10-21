import argparse
from pathlib import Path

import cv2
from PIL import Image, ImageDraw


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("video")
    parser.add_argument("output")
    parser.add_argument("--step", type=float, default=12)
    parser.add_argument("--width", type=int, default=300)
    parser.add_argument("--times", nargs="*", type=float)
    args = parser.parse_args()

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    capture = cv2.VideoCapture(args.video)
    fps = capture.get(cv2.CAP_PROP_FPS)
    frames = capture.get(cv2.CAP_PROP_FRAME_COUNT)
    duration = frames / fps
    if args.times is not None:
        for time in args.times:
            capture.set(cv2.CAP_PROP_POS_MSEC, time * 1000)
            ok, frame = capture.read()
            if not ok:
                print(f"failed {time}")
                continue
            path = output / f"t{time:06.1f}.jpg"
            cv2.imwrite(str(path), frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
            print(path)
        capture.release()
        print(f"duration={duration:.3f} frames={frames:.0f} fps={fps:.3f}")
        return
    images = []
    time = 0.0
    while time < duration:
        capture.set(cv2.CAP_PROP_POS_MSEC, time * 1000)
        ok, frame = capture.read()
        if ok:
            height, width = frame.shape[:2]
            scaled = cv2.resize(frame, (args.width, round(height * args.width / width)))
            rgb = cv2.cvtColor(scaled, cv2.COLOR_BGR2RGB)
            im = Image.fromarray(rgb)
            images.append((time, im))
        time += args.step
    capture.release()
    if not images:
        raise RuntimeError("No frames decoded")
    cell_w = images[0][1].width
    cell_h = images[0][1].height + 32
    for page_index in range(0, len(images), 12):
        subset = images[page_index:page_index + 12]
        sheet = Image.new("RGB", (cell_w * 4, cell_h * 3), "white")
        draw = ImageDraw.Draw(sheet)
        for slot, (time, im) in enumerate(subset):
            x = (slot % 4) * cell_w
            y = (slot // 4) * cell_h
            draw.text((x + 4, y + 4), f"{time:.0f}s / {int(time // 60):02d}:{int(time % 60):02d}", fill="black")
            sheet.paste(im, (x, y + 32))
        path = output / f"contact_{page_index // 12 + 1:02d}.jpg"
        sheet.save(path, quality=83)
        print(path)
    print(f"duration={duration:.3f} frames={frames:.0f} fps={fps:.3f} images={len(images)}")


if __name__ == "__main__":
    main()
