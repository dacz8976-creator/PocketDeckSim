# DRAFT (for the coordinator to review and launch): the exam v2 independent selection check, in two jobs

Under PREREG_RUN3 addendum 5 (G3), a turn becomes a point ONLY if BOTH the usability job (`INV_JOB.md`) and an independent second coding say it is usable. That second coding must be blind to the first, so the check runs as TWO fresh credit-worker jobs:
- **Part A:** the blind second coding. It sees the reviews and the list of his turns, never the first coding, the selection, the labels or any mix.
- **Part B:** the selection check itself, which also gets Part A's coding.

Both run after the build and the labels and before any bot or judge runs. Neither worker has seen any bot's or judge's results on these exams.

## Part A: the blind second coding

**Launch** (the coordinator, its own API credits):

    cd /home/dacz8976/exam_v2 && claude -p "$(cat /home/dacz8976/exam_v2/jobs/SELCODE_JOB_PROMPT.txt)" --max-budget-usd 8 --output-format text > selcode_out/job.log 2>&1

**The laptop stages, before launch** (`/home/dacz8976/exam_v2/selcode_in/`, nothing else):
- `INV_BRIEF.md`: v1.6's usability rules.
- `RULES_EXCERPT.md`: PREREG_RUN3 section 2's usability lines; addendum 4's E1, E2 and E7; addendum 5's G3 and G6. Nothing else of addendum 5.
- `sources/<game>/`: the same hash-checked snapshot as INV_JOB's. It is ONE folder per game; a battle in several clips has `clip01_…/`, `clip02_…/` in order and `CLIPS.json`.
- `turns.json`: for every in-window game, his turns as `{"point_id": "LAD-<game>-t<global turn>", "game", "global_turn", "clip"}`. It is made mechanically from the first coding with every coded field removed.

**Launch checklist:**
- [ ] `selcode_in/` holds only the four items above. There is no `inventory.json`, `selection.json`, labels file or mix file.
- [ ] `turns.json` carries no coded field (no `*_known`, `real_choice`, `usable`, `kind` or reason), and every point id in it is unique.
- [ ] Every linked battle is ONE folder in `sources/`, with its clips in order and `CLIPS.json`.
- [ ] The prompt below contains the shared "Turns and ids" rule and E7's gap rule, word for word as in INV_JOB.

---- the prompt (SELCODE_JOB_PROMPT.txt) ----

You are an independent coder for Dustin's PocketDeckSim project (Pokémon TCG Pocket, the mobile game; read /mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/RULES_FOR_AGENTS.md first). The coordinator launched you. You have never seen any bot's or judge's results on these exams, and you must not look for them. Never print environment variables or any key.

**Hard rules**
- **Read only:** /home/dacz8976/exam_v2/selcode_in/ and RULES_FOR_AGENTS.md. Text files only, never images or videos.
- **Write only** under /home/dacz8976/exam_v2/selcode_out/.
- No git, no cargo, no subagents, no bot, no judge.
- **Never open:** rl/results/weekly_review_2026-10-18/, rl/ai_judge/, ~/exam/, ~/exam_run1/, ~/exam_run2/, any other folder of /home/dacz8976/exam_v2/, the agent mailbox.
- **Budget:** $8.

## The job: code every one of his turns in `turns.json`, by `INV_BRIEF.md`, from its game's review
- **Turns and ids.** Every game's turns carry ONE global turn count: the game's own turn counter, both players' turns (as v1.6's `source.global_turn`).
  - A game whose folder holds `clip01_…`, `clip02_…` and so on is ONE battle recorded in several clips: read the clips in order as one game. Its count continues across clips and never restarts.
  - Every turn is named by its point id `LAD-<game id>-t<global turn count>`.
  - Use the `point_id`s in `turns.json`. If the review shows one of his turns that `turns.json` lacks, a turn that isn't his, or a wrong number, report it in `turn_list_problems`; don't change the list.
- **For each turn,** give board_known, hand_known, move_known and real_choice ("yes", "partly", "unclear" or "no", as the brief defines them), and `usable`: true only when all four are "yes". "Partly" and "unclear" are not usable.
- **After a gap** in a review (it misses turns, at a clip boundary or inside a clip; PREREG_RUN3 addendum 4, E7): a turn right after the gap is usable only if the FULL state at that turn is established from the review.
  - That means the board, the hand, both discards, the points, and every effect still running from earlier turns: a Supporter already played this turn, Energy already attached, a retreat already used, and lasting attack and Ability effects.
  - If any of it is not established, the turn is not usable, with the reason "after a gap: <what is missing>".
- **For every turn that isn't usable,** give the reason in one line.
- **Don't choose points, rank turns or prefer any kind of turn.**

Write `selcode_out/coding.json`: `{"format": "pds-exam-v2-selcode", "turns": {"<point_id>": {"board_known", "hand_known", "move_known", "real_choice", "usable", "why_not"}}, "turn_list_problems": [{"game", "what", "why"}]}`, with every point_id of `turns.json` exactly once. Finish by printing the counts of usable and not usable turns per game, and the number of turn-list problems.

## Part B: the selection check

**Launch** (the coordinator, its own API credits, after Part A has finished):

    cd /home/dacz8976/exam_v2 && claude -p "$(cat /home/dacz8976/exam_v2/jobs/SELCHECK_JOB_PROMPT.txt)" --max-budget-usd 10 --output-format text > selcheck_out/job.log 2>&1

**The laptop stages, before launch** (`/home/dacz8976/exam_v2/selcheck_in/`):
- `PREREG_EXCERPT.md`, which is:
  - PREREG_RUN3 sections 1-2 and addendum 1;
  - addendum 3's D1-D2 (the exact-list rule and ruling);
  - addendum 4's E1, E2 and E7 (linked battles, partial reviews, gaps);
  - addendum 5's G1, G3, G6, G8 and G9.

  NOT addendum 5's G2 trial paragraph, G7 or G12.
- `INV_BRIEF.md` and `A_BRIEF.md`: v1.6's usability rules, and stage 3's building rules. Stage 2's quotas are NOT applied.
- `window.json`: every recording in the window's time span found in the review index (`BATTLE_REVIEW_INDEX.csv`, copied) and the Evidence batches, with its status (in, or excluded with the reason).
- `inventory.json`: the first coding (the usability job's), every turn of every in-window game, keyed by point id.
- `coding.json`: Part A's blind second coding, keyed by the same point ids.
- `selection.json`: every turn both codings call usable, and the points built or dropped at build with their reason.
- `build_drops/<point id>.txt`: for every point dropped at build, the VERBATIM pg_legal output that forces it.
- `lister_drops/<point id>.txt`: for every point where frozen-7's lister check found a problem, its problem types and step counts (check_lister_v2.py `--drops-out`; no labels).
- `sources/<game>/REVIEW.md`: the hash-checked snapshot, one folder per game, clips in order with `CLIPS.json`.
- `labels_summary.json`: per point, its answer kind, its deck, and how its accepted first segment ends: at a chance action, at an opponent's choice (addendum 5, R1), or at the end of the turn. Counts only; no answers.
- `position_facts.json`: per point id, ONLY the position's free-text fact fields from the candidate view: `opp_ambiguous`, `turn_effects`, `stadium` and each board Pokémon's `effects` (addendum 5, G5; coordinator-038, decision 6). No move, no label.
- `run2_mix.json`: run 2's AGGREGATE mix only:
  - points by deck (13-A 23, deck 12 14, Kingambit 12);
  - points by kind (prepare 22, attack now 22, sacrifice 5);
  - chance-ending points: 33 of 49, counted under v1.6's rule (no opponent's-choice stop);
  - 49 points from 26 games;
  - scope: full 19 / partial 9 / none 21;
  - v1.6's build-time drops: 3 (`../build/BUILD.md`). One was for a list problem; two were "cost judged too high", which addendum 5's G1 no longer allows.
  - No per-point results.

**Launch checklist:**
- [ ] Part A has finished, and `coding.json` names every turn of `turns.json` exactly once.
- [ ] `PREREG_EXCERPT.md` holds exactly the parts listed above.
- [ ] Every linked battle is ONE folder with its clips in order and `CLIPS.json`.
- [ ] The prompt below contains the shared "Turns and ids" rule.

---- the prompt (SELCHECK_JOB_PROMPT.txt) ----

You are an independent checker for Dustin's PocketDeckSim project (Pokémon TCG Pocket, the mobile game; read /mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/RULES_FOR_AGENTS.md first). The coordinator launched you. You have never seen any bot's or judge's results on these exams, and you must not look for them. Never print environment variables or any key.

**Hard rules**
- **Read only:** /home/dacz8976/exam_v2/selcheck_in/ and RULES_FOR_AGENTS.md.
- **Write only** under /home/dacz8976/exam_v2/selcheck_out/.
- No git, no cargo, no subagents, no bot, no judge.
- **Never open:**
  - rl/results/weekly_review_2026-10-18/, rl/ai_judge/, ~/exam/, ~/exam_run1/, ~/exam_run2/, any other folder of /home/dacz8976/exam_v2/;
  - the agent mailbox, or any references or labels file other than labels_summary.json.
- **Budget:** $10.

**Turns and ids.** Every game's turns carry ONE global turn count: the game's own turn counter, both players' turns (as v1.6's `source.global_turn`).
- A game whose folder holds `clip01_…`, `clip02_…` and so on is ONE battle recorded in several clips: read the clips in order as one game. Its count continues across clips and never restarts.
- Every turn is named by its point id `LAD-<game id>-t<global turn count>`, as in `inventory.json` and `coding.json`.

## The job: did the build apply the pre-registered rules to EVERY game in the window, with no picking?
1. **The window** (PREREG_EXCERPT section 1, addenda 3 and 4). Check each recording in `window.json`:
   - is it in the time span (UTC start times)?
   - is it ranked (not a computer/Auto battle, a rules test or a pause game)?
   - is it new (not an exam v1.6 game)?
   - is any exclusion one of the written reasons, and true? The written reasons are:
     - no accepted review whose opening is recorded (addendum 4, E1/E7: an accepted PARTIAL review with a recorded opening counts);
     - no exact deck list (addendum 3, D1-D2; this includes a weak source QR excluded by the coordinator's ruling, addendum 5, G8);
     - developer exposure.
   - is a battle in several clips one game (addendum 4, E1)?

   Report any in-span ranked game missing from the build, and any exclusion that doesn't hold.
2. **The two codings** (INV_BRIEF.md; addendum 5, G3). A turn is a point ONLY if both `inventory.json` and `coding.json` call it usable. That rule settles every disagreement mechanically.
   - Part A's `turn_list_problems` (a turn the first coding's list lacks, has wrongly, or numbers wrongly): check each against the review and report it.
   - Check that `selection.json`'s usable turns are exactly the turns both codings call usable.
   - List every disagreement by point id: field, first coding, second coding.
   - Don't decide any disagreement.
3. **No picking.** Every turn both codings call usable must be a point, or dropped at build ONLY with the verbatim pg_legal output in `build_drops/` that forces it (an illegal recorded action, or a label it can't match), or by frozen-7's lister check with its record in `lister_drops/` (addendum 5, G1). Report:
   - any such turn missing without that evidence;
   - any drop whose evidence doesn't show what forces it;
   - any point that isn't such a turn.
4. **The mix**, next to run 2's (`run2_mix.json`):
   - points by deck and by answer kind;
   - the share ending at a chance action, at an opponent's choice and at the end of the turn. Run 2's 33 of 49 counts chance only, under v1.6's rule;
   - points per game;
   - the build-time drop count;
   - the scope split if `labels_summary.json` has it.

   Describe the differences in plain words. They are not a reason to change the selection.
5. **The free-text facts** (`position_facts.json`; addendum 5, G5). These fields must state facts of the position only, in the review's own terms. Read every point's fields beside its review, and report any wording that:
   - hints at what he did or should do;
   - judges a play;
   - says more than the review states.

   Give the point id, the field and the words. Don't rewrite anything yourself: a flagged text is rewritten to the review's own factual wording, or removed.

Write `selcheck_out/SELECTION_CHECK.md` and `selcheck_out/selection_check.json`:

    {"window_problems": [...],
     "coding_disagreements": [{"point_id", "field", "first", "second"}],
     "turn_list_problems": [...],
     "selection_vs_rule": [...],
     "free_text_flags": [{"point_id", "field", "words", "why"}],
     "picking_problems": [...], "mix": {...}, "verdict": "clean" | "fix_first", "summary": "..."}

`fix_first` means at least one window problem, a confirmed turn-list problem, a selection that doesn't follow the two-codings rule, a picking problem, or a free-text flag. A coding disagreement is not fixed by anyone: the rule settles it. Report it, but don't call it fix_first. Finish by printing the verdict and the counts.
