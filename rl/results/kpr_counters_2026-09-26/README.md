Decision this informs: none by itself (kpr3 is not adopted, laptop reading 055f6f0). These are the counters Fable's kpr review asked for (question 5), so the laptop can attribute the kpr3 mixed rows if they are ever re-read. Engine: `engine/src` identical to e09fb46, the kpr table's commit. The legality_scan example as at a03f491 (scan sha256 cd8ca8a7eebfed0a0548ac22719af4d927213aa629b2b5de92a4e05c81e23295).

Seeds: the table's deals only, 72,000,000 + pairing × 10,000 + i, i < 500, even i = first-named deck in seat 0.

# kp3 and kpr3 with the discard-attack and Ability counters (Sept 26)

## What was run and what it shows

- **The runs.** kp3 and kpr3 each played all 14,000 table games with the scan that carries the new counters (`run_counters.sh`; 2,038 s and 3,161 s on 4 threads, `timing.txt`).
- **The counters only watch.** Move fingerprints and results equal the table files in 14,000 of 14,000 games for kp3 (`../public_pricing_2026-09-25/kp3_500_*.jsonl`) and 14,000 of 14,000 for kpr3 (`../kpr_2026-09-25/kpr3_500.jsonl`). This is the one identity replay the review asked for.
- **What each counter records, per game** (jsonl fields; the txt has them per cell):
  - `discard_attacks`: for Mega Burning, Terminating Tail and Diving Icicles, the turns it could be used, split by whether it would knock out the opponent's Active and whether it was used: [KO-able used, KO-able passed, not KO-able used, not KO-able passed]. `hyper_ray` gives the same for Hyper Ray.
  - `abilities`: every activated Ability, [turns offered, turns used], for the deck that has it.
- **`summarize.py`** puts kp3 and kpr3 side by side per cell (`summary.txt`).

## The numbers, all cells (per cell in `summary.txt`)

| counter | kp3 | kpr3 |
|---|---|---|
| Hyper Ray without a knockout, used | 217 of 1,036 (21%) | 1,105 of 1,227 (90%) |
| Hyper Ray with a knockout, passed | 88 of 2,334 | 38 of 2,434 |
| Mega Burning without a knockout, used | 2,086 of 2,270 (92%) | 2,655 of 2,655 (100%) |
| Terminating Tail without a knockout, used | 758 of 804 (94%) | 909 of 909 (100%) |
| Diving Icicles without a knockout, used | 0 of 0 | 2 of 2 |
| Diving Icicles with a knockout, passed | 0 of 344 | 0 of 432 |
| Roar in Unison, used of offered | 4,409 of 6,311 (70%) | 4,773 of 6,571 (73%) |
| Ice Maker, used of offered | 8,069 of 8,995 (90%) | 8,192 of 9,191 (89%) |
| Boiler Smog, used of offered | 3,424 of 3,427 | 3,441 of 3,451 |

- **Hyper Ray per cell** (not KO-able, used): Hydreigon v Lucario 1% → 91%, the chip the laptop's reading leads with. Altaria 5% → 88%; Blaziken 1% → 68%; Sceptile 6% → 97%; Suicune 40% → 95%; Vespiquen 15% → 84%; Weezing 34% → 95%.
- **Knockouts passed in Hydreigon v Vespiquen:** 79 of 353 → 35 of 352 (22.4% → 9.9%), as the kpr README's Sept 26 correction says.
- **Blaziken's Mega Burning and Sceptile's Terminating Tail** go from about 90% to always used when they can't knock out: kpr3 prices the Energy they discard as coming back.
- **Suicune's own counters barely move:** Ice Maker 90% → 89%; Diving Icicles is almost never offered without a knockout, under either bot. So these counters don't explain Suicune's five moved cells by themselves. That attribution stays with the mixed rows and the Suicune opponents' own counters (Roar in Unison in Hydreigon v Suicune 66% → 72%, Hyper Ray 40% → 95%).

## Files

- `run_counters.sh`: the command. `timing.txt`: wall times.
- `kp3_500_counters.{jsonl,txt}`, `kpr3_500_counters.{jsonl,txt}`: the raw outputs.
- `summarize.py`, `summary.txt`: the side-by-side table.
- **If the kpr3 mixed rows are re-read:** the counters are in every later build of the scan, including the repaired engine of `../rules09_fixes_2026-09-26/`. That engine changes some table games, so rows re-run there are not paired with the Sept 25-26 rows.
