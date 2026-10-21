"""Single bounded retry for each exact owner-requested evening source."""
import argparse, json, os, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path
from free_reviewed_video_space import metadata
ROOT=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser()
p.add_argument('videos',nargs='+',choices=['20261014_214436000_iOS.MP4','20261014_215114000_iOS.MP4','20261014_225451000_iOS.MP4','20261014_225802000_iOS.MP4','20261014_230328000_iOS.MP4','20261014_231006000_iOS.MP4','20261014_232438000_iOS.MP4','20261014_233402000_iOS.MP4','20261014_234511000_iOS.MP4','20261014_234728000_iOS.MP4','20261015_015320000_iOS.MP4','20261015_020931000_iOS.MP4','20261015_021533000_iOS.MP4','20261015_022206000_iOS.MP4'])
p.add_argument('--batch',choices=['BATCH_2026-10-14_EVENING_LADDER','BATCH_2026-10-14_LATE_LADDER_TWO','BATCH_2026-10-14_NEWER_LADDER_FOUR','BATCH_2026-10-14_NIGHT_LADDER_FOUR'],default='BATCH_2026-10-14_EVENING_LADDER')
p.add_argument('--refresh-pin',action='store_true',help='Refresh the local-availability preference for selected unreviewed root sources')
a=p.parse_args()
BATCH=ROOT/'Recording_QA'/a.batch
if a.batch=='BATCH_2026-10-14_NIGHT_LADDER_FOUR':
    assert set(a.videos).issubset(json.loads((BATCH/'OWNER_CONTEXT.json').read_text(encoding='utf-8'))['selected_sources'])
for name in a.videos:
    source=ROOT/name
    packet=BATCH/source.stem
    code='import sys;from pathlib import Path;sys.path.insert(0,sys.argv[1]);from hydrate_competitive_source import hydrate;hydrate(Path(sys.argv[2]));print("S_OK",flush=True)'
    result={'source':name,'utc':datetime.now(timezone.utc).isoformat(),'before':metadata(source),'contents_modified':False}
    if a.refresh_pin:
        assert source.resolve().parent==ROOT.resolve() and not (ROOT/'Reviewed'/name).exists()
        attrib=str(Path(os.environ['SystemRoot'])/'System32/attrib.exe')
        changes=[]
        for flags in [('-P','-U'),('+P','-U')]:
            preference=subprocess.run([attrib,*flags,str(source)],capture_output=True,text=True,timeout=10)
            assert preference.returncode==0,preference.stderr
            changes.append({'flags':list(flags),'exit_code':preference.returncode})
            time.sleep(1)
        result['local_availability_preference_refreshed']=changes
    try:
        r=subprocess.run([sys.executable,'-c',code,str(ROOT/'Recording_QA'),str(source)],capture_output=True,text=True,timeout=35)
        result.update(exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr)
    except subprocess.TimeoutExpired:
        result['result']='Cloud Files hydration timed out after 35 seconds; child stopped'
    result['after']=metadata(source)
    (packet/'HYDRATION_RETRY.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result),flush=True)
