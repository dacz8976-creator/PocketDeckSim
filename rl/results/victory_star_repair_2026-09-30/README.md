Decision this informs: none yet. This is a drafted engine repair for a later engine switch (the Fable coordinator via Dustin, Sept 30: "Yes, have the cloud draft the Victory Star repair"). It is not merged to main and not pinned. There was no table game and no identity replay: the laptop does that replay at the switch that takes this repair.

Seeds: no table deal. The smoke check below played scratch decks only, on seeds 20,930,000,000 + i (Claude Code's diagnostic block, outside START_HERE's ranges).

# Victory Star with a Confused attacker: the drafted repair

## In plain words

- **What Pocket does** (rules/04 §9; rules/09's entry; confirmed in-game Sept 29, recordings 202314 and 203025):
  - A Confused attacker flips its Confusion coin first. That coin is never offered for a reroll.
  - On tails the attack does nothing, and no Victory Star offer appears.
  - On heads the attack's own coins are flipped, and Victory Star is offered on them as usual. If it is taken, the coins are flipped again, with no second Confusion check.
- **What the engine did:** it never offered Victory Star while the attacker was Confused. It flipped Confusion and the attack's coins together, with no offer.
- **What it does now:** exactly what Pocket does, above.
- **What stays as it was** (none of these has been seen in the game with Victory Star):
  - an attacker with CoinFlipToBlockAttack, Confused or not: no offer, the same resolution as before, as rules/09 asks;
  - a Confused attacker with Will pending: the legacy resolution, because which coin Will turns to heads there is unverified;
  - a Confused attacker whose attack flips no coins of its own: no offer, as before;
  - a copied attack (for example Genome Hacking's): unchanged.
- **Who can reach it:** only a side with Victini (B3 025 or P-B 049, the only printings with Victory Star) in play, with a Fire Active that is Confused. No deck list under `decks/` has either id; the only Victini in `decks/` is in a brew scorecard. So no table game reaches the new code, and the laptop's table replay should show 0 changed games.

## Commits (branch `claude/pensive-ptolemy-spwc0b`)

1. `265ce95`: the failing tests, committed before the fix.
2. `4d026a5`: line endings only. The first commit rewrote `b4a_attack_batch2_test.rs` with Unix line endings by accident, which `.gitattributes` forbids. This puts back the Windows ones; the content is unchanged.
3. `6415e39`: the fix, the restated legacy test, and `instrument_scan.py`.
4. The commit that adds this README, `suite.log` and `smoke/`. CLOUD_STATUS.md is updated in the commit after it.
5. The Fable coordinator's addition (via Dustin): the restated test also checks that a Confusion tails offers no reroll, and that the offer on heads is on the attack's own coins. It is test-only, and the engine is unchanged from `6415e39`.

The engine diff from the base (`2711df0`) is 4 files in `engine/`: the two source files and two test files. Nothing in `players/` changed.

## The gate (RUN5's repair template, part 1: read it in the code)

Line numbers are at `6415e39`.

- `engine/src/actions/apply_attack_action.rs`:
  - `victory_star_waits_for_confusion_heads` (line 117) is the gate. It holds for a Confused attacker's own attack (not a copied one), without CoinFlipToBlockAttack and without Will pending.
  - `confusion_tails_outcomes` (136) is the Confusion tails: the attack does nothing. It is the old path's tails branch, through the same defender modifiers.
  - `finish_attack_after_confusion_heads` (152) finishes the attack after the Victory Star choice with the defender's modifiers only, so there is no second Confusion check.
  - `has_unverified_attacker_coin_gate` (96) is unchanged apart from its comment.
- `engine/src/actions/apply_action.rs`:
  - `try_forecast_victory_star_attack` (185):
    - It returns at line 193 unless a Victini is in play, so none of the new lines run without one.
    - Line 197 reads the gate. When it holds, line 290 makes the Confusion coin: tails is committed as the ordinary attack path commits it, and heads is the usual pause on the attack's own coins.
    - When it doesn't hold, line 206 keeps the old refusal for CoinFlipToBlockAttack (and for Confusion with Will pending).
  - `forecast_victory_star_choice` (319) reads the gate again at line 364, where Keep or Reroll commits.
    - A Confused attacker can reach the choice only through its Confusion heads, so the two readings agree.
- Both new paths write a `debug!` line: "Confusion coin first, pause on heads only" and "no second Confusion check".

## Tests

All use a Confused attacker with Victini on the Bench. "Before" is `265ce95`, the engine without the fix.

| test | file | before | after |
|---|---|---|---|
| `confused_heat_charged_flips_confusion_first_then_offers_victory_star_on_its_own_coins` | `b4a_attack_batch2_test.rs` | fails | passes |
| `a_victory_star_reroll_after_confusion_heads_resolves_with_no_second_confusion_check` | `b4a_attack_batch2_test.rs` | fails | passes |
| `coin_flip_to_block_attack_keeps_its_resolution_without_a_victory_star_offer` (guard) | `b4a_attack_batch2_test.rs` | passes | passes |
| `confusion_coin_comes_before_the_attack_effect_pause_and_tails_does_nothing` | `victini_victory_star_test.rs` | fails | passes |

- **The first test:** Team Rocket's Moltres ex (Heat Charged: flip 3 coins, a Fire Energy for each heads), on 200 seeds.
  - On a Confusion tails: nothing is attached, and no offer appears.
  - On a heads: the offer is on Heat Charged's three coins, before any Energy is attached, and Keep attaches one Energy per heads.
  - Before the fix it failed at seed 1: Confusion heads, 2 Energy attached, no offer.
- **The second:** after a Confusion heads, a reroll always resolves its fresh coins. Nothing is attached only when all three are tails (1 in 8), where a second Confusion check would make it nearly 1 in 2. It needs more than a quarter of the rerolls to attach something.
  - Before the fix: 0 rerolls, because no offer was ever made.
- **The guard:** CoinFlipToBlockAttack, Confused or not, 40 seeds each: no pause and no offer, before and after.
- **The restated test** (the one at about line 341 that pinned the old rule): Mega Houndoom ex's Grimhound Flare (flip 3 coins, 80 for each heads), Confused, 40 seeds.
  - No damage lands before the choice.
  - On a Confusion tails the attack does nothing, no reroll is offered, and Victory Star stays unused, exactly as before the repair.
  - On a heads the offer is on Grimhound Flare's three coins.
  - Both cases occur.
  - It replaces `confusion_combination_stays_on_explicit_legacy_boundary`, which asserted that a Confused attacker never gets the pause. That old test passed only because its one seed (3) gave Confusion tails.
  - Before the fix it failed at seed 1: 160 damage at once (the defender at 240), with no pause. It was run on a scratch copy of `265ce95`'s engine, both as first restated and as strengthened.
  - **The order differs from the coordinator's.** The coordinator asked for this test to be flipped, seen to fail and committed before the fix. It was flipped in the fix commit (`6415e39`); only the `b4a` tests were committed before it (`265ce95`). Its failure on the old engine was seen in the scratch copy, not in a commit of its own.

## The unit suite

`cargo test --release --features test-utils`: **1,994 passed, 0 failed, 0 ignored**, in 101 test programs (`suite.log`).

- That is build B's 1,991 (`../km_build_2026-09-30/BUILD.md`) plus the three new tests. The restated test replaces one, so it adds none.
- No other test's expected value was edited.
- The suite ran on the working copy before the line endings in the two source files and the Victini test file were restored. The content, line endings aside, is `6415e39`'s.
- The build has no new warnings: the 5 it prints are the old ones in other files.

## Instrumentation (part 2) and the smoke check

`instrument_scan.py` patches a copy of `engine/examples/legality_scan.rs` in place, like the Sept 26 switch's script. It adds two per-game counters to the `--games-out` line:

- `vs_confused_attack`: attacks by a Confused Fire Active whose side has a Victini in play and has not used Victory Star that turn.
  - It counts a wider set than the gate itself, which also needs coins on the attack and no CoinFlipToBlockAttack or Will. So 0 in a game means the new code never ran there.
- `vs_confused_choice`: Victory Star choices (Keep or Reroll) made while the chooser's Active is Confused. The old engine never offers one.

**The smoke check** (`smoke/`, run in scratch copies; no table deck):

- **Decks:** two 20-card lists made only for this check.
  - `fire_victini.txt`: 2 Team Rocket's Moltres ex, 2 Victini (B3 025), 2 Torchic, and Blaziken's Trainers.
  - `psychic_confuse.txt`: 2 Chatot (A3b 060, Tone-Deaf), 2 Misdreavus (P-A 038, Confuse Ray) and 2 Ralts (B2 063, Confuse Ray), all of which Confuse, and the same Trainers.
- **Play:** kog3 on both sides, 40 games, seeds 20,930,000,000 + i (`--pairs pairs.tsv --seed-base 20930000000 --games 40 --bot kog3`).
- **Three scans:**
  - the engine without the repair (`265ce95`), instrumented;
  - the repaired engine, plain;
  - the repaired engine, instrumented.
- **Results** (`compare.py`, `compare_output.txt`):
  - **The counters change no play:** the repaired engine's plain and instrumented scans give the same moves in 40 of 40 games.
  - **Without the repair:** Confused Fire attacks with a Victini in play in 40 games (164 attacks), and 0 Victory Star choices while Confused.
  - **With the repair:** those attacks in 39 games (174), and 8 Victory Star choices while Confused, in 8 games.
  - **The repair changes 13 of the 40 games.** All 13 had such an attack before the repair: every changed game reaches the mechanic.
  - The other 27 games also had such attacks but are unchanged. In this deck only Moltres ex's Heat Charged flips coins; Torchic's Peck and Victini's V-Flame don't, so those attacks take the old path. The counter counts them too, since it counts a wider set than the gate. Which Pokémon attacked is not recorded per game.
- **The scans' sha256:**
  - without the repair, instrumented: `096a6eef2e39418621c07e193a6ace11228046e4ffc1c76f3b9f54e862b01215`;
  - repaired, plain: `e19cadbbd2b757497cdb5b0904eb7b407cda2ccf66f5a1c07c2295100308d211`;
  - repaired, instrumented: `c20ca07785805b82cd5f95369ecd889ce040fbc065023f616f2b21d54fcc948d`.
  - They are scratch builds, for this check only.

## What the laptop replays later (at the switch that takes this repair)

1. Bring `6415e39`'s changes to the four `engine/` files into the switch's engine and build it.
2. Run the unit suite.
3. Replay the table the switch procedure names (RUN5, "Engine repairs: the switch procedure") on the engines without and with the repair, and list the changed games. **Expected: 0**, because no table deck has a Victini, and the new lines run only with one in play.
4. Run the instrumented scan (`python3 instrument_scan.py <copy of legality_scan.rs>`, then build the copy). Check two things:
   - both counters are 0 in every table game;
   - the scan's move fingerprints equal the plain scan's, so the counters change no play.
5. If any game does change, trace it to its first divergence (the template's part 3), with the counters showing whether it reached the gate.

One caution from RUN5's refactor rule: identical table games never run the new lines, so they say nothing about them. The evidence that those lines do what Pocket does is the tests and the smoke check above.

rules/09's entry and rules/04 §9 are not edited here. The entry stays open until a switch adopts the repair.

## Limits

- The unseen combinations above keep the old resolution. They are gated, not fixed.
- The Confusion coin is the engine's existing coin (half heads, tails does nothing), unchanged. Only its order relative to Victory Star is new.
- The smoke check's decks exist only for this check. Their games say nothing about any deck's strength.

## Files

- `README.md`: this note.
- `instrument_scan.py`: the watch-only counters for the scan.
- `suite.log`: the full unit suite.
- `smoke/`: the smoke check.
  - `fire_victini.txt`, `psychic_confuse.txt`, `pairs.tsv`: its decks and pairing.
  - `games_legacy_instr.jsonl`, `games_fixed_plain.jsonl`, `games_fixed_instr.jsonl`: its games.
  - `compare.py`, `compare_output.txt`: the comparison.
