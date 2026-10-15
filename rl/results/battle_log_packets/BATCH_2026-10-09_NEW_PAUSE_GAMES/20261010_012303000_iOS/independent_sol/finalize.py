import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
root=Path(__file__).resolve().parent.parent
receipt=json.loads((root/'independent_sol/INTEGRITY_CHECK.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for file,digest in receipt['checked_input_sha256'].items():assert sha(root/file)==digest
qr=json.loads((root/'QR_DECODE_RECEIPT.json').read_text(encoding='utf-8-sig'))
live=json.loads((root.parent/'LIVE_NEW_DECKS_VERIFIED.json').read_text(encoding='utf-8-sig'))
deck=json.loads((root/'DECK_USED.json').read_text(encoding='utf-8-sig'))
matched=next(d for d in live['decks'] if d['code']==qr['payload'])
assert matched['name']==deck['deck_name_in_log']
assert Counter((c['name'],c['variant']) for c in deck['cards_in_log_order'])==Counter({(r[1],r[2]):int(r[0]) for r in matched['rows']})
viewed_names='''t0030.00.jpg t0031.00.jpg t0031.50_bottom.jpg t0046.50_bottom.jpg t0165.50_bottom.jpg t0177.00.jpg
t0167.00.jpg t0169.00.jpg t0170.50.jpg t0218.50_bottom.jpg t0221.00.jpg t0228.00.jpg t0288.00.jpg t0319.00.jpg
t0215.00.jpg t0237.00.jpg t0320.00.jpg t0359.00.jpg t0362.25_bottom.jpg t0371.00.jpg t0375.00.jpg t0388.00.jpg t0390.00.jpg
t0291.00.jpg t0109.00_bottom.jpg t0310.50_bottom.jpg t0067.00_bottom.jpg t0129.00_bottom.jpg t0184.00_bottom.jpg t0230.00_bottom.jpg t0318.00_bottom.jpg t0371.00_bottom.jpg
t0046.50_top.jpg t0109.00_top.jpg t0165.50_top.jpg t0218.50_top.jpg t0310.50_top.jpg t0362.25_top.jpg
t0060.00.jpg t0061.00.jpg t0062.00.jpg t0063.00.jpg t0285.00.jpg t0294.00.jpg
t0047.00.jpg t0053.00.jpg t0312.50_bottom.jpg t0315.50.jpg t0368.00.jpg'''.split()
viewed=[{'path':'turn_evidence/'+name,'sha256':sha(root/'turn_evidence'/name),'inspection':'Actually rendered through view_image; full native frame or native crop as filename indicates'} for name in viewed_names]
viewed.append({'path':'independent_sol/source_check_288.25.jpg','sha256':sha(root/'independent_sol/source_check_288.25.jpg'),'seconds':288.25,'inspection':'Fresh bounded original-source decode; Tails! fully visible in Guts coin sequence'})
manifest={'reviewer':'/root/check_012303','model':'gpt-6.1-sol','reasoning_effort':'high','source_video':'20261010_012303000_iOS.MP4','source_sha256':receipt['source_sha256'],'visual_scope':'Bounded independent opening, ordinary first actions, draw/search order, hand/fan counts, consequential state transitions, warning, terminal sequence. Not a second full-battle review.','viewed_count':len(viewed),'viewed':viewed}
(root/'independent_sol/VIEWED_MANIFEST.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
checks=[
 'Source SHA-256 and byte count independently verified at original root path; size and mtime stable during hash.',
 'Fresh native decodes at30/177/375 seconds are byte-identical to retained source frames. One additional288.25-second frame directly resolves full Tails! text.',
 'All eight final core files read and hashed;11 unique contiguous turn rows;235 full native1170x2532 frame sets and bottom1170x507/top1170x620 crops exist; every ledger evidence ID resolves.',
 'Opening30/31/31.5 verifies Nacli,Guts Conkeldurr,Nacli,Naclstack,Copycat and third-slot Nacli selected Active.',
 'All six owner rows have draw-relative+1/+3/+6 native candidates, selected dense pre-play hands and before-end records. Turn9+1/+3/+6 inspected; later candidates show evolution/attachment rather than the initial hand as declared.',
 'Ordinary turn1 first action Arena then Copycat directly checked47/53; Copycat four revealed cards60-63 checked in order. Turn5 first action Research167, two draws169/170.5 and failed Poke Ball177 checked. T7 Wally Stage2 Colorless effect221 precedes normal Fighting attachment; resolved2F+1Colorless Active and1F Timburr checked237.',
 'Owner starting hands selected by name; all six ending counts3,1,1,1,1,0 visually checked and reconciled. Opponent fan counts4,1,3,4,4,5 directly checked from native top crops.',
 'Both players start/end board fields, typed Energy, HP/max/damage, Tool/conditions/effects, Stadium, points and both current/next Energy Zone lines are populated with source-qualified limits. Selected ordinary and consequential boards checked; no contradictory HP/Energy/point arithmetic found.',
 'Guts70HP after80 damage215; Poisoned50HP after turn7 checked237; lethal attack285, Tails288.25 and second opponent point294 verified.',
 'Turn9 attack warning319 and turn10 banner320 confirm pass, no attack. Gurdurr10HP after next Darkness Claw359 and evolution carry-over to Conkeldurr70HP371 checked.',
 'Final Bedrock Breaker120 damage375, Arena removed/Poison/owner3points versus opponent2 at388, and Victory390 verified.',
 'Exact20-slot deck in DECK_USED matches retained live deck rows and identical QR payload. Local verifier rechecked saved provenance; did not access browser or independently refresh live artifact.',
 'Whole-source coverage table0-398.131667 and prose all11 turns/terminal/loading tail consistent with ledger. No second review or source-wide decoding performed by checker; primary full-review coverage plus bounded independent checks form acceptance basis.'
]
result={'schema':'independent-sol-bounded-acceptance-v1','reviewer':'/root/check_012303','model':'gpt-6.1-sol','reasoning_effort':'high','checked_at_utc':datetime.now(timezone.utc).isoformat(),'source_video':'20261010_012303000_iOS.MP4','source_sha256':receipt['source_sha256'],'accepted':True,'status':'accepted_with_recording_limits','blockers':[],'packet_corrections':[],'checked_input_sha256':receipt['checked_input_sha256'],'accepted_input_sha256':receipt['checked_input_sha256'],'source_identity_sha256':sha(root/'SOURCE.json'),'viewed_manifest':'independent_sol/VIEWED_MANIFEST.json','integrity_receipt':'independent_sol/INTEGRITY_CHECK.json','native_binding_checks':receipt['native_bindings'],'checks':checks,'accepted_limits':['No opened discard-pile panels; no full discard contents invented.','Opponent hidden draw identities/full deck and exact human queue unknown.','QR/log establish semantic deck variants; exact artwork/rarity unverified.','Source-local seek timestamps retained, exact frame PTS not independently measured.','Loading tail continues after established Victory; no additional gameplay claimed.'],'outcome':{'opponent':'ナチョス','owner_result':'win','owner_points':3,'opponent_points':2,'terminal_turn':11},'shared_or_external_mutations':False}
(root/'independent_sol/CHECK_RESULT.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
(root/'independent_sol/CHECK_NOTES.md').write_text('# Independent bounded acceptance\n\nAccepted with recording limits. No factual repair was required. The frozen packet covers one continuous11-turn human battle ending in a3-2 owner win. Selected native opening, ordinary first actions, named draws/searches, hand/fan counts, mixed Energy/HP/effect transitions, Guts tails, warning/pass and final knockout/points/Victory match the review.\n\nAll eight final core files were checked and hashed. The original source hash matches; three independent native seeks match retained frames byte-for-byte. A single extra native288.25s capture confirms the complete Tails text. The actual50 rendered images/crops are listed in VIEWED_MANIFEST.json. All235 native evidence sets and ledger references passed integrity checks. Whole coverage was assessed from the full worker account, contiguous turn rows and coverage checklist, not claimed as a second full visual review.\n\nUnknown hidden opponent cards, unopened discard piles, queue identity, artwork/rarity and exact frame PTS remain explicit limits. No blocker remains for lead acceptance. The coordinator retains responsibility for shared registration, external logging and archival.\n',encoding='utf-8')
print('ACCEPTED',len(viewed),'actually viewed images/crops;',len(receipt['checked_input_sha256']),'frozen core hashes')
