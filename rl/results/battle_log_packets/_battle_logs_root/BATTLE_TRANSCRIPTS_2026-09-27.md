# Battle video transcripts, 2026-09-27

| Recording | Result | Review |
| --- | --- | --- |
| `20260927_170847000_iOS.MP4` | Complete 16-turn battle; Dacz8976 wins 3–1 after Terapagos ex knocks out Herdier | [Time-coded turn account](Recording_QA/20260927_170847_sol/REVIEW.md), [coverage](Recording_QA/20260927_170847_sol/COVERAGE.md), [source identity](Recording_QA/20260927_170847_sol/SOURCE.json) |
| `20260927_205715000_iOS.MP4` | Complete 4-turn battle; locura concedes at 0–0, followed by a visible Victory screen | [Time-coded turn account](Recording_QA/20260927_205715_sol/REVIEW.md), [coverage](Recording_QA/20260927_205715_sol/COVERAGE.md), [source identity](Recording_QA/20260927_205715_sol/SOURCE.json) |
| `20260927_205926000_iOS.MP4` | Separate complete 13-turn battle; 阿修羅 concedes at 2–2 during turn 13 | [Time-coded turn account](Recording_QA/20260927_205926_sol/REVIEW.md), [coverage](Recording_QA/20260927_205926_sol/COVERAGE.md), [source identity](Recording_QA/20260927_205926_sol/SOURCE.json), [independent Astra timeline check](Recording_QA/20260927_205926_astra_timeline/RECONCILIATION.md) |
| `20260927_211210000_iOS.MP4` | Separate complete 11-turn battle; KSH concedes at 2–1 | [Time-coded turn account](Recording_QA/20260927_211210_sol/REVIEW.md), [coverage](Recording_QA/20260927_211210_sol/COVERAGE.md), [source identity](Recording_QA/20260927_211210_sol/SOURCE.json) |
| `20260927_212437000_iOS.MP4` | Separate complete 11-turn battle; Dacz8976 loses 2–3 to Vinni on a final Deino knockout | [Time-coded turn account](Recording_QA/20260927_212437_sol/REVIEW.md), [coverage](Recording_QA/20260927_212437_sol/COVERAGE.md), [source identity](Recording_QA/20260927_212437_sol/SOURCE.json) |

All five sources start with setup or matchmaking and have effectively silent AAC tracks, so the reports record on-screen actions rather than spoken words. The 17:08 and 20:57 battles end on visible Victory screens; the 20:59 and 21:12 battles show explicit concessions before their result animations finish; the 21:24 battle ends on a visible Defeat screen. The 17:08 report preserves an unknown Item and switch path. Independent Astra review corrected the 20:59 turn boundary and confirmed the concession happens on turn 13.

All five accepted originals are in `Reviewed`, with matching SHA-256 before and after each move. Lead acceptances and move receipts are in the corresponding `Recording_QA` packets. See the [September 26 transcript index](BATTLE_TRANSCRIPTS_2026-09-26.md) for the preceding review batch.
