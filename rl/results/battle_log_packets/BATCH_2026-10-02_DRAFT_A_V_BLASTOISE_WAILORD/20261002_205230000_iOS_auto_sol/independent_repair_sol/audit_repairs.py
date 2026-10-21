import json, hashlib, pathlib, difflib
B=pathlib.Path(__file__).resolve().parents[2]
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
for game in ['20261002_205230000_iOS_auto_sol','20261002_210612000_iOS_auto_sol']:
 p=B/game; m=read(p/'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json'); o=read(p/'worker_submission/SUBMISSION.json'); r=read(p/'REPAIR_RECEIPT.json'); prior=read(p/'independent_sol/CHECK_RESULT.json')
 errors=[]
 for n,h in m['files'].items():
  if sha(p/n)!=h: errors.append('current:'+n)
 for n,h in m.get('additional_files',{}).items():
  if sha(p/n)!=h: errors.append('additional:'+n)
 for n,h in o['files'].items():
  if sha(p/'worker_submission'/n)!=h: errors.append('original:'+n)
 if sha(p/'SUBMISSION.json')!=sha(p/'worker_submission/SUBMISSION.json'): errors.append('original submission')
 original_sha=m.get('original_submission_sha256',m.get('original_submission_manifest_sha256'))
 if sha(p/'worker_submission/SUBMISSION.json')!=original_sha: errors.append('original manifest hash')
 if sha(p/'independent_sol/CHECK_RESULT.json')!=r.get('independent_findings_sha256',r.get('protected_independent_check_sha256',sha(p/'independent_sol/CHECK_RESULT.json'))): errors.append('prior independent')
 for n,h in m.get('immutable_extraction_manifests',{}).items():
  if sha(p/n)!=h: errors.append('immutable:'+n)
 manifests=[p/'EXTRACTION_MANIFEST.json']
 if (p/'independent_sol/EXTRACTION_MANIFEST.json').exists(): manifests.append(p/'independent_sol/EXTRACTION_MANIFEST.json')
 images=0; frames=0
 for mf in manifests:
  items=read(mf); items=items if isinstance(items,list) else items.get('frames',items.get('evidence',[]))
  for f in items:
   frames+=1
   for path,h in [(f['full_frame_path'],f['full_frame_sha256'])]+[(f[k]['path'],f[k]['sha256']) for k in ['top_crop','bottom_crop'] if k in f]:
    images+=1
    if sha(pathlib.Path(path))!=h: errors.append('image:'+path)
 changed=[n for n,h in o['files'].items() if sha(p/n)!=h]
 rows=read(p/'TURN_LEDGER.json'); print(game,'manifest',sha(p/'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json'),'errors',errors,'files',len(m['files']),'preserved',len(o['files']),'native',frames,'image_hashes',images,'changed',changed,'ledger_type',type(rows).__name__,'prior_full',prior['full_review_coverage_checked'],prior['pause_contract_checked'])
 for n in changed:
  a=(p/'worker_submission'/n).read_text(encoding='utf-8-sig').splitlines(); z=(p/n).read_text(encoding='utf-8-sig').splitlines()
  if n.endswith('.md'): print('\n'.join(difflib.unified_diff(a,z,fromfile='original/'+n,tofile='effective/'+n,n=1)))
 out=p/'independent_repair_sol'; out.mkdir(exist_ok=True)
 (out/'PRESERVATION_AUDIT.json').write_text(json.dumps({'errors':errors,'effective_sha256':sha(p/'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json'),'current_files_checked':len(m['files']),'original_files_preserved':len(o['files']),'native_frames':frames,'image_hashes_checked':images,'changed_files':changed,'prior_complete_coverage':prior['full_review_coverage_checked'],'prior_pause_contract':prior['pause_contract_checked']},indent=2)+'\n',encoding='utf-8')
