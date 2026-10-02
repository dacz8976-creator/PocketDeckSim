Decision this informs: none yet. This is a drafted engine repair for a later engine switch (the Fable coordinator via Dustin, Sept 30). It is not merged to main and not pinned. There was no table game and no identity replay: the laptop does that replay at the switch that takes this repair. Release approval waits on the laptop's review, including the per-thread design in (a), and on its replay checks. **No independent audit of the patch has been done yet.**

Seeds: no table deal. The Part 1 probe used 20,940,000,000 + i, and the smoke check below 20,950,000,000 + i, on scratch decks only (Claude Code's diagnostic block, outside START_HERE's ranges).

# Coin-flip damage prevention: the drafted repair

## In plain words

- **What Pocket does** (rules/02, step 4; rules/09, "Open engine bugs", lines 85-114). Four Abilities read "If any damage is done to this Pokémon by attacks, flip a coin":
  - Carefree Steps (Meowth B2 124, B2 204) and Celestial Blessing (Togekiss A4 080): heads prevents the damage;
  - Guarded Grill (Bastiodon A2 114): heads, −100;
  - Securely Sheltered (Hisuian Goodra B3b 050): heads, −80.
  - They are effects on the Defending Pokémon, so the cut comes after the attacker's bonuses and Weakness.
  - They apply to any damage from an attack, including damage the attacker aims after the attack is chosen.
- **(a) What the engine did:** it took Guarded Grill's and Securely Sheltered's cut off the attack's raw damage, before Weakness and Bounded Field. **Now:** the cut comes off in step 4, with the other effects on the Defending Pokémon.
  - Example: Charmeleon's Fire Claws (60) into Bastiodon under Bounded Field, heads. Before: 60 − 100 = 0. Now: 120 − 100 = 20.
  - Full prevention (Carefree Steps, Celestial Blessing) is order-free and unchanged.
- **(b) What the engine did:** damage an attack delivers through a queued choice (a snipe, or damage to the Pokémon it switches in) never flipped the coin. **Now it does**, for the helpers Part 1 confirmed and this round changes:
  - the `DirectDamage` group (for example Heatmor's Tongue Whip);
  - Pierce the Pain and Blindside;
  - Diving Icicles and Volt Bolt;
  - Energy Arrow;
  - Volcanic Ash;
  - Pull In and Pound and Entrap;
  - **Chase Order (Vespiquen ex), with and without the discard.** This came in the follow-up: Dustin, Sept 30, "fix it now", with `apply_action.rs` allowed as a fourth file.
- **Not changed** (Dustin's answers, Sept 30):
  - **Left open:** `also_choice_bench_damage` in its own-Bench form (Zapdos's Raging Thunder, Emolga, Luxray's Flash Impact). It involves a separate interaction: its one queued choice also hits your own Bench, where a Guts coin would be dropped.
  - **Recorded for a later round, not changed.** Each of these skips the coin too:
    - the six sites Part 1 found outside the seven:
      - Wellspring Mask Ogerpon's Wellspring Dance;
      - Rapid Strike Urshifu's Tornado Shot;
      - Blastoise's Double Splash and Mega Blastoise ex's Triple Bombardment;
      - Mega Kangaskhan ex's second punch;
      - Hoopa's Mischievous Ring;
      - Slowking's Litter.
    - **Gyarados's Wild Swing (A4 045, A4 215),** found during the Chase Order follow-up. Part 1 missed it: it queues its damage through the same discard action as Chase Order (`DiscardOwnBenchedThenDamage`), and is left exactly as it was. A4 045 is in one list: the panel ladder's l-sharpedo.
- **Which games could change: none between two lists under `decks/`.** Both repairs run only when a Pokémon with one of those five Ability printings is in play, and no list under `decks/` has one (`HELPERS.md`, "The defenders").
  - Some lists hold attackers that (b) changes:
    - Heatmor (research/blaziken, t-blaziken, Dustin's 06);
    - Hitmonlee (research/lucario, t-lucario, three gauntlet Lucario variants);
    - Grovyle (research/sceptile, t-sceptile);
    - Absol (Dustin's 02);
    - Gabite (Dustin's 08);
    - Chien-Pao ex (research/suicune, t-suicune, three gauntlet Suicune variants, l-sharpedo);
    - Team Rocket's Hypno (Dustin's 14);
    - Vespiquen ex, Chase Order (B4 011: research/vespiquen, t-vespiquen, and two Vespiquen variants in variants-2026-09-23).
  - Their play changes only in a game against one of those five printings, and no list has one. So Vespiquen ex's 4 lists add nothing: still **0 expected changed table games**. On the ladder, it would be a game where the opponent has one in play.

## Commits (branch `claude/pensive-ptolemy-spwc0b`)

1. `31a9dbf`: the log line in CLOUD_STATUS.md, before the job.
2. `7fa2f85`: Part 1, `HELPERS.md` (read-only; committed before any code). `6accbb0`: its three questions in CLOUD_STATUS.md.
3. `0785365`: the two pinning fixtures in `hooks/core.rs`, flipped to the rules and failing, in their own commit.
4. `d21511a`: more failing tests, before the fix: two for (a) and seven for (b).
5. `5942d1a`: the fix and `instrument_scan.py`.
6. `391a010`: this README, the suite log and `smoke/`. `b35aeff`: CLOUD_STATUS.md.
7. **The Chase Order follow-up:**
   - `a1858cd`: the log line.
   - `c350e70`: the failing tests (no discard and discard) plus the control, in their own commit.
   - `e52a73b`: the gated fix.
   - `66f9731`: this README and `suite.log`. `dc9618c`: CLOUD_STATUS.md.
8. **Sonnet's follow-ups S1-S4** (Sonnet's independent read found both drafts "ready for the laptop's switch review", no blockers):
   - `d42430e`: the log line.
   - `52daee6`: the tests, S1's failing.
   - `c9df626`: S1's hardening, the last engine commit.
   - Then the commit updating this README, `suite.log` and `smoke/rerun_e52a73b/`, and CLOUD_STATUS.md after it.

The engine diff from the base (`31a9dbf`) is 6 files: `attack_outcome.rs`, `hooks/core.rs` and `apply_attack_action.rs` (the three permitted), `apply_action.rs` (the fourth, allowed for Chase Order), and two test files, `tests/pokemon/hisuian_goodra_securely_sheltered_test.rs` and `tests/pokemon/meowth_carefree_steps_test.rs`. Nothing in `players/` changed.

## The gates (RUN5's repair template, part 1: read them in the code)

Line numbers are at `5942d1a`.

- **(a)**
  - `attack_outcome.rs` `split_with_damage_prevention` (619, the new lines at 654-667): on a heads, full prevention still removes the damage. A finite cut now keeps the damage and records the cut in the branch's `heads_coin_cuts` (field at 91).
  - The cut is put in force only while that branch's damage is calculated: `with_heads_coin_cuts` (43), called at 213 when the damage is applied. The same function is used in the expected-damage and knock-out checks for Guts, point denial and Perish Body, so they see the same number.
  - `hooks/core.rs` `modify_damage` (2065) reads it through `heads_coin_cut` (`attack_outcome.rs` 62) and takes it off in step 4, with the other reductions. Everywhere else it is 0.
  - So the new code runs only in a heads branch of Guarded Grill or Securely Sheltered.
- **(b)** `apply_attack_action.rs` `queued_attack_damage_choice` (281), with `coin_damage_prevention` (264):
  - A queued choice aimed at an opponent's Pokémon with a coin Ability becomes `ApplyQueuedAttackDamage`. That runs the defender's attack modifiers (`finish_queued_attack_damage`), as the attack's own damage does, and flips the coin.
  - Every other target stays `ApplyDamage`, exactly as before.
  - Used by `push_direct_damage_choices` (2859), `direct_damage_if_damaged` (2903), `discard_all_energy_of_type_then_damage_any_opponent_pokemon` (2928), `self_discard_energy_then_damage_any_opponent_pokemon` (3894), `damage_to_any_opponent_per_target_energy` (4528) and `switch_in_opponent_benched_then_damage` (6487).
  - For Pull In and Pound, the Pokémon switched in is chosen after the damage is queued. So there the gate is "any of the opponent's Benched Pokémon has a coin Ability", and the coin is checked on the new Active when the damage resolves.
- **Chase Order** (line numbers at `e52a73b`):
  - **Without the discard:** `optional_discard_benched_basic_for_extra_damage` (`apply_attack_action.rs` 4418) queues the damage through `queued_attack_damage_choice`, gated like the helpers above on the opponent's Active.
  - **With the discard:** `apply_action.rs`'s `apply_discard_own_benched_then_damage` (1306) queues the damage through `discard_then_damage_choice` (`apply_attack_action.rs` 311). That takes the coin-flipping path only when both hold:
    - the opponent's Active has a coin Ability;
    - the attacker's Active has Chase Order among its printed attacks (`chase_order_attack`, 329).
  - Otherwise it is the same `ApplyDamage` as before. That covers every other attack sharing the discard action, which today is Gyarados's Wild Swing.
  - The debug line and the scan counter are (b)'s: "Queued attack damage at a coin-flip damage Ability" and `coin_queued_attack_damage`.
- **Logging.** Both gates write a `debug!` line: "Coin-flip damage cut on heads", and "Queued attack damage at a coin-flip damage Ability".
- **Saturation bound.** `hooks/core.rs` `active_attack_damage_saturation_requirement` (1400) still adds the finite cut to the reductions. That bound stays valid with the cut in step 4, so only its comment changed.

## Tests

| test | file | before the fix | after |
|---|---|---|---|
| `guarded_grill_under_bounded_field_comes_off_after_weakness` (was `..._pins_the_engines_current_order_coin_cut_before_weakness`) | `src/hooks/core.rs` | fails: 60, not 70 | passes |
| `a_direct_damage_snipe_on_togekiss_flips_celestial_blessing` (was `..._pins_the_engines_current_behaviour_no_coin`) | `src/hooks/core.rs` | fails: 30, not 15 | passes |
| `test_guarded_grill_cut_comes_off_after_weakness` (Magcargo 90 into Bastiodon: heads 10) | `tests/pokemon/hisuian_goodra_securely_sheltered_test.rs` | fails: heads did 0 | passes |
| `test_securely_sheltered_cut_comes_off_after_the_attackers_bonus` (Dubwool 80 + Training Area into Goodra: heads 10) | same | fails: heads did 0 | passes |
| `carefree_steps_flips_for_a_direct_damage_snipe` (Tongue Whip) | `tests/pokemon/meowth_carefree_steps_test.rs` | fails: 0 prevented of 60 | passes |
| `carefree_steps_flips_for_direct_damage_to_a_damaged_pokemon` (Pierce the Pain) | same | fails: 0 of 60 | passes |
| `carefree_steps_flips_for_damage_after_discarding_all_energy_of_a_type` (Diving Icicles) | same | fails: 0 of 60 | passes |
| `carefree_steps_flips_for_damage_per_energy_on_the_target` (Energy Arrow) | same | fails: 0 of 60 | passes |
| `carefree_steps_flips_for_damage_after_discarding_energy` (Volcanic Ash) | same | fails: 0 of 60 | passes |
| `carefree_steps_flips_for_damage_to_the_pokemon_switched_in` (Pull In and Pound) | same | fails: 0 of 60 | passes |
| `only_a_snipe_at_a_coin_ability_pokemon_takes_the_coin_path` (the gate: a snipe at Bulbasaur stays `ApplyDamage`) | same | fails: both were `ApplyDamage` | passes |
| `carefree_steps_flips_for_chase_order_without_the_discard` (Chase Order 70 into Meowth) | same | fails: 0 of 60 | passes |
| `carefree_steps_flips_for_chase_order_with_the_discard` (a Benched Combee discarded, 140) | same | fails: 0 of 60 | passes |
| `chase_order_into_a_pokemon_without_a_coin_ability_is_unchanged` (the control: into Mega Latios ex, both choices are queued as `ApplyDamage` and do 70 and 140) | same | passes | passes |

| `heads_coin_cuts_are_scoped_to_their_own_call` (S1: a cut is in force only inside its own call and on its own target; an empty inner call doesn't inherit; nothing is left after a panic) | `src/actions/attack_outcome.rs` | fails: an empty inner call saw the outer 100 | passes |
| `wild_swing_into_carefree_steps_pins_todays_behaviour_no_coin` (S2: pins a known gap, Wild Swing with and without the discard, 0 prevented of 60) | `tests/pokemon/meowth_carefree_steps_test.rs` | passes (pin) | passes (pin) |
| `carefree_steps_never_flips_for_an_abilitys_damage` (S4: Greninja's Water Shuriken always does 20) | same | passes | passes |
| `celestial_blessing_never_flips_for_a_tools_damage` (S4: Rocky Helmet always does 20 to an attacking Togekiss) | same | passes | passes |
| `carefree_steps_never_flips_for_the_checkups_damage` (S4: Poison always does 10) | same | passes | passes |

Chase Order's two "before" results are from `c350e70`, the engine before its fix. S1's "before" is from `52daee6`, before its hardening. S2 pins today's behaviour, and the laptop's later round will change it knowingly. S4 pins a rule the code already honoured (rules/09: only attacks trigger these Abilities). Gyarados's four Wild Swing tests, which share the discard action, pass before and after.

The fixtures keep kd's value where it is today, 60 and 30, because kd's follow-on changes are the laptop's. Their last line names the change.

## The unit suite

`cargo test --release --features test-utils`, on `c9df626`'s engine (the last commit that touches `engine/`; the later ones touch only `rl/results/`): **2,011 passed, 0 failed, 0 ignored**, in 101 test programs (`suite.log`).
- That is the Chase Order round's 2,006 (at `e52a73b`) plus Sonnet's five tests (S1, S2 and three for S4).
- No existing test's expected value was edited, apart from the two fixtures the coordinator asked to flip. The Chase Order and S2 commits reworked the Meowth test file's helper (a whole attacker board; counts returned); the earlier tests using it are unchanged and pass.

## Instrumentation (part 2) and the smoke check

`instrument_scan.py` patches a copy of `engine/examples/legality_scan.rs` in place, like the Sept 26 switch's script. It adds two per-game counters to the `--games-out` line:
- `coin_defender_attack`: attack moves (an attack, or queued damage from one) while the mover's opponent has one of the five coin-Ability printings in play.
  - It counts a wider set than either gate, so 0 in a game means the repaired code never ran there.
- `coin_queued_attack_damage`: queued `ApplyQueuedAttackDamage` moves aimed at such a Pokémon, the (b) path.

**The smoke check** (`smoke/`, run in scratch copies; no table deck). It was run on `5942d1a`, before the Chase Order fix, and was not rerun for it; Chase Order's evidence is its unit tests.

- **Decks:** two 20-card lists made only for this check.
  - `fire_heatmor.txt`: 2 Heatmor (Tongue Whip snipes the Bench), 2 Slugma, 2 Magcargo, and Blaziken's Trainers.
  - `meowth_carefree.txt`: 2 Meowth (B2 124, Carefree Steps), 2 Bulbasaur, 2 Chatot, and the same Trainers.
  - Bastiodon and Hisuian Goodra are Stage 2 (Bastiodon from a fossil), so bots rarely get them into play. That makes this a check of (b); (a) rests on its unit tests.
- **Play:** kog3 on both sides, 40 games, seeds 20,950,000,000 + i (`--pairs pairs.tsv --seed-base 20950000000 --games 40 --bot kog3`).
- **Three scans:**
  - the engine without the repair (`d21511a`), instrumented;
  - the repaired engine, plain;
  - the repaired engine, instrumented.
- **Results** (`compare.py`, `compare_output.txt`):
  - **The counters change no play:** the repaired engine's plain and instrumented scans give the same moves in 40 of 40 games.
  - **Without the repair:** no snipe was ever queued through the coin-flipping path.
  - **With the repair:** a snipe at Meowth went through it 15 times, in 8 games.
  - **The repair changes 12 of the 40 games.** 8 of them are exactly the 8 where a redirected snipe at Meowth was chosen; every game with one changed.
  - **The other 4 (i = 16, 23, 29, 32) changed without a redirected snipe being chosen.** Sonnet's S3 traced them (below): each is the bot pricing the coin on a choice the repair changed on the board.
  - The `coin_defender_attack` counter is above 0 in all 40 games, because this deck always has a Meowth. So here it can't tell changed games from unchanged ones. It only confirms that it is never 0 where the code could run.
- **S3: the rerun on `e52a73b` and the trace** (`smoke/rerun_e52a73b/`; Sonnet's S3, Sept 30):
  - **The rerun.** Same decks, bots and seeds, on the Chase Order engine `e52a73b` (and `d21511a` without the repair). All three scans give rows identical to the committed ones: 40 of 40 each (`rerun_check.txt`). Chase Order is in neither deck, so nothing moves.
  - **The trace.** `coin_trace.rs` replays i = 16, 23, 29 and 32 tick by tick on both engines, set up exactly as the scan sets up a game; each replay has the scan's move fingerprint. `first_diff.py` (output in `first_diff_output.txt`) finds each game's first difference.
  - **In all 4, the first differing decision is Tongue Whip's target choice.** It comes right after Heatmor attacks. The board is identical and the same number of targets is offered. The difference: on the repaired engine the target at Meowth is offered as `ApplyQueuedAttackDamage` (the coin path), not `ApplyDamage`.
    - Without the repair, the bot sniped Meowth: a sure 30.
    - With it, the bot sniped a Pokémon without the Ability: Chatot (i = 16) or Bulbasaur (23, 29, 32), a sure 30 instead of 30 on a coin.
  - **So each is the bot pricing the coin**, on a choice the repair changed on the board: the mechanic was reached on the board, not only in the bot's lookahead.
  - The first smoke's `coin_queued_attack_damage` counter counts only redirected snipes that were *chosen*, which is why these 4 showed 0. `coin_defender_attack`, which gates the "0 means never ran" check, was above 0 in all of them.
- **The scans' sha256** (scratch builds, for this check only; the rerun's are in `rerun_check.txt`):
  - without the repair, instrumented: `360eb2738dba78641c749ee36b8f1c3a1096f97e57cd270cbc6abae90c4e8b59`;
  - repaired, plain: `770220094e813aaaf76e78fa5ee47bfdfad7126317f4f846d7fc7f4aadcfe6bb`;
  - repaired, instrumented: `5f2f051b7ecc8811efd48f66878df1208dac48419dfd5dd7d9ae74615108e6de`.

## For the laptop

**kd's two one-line follow-ons** (in `engine/src/hooks/core.rs`, `persistent_defender_damage`; not made here, as asked):
1. **(a)** Guarded Grill and Securely Sheltered: take the heads reduction off the damage after the rest of the pipeline, not off `base_damage`.
   - Today the `CoinFlipToReduceIncomingDamage` arm computes `hit(base_damage.saturating_sub(amount))`.
   - It should subtract `amount` from `hit(base_damage)`'s result.
   - Then the last line of `guarded_grill_under_bounded_field_comes_off_after_weakness` becomes `(engine, engine)`.
2. **(b)** Drop the direct-damage exception, `engine_flips_coin`. Then the last line of `a_direct_damage_snipe_on_togekiss_flips_celestial_blessing` becomes `(engine, engine)`.
   - The engine now flips for the `DirectDamage`, `DirectDamageAndSelfCardEffect` and `DirectDamageIfDamaged` groups, which is all that exception covers.
   - kd already flips for every other attack, as the card text says. So after this change kd and the engine will still disagree on the attacks left unchanged: `also_choice_bench_damage`'s own-Bench form, the six sites outside the seven, and Gyarados's Wild Swing. For Chase Order they now agree.

Nothing in `players/` was touched.

**The replay** (RUN5, "Engine repairs: the switch procedure"):
1. Bring the changes of `5942d1a` and `e52a73b` (the six `engine/` files) into the switch's engine and build it.
2. Run the unit suite.
3. Replay the table the procedure names on the engines without and with the repair, and list the changed games. **Expected: 0**, because no list under `decks/` has a coin-Ability Pokémon, and both gates need one in play.
4. Run the instrumented scan (`python3 instrument_scan.py <copy of legality_scan.rs>`; it can go after the Victory Star script, which uses the same anchors). Check two things:
   - both counters are 0 in every table game;
   - the move fingerprints equal the plain scan's.
5. If any game does change, trace it to its first divergence (the template's part 3).

As with the Victory Star repair, identical table games never run the new lines, so they say nothing about them. The evidence that those lines do what Pocket does is the tests and the smoke check.

rules/09's entries are not edited here. They stay open until a switch adopts the repair.

## Design note: why a per-thread value for (a)

The cut has to reach `modify_damage`'s step 4 for exactly one damage calculation.

**The route used.** `AttackOutcome::into_mutation` puts the cut in force around `handle_damage_only`, and `modify_damage` reads it. Since Sonnet's S1 (`c9df626`), each call puts exactly its own cuts in force. An empty call nested inside a non-empty one clears the outer cuts for its length instead of inheriting them. No engine path nests an empty call today, so no game changed; `heads_coin_cuts_are_scoped_to_their_own_call` tests it. The value is set and cleared by one function, `with_heads_coin_cuts`, which restores the previous value even on a panic. It is not game state: nothing about it is saved, cloned or seen by a player.

**The cleaner routes each need a file outside the three:**
- a field on `DamageModifierContext` (also built in `players/`, which is off-limits);
- passing the cut through `handle_damage_only` (`apply_action_helpers.rs`);
- a temporary stored effect on the defender (removing it needs a method in `played_card.rs`).

If Dustin prefers one of those, it is a small change.

## Limits

- **Chase Order copied by another Pokémon** (for example through Mew ex's Genome Hacking). The choice without the discard flips the coin. But the discard branch looks for Chase Order among the Active's own printed attacks, so a copied Chase Order's discard branch keeps the old path.
- **Not changed, though they skip the coin:**
  - left open: `also_choice_bench_damage`'s own-Bench form;
  - for a later round: Ogerpon, Urshifu, Blastoise and Mega Blastoise ex, Mega Kangaskhan ex's second punch, Hoopa's Mischievous Ring, Slowking's Litter and Gyarados's Wild Swing.
  - See "Not changed" above for Dustin's answers.
- **Side effects of the redirected damage.** Damage redirected to `ApplyQueuedAttackDamage` also:
  - carries the attack's name and text into `modify_damage` (`ApplyDamage` carries none);
  - runs the defender's other attack coins for its target: Guts, point denial and Perish Body.
  - The coin-Ability Pokémon have none of those Abilities, so the other coins matter only through Pull In and Pound's wider gate.
- **Pull In and Pound's gate is wider than the target.** If a coin-Ability Pokémon is on the Bench but another Pokémon is switched in, that damage still takes the attack's path.
- **The knock-out checks' limits are unchanged.** The Guts, point-denial and Perish Body checks, which now include the cut, still forecast on the board before the attack, as before.

## Files

- `HELPERS.md`, `helpers_census.py`, `census_output.txt`, `probe_coin_helpers.rs`, `probe_output.txt`: Part 1.
- `instrument_scan.py`: the watch-only counters.
- `suite.log`: the full unit suite at `c9df626`.
- `smoke/`: the smoke check.
  - `fire_heatmor.txt`, `meowth_carefree.txt`, `pairs.tsv`: its decks and pairing.
  - `games_legacy_instr.jsonl`, `games_fixed_plain.jsonl`, `games_fixed_instr.jsonl`: its games.
  - `compare.py`, `compare_output.txt`: the comparison.
  - `rerun_e52a73b/`: S3's rerun and trace.
    - `rerun_check.txt`: the rerun against the committed games, and the sha256s.
    - `coin_trace.rs`: the trace program.
    - `trace_legacy_d21511a.jsonl.gz`, `trace_fixed_e52a73b.jsonl.gz`: the two engines' tick-by-tick traces of the 4 games.
    - `first_diff.py`, `first_diff_output.txt`: the first differences.
