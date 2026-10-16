from pathlib import Path
import json, hashlib
P=Path(__file__).parent
summary={
 'source_filename':'20261015_020931000_iOS.MP4',
 'source_sha256':'a8e539e31976ed5591bba0a2cfba3db3a44168b61191e259b5cd55bf05e37060',
 'source_bytes':234200478,'duration_seconds':132.836667,
 'reviewer':'/root/night_020931','model':'gpt-6.1-sol','reasoning_effort':'high',
 'scope':'Complete supplied recording: prequeue, setup, all three global turns, concession, results',
 'first_pass_complete':True,'independent_acceptance':'pending separate checker and lead',
 'battle_complete':True,'match_count':1,'match_date':'2026-10-14','match_timezone':'America/Chicago',
 'exact_three_item_note_prefix':'1st | Alolan Ninetales ex no attack | opp N/A',
 'owner':'Dacz8976','opponent':'Rogshamosh','opponent_level':40,
 'results':{'owner_outcome':'win','reason':'opponent conceded','terminal_evidence':'evidence/t0119.00.jpg','victory_evidence':'evidence/t0132.00.jpg','owner_points':0,'opponent_points':0,'owner_damage_done':0,'global_turns_played':3,'owner_turn_at_end':2},
 'score':{'owner':0,'opponent':0,'points_awarded_by_concession':0},
 'mode':{'queue':'Ranked Match','season':'B4b SP','computer':False,'auto_option_observed':False,'pre_match_rank':'Master Ball Rank','pre_match_rank_points':758,'pre_match_standing':'Unranked','post_match_rank_points':None,'evidence':'evidence/t0002.00.jpg'},
 'deck':{'selected_name':'Deck 13-A','visible_core':['Alolan Ninetales ex','Alolan Vulpix','Team Rocket\u2019s Rattata','Team Rocket\u2019s Raticate ex'],'main_attacker':'Alolan Ninetales ex','exact_20_card_list_verified':False,'observed_opponent_core':['Bonsly (30 HP, Teary Attack)'],'observed_opponent_other_cards':['Professor\u2019s Research','Giant Cape'],'hidden_opponent_cards':'unknown'},
 'going_order':'first',
 'firstmainattack':{'pokemon':'Alolan Ninetales ex','attacked':False,'own_turn':None,'global_turn':None,'opponent_points_before_attack':None,'note':'No Alolan Ninetales ex attack; none is put into play. Owner deals zero damage and never attacks.'},
 'supporting_attacks':[],
 'recording_limits':['No apparent recording gap; whole match and terminal outcome are present.','Full hidden decks and opponent hand identities are not established.','Rank after the victory is outside the recording.','Opening share-code image retained but not decoded.'],
 'primary_files':['SOURCE.json','REVIEW.md','COVERAGE.md','UNCERTAINTIES.md','SUMMARY.json']
}
(P/'SUMMARY.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
review='''# Full first-pass review: 20261015_020931000_iOS.MP4

Reviewer: /root/night_020931. Model: gpt-6.1-sol, high reasoning. Review date: October 14, 2026 local / October 15 UTC. First-pass review covers the entire 132.836667-second supplied recording. Separate independent acceptance and lead completion remain pending.

Source binding: SHA-256 `a8e539e31976ed5591bba0a2cfba3db3a44168b61191e259b5cd55bf05e37060`, 234,200,478 bytes, native 1170 x 2532. See SOURCE.json for the bound path and probe. Native retained frames are under evidence; filenames encode source-local seconds. Contact sheets assist navigation and do not replace the native evidence.

## Result and required note

**1st | Alolan Ninetales ex no attack | opp N/A**

Dacz8976 wins against Rogshamosh by an explicit opponent concession on global turn 3, the owner's second turn. The final earned points are **0-0**, with owner damage done **0**. Do not convert the concession into three earned points. No owner attack occurs. Alolan Ninetales ex is the designated main attacker for Deck 13-A; it remains in hand until Copycat shuffles the hand back, never reaches the board, and never attacks. Team Rocket's Rattata and Team Rocket's Raticate ex also do not attack.

At 2.00 the queue explicitly reads Ranked Match, Season B4b SP, Master Ball Rank 758 pts, Unranked standing, with Deck 13-A selected. No Auto option appears in the supplied footage. This is a ranked human ladder match, not a computer or Pause Games review. The opponent introduction identifies Rogshamosh, level 40. The source UTC creation time is October 15 at 02:09:31, corresponding to October 14 at 21:09:31 America/Chicago. Postmatch rank changes are not shown.

## Timeline

| Source time | Turn/phase | Observed actions and state |
|---|---|---|
| 0.00-2.00 | Before queue | A Share With 2D Pattern Code overlay is open, then closes. The code is retained at t0000.00. At t0002.00 the selected Deck 13-A and ranked queue/rank are readable. The code was not decoded, so no exact 20-card list is claimed. |
| 3.00-18.00 | Matchmaking and introduction | Searching for opponent, then handshake/introduction for Rogshamosh, level 40. Loading leads directly into the same match. |
| 18.00-24.00 | Coin/order | Coin sequence, then the setup screen explicitly says the owner is going first. The final result screen independently confirms Went first. |
| 24.00-34.00 | Opening setup | Owner opening five contain Team Rocket's Rattata, Cyrus, Copycat, Professor's Research and Alolan Ninetales ex. Rattata is placed Active at 40 HP. No Bench is filled. Opponent reveals a lone Active Bonsly, 30 HP, Teary Attack 10; no Bench. The opponent Energy Zone shows Darkness. |
| 34.00-38.00 | Start global T1 / owner own T1 | Ready-Go and Current turn: 1. Both scores zero. Owner's turn-start draw is Elegant Cape (38-41). Rattata has no attached Energy, Bonsly has none. |
| 39.00-47.00 | Owner own T1 | Elegant Cape is inspected in hand, not attached. Owner plays Professor's Research, whose draw-two text and animation are visible (45-47). No evolution, Bench placement, Tool attachment or Energy attachment occurs. |
| 48.00-52.00 | Owner own T1 ending | Drawn cards are another Alolan Ninetales ex and Professor's Research; the Ninetales is inspected at 48.00. The hand remains Cyrus, Copycat, original Ninetales, Elegant Cape, Research and second Ninetales. Owner ends turn without attacking. Both Actives and scores unchanged. |
| 53.00-58.00 | Global T2 / opponent own T1 | Opponent's turn begins with Darkness Energy available. A turn draw animation is seen at 57.00. |
| 59.00-65.00 | Opponent own T1 development | Opponent plays Professor's Research and draws two (59-65). No additional Pokemon is placed. |
| 66.00-70.00 | Opponent own T1 attachments | Opponent attaches Darkness Energy to Bonsly and Giant Cape. Cape icon and +20 HP effect are visible at 67-70, raising current/max HP 30 to 50. The Tool's name is independently readable in the discard at 117.00. |
| 71.00-77.00 | Opponent own T1 attack | Bonsly uses Teary Attack. Weakness makes the displayed attack damage 30, reducing Team Rocket's Rattata from 40 to 10 HP. Teary Attack also places the visible attack-reduction marker; its printed text says the Defending Pokemon's attacks do 30 less damage during the opponent's next turn. No knockout or point is scored. |
| 78.00-87.00 | Global T3 / owner own T2 draw and decision | Owner's turn begins; Sabrina is drawn by 83-85. Rattata remains 10 HP, empty Bench, no Energy. Bonsly is 50 HP with Giant Cape and one Darkness Energy, empty Bench. Owner retains zero points; opponent retains zero. |
| 88.00-94.00 | Owner own T2 Copycat | Copycat is played. Its displayed effect shuffles the remaining hand into deck and draws for the opponent's hand count. Five cards are drawn: Field Blower, Team Rocket's Rattata, Team Rocket's Raticate ex, Poke Ball and Alolan Vulpix. No draw/search outside this visible effect is inferred. |
| 95.00-100.00 | Owner own T2 hand inspections | Field Blower, Rattata, Raticate ex, Poke Ball and Alolan Vulpix are individually inspected. These popups are inspections, not plays. The Raticate popup at 97.00 confirms 120 HP, Thieving Incisors and Boost Dash 70 costing two Colorless. Vulpix popup shows 60 HP and Gnaw 20. Neither Basic is benched and Poke Ball is not played. |
| 101.00-108.00 | Owner own T2 evolution/choice | Owner evolves the Active Team Rocket's Rattata into Team Rocket's Raticate ex. Existing 30 damage is retained, yielding 90 HP. At 107.00 the game asks Use the effect of Thieving Incisors? Owner accepts; the ability animation follows at 109.00. |
| 109.00-111.00 | Owner own T2 ability resolution | Thieving Incisors moves Bonsly's single attached Darkness Energy to Raticate ex. At 111.00 Bonsly has no attached Energy and Raticate has one. This is ability transfer, not the owner's ordinary Energy attachment and not an attack. Owner's generated Darkness Energy remains available in the zone. |
| 112.00-118.00 | Owner own T2 Tool removal | Owner plays Field Blower, with the card/effect visible at 112-114. Giant Cape is discarded from Bonsly at 116-117; the HP display returns from 50 to 30 by 118. This is loss of the Tool's HP increase, not attack damage. No Stadium is in play. Owner still has Rattata, Poke Ball and Vulpix in hand. No Bench, extra Energy attachment, retreat, or attack occurs. |
| 119.00-123.00 | Terminal sequence | Explicit banner: Your opponent conceded. The last board has Bonsly at 30 HP without Energy/Tool and owner Raticate ex at 90 HP with the stolen Darkness Energy. Both point counters are zero. This ends the battle during owner own T2, global T3. |
| 124.00-132.836667 | Result | Transition into Victory vs Rogshamosh. At 132.00 results read Went first, Turns played 3, both point rows empty/zero, Damage done 0, Card of the Game None. By 132.70 a subsequent result panel displays opponent Bonsly as its card. The clip ends on the completed victory result, without another match or updated ranked total. |

## Decisions and mechanics

The owner has only Rattata as an opening Basic, so the empty starting Bench is explained by the visible opening hand. Research and then Copycat seek additional development. Copycat produces the Raticate evolution and Basic options. The owner chooses the Active evolution, accepts Thieving Incisors, and removes Giant Cape with Field Blower. These actions visibly deny Bonsly's attached Energy and extra HP. The recording supports the sequence, but does not establish why the opponent conceded or whether any unseen hand line would have changed the game.

Raticate ex is specifically Team Rocket's Raticate ex, not Bibarel. Its 120 HP, printed name, Thieving Incisors and Boost Dash are readable at 97.00. The owner never attaches an ordinary Energy or uses Boost Dash before the concession. No supporting attack should be substituted for the requested Alolan Ninetales ex first-attack metric.

All meaningful recorded state changes reconcile: Rattata 40 to 10 from the sole attack, then evolution to Raticate 90 of 120; Bonsly 30 to 50 with Giant Cape, back to 30 when removed; Darkness Energy Bonsly to Raticate via ability; zero knockouts and zero earned points throughout. There are no switches, coin-dependent attacks, healing, special conditions, additional Pokemon on either Bench, or Stadium plays observed.

## Limits

No apparent recording gap or missing battle phase is observed. Hidden opponent hand/deck and exact owner 20-card list remain unknown. The visible shared code is available for later exact-list work but is outside this review's decoding scope. No postmatch rank total appears. The precise touch instant for Yes is bracketed by the prompt and successful ability resolution; the chosen effect is established by the transferred Energy. All statements are visual observations unless explicitly identified as explanation or limit.
'''
(P/'REVIEW.md').write_text(review,encoding='utf-8')
(P/'COVERAGE.md').write_text('''# Coverage checklist

Reviewer /root/night_020931, gpt-6.1-sol high. Source-bound first pass complete; independent checker and lead acceptance pending.

- [x] Entire supplied interval 0.00-132.836667 reviewed across overview and denser action frames.
- [x] Prequeue code, selected deck, ranked season, rank and matchmaking (0-18).
- [x] Coin/order and opening five/setup, both boards and zones (18-38).
- [x] Global turn 1, owner first turn: draw, inspection, Research, no attack, end (38-52).
- [x] Global turn 2, opponent first turn: draw, Research, Energy, Cape, attack and HP/effect (53-77).
- [x] Global turn 3, owner second turn: draw, Copycat, every displayed hand-card inspection, evolution, ability acceptance, Energy transfer, Field Blower, Tool/HP removal (78-118).
- [x] Concession and last board (119-123).
- [x] Victory, going order, global turns, actual points and damage done, final available panel (124-end).
- [x] All HP, Energy and score changes reconciled; no guessed third point or knockout.
- [x] Alolan Ninetales ex first-attack metric checked separately from supporting Pokemon: no owner attacks at all.
- [x] No visible Auto control; explicit ranked queue supports human ladder classification.
- [x] Source-local timestamps retained; all evidence JPEGs remain native 1170 x 2532.
- [x] One match only; no apparent internal recording gap; no unseen action reconstructed.

Frame selection starts with five-second overview intervals, then two-second action checks plus additional targeted one-second frames for queue, draws, evolution, ability and Tool removal. Card identities and result were checked on native frames. Repeated passive/transition views are bounded by unchanged state; no full-stream transcode was used. Source metadata was preverified in SOURCE.json by the lead; review uses that exact source path.
''',encoding='utf-8')
(P/'UNCERTAINTIES.md').write_text('''# Uncertainties and recording limits

No material ambiguity remains about winner, terminal reason, earned points, going order, deck core, or absence of an Alolan Ninetales ex attack.

- Exact owner 20-card composition and any hidden opponent deck/hand cards are not established. QR image is retained but not decoded. Copies observed in hand are not an exhaustive list.
- Opponent's reason for conceding is unknown. Do not infer an inability to recover solely from the concession.
- No updated rank or point gain after this victory is shown. Prequeue Master Ball Rank 758 pts and Unranked standing are directly visible at 2.00.
- Some animation/press instants are bracketed within the stated source intervals rather than assigned a false exact frame. Thieving Incisors acceptance is established by its successful Energy transfer.
- No apparent recording gap or missing opening/ending. Ending includes explicit concession and victory statistics. This first pass still requires separate independent checking and lead acceptance before registration/archive.
''',encoding='utf-8')
print('Wrote primary review files')
