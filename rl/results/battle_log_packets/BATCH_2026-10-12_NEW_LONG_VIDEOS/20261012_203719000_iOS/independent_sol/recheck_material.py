import pathlib,json,hashlib,subprocess
from PIL import Image,ImageDraw
p=pathlib.Path(__file__).resolve().parent.parent
out=p/'independent_sol'
old=p/'before_independent_repairs_20261012T233338Z'
names=['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
hashes={n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in names}
assert hashes==json.loads((p/'REVIEW_PACKET_HASHES.json').read_text())['review_files_sha256']
(out/'recheck_initial_hashes.json').write_text(json.dumps(hashes,indent=2))
le=json.loads((p/'TURN_LEDGER.json').read_text());ev=json.loads((p/'TURN_EVIDENCE.json').read_text())
look={x['evidence_id']:x for x in ev['frames']}
lines=[]
def diff(a,b,path=''):
    if type(a)!=type(b):return [f'{path}: {a!r} -> {b!r}']
    if isinstance(a,dict):return sum((diff(a.get(k),b.get(k),path+'/'+k) for k in (a.keys()|b.keys())),[])
    if isinstance(a,list):
        if len(a)!=len(b):return [f'{path}: list length {len(a)} -> {len(b)}']
        return sum((diff(x,y,path+'/'+str(i)) for i,(x,y) in enumerate(zip(a,b))),[])
    return [] if a==b else [f'{path}: {a!r} -> {b!r}']
for n in names:
    if n.endswith('.json'):
        a=json.loads((old/n).read_text());b=json.loads((p/n).read_text())
        lines+=['FILE '+n]+diff(a,b)
(out/'recheck_diff.txt').write_text('\n'.join(lines),encoding='utf8')
zones=[]
for t in le['turns']:
    for key in ['board_at_start','board_after']:
        b=t[key]
        for player in ['owner','opponent']:
            zone=b[player]['energy_zone'];e=look[zone['evidence_ids'][0]]
            zones.append({'turn':t['turn_number'],'phase':key,'player':player,'time':e['requested_source_seconds'],'frame':e['full_frame_path'],'zone':zone})
(out/'recheck_zones.json').write_text(json.dumps(zones,indent=2),encoding='utf8')
for st in range(0,len(zones),28):
    group=zones[st:st+28];canvas=Image.new('RGB',(1600,7*340),'white');d=ImageDraw.Draw(canvas)
    for i,z in enumerate(group):
        im=Image.open(p/z['frame']);crop=im.crop((940,1950,1170,2310) if z['player']=='owner' else (0,290,280,480));crop.thumbnail((350,260))
        x=i%4*400;y=i//4*340
        canvas.paste(crop,(x,y+45));d.text((x+5,y+2),f"T{z['turn']} {z['phase']} {z['player']} {z['time']}s",fill='black')
        d.text((x+5,y+18),str(z['zone']['this_turn'])+'\n'+str(z['zone']['next']),fill='black')
    canvas.save(out/f'recheck_zones{st//28}.jpg',quality=97)
ff='C:/Program Files/MiniTool Screen Recorder/FFmpeg/ffmpeg.exe'
for t in [107.5,466.9]:
    subprocess.run([ff,'-v','error','-threads','1','-ss',str(t),'-i','20261012_203719000_iOS.MP4','-frames:v','1','-threads','1','-q:v','2','-y',str(out/f'recheck_fresh_{t:.2f}.jpg')],check=True)
print('Hashes match; repair diffs',len(lines),'zone observations',len(zones))
for t in le['turns']:
    if t['turn_number'] in [3,13,17,19,21]:
        print(t['turn_number'],t['timing'],t['hand_at_start'],t['plays_in_order'][0],t['board_at_start']['owner']['energy_zone'])
