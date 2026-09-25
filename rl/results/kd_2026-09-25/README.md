Decision this informs: whether kd (the defender's Weakness and lasting damage cuts, priced in the threat clock) goes into the pilot on top of kp. On its own table kd3 fits Limitless worse than kp3 (mean squared miss 124.5 against 112.2), though better than k3 (159.3) and kq3 (147.3). It narrows Vespiquen's gap by 1.2 points (±1.7, so not clearly), and it moves Altaria v Lucario the wrong way. The laptop scores it by the adoption rule. Engine commit 0c0e7f9 for the kd3 table; branch commit 413a4aa has the same `engine/`. k3, kp3 and kq3 were shown unchanged at 97ca8f4, and nothing on their path changed after it.

**Outcome (laptop, rule v2):** not adopted; kp3 stays the pilot. Main dfd3919, `rl/results/table_readings_2026-09-24/kd3_paired_reading.md`:
- τ̂: kp3 8.6, kd3 9.4. ΔMSE +14.2 (95%: −11.1 to +39.6). No vetoes.
- The laptop's mixed rows (0c0e7f9 build) matched this table's pairing 1 on 500 of 500 games.
- With kd3 on one side only, Lucario (−2.2 ± 1.4), Vespiquen (−1.5) and Hydreigon (−1.1) were piloted worse beyond noise. The laptop's tier-1 read ties Lucario's drop to how kd prices a sniper as the threat.

Seeds: the table's deals only. 72,000,000 + pairing × 10,000 + i, i < 500, even i = first-named deck in seat 0.

# kd3: kp3 plus the defender's Weakness and damage cuts in the clock (Sept 25)

## What kd is

`kd<N>` = `kp<N>` (k's blind search, with public pricing of the 62 audited opponent-hand/deck texts) with one evaluator change, in the damage-aware threat clock, on both sides. kq's features are off.

**How kd prices each victim.**
- **The damage.** Each victim the clock counts takes the threat's damage through the victim's own public, lasting modifiers, using the engine's own damage steps (`hooks::persistent_defender_damage`):
  - Weakness, including Bounded Field and Double Type; for an evolving threat, the type of the form it attacks as;
  - Safeguard, Intimidating Fang, "takes −X damage" Abilities, the conditional ones (typed attackers, Arceus, Ice Face for the first hit only, Unown GUARD, Coordinated Unit) and Disguise;
  - Heavy Helmet and Steel Apron;
  - the coin-flip Abilities, in expectation;
  - the attack's own text ("isn't affected by Weakness", "…by any effects on your opponent's Active Pokémon");
  - bonuses for who the defender is ("+30 if a Pokémon ex", type, stage, name, has an Ability).
- **Not counted:** effects that last a turn (attack-stored cuts, Metal Core Barrier, turn effects).
- **The attacker.** The threat is chosen as before. A victim it can't damage is priced with the owner's best attack that can, and "never" (30 turns) means nothing can.
- **Reach.** An attack that can only damage the Bench can't touch the Active, and hits a benched victim where it is, as the engine prices Bench damage.
- **Promotion order.** The defender promotes in the order that lasts longest (every order is tried).
- **Engine bugs.** kd prices what the engine does where the engine has a known bug: the coin-cut order, and no coin for direct damage. Both bugs are in `rules/09` "Open engine bugs", each pinned by a test that fails on purpose when the engine is fixed.

**The spec and its changes,** all registered before any kd table, in the commit messages:
- 45a8030: the registered spec;
- 51916e1: first review fixes;
- 97ca8f4: Dustin's amendment, the fallback attacker and kd's own promotion order;
- 349f672: the coin order, mirroring the engine;
- 5ae7490: second review fixes;
- 8004222: third review fixes;
- 0c0e7f9: tests.

## How it was checked before the table

- **Tests.** 44 kd tests. The full suite passes: 1,894, 0 failed.
  - Every damage case is checked against the engine's `modify_damage` or its own damage routine on the same board.
  - The two engine-bug pins run real attacks through the engine's forecast.
- **Adversarial review, three rounds** (3 reviewers, then 2, then 1). Every implementation finding was fixed. The design findings went to Dustin: the fallback attacker and the promotion order (adopted, 97ca8f4). The review's point on snipe targets is settled below.
- **Identity.** k3, kp3 and kq3 replay the whole table exactly with the kd code at 97ca8f4: 14,000 of 14,000 games each, no rule findings (`identity_{k3,kp3,kq3}_500.*`). From 97ca8f4 to 0c0e7f9, only kd's own functions and the tests change.
- **Mutations.** 43 of 46 were caught, on 5ae7490's code. The three that survived are now covered by tests: 8004222 and 0c0e7f9. A rerun on the table's code is to follow.

## For the laptop's kd3 mixed rows

Your two conditions:
1. **Not met as launched.** kd3_500.jsonl was run at 0c0e7f9, not at an engine identical to 5ae7490's.
   - 8004222 changed kd after 5ae7490: an attack's extra damage to the Bench is no longer priced on the Active. On the table, that is Hoopa ex's Shadow Bullet in the Weezing deck, which now does 10 to Shuckle ex, not 30.
   - Its other two changes reach no table deck: the "has an Ability" bonus, and no coin flip for direct damage.
   - So the mixed rows need a rebuild at 0c0e7f9 (or 413a4aa, same `engine/`).
2. Any kd3-v-kd3 pairing from a 0c0e7f9 build should match `kd3_500.jsonl` move for move.

## The table

`kd3_500.{txt,jsonl}`: all 28 pairings × 500 table deals, one JSON line per game. No rule findings. Distinct games 500 of 500 in 26 pairings, 497 in Blaziken v Sceptile and 499 in Lucario v Sceptile. A few deals give the same short game, as in the kp3, k3 and kq3 tables.

**Against Limitless, over 28 cells** (`deck_averages.py`):

| bot | mean abs(miss) | mean squared miss |
|---|---:|---:|
| k3 | 9.66 | 159.3 |
| kp3 | 7.91 | 112.2 |
| kq3 | 9.44 | 147.3 |
| kd3 | 8.59 | 124.5 |

**Deck averages over their seven opponents.** The last column is kd3 − kp3, paired deal by deal, with a 95% range (`deck_averages.py --paired`):

| deck | Limitless | k3 | kp3 | kq3 | kd3 | kd3 − kp3 |
|---|---:|---:|---:|---:|---:|---:|
| Altaria | 54.0 | 46.6 | 49.7 | 50.2 | 48.9 | −0.8 ± 1.2 |
| Blaziken | 57.7 | 56.4 | 55.6 | 57.5 | 56.5 | +0.9 ± 1.3 |
| Hydreigon | 42.6 | 34.6 | 47.4 | 49.7 | 47.0 | −0.4 ± 1.3 |
| Lucario | 50.2 | 52.5 | 52.0 | 53.8 | 50.1 | −1.9 ± 1.6 |
| Sceptile | 48.2 | 62.1 | 58.3 | 60.1 | 58.9 | +0.6 ± 1.3 |
| Suicune | 48.2 | 52.9 | 46.5 | 44.6 | 46.9 | +0.4 ± 1.3 |
| Vespiquen | 56.5 | 48.1 | 45.8 | 42.2 | 46.9 | +1.2 ± 1.7 |
| Weezing | 42.7 | 46.6 | 44.7 | 41.9 | 44.8 | +0.1 ± 1.5 |

**Vespiquen's cells (Vespiquen's score):**

| v | Limitless | k3 | kp3 | kd3 |
|---|---:|---:|---:|---:|
| Altaria | 61.2 | 57.4 | 52.6 | 47.2 |
| Blaziken | 18.6 | 20.5 | 18.6 | 19.9 |
| Hydreigon | 61.6 | 69.2 | 59.0 | 63.0 |
| Lucario | 30.7 | 35.8 | 31.8 | 35.2 |
| Sceptile | 66.9 | 33.4 | 35.6 | 35.8 |
| Suicune | 73.0 | 49.6 | 57.0 | 54.8 |
| Weezing | 83.5 | 70.9 | 65.9 | 72.7 |

**Cells that moved most against kp3** (the first-named deck's score, paired, 95% range):
- Vespiquen v Weezing: +6.8 (+2.0, +11.6), 65.9 → 72.7 against Limitless 83.5. Toward Limitless.
- Lucario v Weezing: −5.8 (−10.5, −1.1), 52.8 → 47.0 against 56.6. Away.
- Sceptile v Suicune: +5.6 (+3.0, +8.2), 60.6 → 66.2 against 47.2. Away.
- Altaria v Vespiquen: +5.4 (+0.9, +9.9), 47.4 → 52.8 against 38.8. Away; from Vespiquen's side, −5.4.

Every cell, against k3 or kp3: `../per_game_table_2026-09-25/analyze_tables.py --base <k3_500 or kp3_500_*> --other kd3_500.jsonl`.

**Altaria v Lucario, the hypothesised blind spot** (Mega Altaria ex and Espeon are Psychic; Lucario, Riolu and Hitmonlee are weak to Psychic):

| | Altaria's score |
|---|---:|
| k3 | 56.6 |
| kp3 | 62.4 |
| kd3 | 59.0 (−3.4; −7.4, +0.6 against kp3) |
| Limitless | 71.9 |

## What this shows, plainly

- **kd changes the Vespiquen deck's play little on average.** Its gap goes from 10.7 to 9.6 points, which is within noise. The cells split:
  - Vespiquen v Weezing moves most toward Limitless (+6.8). That's where Shuckle ex's Solid Shell against Weezing's small attackers bites.
  - Vespiquen v Altaria and v Suicune move away.
- **The Altaria hypothesis doesn't hold on this table.** Pricing Psychic Weakness on Lucario's line lowers Altaria's score in that cell rather than raising it. Altaria's deck average doesn't close either (48.9 against 54.0).
- **Lucario moves to Limitless on average** (52.0 → 50.1 against 50.2). But Lucario v Weezing moves away (−5.8), the cell where kq3 had moved it past Limitless.
- **The overall fit is worse than kp3's.** Mean squared miss 124.5 against 112.2. The biggest single contributor is Sceptile v Suicune moving further from Limitless.
- The laptop's adoption rule decides. This file only reports.

## Known limits (kept as registered)

- **Snipe targets.** kd knocks the Active out first, then lets the defender order all the benched victims, including those a sniper hits where they sit. In the game the attacker picks snipe targets, even before the Active falls, which can win a turn or two sooner (Heatmor, Grovyle, Hitmonlee against benched Pokémon ex). The laptop settled this: no new kd version.
- **The fallback's Energy.** The fallback's missing Energy is counted beyond the threat's, once per Pokémon. That can err either way: it doesn't credit attaching while attacking.
- **The kd/kp comparison.** kd's promotion order differs from k's raw-HP order even on boards with no Weakness or cut, so kd3 − kp3 measures both.
- **Other simplifications:**
  - Damage an attack does to the Bench as well as the Active isn't credited to the Bench.
  - Coin-attack damage is taken at its expected value.
  - Board conditions (Arceus, a second Falinks, a non-GUARD Unown) are read on today's board.
  - A promoted victim that nothing can damage ends the count as "never", even when snipes elsewhere could still win.
  - The snipes-only case leaves out attacks that can hit any of the opponent's Pokémon.
  - For attacks other than direct damage that deliver their damage through a queued choice, kd flips the coin Abilities (as the card text says) where the engine doesn't. That one isn't on the table.

## Files

- `kd3_500.{txt,jsonl}`: the kd3 table. `run_kd3_table.sh` is its command. The legality_scan was built at 0c0e7f9, SHA-256 `f19ad3f378a9042c3e3497bf22361f3db2077c62d6b664c58f065bd46ccb82ae`.
- `identity_{k3,kp3,kq3}_500.{txt,jsonl}`: the full-table replays at 97ca8f4, identical to the reference tables. `run_identity.sh` is their command.
- `identity_k3_45a8030_partial.*`: an earlier partial replay at 45a8030 (pairings 0-4, 2,500 of 2,500 identical).
- `deck_averages.py`: the readouts above. `timing.txt`: wall times.
  - kd3 took 2,913 s, with the kq3 replay sharing the machine for part of it.
  - kp3 took 1,561 s on a free machine, so the two timings aren't a controlled comparison.
