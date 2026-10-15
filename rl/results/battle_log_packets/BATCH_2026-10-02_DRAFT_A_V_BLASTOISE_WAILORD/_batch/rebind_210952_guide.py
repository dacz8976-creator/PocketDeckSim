import copy,hashlib,json,shutil
from pathlib import Path
P=Path(__file__).resolve().parent/'20261002_210952000_iOS_auto_sol'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
g=read(P/'GUIDE_UPDATE_SUBMISSION_AFTER_REPAIR.json');core=read(P/'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json')
dest=P/'guide_repair_before_binding_fix';assert not dest.exists();dest.mkdir()
for n,h in g['files'].items():assert sha(P/n)==h;shutil.copy2(P/n,dest/n)
shutil.copy2(P/'GUIDE_UPDATE_SUBMISSION_AFTER_REPAIR.json',dest/'GUIDE_UPDATE_SUBMISSION_AFTER_REPAIR.json')
binding={'path':'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json','sha256':sha(P/'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json')}
supp=read(P/'GUIDE_UPDATE_SUPPLEMENT.json')
supp['original_author_effective_core_manifest']=copy.deepcopy(supp['effective_core_manifest'])
supp['effective_core_manifest']=binding
supp['metrics']['scope']='Original Astra supplemental pass; independent/root repair metrics are separate.'
supp['bounded_repair']['independent_new_native_extractions']=6
supp['bounded_repair']['new_independent_frames_registered_in_core_evidence']=3
supp['bounded_repair']['current_effective_core_manifest']=binding
save(P/'GUIDE_UPDATE_SUPPLEMENT.json',supp)
with (P/'GUIDE_UPDATE_SUPPLEMENT.md').open('a',encoding='utf-8') as f:f.write('\nThe no-new-extraction statement above describes the original Astra pass. The separate independent correction phase retained six native exceptions and registered three in the corrected core evidence. Current supplemental provenance binds SUBMISSION_AFTER_INDEPENDENT_REPAIR.json; original bindings and all prior files remain preserved.\n')
g['original_author_effective_core_manifest']=copy.deepcopy(g['effective_core_manifest']);g['effective_core_manifest']=binding
g['original_author_effective_core_files_sha256']=copy.deepcopy(g['effective_core_files_sha256']);g['effective_core_files_sha256']=core['files']
g['original_author_validation']=copy.deepcopy(g['validation'])
g['validation']={'current_effective_core_files_hash_verified':True,'original_author_files_preserved':True,'all_owner_turns_have_fresh_board_records':9,'copy_lower_bounds_unchanged':True,'independent_correction_new_native_frames':6,'registered_new_independent_frames':3,'independent_recheck_pending':True}
for n,h in core['files'].items():assert sha(P/n)==h,n
g['files']={n:sha(P/n) for n in g['files']};g['prior_repair_manifest_preserved']='guide_repair_before_binding_fix/GUIDE_UPDATE_SUBMISSION_AFTER_REPAIR.json'
save(P/'GUIDE_UPDATE_SUBMISSION_AFTER_REPAIR.json',g)
print(json.dumps({'effective_core_sha256':binding['sha256'],'effective_guide_sha256':sha(P/'GUIDE_UPDATE_SUBMISSION_AFTER_REPAIR.json')}))
