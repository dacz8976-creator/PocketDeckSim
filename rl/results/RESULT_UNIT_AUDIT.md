# Limitless result-unit audit

## Finding

The B4a aggregate and matchup W-L-T cells are **tournament match outcomes**. A BO1 match is one game; a BO3 match is one series. The public aggregate can therefore pool single-game outcomes with series outcomes when its contributing tournaments use mixed phase modes.

This has high-confidence primary support:

- The official [Tournament API documentation](https://docs.limitlesstcg.com/developer/tournaments.html) defines phase `mode` as the number of games per match and defines the pairings endpoint as one record per match, with one winner or tie value.
- The official [Tournament Settings documentation](https://docs.limitlesstcg.com/organizer/reference) says BO1 is a single game and a BO3 winner needs two game wins.
- The [B4a aggregate page](https://play.limitlesstcg.com/decks/?game=pocket) labels its total and matchup sample counts as “matches.”
- In the official API, Suede's 14 Monday pairing records reproduce the published 11-3 standings record exactly: 5-3 in BO1 Swiss and 6-0 in the BO3 cut. Léo's 14 PMPT #44 pairing records reproduce 12-2 exactly: 5-2 in BO3 Swiss and 7-0 in the BO3 cut. PMPT #44 used BO3 in both phases, so its record cannot be an individual-game record.

## Representative event modes

| Representative deck(s) | Event date UTC | Players | Swiss | Cut | Classification |
|---|---:|---:|---:|---:|---|
| Suicune | 2026-08-28 | 226 | 8 rounds BO1 | BO3 | Mixed |
| Vespiquen | 2026-08-29 | 378 | 7 rounds BO3 | BO3 | All BO3 |
| Blaziken, Weezing | 2026-08-30 | 138 | 7 rounds BO1 | BO3 | Mixed |
| Sceptile | 2026-09-02 | 119 | 6 rounds BO1 | BO3 | Mixed |
| Altaria | 2026-09-04 | 257 | 8 rounds BO1 | BO3 | Mixed |
| Hydreigon | 2026-09-04 | 129 | 6 rounds BO1 | BO3 | Mixed |
| Lucario | 2026-09-07 | 230 | 8 rounds BO1 | BO3 | Mixed |

The saved aggregate pages do not expose a BO1/BO3 breakdown for each archetype cell. A BO1-only matrix is therefore unavailable from the current capture without reconstructing all 55 tournaments from phase metadata, pairings, and decklists.

## Comparison rule

Use the Limitless percentages as a **match/series-level directional benchmark** for the current round robin: compare matchup direction, broad ordering, and large disagreements. Do not describe simulator single-game percentages as directly calibrated to the pooled external percentages.

For a later numeric comparison, either reconstruct a BO1-only external matrix or convert simulated games into the same phase-specific BO1/BO3 match outcomes. A generic percentage conversion is unsupported because the pool mixes phase modes, deck-specific results, and draws.

`RESULT_UNIT_AUDIT.json` preserves the seven official event-detail records, the two complete selected-player pairing trails used for the consistency checks, source URLs, and explicit unknowns.
