import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(r'C:\Users\dacz8\OneDrive\Desktop\Battle Logs\Recording_QA\RETROSPECTIVE_HANDS_2026-10-02')
P = ROOT/'20261002_021402000'
O = ROOT/'independent_wailord/20261002_021402000'
BACK = P/'worker_submission_before_research_provenance_repair'
NAMES = ['HAND_SUPPLEMENT.json','TURN_LEDGER.json','TURN_EVIDENCE.json','REVIEW_SUPPLEMENT.md','UNCERTAINTIES.json']
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def diffs(a,b,path=''):
    if type(a) != type(b): return [path]
    if isinstance(a,dict):
        result=[]
        for k in sorted(set(a)|set(b)):
            if k not in a or k not in b: result.append(path+'/'+k)
            else: result += diffs(a[k],b[k],path+'/'+k)
        return result
    if isinstance(a,list):
        if len(a)!=len(b): return [path+'/length']
        return [s for i,(x,y) in enumerate(zip(a,b)) for s in diffs(x,y,path+'/'+str(i))]
    return [] if a==b else [path]
records=[]
for name in NAMES:
    rec={'file':name,'path':str(P/name),'repaired_sha256':sha(P/name),'preserved_submission_sha256':sha(BACK/name)}
    if name.endswith('.json'): rec['changed_fields']=diffs(read(BACK/name),read(P/name))
    records.append(rec)
hand=read(P/'HAND_SUPPLEMENT.json')['target_rows'][3]['draws_and_searches'][1]
ledger=read(P/'TURN_LEDGER.json')['turns'][6]['draws_and_searches'][1]
assert hand==ledger
assert 'already in the fan' in hand['cards_in_reveal_order'][0]['limit_reason']
assert 'inferred' in hand['cards_in_reveal_order'][0]['basis']
assert hand['cards_in_reveal_order'][1]['timestamp_seconds']==137
assert hand['cards_in_reveal_order'][1]['evidence_ids']==['f0137.00','f0139.00']
prior=read(O/'SOURCE_CHECKS.json')
current_frames=read(P/'TURN_EVIDENCE.json')['frames']
frame_hashes_unchanged=all(sha(Path(x['full_path']))==x['full_sha256'] for x in prior['image_checks'])
assert frame_hashes_unchanged
result={'reviewer':'sol_verify_wailord_021402','checked_utc':datetime.now(timezone.utc).isoformat(),'verdict':'accepted_with_recording_limits','scope':'Focused recheck of turn7 Research provenance repair only, retaining prior30-image independent acceptance findings.','initial_check_sha256':sha(O/'SOURCE_CHECKS.json'),'initial_check_preserved_status':prior['status'],'repaired_files':records,'repaired_research_events_identical':hand==ledger,'retained64_full_image_hashes_unchanged':frame_hashes_unchanged,'registered_frame_count':len(current_frames),'confirmed_observation':'native137.00 shows Indeedee already appended in fan and Copycat enlarged as current Research reveal. Indeedee identity direct; first-card order inferred from append state. Copycat direct137 plus retained fan139.','remaining_issue':None,'recording_limits':['Exact frame PTS and first Indeedee reveal onset unmeasured.','Opponent fan counts turns5/7 retain7-8 overlap ranges.','Boards, accepted actions, outcome and later owner13 retain inherited/outside-target scope.','Historical deck version and intervening discard windows not newly established.'],'metrics':{'new_visual_image_submissions':0,'new_frames':0,'original_reads':0,'token_usage':None,'dollar_usage':None}}
(O/'SOURCE_CHECKS_REPAIR_ACCEPTANCE.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
with (O/'INDEPENDENT_CHECK.md').open('a',encoding='utf-8') as f:
    f.write('\n## Focused repair acceptance\n\nOctober2,2026: **accepted_with_recording_limits**. The lead preserved the initial five-file worker submission and repaired only the turn7 Research provenance fields and corresponding note. HAND_SUPPLEMENT and TURN_LEDGER now agree: Indeedee identity is direct in the137.00 fan, its first-card order is inferred from append state, and Copycat is the enlarged137.00 reveal plus retained139.00 fan. TURN_EVIDENCE, prose and UNCERTAINTIES state the same boundary. No remaining repair is required.\n\nThe original SOURCE_CHECKS.json remains needs_repair as the historical first-check result. SOURCE_CHECKS_REPAIR_ACCEPTANCE.json records the final verdict, all five repaired-file hashes, preserved-submission hashes and exact changed fields. All64 retained full-image hashes are unchanged. This recheck used0 new image submissions,0 new extractions and0 original reads; earlier30 visual submissions remain the evidence basis. All earlier timing, opponent-fan, inherited-scope and historical-version limits remain.\n')
print(json.dumps({'verdict':result['verdict'],'retained_frames_unchanged':frame_hashes_unchanged,'changed_fields':{x['file']:x.get('changed_fields','prose paragraph') for x in records}}))
