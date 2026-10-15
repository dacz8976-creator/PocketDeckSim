import copy, hashlib, json
from pathlib import Path
from datetime import datetime, timezone
out=Path(__file__).resolve().parent
p=out.parent
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
old=read(out/'INDEPENDENT_ACCEPTANCE.rejected.json')
frozen_receipt_sha=sha(out/'INDEPENDENT_ACCEPTANCE.rejected.json')
errors=[]
def check(ok, msg):
    if not ok: errors.append(msg)
current={n:sha(p/n) for n in old['checked_input_sha256']}
backups={n:sha(p/'original_before_R1_R3'/n) for n in old['checked_input_sha256']}
check(backups==old['checked_input_sha256'],'Preserved originals do not match frozen first-pass hashes')
changed=[n for n,h in current.items() if h!=old['checked_input_sha256'][n]]
check(set(changed)=={'TURN_LEDGER.json','REVIEW.md'},'Unexpected changed required inputs')
a=read(p/'original_before_R1_R3/TURN_LEDGER.json')
b=read(p/'TURN_LEDGER.json')
normalized=copy.deepcopy(b)
stadiums=tools=absent=0
for i,(oldrow,newrow,normrow) in enumerate(zip(a['turns'],b['turns'],normalized['turns'])):
    for key in ['board_at_start','board_after']:
        orig=oldrow[key]; board=newrow[key]; norm=normrow[key]
        check(board.get('stadium')=='none' and board.get('stadium_status')=='observed_absent',f'R1 stadium {i} {key}')
        check(board.get('stadium_basis')==orig.get('stadium_basis'),f'R1 stadium basis {i} {key}')
        stadiums+=1
        norm['stadium']=orig['stadium']; norm.pop('stadium_status',None)
        for side in ['owner','opponent']:
            oldmon=[orig[side]['active']]+orig[side]['bench_in_position_order']
            newmon=[board[side]['active']]+board[side]['bench_in_position_order']
            normmon=[norm[side]['active']]+norm[side]['bench_in_position_order']
            for j,(om,nm,cm) in enumerate(zip(oldmon,newmon,normmon)):
                if om.get('status')!='empty' and om.get('name'):
                    check(nm.get('tool')=='none' and nm.get('tool_status')=='observed_absent',f'R1 Tool {i} {key} {side} {j}')
                    check('No attached Tool visible' in nm.get('tool_basis',''),f'R1 Tool basis {i} {key} {side} {j}')
                    tools+=1
                    cm['tool']=om['tool']; cm.pop('tool_status',None)
                    if 'tool_basis' in om: cm['tool_basis']=om['tool_basis']
                    else: cm.pop('tool_basis',None)
        visible=(oldrow['turn_number']==5 and key=='board_after')
        if visible:
            check(board['turn_number_displayed']==6 and board['evidence_ids']==['F014500'],'R2 visible T5 after banner changed')
        else:
            absent+=1
            check(board['turn_number_displayed'] is None,f'R2 absent banner {i} {key}')
            check(board.get('inferred_row_turn_number')==oldrow['turn_number'],f'R2 inferred row {i} {key}')
            check('No readable Current turn label' in board.get('turn_number_limit_reason',''),f'R2 absence reason {i} {key}')
            norm['turn_number_displayed']=orig['turn_number_displayed']
            norm.pop('inferred_row_turn_number',None); norm.pop('turn_number_limit_reason',None)
        if oldrow['turn_number']==4 and key=='board_after':
            check('no readable current-turn banner' in board['phase'] and 'turn 5 displayed' not in board['phase'],'R2 T4 after phase')
            norm['phase']=orig['phase']
check(stadiums==14 and tools==82 and absent==13,'R1/R2 affected counts wrong')
play=b['turns'][5]['plays_in_order'][0]
priorplay=a['turns'][5]['plays_in_order'][0]
event=play['nested_events_in_order'][2]
check(event['timestamp_seconds'] is None,'R3 false exact timestamp persists')
check(event.get('observed_transition_interval_seconds')==[158,160],'R3 wrong interval')
check(event['evidence_ids']==['F015800','F016000'],'R3 wrong nested evidence')
check('After158 (Pop absent), by160 (Pop visible)' in event.get('interval_bounds',''),'R3 bound qualifier missing')
check('Same Lucky Ice Pop returned after158 and by160; not a new deck draw.' in event['details'],'R3 return identity/bound wording')
check(set(play['evidence_ids'])==set(priorplay['evidence_ids'])|{'F016000'},'R3 wrong outer play evidence')
normalized['turns'][5]['plays_in_order'][0]=copy.deepcopy(priorplay)
check(normalized==a,'Unexpected ledger edits outside R1-R3')
before=(p/'original_before_R1_R3/REVIEW.md').read_text(encoding='utf-8-sig')
after=(p/'REVIEW.md').read_text(encoding='utf-8-sig')
oldphrase='coin Heads at 157.5 and return same Item to hand at 158.'
newphrase='coin Heads at 157.5; the same Item is absent at158 and back in hand by160, so the return is bounded after158 and by160, with exact instant unknown.'
check(before.count(oldphrase)==1 and after==before.replace(oldphrase,newphrase),'Unexpected REVIEW changes or missing bounded return')
supp={n:sha(Path(n) if Path(n).is_absolute() else p/n) for n in old['supplemental_checked_input_sha256']}
supp_changes=[n for n,h in supp.items() if h!=old['supplemental_checked_input_sha256'][n]]
check(not supp_changes,'Previously checked supplemental evidence changed')
for n in ['ROOT_CORRECTIONS_R1_R3.json','CORRECTION_LEDGER.md']:
    supp[n]=sha(p/n)
for n in ['INDEPENDENT_ACCEPTANCE.rejected.json','CHECK_RESULT.rejected_R1_R3.json','CHECK_RESULT.json','INTEGRITY_CHECK.json']:
    supp['independent_sol/'+n]=sha(out/n)
check(supp['independent_sol/CHECK_RESULT.rejected_R1_R3.json']==frozen_receipt_sha,'Frozen gate rejection changed')
check(supp['independent_sol/CHECK_RESULT.json']==frozen_receipt_sha,'Original gate rejection changed')
evidence=read(p/'TURN_EVIDENCE.json')
evidence_hashes={}
for frame in evidence['frames']:
    if frame['evidence_id'] not in ['F015800','F016000']: continue
    f=frame['full_frame_path']; evidence_hashes[f]=sha(p/f)
    check(evidence_hashes[f]==old['evidence_checked_sha256'][f],f'Native evidence changed {f}')
    for kind in ['bottom_crop','top_crop']:
        evidence_hashes[frame[kind]['path']]=sha(p/frame[kind]['path'])
check(len(evidence_hashes)==6,'Missing narrowed evidence')
check(current=={n:sha(p/n) for n in current},'Inputs changed during amendment recheck')
receipt={
 'schema':'battle-review/independent-sol-correction-recheck-v1',
 'reviewer':'/root/independent_012140','review_model':'gpt-6.1-sol','reasoning_effort':'high',
 'reviewed_utc':datetime.now(timezone.utc).isoformat(),
 'source_video':old['source_video'],'source_sha256':old['source_sha256'],'duration_seconds':old['duration_seconds'],
 'scope':'Narrow independent amendment check of frozen R1-R3 findings. Read repaired ledger/prose, compared against preserved originals, and viewed unchanged native full frames158/160 at original resolution. Prior bounded acceptance observations remain in frozen rejection. No second full review or source extraction.',
 'accepted':not errors,'decision':'accepted_after_R1_R3_amendment' if not errors else 'rejected_amendment',
 'checked_input_sha256':current,'supplemental_checked_input_sha256':supp,
 'frozen_rejection':'INDEPENDENT_ACCEPTANCE.rejected.json','frozen_rejection_sha256':frozen_receipt_sha,
 'preserved_original_input_sha256':backups,'original_backups_match_frozen':backups==old['checked_input_sha256'],
 'changed_required_inputs':changed,'unchanged_supplemental_inputs':not supp_changes,
 'resolved_findings':[
  {'id':'R1_absence_representation','checked_stadium_boundaries':stadiums,'checked_occupied_tool_absences':tools,'finding':'Explicit none and observed_absent preserve source-grounded absence and empty positional slots.'},
  {'id':'R2_displayed_turn','checked_absent_banner_boundaries':absent,'finding':'Thirteen unsupported displayed-turn values are null with reason and separate inferred row number. Visible T5 after displayed6/F014500 remains intact. T4 after unsupported phase text removed.'},
  {'id':'R3_item_return_time','viewed_source_seconds':[158,160],'evidence_ids':['F015800','F016000'],'finding':'At158 Pop is absent from Scolipede/Whirlipede/Wally/Cyrus fan. At160 Pop is present in Whirlipede/Wally/Cyrus/Pop fan while evolution is underway. Same Item return is bounded after158 and by160; exact instant remains unknown. Ledger and REVIEW agree.'}
 ],
 'evidence_checked_sha256':evidence_hashes,'errors':errors,
 'ordinary_source_timestamps_previously_checked':{'opening':[23.5,25],'first_owner_Ball_decision':[59,60,60.5,61,62.5,64,65.5],'full_ordinary_opponent_turn':[90,91,92,94,96,98,99,100,101,102,103,104]},
 'inherited_limits':'Concealed opponent search identity remains unknown. Exact game-bound20-card list staysnull; prior183108 QR is a qualified candidate with unrecorded edit/version uncertainty. Acceptance rests on native evidence checks and precise amended semantics, not structural validation alone.',
 'astra_required':False,'canonical_files_edited':False,'lead_acceptance_written':False,'registration_media_or_external_writes':False
}
(out/'CORRECTION_RECHECK.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'accepted':receipt['accepted'],'errors':errors,'R1_counts':[stadiums,tools],'R2_count':absent,'changed_required_inputs':changed,'supplemental_changes':supp_changes,'receipt':str(out/'CORRECTION_RECHECK.json')},ensure_ascii=False))
