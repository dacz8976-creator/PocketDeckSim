import json, hashlib
from pathlib import Path
from PIL import Image, ImageChops

P = Path(__file__).resolve().parent.parent
O = P / 'independent_sol'
SHA = '80615dfc9c1e28f95434e3b4712f0540e6efc34392aef816419b6f82a0257329'
FILES = ['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
def read(n): return json.loads((P/n).read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()
E=read('TURN_EVIDENCE.json'); L=read('TURN_LEDGER.json'); D=read('DECK_USED.json')
issues=[]; refs=[]; frames={f['evidence_id']:f for f in E['frames']}
def walk(x,path=''):
    if isinstance(x,dict):
        for k,v in x.items():
            if k=='evidence_ids':
                for r in v:
                    if r not in frames: issues.append('missing ref '+path+' '+r)
            if k in ('source_sha256','sha256') and v!=SHA:issues.append('SHA mismatch '+path)
            if k in ('source_video','video_basename') and v!='20261010_013009000_iOS.MP4':issues.append('source mismatch '+path)
            walk(v,path+'/'+k)
    elif isinstance(x,list):
        for i,v in enumerate(x):walk(v,path+'/'+str(i))
for n in FILES:
    if n.endswith('.json'):walk(read(n),n)
for f in E['frames']:
    p=P/f['full_frame_path']
    if not p.exists(): issues.append('missing frame '+f['evidence_id']);continue
    if sha(p)!=f.get('retained_full_frame_sha256'): issues.append('frame hash '+f['evidence_id'])
    im=Image.open(p).convert('RGB')
    if im.size!=(1170,2532):issues.append('non native '+f['evidence_id'])
    for k in ('bottom_crop','top_crop'):
        crop=f[k]; cp=P/crop['path']; bounds=crop['pixel_bounds_x0_y0_x1_y1']
        if not cp.exists():issues.append('missing crop '+f['evidence_id']+' '+k);continue
        ci=Image.open(cp).convert('RGB')
        expected=im.crop(bounds)
        if ci.size!=expected.size or ImageChops.difference(ci,expected).getbbox():issues.append('crop pixels '+f['evidence_id']+' '+k)
    if f['bottom_crop']['pixel_bounds_x0_y0_x1_y1']!=[0,2025,1170,2532]:issues.append('bottom bounds '+f['evidence_id'])
    if not 0<=f['requested_source_seconds']<=565.725:issues.append('timestamp '+f['evidence_id'])
if [t['turn_number'] for t in L['turns']]!=list(range(1,17)):issues.append('turn count/order')
turn_summaries=[]
for t in L['turns']:
    if [a['order'] for a in t['plays_in_order']]!=list(range(1,len(t['plays_in_order'])+1)):issues.append('action order '+str(t['turn_number']))
    for b in ('board_at_start','board_after'):
        for side in ('owner','opponent'):
            bd=t[b][side]
            for pk in [bd['active']]+bd['bench_in_position_order']:
                if pk is None:continue
                if pk['attached_energy']['total']!=sum(pk['attached_energy']['by_type'].values()):issues.append('energy sum '+str(t['turn_number']))
                if pk['hp_now'] is not None and pk['hp_max'] is not None and pk['damage']!=pk['hp_max']-pk['hp_now']:issues.append('HP sum '+str(t['turn_number']))
    turn_summaries.append({'turn':t['turn_number'],'who':t['who_played'],'start':t['hand_at_start']['count'],'end':t.get('owner_hand_end',{}).get('count'),'normal_draw':[x['cards_in_reveal_order'] for x in t['draws_and_searches'] if x['kind']=='normal_draw'],'first_move':t['plays_in_order'][0] if t['plays_in_order'] else None})
if len(D['cards_in_log_order'])!=20:issues.append('deck slots')
counts=D['counts_by_name_and_variant']
count_sum=sum(x['count'] for x in counts) if isinstance(counts,list) else sum(counts.values())
if count_sum!=20:issues.append('deck quantities')
source=P.parents[2]/'20261010_013009000_iOS.MP4'
source_hash=sha(source)
if source_hash!=SHA:issues.append('current source SHA')
out={'issues':issues,'frame_count':len(frames),'turn_count':len(L['turns']),'deck_slots':len(D['cards_in_log_order']),'deck_count_sum':count_sum,'source_path':str(source),'source_bytes':source.stat().st_size,'source_sha256_verified':source_hash,'input_hashes':{n:sha(P/n) for n in FILES},'turn_summaries':turn_summaries}
(O/'STRUCTURAL_CHECK.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k not in ['turn_summaries','input_hashes']},ensure_ascii=False,indent=2))
