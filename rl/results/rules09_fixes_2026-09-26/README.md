Decision this informs: which engine every later reading uses. The Sept 26 repairs change table games through two of them (Legendary Pulse's order, promotion timing), so kp3's reference table is regenerated at the repaired engine, and every candidate after it (kt, koa, kpf) is paired against that table, not the Sept 25 one. Engines:
- the repaired engine e935f42, run with scan af8489f (the example with openings and decisions);
- the pre-repair engine 07927e2 (engine src = e09fb46, the Sept 25 table's);
- one run at each repair commit.

Seeds: the table's deals only, 72,000,000 + pairing × 10,000 + i, i < 500 (i < 40 for the spot references), even i = first-named deck in seat 0.

# The Sept 26 engine repairs: what each one changes on the table

## In plain words

- **Ten repairs, each its own commit with a test** (rules/09's Fixed section; the laptop's repair list items 1 to 10, plus the two discard-pile items from the same source). Only two of them change table games: Legendary Pulse drawing before Hiking Trail, and promotion after an end-of-turn or Checkup knockout.
- **A game's record can change without its play changing.** The scan fingerprints every step of a game ("moves"), forced ones included. Two repairs change the forced steps themselves:
  - Legendary Pulse's draw is no longer a separate queued step;
  - the promotion repair adds a "finish Checkup" step.

  So from af8489f's scan on, each game also carries a fingerprint of its choices only ("decisions": moves picked from two or more options). A game with the same decisions was played the same way.
- **The new references are `af8489f_k3_500.jsonl` and `af8489f_kp3_500.jsonl`**, plus the spot references `af8489f_{kq3,kd3,kpr3}_40.jsonl` for i < 40. Scoreboard v2's kp3 row and every later candidate read against these.

## Per repair, k3 and kp3 over the 14,000 table games

| commit | repair | k3: records / choices / results differ | kp3: records / choices / results differ |
|---|---|---|---|
| 07927e2 | none (pre-repair engine, new scan) | 0 / – / 0 against the Sept 25 tables | 0 / – / 0 against the Sept 25 tables |
| 3c2250f, 14745ce, 050cf51, a30b5f8 | Poké Ball A2b 111; Rare Candy v Primeval Law; Heavy Helmet at the current Retreat Cost; discard-all-Energy to the pile | 0 each (the laptop's replays, main 5b78a8c and 746ca9a) | 0 each (same) |
| 3102c9e | the random Energy pick (and the four above, cumulative) | 0 / 0 / 0 | 0 / 0 / 0 |
| 5b75bf9 | Legendary Pulse before Hiking Trail | 3,124 / 1,261 / 434 | 3,197 / 758 / 244 |
| 5bab907 | promotion before the next turn after an end-of-turn or Checkup knockout | 3,649 / 1,421 / 520 | 3,812 / 1,590 / 620 |
| 02fe9de, 53cba79, 213c090, 4407c55, e935f42 | Disguise; Bad Dreams v protections; Clemont's Backpack; Zone-to-self Abilities under the lock; Clemont's hand cap | cumulative (5bab907 → af8489f): 0 / 0 / 0; per commit: running | cumulative: 0 / 0 / 0; per commit: running |
| af8489f (e935f42) | all ten, against the Sept 25 tables | 6,167 records, 940 results | 6,367 records, 855 results |

### Legendary Pulse (5b75bf9), per cell: records / choices / results

| cell | k3 | kp3 |
|---|---|---|
| altaria v suicune | 452 / 253 / 103 | 459 / 162 / 54 |
| suicune v vespiquen | 455 / 200 / 68 | 464 / 105 / 27 |
| blaziken v suicune | 429 / 179 / 36 | 436 / 113 / 38 |
| hydreigon v suicune | 437 / 163 / 73 | 450 / 101 / 51 |
| suicune v weezing | 462 / 162 / 55 | 467 / 96 / 29 |
| lucario v suicune | 445 / 173 / 50 | 459 / 84 / 12 |
| sceptile v suicune | 444 / 131 / 49 | 462 / 97 / 33 |

- Every Suicune cell changes, not only Blaziken v Suicune (the Hiking Trail cell rules/09 named).
- About 450 of 500 records change in each: the queued draw step is gone wherever Suicune ex sat Active at the end of a turn.
- Choices change in 84 to 253 games per cell. Pulse's card now reaches the hand inside the end of the turn, where the searches see it; before, it waited as a separate draw at the next turn's start. That is the likely reason; it is not traced game by game.

### Promotion timing (5bab907), per cell: records / choices / results

| cell | k3 | kp3 |
|---|---|---|
| altaria v weezing | 351 / 220 / 89 | 355 / 238 / 96 |
| hydreigon v weezing | 301 / 159 / 61 | 278 / 154 / 67 |
| blaziken v weezing | 280 / 131 / 38 | 304 / 163 / 57 |
| lucario v weezing | 253 / 127 / 42 | 289 / 152 / 59 |
| altaria v blaziken | 282 / 91 / 34 | 295 / 114 / 53 |
| suicune v weezing | 174 / 89 / 29 | 196 / 110 / 47 |
| altaria v hydreigon | 237 / 93 / 40 | 217 / 85 / 34 |
| altaria v lucario | 237 / 69 / 19 | 267 / 95 / 20 |
| sceptile v weezing | 229 / 60 / 28 | 240 / 78 / 28 |
| altaria v suicune | 140 / 67 / 24 | 129 / 61 / 30 |
| vespiquen v weezing | 84 / 48 / 17 | 91 / 59 / 20 |
| blaziken v suicune | 195 / 44 / 25 | 207 / 61 / 30 |
| blaziken v hydreigon | 132 / 48 / 13 | 123 / 49 / 23 |
| altaria v sceptile | 138 / 38 / 14 | 152 / 32 / 12 |
| hydreigon v lucario | 71 / 26 / 3 | 75 / 30 / 3 |
| blaziken v sceptile | 113 / 19 / 8 | 121 / 20 / 11 |
| altaria v vespiquen | 70 / 17 / 4 | 63 / 14 / 3 |
| hydreigon v sceptile | 76 / 12 / 8 | 103 / 19 / 9 |
| hydreigon v suicune | 84 / 18 / 6 | 79 / 13 / 2 |
| sceptile v suicune | 68 / 11 / 4 | 75 / 13 / 4 |
| hydreigon v vespiquen | 43 / 7 / 2 | 57 / 14 / 5 |
| blaziken v lucario | 38 / 10 / 5 | 39 / 8 / 2 |
| blaziken v vespiquen | 34 / 10 / 5 | 38 / 7 / 4 |
| sceptile v vespiquen | 19 / 7 / 2 | 19 / 1 / 1 |

- It reaches every cell where a Pokémon is knocked out at the end of a turn or in Checkup: Poison (Weezing's cells lead), Bad Dreams (Altaria's) and Burn (Blaziken's).
- Lucario v Sceptile and Lucario v Vespiquen are unchanged.
- Choices change where a promotion is now made without the next draw and Energy in view, and where the search reads the paused turn differently.

## Files

- `run_replay.sh`: the command (a `BOTS` list for the spot references). `compare.py`: the comparison. `timing.txt`: wall times, scan hashes, and the note on the four commits the laptop replayed.
- `<commit>_{k3,kp3}_500.{jsonl,txt}`: the raw outputs. `af8489f_{kq3,kd3,kpr3}_40.*`: the spot references.
- `compare_af8489f_vs_reference.txt`: the repaired engine against the Sept 25 tables, per cell, with seeds.
- `compare_per_repair.txt`: each repair against the commit before it, records and choices, per cell, with seeds.
- **Scans:** 07927e2, 3102c9e, 5b75bf9, 5bab907 and af8489f were run with the example at af8489f (openings and decisions); their hashes are in `timing.txt`. 02fe9de, 53cba79, 213c090 and 4407c55 run with the example at a03f491 (moves only), built at each commit.
