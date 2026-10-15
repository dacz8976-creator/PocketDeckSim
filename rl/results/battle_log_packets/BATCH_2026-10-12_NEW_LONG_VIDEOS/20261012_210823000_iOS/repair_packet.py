from pathlib import Path
import json,hashlib,datetime,re,subprocess
p=Path(__file__).parent
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
names=['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
docs={n:json.loads((p/n).read_text(encoding='utf-8-sig')) for n in names if n.endswith('.json')}
video=docs['SUMMARY.json']['video_basename'];sha=docs['SUMMARY.json']['source_sha256']
def eid(t):return f'native_{t:07.2f}'
def ids(*ts):return [eid(t) for t in ts]
audit={
38:((0,1),(0,1)),50:((0,1),(0,1)),54.5:((0,1),(1,1)),85.5:((0,1),(0,1)),
87:((0,1),(0,1)),114:((0,1),(0,1)),117:((0,1),(0,None)),160:((0,1),(0,1)),
166:((1,None),(0,1)),200:((0,None),(0,None)),206.5:((0,1),(1,None)),220.5:((0,1),(0,1)),
224:((1,1),(0,1)),287:((0,1),(0,1)),292:((0,1),(1,None)),314:((0,1),(0,1)),
316:((1,1),(0,1)),352:((0,1),(0,1)),355.5:((0,1),(0,1)),388:((0,1),(0,1)),
426:((0,1),(0,1)),429:((0,1),(1,1)),432:((0,1),(1,1))}
audit_records=[]
for turn in docs['TURN_LEDGER.json']['turns']:
 for field in ['board_at_start','board_after']:
  b=turn[field];t=b['source_seconds']
  for side,i in [('opponent',0),('owner',1)]:
   current,nxt=audit[t][i]
   limit=None
   if nxt is None:
    limit=('The small next glyph is obscured by the opponent prompt at 166 seconds.' if t==166 else
      'The small next glyph is temporarily absent during this generation or attack phase. Future Energy type, count and availability are not established at this frame.')
   z={'this_turn':{'type':'Darkness' if current else None,'count':current,'available':bool(current),'display_status':'filled_Darkness_orb' if current else 'visible_empty_current_circle'},
      'next':{'type':'Darkness' if nxt else None,'count':nxt,'available':False if nxt else None,'display_status':'visible_Darkness_preview' if nxt else ('obscured_by_prompt' if t==166 else 'temporarily_absent_glyph')},
      'basis':'Direct inspection of large current circle and small next glyph at the stated native frame. No deck configuration or subsequent frame supplies an absent value.',
      'source_video':video,'source_seconds':t,'evidence_ids':ids(t),'limit_reason':limit,'audit_crop_path':f'energy_zone_audit/t{t:07.2f}_{side}.png'}
   if t==166 and side=='opponent':z['basis']+=' The top of the filled current Darkness orb remains readable above the prompt; the next preview is obscured.'
   b[side]['energy_zone']=z
   audit_records.append({'turn_number':turn['turn_number'],'board_field':field,'player':side,**z})
 docs['TURN_LEDGER.json']['turns'][turn['turn_number']-1]=turn
last=docs['TURN_LEDGER.json']['turns'][-1]
last['draws_and_searches']=[{'kind':'normal_draw_failed','caused_by':'Empty owner deck','linked_play_order':None,'cards_in_reveal_order':[],'drawn_card_count':0,'hand_count_before':3,'hand_count_after':3,'returned_or_discarded_cards':[],'source_video':video,'timestamp_seconds':428,'evidence_ids':ids(428,428.5),'basis':'Observed system message: No cards left in deck; unable to draw cards','limit_reason':'No card is drawn, so a successful draw animation end and its candidate offsets do not exist.'}]
last['automatic_events_in_order']=[{'timestamp_seconds':428,'event':'No cards left in deck; unable to draw cards. Owner normal draw fails because the deck is empty; no card enters hand.','basis':'Explicit observed system message','evidence_ids':ids(428,428.5)},
 {'timestamp_seconds':430,'event':'Your opponent conceded. Hons concedes during owner turn 12.','basis':'Explicit observed system message, also independently verified by direct source extraction','evidence_ids':ids(430,430.5,431)},
 {'timestamp_seconds':439,'event':'Victory! versus Hons; Glimmora is Card of the Game.','basis':'Explicit observed result','evidence_ids':ids(439)}]
last['limits']=['Normal draw fails due to the explicitly empty owner deck. No successful draw-end timestamp or +1/+3/+6 offsets are manufactured. The unchanged three-card hand is retained.','No owner voluntary play or End Turn action occurs before the opponent concession. The last clear hand at 432 seconds is the terminal hand, not an inferred owner-ending action.','Neither player opens a discard-pile contents view this turn; only top discard cards and play history are available.']
last['terminal_cause']='opponent_concession';last['terminal_evidence_ids']=ids(430,430.5,431,439)
last['turn_evidence_ids']=sorted(set(last['turn_evidence_ids']+ids(428,428.5,430,430.5,431,439)))
last['board_after']['phase']='last_observed_board_at_terminal_concession_boundary'
docs['TURN_LEDGER.json']['limits'].append('Every starting and ending Energy Zone record was audited at its own native frame after independent rejection. Temporarily absent or obscured next glyphs are null with phase-specific limits.')
docs['UNCERTAINTIES.json']['unresolved']=[u for u in docs['UNCERTAINTIES.json']['unresolved'] if u['id'] not in ['normal_draw_turn_12','terminal_cause']]
docs['UNCERTAINTIES.json']['resolved_by_source']=[{'id':'normal_draw_turn_12','finding':'Explicit empty-deck draw-failure message','evidence_ids':ids(428,428.5)}, {'id':'terminal_cause','finding':'Explicit opponent concession message','evidence_ids':ids(430,430.5,431)}]
docs['UNCERTAINTIES.json']['unresolved'].append({'id':'energy_zone_transient_preview','status':'phase_specific_recording_limit','detail':'Owner next glyphs at 117, 206.5 and 292 seconds are temporarily absent; opponent next glyph at 166 is prompt-obscured; both next glyphs at 200 are absent in the attack animation. Their type, count and availability remain null at those exact frames. Other chosen boundaries were inspected individually.'})
for n in ['SUMMARY.json','PAUSE_GAME.json']:
 docs[n]['terminal_cause']='opponent_concession'
 docs[n]['terminal_cause_basis']='Explicit source message at 430, 430.5 and 431 seconds: Your opponent conceded'
 docs[n]['terminal_evidence_ids']=ids(430,430.5,431,439)
 docs[n]['normal_draw_turn_12']={'status':'observed_failed_draw_empty_deck','drawn_cards':0,'hand_count_before':3,'hand_count_after':3,'evidence_ids':ids(428,428.5)}
 docs[n]['final_result_statistics']=None
 docs[n]['last_observed_points_basis']='Visible board before concession; this is not a final scored result or result-statistics total'
docs['SUMMARY.json']['outcome_evidence']=ids(430,430.5,431,439)
docs['PAUSE_GAME.json']['limits']=docs['UNCERTAINTIES.json']['unresolved']
docs['DECK_USED.json']['game_review_binding']={'outcome':'owner_win','terminal_cause':'observed_opponent_concession','terminal_evidence_ids':ids(430,430.5,431),'scope_note':'The filmed QR list and absent live-log snapshot status are unaffected by this corrected game outcome.'}
ev=docs['TURN_EVIDENCE.json']
for f in ev['frames']:
 t=f['requested_source_seconds']
 if t in [428,428.5]:
  f['role']+=', observed_empty_deck_draw_failure';f['turn_number']=12;f['who_played']='owner';f['observation']='No cards left in deck; unable to draw cards';f['suitability_or_limit']='Readable explicit system message establishes empty owner deck and failed normal draw, not a successful draw animation.'
 if t in [430,430.5,431]:
  f['role']+=', observed_opponent_concession';f['turn_number']=12;f['who_played']='owner';f['observation']='Your opponent conceded';f['suitability_or_limit']='Readable explicit system message establishes opponent concession; source result confirms owner victory.'
 if t in audit:
  f['energy_zone_observations']={'source_seconds':t,'opponent':{'current_count':audit[t][0][0],'next_count':audit[t][0][1]},'owner':{'current_count':audit[t][1][0],'next_count':audit[t][1][1]},'basis':'Separate native zone crop inspection; null next means absent or obscured glyph, not an inferred future Energy.'}
  f['energy_zone_crops']={'opponent':{'path':f'energy_zone_audit/t{t:07.2f}_opponent.png','pixel_bounds_x0_y0_x1_y1':[80,240,350,620]},'owner':{'path':f'energy_zone_audit/t{t:07.2f}_owner.png','pixel_bounds_x0_y0_x1_y1':[900,2015,1170,2395]}}
ev['scheduled_capture_limits']=[s.replace('Turn 12 shows no normal draw.','Turn 12 explicitly shows a failed normal draw because the deck is empty.').replace('no owner ending action occurs','the opponent concedes before an owner ending action occurs') for s in ev['scheduled_capture_limits']]
ev['energy_zone_audit_file']='energy_zone_audit/ENERGY_ZONE_AUDIT.json'
ev['terminal_events']=[{'source_seconds':428,'event':'Observed empty-deck draw failure','evidence_ids':ids(428,428.5)},{'source_seconds':430,'event':'Observed opponent concession','evidence_ids':ids(430,430.5,431)},{'source_seconds':439,'event':'Observed Victory versus Hons','evidence_ids':ids(439)}]
for n,d in docs.items():
 d['review_revision']={'number':2,'status':'repaired_after_independent_rejection_pending_recheck','repaired_at_utc':now,'repair_notes':'REPAIR_NOTES.md'}
 (p/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
review=(p/'REVIEW.md').read_text(encoding='utf-8')
review=review.replace('The exact terminal cause is unknown. No explicit concession, disconnect, or timeout wording is visible in the dense 426-433.5 second ending.','The source explicitly says **Your opponent conceded** at 430, 430.5 and 431 seconds. Hons concedes during owner turn 12. The last observed 0-1 board is kept separately from final result statistics, which are not opened.')
review=review.replace('The owner starts turns with a Darkness available and a next Darkness icon; used Energy is absent at the pre-end boundary. Turn 12 retains its unused Darkness. Opposing Darkness Energy is visible rather than inferred from deck membership.','The large current circle and small next glyph are recorded separately at each chosen source frame. Current Energy can still be empty during a turn transition, and next glyphs can be absent or obscured during animation. No configured deck Energy fills an absent field. Turn 12 retains its visibly unused Darkness.')
review=re.sub(r'^\| 12 \|.*$', '| 12 | owner | 426-433 s | No owner voluntary play. At 428-428.5 seconds the system says No cards left in deck; unable to draw cards. The owner hand stays at three. At 430-431 seconds the system says Your opponent conceded. Hons concedes and the source subsequently shows owner Victory. |',review,flags=re.M)
review=review.replace('- Turn 12: no normal draw or added card is visible. The same three cards persist through the terminal boundary. No timestamp is invented for a draw that the recording does not show.','- Turn 12: the system explicitly reports No cards left in deck; unable to draw cards at 428-428.5 seconds. The normal draw fails because the owner deck is empty. No card enters the hand, which stays as Lucky Ice Pop, Lucky Ice Pop and Poké Ball. No successful draw-end timestamp is invented.')
review=review.replace('because no owner end action occurs','because the opponent concedes before an owner end action')
review=review.replace('Their recorded immediate starting zones are empty with next Darkness visible; the Darkness appears before the attachment.','Their immediate current circles are empty. At 117 seconds the owner next glyph is also absent, while at 355.5 seconds next Darkness is visible. The Darkness appears before the later attachment. At 206.5 and 292 seconds owner current Darkness is visible while the next glyph is absent.')
review=review.replace('The owner wins during the next displayed turn without a visible owner attack or point award.','During turn 12 the owner cannot draw because the deck is empty, then Hons explicitly concedes. The owner wins without an owner attack or point award.')
review=review.replace('The battle result is certain, but its exact terminal cause and detailed result statistics are unavailable.','The battle result and opponent concession are explicit. Detailed final result statistics are unavailable. The owner empty-deck draw failure is also directly observed.')
review+='\n\n## Independent repair revision\n\nThe first submission incorrectly denied two readable system messages and used Energy Zone defaults across different phases. Those claims are corrected from the native frames. All starting and ending zone records now use their own captured frame, with absent or obscured preview glyphs left null. The eight rejected inputs are preserved with their exact checked hashes in before_independent_repairs_20261012T234354Z. This repaired revision remains pending independent recheck. See REPAIR_NOTES.md and energy_zone_audit/ENERGY_ZONE_AUDIT.json.\n'
(p/'REVIEW.md').write_text(review,encoding='utf-8')
coverage=(p/'COVERAGE.md').read_text(encoding='utf-8')
coverage=coverage.replace('the explicit final result is owner victory with cause unknown.','the explicit final result is owner victory following the observed opponent concession at 430-431 seconds. The last board is not a final result-statistics score.')
coverage+='\nIndependent repair revision: all eight rejected files were preserved with matching hashes. Turn 12 includes the explicit empty-deck normal-draw failure at 428-428.5 seconds and the explicit opponent concession at 430-431 seconds. Every chosen start/end frame was audited for both Energy Zone lines; current empty circles remain zero, while transiently absent or obscured next glyphs remain null. This is submitted for independent recheck, not acceptance.\n'
(p/'COVERAGE.md').write_text(coverage,encoding='utf-8')
(p/'energy_zone_audit/ENERGY_ZONE_AUDIT.json').write_text(json.dumps({'source_video':video,'source_sha256':sha,'audited_at_utc':now,'native_frame_count':len(audit),'board_player_records':len(audit_records),'records':audit_records,'method':'Every one of the 24 start/end board records has both player zones inspected against its own frame. The 23 unique frames are retained as native crops and three contact sheets. No deck or later-frame default supplies an absent field.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(p/'REPAIR_NOTES.md').write_text('''# Independent repair notes

Revision 2 repairs the rejected eight-file submission. Rejected inputs were copied before mutation into before_independent_repairs_20261012T234354Z. SHA-256 of every original and every archived copy matched independent_sol/CHECK_RESULT.json.

The original reviewer overlooked the central ending messages while examining hand crops. The retained full native frames show the owner empty-deck draw failure at 428 and 428.5 seconds, and the opponent concession at 430, 430.5 and 431 seconds. The repaired ledger and prose record both as observed system events. Terminal-cause and deck-exhaustion uncertainties were removed. The three-card hand and no owner voluntary play remain correct. Last observed points 0-1 remain separate from unopened final statistics.

Every starting and ending board Energy Zone was audited against its own native frame. The opponent current circle at 87 seconds is empty. Owner next glyphs at 117, 206.5 and 292 are absent, both next glyphs at 200 are absent during animation, and opponent next at 166 is prompt-obscured. Those next fields are null with specific reasons. Other visible current and next glyphs were transcribed individually. energy_zone_audit/ENERGY_ZONE_AUDIT.json contains 48 board/player records across 23 unique source frames, with retained native zone crops and three contact sheets.

All eight files carry revision provenance or a prose repair note. The filmed QR deck binding, 12 turns, opening, owner hand reconciliation, no opened discards, unresolved Colorless origin and unreadable opponent ability limits are preserved. No source, shared log, external artifact, registration or archive location was changed. Structural validation and final hashes are saved in REPAIR_VALIDATION.json and REPAIR_FINAL_HASHES.json. This repair is pending independent recheck.
''',encoding='utf-8')
# Prevent accidental regeneration from the superseded first-pass builder.
builder=p/'build_packet.py'
original=builder.read_text(encoding='utf-8')
if not original.startswith("raise RuntimeError"):
 builder.write_text("raise RuntimeError('Superseded after independent rejection. Do not rerun; use repaired packet and repair provenance.')\n"+original,encoding='utf-8')
validator=p.parents[0]/'BATCH_2026-10-11_NEW_PAUSE_GAMES/validate_packet.py'
validator=p.parents[1]/'BATCH_2026-10-11_NEW_PAUSE_GAMES/validate_packet.py'
py=r'C:\Users\dacz8\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
r=subprocess.run([py,'-X','utf8',str(validator),str(p)],capture_output=True,text=True,encoding='utf-8')
(p/'REPAIR_VALIDATION.json').write_text(r.stdout,encoding='utf-8')
if r.returncode:print(r.stdout);raise SystemExit(r.returncode)
(p/'REPAIR_FINAL_HASHES.json').write_text(json.dumps({'revision':2,'repaired_at_utc':now,'source_sha256':sha,'file_sha256':{n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in names},'acceptance_status':'pending_independent_recheck'},indent=2)+'\n',encoding='utf-8')
print(r.stdout)
print('Preserved rejected inputs, repaired all eight files and saved final hashes. Independent recheck remains pending.')
