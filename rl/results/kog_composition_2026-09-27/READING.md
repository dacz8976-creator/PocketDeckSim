# kog's composition check: PASSES (Sept 28, laptop)

kog = kp3 + koa's opening switch A + kpg's discard-Energy credit F, built by the cloud at a823b6d. It is read here by `READING_PLAN.md`, which was committed before any laptop game (1cf69db). The numbers are in `READING_numbers.txt`, from `read_kog.py`.

| Item (RUN5 "Composing candidates into one pilot") | Result |
|---|---|
| 1. Identity | The laptop's kog3 table equals the cloud's, **14,000 of 14,000** games (moves, choices, openings, result). k3 and kp3 equal the official references, 1,120 of 1,120 each. |
| 2. One table on the 45 cells, against kp3 | real error **15.5 → 14.0**; ΔMSE −43.1 (95% −62.3 to −25.3); τ̂ margin +1.46 (90% +0.84 to +1.71); rule v2 reads "adopt" |
| 3. No veto | **none**, no cell or deck veto, with kog3's mixed rows on all 45 cells |
| 4. Accuracy no worse than the better component (kpg3) | margin (kpg3 minus kog3) **−0.01**, 90% −0.16 to +0.14; the bound is −1.0, so it **passes** |

- **Against koa3,** reported: +1.47 (+0.88 to +1.70). kog carries kpg's accuracy gain, and koa's part neither adds nor costs accuracy, as its own reading found.
- **Where the parts meet** (first-named deck's score):
  - Altaria v Blaziken: kp3 58.0, koa3 59.2, kpg3 57.4, kog3 58.6.
  - Rayquaza v Altaria: kp3 35.4, koa3 34.4, kpg3 36.0, kog3 35.4.
  - Each sits where its two parts together predict. Nothing is out of line.
- **Not part of this check,** as the plan fixed: B2e and the coverage decks. Each component's own held-out and coverage readings stand.

## What follows

- **kog becomes the working pilot for the table and the screen together, "unconfirmed"** until the post-freeze read. It joins that pull's list (`../postfreeze_2026-09-27/README.md`) as the pilot-level check, beside kpg's and koa's own.
- **Its baselines are these runs:** `table_kog3`, `new17_kog3`, and the mixed rows against kp3.
- **kph is not run.** The cloud builds `koh` = kog + R′. The laptop reads it against kog3 on the 45 cells: the same registered reading, with the base changed as registration section 2 allows.
- **kt is re-issued on kog** (its registration names kp3).
- **For the screen to use kog,** the official engine has to carry kog's code. The official engine is main-83e17ae and kog is only on the cloud branch.
  - The step is a merge of the branch into main, then a new pinned engine by RUN5's switch procedure.
  - k3 and kp3 already replay 14,000 of 14,000 at a823b6d, on the cloud and here, so no table game changes.
  - Until then the screen stays on kp3. This is Dustin's go-ahead.
