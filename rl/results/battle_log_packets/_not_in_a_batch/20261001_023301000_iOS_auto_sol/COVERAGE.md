# Coverage and retained evidence

**Current status: completed full-battle review accepted by the lead; original archived unchanged in `Reviewed`. Excluded from Ladder Log.**

Status: complete visual coverage accepted by the lead; registration and archival are verified. One battle, no split continuation or additional match detected. Source identity is in preserved SOURCE.json. Original unchanged.

The worker inspected all eight overview contact sheets covering 65 samples at 3-second spacing, labeled 1.5 through 193.5 seconds, then inspected targeted source frames and grouped evidence for material actions, coins, switching and Energy accounting. The overview labels are fps midpoint samples. Exact-time target filenames use input seek times and are reference frames, not asserted event onset times.

| Interval | Coverage | Principal evidence |
|---|---|---|
| 0-18 s | Loading, AI intro, going second, Auto, both Active setup | overview/sheet_01.jpg; target/t0011.00.jpg |
| 18-25 s | Opponent turn 1, Poké Ball and Gastly bench | overview/sheet_01.jpg; target/t0021.00.jpg; t0022.00.jpg; t0024.00.jpg |
| 25-32 s | Owner turn 2, draw and attachment | overview/sheet_02.jpg; target/t0032.00.jpg |
| 32-41.5 s | Opponent turn 3, evolution, attachment, attack | overview/sheet_02.jpg; target/t0035.00.jpg; t0036.00.jpg; t0037.00.jpg; t0041.50.jpg |
| 41.5-57 s | Owner turn 4, Donphan draw, second attachment, Ice Pop heal and Heads | overview/sheet_02.jpg and sheet_03.jpg; target/opening_and_turn4.jpg; t0054.50.jpg; t0057.00.jpg |
| 57-64.5 s | Opponent turn 5, Haunter attachment and Bombirdier attack | overview/sheet_03.jpg; target/midgame.jpg; t0062.00.jpg |
| 64.5-94.5 s | Owner turn 6, Meditite draw, attachment, heal/Heads, Land Laser 1H1T, KO and first point | overview/sheet_03.jpg and sheet_04.jpg; target/t0066.00.jpg; t0069.00.jpg; t0077.00.jpg; t0082.50.jpg |
| 94.5-106.5 s | Opponent turn 7, second Haunter attachment, Skrelp bench, Spin Turn 40 and switch | overview/sheet_04.jpg; target/midgame.jpg; t0104.00.jpg; t0105.00.jpg |
| 106.5-144 s | Owner turn 8, Koraidon draw/bench, Auto pause, Legendary Drive switch and three-Energy transfer, Stadium, later Zygarde attachment, World Wrecker 220, first discard, second point, Haunter promotion | overview/sheet_05.jpg and sheet_06.jpg; target/t0114.50.jpg; t0122.00.jpg; t0128.00.jpg; t0129.00.jpg; t0131.00.jpg; t0134.00.jpg; t0136.00.jpg; t0146.00.jpg; bench_energy_check.jpg |
| 144-156 s | Opponent turn 9, Poké Ball/shuffle, third Haunter attachment, Spin Turn 40, no Bench switch | overview/sheet_06.jpg; target/closing_transactions.jpg; t0147.00.jpg; t0149.00.jpg; t0155.50.jpg; t0156.00.jpg |
| 156-189 s | Owner turn 10, Master Plan draw, two Ice Pops with Heads, second benched Zygarde attachment, World Wrecker 220 and final one-point KO | overview/sheet_06.jpg and sheet_07.jpg; target/t0167.50.jpg; t0175.50.jpg; t0177.00.jpg; t0180.00.jpg |
| 189-195.268333 s | Victory and full results stats | overview/sheet_08.jpg; target/t0194.80.jpg |

All meaningful visible actions are recorded in REVIEW.md. Routine loading, transitions and attack animations are covered by the overview plus adjacent settled state. No battle interval remains assigned but unreviewed. This does not mean every individual video frame was inspected.

Retained files: overview/sample_frames holds the 65 source samples; overview/sheet_01.jpg through sheet_08.jpg provide the chronological contact sheets. target/t*.jpg holds 69 full-resolution source frames. Five useful target sheets/crops show healing coins, opening/turn 4, midgame, closing transactions, and settled benched Energy counts. make_evidence_sheets.py reproduces three grouped sheets. All are local derivatives inside this packet.

Lead check anchors:

- Opening: 11, 21, 24 and 32 s for setup, Auto, Poké Ball, Gastly and first Energy.
- Ordinary turn: 41.5, 44.5, 47, 51 and 54.5 s for turn 4 draw, attachment, HP healing and explicit Heads.
- First point: 77, 82.5, 85.5, 91.5 and 94.5 s for healing Heads, Land Laser 1H1T, 100 damage, award and Haunter promotion.
- Decisive chain: 111.5, 114.5, 118, 122, 126, 128, 129, 131, 134 and 146 s for ability text, Auto off/on, transfer settling, Stadium, normal later attachment, 220 damage and visible Mega Medicham ex discard.
- Final: 167.5, 175.5, 177, 180, 187.5 and 194.8 s for the two Heads, attachment, 220 attack, third point and results 540/10/3-0.

Attribution: this file describes this delegated worker's visual first pass. Parent feedback on selected frames is not counted as a second complete battle review or final acceptance. No independent verifier or lead acceptance is claimed here.
