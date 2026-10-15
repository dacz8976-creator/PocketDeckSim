import json
from pathlib import Path
from PIL import Image
P=Path(__file__).parent
def read(n):return json.loads((P/n).read_text(encoding='utf-8'))
def save(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
E=read('TURN_EVIDENCE.json');L=read('TURN_LEDGER.json');index={f['evidence_id']:f for f in E['frames']};prototype=E['frames'][0]
for t in [172,374,376]:
    name=f't{t:07.2f}.jpg';k='f'+f'{t:07.2f}'.replace('.','_')
    with Image.open(P/'turn_evidence'/name) as im:
        for suffix,bounds in [('bottom',(0,2025,1170,2532)),('top',(0,0,1170,700))]:im.crop(bounds).save(P/'turn_evidence'/f'{name[:-4]}_{suffix}.png')
    f={'evidence_id':k,'role':'native_boundary_recheck','turn_number':6 if t==172 else 12,'source_video':prototype['source_video'],'source_sha256':prototype['source_sha256'],
       'requested_source_seconds':t,'actual_frame_seconds_if_measured':None,'full_frame_path':'turn_evidence/'+name,
       'native_dimensions':{'width':1170,'height':2532},'bottom_crop':{'path':f'turn_evidence/{name[:-4]}_bottom.png','pixel_bounds_x0_y0_x1_y1':[0,2025,1170,2532]},
       'top_crop':{'path':f'turn_evidence/{name[:-4]}_top.png','pixel_bounds_x0_y0_x1_y1':[0,0,1170,700]},
       'selected_for_start_hand':False,'before_first_play':True if t==172 else None,'unzoomed':True,
       'observation':'Turn6 normal draw merged, prior Cufant and empty current Metal before generation/evolution' if t==172 else 'Copperajah still has2Metal, large current Metal still unused before attachment by378',
       'suitability_or_limit':'Inspected original-resolution native view; requested seek timestamp, not measured PTS.'}
    E['frames'].append(f);index[k]=f
unzoomed={1:[True,True,True],3:[False,False,False],5:[True,True,False],7:[True,False,False],9:[False,False,False],11:[True,True,True],13:[True,True,True],15:[True,False,False],17:[True,True,False]}
for r in L['turns']:
    if r['turn_number']%2:
        for i,k in enumerate(r['capture_candidates']):index[k]['unzoomed']=unzoomed[r['turn_number']][i]
    if r['turn_number']==6:
        r['owner_hand_start']['evidence_ids']=['f0172_00'];r['turn_evidence_ids']=sorted(set(r['turn_evidence_ids']+['f0172_00']))
        z=r['board_at_start']['opponent']['energy_zone'];z['generation_bounds_seconds']=[172,176];z['generation_evidence_ids']=['f0172_00','f0176_00']
    # Evidence list includes any newly referenced native boundary frames.
    def refs(v):
        result=[]
        if isinstance(v,dict):
            for k,x in v.items():
                if k in ['evidence_ids','generation_evidence_ids'] and isinstance(x,list):result.extend(x)
                else:result.extend(refs(x))
        elif isinstance(v,list):
            for x in v:result.extend(refs(x))
        return result
    r['turn_evidence_ids']=sorted(set(r['turn_evidence_ids']+refs(r)))
E['frames'].sort(key=lambda f:f['requested_source_seconds'])
save('TURN_EVIDENCE.json',E);save('TURN_LEDGER.json',L)
print('Frame manifest and candidate flags reconciled.')
