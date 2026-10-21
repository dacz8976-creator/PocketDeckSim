import json
from pathlib import Path
from datetime import datetime, timezone

BATCH=Path(__file__).resolve().parent
def read(path):
    try:
        return json.loads(path.read_text(encoding='utf-8-sig'))
    except (OSError,json.JSONDecodeError):
        return {}
inventory=read(BATCH/'INVENTORY.json')
rows=[]
for game in inventory['recordings']:
    stem=game['source'].split('_iOS')[0]
    folder=BATCH/stem
    lead=read(folder/'LEAD_ACCEPTANCE.json')
    assignment=read(folder/'ASSIGNMENT.json')
    hand=read(folder/'HAND_SUPPLEMENT.json')
    classification=read(folder/'CLASSIFICATION_RECEIPT.json')
    source_delivery=read(folder/'ROOT_SOURCE_VERIFICATION.json')
    submission=read(folder/'SUBMISSION.json')
    capture_status=hand.get('capture_status') or submission.get('capture_status') or submission.get('source_work_status')
    if lead.get('shared_registration')=='complete':
        state='Accepted and registered'
    elif lead.get('verdict','').startswith('accepted'):
        state='Accepted, registration pending'
    elif assignment and (folder/'REVIEW_SUPPLEMENT.md').exists() and (capture_status or '').startswith('complete'):
        state='Worker packet saved, independent check pending'
    elif assignment:
        state='In progress'
    elif source_delivery.get('status')=='delivery_read_in_progress':
        state='Source downloading for native evidence'
    elif source_delivery.get('status')=='verified_sha256_match':
        state='Source verified, reviewer queued'
    elif (folder/'LOCAL_DELIVERY_REQUEST.json').is_file():
        state='Local source requested, waiting for OneDrive'
    else:
        state='Queued'
    if game['group']=='sharpedo':
        scope='Turns '+', '.join(str(t) for t in ({'20261002_132311000':[5,11],'20261002_115323000':[13],'20261002_143837000':[5,7]}[stem]))
    elif game['group']=='wailord':
        scope='Opening and first six owner turns'
    else:
        scope='Setup and recorded turn fields'
    rows.append({'source':game['source'],'group':game['group'],'scope':scope,'status':state,'packet':str(folder),'capture_status':capture_status,'reviewer':assignment.get('reviewer'),'classification':classification.get('classification'),'excluded_from_ladder':classification.get('excluded_from_ladder'),'owner_designated_pause_games':game['group'] in ['sharpedo','wailord'],'classification_receipt':str(folder/'CLASSIFICATION_RECEIPT.json') if classification else None})
now=datetime.now(timezone.utc).isoformat()
integrity=read(BATCH/'BATCH_COMPLETION_VERIFICATION.json')
storage=read(BATCH/'STORAGE_VERIFICATION.json')
history=read(BATCH/'HISTORY_VERIFICATION.json')
all_registered=all(r['status']=='Accepted and registered' for r in rows)
all_online=set(storage.get('online_only_verified',[]))=={r['source'] for r in rows}
finished=all_registered and integrity.get('passed') is True and integrity.get('partial_check') is False and integrity.get('accepted_registered')==len(rows) and storage.get('passed') is True and storage.get('partial_check') is False and all_online and history.get('passed') is True
(BATCH/'BATCH_ASSIGNMENT.json').write_text(json.dumps({**read(BATCH/'BATCH_ASSIGNMENT.json'),'status':'complete' if finished else 'accepted_final_verification_pending' if all_registered else 'retrospective_batch_in_progress','updated_utc':now,'active_supplement_assignments':[r for r in rows if r['status'] not in ['Queued','Accepted and registered']],'completed_supplements':[r['source'] for r in rows if r['status']=='Accepted and registered']},indent=2),encoding='utf-8')
(BATCH/'BATCH_PROGRESS.json').write_text(json.dumps({'updated_utc':now,'active_recordings':16,'approved_limit':19,'corrected_guide_used':True,'recordings':rows},indent=2),encoding='utf-8')
text='# Retrospective review batch\n\n'+('Completed: all sixteen selected recordings have separate supplements, independent Sol acceptance, shared registration and verified online-only storage.\n\n' if finished else 'Current progress, updated '+now+'. Queued and in-progress recordings are still unfinished.\n\n')
text+='The corrected guide requires sixteen recordings: five uncertain hands across three Sharpedo games, the opening and first six owner turns in two Wailord games, and eleven selected historical recordings. This stays within the approved nineteen-recording limit. Wailord 020315, 020920 and 023418 are already rebuilt and excluded; the separate 26-recording Auto set and rule-test recordings are outside this batch. Accepted outcomes and original packets are preserved. Under the owner\'s later clarification, any visible Auto option identifies a computer battle even if off. These selected recordings are still processed, but confirmed cases are excluded from ladder totals and kept in [computer battle history](../../COMPUTER_BATTLE_HISTORY.md). Auto enabled state and individual action authorship are recorded separately.\n\n| Source | Addition | Status | Classification correction | Readable packet |\n|---|---|---|---|---|\n'
for row in rows:
    folder=BATCH/row['source'].split('_iOS')[0]
    links=[]
    for name,label in [('REVIEW_SUPPLEMENT.md','Supplement'),('TURN_TABLE.md','Turn table'),('HAND_SUPPLEMENT.json','Hand data')]:
        if (folder/name).is_file():
            links.append('['+label+']('+folder.name+'/'+name+')')
    destination='Computer battle; excluded from ladder' if row['excluded_from_ladder'] else 'Pause Games; excluded from ladder by owner designation' if row['owner_designated_pause_games'] else 'Ladder classification retained; exact mode limits in packet'
    text += '| `'+row['source']+'` | '+row['scope']+' | '+row['status']+' | '+destination+' | '+'; '.join(links)+' |\n'
sharpedo_rows=[r for r in rows if r['group']=='sharpedo']
if all(r['status']=='Accepted and registered' for r in sharpedo_rows):
    text+='\nThe five uncertain Sharpedo starting hands are now supported by native preplay evidence. Card names below follow the independently accepted supplements; exact card printings remain unassigned.\n\n| Recording | Owner turn | Starting hand, left to right |\n|---|---|---|\n'
    text+='| [132311](20261002_132311000/REVIEW_SUPPLEMENT.md) | 5 | Lucky Ice Pop; Cyrus; Alolan Ninetales ex; Misty; Irida; Mega Sharpedo ex |\n'
    text+='| [132311](20261002_132311000/REVIEW_SUPPLEMENT.md) | 11 | Cyrus; Misty; Irida; Alolan Vulpix; Copycat; Elegant Cape |\n'
    text+='| [115323](20261002_115323000/REVIEW_SUPPLEMENT.md) | 13 | Cyrus; Alolan Ninetales ex |\n'
    text+='| [143837](20261002_143837000/REVIEW_SUPPLEMENT.md) | 5 | Mega Sharpedo ex; Lucky Ice Pop; Copycat; Poké Ball |\n'
    text+='| [143837](20261002_143837000/REVIEW_SUPPLEMENT.md) | 7 | Mega Sharpedo ex; Lucky Ice Pop; Copycat; Misty |\n'
wailord_rows=[r for r in rows if r['group']=='wailord']
if all(r['status']=='Accepted and registered' for r in wailord_rows):
    text+='\nBoth Wailord packets add the opening and the first six owner hands. [021402](20261002_021402000/REVIEW_SUPPLEMENT.md) opens with Poké Ball, Pokémon Center Lady, Heavy Helmet, Wailmer and Irida. [022135](20261002_022135000/REVIEW_SUPPLEMENT.md) opens with Lucky Ice Pop, Heavy Helmet, Professor\'s Research, Lucky Ice Pop and Wailmer. In 022135 turn 1, the Indeedee ex draw is directly readable, but its settled position in a five-card fan is unavailable.\n'
text+='\nEach finished packet includes source-bound native hand evidence and explicit observed/inferred/unavailable fields. Independent Sol checks and lead acceptance are separate from deterministic JSON/file checks. Exact token/dollar usage is unavailable unless measured. No duplicate external game entries are created.\n'
text+='\nFor full-turn supplements, TURN_TABLE.json keeps setup plus one row per recorded turn with the same column names, and retains the original turn rows without information loss. The targeted Sharpedo packets contain only the five requested hands. Wailord observations beyond the opening and first six owner turns remain inherited from the accepted reviews.\n'
text+='\nHidden opponent cards and unrecorded information remain unknown. The exact historical 20-card lists for the eleven older recordings are unavailable; current deck lists were not substituted. Reduced one-frame-per-second scans locate events and have explicit limits for subsecond prompts. Native captures, requested times and measured frame times are distinguished in each packet.\n'
if finished:
    exports=read(BATCH/'TURN_TABLE_EXPORT_VERIFICATION.json').get('exports',[])
    text+='\nThe standard exports contain '+str(len(exports))+' full turn tables, '+str(sum(e['turns'] for e in exports))+' recorded-turn rows and '+str(sum(e['setup_rows'] for e in exports))+' setup rows. Each JSON export retains its original structured turn rows without information loss.\n'
    text+='\nFinal checks confirmed all '+str(integrity['original_accepted_files_checked'])+' original accepted packet files unchanged, all sixteen selected sources still in Reviewed, and all sixteen online-only with no local movie allocation. No originals were deleted. See [completion verification](BATCH_COMPLETION_VERIFICATION.json), [table export verification](TURN_TABLE_EXPORT_VERIFICATION.json), [history verification](HISTORY_VERIFICATION.json) and [storage verification](STORAGE_VERIFICATION.json).\n'
    totals=history['historical_ladder_total']
    text+='\nThe selected pre-season ladder history now contains '+str(totals['games'])+' games, '+str(totals['wins'])+' wins and '+str(totals['losses'])+' losses. The Ogerpon/Whimsicott computer win from 012720 is retained separately, so it does not contribute to those totals. Rotom\'s opponent name is corrected to the source-visible name; all results remain unchanged.\n'
    text+='\nThe Manectric 023151 source read succeeded after the owner confirmed its OneDrive download. Its SHA matched the frozen accepted source, and the new native evidence and final independent check passed. The earlier file-access failure is preserved in the delivery receipts and does not establish video corruption.\n'
    text+='\nEarlier ladder results stay in [pre-season history](../../LADDER_HISTORY_PRE_2026-09-15.md). The live season beginning September 15 received no duplicate games or result changes from this supplemental review.\n'
(BATCH/'BATCH_REPORT.md').write_text(text,encoding='utf-8')
print(json.dumps({'active':16,'statuses':{s:sum(r['status']==s for r in rows) for s in sorted({r['status'] for r in rows})}}))
