# DRAFT (for the coordinator to review and launch): the exam v2 labelling job

**Launch checklist** (the coordinator ticks every line before launching; addendum 5, G5 and G6):
- [ ] `positions.json` is written from `build/v2_helpers.label_view`, which refuses `notes`, `approximate_reason`, `kind`, `_draws` and `_vpatch`; a check of the staged file finds none of them.
- [ ] Every linked battle is ONE folder in `sources/`, with its clips in order and `CLIPS.json`.
- [ ] The prompt below contains the shared "Turns and ids" rule: one global turn count for every game, never restarting in a later clip.

**Launch** (the coordinator, from WSL, its own API credits, after the laptop says the inputs are staged):

    cd /home/dacz8976/exam_v2 && claude -p "$(cat /home/dacz8976/exam_v2/jobs/LABEL_JOB_PROMPT.txt)" --max-budget-usd 15 --output-format text > label_out/job.log 2>&1

The laptop stages, before launch (copies; the job sees nothing else):
- `/home/dacz8976/exam_v2/label_in/positions.json`: run 3's positions as `build/v2_helpers.label_view` gives them: the candidate view plus `his_move` (his recorded whole turn in engine labels). The builder's `notes`, `approximate_reason` and `kind` are never staged; the builder has seen run 2's per-point results (PREREG_RUN3 addendum 5, G5).
- `legal.jsonl`: the engine's legal list at each step of his line.
- `selection.json`: point id, game, global turn count, the clip the turn is in, and the review file.
- `sources/<game>/REVIEW.md`, with `UNCERTAINTIES.json` and `LADDER_ENTRY.json`: the accepted reviews, a hash-checked snapshot.
  - ONE folder per game. A battle recorded in several clips (PREREG_RUN3 addendum 4) has its clips in order (`clip01_<packet>/REVIEW.md`, `clip02_<packet>/REVIEW.md`, ...) and `CLIPS.json`.
  - Point ids are `LAD-<game id>-t<n>`, where n is the game's ONE global turn count. It continues across clips and never restarts, so ids can't collide or mis-order (advisor finding F6, Oct 23).
- `decks/*.txt`: his exact lists, from the QR payloads.
- `ADJUDICATION_RULES.md`.

---- the prompt (LABEL_JOB_PROMPT.txt) ----

You are a credit-billed worker for Dustin's PocketDeckSim project (Pokémon TCG Pocket, the mobile game; read /mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/RULES_FOR_AGENTS.md first, because Pocket is not the physical TCG). The coordinator launched you. Never print environment variables or any key.

**Hard rules**
- **Read only:**
  - /home/dacz8976/exam_v2/label_in/;
  - RULES_FOR_AGENTS.md (path above);
  - card text, through `python3 lib/card.py <name or id>` run in /home/dacz8976/pincand.
- **Write only** under /home/dacz8976/exam_v2/label_out/.
- No git, no cargo, no subagents. Never run pg_pos, a bot or any judge.
- **Never open:**
  - anything under rl/results/weekly_review_2026-10-18/ (the earlier exam, its runs and results) or rl/ai_judge/;
  - /home/dacz8976/exam/, ~/exam_run1/, ~/exam_run2/, any other folder of /home/dacz8976/exam_v2/, the agent mailbox, any references.json;
  - anything under rl/results/pause_games* or rl/results/next_pilot_2026-10/.
  - You must label without seeing how any bot or judge played these or other exam positions.
- Look cards up with lib/card.py, never from memory.
- **Budget:** $15. Be careful: these labels are the exam's answer key.

## The job: label exam v2's points by ADJUDICATION_RULES.md, exactly
Read `label_in/ADJUDICATION_RULES.md` first. Its section 2 is your job; section 3 is done later by the assembly, so don't do it.

**Turns and ids.** Every game's turns carry ONE global turn count: the game's own turn counter, both players' turns (as v1.6's `source.global_turn`).
- A game whose folder holds `clip01_…`, `clip02_…` and so on is ONE battle recorded in several clips: read the clips in order as one game. Its count continues across clips and never restarts.
- Every point is named by its id `LAD-<game id>-t<global turn count>`.

**For each point** in `label_in/positions.json`:
- **Where to read:** its review is in `label_in/sources/<game>/REVIEW.md`. For a battle in several clips, read the clip `selection.json` names, together with the clips before it.
- **Its turn** is in `selection.json`, counted globally.
- **His deck list** is in `label_in/decks/`.

For each point, give:
- `his_move`: exactly the point's `his_move`.
- `acceptable`: `[{"line": [labels], "reason": "..."}]`, by the rules' section 2.
  - Only genuinely comparable whole turns that a strong player with the same plan could choose. None is fine.
  - The first action of each line must be in that point's legal list (`legal.jsonl`).
- `answer_kind`: prepare, sacrifice, attack now or abandon.
- `ambiguous`: null, or ONE plain question for Dustin (at most 6 in the whole exam). If you list an alternative you're unsure of, put it in `pending_alternatives` with the question; it won't count until he answers.
- `why_his`: one line.

**For each deck** in `label_in/decks/`: `deck_kinds` (several allowed) with a one-line reason each, from the list and the card text.

Write `label_out/labels.json`:

    {"format": "pds-exam-v2-labels",
     "points": {"<point id>": {"his_move": [...], "acceptable": [...], "pending_alternatives": [...],
                                "answer_kind": "...", "ambiguous": null | "...", "why_his": "..."}},
     "decks": {"<deck key>": {"deck_kinds": [...], "why": {"<kind>": "..."}}}}

Also write `label_out/LABELS.md`: in plain words, the counts by answer kind and deck, every ambiguous question (point id and the question), and anything you couldn't label and why.

Finish by printing the counts and the questions.
