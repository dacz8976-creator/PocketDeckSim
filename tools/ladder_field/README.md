# Ladder Field

Who Dustin meets on the ranked ladder. It covers the opponent deck types (by the Pokémon each deck is built around), their Energy types and plans, and his record against each. The results are shown on the Ladder Field dashboard: https://claude.ai/artifact/8ZWYkbZtCga9R9g4Ge3P1x

Built Oct 25, 2026, on Dustin's request, verbatim: "Are we keeping track of the kind of decks I face on the ladder? Do we have a way to classify frameworks or schemas of decks? ... What about the ability to tell me percentages of energy types I saw in ladder play?" He added: "Having the tool built could be useful in the future as well."

## Where the data comes from
- **The Ladder Log** (https://claude.ai/artifact/GHSfGSCzNiWNj8SFPXV3R1, db collection `logs`, one doc per deck id) lists every ranked game: the deck, the time, the result, the opponent's Pokémon as text, and a note.
- **Codex's video reviews** (`REVIEW.md`, plus `SUMMARY.json` and `LADDER_ENTRY.json` when present) give the detail. They're listed in `BATTLE_REVIEW_INDEX.csv`, column `Review evidence`. Games link to their reviews through the recording filenames in the Ladder Log note.
- **The engine's card database** (`engine/database.json`) gives Pokémon types. These are used only to infer Energy for games with no review, or a review that names no opponent Energy.

## The pipeline
1. **Pull the Ladder Log.** Use `ArtifactData` `list` on the Ladder Log, collection `logs`, with `out_dir` → `ladder_log/logs/*.json`. It's the only step that needs a Claude session; a page's db can't be read from a script.
2. `python make_games.py ladder_log/logs BATTLE_REVIEW_INDEX.csv games.json` gives one entry per game, with its review paths.
3. `python make_batches.py .` splits the reviewed games into `extract/batch_k.json` (5 parts; edit k for a different count).
4. **Extract.** One job per batch follows `EXTRACT_BRIEF.md` and writes `extract/out_k.jsonl`.
   - **On refresh, only new games need extracting.** Keep the old `out_*.jsonl` files and put only the games missing from them into a new batch. `ladder_field.py` prints any reviewed game without a record as "missing extraction".
   - Any Claude session can run a batch, as a subagent on the subscription. So can the API credit worker: `claude -p` with the brief, about 30 games per job.
5. `python ladder_field.py games.json extract database.json ladder_field_rows.json` writes the rows. It prints counts by season, Energy, plan and top deck types to sanity-check.
6. **Publish to the dashboard:**
   - upload `ladder_field_rows.json` as an asset (Artifact `publish`, `asset: true`, the dashboard's url);
   - then `ArtifactData` `update` `datasets/games` with the new `url`, `name` and `updated: {at, by}`.
   - The page (`dashboard/index.html`, stored in the dashboard as `files/index.html`) needs no change.

## Rules the extraction follows (EXTRACT_BRIEF.md)
- Only what the game showed. No cards are guessed from an archetype.
- The opponent's Energy is what they attached, or what their Energy Zone showed. Otherwise it's inferred from Pokémon types and marked `inferred`.
- The plan is one of: basic attackers, evolution setup, status and control, Bench damage, healing and walls, or unclear.
- No opponent player names go into the rows.

## Seasons
`ladder_field.py` `SEASONS`:
- before Oct 14 (06:00Z);
- the B4b season;
- Dual Fusion, from its release, Oct 29 01:00Z (Wed Oct 28, 8 PM CT).

Add a line there when a new season starts.

## Known limits
- **Small samples.** One game in 124 is 0.8 percentage points.
- **A deck type is labelled by its main attacker,** so different builds around one Pokémon share a row.
- **September has 32 games with no video review.** For those, Energy is inferred and the plan is Unclear.
