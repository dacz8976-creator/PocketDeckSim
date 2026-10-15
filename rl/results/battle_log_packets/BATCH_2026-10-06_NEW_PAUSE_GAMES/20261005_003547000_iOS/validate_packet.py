import json
from pathlib import Path
from PIL import Image
P=Path(__file__).resolve().parent
names=['SOURCE','SUMMARY','UNCERTAINTIES','PAUSE_GAME','DECK_USED','TURN_LEDGER','TURN_EVIDENCE']
j={n:json.loads((P/(n+'.json')).read_text(encoding='utf-8')) for n in names}
t=j['TURN_LEDGER']['turns']; e=j['TURN_EVIDENCE']['frames']; ids={x['evidence_id'] for x in e}
assert [x['turn_number'] for x in t]==list(range(1,15))
assert len(j['DECK_USED']['filmed_cards_20_slots'])==20
assert j['PAUSE_GAME']['opening']['recorded_card_count']==5
assert j['PAUSE_GAME']['match_date']=='2026-10-04'
assert j['PAUSE_GAME']['outcome']['owner_points']==0 and j['PAUSE_GAME']['outcome']['opponent_points']==3
for x in e:
    assert x['source_sha256']==j['SOURCE']['sha256']
    assert Image.open(P/x['full_frame_path']).size==(1170,2532)
    assert Image.open(P/x['bottom_crop']['path']).size==(1170,507)
    assert Image.open(P/x['top_crop']['path']).size==(1170,700)
for row in t:
    assert row['who_played']==('owner' if row['turn_number']%2 else 'opponent')
    assert [p['order'] for p in row['plays_in_order']]==list(range(1,len(row['plays_in_order'])+1))
    for board in [row['board_at_start'],row['board_after']]:
        for side in ['owner','opponent']:
            assert len(board[side]['bench_in_position_order'])==3
            for m in [board[side]['active']]+board[side]['bench_in_position_order']:
                if m and m.get('name'):
                    assert m['hp_now']<=m['hp_max']
                    assert m['attached_energy']['total']==sum(m['attached_energy']['by_type'].values())
    if row['who_played']=='owner':
        for key in ['owner_hand_start','owner_hand_end','owner_hand_before_end_action']:
            h=row[key];assert h['count']==len(h['cards_left_to_right'])
        assert len([a for a in row['turn_evidence_ids'] if next(x for x in e if x['evidence_id']==a)['role'] in ['draw_relative_candidate','failed_draw_relative_candidate'] or 'draw_relative_candidate' in next(x for x in e if x['evidence_id']==a)['roles'] or 'failed_draw_relative_candidate' in next(x for x in e if x['evidence_id']==a)['roles']])>=3
def refs(obj):
    if isinstance(obj,dict):
        for k,v in obj.items():
            if k in ['evidence_ids','turn_evidence_ids','result_evidence']: assert all(x in ids for x in v),v
            else: refs(v)
    elif isinstance(obj,list):
        for v in obj: refs(v)
for n in names[1:]: refs(j[n])
b11=t[10]['board_after']['owner'];b13=t[12]['board_after']['owner']
assert [m['attached_energy']['total'] for m in b11['bench_in_position_order']]==[0,1,0]
assert [m['attached_energy']['total'] for m in b13['bench_in_position_order']]==[1,1,1]
assert b13['active']['attached_energy']['total']==1
assert t[12]['plays_in_order'][2]['kind']=='energy_attachment'
receipt={'status':'passed','turns':14,'indexed_native_frames':len(e),'crop_dimensions_verified':True,'all_evidence_references_resolve':True,'filmed_semantic_deck_slots':20,'late_energy_transitions_checked':True,'independent_acceptance':'pending'}
(P/'STRUCTURAL_CHECK.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt))
