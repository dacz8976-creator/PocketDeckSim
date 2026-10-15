import json, pathlib, hashlib, sys
from PIL import Image, ImageDraw
P=pathlib.Path(__file__).resolve().parent.parent
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sheet(times,name,sub='',area=None,w=390,cols=4):
    q=P/sub; ev=read(q/'TURN_EVIDENCE.json')['frames']; em={r['requested_source_seconds']:r for r in ev}
    ims=[]
    for t in times:
        f=em.get(t)
        if not f: print('MISSING',sub,t); continue
        im=Image.open(q/f['full_frame_path']).convert('RGB')
        if area: im=im.crop(area)
        im.thumbnail((w,3000)); ims.append((t,im))
    h=max(im.height for t,im in ims)+25
    out=Image.new('RGB',(cols*w,((len(ims)+cols-1)//cols)*h),'white');d=ImageDraw.Draw(out)
    for i,(t,im) in enumerate(ims):
        x=i%cols*w;y=i//cols*h;out.paste(im,(x,y+25));d.text((x+10,y+5),str(t),fill='black')
    dst=P/'independent_sol'/name;out.save(dst);print(dst)
if sys.argv[1]=='sheet':
    sheet([float(x) for x in sys.argv[2].split(',')],sys.argv[3],sys.argv[4] if len(sys.argv)>4 else '',json.loads(sys.argv[5]) if len(sys.argv)>5 else None,int(sys.argv[6]) if len(sys.argv)>6 else 390)
if sys.argv[1]=='compact':
 for sub in ['', 'game_02']:
    q=P/sub
    print('PACKET',sub)
    for name in ['COVERAGE.md','CORRECTION_LEDGER.json']:
        if (q/name).exists():print(name,(q/name).read_text(encoding='utf-8-sig'))
    l=read(q/'TURN_LEDGER.json')
    for r in l['turns']:
        print('TURN',r['turn_number'],r['who_played'],r['source_interval_seconds'],r['timing'])
        print('HANDS',json.dumps({k:r.get(k) for k in ['hand_at_start','owner_hand_start','owner_hand_end','opponent_hand_at_owner_turn_start']},ensure_ascii=True))
        print('DRAW',json.dumps(r['draws_and_searches'],ensure_ascii=True))
        print('PLAYS',json.dumps([{k:a.get(k) for k in ['order','kind','card_name','timestamp_seconds','target','energy','result','nested_events_in_order','hand_count_after','evidence_ids']} for a in r['plays_in_order']],ensure_ascii=True))
        for bn in ['board_at_start','board_after']:
            b=r[bn];print(bn,json.dumps({k:b.get(k) for k in ['turn_number_displayed','timestamp_seconds','phase','stadium','evidence_ids']},ensure_ascii=True))
            for player in ['owner','opponent']:
                bb=b[player]
                print(player,json.dumps({k:bb.get(k) for k in ['active','bench_in_position_order','energy_zone','points','evidence_ids']},ensure_ascii=True))
