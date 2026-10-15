"""Prepare source-qualified deck definitions for the existing Pause Games artifact."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

BATCH=Path(__file__).resolve().parent
KNOWN={
    '20261004_213625000_iOS':('Butterfree / Accelgor','New deck 24','New Grass deck; absent from the nine current live deck choices.'),
    '20261004_215749000_iOS':('Mega Blaziken / Combusken','New deck 1','Separate variant: Combusken x2 replaces Rare Candy x2 in the current tournament list.'),
    '20261005_003547000_iOS':('Wailord / Mega Sharpedo / Suicune','New deck 6','New Water deck; distinct from Wailord / Indeedee wall and Draft A: Shark Tempo.'),
    '20261005_031138000_iOS':('Hatterene / Aromatisse / Togekiss','New deck 6','New Psychic deck; distinct from Draft C Meowstic / Hatterene v2. The filmed slot label was reused for a different deck.'),
    '20261005_032023000_iOS':("Aegislash / Tinkaton ex / Team Rocket's Tinkaton",None,"Metal variant with one Tinkaton ex and one Team Rocket's Tinkaton."),
    '20261005_032857000_iOS':("Aegislash / Team Rocket's Tinkaton",None,"Metal revision with two Team Rocket's Tinkaton and no Tinkaton ex."),
    '20261005_033529000_iOS':('Skarmory ex / Aegislash / Orthworm',None,'Distinct Metal list with two Skarmory ex and one Orthworm.'),
    '20261005_034953000_iOS':('Aegislash / Melmetal ex / Magnezone',None,'Distinct Metal list; preserves two Honedge, Doublade and Aegislash versions by semantic identity.'),
    '20261005_123812000_iOS':('Nidoking / Nihilego / Darkrai ex (two Darkrai)',None,'Darkness variant with two Darkrai ex.'),
    '20261005_124532000_iOS':('Nidoking / Nihilego / Darkrai ex (one Darkrai)',None,'Darkness revision with one Darkrai ex; Trainer composition also preserved from this QR.'),
    '20261005_183108000_iOS':('Scolipede / Mega Sableye ex',None,'Distinct Darkness list with two Mega Sableye ex.'),
    '20261006_012927000_iOS':('Terapagos ex / Silvally / Persian',None,'Distinct list with Snorlax ex and Grass, Darkness and Metal Energy; two Meowth versions preserved.'),
    '20261006_020518000_iOS':('Conkeldurr / Sandslash / Hitmonchan ex',None,'Distinct Fighting list; two Conkeldurr and Sandslash versions preserved.'),
}
entries=[]
for packet_name,(label,filmed_label,note) in KNOWN.items():
    packet=BATCH/packet_name
    qr_path=packet/'QR_DECODE.json'
    if not qr_path.exists(): qr_path=packet/'QR_DECODE_RECEIPT.json'
    if not qr_path.exists():
        candidates=list((packet/'qr_intake').glob('QR_DECODE_*.json'))
        assert len(candidates)==1
        qr_path=candidates[0]
    qr=json.loads(qr_path.read_text(encoding='utf-8'))
    source=json.loads((packet/'SOURCE.json').read_text(encoding='utf-8'))
    assert qr['source_sha256']==source['sha256'] and qr['card_slot_count']==20 and qr['decoded']['roundtrip']
    assert all(c['name'] and len(c['functional_ids'])==1 for c in qr['cards'])
    image=Path(qr['retained_image'])
    assert hashlib.sha256(image.read_bytes()).hexdigest()==qr['retained_image_sha256']
    cards=sorted(qr['cards'],key=lambda c:(c['entity_kind']!='pokemon',qr['cards'].index(c)))
    assert sum(c['count'] for c in cards)==20
    entries.append({'id':'filmed-qr-'+qr['payload_ascii_sha256'][:12],'deck_name':label,'filmed_deck_label':filmed_label,
        'cards_in_display_order':[{'name':c['name'],'count':c['count'],'entity_kind':c['entity_kind'],'entity_id':c['entity_id'],'functional_id':c['functional_ids'][0],'semantic_variant_references':c['printing_aliases'],
            'printing':None,'printing_limit':'QR carries playable identity; artwork and rarity remain unspecified.'} for c in cards],
        'card_slots':[{'name':c['name'],'entity_id':c['entity_id']} for c in cards for _ in range(c['count'])],
        'total_card_slots':20,'energy_configuration':[e['name'] for e in qr['decoded']['energy']],
        'deck_code':qr['payload'],'variant_note':note,'source_video':source['video_basename'],'source_sha256':source['sha256'],
        'source_seconds':qr['source_seconds'],'QR_receipt':str(qr_path),'prepared_status':'source_QR_verified_external_deck_entry_prepared',
        'external_saved':False,'card_catalog_provenance':'Pinned local community crosswalk; filmed QR is original payload evidence.'})
documents=[{'document_id':d['id'],'fields':{'name':d['deck_name'],'energy':', '.join(d['energy_configuration']),'group':'filmed','status':'active','tag':'Filmed QR',
    'order':100+i,'note':d['variant_note']+' QR identifies playable versions; listed references do not establish filmed artwork or rarity.',
    'code':d['deck_code'],'source':d['source_video']+f" at {d['source_seconds']:.2f}s; SHA-256 "+d['source_sha256'],
    'cards':[{'n':c['count'],'name':c['name'],'kind':'Pokémon' if c['entity_kind']=='pokemon' else 'Trainer','id':c['semantic_variant_references'][0]} for c in d['cards_in_display_order']]}}
    for i,d in enumerate(entries)]
document={'prepared_utc':datetime.now(timezone.utc).isoformat(),'destination':'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd',
    'owner_authorization':'Prepare new deck entries for the existing artifact','decks':entries,
    'limits':['These are prepared definitions, not a claim of saved live entries. Game-to-deck binding requires each game review and conflict check.']}
(BATCH/'NEW_DECK_ENTRIES.json').write_text(json.dumps(document,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(BATCH/'PAUSE_DECKS_IMPORT.json').write_text(json.dumps({'collection':'pause_decks','existing_artifact':document['destination'],'external_saved':False,
    'operation':'Create only missing source-qualified deck documents; preserve every existing deck and game. Check matching code and document ID before creating.',
    'schema_basis':'Published artifact HTML export deckCard and paintSelect; source retained in LIVE_ARTIFACT_BEFORE.html','documents':documents},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# New deck entries for Pause Games','','Prepared from retained filmed QR codes. Existing decks and earlier game entries remain preserved. These definitions have not yet been saved in the live artifact.','']
for deck in entries:
    lines.extend(['## '+deck['deck_name'],'',f"Filmed label: {deck['filmed_deck_label'] or 'awaiting visual label check'}. Energy: {', '.join(deck['energy_configuration'])}.",'',deck['variant_note'],'','| Count | Card |','| --- | --- |'])
    duplicate_names={c['name'] for c in deck['cards_in_display_order'] if sum(x['name']==c['name'] for x in deck['cards_in_display_order'])>1}
    lines.extend(f"| {c['count']} | {c['name']}"+(f" (semantic variant {c['entity_id']}; reference {c['semantic_variant_references'][0]})" if c['name'] in duplicate_names else '')+" |" for c in deck['cards_in_display_order'])
    lines.extend(['',f"Total: {deck['total_card_slots']} cards. Source: {deck['source_video']} at {deck['source_seconds']:.2f} seconds.",'','Deck code:','',f"```text\n{deck['deck_code']}\n```",''])
(BATCH/'NEW_DECK_ENTRIES.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Prepared '+str(len(entries))+' exact twenty-card deck entries')
