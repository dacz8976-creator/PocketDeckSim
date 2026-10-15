import json,hashlib,subprocess,sys
from pathlib import Path
P=Path(__file__).resolve().parent
def load(n):return json.loads((P/n).read_text(encoding='utf-8'))
def save(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def eid(t):return 'f_'+f'{t:07.2f}'.replace('.','_')
L=load('TURN_LEDGER.json'); ts=L['turns']
ts[3]['source_interval_seconds'][1]=211
ts[3]['timing']['end_after_resolution_seconds']=211
ts[4]['source_interval_seconds'][0]=211
labels={1:44,2:64,3:108,4:128,5:211,6:229,7:280,8:327}
for t in ts:
 t['turn_label_evidence']={'displayed_current_turn':t['turn_number'],'timestamp_seconds':labels[t['turn_number']],'evidence_ids':[eid(labels[t['turn_number']])],'basis':'Actual visible Current turn transition label, read separately from ordinary snapshots.'}
 if t['who_played']=='opponent':
  for p in t['plays_in_order']:
   p['limit_reason']='Opponent touch input is not exposed on the owner device; this timestamp bounds the visible action/reveal/resolution, not a directly observed opponent finger input.'
ts[-1]['plays_in_order'][-1]['nested_events_in_order'][0]['evidence_ids']=[eid(356),eid(357),eid(358)]
ts[-1]['plays_in_order'][-1]['nested_events_in_order'][0]['result']='170 Damage is explicitly displayed at356; HP0 at357; Skarmory is removed by358 and absent359.'
save('TURN_LEDGER.json',L)
E=load('TURN_EVIDENCE.json')
for f in E['frames']:
 tm=f['requested_source_seconds']
 if 211<=tm<229:f['turn_number']=5;f['who_played']='owner'
 if f['selected_for_start_hand'] or f['role']=='before_end_action':
  f['visual_inspection'].update({'full_frame':'inspected','bottom_crop':'inspected_native','top_crop':'inspected_native'})
 if tm in [31,67,132,145,163,185,232,330,356,357,358,359,211]:f['visual_inspection']['full_frame']='inspected'
 if tm==211:f['observation']='Actual Your turn / Current turn5 transition before normal draw.'
 if tm==356:f['observation']='Native impact explicitly displays170 Damage on Skarmory.'
 if tm==357:f['observation']='Skarmory current HP0; card still visible before removal.'
 if tm==358:f['observation']='Skarmory removal animation; do not represent it as occupied terminal Active.'
save('TURN_EVIDENCE.json',E)
review='''# Pause Games review: 20261005_034229000_iOS.MP4

Dacz8976 loses 0-3 against Tideisrising91 in eight actual turns. The final screen confirms that the owner went first and dealt 110 damage. This worker packet is complete with recording limits and awaits independent acceptance. No Auto control is visible. Online matchmaking and opponent identity are filmed, but the particular ranked or casual queue is not shown.

The frozen SOURCE.json binds the 684,713,902-byte video, SHA-256 0bb007528bcaa32a3ee7abbbbf8f5dfaeeb976140d3aaedd774de3e73ee681b2, duration 374.588333 seconds and native 1170x2532 frame size. Embedded movie creation time is 2026-10-05T03:42:29Z, which is October 4, 2026 at 22:42:29 in America/Chicago. The filename is not treated as a local match date. Timestamps here are source-local requested seeks; actual decoded presentation timestamps were not measured.

Source-wide overview inspection located the setup, all eight turns, meaningful actions and final result. Dense native evidence then resolves opening cards, actual owner input brackets, each card reveal, targets, Energy transfers, draw-timed hands and post-resolution boards. A fixed overview grid does not establish the owner start hand. Native full frames and bottom/top crops are retained and indexed in TURN_EVIDENCE.json. Hidden opponent card identities remain unnamed.

At 24.8 seconds, before Active placement, the five cards from left to right are standard-art Metal Core Barrier, Orthworm (Iron Supply, 100 HP), Professor's Research, gold-border Honedge (Pierce, 60 HP), and Poke Ball. Orthworm is placed Active around 26-28; Honedge is placed in owner bench position 1 around 31-33. No opening redraw is filmed. Opponent Active is Ralts, 60 HP, with all three bench positions empty.

Turn 1 is labeled at 44. The normal draw is gold-art Metal Core Barrier at 45-46.2. Selected native frame 46.2 shows the intact four-card hand before first input. Poke Ball input is bounded by 46.5-47.0; Skarmory ex is revealed at 50 and reaches hand by 52.2. The reveal is not the first input. Skarmory ex, 140 HP, is benched in position 2 by 54. Research input is around 56.5-57; it reveals Aegislash (Cursed Metal, 140 HP) first at 60.5 and Lucky Ice Pop second at 61.5. Before End Turn at 62.5, the hand is both Core Barriers, Aegislash, Pop. End Turn at 63-63.5 has no attack and no Energy attachment: the first player's current Energy Zone is empty. Opponent fan has four cards.

Turn 2 is labeled at 64. Hidden normal draw makes the opponent fan five. Opponent attaches Psychic to Ralts at 78, plays Poke Ball at 81 with a hidden search by 83, Research at 86 with two hidden draws by 90, and another Poke Ball at 93 with a hidden search by 96. Confuse Ray at 103-107 causes Confusion without damage: Orthworm stays 100 HP. Ralts has one Psychic; opponent bench stays empty and its end fan has six. The opponent's finger inputs are not exposed, so these timestamps bound displayed actions rather than claimed touches.

Turn 3 is labeled at 108. Normal Steel Apron draw ends around 111; selected frame 111 has five intact cards. The first owner input at 111-112 is Steel Apron, followed by its target prompt at 112. It attaches to Orthworm, applies incoming attack damage -10 and condition recovery/immunity, then the recovery message clears Confusion at 119. Regular Metal attachment at 118 gives Orthworm one Metal. Intact before-attack hand at 119.3 has both Cores, Aegislash and Pop; the recovery banner still overlays the upper board. Iron Supply attack input is bounded 119.3-119.8. It deals 10 to Ralts, lowering 60 to 50, and the nested additional-Energy choice targets benched Honedge at 125-126. By 127, Orthworm and Honedge each have one Metal. The extra Energy is an attack effect, not a second ordinary attachment.

Turn 4 is labeled at 128. Hidden normal draw makes the opponent fan seven. Dark-art Mewtwo ex is benched in position 2 around 140, then gold-art Mewtwo ex in position 3 around 145, both 150 HP. Peculiar Plaza is placed at 150-154 and remains the Stadium, reducing Psychic retreat cost by two. Copycat at 158-163 returns the three remaining hidden hand cards after Copycat leaves hand, then draws four to match owner hand count four. Rare Candy at 169-174 evolves Ralts directly into Mega Gardevoir ex. It retains one Psychic and inherited 10 damage, so current HP is 200 of printed 210. Mega Diancie ex, 170 HP, is benched in position 1 around 176-179. Regular Psychic at 181 gives Gardevoir two. Fantasia Force at 185-195 deals 110 minus Steel Apron 10, knocking out the 100-HP Orthworm, and attaches three extra Psychic to Diancie. Opponent earns one point by 200. Orthworm, its tool and Energy leave the board. The forced owner replacement prompt at 203 selects Skarmory ex at 207-209. This replacement is nested in the opponent KO, not an additional owner turn. Both Mewtwos still have zero Energy and the opponent ends with one hidden card.

Turn 5 is visibly labeled at 211. Normal draw reveals Rare Candy at 213; selected intact frame 213.7 contains both Cores, Aegislash, Pop and Candy. Candy input at 213.7-214 consumes Candy and the hand Aegislash to evolve Honedge in bench position 1. Aegislash resolves at 217.7 with 140 HP and keeps Honedge's one Metal. Cursed Metal applies at 219: attacks used by the owner's Psychic and Metal Pokemon do +30 to the opponent's Active. It does not increase the opponent's Diancie attack. Gold Core Barrier is attached to Skarmory around 220.5-223, before the regular Metal attachment around 223-225. Skarmory now has one Metal. Intact hand 227.5 has standard Core and Pop, count two. End Turn at 228 has no attack, as Steel Wing requires two Metal. No Special Conditions remain.

Turn 6 is labeled at 229. Hidden normal draw gives opponent fan two. The long waiting interval has no additional visible action. Regular Psychic at 258-260 targets the dark-art Mewtwo in bench position 2, not Gardevoir. Fantasia Force at 266 deals 110 minus gold Core Barrier 50, lowering Skarmory 140 to 80. Its three extra Psychic also go to dark Mewtwo, giving that Pokemon four total. By 280, Gardevoir still has two, Diancie three, gold Mewtwo zero. Gold Core expires and is discarded at opponent turn end, 276-280. Owner hand remains standard Core plus Pop.

Turn 7 is labeled at 280. Honedge normal draw occurs at 282 and selected frame 283 has the intact three-card hand before the 283-283.8 bench input. This Honedge is placed in the RIGHT bench position 3, with the middle position 2 empty. Lucky Ice Pop is used three separate times: first input 285.8-287 heals 80 to 100, Heads at 294 returns it; second 296-298 heals 100 to 120, Heads at 303 returns it; third 305-307 heals 120 to 140, Heads at 312 returns it. The same returned card is used again; three Pop uses do not establish three copies in the deck. Standard Core Barrier is then attached around 313-316, followed by regular Metal around 317-318. Skarmory reaches two Metal by the attack menu at 321. Before-end frame 320 has intact one-card hand, Lucky Ice Pop, while the Energy animation is still resolving. Steel Wing at 321-324 deals 70 plus Cursed Metal 30, lowering Gardevoir 200 to 100, and gives Skarmory incoming attack damage -20 during the next opponent turn. Native 326 confirms two attached Metal, Core Barrier and the Steel Wing effect.

Turn 8 is labeled at 327. Hidden normal draw makes opponent fan three. Regular Psychic at 334 gives Gardevoir a third Psychic. It retreats at 347-349 for zero under Peculiar Plaza, retains all three Psychic and moves to bench position 1, while Mega Diancie becomes Active. Native 352 shows ten opposing Psychic Energy: Diancie three, Gardevoir three, dark Mewtwo four, gold Mewtwo zero. Native 355 clearly names Brilliant Storm and shows its rule: 40 plus 20 for each Psychic Energy on all the attacker's Pokemon. The calculated raw 240 is reduced by Steel Wing 20 and Core Barrier 50 to 170. Independently, native 356 explicitly displays 170 Damage. Skarmory HP is zero at 357, it is removed by 358 and the Active position is empty at 359. Opponent earns two more points to reach three at 361; owner remains zero. Defeat at 364 and final statistics at 373-374 establish the loss. No terminal owner replacement occurs because the game ends. Owner remaining bench is Aegislash 140 HP with one Metal at position 1, empty position 2, Honedge 60 HP with zero Energy at position 3. Opponent Active Diancie is 170 HP with three Psychic; bench Gardevoir is 100/210 HP with three Psychic, dark Mewtwo 150 HP with four Psychic, gold Mewtwo 150 HP with zero Energy.

No QR, deck list or deck selection is filmed anywhere from search to result. The visible owner core is Skarmory ex / Aegislash / Orthworm. The nearby 033529 QR is a qualified candidate only; an unrecorded gap does not prove an unchanged twenty-card list. DECK_USED.json leaves the exact played/log snapshot null with that reason. Full discard piles are never opened or scrolled. Scheduled discard records are explicit top previews only, and visible KO transfers do not establish complete ordered piles. No separate no-effect action or explicit decline is filmed; hidden choices are not invented. This worker performed no external registration, source movement or archival. Structural validation and worker reconciliation are not independent acceptance.
'''
(P/'REVIEW.md').write_text(review,encoding='utf-8')
coverage='''# Source coverage and capture limits

The reviewed source interval is 0.000-374.588333 seconds, from online matchmaking to final result. All 125 overview midpoint frames at three-second spacing were inspected across 14 sheets to locate phases/actions. Dense native evidence then supports every meaningful action, input/reveal/resolution boundary, actual turn, Energy transfer and result. A full real-time uninterrupted playback and decoded-PTS audit are not claimed. Long waits are recorded as waits. No later QR, deck selection or Auto control is visible.

| Seconds | Phase | Native evidence anchors |
|---|---|---|
| 0-43 | Search, opponent identity, first-player setup, five-card opening and placement | 24.8, 26, 28, 31, 40, 44 |
| 43-64 | T1 normal Core draw, Poke Ball search, Skarmory bench, Research draws, End Turn | 46.2, 46.5, 46.8, 47.2, 50, 52.2, 54, 57, 60.5, 61.5, 62.5, 63, 63.5, 64 |
| 64-108 | T2 normal hidden draw and five voluntary actions, ending Confuse Ray | 67, 78, 81, 83, 86, 90, 93, 96, 103, 107, 108 |
| 108-128 | T3 Apron prompt/recovery, regular Energy, Iron Supply and nested target | 110, 111, 112, 114, 117, 118, 119.3, 119.8, 124, 125, 127, 128 |
| 128-211 | T4 two Mewtwos, Stadium, Copycat, Candy, Diancie, Energy, attack, KO and forced replacement | 132, 140, 145, 150, 160, 163, 169, 172, 174, 176, 179, 181, 185, 188, 195, 200, 203, 207, 209, 210, 211 |
| 211-229 | T5 normal Candy, evolution, Core before Energy, End Turn | 211, 213, 213.5, 213.7, 214, 214.5, 216.5, 217.7, 219, 219.5, 222, 225, 227.5, 228, 229 |
| 229-280 | T6 wait, regular Energy to Mewtwo, attack, extra Energy, Core expiration | 232, 258, 260, 266, 269, 274, 276, 280 |
| 280-327 | T7 normal Honedge, right bench, three Pop inputs and Heads, Core, Energy, Steel Wing | 282, 282.7, 283, 283.8, 285.8, 286, 288.8, 294, 295, 298, 303, 304, 307, 312, 313, 316, 318, 320, 321, 324, 326, 327 |
| 327-374.588333 | T8 hidden draw, Energy, free retreat, Brilliant Storm, KO, points, Defeat and statistics | 330, 334, 349, 352, 355, 356, 357, 358, 359, 361, 364, 374 |

All actual Current turn labels are retained and read: 1 at 44, 2 at 64, 3 at 108, 4 at 128, 5 at 211, 6 at 229, 7 at 280 and 8 at 327. Ordinary board snapshots often do not display that label, and their displayed-label fields remain null with a reason. Turn sequence is not substituted for a label on a particular frame.

The five-card opening is directly inspected at native 24.8, before Active placement. Four owner turns have twelve draw-end +1/+3/+6 candidate full/bottom/top captures. Each candidate occurs after an input, so none is falsely selected as an intact turn-start hand. Earlier dense intact selections 46.2, 111, 213.7 and 283 establish the respective post-draw preplay hands. Candidate draw ends are visual estimates, with requested offsets relative to those estimates, not measured PTS. Before-end full/bottom/top frames 62.5, 119.3, 227.5 and 320 are separately inspected. The 119.3 top has a recovery banner; 320 still resolves the final Energy, with 321/326 independently proving the resolved count.

Retained dimensions are native 1170x2532. Bottom fifth bounds are [0,2025,1170,2532], top bounds [0,0,1170,730]. Crops supplement full native frames; the bottom fifth alone can truncate card headers, so identities are read in the full view. Opponent hidden fan identities remain unknown. Full discard pile views/scrolls are absent at the scheduled turns, and periodic top previews are explicitly partial. Exact played twenty-card list remains unverified because this source shows no QR, deck list or filmed selection binding the nearby candidate.
'''
(P/'COVERAGE.md').write_text(coverage,encoding='utf-8')
# Executable reconciliation supplements the authored arithmetic.
assert [t['turn_number'] for t in ts]==list(range(1,9))
assert [t['owner_hand_start']['count'] for t in ts[::2]]==[4,5,5,3]
assert [t['owner_hand_end']['count'] for t in ts[::2]]==[4,4,2,1]
assert [len(t['plays_in_order']) for t in ts]==[4,5,3,8,4,2,7,3]
assert [t['opponent_hand_at_owner_turn_start']['count'] for t in ts[::2]]==[4,6,1,2]
assert ts[5]['board_after']['opponent']['active']['attached_energy']['by_type']=={'Psychic':2}
assert ts[5]['board_after']['opponent']['bench_in_position_order'][1]['attached_energy']['by_type']=={'Psychic':4}
assert ts[6]['board_after']['owner']['active']['hp_now']==140
assert ts[6]['board_after']['owner']['active']['attached_energy']['by_type']=={'Metal':2}
assert ts[-1]['board_after']['owner']['active']['status']=='visible_empty'
assert ts[-1]['board_after']['opponent']['points']==3
assert ts[-1]['plays_in_order'][-1]['observed_damage']['amount']==170
receipt=load('WORKER_CONSISTENCY.json');receipt['executable_assertions']='All eleven hand/action/fan/Energy/terminal assertions passed after final JSON read.';save('WORKER_CONSISTENCY.json',receipt)
result=subprocess.run([sys.executable,str(P.parent/'validate_packet.py'),str(P)],capture_output=True,text=True,encoding='utf-8')
(P/'VALIDATION.json').write_text(result.stdout,encoding='utf-8')
print(result.stdout)
if result.returncode:raise SystemExit(result.returncode)
names=['SOURCE.json','REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json','WORKER_CONSISTENCY.json','VALIDATION.json']
save('WORKER_PACKET_MANIFEST.json',{'worker_complete':True,'independent_acceptance':False,'files':[{'path':n,'bytes':(P/n).stat().st_size,'sha256':hashlib.sha256((P/n).read_bytes()).hexdigest()} for n in names]})
