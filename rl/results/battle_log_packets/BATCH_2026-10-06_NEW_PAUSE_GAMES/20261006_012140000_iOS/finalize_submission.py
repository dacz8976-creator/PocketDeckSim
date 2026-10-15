from pathlib import Path
from datetime import datetime, timezone
import json, subprocess, sys, hashlib
P=Path(__file__).resolve().parent
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def save(name,obj): (P/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
result=subprocess.run([sys.executable,str(P.parent/'validate_packet.py'),str(P)],capture_output=True,text=True,encoding='utf-8',check=True)
structural=json.loads(result.stdout);structural['verified_utc']=datetime.now(timezone.utc).isoformat()
save('STRUCTURAL_VALIDATION.json',structural)
required=['SOURCE.json','REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
ev=json.loads((P/'TURN_EVIDENCE.json').read_text(encoding='utf-8'))
files=required+['QUALIFIED_DECK_CANDIDATE.json','STRUCTURAL_VALIDATION.json']
for frame in ev['frames']:
 files += [frame['full_frame_path'],frame['bottom_crop']['path'],frame['top_crop']['path']]
files=sorted(set(files))
first={name:{'bytes':(P/name).stat().st_size,'sha256':digest(P/name)} for name in files}
second={name:{'bytes':(P/name).stat().st_size,'sha256':digest(P/name)} for name in files}
assert first==second,'Packet changed while submission hashes were checked'
source=json.loads((P/'SOURCE.json').read_text(encoding='utf-8'))
sp=Path(source['source_path_at_review']);before=sp.stat();source_hash=digest(sp);after=sp.stat()
assert source_hash==source['sha256'] and before.st_size==after.st_size==source['bytes'] and before.st_mtime_ns==after.st_mtime_ns
receipt={'schema':'battle-review/first-pass-submission-v1','submitted_utc':datetime.now(timezone.utc).isoformat(),'worker_task':'pause_012140','packet':str(P),'source_video':source['video_basename'],'source_sha256':source_hash,'source_bytes':after.st_size,'source_size_mtime_stable_during_hash':True,'required_files':required,'turn_rows':7,'native_frames':len(ev['frames']),'required_plus_evidence_files':len(files),'structural_validation_file':'STRUCTURAL_VALIDATION.json','structural_pass':True,'structural_issues':[],'packet_stable_across_two_manifest_passes':True,'file_manifest':first,'independent_acceptance':False,'registration_performed_by_worker':False,'source_moved_by_worker':False,'external_log_written_by_worker':False,'astra_required':False,'limit':'First-pass completeness and integrity submission; independent visual acceptance remains the lead responsibility.'}
save('SUBMISSION_RECEIPT.json',receipt)
print(json.dumps({k:receipt[k] for k in ['submitted_utc','turn_rows','native_frames','required_plus_evidence_files','structural_pass','packet_stable_across_two_manifest_passes','astra_required']},indent=2))
