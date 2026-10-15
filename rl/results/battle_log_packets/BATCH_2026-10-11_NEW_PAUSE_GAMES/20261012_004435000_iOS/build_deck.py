from pathlib import Path
import json
p=Path(__file__).parent
snap=json.loads((p.parent/'LIVE_DECK_SNAPSHOT.json').read_text(encoding='utf-8'))
d=snap['decks'][24]
qr=json.loads((p/'QR_DECODE.json').read_text(encoding='utf-8'))
def fix(s):
 return s.replace('Rocket�s',"Rocket's").replace('Professor�s',"Professor's").replace('Pok�','Poké')
counts=[dict(name=fix(x['name']),variant=x['variant'],count=x['quantity']) for x in d['counts_by_name_and_variant']]
slots=[dict(name=x['name'],variant=x['variant']) for x in counts for i in range(x['count'])]
out={'is_template':False,'schema':'pause-games/deck-snapshot-v1','game_id':'20261012_004435000_iOS-game1','deck_name':d['label'],'log_url':snap['source_url'],'retrieved_utc':snap['retrieved_utc'],'exact_list_status':'verified_20_slots_live_log_snapshot_and_matching_filmed_QR','energy_configuration':['Water'],'cards_in_log_order':slots,'counts_by_name_and_variant':counts,'total_card_slots':sum(x['count'] for x in counts),'captured_source_reference':'../LIVE_DECK_SNAPSHOT.json, deck index24','filmed_QR_reference':'QR_DECODE.json','filmed_QR_source_seconds':0,'filmed_QR_payload_matches_snapshot':qr['payload']==d['code'],'version_conflicts':[],'limits':['QR verifies semantic identity and Water Energy, not exact artwork or rarity; variants are live-log labels.','Preserved batch text has replacement characters in several names. Packet names use decoded semantic names; raw log text remains preserved in the shared snapshot.']}
(p/'DECK_USED.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(out['total_card_slots'],out['filmed_QR_payload_matches_snapshot'])
