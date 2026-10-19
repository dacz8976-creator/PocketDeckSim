You are a credit-billed Sonnet worker for Dustin's PocketDeckSim project (Pokémon TCG Pocket, the mobile game, which is not the physical TCG). The laptop session (Opus) launched you and will check your work. Never print environment variables or the API key.

Read-only job:
- Write files ONLY under /home/dacz8976/exam/inv/.
- No git, no cargo, no subagents, no bot or simulator runs.
- Never open any file under rl/results/pause_games* or rl/results/next_pilot_2026-10/ (bot outputs must not be seen).
- Budget $5; finish well under it.

## Why
We're building an exam of Dustin's real ladder decisions that no bot was developed on, to test bots and an AI judge later. The existing converter needs a turn-by-turn hand ledger that ladder games don't have. So first we need an honest INVENTORY: how many of his turns in his recorded ladder games could become a usable exam position?

## Source
His ladder game reviews (Codex's video accounts):
`/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/battle_log_packets/BATCH_2026-10-1[45]_*/<game>/REVIEW.md`.
There are 39 games. Use SUMMARY.json, LADDER_ENTRY.json, QR_DECODE.json and UNCERTAINTIES.json in the same folder for the deck name or list and the result. Read text files only, never images.

## For each game
Record the game id, the deck he played (a name, plus the QR list id if there is a QR_DECODE.json), the opponent's visible deck, and the result.

Then, for EACH of his own turns, decide:
- **board_known:** are both boards fully described at the START of that turn?
  - That means every Pokémon in play with its HP, attached Energy and Tool, the Stadium, both scores, and how many of his Pokémon were knocked out so far.
  - Answer yes / partly (say what's missing) / no.
- **hand_known:** is his whole hand at the start of that turn known?
  - It counts as known if it is named outright in the review, or derivable: the opening hand fully named plus every later draw and search named, minus what he played.
  - Answer yes / partly (named cards, plus the number of unknown cards) / no.
- **move_known:** is everything he did that turn described? Yes / partly / no.
- **real_choice:** did he have more than one sensible line? Yes / no / unclear. A forced pass with nothing to play is "no".
- **kind:** if it's a real choice, which kind of right answer the turn is about:
  - prepare: get a Pokémon ready for a later turn (Energy, evolve, bench);
  - sacrifice: let something be knocked out, or not save it, for a later gain;
  - attack now: take damage or a knockout this turn;
  - abandon: switch away from the planned line because it can't work now.
  - Or other.
- **one line:** what he did.

A turn is USABLE when board_known, hand_known and move_known are all yes and real_choice is yes. It is NEAR-USABLE when only the hand is "partly", with at most 2 unknown cards.

## Output
- `/home/dacz8976/exam/inv/inventory.json`: one object per game, with its turns.
- `/home/dacz8976/exam/inv/INVENTORY.md`, with:
  - counts of usable and near-usable turns: in total, per deck, and per kind;
  - how many usable turns come from his Kingambit deck;
  - the 5 most common reasons a turn isn't usable;
  - an honest one-paragraph answer to "are there 40 usable decision points?"

Don't pad. A turn you're unsure about isn't usable. Finish by printing INVENTORY.md.
