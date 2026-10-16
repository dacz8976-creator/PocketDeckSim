from pathlib import Path
import json, hashlib, datetime
p=Path(__file__).parent
sha='72d27860d438ef14528f60da481f7bbe24c5c650a3737844ecb4d14c280ef48f'
prefix='second | Glimmora first attack own turn 2; Kingambit/Alolan Muk/Regigigas no attack | opponent 0 points at Glimmora first attack; other cores N/A'
review='''# Full battle review: 20261016_031512000_iOS.MP4

Reviewer: /root/ladder_031512, gpt-6.1-sol, high. Review date: October 15, 2026 CDT. This is the primary full-source review, awaiting separate lead/independent acceptance. No shared registry, external log or media move was performed by this reviewer.

Source: 536,481,462 bytes; 290.638333 seconds; SHA-256 72d27860d438ef14528f60da481f7bbe24c5c650a3737844ecb4d14c280ef48f. SOURCE.json and PROBE.json bind the exact recording. Source creation 2026-10-16 03:15:12 UTC corresponds to October 15, 2026 at 22:15:12 CDT. All timestamps below are seconds from this source.

## Result and routing

One complete ranked match, Dacz8976 versus Pogue. Both versus cards show Master Ball Rank and the final screen confirms ranked Defeat versus Pogue. No Auto control or option appears in reviewed gameplay. Treat as owner ladder, eligible for one loss entry after independent acceptance and filename deduplication. Owner goes second, taking five own turns, global turns 2, 4, 6, 8 and 10. Owner concedes on global turn 10 with the last board score owner 0, Pogue 2. Do not convert this to a three-point knockout result. Native t0281.00.jpg shows the Concede menu, t0283.00.jpg the Defeat overlay, and t0290.50.jpg the ranked result, 776 points and zero points lost.

Three-item note prefix:

'''+prefix+'''

## Visible decks and identity limits

At 1.50 the owner deck preview is titled New deck 16, with Darkness Energy and visible Alolan Grimer, Alolan Muk, two Glimmet, two Glimmora, Pawniard, Kingambit and Regigigas. It is a partial visible preview, not a complete 20-card reconstruction. During battle Glimmet evolves to the 90-HP Glimmora with Shattering Crystal and Venomous Hit. Pawniard, Regigigas and late Alolan Grimer enter play. Alolan Muk remains in hand and Kingambit is not drawn/played in the reviewed match. The preview proves Kingambit is in the displayed deck; it does not prove any unshown counts or cards.

Pogue's confirmed visible core is Entei ex and Mega Charizard Y ex with two Charmander and two Charmeleon observed across the game. Native 90.00 identifies Entei ex, 86.50 identifies Charmeleon and Ignition, and 255.00 identifies Mega Charizard Y ex and Crimson Dive. Two Entei ex are visible. No full opponent deck list is inferred.

## Complete time-coded account

| Source interval | Phase / global turn | Meaningful actions and reconciled state |
|---|---|---|
| 0-20 | Deck / matchmaking | Partial New deck 16 preview, search, opponent found Pogue, Master Ball versus screen and coin/setup transition. No additional match. Native 1.50 and overview 18 support identities/rank. |
| 20-35 | Setup | Owner chooses Glimmet 60 Active, no Bench. Opening hand after placing it visibly contains Lucky Ice Pop, two Glimmora and Poke Ball. Opponent reveals Charmander 60 Active. Both scores zero. Native 35.00. |
| 35-49 | Pogue turn 1 | Plays Poke Ball, obtains and benches Entei ex 140. No attack and no damage. Charmander remains Active. Native 42.00 and 47.00. |
| 49-66 | Owner turn 1 / global 2 | Draws Alolan Muk. Plays Poke Ball, revealed search result Pawniard 50 enters hand, initially stays there. Attaches one Darkness Energy to Active Glimmet. Ends without attacking, despite Hang Down being displayed; opponent Charmander remains 60. No reason for the decline is supplied. Native 51.00, 54.00, 57.00, 60.00 and 63.00. |
| 66-100 | Pogue turn 2 / global 3 | Draw, benches a second Charmander 60. Fire attachment to initial Active Charmander supports its retreat, with Entei ex becoming Active. Evolves the retreated Charmander to Charmeleon 80; its Ignition card/effect adds Fire to Active Entei ex. Entei ends with one Fire, cannot pay its two-Fire Blazing Beatdown yet, and uses Legendary Pulse to draw at end of turn. No attack, HP unchanged and score 0-0. Native 73.50 through 97.50, with card face at 86.50 and end-phase state at 94.50. |
| 100-121 | Owner turn 2 / global 4 | Draws Rare Candy, which remains unused. Evolves Active Glimmet into Glimmora 90, benches Pawniard 50 and attaches Darkness to Pawniard. Glimmora retains its original one Darkness. First Venomous Hit at about 115.5 deals 30 and poisons Entei ex: 140 to 110, then checkup to 100. Pogue has zero points at this first owner attack. Native 103.50, 109.50, 115.50, 118.50 and 121.50. |
| 121-154 | Pogue turn 3 / global 5 | Evolves Charmeleon into Mega Charizard Y ex 220 on Bench. Attaches another Fire to Active Entei, bringing it to two. Pokemon Center Lady heals Entei 100 to 130 and cures poison. A second Entei ex 140 is benched. Entei uses Blazing Beatdown for 60: Glimmora 90 to 30. Legendary Pulse draws. No knockout or point. Native 130.50, 135.00, 139.50, 145.50, 148.50 and 151.00. The rotated crop from native 183.00 separately confirms the discarded Pokemon Center Lady name. |
| 154-178 | Owner turn 3 / global 6 | Draws Regigigas, benches it at 150 and attaches Darkness to it. Its Seal of Antiquity prevents attack without Regirock, Regice and Registeel on Bench; the Can't attack message appears during inspection. Lucky Ice Pop heals Glimmora 30 to 50, flips tails and is discarded. Glimmora uses a second Venomous Hit, Entei 130 to 100 then poison checkup to 90. Native 158.00, 160.50, 163.50, 168.50 (Tails), 172.50, 175.50 and 178.50. |
| 178-214 | Pogue turn 4 / global 7 | Plays Poke Ball with no eligible deck target; the explicit no-cards target message appears around 188. Plays Wally, whose face at 189.50 says to attach a Colorless Energy to a Stage 2; Mega Charizard Y ex receives it. A Fire attachment also leaves Mega Charizard with one Fire plus one Colorless. Entei uses Blazing Beatdown for 60, knocking out the 50-HP Glimmora. The temporary HP decrement animation is not a surviving 20-HP state. Shattering Crystal flips tails at 202.50, so Pogue receives one point. Owner promotes Regigigas 150. Legendary Pulse draw and poison checkup lower Entei 90 to 80. Score owner 0, Pogue 1. Native 183.00, 188.00, 189.50, 193.50, 196.00, 202.50, 205.50, 208.50 and 214.50. |
| 214-226 | Owner turn 4 / global 8 | Draws Ilima, keeps it. Attaches second Darkness to Active Regigigas. Seal of Antiquity remains visibly blocking attack; owner ends without attacking. Pawniard remains 50 with one Darkness on Bench. Entei poison checkup 80 to 70. Native 214.00, 217.50, 220.50, 223.50 and 226.50. |
| 226-265 | Pogue turn 5 / global 9 | Adds Fire to Entei, then retreats poisoned Entei to Bench, clearing poison and promoting Mega Charizard Y ex. Damaged Entei remains 70 with one Fire after retreat. Evolves second Charmander into Charmeleon 80 and triggers Ignition for Active Mega Charizard Y ex. Plays Flame Patch; together with the earlier Fire/Colorless and Ignition, Mega Charizard ends with three Fire plus one Colorless. Crimson Dive deals 250 to Regigigas 150, knocking it out, and deals 50 to itself, 220 to 170. Pogue earns a second point; owner still zero. Native 229.50, 232.50, 238.50, 239.00, 240.00, 243.00, 249.50, 250.50, 255.00, 256.50, 259.50 and 262.50. |
| 265-282.2 | Owner turn 5 / global 10 | Promotes Pawniard 50 with one Darkness, draws Professor's Research and plays it, drawing Alolan Grimer plus another Research visible in hand. Benches Alolan Grimer 70. No evolution, attachment or attack follows. Opens menu showing Concede at 281.00; transition to defeat follows. Last board: Pawniard 50 Active and Alolan Grimer 70 Bench versus Mega Charizard Y ex 170 Active, Entei ex 70, Entei ex 140 and Charmeleon 80 Bench. Score 0-2. Native 265.50, 271.50, 274.50, 277.50, 280.50, 281.00 and 282.00. |
| 282.2-290.638 | Terminal / ranked results | Defeat overlay about 283.00 then ranked Defeat versus Pogue, Master Ball Rank, 776 points, zero points lost. No additional match or unreviewed battle phase. Native 283.00, 289.50, 290.00 and 290.50. |

## Mechanically relevant decisions and limits

Observed: the first Glimmet turn ends without using its available one-Energy Hang Down. This misses 20 visible damage that turn; the reason is unknown. Do not invent intent or claim that this alone decided the match.

Observed: Glimmora supplies both owner attacks, 30 plus poison each time. Pokemon Center Lady cancels the first poison and heals 30. Lucky Ice Pop's tails gives only one 20-point heal; Glimmora remains within Entei's 60-damage knockout range. Shattering Crystal tails permits Pogue's first point.

Observed: Regigigas is unable to attack under Seal of Antiquity. It receives two Darkness and becomes a temporary Active with 150 HP, then is knocked out by Crimson Dive. Pawniard could provide a separate one-Darkness attack but remains Bench until after Regigigas falls. No Kingambit evolution occurs, and Alolan Muk has no Alolan Grimer in play until the final own turn. These are visible development constraints, not proof of a full-list consistency problem.

The owner concedes with two opposing points, not after a third knockout. The final ranked result proves a loss independently of the last board. No hidden opponent hand, unseen deck cards, exact unshown counts or predicted alternative outcome is supplied. UNCERTAINTIES.json preserves those limits.

## Evidence method and completion boundary

Coarse 12-second overview was used only for orientation. The turn pass used approximately 3-second sequential scan frames for the opening and native-resolution selected frames covering 73.5-289.5 at 3-second spacing, followed by denser native checks for card identities, both coin flips, healing, ordinary early turns, both knockouts, Energy development and the concession. All retained native images are 1170 by 2532. Contact sheets are viewing aids, not substitutes for native identity evidence. The slower optional sequential scan was stopped after useful coverage; it was never the completion criterion. EVIDENCE_MAP.json distinguishes approximate overview/scan timestamps and exact native seek timestamps.

Primary review covers the entire supplied source. Separate reviewer/lead acceptance and registry/log/archive actions remain the lead's responsibility. This primary packet becomes immutable when REVIEW_PACKET_HASHES.json is written; later clarification belongs in an addendum.
'''
p.joinpath('REVIEW.md').write_text(review,encoding='utf-8')
coverage='''# Coverage checklist

Source: 20261016_031512000_iOS.MP4, SHA-256 72d27860d438ef14528f60da481f7bbe24c5c650a3737844ecb4d14c280ef48f, duration 290.638333 seconds.

- [x] 0-35: displayed deck, queue, rank/opponent, coin/setup and opening board.
- [x] 35-49: global 1, Poke Ball and benched Entei ex, no attack.
- [x] 49-66: global 2/own 1, Alolan Muk draw, Poke Ball/Pawniard, Darkness to Glimmet, explicit end without attack.
- [x] 66-100: global 3, second Charmander, retreat, Charmeleon/Ignition, Entei Active and Legendary Pulse.
- [x] 100-121: global 4/own 2, Rare Candy draw, Glimmora evolution, Pawniard bench/Energy, first attack and poison.
- [x] 121-154: global 5, Mega evolution, second Entei, Fire, Pokemon Center Lady, 60 damage and Pulse.
- [x] 154-178: global 6/own 3, Regigigas bench/Energy, attack restriction, Lucky Ice Pop heal/tails, second attack/poison.
- [x] 178-214: global 7, no-target Poke Ball, Wally and Mega Energy, Entei KO, Shattering Crystal tails, point 1, promotion/Pulse/checkup.
- [x] 214-226: global 8/own 4, Ilima draw, Regigigas Energy, no attack, poison checkup.
- [x] 226-265: global 9, Fire, retreat/cure, second Charmeleon/Ignition, Flame Patch, Crimson Dive KO/self-damage, point 2.
- [x] 265-282.2: global 10/own 5, Pawniard promotion, Research and two draws, Alolan Grimer Bench, Concede menu.
- [x] 282.2-290.638333: Defeat and ranked result against Pogue, no second match.
- [x] HP reconciled: Entei 140-110-100, heal130, 130-100-90-80-70; Glimmora90-30+20=50, KO; Regigigas150 KO; Mega220-50=170.
- [x] Points reconciled: 0-0 until Glimmora KO; Shattering Crystal tails makes0-1; Regigigas KO makes0-2; concession ends the match.
- [x] Native confirmed attacker names, attacks/abilities, healing card, Wally, coins and final outcome; no coarse identity guesses retained.
- [x] No Auto observed; ranked screens establish mode.

No unreviewed available interval remains. Hidden information is not a coverage gap. Independent acceptance is still required; this file does not register final completion or authorize a media move by itself.
'''
p.joinpath('COVERAGE.md').write_text(coverage,encoding='utf-8')
summary={'source_filename':'20261016_031512000_iOS.MP4','source_sha256':sha,'source_bytes':536481462,'duration_seconds':290.638333,'reviewer':'/root/ladder_031512','model':'gpt-6.1-sol','reasoning_effort':'high','battle_complete':True,'match_count':1,'full_available_source_reviewed':True,'outcome':'loss','outcome_mechanism':'owner concession, followed by ranked Defeat','opponent_identifier':'Pogue','owner_identifier':'Dacz8976','match_date_local':'2026-10-15','source_creation_local':'2026-10-15T22:15:12-05:00','mode':'ranked ladder, Master Ball Rank','auto_control_seen':False,'auto_status':'No Auto control/option visible in reviewed source','computer_battle':False,'ladder_eligible':True,'pause_games_protocol_applied':False,'visible_owner_core':['Glimmet/Glimmora','Pawniard/Kingambit (Kingambit preview only)','Alolan Grimer/Alolan Muk (Muk hand only)','Regigigas'],'visible_opponent_core':['Entei ex','Charmander/Charmeleon/Mega Charizard Y ex'],'exact_decks_known':False,'first_or_second':'second','owner_turns':5,'global_terminal_turn':10,'terminal_board_points':{'owner':0,'opponent':2},'first_attacks_by_core':{'Glimmora':{'own_turn':2,'global_turn':4,'source_seconds_approx':115.5,'opponent_points':0},'Glimmet':{'attack':'no attack','opponent_points':None},'Kingambit':{'attack':'no attack','opponent_points':None},'Alolan Muk':{'attack':'no attack','opponent_points':None},'Regigigas':{'attack':'no attack','opponent_points':None},'Pawniard':{'attack':'no attack','opponent_points':None}},'exact_three_item_note_prefix':prefix,'decisive_native_evidence':['evidence/native/t0189.50.jpg','evidence/native/t0202.50.jpg','evidence/native/t0255.00.jpg','evidence/native/t0262.50.jpg','evidence/native/t0281.00.jpg','evidence/native/t0283.00.jpg','evidence/native/t0290.50.jpg'],'independent_acceptance_pending':True}
p.joinpath('SUMMARY.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
unc={'source_filename':summary['source_filename'],'source_sha256':sha,'coverage_gaps':[],'material_unresolved_outcome_questions':[],'uncertainties':[{'topic':'Exact decks','status':'unknown','detail':'Owner preview shows part of New deck 16 and battle reveals additional cards; complete exact20 and unshown counts not established. Opponent hidden hand/list remain unknown.'},{'topic':'Owner intent','status':'unknown','detail':'No stated reason for ending first Glimmet turn without Hang Down or for promoting/investing in attack-blocked Regigigas. Do not attribute a test intention or predict a certain alternative win.'},{'topic':'Timestamps','status':'bounded','detail':'Review phase endpoints are approximate animation boundaries. Native filenames use explicit source seek seconds; scan/contact timestamps are orientation approximations.'}], 'resolved_by_native_checks':['Entei ex and Mega Charizard Y ex identities','Wally name and Stage2 Colorless attachment','Pokemon Center Lady heal/cure','Lucky Ice Pop tails','Shattering Crystal tails','Concede menu followed by ranked Defeat']}
p.joinpath('UNCERTAINTIES.json').write_text(json.dumps(unc,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
frames=[]
for f in sorted((p/'evidence').rglob('*')):
 if not f.is_file():continue
 rel=f.relative_to(p).as_posix(); stem=f.stem
 kind='contact sheet / orientation aid'; t=None
 if f.parent.name=='native' and stem.startswith('t'):
  kind='native source frame';t=float(stem[1:])
 elif stem.startswith('overview_'):
  kind='scaled orientation frame';t=min((int(stem.split('_')[1])-.5)*12,290.488333)
 elif stem.startswith('scan_') and stem.split('_')[1].isdigit():
  kind='scaled sequential scan frame';t=(int(stem.split('_')[1])-1)*3+1.5
 elif stem=='183_opponent_discard_rotated':kind='native crop, 180 degree rotation from t0183.00.jpg';t=183.0
 frames.append({'path':rel,'kind':kind,'source_seconds':t,'timestamp_precision':'explicit seek' if kind=='native source frame' else 'approximate or derived'})
p.joinpath('EVIDENCE_MAP.json').write_text(json.dumps({'source_filename':summary['source_filename'],'source_sha256':sha,'frames':frames},indent=2)+'\n',encoding='utf-8')
print('Primary prose/summary/evidence map written; not frozen yet.')
