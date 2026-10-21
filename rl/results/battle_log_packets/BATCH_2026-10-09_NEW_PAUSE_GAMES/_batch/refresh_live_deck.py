"""Lead refresh from retained rendered live deck rows, preserving initial provenance."""
import argparse, hashlib, json, shutil
from pathlib import Path
from datetime import datetime, timezone
b=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('packet');ap.add_argument('--candidate',action='store_true');a=ap.parse_args()
p=b/a.packet
live=json.loads((b/'LIVE_NEW_DECKS_VERIFIED.json').read_text(encoding='utf-8'))
prepared=json.loads((b/'PREPARED_QR_DECKS.json').read_text(encoding='utf-8'))
label='Conkeldurr / Garganacl' if a.packet in ('20261010_012303000_iOS','20261010_013009000_iOS') else "Kingdra ex / Team Rocket's Weezing ex"
d=next(x for x in live['decks'] if x['name']==label)
prep=next(x for x in prepared['decks'] if x['deck_name']==label)
assert d['code']==prep['deck_code']
expected=[(str(c['n']),c['name'],c['id']) for c in prep['cards']]
assert [tuple(r) for r in d['rows']]==expected
counts=[{'count':int(r[0]),'name':r[1],'variant':r[2]} for r in d['rows']]
assert sum(c['count'] for c in counts)==20
path=p/'DECK_USED.json';deck=json.loads(path.read_text(encoding='utf-8'))
assert deck.get('is_template') is False
backup=p/'DECK_USED.before_live_refresh.json'
if not backup.exists():shutil.copy2(path,backup)
binding=deck.get('game_version_binding_basis','')
if a.candidate:binding='Later filmed QR candidate agrees with visible core but does not prove earlier exact game list.'
elif isinstance(binding,dict):binding={**binding,'live_refresh':'Source-qualified live addition matches filmed QR exactly.'}
else:binding=str(binding)+' Source-qualified live addition now matches the filmed QR exactly.'
deck.update(deck_name_in_log=label,captured_at=live['retrieved_at_utc'],log_list_version='Rendered live addition verified after save; '+d['id'],
 cards_in_log_order=[{'name':c['name'],'variant':c['variant']} for c in counts for _ in range(c['count'])],
 counts_by_name_and_variant=counts,energy_configuration_from_log=prep['energy_configuration'],actual_card_count=20,
 capture_source_text_or_image='../LIVE_NEW_DECKS_VERIFIED.json',
 exact_list_status='verified_live_list_game_version_unverified' if a.candidate else 'verified_live_list_and_filmed_qr_game_binding',
 game_version_binding_basis=binding,
 initial_log_snapshot='DECK_USED.before_live_refresh.json',live_refresh_utc=datetime.now(timezone.utc).isoformat())
deck['limits']=[x for x in deck.get('limits',[]) if 'unavailable until' not in x and 'absent from' not in x and 'no matching' not in x.lower()]
if a.candidate:deck['limits'].append('Earlier exact game20 is unverified; later QR is only a candidate version.')
path.write_text(json.dumps(deck,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'packet':a.packet,'deck':label,'live_card_count':20,'candidate_only':a.candidate}))
