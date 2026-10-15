"""Apply the four bounded independent corrections, preserving the submission."""
from pathlib import Path
import copy, json, shutil, hashlib
from PIL import Image

B=Path(__file__).resolve().parent
P=B/'20261005_003547000_iOS'
backup=P/'submitted_before_independent_corrections'
backup.mkdir(exist_ok=True)
files=['TURN_LEDGER.json','TURN_EVIDENCE.json','DECK_USED.json','REVIEW.md']
for name in files:
    if not (backup/name).exists(): shutil.copy2(P/name,backup/name)
def read(name): return json.loads((P/name).read_text(encoding='utf-8'))
def save(name,value): (P/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ledger=read('TURN_LEDGER.json'); evidence=read('TURN_EVIDENCE.json')
frames={f['evidence_id']:f for f in evidence['frames']}
def add_frame(t,origin,role,observation):
    eid=f'f{t:07.2f}'; out=P/'turn_evidence'/f't{t:07.2f}.jpg'
    shutil.copy2(P/origin,out)
    im=Image.open(out)
    stem=out.stem
    im.crop((0,2025,1170,2532)).save(out.with_name(stem+'_bottom.png'))
    im.crop((0,0,1170,700)).save(out.with_name(stem+'_top.png'))
    f=copy.deepcopy(frames['f0068.00']); f.update(evidence_id=eid,role=role,roles=[role],requested_source_seconds=t,full_frame_path='turn_evidence/'+out.name,selected_for_start_hand=role=='selected_preplay_hand',before_first_play=role=='selected_preplay_hand',draw_animation_end_seconds=67 if role=='selected_preplay_hand' else None,offset_after_draw_seconds=t-67 if role=='selected_preplay_hand' else None,observation=observation,suitability_or_limit='Independently inspected retained native evidence.')
    f['bottom_crop']['path']='turn_evidence/'+stem+'_bottom.png'; f['top_crop']['path']='turn_evidence/'+stem+'_top.png'
    f['unzoomed']=True if role=='selected_preplay_hand' else False
    f['hand_spread']=True if role=='selected_preplay_hand' else None
    evidence['frames'].append(f); frames[eid]=f
add_frame(67.5,'focus/t0067.50.jpg','selected_preplay_hand','Intact five-card hand before Ball leaves the fan: Research, Copycat, Ball, Mega Sharpedo ex, Lucky Ice Pop.')
add_frame(84,'detail/t0084.00.jpg','draw_or_search_reveal','Second Research reveal Wallace; Soothing Shore is already in hand.')
for eid,description in [('f0068.00','Ball has left the fan; four-card hand during search.'),('f0070.00','Four-card hand while Ball search resolves; not intact starting hand.')]:
    f=frames[eid]; f.update(selected_for_start_hand=False,before_first_play=False,role='draw_relative_candidate',roles=['draw_relative_candidate'],observation=description,suitability_or_limit=description)
frames['f0071.00']['observation']='Carvanha search reveal, after Ball input bounded to67.5-68s.'
frames['f0083.00']['observation']='First Research reveal Soothing Shore.'
frames['f0085.00']['observation']='Resolved five-card hand after Shore then Wallace reveals; not an individual reveal.'
t=ledger['turns'][0]
def replace_evidence(value):
    if isinstance(value,dict):
        for k,v in value.items():
            if k=='evidence_ids': value[k]=['f0067.50' if x=='f0068.00' else x for x in v]
            else: replace_evidence(v)
    elif isinstance(value,list):
        for v in value: replace_evidence(v)
for key in ['owner_hand_start','hand_at_start','board_at_start']: replace_evidence(t[key])
t['timing']['first_voluntary_move_seconds']=67.5
t['timing']['first_voluntary_move_window_seconds']=[67.5,68]
t['timing']['first_voluntary_move_basis']='Ball visible in intact fan at67.5; absent at68. Exact input occurs between retained frames.'
p=t['plays_in_order'][0]; p.update(timestamp_seconds=67.5,timestamp_window_seconds=[67.5,68],evidence_ids=['f0067.50','f0068.00','f0071.00'],result='Ball input67.5-68s; Carvanha is revealed at71s and resolved into hand by72s.')
s=t['draws_and_searches'][1]; s.update(timestamp_seconds=71,evidence_ids=['f0071.00','f0072.00'])
s['cards_in_reveal_order'][0].update(timestamp_seconds=71,evidence_ids=['f0071.00'])
r=t['draws_and_searches'][2]
r['cards_in_reveal_order']=[dict(name='Soothing Shore',reveal_position=1,source_video=t['source_video'],timestamp_seconds=83,evidence_ids=['f0083.00'],basis='visible named reveal',limit_reason=None),dict(name='Wallace',reveal_position=2,source_video=t['source_video'],timestamp_seconds=84,evidence_ids=['f0084.00'],basis='visible named reveal; Shore already in hand',limit_reason=None)]
r.update(timestamp_seconds=83,evidence_ids=['f0083.00','f0084.00','f0085.00'])
t['plays_in_order'][2]['result']='Draw Soothing Shore at83, then Wallace at84; resolved five-card hand at85.'
t['turn_evidence_ids']=list(dict.fromkeys(['f0067.50','f0084.00']+t['turn_evidence_ids']))
visible={'f0128.00':3,'f0224.00':5,'f0335.00':7,'f0360.00':8,'f0454.00':11,'f0528.00':14}
for row in ledger['turns']:
    for key in ['board_at_start','board_after']:
        board=row[key]; label=next((visible[x] for x in board.get('evidence_ids',[]) if x in visible),None)
        board['turn_number_displayed']=label
        board['turn_number_displayed_basis']='Readable Current turn transition label in referenced frame.' if label else 'The selected board evidence does not independently establish a readable Current turn label; chronological turn is recorded separately.'
        board['turn_number_displayed_limit_reason']=None if label else 'Do not infer an observed label from the chronological row number.'
        board['chronological_turn_number']=row['turn_number']
        if label and key=='board_after': board['phase']=f'After chronological turn{row["turn_number"]}; transition displays Current turn{label}.'
deck=read('DECK_USED.json')
def normalize(v):
    if isinstance(v,str):
        if any(x in v for x in ['Ã','â€','Â']):
            try: return v.encode('cp1252').decode('utf-8')
            except (UnicodeEncodeError,UnicodeDecodeError): pass
        return v
    if isinstance(v,list): return [normalize(x) for x in v]
    if isinstance(v,dict): return {k:normalize(x) for k,x in v.items()}
    return v
deck=normalize(deck)
review=(P/'REVIEW.md').read_text(encoding='utf-8').replace('Pre-play hand frame 68s;','Pre-play hand frame 67.5s;').replace('1. 71s: Poké Ball; Search reveals Carvanha at72.','1. 67.5-68s: Poké Ball leaves the intact hand; Carvanha reveal at71, resolved hand at72.').replace('Draw Wallace at83, then Soothing Shore at85.','Draw Soothing Shore at83, then Wallace at84; resolved hand at85.')
review+='\nIndependent corrections C1-C4: selected intact pre-play hand67.5s replaces post-play68s; Research reveal order Shore83 then Wallace84; displayed transition numbers are separate from chronological rows; authored deck names normalized to UTF-8. Original submission is retained.\n'
save('TURN_LEDGER.json',ledger); save('TURN_EVIDENCE.json',evidence); save('DECK_USED.json',deck)
(P/'REVIEW.md').write_text(review,encoding='utf-8')
save('INDEPENDENT_CORRECTIONS.json',{'correction_ids':['C1','C2','C3','C4'],'source_video':t['source_video'],'independent_report':'independent_sol/CHECK_RESULT.json','prior_submission':'submitted_before_independent_corrections','changes':'Only independently identified evidence, reveal order, observed turn labels and authored name encoding corrected; source and QR receipt unchanged.','current_sha256':{n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in files}})
print('Applied C1-C4 with native retained frames and preserved submission.')
