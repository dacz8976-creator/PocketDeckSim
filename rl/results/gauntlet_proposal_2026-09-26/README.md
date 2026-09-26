# Gauntlet proposal (Sept 26, 2026)

Dustin asked for a "gauntlet": the most-used Limitless decks, with at least one deck of every Energy
type, as the large test for engine and pilot changes (small tests stay for finding bugs). He added that
it should grow toward covering as much real Limitless play as practical, so that it mimics the ladder and
can later test new brews.

This is list counting only: no engine games, no builds, no web (game8 was not fetched). It uses the
**development half** of the Limitless pull only: 63 events, 4,722 decklists, Aug 26 to Sept 24. The 63
holdout files were never opened. Numbers: `gauntlet.json`. Script: `gauntlet.py`.

## In plain words

- **Today's 16 test lists are 15 Limitless decks** (the two Charizard Y lists are the same deck). They
  cover 7 of the 8 Energy types. **Only Metal is missing.**
- **Metal is almost absent from tournaments.** The 22 decks that run Metal Energy alone have 41 of the
  4,722 lists between them (0.9%). The most-used is **Mega Scizor ex / Revavroom**: 9 lists, one top-8 finish.
  Adding it is the one addition needed for "a deck of every Energy type". It would test the engine on Metal
  cards; it adds almost nothing to realism (0.2% of lists).
  - The suggested Metal list (section 1) is a real list two different players registered.
  - No Metal list exists in the repo yet. It needs the usual card check before it is used.
- **Lightning, Psychic and Fighting are thin.** Each has only one test deck that runs that Energy alone
  (Manectric, Altaria, Lucario).
- **Two bigger gaps than Metal.** The gauntlet lacks the **7th and 10th most-used decks**:
  - **Dragonair / Mega Rayquaza ex** (Fire + Lightning): 143 lists, 15 top-8 finishes.
  - **Mega Altaria ex / Greninja** (Psychic): 125 lists, 18 top-8 finishes.
  - Each has more lists than 7 of our 15 decks, and together they also thicken Lightning and Psychic.
    They are the best next additions if the gauntlet grows.
- **How much of Limitless each version covers** (share of lists / share of top-8 finishes):

  | Version | Lists | Top-8 finishes |
  |---|---|---|
  | The 8 table decks | 38% | 45% |
  | Today's 16 lists | 49% | 56% |
  | + Metal | 49% | 57% |
  | + Rayquaza and Altaria/Greninja | 55% | 64% |

- **The long tail is long.** Taking decks in order of use:
  - 13 decks reach 50% of lists;
  - 18 reach 60%;
  - 30 reach 70%;
  - 56 reach 80%.
  - Limitless has 486 deck names in all.
- **Cost per pilot reading** (500 games per pairing, both seats; each deck plays the 8 table decks):

  | Version | Games per pilot reading |
  |---|---|
  | Today's table | 14,000 |
  | The Energy gauntlet (16 decks) | 46,000 (60,000 for a full round robin) |
  | + the two gaps | 54,000 |
  | The 80% version | 206,000 |

  The 80% version is not practical. Also, Limitless has too few matches to check most of those extra cells
  anyway: at most 54 pairings have 30 or more Limitless matches, however big the gauntlet gets.
- **Weighting by Limitless share doesn't add coverage.** It costs the same games and rebalances the decks
  already in the gauntlet. It makes the average somewhat noisier (16 decks behave like about 10), and it
  gives the Metal deck almost no weight (0.4%).
- **Dustin's ladder:**
  - Today's 16 lists match 16 of his 33 logged ladder opponents by exact deck name, and 22 of 33 counting
    variants of the table decks.
  - A gauntlet built purely by usage needs 30 decks to match 17 exact.
  - The held-out and ladder lists were picked from his games, so they already fit his ladder better than
    usage alone would.
- **How much the lists vary:**
  - 8 of our 16 lists are exactly the most common list of their deck, 6 are common variants and 2 are
    unusual (details in section 5).
  - Some decks are nearly fixed: 81% of Mega Blaziken ex lists are the same 20 cards.
  - Others vary a lot. Lucario has 146 different lists among 398, and the most common is only 16%.
    Suicune's most common list is only 9%.
  - As Dustin said, the variation is mostly Trainers: in 15 of 16 decks the flexible slots hold more
    Trainers than Pokémon. Vespiquen is the exception.
- **Two ways to test list variation** (section 6):
  - **A:** a second real list for the 4 most-used, most variable decks (Lucario, Suicune, Weezing,
    Charizard Y), played only in the big gauntlet. Cost: +30,000 games per run (+14,500 if they play only
    the 8 table decks).
  - **B:** a one-off check of those 4 decks. The second list and two single-card Trainer swaps each play
    the table decks. Cost: 43,500 games, once.
  - Suggested order: B first; keep A only for decks where B finds a shift of 3 points or more.
- **What the lists cannot show:** which cards anyone drew or played, or whether a flex card helped. A card's
  rate is its popularity, not its strength. Section 7 has the rest.

## 1. The proposed gauntlet

The current 16 lists plus one Metal deck: 16 decks, 17 list files. "Usage rank" is by number of
development-half lists. "Our list" compares the test file with that deck's Limitless lists (section 5).

| # | Deck (exact Limitless name) | List file | Energy | Usage rank | Lists (share) | Top-8 | Our list |
|---|---|---|---|---|---|---|---|
| 1 | Mega Lucario ex Lucario | `decks/screen/opponents/t-lucario.txt` | Fighting | 1 | 398 (8.4%) | 43 | most common (65 copies) |
| 2 | Mega Altaria ex Espeon | `t-altaria.txt` | Psychic | 2 | 336 (7.1%) | 51 | most common (144) |
| 3 | Butterfree Mega Sceptile ex | `t-sceptile.txt` | Grass | 3 | 244 (5.2%) | 30 | most common (173) |
| 4 | Vespiquen ex Shuckle ex | `t-vespiquen.txt` | Grass | 4 | 233 (4.9%) | 33 | most common (69) |
| 5 | Suicune ex Baxcalibur | `t-suicune.txt` | Water | 5 | 200 (4.2%) | 22 | common variant (13 copies, 3 cards off) |
| 6 | Team Rocket's Weezing ex Hoopa ex | `t-weezing.txt` | Darkness | 6 | 152 (3.2%) | 16 | common variant (10, 4 cards off) |
| 7 | Hydreigon Mega Absol ex | `t-hydreigon.txt` | Darkness | 8 | 139 (2.9%) | 12 | most common (81) |
| 8 | Hoopa ex Mega Absol ex | `h-hoopa_absol.txt` | Darkness | 9 | 128 (2.7%) | 20 | common variant (15, 1 card off) |
| 9 | Mega Manectric ex Heliolisk | `h-manectric.txt` | Lightning | 11 | 111 (2.4%) | 11 | most common (69) |
| 10 | Mega Blaziken ex | `t-blaziken.txt` | Fire | 12 | 108 (2.3%) | 9 | most common (88) |
| 11 | Mega Charizard Y ex Entei ex | `h-charizardy_entei.txt` and `l-charizardy.txt` | Fire | 13 | 106 (2.2%) | 13 | both common variants (3 and 4 copies; 1 and 2 cards off) |
| 12 | Team Rocket's Raticate ex Alolan Ninetales ex | `h-raticate.txt` | Water | 19 | 55 (1.2%) | 3 | most common (10) |
| 13 | Garchomp | `h-garchomp.txt` | Water + Fighting | 25 | 36 (0.8%) | 1 | common variant (3 copies) but 8 cards off |
| 14 | Mega Sharpedo ex Gyarados | `l-sharpedo.txt` | Water | 26 | 35 (0.7%) | 3 | unusual (0 copies in this half; 2 cards off) |
| 15 | Whimsicott ex Ariados | `h-whimsicott.txt` | Grass | 37 | 21 (0.4%) | 2 | unusual (only its own copy; 4 cards off) |
| 16 | **Mega Scizor ex Revavroom (new)** | none yet, list below | Metal | 64 | 9 (0.2%) | 1 | - |

`t-` files are in `decks/screen/opponents/` (same cards as `decks/research/`), `h-` in
`rl/results/b2e_card_check_2026-09-26/decks/`, `l-` in `decks/screen/panel_ladder_2026-09-26/`.
"N cards off" is how many of the 20 cards differ from the deck's most common exact list.

**The Metal addition's representative list.**
- **Why this deck.** It is the most-used deck whose lists run Metal alone.
  - All 6 of its lists that state an Energy say Metal, and its attackers are Metal (`lib/card.py`: Mega
    Scizor ex's Bullet Slugger costs [MMC]; Revavroom's attack costs [MC]).
  - Team Rocket's Raticate ex / Terapagos ex has one more list (10), but its lists mix three Energies
    (Psychic+Fighting+Metal, Grass+Psychic+Metal, Fighting+Darkness+Metal), so Metal is not what it runs
    on. 9 against 10 is a tie in any case.
- **Why this list.** Its most common exact list is a two-way tie at 2 copies each, below the 10% bar, so
  the representative is "core plus the most common flex cards" (section 5).
  - That build turns out to equal one of the two tied lists, registered by two different players:
    lockpick04 (219 players, Sept 11, 3-4) and pattyd (68 players, Sept 23, 25th, 3-4).
  - The other tied list is one player (scavagerx) registering it twice.
  - The deck's only top-8 was a different list (acad, 8th of 31, Sept 2).
- **Before use.** The engine's support for these cards was not checked here (no engine run). It needs
  the B2e-style card check (card text plus `goldfish --coverage` at 0 games) before it joins.

```
Energy: Metal
2 Varoom A2b 055
1 Orthworm B2a 077
2 Scyther B2b 001
2 Mega Scizor ex B2b 047
2 Revavroom B2b 050
1 Cyrus A2 150
1 Red A2b 071
2 Poké Ball P-A 005
2 Professor's Research P-A 007
2 Copycat B1 225
2 Metal Core Barrier B2 148
1 Training Area B2 153
```

**If the gauntlet grows, the next two** are the biggest usage gaps. For both, the most common exact list
is played often enough to be the representative:
- **Dragonair Mega Rayquaza ex** (rank 7; Energy Fire + Lightning in all 101 lists that state it). Its
  most common list has 19 of 143 copies (13%).
  - The repo already has `rl/results/kt_carrier_census_2026-09-26/decks/c-dragonair_mega_rayquaza_ex.txt`.
  - That file is 4 cards off the most common list and carries Skull Fossil, which only 2% of lists run, so
    the most common list is the better gauntlet list.
- **Mega Altaria ex Greninja** (rank 10; Psychic). Its most common list has 40 of 125 copies (32%).
  There is no list in the repo.

```
Energy: Fire, Lightning                    Energy: Psychic
2 Dratini B2b 051                          2 Froakie A1 087
2 Gouging Fire B3a 054                     2 Greninja A1 089
2 Dragonair B4 117                         1 Mega Altaria ex B1 102
1 Mega Rayquaza ex B4 120                  2 Swablu B1 196
1 Sabrina A1 225                           1 Bonsly B3 078
1 Pokémon Center Lady A2b 070              1 Oricorio B4 078
2 Poké Ball P-A 005                        1 Cyrus A2 150
2 Professor's Research P-A 007             2 Poké Ball P-A 005
2 Copycat B1 225                           2 Rare Candy A3 144
1 Ancient Booster Energy Capsule B3a 069   2 Professor's Research P-A 007
1 Professor Sada B3a 072                   2 Copycat B1 225
1 Small Balloon B3b 064                    1 Hiking Trail B2b 069
2 Rainbow Cave B4 155                      1 Small Balloon B3b 064
```

The same card check applies to both.

## 2. Usage (development half)

4,722 lists from 63 events; 477 top-8 finishes (a list whose placing is 8 or better). Ranked by lists.
"Sept 10" is the rank in `decks/classifier/limitless_2026-09-10.json`, a different window.

| Rank | Deck | Lists | Share | Top-8 | Top-8 rank | Sept 10 | Energy | In gauntlet |
|---|---|---|---|---|---|---|---|---|
| 1 | Mega Lucario ex Lucario | 398 | 8.4% | 43 | 2 | 1 | Fighting | yes |
| 2 | Mega Altaria ex Espeon | 336 | 7.1% | 51 | 1 | 2 | Psychic | yes |
| 3 | Butterfree Mega Sceptile ex | 244 | 5.2% | 30 | 4 | 3 | Grass | yes |
| 4 | Vespiquen ex Shuckle ex | 233 | 4.9% | 33 | 3 | 4 | Grass | yes |
| 5 | Suicune ex Baxcalibur | 200 | 4.2% | 22 | 5 | 5 | Water | yes |
| 6 | Team Rocket's Weezing ex Hoopa ex | 152 | 3.2% | 16 | 8 | 6 | Darkness | yes |
| 7 | Dragonair Mega Rayquaza ex | 143 | 3.0% | 15 | 9 | 22 | Fire + Lightning | **no** |
| 8 | Hydreigon Mega Absol ex | 139 | 2.9% | 12 | 12 | 8 | Darkness | yes |
| 9 | Hoopa ex Mega Absol ex | 128 | 2.7% | 20 | 6 | 14 | Darkness | yes |
| 10 | Mega Altaria ex Greninja | 125 | 2.6% | 18 | 7 | 16 | Psychic | **no** |
| 11 | Mega Manectric ex Heliolisk | 111 | 2.4% | 11 | 13 | 11 | Lightning | yes |
| 12 | Mega Blaziken ex | 108 | 2.3% | 9 | 16 | 7 | Fire | yes |
| 13 | Mega Charizard Y ex Entei ex | 106 | 2.2% | 13 | 11 | 12 | Fire | yes |
| 14 | Mega Sceptile ex Greninja | 98 | 2.1% | 10 | 15 | 9 | Grass | no |
| 15 | Dedenne ex Indeedee ex | 95 | 2.0% | 11 | 14 | 17 | Lightning | no |
| 16 | Magnezone Miraidon ex | 90 | 1.9% | 15 | 10 | 13 | Lightning | no |
| 17 | Magnezone ex Magnezone | 65 | 1.4% | 5 | 21 | 15 | Lightning | no |
| 18 | Mega Blaziken ex Greninja | 63 | 1.3% | 8 | 17 | 20 | Fire | no |
| 19 | Team Rocket's Raticate ex Alolan Ninetales ex | 55 | 1.2% | 3 | 28 | 10 | Water | yes |
| 20 | Zoroark ex Mega Absol ex | 54 | 1.1% | 5 | 22 | - | Darkness | no |
| 21 | Milotic ex Eevee ex | 51 | 1.1% | 7 | 18 | 18 | Water | no |
| 22 | Beautifly Dustox | 47 | 1.0% | 5 | 23 | - | Grass | no |
| 23 | Mega Altaria ex | 44 | 0.9% | 6 | 19 | 19 | Psychic | no |
| 24 | Mega Altaria ex Chingling | 38 | 0.8% | 2 | 35 | 27 | Psychic | no |
| 25 | Garchomp | 36 | 0.8% | 1 | 48 | 21 | Water + Fighting | yes |
| 26 | Mega Sharpedo ex Gyarados | 35 | 0.7% | 3 | 29 | 24 | Water | yes |
| 27 | Hoopa ex Mega Sableye ex | 34 | 0.7% | 3 | 30 | - | Darkness | no |
| 28 | Miraidon ex Magnezone | 33 | 0.7% | 4 | 25 | - | Lightning | no |
| 29 | Hoopa ex Greninja | 31 | 0.7% | 3 | 31 | - | Darkness | no |
| 30 | Mega Charizard X ex Mega Charizard Y ex | 30 | 0.6% | 2 | 36 | 23 | Fire | no |
| 37 | Whimsicott ex Ariados | 21 | 0.4% | 2 | 38 | 26 | Grass | yes |
| 64 | Mega Scizor ex Revavroom | 9 | 0.2% | 1 | 59 | - | Metal | proposed |

By top-8 finishes the order is Altaria/Espeon 51, Lucario 43, Vespiquen 33, Sceptile 30, Suicune 22,
Hoopa/Absol 20, Altaria/Greninja 18, Weezing 16, then Rayquaza and Magnezone/Miraidon at 15. Ranks 31 to 40
are in `gauntlet.json` (`usage_top40`).

**How the Energy was decided.**
- 3,010 of the 4,722 lists state their Energy. A deck uses a type when at least half of its lists that
  state an Energy include that type.
- Every deck in the top 40 has at least 9 lists that state it, so the fallback was never needed there.
  The fallback is the attack costs of the Pokémon named in the deck name.
- **Cross-check.** For the 74 decks with 5 or more stating lists:
  - the attack-cost rule gives the same types for 65, and a subset for 1;
  - the 8 disagreements are all decks named after a partner whose attack isn't used (Greninja in four
    decks; Indeedee, Electrode, Goomy and Team Rocket's Magmar in one each), where the attack-cost rule
    would add an Energy the lists don't run.
  - So the lists' own field is the better source.
- All 16 test files' `Energy:` lines equal their deck's Energy by this rule.

## 3. Energy coverage

- **Status rule.**
  - "Covered": two or more of our decks run that Energy alone.
  - "Thin": only one does, or only a two-Energy deck uses it.
  - "Missing": none of our decks uses it.
- **Share of lists** counts every list whose deck uses the type, so two-Energy decks count twice and the
  column adds up to more than 100%.

| Energy | Status | Our decks | Limitless lists of this type | Most-used deck of this type | Most-used not in our set |
|---|---|---|---|---|---|
| Grass | covered | Sceptile, Vespiquen, Whimsicott | 795 (16.8%) | Butterfree Mega Sceptile ex (#3, ours) | Mega Sceptile ex Greninja (#14, 98 lists) |
| Fire | covered | Blaziken, Charizard Y (2 lists) | 583 (12.3%) | Dragonair Mega Rayquaza ex (#7, Fire+Lightning); Fire only: Mega Blaziken ex (#12, ours) | Dragonair Mega Rayquaza ex (#7, 143) |
| Water | covered | Suicune, Raticate/Ninetales, Sharpedo; Garchomp (Water+Fighting) | 665 (14.1%) | Suicune ex Baxcalibur (#5, ours) | Milotic ex Eevee ex (#21, 51) |
| Lightning | **thin** | Manectric | 813 (17.2%) | Dragonair Mega Rayquaza ex (#7, Fire+Lightning); Lightning only: Mega Manectric ex Heliolisk (#11, ours) | Rayquaza (#7); Lightning only: Dedenne ex Indeedee ex (#15, 95) |
| Psychic | **thin** | Altaria/Espeon | 853 (18.1%) | Mega Altaria ex Espeon (#2, ours) | Mega Altaria ex Greninja (#10, 125) |
| Fighting | **thin** | Lucario; Garchomp (Water+Fighting) | 662 (14.0%) | Mega Lucario ex Lucario (#1, ours) | Garchomp Greninja (#38, 21, Water+Fighting); Fighting only: Mega Lucario ex Igglybuff (#48, 14) |
| Darkness | covered | Hydreigon, Weezing, Hoopa/Absol | 723 (15.3%) | Team Rocket's Weezing ex Hoopa ex (#6, ours) | Zoroark ex Mega Absol ex (#20, 54) |
| Metal | **missing** | none | 69 (1.5%); decks running Metal alone: 41 (0.9%) | Metal alone: **Mega Scizor ex Revavroom** (#64, 9); any Metal: TR Raticate ex Terapagos ex (#59, 10) | same |

**The fewest additions for one deck per Energy type: one, the Metal deck.**
- The three thin types don't need an addition to be covered. For Lightning and Psychic, the obvious
  thickeners are the two usage gaps (Rayquaza, Altaria/Greninja).
- Fighting is essentially one deck on Limitless (Lucario's 398 lists; the next Fighting-only deck has 14),
  so there is nothing worth adding.
- The full list of the 34 decks that use Metal is in `gauntlet.json` → `energy_coverage` → `Metal`.

## 4. Coverage, cost and the ladder (Dustin's addition)

### (a) Share of the development half covered

| Version | Decks | Lists covered | Top-8 finishes covered | Dustin's 33 ladder games, exact name | ... counting variants of the table decks |
|---|---|---|---|---|---|
| 8 table decks | 8 | 38.3% | 45.3% | 9 (27%) | 15 (45%) |
| + 6 held-out decks | 14 | 48.0% | 55.8% | 14 (42%) | 20 (61%) |
| + 2 ladder-panel lists (adds Sharpedo; Charizard Y was already in) | 15 | 48.8% | 56.4% | 16 (48%) | 22 (67%) |
| + the Metal deck | 16 | 48.9% | 56.6% | 16 (48%) | 22 (67%) |
| + Rayquaza and Altaria/Greninja | 18 | 54.6% | 63.5% | 17 (52%) | 23 (70%) |
| + the rest of the usage top 18 | 23 | 63.3% | 73.8% | 17 (52%) | 23 (70%) |

### (b) The cumulative curve (decks taken in usage order)

| Target | Decks needed | Lists | Top-8 | Which | Already have a list in the repo |
|---|---|---|---|---|---|
| 50% | 13 | 51.3% | 61.4% | ranks 1-13 (section 2) | 12 of 13; missing Mega Altaria ex Greninja |
| 60% | 18 | 60.0% | 71.7% | + Mega Sceptile ex Greninja, Dedenne ex Indeedee ex, Magnezone Miraidon ex, Magnezone ex Magnezone, Mega Blaziken ex Greninja | 13 of 18 (Magnezone ex Magnezone has `c-magnezone_ex_magnezone.txt`, the most common list) |
| 70% | 30 | 70.3% | 80.9% | + ranks 19-30 | 16 of 30 |
| 80% | 56 | 80.1% | 90.4% | + ranks 31-56 | 19 of 56 |

- "A list in the repo" means one of our 16 test files, or another file outside `decks/dustin/` and
  `decks/brews/` whose closest development list (17 or more of 20 cards shared) is that deck.
- The other files are the `decks/variants-2026-09-23/` lists, the kt census `c-` lists and the pull's
  `decklists/`. The full per-rank list is `cumulative_curve_top40` and `coverage_levels` in the JSON.
- Three of the six decks between ranks 10 and 18 that we don't have are Greninja-partner versions of decks
  we do have (Altaria, Sceptile, Blaziken). Their Pokémon line differs (Froakie and Greninja), so for the
  engine they are different decks. On the ladder they look like a known deck with a Greninja.

### (c) Cost per candidate reading

- **"Pilot reading":**
  - Every deck in the version plays each of the 8 table decks (the core), and the 8 play each other
    (today's 28 pairings).
  - Each pairing is 500 games, 250 in each seat.
  - A full round robin (every pair of decks) is shown for comparison.
- **"Brew reading":** one brew plays every deck in the version, 500 games each.
- **"Limitless-checkable pairings":** pilot-reading pairings with 30 or more Limitless matches in the
  development half. Only these can be compared with real results.
- The margins are 95% margins on a brew's average win rate near 50%.

| Version | Decks | Pilot reading: pairings / games | Limitless-checkable pairings | Full round robin, games | Brew reading, games | Brew average ±, equal weights | ± with usage weights (same games) | Usage weights act like N decks |
|---|---|---|---|---|---|---|---|---|
| 8 table decks | 8 | 28 / 14,000 | 23 | 14,000 | 4,000 | 1.5 | 1.7 | 6.8 |
| + 6 held-out | 14 | 76 / 38,000 | 34 | 45,500 | 7,000 | 1.2 | 1.4 | 9.8 |
| + 2 ladder lists | 15 | 84 / 42,000 | 34 | 52,500 | 7,500 | 1.1 | 1.4 | 10.1 |
| + Metal (the Energy gauntlet) | 16 | 92 / 46,000 | 34 | 60,000 | 8,000 | 1.1 | 1.4 | 10.2 |
| + the two gaps | 18 | 108 / 54,000 | 43 | 76,500 | 9,000 | 1.0 | 1.3 | 11.8 |
| + rest of the usage top 18 | 23 | 148 / 74,000 | 53 | 126,500 | 11,500 | 0.9 | 1.1 | 15.0 |
| usage top 13 (50%) | 13 | 68 / 34,000 | 43 | 39,000 | 6,500 | 1.2 | 1.4 | 10.6 |
| usage top 18 (60%) | 18 | 108 / 54,000 | 53 | 76,500 | 9,000 | 1.0 | 1.2 | 13.6 |
| usage top 30 (70%) | 30 | 204 / 102,000 | 54 | 217,500 | 15,000 | 0.8 | 1.0 | 18.1 |
| usage top 56 (80%) | 56 | 412 / 206,000 | 54 | 770,000 | 28,000 | 0.6 | 0.9 | 23.1 |

**Compared with a usage-weighted panel.**
- **Same cost.** Weighting each deck's result by its Limitless share costs the same games if every deck
  keeps 500 games per pairing. It changes the readout, not the bill.
- **No extra coverage.** The Energy gauntlet still stands for 49% of lists whichever way its results are
  weighted.
- **Noisier.** The weighted average is somewhat noisier: 16 decks weighted by share behave like about 10
  equal ones (±1.4 against ±1.1 points).
- **It works against the Energy goal.** The Metal deck would carry 0.4% of the weight.
- **Spending games by share instead** (same 8,000 total for a brew) keeps the precision, but gives Lucario
  1,378 games and the Metal deck 31. The small decks' own results then can't be read.
- **Two things set the cost:**
  - Games grow with the number of pairings because of the 500-per-pairing floor, not because the average
    needs them. The brew average is within ±1.5 points at every version.
  - For pilot readings checked against Limitless, only 23 pairings are checkable today and at most 54 ever
    are. Beyond the usage top 18, new decks add cells that nothing real can check. There, weighting cells
    by their Limitless match count is natural and costs nothing extra.
- **For scale only.** The ladder-panel smoke measured about 2 s a game on the laptop under load. At that
  pace 46,000 games is roughly 26 laptop-hours; parallel or cloud runs are faster.

### (d) Cross-check with Dustin's ladder (`decks/screen/panel_ladder_2026-09-26/ladder_mapping.csv`)

The ladder columns of table (a):
- **The table decks alone** match 9 of his 33 games by exact name. `ladder_counts.md` says 10: the
  skeptic pass renamed one game to "Mega Blaziken ex Castform Sunny Form", which is a separate Limitless
  name for the same list as ours, so it counts under "variants" here.
- **Today's 16 lists** match 16 exact and 22 with variants.
- **Usage alone** does worse at the same size: the usage top 13 and top 18 both match 13 exact (19 with
  variants), because Sharpedo, Garchomp and Whimsicott, which he met, rank 25th to 37th.
- **The usage top 56** reaches 22 exact (25 with variants).
- **Never covered** by any version here (8 games, one each): Milotic ex Igglybuff, Rotom ex, TR Raticate
  ex / Mega Lucario ex, Vaporeon ex / Greninja ex, Growlithe / Lillipup, Dustox / TR Magmar, Mega
  Kangaskhan ex, and the homebrew poison pile.
- **Small sample.** 33 games is small: one game is 3 points.

## 5. List variation

**Terms.**
- **"Most common list"** is the modal exact 20-card list. Printings with identical database text (alternate
  arts) count as the same card.
- **"Core"** cards are in at least 90% of lists, at the count that at least 90% run.
- **"Flex slots"** are the other 20 minus core slots.
- **Flex copies per list** splits the non-core cards into Pokémon and Trainers.
- **Our list's class:**
  - "most common" means it is the modal list;
  - "common variant" means at least 3 exact copies and 2% of lists, or every card count in it is shared by
    at least 10% of lists;
  - "unusual" means neither.
  - A list taken from this data always matches itself once, so exact copies count only from 3.

| Deck | Lists | Different lists | Most common list's share | Lists needed to cover half | Typical list, cards off the most common | Core / flex slots | Flex copies: Pokémon / Trainer | Most common Pokémon line | Our list |
|---|---|---|---|---|---|---|---|---|---|
| Lucario | 398 | 146 | 16.3% | 15 | 3 | 11 / 9 | 4.0 / 5.0 | 25% | most common |
| Altaria/Espeon | 336 | 43 | 42.9% | 2 | 1 | 16 / 4 | 1.2 / 3.1 | 70% | most common |
| Sceptile | 244 | 44 | 70.9% | 1 | 0 | 18 / 2 | 0.1 / 2.1 | 93% | most common |
| Vespiquen | 233 | 55 | 29.6% | 2 | 1 | 15 / 5 | 3.6 / 1.7 | 37% | most common |
| Suicune | 200 | 64 | 9.0% | 9 | 2 | 15 / 5 | 1.1 / 4.1 | 89% | common variant |
| Weezing/Hoopa | 152 | 55 | 15.8% | 5 | 2 | 16 / 4 | 1.1 / 3.3 | 44% | common variant |
| Hydreigon | 139 | 38 | 58.3% | 1 | 0 | 17 / 3 | 0.2 / 3.0 | 78% | most common |
| Hoopa/Absol | 128 | 37 | 33.6% | 3 | 1 | 15 / 5 | 0.1 / 5.1 | 95% | common variant |
| Manectric | 111 | 29 | 62.2% | 1 | 0 | 16 / 4 | 1.5 / 2.8 | 67% | most common |
| Blaziken | 108 | 12 | 81.5% | 1 | 0 | 19 / 1 | 0.0 / 1.1 | 99% | most common |
| Charizard Y | 106 | 52 | 15.1% | 9 | 2 | 14 / 6 | 2.5 / 3.7 | 43% | both common variants |
| Raticate/Ninetales | 55 | 30 | 18.2% | 8 | 3 | 13 / 7 | 1.5 / 5.8 | 49% | most common |
| Garchomp | 36 | 29 | 13.9% | 11 | 6 | 8 / 12 | 4.4 / 7.7 | 19% | common variant |
| Sharpedo | 35 | 16 | 22.9% | 3 | 1 | 16 / 4 | 2.0 / 2.3 | 66% | unusual |
| Whimsicott | 21 | 17 | 14.3% | 7 | 4 | 12 / 8 | 2.2 / 6.1 | 62% | unusual |
| Scizor (new) | 9 | 7 | 22.2% (tie) | 3 | 4 | 9 / 11 | 4.6 / 6.4 | 22% | - |

**A counting effect to know.** When players split between two printings of the same Pokémon with
different attacks, neither printing reaches 90%. The Pokémon then shows as flex although every list runs
one. This inflates the Pokémon flex numbers for:
- Lucario (Riolu A2 091 Jab / B3 079 Fighting Fist);
- Charizard Y (three Charmanders);
- Sharpedo (two Magikarps);
- Manectric (two Electrikes);
- Vespiquen (two Combees);
- Raticate (two Alolan Vulpix);
- Scizor (two Varooms).

Even so, Trainers make up more of the flex than Pokémon in 15 of 16 decks. Vespiquen is the exception: a
third of its lists add Vespiquen A2 018, and the Combee printing and the second Shuckle ex vary.

**Per deck.** Shares are of that deck's lists. The full core and flex lists, with counts, are in
`gauntlet.json` → `variation`.

- **Mega Lucario ex Lucario.**
  - Core: 2 Mega Lucario ex, 1 Lucario A2 092, Korrina, Arena of Antiquity, Cyrus, 2 Professor's
    Research, 2 Poké Ball, 1 Copycat.
  - Flex: X Speed 86%, Field Blower 84%, Bonsly 83%, 2nd Copycat 76%, Pokémon Center Lady 75%, Hitmonlee
    64%, Riolu A2 091 60%, Riolu B3 079 59%, Lucky Ice Pop 57%, Protective Poncho 53%, Hitmontop 27%,
    Sabrina 21%.
  - Ours is the most common list (65 of 398). Even so, only a quarter of lists share its Pokémon line.
- **Mega Altaria ex Espeon.**
  - Core: the whole Pokémon line except a 2nd Swablu, plus Sabrina, Training Area, 2 Professor's Research,
    2 Poké Ball, 1 Copycat.
  - Flex: 2nd Copycat 85%, 2nd Swablu 84%, Small Balloon 76%, Field Blower 71%, Cyrus 47%, 2nd Igglybuff
    21%.
  - Ours is the most common list (144).
- **Butterfree Mega Sceptile ex.**
  - Core: 18 of 20 cards.
  - Flex: Sabrina 90%, Erika 84%, X Speed 9%, Teal Mask Ogerpon ex 6%.
  - Ours is the most common list (173).
- **Vespiquen ex Shuckle ex.**
  - Core: 2 Vespiquen ex, 1 Shuckle ex, Teal Mask Ogerpon ex, 2 Leaf Cape, 2 Fragrant Forest, Sabrina,
    Cyrus, Field Blower, X Speed, 2 Professor's Research, 1 Copycat.
  - Flex: 2nd Shuckle ex 90%, Combee B4 010 85%, 2nd Copycat 84%, 2nd X Speed 46%, Vespiquen A2 018 33%,
    Erika 15%, Combee A2 017 13%.
  - Ours is the most common list (69).
- **Suicune ex Baxcalibur** (the most spread of the big decks).
  - Core: 2 Suicune ex, 2 Baxcalibur, 1 Frigibax B2a 034, Chien-Pao ex, 2 Rare Candy, 2 Poké Ball, 2
    Professor's Research, 1 Copycat, 1 Giant Cape, Inflatable Boat.
  - Flex: 2nd Frigibax B2a 034 89%, Soothing Shore 76%, Pokémon Center Lady 74%, 2nd Giant Cape 72%, Field
    Blower 51%, Team Rocket's Boss 36%, Mars 31%, 2nd Copycat 24%.
  - The Pokémon hardly vary (89% the same); the spread is Trainers.
  - Ours: 13 copies, 3 cards off the most common. It runs Field Blower, Team Rocket's Boss and Frigibax
    P-B 037 (Stiffen) where the most common runs a 2nd Giant Cape, Mars and a 2nd Frigibax B2a 034
    (Chilly). Only 8% of lists share its Pokémon line.
- **Team Rocket's Weezing ex Hoopa ex.**
  - Core: 2 Hoopa ex, 2 Koffing, 2 Weezing ex, 2 Cyrus, 2 Deceptive Needle, X Speed, 2 Professor's
    Research, 2 Poké Ball, 1 Copycat.
  - Flex: Lucky Ice Pop 73%, Pokémon Center Lady 60%, Field Blower 50%, Mega Absol ex 49%, 2nd Copycat
    34%, Darkrai ex 24%, Mega Sableye ex 23%.
  - The fourth Pokémon varies: Mega Absol ex 44%, Mega Sableye ex 23%, Darkrai ex 16%.
  - Ours: 10 copies, 4 cards off. It runs Darkrai ex, Mars, a 2nd Copycat and Field Blower instead of
    Mega Absol ex, Pokémon Center Lady and 2 Lucky Ice Pop. Its single Mars is run by 9% of lists.
- **Hydreigon Mega Absol ex.**
  - Core: 17 of 20.
  - Flex: 2nd Deceptive Needle 86%, Sabrina 80%, 2nd Lucky Ice Pop 78%, Pokémon Center Lady 13%.
  - Ours is the most common list (81).
- **Hoopa ex Mega Absol ex.**
  - The Pokémon are fixed (95%).
  - Flex: 2nd Lucky Ice Pop 90%, Repel 79%, Pokémon Center Lady 76%, X Speed 68%, Starting Plains 46%,
    2nd Copycat 44%, Mars 41%, Small Balloon 33%.
  - Ours: 15 copies, 1 card off (Starting Plains instead of Mars).
- **Mega Manectric ex Heliolisk.**
  - Flex: Elegant Cape 87%, Field Blower 81%, Electrike B2b 026 80%, Training Area 78%, Electrike P-B 043
    24%.
  - Ours is the most common list (69).
- **Mega Blaziken ex.**
  - Core: 19 of 20.
  - Flex: Rocky Helmet 89%, Sabrina 13%.
  - Ours is the most common list (88).
- **Mega Charizard Y ex Entei ex.**
  - Core: 2 Entei ex, 1 Mega Charizard Y ex, 2 Charmeleon, 2 Flame Patch, Wally, Rainbow Cave, 2 Poké
    Ball, 2 Professor's Research, 1 Copycat.
  - Flex: Pokémon Center Lady 83%, Giant Cape 76%, Charmander B2b 007 75%, Lucky Ice Pop 55%, 2nd Rainbow
    Cave 42%, Charizard B1a 013 35%, Sabrina 26%, 2nd Copycat 21%, Protective Poncho 21%.
  - `h-` is 1 card off the most common (a 2nd Copycat instead of a 2nd Rainbow Cave).
  - `l-` is 2 cards off (a 2nd Copycat and Protective Poncho instead of Pokémon Center Lady and Lucky Ice
    Pop).
  - The most common list (16 copies) is neither. This answers the ladder panel's open question 5 with
    numbers: `h-` is the closer one, `l-` the more copied (4 against 3).
- **Team Rocket's Raticate ex Alolan Ninetales ex** (a Trainer-heavy spread: 5.8 flex Trainer copies per
  list).
  - Flex: Elegant Cape 82%, 2nd Alolan Vulpix 78%, Sabrina 76%, Soothing Shore 64%, 2nd Copycat 55%,
    Training Area 42%, Sightseer 38%, Repel 29%, Team Rocket Grunt 29%.
  - Ours is the most common list (10 of 55).
- **Garchomp** (the least settled deck: a typical list is 6 cards off the most common).
  - Core: only 8 slots.
  - Flex: 2nd Cynthia 86%, Mantyke 81%, 2nd Gible 81%, 2nd Garchomp 78%, Rainbow Cave 78%.
  - Ours has 3 exact copies, but it is 8 cards off the most common, and 8% share its Pokémon line (Gible
    A2 121, Cleffa, Happiny). With 36 lists, "most common" means little here.
- **Mega Sharpedo ex Gyarados.**
  - Core: 2 Wallace and 1 Lisia (both in all lists).
  - Flex: Training Area 83%, Magikarp A4 044 74%.
  - Ours is unusual. It runs 2 Lisia (6% of lists) and 1 Wallace (9%). The most common list (8 copies)
    runs 1 Lisia, 2 Wallace and Pokémon Center Lady instead of Soothing Shore.
  - Ours came from a holdout-half event, so it has no copy in this half.
- **Whimsicott ex Ariados.**
  - Ours is unusual: its Pheromosa is in 1 of 21 lists (its own).
  - It is 4 cards off the most common: Cyrus, Pheromosa, a 2nd Quick-Grow Extract and a 2nd Fragrant
    Forest instead of Sabrina, a 2nd Leaf Cape, a 2nd Copycat and X Speed.
  - 21 lists are too few to call any list typical.
- **Mega Scizor ex Revavroom (new).**
  - Core: 2 Scyther, 1 Mega Scizor ex, 2 Revavroom, Cyrus, 2 Professor's Research, 1 Copycat.
  - Flex: Metal Core Barrier 89%, Poké Ball 89%, Red 78%, Varoom A2b 055 78%, 2nd Mega Scizor ex 78%,
    Orthworm 67%.

## 6. Two ways to test list variation

Both use the same four decks: the most-used decks (usage rank 15 or better) whose most common list is
under 20% of their lists. They are Suicune (9%), Charizard Y (15%), Weezing (16%) and Lucario (16%).
Garchomp, Whimsicott and Raticate vary as much, but they are small (21 to 55 lists).

**The second list** for each is a real, often-registered list at least 2 cards from ours:

| Deck | Second list | How it differs from our list |
|---|---|---|
| Lucario | 2nd most common, 20 copies (5%) | 2 Riolu A2 091 and Lucky Ice Pop, for 2 Riolu B3 079 and Protective Poncho |
| Suicune | the most common, 18 copies (9%) | 2nd Giant Cape, Mars and a 2nd Frigibax B2a 034, for Field Blower, Team Rocket's Boss and Frigibax P-B 037 |
| Weezing | the most common, 24 copies (16%) | Mega Absol ex, Pokémon Center Lady and 2 Lucky Ice Pop, for Darkrai ex, Mars, 2nd Copycat and Field Blower |
| Charizard Y | `l-charizardy.txt`, already on file, 4 copies | 2 cards from `h-charizardy_entei.txt` |

Three new list files would be needed (the Charizard pair exists). The lists are in `gauntlet.json` →
`variation` → each test's `twin`.

**Proposal A: second lists, in the big gauntlet only.**
- **How it runs.** Each second list plays the other 15 decks' main lists. It does not play its own main
  list or the other second lists. The small bug-finding tests don't change.
- **Cost.** 4 × 15 = 60 pairings = **+30,000 games per gauntlet run**, on top of the 60,000-game round
  robin (+50%).
- **Cheaper version.** The second lists play only the 8 table decks: 29 pairings = **+14,500 games**
  (+24%).
- **The broad version is too costly.** "A second list for every deck whose most common list is under half
  its lists" would be 12 decks. That adds 90,000 games (or 45,500 against the table decks), more than the
  gauntlet itself.

**Proposal B: a one-off sensitivity check** (once per new engine or confirmed pilot, not per candidate).
- **What plays.** Each of the four decks plays the 8 table decks (7 for a table deck) in three versions,
  on the same seeds as its main list:
  - its second list;
  - two single-card Trainer swaps. Each swap puts in the most common Trainer our list lacks, in place of
    our list's least common Trainer choice.
- **The swaps:**
  - Lucario: Lucky Ice Pop (57% of lists) for Protective Poncho; Sabrina (21%) for Pokémon Center Lady.
  - Suicune: 2nd Giant Cape (72%) for Team Rocket's Boss; Mars (31%) for Field Blower.
  - Weezing: Lucky Ice Pop (73%) for Mars; Pokémon Center Lady (60%) for the 2nd Copycat.
  - Charizard Y (`h-`): 2nd Rainbow Cave (42%) for the 2nd Copycat; Sabrina (26%) for Lucky Ice Pop.
- **Cost.** 3 versions × 7 or 8 opponents × 500 = **43,500 games, once**. The second lists alone are
  14,500.
- **Reading rule, set in advance.**
  - If no version moves its deck's average against the table decks by 3 points or more, one list per deck
    is enough and A isn't needed.
  - If one does, that deck's second list joins the big gauntlet (A for that deck only).
- **What 500 games per pairing can see.**
  - One pairing's 95% margin is about ±4.4 points.
  - A version's average over 7 or 8 opponents is about ±1.6.
  - The difference between a version and the main list is about ±2.3 at most (less when the same seeds
    help).
  - So shifts of about 3 points show up. Single-pairing differences under about 5 points don't, as
    START_HERE says for card-against-card tests.

**Suggested order:** B first, then A only for decks where B found a shift.

## 7. What the data can't show

- **Which cards anyone drew or played, or whether a flex card helped.** These are registered lists. A
  card's rate is how popular it is, not how good it is. Popular lists also spread by copying.
- **How a player pilots a variant.** The bot plays every list the same way.
- **Families.** Limitless's deck names come from its own classifier, so one deck can sit under two
  names. Our Blaziken list is also "Mega Blaziken ex Castform Sunny Form" (19 more lists), and the Greninja
  partners are separate names. Exact-name coverage therefore understates families.
- **Time and set.** This is the development half only (63 of 126 events, Aug 26 to Sept 24). Nothing after
  Sept 24 is included, and a new set would reshuffle the ranks.
- **Energy for 36% of lists.** 1,712 lists state no Energy; they were given their deck's majority Energy.
- **Top-8.** A top-8 finish is a placing of 8 or better in an event of any size (the smallest had 6
  players). 1,284 lists have no placing.
- **Tournaments are not the ladder.** Dustin's 33 logged games are the only ladder evidence, and one game
  is 3 points.
- **Other sources' alternatives.** game8 and similar sites were not read. What our 4,722 lists give is
  every alternative tournament players actually registered, with how often. They don't give editorial
  suggestions or reasons.
- **Engine readiness.** Whether the engine implements every card in the Scizor, Rayquaza and
  Altaria/Greninja lists was not checked, because no engine was run.

## 8. Method and checks

- **Source.** `rl/results/limitless_skill_model_2026-09-25/raw/<event>_standings.json.gz` and
  `_details.json.gz` for the 63 development ids in `split.json`.
  - The script builds file paths only from development ids and asserts it never opens a holdout id.
  - `matches.csv` is read for `split == development` rows only, to count Limitless matches per pairing.
  - 4,884 entries; 4,722 with a decklist; all 20 cards; every card id is in `lib/deckgym-database.json`.
- **Deck = exact Limitless `deck.name`.**
  - Each test file's deck comes from its Limitless deck id (`deck_mapping.json`; the two ladder lists by
    their ids in the ladder-panel README).
  - Every id maps to one name in this half.
- **Dustin's decks.** Only `decks/dustin/` and `decks/brews/` are his. None of their files is used or
  counted as a test list. Decks he also plays (Manectric, Garchomp, Raticate/Ninetales, Hoopa/Absol,
  Whimsicott/Ariados, Charizard Y/Entei, Blaziken) stay test decks, per the rule.
- **Checks:**
  - **Independent recount.** A separate script used raw set and number ids without merging reprints; it
    was run from the session scratchpad and not added here. It matches all of the following:
    - the totals (4,722 lists, 477 top-8 finishes);
    - the curve points (13, 18, 30, 56);
    - every coverage share in 4(a);
    - lists, top-8, usage rank, most-common-list share and number of different lists for all 18 decks
      named here;
    - the exact-copy counts of all 16 test files;
    - the ladder exact-name counts.
  - **Against earlier work.**
    - 144 lists equal `t-altaria.txt` and 235 share its Pokémon line
      (`opening_active_census_2026-09-26/limitless_carriers.md` has the same).
    - The two Altaria variant files recur in 34 and 27 lists (same).
    - The Altaria/Greninja, bare Altaria, Chingling and Igglybuff list counts (125, 44, 38, 25) equal the
      kt carrier census.
  - **Files.** `decks/research/*.txt` equal `decks/screen/opponents/t-*.txt` card for card, Energy
    included (all 8).
  - **Cards.** The Scizor list's cards and the Frigibax, Riolu, Pheromosa, Lisia and Wallace printings
    named above were read with `lib/card.py`.

## 9. Files

- `README.md`: this file.
- `gauntlet.py`: the script (WSL `python3`, standard library only; run from the repo root). It writes
  `gauntlet.json` and prints a summary.
- `gauntlet.json`, with these parts:
  - `data`: counts.
  - `usage_top40`.
  - `energy_coverage`: per type, including all 34 Metal decks.
  - `additions`: the Metal deck, its list, who registered it, and its top-8 list.
  - `variation`: per gauntlet deck, including the core, flex alternatives, Pokémon lines, the most common
    and core-plus-flex lists, the test lists' classes, second lists and swaps.
  - `variation_growth_candidates`: the 7 usage-top-18 decks not in the gauntlet.
  - `variation_spread_ranking`.
  - `proposal_A_twins` and `proposal_B_sensitivity`.
  - `coverage_levels`: the (a), (c) and (d) numbers, per version.
  - `cumulative_curve_top40`.
  - `repo_list_files`: every repo list and the deck it matches.
