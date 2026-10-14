"""Narrow correction from independent native-frame review; preserves worker submission."""
import json, shutil
from pathlib import Path
BATCH=Path(__file__).resolve().parent
folder=BATCH/'20261002_021402000'
snapshot=folder/'worker_submission_before_research_provenance_repair'
snapshot.mkdir(exist_ok=False)
names=['HAND_SUPPLEMENT.json','TURN_LEDGER.json','TURN_EVIDENCE.json','REVIEW_SUPPLEMENT.md','UNCERTAINTIES.json']
for name in names:
    shutil.copy2(folder/name,snapshot/name)
reason='Native137 shows Indeedee ex already appended in the fan and Copycat enlarged as the current Research reveal. Indeedee identity is directly observed in the fan; its first-card order is inferred from this append state preceding the displayed second card. Copycat reveal is directly observed at137 and its retained fan at139. Exact first-reveal onset is unmeasured.'
for name,key in [('HAND_SUPPLEMENT.json','target_rows'),('TURN_LEDGER.json','turns')]:
    data=json.loads((folder/name).read_text(encoding='utf-8-sig'))
    row=next(r for r in data[key] if r['turn_number']==7)
    draw=next(d for d in row['draws_and_searches'] if d['kind']=='research')
    first,second=draw['cards_in_reveal_order']
    first['basis']='direct_fan_identity_with_order_inferred_from_second_reveal_and_append_state'
    first['limit_reason']='At137 Indeedee is already in the fan; its first reveal is not directly captured in this cited frame.'
    second.update(timestamp_seconds=137,evidence_ids=['f0137.00','f0139.00'],basis='direct_enlarged_reveal_at137_and_retained_fan_at139')
    draw['reveal_order_basis']='append_state_at137_with_Copycat_displayed_as_second_Research_card'
    draw['limit_reason']=reason
    (folder/name).write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')
evidence=json.loads((folder/'TURN_EVIDENCE.json').read_text(encoding='utf-8-sig'))
def repair_refs(value):
    if isinstance(value,dict):
        if value.get('evidence_id')=='f0137.00':
            value['observation']='Research: Copycat is enlarged in its reveal while Indeedee ex is already appended to the bottom fan. This is not the first-card reveal.'
        for child in value.values():
            repair_refs(child)
    elif isinstance(value,list):
        for child in value:
            repair_refs(child)
repair_refs(evidence)
(folder/'TURN_EVIDENCE.json').write_text(json.dumps(evidence,indent=2,ensure_ascii=False),encoding='utf-8')
review=(folder/'REVIEW_SUPPLEMENT.md').read_text(encoding='utf-8')
old='Turn7 Research adds Indeedee ex, then Copycat. Indeedee is directly visible at137.00s, and Copycat is directly readable in the retained hand at139.00s after Indeedee is placed.'
new='Turn7 Research adds Indeedee ex, then Copycat. Native137.00s shows Indeedee already in the fan and Copycat enlarged as the current reveal; Indeedee-first order is inferred from this append state, with both identities directly readable. Copycat remains directly readable in the retained hand at139.00s after Indeedee is placed.'
assert old in review
(folder/'REVIEW_SUPPLEMENT.md').write_text(review.replace(old,new),encoding='utf-8')
uncertainty=json.loads((folder/'UNCERTAINTIES.json').read_text(encoding='utf-8-sig'))
if isinstance(uncertainty,dict):
    uncertainty['independent_provenance_repair']={'turn_number':7,'field':'Research pair reveal provenance','reason':reason,'worker_submission_preserved':str(snapshot)}
else:
    uncertainty.append({'turn_number':7,'reason':reason,'worker_submission_preserved':str(snapshot)})
(folder/'UNCERTAINTIES.json').write_text(json.dumps(uncertainty,indent=2,ensure_ascii=False),encoding='utf-8')
print('Corrected turn7 Research provenance; worker submission preserved.')
