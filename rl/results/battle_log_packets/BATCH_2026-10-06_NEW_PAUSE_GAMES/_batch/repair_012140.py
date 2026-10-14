"""One-time root repair of the three frozen independent 012140 findings."""
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

B=Path(__file__).resolve().parent
P=B/'20261006_012140000_iOS'
receipt=json.loads((P/'independent_sol/INDEPENDENT_ACCEPTANCE.rejected.json').read_text(encoding='utf-8'))
backup=P/'original_before_R1_R3'
assert not backup.exists(), 'Do not rerun this repair'
backup.mkdir()
for name,expected in receipt['checked_input_sha256'].items():
    assert hashlib.sha256((P/name).read_bytes()).hexdigest()==expected, name
    shutil.copy2(P/name,backup/name)

def save(name,value):
    (P/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

ledger=json.loads((P/'TURN_LEDGER.json').read_text(encoding='utf-8'))
tool_count=0
for turn in ledger['turns']:
    for key in ('board_at_start','board_after'):
        board=turn[key]
        assert board['stadium'] is None
        board['stadium']='none'
        board['stadium_status']='observed_absent'
        for player in ('owner','opponent'):
            side=board[player]
            for mon in [side.get('active')]+side.get('bench_in_position_order',[]):
                if isinstance(mon,dict) and mon.get('name') and mon.get('status')!='visibly_empty' and mon.get('tool') is None:
                    mon['tool']='none';mon['tool_status']='observed_absent'
                    mon['tool_basis']='No attached Tool visible in the cited native board; no Tool play in the fully reviewed source.'
                    tool_count+=1
        if not (turn['turn_number']==5 and key=='board_after'):
            board['turn_number_displayed']=None
            board['turn_number_limit_reason']='No readable Current turn label in this cited native frame; ledger row turn comes from separately observed transitions.'
            board['inferred_row_turn_number']=turn['turn_number']
        if turn['turn_number']==4 and key=='board_after':
            board['phase']='Turn4 attack and checkup resolved; row turn from observed source transitions, no readable current-turn banner in this frame.'
assert ledger['turns'][4]['board_after']['turn_number_displayed']==6
play=ledger['turns'][5]['plays_in_order'][0]
event=next(e for e in play['nested_events_in_order'] if e['event']=='return same Item')
assert event['timestamp_seconds']==158
event['timestamp_seconds']=None
event['observed_transition_interval_seconds']=[158,160]
event['interval_bounds']='After158 (Pop absent), by160 (Pop visible); exact return instant not measured.'
event['evidence_ids']=['F015800','F016000']
event['details']='Same Lucky Ice Pop returned after158 and by160; not a new deck draw. At160 Scolipede evolution is already underway.'
if 'F016000' not in play['evidence_ids']:play['evidence_ids'].append('F016000')
save('TURN_LEDGER.json',ledger)
review=(P/'REVIEW.md').read_text(encoding='utf-8')
old='coin Heads at 157.5 and return same Item to hand at 158.'
assert old in review
review=review.replace(old,'coin Heads at 157.5; the same Item is absent at158 and back in hand by160, so the return is bounded after158 and by160, with exact instant unknown.')
(P/'REVIEW.md').write_text(review,encoding='utf-8')
changes={'repaired_utc':datetime.now(timezone.utc).isoformat(),'root':'/root','frozen_rejection':'independent_sol/INDEPENDENT_ACCEPTANCE.rejected.json','R1':{'stadium_boundaries':14,'occupied_tool_absences':tool_count},'R2':{'absent_banner_values':13,'preserved_visible_banner':'T5 board_after displayed6, F014500'},'R3':{'same_Item_return_interval_seconds':[158,160],'exact_instant':None,'evidence_ids':['F015800','F016000']},'independent_recheck_required':True}
save('ROOT_CORRECTIONS_R1_R3.json',changes)
(P/'CORRECTION_LEDGER.md').write_text('# Independent correction record\n\nPreserved all nine frozen first-pass inputs in original_before_R1_R3. Root corrected observed-absence scalars, thirteen unsupported displayed-turn fields and the bounded Item-return time. Native frames, action order, ending counts, deck qualification and result remain source-bound. Independent amended-field acceptance is required.\n',encoding='utf-8')
result=subprocess.run([sys.executable,str(B/'validate_packet.py'),str(P)],capture_output=True,text=True,encoding='utf-8',check=True)
structure=json.loads(result.stdout);assert structure['structural_pass']
save('ROOT_REPAIR_STRUCTURE_CHECK.json',structure)
print(json.dumps(changes))
