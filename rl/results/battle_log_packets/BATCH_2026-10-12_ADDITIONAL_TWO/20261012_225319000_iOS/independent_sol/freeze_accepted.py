from pathlib import Path
import json,hashlib,datetime,subprocess,sys
p=Path(__file__).resolve().parent.parent;out=p/'independent_sol'
names=['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
manifest=json.loads((p/'REVIEW_PACKET_HASHES.json').read_text(encoding='utf-8-sig'))
data={n:(p/n).read_bytes() for n in names};hashes={n:hashlib.sha256(b).hexdigest() for n,b in data.items()}
assert hashes==manifest['files'],'Files differ from final primary freeze'
docs={n:json.loads(b.decode('utf-8-sig')) for n,b in data.items() if n.endswith('.json')}
turns=docs['TURN_LEDGER.json']['turns'];assert [t['turn_number'] for t in turns]==list(range(1,10))
assert len(docs['PAUSE_GAME.json']['opening']['cards_left_to_right'])==5
assert [x['name'] for x in docs['PAUSE_GAME.json']['opening']['cards_left_to_right']]==['Rare Candy','Pawniard','Ilima','Professor’s Research','Heavy Helmet']
assert len(docs['DECK_USED.json']['cards_in_log_order'])==20
snapshot=json.loads((p.parent/'LIVE_DECK_SNAPSHOT.json').read_text(encoding='utf-8-sig'))
assert docs['DECK_USED.json']['cards_in_log_order']==snapshot['cards_in_log_order']
assert json.loads((out/'QR_CHECK.json').read_text())['exact_payload_match']
t6=turns[5];assert [x['kind'] for x in t6['plays_in_order']]==['ability','energy_attachment','retreat','end_turn']
assert t6['plays_in_order'][1]['energy']['destination']=='Pawniard'
assert t6['plays_in_order'][2]['energy']['retreat_payment_by_type']=={'Darkness':1}
assert t6['board_after']['owner']['energy_zone']['this_turn']['count']==0
assert t6['board_after']['turn_number_displayed']==7
assert t6['timing']['before_end_action_seconds']==339.5
assert [t['owner_hand_end']['count'] for t in turns if t['who_played']=='owner']==[4,1,2,2]
for t in turns:
 for bname in ['board_at_start','board_after']:
  for side in ['owner','opponent']:
   preview=t[bname][side]['energy_zone']['next'];assert preview['count'] is None and preview['available'] is None
assert docs['SUMMARY.json']['outcome']=='owner defeat by concession'
assert docs['SUMMARY.json']['points']=={'owner':0,'opponent':2}
validator=p.parents[1]/'BATCH_2026-10-11_NEW_PAUSE_GAMES/validate_packet.py'
r=subprocess.run([sys.executable,'-X','utf8',str(validator),str(p)],capture_output=True,text=True,check=True)
struct=json.loads(r.stdout);assert struct['structural_pass']
(out/'STRUCTURAL_CHECK.json').write_text(json.dumps(struct,indent=2),encoding='utf-8')
assert all(hashlib.sha256((p/n).read_bytes()).hexdigest()==h for n,h in hashes.items()),'Primary files changed during checking'
source=json.loads((p/'SOURCE.json').read_text(encoding='utf-8-sig'))
receipt={'status':'accepted_with_recording_limits','accepted':True,'semantic_acceptance':True,'checker':'/root/check_later_225319','model':'gpt-6.1-sol','checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_video':source['video_basename'],'source_sha256':source['sha256'],'source_bytes':source['bytes'],'duration_seconds':source['duration_seconds'],'primary_frozen_utc':manifest['frozen_utc'],'accepted_input_sha256':hashes,'scope':'Source-bound bounded independent checks of opening, source/turn coverage, terminal, ordinary owner turns2 and6, additional Copycat turn4, draw/search reveal order, hand arithmetic, boards and both Energy Zones; final eight-file semantic reconciliation. Primary full battle account accepted.','ordinary_owner_turns_checked':[2,6],'additional_turn_checks':[4],'source_evidence':['independent_sol/QR_CHECK.json','independent_sol/SOURCE_CHECK_NOTES.md','independent_sol/T6_CORRECTION.md','independent_sol/FINAL_RECONCILIATION.md'],'preserved_rejection':'independent_sol/CHECK_RESULT.rejected_t6.json','structural_validation':'independent_sol/STRUCTURAL_CHECK.json','outcome':'owner defeat by explicit concession','points':{'owner':0,'opponent':2},'turns':9,'unresolved_material_findings':[],'recording_limits':['Opponent hidden draw/search identities remain unknown.','Opponent fan overlap supports ranges3-4 atT2 and5-6 atT8.','No opened discard-pile views are recorded.','Next Energy icons establish type previews, not numeric future availability.','Requested timestamps and animation boundaries retained; actual frame PTS unmeasured.','Exact semantic20-card deck matches QR/live snapshot; artwork and rarity unverified.'],'independent_continuous_full_pass':False,'shared_writes_performed':False,'source_moved':False,'external_changes':False}
(out/'CHECK_RESULT.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps(receipt,indent=2))
