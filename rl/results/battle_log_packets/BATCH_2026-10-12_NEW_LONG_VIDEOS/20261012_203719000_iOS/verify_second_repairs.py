import json, hashlib
from pathlib import Path
p=Path(__file__).parent
names=['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
old=p/'before_second_independent_repairs_20261012T235813Z'
ledger=json.loads((p/'TURN_LEDGER.json').read_text(encoding='utf-8'))
for n,later in [(3,True),(9,False)]:
 zone=ledger['turns'][n-1]['board_at_start']['owner']['energy_zone']
 if later:zone=zone['later_within_turn_observation']
 assert zone['this_turn']['type']=='Darkness' and zone['this_turn']['count']==1
 assert all(zone['next'][k] is None for k in ['type','count','available'])
 assert zone['limit_reason']
a=ledger['turns'][18]['plays_in_order'][0]
assert a['evidence_ids']==['f722_00','f732_00'] and a['timestamp_seconds']==723
assert ledger['turns'][18]['hand_at_start']['evidence_ids']==['f722_00']
assert len(ledger['turns'])==21
hashes={n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in names}
changed=[n for n in names if (p/n).read_bytes()!=(old/n).read_bytes()]
assert changed==['SUMMARY.json','TURN_LEDGER.json'],changed
receipt={'source_sha256':'e85ac056e49ababe79fbd0388e8b132f3cc984a5deb445390a2f4df7b0137869','review_files_sha256':hashes,'basis':'Second independent recheck repairs R2a, R2b and R3. Fresh independent acceptance pending.','before_repairs_snapshot':old.name,'changed_required_files':changed,'attachment_proof':'Native f732_00 shows Kingambit with three Darkness; f722_00 remains preplay hand/start board.'}
(p/'REVIEW_PACKET_HASHES.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,indent=2))
