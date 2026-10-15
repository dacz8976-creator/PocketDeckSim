# Source coverage and capture reconciliation

Source: 20261013_015011000_iOS.MP4. SHA-256: 7394580c71facb269a7c6703e890ff1eb360ffd509875eb09d03343f43b4fe7a. Duration 182.693333 s. Reviewer: /root/pause_20261013_015011000_iOS. One game, three turns, all recorded phases inspected. No unreviewed interval or linked clip identified. Independent acceptance pending.

| Interval | Coverage | Retained evidence |
|---|---|---|
|0 to 4|Native filmed deck QR, closure and unchanged deck selection|native 1.00 plus overview 1/3|
|4 to 25|Match search, opponent profile, versus, first-player decision|overview 5 to 25|
|25 to 37|All five opening cards before Active, Active and Bench selection, opponent setup|native 27.50/28.50/34.50/37.00|
|37 to 71.80|Turn 1 draw, search, Bench placement, restriction feedback, Copycat and all four reveals, hand/end reconciliation|native 42 to 71.80, overview 37 to 71|
|71.80 to 83|Opponent draw, Energy generation, Tyrogue placement, Falinks attachment|native 72.30/73.50/75.50/79.50/81.50|
|83 to 162.50|Persistent board and hand, wait, opponent-return warning, countdown expiration|Every2s overview sample plus native 107/162.50|
|162.50 to 170.50|Turn 3 draw, pre-play hand, Energy generation, no voluntary play, error|native 162.50 to 170.50|
|170.50 to 182.693333|Victory animation, loading, final Victory details, end|overview 171 to 181, native 172/181.50/182.30|

| Required capture | Result |
|---|---|
|Five opening slots and selected Active|All 5 named; opening Copycat label clipped and artwork corroborated at 43.50; position 4 Pawniard, native 27.50; right Bench Alolan Grimer confirmed34.50.|
|Turn 1 draw+1/+3/+6|44.20/46.20/49.20 retained with crops. First play before+1. Dense43.50 selected before play.|
|Turn 3 draw+1/+3/+6|167/169/172 retained with crops.167 selected.169 error; 172 Victory, documented unsuitable.|
|Before end hands|Turn 1 native 71.50, 4 cards. Turn 3 native 167.50, 5 cards before terminal error because no end action.|
|Every named draw/search|Ilima; Poke Ball Regigigas; Copycat Research/Research/Heavy Helmet/Lucky Ice Pop; Glimmora. Hidden opponent normal draw explicitly null.|
|Numbered actions and no-effect/declines|Poke Ball, bench Regigigas, Copycat, End Turn; opponent bench Tyrogue then Fighting attachment. Restriction feedback/inspection separate from plays. No offered decline/warning shown.|
|Boards and Energy Zones|Both players at every row start/after, all Bench positions; effective maxima equal printed HP without modifiers; current availability observed, future counts null.|
|Opponent fan counts|4 at owner turn 1; 4 at owner turn 3. Opponent turn 2 fan 5 after draw, 4 after Tyrogue, observed and arithmetic cross-checked.|
|Discard views|No opened pile anywhere; separate absent snapshot entries for each player. Side display is not claimed full coverage.|
|Exact20-card deck|Own native QR20 slots and Darkness, continuous binding to New deck 16, no filmed edit. Exact code matches the historical log snapshot at its recorded retrieval time; fresh live readback unavailable.|
|One structured row per turn|Rows1, 2, 3 exactly once, table and prose links in REVIEW.md.|
|Outcome|Return-failure error169; Victory181.50; details182.30 show 3 turns, 0-0,damage 0.|

Evidence is native 1170x2532 with bottom bounds[0, 2025, 1170, 2532] and top bounds[0, 0, 1170, 760]. Reduced overview is labeled separately and never used as native hand evidence. No source moved or external/shared state written by worker.
