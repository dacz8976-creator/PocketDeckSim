"""One-time root correction of frozen 020518 timestamp and capture findings."""
import hashlib,json,shutil,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
B=Path(__file__).resolve().parent;P=B/'20261006_020518000_iOS'
r=json.loads((P/'independent_sol/CHECK_RESULT_REJECTED_R1_R2.json').read_text(encoding='utf-8'))
backup=P/'original_before_R1_R2';assert not backup.exists();backup.mkdir()
for n,h in r['checked_input_sha256'].items():
    assert hashlib.sha256((P/n).read_bytes()).hexdigest()==h,n
    shutil.copy2(P/n,backup/n)
def read(n):return json.loads((P/n).read_text(encoding='utf-8'))
def save(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
l=read('TURN_LEDGER.json')
for t in l['turns']:
    for play in t['plays_in_order']:
        play['timestamp_role']='Source-local reference anchor; may precede input or presentation, not an exact consuming input.'
        play['input_and_resolution_distinction']='Cited native frames bound selection, public presentation and resolution separately. Reference timestamp alone does not establish first input; exact touch and remote tap are unknown unless specifically bounded.'
        play['basis']='Public card, Energy, target or resolved-state changes in the cited source interval; ordered effects are separate from exact input timing.'
        if play.get('observed_actor')=='opponent':play['limit_reason']='Remote input/touch is unrecorded; timestamp is a public reference anchor, with presentation/resolution separately bounded where shown.'
changes=[(2,1,[72,75],75,'72 current Metal unused; by75 Metal attached to Tinkatink.'),
         (12,1,[376,378],378,'376 Copperajah has2Metal and current Metal unused;378 has3Metal and current empty.'),
         (12,2,[378,380],408.5,'378 pre-May state; May face presented380; hidden draws and returns resolved by408.5. Exact remote consumption unknown.'),
         (13,1,[435.5,440],440,'435.5 hand selection/current Energy available;438.5 held Fighting in target selection;440 third Fighting attached.'),
         (17,1,[570,571.5],573,'570 preattachment; transfer visible571.5;573 settled attached state.')]
for turn,order,window,resolved,basis in changes:
    play=l['turns'][turn-1]['plays_in_order'][order-1]
    play['public_transition_interval_seconds']=window
    play['exact_consuming_input_seconds']=None
    play['resolved_state_observed_seconds']=resolved
    play['transition_basis']=basis
    for sec in window+[resolved]:
        fid='f'+f'{sec:07.2f}'.replace('.','_')
        if fid not in play['evidence_ids']:play['evidence_ids'].append(fid)
l['turns'][11]['plays_in_order'][1]['public_presentation_observed_seconds']=380
l['turns'][11]['plays_in_order'][1]['public_transition_kind']='May presentation, separate from resolved draw/return effect'
for turn,window in [(13,[435.5,440]),(17,[570,571.5])]:
    timing=l['turns'][turn-1]['timing']
    timing['first_move_reference_seconds']=timing['first_voluntary_move_seconds']
    timing['first_voluntary_move_seconds']=None
    timing['first_voluntary_move_window_seconds']=window
    timing['first_move_time_basis']='Public transition bound; original reference anchor does not prove exact consuming input.'
end=l['turns'][4]['owner_hand_end']
end['basis']='Four end-hand cards visible beneath enlarged Active attack/retreat selection overlay; identities checked against named reveals/removals.'
end['limit_reason']='161.5 is an enlarged Active overlay, not an unzoomed board; retained fan identities remain readable.'
save('TURN_LEDGER.json',l)
e=read('TURN_EVIDENCE.json');frames={f['requested_source_seconds']:f for f in e['frames']}
for sec in [95.5,97.5,199.5,488.5,491.5,576.5]:frames[sec]['unzoomed']=True
frames[161.5]['unzoomed']=False
texts={
100.5:'Coin resolution still underway after Ice Pop heal; Item discard is not yet established in this frame. Not a preplay hand.',
161.5:'Enlarged Active Sandslash attack/retreat selection overlay after Energy attachment; four end-hand identities readable below, not an intact unzoomed board.',
199.5:'Normal-scale board during Ice Pop resolution after consumption; no enlarged-card zoom. Hand has already changed.',
435.5:'Normal-scale board and selected hand card; current Fighting remains available. Energy target selection is not yet shown.',
438.5:'Normal-scale board with held Fighting and glowing target selection; Energy not yet attached. Notification obscures top area.'}
for sec,txt in texts.items():
    frames[sec]['observation']=txt
    frames[sec]['suitability_or_limit']='Inspected candidate: '+txt
frames[435.5]['before_first_play']=None
frames[435.5]['suitability_or_limit']+=' Exact consuming input not established here; original intact preplay hand selected separately at433.'
save('TURN_EVIDENCE.json',e)
save('ROOT_CORRECTIONS_R1_R2.json',{'repaired_utc':datetime.now(timezone.utc).isoformat(),'frozen_rejection':'independent_sol/CHECK_RESULT_REJECTED_R1_R2.json','R1':'Timestamp reference qualifiers and five bounded transitions; T13/T17 first-action exact times null with bounded windows. Verified order unchanged.','R2':'Independent zoom flags, coin/target descriptions and overlaid end-hand qualification corrected. Late candidates remain unselected.','independent_recheck_required':True})
(P/'CORRECTION_LEDGER.md').write_text('# Independent corrections\n\nAll frozen inputs preserved in original_before_R1_R2. Root qualified input versus public-reference timing, corrected native candidate zoom and phase descriptions, and kept the ordered public results. A separate narrow recheck must accept current hashes before registration.\n',encoding='utf-8')
result=subprocess.run([sys.executable,str(B/'validate_packet.py'),str(P)],capture_output=True,text=True,encoding='utf-8',check=True)
structure=json.loads(result.stdout);assert structure['structural_pass'];save('ROOT_REPAIR_STRUCTURE_CHECK.json',structure)
print('020518 R1/R2 repaired; independent recheck required')
