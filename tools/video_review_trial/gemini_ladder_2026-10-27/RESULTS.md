# Gemini beside Codex: 10 ranked games (Oct 25-27, 2026)

Dustin, Oct 27: "Yes: run Gemini alongside Codex on my next ~10 ranked games, settle disagreements from the frames, and if it holds up, set it up to fill the Ladder Field. Google credits only."

## Setup
- **Games:** Codex's batch `DRIVE_LADDER_2026-10-27`, 10 games recorded Oct 25-27. Codex had already reviewed them; Gemini read them blind.
- **Gemini 4 Argon on Vertex AI**, two passes per game:
  - full review: 2 fps, HIGH media resolution;
  - cheap pass: the same brief at the default resolution, used only for its opponent sheet.
- **Scoring:** one Sonnet scorer per game compared the two reviews turn by turn. It settled each disagreement from full-resolution frames (1 per second) and graded errors as major or minor. It also checked 12 opponent-sheet fields per sheet against the frames. Brief: `BRIEF_VS_CODEX.md`.

## Rules set before any game
1. Gemini's full review can replace Codex's if its major errors are no more than Codex's.
2. The tracker uses the cheap pass's sheet if it gets at least 95% of fields right, otherwise the full pass's sheet.
3. Report both counts, the cost, and any game where either got the result or the main opponent Pokémon wrong.

## Results
| game | Gemini major/minor | Codex major/minor | disagreements settled: Gemini right / Codex right / unsettled |
|---|---|---|---|
| 10-25 21-13-31 | 2/4 | 3/1 | 4/6/0 |
| 10-25 21-21-11 | 1/0 | 0/2 | 2/1/0 |
| 10-25 21-28-49 | 1/0 | 4/0 | 4/1/1 |
| 10-26 07-07-35 | 0/0 | 0/1 | 1/0/0 |
| 10-26 07-29-50 | 2/1 | 0/1 | 1/3/0 |
| 10-26 07-35-58 | 1/1 | 3/0 | 4/2/0 |
| 10-27 13-48-10 | 1/0 | 0/2 | 2/1/0 |
| 10-27 13-54-47 | 2/0 | 2/1 | 3/2/0 |
| 10-27 14-06-26 | 0/0 | 0/1 | 1/0/0 |
| 10-27 14-11-19 | 0/0 | 1/7 | 8/0/0 |
| **total** | **10/6** | **13/16** | **30/16/1** |

- **Rule 1: PASS.** Gemini had 10 major errors, Codex 13.
  - Gemini's majors are mostly wrong Energy-attachment targets, plus one invented retreat discard and one invented attach.
  - Codex's majors are mostly missed plays: Trainers (Professor's Research, Poké Ball, Rare Candy, Field Blower) and Energy attachments.
- **Rule 2: the cheap sheet** is right on 116 of 120 fields (96.7%).
  - Its 4 misses: 3 wrong or missing side Pokémon (Chingling for Igglybuff, Farfetch'd for Furfrou, missing Mantyke) and 1 Special Condition from the owner's own attack.
  - The full sheet scored 120 of 120; Codex's sheet 118 of 120.
- **Rule 3:** in no game did either review get the result or the main opponent Pokémon wrong.
- **Cost (Google credits):** $8.42 actual over 20 calls, about $0.57 per game for the full review and $0.27 for the cheap pass. The ledger shows $10.60 because it books worst-case holds for one rate-limited call and one stopped call. Argon's price doubles after Nov 30.

## Limits
- Ten games only.
- One scorer per game, not double-checked.
- The scorers read frames at 1 per second.
- Both reviews still make major errors, of different kinds (Gemini mis-targets; Codex omits).
