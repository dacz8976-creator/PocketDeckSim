# Exam v2 (run 3): the selection check's Part B as staged, and its launch (Oct 25, 2026)

Staged by the laptop session from the assembly after note 044's fixes (PREREG_RUN3 addendum 8, K12). The coordinator reviews this record and launches the jobs. Where it differs from `SELCHECK_JOB.md`'s Part B launch line, this record rules.

## Six jobs instead of one (for the coordinator to accept)
One session cannot read 258 points' free-text facts beside about 1 MB of reviews. So Part B runs as:
- **The main job:** items 1-4 (the window, the two codings, no picking, the mix).
  - In `~/exam_v2/selcheck_in/`: `PREREG_EXCERPT.md`, `INV_BRIEF.md`, `A_BRIEF.md`, `window.json`, `BATTLE_REVIEW_INDEX.csv`, `inventory.json`, `coding.json`, `selection.json`, `build_drops/`, `lister_drops/`, `labels_summary.json`, `run2_mix.json`, the reviews of the two games with a build drop (`sources/`), `RULES_FOR_AGENTS.md` and `FILES.txt`.
  - Part A reported no turn-list problem, so the reviews of other games aren't needed there.
- **Five facts jobs:** item 5, one per labelling part.
  - In `~/exam_v2/selcheck_facts_in_p<k>/`: `position_facts.json` (only the free-text fact fields), the part's games' reviews, `FACTS_RULES.md` (G5 and G13 item 6, verbatim), `RULES_FOR_AGENTS.md` and `FILES.txt`.
- **Departures from the spec's file list** (for the coordinator to tick):
  - **The excerpt** adds addendum 6's H2-H4 (the window as closed) and addendum 8's K1 (how G3 was read).
  - **`agreement.json`,** which K1 names, is not staged; the main prompt says so.
  - **`FACTS_RULES.md`** is new.
  - **`lister_drops/`** files give only the problem types and step counts, and say "not dropped: resolved by R1". All three are such points.
- **ONE SENTENCE NEEDS YOUR APPROVAL.** The facts prompts narrow item 5 for printing notes:
  > A note of which card printing was chosen, among the printings that match the facts the review shows, is the builder's record of a choice the review can't settle: flag the choice of printing itself only if it hints at his move or judges a play. Check every fact such a note cites (a name, an HP, an attack or Ability title) and every other statement in it against the review, at or before the point's turn, by the three tests above.

  **Why:** 251 of 258 points carry such notes, and under the literal third test ("says more than the review states") every one would be flagged, which would tell nothing. The cited facts are still checked.
  **If you don't approve,** delete that paragraph from the five prompts before launch. Their hashes are in the staging record.

## The merge rule (decided before launch)
- **Part B's verdict is `fix_first`** when any of these holds:
  - the main job's verdict is `fix_first`;
  - any facts job lists a flag;
  - any facts job's `checked` is not exactly its `position_facts.json` point ids;
  - any job does not finish.
- **The merged report** lists every flag with its part. Coding disagreements are reported, not fixed (G3).

## Confinement and launch (the same flags as the other jobs)
- **Main job:**

      cd /home/dacz8976/exam_v2/selcheck_in && claude -p "$(cat /home/dacz8976/exam_v2/jobs/SELCHECK_JOB_PROMPT.txt)" --bare --restricted --strict-mcp-config --add-dir /home/dacz8976/exam_v2/selcheck_out --permission-mode acceptEdits --model claude-sonnet-5-5 --max-budget-usd 10 --output-format text > /home/dacz8976/exam_v2/selcheck_out/job.log 2>&1

- **Facts jobs** (parts 1-5; the same with p1…p5 in the three places):

      cd /home/dacz8976/exam_v2/selcheck_facts_in_p1 && claude -p "$(cat /home/dacz8976/exam_v2/jobs/SELCHECK_FACTS_PROMPT_p1.txt)" --bare --restricted --strict-mcp-config --add-dir /home/dacz8976/exam_v2/selcheck_facts_out_p1 --permission-mode acceptEdits --model claude-sonnet-5-5 --max-budget-usd 5 --output-format text > /home/dacz8976/exam_v2/selcheck_facts_out_p1/job.log 2>&1

- **Budget:** $10 + 5 × $5 = **$35 at most**, against the spec's $10 for one job.
- **Model:** the laptop suggests claude-sonnet-5-5, as the coders were. The coordinator decides; use one model for all six jobs.
- **Order:** all six may run at once. They read only the selection-check inputs and never the labels.
