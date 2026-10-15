import json,hashlib,re
from pathlib import Path
from datetime import datetime,timezone
p=Path(__file__).resolve().parent
names=['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
for name in ['REVIEW.md','COVERAGE.md']:
 for target in re.findall(r'\]\(([^)]+)\)',(p/name).read_text(encoding='utf-8')):
  assert (p/target).exists(),target
d=json.loads((p/'TURN_LEDGER.json').read_text(encoding='utf-8'))
assert len(d['turns'])==16
assert [x['timestamp_seconds'] for x in d['turns'][0]['draws_and_searches'][1]['cards_in_reveal_order']]==[58,58.5,59.5,60.5]
assert [x['timestamp_seconds'] for x in d['turns'][2]['draws_and_searches'][1]['cards_in_reveal_order']]==[126,127]
assert d['turns'][2]['timing']['first_voluntary_move_seconds']==119
assert d['turns'][10]['timing']['before_end_action_seconds']==430
assert 'Supporter' in d['turns'][10]['plays_in_order'][4]['prompt_text']
e=json.loads((p/'TURN_EVIDENCE.json').read_text(encoding='utf-8'))
f=next(x for x in e['frames'] if x['evidence_id']=='f0322.00')
assert f['unzoomed'] is False and f['hand_spread'] is False
rows=[]
for name in names:
 b=(p/name).read_bytes();rows.append(dict(file=name,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b)))
out=dict(schema='review-packet-hashes-v1',source_video='20261013_030351000_iOS.MP4',source_sha256='d0a221cd236c620f467bbf34ad8078fd59c72323a7dca71a4af344f0489c6c7f',frozen_at_utc=datetime.now(timezone.utc).isoformat(),status='final_eight_frozen_pending_independent_acceptance',files=rows)
(p/'REVIEW_PACKET_HASHES.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out,indent=2))
