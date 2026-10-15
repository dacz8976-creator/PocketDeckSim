"""Narrow corrections from independently inspected source; retain prior submission."""
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

p=Path(__file__).resolve().parent/'20261004_215749000_iOS'
files=['TURN_LEDGER.json','TURN_EVIDENCE.json','REVIEW.md','COVERAGE.md','UNCERTAINTIES.json']
backup=p/'submitted_before_independent_corrections'
backup.mkdir(exist_ok=True)
for name in files:
    target=backup/name
    if not target.exists(): shutil.copy2(p/name,target)

def normalize(v):
    if isinstance(v,str):
        return v.replace('Pok\u00c3\u00a9','Pok\u00e9').replace('\u00e2\u20ac\u2122',"'")
    if isinstance(v,list): return [normalize(x) for x in v]
    if isinstance(v,dict): return {k:normalize(x) for k,x in v.items()}
    return v

d=normalize(json.loads((p/'TURN_LEDGER.json').read_text(encoding='utf-8')))
def resolved_refs(v):
    if isinstance(v,str): return v.replace('f0225.00','f0226.00').replace('Visible225-226s','Visible226s')
    if isinstance(v,list): return [resolved_refs(x) for x in v]
    if isinstance(v,dict):
        return {k:(226 if k=='timestamp_seconds' and x==225 else resolved_refs(x)) for k,x in v.items()}
    return v
t=resolved_refs(d['turns'][4]); d['turns'][4]=t
lim='The 225s Connection is unstable overlay obscures resolution. The clear226s frame establishes the added card and replacement board; exact reveal onset and draw-versus-replacement order are not established.'
dr=t['draws_and_searches'][-1]
dr['limit_reason']=lim
dr['cards_in_reveal_order'][0]['limit_reason']=lim
dr['cards_in_reveal_order'][0]['basis']='observed in resolved hand; draw source supported by Stadium text and hand count change'
t['automatic_events_in_order']=[t['automatic_events_in_order'][0],{
    'order':2,'name':'End-turn resolution','timestamp_seconds':226,
    'result':'Resolved hand has Field Blower, Copycat and Mega Blaziken ex, consistent with Hiking Trail end-turn draw. Meltan is Active with its one Metal retained. The relative order of draw and replacement is obscured.',
    'evidence_ids':['f0206.00','f0225.00','f0226.00'],'limit_reason':lim}]
t['owner_hand_end']['basis']='Visible226s resolved hand after Hiking Trail end-turn draw, distinct from pre-attack two-card hand'
t['board_after']['turn_number_displayed']=None
t['board_after']['turn_number_displayed_limit']='No Current turn label in the226s resolved-board frame; this is the board after owner turn5, before opponent voluntary actions.'
t['board_after']['phase']='Resolved end of owner turn5 and transition to opponent turn6'
d['turns'][0]['board_after']['turn_number_displayed']=2
d['turns'][0]['board_after']['phase']='Resolved owner turn1 board with opponent turn2 transition displayed at74s'
for row in d['turns']:
    for key in (k for k in row if k.startswith('board_') and isinstance(row[k],dict)):
        b=row[key]
        if b.get('stadium') is None:
            b['stadium']='none'
            b['stadium_status']='observed_absent'
        for who in ('owner','opponent'):
            side=b[who]
            pokemon=[side.get('active')]+[x for x in side.get('bench_in_position_order',[]) if x]
            for mon in pokemon:
                if isinstance(mon,dict) and mon.get('tool') is None and mon.get('status')=='observed':
                    mon['tool']='none'; mon['tool_status']='observed_absent'
            side['bench_empty_positions']=[i+1 for i,x in enumerate(side['bench_in_position_order']) if x is None]
            side['bench_empty_positions_basis']='These null positional entries are visibly empty Bench slots, not unknown Pokemon.'
(p/'TURN_LEDGER.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

for name in ['REVIEW.md','COVERAGE.md','TURN_EVIDENCE.json']:
    text=(p/name).read_text(encoding='utf-8')
    text=text.replace('by225s','by226s').replace('225-226s','226s').replace('post-Trail225s','post-Trail226s')
    text=text.replace('in225-226s hand','in226s hand')
    if name=='REVIEW.md':
        text+='\nIndependent-check correction: The225s Connection is unstable overlay does not establish the resolved hand or replacement board. The clear226s frame supports both; exact draw onset and draw-versus-replacement order remain obscured. Turn1 board-after evidence displays the transition to turn2. Observed absence of Tools/Stadium and visibly empty Bench positions are now explicit.\n'
    (p/name).write_text(text,encoding='utf-8')
u=json.loads((p/'UNCERTAINTIES.json').read_text(encoding='utf-8'))
for item in u['items']:
    if item['id']=='end_turn_draw':
        item['finding']=lim+' Low-battery notification also obscures part of222-224s. The known pre-attack hand is two cards; the resolved226s hand is three with Mega Blaziken ex.'
        item['evidence']=['f0206.00','f0225.00','f0226.00']
(p/'UNCERTAINTIES.json').write_text(json.dumps(u,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(p/'INDEPENDENT_CORRECTIONS.json').write_text(json.dumps({'corrected_utc':datetime.now(timezone.utc).isoformat(),'author':'/root','basis':'independent_sol/CHECK_RESULT.json and root inspected225/226/74 native frames','findings_addressed':['F1','F2','F3','F4'],'historical_submission':str(backup),'pending_independent_recheck':True},indent=2)+'\n',encoding='utf-8')
print('Applied four narrow corrections; prior submission retained.')
