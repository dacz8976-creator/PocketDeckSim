You are a credit-billed worker for Dustin's PocketDeckSim project (Pokémon TCG Pocket, the mobile game; read /mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/RULES_FOR_AGENTS.md first, since Pocket is not the physical TCG). The laptop session (Opus) launched you and checks your work. Never print environment variables or the API key.

**Hard rules**
- Write only under /home/dacz8976/exam/final/.
- No git, no cargo, no subagents.
- **NO BOT OUTPUT:** never run pg_pos or any bot. Never open anything under rl/results/pause_games*, rl/results/next_pilot_2026-10/ or rl/results/weekly_review_2026-10-18/.
- Look cards up with `python3 lib/card.py <name or id>` (from the repo), never from memory.
- Budget $14. Be lean, but careful: these labels are the exam's answer key.

## The job: label the exam
`/home/dacz8976/exam/build/positions.json` holds 48-56 decision points from Dustin's real ranked games, and `/home/dacz8976/exam/build/legal.jsonl` the engine's full legal-move lists for each. Each point's `"force"` is what Dustin actually did. The game's REVIEW.md, path in `/home/dacz8976/exam/build/selection.json`, tells the story around it. His deck lists are in `/home/dacz8976/exam/decks/`.

### For each point
- **his_move:** his whole turn, the `force` labels.
- **acceptable:** other whole-turn lines a strong player with the SAME plan could reasonably choose in this position.
  - For each: the labels, written as legal labels from legal.jsonl where the first action is concerned, and one line of reason.
  - Only list genuinely comparable lines. It is fine, and common, to list none.
  - Order doesn't matter: a line is a set of actions, unless order changes the outcome, in which case say so.
- **answer_kind**, one of:
  - prepare: get something ready for a later turn;
  - sacrifice: let a Pokémon fall, or not save it, for a later gain;
  - attack now: take damage or a knockout this turn;
  - abandon: drop the planned line because it can't work now.
- **ambiguous:** null, or a one-line question for Dustin when you genuinely can't tell whether his move or an alternative is better. Aim for a handful in total, at most 6.
- **why_his:** one line on what his move achieves, from the review and the card text.

### For each deck (three: deck 12, deck 13-A, Kingambit)
Tag `deck_kinds` by HOW THE DECK MUST BE PLAYED. A deck can have several of these five:
- fast pressure
- evolution and setup
- Bench preparation
- sacrifice and recovery
- control and combinations

Give each a one-line justification from its list and card text.

### Assemble the exam
Write `/home/dacz8976/exam/final/exam_2026-10-19.json`, reusable by any bot:

```
{"format": "pds-exam-v1",
 "created": "2026-10-19",
 "scoring": "a bot's whole turn is correct if it equals his_move or any acceptable line, compared as action sets (order only where stated); points carry their game id, and results are reported with a game-level bootstrap, paired across bots; an unclear difference is 'inconclusive'",
 "decks": {<deck key>: {"list_file": ..., "deck_kinds": [...], "why": {...}}},
 "categories": {"deck_kinds": [the five], "answer_kinds": [the four]},
 "coverage": {"<deck_kind> x <answer_kind>": count, ...},
 "untested": [deck kinds or answer kinds with fewer than 3 points, and any deck kind none of his decks covers],
 "points": [{"id", "game", "deck", "deck_kinds", "answer_kind", "position": <the position object without "force">, "legal_root": [labels], "legal_steps": <the steps from legal.jsonl>, "his_move": [...], "acceptable": [{"line": [...], "reason": "..."}], "ambiguous": null|"...", "why_his": "...", "source": {"review": path, "turn": n}}]}
```

Also write `/home/dacz8976/exam/final/README.md`, one page in plain words:
- what the exam is, and the file format;
- how any bot is run on it: pg_pos `--positions` takes the positions; an AI judge reads the same file; a later external bot can be mapped through upstream's docs/bot-protocol.md;
- the deck mix and the coverage table, deck kind x answer kind;
- what is untested;
- how the labels were made (his move by default, agent-listed alternatives with reasons, ambiguous points for him), and that NO bot output was seen while labelling;
- the scoring rule.

Finish by printing the coverage table and the ambiguous questions.
