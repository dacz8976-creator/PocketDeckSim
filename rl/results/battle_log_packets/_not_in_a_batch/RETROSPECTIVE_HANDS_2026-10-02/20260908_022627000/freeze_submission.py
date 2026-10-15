import json,hashlib,datetime
from pathlib import Path
B=Path(__file__).parent
def read(n):return json.loads((B/n).read_text(encoding='utf-8-sig'))
def save(n,x):(B/n).write_text(json.dumps(x,indent=2),encoding='utf-8')
e=read('TURN_EVIDENCE.json')
zoom={'R0041.00','F0098.00','F0166.00','F0348.00','F0591.00'}
nativeplain={'F0043.00','F0046.00','R0049.00','F0097.00','F0100.00','F0271.00','F0273.00','F0276.00','F0350.00','F0352.00','F0355.00','F0411.00','F0413.00','F0416.00','F0500.00','F0501.00','F0503.00','F0506.00','R0509.00','F0590.00','F0593.00','F0596.00','F0673.00','F0675.00','F0678.00'}
for f in e['frames']:
 if f['evidence_id'] in zoom:f['unzoomed']=False;f['hand_spread']='Enlarged incoming card or selected card overlays ordinary fan.'
 elif f['evidence_id'] in nativeplain:f['unzoomed']=True;f['hand_spread']='Native ordinary fan with overlap; named positions resolved from same-source hand and transaction evidence.'
 else:f['presentation_limit']='This frame is an action/board/reference anchor; settled-hand suitability is not required or certified for every retained frame.'
save('TURN_EVIDENCE.json',e)
m=read('METRICS.json');m['source_work_finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();m['source_work_wall_seconds']=round((datetime.datetime.fromisoformat(m['source_work_finished_utc'])-datetime.datetime.fromisoformat(m['registered_utc'])).total_seconds(),2);save('METRICS.json',m)
files=['ASSIGNMENT.json','PAUSE_GAME.json','TURN_LEDGER.json','HAND_SUPPLEMENT.json','SOURCE_REFERENCE.json','TURN_EVIDENCE.json','REVIEW_SUPPLEMENT.md','UNCERTAINTIES.json','DECK_USED.json','METRICS.json','MODE_QUESTION.json','ASTRA_QUESTIONS.json','LOCATOR_SCAN.json','SOURCE_VERIFICATION.json','PACKET_VALIDATION.json']
submission={'status':'provisional_source_packet_frozen_for_independent_checks','frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'capture_status':'complete_with_recording_limits','independent_acceptance_status':'pending_separate_sol_and_bounded_astra_checks','turns':18,'owner_hands':9,'new_native_frames':72,'reused_native_frames':52,'locator_samples':721,'accepted_owner_loss':'preserved','old_packet':'untouched','files':[{'path':str((B/n).resolve()),'bytes':(B/n).stat().st_size,'sha256':hashlib.sha256((B/n).read_bytes()).hexdigest()} for n in files]}
save('SUBMISSION.json',submission)
print('Frozen provisional source packet, independent acceptance pending')
