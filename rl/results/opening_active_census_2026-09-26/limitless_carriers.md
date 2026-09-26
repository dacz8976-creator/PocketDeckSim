Decision this informs: whether the reserve route's clause (d) has a carrier archetype for switch A (`koa`) of the "opening Active choice" candidate (`REGISTRATION_DRAFT.md`, section 7; `docs/REVIEW_2026-09-24_direction.md`, section 8, line 130).

# Limitless carriers of switch A among Altaria lists (Sept 26)

List counting only. No engine game, no build, no seed. Development-half Limitless standings only; the 63 holdout standings files were never opened. Machine-readable figures: `limitless_carriers.json`.

## In plain words

- **Almost every Mega Altaria ex Espeon list carries the card switch A reads.** 335 of its 336 development-half lists (99.7%; 95% interval 98.3 to 99.9%) run Eevee B1 184, the Eevee with Boosted Evolution. That is every one of its 52 events, and all 51 of its top-8 finishes. 333 run two copies, 2 run one.
  - The one list without it runs two Eevee B4 131 (Tail Rap, no Ability) instead.
  - Every carrier also runs Espeon B3a 020, so switch A's other condition (an Eevee evolution in deck or hand) holds in all 335.
  - This is close to built in: an Espeon deck needs an Eevee, and B1 184 is the Eevee everyone chose.
- **The archetype is Sept 10 rank 2 and window rank 2, and it is not Dustin's** by the kt carrier census's rule (no Pokémon in its name is in any of his files).
- **The table's Altaria list is this archetype's list.** 144 of the 336 Limitless lists equal `decks/screen/opponents/t-altaria.txt` card for card, and 235 run exactly its Pokémon.
- **The other Altaria variants barely carry it.** Mega Altaria ex Igglybuff: 4 of 25 lists, one copy each, no top-8 finish. Greninja, Chingling, bare Mega Altaria ex and the 17 small Altaria labels: 0.
- **No other top-30 archetype carries it at all** (either top-30 reading). The Eevee decks that do (Slowking/Sylveon, Raticate/Jolteon and 27 more) are all outside both top 30s.
- **There is no pooled figure.** Counting the holdout half means opening its 63 standings files, which this count did not do (section 2).

## 1. Method

- **Source.** The Cowork Limitless pull, `rl/results/limitless_skill_model_2026-09-25/raw/<event>_standings.json.gz`. The window is Aug 26 to Sept 24, 2026, with 126 events split 63/63 by `split.json` (seed 26092500001).
- **What was opened.** From the pull's `raw/` folder, only the 63 development events' details and standings files (the event lists come from `split.json`): 4,884 standings entries, 4,722 of them with a decklist. `matches.csv` was not read.
- **The flag's printings.** These are the cards whose Ability is `CanEvolveOnFirstTurnIfActive`: Eevee B1 184, P-B 011 and P-B 054, all "Boosted Evolution".
  - Found by a scan of `lib/deckgym-database.json` for the Ability named Boosted Evolution, whose text is the one the engine's mechanic map sends to that flag (`effect_ability_mechanic_map.rs` 36-38; README section 3), and confirmed with `python3 lib/card.py Eevee`, which prints the same three ids and the text "As long as this Pokémon is in the Active Spot, it can evolve during your first turn or the turn you play it."
  - The other 11 Eevee cards and Eevee ex (Veevee 'volve) don't carry it.
- **What counts as a carrier.** A list carries the flag when one of its lines has one of those three set-and-number ids (Limitless numbers zero-padded to three digits). The same name at another printing doesn't count, as in the kt census.
- **What counts as an archetype.** The exact Limitless `deck.name`. "Altaria lists" are every name that contains "Altaria", grouped as Espeon, Igglybuff, Greninja, Chingling, bare ("Mega Altaria ex") and other (17 small labels, 61 lists).
- **Ranks and Dustin flags** come from the kt carrier census (`../kt_carrier_census_2026-09-26/census_summary.json`). Sept 10 ranks are by players (`decks/classifier/limitless_2026-09-10.json`); window ranks are by development-half matches.
- **The script** (`limitless_carriers.py`) and the recount were run from the session scratchpad and not added here, because this folder's brief allowed only this file, the `.json` and the draft edits. The method above reproduces from the pull alone.

## 2. Why only the development half

- `split.json` fixes the pull's rule: "all_estimates: development only, including skill records and decklist selection".
- The kt carrier census and B2e (both Sept 26, after the holdout was spent on kp3) counted lists from development standings only and never opened the holdout standings. This count keeps to the same rule.
- The holdout is spent "for pilot decisions" (the pull's README, Sept 25 note). Whether its standings may now be opened for card counts is Fable's or Dustin's call.
- The clause doesn't need it. The first draft's clause (d) to-do asked for the development-half share, and that half alone has 336 Espeon lists.

## 3. The count, by variant (development half)

| Altaria variant (Limitless name) | Sept 10 rank (players) | window rank | Dustin's? | lists (events) | carriers of B1 184 / P-B 011 / P-B 054 | share, 95% interval | events with a carrier | top-8 finishes carrying it |
|---|---|---|---|---|---|---|---|---|
| **Mega Altaria ex Espeon** | 2 (289) | 2 | no | 336 (52) | **335** (all B1 184; 333 with two copies, 2 with one) | **99.7%**, 98.3 to 99.9 | 52 of 52 | 51 of 51 |
| Mega Altaria ex Igglybuff | 29 (34) | 34 | no | 25 (20) | 4 (B1 184, one copy each) | 16.0%, 6.4 to 34.7 | 4 | 0 of 2 |
| Mega Altaria ex Greninja | 16 (79) | 10 | no | 125 (42) | 0 | 0%, 0 to 3.0 | 0 | 0 of 18 |
| Mega Altaria ex Chingling | 27 (37) | 27 | no | 38 (17) | 0 | 0%, 0 to 9.2 | 0 | 0 of 2 |
| Mega Altaria ex (bare) | 19 (71) | 21 | no | 44 (28) | 0 | 0%, 0 to 8.0 | 0 | 0 of 6 |
| other Altaria labels (Happiny 24, Gourgeist 11, 15 more) | not top 30 | not top 30 | - | 61 (32) | 0 | 0%, 0 to 5.9 | 0 | 0 of 8 |
| **all Altaria-named lists** | | | | 629 (55) | 339 | 53.9%, 50.0 to 57.8 | 53 | 51 of 87 |

- Intervals are Wilson 95% intervals. They count lists; a player who entered several events counts once per list.
- No P-B 011 or P-B 054 appears in any Altaria list; all 339 carriers use B1 184.
- None of the 629 lists runs Eevee ex.

**Mega Altaria ex Espeon, more closely.**
- All 336 lists run Espeon B3a 020 and Darkrai B2b 040 (the Darkrai is switch B's flagged Basic in the table list), almost all at two copies. 333 run Igglybuff A4a 059.
- The most common Pokémon line is the table list's exactly (1 Igglybuff, 1 Mega Altaria ex, 2 Eevee, 2 Swablu, 2 Darkrai, 2 Espeon), in 235 of 336 lists. Next: 2 Igglybuff and 1 Swablu (46), then 2 Mega Altaria ex (17).
- 144 lists equal the table list card for card (all 20 cards).
- The two variant files already on file (`decks/variants-2026-09-23/`) recur too: jlng's in 34 lists, lanora's in 27. Both carry 2 Eevee B1 184.
- The one non-carrier: `therico01`, Sept 5, 120 players, no placing recorded, with 2 Eevee B4 131 and 1 Swablu B3a 061 ([decklist](https://play.limitlesstcg.com/tournament/6a789b5ccdc0391d7fa61ba9/player/therico01/decklist)).

**Mega Altaria ex Igglybuff's four carriers** all run the Espeon package at one copy (1 Eevee B1 184, 1 Espeon B3a 020) beside the full Igglybuff line. They come from three players, one of them twice:
- 9th of 24, Aug 29 ([decklist](https://play.limitlesstcg.com/tournament/6a88ce398302ae761e5f8954/player/leonemesis/decklist));
- 63rd of 81, Aug 26 ([decklist](https://play.limitlesstcg.com/tournament/6a8b75058302ae761e5fab7e/player/pamnardo_s2/decklist));
- 67th of 69, Aug 26 ([decklist](https://play.limitlesstcg.com/tournament/6a8f27e57a62de813013fb20/player/pamnardo_s2/decklist));
- 61st of 112, Sept 10 ([decklist](https://play.limitlesstcg.com/tournament/6aa22425a4272c53be64ca36/player/fluffy_panda1995/decklist)).

The other 21 run no Eevee. The kt census's representative Igglybuff list (`../kt_carrier_census_2026-09-26/decks/c-mega_altaria_ex_igglybuff.txt`) is one of those 21.

## 4. Every archetype that carries it (development half)

31 Limitless archetypes have at least one carrier. Only the two Altaria variants above are in either top 30. The largest of the rest:
- Team Rocket's Slowking ex Sylveon ex: 16 of 17.
- Team Rocket's Raticate ex Jolteon ex: 10 of 10.
- Jolteon ex Mega Manectric ex: 7 of 7.
- Leafeon ex Serperior: 6 of 6.
- 25 more, with 1 to 5 lists each.

Every carrier in them also runs an Eevee evolution, and none of these archetypes is in the Sept 10 top 30 or the window top 30. Milotic ex Eevee ex (Sept 10 rank 18) has no carrier. The full list is in `limitless_carriers.json` → `all_archetypes_with_a_carrier`.

## 5. What this means for clause (d), stated against the fixed text

The clause (section 8, line 130) asks for a gain "on at least one Limitless top-30 archetype that is not Dustin's deck and carries the relevant cards".
- **Mega Altaria ex Espeon meets all three conditions on the numbers.**
  - It is top 30: rank 2 on both readings.
  - It is not Dustin's by the kt census's rule.
  - It carries the card in 99.7% of its lists, with usable decklists in numbers (144 equal to the table list).
- **It is a panel deck.** The table's Altaria list is this archetype's list, so the (d) gain and the new bot's own-side gain are read on the same mixed rows.
  - Whether a panel deck may serve as the (d) archetype is Dustin's ruling.
  - The kt carrier census raised the same question for Suicune (kt switch 1, README section 7), so one ruling answers both.
- **A fact for that ruling, with no position taken.** The card switch A reads, Eevee B1 184, is also in Dustin's deck 15 (2 copies; switch A changes that deck's opening in 9.7% of deals). The archetype is still not his by the kt rule, which looks at the archetype's named Pokémon. This differs from the Rayquaza case, where the priced card (Gouging Fire) was in no Dustin file.
- **If Dustin rules that a panel deck may not serve,** the only top-30 carrier off the panel is Mega Altaria ex Igglybuff.
  - It carries the card occasionally: 4 of 25 lists (16%), one copy each, no top-8 finish. It is Sept 10 rank 29, but window rank 34 (outside the window top 30). No carrier list was built here.
  - Whether a 16% occasional carrier "carries the relevant cards" is the same reading of fixed text that the kt census left open for Suicune's 11% and Vespiquen's 1.7%.
- **Whether the closure sentence triggers turns on the panel-deck ruling.**
  - If a panel deck may serve, the count found a top-30 archetype outside Dustin's decks that carries the card, with usable decklists, and the sentence does not close the route.
  - If not, it turns on whether Igglybuff's 16% counts as carrying the card. If that fails too, the route is closed for `koa`, as the sentence says.

## 6. Altaria's seven Limitless cells, the "before" figures

The route reports these before and after, not as a gate. Limitless is the development-half scoreboard v2 (`../scoreboard_v2_2026-09-25/limitless_v2_dev.json`, score = (W + T/2)/n, ±95% binomial). kp3 is Altaria's side on the table (`../table_readings_2026-09-24/kpr3_paired_reading.md` 167-173).

| Altaria v | kp3 table | Limitless v2 (W-L-T, n) | kp3 minus Limitless |
|---|---:|---|---:|
| Blaziken | 58.6 | 76.5 ± 14.3 (25-7-2, 34) | −17.9 |
| Hydreigon | 47.6 | 54.5 ± 13.0 (29-24-3, 56) | −6.9 |
| Lucario | 62.4 | 72.4 ± 6.9 (114-42-5, 161) | −10.0 |
| Sceptile (quarantined) | 42.8 | 45.4 ± 9.4 (45-55-8, 108) | −2.6 |
| Suicune | 48.8 | 56.2 ± 12.1 (35-27-3, 65) | −7.4 |
| Vespiquen | 47.4 | 37.6 ± 9.8 (32-55-6, 93) | +9.8 |
| Weezing | 40.4 | 33.0 ± 13.4 (14-30-3, 47) | +7.4 |

## 7. Checks

- **Independent recount.** A second script, written separately and run under WSL `python3`, matched the raw set and number strings in each development list's Pokémon section. It gives the same lists and carriers for every Altaria label (Espeon 336/335, Igglybuff 25/4, Greninja 125/0, bare 44/0, Chingling 38/0; all Altaria-named 629/339), and names the same single Espeon non-carrier.
- **Against the kt carrier census.** The list and event counts per Altaria archetype equal its `census_summary.json` (Espeon 336 in 52 events, Greninja 125/42, bare 44/28, Chingling 38/17, Igglybuff 25/20). The total 4,884 entries and 4,722 decklists match too.
- The table list and both variant files carry 2 Eevee B1 184 each (read from the files).
- **Verifier's third count (Sept 26).** A third script, written without reading either script above, opened only the 63 development standings and details files. It found the flag's printings again by searching the database for the mapped Ability text, and got the same three ids. Its results match this file on:
  - every Altaria group's lists, events, carriers, copies, events with a carrier, top-8 counts and Wilson intervals;
  - the one Espeon non-carrier and the four Igglybuff carriers (players, events, placings);
  - the 144, 34 and 27 exact-list matches, the 235, 46 and 17 Pokémon lines, and the Espeon, Darkrai and Igglybuff counts;
  - the 31 archetypes with a carrier (the same four largest), that every carrier runs an Eevee evolution, and the top-30 check against the kt census.
  - The closure sentence was also checked character for character against `docs/REVIEW_2026-09-24_direction.md` line 130.

## 8. Limits

- **Development half only.** The holdout half's lists are unread (section 2).
- **Limitless's labels decide the archetype.** A list with the Espeon package labelled "Igglybuff" counts under Igglybuff. That is why the four Igglybuff carriers look like light Espeon lists.
- **Carrying the card is not the same as switch A changing the opening.** That also needs a hand with an Eevee beside another Basic. The census's 24.0% is for the table list; lists with 2 Igglybuff or 1 Swablu would differ somewhat. The clause asks only for carrying.
- **Placings and records** were read only to report top-8 finishes and to name the listed entries; no score was computed from them.
