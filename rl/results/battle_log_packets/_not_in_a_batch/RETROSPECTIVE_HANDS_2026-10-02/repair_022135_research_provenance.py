"""Correct direct reveal provenance identified by the independent native-frame check."""
import json, shutil
from pathlib import Path
BATCH=Path(__file__).resolve().parent
folder=BATCH/'20261002_022135000'
snapshot=folder/'worker_submission_before_research_provenance_repair'
snapshot.mkdir(exist_ok=False)
names=['HAND_SUPPLEMENT.json','TURN_LEDGER.json','TURN_EVIDENCE.json','PAUSE_GAME.json','UNCERTAINTIES.json','REVIEW_SUPPLEMENT.md']
for name in names:
    shutil.copy2(folder/name,snapshot/name)
old='Research first draw Poké Ball is directly visible at52s; Pokémon Center Lady is directly present by54s after the quick Poké Ball play. Its identity as the second Research addition is transaction-reconciled, not an isolated readable second-draw animation.'
new='Native52s directly displays Pokémon Center Lady as the current enlarged Research reveal, with Poké Ball already in the fan. Both identities are directly observed; Ball-first order follows the append state preceding the displayed second card. Requested52s is not measured decoded frame PTS.'
def replace_limits(value):
    if isinstance(value,str):
        return value.replace(old,new)
    if isinstance(value,list):
        return [replace_limits(v) for v in value]
    if isinstance(value,dict):
        return {k:replace_limits(v) for k,v in value.items()}
    return value
for name in names[:-1]:
    data=replace_limits(json.loads((folder/name).read_text(encoding='utf-8-sig')))
    if name in ['HAND_SUPPLEMENT.json','TURN_LEDGER.json']:
        row=next(r for r in data['target_rows' if name.startswith('HAND') else 'turns'] if r['turn_number']==1)
        draw=next(d for d in row['draws_and_searches'] if d.get('caused_by')=="Professor's Research")
        first,second=draw['cards_in_reveal_order']
        first['basis']='direct_fan_identity_with_first_card_order_from_second_reveal_append_state'
        first['limit_reason']='At52 Poké Ball is already in the fan; this cited frame is not its isolated enlarged reveal.'
        second.update(basis='direct_enlarged_native_reveal',evidence_ids=['f_0052.00'],timestamp_seconds=52,limit_reason='Requested source time retained; actual decoded PTS unmeasured.')
        draw['reveal_order_basis']='Ball already appended while CenterLady is displayed as current second Research reveal.'
        draw['limit_reason']=new
    if name=='TURN_EVIDENCE.json':
        def add_observation(value):
            if isinstance(value,dict):
                if value.get('evidence_id')=='f_0052.00':
                    value['observation']='Enlarged Pokémon Center Lady Research reveal; Poké Ball already in fan with two Lucky Ice Pops.'
                for child in value.values():
                    add_observation(child)
            elif isinstance(value,list):
                for child in value:
                    add_observation(child)
        add_observation(data)
    (folder/name).write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')
review=(folder/'REVIEW_SUPPLEMENT.md').read_text(encoding='utf-8')
old_para='Turn1 Research adds Poké Ball and Pokémon Center Lady. Poké Ball is directly visible at52s; the second addition is reconciled from the new Center Lady observed by54s, after the quick Ball play.'
new_para='Turn1 Research adds Poké Ball and Pokémon Center Lady. Native52s directly shows Center Lady enlarged as the current reveal, with Ball already in the fan. Ball-first order follows this append state; both identities are directly observed.'
assert old_para in review
(folder/'REVIEW_SUPPLEMENT.md').write_text(review.replace(old_para,new_para).replace(old,new),encoding='utf-8')
print('Corrected direct Research reveal provenance across six files; worker submission preserved.')
