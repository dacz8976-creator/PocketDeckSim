# Coverage and retained evidence

**Current status: completed full-battle review accepted by the lead; original archived unchanged in `Reviewed`. Excluded from Ladder Log.**

Reviewer: sol_auto_evening_024209000, gpt-6.1-sol / high. Scope: one full 227.535-second battle, setup through final result. Full review accepted by the lead; registration and archival are verified.

All source intervals are covered by the inspected three-second overview plus targeted native-resolution evidence. Interval boundaries below are approximate phase brackets, not exact action onsets. Overview frame labels use fps midpoint sampling. Native `t...` filenames are requested source timestamps.

| Interval in seconds | Phase | Meaningful coverage | Retained evidence |
|---|---|---|---|
| 0-19 | Setup | Load, coin animation, hand, Victini/Numel and Scyther, checked Auto | overview/sheet_01.jpg; targeted/t0015.00.jpg |
| 19-29 | Turn 1 opponent | Draw, Poké Ball, Wynaut Bench, no attack | dense/t0023.00.jpg; dense/t0024.00.jpg; dense/t0026.00.jpg; targeted/t0027.00.jpg; targeted/t0029.00.jpg |
| 29-36 | Turn 2 owner | Bounded Field draw retained, Fire to Numel, pass | overview/sheet_02.jpg; targeted/t0032.00.jpg; targeted/t0034.00.jpg; dense/t0035.00.jpg |
| 36-49 | Turn 3 opponent | Honedge Bench, Scyther Metal, U-turn 10, Wynaut promotion | overview/sheet_02.jpg; targeted/t0041.00.jpg; targeted/t0045.00.jpg; targeted/t0049.00.jpg |
| 49-57 | Turn 4 owner | Numel draw, Mega Camerupt evolution, second Fire, no attack | dense/t0051.00.jpg; targeted/t0053.00.jpg; dense/t0054.00.jpg; targeted/t0057.00.jpg |
| 57-69 | Turn 5 opponent | Doublade evolution/first Metal, Stompy Jammer 10/cost marker | overview/sheet_03.jpg; targeted/t0061.00.jpg; targeted/t0065.00.jpg |
| 69-81 | Turn 6 owner | Research/draws, third Fire, second Victini Bench, ability text | overview/sheet_03.jpg; targeted/t0069.00.jpg; targeted/t0074.00.jpg; dense/t0076.00.jpg; targeted/t0080.00.jpg |
| 81-91 | Turn 7 opponent | Second Scyther, Doublade second Metal, Jammer 10 | dense/t0081.00.jpg; targeted/t0083.00.jpg; overview/sheet_04.jpg; targeted/t0090.00.jpg |
| 91-136 | Turn 8 owner | Manual Auto pause, Rainbow Cave/play/use, Research, actual Flame Patch, retreat, Fire4, Numel Bench, random Scyther KO/point1 | dense/sheet_1.jpg; dense/sheet_2.jpg; dense/sheet_3.jpg; targeted/t0116.00.jpg; dense/t0118.00.jpg; targeted/t0121.00.jpg; dense/t0122.00.jpg; dense/t0126.00.jpg; targeted/t0127.00.jpg; targeted/t0130.00.jpg; targeted/t0136.00.jpg |
| 136-151 | Turn 9 opponent | Scyther first Metal, Training Area replaces Rainbow, switch to Doublade, Slash50 | targeted/t0141.00.jpg; targeted/t0144.00.jpg; dense/t0145.00.jpg; dense/t0146.00.jpg; targeted/t0149.00.jpg; dense/t0151.00.jpg |
| 151-169 | Turn 10 owner | Pansear draw retained, Numel Fire1, random Doublade190/KO/point2, Scyther promoted | targeted/t0153.00.jpg; dense/t0155.00.jpg; targeted/t0157.00.jpg; dense/t0158.00.jpg; dense/t0160.00.jpg; dense/t0161.00.jpg; targeted/t0162.00.jpg; targeted/t0169.00.jpg |
| 169-188 | Turn 11 opponent | Scyther Metal2/Mega Scizor evolution, Honedge Bench, Skyla switch to Wynaut, Jammer10 | targeted/t0174.00.jpg; targeted/t0178.00.jpg; extra/t0179.50.jpg; dense/t0180.00.jpg; dense/t0182.00.jpg; targeted/t0185.00.jpg; dense/t0186.00.jpg; dense/t0187.00.jpg; dense/t0188.00.jpg |
| 188-200 | Turn 12 owner | Flame Patch draw retained, Mega Fire4->5, random Mega Scizor160/200->40, no point | dense/t0189.00.jpg; targeted/t0190.00.jpg; dense/t0191.00.jpg; dense/t0192.00.jpg; dense/t0193.00.jpg; targeted/t0194.00.jpg; dense/t0195.00.jpg; targeted/t0197.00.jpg; dense/t0198.00.jpg; targeted/t0200.00.jpg |
| 200-220 | Turn 13 opponent | Second Doublade evolution, Mega Metal3, detail overlay/gray Auto, Wynaut switch, Bullet Slugger160, Camerupt150->0, opponent+3 | targeted/t0202.00.jpg; dense/t0203.00.jpg; dense/t0204.00.jpg; targeted/t0205.00.jpg; dense/t0206.00.jpg; dense/t0207.00.jpg; targeted/t0209.00.jpg; dense/t0212.00.jpg; dense/t0213.00.jpg; targeted/t0214.00.jpg; targeted/t0219.00.jpg; dense/t0220.00.jpg |
| 220-227.535 | Terminal | Defeat, named Solo challenge, Card of Game, completed stats | overview/sheet_09.jpg; targeted/t0226.00.jpg; terminal/t0227.40.jpg |

Overview sheets 01-09 all inspected, including every intermediate ordinary phase. Native targeted and dense sheets inspected, including retained attack snapshots. No unexplored turn or material interval remains in this first pass. Exact coin face, hidden cards and second brief Auto detail state remain explicitly limited in UNCERTAINTIES.json.

## Suggested independent lead checks

- Opening: 15.00 seconds, Victini70 active / Numel70 Bench / Scyther70 active and Auto checked.
- Ordinary phase: 83.00 seconds, Victini50 active; Mega Camerupt210 with three Fire and Victini70 Bench; opposing Wynaut30 active, Scyther70/one Metal and Doublade90/one Metal on Bench.
- Manual resource sequence: 96.00, 103.00-107.00, 115.00, 118.00, 121.00-122.00 seconds for Auto pause, Rainbow Energy discard/regeneration, Flame Patch to Victini, retreat and Camerupt Fire4.
- First knockout: 126.00-130.00 seconds, random Scyther bench hit160 and removal; point shown by136.00.
- Second knockout: 157.00, 160.00-162.00 seconds, reserve Numel Fire1, Camerupt Fire4, active Doublade displayed190 and KO.
- Skyla: 179.50 seconds exact readable card effect and 182.00 seconds resulting Wynaut active / Scizor Bench2 Metal.
- Decisive attack choice/outcome: 189.00-194.00 seconds Fire4->5 and retained Flame Patch; 197.00-198.00 seconds Scizor200->40, score2-0.
- Terminal chain: 207.00-209.00 seconds Scizor promoted/three Metal; 213.00 seconds damage160; 214.00 seconds Camerupt HP0; 219.00 seconds opponent+3; 227.40 seconds completed stats.
