# Coverage and verification anchors

Source: `20260930_155635000_iOS.MP4`, SHA-256 `a2bccb37d07e74872afe49c51c5ee5a6ad9199703d25a6cde6f97701ef25ff9a`, duration 204.473333 s. Reviewer `sol_auto_155635000`, gpt-6.1-sol high, September 30, 2026.

Primary visual review is complete across the available file, including every meaningful turn from setup through the terminal result. This is not lead acceptance: the coordinator retains responsibility for independent verification, final registration and archival.

## End-to-end intervals

| Interval | Reviewed content | Retained overview |
|---|---|---|
| 0-27 s | Loading, AI/owner identity, second-player order, Auto, initial setup and AI turn 1 Juliana | `overview/sheet_01.jpg` |
| 27-54 s | Owner turn 2 search, draw, both Froakie bench plays, attachment and weakness-adjusted Tackle | `overview/sheet_02.jpg` |
| 54-81 s | AI turn 3 Quilava/Meowth development, retreat; owner turn 4 Misty, Rare Candy and Mega evolution | `overview/sheet_03.jpg` |
| 81-108 s | Owner turn 4 normal attachment, defensive tails, 150 attack, two-Energy discard, Meowth KO, +1; AI turn 5 draw/attachment/Research | `overview/sheet_04.jpg` |
| 108-135 s | End turn 5, owner turn 6 Frogadier and second Water, AI turn 7 Typhlosion evolution, Flame Patch, third Fire, attack | `overview/sheet_05.jpg` |
| 135-162 s | Completed first Typhlosion coin chain/Energy loss/120 HP; owner turn 8 Research draws and failed Poke Ball, attachment; AI turn 9 attack start | `overview/sheet_06.jpg` |
| 162-189 s | Turn 9 zero-heads tails and 10 HP; turn 10 Mega Slowbro draw and second Water; turn 11 attack, 1-head coin and Mega KO | `overview/sheet_07.jpg` |
| 189-204.473333 s | Opponent three-point award, defeat, complete results, Card of the Game views and file ending | `overview/sheet_08.jpg`, `targets/t0204.40.jpg` |

All eight sheets and their 68 displayed frames were inspected. Labels use the extraction helper's fps midpoint convention and are approximate. Direct full-resolution targets refine the relevant action and state transitions. Continuous playback was not claimed; all battle phases are covered through overview plus selective dense source seeks. The final direct seek is at 204.40 s, 0.073333 s before registered duration, inside the already established post-match view. No continuation is needed.

## Turn checklist

- Setup, opening AI identity and Auto: checked.
- Opponent turn 1: draw, Juliana, pass: checked.
- Owner turn 2: Poke Ball, Froakie plays, Research, Water, Tackle, stable Cyndaquil 20: checked.
- Opponent turn 3: Quilava, Fire, Meowth bench and retreat, no attack: checked.
- Owner turn 4: Misty 1 heads/1 tails, two Water then normal third Water, Rare Candy/Mega evolution, Carefree Steps tails, 150 attack, two-Energy removal, KO and +1: checked.
- Opponent turn 5: Fire, Research, no attack: checked.
- Owner turn 6: Frogadier draw/evolution and second Water, no attack: checked.
- Opponent turn 7: Typhlosion evolution, Flame Patch and normal Fire, 110 attack, 3 heads/1 tails, only two available Water removed, stable 120 HP: checked.
- Owner turn 8: Research draw/play, Poke Ball and Rare Candy drawn, one failed Poke Ball play, one Water, no attack: checked.
- Opponent turn 9: Torchic Fire, 110 attack, 0 heads/1 tails, Water retained, stable 10 HP: checked.
- Owner turn 10: Mega Slowbro draw remains hand, second Water, no attack or switch: checked.
- Opponent turn 11: 110 attack, 1 heads/1 tails, one Water removal, Mega HP 0 and one three-point award: checked.
- Defeat and results: checked. 1-3, 11 turns, damage 190, no second battle.

## Bounded independent-check anchors

| Check | Evidence |
|---|---|
| Opening AI opponent, owner and Auto | `overview/sheet_01.jpg` at 4.5, 7.5, 10.5 and 16.5 s; `targets/t0026.00.jpg` for settled opening board/Auto |
| Ordinary turn, public draw versus play | `targets/t0111.00.jpg`, `t0114.00.jpg`, `t0116.50.jpg` show Frogadier reveal, evolution and turn 7 handoff with Mega's two Water |
| First owner KO and Energy effect | `targets/t0071.50.jpg`, `t0074.50.jpg`, `t0079.00.jpg`, `t0081.50.jpg`, `t0087.00.jpg`, `t0089.00.jpg`, `t0093.00.jpg`, `t0095.50.jpg`, `t0099.00.jpg` |
| Important draw/play trap on turn 8 | `targets/t0146.50.jpg` Research animation; `t0149.50.jpg` golden Rare Candy reveal with Poke Ball still in hand; `t0153.00.jpg` and `t0155.00.jpg` failed Poke Ball and Rare Candy remaining hand |
| Typhlosion setup and first coin chain | `targets/t0125.00.jpg` Flame Patch; `t0128.00.jpg` attachment; `t0138.30.jpg` completed 3 heads/1 tails; `t0139.50.jpg` 120 HP/no Water |
| Final resource constraint | `targets/t0170.00.jpg` Mega Slowbro reveal; `t0173.50.jpg` two Water on 10-HP Active; `t0176.00.jpg` unchanged after turn passes |
| Decisive attack and result | `overview/sheet_07.jpg` 178.5-187.5 s; `targets/t0186.00.jpg` HP 0/one Water removal; `t0189.70.jpg` third point filling; `t0193.00.jpg` Defeat; `t0201.00.jpg` exact result summary |
| Actual file end | `targets/t0204.40.jpg` opponent Typhlosion ex Card of the Game |

No source move, shared index change, shared log write or Ladder Log change was made by this reviewer.
