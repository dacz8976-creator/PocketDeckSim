# Coverage

Source: 20260930_161633000_iOS.MP4,169.925s, SHA-2560795e24efb0f71c3461d23b5860a736a30755cf2071a3047eb4b90a731193a79. Registered identity in SOURCE.json.

Inspected all57 three-second overview samples and all seven sheets: overview/sheet_01.jpg through sheet_07.jpg. Each sheet contains up to9source frames; labels1.50-169.50s are fps midpoints. Native-resolution targeted frames in targets/ were inspected at23,27,30,33,36,39,48,49,51,56,59,64,65,66,69,72,74,77,80,83,86,87,88,90,93,95,96,110,113,116,117,118.7,119,125,126,141,144,147,155,156,157,169seconds. Every retained target was reviewed;42target frames total.

| Interval | Coverage | Evidence anchors |
|---|---|---|
| 0-18 | Setup/deal/coin/Auto and Active reveal | sheet01; sample00004 at10.50s; target23 confirms card text and player identity |
| 18-25.50 | Computer turn1 and owner turn2 handoff | sheet01; target23; sample00009 at25.50s |
| 25.50-43.50 | Owner turn2: draw versus search, distinctDrilbur versions, bench, attachment, attack | sheet02; targets27,30,33,36,39;40.50attackbanner/43.50stableHP |
| 43.50-69 | Computer turn3: Heliolisk, Research, Pikachu, Bellibolt, Energy, Tool | sheets02-03; targets48,49,51,56,59,64,65,66,69 |
| 69-80 | Owner turn4: LuckyIcePopdraw, BenchEnergy, Riolu60damage | sheet03; targets72,74,77,80 |
| 80-109.50 | Computer turn5: RaichuEvoshocktails, ElectricGeneratortails, attachment,70damage, KO/point/promotion | sheet04; targets83,86,87,88,90,93,95,96;103.50point/106.50promotion |
| 109.50-124.50 | Owner turn6: MegaLucariodraw, DrilburBbench, BenchEnergy, Scratch30 | sheet05; targets110,113,116,117,118.7,119,125 |
| 124.50-141 | Computer turn7: RaichuEnergy, Cannon, KO/point/promotion | sheets05-06; target126;127.50attack/130.50zero/133.50point;target141turn8 |
| 141-151.50 | Owner turn8: Arenaheld, secondFighting, HeadbuttBounce50 | sheet06; targets144,147;148.50attack/151.50Bellibolt20 |
| 151.50-163.50 | Computer turn9: Cannon70, thirdKO/point | sheet06-07; targets155,156,157;157.50zero/160.50thirdpoint |
| 163.50-169.925 | Terminal transition and explicit Defeat | sheet07;target169;sample00057at169.50 |

Coverage conclusion: end-to-end meaningful phase coverage for the single complete battle, including every numbered turn. Sampling is not a frame-by-frame transcript; final425ms follows the established terminal result. Hidden information and untested interactions are limits rather than uncovered battle phases. No second broad extraction was performed. No consequential hard ambiguity requiring Astra remains after targeted checks; exact Tool title stays unknown while its effect and state transition are independently visible.
