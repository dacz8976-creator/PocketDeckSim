import json, shutil
from pathlib import Path

BATCH=Path(__file__).resolve().parent
folder=BATCH/'20261002_115323000'
backup=folder/'worker_submission_before_endpoint_repair'
backup.mkdir(exist_ok=True)
for name in ['HAND_SUPPLEMENT.json','TURN_EVIDENCE.json','REVIEW_SUPPLEMENT.md','UNCERTAINTIES.json']:
    destination=backup/name
    if not destination.exists():
        shutil.copyfile(folder/name,destination)
path=folder/'HAND_SUPPLEMENT.json'
data=json.loads(path.read_text(encoding='utf-8-sig'))
turn=data['turns'][0]
end=turn['owner_hand_end']
end['cards_left_to_right'][0].update(basis='matching_artwork_observation_and_identity_continuity_inference',evidence_ids=['e461','e478'],limit_reason='Printed Cyrus header is obscured by the board zoom at 478; one-card count and matching artwork are observed, identity is inferred by continuity from clear preplay461.')
end['basis']='Observed single-card count and matching artwork before attack; Cyrus identity continuity from clear461 fan.479/481 are after-trigger corroboration only.'
end['status']='observed_count_with_identity_continuity_inference'
end['limit_reason']='478 board-card zoom hides the printed Cyrus header; later479/481 cannot be treated as before-attack views.'
turn['hand_count_reconciliation']['basis']='Inference from observed start/end counts and card continuity; identity is not inferred from arithmetic alone.'
data['lead_endpoint_repair']='Independent Sol check corrected the readability claim only; the directly observed461 starting hand is unchanged.'
path.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')
path=folder/'TURN_EVIDENCE.json'
data=json.loads(path.read_text(encoding='utf-8-sig'))
for frame in data['frames']:
    if frame['evidence_id']=='e478':
        frame['observation']='Ninetales board-card attack-selection zoom; one remaining hand card with matching Cyrus artwork is visible, while its printed name/header is obscured.'
        frame['suitability_or_limit']='Before-attack count1 and matching artwork observed. Cyrus identity uses continuity from clear461; exact attack trigger is between478 and479.'
path.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')
path=folder/'UNCERTAINTIES.json'
data=json.loads(path.read_text(encoding='utf-8-sig'))
data['unresolved_facts'].append({'field':'printed_owner_ending_hand_name_at478','reason':'Board zoom obscures the printed header. Count1 and matching artwork are observed; Cyrus identity is continuity inference from clear461.479/481 remain after-trigger corroboration.','material_to_target_starting_hand':False})
path.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')
path=folder/'REVIEW_SUPPLEMENT.md'
text=path.read_text(encoding='utf-8-sig')
text=text.replace('At 478 the board-card attack selection zoom leaves the single Cyrus hand card readable.','At 478 the board-card attack selection zoom hides the printed header of the single remaining card. Its count and matching Cyrus artwork are observed; the identity is a continuity inference from the clear 461 fan. Later 479/481 views are after-trigger corroboration only.')
text=text.replace('Starting count 2 and ending count 1 are observed.','Starting count 2 and ending count 1 are observed. The ending card name at 478 uses the continuity inference above.')
text=text.replace('Cyrus, count 1, at before-attack view 478','One card, count 1 at 478; Cyrus identity by artwork and continuity')
text += '\n\nIndependent Sol endpoint correction: the printed Cyrus header at 478 is covered, so this supplement labels the observed count/artwork and identity continuity inference separately. The requested Ninetales starting hand remains directly observed. Original worker wording is preserved in worker_submission_before_endpoint_repair.\n'
path.write_text(text,encoding='utf-8')
print('Corrected endpoint basis in separate115323 supplement; worker submission preserved.')
