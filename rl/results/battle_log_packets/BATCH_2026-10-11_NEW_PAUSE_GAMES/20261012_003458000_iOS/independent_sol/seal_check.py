import json, hashlib, subprocess
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

P=Path(__file__).resolve().parent.parent
O=P/'independent_sol'
names=['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
H='399ef7e1be5545ca1284a7aedb9f6eea70abb5929ed7cbf2083d539dae64f413'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
docs={n:read(P/n) for n in names if n.endswith('.json')}
source=read(P/'SOURCE.json')
assert source['sha256']==H and source['video_basename']=='20261012_003458000_iOS.MP4'
turns=docs['TURN_LEDGER.json']['turns']
assert [x['turn_number'] for x in turns]==list(range(1,12))
assert [x['who_played'] for x in turns]==['owner' if i%2 else 'opponent' for i in range(1,12)]
assert [turns[i-1]['owner_hand_end']['count'] for i in [1,3,5,7,9,11]]==[5,5,3,3,4,5]
assert turns[0]['owner_hand_start']['count']==4 and turns[2]['owner_hand_start']['count']==6
assert turns[0]['owner_hand_start']['status']=='observed_with_recording_limits'
assert turns[2]['owner_hand_start']['evidence_ids']==['N088p000']
assert turns[0]['board_after']['turn_number_displayed']==2
assert turns[7]['board_at_start']['opponent']['energy_zone']['this_turn']['available'] is False
assert turns[10]['board_at_start']['owner']['energy_zone']['this_turn']['available'] is False
assert turns[10]['board_after']['owner']['energy_zone']['this_turn']['available'] is True
assert turns[10]['plays_in_order']==[]
assert docs['PAUSE_GAME.json']['opening']['status']=='observed_with_recording_limits'
assert docs['PAUSE_GAME.json']['outcome']['method']=='opponent_concession'
assert docs['PAUSE_GAME.json']['match_date']=='2026-10-11'
assert docs['PAUSE_GAME.json']['capture_status']=='complete_with_recording_limits'
evidence=docs['TURN_EVIDENCE.json']
ids={x['evidence_id'] for x in evidence['frames']+evidence['overview_frames']}
unknown=[]
def scan(x):
    if isinstance(x,dict):
        for k,v in x.items():
            if k=='evidence_ids' and isinstance(v,list):
                unknown.extend(i for i in v if i not in ids)
            scan(v)
    elif isinstance(x,list):
        for v in x: scan(v)
for x in docs.values():scan(x)
assert not unknown, unknown
for n in ['PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']:
    assert docs[n]['sources'][0]['sha256']==H
deck=docs['DECK_USED.json']
qr=read(O/'QR_RESCAN.json')
fresh=read(P.parent/'LIVE_DECK_SNAPSHOT_RESUME.json')
original=read(P.parent/'LIVE_DECK_SNAPSHOT.json')
f=next(d for d in fresh['decks'] if d['label'].startswith('Kingdra'))
o=next(d for d in original['decks'] if d['label'].startswith('Kingdra'))
assert qr['payload']==f['code']==o['code'] and qr['card_slot_count']==20
assert len(deck['cards_in_log_order'])==20
assert sum(c['count'] for c in deck['counts_by_name_and_variant'])==20
assert Counter((c['name'],c['variant']) for c in deck['cards_in_log_order'])==Counter({(c['name'],c['variant']):c['quantity'] for c in f['counts_by_name_and_variant']})
assert qr['decoded']['energy']==[{'value':3,'name':'Water','selectable':True}]
result=subprocess.run([__import__('sys').executable,str(P.parent/'validate_packet.py'),str(P)],capture_output=True,text=True,check=True)
validation=json.loads(result.stdout)
assert validation['structural_pass'] is True, validation
hashes={n:digest(P/n) for n in names}
assert hashes==read(P/'FROZEN_FIRST_PASS_HASHES.json')['files']
checks=[
 {'topic':'opening_and_mode','source_seconds':[8,26,27,30,40],'finding':'Human opponent found, owner going first, five named opening slots with explicit zoom/edge limit, shiny Horsea Active and gold-art Horsea Bench.'},
 {'topic':'ordinary_first_moves_and_draws','source_seconds':[43,44,45,46,49,50,53,86,88,89,92,97,98,106],'finding':'T1 Research first; qualified four-card pre-play hand ends at five. T3 Seadra evolution before attachment/Research/Tool; clear six-card pre-play hand ends at five.'},
 {'topic':'search_copycat_order_and_hand','source_seconds':[136,140,148,152,154,156,157,158,159,160,162,166,174,182,190,194],'finding':'Poke Ball search before Copycat; returned four cards and all five named reveals preserved; bench then evolution and attachment before Pichu knockout; end hand three; Dragonair promotion after 184 accurately cited at 190.'},
 {'topic':'boards_energy_zones_and_effects','source_seconds':[54,60,82,88,107,112,122,132,134,190,194,229,232,238,254,260,270,272,303,304,309,324,328,348,351,352,353,354],'finding':'Both boards and typed attached Energy align at selected ordinary/terminal phases. Pre-generation empty zones, unreadable generation symbols and already-visible next-turn banners are explicitly qualified. T7 and T9 Supporter warnings are present.'},
 {'topic':'opponent_fans','source_seconds':[45,86,137,231,304,305,351],'finding':'Actual card-back edges support counts 4/5/5/3/4/5 for owner turns 1/3/5/7/9/11; hidden identities remain unknown.'},
 {'topic':'terminal_and_end_hand','source_seconds':[318,342,346,350,351,352,353,354],'finding':'Score ties 2-2; Slam two tails causes zero damage; normal Weezing ex draw leaves final five cards; concession establishes owner win before any T11 voluntary action.'},
 {'topic':'deck_membership','source_seconds':[0],'finding':'Independent retained QR rescan matches both saved live snapshots, twenty semantic slots and Water. Live list labels are preserved; QR does not establish artwork or rarity.'}
]
receipt={
 'schema':'bounded_independent_pause_acceptance_v1',
 'reviewer':'/root/verify_pause_003458','review_model':'gpt-6.1-sol','reasoning_effort':'high',
 'accepted':True,'sealed_at_utc':datetime.now(timezone.utc).isoformat(),
 'source_video':source['video_basename'],'source_sha256':H,
 'source_identity_basis':'Frozen SOURCE.json intake CLI SHA-256 receipt; no duplicate source decode or rehash performed by independent reviewer.',
 'accepted_input_sha256':hashes,'required_repairs':[],
 'resolved_repairs':['Qualified opening zoom/edge capture','T1 pre-play hand evidence and fast-play candidate suitability','T3 clear unzoomed N088 selection','Literal Energy Zone states and displayed boundary phases','Post-knockout Dragonair promotion cited after resolution','T9 offered Supporter warning preserved','Readable prose spacing'],
 'scope':'Separate bounded semantic checks and whole-packet contract reconciliation; not a second full-source visual pass.',
 'evidence_checks':checks,'structural_validation':validation,
 'recording_limits':['Exact queue label not shown','Opening Horsea zoom and clipped outer card; T1 lacks ideal unzoomed pre-play view','Opponent draw/search faces and May returns hidden','Neither discard pile opened','Energy generation has explicitly unreadable or pre-generation boundary symbols','QR semantic identity does not establish exact artwork/rarity','Source ends during result transition after explicit concession'],
 'report_sha256':digest(O/'REVIEW.md'),'qr_rescan_sha256':digest(O/'QR_RESCAN.json')
}
(O/'CHECK_RESULT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
saved=read(O/'CHECK_RESULT.json')
assert saved==receipt
assert {n:digest(P/n) for n in names}==hashes
assert digest(O/'REVIEW.md')==saved['report_sha256']
print(json.dumps({'accepted':saved['accepted'],'required_repairs':saved['required_repairs'],'inputs':len(hashes),'readback_verified':True,'report':str(O/'REVIEW.md'),'receipt':str(O/'CHECK_RESULT.json')}))
