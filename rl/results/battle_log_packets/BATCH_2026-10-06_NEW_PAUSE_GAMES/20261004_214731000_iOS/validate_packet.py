import json,re
from pathlib import Path
p=Path(__file__).resolve().parent
a=json.loads((p/'TURN_LEDGER.json').read_text(encoding='utf-8'))
e=json.loads((p/'TURN_EVIDENCE.json').read_text(encoding='utf-8'))
ids={x['evidence_id'] for x in e['frames']}
refs=set(re.findall(r'e_\d{4}\.\d{2}',(p/'TURN_LEDGER.json').read_text(encoding='utf-8')))
missing=sorted(refs-ids)
assert len(a['turns'])==8 and [x['turn_number'] for x in a['turns']]==list(range(1,9))
assert not missing,missing
for f in e['frames']:
    assert (p/f['full_frame_path']).exists()
    for k in ['bottom_crop','top_crop']:assert (p/f[k]['path']).exists()
    assert f['native_dimensions']=={'width':1170,'height':2532}
for f in ['PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']:
    j=json.loads((p/f).read_text(encoding='utf-8'));assert j['is_template']==False
    assert j['sources'][0]['sha256']=='d363bdd1c3f4aafc5ad9423764e706f8944407d68a04c82d72317592d7e7e198'
for n in [2,4,6,8]:
    fs=[f for f in e['frames'] if f['turn_number']==n]
    assert sorted(f['offset_after_draw_seconds'] for f in fs if f['role']=='draw_offset_candidate')==[1,3,6]
    assert len([f for f in fs if f['selected_for_start_hand']])==1
    assert len([f for f in fs if f['role']=='before_end_action'])==1
print(f'PASS:8orderedturns; {len(e["frames"])} nativeframes; allsource/hash/path/crop/candidate checks. Semantic acceptance remains independent.')
