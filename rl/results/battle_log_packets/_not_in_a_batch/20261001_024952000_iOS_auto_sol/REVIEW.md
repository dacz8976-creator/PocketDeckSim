# Full first-pass battle review

**Current status: completed full-battle review accepted by the lead; original archived unchanged in `Reviewed`. Excluded from Ladder Log.**

Reviewer: sol_auto_evening_024952000. Model: gpt-6.1-sol, high reasoning. Reviewed October 1, 2026 UTC. Status: full review accepted by the lead, registered and archived. The worker did not perform global registration or movement. The lead has since registered completion and archived the original; no Ladder Log entry was created.

Source: 20261001_024952000_iOS.MP4, 271.01 seconds. Immutable identity is in SOURCE.json, SHA-256 74748aec4973d0748eb81229186e3aeb65bb346c50930092400d24bb961ed19e. The lead's intake event verified identity; this worker reused that binding and decoded the assigned original. Filename clock basis remains unverified. Owner identifies these as Auto AI games and excludes them from Ladder Log.

The owner loses on turn 14. The circles show owner 2, opponent 3; actual opponent awards total 5, comprising Victini 1, Pansear 1, and Mega Camerupt ex 3. The result at native 270.90 seconds says "vs. Mega Scizor ex & Gholdengo ex Deck (Deluxe Pack: Mega)" and "Defeat...", with Mega Scizor ex as Card of the Game. No damage statistics panel is shown before the recording ends.

## Method and mode

All setup and turns 1 through 14 were inspected through the complete 3-second overview, then targeted native-resolution frames. Overview labels are fps sampling midpoints, not action-start timestamps. Timeline ranges below are approximate phase boundaries; native frame filenames are exact requested source times. COVERAGE.md maps every phase to retained evidence.

Auto is checked during setup, the early turns, and the ending. There is a real interruption during turn 11: native 191.00 still has checked Auto, 194.00 has an empty gray toggle and an End Turn button, and 210.00 still has Auto off. The overview at 211.50 has checked Auto again. Bounded Field and the second owner Poke Ball are played within the off interval. They must not be attributed to uninterrupted Auto policy. The precise input that changed the toggle and the person's intent are not visible.

## Visible cards and relevant printings

Owner: Victini, Numel, Mega Camerupt ex, Pansear. A second Mega Camerupt ex, Pansear, Simisear, second Numel, and second Victini become visible in hand without being played. Trainers actually played are Rocky Helmet, two Poke Balls, two Professor's Research, Elegant Cape, and Bounded Field. Two Flame Patches stay in hand throughout the match.

Opponent: Wynaut, two Honedge, Doublade, Gimmighoul to Gholdengo ex, and two Scyther with one evolving to Mega Scizor ex. Professor's Research, two Poke Balls, Skyla, and Training Area are publicly played. Hidden cards and the full deck list remain unknown.

Native text establishes Mega Camerupt ex as 210 HP, Stage 1 from Numel, with Volcanic Kaboom costing three Fire and one Colorless: randomly choose one opposing Pokemon and do 160 damage to it (214.00). It has no printed Energy-discard effect. Mega Scizor ex has 200 HP and Bullet Slugger 100 plus 50 if it moved from Bench to Active that turn (238.00). Both give three points when knocked out. Elegant Cape gives its attached Stage 1 Pokemon 30 extra HP (186.00). Bounded Field explicitly excludes Mega Evolution ex attackers from its doubled Weakness effect (198.00). These readings agree with the local deckgym-database.json entries; this is corroboration, not an engine replay.

## Complete timeline

### Setup and turn 1, owner, approximately 0-22 seconds

The opening matchup/loading animation leads to Dacz8976 versus Opponent. Owner starts Victini Active at 70 HP and Numel on Bench at 70. Opponent starts Wynaut Active at 30. Owner goes first. The visible starting hand includes two Flame Patches and Mega Camerupt ex; Rocky Helmet becomes the first-turn draw. Victini's Victory Star explanation appears, but this popup is not an ability activation or coin flip. Owner attaches Rocky Helmet to Victini, then passes without an attack or Energy attachment. Native 13.00 shows the starting core; 18.00 shows Helmet before play; overview 19.50 displays its printed effect and 22.50 marks opponent turn 2.

### Turn 2, opponent, approximately 22-33 seconds

Opponent benches Honedge at 60 HP, plays Professor's Research, attaches one Metal Energy to Honedge, and benches Gimmighoul at 60. Wynaut stays Active at 30 and does not attack. Owner Victini remains at 70. Native 30.00 and 31.00 cover the developing board; 37.00 shows the settled state after the turn and the Professor's Research discard. The enlarged owner Poke Ball around the next draw is not an opponent Poke Ball play.

### Turn 3, owner, approximately 33-53 seconds

Owner draws Poke Ball, evolves benched Numel directly into Mega Camerupt ex at 210, plays Poke Ball to obtain Pansear, benches Pansear at 60, and attaches one Fire Energy to Mega Camerupt ex. Victini remains Active without Energy and does not attack. Native 39.00 captures evolution, 41.00 the owner Poke Ball play, 49.00 Pansear entering Bench, and 51.00 the settled one-Energy Mega. No Rare Candy is played.

### Turn 4, opponent, approximately 53-71 seconds

Honedge evolves into Doublade at 90. Opponent plays its first Poke Ball and benches Scyther at 70. Wynaut retreats for free into Doublade, and a second Metal Energy goes to Doublade. Slash does 40: Victini 70 to 30. Rocky Helmet then does 20 to the attacker: Doublade 90 to 70. Native 54.00, 56.00, 59.00, 61.00, 63.00, 65.00, 67.00 and 69.00 establish the development, switch, attack and retaliation. Score stays 0-0.

### Turn 5, owner, approximately 71-81 seconds

Owner draws a second Mega Camerupt ex and attaches a second Fire Energy to the benched Mega Camerupt ex. The drawn card remains in hand. Victini stays Active at 30 with Rocky Helmet, Pansear remains at 60 on Bench, and no attack occurs. Native 72.00 and 80.00 bracket the Energy increment and unchanged board. Neither Flame Patch is used.

### Turn 6, opponent, approximately 81-106 seconds

Scyther evolves into Mega Scizor ex at 200. Opponent plays its second Poke Ball and begins charging the benched Mega Scizor with one Metal Energy. Doublade attacks Victini again with Slash for 40. Victini reaches zero; Rocky Helmet still returns 20, leaving Doublade at 50. Opponent receives one point. Owner promotes Pansear at 60, while Mega Camerupt ex remains Benched at 210 with two Fire Energy. Native 85.00 shows Poke Ball and the new Mega, overview 91.50-100.50 shows damage, Helmet and award, and native 106.00 shows the promotion. The fetched hidden Basic is not identified merely from the Poke Ball animation.

### Turn 7, owner, approximately 106-119 seconds

Owner draws a second Pansear but leaves it in hand, attaches one Fire Energy to Active Pansear, and attacks Doublade with Beat. Its printed 10 plus Fire Weakness 20 gives 30 damage, taking Doublade 50 to 20. Mega Camerupt remains at two Energy. Native 110.00, 112.50 overview and 120.00 cover the card, attack and settled state. Score is owner 0, opponent 1.

### Turn 8, opponent, approximately 119-137 seconds

Opponent attaches a second Metal Energy to Mega Scizor ex. Skyla switches Active Stage 1 Doublade into Wynaut. Wynaut then retreats for free back into the same Doublade. The two Metal Energy on Doublade remain, consistent with the switch and free retreat rather than paying Doublade's two-Energy retreat cost. Native 123.00 and 125.00 show Wynaut Active with Skyla in the discard; 126.00 shows Doublade returning. Skyla's text is corroborated by the local catalog: switch your Active Stage 1 with a Benched Pokemon. Opponent plays Training Area, which adds 10 damage to attacks by Stage 1 Pokemon against the opposing Active. Doublade's Slash now does 50, taking Pansear 60 to 10. Native 128.00 and overview 130.50-136.50 establish the Stadium and damage. No points are awarded.

### Turn 9, owner, approximately 137-158 seconds

Owner attaches a third Fire Energy to Mega Camerupt ex, plays Professor's Research and draws Simisear plus Poke Ball. Simisear is revealed/drawn, not evolved onto Pansear. Pansear stays at 10 HP with one Fire Energy and uses Beat again for 30 including Weakness, knocking out the 20-HP Doublade. Owner receives one point and opponent promotes Wynaut at 30. Native 142.00 shows three Energy on the Mega and Research before play; 145.00 displays Simisear; overview 148.50-157.50 covers Beat, the award and Wynaut. Score becomes 1-1.

### Turn 10, opponent, approximately 158-178 seconds

Opponent benches a second Honedge at 60 and attaches a third Metal Energy to Mega Scizor ex. Wynaut uses Stompy Jammer, a zero-Energy 10-damage attack, knocking out Pansear at 10. Its printed next-turn cost increase applies to the Defending Pokemon; that Pansear is knocked out. Opponent gets one point and owner promotes Mega Camerupt ex at 210 with three Fire Energy. Native 162.00 shows the new Honedge and third Scizor Energy; overview 163.50-175.50 covers the attack, knockout, award and promotion. Score becomes owner 1, opponent 2. No Metal attachment to Wynaut is asserted.

### Turn 11, owner, approximately 178-223 seconds

Owner plays a second Professor's Research, revealing Elegant Cape and Bounded Field. Elegant Cape is attached to Mega Camerupt ex, increasing displayed HP from 210 to 240. The turn then includes the documented Auto-off interval. Bounded Field replaces Training Area. Owner's second Poke Ball is played and finds Numel, which remains in hand. Auto resumes before the final attachment/attack. A fourth Fire Energy is attached to Active Mega Camerupt ex, enabling Volcanic Kaboom. The attack randomly hits the opposing benched Honedge, not Active Wynaut, for 160, knocking Honedge out and awarding one point. Wynaut stays at 30, Gimmighoul at 60 and Mega Scizor at 200. Owner Bench remains empty. Native 181.00, 186.00, 191.00, 194.00, 198.00, 200.00, 207.00 and 210.00 distinguish Research/Cape, pause and actual Trainer plays. Overview 211.50-220.50 shows resumed Auto, attachment, random hit and point award. Score becomes 2-2. Both Flame Patches remain in hand, so the four Energy are not evidence of a Patch play.

### Turn 12, opponent, approximately 223-242 seconds

Gimmighoul evolves into Gholdengo ex at 150. Wynaut retreats for free into the charged Mega Scizor ex. Opponent benches a second Scyther at 70 and attaches one Metal Energy to Gholdengo ex. Mega Scizor uses Bullet Slugger with its same-turn promotion bonus for 150 damage: Mega Camerupt 240 to 90. Bounded Field remains. Native 225.00 and 228.00 cover evolution, 232.00 promotion, 238.00 the attack wording and 244.00 the resulting HP and one Energy on Gholdengo. Score stays 2-2.

### Turn 13, owner, approximately 242-252 seconds

Owner draws a second Victini and leaves it in hand. Auto attaches a fifth Fire Energy to Mega Camerupt ex, despite already meeting the four-Energy cost. No new Basic is benched. Volcanic Kaboom randomly selects Active Mega Scizor ex and does 180: its base 160 plus normal Fire Weakness 20. Mega Scizor goes from 200 to 20, surviving. Bounded Field does not double this Mega attack. Native 244.00 shows the new Victini in hand and pre-attack four Energy; 248.00 the attack; 251.00 the settled five Energy and Scizor at 20. No coin flip or Victory Star reroll occurs. Score stays 2-2.

### Turn 14 and result, approximately 252-271.01 seconds

Mega Scizor stays Active, so Bullet Slugger is 100 rather than 150. Its settled attached Energy remains three Metal; Gholdengo remains at one. No additional settled attachment is evidenced. Native 255.00 shows Bullet Slugger, and 258.00-260.00 show Mega Camerupt removed. Its 90 remaining HP cannot survive the 100 attack. Opponent receives three points for the Mega knockout, bringing awards to five although the circles cap at three. Native 263.00 shows the explicit +3 award and owner still at two. Defeat appears by 266.00. Native 270.90 supplies the named computer challenge and Card of the Game. The recording ends during that result view, without another match or results-statistics page.

## Findings and limits

1. Damage, HP, Energy and points reconcile: two Helmet returns account for Doublade 90 to 50; two weak Beat attacks account for its remaining 50; Training Area accounts for the 50 Slash; Elegant Cape accounts for 240 maximum HP; promoted Bullet Slugger accounts for 240 to 90; Volcanic Kaboom plus Weakness accounts for Scizor 200 to 20; ordinary Bullet Slugger ends the battle.
2. Bounded Field provides no doubled Weakness to Mega Camerupt. Replacing Training Area removes the shared +10 Stage 1 damage, but this footage does not show that decision causing the loss. Retaining it would still leave Scizor alive after one 160-based Active hit, and the final 100 attack would still be lethal in that observed line. This is a conditional arithmetic comparison, not an observed alternative game.
3. The two random Volcanic Kaboom selections matter: the first gets a single-point Bench knockout and the second damages the three-point Mega without knocking it out. On turn 13 each of the three Benched targets had at most 160 HP and would have supplied the remaining point if selected; the actual Active Mega was the only visible target that survived this hit. No numerical probability is asserted. These are attack randomness, not coin results or intentional target choices.
4. The opponent's Skyla-to-Wynaut then free-retreat-to-Doublade sequence consumes a Supporter and ends with the same attacker and Energy. It is visible policy behavior, with no rule mismatch established.
5. Owner Auto attaches a fifth Energy rather than developing the empty Bench on turn 13, with Numel/Pansear/Victini available in hand. A backup could change later lines, but cannot prevent the immediate opponent win from a three-point Mega knockout in this position. The footage alone does not establish a winning alternative. Simisear was available earlier, but it was not played and no Fury Swipes coins occurred.
6. No healing, Burn, Sleep, paralysis, poison, Energy transfers, or actual Victory Star activation is observed. Unknown hidden cards, exact unseen deck counts and manual intent are retained as unknowns. No battle phase remains unreviewed in the supplied recording.


## Lead completion

Accepted as a completed full-battle review after the source checks documented in `LEAD_ACCEPTANCE.json`. The unchanged original is archived in `Reviewed`; matching before/after SHA-256 is recorded in `MOVE_RECEIPT.20261001_024952000_iOS.MP4.json`. No Ladder Log entry was created.
