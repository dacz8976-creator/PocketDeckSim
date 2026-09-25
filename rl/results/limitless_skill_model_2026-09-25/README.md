# Limitless skill diagnostic — 2026-09-25

**Diagnostic only. These numbers must never be used to rank decks.** Files belong to the laptop session; no engine, source deck, training run, previous result, or repository commit was changed.

The development data do not explain away the three main simulator misses. Equalizing this record-based skill measure changes Altaria, Vespiquen and Sceptile by less than 0.6 percentage points. Their adjusted averages remain about 7.1 points above, 7.9 points above and 11.2 points below the simulator, respectively. They remain leads for bot/engine investigation under the requested rule; this observational model cannot prove an engine bug.

Collection: **126 Standard events**, scheduled August 26–September 24, 2026, inclusive. The run began September 24 in America/Chicago (September 25 UTC); the folder date does not add September 25 events. **63 development / 63 frozen holdout**, split before inspecting player outcomes. Seed **26092500001**; exact IDs and algorithm are in [split.json](split.json). The API currently uses `format: null` for Pocket Standard; CUSTOM and NOEX were excluded. The initial 1,000-event response reaches March, so it covers the complete requested date window.

## What the development half says

Each deck is averaged equally over the other seven panel decks. This is a diagnostic panel average, not a field-weighted tournament win rate. Intervals resample events; the simulator column is the fixed `K3` dictionary in the supplied `deep_table.py`. Gap = observed/adjusted score **minus** simulator score.

| Deck | K3 % | Development raw % | Equal skill / both p75 % (95%) | Raw gap pp | Adjusted gap pp | Requested verdict |
|---|---|---|---|---|---|---|
| altaria | 47.0 | 53.6 | 54.2 (49.8–58.0) | +6.6 | +7.1 | bot/engine |
| blaziken | 56.7 | 55.9 | 55.7 (51.0–60.5) | -0.7 | -0.9 | bot/engine |
| hydreigon | 34.7 | 42.2 | 41.6 (36.4–47.2) | +7.4 | +6.9 | bot/engine |
| lucario | 53.3 | 50.4 | 50.9 (47.2–54.3) | -2.9 | -2.3 | bot/engine |
| sceptile | 61.8 | 50.4 | 50.6 (44.3–56.0) | -11.4 | -11.2 | bot/engine |
| suicune | 52.6 | 47.1 | 46.8 (42.3–51.6) | -5.5 | -5.7 | bot/engine |
| vespiquen | 48.6 | 56.6 | 56.5 (52.3–60.6) | +8.0 | +7.9 | bot/engine |
| weezing | 45.3 | 43.8 | 43.6 (37.8–50.3) | -1.5 | -1.7 | bot/engine |

The verdict compares the raw **development** gap with the adjusted development gap. “Population” requires more than 50% shrinkage in the absolute gap; “bot/engine” means at least half remains in the same direction. Estimates whose 95% interval extends more than 8 points on either side, or lacks adequate bootstrap coverage, are “undetermined.” None exceeded that width here. These are the requested point-estimate labels. **Blaziken, Lucario and Weezing have intervals containing the simulator value**, so their labels do not establish a real deck-level miss or justify prioritizing work. No deck receives a Population label.

**Skill coefficient β = 0.292, event-bootstrap 95% interval -0.065 to 0.430.** This proxy has a weak, uncertain association with the match outcome after the pair effects. The analysis uses 1,918 panel-vs-panel matches, including 310 mirrors (which inform β but not the seven-opponent averages), and 85 ties.

With the requested difference-only model, both players at the **same** 75th percentile (0.1014 logit units, measured across development player-event records) gives `s1 − s2 = 0`. Therefore the p75 averages **and all their intervals are exactly the equal-skill values** above. This model cannot identify whether two strong players change a particular matchup compared with two weak players.

## Does one matchup cause the whole gap?

For each deck, remove its largest absolute raw development-vs-K3 cell discrepancy. Use the same remaining six opponents for all three averages; keep the fitted model unchanged. Positive gaps mean the tournament score exceeds the simulator.

| Deck | Removed opponent | K3, six opponents % | Raw gap, six pp | Adjusted gap, six pp |
|---|---|---|---|---|
| altaria | blaziken | 45.1 | +4.7 | +5.2 |
| blaziken | altaria | 59.1 | +2.2 | +2.1 |
| hydreigon | lucario | 35.5 | +3.1 | +2.6 |
| lucario | hydreigon | 50.5 | +2.2 | +2.7 |
| sceptile | vespiquen | 61.1 | -8.2 | -8.1 |
| suicune | vespiquen | 53.7 | -3.5 | -3.7 |
| vespiquen | sceptile | 51.1 | +4.3 | +4.2 |
| weezing | vespiquen | 47.6 | +0.7 | +0.6 |

Altaria, Vespiquen and Sceptile still have adjusted gaps of about +5.2, +4.2 and −8.1 points after their largest cell is removed. This check describes sensitivity; it has no separately claimed confidence interval.

## Historical reproduction — all events, integrity check

The rule and tolerance were written in [integrity_protocol.json](integrity_protocol.json) **before opening the holdout API outcomes**. The reproduction was run once, recorded in [reproduction_once.json](reproduction_once.json), and was not used to change the event selection, parser, or mapping. A repeat invocation reuses the saved report rather than calculating it again.

Fixed rule: use the initial frozen API list; Pocket Standard (`null`/`STANDARD`), scheduled start from August 26 00:00 UTC through September 23 23:30 UTC inclusive. That gives **124 events versus the old 111**. Scheduled start is the only timestamp available; the API does not provide an event completion timestamp. Do not interpret this as the exact finished-event set seen in the historical pull. No events were dropped after inspecting results.

The total comparison counts two-player decisive/tied pairings with deck IDs for both participants, all archetypes. Byes, single-player administrative losses, double losses, unresolved outcomes and absent deck labels do not enter that total. The fixed tolerance is **±1,257 matches (5% of 25,143, rounded down)**. Each of 28 half-tie cell scores must also fall within the old cell’s `p ± 1.96 √[p(1−p)/n]`. This is a descriptive binomial-noise tolerance, not a test of independent samples: the snapshots overlap.

**Approximate tolerance pass; exact match: False.** Rebuilt labeled-match total **25,856** versus **25,143** (difference **+713**). **10/28** cells match W-L-T exactly; **28/28** fall within the fixed noise tolerance. Label: **approximate, event-count difference +13**. The actual number and identity of differing event memberships are unknown because the old 111 event IDs were not saved; +13 is a count difference, not a reconstructed set difference.

Every differing cell is listed below. W-L-T is for the first, alphabetically named deck. These are **pooled all-event integrity totals only**; no holdout-specific, per-split or per-event rates were calculated. The historical comparison comes exclusively from the existing `LIMITLESS` dictionary, never from live-page win rates.

| Pair | Published Sept 23 W-L-T | Rebuilt W-L-T | Δ W-L-T | Within fixed noise? |
|---|---|---|---|---|
| altaria v blaziken | 69-23-3 | 72-24-3 | +3 / +1 / +0 | True |
| altaria v hydreigon | 74-55-6 | 76-56-6 | +2 / +1 / +0 | True |
| altaria v lucario | 223-84-11 | 234-88-11 | +11 / +4 / +0 | True |
| altaria v sceptile | 101-105-13 | 108-111-13 | +7 / +6 / +0 | True |
| altaria v suicune | 76-69-5 | 79-70-5 | +3 / +1 / +0 | True |
| altaria v vespiquen | 72-117-11 | 74-122-11 | +2 / +5 / +0 | True |
| altaria v weezing | 33-64-5 | 34-64-5 | +1 / +0 / +0 | True |
| blaziken v vespiquen | 28-6-1 | 56-17-2 | +28 / +11 / +1 | True |
| hydreigon v lucario | 78-65-6 | 83-68-6 | +5 / +3 / +0 | True |
| hydreigon v sceptile | 30-47-3 | 31-47-4 | +1 / +0 / +1 | True |
| hydreigon v suicune | 20-39-3 | 21-44-3 | +1 / +5 / +0 | True |
| hydreigon v vespiquen | 35-57-3 | 36-58-3 | +1 / +1 / +0 | True |
| lucario v sceptile | 85-141-5 | 86-145-5 | +1 / +4 / +0 | True |
| lucario v suicune | 91-64-3 | 100-73-3 | +9 / +9 / +0 | True |
| lucario v vespiquen | 133-57-7 | 140-58-7 | +7 / +1 / +0 | True |
| sceptile v suicune | 49-55-3 | 49-55-4 | +0 / +0 / +1 | True |
| sceptile v vespiquen | 41-84-2 | 45-90-4 | +4 / +6 / +2 | True |
| suicune v vespiquen | 33-92-3 | 35-92-3 | +2 / +0 / +0 | True |

No attempt was made to chase these discrepancies or infer missing historical events from outcomes. All 28 cells, including exact ones, are in [integrity_reproduction.csv](integrity_reproduction.csv).

## Deck-definition counts — all events, integrity check

These current B4a pages pool all events and are treated as holdout material. Only the requested match counts are read; their win rates are never used in an estimate or a comparison. An early HTML-inspection tool excerpt incidentally exposed rate attributes before the clarified rule; they were not used in calculations. This is recorded in the protocol rather than hidden.

| Page → opponent | Current page n | Pairings W-L-T n | All two-sided pairing entries | Pairings − page |
|---|---|---|---|---|
| sceptile → vespiquen | 137 | 139 | 142 | 2 |
| vespiquen → sceptile | 137 | 139 | 142 | 2 |
| altaria → sceptile | 229 | 233 | 240 | 4 |
| sceptile → altaria | 229 | 233 | 240 | 4 |

Pairings have 2 additional resolved Sceptile–Vespiquen matches and 4 additional resolved Altaria–Sceptile matches versus these live pages. All two-sided counts also retain administrative double losses, which are separately excluded from W-L-T. No attempt was made to tune event selection to those differences. The exact Vespiquen/Shuckle and Sceptile/Butterfree subtype pages now agree with each other. The old “under half” Vespiquen-page count is not reproduced at these exact current URLs. Generic species URLs and “combine variants” pages define different groups; they must not be substituted for this panel. The old raw page snapshots were not available in the referenced simulator result, so this cannot establish why the earlier page was short. [integrity_page_counts.csv](integrity_page_counts.csv) records the precise URLs.

## Early versus late — development only

The median development event **UTC calendar date is 2026-09-06**. Early includes that date (33 events); late starts the next date (30 events). All phases follow their event date. These are raw half-tie scores, not skill-adjusted. Small cells are noisy; this is not evidence that any single change caused a shift.

| Deck | Early seven-opponent average % | Late seven-opponent average % |
|---|---|---|
| altaria | 55.7 | 52.5 |
| blaziken | 57.0 | 53.4 |
| hydreigon | 39.8 | 41.8 |
| lucario | 52.8 | 47.7 |
| sceptile | 50.7 | 50.8 |
| suicune | 45.0 | 50.1 |
| vespiquen | 55.4 | 59.0 |
| weezing | 43.6 | 44.6 |

The two flagged cells change with time in this development sample: Altaria–Sceptile is 37.5% early (n=28), 48.1% late (n=80); Sceptile–Vespiquen is 45.0% early (n=30), 25.0% late (n=26). This split pools match formats and uses different events from the cited Sept 8 BO1 subset; it is not a reproduction of that subset.

| Pair (first deck) | Early W-L-T | Early % (n) | Late W-L-T | Late % (n) |
|---|---|---|---|---|
| altaria v blaziken | 14-2-1 | 85.3 (17) | 11-5-1 | 67.6 (17) |
| altaria v hydreigon | 10-6-2 | 61.1 (18) | 19-18-1 | 51.3 (38) |
| altaria v lucario | 48-15-5 | 74.3 (68) | 66-27-0 | 71.0 (93) |
| altaria v sceptile | 10-17-1 | 37.5 (28) | 35-38-7 | 48.1 (80) |
| altaria v suicune | 20-9-0 | 69.0 (29) | 15-18-3 | 45.8 (36) |
| altaria v vespiquen | 12-18-1 | 40.3 (31) | 20-37-5 | 36.3 (62) |
| altaria v weezing | 5-20-2 | 22.2 (27) | 9-10-1 | 47.5 (20) |
| blaziken v hydreigon | 10-1-2 | 84.6 (13) | 5-6-0 | 45.5 (11) |
| blaziken v lucario | 13-23-0 | 36.1 (36) | 11-12-0 | 47.8 (23) |
| blaziken v sceptile | 12-2-1 | 83.3 (15) | 5-3-0 | 62.5 (8) |
| blaziken v suicune | 7-6-1 | 53.6 (14) | 6-1-0 | 85.7 (7) |
| blaziken v vespiquen | 18-3-1 | 84.1 (22) | 6-3-0 | 66.7 (9) |
| blaziken v weezing | 5-7-2 | 42.9 (14) | 1-2-0 | 33.3 (3) |
| hydreigon v lucario | 14-13-2 | 51.7 (29) | 20-6-0 | 76.9 (26) |
| hydreigon v sceptile | 8-7-3 | 52.8 (18) | 4-12-1 | 26.5 (17) |
| hydreigon v suicune | 9-18-1 | 33.9 (28) | 1-6-0 | 14.3 (7) |
| hydreigon v vespiquen | 7-15-1 | 32.6 (23) | 6-8-1 | 43.3 (15) |
| hydreigon v weezing | 9-8-0 | 52.9 (17) | 2-5-0 | 28.6 (7) |
| lucario v sceptile | 25-34-2 | 42.6 (61) | 19-34-0 | 35.8 (53) |
| lucario v suicune | 35-22-1 | 61.2 (58) | 14-12-1 | 53.7 (27) |
| lucario v vespiquen | 46-20-1 | 69.4 (67) | 27-11-2 | 70.0 (40) |
| lucario v weezing | 32-22-4 | 58.6 (58) | 14-6-0 | 70.0 (20) |
| sceptile v suicune | 12-12-1 | 50.0 (25) | 13-13-1 | 50.0 (27) |
| sceptile v vespiquen | 13-16-1 | 45.0 (30) | 6-19-1 | 25.0 (26) |
| sceptile v weezing | 17-5-1 | 76.1 (23) | 7-6-0 | 53.8 (13) |
| suicune v vespiquen | 10-39-0 | 20.4 (49) | 10-12-1 | 45.7 (23) |
| suicune v weezing | 17-10-1 | 62.5 (28) | 6-5-0 | 54.5 (11) |
| vespiquen v weezing | 26-6-2 | 79.4 (34) | 9-0-0 | 100.0 (9) |

## Six held-out archetypes — development events only

“Held-out archetype” means a deck outside the eight-deck panel. It does **not** authorize using frozen holdout events. Each entry is **W-L-T (n)** for the named outside archetype. The final column pools its individual matches against the panel; it does not equally weight the eight opponents.

| Archetype | altaria | blaziken | hydreigon | lucario | sceptile | suicune | vespiquen | weezing | Panel pooled |
|---|---|---|---|---|---|---|---|---|---|
| manectric_heliolisk | 26-22-3 (51) | 10-3-2 (15) | 8-12-0 (20) | 14-21-1 (36) | 13-22-2 (37) | 17-9-2 (28) | 11-17-1 (29) | 4-8-0 (12) | 103-114-11 (228) |
| raticate_ninetales | 1-9-0 (10) | 7-1-0 (8) | 3-4-0 (7) | 12-13-0 (25) | 8-7-1 (16) | 8-11-0 (19) | 6-8-0 (14) | 4-9-1 (14) | 49-62-2 (113) |
| hoopa_absol | 54-21-6 (81) | 9-2-1 (12) | 17-9-0 (26) | 29-30-1 (60) | 18-27-2 (47) | 14-15-1 (30) | 5-20-3 (28) | 7-12-0 (19) | 153-136-14 (303) |
| garchomp | 2-7-0 (9) | 1-1-0 (2) | 2-4-0 (6) | 9-8-1 (18) | 3-3-0 (6) | 1-7-0 (8) | 2-2-0 (4) | 1-8-1 (10) | 21-40-2 (63) |
| whimsicott_ariados | 1-0-0 (1) | 0-0-0 (0) | 2-3-0 (5) | 5-3-0 (8) | 0-2-0 (2) | 3-3-0 (6) | 3-4-0 (7) | 1-4-0 (5) | 15-19-0 (34) |
| charizardy_entei | 21-32-1 (54) | 4-7-0 (11) | 10-13-1 (24) | 34-13-0 (47) | 23-8-0 (31) | 3-12-0 (15) | 12-10-1 (23) | 6-7-1 (14) | 113-102-4 (219) |

Lists use the most common exact 20-card multiset among development entrants finishing 1st–8th, with ties resolved by best placing, largest event, earliest date, player ID, then card multiset. Different art printings are not silently merged. This rule selects representative files; it is not a performance ranking. Numbers below show repeated **top-eight appearances of the same exact list**, not all registrations.

| Archetype/list | Exact-list appearances / eligible top-eight finishes | Representative source |
|---|---|---|
| [manectric_heliolisk](decklists/manectric_heliolisk.txt) | 9 / 11 | [nyrq, place 1/142, 2026-09-14](https://play.limitlesstcg.com/tournament/6aa0471eab080c8c957fe27d/player/nyrq/decklist) |
| [raticate_ninetales](decklists/raticate_ninetales.txt) | 2 / 3 | [shmo, place 3/27, 2026-09-17](https://play.limitlesstcg.com/tournament/6aaad41638886b36383c1ad5/player/shmo/decklist) |
| [hoopa_absol](decklists/hoopa_absol.txt) | 12 / 20 | [douka, place 1/83, 2026-09-13](https://play.limitlesstcg.com/tournament/6aa682e4f1243e65f97ffebe/player/douka/decklist) |
| [garchomp](decklists/garchomp.txt) | 1 / 1 | [cosmooo, place 2/21, 2026-08-28](https://play.limitlesstcg.com/tournament/6a91426eabb94822375023de/player/cosmooo/decklist) |
| [whimsicott_ariados](decklists/whimsicott_ariados.txt) | 1 / 2 | [birdnest, place 3/97, 2026-08-28](https://play.limitlesstcg.com/tournament/6a90e8157a62de8130140dee/player/birdnest/decklist) |
| [charizardy_entei](decklists/charizardy_entei.txt) | 3 / 13 | [ibfasting, place 6/97, 2026-09-06](https://play.limitlesstcg.com/tournament/6a9b4f52ab080c8c957fa3d7/player/ibfasting/decklist) |

Garchomp has only one eligible top-eight list and Whimsicott’s selected exact list appears once; those choices are especially thin. Card IDs came directly from the selected API decklists, with card numbers padded to three digits. Each `.txt` has only `<count> <SET> <NNN>` lines, totaling 20 cards. No Energy line was invented. [decklist_sources.json](decklist_sources.json) preserves provenance, cards, frequency and tie-breaking evidence.

## Exact deck IDs

The Sept 8 roster behind the Sept 23 comparison used specific subtypes. Short simulator names are not a request to combine every list containing that Pokémon. Mapping uses exact API ID equality. Reversed subtype labels, other partners, and different card-set definitions remain separate. Garchomp here is the B4a definition; Manectric’s Heliolisk is B4.

| Panel/held-out name | Exact API deck ID(s) |
|---|---|
| altaria | `mega-altaria-ex-b1-espeon-b3a` |
| blaziken | `mega-blaziken-ex-b1` |
| hydreigon | `hydreigon-mega-absol-ex-b1` |
| lucario | `mega-lucario-ex-b3-lucario-a2` |
| sceptile | `butterfree-b3b-mega-sceptile-ex-b3` |
| suicune | `suicune-ex-a4a-baxcalibur-b2a` |
| vespiquen | `vespiquen-ex-b4-shuckle-ex-a4` |
| weezing | `team-rockets-weezing-ex-b4a-hoopa-ex-b4` |
| manectric_heliolisk | `mega-manectric-ex-b2b-heliolisk-b4` |
| raticate_ninetales | `team-rockets-raticate-ex-b4a-alolan-ninetales-ex-b2` |
| hoopa_absol | `hoopa-ex-b4-mega-absol-ex-b1` |
| garchomp | `garchomp-b4a` |
| whimsicott_ariados | `whimsicott-ex-b1-ariados-b1a` |
| charizardy_entei | `mega-charizard-y-ex-b1a-entei-ex-a4a` |

The mapping was based on the historical roster descriptions and deck-ID labels, before the one-shot reproduction; it was not tuned to reproduce outcome cells. The subtype descriptions came from the read-only Pocket Deck Lab file `Boss Folder/competitive-deck-study-2026-09-08/round-robin-checkpoint/reports/research/README.md`. The supplied simulator dictionary path and hash are in [reference_inputs.json](reference_inputs.json).

## Method and what this cannot tell

Source semantics follow the [official Limitless Tournament API documentation](https://docs.limitlesstcg.com/developer/tournaments.html), cached in `raw/tournament_docs.html.gz`: player IDs are stable, pairings describe match outcomes, and phase mode distinguishes BO1/BO3/BO5. The [Pocket B4a deck page](https://play.limitlesstcg.com/decks?game=POCKET&format=standard&set=B4a) supplies deck labels; no live-page win rate enters this analysis.

For every development player-event appearance, sum that player’s final W/L/T records in all **other development events**, regardless of deck. Then `s = logit((W+5)/(W+L+T+10))`. A player with no other games has skill zero. Stable API `player` IDs are used, not display names. Final standings records retain byes and administrative outcomes as the API records them; this is a record proxy, not an independently measured rating. No current-event final record enters its own rating.

The unpenalized logistic fit has one effect for each of 28 unordered archetype pairs, reversed in sign when seats are reversed, plus `β × (s1−s2)`. Same-deck matches have pair effect zero and can inform β. Player1 is just API pairing order; it does not identify who went first in the game.

**Draw handling:** to match the old comparison’s `(W + ½T)/N`, a win is 1, a loss 0 and a tie ½ in the binomial log-likelihood. Thus the fitted percentage is expected **match score**, or a win-equivalent percentage. It is not a separate literal probability of a win when ties are possible. Double losses (`winner=-1`) are not ties (`winner=0`); neither byes nor double losses enter matchup W-L-T or the fit. They remain in the raw archive and `matches.csv`.

The model intervals use **2,000 successful event-bootstrap resamples**, seed **26092500002**. Each draw samples all 63 development events with replacement and recomputes ratings. Every duplicate of the current source event is excluded from its rating. Percentiles 2.5 and 97.5 give the intervals. No failed fits were discarded here. 568 of 4,884 development player-event ratings have no other games and therefore fall back to zero.

A player’s record also reflects their deck, opponents, tournament, draws, attendance and ability. Leave-one-event-out avoids using the current event’s outcomes but does not separate these causes, and it can use later development events by design. A weak or noisy skill proxy can leave real population effects unremoved. Conversely, adjusting record differences can remove genuine deck effects. “Bot/engine” is an investigation label, not causal proof.

Tournament matches mix BO1 games and BO3 series (and a small number of BO5 matches in the archive). Simulator K3 values describe single games. The requested pooled model does not adjust for match format, phase, date, opponent strength, decklist variants, or skill-by-deck interactions. Event intervals do not fully account for dependence from players returning across events; they do not include simulator Monte Carlo uncertainty or simultaneous eight-deck comparisons. Results concern tournament participants, not Dustin’s ladder.

[development_freeze.json](development_freeze.json) records checksums of the completed development outputs before the all-event API join. [archive_validation.json](archive_validation.json) confirms those outputs stayed unchanged afterward and that all 378 event endpoints and 30,216 raw pairing entries were archived.

The frozen half is archived and used only for the two explicitly labeled integrity checks. It has supplied no skill records, early/late estimates, verdicts, outside-archetype W-L-T, decklist selections, or validation estimates. A later one-time confirmation can rate holdout players from development events, after these verdicts are frozen. The existing Sept 23 aggregate had already exposed pooled information about some frozen events; this is a new event split, not a claim that all historical aggregate information was unseen.

## Ladder Log

[ladder_log_games.csv](ladder_log_games.csv) contains the saved season snapshot: **33 games, 12 wins and 21 losses**, September 15–24. It was exported from the saved authoritative Claude artifact database read, not from the obsolete July log. Opponent and note text are preserved. [ladder_log_provenance.json](ladder_log_provenance.json) records the source artifact, snapshot, timezone and limitations. It was not used in the skill model.

## Files and reproduction

- `raw/`: gzipped original HTTP bodies plus response headers, status and retrieval time. Includes the API index, every event’s details/standings/pairings, documentation and source pages. API requests honor returned RateLimit/Retry-After headers and cached successful responses are reused.
- `matches.csv`: one row per API pairing entry, including byes/administrative entries with explicit status, both players’ exact deck IDs/names, phase/mode, final W/L/T and placing. `development_matches.csv` is the development-only working extract. Missing placings remain blank.
- `split.json`, `events.json`, `deck_mapping.json`, `integrity_protocol.json`, `reproduction_once.json`: fixed identities and one-shot audit record.
- `model_cells.csv`, `deck_verdicts.csv`, `model_summary.json`, `development_player_skills.csv`, `bootstrap_samples.npz`: complete development fit and uncertainty.
- `early_late_cells.csv`, `early_late_decks.csv`, `early_late_split.json`: every early/late cell and seven-opponent average.
- `held_archetype_records.csv`, `decklists/`, `decklist_sources.json`: all 48 outside-archetype cells, six pooled rows and source-backed lists.
- `collect.py`, `fetch.py`, `capture_pages.py`, `analyze.py`, `verify.py`, `report.py`, `requirements.txt`: acquisition, analysis and report code.
- `validation.json`, `development_data_quality.json`, `raw_manifest.json`: independent fit/decklist checks, development exclusions, archive checksums.

To rerun the development estimates with the saved cache, install `requirements.txt` in a Python environment and run from this folder:

```bash
python analyze.py --development-only --bootstrap 2000
python verify.py
python report.py
```

`collect.py` resumes the fixed cached collection; it will not redraw the split. `analyze.py --integrity-only` archives the full match join and reuses the already completed integrity results. Do not delete the one-shot marker or change the event rule to chase a closer historical match. The current page-capture code is for source caching and permitted counts only.

Independent verification passed: all 4,884 rating rows were recomputed directly; a separate statsmodels fit agreed with the SciPy fit to within 0.001 percentage points per cell; duplicate-event exclusion and the p75 identity passed; all six lists exactly matched their source 20-card multiset. No holdout fit or confirmation was run.
