from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib, json, sys
from PIL import Image, ImageChops
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'qr_support/deps'))
import zxingcpp
P=Path(__file__).resolve().parent.parent; O=P/'independent_sol'; B=P.parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
S=read(P/'SOURCE.json'); E=read(P/'TURN_EVIDENCE.json'); L=read(P/'TURN_LEDGER.json'); D=read(P/'DECK_USED.json'); Q=read(P/'qr_intake/QR_DECODE_0001.00.json')
frozen=read(O/'FROZEN_INPUT_SHA256.json'); current={n:sha(P/n) for n in frozen}
assert current==frozen, 'Canonical inputs changed during independent check'
now=datetime.now(timezone.utc).isoformat()
base={'schema':'bounded-independent-sol-acceptance-v1','reviewer':'/root/independent_183108','review_model':'gpt-6.1-sol','review_role':'Fresh separate Sol bounded independent acceptance, not the full-review worker','checked_at_utc':now,'source_video':S['video_basename'],'source_sha256':S['sha256'],'source_duration_seconds':S['duration_seconds'],'media_rehashed':False,'identity_basis':'Frozen CLI SOURCE.json binding; retained native evidence checked and hashed. No original media decoding or mutation.'}
all_dims=[];special=[]
for f in E['frames']:
 fp=P/f['full_frame_path']; im=Image.open(fp); assert im.size==(1170,2532)
 for k in ['bottom_crop','top_crop']:
  c=f[k]; cp=P/c['path']; box=c['pixel_bounds_x0_y0_x1_y1']; ci=Image.open(cp)
  assert ci.size==(box[2]-box[0],box[3]-box[1])
  assert box==([0,2025,1170,2532] if k=='bottom_crop' else [0,0,1170,720])
 if f['role']!='supporting_native_frame':
  row={k:f.get(k) for k in ['evidence_id','role','turn_number','requested_source_seconds','draw_animation_end_seconds','offset_after_draw_seconds','selected_for_start_hand','before_first_play','unzoomed','hand_spread','suitability_or_limit']}
  row['full_frame_path']=f['full_frame_path'];row['full_frame_sha256']=sha(fp);row['native_dimensions']=[1170,2532]
  for k in ['bottom_crop','top_crop']:
   c=f[k];cp=P/c['path'];ci=Image.open(cp).convert('RGB');expected=im.convert('RGB').crop(tuple(c['pixel_bounds_x0_y0_x1_y1'])); assert ImageChops.difference(ci,expected).getbbox() is None
   row[k]={**c,'sha256':sha(cp),'dimensions':list(ci.size),'exact_native_pixel_crop':True}
  special.append(row)
write('CAPTURE_CHECK.json',{**base,'frame_count':len(E['frames']),'unique_evidence_ids':len({f['evidence_id'] for f in E['frames']}),'all_391_full_and_782_crop_files_exist_and_have_correct_dimensions':True,'all_crop_bounds_checked':True,'special_capture_pixel_comparisons_checked':len(special),'bottom_rounding_note':'2025 is floor(0.8*2532); final507px retained at full width.','captures':special,'fact_check_note':'Recorded candidate booleans are frozen original claims; required independent corrections are in CHECK_RESULT.json.'})
qrimage=P/'qr_intake/t0001.00.png';result=zxingcpp.read_barcode(Image.open(qrimage));assert result is not None and result.text==Q['payload']; assert sha(qrimage)==Q['retained_image_sha256'];assert hashlib.sha256(result.text.encode('ascii')).hexdigest()==Q['payload_ascii_sha256']
qrentities=Counter({(c['entity_kind'],c['entity_id']):c['count'] for c in Q['cards']});deckentities=Counter((c['entity_kind'],c['entity_id']) for c in D['cards_in_log_order']);assert qrentities==deckentities and sum(qrentities.values())==20
write('QR_RECHECK.json',{**base,'status':'exact_20_filmed_QR_definition_supported_live_save_pending','native_image':str(qrimage),'native_image_sha256':sha(qrimage),'independent_native_zxing_payload_matches':True,'payload_ascii_sha256':Q['payload_ascii_sha256'],'twenty_slot_entity_counts_match_packet':True,'cards':Q['cards'],'energy':Q['decoded']['energy'],'continuity_witnesses_seconds':[1,4,8,16,32,40],'continuity_finding':'Retained filmed QR, Event selection New deck 6 slot11, human matchmaking, opening and Venipede placement agree with full-worker continuous setup account. No second game or edit is claimed by the packet.','limits':['Full worker supplies whole-source continuity; this is a bounded independent witness check, not a second full decode.','Exact playable QR definitions do not specify artwork/rarity and do not establish hidden card identities.','Live Pause Games saved-deck and game registration remain lead-only; this receipt does not claim either.']})
viewed=set()
for p in O.glob('*.png'):
 pieces=p.stem.split('_'); mode=pieces[0]
 if mode in ['locator','board','bottom','top']:
  viewed.update(float(s) for s in pieces[1:])
viewed.update([1,93.8,94,95,196.5,265,314,389])
views=[]
for f in E['frames']:
 if f['requested_source_seconds'] in viewed:
  views.append({'evidence_id':f['evidence_id'],'requested_source_seconds':f['requested_source_seconds'],'actual_frame_pts':None,'full_frame_path':f['full_frame_path'],'full_frame_sha256':sha(P/f['full_frame_path']),'top_crop':{**f['top_crop'],'sha256':sha(P/f['top_crop']['path'])},'bottom_crop':{**f['bottom_crop'],'sha256':sha(P/f['bottom_crop']['path'])}})
write('VIEWED_EVIDENCE.json',{**base,'inspected_retained_source_times':sorted(viewed),'retained_frame_records':views,'viewing_method':'Native full frames and native-resolution unchanged crop/board tiles used for names/counts/state. Reduced locator derivatives were used to inspect public sequence and select native detail witnesses; they are not substitutes for retained native captures.','review_images':[{'path':p.name,'sha256':sha(p)} for p in sorted(O.glob('*.png'))],'outside_packet_view':{'path':'qr_intake/t0001.00.png','sha256':sha(qrimage)},'limits':'Requested source-local seeks only; actual PTS and exact touch/remote input not asserted.'})
supplement_names=['ASSIGNMENT.json','ASSIGNMENT.md','RECORDING_METADATA.json','qr_intake/QR_DECODE_0001.00.json','qr_intake/INTAKE_RESULT.json','qr_intake/t0001.00.png','astra_gap/CHECK_RESULT.json','astra_gap/VIEWED_EVIDENCE.json']
supp={n:sha(P/n) for n in supplement_names}
for n in ['STANDARD_WORKER_ASSIGNMENT.md','LIVE_DECK_SNAPSHOT.json','NEW_DECK_ENTRIES.json','PAUSE_DECKS_IMPORT.json','OWNER_CONTEXT.json']:
 if (B/n).exists():supp['../'+n]=sha(B/n)
for n in ['CAPTURE_CHECK.json','QR_RECHECK.json','VIEWED_EVIDENCE.json']:supp['independent_sol/'+n]=sha(O/n)
none_locations=[]
for t in L['turns']:
 for bname in ['board_at_start','board_after']:
  b=t[bname]
  if b['stadium'] is None:none_locations.append(f'turn{t["turn_number"]}.{bname}.stadium')
  for side in ['owner','opponent']:
   s=b[side]
   for place,m in [('active',s['active'])]+[(f'bench[{i}]',m) for i,m in enumerate(s['bench_in_position_order'])]:
    if m.get('name') and m.get('tool') is None:none_locations.append(f'turn{t["turn_number"]}.{bname}.{side}.{place}.tool')
qualifications={53:[True,True],56:[True,True],94.5:[True,True],96.5:[True,True],99.5:[False,True],177:[False,True],179:[True,True],182:[True,True],253:[True,True],315:[True,True],317:[True,True],320:[False,False],196.5:[False,True]}
repairs=[
 {'id':'R1_T6_DRAW_COUNT','location':'TURN_LEDGER.json turn6.draws_and_searches[0]','rejected_claim':{'hand_count_before':3,'hand_count_after':4},'supported_replacement':{'hand_count_before':4,'hand_count_after':5},'evidence_ids':['F_0203_00','F_0205_00'],'reason':'Native top fan has4 backs at203,5 at205 and before connection refresh,3 at219.5 after two Pokemon cards leave. Astra agrees independently.','required_action':'Correct counts and cite203/205; preserve unknown identities, unknown buffered mutual order, and no invented extra draw.'},
 {'id':'R2_KNOWN_ABSENCE_SCALARS','location':'TURN_LEDGER.json observed living Pokemon Tool fields and absent Stadium fields','rejected_claim':'Null for observed no Tool/no Stadium, without absence status or reason.','required_action':'Use none or explicit observed_absent status for established absence. Keep null for truly unknown values and for not-applicable empty Pokemon slots; do not fill hidden values.','affected_locations':none_locations,'evidence_ids':['F_0051_00','F_0053_00','F_0093_50','F_0176_00','F_0248_00','F_0314_00','F_0368_00','F_0389_00'],'reason':'Protocol and STANDARD_WORKER_ASSIGNMENT distinguish known absence from unknown. Existing visibly_empty positional Bench objects are valid.'},
 {'id':'R3_CAPTURE_QUALIFICATIONS','location':'TURN_EVIDENCE.json draw-offset candidates and F_0196_50; TURN_LEDGER turn5.owner_hand_end.basis','rejected_claim':'All postplay candidates get unzoomed:false/hand_spread:false regardless of actual view; F_0196_50 claims unzoomed:true and intact unzoomed ending hand.','required_action':'Correct each independent flag based on actual frame, preserving before_first_play:false and unsuitability for postplay candidates. At196.5 label the large Scolipede attack zoom; the two ending cards Copycat/Scolipede remain readable and count2 is supported. Either retain that witnessed ending hand with accurate zoom limitation, or select another retained clear preattack view. Do not replace it with a postattack view.','supported_unzoomed_hand_spread_by_requested_seconds':{str(k):{'unzoomed':v[0],'hand_spread':v[1]} for k,v in qualifications.items()},'reason':'A spread, unzoomed changed hand is still unsuitable for the initial preplay hand; suitability must not overwrite independent factual capture properties. At320 coin modal blurs the hand and neither property is supported.'},
 {'id':'R4_TERMINAL_COMPOSITE_EVIDENCE','location':'TURN_LEDGER.json turn10.board_after and knockout_removal evidence','rejected_claim':'Entire terminal typed board directly observed from392 alone.','required_action':'Bind the board/mon/Zone fields to clean389 postremoval evidence and the opponent awarded total3 to392. Add explicit composite phase/basis with389 prior1 and392 point award3. Cite389 for owner empty Active and no terminal promotion; retain386/387 retaliation and388 removal animation separately.','evidence_ids':['F_0386_00','F_0387_00','F_0388_00','F_0389_00','F_0392_00','F_0402_00'],'supported_board_389':{'owner_active':'visibly empty','owner_bench_center':'Mega Sableye ex170/170,Darkness1,noTool','opponent_active':'Houndstone60/130,Psychic2,noTool','opponent_right_bench':'Meloetta10/70,noEnergy,noTool','stadium':'Peculiar Plaza','points_before_award':[2,1]},'reason':'392 +3 point overlay obscures both Active slots.389 cleanly supports postremoval board before the overlay, whereas388 is still bright removal animation.'}
]
anchors=[
 {'scope':'opening/setup','seconds':[1,4,8,16,32,40],'finding':'One human Event setup, filmed New deck6 slot11. Five opening slots Copycat,Wally,Whirlipede,Scolipede,Venipede; Venipede placed Active.'},
 {'scope':'ordinary ownerT1','seconds':[49,51,51.5,52,53,56],'finding':'Normal Scolipede draw; five-card selected/end hand at51. No Energy/card play. End Turn warning A Supporter card can be used shown51.5/52; accepted into Current turn2 by53.'},
 {'scope':'ordinary full opponentT2','seconds':[53,56,60,63,65,67,69,72.5,79,85,89,91,93.5],'finding':'Hidden normal draw; Research two hidden draws; Plaza; Meloetta bench; free Pumpkaboo retreat to center Bench and Meloetta Active;Psychic attached to benchedPumpkaboo. No attack. Names, typed targets, ordering and final board match.'},
 {'scope':'ordinary ownerT3','seconds':[93.5,93.8,94,94.5,95,96.5,99.5,103,104,116],'finding':'Six-card intact preplay hand ends Mega Sableye ex; first voluntary move benches Mega; later Whirlipede evolution thenDarkness toActive. Current Zone empty at93.5 before generation; hand4 at104, Poison/40 andcheckup10 reconciled in full account.'},
 {'scope':'ownerT5','seconds':[174.5,175.5,176,176.5,177.5,180.5,181,184,186,189,190,194,196.5,198,203],'finding':'Normal Needle draw then preplay5 at176; rapid Scolipede evolution preserves70damage;WallyColorless toScolipede;Needle andnormalDarkness tobenchedMega. Owner endinghand2. Zoom qualification needsR3.'},
 {'scope':'T6buffer','seconds':[203,205,219.5],'finding':'Independent top crops confirm4→5normaldraw, then3postbuffer. Astra19nativeframe clarification independently supports changed boards and unknown mutual order; accepted unknown order preserved.'},
 {'scope':'Copycat','seconds':[248,250,253,255,256,257,261,262,263,265,285],'finding':'First Darkness toActiveMega thenCopycat;Scolipede/Cyrus returned todeck, drawsCyrus firstthenLuckyIcePop to matchfan2. Endinghand2; attack100,GourgeistKO,+1,promotionMeloetta20,Needle10 thenCurrentturn8.'},
 {'scope':'two Pop uses and T9 resolution','seconds':[312,313.5,314,315,318,321,323,325,327,330,332,334,336,340.5,342,344.5,345.5,349.5,351,356,358,364,368],'finding':'Mega normaldraw;two separateuses sameLuckyIcePop40→60Headsreturned then60→80Tailsdiscarded. SecondMega bench,Darkness toBench notActive;Cyrus onlyendhand1. Attack100,HoundstoneKO,+1total2,promotedGreavard70→60Needle;Supporterwarningaccepted.'},
 {'scope':'terminalT10','seconds':[370,372,378,382,384,386,388,389,392,394,402,403],'finding':'Greavard evolveswith10damage toHoundstone120;secondPsychic;LastRespects170 dropsMega80→0;retaliation60 dropsHoundstone120→60 beforeMega removal. Owner Activeempty andBenchMega survives. +3points,Defeat,10turns,owner2/opponent3,470damage. Composite evidence needsR4.'}
]
receipt={**base,'status':'rejected_pending_surgical_repairs','stable_inputs':True,'checked_input_sha256':current,'supplemental_checked_input_sha256':supp,'independent_acceptance':False,'whole_source_second_pass_claim':False,'scope':'Bounded independent acceptance against complete first-pass source packet; opening, ordinary owner T1/T3 and full ordinary opponent T2 independently checked beyond worker flagged ambiguity, all scheduled owner captures inspected, consequential sequences and terminal checked.','required_repairs':repairs,'ordinary_and_consequential_anchors':anchors,'supported_outcome':{'classification':'human_event','opponent':'ぐー、','owner_outcome':'loss','owner_points':2,'opponent_points':3,'turns':10,'damage_dealt':470},'captured_deck_status':'Exact20 filmed QR independently re-read and entity-count matched; live save pending lead.','turn_rows':len(L['turns']),'crop_verification':'391native full/782 crops correct dimensions and bounds;22special captures exact pixel comparisons and hashes in CAPTURE_CHECK.json.','preserve_limits':['T6 internal buffered action order and remote input times unavailable; do not reconstruct.','Opponent hidden draws/search identities remain unknown.','No full opened/scroll discard pile available; periodic snapshots explicitly limited.','Native seek times are requested local timestamps; actual PTS and exact touch timing not measured.','Opponent name image transcription is supported; no underlying account ID assertion.','Prepared filmed deck definition is not a saved-live-log claim.'],'recheck_scope':'After lead applies one surgical repair, rehash nine inputs and narrowly recheckR1-R4 and affected cross-file consistency. Do not rerun whole builder/fulldecode or modify frozen rejected receipt.','canonical_files_modified':False,'external_written':False,'registration_or_media_changes':False,'files_written':['independent_sol/FROZEN_INPUT_SHA256.json','independent_sol/CAPTURE_CHECK.json','independent_sol/QR_RECHECK.json','independent_sol/VIEWED_EVIDENCE.json','independent_sol/CHECK_RESULT.json']}
write('CHECK_RESULT.json',receipt)
print(json.dumps({'status':receipt['status'],'stable_inputs':True,'required_repair_ids':[r['id'] for r in repairs],'native_count':len(E['frames']),'special_captures':len(special),'viewed_source_times':len(viewed),'checked_input_sha256':current},ensure_ascii=True,indent=2))

