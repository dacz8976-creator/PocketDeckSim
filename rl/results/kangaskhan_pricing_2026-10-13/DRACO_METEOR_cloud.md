# Draco Meteor and other random-target damage in km3's forecast (the cloud, Oct 15)

Asked by Fable (direct route, Oct 15): Sonnet's readers said, from reading the code, that km3 prices Draco Meteor's random hits as zero
expected damage in its forecasts (`players/mod.rs:697`, `value_functions.rs:342`). Verify with a test.

## Answer: true

- **In km3's clocks, the estimate of Draco Meteor's damage is 0.** The engine's average over 2,000 seeds is 152 HP of damage per attack.
- **So a loaded Dragonite doesn't threaten anything.** km3's clock for the opponent's attacker says the opponent never wins (the
  clock's 30) instead of 3 turns.
- **The same holds for the other attacks that print 0 and choose their targets at random:**
  - Wugtrio ex, Wiglett, Magcargo, Zapdos (B2 051), Gholdengo ex, Mega Camerupt ex, Noivern, Rayquaza ex;
  - 22 printings of 9 attacks in all.
- **No list in our panel, scoreboard, gauntlet or Dustin decks carries one.** So no measured number is affected. One ladder opponent
  (Gholdengo ex / Orthworm) did carry one.

## Why: the reader's two lines

- **`value_functions.rs:342-343` is km's value function:**
  `parametric_value_function_ex6(state, myself, &baseline, public_eval true, value_aware false, clock_aware true, effect_aware true,
  reserve_aware false, EvalFeatures::KM)`. `players/mod.rs:697` maps the `km` code to it.
- **Why that gives 0:**
  - km's clocks (`kt_clocks` → `kt_clock_c2`, `:1802`) call `estimated_attack_damage_ex(atk, slot, state, owner, reserve_aware)`.
    The last argument is `spread_aware`, so it is false for km.
  - The random-spread classes (`RandomSpreadDamage`, `AlsoRandomBenchDamage`, `RandomDamageToOpponentPokemonPerSelfEnergy`, plus
    the coin-flip discard class) are priced only when `spread_aware` is true (§117, `:2358-2397`). The flag was kept off so the §116
    tier stays byte-compatible.
  - Without it, they fall through to `_ => fixed`: the printed damage, 0 for Draco Meteor.
- **So the readers read it right.** The one thing to add: km3's search applies attacks through the engine, so the damage of an
  attack km3 makes this turn is real in its search. What is wrong is the forecast: both clocks (how soon the opponent wins, how soon
  km3 wins), and with them the value of every position where such an attacker is loaded or being powered up.

## The test (`draco_meteor_check.rs`)

A scratch test, appended to `engine/src/players/value_functions.rs` in a copy of this branch's engine (tree 7ab75e71). It isn't in
the engine: it reaches private functions.

```
cargo test --release --features test-utils --lib draco_meteor_check -- --nocapture --test-threads 1
```

**The board:**
- Player 0: Hitmonlee (80) Active, Bulbasaur (70) and Hitmonlee (80) on the Bench, to move on turn 5.
- Player 1: Dragonite (A1 185) Active with Draco Meteor paid for ([WLCC]: 4 times 50 to a random opposing Pokémon).

| What | Value |
|---|---:|
| `estimated_attack_damage_ex`, `spread_aware` false (km3's clocks) | **0** |
| `estimated_attack_damage_ex`, `spread_aware` true | 200 |
| km3's clock, turns until the opponent wins (`kt_clocks`, km's flags) | **30** (no threat) |
| The same clock with the spread-aware estimate | 3 |
| km3's clock with the Dragonite unpowered | 30 |
| **The engine**, Draco Meteor from this board, 2,000 seeds (20,000,015,000 and up) | mean 152.2 HP lost (51.5 on the Active); the Active knocked out 39.9%; 1.22 knock-outs per attack |

- **The clock can't tell a loaded Dragonite from an unpowered one:** 30 both times. km3's value of the position does fall, from 2,289
  to 1,149, but through other terms, not the threat.
- **The spread-aware estimate is not the right fix as it stands.** It puts the whole 200 on the clock's victim, the Active. The
  engine puts 51.5 on the Active on average and spreads the rest: a third of it off the Bench Hitmonlee, a third off the Bulbasaur.
  The clock would then say the Active falls in one hit when it falls 40% of the time.

## Every attack with random-target damage (the whole database, from the test)

29 printings. "km3" is the estimate in km3's clocks; "aware" is with `spread_aware` on (the full sum of the hits).

| Attack | Printings | Printed | km3 | aware | Targets |
|---|---|---:|---:|---:|---|
| Draco Meteor (Dragonite) | A1 185, A1 244 | 0 | **0** | 200 | 4 x 50, opponent's Pokémon |
| Draco Meteor (Noivern) | B4 122, B4 176, P-B 083 | 0 | **0** | 180 | 3 x 60, opponent's |
| Draco Meteor (Rayquaza ex) | P-A 064, P-A 065 | 0 | **0** | 160 | 4 x 40, opponent's |
| Pop Out Throughout (Wugtrio ex) | A2b 019, A2b 081, A2b 109, A4b 127 | 0 | **0** | 150 | 3 x 50, opponent's |
| Spring Out (Wiglett) | A2b 018, A2b 101, A4b 125, A4b 126 | 0 | **0** | 30 | 1 x 30, opponent's |
| Spurt Fire (Magcargo) | A4 031 | 0 | **0** | 150 | 3 x 50, any other Pokémon, own Bench included |
| Heavy Thunder (Zapdos) | B2 051 | 0 | **0** | 100 | 1 x 100, any other Pokémon, own included |
| Volcanic Kaboom (Mega Camerupt ex) | B3 023, B3 181, B3 195 | 0 | **0** | 160 | 1 x 160, opponent's |
| Spending Rush (Gholdengo ex) | B2a 078, B2a 104, B2a 114 | 0 | **0** | 40 per [M] | 1 x 40 per [M] attached, opponent's |
| Zapping Bullet (Ampharos) | B1 084, B3b 096 | 90 | 90 | 110 | 90 to the Active, plus 20 to a random Benched |
| Lightning Lancer (Mega Ampharos ex) | B1 085, B1 258, B1 277, B3b 103 | 100 | 100 | 100 | 100 to the Active, plus 3 x 20 to random Benched (its own mechanic; neither estimate counts the Bench) |

- **Not random-target, but gated with them:** Camerupt (B3 022)'s coin-flip Fire discard (`DiscardSelfEnergyPerHeadsExtraDamage`),
  also priced only with `spread_aware`.
- **The two Ampharos lines are fine for the Active.** Their printed damage is the Active's. Only the Bench extra is missing, which km3's
  Active-only clock doesn't use anyway.

## Which decks carry one

A search of every deck list in the repository:
- `decks/` (screen and its 8 panel opponents, gauntlet, brews, dustin, consistency, research, variants, computer);
- `engine/example_decks/`;
- every `rl/**/decks/` folder.

It found **none** of the 29 printings.
- **The pause-game and position decks** (`pause_games_new_*/decks`) carry none either.
- **The ladder log** (`decks/screen/panel_ladder_2026-09-26/ladder_counts.md`) records opponents with no lists:
  - "Gholdengo ex Orthworm", 1 game (a win, with the Hydreigon / Galarian Obstagoon deck). Gholdengo ex's Spending Rush is in the
    class.
  - "Dragonite Oricorio", 1 game. Which Dragonite isn't recorded: A1 185 / A1 244's Draco Meteor if it is that one.
  - "Dragonite ex", 1 game: not in the class (another card).
- **Limitless (`decks/classifier/limitless_2026-09-10.json`):** none of these archetypes is named.
- **What that means:** screen, floor, scoreboard, exam and slow-report numbers are not affected. It matters on the ladder, against
  Gholdengo, Dragonite, Wugtrio, Noivern or Camerupt decks, and in any brew of Dustin's that uses one.

## The correction candidate (for the next pilot round; nothing is built)

The same shape as the Kangaskhan decision (`DECISION.md`): a separately testable correction, behind a new preset parameter on a
named pilot. It is not an edit to the pinned km3.

**What it changes:**
- A new `EvalFeatures` flag (for example `random_targets`, preset suffix `_rand`). Under it, km's clocks price the random-target
  classes above at their expected damage on each victim, not on the Active alone.
- **On the clock's Active victim:** each hit lands on the Active with chance 1/n, where n is the number of Pokémon it can choose
  among (the opponent's in play; for Spurt Fire and Heavy Thunder every other Pokémon, both sides). So the Active expects
  times x damage / n.
  - Here: 4 x 50 / 3 = 66.7 on the Active. The engine gives 51.5, because hits on an already knocked-out Pokémon are wasted (80 HP
    takes at most 80).
  - Capping each target's expected damage at its HP closes most of that gap. The test has the board to check the cap.
- **On the Bench victims:** the clock's "rest" takes their expected share the same way.
- **Gholdengo ex:** per Metal Energy attached, as the §117 arm already does.
- **Kept out:** the §117 coin-flip discard class (Camerupt B3 022) and Ampharos's Bench extra. They are not random-target damage on
  the clock's victims, and keeping them out keeps the flag's reach to the 22 printings.

**Tests to pin it:**
- The board above: Active share 66.7 uncapped, near the engine's 51.5 with the cap; the opponent's clock finite (not 30).
- A single-target Volcanic Kaboom against one Pokémon in play (n = 1): 160 on it.
- Spurt Fire counting the attacker's own Bench in n.
- The flag off: every clock and value unchanged, byte for byte.

**The gate:**
- **With the flag off:** km3's self-check digest and the floor games equal, as for any preset (the decks carry none of these cards).
- **With the flag on:**
  - Every game on decks without these 22 printings is identical. That is all of the current panel, so identity is expected there.
  - A small paired run on decks that carry one: a Dragonite or Gholdengo opponent list from the ladder, rebuilt as a list, against
    the panel.
- **The scope note, as for Kangaskhan:** kx3's play-outs already deal these hits for real (the engine resolves them). The defect is
  in the judgment that proposes and plays moves inside them.
