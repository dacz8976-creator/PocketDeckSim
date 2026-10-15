# Full visual battle review

**Current status: completed full-battle review accepted by the lead; original archived unchanged in `Reviewed`. Excluded from Ladder Log.**

Reviewer: `sol_auto_153142000` | Model: `gpt-6.1-sol`, high reasoning | Review date: September 30, 2026.

Scope: one complete battle, setup through the terminal result, all 10 turns. The visual account is complete and awaits the lead's independent completion check. No global record, Ladder Log entry, source move or source edit was made by this reviewer.

Source: `20260930_153142000_iOS.MP4`, 166.923855 seconds, 305240430 bytes, SHA-256 `7b2083a31e6949035824d9c9a71605a9b48fb4f5c5d7695aa8eed4b30f42d601`. Identity was supplied and verified by the lead; see `SOURCE.json`.

## Mode and result

The opening explicitly labels the opponent `AI` at 4.50 seconds. The checked Auto indicator is visible during setup and throughout the battle; no mode change is observed. This independently supports the owner's description of autopilot against the computer. This battle is excluded from ladder results by the owner's instruction.

Dacz8976 goes second and wins 3 to 0 on turn 10. At 166.50 seconds the result reads `vs. Raticate Deck (Deluxe Pack: Mega)`, `Victory!`, `Turns played 10`, three owner points, zero opponent points, and `Damage done 270`. Hitmonchan ex is the displayed Card of the Game.

## Visible cards and starting state

Owner starts Active Hitmonchan ex, 130 HP, Quick Straight 50 for one Fighting Energy. Its visible attack text says damage is not affected by Weakness. The opening Bench contains Cubone, 60 HP, Bone Beatdown 20. Initial remaining visible hand: Pokemon Flute and two Toxicroak, 90 HP, Poison Jab 40. Subsequent draws reveal a second Cubone, 60 HP, Beat 30; Drilbur, 70 HP, Mud-Slap 20; Excadrill, 110 HP, Mud Shot 50; Marowak ex, 140 HP, Bonemerang 80 times coin heads; and a second Excadrill. These are revealed cards, not a complete deck list.

AI starts Active Eevee, 50 HP, Boosted Evolution ability, Stampede 10. Its first turn fills the Bench with two Ducklett, 60 HP, Wing Attack 30, and Rookidee, 60 HP, Pluck 10. Later revealed cards are Corvisquire, 80 HP, Joust 30 for two Colorless; its printed effect discards all Pokemon Tools from the opponent's Active before doing damage; Buneary, 60 HP, Double Kick 20 per heads; Rattata, 50 HP, Surprise Attack 40; Professor's Research (Professor Oak); and Poke Ball. The results deck name does not establish which unrevealed cards were present or drawn.

The owner's generated Energy is Fighting; the AI's is Metal. The owner starts with no attached Energy, as does the AI. No Stadium, Tool or Special Condition is visible at setup or later.

## Complete turn account

Times are source seconds. Turn boundaries are approximate transition windows. Evidence paths are relative to this packet. All seven `overview/sheet_*.jpg` sheets were inspected, with full-resolution checks and the denser turn 9 sequence below.

| Phase / time | Meaningful visible actions and reconciled state | Evidence |
| --- | --- | --- |
| Opening and setup, 0 to 21 | Loading, AI introduction, turn-order animation, owner told they are going second. Auto places Hitmonchan ex Active and Bone Beatdown Cubone on the left Bench. AI reveals Eevee Active. Eevee's Boosted Evolution text is highlighted; no evolution follows. Points 0 to 0. | `keyframes/t0004.50.jpg`, `keyframes/t0018.00.jpg`, overview sheet 01 |
| Turn 1, AI, about 21 to 30 | AI benches both Ducklett and Rookidee, filling all three Bench positions. No attached Energy or attack is observed. Eevee stays 50 HP and Hitmonchan ex stays 130 HP. | overview sheets 01 and 02; `keyframes/t0032.00.jpg` shows completed AI board |
| Turn 2, owner, about 30 to 44 | Draws Beat Cubone. Attaches one Fighting to Active Hitmonchan ex and uses Quick Straight. Eevee takes 50 and is knocked out. Owner gains point 1, AI remains 0. AI promotes one Ducklett at full 60 HP. Beat Cubone remains in hand during this turn. | overview sheet 02, especially 34.5, 37.5, 40.5 and 43.5 second panels |
| Turn 3, AI, about 44 to 54 | AI benches Buneary in the vacancy, attaches one Metal to Active Ducklett, and evolves Rookidee to Corvisquire, 80 HP. Ducklett's visible Wing Attack requires two Energy; with only one attached it makes no attack. Hitmonchan remains 130 HP, Ducklett remains 60 HP. | `keyframes/t0053.00.jpg`, overview sheet 02 |
| Turn 4, owner, about 54 to 67 | Draws Drilbur. Benches Beat Cubone on the right, attaches one Fighting to it, then keeps Hitmonchan ex Active and uses Quick Straight for 50. Ducklett goes from 60 to 10 HP. Points remain 1 to 0. The left Cubone has no Energy, right Cubone has one, Hitmonchan has one. | `keyframes/t0059.00.jpg`, `keyframes/t0066.00.jpg`, overview sheet 03 |
| Turn 5, AI, about 67 to 77 | Adds a second Metal to Active Ducklett. Wing Attack deals 30 to Hitmonchan ex, reducing it from 130 to 100 HP. Ducklett remains at 10 HP with two Metal. No new Bench changes or Trainer play is observed. | `keyframes/t0071.00.jpg`, overview sheet 03 |
| Turn 6, owner, about 77 to 92 | Draws Excadrill. Benches Drilbur in the middle vacancy and attaches one Fighting to it. Hitmonchan ex uses Quick Straight for 50 and knocks out the 10 HP Ducklett. Owner gains point 2. AI promotes Buneary, 60 HP. Owner has Hitmonchan 100 HP with one Fighting, Cubone left 60 HP without Energy, Drilbur 70 HP with one Fighting, and Cubone right 60 HP with one Fighting. | `keyframes/t0080.00.jpg`, `keyframes/t0095.00.jpg`, overview sheets 03 and 04 |
| Turn 7, AI, about 92 to 108 | AI benches Rattata in its right vacancy and attaches one Metal to Active Buneary. Buneary uses Double Kick. The two coins finish two heads and zero tails, dealing 40. Hitmonchan goes from 100 to 60 HP. AI Bench is Ducklett 60, Corvisquire 80, Rattata 50. Points remain 2 to 0. | `keyframes/t0101.50.jpg`, `keyframes/t0102.00.jpg`, overview sheet 04 |
| Turn 8, owner, about 108 to 125 | Draws Marowak ex. Evolves right Beat Cubone to Marowak ex, 140 HP, then middle Drilbur to Excadrill, 110 HP, retaining its one Fighting. Adds a second Fighting to Marowak ex. Hitmonchan ex stays Active with 60 HP and one Fighting; Quick Straight deals 50, reducing Buneary from 60 to 10 HP. No separate damaging ability occurs: the intermediate HP animation resolves to this single 50-damage attack. | `keyframes/t0116.00.jpg`, `keyframes/t0119.00.jpg`, `keyframes/t0122.00.jpg`, overview sheet 05 |
| Turn 9, AI, about 125 to 142 | AI plays Professor's Research, visibly `Draw 2 cards`, then Poke Ball, visibly putting a random Basic from its deck into its hand. The fetched Basic stays face down and unidentified. AI attaches one Metal to benched Rattata; Buneary retains its existing one Metal. Buneary uses Double Kick again. The first coin is tails, second heads; final tally one head and one tail. Damage is 20, reducing Hitmonchan from 60 to 40 HP. Points remain 2 to 0. No evolution, retreat, healing or Bench replacement occurs. | `turn9_detail/sheet_01.jpg`, `turn9_detail/sheet_02.jpg`, `keyframes/t0129.50.jpg`, `keyframes/t0138.00.jpg`, `keyframes/t0146.00.jpg` |
| Turn 10, owner, about 142 to 158 | Draws second Excadrill. Retreats Hitmonchan ex, moving it to the middle Bench and promoting the 110 HP Excadrill. Hitmonchan's sole Fighting is no longer attached after this move, consistent with the visible one-Energy retreat cost. Adds the turn's Fighting to left Bone Beatdown Cubone. Excadrill retains one Fighting and uses Mud Shot. The displayed Weakness damage is 70; Buneary at 10 HP is knocked out. Owner gains the third point, finishing 3 to 0. No additional AI promotion is needed. | `keyframes/t0146.00.jpg`, `keyframes/t0149.00.jpg`, `keyframes/t0150.00.jpg`, `keyframes/t0153.00.jpg`, `keyframes/t0155.00.jpg`, overview sheet 06 |
| Result, about 158 to 166.923855 | Third-point animation, white transition, then completed Victory screen. The recording ends after the result is established, without opening Battle Log. | `keyframes/t0166.50.jpg`, overview sheets 06 and 07 |

## State reconciliation and decision notes

Owner damage dealt reconciles exactly with the result's 270: four Quick Straight attacks at 50 each, plus one Mud Shot displayed as 70. The owner receives three ordinary single-point knockouts: Eevee, Ducklett and Buneary. AI scores none. Hitmonchan ex's HP progression is 130, then 100 after Ducklett's 30, 60 after Buneary's two heads, and 40 after Buneary's one head. It survives and finishes benched.

Owner Energy allocation across its five turns is Hitmonchan ex, right Cubone, Drilbur, Marowak ex's second Energy, then left Cubone. Final attachments are one Fighting on Active Excadrill, one on left Cubone, none on benched Hitmonchan ex, and two on Marowak ex. AI attachments are Ducklett's first and second Metal on turns 3 and 5, Buneary's Metal on turn 7, and Rattata's Metal on turn 9. Knocked-out Ducklett and Buneary leave play with their Energy.

Observed ability display is Eevee's passive Boosted Evolution reminder at setup; no Eevee evolution occurs. No owner Trainer is played: Pokemon Flute stays in hand. No Tools, Stadiums, healing or Special Conditions are observed. No attack by Corvisquire, Rattata, either Cubone, Drilbur, Marowak ex or Toxicroak occurs. The only switches are the AI's forced promotions following knockouts and the owner's final retreat.

Interpretation: the final retreat is a successful but unnecessary step for this immediate win. The visible alternative is to leave the one-Energy Hitmonchan ex Active and use its 50-damage Quick Straight against 10 HP Buneary. Both attacks visibly exceed remaining HP. This is a bounded tactical observation, not evidence of a rules bug or a general assessment of bot strength. Marowak ex is developed as an unused backup; no claim is made about hidden cards or later hypothetical turns.

The observed difference between Quick Straight's 50 and Mud Shot's 70 is supported by the visible attack text and final Weakness display. It is an observation in this match, not an independently tested general rule or simulator verification.

## Uncertainty and limitations

No consequential unresolved state transition remains. Exact card collection numbers, unseen deck contents, AI draws, and the Basic fetched by Poke Ball are unknown. The initial turn-order coin's final face is not separately established; second-player status is directly shown and confirmed on the results screen. Audio was not used. Frame inspection covers meaningful states and transitions, not a frame-by-frame replay of routine animations. See `UNCERTAINTIES.json` and `COVERAGE.md`.


## Lead completion

Accepted as a completed full-battle review after the source checks documented in `LEAD_ACCEPTANCE.json`. The unchanged original is archived in `Reviewed`; matching before/after SHA-256 is recorded in `MOVE_RECEIPT.20260930_153142000_iOS.MP4.json`. No Ladder Log entry was created.


## Post-acceptance wording and status check

The accepted review has received a targeted wording/status follow-up. See [the correction record](POST_ACCEPTANCE_CORRECTIONS.md) for exact changes, preserved history and result-display limits. Outcome, score, source identity and Ladder exclusion are unchanged.
