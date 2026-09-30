Decision this informs: none on its own. This is the cloud's build of switch N1 as a new preset, `kn<N>` (the Fable coordinator via Dustin, Sept 30: "build switch N1 as parked in rl/results/trainer_pricing_2026-09-28/REGISTRATION_DRAFT.md ('Appendix. Parked: N1') … as a new preset kn<N> (km + N1) … with N1 off reproducing km exactly").
- It is not registered. The registration text is the laptop's and Dustin's.
- No table game was played, there was no identity replay, and nothing was merged.
- **The build is commit `71877f6`,** which changes `engine/src/players/` only (three files).

Seeds: only Claude diagnostic seeds, and only scratch decks.
- The unit tests' random games use 20,950,000,000 + 10 × pair + game, and their 200 deals 20,951,000,000 + i.
- The smoke uses 20,960,000,000 + 100,000 × deck + 10,000 × opponent + 5,000 × seat + game.

# kn: km + N1, the opponent's Active Retreat Cost in the score (Sept 30)

## In plain words

- **kn3 is km3 with one change.** The score now counts the opponent's Active Retreat Cost the way it already counted its own: +1 for each Energy of theirs, −1 for each of its own.
  - It uses the same board cost the engine computes (Goo-zooka's +1, Trap Territory, Peculiar Plaza, Small Balloon, Inflatable Boat and the rest) and the same weight.
  - Nothing else changes. With the switch off, kn3 plays exactly as km3, checked move for move on 200 scratch deals.
- **The play rate moves** (the smoke, on scratch decks, 600 games a deck and code):
  - **Goo-zooka:**
    - In a plain Goo-zooka deck, km3 plays it on 0.1% of its chances and kn3 on 86%.
    - In a Grass Knot deck (Whimsicott ex, whose attack reads the raised cost), km3 plays it on 18% and kn3 on 88%.
  - **Peculiar Plaza:** 96% under both where it helps only the bot's own side. Against a Psychic deck, where it helps both sides, it falls from 100% to 29%.
  - **A control deck with no N1 card** (Cyrus and Sabrina, against lists with Small Balloon and Inflatable Boat): 2 of 600 games differ.
- **kn3 plays Goo-zooka at its first chance** (median turn 2, against turn 7 to 8 for km3's rare plays).
  - Under N1 the play is level with not playing it: +1 for the effect, −1 for the card leaving the hand. The tie goes to the play by the order the moves are listed in.
  - The parked text predicted this ("In Trail-less matchups it rises by the tie-break", N1's "Honest size").
  - So kn3 spends the card early rather than on the turn it matters. The unplayed-Trainer diagnosis found the turns it matters: after a gust, or when the opponent's Active is one Energy short of retreating (`../trainer_unplayed_diag_2026-09-30/`).
- **In the Grass Knot deck this cost the attack its bonus.**
  - km3 played Goo-zooka 360 times, 359 of them just before a Grass Knot that same turn (30 more damage).
  - kn3 played it 677 times, only 120 of them before a Grass Knot.
  - On the same deals that deck won fewer games with kn3: 23 won only with km3 against 3 only with kn3 (against the Psychic deck), and 17 against 3 (against the Water deck).
  - The plain Goo-zooka deck and the Plaza deck show no such gap.
  - These are scratch decks and 200 deals a row. They describe these games, not strength. Dustin's caution applies as written: "Goo-zooka being played more often is a footprint, not a gain, and the footprint alone doesn't confirm the switch."

## What was built (`git diff cae37a3 71877f6 -- engine/`)

- **`value_functions.rs`:**
  - **The flag.** `EvalFeatures` gets `opponent_retreat_cost`. It is false in `OFF`, `KQ`, `KD` and `KPR` (the presets that list every field), and so in every preset but the new `KN = EvalFeatures { opponent_retreat_cost: true, ..EvalFeatures::KM }`.
  - **The value function.** `public_clock_effect_kn_value_function` is km's call with `KN`.
  - **The term.** The score's one-sided `(−my.active_retreat_cost) × weight` becomes `(opp.active_retreat_cost − my.active_retreat_cost) × weight` with the flag on.
    - It stays in the same place in the sum, as the parked text's implementation constraint asks.
    - With the flag off it is the same expression, added in the same order, so km's value is bit for bit what it was (tested below).
    - The opponent's cost was already extracted for the score (`extract_features`, through `get_active_retreat_cost`, the board cost without this turn's discounts) and then dropped. No new function reads anything.
  - **Setup is untouched:** the setup evaluation never reads the opponent, whose board is masked.
- **`mod.rs`:**
  - `PlayerCode::KN`;
  - its parser line, `kn<N>`, before `k<N>`, which would reject it. No other code starts with `kn`; km's line and the others are unchanged;
  - its arm in `get_player`, the same pilot as km: public pricing, depth N, no opponent ply.
- **`public_pricing_player.rs`:** the two wiring tests only.

## Tests (all pass)

| test | what it shows |
|---|---|
| `kn_is_km_plus_n1_and_nothing_else` | `KN` with its flag cleared equals `KM`, every field; all 19 other presets have the flag off |
| `n1_the_term_is_the_opponents_active_retreat_cost` | Actives with costs 0 to 3 on each side: kn − km = the opponent's cost, from both players' views (the parked "N1, the term") |
| `n1_reads_the_board_cost_the_engine_computes` | kn − km equals the engine's own board cost of the opponent's Active: printed 2; Goo-zooka 3; Trap Territory 3; Plaza on a [P] Active 0 and on a non-[P] Active 2; Small Balloon 1; Inflatable Boat 1 |
| `n1_goo_zooka_moves_kn_by_one_and_km_by_nothing` | the effect alone: kn +1, km 0. The whole play through the game: km −1 (the card leaving the hand), kn level (the parked "N1, Goo-zooka") |
| `n1_peculiar_plaza_counts_for_both_sides` | [P] cost-2 Actives on both sides: kn 0, km +2. Only the bot's: +2 under both. Only theirs: kn −2, km 0 (the parked "N1, Plaza") |
| `n1_leaves_setup_to_km_and_reads_no_hidden_card` | in setup kn = km bit for bit; the term doesn't move when the opponent's hand and deck are swapped for other cards (the parked "N1, setup and hidden cards") |
| `on_played_states_kn_is_km_plus_the_opponents_active_retreat_cost` | every position of 10 random games of the scratch pairs, both views: in setup kn = km bit for bit; after it, kn − km is the opponent's board cost; and everywhere kn with its flag cleared is km, bit for bit |
| `kn3_with_n1_off_equals_km3_move_for_move_on_200_scratch_deals` | the five scratch pairs, 40 deals each: km3 against km3 (as `deckgym simulate` builds them) and kn3 with N1 off against itself play the same moves, choices and results in all 200. kn3 itself differs from km3 in at least one of the first 40, so the test reaches N1 |
| `kn3_from_get_player_declines_a_plaza_that_helps_both_sides_where_km3_plays_it` | Mewtwo ex against Mewtwo ex, Plaza the only card: km3 plays it (+2 own, −1 card), kn3 doesn't (level, −1 card). Against a Machop both play it |
| `kn3_from_get_player_plays_goo_zooka_on_the_tie_where_km3_ends_the_turn` | Dratini against Machop, Goo-zooka the only card: km3 ends the turn (−1); kn3 plays it on the tie |
| `kn_parses_before_k_and_nothing_else_moves` | `kn3` and `KN5` parse; `kn`, `knx`, `kn3x` and `kn1a` don't; `km3`, `kog3`, `kt3`, `kta3`, `ktb3`, `ktc3`, `koh3`, `kph3` and `k3` parse as before |

- **The scratch decks** (in the test, and as files in `smoke/`) were made for this build. They are not table, held-out or Dustin's lists.
- **Planted faults, before the commit** (`run_faults.sh`, `faults.log`). The code was changed by a script, kn's tests were run, and the files were restored byte for byte:
  1. **The term reads the opponent's printed cost instead of the board cost:** 7 tests fail. The board-cost, Goo-zooka, Plaza and played-state tests fail, both wiring tests fail, and so does the 200-deal test. There it can only be its second check (kn3 differs from km3 in the first 40), since this fault leaves the flag-off path alone.
  2. **`get_player` gives kn km's value function:** the two wiring tests and the 200-deal test fail.
  3. **The 200-deal test's "N1 off" player has N1 on:** that test fails. So it does see a difference when there is one.
- **The full suite** (`suite.log`), on this branch's engine at `71877f6`: **2,022 passed, 0 failed, 0 ignored.**
  - That is the branch's previous 2,011 (`../coin_prevention_repair_2026-09-30/README.md`) plus kn's 11.
  - No existing test's expected value was edited.
  - The build prints the same 5 old warnings.

## The smoke (`smoke/`)

**How.** `run_smoke.sh` builds `kn_smoke` in a scratch copy of the official engine's source: `d363ba8`'s `engine/` (`rl/engine-2026-09-30/`) with `71877f6`'s `engine/src/players/`. `scratch_engine_diff.txt` shows that copy differs from `d363ba8` only in those three files and the added example.
- Each scratch deck plays each scratch opponent, both seats, 100 games a seat.
- There are two arms on the same seeds: km3 as the deck's pilot, then kn3. The opponent is km3 in both.
- A chance is one of the deck's turns on which playing the card was offered, as the floor counts a played Trainer.
- A game differs when any move differs.
- `smoke.py` makes the tables (`smoke_output.txt`). The program's sha256 is in `kn_smoke.sha256`.
- The run was made twice, the second time to record the deck's attacks. All 4,800 games were the same both times.

**The decks.**
- `goo`: Machop line, Team Rocket's Raticate ex, 2 Goo-zooka, Sabrina, Cyrus.
- `grass_goo`: Whimsicott ex, Ariados, 2 Goo-zooka, Sabrina, Cyrus. It has the carrier's shape but is not the held-out list.
- `plaza`: Mewtwo ex, Gardevoir line, 2 Peculiar Plaza.
- `psychic`: `plaza` without the Plaza. It is the control, counting Cyrus.
- The opponents: `water_boat` (Suicune ex, Blastoise line, 2 Inflatable Boat), `fire_balloon` (Charizard line, 2 Small Balloon) and `psychic`.

| deck (card) | opponent | km3: plays / chances | kn3: plays / chances | km3 wins | kn3 wins | games that differ |
|---|---|---|---|---|---|---|
| goo (Goo-zooka) | fire_balloon | 0 / 853 (0.0%) | 206 / 253 (81.4%) | 194 / 200 | 191 / 200 | 163 / 200 |
| goo (Goo-zooka) | psychic | 3 / 846 (0.4%) | 228 / 255 (89.4%) | 60 / 200 | 63 / 200 | 178 / 200 |
| goo (Goo-zooka) | water_boat | 0 / 988 (0.0%) | 248 / 284 (87.3%) | 136 / 200 | 132 / 200 | 173 / 200 |
| grass_goo (Goo-zooka) | fire_balloon | 72 / 636 (11.3%) | 199 / 241 (82.6%) | 135 / 200 | 135 / 200 | 155 / 200 |
| grass_goo (Goo-zooka) | psychic | 123 / 675 (18.2%) | 229 / 251 (91.2%) | 105 / 200 | 85 / 200 | 155 / 200 |
| grass_goo (Goo-zooka) | water_boat | 165 / 683 (24.2%) | 249 / 278 (89.6%) | 126 / 200 | 112 / 200 | 157 / 200 |
| plaza (Plaza) | fire_balloon | 166 / 173 (96.0%) | 166 / 173 (96.0%) | 188 / 200 | 188 / 200 | 0 / 200 |
| plaza (Plaza) | psychic | 176 / 176 (100.0%) | 116 / 397 (29.2%) | 86 / 200 | 88 / 200 | 124 / 200 |
| plaza (Plaza) | water_boat | 169 / 176 (96.0%) | 169 / 176 (96.0%) | 109 / 200 | 109 / 200 | 0 / 200 |
| psychic (Cyrus; control) | fire_balloon | 17 / 21 (81.0%) | 17 / 21 (81.0%) | 192 / 200 | 192 / 200 | 0 / 200 |
| psychic (Cyrus; control) | psychic | 38 / 58 (65.5%) | 38 / 58 (65.5%) | 100 / 200 | 100 / 200 | 2 / 200 |
| psychic (Cyrus; control) | water_boat | 83 / 92 (90.2%) | 83 / 92 (90.2%) | 115 / 200 | 115 / 200 | 0 / 200 |

**Plays per chance undercount the change.** kn3 plays the card at its first chances, so fewer chance turns follow.

| deck | code | games with a chance | games with a play | median turn of the first play |
|---|---|---|---|---|
| goo | km3 | 542 / 600 | 3 | 7 |
| goo | kn3 | 542 / 600 | 513 | 2 |
| grass_goo | km3 | 537 / 600 | 317 | 8 |
| grass_goo | kn3 | 537 / 600 | 520 | 2 |
| plaza | km3 | 525 / 600 | 511 | 2 |
| plaza | kn3 | 525 / 600 | 451 | 2 |

**The Grass Knot deck:**
- km3's Goo-zooka plays: 360, and 359 of them came just before a Grass Knot that turn.
- kn3's: 677, and 120 of them.
- Games won only with km3 against only with kn3, on the same deals:

  | opponent | only km3 | only kn3 |
  |---|---|---|
  | psychic | 23 | 3 |
  | water_boat | 17 | 3 |
  | fire_balloon | 1 | 1 |

- In the plain Goo-zooka deck the pairs are 3 and 0, 1 and 4, 8 and 4. In the Plaza deck they are 3 and 5 against psychic, and none elsewhere.

**Not covered by the smoke:**
- Hiking Trail, under which the parked text predicts a strict gain (+2 under N1);
- Field Blower on an opponent's Balloon or Boat;
- any table, held-out or Dustin's list.

## The carrier suggestion: Whimsicott ex Ariados

This is the parked text's suggestion, repeated here, not a registration (`REGISTRATION_DRAFT.md`, "N1 is not in km").
- **Why it fits:**
  - It was Sept 10 rank 26, and Goo-zooka and Ariados are in 21 of its 21 development lists.
  - It is the one archetype that carries N1's cards, and none of the 45 cells' lists does.
  - Its held-out list exists: `../b2e_card_check_2026-09-26/decks/h-whimsicott.txt`, with 2 Goo-zooka, 2 Ariados, 2 Whimsicott ex and 2 Fragrant Forest, and no Hiking Trail.
- **What the smoke adds, for whoever registers it:**
  - Under km3 the carrier's Goo-zooka already pays through Grass Knot in the same turn (the census's "partly read"). The smoke's scratch list of the same shape played it almost only on those turns.
  - Under kn3 the tie-break moves most plays to the first chance, away from Grass Knot turns.
  - So the carrier is also the list where N1's early plays show a cost in the smoke.
  - Trap Territory is now priced too: Ariados in play is +1 to the opponent's cost under kn.
  - Grass Knot's damage is still not in the clock (the parked text's simplification).

## The footprint expected

The footprint is the share of games in which kn3's moves differ from km3's, counted as km's and kt's are.
- **Lists with Goo-zooka or Peculiar Plaza: large.** In the smoke 78 to 86% of the Goo-zooka decks' games differ, 62% of Plaza's against a Psychic deck, and none where Plaza helps only its own side.
  - So the rows that carry these cards will change in most games:
    - B2e's Whimsicott rows;
    - Dustin's decks 12, 14 and 15 and brews 03a and 03b (Goo-zooka);
    - brews 05b and 10 (Plaza).
  - Deck 12 has Hiking Trail as well.
- **The 45 cells: small.** By the parked reach table, none of their lists carries Goo-zooka, Plaza or Trap Territory. N1 can still act there in three ways:
  - which Pokémon a gust leaves Active (Cyrus: the bot picks; Sabrina: the opponent picks, as the search prices their reply);
  - removing an opponent's retreat Tool (Field Blower on Altaria's Small Balloon or Suicune's Inflatable Boat);
  - close lines that leave different opponent Actives.
  - The smoke's control deck differed in 2 of 600 games, but it has no Field Blower, and Field Blower is in 6 of the 8 panel lists.
  - My expectation for those cells is of the order of the parked text's guess (1 to 2% of games) or less. It is not measured here: no table list was played.
- **Dustin's decks without N1's cards:** as for the 45 cells.

## For the laptop

- **Build kn on the official source.** Take `git archive d363ba8 engine` and replace `engine/src/players/` with `71877f6`'s; `run_smoke.sh` does exactly this. The branch's own `engine/` also carries the unmerged Victory Star and coin-flip repair drafts.
- Programs built there will have their own sha256. What carries across machines is the commit and the tests.
- **One point for the registration, from the code and the smoke.** The Goo-zooka rate rises because the play ties with not playing and the move order breaks the tie. It is not because kn prices the turn it matters more than another turn. Nothing here changes that; whether it is acceptable is the registration's question.

## Limits

- The smoke's decks exist only for this build. Their win counts describe these games and are not a strength result.
- The 200-deal identity is kn3 with N1 off against km3 in one build. It is not the laptop's identity replay against committed references, which this job doesn't do.
- The term counts the opponent's cost even when they can't retreat anyway (Asleep, Paralyzed, Bind Down), as the bot's own term does.

## Files

- `README.md`: this note.
- `suite.log`: the full unit suite at `71877f6`.
- `run_faults.sh`, `faults.log`: the planted faults.
- `smoke/`:
  - `goo.txt`, `grass_goo.txt`, `plaza.txt`, `psychic.txt`, `water_boat.txt`, `fire_balloon.txt`: the scratch decks.
  - `kn_smoke.rs`, `run_smoke.sh`, `kn_smoke.sha256`, `scratch_engine_diff.txt`: the program and how it was built and run.
  - `games.jsonl`: one row per game.
  - `smoke.py`, `smoke_output.txt`: the tables.
