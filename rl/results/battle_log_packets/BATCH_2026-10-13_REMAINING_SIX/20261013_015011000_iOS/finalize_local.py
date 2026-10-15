import json,hashlib,re
from pathlib import Path
P=Path(__file__).resolve().parent
def read(n):return json.loads((P/n).read_text(encoding='utf-8-sig'))
def save(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
q=read('QR_DECODE.json');cat=json.loads((P.parent/'HISTORICAL_DECK_CATALOG.json').read_text(encoding='utf-8-sig'))
match=[d for d in cat['decks'] if d['code']==q['payload']]
assert len(match)==1
d=match[0];slots=[];counts=[]
for count,name,variant in d['rows']:
 counts.append(dict(name=name,variant_as_shown_in_log=variant,count=int(count)))
 slots.extend(dict(name=name,variant_as_shown_in_log=variant) for _ in range(int(count)))
assert len(slots)==20
save('DECK_USED.json',dict(schema='pause-games/turn-capture-v1',is_template=False,game_id=q['source_video'].removesuffix('.MP4'),sources=[dict(video_basename=q['source_video'],sha256=q['source_sha256'],source_json='SOURCE.json')],deck_name_in_log=d['name'],source_url=cat['artifact_url'],captured_at=cat['retrieved_utc'],fresh_live_readback=False,log_list_version='Historical public readback at recorded UTC, qualified current-access limit',expected_card_count=20,cards_in_log_order=slots,counts_by_name_and_variant=counts,energy_configuration_from_log=['Darkness'],actual_card_count=20,capture_source_text_or_image=d['text'],historical_snapshot_source='../HISTORICAL_DECK_CATALOG.json',filmed_qr_receipt='QR_DECODE.json',filmed_cards_in_qr_order=q['slots'],filmed_energy=q['energy'],game_version_binding_basis='Own source native QR at1.00 exactly equals historical log code; continuous QR closure/deck selection/New deck16/matchmaking/game with no edit.',conflicts_with_filmed_cards=[],exact_list_status='exact_historical_log_and_filmed_qr_match',limits=['Fresh live readback unavailable this turn, per root EXTERNAL_ACCESS_BLOCK.json. Historical snapshot is not claimed current.','Log printing labels preserved as supplied; filmed QR proves playable entity/count/Energy, not artwork/rarity.']))
x=read('SUMMARY.json');x['deck_name_in_log']=d['name'];x['deck_snapshot_status']='exact_historical_log_and_filmed_qr_match';save('SUMMARY.json',x)
x=read('PAUSE_GAME.json');x['deck_name']=d['name'];x['limits']=[z.replace('Filmed QR exact20 saved; fresh live log snapshot pending lead supplement.','Own filmed QR exactly matches20-card historical log snapshot; fresh live readback unavailable this turn.') for z in x['limits']];save('PAUSE_GAME.json',x)
x=read('TURN_LEDGER.json');x['turns'][0]['plays_in_order'][0]['hand_count_after']=4;x['turns'][0]['board_after']['phase']='After End Turn resolves, before opponent draw';x['turns'][0]['board_after']['evidence_ids']=['n71_80'];save('TURN_LEDGER.json',x)
x=read('UNCERTAINTIES.json');x['items'][4]['issue']='Source local date verified by SOURCE_TIME and phone clock; own QR exactly matches historical log snapshot; fresh live readback unavailable per root access block.';save('UNCERTAINTIES.json',x)
for name in ['REVIEW.md','COVERAGE.md']:
 text=(P/name).read_text(encoding='utf-8')
 text=text.replace('Fresh live Pause Games comparison is pending a separate root supplement; the filmed list is not claimed to be a fresh live snapshot.','The own filmed code exactly matches the20-card historical Pause Games snapshot retrieved2026-10-13T04:53:35.861Z, deck Glimmora / Alolan Muk / Kingambit / Regigigas. DECK_USED.json preserves that actual20-card list, all log printing labels, source text and historical retrieval time. Fresh live readback is unavailable this turn per root access block. This snapshot is explicitly historical.').replace('Fresh live snapshot remains a root supplement.','Exact code matches the historical log snapshot at its recorded retrieval time; fresh live readback unavailable.').replace('Fresh live snapshot remains a root supplement.','Fresh live readback unavailable this turn.')
 # Ordinary spaces in authored prose, without altering filenames, hashes, dates or decimal timestamps.
 text=re.sub(r'\b(at|native|turns|fan|hand|entity|about|sample|cards|after|All|all|exact|printed|version)(?=\d)',r'\1 ',text)
 text=re.sub(r'\b(\d+)(?=(HP|PM|s\b|cards\b|turns\b|slots\b|card\b|damage\b))',r'\1 ',text)
 text=text.replace('20-card','20-card').replace('Native1170','Native 1170').replace('native1170','native 1170').replace('deck16','deck 16').replace('New deck16','New deck 16').replace('at20:','at 20:').replace('at2026','at 2026').replace('October12','October 12').replace('October13','October 13').replace('at27.','at 27.').replace('at13.','at 13.').replace('at21.','at 21.').replace('clock8:','clock 8:').replace('and8:','and 8:').replace('game3','game 3').replace('All5','All 5').replace('Retained evidence |','Retained evidence |')
 (P/name).write_text(text,encoding='utf-8')
print('Qualified historical deck snapshot integrated; eight files ready for structural validation.')
