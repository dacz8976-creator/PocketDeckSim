# The one-time holdout confirmation of kp3 against k3 (Sept 25)

**Status: opened once, at 2026-09-25T19:49:50Z, on Dustin's "Kp3" in the laptop session's chat. kp3 is confirmed** (`READING.md`).
- Before opening, the only thing read from `matches.csv` was the header and the count of rows per split: 16,089 holdout, 14,127 development.
- `OPENED.txt` holds the time and counts.

**The rule:** `../table_readings_2026-09-24/README.md`, "The holdout confirmation of kp3".
- Conditions (1) to (3) were committed at 10c4e66. Condition (4), size and direction on the holdout alone, was added at e45eb50, and its reporting note at b1740b4, all before opening.
- Kp3 is confirmed only if all four hold. Otherwise kp3 stays the working pilot by Dustin's override, and the next confirmation is on events after the freeze date.

**How it runs** (`run_confirmation.sh`, once):
1. It refuses unless kp3's mixed rows are complete and the holdout hasn't been opened before.
2. `build_holdout.py --open-holdout`:
   - First it rebuilds the development cells from `matches.csv` and checks them against `limitless_v2_dev.json` (safe to run before opening, with `--check-development`).
   - Then it counts the holdout rows exactly as `build_v2.py` counts the development half, and writes the holdout cells, the pooled development + holdout cells, and each one's per-event cells.
3. `score.py --rules v2`, kp3 against k3 paired by deal, with kp3's mixed rows on all 28 pairings:
   - on the holdout alone (conditions 1, 3 and 4);
   - on the pooled cells (condition 2);
   - on the development half with the same mixed rows, for comparison.

**The limit on reuse:**
- The skill-model folder's holdout discipline (`../limitless_skill_model_2026-09-25/README.md` and `split.json`) says the frozen half is used once, for a confirmation.
- This is that use. The pilot it is spent on is Dustin's pick.
