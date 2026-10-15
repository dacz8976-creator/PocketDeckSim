import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
p=Path(__file__).resolve().parent
names=['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
receipt={'source_video':'20261013_022530000_iOS.MP4','source_sha256':'02714096351099424338ac83d3f529ef4f0e6979a978a50f48c5ff505a2b6cb7','frozen_utc':datetime.now(timezone.utc).isoformat(),'reviewer':'/root/pause_20261013_022530000_iOS','actual_worker':'/root/newest_022530','files':{n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in names},'file_sizes':{n:(p/n).stat().st_size for n in names},'scope':'Eight final authored review files. Independent visual acceptance remains separate.','status':'submitted_for_independent_acceptance','correction_history':'Copycat named-hand anchor and unresolved arrival order, ordinary prose spacing, owner hand arithmetic, and turn 6 Rocky Helmet resolution corrected before this freeze.'}
(p/'REVIEW_PACKET_HASHES.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ed=json.loads((p/'TURN_EVIDENCE.json').read_text(encoding='utf-8'))
paths=set()
for frame in ed['frames']:
    paths.add(frame['full_frame_path'])
    paths.add(frame['bottom_crop']['path'])
    paths.add(frame['top_crop']['path'])
eh={'source_sha256':receipt['source_sha256'],'frozen_utc':receipt['frozen_utc'],'scope':'All native full frames and crops referenced in TURN_EVIDENCE.json, at authored packet freeze.','files':{n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in sorted(paths)}}
(p/'TURN_EVIDENCE_HASHES.json').write_text(json.dumps(eh,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'eight_files':len(receipt['files']),'evidence_files':len(eh['files']),'frozen_utc':receipt['frozen_utc']},indent=2))
