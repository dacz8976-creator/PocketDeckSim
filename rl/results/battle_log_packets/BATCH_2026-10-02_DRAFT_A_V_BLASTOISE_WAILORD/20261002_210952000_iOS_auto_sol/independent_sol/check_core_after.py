import json,hashlib,datetime
from pathlib import Path
b=Path(__file__).resolve().parent.parent;p=b/'independent_sol'
r=lambda f:json.loads((b/f).read_text(encoding='utf-8-sig'));sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
fn='SUBMISSION_AFTER_INDEPENDENT_REPAIR.json';sub=r(fn);old=r('worker_submission/SUBMISSION.json')
assert sha(b/fn)=='7b6e7108591db334dc3bb20f9cd31219343c443ab2c810182071ceb0284a8f03'
for n,h in sub['files'].items():assert sha(b/n)==h
for n,h in old['files'].items():assert sha(b/'worker_submission'/n)==h
l=r('TURN_LEDGER.json');t18=l['turns'][17]['board_at_start']['owner']['energy_zone']['this_turn']
assert t18=={'type':None,'count':0,'available':False,'phase':'pending_generation'}
expected=[(2,1,0,'Alolan Ninetales ex',35.5,35.515,'independent_sol:F0035.50'),(2,1,1,'Poké Ball',36.4,36.415,'F0036.40'),(2,2,0,'Alolan Vulpix',41.0,41.015,'independent_sol:F0041.00'),(6,1,0,'Misty',93.0,93.015,'F0093.00'),(6,1,1,'Mega Sharpedo ex',93.4,93.415,'F0093.40')]
for tn,di,ci,name,time,pts,eid in expected:
 q=l['turns'][tn-1]['draws_and_searches'][di]['cards_in_reveal_order'][ci]
 assert(q['name'],q['timestamp_seconds'],q['actual_frame_seconds_if_measured'],q['evidence_ids'])==(name,time,pts,[eid])
d=r('independent_sol/CHECK_RESULT.json')
d.update(accepted=True,checked_submission_path=str(b/fn),checked_submission_sha256=sha(b/fn),checked_files_sha256=sub['files'],created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),acceptance_status='accepted_after_bounded_independent_recheck',findings=[],remaining_coverage_gaps=[],unverified_material_claims=[],independently_inspected_image_paths=r('independent_sol/INSPECTED_IMAGES_FINAL.json'),resolved_findings=d['findings'],original_check_receipt={'path':'independent_sol/CHECK_RESULT.json','sha256':sha(p/'CHECK_RESULT.json')},original_submission_preserved={'path':'worker_submission/SUBMISSION.json','sha256':sha(b/'worker_submission/SUBMISSION.json')},recheck_scope='Exact old/current diff, all16effectivefilehashes, preserved original15filehashes, T18zone and fiveT2/T6namedrevealanchors plus registered independentrefs; prior full bounded visual coverage retained without wholepass redecoding.',structural_check_receipt={'path':'independent_sol/STRUCTURAL_CHECK.json','sha256':sha(p/'STRUCTURAL_CHECK.json')},independent_extraction_manifest={'path':'independent_sol/EXTRACTION_MANIFEST.json','sha256':sha(p/'EXTRACTION_MANIFEST.json')})
d['verified_checks']+=['All retained +3/+6 native bottom candidate crops individually inspected across9ownerturns, including T18+1/+3/+6; no additional findings.','Afterrepair all ledger/supplementrefsresolve145registeredframes; original primary142manifestunchanged.']
(p/'CHECK_RESULT_AFTER_REPAIR.json').write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
(p/'CHECK_RESULT_AFTER_REPAIR.md').write_text('# Independent Sol core acceptance after repair\n\nAccepted true. Full review coverage and Pause capture contract checked. Reviewer /root/ind_drafta_auto4, gpt-6.1-sol high.\n\nChecked SUBMISSION_AFTER_INDEPENDENT_REPAIR.json SHA256 '+d['checked_submission_sha256']+' and its exact16file map. Original15files and rejected initial receipt verified preserved. T18 pending Energy generation and all five T2/T6 individual reveal anchors corrected. 113unique images independently inspected. No remaining coverage gaps or unverified material claims within the recording limits.\n\nThe footage confirms Defeat after19turns, wentsecond, owner2/opponent3points, damage500. Final Blastoise attack causes one benchNinetales KO; ActiveSharpedo survives60. Computer battle remains excluded from human Pause and Ladder logs.\n\nLimits: concealed cards, unopened piles, hidden lowerfaces and absent inputtelemetry remain unobservable. Evolution history is separately labeled. Exact supplied20carddeck remains separate from visual19physicalcardlowerbound. See JSON for all limits and complete evidence paths.\n',encoding='utf-8')
print(sha(p/'CHECK_RESULT_AFTER_REPAIR.json'))

