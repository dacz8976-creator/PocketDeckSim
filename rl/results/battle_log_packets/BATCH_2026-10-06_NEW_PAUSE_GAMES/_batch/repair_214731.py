"""Correct four independently checked boundary/capture labels, preserving draft."""
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
p=Path(__file__).resolve().parent/'20261004_214731000_iOS'
backup=p/'submitted_before_independent_corrections';backup.mkdir(exist_ok=True)
names=['TURN_LEDGER.json','TURN_EVIDENCE.json','REVIEW.md','DECK_USED.json']
for n in names:
    if not (backup/n).exists():shutil.copy2(p/n,backup/n)
d=json.loads((p/'TURN_LEDGER.json').read_text(encoding='utf-8'))
d['turns'][5]['board_after']['turn_number_displayed']=7
d['turns'][5]['board_after']['phase']='Resolved turn6 board with transition to turn7 displayed'
d['turns'][6]['board_after']['turn_number_displayed']=8
d['turns'][6]['board_after']['phase']='Resolved turn7 board with transition to turn8 displayed'
d['turns'][5]['timing']['first_voluntary_move_seconds']=245
d['turns'][5]['timing']['first_voluntary_move_limit']='Hiking Trail has left the hand by245s and replacement resolves246s; this is a bounded input/animation window, not exact input PTS.'
b=d['turns'][7]['board_after']
def reref(v):
    if isinstance(v,str):return v.replace('e_0355.00','e_0354.00')
    if isinstance(v,list):return [reref(x) for x in v]
    if isinstance(v,dict):return {k:reref(x) for k,x in v.items()}
    return v
b=reref(b);d['turns'][7]['board_after']=b
b['phase']='Last fully visible KO board at354s before removal and point award; not a resolved post-removal Active state'
b['owner']['points']=0
b['terminal_resolution']={'owner_points_after_award':3,'opponent_points_after_award':0,'result':'victory','evidence_ids':['e_0359.00','e_0374.00'],
    'basis':'359s displays +3points;374s displays final3-0 Victory. Rayquaza removal begins355s. No post-removal stable board is claimed here.'}
(p/'TURN_LEDGER.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
e=json.loads((p/'TURN_EVIDENCE.json').read_text(encoding='utf-8'))
for f in e['frames']:
    if f['evidence_id']=='e_0278.00':
        f['unzoomed']=False;f['suitability_or_limit']='Accelgor attack zoom before attack resolution. Empty hand is established; this is a zoom substitution, corroborated by clear273s empty-hand view before retreat.'
    if f['evidence_id']=='e_0245.00':
        f['before_first_play']=False;f['suitability_or_limit']='Hiking Trail play in progress; only Accelgor and Lucky Ice Pop remain in the hand. Selected244s retains the intact3-card preplay hand. First input is bounded by245-246s animation.'
(p/'TURN_EVIDENCE.json').write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
text=(p/'REVIEW.md').read_text(encoding='utf-8')
text+='\nIndependent-check corrections: The245s hand candidate is already during Hiking Trail play;244s is the selected intact hand. The278s pre-attack view is zoomed and the empty hand has clear273s corroboration. Turn6/7 board-after displays are7/8 at transition. The terminal structured board is the last fully visible KO state354s with0points displayed;359s and374s independently establish the subsequent3-point award and3-0 victory. Recording local date is confirmed in RECORDING_METADATA.json.\n'
(p/'REVIEW.md').write_text(text,encoding='utf-8')
for n in names:
    text=(p/n).read_text(encoding='utf-8').replace('Pok\ufffdmon','Pok\u00e9mon').replace('Pok\ufffd Ball','Pok\u00e9 Ball')
    (p/n).write_text(text,encoding='utf-8')
(p/'INDEPENDENT_CORRECTIONS.json').write_text(json.dumps({'author':'/root','corrected_utc':datetime.now(timezone.utc).isoformat(),'basis':'independent_sol/CHECK_RESULT.json; root inspected354/355/359native frames','findings_addressed':['R1','R2','R3','R4'],'historical_submission':str(backup),'pending_independent_recheck':True},indent=2)+'\n',encoding='utf-8')
print('Applied four narrow corrections; prior submission retained.')
