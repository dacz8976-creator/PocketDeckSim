# DRAFT (proposed, for the coordinator to accept or not): the exam v2 usability-coding job

**Staged Oct 25 in three parts:** see `LAUNCH_2026-10-25.md`. Its launch lines, folders and flags supersede the launch line below; the prompt's rules are unchanged.

**Why a job:** under PREREG_RUN3 section 2, every USABLE turn is a point, so this coding decides the points. v1.6's coding was also a credit job (INV_BRIEF.md). A fresh job keeps the laptop session, which has seen run 2's per-point results, out of that judgment. The selection check (SELCHECK_JOB.md) then re-checks it.

**Launch** (the coordinator, its own API credits, after the window closes and the laptop stages the snapshot):

    cd /home/dacz8976/exam_v2 && claude -p "$(cat /home/dacz8976/exam_v2/jobs/INV_JOB_PROMPT.txt)" --max-budget-usd 8 --output-format text > inv_out/job.log 2>&1

The laptop stages, before launch:
- `/home/dacz8976/exam_v2/inv_in/sources/<game>/`: ONE folder per game, holding each in-window game's accepted, hash-checked REVIEW.md, LEAD_ACCEPTANCE.json, LADDER_ENTRY.json (where present), QR file and UNCERTAINTIES.json.
  - **A battle recorded in several clips is ONE game** (PREREG_RUN3 addendum 4). Its folder holds the clips in order: `clip01_<packet>/`, `clip02_<packet>/`, ..., plus `CLIPS.json`, which lists them in order. The laptop builds `CLIPS.json` from the snapshot's metadata alone (window.json's clip order, packet names and start times), never from a review. The worker records each clip's turn range in `inventory.json`.
  - The game id is the opening clip's.
- `inv_in/window.json`: the in-window games, from PREREG_RUN3 section 1.
- `inv_in/INV_BRIEF.md`: v1.6's brief.

**Launch checklist** (the coordinator ticks every line before launching; advisor finding F6, Oct 23):
- [ ] The snapshot is staged, and its hashes are checked against the snapshot record.
- [ ] Every linked battle is ONE folder, with its clips in order and `CLIPS.json`.
- [ ] The prompt below contains the shared "Turns and ids" rule: one GLOBAL turn count for every game, never restarting in a later clip; each turn's clip and each clip's turn range.
- [ ] The prompt below contains E7's gap rule (PREREG_RUN3 addendum 4, E7): a turn right after a gap is usable only if the full state there, turn effects included, is established.

---- the prompt (INV_JOB_PROMPT.txt) ----

You are a credit-billed worker for Dustin's PocketDeckSim project (Pokémon TCG Pocket, the mobile game; read /mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/RULES_FOR_AGENTS.md first). The coordinator launched you. Never print environment variables or any key.

**Hard rules**
- **Read only:** /home/dacz8976/exam_v2/inv_in/ and RULES_FOR_AGENTS.md. Text files only, never images or videos.
- **Write only** under /home/dacz8976/exam_v2/inv_out/.
- No git, no cargo, no subagents, no bot, no judge.
- **Never open:** rl/results/weekly_review_2026-10-18/, rl/ai_judge/, ~/exam/, ~/exam_run1/, ~/exam_run2/, any other folder of /home/dacz8976/exam_v2/, the agent mailbox.
- **Budget:** $8.

## The job
Do exactly what `inv_in/INV_BRIEF.md` says ("For each game" and "Output"), for every game in `inv_in/window.json`, from `inv_in/sources/<game>/`.
- **Where the brief names other files,** use these instead:
  - take acceptance and ranked eligibility from LEAD_ACCEPTANCE.json, not from FINDINGS.json, which can carry stale "candidate" fields;
  - take the result from LADDER_ENTRY.json, or from the review where there isn't one;
  - take his deck from the QR file's card list.
- **A turn is USABLE** only when board_known, hand_known and move_known are all "yes" and real_choice is "yes". "Partly" and "unclear" are not usable. The near-usable count is reported but never used.
- **Turns and ids.** Every game's turns carry ONE global turn count: the game's own turn counter, both players' turns (as v1.6's `source.global_turn`).
  - A game whose folder holds `clip01_…`, `clip02_…` and so on is ONE battle recorded in several clips: read the clips in order as one game. Its count continues across clips and never restarts.
  - Every turn is named by its point id `LAD-<game id>-t<global turn count>`.
  - For a game in several clips, give each turn's clip, and each clip's first and last global turn (clips in `CLIPS.json`'s order).
- **After a gap** in a review (it misses turns, at a clip boundary or inside a clip; PREREG_RUN3 addendum 4, E7): a turn right after the gap is usable only if the FULL state at that turn is established from the review.
  - That means the board, the hand, both discards, the points, and every effect still running from earlier turns: a Supporter already played this turn, Energy already attached, a retreat already used, and lasting attack and Ability effects.
  - If any of it is not established, the turn is not usable, with the reason "after a gap: <what is missing>".
- **For every turn that isn't usable,** give the reason in one line.
- **Don't choose points, rank turns or prefer any kind of turn:** every usable turn will become a point.

Write `inv_out/inventory.json`. It holds one object per game:
- the game id;
- its clips in order, with each clip's first and last global turn, if there is more than one;
- the deck and the result;
- every one of his turns, with its point id, global turn count, clip, the four fields, kind, one line, and the reason when it isn't usable.

Also write and `inv_out/INVENTORY.md` (the counts per game, deck and kind, and the five most common reasons a turn isn't usable). Finish by printing the counts.
