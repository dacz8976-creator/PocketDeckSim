# Gemini v7 reconciliation

Gemini v7 produced the primary outline for all available footage, including setup, Turn 1, Turn 2, the Opponent Turn 3 banner, visible battle-state changes, and the unresolved cutoff. The successful two-pass run reported an estimated cost of $0.106587 to $0.116772. An earlier preflight-only request cost $0.016433 and stopped before the main review because the first validator incorrectly rejected an honest unknown outcome for an incomplete recording.

The preflight and main prompts now explicitly allow incomplete recordings to retain an unknown outcome without inventing an ending. The validator now permits unknown terminal fields only when the recording lacks a terminal result, while still requiring observed opponent and opening identities. The parser also restores an omitted non-semantic `battle_identity.version: 1` field. The updated local suite passes 70 tests.

## Accepted after correction

- Gemini's setup, Turn 1, Turn 2, board state, score, cutoff, and unknown outcome are retained.
- Rainbow Cave wording was corrected so it does not claim a direct Fighting-to-Metal conversion.
- The recording date is identified as 2026-09-08 from the source filename, not from an in-video date.
- AI, Solo, and Auto metadata are not relied upon in the accepted battle reconstruction.
- The clip remains a complete review of its available footage. A later exact-continuity check linked it to `20260908_015702000_iOS.MP4`, so the combined full battle is now complete and ends in a player win, 3-2.

The untouched successful Gemini response and candidate packet remain in `submission-history/gemini-v7/`. The initial rejected preflight remains in `submission-history/gemini-v7-initial-incomplete-preflight/`. REVIEW.md, COVERAGE.md, SOURCE.json, and UNCERTAINTIES.json are the accepted corrected available-footage record.
