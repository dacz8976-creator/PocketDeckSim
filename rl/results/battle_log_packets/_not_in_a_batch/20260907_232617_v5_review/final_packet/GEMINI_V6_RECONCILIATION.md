# Gemini v6 reconciliation

Gemini v6 was correctly bound to `20260907_232617000_iOS.MP4` by filename, SHA-256, byte count and duration, but its gameplay account is not from this recording. It described a Kuro battle involving Koffing, Weezing, Arbok and Articuno ex and claimed Victory. The verified source instead shows opponent Ddiioocc, Falinks, Jolteon ex and Mega Lucario ex, ending in Defeat.

Parser v3.0 blocked the draft because it was truncated before the required packet sections and final marker. That structural block prevented automatic handoff. Independent source review then established that the available content was also semantically unusable. No gameplay fact from the Gemini response was accepted.

The single Gemini request used 3,109 input tokens, 5,966 reported output tokens and 18,030 thought tokens. The estimated cost range was $0.069944-$0.092317. The original response, usage, cost record and parse report are preserved in `submission-history/gemini-v6/`.

## Verified replacement

- Player Dacz8976 loses to Ddiioocc on Turn 11.
- The terminal display shows player 1 and three opponent markers, plus a literal `+2 points` award for the final Jolteon ex knockout and a `Defeat` banner.
- Mega Lucario ex uses Fighting Pulse for 180 to knock out the full-HP 140 Jolteon ex.
- Thieving Incisors transfers Falinks's sole Fighting Energy to Benched Team Rocket's Raticate ex.
- Electromagnetic Wall triggers twice for 20 damage each.
- Manual interaction and clocks are visible. No Auto control is visible, but an exact mode or AI classification is not claimed.

The accepted source-grounded account is `REVIEW.md`. Remaining limits are recorded in `UNCERTAINTIES.json`.
