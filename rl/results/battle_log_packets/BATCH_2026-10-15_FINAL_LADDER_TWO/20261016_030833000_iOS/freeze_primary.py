from pathlib import Path
import json, hashlib, datetime, re

p=Path(__file__).parent
e=p/'evidence'
native=sorted(e.glob('t*.jpg'))
overview=sorted(e.glob('overview_*.jpg'))
overview_sheets=sorted(e.glob('contact_*.jpg'))+[e/'early_contact.jpg']
# Only files actually reviewed; trailing continuous extraction is auxiliary.
dense=[e/f'dense_{i:04d}.jpg' for i in range(1,67)]
dense_sheets=[e/f'dense_sheet_{i:02d}.jpg' for i in range(1,8)]
native_sheets=sorted(e.glob('native_sheet_*.jpg'))
used=native+overview+overview_sheets+dense+dense_sheets+native_sheets
assert all(f.is_file() for f in used)
evidence={
  'source_filename':'20261016_030833000_iOS.MP4',
  'source_sha256':'6b96796ba0645aab33f131c8bd6b62a23951406662a33f456911e20f2d51e541',
  'reviewed_evidence_files':[str(f.relative_to(p)).replace('\\','/') for f in used],
  'native_frame_count':len(native),
  'dense_raw_reviewed_count':66,
  'excluded_auxiliary':['evidence/dense_0067.jpg and all later dense_####.jpg','evidence/dense_sheet_08.jpg and all later dense sheets'],
  'reason':'Explicit stable reviewed subset; bounded auxiliary extraction may still append redundant files.'
}
(p/'EVIDENCE_USED.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
base=['SOURCE.json','PROBE.json','LOCAL_METADATA.json','ASSIGNMENT.json','ASSIGNMENT_REGISTRATION.json','REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','EVIDENCE_USED.json','make_sheets.py','freeze_primary.py']
fs=[p/f for f in base]+used
rows=[]
for f in fs:
    raw=f.read_bytes()
    rows.append({'path':str(f.relative_to(p)).replace('\\','/'),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
out={
  'source_filename':evidence['source_filename'], 'source_sha256':evidence['source_sha256'],
  'reviewer':'/root/ladder_030833','model':'gpt-6.1-sol','effort':'high',
  'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'scope':'Primary source/probe/assignment/review and explicit stable reviewed evidence only',
  'excluded':['REVIEW_PACKET_HASHES.json','independent_sol','lead/external/completion/archive files']+evidence['excluded_auxiliary'],
  'files':{row['path']:row['sha256'] for row in rows},
  'file_details':rows
}
(p/'REVIEW_PACKET_HASHES.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'frozen_files':len(rows),'native_frames':len(native),'reviewed_dense_frames':len(dense)}))
