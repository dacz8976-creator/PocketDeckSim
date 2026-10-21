# DRAFT (for the coordinator to review and launch): the exam v2 independent selection check

**Launch** (the coordinator, its own API credits, after the build and the labels, before any bot or judge runs):

    cd /home/dacz8976/exam_v2 && claude -p "$(cat /home/dacz8976/exam_v2/jobs/SELCHECK_JOB_PROMPT.txt)" --max-budget-usd 10 --output-format text > selcheck_out/job.log 2>&1

The laptop stages, before launch:
- `/home/dacz8976/exam_v2/selcheck_in/`:
  - `PREREG_RUN3.md`: sections 1-2, the window and the point rules, and addendum 1.
  - `INV_BRIEF.md` and `A_BRIEF.md`: v1.6's usability rules, and stage 3's building rules. Stage 2's quotas are NOT applied.
  - `window.json`: every recording in the window's time span found in the review index (`BATTLE_REVIEW_INDEX.csv`, copied) and the Evidence batches. Each comes with its status: in, or excluded with the reason.
  - `inventory.json`: every turn of every in-window game, with board_known / hand_known / move_known / real_choice, its kind, and a reason when it isn't usable.
  - `selection.json`: every usable turn, and the points built or dropped at build with their reason.
  - `sources/<game>/REVIEW.md`: the hash-checked snapshot.
  - `labels_summary.json`: each point's answer kind and deck, and whether its accepted line ends at a chance action. Counts only, no answers.
  - `run2_mix.json`: run 2's AGGREGATE mix only:
    - points by deck (13-A 23, deck 12 14, Kingambit 12);
    - points by kind (prepare 22, attack now 22, sacrifice 5);
    - chance-ending points 33 of 49;
    - 49 points from 26 games;
    - scope full 19 / partial 9 / none 21.
    - No per-point results.

---- the prompt (SELCHECK_JOB_PROMPT.txt) ----

You are an independent checker for Dustin's PocketDeckSim project (Pokémon TCG Pocket, the mobile game; read /mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/RULES_FOR_AGENTS.md first). The coordinator launched you. You have never seen any bot's or judge's results on these exams, and you must not look for them. Never print environment variables or any key.

**Hard rules**
- **Read only:** /home/dacz8976/exam_v2/selcheck_in/ and RULES_FOR_AGENTS.md.
- **Write only** under /home/dacz8976/exam_v2/selcheck_out/.
- No git, no cargo, no subagents, no bot, no judge.
- **Never open:**
  - rl/results/weekly_review_2026-10-18/, rl/ai_judge/, ~/exam/, ~/exam_run1/, ~/exam_run2/;
  - the agent mailbox, or any references or labels file other than labels_summary.json.
- **Budget:** $10.

## The job: did the build apply the pre-registered rules to EVERY game in the window, with no picking?
1. **The window** (PREREG_RUN3.md section 1). Check each recording in `window.json`:
   - is it in the time span (UTC start times)?
   - is it ranked (not a computer/Auto battle, a rules test or a pause game)?
   - is it new (not an exam v1.6 game)?
   - is any exclusion one of the written reasons (no usable full review, no exact deck list, developer exposure) and true?

   Report any in-span ranked game missing from the build, and any exclusion that doesn't hold.
2. **The usability coding** (INV_BRIEF.md). For every in-window game, read its REVIEW.md and check each turn's coding in `inventory.json`:
   - board_known, hand_known, move_known, real_choice, all as the brief defines them;
   - "partly" and "unclear" are NOT usable.

   Report every turn you would code differently and why. Report separately the turns coded usable that you think aren't, and the reverse.
3. **No picking.** Every usable turn must be a point, or dropped at build with a reason that fits A_BRIEF stage 3 (it can't be built cleanly: an illegal recorded action, a list mismatch, an unreconstructable board or hand). Report any usable turn missing without such a reason, and any point that isn't a usable turn.
4. **The mix**, next to run 2's (`run2_mix.json`):
   - points by deck and by answer kind;
   - the share of chance-ending points;
   - points per game;
   - the scope split if `labels_summary.json` has it.

   Describe the differences in plain words. They are not a reason to change the selection.

Write `selcheck_out/SELECTION_CHECK.md` and `selcheck_out/selection_check.json`:

    {"window_problems": [...], "coding_disagreements": [{"game", "turn", "field", "coded", "yours", "why"}],
     "picking_problems": [...], "mix": {...}, "verdict": "clean" | "fix_first", "summary": "..."}

`fix_first` means at least one window or picking problem, or a coding disagreement that changes whether a turn is usable. Finish by printing the verdict and the counts.
