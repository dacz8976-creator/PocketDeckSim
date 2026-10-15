# Wailord competitive reviews, October 1, 2026

All five recordings are fully reviewed, independently accepted, registered and archived unchanged. Saved once each in [Pause Games](https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd) and verified after reload: **2 wins, 3 losses, 2 wins by concession**. Logged under the owner's Wailord / Indeedee wall with Water Energy. Each full review distinguishes visible cards from the configured hidden list. Competitive intent is owner testimony; the exact selected queue and hidden full lists remain unknown. These results are excluded from the ranked Ladder Log. Numeric ratings remain blank.

| Source | Result | Turn order | First attack, global turn | Opponent visible core | Full review |
|---|---|---|---|---|---|
| 20261002_020315000_iOS.MP4 | Loss, 1-3 displayed points | second | 6 | るか: Palkia ex / Baxcalibur / Milotic ex | [Review](Recording_QA/20261002_020315000_iOS_competitive_sol/REVIEW.md) |
| 20261002_020920000_iOS.MP4 | Win by concession, 0-0 actual points at concession | second | 8 | おさるの上司: Charmander / Charmeleon / Entei ex | [Review](Recording_QA/20261002_020920000_iOS_competitive_sol/REVIEW.md) |
| 20261002_021402000_iOS.MP4 | Loss, 0-3 displayed points | first | 13 | ポジビン: Meloetta / Giratina ex / Mega Gardevoir ex / Mega Diancie ex | [Review](Recording_QA/20261002_021402000_iOS_competitive_sol/REVIEW.md) |
| 20261002_022135000_iOS.MP4 | Loss, 1-3 displayed points | first | 7 | だんくしゅー: Swablu / Mega Altaria ex / Greninja / Chingling | [Review](Recording_QA/20261002_022135000_iOS_competitive_sol/REVIEW.md) |
| 20261002_023418000_iOS.MP4 | Win by concession, 0-1 actual points at concession | first | 9 | KO歐~YOU: Bonsly / Lucario / Mega Lucario ex / Hitmonchan | [Review](Recording_QA/20261002_023418000_iOS_competitive_sol/REVIEW.md) |

## What made it feel slow

Dustin reported: "How it felt was slow. Takes too long to build up energy." The reports distinguish the four-Energy requirement from rebuilding after a knockout, early evolution, forced switching and attachment choices. No acceleration was tested. Normal Wailord can use any Energy for its four-Colorless cost, but its bonus counts Water. Changing types alone does not reduce the number of attachments. Wailmer and Wailord ex require Water; Indeedee can heal without Energy but needs two Psychic to attack.

[Astra's Energy check](Recording_QA/BATCH_2026-10-02_COMPETITIVE/ASTRA_ENERGY_CHECK.md) confirms Misty is compatible with this core, with coin-dependent acceleration. Testing it first is a practical recommendation, not a measured improvement. Mega Sharpedo ex is another Water route: it attacks for one Water and adds Water to a Benched Water Pokémon, then can retreat free. It adds an evolution line and its knockout gives three points, so it needs a separate build and test. An alternate Energy route needs an actual acceleration engine to improve setup speed and can reduce normal Wailord's Water damage bonus. None of these is a validated fix or an implemented deck change.

## Bounded tactical findings

[Astra's retained-source checks](Recording_QA/BATCH_2026-10-02_COMPETITIVE/ASTRA_TACTICAL_CHECKS.md) accepted three narrow conclusions:

- In 020920, keeping Wailmer unevolved through turn 6 could enable Wave Splash for 80 into Charmeleon at 80 HP under the same visible continuation. The larger evolution HP buffer is traded for earlier damage, and later evolution must wait for another turn.
- In 021402, Indeedee can survive the observed 110 at 20 HP and retreat free under Peculiar Plaza before replacing that Stadium, permitting a turn 9 Wailord attack for 100. It would leave a vulnerable two-point Indeedee on the Bench. This is not a proven reversal of the loss.
- In 023418, Cyrus switches the opponent only. Bonsly's minus 30 remains on Wailord, so five-Water Whale Pump would deal 80 into Mega Lucario at 110 HP, leaving 30. The actual win is concession before attack; the opponent's reason is unknown.

In 022135, both Wailmer are lost; the remaining Indeedee heal but cannot attack with Water-only Energy. The terminal Indeedee ex knockout awards two points, while the final result panel has a maximum of three opponent point markers. Preserve that displayed 1-3 result without treating the ex knockout as a one-point event.

The earlier Garchomp/Froakie files 011527 and 012229 are outside this Wailord batch. Their source files remain in the main folder; 012229's initial assignment was explicitly corrected to intake-only in append-only history. Older pending excerpts remain pending.


## Preservation and verification

All five before/after move hashes match. The 116 baseline index rows were preserved exactly. Current inventory: 122 indexed, 106 full-battle reviews, 8 completed rule tests, 8 indexed pending items.

5 of 5 originals are confirmed online-only; local allocation is 0.00 GB. No original was deleted. Review packets and evidence remain pinned locally. [Verification records](Recording_QA/BATCH_2026-10-02_COMPETITIVE/FINAL_CHECKS.json) and [saved-log proof](Recording_QA/BATCH_2026-10-02_COMPETITIVE/PAUSE_GAMES_5_VERIFIED.png) are retained.
