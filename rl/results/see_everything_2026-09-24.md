# See-everything test — 2026-09-24

**DIAGNOSTIC ONLY. These numbers come from bots that cheat, or that are handed the opponent's list. Never use them in a deck ranking or a win-rate table.**

Ran in Claude's cloud copy of the engine, not on the laptop. **Before any number here goes into RUN5.md or a plan, reproduce the Hydreigon v Lucario "list" row on the repo build** (the 58.3% rule, applied to a result). The patch is in `open-info.diff`.

## Question

Is the search bot losing games because it can't anticipate what the opponent holds? If a bot that knows more closes the gap to Limitless, is a bot that *guesses* from the opponent's list enough?

## Setup

- **Engine:** rules4 source (deckgym-fork-s193, `source-after.tar.gz` 69a7ce40…), add-on `pdl_rl_env` 0.7.2.
  - An unpatched rebuild of that source reproduces the laptop wheel's games (56/56).
  - Patched module: `mod-open2`, SHA-256 `fcb649c50b8f21d8…`. With `PDL_OPEN_INFO` unset it reproduces 28/28 table games.
- **Bot, both seats: `kr3`** (added by the patch). It is k3's search and value function (`public_clock_effect_value_function`, depth 3), plus a 3-ply search of the opponent's reply turn (`opponent_ply 3`, `consistent_horizon true`, `soft_opponent false`).
- **Deals:** the same as the Sept 23 k3 table. Seed = 72,000,000 + pairing×10,000 + i, with i = 0–499. Even i puts the first-named deck in seat 0. The "k3" column is k3 on those exact 500 seeds.
- **Pairings:** the five worst from the Sept 23 table.

### Arms (`PDL_OPEN_INFO=<mode>:<seats>`)

| Arm | Who gets extra information | What they get |
|---|---|---|
| blind | nobody | normal closed information |
| hand | both (symmetric) | real hands; **both decks' order reshuffled** at every decision, so deck order is unknown |
| full | both (symmetric) | real hands and real deck order |
| fullA / fullB | first-named / second-named deck only | real hands and real deck order |
| list | both (symmetric) | **not the hand.** The opponent's unseen cards (hand + deck, which is the exact list minus everything public) are pooled, shuffled and re-dealt to the real hand size. The bot's own deck is reshuffled too. One random guess per decision. |
| listA | first-named deck only | same as list |

To answer the handoff question directly: the main test was symmetric and ran both hand-only and hand-plus-deck-order arms. The one-sided arms used full information (hand plus order), and the list arms ran symmetric and Hydreigon-only.

## Results (first-named deck's score %, n = 500 per cell; ± is a 95% paired interval vs k3)

| Pairing | Limitless | k3 | blind kr3 | hand | full | fullA | fullB | list | listA |
|---|---|---|---|---|---|---|---|---|---|
| Altaria v Blaziken | 74.2 ±8.8 | 56.0 | 56.8 | 55.7 (−0.3 ±5.6) | 55.1 (−0.9) | 56.8 (+0.8) | 60.4 (+4.4 ±5.2) | – | – |
| Altaria v Lucario | 71.9 ±4.9 | 56.6 | 57.6 | 57.2 (+0.6 ±5.8) | 54.6 (−2.0) | 51.8 (−4.8 ±5.2) | 62.2 (+5.6 ±5.0) | – | – |
| Blaziken v Sceptile | 82.8 ±9.0 | 59.6 | 59.6 | 63.2 (+3.6 ±5.2) | 64.7 (+5.1 ±5.1) | 64.0 (+4.4) | 60.0 (+0.4) | – | – |
| **Hydreigon v Lucario** | **54.4 ±8.0** | **30.6** | 30.8 | **44.7 (+14.1 ±5.4)** | **46.8 (+16.2 ±5.5)** | 42.6 (+12.0 ±4.5) | 36.8 (+6.2 ±4.9) | **47.0 (+16.4 ±5.5)** | **42.4 (+11.8 ±4.5)** |
| Sceptile v Vespiquen | 33.1 ±8.2 | 66.6 | 66.6 | 65.8 (−0.8 ±5.3) | 67.0 (+0.4) | 60.4 (−6.2 ±4.7) | 69.6 (+3.0 ±4.9) | – | – |

Blind kr3 is the same game as k3 in 2,440 of 2,500 deals. Without extra information, the reply search almost never runs. It stops as soon as the opponent's opening draw would reveal an unknown card (`hidden_continuation_reason`).

## What it shows

1. **Hydreigon v Lucario is the only pairing that clearly moves, and guessing from the list gets all of it.** (Blaziken v Sceptile full +5.1 ±5.1 is borderline.)
   - Symmetric: list +16.4, hand +14.1, full +16.2.
   - Hydreigon only: list +11.8, full +12.0.
   - Knowing the real hand adds nothing over knowing the list, and deck order adds about 2 points (within noise).
   - That is about two-thirds of the gap to Limitless (16.4 of 23.8). The list arm lands at 47.0, inside Limitless's 54.4 ±8.0.
2. **What the bot lacked was not the hand. It was the ability to search past the end of its own turn.** Any complete guess at the opponent's cards lets the reply search run. Blind, it stops at the opponent's first draw.
3. **The gain is the Hyper Ray blind spot being fixed.** k3 fires Hyper Ray almost only for a KO. With the turn-crossing search, Hydreigon fires it in most spots where it doesn't KO: 84% when guessing from the list, 82% when seeing everything, vs 3% for k3 (next section).
4. **The other four pairings don't move in the symmetric arms.** This does not support "the bot can't anticipate the opponent" as the cause of the Altaria, Sceptile and Vespiquen misses. It does **not** rule it out, for two reasons:
   - It covers only this reply search.
   - The one-sided arms show that seeing everything can make a deck *worse*. Seven of the ten one-sided cells went against the deck that could see. Three of them are beyond noise: Lucario seeing in Altaria v Lucario (+5.6 for Altaria) and in Hydreigon v Lucario (+6.2 for Hydreigon), and Sceptile seeing in Sceptile v Vespiquen (−6.2). The reply search assumes the opponent's best answer every time, so more information can make it more timid.
   - So a flat symmetric result can hide gains and losses that cancel. Nulls here are weak, and this is not an upper bound.
5. **Quick Growth (Caterpie, in the Sceptile list):** weak evidence that it is not the main Sceptile cause.
   - In fullB, Vespiquen sees Sceptile's deck. That is exactly the case where the engine *can* price Quick Growth at end of turn (below). Sceptile v Vespiquen did not move toward Limitless (+3.0 ±4.9, the wrong way).
   - This bears only on whether the *opponent* anticipates Quick Growth. It says nothing about whether Quick Growth fires more often than in real games, which is what the code agent's Quick-Growth-off test (Sceptile 59% → 43%, real 48%) points at.
   - kr3 changes other things at once, so this isn't a clean test. The clean test is to fix only the Quick Growth pricing and rerun Sceptile's pairings.

## Speed (measured 2026-09-24; one cloud core, 20 games per cell, same deals)

| Pairing | k3 | kr3 blind | kr3 guessing from list (both sides) | list ÷ k3 |
|---|---|---|---|---|
| Altaria v Blaziken | 0.37 s | 0.55 s | 3.01 s | 8.1× |
| Altaria v Lucario | 0.38 s | 0.58 s | 2.55 s | 6.7× |
| Blaziken v Sceptile | 0.23 s | 0.33 s | 1.93 s | 8.4× |
| Hydreigon v Lucario | 0.23 s | 0.33 s | 1.69 s | 7.3× |
| Sceptile v Vespiquen | 0.70 s | 1.03 s | 4.68 s | 6.7× |
| Average | 0.38 s | 0.56 s | 2.77 s | **about 7×** |

- **One guess per decision.** The 47.0 came from a single guess, so no more guesses are needed. Each extra guess would multiply the cost.
- Games also run about 1.5 turns longer with the list.
- **Re-scoring all 28 matchups** at about 2.8 s per game:
  - 500 games per matchup ≈ 11 core-hours, about 5.5 hours on two cloud cores;
  - 1,000 per matchup ≈ 22 core-hours, about 11 hours.
  - This is an estimate from 5 of 28 pairings. Suicune and Vespiquen games are the slowest.
- **Training-time opponent: no, as built.** It manages about 0.35 games per second per core, against stage 1's 2M games in 7.4 hours (≈ 75 games per second). It is an evaluation-time bot.
- Blind kr3 costs 1.4–1.5× k3 and plays the same games. Option B should only run the reply search when it has a list to guess from.
- The code agent should re-measure on the repo build before planning the re-score. `scripts/speed.py` does it.

## Reproducing on the repo's option B player (`b` codes, commit 1adc455)

Read from the repo code on Sept 24, not tested.

- **The closest match to the list arm is `b3o3n1`:** k3's search, a 3-action opponent reply, and one guess per decision. The default is 4 guesses (`n4`), which should cost about 4× more (≈ 28× k3). The 47.0 came from one guess, so reproduce with `n1` first, then see whether `n4` adds anything.
- **`b3` with no `o` should behave like k3 here.** The Hyper Ray gain comes from searching into the opponent's turn. Without a reply search there's no turn to cross.
- **One real difference.** The repo's b player keeps the opponent's reply limited to public moves (`is_public_information_action`: attacks, retreats, abilities, draws, energy, ending the turn). My patch let the opponent play *any* card from its guessed hand in the reply. If `b3o3n1` falls short of about 47 on Hydreigon v Lucario, test this difference first.
- **Other differences that should be neutral:**
  - The repo scores each move per guess and adds the scores up; mine searched from one guessed state.
  - Both draw the hidden cards from the list minus everything visible.

## Hyper Ray and Roar in Unison (Hydreigon v Lucario, both bots kr3 unless noted)

| Condition | Hydreigon wins | Hyper Ray when it KOs: used / passed | Hyper Ray when it doesn't KO: used / passed | Roar used when healthy |
|---|---|---|---|---|
| k3, blind (first 500 table seeds) | 153/500 | 366 / 4 | 8 / 225 (**3%**) | 630/776 |
| kr3, Hydreigon sees everything (fullA) | 213/500 | 312 / 15 | 74 / 16 (**82%**) | 786/815 |
| kr3, Hydreigon guesses from list (listA) | 212/500 | 304 / 21 | 66 / 13 (**84%**) | 783/816 |

"KOs" means the opponent's Active had ≤130 HP left. The 8 "violations" flagged in the fullA count were artifacts of the check (two Hydreigon at the same board index, one self-KO), confirmed by replay. The 3 flags in the listA count are the same kind: a retreat moved a second Hydreigon into the index the first had used, and each Hydreigon used Roar once. One of those was a legal but odd play: Roar used on a 20-HP Hydreigon, knocking itself out.

## For the Hydreigon network run

The network run and this test target **the same blind spot**: Hyper Ray valued only as a KO, because k3's search never crosses into the opponent's turn. Expect the two fixes to overlap, not add up.

- Run the network blind, as designed. Adding an information condition would mix the two levers.
- **Record its Hyper Ray use when the attack doesn't KO**, alongside the win rate. If it approaches the searched bot's ~80%, the network learned the same fix. If it wins more with Hyper Ray still low, it found something else.
- The part neither explains yet is 47 → 54.4, which is within Limitless's ±8.0.

## Quick Growth: how the engine handles it (read from code, not tested)

`hidden_continuation_reason` (observation.rs) leaves EndTurn unpriced when the next player's Active has `RandomEvolutionFromDeck{EndOfOpponentTurnIfActive}` (Caterpie's Quick Growth) and that player's deck holds unknown cards. So the bot facing an Active Caterpie values its turn as if Caterpie will not evolve, and as if Checkup won't happen. The effect is consistent across its own choices, but it never prefers "KO the Caterpie now" for the reason that it's about to evolve.

## Caveats

- **Patch bug history.** The first list build crashed (`Player hand should contain card to remove`). Moves generated from the real state named hand cards that the re-dealt hand didn't have. The fix: during a pending mid-effect choice, list mode keeps the real state for that decision. That is a small leak toward full information on those decisions.
  - All crashed-build games were discarded.
  - A second runner left over from the crashed build wrote 48 duplicate rows. All matched the fixed build and were removed.
  - The first 120 list rows were re-played with the fixed module: 120/120 identical.
- **The list arms used the exact list.** A real version would guess the list from the archetype. List drift among top lists was small in the Sept 23 check, but that is an assumption to test.
- **One random guess per decision.** Averaging several guesses could do a little better or a little worse.
- **Only one pairing had list arms.** Hydreigon v Lucario was the only one where information mattered.

## Files

- `open-info.diff`: the full patch (diagnostic only; unset env var = unchanged engine), applied to deckgym-fork-s193/src. It touches four files:
  - `observation.rs`: the mode and the thread-local store;
  - `game.rs`: builds the open state for each decision;
  - `players/expectiminimax_player.rs`: searches from it and lets the reply search consider every opponent move;
  - `players/mod.rs`: the `kr<N>[o<P>]` code.
- `omnirun.py`: runs the arms; `MOD`, `ONLY`, then arms and games as arguments; resumable.
- `omnian.py`: prints the results table.
- `hydcount_open.py` and `hydsum.py`: the Hyper Ray/Roar counts (`OPENMODE=hydfull|hydlist`).
- `omni_games.jsonl`: all 13,500 games.
- `k3table_games.jsonl`: the Sept 23 k3 table, 28,000 games.
- `hydcount_*.json`: per-turn counts.
- `limitless_b4a_2026-09-23.json`: the Limitless cells.
- `decks/`: the eight lists used. Fingerprints (first 16 hex of SHA-256):
  - altaria 435a2bebc567ca83, blaziken fb08470e8801e93c
  - hydreigon 6ea0042236b48444, lucario 46a4820bc788b4fd
  - sceptile 7404c99e49161e68, suicune 7affe6530b8d096b
  - vespiquen fc3a0ffd1997f202, weezing c322fe64d6052bf9
- `modcheck.py`: confirms a build reproduces the Sept 23 table games.
- `omniverify.py`: re-plays list rows to check them.
- The scripts use a hard-coded scratch path (`S=`); change it to the repo location.
