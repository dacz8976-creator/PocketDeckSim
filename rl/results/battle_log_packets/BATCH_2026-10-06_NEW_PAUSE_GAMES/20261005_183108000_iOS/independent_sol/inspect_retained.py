from pathlib import Path
import json, hashlib, sys
from PIL import Image, ImageDraw
P=Path(__file__).resolve().parent.parent
O=P/'independent_sol'
def read(n): return json.loads((P/n).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
E=read('TURN_EVIDENCE.json'); L=read('TURN_LEDGER.json'); F={f['requested_source_seconds']: f for f in E['frames']}
if sys.argv[1]=='freeze':
 names=['SOURCE.json','REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
 (O/'FROZEN_INPUT_SHA256.json').write_text(json.dumps({n:sha(P/n) for n in names},indent=2)+'\n',encoding='utf-8')
 for t in L['turns']:
  print('TURN',t['turn_number'],'endhand',t.get('owner_hand_end'))
  for k in ['board_at_start','board_after']:
   b=t[k]; print(k,'time',b['timestamp_seconds'],'display',b.get('turn_number_displayed'),'stadium',b.get('stadium'), 'phase',b.get('phase'))
   for side in ['owner','opponent']:
    s=b[side]; print(side,'points',s.get('points'),'zone',s.get('energy_zone'))
    for mon in [s['active']]+s['bench_in_position_order']:
     print({a:mon.get(a) for a in ['name','status','hp_now','hp_max','damage','attached_energy','tool','special_conditions','active_effects','evidence_ids']})
 print('SPECIAL FRAMES')
 for f in E['frames']:
  if f['role']!='supporting_native_frame': print({k:f.get(k) for k in ['evidence_id','role','requested_source_seconds','turn_number','draw_animation_end_seconds','offset_after_draw_seconds','selected_for_start_hand','before_first_play','unzoomed','hand_spread','suitability_or_limit']})
elif sys.argv[1]=='sheet':
 mode=sys.argv[2]; times=[float(x) for x in sys.argv[3].split(',')]; panels=[]
 for tm in times:
  f=F[tm]; path=P/f['full_frame_path']
  im=Image.open(path).convert('RGB')
  if mode in ['top','bottom']: im=Image.open(P/f[mode+'_crop']['path']).convert('RGB')
  elif mode=='board': im=im.crop((0,650,1170,2025))
  elif mode=='locator': im=im.resize((468,1013))
  panel=Image.new('RGB',(im.width,im.height+34),'white');panel.paste(im,(0,34));ImageDraw.Draw(panel).text((8,8),f'{tm:g}s {mode}',fill='black');panels.append(panel)
 cols=min(2,len(panels)); w=panels[0].width;h=max(im.height for im in panels);sheet=Image.new('RGB',(cols*w,((len(panels)+cols-1)//cols)*h),'#777777')
 for i,im in enumerate(panels):sheet.paste(im,((i%cols)*w,(i//cols)*h))
 out=O/(mode+'_'+sys.argv[3].replace(',','_')+'.png');sheet.save(out);print(out)
elif sys.argv[1]=='draws':
 for t in L['turns']:
  print(t['turn_number'],json.dumps(t['draws_and_searches'],ensure_ascii=False))
