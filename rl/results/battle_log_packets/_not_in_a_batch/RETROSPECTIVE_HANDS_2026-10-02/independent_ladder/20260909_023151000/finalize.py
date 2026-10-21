import json,hashlib,datetime
from pathlib import Path
from PIL import Image
BASE=Path(r'C:\Users\dacz8\OneDrive\Desktop\Battle Logs\Recording_QA\RETROSPECTIVE_HANDS_2026-10-02')
P=BASE/'20260909_023151000'; C=BASE/'independent_ladder'/'20260909_023151000'
def read(n): return json.loads((P/n).read_text(encoding='utf-8-sig'))
S=read('SUBMISSION.json');E=read('TURN_EVIDENCE.json');L=read('TURN_LEDGER.json');H=read('HAND_SUPPLEMENT.json');R=read('SOURCE_REFERENCE.json')
hashrows=[]
for x in S['submitted_files']:
 actual=hashlib.sha256(Path(x['path']).read_bytes()).hexdigest(); hashrows.append({'path':x['path'],'matches':actual==x['sha256'],'expected':x['sha256'],'actual':actual})
crop=[]
for x in E['frames']:
 for key in ['bottom_crop','top_crop']:
  if x.get(key):
   a=x[key]; actual=hashlib.sha256(Path(a['path']).read_bytes()).hexdigest()
   crop.append({'id':x['evidence_id'],'kind':key,'hash_matches':actual==a['sha256'],'parent_matches':a.get('parent_sha256')==x['full_frame_sha256']})
native=[x for x in E['frames'] if x['native_dimensions']['width']==1170]
ids={x['evidence_id'] for x in E['frames']}; missing=[]
def refs(o,path):
 if isinstance(o,dict):
  for k,v in o.items():
   if k.endswith('evidence_ids') and isinstance(v,list):
    for i in v:
     if i not in ids: missing.append({'path':path+'.'+k,'id':i})
   refs(v,path+'.'+k)
 elif isinstance(o,list):
  for j,v in enumerate(o): refs(v,path+f'[{j}]')
refs(L,'TURN_LEDGER');refs(H,'HAND_SUPPLEMENT')
oldsource=Path(R['frozen_accepted_source_json']); old=json.loads(oldsource.read_text(encoding='utf-8-sig'))
receipt=read('ROOT_SOURCE_VERIFICATION.json')
validation={'producer_freeze':S['frozen_utc'],'submission_files':hashrows,'all_submission_hashes_match':all(x['matches'] for x in hashrows),'native_catalogued':len(native),'new_native_catalogued':sum(not x['reused_from_accepted_packet'] for x in native),'reused_native_catalogued':sum(x['reused_from_accepted_packet'] for x in native),'reduced_locator_references':len(E['frames'])-len(native),'crop_records':len(crop),'all_crops_match':all(x['hash_matches'] and x['parent_matches'] for x in crop),'missing_field_evidence_references':missing,'retained_source_json_hash_matches':hashlib.sha256(oldsource.read_bytes()).hexdigest()==R['frozen_source_json_sha256'],'root_verification_receipt':receipt,'source_movie_read_or_decoded_by_checker':False}
(C/'SCOPE_VALIDATION.json').write_text(json.dumps(validation,indent=2),encoding='utf-8')
result={'source':S['source'],'source_sha256':S['source_sha256'],'producer_freeze':S['frozen_utc'],'checker':'Sol, different producer','completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'repair_required_minor_packaging_only','substantive_source_fields':'accepted_with_recording_limits','consequential_items':[],'required_repairs':[{'file':'HAND_SUPPLEMENT.json','paths':['target_rows','target_turn_numbers','capture_status'],'action':'Add required canonical aliases from existing five owner_turns, [1,3,5,7,9] and complete_with_recording_limits. No new source work.'},{'file':'SOURCE_REFERENCE.json','path':'sha256','action':'Add requested top-level sha256 alias equal to source_sha256.'},{'file':'HAND_SUPPLEMENT.json','path':'owner_turns[3].before_end_hand','action':'t0241.50 is an attack-selection overlay with the sole Helioptile partly covered. Qualify basis/limit explicitly or use clean t0240.00 as primary before-end reference, retain t0241.50 as secondary. Count/identity one Helioptile accepted.'}],'owner_hands':[{'turn':x['turn_number'],'start':x['start_hand']['cards_left_to_right'],'end':x['before_end_hand']['cards_left_to_right'],'start_ids':x['selected_start_evidence_ids'],'end_ids':x['before_end_evidence_ids'],'result':'identity/count accepted; phase qualification retained'} for x in H['owner_turns']],'checks':['Opening five and slot4 Electrike Active verified at native23.5; owner first.','All 59 catalogued native frames independently viewed, including five starts, before-end anchors and timed candidates. 40 new and19 reused catalogue records; capture inventory may retain one unused old anchor.','All nine structured turns inspected; both boards, typed Energy, tools, effects, Stadium, points and Zones reconcile with sampled native endpoints. Start current-empty states are separately qualified as preceding generation where appropriate.','T2 Research fan6 native85, concealed Ball native95 and subsequent Entei bench native99 support null find identity. Later Entei is not a named search reveal.','T3 Lightning/Cape to healthy Bench1 Electrike; T5 Mega inherits Lightning1, Elegant Cape30 raises180 to210; Heliolisk receives Lightning1 and Backpack effect +20 against opponent Pokemon. T7 extra Lightning to Bench Mega1→2.','T5 damage endpoints70 Active/30 each Bench; T6 High Jump Kick60; T7 displayed50 and endpoints CombuskenKO/bench10; T8 Rare Candy then damaged Mega Blaziken200/210, EnteiFire1→2, HelioliskKO and Legendary Pulse fan3→4.','T9 warning text is direct, OK input inference retained; Research remains in hand and generated Lightning unused. Displayed120 attack precedes settled3–2 native342.','No Auto option observed in these sampled native control anchors. Owner rule any visible option evenOFF retained; enabled state/authorship uncertified. Default ladder candidate acceptable with sampled-absence limit.','No source movie hash/read/decode or repeated locator pass; root completed verification reused. Seven existing reduced cues viewed for phase/animation only, not new card identities.','Periodic closed discard tops and hidden opponent cards remain qualified; exact historical20 remains unavailable. No outcome/rules audit or shared changes.'],'viewed_native_evidence_ids':[x['evidence_id'] for x in native],'viewed_reduced_cue_ids':['cue_122','cue_125','cue_167','cue_191','cue_198','cue_250','cue_310'],'limits':['Actual PTS is unmeasured in producer captures and kept distinct from requested/nominal seeks.','The producer screened all344 reduced samples; checker reviewed the frozen audit and selected cues without claiming to repeat its systematic scan. Subsecond events/unsampled controls remain limited.','T7 selected ending view is an attack-selection overlay; T9 ending candidate is warning overlay with full lower hand visible. Neither should be called a clean unoccluded preselection board.'],'producer_files_modified':False}
(C/'CHECK_RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
(C/'CHECK_RESULT.md').write_text('''# Independent Manectric 023151 check

Substantive source fields accepted with recording limits. Three minor packaging repairs are required before final packet acceptance: add HAND_SUPPLEMENT target_rows, target_turn_numbers and capture_status aliases; add SOURCE_REFERENCE.sha256; qualify the Turn7 attack-selection overlay or use the existing clean240.00 before-end anchor. Count and identity remain one Helioptile.

All26 submitted hashes match. All59 catalogued full native frames were independently viewed (40 new,19 reused). All five owner starts, ending inventories and draw-offset candidates agree. All nine rows, typed Energy targets, Cape/Mega HP, Backpack and Stadium effects, damage endpoints, fan transitions and settled3–2 terminal points reconcile. T2 Ball find stays concealed/null. T9 warning text is direct and OK acceptance remains inferred. No consequential disagreement or further capture needed.

No Auto option was observed in inspected native anchors; sampled absence and unknown action authorship remain qualified. Exact historical20 and concealed opponent identities/piles remain unknown. Root verification was reused. No source movie read/hash/decode, repeated locator pass, producer edits or shared registration changes were performed. Seven existing reduced cues were checked for phase only. See CHECK_RESULT.json and SCOPE_VALIDATION.json for exact evidence and frozen hash validation.
''',encoding='utf-8')
print('validation',validation['all_submission_hashes_match'],validation['all_crops_match'],'refs',len(missing),'native',len(native),'crops',len(crop))
