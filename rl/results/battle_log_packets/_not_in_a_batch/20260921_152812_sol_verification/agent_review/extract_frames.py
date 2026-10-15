import sys
from pathlib import Path
sys.path.insert(0, r'C:\Users\dacz8\AppData\Local\CodexTranscription\faster-whisper')
import av
from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parent
VIDEO = BASE.parents[2] / '20260921_152812000_iOS.MP4'
out = BASE / 'frames'
out.mkdir(exist_ok=True)
times = [float(x) for x in sys.argv[1].split(',')]
container = av.open(str(VIDEO))
stream = container.streams.video[0]
print({'duration': container.duration / av.time_base, 'codec': stream.codec_context.name, 'width': stream.width, 'height': stream.height, 'rate': str(stream.average_rate), 'frames': stream.frames})
thumbs=[]
for t in times:
    container.seek(int(t / stream.time_base), stream=stream, backward=True)
    for frame in container.decode(stream):
        if float(frame.time) >= t:
            im=frame.to_image()
            dest=out / f'{t:07.3f}.jpg'
            im.save(dest, quality=92)
            im.thumbnail((300,650))
            thumb=Image.new('RGB',(300,680),'white')
            thumb.paste(im,(0,30))
            ImageDraw.Draw(thumb).text((6,6),f'{int(t//60):02}:{t%60:06.3f}',fill='black')
            thumbs.append(thumb)
            break
for start in range(0,len(thumbs),8):
    batch=thumbs[start:start+8]
    montage=Image.new('RGB',(300*len(batch),680),'white')
    for i,im in enumerate(batch): montage.paste(im,(i*300,0))
    dest=BASE/f'sheet_{times[start]:07.3f}.jpg'
    montage.save(dest,quality=92)
    print(dest)
