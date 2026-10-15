"""Apply frozen independent R1: intact turn12 hand and actual first-input window."""
import copy,hashlib,json,shutil,subprocess,sys
from pathlib import Path
from PIL import Image
B=Path(__file__).resolve().parent;P=B/'20261005_032023000_iOS'
report=json.loads((P/'independent_sol/CHECK_RESULT.json').read_text(encoding='utf-8'))
assert report['accepted'] is False and [r['id'] for r in report['required_repairs']]==['R1']
for name,digest in report['checked_input_sha256'].items():assert hashlib.sha256((P/name).read_bytes()).hexdigest()==digest,name
backup=P/'submitted_before_independent_corrections';backup.mkdir(exist_ok=True)
files=['TURN_LEDGER.json','TURN_EVIDENCE.json','REVIEW.md','COVERAGE.md']
for name in files:
    if not (backup/name).exists():shutil.copy2(P/name,backup/name)
ledger=json.loads((P/'TURN_LEDGER.json').read_text(encoding='utf-8'))
evidence=json.loads((P/'TURN_EVIDENCE.json').read_text(encoding='utf-8'))
old=next(f for f in evidence['frames'] if f['evidence_id']=='f0397.50')
new=copy.deepcopy(old)
im=Image.open(P/'turn_evidence/t0397.00.jpg')
im.crop((0,2025,1170,2532)).save(P/'turn_evidence/t0397.00_bottom.png')
im.crop((0,0,1170,770)).save(P/'turn_evidence/t0397.00_top.png')
new.update(evidence_id='f0397.00',full_frame_path='turn_evidence/t0397.00.jpg',draw_animation_end_seconds=397,requested_source_seconds=397,offset_after_draw_seconds=0,observation='Intact four-card hand: Superb Shield Aegislash, Team Rocket\'s Tinkaton, Cursed Metal Aegislash, Research. Native frame precedes Research selection seen by397.2s.')
new['bottom_crop']['path']='turn_evidence/t0397.00_bottom.png';new['top_crop']['path']='turn_evidence/t0397.00_top.png'
old.update(role=['post_first_play_board'],selected_for_start_hand=False,before_first_play=False,observation='Research has already left the fan. Three prior cards remain; board unchanged before Research draws resolve.',suitability_or_limit='After Research selection; unsuitable as the intact starting four-card hand.')
evidence['frames'].append(new)
for f in evidence['frames']:
    if f.get('turn_number')==12 and f.get('draw_animation_end_seconds') is not None:
        f['draw_animation_end_seconds']=397
        f['offset_after_draw_seconds']=round(f['requested_source_seconds']-397,3)
t=ledger['turns'][11]
def replace(value):
    if isinstance(value,dict):
        for k,v in value.items():
            if k=='evidence_ids':value[k]=['f0397.00' if x=='f0397.50' else x for x in v]
            else:replace(v)
    elif isinstance(value,list):
        for v in value:replace(v)
for key in ['hand_at_start','owner_hand_start','board_at_start']:replace(t[key])
t['timing'].update(draw_animation_end_seconds=397,draw_end_precision='Approximately397.0s: intact settled four-card fan visible, selection already shown at397.2. Requested seek times, decoded PTS not measured.',first_voluntary_move_seconds=397.2,first_voluntary_move_window_seconds=[397,397.2])
t['board_at_start']['phase']='Turn12 start after normal draw and before first Research selection; current Metal generation visible.'
action=t['plays_in_order'][0]
action.update(timestamp_seconds=397.2,input_timestamp_seconds=397.2,input_timestamp_window_seconds=[397,397.2],evidence_ids=list(dict.fromkeys(['f0397.00','f0397.50']+action['evidence_ids'])),basis='Research present in intact hand397.0, selected by397.2 and absent397.5.398/399 show later play animation, not earliest input.',limit_reason='Exact tap lies between retained397.0 and397.2 source seeks.')
t['turn_evidence_ids']=list(dict.fromkeys(['f0397.00']+t['turn_evidence_ids']))
for name,value in [('TURN_LEDGER.json',ledger),('TURN_EVIDENCE.json',evidence)]:
    (P/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
review=(P/'REVIEW.md').read_text(encoding='utf-8').replace('Normal Research396-397.5. Research input398;','Normal Research396-397.0. Research selection397.0-397.2; later play animation398-399;')
review+='\nIndependent R1 correction: turn12 intact preplay hand is397.0s, not the three-card397.5s fan after Research selection. Current metadata/crops and input window are corrected; original submission and historical worker self-check receipts remain preserved.\n'
(P/'REVIEW.md').write_text(review,encoding='utf-8')
coverage=(P/'COVERAGE.md').read_text(encoding='utf-8').replace('starting board397.5s','starting board and intact hand397.0s')
coverage+='\nR1 recheck supersedes the original turn12 hand/input assertion without changing complete source coverage. See INDEPENDENT_CORRECTIONS.json and independent_sol/CORRECTION_RECHECK.json when accepted.\n'
(P/'COVERAGE.md').write_text(coverage,encoding='utf-8')
(P/'INDEPENDENT_CORRECTIONS.json').write_text(json.dumps({'repair_id':'R1','initial_independent_report':'independent_sol/CHECK_RESULT.json','prior_submission':'submitted_before_independent_corrections','scope':'Only turn12 hand/board evidence references, input/draw timing, candidate offsets and associated prose corrected. Four starting identities and three ending cards unchanged. Historical CONSISTENCY_RECEIPT/VALIDATION_RECEIPT are original submission checks; ROOT_R1_STRUCTURE_CHECK is current.','current_sha256':{n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in files}},indent=2)+'\n',encoding='utf-8')
result=subprocess.run([sys.executable,str(B/'validate_packet.py'),str(P)],capture_output=True,text=True,encoding='utf-8',check=True)
(P/'ROOT_R1_STRUCTURE_CHECK.json').write_text(result.stdout,encoding='utf-8')
print('R1 corrected; native files, source bindings and references pass.')
