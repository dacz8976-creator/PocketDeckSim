# Gemini v7 reconciliation

Gemini v7 produced the primary full-battle outline and covered setup, all 11 turns, visible battle-state changes, knockouts, scoring, and the terminal result. Its source binding and independent identity preflight agreed. The two-pass run reported an estimated cost of $0.345878.

The parser correctly blocked automatic acceptance for mechanical issues: the battle-identity version was missing, two event groups lacked the named `Thieving Incisors` cause, and two event groups were not in chronological order. These blocks prompted selective review instead of silent acceptance.

## Accepted after correction

- Gemini's 11-turn structure, major actions, damage, knockout, scoring, and 3-1 opponent win are retained.
- Turn 6 now records the correct order: evolution, Thieving Incisors transfer, then manual Water attachment.
- Turn 9 now distinguishes attack impact, 0 HP/healing, and knockout removal timing.
- The explicit going-second banner is anchored at 00:10.400.
- Turn 11 includes Sparkling Aria's final 20 HP heal.
- The filename-derived date is correctly recorded as 2026-09-08.
- The structured record now includes battle identity version 1, chronological event order, and named causes for all Thieving Incisors Energy effects.

The untouched Gemini response and candidate packet remain in `submission-history/gemini-v7/`. REVIEW.md, COVERAGE.md, SOURCE.json, and UNCERTAINTIES.json are the accepted corrected record.
