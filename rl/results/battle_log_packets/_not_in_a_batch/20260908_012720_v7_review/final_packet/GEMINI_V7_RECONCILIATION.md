# Gemini v7 reconciliation

Gemini v7 produced the primary full-battle outline and covered setup, all 12 turns, visible battle-state changes, knockouts, scoring, and the terminal result. The successful two-pass run reported an estimated cost of $0.390142. An earlier preflight-only request cost $0.062405 and stopped before the main review because Gemini encoded `04:36` as `436.0` seconds, outside the 282.628-second source.

The timestamp guard worked as intended and prevented a bad handoff. The preflight prompt was then strengthened to require elapsed decimal seconds with an explicit `04:36 = 276.0` example. The parser was also improved to restore an omitted non-semantic `battle_identity.version: 1` field while still rejecting wrong versions or factual mismatches. The updated parser passes 69 tests, and this saved response reparses as ready for independent review without another API request.

## Accepted after correction

- Gemini's 12-turn structure, major actions, evolutions, Tools, attacks, knockout chain, scoring, 3-2 player win, and Victory banner are retained.
- A Turn 3 Darkness attachment to Weezing ex was added; the Turn 9 attachment is its second.
- Both Magmar Energy attachments are Darkness rather than Fire.
- Ogerpon's Turn 8 retreat now records its one-Grass discard, and the Turn 12 X Speed retreat correctly records no Whimsicott Energy discard.
- Turn 5 and Turn 7 Derisive Roasting damage formulas were corrected.
- Turn 8 Soothing Wind protection is attributed to Whimsicott having Energy attached while Ogerpon's Ability is active.
- The final score wording is corrected to the game's displayed 3-2 win threshold.
- AI/Solo and Auto metadata are not relied upon in the accepted battle reconstruction.

The untouched successful Gemini response and candidate packet remain in `submission-history/gemini-v7/`. The initial rejected preflight remains in `submission-history/gemini-v7-initial-preflight-failure/`. REVIEW.md, COVERAGE.md, SOURCE.json, and UNCERTAINTIES.json are the accepted corrected record.
