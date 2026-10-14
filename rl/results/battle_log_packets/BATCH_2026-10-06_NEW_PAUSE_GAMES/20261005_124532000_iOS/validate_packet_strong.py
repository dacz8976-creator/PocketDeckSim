"""Source/evidence and ledger consistency receipt, never visual acceptance."""
from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,subprocess,sys
P=Path(__file__).parent.resolve()
def read(n): return json.loads((P/n).read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for part in iter(lambda:f.read(1048576),b''):h.update(part)
    return h.hexdigest()
base=subprocess.run([sys.executable,str(P.parent/'validate_packet.py'),str(P)],capture_output=True,text=True,encoding='utf-8')
base_receipt=json.loads(base.stdout)
issues=list(base_receipt['issues'])
S=read('SOURCE.json'); E=read('TURN_EVIDENCE.json'); L=read('TURN_LEDGER.json'); G=read('PAUSE_GAME.json'); D=read('DECK_USED.json'); R=read('SUMMARY.json')
frames={x['evidence_id']:x for x in E['frames']}
def check(ok,why):
    if not ok:issues.append(why)
def refs(v,trail):
    if isinstance(v,dict):
        for k,x in v.items():
            if (k.endswith('evidence_ids') or k=='evidence_ids') and isinstance(x,list):
                for key in x:check(key in frames,trail+'.'+k+' unknown frame '+str(key))
            else:refs(x,trail+'.'+k)
    elif isinstance(v,list):
        for i,x in enumerate(v):refs(x,trail+'['+str(i)+']')
for name in ['TURN_LEDGER.json','PAUSE_GAME.json','DECK_USED.json','SUMMARY.json','TURN_EVIDENCE.json','FILMED_DECK_SNAPSHOT.json']:
    refs(read(name),name)
check([x['turn_number'] for x in L['turns']]==list(range(1,9)),'actual turn rows 1 to 8 differ')
check(G['turn_count']==R['turn_count']==8,'turn count differs from inspected result')
check(G['final_points']==R['final_points']=={'owner':0,'opponent':3},'summary result differs')
check(len(G['opening']['cards_left_to_right'])==G['opening']['recorded_card_count']==5,'original opening five differs')
check(len(D['filmed_cards_in_order'])==20,'filmed QR deck lacks twenty semantic slots')
check(sum(x['name']=='Darkrai ex' for x in D['filmed_cards_in_order'])==1,'Darkrai revision count differs')
check(sum(x['name']=='Cyrus' for x in D['filmed_cards_in_order'])==1,'Cyrus revision count differs')
for t in L['turns']:
    n=t['turn_number'];h=t['hand_at_start']
    check(len(h['cards_left_to_right'])==h['count'],f'turn {n} start slot count differs')
    if t['who_played']=='owner':
        check(t['owner_hand_end']['count']==len(t['owner_hand_end']['cards_left_to_right']),f'turn {n} end hand count differs')
    for bname in ['board_at_start','board_after']:
        b=t[bname];check(b.get('stadium') is not None,f'turn {n} unexplained Stadium null')
        check(bool(b.get('stadium_basis')),f'turn {n} Stadium basis missing')
        for side in ['owner','opponent']:
            state=b[side];check([x['bench_position'] for x in state['bench_in_position_order']]==[1,2,3],f'turn {n} Bench positions differ')
            for m in [state['active']]+state['bench_in_position_order']:
                if m['name']=='none':check(bool(m['status']),f'turn {n} empty slot basis missing');continue
                check(m['tool'] is not None and bool(m['tool_basis']),f'turn {n} Tool absence unexplained')
                check(m['attached_energy']['total']==sum(m['attached_energy']['by_type'].values()),f'turn {n} attached Energy totals differ')
                check(m['damage']==m['hp_max']-m['hp_now'],f'turn {n} HP/damage arithmetic differs')
            z=state['energy_zone']['this_turn']
            check((z['count']==0 and z['type']=='none' and not z['available']) or (z['count']==1 and z['type'] in ['Darkness','Fire'] and z['available']),f'turn {n} Energy Zone typing differs')
for n in [3,7]:check(L['turns'][n-1]['board_at_start']['owner']['energy_zone']['this_turn']['count']==0,f'turn {n} selected absent Energy changed')
check([L['turns'][n-1]['opponent_hand_at_owner_turn_start']['count'] for n in [1,3,5,7]]==[3,4,3,3],'native owner-start exposed-back counts differ')
for cap in E['owner_turn_captures']:
    turn=L['turns'][cap['turn_number']-1]
    check(len(cap['candidate_evidence_ids'])==3,'draw offset candidates missing')
    for expected,key in zip([1,3,6],cap['candidate_evidence_ids']):check(abs(frames[key]['offset_after_draw_seconds']-expected)<=.25,'draw relative candidate outside approximate target')
    for key in cap['selected_preplay_evidence_ids']:
        f=frames[key];check(f['selected_for_start_hand'] and f['before_first_play'] and f['unzoomed'],'selected preplay suitability differs')
        check(f['requested_source_seconds']<=turn['timing']['first_voluntary_move_seconds'],'selected preplay after commit')
hashes={}
for f in E['frames']:
    p=P/f['full_frame_path'];check(p.is_relative_to(P),'frame outside own packet')
    check(float(p.stem[1:])==f['requested_source_seconds'],'frame alias does not match actual retained filename request')
    hashes[f['full_frame_path']]=sha(p)
    for kind in ['bottom_crop','top_crop']:hashes[f[kind]['path']]=sha(P/f[kind]['path'])
source_path=Path(S.get('source_path_at_review',S.get('sourcePath',S.get('source_path',''))))
source_hash=None
if source_path.is_file():
    source_hash=sha(source_path);check(source_hash==S['sha256'],'current source bytes differ from frozen SOURCE hash')
else:issues.append('source path missing for frozen-byte verification')
for name in ['SOURCE.json','REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json','QR_DECODE.json','FILMED_DECK_SNAPSHOT.json','WORKER_CHECKS.json']:hashes[name]=sha(P/name)
receipt=dict(performed_at_utc=datetime.now(timezone.utc).isoformat(),source_video=S['video_basename'],source_sha256=S['sha256'],recomputed_source_sha256=source_hash,structural_pass=not issues,issues=issues,base_validation=base_receipt,turn_rows=8,native_evidence_frames=len(frames),owner_turn_numbers=[1,3,5,7],owner_end_hand_counts=[3,4,5,5],opponent_selected_fan_counts=[3,4,3,3],all_json_reference_arrays_checked=True,native_filename_timestamp_aliases_checked=True,typed_energy_HP_tools_and_stadium_checked=True,draw_relative_candidates_checked=True,sha256_by_packet_path=hashes,visual_acceptance=False,independent_acceptance=False,limit='Structure, source-byte and consistency checks do not independently establish semantic visual acceptance.')
(P/'VALIDATION_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:receipt[k] for k in ['structural_pass','issues','turn_rows','native_evidence_frames','recomputed_source_sha256','visual_acceptance']},indent=2))
raise SystemExit(1 if issues else 0)
