# Coverage check

Source: `20261009_222100000_iOS.MP4`, SHA-256 in `SOURCE.json`. Full visual sweep used a labeled one-frame-per-second overview (0-195s), then original-resolution targeted frames. The terminal 167-170s interval was checked at 10 frames per second. The overview is navigation only; consequential claims cite native frames in `REVIEW.md` and `FRAME_INDEX.md`.

| Interval | Coverage | Status |
| --- | --- | --- |
| 0-23s | Loading, opponent and turn order, starting Active, Bench, hand | Covered |
| 24-55s | Owner turn 1: Stadium, Copycat, Bench, Poke Ball, no attack | Covered |
| 55-72s | Opponent turn 2: bench, Energy, Tool, Headbutt | Covered; Tool identity unknown |
| 73-87s | Owner turn 3: Heavy Helmet, Watch Over, Energy, end turn | Covered |
| 88-118s | Opponent turn 4: Rare Candy, Roar in Unison, Hyper Ray, first point | Covered |
| 119-132s | Owner turn 5: promotion, failed Poke Ball, second Energy, end turn | Covered |
| 133-159s | Opponent turn 6: second Roar in Unison, Poke Ball, Hyper Ray, second point | Covered |
| 159-169s | Active selection, Concede dialog, owner turn 7, Wailord drawn, Defeat | Covered; exact final input unknown |
| 170-195.99s | Results screen through end; no second match | Covered |

Points reconcile 0-0 -> 0-1 -> 0-2; no third point. The full recorded battle and result are reviewed. Independent lead acceptance and review-log registration remain outside this worker's scope.
