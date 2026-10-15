"""One source read while OneDrive delivers an upcoming authorized review."""
import argparse, hashlib, json, time
from datetime import datetime, timezone
from pathlib import Path
BATCH=Path(__file__).resolve().parent
ROOT=BATCH.parents[1]
p=argparse.ArgumentParser()
p.add_argument('stem',choices=['20260908_012720000','20260908_021327000','20260929_020916000','20260929_002539000','20260928_200654000','20260909_023151000'])
p.add_argument('--attempt-number',type=int,choices=[1,2,3],default=1)
a=p.parse_args()
name=a.stem+'_iOS.MP4'
folder=BATCH/a.stem
receipt=folder/'ROOT_SOURCE_VERIFICATION.json'
if receipt.exists():
    raise SystemExit('Receipt exists; do not duplicate a source read automatically. Preserve a completed failed attempt before an explicitly coordinated retry.')
prior_receipt=folder/('ROOT_SOURCE_VERIFICATION_ATTEMPT_'+str(a.attempt_number-1)+'.json')
if a.attempt_number in [2,3]:
    prior=json.loads(prior_receipt.read_text(encoding='utf-8-sig'))
    assert prior['status']=='source_access_error', 'Only a completed failed first read may be retried'
if a.attempt_number==3:
    delivery=json.loads((folder/'LOCAL_DELIVERY_REQUEST.json').read_text(encoding='utf-8-sig'))
    assert delivery['exit_code']==0, 'Third read requires a changed delivery state after explicit OneDrive request'
if a.stem == '20260909_023151000':
    old=Path(r'C:\Users\dacz8\Projects\Pocket Deck Lab\Boss Folder\video-review-coordinator-2026-09-09\previously-finished-audit\battle-023151\SOURCE.json')
elif a.stem in ['20260929_020916000','20260929_002539000','20260928_200654000']:
    old=ROOT/'Recording_QA'/(a.stem+'_iOS_sol')/'SOURCE.json'
else:
    old=ROOT/'Recording_QA'/('20260908_012720_v7_review' if '012720' in a.stem else '20260908_021327_v7_review')/'final_packet'/'SOURCE.json'
frozen=json.loads(old.read_text(encoding='utf-8-sig'))
frozen_hash=frozen.get('sha256') or frozen.get('source_sha256')
frozen_bytes=frozen.get('bytes') or frozen.get('source_size_bytes')
assert frozen_hash and frozen_bytes, 'Frozen identity is incomplete'
source=ROOT/'Reviewed'/name
before=source.stat()
start=time.monotonic()
data={'source':name,'current_path':str(source),'frozen_source_json':str(old),'expected_sha256':frozen_hash.lower(),
 'expected_bytes':frozen_bytes,'started_utc':datetime.now(timezone.utc).isoformat(),'status':'delivery_read_in_progress',
 'original_content_read_attempts':1,'scope':'Source verification for upcoming authorized hand/turn field supplement; no review acceptance'}
data['attempt_number']=a.attempt_number
if a.attempt_number in [2,3]:
    data['previous_attempt_receipt']=str(prior_receipt)
    data['total_attempts_including_prior_failure']=a.attempt_number
receipt.write_text(json.dumps(data,indent=2),encoding='utf-8')
try:
    digest=hashlib.sha256()
    with source.open('rb') as stream:
        while chunk:=stream.read(16*1024*1024):
            digest.update(chunk)
    after=source.stat()
    actual=digest.hexdigest()
    match=actual==data['expected_sha256'] and before.st_size==after.st_size==frozen_bytes and before.st_mtime_ns==after.st_mtime_ns
    data.update(status='verified_sha256_match' if match else 'identity_mismatch',actual_sha256=actual,actual_bytes=after.st_size,source_stable_during_read=before.st_mtime_ns==after.st_mtime_ns)
except OSError as error:
    data.update(status='source_access_error',error_type=type(error).__name__,error=str(error))
data.update(finished_utc=datetime.now(timezone.utc).isoformat(),wall_seconds=round(time.monotonic()-start,2))
receipt.write_text(json.dumps(data,indent=2),encoding='utf-8')
print(json.dumps(data))
if data['status']!='verified_sha256_match':
    raise SystemExit(1)
