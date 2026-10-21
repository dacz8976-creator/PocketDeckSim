from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
P=Path(__file__).resolve().parent.parent;O=P/'independent_sol';OLD=P/'original_before_R1_R4'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
frozen=read(O/'FROZEN_INPUT_SHA256.json'); prior=read(O/'CHECK_RESULT.rejected_R1_R4.json')
current={n:sha(P/n) for n in frozen};backups={n:sha(OLD/n) for n in frozen};assert backups==frozen==prior['checked_input_sha256']
assert sha(O/'CHECK_RESULT.json')==sha(O/'CHECK_RESULT.rejected_R1_R4.json')
l=read(P/'TURN_LEDGER.json');old=read(OLD/'TURN_LEDGER.json');e=read(P/'TURN_EVIDENCE.json');olde=read(OLD/'TURN_EVIDENCE.json')
checks={}
d=l['turns'][5]['draws_and_searches'][0];checks['R1']=d['hand_count_before']==4 and d['hand_count_after']==5 and d['evidence_ids']==['F_0203_00','F_0205_00'] and d['cards_in_reveal_order']==old['turns'][5]['draws_and_searches'][0]['cards_in_reveal_order'] and l['turns'][5]['plays_in_order']==old['turns'][5]['plays_in_order']
absent=[];needle=[];empty=[]
for t,ot in zip(l['turns'],old['turns']):
 for bn in ['board_at_start','board_after']:
  b=t[bn];ob=ot[bn]
  if ob['stadium'] is None:assert b['stadium']=='none' and b['stadium_status']=='observed_absent';absent.append(f'turn{t["turn_number"]}.{bn}.stadium')
  for side in ['owner','opponent']:
   mons=[b[side]['active']]+b[side]['bench_in_position_order'];omons=[ob[side]['active']]+ob[side]['bench_in_position_order']
   for i,(m,om) in enumerate(zip(mons,omons)):
    if om.get('name') and om.get('tool') is None:
     assert m['tool']=='none' and m['tool_status']=='observed_absent' and m['tool_basis'];absent.append(f'turn{t["turn_number"]}.{bn}.{side}.mon{i}')
    elif om.get('tool')=='Deceptive Needle':assert m['tool']==om['tool'];needle.append(f'turn{t["turn_number"]}.{bn}.{side}.mon{i}')
    elif om.get('status')=='visibly_empty':
     copy={k:v for k,v in m.items() if k!='evidence_ids'};ocopy={k:v for k,v in om.items() if k!='evidence_ids'};assert copy==ocopy;empty.append(f'turn{t["turn_number"]}.{bn}.{side}.mon{i}')
checks['R2']=True
mapping=prior['required_repairs'][2]['supported_unzoomed_hand_spread_by_requested_seconds'];ef={f['requested_source_seconds']:f for f in e['frames']};oef={f['requested_source_seconds']:f for f in olde['frames']}
for tm,flags in mapping.items():
 f=ef[float(tm)];of=oef[float(tm)]
 assert f['unzoomed']==flags['unzoomed'] and f['hand_spread']==flags['hand_spread']
 assert f['before_first_play']==of['before_first_play'] and f['selected_for_start_hand']==of['selected_for_start_hand']
 for k in ['full_frame_path','native_dimensions','bottom_crop','top_crop','source_video','source_sha256','requested_source_seconds']:assert f[k]==of[k]
h=l['turns'][4]['owner_hand_end'];oh=old['turns'][4]['owner_hand_end'];assert h['cards_left_to_right']==oh['cards_left_to_right'] and h['count']==2 and 'zoom' in h['limit_reason']
checks['R3']=True
b=l['turns'][9]['board_after'];assert b['timestamp_seconds']==389 and b['turn_number_displayed'] is None and b['turn_number_limit'];assert 'Composite' in b['phase'] and '392' in b['basis']
assert b['owner']['active']['status']=='visibly_empty' and b['owner']['active']['evidence_ids']==['F_0389_00']
assert b['owner']['points']==2 and b['owner']['points_observed_seconds']==389 and b['owner']['points_evidence_ids']==['F_0389_00']
assert b['opponent']['points']==3 and b['opponent']['points_before_award']==1 and b['opponent']['points_before_award_seconds']==389 and b['opponent']['points_observed_seconds']==392 and b['opponent']['points_evidence_ids']==['F_0392_00']
for side in ['owner','opponent']:
 for m in [b[side]['active']]+b[side]['bench_in_position_order']:assert m['evidence_ids']==['F_0389_00']
 assert b[side]['energy_zone']['evidence_ids']==['F_0389_00']
assert b['owner']['bench_in_position_order'][1]['hp_now']==170 and b['owner']['bench_in_position_order'][1]['attached_energy']=={'total':1,'by_type':{'Darkness':1}}
assert b['opponent']['active']['hp_now']==60 and b['opponent']['active']['hp_max']==130 and b['opponent']['active']['attached_energy']=={'total':2,'by_type':{'Psychic':2}}
assert b['opponent']['bench_in_position_order'][2]['hp_now']==10 and b['opponent']['bench_in_position_order'][2]['attached_energy']=={'total':0,'by_type':{}} and b['stadium']=='Peculiar Plaza'
event=l['turns'][9]['automatic_events_in_order'][1];assert event['first_clear_empty_active_seconds']==389 and 'F_0389_00' in event['evidence_ids']
checks['R4']=True;assert all(checks.values())
assert sha(P/'DECK_USED.json')==frozen['DECK_USED.json'];assert len(read(P/'DECK_USED.json')['cards_in_log_order'])==20
supp={}
for rel in ['independent_sol/CHECK_RESULT.rejected_R1_R4.json','independent_sol/FROZEN_INPUT_SHA256.json','independent_sol/VIEWED_EVIDENCE.json','independent_sol/CAPTURE_CHECK.json','independent_sol/QR_RECHECK.json','astra_gap/CHECK_RESULT.json','astra_gap/VIEWED_EVIDENCE.json','qr_intake/QR_DECODE_0001.00.json','qr_intake/t0001.00.png','RECORDING_METADATA.json','ROOT_CORRECTIONS_R1_R4.json','ROOT_REPAIR_STRUCTURE_CHECK.json','ROOT_VIEWED_EVIDENCE.json','turn_evidence/crops/F_0203_00_top.png','turn_evidence/crops/F_0205_00_top.png','turn_evidence/t0196.50.jpg','turn_evidence/t0389.00.jpg','turn_evidence/t0392.00.jpg']:
 supp[rel]=sha(P/rel)
for rel in ['LIVE_DECK_SNAPSHOT.json','NEW_DECK_ENTRIES.json','PAUSE_DECKS_IMPORT.json']:
 if (P.parent/rel).exists():supp['../'+rel]=sha(P.parent/rel)
assert current=={n:sha(P/n) for n in frozen}
r={'schema':'bounded-independent-sol-correction-recheck-v1','reviewer':'/root/independent_183108','review_model':'gpt-6.1-sol','checked_at_utc':datetime.now(timezone.utc).isoformat(),'source_video':read(P/'SOURCE.json')['video_basename'],'source_sha256':read(P/'SOURCE.json')['sha256'],'source_duration_seconds':403.317007,'status':'accepted_after_R1_R4_corrections','independent_acceptance':True,'scope':'Tiny amended-field recheck after prior fresh bounded independent review; not a new whole-source/fulldecode pass. Previous full first-pass coverage and independently checked ordinary/consequential anchors carry forward.','checked_input_sha256':current,'supplemental_checked_input_sha256':supp,'original_nine_backup_sha256':backups,'backups_match_frozen_rejected_inputs':True,'rejected_receipt_preserved_byte_identical':True,'stable_current_inputs':True,'repair_checks':checks,'details':{'R1':'Native203/205 top crops revisited:4backs→5; hidden identity and entire buffered action/unknown order unchanged.','R2':{'observed_absence_locations_corrected':len(absent),'Needle_instances_preserved':len(needle),'empty_slots_semantics_preserved':len(empty)},'R3':'All13 specified capture flag mappings match, preplay rejection flags/selections and native references preserved.196.5 enlarged attack overlay revisited;Copycat/Scolipede ending2 unchanged and accurately limited.','R4':'Clean389 native frame revisited:owner Activeempty,centerMega170/Darkness1,opponentHoundstone60/Psychic2,rightMeloetta10,noEnergy,Plaza,owner2/opponent1. Packet explicitly separates392 awardedopponent3, with proper per-field references;removal animation388 andfirstclean389 separated.'},'native_evidence_revisited_seconds':[203,205,196.5,389],'remaining_required_repairs':[],'accepted_outcome':{'classification':'human_event','opponent':'ぐー、','owner_outcome':'loss','owner_points':2,'opponent_points':3,'turns':10,'damage_dealt':470},'capture_status':'complete_with_recording_limits','preserved_recording_limits':['T6 buffered internal order and exact remote inputs unknown.','Opponent hidden card identities unknown.','Full discard piles not opened.','PTS/exacttouch timestamps not measured.','Exact20 filmed QR definition is prepared;live saved deck/game verification remains lead-only.'],'whole_source_second_pass_claim':False,'media_rehashed_or_decoded':False,'canonical_files_modified':False,'external_or_registration_or_media_changes':False,'receipt_written':'independent_sol/CORRECTION_RECHECK.json'}
(O/'CORRECTION_RECHECK.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':r['status'],'checks':checks,'backups_match':True,'checked_input_sha256':current,'known_none_corrected':len(absent),'needle_preserved':len(needle)},indent=2))
