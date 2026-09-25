# Dustin's recorded battles against the official engine, Sept 25

**In plain words:** nothing in Dustin's recorded battles contradicts the engine. That covers every rule his finished reviews describe, across about 44 battles.
- 249 distinct rule claims were checked against the engine's code and tests. 235 match.
- 8 looked like disagreements. Three skeptics threw each one out, 3 votes to 0 every time: in each case the note had misread the video or said more than it showed.
- The footage can't settle 4. 2 are screen-only details the engine doesn't model.
- The plain report for Dustin, with what to record next time he plays, is `report_for_dustin.md`.

**What was read, and what wasn't:**
- The evidence is the **written reviews** of the recordings in `C:\Users\dacz8\OneDrive\Desktop\Battle Logs` (93 review files, none missing). No video was watched, on Dustin's instruction: the transcripts and reviews are the source.
- Each observation carries the review's own strength: seen on screen, inferred, Dustin's testimony, or unclear.
- "engine matches" means the checker found the engine's code, and where one exists a test, doing what the recording shows. Not every claim has a test pinning it. For example, Cyrus has no engine test yet.

**How:** a workflow run in the laptop session (wf_e6a65d03-a0d, finished Sept 25 early afternoon).
- Ten cheaper reader agents pulled 528 rules observations from the reviews. Strategy and hidden-card guesses were skipped.
- The observations were merged into distinct claims, first in chunks of 60 and then per area. The first attempt, one call over all 528, ran past the output limit and returned nothing.
- One checker per area and group of up to 12 claims read the engine code, the tests and `rules/`.
- Three independent skeptics looked at every apparent contradiction.

**Claims by area:**

| area | claims |
|---|---:|
| attacks | 71 |
| Trainers, Tools, Stadiums | 58 |
| abilities | 33 |
| Checkup and status | 17 |
| draw, search, deck | 16 |
| Energy and retreat | 15 |
| knockout, points, promotion | 12 |
| damage and Weakness | 10 |
| evolution | 8 |
| setup and turn order | 4 |
| ties and endgame | 3 |
| other | 2 |

**What today's work leans on, and what the recordings say about it:**
- **Confirmed:**
  - Weakness is +20 flat (×2 only under Bounded Field), added before Tool reductions.
  - Cyrus pulls only a damaged Benched Pokémon.
  - Soothing Wind covers any Pokémon with Energy.
  - Boiler Smog is optional, and gives Poison and Burn on evolving.
  - Thieving Incisors is optional and moves one Energy.
  - Darkness Claw is an attack that can discard only a Supporter.
  - Roar in Unison and Hyper Ray behave as the engine has them.
  - Copycat shuffles your hand in and draws as many cards as the opponent holds.
  - Quick Growth evolves Caterpie at the end of the other player's turn.
- **No recording covers them:** Chase Order and Solid Shell.

**Three side notes from the checkers were then verified by a separate agent, by reading the code and card texts.** All three are real engine deviations. None changes any current simulation, because no deck in `decks/research`, `decks/dustin` or `decks/brews` has the combination that triggers it. None was in `rules/05` or `rules/09`. They go to the cloud session, which owns engine fixes and the open-bugs list.

1. **"Discard all Energy from this Pokémon" never puts that Energy in the discard pile.**
   - The code: `damage_and_discard_all_energy` (`apply_attack_action.rs:3526-3531`) clears the Energy without adding it to `state.discard_energies`. The normal path does add it (`state/mod.rs:1355`).
   - Affected attacks: Hyper Ray (Hydreigon), Thunderbolt (Raichu, Pikachu ex, Heliolisk), Luster Purge (Latios), Gaia Impact (Landorus), Sonic Impulse (Mega Latios ex), and Mesprit's Supreme Blast.
   - Cards that read the pile: Volkner, Lusamine, Professor Sada, Flame Patch, Flareon ex's Combust, Dragonair's Dragon's Blessing, and the bot's `discard_energy_credit`.
   - Watch for, in future brews: Mega Latios ex with Dragonair; Pikachu ex or Raichu with Volkner; Hydreigon with Lusamine or Sada.
2. **Two "random" Energy effects always take the last-attached Energy.**
   - The cards: Crawdaunt's Unruly Claw ("discard a random Energy from your opponent's Active Pokémon") and the Supporter Psychic ("move a random Energy"). The engine uses `.last()` at `apply_action.rs:922-933` and 998-1005, and treats the outcome as fixed, so the bots do too.
   - Piers, the case its code comment cites, was already fixed to pick at random.
   - It matters only for a Pokémon with more than one Energy type. The 015702 turn 5 observation (the game took the older Metal) fits a random pick.
   - Exposure today: Dustin's deck 05 plays Psychic, but the table decks each use one Energy type. On the ladder, his two-type decks (08, 11) are exposed to Crawdaunt.
3. **Rare Candy ignores Aerodactyl ex's Primeval Law** ("Your opponent can't play any Pokémon from their hand to evolve their Active Pokémon").
   - The code: the Primeval Law check is only in `can_evolve_at_position` (`move_generation/mod.rs:252-282`). `can_play_rare_candy` (`move_generation_trainer.rs:663-685`) checks Malamar's Evolution Jammer but not Primeval Law.
   - The engine's own comment (`mod.rs:260-262`) says Jammer's near-identical wording also stops Rare Candy, so the engine disagrees with itself.
   - No Pocket source settles the ruling.
   - Exposure: no deck has Aerodactyl ex. Against one, these Rare Candy decks would get an illegal play:
     - research: Hydreigon, Blaziken, Suicune
     - Dustin's: 01, 02, 05, 06
     - brews: 01, 03b, 05, 05b, 09

**Files:**
- `report_for_dustin.md`: the plain report.
- `claims.json`: every claim with its support (battle @ time, strength), the checker's verdict and evidence (file:line), and notes.
- `skeptics.json`: the three skeptics' votes and reasons for each of the 8 apparent contradictions.
