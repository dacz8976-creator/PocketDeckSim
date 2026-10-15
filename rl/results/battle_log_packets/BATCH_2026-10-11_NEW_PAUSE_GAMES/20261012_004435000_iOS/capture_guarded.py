from pathlib import Path
import argparse,subprocess,shutil
p=Path(__file__).parent
a=argparse.ArgumentParser();a.add_argument('--kind',choices=['native','overview'],default='native');a.add_argument('--times',nargs='+',type=float,required=True);args=a.parse_args()
out=p/('turn_evidence' if args.kind=='native' else 'overview_seek');out.mkdir(exist_ok=True)
ff=r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffmpeg.exe';added=0
for t in args.times:
 if shutil.disk_usage(p).free<100*1024*1024 or added>9*1024*1024:
  print('STOP_GATE',added,shutil.disk_usage(p).free,t);break
 f=out/(f't{t:07.2f}.jpg' if args.kind=='native' else f't{t:03.0f}.jpg')
 if f.exists() and f.stat().st_size>0: continue
 cmd=[ff,'-hide_banner','-loglevel','error','-threads','1','-ss',str(t),'-i',str(p.parents[2]/'20261012_004435000_iOS.MP4'),'-frames:v','1']
 if args.kind=='overview':cmd+=['-vf','scale=390:-1']
 subprocess.run(cmd+['-q:v','4' if args.kind=='native' else '3','-y',str(f)],check=True)
 added+=f.stat().st_size
print('ADDED_BYTES',added,'FREE_BYTES',shutil.disk_usage(p).free)
