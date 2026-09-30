# Independent check of the M1 and M2 thresholds (Sept 30)

**Verdict: The independent check agrees.** Every number in `thresholds.json` came out exactly the
same in both independent checks. That includes the two bootstrap bounds on each line, which match
to the last bit.

## What was checked

`thresholds.json` holds the two trainer lines' thresholds. It was made by `km_thresholds.py`
(sha256 `c84a8768…263a`) from the sample rows committed at 1fc9e0b:

- `1f6319e_sample_kta3_rows.jsonl`
- `1f6319e_sample_km3_rows.jsonl`

Each file has 1,400 rows: deals 200-299 in each of the 14 gating cells.

- **M1**: Arena of Antiquity, on Lucario's side, 9 cells.
- **M2**: Training Area, on Altaria's side, the 5 named cells.

The rule comes from `rl/results/trainer_pricing_2026-09-28/REGISTRATION_DRAFT.md`:

- The registration block, items 1-5.
- Section 5 step 3: "The threshold rule for T1 and T2" and the frozen paired-noise calculation.
- Amendment 1 (b) item 2: kta3 is the baseline and km3 the candidate. T is the exact midpoint of
  the two rates. Each bootstrap replicate is km3's played/offered minus kta3's.

## Who checked it

Two separate agents, checker a and checker b, did the check. Neither one wrote `km_thresholds.py`.
Each wrote its own program from the text alone:

- Checker a: `independent_check_a/check_a.py` (sha256 `bce860fe…e3a3`)
- Checker b: `independent_check_b/check_b.py` (sha256 `84151757…5851`)

Both say they wrote their numbers to a file first and opened `thresholds.json` only afterwards.
Neither opened `km_thresholds.py` or `test_km_thresholds.py`, and neither looked at the other
checker's folder. Each then compared its numbers with `thresholds.json` in a second step:

- Checker a (`compare_a.py`): 39 figures compared, 39 AGREE, 0 DISAGREE.
- Checker b (`compare_b.py`): 40 figures compared, 40 AGREE, 0 DISAGREE.

This file was written by a third agent, the recorder. It reads the checkers' two output files and
`thresholds.json`.

Both checkers read the text the same way:

- The owner's side is the side whose deck is exactly "lucario" (M1) or exactly "altaria" (M2).
  "altaria_greninja" is a different deck. Its cell (new_decks.tsv 16) is in M1, as Lucario's
  opponent.
- If a card is missing from a side, that side counts as 0 offered and 0 played.
- Each line gets its own fresh `random.Random` seed. The loop order is: replicate, then each cell
  in the fixed order, then 100 draws of `randrange(100)` over deals 200-299 in increasing order.
- Each replicate's difference is km3's rate minus kta3's rate, as Python floats.
- The bounds come from `pct` in `rl/results/table_readings_2026-09-24/score.py` (lines 143-144),
  at the 2.5% and 97.5% points. With 10,000 replicates, those are sorted positions 250 and 9750.

## The numbers, side by side

### Inputs

| Figure | thresholds.json | checker a | checker b | |
|---|---|---|---|---|
| kta3 rows file, sha256 | `743176c6f66951e506cb72a946d122f33543b0358b04b4e61f1c00f795b73fc3` | same | same | AGREE |
| kta3 rows | 1400 | 1400 | 1400 | AGREE |
| km3 rows file, sha256 | `687e138a5bc924869f27e1a4bfe9118db76424fa4ca79e0d13677fc19c2d3846` | same | same | AGREE |
| km3 rows | 1400 | 1400 | 1400 | AGREE |
| Python | 3.14.4 | 3.14.4 | 3.14.4 | AGREE |

### M1: Arena of Antiquity (Lucario's side)

| Figure | thresholds.json | checker a | checker b | |
|---|---|---|---|---|
| Owner side | lucario | lucario | lucario | AGREE |
| Cells, in order | table 2, 8, 13, 18, 19, 20, 21; new_decks.tsv 8, 16 | same | same | AGREE |
| Deals | 200-299 | 200-299 | 200-299 | AGREE |
| Bootstrap seed | 20260929 | 20260929 | 20260929 | AGREE |
| Replicates | 10000 | 10000 | 10000 | AGREE |
| kta3 offered | 1664 | 1664 | 1664 | AGREE |
| kta3 played | 355 | 355 | 355 | AGREE |
| kta3 rate, exact | 355/1664 | 355/1664 | 355/1664 | AGREE |
| kta3 rate, shown | 21.3% | 21.3% | 21.3% | AGREE |
| km3 offered | 1308 | 1308 | 1308 | AGREE |
| km3 played | 444 | 444 | 444 | AGREE |
| km3 rate, exact | 37/109 | 37/109 | 37/109 | AGREE |
| km3 rate, shown | 33.9% | 33.9% | 33.9% | AGREE |
| T1, exact | 100263/362752 | 100263/362752 | 100263/362752 | AGREE |
| T1, shown | 27.6% | 27.6% | 27.6% | AGREE |
| Sorted positions used | 250, 9750 | 250, 9750 | 250, 9750 | AGREE |
| Replicates with 0 offered | 0 | 0 | 0 | AGREE |
| Lower bound | 0.10706821380818238 | 0.10706821380818238 | 0.10706821380818238 | AGREE |
| Lower bound, bits (float.hex) | 0x1.b68d28cbf4dacp-4 | 0x1.b68d28cbf4dacp-4 | 0x1.b68d28cbf4dacp-4 | AGREE |
| Upper bound | 0.14692109105529338 | 0.14692109105529338 | 0.14692109105529338 | AGREE |
| Upper bound, bits (float.hex) | 0x1.2ce4f70966a70p-3 | 0x1.2ce4f70966a70p-3 | 0x1.2ce4f70966a70p-3 | AGREE |
| Result | threshold (lower bound above zero) | can pass | can pass | AGREE |

### M2: Training Area (Altaria's side)

| Figure | thresholds.json | checker a | checker b | |
|---|---|---|---|---|
| Owner side | altaria | altaria | altaria | AGREE |
| Cells, in order | table 0, 1, 3, 4; new_decks.tsv 9 | same | same | AGREE |
| Deals | 200-299 | 200-299 | 200-299 | AGREE |
| Bootstrap seed | 20260930 | 20260930 | 20260930 | AGREE |
| Replicates | 10000 | 10000 | 10000 | AGREE |
| kta3 offered | 870 | 870 | 870 | AGREE |
| kta3 played | 254 | 254 | 254 | AGREE |
| kta3 rate, exact | 127/435 | 127/435 | 127/435 | AGREE |
| kta3 rate, shown | 29.2% | 29.2% | 29.2% | AGREE |
| km3 offered | 786 | 786 | 786 | AGREE |
| km3 played | 275 | 275 | 275 | AGREE |
| km3 rate, exact | 275/786 | 275/786 | 275/786 | AGREE |
| km3 rate, shown | 35.0% | 35.0% | 35.0% | AGREE |
| T2, exact | 24383/75980 | 24383/75980 | 24383/75980 | AGREE |
| T2, shown | 32.1% | 32.1% | 32.1% | AGREE |
| Sorted positions used | 250, 9750 | 250, 9750 | 250, 9750 | AGREE |
| Replicates with 0 offered | 0 | 0 | 0 | AGREE |
| Lower bound | 0.03862448982989242 | 0.03862448982989242 | 0.03862448982989242 | AGREE |
| Lower bound, bits (float.hex) | 0x1.3c696d149c3e0p-5 | 0x1.3c696d149c3e0p-5 | 0x1.3c696d149c3e0p-5 | AGREE |
| Upper bound | 0.0782545074154864 | 0.0782545074154864 | 0.0782545074154864 | AGREE |
| Upper bound, bits (float.hex) | 0x1.4087cc61d35e4p-4 | 0x1.4087cc61d35e4p-4 | 0x1.4087cc61d35e4p-4 | AGREE |
| Result | threshold (lower bound above zero) | can pass | can pass | AGREE |

`thresholds.json` stores the bounds as numbers and as repr strings, not in hex. The hex in its
column is checker a's `float.hex` of the stored value. A float's repr maps back to exactly one
float, so matching repr strings already means the bits match.

### Per-cell counts (checker a v checker b; `thresholds.json` does not list these)

The figures are played/offered, owner's side, deals 200-299. All 14 cells agree between the two
checkers. In each line the cells add up to the pooled counts above.

| Line | Cell | kta3 (a) | kta3 (b) | km3 (a) | km3 (b) | |
|---|---|---|---|---|---|---|
| M1 | table 2, altaria v lucario | 31/175 | 31/175 | 38/153 | 38/153 | AGREE |
| M1 | table 8, blaziken v lucario | 38/205 | 38/205 | 47/180 | 47/180 | AGREE |
| M1 | table 13, hydreigon v lucario | 40/209 | 40/209 | 54/127 | 54/127 | AGREE |
| M1 | table 18, lucario v sceptile | 23/218 | 23/218 | 29/208 | 29/208 | AGREE |
| M1 | table 19, lucario v suicune | 41/139 | 41/139 | 48/95 | 48/95 | AGREE |
| M1 | table 20, lucario v vespiquen | 56/123 | 56/123 | 69/84 | 69/84 | AGREE |
| M1 | table 21, lucario v weezing | 56/135 | 56/135 | 68/88 | 68/88 | AGREE |
| M1 | new_decks.tsv 8, rayquaza v lucario | 44/262 | 44/262 | 56/189 | 56/189 | AGREE |
| M1 | new_decks.tsv 16, altaria_greninja v lucario | 26/198 | 26/198 | 35/184 | 35/184 | AGREE |
| M2 | table 0, altaria v blaziken | 41/165 | 41/165 | 46/159 | 46/159 | AGREE |
| M2 | table 1, altaria v hydreigon | 53/176 | 53/176 | 59/154 | 59/154 | AGREE |
| M2 | table 3, altaria v sceptile | 44/159 | 44/159 | 44/155 | 44/155 | AGREE |
| M2 | table 4, altaria v suicune | 54/162 | 54/162 | 62/135 | 62/135 | AGREE |
| M2 | new_decks.tsv 9, rayquaza v altaria | 62/208 | 62/208 | 64/183 | 64/183 | AGREE |

## What the result means

Both lines' lower bounds are above zero: 0.107 for M1 and 0.039 for M2. So neither line hits a
"cannot pass" rule, and both thresholds stand:

- **T1 = 100263/362752 (27.6%)**, for Arena of Antiquity.
- **T2 = 24383/75980 (32.1%)**, for Training Area.

This check does not hold up the thresholds amendment.

## Other checks the checkers made

- Both confirmed that the two raw files in the working folder are the same as the copies
  committed at 1fc9e0b.
- Both confirmed that each file holds exactly the 14 cells times deals 200-299. On every deal, the
  kta3 row and the km3 row agree on the seed, the seats, who goes first and the deck files.
- Checker b also checked these things:
  - Each seed follows the seed formula.
  - The seats alternate by deal number.
  - No row has played above offered.
- Checker b deliberately left out comparing move fingerprints between the two arms. That would be
  a footprint share, and the text reads nothing else from the sample before the footprint is
  committed.

## What the recorder checked itself

- I re-hashed these files today (sha256). Each hash matches the one the checkers printed:
  - the two raw row files
  - `thresholds.json` (`3bf6a248…efff`)
  - `check_a.py` and `check_b.py`
  - `compare_b.py` (`cd724391…300e`)
- I added up the per-cell counts by hand. They match the pooled counts in all three sources.
- I redid both midpoints by hand as exact fractions:
  - (355/1664 + 37/109)/2 = 100263/362752
  - (127/435 + 275/786)/2 = 24383/75980, which is fully reduced
- I did not re-run either checker's program or the bootstrap.
- I did not open `km_thresholds.py`, `test_km_thresholds.py`, `thresholds.txt` or `STATUS.txt`.

One side note: the task pointed to `score.py` in `scoreboard_v3_2026-09-27/` or
`kpf_2026-09-26/reading/`. Neither folder has a `score.py` with `pct`. Both checkers used the one
the text cites, `rl/results/table_readings_2026-09-24/score.py`.

## Files

- `independent_check_a/check_a.txt`: checker a's numbers, with its comparison added after them.
- `independent_check_b/check_b.txt`: checker b's numbers, with its comparison added after them.
- `thresholds.json`: the file that was checked.

Nothing was committed or built, and no game was played.
