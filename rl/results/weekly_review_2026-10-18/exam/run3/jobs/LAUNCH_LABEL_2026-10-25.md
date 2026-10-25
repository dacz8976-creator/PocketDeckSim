# Exam v2 (run 3): how the labelling job was staged and is launched (Oct 25, 2026)

Staged by the laptop session after the build (PREREG_RUN3 addendum 8). The coordinator reviews this record and launches the jobs on the credit worker. Where it differs from `LABEL_JOB.md`'s launch line, this record rules. The prompt's rules are LABEL_JOB.md's; only the paths and the lines listed under "The prompts" differ.

## What was staged (`stage_label.py`; record: `LABEL_STAGING_2026-10-25.json` here = `~/exam_v2/LABEL_STAGING.json`)
- **The points:** all 258 built points, minus nothing else; the 3 G1 drops (addendum 8, K2) are left out.
- **Five parts,** each two build batches (whole games, in time order):

  | part | batches | games | points |
  |---|---|---|---|
  | p1 | 1-2 | 17 | 54 |
  | p2 | 3-4 | 13 | 52 |
  | p3 | 5-6 | 14 | 48 |
  | p4 | 7-8 | 16 | 53 |
  | p5 | 9-10 | 16 | 51 |

  v1.6's single labelling job had 51 points, so each part is about v1.6's size.
- **`~/exam_v2/label_in_pk/`** (read-only) holds:
  - `positions.json`: `v2_helpers.label_view`, the candidate view plus `his_move`, with no `notes`, `approximate_reason`, `kind`, `force`, `_draws` or `_vpatch` (checked in the staged file);
  - `legal.jsonl`: pg_legal_v14's legal list at each step of his move;
  - `selection.json`: point id, game, global turn, clip and review file;
  - `sources/<game>/`: REVIEW.md, UNCERTAINTIES.json and LADDER_ENTRY.json, plus the clip folders and CLIPS.json for a linked battle. They are copied from the usability staging, with their hashes checked again;
  - `decks/` and `DECK_KINDS_FOR.txt`;
  - `CARDS.md`: the card text of every card in the part's decks and positions, from the frozen database;
  - `ADJUDICATION_RULES.md`, `RULES_FOR_AGENTS.md` and `FILES.txt`.

## The prompts (`~/exam_v2/jobs/LABEL_JOB_PROMPT_pk.txt`)
They are LABEL_JOB.md's prompt. The differences:
- **Paths:** absolute paths to the part's folders.
- **`FILES.txt`:** the confined worker has no search, listing or shell tool, so the file list is named in the prompt.
- **Card text** comes from `CARDS.md` instead of `lib/card.py`, which the worker can't run.
- **The linked-battle line** (one whole-battle review, read once).
- **The question cap:** "at most 1 in this part". ADJUDICATION_RULES allows at most 6 in the whole exam, and 5 parts × 1 stays within it. **The coordinator may change it.**
- **`deck_kinds`** is asked only for the decks in `DECK_KINDS_FOR.txt`. Each of the 24 decks is in exactly one part, the one holding most of its points, so the parts can't disagree.

## Confinement
The same flags as the coding jobs (`LAUNCH_2026-10-25.md`, smoke-tested): `--bare --restricted --strict-mcp-config`, the cwd is the read-only in-folder, and `--add-dir` is the out-folder.

## The launch lines (the five parts are independent and may run at the same time)

    cd /home/dacz8976/exam_v2/label_in_p1 && claude -p "$(cat /home/dacz8976/exam_v2/jobs/LABEL_JOB_PROMPT_p1.txt)" --bare --restricted --strict-mcp-config --add-dir /home/dacz8976/exam_v2/label_out_p1 --permission-mode acceptEdits --model claude-opus-5-5 --max-budget-usd 15 --output-format text > /home/dacz8976/exam_v2/label_out_p1/job.log 2>&1

Parts 2-5: the same with `p2`…`p5` in the three places.

**For the coordinator to decide:**
- **Model.** The laptop's recommendation is `claude-opus-5-5`, because the labels are the exam's answer key: the acceptable alternatives decide what a bot gets credit for. `claude-sonnet-5-5` is cheaper. Use one model for all five parts.
- **Budget.** $15 per part, LABEL_JOB.md's figure for one job: at most $75 in all.
- **The question cap** (1 per part), as above.

## After the labels (the assembly, mechanical)
- Every accepted line is cut after its Attack, as his line is (frozen-7's rule; addendum 8, K3).
- Then, in order (G2): the lister check on every accepted line, Part B, Dustin's answers, the lister check again, `validate_v2.py`, the freeze.
