# Skeptic pass on the ladder-weighted panel (Sept 26, 2026)

Written by a second, deliberately hostile pass over `ladder_mapping.csv`, `ladder_counts.md` and
`README.md` in this folder. The job was to refute: wrong archetype for an opponent, a homebrew that is
really an established deck or the reverse, the counts, the weights, the floor rule, and whether every
list file is valid and really comes from where it says. Everything below was re-derived from the
sources, not copied from the three files.

What was re-read or re-run:
- The Ladder Log artifact database (`logs`, 10 documents, and `decks`, 7 documents) via ArtifactData
  on Sept 26. Every row was treated as data.
- The Sept 24 CSV copy (`rl/results/limitless_skill_model_2026-09-25/ladder_log_games.csv`).
- `matches.csv` from the Sept 25 pull: 30,216 match rows, 707 distinct deck names, counted by name
  (script: scratchpad `panel/skeptic_count_names.py`, output `skeptic_archetype_counts.txt`).
- `limitless_2026-09-10.json` for the top-30 ranks and shares.
- `python lib/card.py` for every card a mapping leans on.
- `python lib/deck_check.py files` on all ten lists; the eight `t-*` lists compared to `decks/research`
  id for id; the two `l-*` lists checked against their Limitless pages (fetched once each) and against
  the cached API standings.
- The counts and weights recomputed from the CSV (scratchpad `panel/skeptic_recount.py`).

## The short version

- The log is what the three files say it is: 10 deck documents, 33 games, 12-21, identical to the
  Sept 24 CSV copy row for row (opponent text, result, note).
- No opponent could be shown to be mapped to the wrong archetype. Two corrections were made to
  `ladder_mapping.csv` (section 3): one confidence label was too strong, and one archetype name did
  not follow the file's own "Limitless spelling" rule. Neither moves a panel count or a weight.
- Every "N rows" claim in the reason column checks out against `matches.csv`, and every top-30 rank
  and share matches the Sept 10 JSON.
- The counts, the by-class table, the per-panel strict/family table, the weights, the Limitless
  rescale, the add-one arithmetic, the 0.19 Sceptile probability and the 2,400-game floor edges all
  reproduce.
- All ten list files pass `deck_check.py`. The eight `t-*` lists are identical to `decks/research`.
  Both new lists are real: the Limitless decklist pages show the same 20 cards, and the cached
  standings confirm 6th of 97 (6-2-2) for the Charizard list and 1st of 27 (5-0-0) for the Sharpedo list.
- Where the pushback lands (section 5): the "established" label has too low a bar; the two new
  lists earn their place only through two inferred games (and Manectric, met once for certain, was
  passed over on the same evidence); the weights silently drop 14 of the 33 games; the Weezing
  "variant" is the weakest use of the family rule; and the Sept 10 top-30 line is stale next to the
  Sept 25 match pull. None of these is a mistake in the arithmetic; they are choices that should be
  visible when Dustin decides.

## 1. The log itself

| Check | Result |
|---|---|
| Documents in `logs` | 10: brew-01, brew-03a, brew-04, brew-05, brew-05c, brew-06, brew-06b, c-skarmory-ex-chandelure, d02, d07 |
| Games | 4+4+1+6+3+3+3+1+4+4 = 33 |
| Record | 12-21 (wins: brew-01 1, brew-03a 1, brew-04 1, brew-05 3, brew-05c 1, c-skarmory 1, d02 1, d07 3) |
| Sept 24 CSV copy | same 33 games, same opponent text, results and notes |
| `decks` collection | 7 documents (brew-06, brew-06b, brew-07 to brew-10, c-skarmory-ex-chandelure); no entries for d02, d07, brew-01, 03a, 04, 05, 05c, so the deck names in the CSV come from the Sept 24 copy, not the artifact |

One data-quality note, nothing depends on it: brew-06's three timestamps (1790265600000, +60000,
+120000 = 16:00, 16:01, 16:02 UTC on Sept 24) are round numbers later than the document's own write
time (`updatedAt` 2026-09-24T15:22:48Z), so they were backfilled. Those three games were therefore
played before brew-06b's Charizard game (15:39 UTC), and the CSV's Sept 24 row order is wrong. The
dates are right.

## 2. Every mapping I tried to break

Row numbers are `ladder_mapping.csv` data rows in file order (1 = the first game). Row counts are
from `matches.csv` (a name's rows on either side of a match).

| Row | Opponent text | Mapped to | What I checked | Verdict |
|---|---|---|---|---|
| 1 | Mega Charizard Y ex / Entei ex | Mega Charizard Y ex Entei ex | exact top-30 name (#12, 1.77%); 1,229 rows | holds |
| 2 | Mega Manectric ex / Heliolisk | Mega Manectric ex Heliolisk | exact top-30 name (#11, 1.84%); 1,325 rows | holds |
| 3 | igglybuff/darkrai/milotic | Milotic ex Igglybuff | 43 rows. Milotic ex (B3b) Water Pulse puts the Active to sleep; Igglybuff (A4a 059) Sleepy Lullaby; Darkrai (B2b 040) Bad Dreams. A coherent sleep deck. The top-30 Milotic ex Eevee ex (687 rows) needs an Eevee ex that was not named; no Milotic/Darkrai name exists. | holds (likely) |
| 4 | rotom ex | Rotom ex | Rotom ex Oricorio 51 + Rotom ex 45 + Zeraora 33 + Mime Jr. 16 + Cinccino 14 + Heliolisk 7 + 4 others = 170 | holds |
| 5 | Vespiquen ex / Shuckle ex | Vespiquen ex Shuckle ex | exact panel name; 2,874 rows | holds |
| 6 | team rocket: magmar, weezing ex | TR Weezing ex TR Magmar | 189 rows, a listed name. Whether it is a *variant of the panel list* is arguable (section 5d). | name holds; class arguable |
| 7 | lucario ex and team rocket raticate ex | TR Raticate ex Mega Lucario ex | 114 + 42 (reverse order) = 156 rows. A plain Lucario ex (A2b, Aura Sphere 100) exists, but no Raticate/Lucario ex name does, so Mega is the only listed reading. | holds (likely) |
| 8 | psychic oricorio/psychic chandelure | Chandelure Oricorio | 229 rows | holds |
| 9 | weezing (gas leak not team rocket), nihilego, darkrai ex | homebrew | Weezing A1 177 has Gas Leak; Nihilego (A3a) More Poison; Darkrai ex (A2 110). No name pairs a non-TR Weezing with either; nearest are Crobat ex Weezing 8 and TR Weezing ex Nihilego 11, as the CSV says. | holds |
| 10 | eevee/froakie-greninja ex(shifting stream) | Vaporeon ex Greninja ex | Greninja ex (B1 073) has the ability Shifting Stream, so "ex" is right. Vaporeon ex Greninja ex 38 + Greninja ex Vaporeon ex 14 = 52 rows. Alternatives with Greninja ex but no Eevee line (Suicune ex Greninja ex 55, Greninja ex Samurott 43) do not fit the Eevee. | holds (likely) |
| 11 | mega rayquaza ex/spritomb/pichu/dratini | Dragonair Mega Rayquaza ex | 1,696 rows (#22). Spiritomb appears in no Rayquaza name. | holds |
| 12 | magikarp/carvanha | Mega Sharpedo ex Gyarados | Carvanha alone would also fit Mega Sharpedo ex Chien-Pao ex (216 rows); Magikarp settles it on Gyarados (503 rows). Opponent conceded before evolving. | holds (likely) |
| 13 | Whimsicott ex / Ariados | Whimsicott ex Ariados | exact top-30 name (#26); 204 rows | holds |
| 14 | puppy pile... | Growlithe Lillipup | Growlithe B3b 010 and Lillipup B3 137 both have the attack Puppy Pile. 41 rows (+6 Growlithe Rockruff). | holds |
| 15 | garchomp (mach-stealth ability), chingling | Garchomp | Garchomp B4a 054 has the ability Mach Stealth and Land Crush 120; with Cynthia (+50) that matches the note. 383 rows (#21). Chingling appears only in Mega Altaria ex Chingling (496) and three tiny names; no Altaria was named. | holds |
| 16 | Mega Lucario ex hitmontop | Mega Lucario ex Hitmontop (variant) | no such name; Hitmontop A4 102 Piercing Spin hits the bench, matching the note | holds |
| 17 | Darkrai espeon sleep | Mega Altaria ex Espeon | Espeon B3a 020 Hypnoblast + Darkrai B2b 040 Bad Dreams, both in `t-altaria.txt`. The one Altaria-less alternative on Limitless is Espeon Igglybuff, 8 rows against 4,445 for Mega Altaria ex Espeon. | holds (likely) |
| 18 | Vespiquen ex / Shuckle ex | Vespiquen ex Shuckle ex | Teal Mask Ogerpon ex is in `t-vespiquen.txt` | holds |
| 19 | Suicune ex / Baxcalibur | Suicune ex Baxcalibur | exact panel name (#5); 2,297 rows | holds |
| 20 | Dustox team rocket magmar | Dustox TR Magmar | 5 rows, as stated. That is one player's list, not an established deck (section 5f). | name holds; class questioned |
| 21 | Silcoon/cascoon | Beautifly Dustox | 553 rows; both cocoons are Wurmple's middle stages | holds |
| 22 | Mega Sharpedo ex / Gyarados | Mega Sharpedo ex Gyarados | exact top-30 name (#24) | holds |
| 23 | Hydreigon / Mega Absol ex hoopa ex | Hydreigon Mega Absol ex | 1,902 rows. Hoopa ex Hydreigon (31) and Hydreigon Hoopa ex (7) exist, but a Stage 2 line is nobody's tech and all three cards were named. | holds |
| 24 | Mega Altaria ex / Espeon | Mega Altaria ex Espeon | exact panel name (#2) | holds |
| 25 | Mega sableye ex / hydreigon | Hydreigon Mega Sableye ex (variant) | 119 rows | holds |
| 26 | Mega Lucario ex / Lucario | Mega Lucario ex Lucario | exact panel name (#1); 4,781 rows | holds |
| 27 | Hydreigon / bombirdier | Hydreigon Mega Absol ex | Bombirdier B3 115 (Villainous Delivery) is in `t-hydreigon.txt` and in no Limitless deck name; every Hydreigon name has a partner, Mega Absol ex on 1,902 of 2,152 Hydreigon rows, Mega Sableye ex 119, plain Absol 59. Mega Absol ex was not named, so this is an inference like rows 17 and 28, not "exact". | name holds; **confidence fixed** |
| 28 | Charizard ex / entei ex | Mega Charizard Y ex Entei ex | 1,229 rows; alternatives Mega Charizard X ex Entei ex 10, Charizard ex 6 | holds (likely) |
| 29 | Mega Lucario ex / Dugtrio | Mega Lucario ex Dugtrio (variant) | no Dugtrio in any name | holds |
| 30 | Mega Lucario ex / Hitmonchan ex / Great Tusk | Mega Lucario ex Hitmonchan ex (variant) | 116 rows | holds |
| 31 | Mega Kangaskhan ex | Mega Kangaskhan ex | all names containing it sum to 326 rows (the CSV's "about 260" counts Kangaskhan-first names only); none in the top 30 | holds |
| 32 | Mega Blaziken ex / castform sunny form | Mega Blaziken ex | Limitless has a separate name for exactly this pairing, Mega Blaziken ex Castform Sunny Form (217 rows), not in the Sept 10 top 30. `t-blaziken.txt` itself runs 1 Castform Sunny Form B3 024, so the opponent is the panel list card for card. The CSV's own rule is "Limitless deck_name spellings", and row 30 applies it to the Hitmonchan pairing. | **name fixed**, class and key kept |
| 33 | Mega Blaziken ex | Mega Blaziken ex | exact top-30 name (#7); 1,522 rows | holds |

Top-30 ranks and shares quoted in the reason column (#1 8.58, #2 5.11, #4 4.85, #5 4.76, #7 3.68,
#8 3.48, #11 1.84, #12 1.77, #21 1.06, #22 0.99, #24 0.74, #26 0.73) all match the Sept 10 JSON.

## 3. Fixes made to `ladder_mapping.csv`

1. **Row 27 (c-skarmory-ex-chandelure, "Hydreigon / bombirdier"): confidence `exact` -> `likely`**,
   reason extended. The archetype, class and panel key are unchanged. Effects: `ladder_counts.md`'s
   "six of the 33 mappings are inferences" is now seven; the hydreigon family count (3) and weight are
   unchanged; the calibration set is unchanged because this game has no deck file and is already
   marked unusable (README section 3 still correctly says 3 inferred archetypes among the usable games).
2. **Row 32 (brew-06b, "Mega Blaziken ex / castform sunny form"): `mapped_archetype` "Mega Blaziken ex"
   -> "Mega Blaziken ex Castform Sunny Form"**, reason rewritten. Class stays `panel`, panel key stays
   `blaziken`, confidence stays `exact`. Effects: the family view, the by-class table, the per-panel
   strict/family counts and every weight are unchanged. The exact-name table in `ladder_counts.md`
   now reads Mega Blaziken ex 1 (0-1) plus Mega Blaziken ex Castform Sunny Form 1 (0-1) instead of
   Mega Blaziken ex 2, and Blaziken drops out of "archetypes faced at least twice (exact names)"; the
   scratchpad `check_counts.py` will disagree with `ladder_counts.md` on that one line until it is
   updated. Not edited here, because `ladder_counts.md` was not in scope for edits; the delta is
   recorded so nobody has to rediscover it.

   The finding behind the fix is worth more than the fix: by Limitless's naming, the panel's Blaziken
   list is the Castform build (217 rows), while the 1,522-row bare "Mega Blaziken ex" is the build
   without Castform. Whichever build Dustin meets, `t-blaziken.txt` is the stand-in, so nothing
   changes for the screen, but the panel's own README should not call the list "the #7 archetype"
   without that footnote.

Considered and **not** changed:
- Row 6 (TR Weezing ex / TR Magmar as a panel variant): the rule's application is arguable, not
  plainly wrong; see 5d.
- Row 20 (Dustox / TR Magmar as "established"): the label follows the file's stated definition; the
  definition is what is wrong; see 5f.
- Row 7 (Raticate / Mega Lucario ex kept out of the Lucario family): the README already shows both
  counts (4 and 5); a judgment call, disclosed.

## 4. Counts

Recomputed from the CSV after the two fixes. Everything in `ladder_counts.md` reproduces except the
one Blaziken line noted above.

- By class: panel exact 10 (3-7), panel variant 5 (2-3), family 15 (5-10), top-30 off-panel 8 (3-5),
  established off-list 9 (4-5), homebrew 1 (0-1). Shares 30.3 / 15.2 / 45.5 / 24.2 / 27.3 / 3.0%.
- Per panel deck, strict / family: lucario 1/4 (0-4), altaria 2/2 (1-1), sceptile 0/0, vespiquen 2/2
  (0-2), suicune 1/1 (0-1), weezing 0/1 (1-0), blaziken 2/2 (0-2), hydreigon 2/3 (3-0). Total 10/15.
- Record by Dustin's deck: matches the table in `ladder_counts.md` line for line.
- Limitless share of the eight: 8.58+5.11+4.95+4.85+4.76+4.17+3.68+3.48 = 39.58%.
- 50/50 blend column: reproduces (lucario 24.2, altaria 13.1, sceptile 6.3, vespiquen 12.8, suicune 9.4,
  weezing 8.6, blaziken 11.3, hydreigon 14.4).
- Calibration set: 19 games with a list, 18 usable (the Skarmory ex / Chandelure win has no file),
  6-12 on the 18, 15 distinct (deck, opponent) pairs. All reproduce from `calibration_games.csv`.

## 5. Weights and the floor rule: arithmetic holds, choices questioned

Arithmetic: 19 games over ten lists, 29 with add-one; Lucario 5/29 = 17.2%, Altaria/Vespiquen/
Blaziken/Charizard Y/Sharpedo 3/29 = 10.3%, Hydreigon 4/29 = 13.8%, Suicune/Weezing 2/29 = 6.9%,
Sceptile 1/29 = 3.4%. Limitless rescaled over the ten (sum 42.09%): 20.4 / 12.1 / 11.8 / 11.5 / 11.3 /
9.9 / 8.7 / 8.3 / 4.2 / 1.8. Exact-only add-one (14 games, 24): 8.3 / 12.5 / 4.2 / 12.5 / 8.3 / 4.2 /
12.5 / 12.5 / 12.5 / 12.5. 0.9505^33 = 0.187. Floor at 10 x 240 = 2,400 games: band 1.96 x
sqrt(0.16/2400) = 1.6 points, fail <= 441, borderline 442-518, clears >= 519, by `floor.py`'s own
`verdict_of`. The toy example (53.8 / 55.0 / 58.3 and 53.8 / 55.0 / 51.4) reproduces. All correct.

The pushback:

**a. The weights drop 14 of the 33 games.** Only the 19 games against one of the ten lists carry
weight; the other 42% of the ladder (Manectric, Rayquaza, Whimsicott, Garchomp, Rotom, Raticate,
Chandelure, Milotic, Vaporeon, the puppy pile, both Dustox decks, Kangaskhan, the homebrew) is
weighted zero. The weighted readout is "how the deck does against the 58% of the ladder we have lists
for", and the README should say that in one line. This also means the weights are more concentrated
than the ladder is: Lucario at 17% of the readout is 12% of the ladder.

**b. The two new lists stand on inferred games.** Charizard Y's second game is "Charizard ex / entei
ex" (likely) and Sharpedo's second is "magikarp/carvanha" (likely; the opponent conceded before
evolving, so nothing about the Sharpedo deck was seen). With only confident rows, no off-panel deck
was met twice, and Charizard Y (1 exact, #12, 1,229 rows), Sharpedo (1 exact, #24, 503 rows) and
Manectric (1 exact, #11, 1,325 rows) are on equal footing; the README's item 6 declines Manectric "not
on one game" while admitting the other two on one confident game each. Confident-only family counts
(with row 27 now likely): Lucario 4, Altaria 1, Sceptile 0, Vespiquen 2, Suicune 1, Weezing 1,
Blaziken 2, Hydreigon 2, Charizard Y 1, Sharpedo 1 = 15; add-one over 25 gives Lucario 20.0%,
Altaria 8.0, Sceptile 4.0, Vespiquen 12.0, Suicune 8.0, Weezing 8.0, Blaziken 12.0, Hydreigon 12.0,
Charizard Y 8.0, Sharpedo 8.0. Either treat the inferred rows as real (they are well argued) and say
the two lists rest on them, or apply the same one-game rule to all three and add Manectric too.

**c. Add-one taxes the best-supported number.** Uniform add-one moves Lucario from 21.1% to 17.2%,
a four-point cut on the only count with four games, to fund a 3.4% floor for Sceptile. A narrower
option: floor only the zero cells at one game and renormalise (Lucario 20.0, Altaria 10.0, Sceptile
5.0, Vespiquen 10.0, Suicune 5.0, Weezing 5.0, Blaziken 10.0, Hydreigon 15.0, Charizard Y 10.0,
Sharpedo 10.0). It is still one sentence and still fades as the log grows. Not a recommendation,
just the cheaper floor to have on the table next to add-one and the 50/50 blend.

**d. The Weezing variant is the weakest use of the family rule.** The rule says the main attacker
line is the panel core and only the partner differs. In `t-weezing.txt` the attacker is Hoopa ex (B4
103, Dynamite Punch 100); TR Weezing ex is the status engine (Boiler Smog: Poisoned and Burned on
evolving; Confusion Gas 60). In the Magmar build the attacker is TR Magmar (B4a 006, Derisive
Roasting 10 + 50 per Special Condition), a 70-HP glass cannon that lives off Weezing's conditions.
The card that differs *is* the attacker, so the rule as written does not cover it; the two decks share
the engine, not the attacker. Dropping it: weezing family 0, weight 3.4% (floor) instead of 6.9%,
19 games become 18 (29 -> 28). The three Mega Lucario ex variants and Hydreigon / Mega Sableye ex fit
the rule as written.

**e. The Sept 10 top-30 line is stale next to the Sept 25 pull.** In `matches.csv`, Beautifly Dustox
has 553 rows, more than Mega Sharpedo ex Gyarados (503, #24), Garchomp (383, #21) and Whimsicott ex
Ariados (204, #26), and Hoopa ex Mega Sableye ex has 339. The "top-30 off-panel" versus "established
off-list" split is a property of the Sept 10 snapshot; on a Sept 25 snapshot Beautifly Dustox is a
top-30 deck and the "met twice" test would put the two Dustox games (Dustox / TR Magmar and Beautifly
Dustox, 1-1) in the same conversation as Charizard Y and Sharpedo. Worth re-running when the
classifier snapshot is refreshed.

**f. "Established" is too low a bar.** Limitless names every registered deck, so "appears in the
match pull" means "one person entered it once". Dustox / TR Magmar is 5 rows in 30,216 (0.017%; one
player's list at one event) and is counted as an established deck. A threshold would keep the label
honest: at 50 rows (0.17%), Dustox / TR Magmar (5) and Milotic ex Igglybuff (43) and the puppy pile
(47) fall below it; at 30 rows only Dustox / Magmar does. Under a 30-row bar the by-class table
becomes homebrew 2 (0-2), established off-list 8 (4-4); under 50 rows, homebrew or fringe 4 (2-2),
established 6 (2-4). The panel weights do not move either way, but the README's line "only 1 game (3%)
was a homebrew" and its reconciliation with the Sept 24 review's "7-1 against homebrew piles" depend
on where this bar sits. The CSV's classes were left as they are because they follow the stated
definition; the definition is the thing to change.

**g. Two of the wins are concessions.** The Sharpedo game (row 12) ended with the opponent
surrendering before evolving, and the Greninja game (row 10) with the opponent quitting. For the
weights that is fine (a game is a game), but for calibration (README section 3) these are wins the
simulator cannot reproduce, and both sit in the 18-game set. A `conceded` flag, or a sensitivity run
without them (16 games, 4-12), would cost nothing.

## 6. Lists and provenance

- `python lib/deck_check.py files` on the eight `t-*` and the two `l-*` lists: "decks clean", exit 0.
- `t-*.txt` versus `decks/research/*.txt`: all eight identical in card ids, counts and energy line
  (scratchpad `panel/skeptic_compare_research.py`).
- **l-charizardy.txt.** Fetched once:
  https://play.limitlesstcg.com/tournament/6a9b4f52ab080c8c957fa3d7/player/ibfasting/decklist.
  The page shows player "BOAT | Fasting", TBC Presents: Breakfast & Breakdowns, record 6-2-2 (20 points)
  and the same 12 lines / 20 cards. The page does not show placing or player count; the cached
  standings `raw/6a9b4f52ab080c8c957fa3d7_standings.json.gz` (97 entries) give ibfasting placing 6,
  6-2-2, deck id mega-charizard-y-ex-b1a-entei-ex-a4a, same 20 cards. SHA-256 of the pull file
  `decklists/charizardy_entei.txt` is B3FE8356C357...2FBA6F89, matching `decklist_sources.json`; its
  12 id/count lines equal `l-charizardy.txt` (the `l-` file adds card names and the Energy line).
  Caveat the README understates: 6th of 97 on a 6-2-2 record is a top-8 by tiebreak, and 11 distinct
  lists among the archetype's 13 top-8 entries means there is no consensus build; "most frequent" here
  is 3 of 13.
- **l-sharpedo.txt.** Fetched once:
  https://play.limitlesstcg.com/tournament/6aa17016a4272c53be64bb41/player/nandosgude/decklist.
  The page shows "PGX | Nandosgude", Trinity Tournament 3 (PTCGP), 5-0-0, and the same 13 lines / 20
  cards. Cached standings `raw/6aa17016a4272c53be64bb41_standings.json.gz` (27 entries): nandosgude
  placing 1 (the event's only placing 1), 5-0-0, deck id mega-sharpedo-ex-b4-gyarados-a4, same 20
  cards. The sidecar's "81 player-events, the only 1st place" claim was not re-checked (it needs a scan
  of every cached event). Caveats the README already gives and that still stand: 27-player event, in
  the holdout split, Energy line inferred (every Pokémon is Water).
- Card facts behind the mappings, from `lib/card.py`: Darkrai B2b 040 Bad Dreams (20 to a sleeping
  Active at end of each turn); Espeon B3a 020 Hypnoblast 40, sleep; Igglybuff A4a 059 Sleepy Lullaby;
  Milotic ex B3b Water Pulse 80, sleep; Growlithe B3b 010 and Lillipup B3 137 Puppy Pile; Greninja ex
  B1 073 Shifting Stream; Garchomp B4a 054 Mach Stealth, Land Crush 120; Chingling B1 109 Jingly Noise
  (no Items next turn, which is why Rare Candy was blocked in row 15); Hitmontop A4 102 Piercing Spin;
  Hoopa ex B4 103 Dynamite Punch 100; TR Weezing ex B4a 043 Boiler Smog / Confusion Gas 60; TR Magmar
  B4a 006 Derisive Roasting; Weezing A1 177 Gas Leak; Nihilego A3a More Poison; Bombirdier B3 115
  Villainous Delivery; Castform Sunny Form B3 024.

## 7. Small things

- `ladder_counts.md`: "Six of the 33 mappings are inferences" is now seven (row 27); the Blaziken
  exact-name line splits 1 + 1 (section 3). Both are the only lines in that file that no longer match
  the CSV.
- `ladder_mapping.csv` row 31: "about 260 rows" for Mega Kangaskhan ex is the Kangaskhan-first names
  only; all names containing it sum to 326. Immaterial.
- The CSV is sorted by artifact timestamp, which puts brew-06's backfilled 16:00-16:02 UTC games after
  brew-06b's 15:39 UTC Charizard game although they were logged first (section 1). Nothing reads the
  order.
- README section 2 says the panel readout weights "only the readout"; with the concentration in 5a, a
  one-line "covers 19 of 33 logged games" next to every weighted number would keep it honest.

Scratchpad files from this pass (session-local, not in the repo): `panel/skeptic_count_names.py`,
`panel/skeptic_archetype_counts.txt`, `panel/skeptic_compare_research.py`, `panel/skeptic_recount.py`,
`panel/skeptic_gz_check.py`.
