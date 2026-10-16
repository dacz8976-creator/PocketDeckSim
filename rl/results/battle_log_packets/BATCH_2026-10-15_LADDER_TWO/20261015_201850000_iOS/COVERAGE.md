# Coverage checklist

Source: 20261015_201850000_iOS.MP4, SHA-256 877668e7f12e0619f4cd1a372cba29d9c1e45af52f98ca4a0274d1f026c215cb, duration 801.665 seconds. Reviewer /root/ladder_201850, gpt-6.1-sol high. One match, 22 global turns, 11 owner turns, complete setup and terminal result.

All rows below were visually inspected. Times are approximate source-local phase boundaries. The overview is supplemented by the five-second dense sequence and native inspection, not used alone as proof of complete coverage.

| Phase | Seconds | Evidence | Status |
|---|---:|---|---|
| Prematch, exact ranked queue, opponent and setup | 0-36 | dense01-02; native4,30,35 | Covered |
| Global1 opponent development | 36-86 | dense02-03 | Covered |
| Global2 / ownerT1 | 86-121 | dense03-05; native98,115 | Covered |
| Global3 opponent evolution/stadium | 121-174 | dense05-06; native160 | Covered |
| Global4 / ownerT2 search/retreat/evolve | 174-207 | dense06-07; native195,215 | Covered |
| Global5 Dragonair attack | 207-239 | dense08; native215,252 before/after | Covered |
| Global6 / ownerT3 first attack | 239-270 | dense09; native252,262,270 | Covered |
| Global7 switch/Sabrina | 270-334 | dense10-12; native320,326,329 | Covered |
| Global8 / ownerT4 retained Ilima | 334-354 | dense12; native340,350 | Covered |
| Global9 bench attack | 354-381 | dense13; native380 | Covered |
| Global10 / ownerT5 failed search/attachment | 381-410 | dense13-14; native400 | Covered |
| Global11 development/bench attack | 410-440 | dense14-15; native430 | Covered |
| Global12 / ownerT6 Muk | 440-460 | dense15-16; native448-450,455 | Covered |
| Global13 bench attack | 460-496 | dense16-17; native480 | Covered |
| Global14 / ownerT7 Copycat/evolution | 496-517 | dense17-18; native515 | Covered |
| Global15 Cyrus/TakeDown | 517-555 | dense18-19; native528.30,530,548,550,551 | Covered |
| Global16 / ownerT8 Glimmora attack | 555-573 | dense19-20; native565,580 | Covered |
| Global17 first KO/point | 573-628 | dense20-21; native600,605,609,613,615 | Covered |
| Global18 / ownerT9 GigaTurbo shield | 628-650 | dense22; native635,639-645,650 | Covered |
| Global19 Mega/Regigigas KO | 650-695 | dense23-24; native670,685 | Covered |
| Global20 / ownerT10 pressure/setup | 695-712 | dense24; native700 | Covered |
| Global21 Glimmora KO/heads/no point | 712-766 | dense25-26; native745,750,751,754,755,758,761,763,765 | Covered |
| Global22 / ownerT11 RareCandy/Kingambit/+3 | 766-789 | dense26-27; native769-776,778,780,790 | Covered |
| Victory result/end-of-file | 789-801.665 | dense27; native801 | Covered |

Decisive reconciliations checked: owner second; first Glimmora attack ownT3/opponent0; Regigigas GigaTurbo ownT9/opponent1 with shield preventing damage; Kingambit first attack ownT11/opponent2; three owner KOs but only two opponent points; 180 Overlord's Blade into Mega170; +3 points; final3-2; result270damage. No Auto option was seen. No additional match or continuation is present. Uncertainty is limited to hidden/unreadable information described in UNCERTAINTIES.json; no phase remains pending.
