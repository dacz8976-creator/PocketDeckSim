"""Prepare only source-bound filmed deck variants absent from the live snapshot."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

batch=Path(__file__).resolve().parent
live=json.loads((batch/'LIVE_DECK_SNAPSHOT.json').read_text(encoding='utf-8'))
known_codes={d.get('deck_code') for d in live['decks']}
labels={'20261010_013009000_iOS':'Conkeldurr / Garganacl',
        '20261010_015452000_iOS':"Kingdra ex / Team Rocket's Weezing ex"}
decks=[]
for packet_name,label in labels.items():
    packet=batch/packet_name
    qr_path=packet/'QR_DECODE.json'
    qr=json.loads(qr_path.read_text(encoding='utf-8'))
    source=json.loads((packet/'SOURCE.json').read_text(encoding='utf-8'))
    assert qr['source_sha256']==source['sha256']
    assert qr['card_slot_count']==20 and qr['decoded']['roundtrip'] is True
    assert hashlib.sha256(Path(qr['retained_image']).read_bytes()).hexdigest()==qr['retained_image_sha256']
    assert all(c['name'] and len(c['functional_ids'])==1 for c in qr['cards'])
    cards=sorted(qr['cards'],key=lambda c:c['entity_kind']!='pokemon')
    decks.append({'id':'filmed-qr-'+qr['payload_ascii_sha256'][:12],
        'deck_name':label,'source_video':source['video_basename'],'source_sha256':source['sha256'],
        'source_seconds':qr['source_seconds'],'QR_receipt':str(qr_path),
        'card_slots':[{'name':c['name'],'semantic_variant_reference':c['printing_aliases'][0],'entity_id':c['entity_id'],
                       'entity_kind':c['entity_kind']} for c in cards for _ in range(c['count'])],
        'cards':[{'n':c['count'],'name':c['name'],'kind':'Pokémon' if c['entity_kind']=='pokemon' else 'Trainer',
                  'id':c['printing_aliases'][0]} for c in cards],
        'energy_configuration':[e['name'] for e in qr['decoded']['energy']],
        'deck_code':qr['payload'],'already_in_live_snapshot':qr['payload'] in known_codes,
        'game_binding_status':'awaiting full source review and independent acceptance',
        'printing_limit':'QR establishes playable identities; reference labels do not establish filmed artwork or rarity',
        'external_saved':False})
assert all(len(d['card_slots'])==20 and sum(c['n'] for c in d['cards'])==20 for d in decks)
(batch/'PREPARED_QR_DECKS.json').write_text(json.dumps({'prepared_utc':datetime.now(timezone.utc).isoformat(),
    'destination':live['source_url'],'decks':decks},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'prepared_decks':len(decks),'absent_from_live':sum(not d['already_in_live_snapshot'] for d in decks)}))
