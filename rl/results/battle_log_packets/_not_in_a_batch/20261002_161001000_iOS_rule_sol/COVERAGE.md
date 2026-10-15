# Coverage: 20261002_161001000_iOS.MP4

**Current status: lead-accepted rule_test_review_complete; original archived unchanged in `Reviewed`. Excluded from Ladder Log.**

Complete available-footage review: true. Reviewed range: 0.00 to 206.873537s. Battle-complete assertion: false because this is a split recording with a gap. Source binding was read before decode, and part 2 was decoded only after root confirmed frozen intake.

Shared overview: Recording_QA/extract_auto_review.py, four-second interval, two decode threads, 390-pixel overview width. All 52 overview samples and every sheet below were visually inspected. The full timeline in REVIEW.md covers setup or continuation, every visible turn, checkups, development, attacks, promotions and the source ending. Sampling was supplemented with native frames for short events and text, so decisive conclusions do not depend only on the overview.

- [sheet_01.jpg](overview/sheet_01.jpg)
- [sheet_02.jpg](overview/sheet_02.jpg)
- [sheet_03.jpg](overview/sheet_03.jpg)
- [sheet_04.jpg](overview/sheet_04.jpg)
- [sheet_05.jpg](overview/sheet_05.jpg)
- [sheet_06.jpg](overview/sheet_06.jpg)

Native frames specifically inspected include these file-local timestamps (additional retained frames are not automatically claimed as inspected):

17.00, 29.00, 44.00, 55.00, 65.00, 80.00, 148.00, 176.00, 181.00, 193.00, 198.00, 201.00, 206.80 seconds.

Native checks resolve Meowth Carefree Steps text, Victini Victory Star text, equipment HP, damage changes, retreat and source ending.

The last frame of part 1 (206.80s) and first frame of part 2 (0.00s) show the same public board at owner turn 7: owner Entei ex 70 HP active with two Fire Energy and Lum Berry, Heatmor 100 HP with Giant Cape and Houndour 60 HP with Elegant Cape on the Bench; opponent Meowth 50 HP active with one Fire Energy, Combusken 20 HP with two Fire Energy and Victini 70 HP on the Bench; Rainbow Cave and a 0-0 score. Both show Dacz8976 and phone time 11:13. This supports the owner testimony that these are two parts of one battle. The visible hand differs, so no unseen draw or action is reconstructed. The recording cut is real; its duration and intervening actions are not established. All timestamps stay local to each file.

No footage is assigned to the unrecorded cut interval. No action is invented there. This packet uses only its own evidence images; its counterpart is identified by source identity and report link.


## Independent lead check

Lead read the entire source review, coverage, summary and uncertainty packet and reconciled visible turns1-7, HP, Energy and score. Independently inspected ordinary opening and middle overview sheets01 and04, native193s damage-prevention tooltip and final206.8s board. Compared that board with the continuation first frame: same public turn7 state, hand difference and unknown cut actions/duration retained. This source supplies setup and defender identification; the linked second source supplies the conclusive snipe and computer ending. The owner clarified that Tongue Whip is the filmed example of the snipe class; another Linear Attack trial is not required. Auto off during visible battle UI; blue hexagon is prevention, not Sleep. Entire available source accepted under the explicit rule-test exception, with battle_complete false and both competitive logs excluded.

First-pass reviewer: sol_rules_20261002_carefree_steps; gpt-6.1-sol high. Independent lead and targeted Astra checks: October 2, 2026.

[Targeted Astra check](../BATCH_2026-10-02_CAREFREE_SNIPES/ASTRA_CAREFREE_CHECK.md).
