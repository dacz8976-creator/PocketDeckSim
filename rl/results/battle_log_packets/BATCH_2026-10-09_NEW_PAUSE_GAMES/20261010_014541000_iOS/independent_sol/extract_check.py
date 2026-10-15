from pathlib import Path
import subprocess
p=Path(__file__).parent
source=p.parents[3]/'20261010_014541000_iOS.MP4'
ff=r'C:/Program Files/MiniTool Screen Recorder/FFmpeg/ffmpeg.exe'
for t in [264,293,469,470,471,490,491,492]:
    subprocess.run([ff,'-hide_banner','-loglevel','error','-threads','2','-ss',str(t),'-i',str(source),'-frames:v','1','-q:v','2','-y',str(p/f't{t:07.2f}.jpg')],check=True)
    print(t,flush=True)
