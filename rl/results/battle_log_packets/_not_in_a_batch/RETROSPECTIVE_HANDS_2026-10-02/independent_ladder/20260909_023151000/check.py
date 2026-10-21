import json,hashlib,datetime
from pathlib import Path
from PIL import Image
BASE=Path(r'C:\Users\dacz8\OneDrive\Desktop\Battle Logs\Recording_QA\RETROSPECTIVE_HANDS_2026-10-02')
P=BASE/'20260909_023151000'
C=BASE/'independent_ladder'/'20260909_023151000'
def read(n): return json.loads((P/n).read_text(encoding='utf-8-sig'))
S=read('SUBMISSION.json'); E=read('TURN_EVIDENCE.json')
hashes=[]
for r in S['submitted_files']:
 p=Path(r['path']); actual=hashlib.sha256(p.read_bytes()).hexdigest()
 hashes.append({'path':str(p),'expected':r['sha256'],'actual':actual,'matches':actual==r['sha256']})
frames=[]
for r in E['frames']:
 p=Path(r['full_frame_path'])
 with Image.open(p) as im: dims=list(im.size)
 actual=hashlib.sha256(p.read_bytes()).hexdigest()
 frames.append({'id':r['evidence_id'],'path':str(p),'dimensions':dims,'hash_matches':actual==r['full_frame_sha256'],'source_matches':r['source_sha256']==S['source_sha256']})
C.mkdir(parents=True,exist_ok=True)
(C/'ASSIGNMENT.json').write_text(json.dumps({'checker':'Sol, different producer','source':S['source'],'source_sha256':S['source_sha256'],'producer_freeze':S['frozen_utc'],'scope':'Independent check of setup, all five owner hand starts/endings and offsets, all nine turns actions/boards/Zones/fans, search concealment, warning and terminal evidence; preserve producer files. No source hash or decode.','registered_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'in_progress'},indent=2),encoding='utf-8')
(C/'HASH_VALIDATION.json').write_text(json.dumps({'source_movie_read':False,'submitted_files':hashes,'frames':frames,'all_submission_hashes_match':all(x['matches'] for x in hashes),'all_frame_hashes_match':all(x['hash_matches'] for x in frames)},indent=2),encoding='utf-8')
print('files',len(hashes),'match',all(x['matches'] for x in hashes),'frames',len(frames),'match',all(x['hash_matches'] for x in frames))
print([(x['evidence_id'],x.get('requested_source_seconds'),x['full_frame_path'].split('\\')[-1]) for x in E['frames']])
print('ledger keys',read('TURN_LEDGER.json').keys())
