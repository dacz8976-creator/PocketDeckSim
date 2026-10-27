# Gemini video trial, Oct 27, 2026

Dustin asked whether Gemini (Gemini 4 Argon on Vertex AI, paid from his Google credits) could read his ranked-game recordings. The trial capped spend at $10, and he agreed to send these three videos to Google. It used the same three games as the Oct 25-26 Claude v Codex trial (`../results/`), where the facts had already been settled from the frames:
- g1 = ScreenRecording_10-24-2026 15-29-43, 12 turns, 362 s;
- g2 = 12-51-31, 6 turns, 251 s;
- g3 = 13-24-53, 15 turns, 510 s.

Codex had tried Gemini on battle videos before Argon came out. Dustin says it "wasn't very reliable" and they abandoned it.

## How it ran
- **`encode.sh`** shrinks each recording to about 10 MB (540 px wide, 5 fps, no audio, same timeline). That fits one inline request.
- **`gemini_video.py`** makes one generateContent call per pass.
  - countTokens runs first and is free.
  - A hard ledger cap of $10 reserves each call's worst case at $4/$20 per M tokens. The actual cost is settled at $2/$10, the price through Nov 30, with thinking billed as output.
- **Three passes:**
  - **field:** `FIELD_VIDEO.md`, 1 fps, default media resolution. Only the opponent sheet.
  - **review:** `REVIEW_VIDEO.md`, the Oct 25 review brief adapted to video. 2 fps, media resolution HIGH. The full turn-by-turn record, the opponent sheet and the uncertainties.
  - **review_default:** the same review brief at 2 fps with the default media resolution, the cheaper setting.
- **Scoring:** a Sonnet scorer per run, using `BRIEF_SCORE.md`.
  - It compared Gemini's review with the checked Claude final (g1 `out_check`, g2 `arm_s`, g3 `ch_s`).
  - It settled every disagreement from full-resolution frames, using `compare.json` and `CHECK_NOTES.md` where they already covered it.
  - The coordinator spot-checked g3's turn-1 Poké Ball call on the frames. It holds: two Poké Balls, at 19:51 and 19:46.

## Results

| Game | Pass | Cost | Seconds | Major | Minor | Gemini right where the checked final was wrong | Opponent sheet |
|---|---|---|---|---|---|---|---|
| g1 | review (HIGH) | $0.61 | 291 | 0 | 2 | 2 | 11/12 |
| g2 | review (HIGH) | $0.39 | 157 | 2 | 0 | 3 | 12/12 |
| g3 | review (HIGH) | $0.77 | 275 | 0 | 0 | 6 | 12/12 |
| g1 | review (default) | $0.26 | 397 | 7 | 2 | 1 | 12/12 |
| g2 | review (default) | $0.19 | 154 | 4 | 1 | 2 | 11/12 (the miss settled for Gemini) |
| g3 | review (default) | $0.31 | 213 | 4 | 3 | 3 | 12/12 |
| g1 | field | $0.09 | 61 | | | | 12/12 |
| g2 | field | $0.07 | 63 | | | | 11/12 (misnamed Team Rocket's Master Plan) |
| g3 | field | $0.12 | 74 | | | | 11/12 (dropped 3 Supporters and a Tool shown only as flashes) |

**Total Gemini spend: $2.78 for 9 calls** (`ledger.json`).

**For comparison, the Oct 25-26 Claude first passes:**
- Sonnet whole game: g1 1 major, $0.91; g2 1 major, $0.81.
- Sonnet in 54-s pieces plus a merge: g3 2 majors, $2.41.

Those majors were counted by an Opus check, not by this scorer, so the two columns are close but not identical measures.

**The HIGH review's two g2 majors:**
- an Energy discard on a retreat that didn't happen;
- one of three milled cards named Steel Apron, when those cards can't be read.

**The default-resolution reviews' majors** are mostly card names, Energy targets and HP read from small text.

## What it shows (3 games only)
- **At HIGH media resolution, Gemini's single pass is as accurate as Claude's best first pass, or better,** at a quarter to two thirds of the cost.
  - It was more complete than the checked finals on several facts.
  - About $0.09-0.10 per minute of game at November prices; the price doubles from Dec 1.
- **The default resolution halves the cost but multiplies the major errors.** Use it for opponent sheets only: 3 of 3 were right or settled for Gemini.
- **The 1-fps field pass** is the cheapest at about $0.10 a game. It misses Trainer cards shown only briefly.

Frames and shrunk videos were deleted after scoring. The videos are on Google Drive.
