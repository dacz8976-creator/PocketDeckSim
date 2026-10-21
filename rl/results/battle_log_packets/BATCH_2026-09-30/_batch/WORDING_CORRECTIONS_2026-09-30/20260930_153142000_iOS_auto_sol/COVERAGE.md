# Coverage record

Reviewer: `sol_auto_153142000`, fresh Sol full visual pass. Source duration: 166.923855 seconds. Full available battle reviewed, opening through Victory, with all 10 turns reconciled. Lead acceptance is pending.

## Inspection method

Inspected all 56 full-duration overview samples through seven contact sheets in `overview/`. Labels use the extraction helper's FPS midpoint convention, at 1.5, 4.5, 7.5 seconds and onward through 166.5. Targeted full-resolution evidence was extracted and inspected for card identities, Energy allocations, damage, coins, the final retreat and ending. The rapid AI Trainer window from 126 to 135 seconds was inspected at half-second intervals through both `turn9_detail/sheet_*.jpg` sheets. Routine animations were allowed to remain sparse when the meaningful before and after states reconciled.

## Phase checklist

| Interval, seconds | Covered phase | Verified state or action |
| --- | --- | --- |
| 0 to 21 | Loading, AI introduction, turn-order/setup | AI label, Auto, owner second, Hitmonchan ex and Cubone, Eevee |
| 21 to 30 | AI turn 1 | Bench filled with two Ducklett and Rookidee; no attack |
| 30 to 44 | Owner turn 2 | Fighting on Hitmonchan, Quick Straight 50, Eevee KO, point 1, Ducklett promotion |
| 44 to 54 | AI turn 3 | Buneary benched, Rookidee evolves to Corvisquire, first Metal on Ducklett, no attack |
| 54 to 67 | Owner turn 4 | Drilbur draw, Beat Cubone benched and energized, Ducklett 60 to 10 |
| 67 to 77 | AI turn 5 | Second Metal on Ducklett, Wing Attack 30, Hitmonchan 130 to 100 |
| 77 to 92 | Owner turn 6 | Excadrill draw, Drilbur benched and energized, Ducklett KO, point 2, Buneary promotion |
| 92 to 108 | AI turn 7 | Rattata benched, Buneary energized, HH Double Kick 40, Hitmonchan 100 to 60 |
| 108 to 125 | Owner turn 8 | Marowak ex and Excadrill evolution, second Fighting to Marowak, Quick Straight 50, Buneary 60 to 10 |
| 125 to 142 | AI turn 9 | Professor's Research then Poke Ball, Metal to Rattata, TH Double Kick 20, Hitmonchan 60 to 40 |
| 142 to 158 | Owner turn 10 and terminal KO | Second Excadrill draw, retreat into Excadrill, Fighting to left Cubone, Mud Shot 70, Buneary KO, third point |
| 158 to 166.923855 | Result | Victory, owner 3 AI 0, 10 turns, 270 damage, AI deck name |

## Reconciliation checks

- [x] Opening and ending belong to one continuous match.
- [x] Every owner and AI turn has a meaningful action account.
- [x] Active and Bench development reconciles, including both Cubone versions and both Ducklett.
- [x] Attached Energy recipient and count reconcile each turn and at the terminal board.
- [x] Attack damage and HP reconcile; 270 total damage matches the results screen.
- [x] Buneary coins checked at completed result tallies: HH at 101.5 to 102, TH at 138 seconds.
- [x] Point progression 0 to 1 to 2 to 3 reconciles with three single-point knockouts and zero AI points.
- [x] Trainer sequence checked densely; hidden search result retained as unknown.
- [x] Ability display, lack of Tool/Stadium/conditions/healing, forced promotions and final retreat accounted for.
- [x] Visible AI and Auto checked; ladder exclusion retained.
- [x] No unreviewed meaningful phase remains; routine transition animation does not obscure the established result.

## Independent lead check targets

Packet base: `C:\Users\dacz8\OneDrive\Desktop\Battle Logs\Recording_QA\20260930_153142000_iOS_auto_sol`.

- Opening mode: `keyframes/t0004.50.jpg` for AI, `keyframes/t0018.00.jpg` for Auto and setup.
- Ordinary turn pair: `keyframes/t0066.00.jpg` before AI turn 5 attack, `keyframes/t0071.00.jpg` with two Metal and 30 damage; overview sheet 03 has the resulting 100 HP.
- Ordinary development: `keyframes/t0095.00.jpg` shows both Cubone versions, Drilbur with Fighting, Hitmonchan 100 HP, owner point 2.
- Trainer and coin window: `turn9_detail/sheet_01.jpg`, `turn9_detail/sheet_02.jpg`, `keyframes/t0138.00.jpg`.
- Decisive sequence: `keyframes/t0146.00.jpg` before retreat, `keyframes/t0149.00.jpg` after retreat, `keyframes/t0150.00.jpg` Energy attachment, `keyframes/t0153.00.jpg` 70 Weakness damage, `keyframes/t0155.00.jpg` terminal board.
- Victory: `keyframes/t0166.50.jpg`.

No selective Astra question is needed from this pass. Independent verification remains the lead's responsibility.
