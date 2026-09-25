# Option B attribution: which part moves the table (Sept 24–25, Claude Code, cloud)

Asked by the laptop session for Dustin's overnight plan. Diagnostic only, never for a ranking. Code is on
branch `claude/pensive-ptolemy-spwc0b` (not merged): `25a6d00` (Hyper Ray counter), `1ff4b83` (fix 1),
`43ef80a` (fix c). Raw outputs and scripts: `option_b_attribution_2026-09-24/`.

## Short answer

- **The guess is the part that moves the table.** On its own (`b3n1`, one guess, no reply search), it moves
  Hydreigon v Lucario +12.2 and Blaziken v Sceptile +9.5, both toward Limitless.
- **Averaging 4 guesses adds nothing measurable** (every n4 vs n1 difference is under 3.5 points). One
  guess is enough, at a quarter of the cost.
- **The reply search adds little win rate** on top of the guess (+1.9 on Hydreigon v Lucario, within
  noise). It is what turns Hyper Ray chipping back on (1% → 65%).
- **Neither code fix changed a single game** in the 2,500 deals: same numbers, cell for cell.
- **Why the guess helps: k3 refuses to price four cards while the opponent's hand is hidden**, and a guess
  unblocks them. Copycat is in all eight lists. Hydreigon's gain comes mostly from Mega Absol ex's
  Darkness Claw and Copycat, not from Hyper Ray. That suggests a cheaper fix with no list at all (last
  section).

## Win rates (first deck %, the table's first 500 deals)

| Pairing | Limitless | k3 | b3n1 | b3n4 (laptop) | b3o3n1 | b3o3n4 (laptop) |
|---|---:|---:|---:|---:|---:|---:|
| Hydreigon v Lucario | 54.4 ±8.0 | 30.6 | 42.8 | 42.8 | 44.7 | 45.4 |
| Blaziken v Sceptile | 82.8 ±9.0 | 59.6 | 69.1 | 68.3 | 64.1 | 65.0 |
| Altaria v Blaziken | 74.2 ±8.8 | 56.0 | 59.4 | 56.0 | 58.0 | 58.4 |
| Altaria v Lucario | 71.9 ±4.9 | 56.6 | 54.6 | 56.2 | 58.2 | 59.0 |
| Sceptile v Vespiquen | 33.1 ±8.2 | 66.6 | 64.6 | 63.6 | 62.4 | 61.2 |

- My k3 reproduces the laptop's k3 exactly, down to the distinct-game counts (497–500 of 500 per cell; a
  few different deals play out to identical move lists, which is not the one-game-N-times bug).
- With fix 1, and with fixes 1 and c together, `b3n1` and `b3o3n1` give **identical** numbers in every cell,
  and identical Hyper Ray counts. `b3n4` and `b3o3n4` rerun on Hydreigon v Lucario with both fixes give
  42.8 and 45.4, the laptop's pre-fix numbers exactly.
- **Noise:** 500 paired deals per cell. Treat differences under about 5 points as noise.

## What each part contributes

| Comparison | What it isolates | HvL | BvS | AvB | AvL | SvV |
|---|---|---:|---:|---:|---:|---:|
| b3n1 − k3 | the guess (and the lost certificate, which never fires; below) | **+12.2** | **+9.5** | +3.4 | −2.0 | −2.0 |
| b3n4 − b3n1 | averaging over 4 guesses | 0.0 | −0.8 | −3.4 | +1.6 | −1.0 |
| b3o3n1 − b3n1 | the 3-move reply search | +1.9 | −5.0 | −1.4 | +3.6 | −2.2 |
| b3o3n4 − b3o3n1 | averaging, with the reply search | +0.7 | +0.9 | +0.4 | +0.8 | −1.2 |
| fix 1, fix c | the two code fixes | 0 | 0 | 0 | 0 | 0 |

Only the guess moves anything beyond noise, and only in the two pairings where a card it unblocks is played
a lot (below).

- Altaria's two cells and Sceptile v Vespiquen don't move beyond noise under any variant.
- Even the best variant leaves every cell but Hydreigon v Lucario 13 or more points off Limitless (Altaria v
  Lucario by 12.9). Those misses are not about hidden cards or this reply search.

## Why the guess helps: cards k3 leaves unpriced

`hidden_continuation_reason` (`engine/src/observation.rs`) leaves unpriced any Trainer, attack or ability
whose text contains "opponent" together with "hand" or "deck", whenever the opponent's hand or deck holds
Unknown cards. Unpriced means k3 scores the position as if the move did nothing. So Darkness Claw's 80 damage
counts as zero, and Copycat counts as a no-op. Blind, the opponent's zones are always Unknown.

Cards in the eight table lists that the rule catches:

| Card | In | Text |
|---|---|---|
| Copycat | all eight | Shuffle your hand into your deck. Draw a card for each card in your opponent's hand. |
| Mega Absol ex, Darkness Claw | Hydreigon | Your opponent reveals their hand. Choose a Supporter card you find there and discard it. |
| Mars | Weezing | Your opponent shuffles their hand into their deck and draws a card for each of their remaining points needed to win. |
| Team Rocket's Boss | Suicune | Look at your opponent's hand and put any number of Basic Pokémon you find there onto your opponent's Bench. |

(Caterpie's Quick Growth and Team Rocket's Weezing ex's Boiler Smog are handled by separate rules.)

A guess fills the Unknown slots, so these are priced. Plays in 250 games, both sides the same bot
(`tally_attacks.sh`):

| | k3 | b3n1 |
|---|---:|---:|
| **Hydreigon v Lucario:** Hydreigon wins | 32.0% | 38.4% |
| Darkness Claw | 76 | **255** |
| Copycat (both sides) | 214 | **457** |
| Hyper Ray | 198 | 155 |
| **Blaziken v Sceptile:** Blaziken wins | 61.2% | 70.8% |
| Copycat (both sides) | 88 | **347** |
| Attacks | nearly unchanged | nearly unchanged |

Seeds: 72,130,000–72,130,249 with Hydreigon always in seat 0; 72,090,000–72,090,249 with Blaziken always in
seat 0. These are table seeds, but not the table's alternating seats.

## Hyper Ray (Hydreigon v Lucario, same per-turn definition as `see_everything_2026-09-24.md`)

| Bot | Hydreigon wins | KO-able: used / passed | Not KO-able: used / passed |
|---|---:|---|---|
| k3 | 30.6% | 366 / 4 | 8 / 225 (**3%**) |
| b3n1 | 42.8% | 320 / 4 | 1 / 114 (**1%**) |
| b3n4 | 42.8% | 312 / 3 | 1 / 88 (**1%**) |
| b3o3n1 | 44.7% | 309 / 29 | 67 / 36 (**65%**) |
| b3o3n4 | 45.4% | 299 / 20 | 59 / 30 (**66%**) |
| see-everything, Hydreigon guessing from the list (reference) | 42.4% | 304 / 21 | 66 / 13 (84%) |

- The counter reproduces the see-everything file's k3 row exactly.
- Without the reply search, the guess wins more while chipping with Hyper Ray *less* than k3. The gain is
  elsewhere (the card table above).
- The reply search turns chipping on, 65% against the see-everything patch's 84%. One plausible reason: the
  repo's reply search only considers the opponent's public moves (`is_public_information_action`), while
  that patch let the opponent play any card from the guessed hand.

## The two code fixes

- **Fix 1** (`1ff4b83`): the b-tiers now consult the public-reply certificate before a turn-boundary
  fallback, as k3 always does.
  - It is correct and costs nothing, but it changes no game here.
  - A counting probe (`certificate_count_probe.patch`, scratch only) ran 100 deals each of Hydreigon v Lucario
    and Altaria v Blaziken. The certificate proved an opponent win **0 times**: out of 208,606 consultations
    for k3, 252,640 for b3n1 and 603,884 for b3o3n1.
  - It is an audited, narrow registry that none of these decks' attacks reach. So "the lost certificate" is
    not part of b3's effect here.
- **Fix c** (`43ef80a`): cards publicly known to be in the opponent's deck are no longer guessed into their
  hand. No game changed in these deals. With nothing known it is the same random stream as before, by
  construction.
- **Checks:**
  - k3 Altaria v Blaziken, 1,000 table deals, with both fixes: **58.3%** (the table's number).
  - The b3-with-an-empty-list = k3 test passes.
  - The full engine suite: 1,829 passed, 0 failed.
  - Each new test was shown to fail without its fix.

## Speed (this cloud machine, 4 cores, 2,500 games per bot)

k3 took 247 s (while builds shared the CPU), b3n1 257–268 s and b3o3n1 825–843 s.

- b3n1 costs about the same as k3, and b3o3n1 about 3.4× k3. That is well under the see-everything estimate
  of 7×.
- A 28-pairing × 500-deal re-score with b3o3n1 would take about 80 minutes here.
- n4 costs about 4× n1 for no measurable change, so b3o3n1 would do for tonight's laptop re-score just as
  well as b3o3n4.

## Proposed next step (not built)

Price the four cards from public information in blind k3, and drop the list:

- Copycat by the opponent's hand *count*, which is public.
- Darkness Claw by its fixed damage, with the discard left unpriced.
- Mars by the opponent's remaining points, which are public.
- Team Rocket's Boss as a small expected bench change.

Then compare "k3 + public pricing" with b3n1 on these five cells. If it reproduces b3n1's +12 and +9.5, the
table gets the guess's gain without assuming anyone's decklist, which also serves brews with no list to guess
from.

## Seeds and files

- **Seeds:**
  - Win rates: the table's deals only, 72,000,000 + pairing × 10,000 + i with i < 500 (i < 1,000 for the
    58.3% check, i < 100 for the certificate probe), even i = first-named deck in seat 0.
  - Tallies: as noted above.
  - No new seed blocks were used.
- **Files:**
  - `a_before_fix_*`: k3, b3n1, b3o3n1 before the fixes.
  - `b_fix1_*`: fix 1 only.
  - `c_fix1c_*`: fixes 1 and c.
  - `check_k3_fix1c_k3.txt`: the 58.3% check.
  - `d_fix1c_hvl_*`: the n4 Hyper Ray counts.
  - `timing.txt`
  - `queue.sh`: the run order.
  - `tally_attacks.sh` and the four `*_attacks_*.log.gz`: the card tallies.
  - `certificate_count_probe.patch` and `_output.txt`.
- The laptop's b3n4 and b3o3n4 numbers are from `option_b_first_look_2026-09-24.txt`.
