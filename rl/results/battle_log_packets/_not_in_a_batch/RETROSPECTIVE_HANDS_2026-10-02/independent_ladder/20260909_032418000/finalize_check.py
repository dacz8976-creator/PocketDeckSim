from pathlib import Path
import json,hashlib,datetime
BASE=Path(__file__).resolve().parent
P=BASE.parents[1]/'20260909_032418000'
read=lambda n:json.loads((P/n).read_text(encoding='utf-8-sig'))
submission=read('SUBMISSION.json')
hashes=[{'path':f['path'],'expected_sha256':f['sha256'],'actual_sha256':hashlib.sha256(Path(f['path']).read_bytes()).hexdigest()} for f in submission['submitted_files']]
assert len(hashes)==17 and all(h['expected_sha256']==h['actual_sha256'] for h in hashes)
ledger=read('TURN_LEDGER.json')['turns']; hands=read('HAND_SUPPLEMENT.json')['owner_turns']; review=read('REVIEW_SUPPLEMENT.json')
assert len(ledger)==10 and [r['turn_number'] for r in hands]==[1,3,5,7,9]
expected={1:4,3:3,5:4,7:5,9:6}
for row in ledger:
 if row['turn_number'] in expected: assert row['opponent_hand_at_owner_turn_start']['count']==expected[row['turn_number']]
for row in hands:
 canonical=ledger[row['turn_number']-1]
 assert row['start_hand']['cards_left_to_right']==canonical['owner_hand_start']['cards_left_to_right']
 assert row['before_end_hand']['cards_left_to_right']==canonical['owner_hand_end']['cards_left_to_right']
frames=read('TURN_EVIDENCE.json')['frames']; ids={f['evidence_id'] for f in frames}
missing=[]
def walk(v):
 if isinstance(v,dict):
  for k,x in v.items():
   if k.endswith('evidence_ids') and isinstance(x,list): missing.extend(e for e in x if isinstance(e,str) and e not in ids)
   walk(x)
 elif isinstance(v,list):
  for x in v:walk(x)
for f in submission['submitted_files']:
 if f['path'].endswith('.json'): walk(json.loads(Path(f['path']).read_text(encoding='utf-8-sig')))
assert not missing,missing
result={'source':submission['source'],'source_sha256':submission['source_sha256'],'checker':'sol_retro_ladder_012720','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'producer_frozen_utc':submission['frozen_utc'],'verdict':'accepted_with_recording_limits','required_repairs':[],'consequential_unresolved_items':[],'submitted_file_count':17,'submitted_hash_checks':hashes,'turn_rows':10,'owner_hand_turns':[1,3,5,7,9],'source_hash_reads':0,'new_native_frames':0,'producer_files_modified':False,'native_inspection_manifest':'INSPECTED_NATIVE.json','checks':[{'field':'opening and all owner hands','result':'Five opening identities and left-to-right duplicates confirmed; owner start/end counts 5/4,5/0,1/0,1/0,1/0. T9 sole Ice Pop identity visible in inspection overlay, with clean-view limit correctly retained.'},{'field':'draw timing','result':'Dense preplay start anchors and about +1/+3/+6 candidates retained; source seek labels are requested times, actual PTS remains null rather than invented.'},{'field':'opponent fans','result':'Final version owner starts 4,3,4,5,6. T2 preboundary4, after-normal-draw5, ending3. Counts agree across canonical rows and owner hands.'},{'field':'actions/no effect/declines','result':'Native prompts plus action/board endpoints support both Hammers, Luxury Coin declined/used qualification, Order Pad failed search, two uses of same returned Ice Pop, Energy placement/retreat, poison and preaward empty owner board.'},{'field':'discard','result':'Native189.5 and255 views support visible Items and one Lightning at255; panel layouts are not chronological. Hidden opponent pile contents remain unknown.'},{'field':'mode','result':'No Auto option seen in inspected unoccluded controls. Candidate classification remains qualified; enabled state and individual authorship are unknown. Owner Auto-option rule preserved.'},{'field':'source/outcome','result':'Source-bound retained frames reused with completed producer verification receipt; no video hash/read/decode repeated. Historical0-3loss preserved;337.5 is explicitly preaward, not final score proof.'}],'nonblocking_notes':[{'field':'HAND_SUPPLEMENT.owner_turns[4].before_end_hand.evidence_ids','note':'Lists t0314.00 boundary after attack, while before_end_evidence_ids correctly points to t0305.00 before attack. Both directly show the same empty hand. Phase distinction is recorded here; no identity/count correction needed.'},{'field':'earlier working-version concerns','note':'Initial check saw stale fan/reference data. Latest22:48:26 freeze already corrected counts and registers r0035.00. Root performed no repair. Only latest17-file hashes govern this verdict.'}],'limits':['Checker inspected selected native anchors, not every movie instant or every retained image. Producer systematic345sample1fps coverage audit was read; locator decode was not repeated.','Hidden opponent draws/refills and unopened pile identities remain null. Exact historical20-card deck absent; visible core does not substitute current deck.','Requested source seconds and approximate draw endpoints are not measured decoded PTS.']}
(BASE/'CHECK_RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
text='# Independent Sol check: Rotom 032418\n\nAccepted with recording limits. The latest frozen packet from '+submission['frozen_utc']+' passes all 17 submitted-file SHA checks. No required repair or consequential unresolved item remains.\n\nOpening five and all five owner starting/ending hands were checked in native evidence, including duplicate Hammers and both Goo-zooka appearances. Final owner-start opponent fan counts are 4, 3, 4, 5, 6. The earlier count/reference concern belonged to a working version and is already corrected in this freeze. Root made no repair.\n\nNative prompts and board endpoints support failed/no-effect coin actions, the qualified Luxury Coin decline, returned Ice Pop reuse, retreat, typed attachments, poison and the preaward terminal board. The inherited 0-3 loss stands. No Auto option was seen in selected unoccluded controls; the candidate classification and authorship limits remain qualified.\n\nOne harmless provenance note remains: T9 before-end hand cites the later314 boundary, while its capture list correctly cites305 before the attack. Both show zero cards. The checker preserves this phase distinction without changing producer files. Requested times are not measured PTS. Hidden opponent identities and the unavailable historical exact20 remain unknown.\n\nNo source hash, locator decode, new frame capture or producer edit was performed. See CHECK_RESULT.json and INSPECTED_NATIVE.json for the frozen file checks and directly inspected evidence.\n'
(BASE/'CHECK_RESULT.md').write_text(text,encoding='utf-8')
print(json.dumps({'verdict':result['verdict'],'hashes':len(hashes),'registered_frames':len(frames),'missing_refs':missing}))
