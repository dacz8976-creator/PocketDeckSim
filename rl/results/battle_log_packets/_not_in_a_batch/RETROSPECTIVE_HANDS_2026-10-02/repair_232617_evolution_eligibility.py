"""Fill the one source-supported conditional effect missing from the submitted row."""
import json, shutil
from pathlib import Path
BATCH=Path(__file__).resolve().parent
folder=BATCH/'20260907_232617000'
snapshot=folder/'worker_submission_before_evolution_eligibility_repair'
snapshot.mkdir(exist_ok=False)
names=['TURN_LEDGER.json','TURN_EVIDENCE.json','REVIEW_SUPPLEMENT.md','UNCERTAINTIES.json']
for name in names:
    shutil.copy2(folder/name,snapshot/name)
ledger=json.loads((folder/'TURN_LEDGER.json').read_text(encoding='utf-8-sig'))
row=next(r for r in ledger['turns'] if r['turn_number']==2)
active=row['board_at_start']['owner']['active']
assert active['name']=='Eevee' and active['active_effects'] is None
active['active_effects']=[{'name':'Boosted Evolution','kind':'conditional_evolution_eligibility',
 'description':'Active Eevee can evolve during the first owner turn or the turn it is played.',
 'currently_eligible':True,'eligibility_basis':'Native52 printed Ability text plus observed Active Eevee and first owner turn after going second.',
 'basis':'direct_native_ability_text_with_condition_applied_to_observed_phase','evidence_ids':['f52.000'],
 'limit_reason':'Applies to this turn2 starting Active Eevee. No ongoing eligibility is asserted for later benched Eevee or the evolved Jolteon ex.'}]
(folder/'TURN_LEDGER.json').write_text(json.dumps(ledger,indent=2,ensure_ascii=False),encoding='utf-8')
evidence=json.loads((folder/'TURN_EVIDENCE.json').read_text(encoding='utf-8-sig'))
frame=next(f for f in evidence['frames'] if f['evidence_id']=='f52.000')
frame['observed_ability_text_summary']='Boosted Evolution permits evolution during the first owner turn or the turn Eevee is played, while Eevee is Active.'
frame['ability_eligibility_application']='Owner turn2 is the first owner turn and Eevee is Active. Later badge views alone are not treated as continuing eligibility.'
(folder/'TURN_EVIDENCE.json').write_text(json.dumps(evidence,indent=2,ensure_ascii=False),encoding='utf-8')
with (folder/'REVIEW_SUPPLEMENT.md').open('a',encoding='utf-8') as out:
    out.write('\nIndependent field repair: At the start of owner turn2, Active Eevee has conditional Boosted Evolution eligibility. Native52s shows the printed Ability permitting evolution on the first owner turn or the turn it is played while Active. This condition is included only in that starting-board row; no continuing eligibility is asserted for later benched Eevee.\n')
uncertainty=json.loads((folder/'UNCERTAINTIES.json').read_text(encoding='utf-8-sig'))
repair={'turn_number':2,'field':'board_at_start.owner.active.active_effects','source':'f52.000',
 'reason':'Conditional first-owner-turn evolution eligibility added from visible Ability text and observed starting state.',
 'worker_submission_preserved':str(snapshot)}
if isinstance(uncertainty,dict):
    uncertainty['independent_field_repair']=repair
else:
    uncertainty.append(repair)
(folder/'UNCERTAINTIES.json').write_text(json.dumps(uncertainty,indent=2,ensure_ascii=False),encoding='utf-8')
print('Added turn2 conditional evolution eligibility; worker submission preserved.')
