# Full-source coverage

Source: 20261012_004435000_iOS.MP4, 463.93 seconds. SHA-256:`7326d0f49952bda981acb67765fb118375963a485c52161e693cb7cf85be37fe`. Reviewer:`/root/pause_20261012_004435000_ios`. Complete first pass, awaiting independent acceptance.

| Interval seconds | Phase | Coverage and retained evidence |
|---|---|---|
| 0–43 | Filmed QR, matchmaking, five-card opening, turn order and setup | Overview 0–40; native 0/5/10/20/26/27/43/44, decoded source-boundQR. |
| 43–132 | Opponent turn 1 | All reduced 4 second samples 44–132 inspected, including long wait; native 44/127/129/134 boundary. Tool and timeout checked. |
| 132–140 | Owner turn 2 | Native 134 normaldraw;135 drawend;136/138/141 scheduled candidates;136 selected;139 endinghand. |
| 140–186 | Opponent turn 3 | Reduced 140–184; native 141/150/151.5/154/158/162/166/170/174/178/185/186. Research, Benches, Energy, Stadium, evolution, timeout. |
| 186–223 | Owner turn 4 and checkup | Native 187.5 draw, 188.3 densepreplay;189/191/194 candidates;197–202 evolution/ability;207/210/213/214/222/223 resolution. |
| 223–271 | Opponent turn 5 | Reduced 224–268; native 230/233/237/242/243/244/246/249/267/270. Irida text, heal cap, both conditions and tails checked. |
| 271–300 | Owner turn 6 and checkup | Native 272.5 draw, 274.5 preplay;275/277/280 candidates;278/279 search;281/286/289/291 plays andpreend;293/294 Stadiumdraw;299/300 Burnrecovery. |
| 300–347 | Opponent turn 7 | Reduced 300–344; native 304 start, 309/310/313/315 evolution/AquaCharge, 333/342/346 end. Both Water destinations reconciled. |
| 347–416 | Owner turn 8 | Native 350 draw, 351.4 densepreplay;352/354/357 candidates;358/369/373–380 Copycat/Tool;392/394/397–410 retreat/attack/Poison;414 endStadiumdraw. |
| 416–445 | Opponent turn 9 and checkup | Reduced 416–444; native 419/423/424/425/426/427 Energyorder;435 Researchresultfan;437 attack, 441 milltop;443/446 Poisonchanges. |
| 445–453 | Owner turn 10 and concession | Native 445/446/447 draw;448 all 4;449/451/454 scheduledcandidates;449 preinspection;450/450.5 Researchinspection;451/452 notice. |
| 453–463.93 | Terminal transition and final result | Native 453/454/455/462; reduced 456/460; final source endpoint examined. Victory/10 turns/0 points/90 damage. No additional game. |

Method: a bounded reduced overview every 4 seconds from 0 through 460 established complete sequence, with native 1170×2532 captures around every meaningful action, fast play, draw, board boundary and terminal event. All 116 reduced overview frames were inspected. Native frames already retained were reused. Independent review has reused the same source-bound frames and 42 native hand/top crop pairs.

Draw-timed evidence uses actual located draw-animation ends, not the grid. Owner turn candidate sets are T2: 136/138/141;T4: 189/191/194 plus 188.3 densepreplay;T6: 275/277/280 plus 274.5 densepreplay;T8: 352/354/357 plus 351.4 densepreplay;T10: 449/451/454. Before-ending hands: 139/213/289/402/449. Post-resolution hands: 139/213/294/419/452. Full native evidence, crop pixel bounds, source SHA and selection limits are in TURN_EVIDENCE.json.

All turns 1–10 have exactly one TURN_LEDGER.json row. No source interval or recorded turn remains unreviewed. All 5 opening identities, all owner normal draws, Poké Ball find, all 3 Copycat reveals and both owner Hiking Trail draws are directly named. Opponent hidden draws remain null individually. Opponent native fan counts at owner starts are 4/2/3/3/5.

No discard-pile screen is opened in any inspected interval. Scheduled owner/opponent discard requests are explicitly marked not shown, with inspected full-source limits, rather than inventing full piles. T9 three-card mill retains only observed final top Soothing Shore; other 2 identities stay null. Exact source-frame PTS was not measured. These are recording/evidence limits, not unfinished coverage.
