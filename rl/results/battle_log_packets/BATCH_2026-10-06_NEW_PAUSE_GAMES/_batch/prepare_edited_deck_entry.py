"""Prepare the filmed game-two revision separately from the frozen13 QR entries."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

B = Path(__file__).resolve().parent
P = B / '20261006_012927000_iOS'
CATALOG = Path(r'C:\Users\dacz8\Projects\Pocket Deck Lab\s216_card_catalog_v1.json')
frozen_hash = hashlib.sha256((B/'NEW_DECK_ENTRIES.json').read_bytes()).hexdigest()
catalog = json.loads(CATALOG.read_text(encoding='utf-8'))
source = json.loads((P/'SOURCE.json').read_text(encoding='utf-8'))
spec = [('pokemon',8490,1),('pokemon',21710,2),('pokemon',21720,2),('pokemon',7940,2),('pokemon',21050,1),('pokemon',7950,1),('trainer',30,2),('trainer',1060,2),('trainer',1280,1),('trainer',40,2),('trainer',320,1),('trainer',990,1),('trainer',1580,2)]
cards = []
for kind, entity_id, count in spec:
    matches = [e for e in catalog['entities'] if e['kind']==kind and e['entity_id']==entity_id]
    assert len(matches)==1
    entity = matches[0]
    aliases = [a for a in catalog['aliases'] if a['entity_key']==entity['entity_key']]
    assert aliases and {a['functional_id'] for a in aliases}=={entity['functional_id']}
    cards.append({'name':entity['canonical_name'],'count':count,'entity_kind':kind,'entity_id':entity_id,'functional_id':entity['functional_id'],'semantic_variant_references':sorted({a['printing_id'] for a in aliases}),'visible_variant':', '.join(a['title'] for a in entity.get('full_attacks',[])) or None,'printing':None,'printing_limit':'Semantic card version resolved from filmed edits and the pinned catalog; exact artwork reference is not asserted.'})
assert sum(c['count'] for c in cards)==20
identity = {'cards':[(c['entity_kind'],c['entity_id'],c['count']) for c in cards], 'energy':['Water']}
semantic_hash = hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
evidence=[]
for seconds in [450,590,600,620]:
    path=P/f'native/t{seconds:07.2f}.jpg'
    assert path.exists()
    evidence.append({'source_seconds':seconds,'path':str(path),'image_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'observation':'Brave Buddies related-card view' if seconds==450 else 'Final20/20 deck Pokemon versions' if seconds==590 else 'Final20/20 deck and Water-only Energy'})
entry={'id':'filmed-edit-'+semantic_hash[:12],'deck_name':"Snorlax ex / Team Rocket's Persian / Silvally (Water revision)",'filmed_deck_label':'New deck 6','cards_in_display_order':cards,'card_slots':[{'name':c['name'],'entity_id':c['entity_id']} for c in cards for _ in range(c['count'])],'total_card_slots':20,'energy_configuration':['Water'],'deck_code':None,'variant_note':'Continuous filmed edit between games replaces ordinary Meowth/Persian with Team Rocket versions, removes Terapagos ex, splits Silvally into Gold Breaker and Brave Buddies, adds two Soothing Shore, and sets Water only. No revised QR was filmed.','source_video':source['video_basename'],'source_sha256':source['sha256'],'game_number_in_source':2,'source_edit_window_seconds':[420,622],'native_final_views':evidence,'original_QR_receipt':str(P/'qr_intake/QR_DECODE_0001.00.json'),'edit_ledger':str(P/'DECK_EDIT_LEDGER.json'),'prepared_status':'filmed_edit_definition_prepared_independent_game_binding_pending','external_saved':False,'semantic_identity_sha256':semantic_hash,'catalog_sha256':hashlib.sha256(CATALOG.read_bytes()).hexdigest(),'limits':['Exact edit input order within fast UI clusters may be unresolved; the final entity counts and game binding require the full edit ledger and independent acceptance.','No code is presented as a filmed QR. Existing13 QR entries remain frozen.']}
doc={'prepared_utc':datetime.now(timezone.utc).isoformat(),'destination':'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd','owner_authorization':'Prepare new deck entries for the existing artifact','decks':[entry],'external_saved':False}
(B/'EDITED_DECK_ENTRY.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
fields={'name':entry['deck_name'],'energy':'Water','group':'filmed','status':'active','tag':'Filmed edit','order':113,'note':entry['variant_note']+' Semantic references do not assert the filmed artwork.','code':'','source':entry['source_video']+' game2, continuous edit420-622s; SHA-256 '+entry['source_sha256'],'cards':[{'n':c['count'],'name':c['name'],'kind':'Pokémon' if c['entity_kind']=='pokemon' else 'Trainer','id':c['semantic_variant_references'][0]} for c in cards]}
(B/'PAUSE_EDITED_DECK_IMPORT.json').write_text(json.dumps({'collection':'pause_decks','existing_artifact':doc['destination'],'external_saved':False,'operation':'Create only the missing filmed-edit definition after acceptance; preserve all existing decks and games.','documents':[{'document_id':entry['id'],'fields':fields}]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# Filmed deck revision for game2','',entry['deck_name'],'','Prepared as a separate fourteenth entry. The continuous edit and second game still require independent acceptance. This definition has not been saved in the live artifact.','','Energy: Water only. No revised QR was filmed.','','| Count | Card | Visible version |','| --- | --- | --- |']
lines += [f"| {c['count']} | {c['name']} | {c['visible_variant'] or 'Trainer'} |" for c in cards]
lines += ['', 'Total:20 cards. Source:20261006_012927000_iOS.MP4, edited420-622 seconds, game2.','',entry['variant_note'],'','Original13 QR definitions remain unchanged. The full edit ledger retains any unresolved order within fast UI clusters.']
(B/'EDITED_DECK_ENTRY.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
assert hashlib.sha256((B/'NEW_DECK_ENTRIES.json').read_bytes()).hexdigest()==frozen_hash
print('Prepared separate edited20-card entry '+entry['id']+'; frozen13 unchanged; independent game binding pending')
