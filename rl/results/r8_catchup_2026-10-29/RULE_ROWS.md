# R8 rule rows: replay predictions, written before the tests

R8's rule rows (coordinator-120, -124, -125, -136, -137) each get their own commit, test-first. Each game-changing row
records here, before its test, which existing replay and check games it can change. A diff outside these predictions
at the replay night is a STOP.

## Sources searched (at R8 tip 28b9d4c8, Nov 3)
- (a) **The kx3 replay check** (`rl/results/kx3_on_r6_2026-10-29/` on `laptop/kx3-replay-r6-2026-10-29`):
  - replay_a: decks 09, 06 and 10 v the 8 panel lists;
  - replay_b: decks 01, 05 and draft A (`decks/brews/drafts_2026-10-01/draft-A-shark-tempo.txt`) v the 8 panel lists;
  - replay_c: deck 10 v t-weezing;
  - the 8 panel lists are `decks/screen/opponents/t-*.txt`;
  - kx3's play-out pool: 16 lists, the 8 t-lists plus 8 research twins (its REACH.json).
- (b) **The floor check** (floor2.py PIECES):
  - brew-06, brew-06b, 14 (k3 pilots), brew-05b, 07, 12, brew-07, brew-09, draft D (root, amended, Victini-passive), and run_screen;
  - opponents: the 8 panel lists.
- (c) **The lane replays:** the 7 pages of `rl/results/engine_switch_rules2_2026-10/floor_7c.tsv`, and the 15 `.run` replays of `rl/results/engine_candidate_2026-10-20/release/tools/lane_b2.sh`.
- (d) **The self-checks** sc_km3 and sc_kx3.
- (e) **Every tracked deck-like file under `decks/` and `rl/results/`.** A names-only grep for each row's card ids, which also covers sources the read-only sweep could not open (the rules-switch carriers and scratch decks, the b2e decks, the gauntlet and kt-census decks).
  - The grep was re-run with every never-open path excluded by pathspec (self-test 0), so never-open paths were not searched.

## The rows and their predictions

### Misty: choose the [W] Pokémon first, then flip (A1 220, A1 267)
- **Test first.** If the test shows our Misty already asks for its target before the coins, the row is tests-only: **0 games change.**
- **Otherwise (a game change), it can act only in games of a deck holding Misty.** Among the sources that is only draft A (2x A1 220):
  - kx3 replay_b, draft A v the 8 panel lists, deals 0-1, both seats, the kx3 and km3 arms: 64 games;
  - only in deals where draft A's seat plays Misty with a [W] Pokémon in play, or where km3's search or kx3's play-outs weigh a Misty line.
- **Not played by any check:** draft-A-wallace and `pause_games_decisions_2026-10-02/decks/draftA.txt` also hold Misty. No panel list, research twin or floor piece holds Misty.

### Sweet Honey: choose a damaged Pokémon first (C1 119, C1 152)
- Already so since R8-07a (82e9aeae). No tracked deck-like file under decks/ or rl/results/ holds Sweet Honey. **0 games change.**

### Darkrai ex: Nightmare Aura also fires on [D] Energy an effect attaches from the Zone (`only_turn_energy: false`)
- **The printings:** A2 110, A2 187, A2 202, A4b 245, A4b 378, P-A 042.
- **What it takes to act:** a deck holding Darkrai ex AND an effect that attaches [D] Energy from the Energy Zone to it.
  - The only such effect is Sableye B3a 040 / P-B 070's Jeweled Gift (a random Basic Energy type to a Benched Pokémon).
  - Hydreigon's Roar in Unison attaches [D] only to Hydreigon itself.
  - The other Zone-attach texts are fixed non-[D] types or [C].
  - In `engine/database.json`, exactly 10 card texts name both [D] and the Energy Zone: Nightmare Aura x6, Roar in Unison x2 and Jeweled Gift x2.
- **No tracked deck-like file under decks/ or rl/results/ holds B3a 040 or P-B 070.** These Darkrai ex holders are reached only on the turn's normal attach, which is unchanged:
  - t-weezing, research/weezing, brew-07, 04, b2e's h-hoopa_absol;
  - the v-weezing swaps and others.
- **0 games change.**

### Iris: the bonus point for all 5 Haxorus printings (adds B4b 176, B4b 348)
- No tracked deck-like file under decks/ or rl/results/ holds B4b 176 or B4b 348. The only Iris deck in `decks/` (11) holds B2b 056, which is already counted.
- **0 games change.**

### Triple Bombardment: 50 to the one Benched Pokémon when there is exactly 1 (B1a 020, B1a 078, B1a 084, B4b 054, B4b 414)
- Only `decks/computer/blastoise-wailord-deluxe.txt` (1x B1a 020) and its copy under `pause_games_decisions_2026-10-02/decks/computer/` hold Mega Blastoise ex, and no check plays them.
- **0 games change.**
- In general it can act only in deals where Triple Bombardment is used with 3 extra [W] attached and the opponent has exactly 1 Benched Pokémon.

### Starting Plains: a Knock Out from its lost +20 inside an attack is not the attack's Knock Out (R8-10e; coordinator-139, -141; Dustin, Nov 3)
- **What changes:** Machop B2 079's Shatter, Conkeldurr B4 089's Bedrock Breaker or Palkia C1 038 / C1 140's Spacial Rend discards Starting Plains (B2 154, B4b 235, B4b 401). A Pokémon still in play after the attack's damage that is then Knocked Out by losing the +20 still gives its point. But nothing that reads "Knocked Out by damage from an attack" fires for it (for example the flag Marshadow's Revenge reads, Zarude's Dark Vengeance tally, Rescue Scarf, Lucky Egg, Innards Out). Promotion order and Field Blower's path are unchanged.
- **What it takes to act:** one of those attacks discards Starting Plains while a damaged Basic Pokémon is in play, the lost +20 Knocks it Out, and such an effect is in play.
- **Searched at b20d75c0, names only** (the R8-10a-d commits since then change no deck file). **Every never-open, exam and frozen path was excluded by pathspec, so never-open paths were not searched.**
  - In `engine/database.json` these are the only Starting Plains printings and the only attacks that discard a Stadium (the other Stadium discard is Field Blower, an Item).
  - Starting Plains (only B2 154) is in 9 tracked deck files: brew-07, brew-08, brew-09, brew-10, Dustin's 02, 04 and 07, b2e's h-hoopa_absol, and the brew08 copy in `pause_games_decisions_2026-10-02/decks/`.
  - No deck list under `decks/` holds Machop B2 079, Conkeldurr B4 089 or either Palkia, so no panel list, research twin or floor piece holds an attacker.
  - Under `rl/results/pause_games_new_2026-10-12/`, Conkeldurr B4 089 is in 3 single-deck files and one reader script there. None of the deck files holds Starting Plains, and no check plays them. The Palkia ids appear only in 3 `status_R.txt` logs.
- **0 games change.**

### Item 11: Urshifu's Double Type counts in the in-play type checks (B3 051, B3 113; last of the rule rows, coordinator-088)
- **What changes:** item 11 (`laptop/urshifu-in-play-type-2026-10-29`, 142963ea) sends the 11 in-play printed-type checks through the in-play type check (`State::pokemon_is_type`); Leaf Cape stays on the printed type. That check differs from the printed type only for the two Urshifu, and only while their Abilities are on: Rapid Strike Urshifu B3 051 (printed [W]) is [W] and [F] in play, Single Strike Urshifu B3 113 (printed [D]) is [F] and [D]. Double Type adds only [F] and keeps the printed type, so only the checks that ask for [F] change: Snover A2 044's Ice Shard (+30) and Sealeo B4 039's Frozen Splash (+70) against an Active Urshifu.
- **What it takes to act:** Ice Shard or Frozen Splash hits an Active Urshifu whose Abilities are not switched off.
- **Searched at 2d62a11b, names only.** Every never-open, exam and frozen path was excluded by pathspec (self-test 0), so never-open paths were not searched.
  - No deck list under `decks/` holds either Urshifu. Under `rl/results/` the only deck-like files that name one are the Oct 1 smoke deck `water_round2.txt` (in `coin_prevention_round2_2026-10-01/smoke/` and its copy in `engine_switch_rules2_2026-10/scratch_8b2/`), the 8b study's game outputs (`08a9b3a_8b_new2_*.txt`) and `8c/revert/revert_8c.tsv`; no check plays them. Every other hit is a study note, log, test probe, program binary or card-status file.
  - No deck list under `decks/` or `rl/results/` holds Snover A2 044 or Sealeo B4 039.
  - The kx3 replay check's folder (on `laptop/kx3-replay-r6-2026-10-29`), the floor check (`~/pincand_work/floor2*`) and the 18 lane replays' deck and config files (`RR_ABC_d0792568`, its engine copy left out) hold no Urshifu.
- **Not changed:** the bots' pricing of the bonus (`players/value_functions.rs:1604`) still reads the printed type; item 11 records it as a follow-up (post-R8 list).
- **0 games change.**
