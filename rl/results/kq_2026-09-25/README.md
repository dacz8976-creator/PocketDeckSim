Decision this informs: whether the B5 habits (next-attack reduction in the threat clock, and benched-attacker readiness at a pre-set 250) go into the pilot on top of kp. On their own table they make the fit to Limitless worse than kp3 (mean squared miss 147.3 against kp3's 112.2, though still better than k3's 159.3). They reproduce the network's direction on Lucario v Weezing (+10.0 over kp3), but they widen Vespiquen's under-rating further. The laptop scores it by the adoption rule. Engine commit ba20dd8 for the kq3 table. k3 and kp3 were shown unchanged at a188c14 (full table) and at ba20dd8 (subset).

Seeds: the table's deals only. 72,000,000 + pairing × 10,000 + i, i < 500, even i = first-named deck in seat 0.

# kq3: kp3 plus the two B5 habits (Sept 25)

## What kq is

`kq<N>` = `kp<N>` (k's blind search, with public pricing of opponent-hand and deck effects) plus two card-agnostic evaluation features. Both were fixed in the commit messages before any table was run (a188c14, 440e239, ba20dd8) and not tuned.

1. **Next-attack reduction in the threat clock** (`first_attack_turn` in `players/value_functions.rs`).
   - **When it applies:** the threatening Pokémon is the Active and carries effects that cut or cancel its next attack.
   - **The effect types** (keyed on type, never on card names):
     - `ReducedAttackDamage`: the amounts summed.
     - `CannotAttack`.
     - `CannotUseAttack(title)`: the best other attack it can pay for.
     - `CoinFlipToBlockAttack`: a 50/50 expectation over turns.
   - **What changes:** the first knockout's first attack turn is priced through those effects, or through the owner's escape, whichever is faster. The escape is a payable retreat into a benched attacker that can hit the Active and is paid for that turn; retreating clears the effects.
   - **Timing follows Pocket:** one attach a turn, from the Energy Zone if this turn's is still there, and a Pokémon may attack the turn it attaches. An effect counts only if it is still live on the Active's first attack turn.
   - **Cap:** damage is capped at the clock's own pace, so kq never makes an opponent faster than k does.
   - **Not counted as an escape:** evolving, which also clears the effects.
2. **Benched-attacker readiness** (`best_benched_attacker_online_score`).
   - **The score:** the highest k online score (the Active's measure, unchanged) among benched attackers, weighted **250**, half the Active's 500. It counts as (mine − opponent's), with the opponent's Bench priced from the board only.
   - **What counts as an attacker:** a benched Pokémon with, in one of its target forms, an attack that costs Energy, can hit the Active, and does damage. Damage means printed damage, a spread-aware damage estimate, or a damage mechanic the estimate doesn't price.
   - **Why that definition:** free attacks (Bonsly), Bench-only snipes and utility attacks can't stand in for an attacker, and benching a Pokémon can never lower the score.

**How it was checked before the table:**
- **First adversarial review:** 5 lenses, 3 skeptics per finding. 13 findings upheld, 0 refuted, all fixed (440e239).
- **Re-review:** 8 findings upheld, 6 refuted, all fixed (ba20dd8).
- **Tests:** 15 kq tests, plus kq parse checks in an existing parse test. The full suite passes: 1,850, 0 failed.
- **Mutations:** each of 14 mutations (each feature off, the escape, the cap, the coin, the timing, the retreat check, Bench-only and hidden-zone reads, the attacker rules) makes at least one test fail.
- **Identity:** k3 and kp3 replay the whole table exactly with the kq code: 14,000 of 14,000 games each at a188c14. After the fixes, 1,120 of 1,120 each on the first 40 deals of every pairing at ba20dd8. The fixes touch only kq's own branches.
- **get_player test:** in the B2c position, kp3 retreats Bonsly into Riolu, while kq3 puts the turn's Energy on the benched Riolu.

## The table

`kq3_500.{txt,jsonl}`: all 28 pairings × 500 table deals, one line per game. No rule findings.

**Against Limitless, over 28 cells:**

| bot | mean abs(miss) | mean squared miss |
|---|---:|---:|
| k3 | 9.66 | 159.3 |
| kp3 | 7.91 | 112.2 |
| kq3 | 9.44 | 147.3 |

**Deck averages over their seven opponents:**

| deck | Limitless | k3 | kp3 | kq3 | kq3 − kp3 |
|---|---:|---:|---:|---:|---:|
| Altaria | 54.0 | 46.6 | 49.7 | 50.2 | +0.5 |
| Blaziken | 57.7 | 56.4 | 55.6 | 57.5 | +2.0 |
| Hydreigon | 42.6 | 34.6 | 47.4 | 49.7 | +2.3 |
| Lucario | 50.2 | 52.5 | 52.0 | 53.8 | +1.8 |
| Sceptile | 48.2 | 62.1 | 58.3 | 60.1 | +1.8 |
| Suicune | 48.2 | 52.9 | 46.5 | 44.6 | −1.9 |
| Vespiquen | 56.5 | 48.1 | 45.8 | 42.2 | −3.6 |
| Weezing | 42.7 | 46.6 | 44.7 | 41.9 | −2.9 |

**Cells that changed most against kp3** (paired on the same deals, 95% range):
- Lucario v Weezing +10.0 (+6.0, +14.0)
- Hydreigon v Vespiquen +8.2 (+3.8, +12.6)
- Suicune v Weezing +6.6 (+2.6, +10.6)
- Sceptile v Suicune +5.0 (+1.7, +8.3)
- Altaria v Vespiquen +4.8 (+0.8, +8.8)
- Blaziken v Suicune +4.6 (+0.7, +8.5)
- Hydreigon v Suicune +4.4 (+0.4, +8.4)

Every cell, against k3 and kp3: `../per_game_table_2026-09-25/analyze_tables.py --base <k3_500 or kp3_500_*> --other kq3_500.jsonl`.

**Lucario v Weezing (pairing 21), where B2c found the habits:**

| | Lucario's score |
|---|---:|
| k3 | 50.4 |
| kp3 | 52.8 |
| kq3 | 62.8 |
| Limitless | 56.6 |
| the network against k3 (B2c, different deals) | 72.0 |

The habits move this cell the way the network plays it, and past Limitless.

What this shows, plainly:

- **The features do what they were built to do,** and they help the decks that build an attacker behind a cheap front Pokémon: Lucario, Blaziken, Hydreigon and Sceptile go up. On this table that is mostly the wrong direction. Sceptile and Hydreigon were already over-rated, and Lucario moves past Limitless.
- **Vespiquen gets worse again,** from 45.8 to 42.2 against 56.5, and Suicune drops a little further below Limitless. From the mixed rows (`../vespiquen_mixed_rows_2026-09-25`), Vespiquen loses when its opponents get better. Here the opponents' gains again outweigh anything the features give Vespiquen. So the Vespiquen deck-gap veto will very likely fire again.
- **Altaria is still under-rated** (50.2 against 54.0). The B5 habits don't close that gap.
- The laptop's adoption rule decides. This file only reports.

A natural follow-up is to run each feature alone (kq with only the clock change, and kq with only the Bench term, both at the same pre-set 250), to see which one moves which deck. That's a diagnostic, not a tuning, but it needs two new player codes, so it's the laptop's and Dustin's call.

## Files

- `kq3_500.{txt,jsonl}`: the kq3 table. `run_kq3_table.sh`: its command (legality_scan at ba20dd8).
- `identity_{k3,kp3}_500.{txt,jsonl}`: the full-table replays of k3 and kp3 with the kq code (a188c14), identical to the reference tables. `run_identity.sh`: their command.
- `timing.txt`: wall times.
