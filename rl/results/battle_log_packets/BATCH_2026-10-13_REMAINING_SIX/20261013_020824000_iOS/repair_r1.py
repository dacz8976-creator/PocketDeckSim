import json,hashlib,datetime
from pathlib import Path
p=Path(__file__).resolve().parent
names=['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
old=p/'independent_sol/rejected_original'
rejected=json.loads((old/'REVIEW_PACKET_HASHES.json').read_text(encoding='utf-8'))
for n,h in rejected['files'].items():
 assert hashlib.sha256((old/n).read_bytes()).hexdigest()==h, 'Preserved rejected bytes differ: '+n
 assert hashlib.sha256((p/n).read_bytes()).hexdigest()==h, 'Current packet has changed: '+n
def read(n):return json.loads((p/n).read_text(encoding='utf-8'))
def save(n,d):(p/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ledger=read('TURN_LEDGER.json');t=next(x for x in ledger['turns'] if x['turn_number']==3)
t['timing']['first_voluntary_move_seconds']=127.3
t['timing']['actual_first_play_seconds']=127.3
t['timing']['actual_first_play_time_basis']='Confirmed placed by retained 127.30s; exact commit lies after inspection at125.30s and at/before127.30s, not measured to exact frame.'
t['timing']['actual_first_play_window_seconds']=[125.3,127.3]
t['inspections_in_order']=[dict(order=1,kind='inspection_selection',card_name='Glimmora',source_video=t['source_video'],timestamp_seconds=125.3,approximate_selection_start_seconds=125.1,evidence_ids=['N0125_30'],hand_count=6,result='Glimmora remains in hand; no completed evolution or card removal at this frame',counts_as_numbered_play=False)]
first=t['plays_in_order'][0]
first['timestamp_seconds']=127.3
first['evidence_ids']=['N0127_30']
first['details']='Complete first play: evolve Active Glimmet into Glimmora, placed by127.30s after inspection125.30s; preserve40 damage, HP becomes50.'
first['hand_count_after']=5
first['timing_qualification']='125.30s is inspection with six cards. Evolution commit is bracketed (125.30,127.30], with placement confirmed at127.30s.'
t['evidence_ids']=list(dict.fromkeys(t['evidence_ids']+['N0125_30','N0127_30']))
save('TURN_LEDGER.json',ledger)
ev=read('TURN_EVIDENCE.json')
for f in ev['frames']:
 if f['requested_source_seconds']==125.3:
  f['role']='draw_timed_candidate; inspection_selection'
  f['before_first_play']=True;f['unzoomed']=False
  f['observation']='Glimmora inspection/selection overlay; six cards remain in hand. Evolution not committed in this frame.'
  f['suitability_or_limit']='Before actual completed first play, but inspection zoom makes it unsuitable as selected pre-play hand. Use124.60s.'
 if f['requested_source_seconds']==127.3:
  f['role']='draw_timed_candidate; completed_first_evolution_anchor'
  f['before_first_play']=False;f['unzoomed']=False
  f['observation']='Glimmora placed on Active in evolution animation; five hand cards remain. First evolution is committed by this frame.'
  f['suitability_or_limit']='After completed first play; retained placement anchor, not start-hand selection.'
ev['scheduled_capture_limits']=[x.replace('fast turns3,5,7,13','fast turns5,7,13') for x in ev['scheduled_capture_limits']]
ev['scheduled_capture_limits'].append('Turn3 +1 candidate125.30s is inspection with six hand cards; +3 candidate127.30s confirms placed evolution and five cards. Actual commit bracketed after125.30 and by127.30; pre-play hand stays124.60s.')
save('TURN_EVIDENCE.json',ev)
coverage=(p/'COVERAGE.md').read_text(encoding='utf-8').replace('first evolution 125.3s','inspection/selection 125.30s with six cards, completed first evolution placed by127.30s with five cards (commit bracketed after125.30s and by127.30s)')
(p/'COVERAGE.md').write_text(coverage,encoding='utf-8')
review=(p/'REVIEW.md').read_text(encoding='utf-8')
review=review.replace('Evolve Active Glimmet into Glimmora; preserve 40 damage, HP becomes50','Complete first play: evolve Active Glimmet into Glimmora, placed by127.30s after inspection125.30s; preserve40 damage, HP becomes50')
review=review.replace('Turn 3 normal Pawniard; full six-card pre-play 124.60s and two-card ending 144.20s.','Turn 3 normal Pawniard; full six-card pre-play124.60s. Glimmora inspection/selection125.30s retains all six cards and is separate from numbered play1. Completed evolution is placed by127.30s with five hand cards; its commit is bracketed after125.30s and by127.30s. Ending144.20s has two cards.')
(p/'REVIEW.md').write_text(review,encoding='utf-8')
hashes={n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in names}
freeze=read('REVIEW_PACKET_HASHES.json');freeze['files']=hashes;freeze['revision']='R1 inspection versus completed evolution timing';freeze['frozen_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save('REVIEW_PACKET_HASHES.json',freeze)
save('R1_REPAIR_RECEIPT.json',dict(repair_id='R1',source_video=freeze['source_video'],source_sha256=freeze['source_sha256'],preserved_rejected_packet='independent_sol/rejected_original',rejected_sha256=rejected['files'],revised_sha256=hashes,changed_files=[n for n in names if rejected['files'][n]!=hashes[n]],scope='Separate125.30s inspection from first completed evolution placed by127.30s; no new decoding; all other material claims retained.',ready_for_narrow_independent_recheck=True))
print(json.dumps(dict(changed_files=[n for n in names if rejected['files'][n]!=hashes[n]],all_eight_refrozen=True),indent=2))
