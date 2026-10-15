import hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone

B=Path(__file__).resolve().parent
P=B/'20261002_205731000_iOS_auto_sol'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifest=read(P/'GUIDE_UPDATE_SUBMISSION.json')
original=P/'guide_submission_before_timing_repair'
assert not original.exists()
original.mkdir()
for name,expected in manifest['files'].items():
 assert sha(P/name)==expected
 shutil.copy2(P/name,original/name)
shutil.copy2(P/'GUIDE_UPDATE_SUBMISSION.json',original/'GUIDE_UPDATE_SUBMISSION.json')
frames={f['evidence_id']:f['actual_frame_seconds_if_measured'] for f in read(P/'EXTRACTION_MANIFEST.json')}
inventory=read(P/'SEEN_CARD_INVENTORY.json')
changed=0
for card in inventory['cards']:
 for occurrence in card['occurrences']:
  ids=occurrence['evidence_ids']
  times=[frames[i] for i in ids if i in frames]
  occurrence['evidence_frame_seconds_range']=[min(times),max(times)] if times else None
  if occurrence['context'] in ('owner_hand_end','board_after'):
   occurrence['source_seconds']=None
   occurrence['timestamp_basis']='Composite accepted end-state evidence spanning the listed measured frames. The earliest frame can precede this card entering that end state; no exact occurrence instant is asserted. Consult the native anchors and ordered actions.'
   changed+=1
  else:
   occurrence['timestamp_basis']='Named action/reveal time or selected snapshot; listed evidence anchors retain their separate measured PTS.'
 for observation in card['simultaneous_hand_duplicate_observations']:
  times=[frames[i] for i in observation['evidence_ids'] if i in frames]
  observation['evidence_frame_seconds_range']=[min(times),max(times)] if times else None
  observation['basis']='Composite accepted end-hand state; no single instant assigned to this evidence group.' if observation['context']=='owner_hand_end' else 'Selected start-hand snapshot supports simultaneous faces.'
inventory['timing_limit']='Composite owner_hand_end and board_after observations have null source_seconds and measured evidence ranges. Their earliest anchor is not an exact card appearance time.'
save(P/'SEEN_CARD_INVENTORY.json',inventory)
for name in ('SEEN_CARD_INVENTORY.md','GUIDE_UPDATE_SUPPLEMENT.md'):
 with (P/name).open('a',encoding='utf-8') as f:
  f.write('\nComposite inventory end-state observations use null exact occurrence times and separate measured evidence-frame ranges. The earliest frame in a group can precede that card entering the end state; it is not labelled as its appearance time. Single start snapshots and named draws/actions remain separately timed.\n')
manifest['files']={name:sha(P/name) for name in manifest['files']}
manifest['timing_repair_utc']=datetime.now(timezone.utc).isoformat()
manifest['preserved_prior_manifest']='guide_submission_before_timing_repair/GUIDE_UPDATE_SUBMISSION.json'
manifest['preserved_prior_manifest_sha256']=sha(original/'GUIDE_UPDATE_SUBMISSION.json')
save(P/'GUIDE_UPDATE_SUBMISSION.json',manifest)
for name,expected in read(P/'SUBMISSION.json')['files'].items():assert sha(P/name)==expected
print(json.dumps({'composite_occurrences_clarified':changed,'manifest_sha256':sha(P/'GUIDE_UPDATE_SUBMISSION.json'),'original_core_unchanged':True}))
