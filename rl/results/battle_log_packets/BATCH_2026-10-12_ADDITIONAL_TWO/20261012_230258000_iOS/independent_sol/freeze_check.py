from pathlib import Path
import json,hashlib,sys,datetime,shutil
p=Path(__file__).resolve().parent
names=['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
status=sys.argv[1]
now=datetime.datetime.now(datetime.timezone.utc)
snapshot=p/(('accepted_' if status=='accepted' else 'rejected_')+now.strftime('%Y%m%dT%H%M%SZ'))
snapshot.mkdir()
hashes={}
for name in names:
    f=p.parent/name
    data=f.read_bytes(); hashes[name]=hashlib.sha256(data).hexdigest()
    (snapshot/name).write_bytes(data)
source=json.loads((p.parent/'SOURCE.json').read_text())
o={'checker':'/root/check_later_230258','checked_utc':now.isoformat(),'status':status,'accepted':status=='accepted','source_video':source['video_basename'],'source_sha256':source['sha256'],'source_identity_basis':'Frozen intake SOURCE.json and independently inspected source-derived native frames; source not rehashed by checker','scope':'Bounded independent visual checks plus all eight current packet files reconciled','checked_input_sha256':hashes,'accepted_input_sha256':hashes if status=='accepted' else {},'snapshot_directory':str(snapshot),'source_checks':'INDEPENDENT_SOURCE_CHECKS.md','qr_check':'QR_CHECK.json','findings':sys.argv[2:],'limitations':['Hidden opponent draws/searches are not identified from later plays.','Neither opened discard pile is shown.','Exact artwork/rarity and specific queue remain unestablished.','Source-local requested seek times are not measured frame PTS.'],'no_shared_index_or_external_mutation':True}
(snapshot/'CHECK_RESULT.json').write_text(json.dumps(o,indent=2)+'\n')
if status=='accepted':(p/'CHECK_RESULT.json').write_text(json.dumps(o,indent=2)+'\n')
print(json.dumps({'status':status,'snapshot':str(snapshot),'hashes':hashes}))
