import json,datetime
from pathlib import Path
p=Path('Recording_QA/BATCH_2026-10-14_EVENING_LADDER/20261014_215114000_iOS')
review='''# Full battle review: 20261014_215114000_iOS.MP4

Reviewer: /root/evening_215114. Assigned model: gpt-6.1-sol, high. Review date: October 14, 2026. Scope: this complete 447.65-second source, opening deck screen and matchmaking through all 13 global turns, concession and final results. Independent acceptance and shared registration remain the lead's responsibility.

Source binding: SOURCE.json, SHA-256 b3170e7b962e7141ab0168cf4ca9aa2ce7e1241e6b750eee785eff51657c8a4a, 829014558 bytes. The source was preserved. Every timestamp below is source-local seconds. Evidence filenames encode exact requested extraction times. Contact sheets are navigation aids; retained evidence/ frames are original 1170 x 2532 pixels.

## Result and requested note

Win by opponent concession versus 羊羽. The owner went second. Final score was 2-2, with 13 global turns and 340 displayed damage. Concession is explicitly visible at 436s and Victory plus the statistics at 447s. Do not convert the concession to a third knockout point.

Exact three-item note prefix: **2nd | Alolan Ninetales ex T3 | opp 2 pts**.

The first main-attacker attack is Alolan Ninetales ex's Binding Snow on owner T3, global turn 6. The named attack banner is visible at 201s, and the 80-damage animation at 203s. The opponent already has 2 points in both frames. Before/after: first Hydreigon 90 HP to 10 HP; Ninetales ex at 180 HP with Elegant Cape and two Water Energy. This is the first Ninetales attack, not the owner's first attack: opening Vulpix previously used Gnaw for 20.

## Mode and visible deck identity

Ranked human ladder battle: the versus introduction at 19s shows Ultra Ball Rank 4 for both players. No Auto control or option is visible in the inspected setup, turn UI or result. Owner choices have visible manual taps. No computer classification trigger was observed. The exact queue menu was not captured, but ranked badges and the human opponent screen are observed.

The owner's visible label is **Deck 13-A** at 0s. Visible core: two Alolan Vulpix, Alolan Ninetales ex, Team Rocket's Rattata and Team Rocket's Raticate ex. The opening deck editor also shows two Ninetales ex and two Raticate ex cards; this report does not infer a full 20-card list or unseen Trainer quantities. Publicly seen owner support includes Professor's Research, Poké Ball, Sightseer, Soothing Shore and Elegant Cape; Ilima, Copycat, Field Blower and Cyrus are visible in hand, and Sabrina appears in Sightseer's four-card view.

Opponent's public core: Deino into Hydreigon (Roar in Unison / Hyper Ray), Mega Absol ex, Absol (Enhanced Blade) and late Bombirdier. Rare Candy, Poké Ball, Lucky Ice Pop, Clear Veil, Deceptive Needle and Copycat are observed. Unknown remaining deck contents are not guessed. Mega Absol ex remains on the Bench and never attacks in this match.

## Complete time-coded account

### Opening and setup, 0-31s

0s: Deck 13-A in the editor with 20/20 indicated and the visible core. Matchmaking follows. 19s: 羊羽 versus Dacz8976, both Ultra Ball Rank 4. 24-28s: opening five cards are Alolan Vulpix, Soothing Shore, Sightseer, Ilima and Professor's Research. The owner places Vulpix Active with no starting Bench. Opponent reveals Deino Active (60 HP). The opponent acts first, independently confirmed by turn 1 at 32s and the final Went second statistic.

### Global 1, opponent own T1, about 32-50s

Opponent uses two Poké Balls (first discarded by 38-40s, second displayed at 42s), then benches Absol (70 HP) and a second Deino (60 HP). Opening Active Deino stays 60 HP. No attack or Energy attachment is observed on this first turn. Scores 0-0. Evidence: 32, 38, 42, 48, 50s.

### Global 2, owner T1, about 51-77s

Draws Elegant Cape. Uses Professor's Research and obtains Team Rocket's Rattata plus another Professor's Research. Benches Rattata (40 HP); attaches the generated Water Energy to Active Vulpix. Plays Soothing Shore. Vulpix uses Gnaw for 20, reducing opposing Active Deino from 60 to 40 HP. Scores stay 0-0. Elegant Cape remains in hand at this point, not attached to opening Vulpix. Evidence: 52, 58, 64, 66, 68, 70, 72, 76s.

### Global 3, opponent own T2, about 78-123s

Benches Mega Absol ex (170 HP). Uses Rare Candy to evolve the damaged Active Deino into Hydreigon; carried damage leaves it at 130 HP. Roar in Unison supplies two Darkness Energy and causes 30 self-damage, and the normal Darkness attachment provides the three Energy needed for Hyper Ray. Hydreigon is at 100 HP before Lucky Ice Pop heals 20 to 120 HP. The Ice Pop coin is tails at 109s, so the item is discarded. Hyper Ray (130) knocks out opening Vulpix and discards Hydreigon's Energy. Opponent gains the first point, shown at 120s. Owner promotes Rattata. Evidence: 80, 84, 90, 94, 96, 100, 104, 109, 112, 116, 120, 124s.

### Global 4, owner T2, about 124-152s

Rattata is Active without Energy. Draws Copycat. Uses the remaining Professor's Research, obtaining Field Blower and Poké Ball. Poké Ball finds the second Alolan Vulpix. Benches that Vulpix at the right, attaches Elegant Cape and Water Energy to it. Vulpix is still a Basic with 60 HP; the Cape's Stage 1 HP increase has not yet applied. Owner ends without attacking; opposing Hydreigon remains 120 HP. Scores owner 0, opponent 1. Evidence: 124, 128, 130, 134, 138, 140, 144, 148, 150, 152, 153s.

### Global 5, opponent own T3, about 153-178s

Hydreigon uses Roar in Unison again, going from 120 to 90 HP. Ability-generated Darkness and the ordinary attachment replenish three Energy. Hyper Ray knocks out Active Rattata and discards all Hydreigon Energy again. Opponent gains point 2. The owner promotes the prepared Vulpix with Cape and one Water Energy. Evidence: 153, 156, 160, 164, 168, 172, 176, 178, 180s.

### Global 6, owner T3, about 179-204s

Draws Cyrus. Uses Sightseer: its four-card view includes Poké Ball, Rattata, Alolan Ninetales ex and Sabrina. Selects Ninetales ex and evolves Active Vulpix. Elegant Cape raises maximum/current HP to 180. Attaches the second Water Energy. Binding Snow is announced at 201s and deals 80 at 203s, leaving opposing Hydreigon at 10 HP. The attack places the next-turn restriction on taking Energy from the Energy Zone to attach to the opponent's Active Pokémon. This is the requested first main-attacker attack: owner T3, global 6, opponent 2 points. Scores remain 0-2. Evidence: 180, 182, 184, 185, 188, 189, 192, 194, 196, 198, 200, 201, 203, 204s.

### Global 7, opponent own T4, about 205-224s

Active Hydreigon has 10 HP and no Energy while the Binding Snow restriction is displayed. Opponent evolves the remaining benched Deino into a second Hydreigon through Rare Candy. The bench Hydreigon is 150 HP. A Darkness Energy is placed on benched Absol. No attack, healing or Active Energy recharge occurs. Scores remain 0-2. Evidence: 208, 212, 214, 216, 220, 222, 224s.

### Global 8, owner T4, about 225-250s

Draws Team Rocket's Raticate ex. Attaches a third Water Energy to Ninetales ex. Uses Binding Snow again, knocking out the 10-HP first Hydreigon. Owner receives point 1 at 248s; opponent promotes the 70-HP Absol carrying one Darkness Energy. Ninetales remains 180 HP. The next-turn Active attachment restriction is shown during the attack/KO sequence. Scores 1-2. Evidence: 226, 228, 230, 232, 236, 240, 244, 248, 252s.

### Global 9, opponent own T5, about 251-273s

Attaches Clear Veil to Absol; its prevention-of-attack-effects message is visible. Builds the benched second Hydreigon with Roar in Unison and a normal Darkness attachment, giving it three Darkness Energy and reducing it from 150 to 120 HP. Absol uses Enhanced Blade. Its attached Tool adds 30 to the printed 20, giving 50 damage to Ninetales ex (180 to 130). The native card text at 271s and 130-HP board at 273s confirm this; no Soothing Shore recovery is assigned to this opponent turn ending. Scores stay 1-2. No Mega Absol attack occurs. Evidence: 254, 256, 258, 260, 264, 268, 270, 271, 272, 273, 274s.

### Global 10, owner T5, about 274-332s

Draws and uses Poké Ball, finding another Team Rocket's Rattata. Benches it at the left. Ninetales stays at 130 HP during the extended decision interval. No Supporter or Energy attachment is observed on this turn; the generated Water Energy remains available while the owner examines the board. The confirmation at 313s explicitly warns that Energy can be attached and a Supporter can be used. Binding Snow deals 80 to Absol, knocking it out despite Clear Veil, which prevents effects rather than damage. Owner gains point 2. Opponent promotes the already charged, 120-HP second Hydreigon. The restriction message is visibly applied to the opponent side. Soothing Shore triggers and heals Ninetales 20 from 130 to 150 HP during this ending sequence. Scores 2-2. Evidence: 274, 276, 280, 282, 284, 286, 288, 292, 296, 300, 304, 308, 312, 316, 320, 324, 328, 330, 332s.

### Global 11, opponent own T6, about 333-352s

Hydreigon is Active at 120 HP with three Darkness Energy saved from the Bench. Attaches **Deceptive Needle**, whose enlarged card text is captured at 338s. Places a Darkness Energy on benched Mega Absol ex. Uses Hyper Ray for 130, reducing Ninetales from 150 to 20 HP and discarding the three Hydreigon Energy. At the end of the opponent turn, Deceptive Needle triggers for 10 more damage (349-351s), leaving Ninetales at 10 HP. This is not an unexplained 140-damage Hyper Ray or a Helmet effect. Scores stay 2-2. Evidence: 336, 337, 338, 340, 342, 344, 345, 346, 347, 348, 349, 350, 351, 352s.

### Global 12, owner T6, about 353-394s

Turn 12 banner at 353s. Draws the second Raticate ex. Evolves benched Rattata into Team Rocket's Raticate ex (120 HP) using the earlier card. Opposing Active Hydreigon already has no Energy after Hyper Ray; no Energy removal is observed from the evolution, and this review does not invent a successful Thieving Incisors transfer. Attaches Water Energy to benched Raticate ex. Leaves Ninetales Active at 10 HP with Cape and three Water Energy. Examines Binding Snow, accepts the reminder that a Supporter can still be used, and attacks anyway. The named Binding Snow banner at 386s precedes Hydreigon's 120 to 40 HP reduction at 388s. The restriction is displayed again. Soothing Shore heals Ninetales 20 from 10 to 30 HP at 390-393s. Scores stay 2-2. Evidence: 353, 355, 358, 360, 362, 364, 366, 370, 374, 376, 378, 380, 383, 384, 385, 386, 388, 390, 392, 394, 396s.

### Global 13, opponent own T7, about 395-438s

Active Hydreigon is 40 HP with no Energy and Deceptive Needle. Binding Snow's attachment restriction remains displayed. Opponent uses Copycat at 402s, shuffling/redrawing to match the owner's visible five-card hand count. Uses Lucky Ice Pop, healing Hydreigon to 60 HP, and flips heads (420s). Reuses it for another 20 heal to 80 HP and flips heads again (428s). Benches Bombirdier (70 HP), whose ability message reduces Darkness Pokémon retreat cost by one. No retreat, Energy recharge, attack, further Needle damage or knockout occurs before the opponent concedes. Explicit **Your opponent conceded** at 436-438s with final score 2-2. Evidence: 396, 400, 402, 404, 406, 410, 412, 414, 416, 418, 420, 422, 424, 426, 428, 430, 432, 434, 435, 436, 437, 438s.

### Terminal sequence, 439-447.65s

439-444s transition animation. 441s Victory banner. 447s final Victory versus 羊羽: Went second; Turns played 13; Your points 2; Opponent's points 2; Damage done 340. Alolan Ninetales ex is Card of the Game. The source ends with this result screen visible; no next match is present.

## Reconciliation and interpretation

Observed point sequence (owner-opponent): 0-0, 0-1 after Vulpix KO, 0-2 after Rattata KO, 1-2 after first Hydreigon KO, 2-2 after Absol KO, then concession. The displayed 340 damage agrees with opening Gnaw 20 plus four Binding Snow attacks of 80. Hydreigon self-damage, Lucky Ice Pop healing, Elegant Cape HP increase, Soothing Shore recovery and Deceptive Needle's separate 10 damage explain the meaningful HP changes. Bench Hydreigon preparation explains how Hyper Ray remains available while Binding Snow prevents an Active Energy recharge. Winning does not itself establish optimal choices.

Source-supported strategic observation: maintaining Ninetales Active repeatedly renews the Energy Zone restriction. Charging Hydreigon while benched allowed the opponent one more Hyper Ray despite that restriction. Raticate evolution occurred after the opposing Active Energy was already spent, so no successful evolution-trigger Energy theft is claimed. Field Blower, Ilima, Copycat and Cyrus remained visible alternatives late in the owner's hand; their optimal use is not evaluated without a full counterfactual analysis.

## Explicit limits

The complete supplied battle was reviewed, including every meaningful turn and the terminal screen. This is not an exact simulator replay. Hidden draws, hidden opponent hand contents and the unshown full deck remainder stay unknown. Trainer quantities and exact set identifiers are not inferred. Turn/action boundaries are approximate to the nearest retained frame unless an exact timestamp is named. No unobserved intention is attributed to either player. Independent acceptance, external Ladder Log saving and safe archival are pending lead actions outside this worker's write scope.
'''
(p/'REVIEW.md').write_text(review,encoding='utf-8')
turns=[(1,'opponent',32,50),(2,'owner',51,77),(3,'opponent',78,123),(4,'owner',124,152),(5,'opponent',153,178),(6,'owner',179,204),(7,'opponent',205,224),(8,'owner',225,250),(9,'opponent',251,273),(10,'owner',274,332),(11,'opponent',333,352),(12,'owner',353,394),(13,'opponent',395,438)]
coverage='''# Coverage

Reviewer: /root/evening_215114, gpt-6.1-sol high. Source: 20261014_215114000_iOS.MP4, SHA-256 b3170e7b962e7141ab0168cf4ca9aa2ce7e1241e6b750eee785eff51657c8a4a.

Method: first orientation at 15-second intervals, followed by original-resolution frames at every 4 seconds across battle play, then targeted 1-2-second frames around setup, Trainers, evolutions, attachments, attacks, coins, HP transitions and concession. All 18 phase sheets and 12 detail sheets were inspected, and decisive native images were individually inspected. Sampling was followed by turn/state reconciliation and adaptive dense checks; the coarse overview was not treated as a full review. Static waits and animation intervals were checked for before/after state continuity. Exact retained images are under evidence/.

| Phase | Source interval, seconds | Covered | Meaningful states/actions reconciled |
|---|---|---|---|
| Deck/matchmaking/setup | 0-31 | Yes | Label, core, ranked badges, opponent, opening five, Active selection |
'''
for g,who,a,b in turns:coverage+=f'| Global {g}, {who} | {a}-{b} | Yes | See corresponding REVIEW.md turn; Trainers, evolution, Energy, attack/pass, HP and points checked |\n'
coverage+='''| Terminal results | 439-447.65 | Yes | Concession then Victory, second, 13 turns, 2-2, 340 damage |

Scope check: one complete match; six owner turns and seven opponent turns, with the opponent conceding during global turn 13. Opening through ending accounted for. No unreviewed meaningful battle phase remains. Hidden information is a visibility limit, not an uncovered phase. No older source was opened. Independent lead acceptance remains pending.
'''
(p/'COVERAGE.md').write_text(coverage,encoding='utf-8')
s={'source_filename':'20261014_215114000_iOS.MP4','source_sha256':'b3170e7b962e7141ab0168cf4ca9aa2ce7e1241e6b750eee785eff51657c8a4a','source_bytes':829014558,'duration_seconds':447.65,'reviewer':'/root/evening_215114','model':'gpt-6.1-sol','reasoning_effort':'high','review_date':'2026-10-14','review_scope':'Complete source, setup through terminal, all meaningful actions in all 13 global turns','battle_complete':True,'review_of_available_source_complete':True,'match_count':1,'match_date':'2026-10-14','mode':{'classification':'human_ranked_ladder','auto_option_seen':False,'auto_enabled':None,'owner_choice_authorship':'visible manual taps','evidence':'evidence/t0019.00.jpg'},'deck':{'label':'Deck 13-A','visible_core':['Alolan Vulpix','Alolan Ninetales ex','Team Rocket\'s Rattata','Team Rocket\'s Raticate ex'],'full_twenty_card_list_established':False,'label_evidence':'evidence/t0000.00.jpg'},'opponent':{'name':'羊羽','visible_core':['Deino','Hydreigon','Mega Absol ex','Absol','Bombirdier'],'full_deck_unknown':True},'result':{'owner_result':'win','method':'opponent_concession','concession_source_seconds':436,'evidence':'evidence/t0436.00.jpg','victory_evidence':'evidence/t0447.00.jpg'},'score':{'owner':2,'opponent':2,'no_third_point_awarded':True,'progression':[[0,0],[0,1],[0,2],[1,2],[2,2]]},'order':{'owner':'second','evidence':'evidence/t0447.00.jpg'},'global_turns_played':13,'damage_done_displayed':340,'first_main_attack':{'pokemon':'Alolan Ninetales ex','attack':'Binding Snow','own_turn':3,'global_turn':6,'source_seconds':201,'source_time_window_seconds':[201,203],'opponent_points_before_attack':2,'evidence':['evidence/t0200.00.jpg','evidence/t0201.00.jpg','evidence/t0203.00.jpg','evidence/t0204.00.jpg'],'named_attack_banner':'evidence/t0201.00.jpg','damage_resolution':'evidence/t0203.00.jpg'},'exact_three_item_note_prefix':'2nd | Alolan Ninetales ex T3 | opp 2 pts','evidence_paths':['evidence/t0000.00.jpg','evidence/t0019.00.jpg','evidence/t0032.00.jpg','evidence/t0124.00.jpg','evidence/t0153.00.jpg','evidence/t0201.00.jpg','evidence/t0203.00.jpg','evidence/t0338.00.jpg','evidence/t0349.00.jpg','evidence/t0351.00.jpg','evidence/t0353.00.jpg','evidence/t0386.00.jpg','evidence/t0436.00.jpg','evidence/t0447.00.jpg'],'independent_acceptance_pending':True,'shared_registration_by_worker':False,'source_moved_by_worker':False,'external_write_by_worker':False,'boss_mirror_by_worker':False}
(p/'SUMMARY.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
u={'source_filename':s['source_filename'],'source_sha256':s['source_sha256'],'reviewer':s['reviewer'],'unreviewed_intervals':[],'blocking_uncertainties':[],'visibility_limits':[{'kind':'hidden_information','detail':'Opponent hidden draws/hand and unseen full deck contents are unknown; no reconstruction.'},{'kind':'deck_scope','detail':'Deck 13-A visible core established; exact twenty-card list and unseen Trainer quantities not claimed.'},{'kind':'timestamp_precision','detail':'Turn boundaries approximate; first main named attack banner 201s and damage 203s.'},{'kind':'counterfactuals','detail':'Outcome does not prove optimal decisions; no unsupported intentions or optimal-line claims.'},{'kind':'lead_work','detail':'Independent acceptance, registration, external saving and archival remain lead responsibilities.'}]}
(p/'UNCERTAINTIES.json').write_text(json.dumps(u,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Wrote REVIEW.md, COVERAGE.md, SUMMARY.json, UNCERTAINTIES.json; not frozen yet.')
