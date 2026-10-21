# Independent verification: 20261009_194445000_iOS.MP4

Decision: **ACCEPT**. Verifier: `/root/verify_194445`, model `gpt-6-sol`, reasoning effort `high`. Source SHA-256: `a16f4a2549d1a7b62c6324e90e7e82d1a553624e486b84a1875e597bd572ee1f`.

The saved review accurately classifies this as a computer battle. The AI opponent is labeled Miraidon ex Deck (Deluxe Pack: Mega); Auto is enabled before play and checked during play. The owner uses New deck 6 with visible Hitmonchan ex, Sandslash and Conkeldurr core. The terminal result is **Defeat, 2-3 points, 13 turns, 440 damage**. Exclusion from the Ladder Log and human-only Pause Games log is correct.

I independently checked the setup, every knockout and point transition, both Poké Ball sequences, the four Lucky Ice Pop heal states, the consequential Energy counts, one ordinary turn, and the terminal result. The point path is 0-2 after Iron Thorns knocks out Hitmonchan ex with 80 damage, 1-2 and 2-2 after Conkeldurr knocks out each Iron Thorns with displayed 120 weakness damage, then 2-3 after Magnezone ex knocks out Conkeldurr with Storm Blade's 130 damage. Four Quick Straight hits at 50 plus two Bedrock Breaker hits at 120 reconcile to 440.

Key original-size proof frames retained in `native_checks/` include `native_5.jpg` for Auto and AI, `native_80.jpg` for the turn-4 board, `native_166.jpg`, `native_193.jpg`, and `native_207.jpg` for Conkeldurr's Energy path and the first 120-damage hit, `native_188.jpg`, `native_240.jpg`, `native_244.jpg`, and `native_257.jpg` for the point path and final knockout. Original-size `intake_frames/2_135.775s.jpg` shows a Lucky Ice Pop Tails. The reviewed one-second preview frames `detail_100_008.jpg`, `_016.jpg`, `_024.jpg`, and `_034.jpg` show 70, 90, 110, and 130 HP after four 20-HP heals. The native bench crops show Sandslash with one Fighting Energy by turn 4 and Sandshrew gaining one on turn 12. The lead incorporated those initially omitted attachments into the final review before acceptance.

The two searches are bounded to visible results: opponent Poké Ball is followed by Magnemite on the Bench, and owner Poké Ball is followed by Timburr in hand and on the Bench. The exact identity of any reused Lucky Ice Pop copy, early coin faces that are not readable, hidden hands and full deck lists remain unresolved. The review does not turn those gaps into asserted facts. The complete 13-turn coverage claim is supported by the primary overview and detail sequences, with the native source retained as the authority. This was a bounded independent check, not a second full decode.

Required changes: none.

Final primary files read and reconciled (SHA-256):

| File | SHA-256 |
|---|---|
| `REVIEW.md` | `dddaec892a6d8d850906fc43dfaa046d25aec494ecd5d33a388a924b11cb5f07` |
| `COVERAGE.md` | `f1a45934813f120291b265b307df5a8674eca86a87a7fc653e1637722e56f138` |
| `FINDINGS.json` | `2dc5fdeb321c17f66e5395c0756116098f170b2b910e31dc7204559c4ec364ea` |
