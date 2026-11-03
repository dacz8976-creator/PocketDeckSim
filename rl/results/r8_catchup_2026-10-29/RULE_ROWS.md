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
  - 3 tracked files under never-open paths name a Misty id; they were not opened.

## The rows and their predictions

### Misty: choose the [W] Pokémon first, then flip (A1 220, A1 267)
- **Test first.** If the test shows our Misty already asks for its target before the coins, the row is tests-only: **0 games change.**
- **Otherwise (a game change), it can act only in games of a deck holding Misty.** Among the sources that is only draft A (2x A1 220):
  - kx3 replay_b, draft A v the 8 panel lists, deals 0-1, both seats, the kx3 and km3 arms: 64 games;
  - only in deals where draft A's seat plays Misty with a [W] Pokémon in play, or where km3's search or kx3's play-outs weigh a Misty line.
- **Not played by any check:** draft-A-wallace and `pause_games_decisions_2026-10-02/decks/draftA.txt` also hold Misty. No panel list, research twin or floor piece holds Misty.

### Sweet Honey: choose a damaged Pokémon first (C1 119, C1 152)
- Already so since R8-07a (82e9aeae). No deck file holds Sweet Honey. **0 games change.**

### Darkrai ex: Nightmare Aura also fires on [D] Energy an effect attaches from the Zone (`only_turn_energy: false`)
- **The printings:** A2 110, A2 187, A2 202, A4b 245, A4b 378, P-A 042.
- **What it takes to act:** a deck holding Darkrai ex AND an effect that attaches [D] Energy from the Energy Zone to it.
  - The only such effect is Sableye B3a 040 / P-B 070's Jeweled Gift (a random Basic Energy type to a Benched Pokémon).
  - Hydreigon's Roar in Unison attaches [D] only to Hydreigon itself.
  - The other Zone-attach texts are fixed non-[D] types or [C].
  - In `engine/database.json`, exactly 10 card texts name both [D] and the Energy Zone: Nightmare Aura x6, Roar in Unison x2 and Jeweled Gift x2.
- **No tracked file holds B3a 040 or P-B 070.** These Darkrai ex holders are reached only on the turn's normal attach, which is unchanged:
  - t-weezing, research/weezing, brew-07, 04, b2e's h-hoopa_absol;
  - the v-weezing swaps and others.
- **0 games change.**

### Iris: the bonus point for all 5 Haxorus printings (adds B4b 176, B4b 348)
- No tracked file holds B4b 176 or B4b 348. The only Iris deck in `decks/` (11) holds B2b 056, which is already counted.
- **0 games change.**

### Triple Bombardment: 50 to the one Benched Pokémon when there is exactly 1 (B1a 020, B1a 078, B1a 084, B4b 054, B4b 414)
- Only `decks/computer/blastoise-wailord-deluxe.txt` (1x B1a 020) and its copy under `pause_games_decisions_2026-10-02/decks/computer/` hold Mega Blastoise ex, and no check plays them.
- **0 games change.**
- In general it can act only in deals where Triple Bombardment is used with 3 extra [W] attached and the opponent has exactly 1 Benched Pokémon.

### Item 11 (later, listed for completeness)
- Urshifu B3 051 appears in `rl/results/engine_switch_rules2_2026-10/scratch_8b2/water_round2.txt`, a smoke copy and `8c/revert/revert_8c.tsv`.
- No tracked file holds Snover A2 044 or Sealeo B4 039.
- Item 11's prediction is written at item 11.
