# DRAFT (for the coordinator to review and launch): the exam v2 labelling job

**Launch** (the coordinator, from WSL, its own API credits, after the laptop says the inputs are staged):

    cd /home/dacz8976/exam_v2 && claude -p "$(cat /home/dacz8976/exam_v2/jobs/LABEL_JOB_PROMPT.txt)" --max-budget-usd 15 --output-format text > label_out/job.log 2>&1

The laptop stages, before launch (copies; the job sees nothing else):
- `/home/dacz8976/exam_v2/label_in/positions.json`: run 3's built positions. Each carries `force`, his recorded whole turn in engine labels.
- `legal.jsonl`: the engine's legal list at each step of his line.
- `selection.json`: point id, game, turn, and the review file.
- `sources/<game>/REVIEW.md`, with `UNCERTAINTIES.json` and `LADDER_ENTRY.json`: the accepted reviews, a hash-checked snapshot.
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
  - /home/dacz8976/exam/, ~/exam_run1/, ~/exam_run2/, the agent mailbox, any references.json;
  - anything under rl/results/pause_games* or rl/results/next_pilot_2026-10/.
  - You must label without seeing how any bot or judge played these or other exam positions.
- Look cards up with lib/card.py, never from memory.
- **Budget:** $15. Be careful: these labels are the exam's answer key.

## The job: label exam v2's points by ADJUDICATION_RULES.md, exactly
Read `label_in/ADJUDICATION_RULES.md` first. Its section 2 is your job; section 3 is done later by the assembly, so don't do it.

**For each point** in `label_in/positions.json` (its review is in `label_in/sources/<game>/REVIEW.md`, the turn in `selection.json`; his deck list is in `label_in/decks/`):
- `his_move`: exactly the point's `force`.
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
