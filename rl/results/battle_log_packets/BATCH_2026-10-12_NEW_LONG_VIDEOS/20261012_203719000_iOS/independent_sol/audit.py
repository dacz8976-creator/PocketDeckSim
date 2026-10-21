import json, pathlib, hashlib, subprocess
from PIL import Image, ImageOps, ImageDraw
p=pathlib.Path(__file__).resolve().parent.parent
out=p/'independent_sol'
ledger=json.loads((p/'TURN_LEDGER.json').read_text())
ev=json.loads((p/'TURN_EVIDENCE.json').read_text())
names=['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
hashes={n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in names}
(out/'initial_hashes.json').write_text(json.dumps(hashes,indent=2))
lookup={x['evidence_id']:x for x in ev['frames']}
lines=[]
for t in ledger['turns']:
    lines.append(f"T{t['turn_number']} {t['who_played']} {t['timing']}")
    lines.append('Start hand '+str([x['name'] for x in (t['owner_hand_start']['cards_left_to_right'] or [])])+' count '+str(t['owner_hand_start']['count']))
    lines.append('Draws '+str([(x['kind'],x.get('caused_by'),[(y['name'],y.get('timestamp_seconds')) for y in (x.get('cards_in_reveal_order') or [])]) for x in t['draws_and_searches']]))
    lines.append('Plays '+str([(x['order'],x['card_name'],x['timestamp_seconds'],x['target'],x['result']) for x in t['plays_in_order']]))
    lines.append('End hand '+str(t['owner_hand_end']))
    for k in ('board_at_start','board_after'):
        b=t[k]
        lines.append(k+' '+str({pl:{'active':b[pl]['active'],'bench':b[pl]['bench_in_position_order'],'zone':b[pl]['energy_zone'],'points':b[pl]['points']} for pl in ('owner','opponent')}))
(out/'ledger_compact.txt').write_text('\n'.join(lines),encoding='utf8')
def sheet(times,name):
    canvas=Image.new('RGB',(1560, (len(times)+3)//4*890),'white')
    d=ImageDraw.Draw(canvas)
    for i,t in enumerate(times):
        nearest=min(ev['frames'],key=lambda e:abs(e['requested_source_seconds']-t))
        f=p/nearest['full_frame_path'];t=nearest['requested_source_seconds']
        im=Image.open(f); im.thumbnail((390,845))
        x=(i%4)*390;y=(i//4)*890
        canvas.paste(im,(x,y+25));d.text((x+10,y+5),f'{t:.2f}s',fill='black')
    canvas.save(out/(name+'.jpg'),quality=95)
sheet([28,30,46.65,52,58,62,107.2,109,118,128,132,142,149,150,152,194,198,202,220],'opening_draws')
sheet([254,264,268,270,272,284,290,334,350,356,358,366,374,416,424,454,460,466,468,472,480],'middle')
sheet([534,538,544,550,556,562,574,580,596,630,640,650,660,698,710,720,730,738,744,754,776,782,786,790,800.5],'ending')
ff=pathlib.Path('C:/Program Files/MiniTool Screen Recorder/FFmpeg/ffmpeg.exe')
src=pathlib.Path('20261012_203719000_iOS.MP4').resolve()
for sec in [107.2,468,790]:
    dest=out/f'fresh_{sec:.2f}.jpg'
    r=subprocess.run([str(ff),'-v','error','-threads','1','-ss',str(sec),'-i',str(src),'-frames:v','1','-threads','1','-q:v','2','-y',str(dest)],capture_output=True)
    if r.returncode: raise RuntimeError(r.stderr.decode(errors='replace'))
print('Audit material ready',len(ledger['turns']),len(ev['frames']))
