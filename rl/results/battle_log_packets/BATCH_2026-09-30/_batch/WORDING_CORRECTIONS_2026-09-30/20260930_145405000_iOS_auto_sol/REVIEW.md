# Full battle review: 20260930_145405000_iOS.MP4

**Current status: completed full-battle review accepted by the lead; original archived unchanged in `Reviewed`. Excluded from Ladder Log.**

Reviewer: sol_auto_145405000. Model: gpt-6.1-sol, high reasoning. Review date: September 30, 2026. Scope: the entire 147.196667-second recording, loading and setup, all eight turns, terminal attack, Victory, and results screen. This is the source-bound Sol first pass for lead acceptance; the worker did not finalize shared records or move media.

Outcome: Dacz8976 wins 3-0, going second, against the AI opponent. The results screen identifies the opponent challenge as **Aegislash Deck (Deluxe Pack: Mega)**, shows eight turns played and damage done 360. This is an autopilot computer battle, excluded from the Ladder Log. The opening visibly labels the opponent AI (`keyframes/t0004.50.jpg`), and the green checked Auto indicator is present during setup and throughout gameplay. No visible switch to manual mode occurs.

## Source and method

The exact source is bound by `SOURCE.json`: SHA-256 `5ffb8cd9f98fc90eedcb61778bc3c9716caffdbf84714eb92883a59993f9eac8`, 267745666 bytes, 1170 x 2532 HEVC, 147.196667 seconds. Identity was verified by the lead's registered intake event, not independently rehashed by this worker. Source bytes were preserved.

All six 3-second overview sheets were inspected, covering 49 samples across the entire file. Meaningful actions were then checked at targeted source timestamps, including Trainer plays, evolution, attachments, attack and recoil states, point awards and ending. `keyframes` retains the targeted full-resolution frames. Overview labels use the extraction helper's fps midpoint convention; event times are approximate windows, and full-resolution keyframe filenames specify the actual requested source time. Sparse sampling is supplemented at the meaningful action windows; this is not an exact hidden-information replay.

## Visible card versions and starting state

Owner: Active Growlithe, 70 HP, Dig Claws 20, one Fire cost. Starting Bench Magmar, 80 HP, Tail Whap 30, two Colorless cost. Arcanine ex in hand is the 150 HP version with Inferno Onrush 120, two Fire plus one Colorless cost, and printed 20 self-damage. Charcadet later benched is 60 HP, Punch 10. Visible but unplayed hand cards include Rotom Dex, a second Magmar, Charmeleon with Ignition and Slash 40, a second Arcanine ex with the same Inferno Onrush mechanics and different art, and later Charmander, 60 HP, Combustion 20. No full owner deck list is established.

Opponent: Active Galarian Meowth, 60 HP, Slash 20. Its turn-1 Bench develops into Beldum, 60 HP, Conductive Body/Ram 10; Rookidee, 60 HP, Pluck 10; and Meltan, 70 HP, Beam 20. Beldum evolves into Metang, 100 HP, Bullet Punch 30+, later. A second Meltan and a second Beldum are publicly played. The challenge title is not proof that an Aegislash card was drawn or played. No card set numbers or hidden full list are inferred.

## Full timeline

| Source time | Phase | Observed meaningful actions and reconciled state |
|---|---|---|
| 0-9 s | Loading and matchup | Loading, then AI Opponent versus Dacz8976. The turn-order animation says Going second. The coin visual establishes turn order; no attack coin result occurs later. |
| 9-19 s | Setup | Checked Auto is visible. Owner places Growlithe Active and Magmar on left Bench. Opponent reveals Galarian Meowth Active. Both scores 0; owner hand visibly includes Rotom Dex, Arcanine ex and Poke Ball. |
| 19-25 s | Turn 1, opponent | Opponent benches Meltan, Rookidee and Beldum, filling its Bench. No Energy attachment, attack, Trainer or ability activation is visible in this turn. Growlithe stays 70 HP and Galarian Meowth 60. Evidence: `sheet_01.jpg`, `keyframes/t0025.50.jpg`. |
| 25-40 s | Turn 2, owner | Owner draws Charmeleon, attaches Fire to Growlithe, then plays Poke Ball. The search reveals a second Magmar into hand; it is not benched. Growlithe uses Dig Claws. The visible Weakness 40 result reduces Galarian Meowth 60 to 20 HP. Growlithe remains 70; score 0-0. Evidence: `target_01.jpg`, `target_02.jpg`, `keyframes/t0038.00.jpg`, overview 40.5 s. |
| 40-51 s | Turn 3, opponent | Opponent draws, attaches Metal to Galarian Meowth, and uses Slash for 20. Growlithe falls 70 to 50 HP. No evolution or other card play appears. Score remains 0-0. Evidence: `sheet_02.jpg`, `keyframes/t0044.00.jpg`, `keyframes/t0045.00.jpg`. |
| 51-73 s | Turn 4, owner | Owner draws and immediately plays another Poke Ball, revealing Charcadet 60 HP into hand. Charcadet is benched on the right. A second Fire is attached to Growlithe. Dig Claws again displays Weakness 40 and knocks out the 20-HP Galarian Meowth. The owner earns point 1; Growlithe stays 50 HP. Opponent promotes Meltan 70 HP from right Bench. Evidence: `target_02.jpg`, `target_03.jpg`, `keyframes/t0065.00.jpg`, `keyframes/t0071.00.jpg`. |
| 73-90 s | Turn 5, opponent | Opponent draws, plays Professor's Research (Professor Oak, Draw 2 cards), benches another Meltan in the vacated right Bench slot, and evolves left Beldum to Metang 100 HP. Metal is attached to Active Meltan. Meltan uses Beam 20, reducing Growlithe 50 to 30 HP. The precise ordering of its Metal attachment relative to the middle card plays is not asserted; the post-play attachment and attack are visible. Score 1-0. Evidence: `keyframes/t0077.30.jpg`, `keyframes/t0080.00.jpg`, `keyframes/t0081.00.jpg`, `target_04.jpg`, `sheet_04.jpg`. |
| 90-115 s | Turn 6, owner | Owner draws Professor's Research. Growlithe evolves into the held Arcanine ex; its 40 accumulated damage carries through visibly, leaving 110 of 150 HP. Owner plays Professor's Research, drawing another Arcanine ex and another Professor's Research. Third Fire is attached to Active Arcanine ex. Inferno Onrush displays Weakness 140 against the 70-HP Meltan and 20 self-damage. Meltan is knocked out; owner earns point 2. Stable Arcanine ex HP is then 90. Opponent promotes its second Meltan, 70 HP. Evidence: `keyframes/t0092.00.jpg`, `keyframes/t0095.00.jpg`, `keyframes/t0102.00.jpg`, `keyframes/t0104.00.jpg`, `keyframes/t0106.50.jpg`, `keyframes/t0110.00.jpg`, `keyframes/t0118.00.jpg`. |
| 115-124 s | Turn 7, opponent | Opponent draws, benches a second Beldum in the newly empty right slot, and attaches Metal to second Active Meltan. Meltan uses Beam 20, reducing Arcanine ex 90 to 70 HP. Metang 100, Rookidee 60 and Beldum 60 remain undamaged on Bench. Score 2-0. Evidence: `target_05.jpg`, `target_06.jpg`, `keyframes/t0121.00.jpg`, `keyframes/t0124.50.jpg`. |
| 124-138 s | Turn 8, owner | Owner draws Charmander, 60 HP, Combustion 20. It stays in hand; the center Bench remains empty. No additional Trainer, ability, switch or Energy attachment is visible. Arcanine ex retains three Fire, and generated Fire remains in the Energy Zone. Inferno Onrush again knocks out a 70-HP Meltan with the same 140-damage sequence and 20 self-damage; Arcanine ex ends at 50 HP. Point 3 is awarded. Evidence: `keyframes/t0126.00.jpg`, `keyframes/t0129.00.jpg`, `keyframes/t0132.50.jpg`, `keyframes/t0134.00.jpg`, `keyframes/t0136.00.jpg`. |
| 138-147.196667 s | Victory and results | Transition to Victory. Arcanine ex is displayed as Card of the Game. Results identify the Aegislash Deck challenge, went second, eight turns, owner three points, opponent zero, damage done 360. The source ends on this results screen; no subsequent match begins. Evidence: `keyframes/t0142.00.jpg`, `keyframes/t0147.00.jpg`. |

## Reconciliation and bounded interpretation

Four owner attacks reconcile to the visible result total: two Dig Claws at 40 each and two Inferno Onrush at 140 each, total 360. The owner point sequence is 0, 1 for Galarian Meowth, 2 for first Meltan, 3 for second Meltan. Opponent never earns a point. Owner Active HP is Growlithe 70, 50, 30, then Arcanine ex 110 after evolution, 90 after first recoil, 70 after second Meltan's Beam, and 50 after final recoil. Bench Magmar and Charcadet remain at 80 and 60 HP, with no visible attached Energy.

Observed resource path is three Fire attachments to the continuing owner Active, one each on turns 2, 4 and 6, and one Metal to each opponent attacker on turns 3, 5 and 7. No retreat or switch Trainer, healing, Tool, Stadium, status condition, attack coin flip or ability activation appears. Printed Beldum and Charmeleon abilities are not evidence of activation. Promotion after each knockout is recorded separately from a voluntary switch.

Interpretation: Arcanine ex's evolution and third attachment convert the owner's established Active into consecutive knockouts. On the last turn, its visible attack is already sufficient to win while surviving its printed recoil. This supports the particular terminal choice. It does not establish overall optimal Auto behavior, general simulator correctness, or what the opponent could have done with its hidden hand. Unused Trainers and Bench spaces are observations, not automatically policy defects.

Unknown hidden cards, unreadable collector identifiers, and small animation timing details are preserved in `UNCERTAINTIES.json`. No consequential ambiguity remains that requires Astra clarification. Lead independent source checks and acceptance are still required before any completion registration or source move.


## Lead completion

Accepted as a completed full-battle review after the source checks documented in `LEAD_ACCEPTANCE.json`. The unchanged original is archived in `Reviewed`; matching before/after SHA-256 is recorded in `MOVE_RECEIPT.20260930_145405000_iOS.MP4.json`. No Ladder Log entry was created.
