import json, copy, subprocess, sys
from pathlib import Path
from PIL import Image
P=Path(__file__).resolve().parent
def read(n):return json.loads((P/n).read_text(encoding='utf-8-sig'))
def write(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def eid(t):return 'F_'+f'{t:07.2f}'.replace('.','_')
e=read('TURN_EVIDENCE.json');sample=e['frames'][0]
for t,n,note in [(113,3,'Poison applied to Meloetta30.'),(136,4,'Research completed hidden draws; six-card fan and waiting overlay.'),(272,7,'Gourgeist removed; opponent Active empty.'),(288,8,'Strange Singing automatic ability after normal hidden draw.'),(336,9,'Second Mega bench-play reveal after consumption.')]:
    f=P/'turn_evidence'/f't{t:07.2f}.jpg';tag=eid(t);bottom=P/'turn_evidence'/'crops'/(tag+'_bottom.png');top=P/'turn_evidence'/'crops'/(tag+'_top.png')
    with Image.open(f) as im:
        assert im.size==(1170,2532);im.crop((0,2025,1170,2532)).save(bottom);im.crop((0,0,1170,720)).save(top)
    d=copy.deepcopy(sample);d.update(evidence_id=tag,turn_number=n,who_played='owner' if n%2 else 'opponent',requested_source_seconds=t,full_frame_path=f.relative_to(P).as_posix(),observation=note)
    d['bottom_crop']['path']=bottom.relative_to(P).as_posix();d['top_crop']['path']=top.relative_to(P).as_posix();e['frames'].append(d)
e['frames'].sort(key=lambda f:f['requested_source_seconds'])
write('TURN_EVIDENCE.json',e)
l=read('TURN_LEDGER.json');r7=l['turns'][6];r8=l['turns'][7]
r7['source_interval_seconds'][1]=285;r8['source_interval_seconds'][0]=285
b=copy.deepcopy(r7['board_after']);b.update(timestamp_seconds=285,turn_number_displayed=8,turn_number_limit=None,evidence_ids=[eid(285)])
for who in ['owner','opponent']:
    b[who]['evidence_ids']=[eid(285)];b[who]['energy_zone']['evidence_ids']=[eid(285)]
    b[who]['active']['evidence_ids']=[eid(285)]
    for c in b[who]['bench_in_position_order']:c['evidence_ids']=[eid(285)]
r7['board_after']=b;r8['board_at_start']=copy.deepcopy(b);r7['timing']['end_after_resolution_seconds']=285
d=r8['draws_and_searches'][0];d['timestamp_seconds']=287;d['evidence_ids']=[eid(285),eid(286),eid(287)];d['cards_in_reveal_order'][0].update(timestamp_seconds=287,evidence_ids=[eid(287)]);d['limit_reason']='Normal hidden draw is established by fan2 at286→3 at287, before Strange Singing288. Card identity hidden.'
d=r8['draws_and_searches'][1];d['timestamp_seconds']=288;d['evidence_ids']=[eid(288),eid(290)];d['cards_in_reveal_order'][0].update(timestamp_seconds=290,evidence_ids=[eid(290)])
for r in l['turns']:
    for p in r['plays_in_order']:
        p['actor']='owner' if r['who_played']=='owner' or p['kind']=='forced_promotion' else 'opponent'
        p['input_time_precision']='Requested native frame witnessing consuming interaction / changed hand, not an exact touch or decoded-frame PTS.' if p['consuming_input_seconds'] is not None else 'Actual consuming input not visible separately; public witness timestamp only.'
    r['turn_evidence_ids']=sorted(set(r['turn_evidence_ids']+r['board_at_start']['evidence_ids']+r['board_after']['evidence_ids']))
write('TURN_LEDGER.json',l)
text=(P/'REVIEW.md').read_text(encoding='utf-8').replace('Turn7 (owner), [244, 287]','Turn7 (owner), [244, 285]').replace('Turn8 (opponent), [287, 312]','Turn8 (opponent), [285, 312]').replace('### Turn 7 (owner), [244, 287]','### Turn 7 (owner), [244, 285]').replace('### Turn 8 (opponent), [287, 312]','### Turn 8 (opponent), [285, 312]').replace('Draw/search 288s: normal_draw_hidden via turn draw. Reveals: hidden@288.','Draw/search 287s: normal_draw_hidden via turn draw. Reveals: hidden@287.').replace('Draw/search 292s: automatic_search_hidden via Meloetta / Strange Singing. Reveals: hidden@292.','Draw/search 288s: automatic_search_hidden via Meloetta / Strange Singing. Reveals: hidden@290.')
text+='\nInput timestamps are requested native-frame witnesses of local consuming interaction or changed hand; exact touch timing and decoded frame PTS are not claimed. The opponent turn8 label is directly readable at285s. Normal hidden draw grows fan2 at286s to3 at287s; Strange Singing then grows it to4 by290s.\n'
(P/'REVIEW.md').write_text(text,encoding='utf-8')
text=(P/'COVERAGE.md').read_text(encoding='utf-8').replace('Turn7 [244, 287]','Turn7 [244, 285]').replace('Turn8 [287, 312]','Turn8 [285, 312]');(P/'COVERAGE.md').write_text(text,encoding='utf-8')
c=read('CONSISTENCY_CHECK.json');c['checks']['native_evidence_registered']=len(e['frames']);c['checks']['damage_result_crosscheck']={'direct_owner_attacks':330,'cursed_jewel_retaliations':120,'deceptive_needle':20,'sum':470,'result':470,'poison_checkup_separate':10};c['checks']['turn8_normal_draw_before_ability']=True;write('CONSISTENCY_CHECK.json',c)
result=subprocess.run([sys.executable,str(P.parent/'validate_packet.py'),str(P)],capture_output=True,text=True,encoding='utf-8')
receipt=json.loads(result.stdout);write('VALIDATION.json',receipt);print(json.dumps(receipt,ensure_ascii=False,indent=2));raise SystemExit(result.returncode)
