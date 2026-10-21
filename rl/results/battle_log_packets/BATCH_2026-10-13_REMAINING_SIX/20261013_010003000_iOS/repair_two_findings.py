import json,hashlib,copy,subprocess
from pathlib import Path
from datetime import datetime,timezone
p=Path(__file__).resolve().parent
def load(n):return json.loads((p/n).read_text(encoding='utf-8-sig'))
def save(n,x):(p/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
src=load('SOURCE.json');v=src['video_basename'];sha=src['sha256']
oldfreeze=load('REVIEW_PACKET_HASHES.json');names=list(oldfreeze['review_components'])
for name,expected in oldfreeze['review_components'].items():
 assert hashlib.sha256((p/name).read_bytes()).hexdigest()==expected,name+' changed before repair'
 assert hashlib.sha256((p/'independent_sol/rejected_inputs'/name).read_bytes()).hexdigest()==expected,name+' rejected original missing'
ledger=load('TURN_LEDGER.json')
search=next(d for d in ledger['turns'][6]['draws_and_searches'] if d['kind']=='search')
search['timestamp_seconds']=286;search['evidence_ids']=['f0286_00']
search['cards_in_reveal_order'][0].update(timestamp_seconds=286,evidence_ids=['f0286_00'],basis='Native286 shows Alolan Grimer as the newly arrived fifth hand card; native284 is still resolving the search and is not arrival evidence')
t=ledger['turns'][10]
t['plays_in_order'].append(dict(order=2,kind='energy_attachment',card_name=None,target='Bench Alolan Muk, position3',energy=dict(type='Darkness',count=1,destination='Bench Alolan Muk',retreat_payment_by_type=None),result='Attached one Darkness from owner Energy Zone to Bench Alolan Muk after Lucky Ice Pop heads. Muk now Darkness1 plus Colorless1, total2; owner current Energy consumed.',prompt_text=None,response=None,nested_events_in_order=[],hand_count_after=5,source_video=v,source_sha256=sha,timestamp_seconds=449.25,evidence_ids=['f0449_00','f0449_25','f0449_50','f0449_75','f0451_00','f0453_00'],basis='Native449 target selection;449.25-449.50 Darkness orb on Muk;449.75 resolution glow;451-453 stable mixed Energy',limit_reason='Inspected attachment window449.00-449.75; exact input onset is not measured. Regigigas menu inspection at450 is separate and no attack resolves.'))
muk=next(m for m in t['board_after']['owner']['bench_in_position_order'] if m['name']=='Alolan Muk')
muk['attached_energy']=dict(total=2,by_type={'Darkness':1,'Colorless':1});muk['evidence_ids']=['f0451_00','f0453_00']
z=t['board_after']['owner']['energy_zone'];z['this_turn']=dict(type='Darkness',count=0,available=False);z['basis']='Owner Darkness is attached to Bench Muk in449.00-449.75 window; native451-453 Zone has no current orb and only Darkness type preview';z['evidence_ids']=['f0449_25','f0451_00','f0453_00']
t['owner_hand_end']['reconciliation']='5 - Lucky Ice Pop + heads return =5; Energy attachment removes no hand card'
save('TURN_LEDGER.json',ledger)
ev=load('TURN_EVIDENCE.json');base=next(f for f in ev['frames'] if f['evidence_id']=='f0449_00')
base['observation']='Owner Energy target-selection view before attachment; Muk has Colorless1 and owner current Darkness is available'
for seconds,eid,obs in [(449.25,'f0449_25','Darkness orb reaches Bench Alolan Muk'),(449.5,'f0449_50','Darkness attachment animation on Bench Muk; owner Zone current Energy consumed'),(449.75,'f0449_75','Attachment resolution glow on Bench Muk before Regigigas menu inspection')]:
 f=copy.deepcopy(base);path=p/'turn_evidence'/f't{seconds:07.2f}.jpg'
 f.update(evidence_id=eid,role='numbered_energy_attachment',requested_source_seconds=seconds,full_frame_path=str(path.relative_to(p)),bottom_crop={},top_crop={},selected_for_start_hand=False,before_first_play=False,unzoomed=True,hand_spread=True,observation=obs,suitability_or_limit='Attachment onset bounded to449.00-449.75; exact frame PTS not measured',image_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
 ev['frames'].append(f)
next(f for f in ev['frames'] if f['evidence_id']=='f0286_00')['observation']='Turn7 Poké Ball search arrival: Alolan Grimer is the fifth hand card'
next(f for f in ev['frames'] if f['evidence_id']=='f0284_00')['observation']='Turn7 search still resolving; owner hand has four cards and Grimer has not arrived'
ev['frames'].sort(key=lambda f:f['requested_source_seconds']);save('TURN_EVIDENCE.json',ev)
text=(p/'REVIEW.md').read_text(encoding='utf-8')
row=next(line for line in text.splitlines() if line.startswith('| 11 |'))
fixed=row.replace('; Automatic:', '; 2. Energy attachment at 449.25 s, within the inspected 449.00-449.75 s window: attached one Darkness to Bench Alolan Muk. Muk ends with Darkness1 and Colorless1, total2; owner current Energy is consumed; [attachment](turn_evidence/t0449.25.jpg), [resolved final board](turn_evidence/t0453.00.jpg); Automatic:')
fixed=fixed.replace('5 - Ice Pop + heads return =5.', '5 - Ice Pop + heads return =5; Energy attachment removes no hand card.')
text=text.replace(row,fixed)
text=text.replace('Atturn11', 'At turn 11').replace('At turn 11 Lucky Ice Pop restores that20 and flips heads.', 'At turn 11 Lucky Ice Pop restores that 20 and flips heads. The owner then attaches one Darkness to Bench Alolan Muk, which already has one Colorless from Giga Turbo. The final board has two Energy on Muk, and the owner current Energy Zone is consumed.')
text=text.replace('At turn11 Lucky Ice Pop restores that20 and flips heads.', 'At turn 11 Lucky Ice Pop restores that 20 and flips heads. The owner then attaches one Darkness to Bench Alolan Muk, which already has one Colorless from Giga Turbo. The final board has two Energy on Muk, and the owner current Energy Zone is consumed.')
text+='\nIndependent repair: Turn 7 Alolan Grimer search arrival is bound to native 286 s, not the still-resolving 284 s view. Turn 11 includes the Darkness attachment after Ice Pop and before the Regigigas inspection. Original rejected eight-component bytes remain in independent_sol/rejected_inputs.\n'
(p/'REVIEW.md').write_text(text,encoding='utf-8')
py=r'C:/Users/dacz8/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';validator=p.parents[1]/'BATCH_2026-10-11_NEW_PAUSE_GAMES/validate_packet.py'
r=subprocess.run([py,'-Xutf8',str(validator),str(p)],capture_output=True,text=True,encoding='utf-8');(p/'STRUCTURAL_VALIDATION.json').write_text(r.stdout,encoding='utf-8');assert r.returncode==0,r.stdout+r.stderr
save('REPAIR_RECEIPT.json',dict(source_video=v,source_sha256=sha,repaired_utc=datetime.now(timezone.utc).isoformat(),scope=['T7_SEARCH_ARRIVAL_REFERENCE','T11_MISSING_ENERGY_ATTACHMENT'],original_rejected_hashes=oldfreeze['review_components'],rejected_originals='independent_sol/rejected_inputs',new_components={n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in names},new_native_frames=['turn_evidence/t0449.25.jpg','turn_evidence/t0449.50.jpg','turn_evidence/t0449.75.jpg'],structural_pass=True,independent_reacceptance_pending=True))
oldfreeze.update(frozen_utc=datetime.now(timezone.utc).isoformat(),review_components={n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in names},repair_receipt='REPAIR_RECEIPT.json',visual_acceptance=False)
oldfreeze['supplement_hashes']['STRUCTURAL_VALIDATION.json']=hashlib.sha256((p/'STRUCTURAL_VALIDATION.json').read_bytes()).hexdigest();oldfreeze['supplement_hashes']['REPAIR_RECEIPT.json']=hashlib.sha256((p/'REPAIR_RECEIPT.json').read_bytes()).hexdigest();save('REVIEW_PACKET_HASHES.json',oldfreeze)
print(r.stdout);print('Two findings repaired and eight current components refrozen; no further edits during narrow recheck.')
