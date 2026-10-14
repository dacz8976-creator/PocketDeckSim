import json,hashlib,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
p=Path(__file__).resolve().parent
def read(n):return json.loads((p/n).read_text(encoding='utf-8'))
def save(n,v):(p/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
old=read('REVIEW_PACKET_HASHES.json')
ledger=read('TURN_LEDGER.json');t=ledger['turns'][7];oldacts=t['plays_in_order'];t['plays_in_order']=[oldacts[1],oldacts[2],oldacts[0],oldacts[3],oldacts[4]]
for i,a in enumerate(t['plays_in_order'],1):a['order']=i
t['plays_in_order'][0].update(timestamp_seconds=177,evidence_ids=['N0177_00'],basis='Arena already installed by native177; exact placement instant is approximate')
t['plays_in_order'][1].update(timestamp_seconds=179,evidence_ids=['O00090','O00092'],basis='Qualified coarse reveal at nominal179 and healing/recovery by nominal183; generated Fighting remains available')
t['plays_in_order'][2].update(timestamp_seconds=185,evidence_ids=['O00092','N0185_00'],basis='Between qualified locating183 with three Fighting and orb available, and native185 with four Fighting and orb consumed; timestamp is completed-state anchor',commit_window_seconds=[183,185])
t['timing']['first_voluntary_move_seconds']=177;t['timing']['first_move_timing_basis']='Arena is already installed by native177; this is a completed-state anchor, not a measured placement instant'
t['turn_evidence_ids']=['N0177_00','O00090','O00092','N0185_00','N0190_50','N0207_00']
t['limits'].append('T8 repaired against retained source: Arena, Center Lady, Fighting attachment, attack, forced owner replacement. Attachment occurs after healing between nominal183 and native185; no173 attachment assertion remains.')
save('TURN_LEDGER.json',ledger)
ev=read('TURN_EVIDENCE.json');ev['ordered_action_evidence_sets']=ev.get('ordered_action_evidence_sets',[])+[{'turn_number':8,'source_video':ledger['sources'][0]['video_basename'],'source_sha256':ledger['source_sha256'],'actions':[{'play_order':1,'kind':'card_play','card_name':'Arena of Antiquity','evidence_ids':['N0177_00'],'timing_basis':'installed by native177 while Mega150HP/3F and orb remains available'},{'play_order':2,'kind':'card_play','card_name':'Pokémon Center Lady','evidence_ids':['O00090','O00092'],'timing_basis':'qualified nominal179 reveal then183 healed180HP/3F/orb available'},{'play_order':3,'kind':'energy_attachment','target':'Active Mega Lucario ex','evidence_ids':['O00092','N0185_00'],'commit_window_seconds':[183,185],'timing_basis':'3F/orb available before,4F/orb consumed by native185; no exact measured instant'},{'play_order':4,'kind':'attack','card_name':'Mega Lucario ex','evidence_ids':['O00094','N0190_50'],'timing_basis':'Fighting Pulse, subsequent Glimmora knockout and ability'},{'play_order':5,'kind':'replacement_choice','target':'right Glimmora','evidence_ids':['N0207_00'],'timing_basis':'forced promotion completed before owner turn9'}]}]
for f in ev['frames']:
 if f['evidence_id']=='N0177_00':f['action_reference']={'turn_number':8,'play_order':1,'role':'Arena installed before healing and attachment; not attachment evidence'}
 if f['evidence_id']=='N0185_00':f['action_reference']={'turn_number':8,'play_order':3,'role':'Fighting attachment completed after healing'}
for f in ev['overview_frames']:
 if f['evidence_id']=='O00090':f['action_reference']={'turn_number':8,'play_order':2,'role':'Center Lady reveal, before attachment'}
 if f['evidence_id']=='O00092':f['action_reference']={'turn_number':8,'play_order':2,'role':'Healing completed180HP/3F, current Fighting remains available'}
save('TURN_EVIDENCE.json',ev)
md=(p/'REVIEW.md').read_text();lines=md.splitlines()
for i,line in enumerate(lines):
 if line.startswith('| 8 (opponent) |'):
  lines[i]='| 8 (opponent) | By 177 to 207 s | Draw: hidden opponent draw. 1. Play Arena of Antiquity, already installed by native 177 s with Mega Lucario ex at 150 HP, three Fighting Energy and current orb available. 2. Play Pokémon Center Lady, revealed at qualified nominal 179 s; heal to 180 HP and cure poison by nominal 183 s, still three Fighting and orb available. 3. Attach one Fighting to Active Mega Lucario ex between nominal 183 and native 185 s; native 185 shows four Fighting and orb consumed. 4. Fighting Pulse knocks out left Glimmora; Shattering Crystal Tails grants opponent point 2. 5. Owner forcibly promotes right Glimmora. See TURN_LEDGER turn 8 and N0177_00, O00090, O00092, N0185_00, N0190_50, N0207_00. | 2 |'
md='\n'.join(lines)+'\n';md+='\nT8 source correction: Arena and Pokémon Center Lady precede the Fighting attachment. The prior 173 s attachment-first account was rejected and its original eight files are preserved in independent_sol/rejected_frozen_20261013_153653. The revised sequence uses the retained before/after Energy evidence and preserves qualified coarse timing.\n';(p/'REVIEW.md').write_text(md,encoding='utf-8')
validator=p.parent.parent/'BATCH_2026-10-11_NEW_PAUSE_GAMES/validate_packet.py';r=subprocess.run([sys.executable,'-X','utf8',str(validator),str(p)],capture_output=True,text=True,encoding='utf-8');assert r.returncode==0,r.stdout+r.stderr;save('STRUCTURAL_VALIDATION.json',json.loads(r.stdout))
eight=['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']; hashes={n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in eight}
save('T8_ORDER_REPAIR_RECEIPT.json',{'source_video':old['source_video'],'source_sha256':old['source_sha256'],'repaired_utc':datetime.now(timezone.utc).isoformat(),'required_repair':'T8_ACTION_ORDER','before_input_sha256':old['review_components'],'after_input_sha256':hashes,'affected_files':['REVIEW.md','TURN_LEDGER.json','TURN_EVIDENCE.json'],'originals_preserved':'independent_sol/rejected_frozen_20261013_153653','source_anchors':['N0177_00','O00090','O00092','N0185_00'],'result':'Arena -> Center Lady -> Fighting attachment -> attack -> forced owner replacement','tool_observation':'Unchanged null name; no owner hypothesis converted to filmed identity','structural_pass':True,'independent_recheck':'pending'})
save('REVIEW_PACKET_HASHES.json',{'source_video':old['source_video'],'source_sha256':old['source_sha256'],'frozen_utc':datetime.now(timezone.utc).isoformat(),'review_components':hashes,'scope':'Eight actual primary components refrozen after T8 action-order correction; separate independent recheck required','repair_receipt':'T8_ORDER_REPAIR_RECEIPT.json','visual_acceptance':False})
print(r.stdout);print('Repaired T8, refroze all eight, edits stopped.')
