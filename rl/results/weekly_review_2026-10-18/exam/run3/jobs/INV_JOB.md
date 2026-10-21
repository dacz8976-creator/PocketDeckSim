# DRAFT (proposed, for the coordinator to accept or not): the exam v2 usability-coding job

**Why a job:** under PREREG_RUN3 section 2, every USABLE turn is a point, so this coding decides the points. v1.6's coding was also a credit job (INV_BRIEF.md). A fresh job keeps the laptop session, which has seen run 2's per-point results, out of that judgment. The selection check (SELCHECK_JOB.md) then re-checks it.

**Launch** (the coordinator, its own API credits, after the window closes and the laptop stages the snapshot):

    cd /home/dacz8976/exam_v2 && claude -p "$(cat /home/dacz8976/exam_v2/jobs/INV_JOB_PROMPT.txt)" --max-budget-usd 8 --output-format text > inv_out/job.log 2>&1

The laptop stages, before launch:
- `/home/dacz8976/exam_v2/inv_in/sources/<game>/`: each in-window game's accepted, hash-checked REVIEW.md, LEAD_ACCEPTANCE.json, LADDER_ENTRY.json (where present), QR file and UNCERTAINTIES.json.
- `inv_in/window.json`: the in-window games, from PREREG_RUN3 section 1.
- `inv_in/INV_BRIEF.md`: v1.6's brief.

---- the prompt (INV_JOB_PROMPT.txt) ----

You are a credit-billed worker for Dustin's PocketDeckSim project (Pokémon TCG Pocket, the mobile game; read /mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/RULES_FOR_AGENTS.md first). The coordinator launched you. Never print environment variables or any key.

**Hard rules**
- **Read only:** /home/dacz8976/exam_v2/inv_in/ and RULES_FOR_AGENTS.md. Text files only, never images or videos.
- **Write only** under /home/dacz8976/exam_v2/inv_out/.
- No git, no cargo, no subagents, no bot, no judge.
- **Never open:** rl/results/weekly_review_2026-10-18/, rl/ai_judge/, ~/exam/, ~/exam_run1/, ~/exam_run2/, the agent mailbox.
- **Budget:** $8.

## The job
Do exactly what `inv_in/INV_BRIEF.md` says ("For each game" and "Output"), for every game in `inv_in/window.json`, from `inv_in/sources/<game>/`.
- **Where the brief names other files,** use these instead:
  - take acceptance and ranked eligibility from LEAD_ACCEPTANCE.json, not from FINDINGS.json, which can carry stale "candidate" fields;
  - take the result from LADDER_ENTRY.json, or from the review where there isn't one;
  - take his deck from the QR file's card list.
- **A turn is USABLE** only when board_known, hand_known and move_known are all "yes" and real_choice is "yes". "Partly" and "unclear" are not usable. The near-usable count is reported but never used.
- **For every turn that isn't usable,** give the reason in one line.
- **Don't choose points, rank turns or prefer any kind of turn:** every usable turn will become a point.

Write `inv_out/inventory.json` (one object per game: game id, deck, result, and every one of his turns with the four fields, kind, one line, and the reason when not usable) and `inv_out/INVENTORY.md` (the counts per game, deck and kind, and the five most common reasons a turn isn't usable). Finish by printing the counts.
