Decision this informs: none yet. This is a drafted engine repair for a later engine switch (the Fable coordinator via Dustin, Oct 1). It stacks on Sonnet's R (1abdbe8, `origin/sonnet/rules-fixes`) on its own branch, `claude/coin-prevention-round2`, and is not merged or pinned. No table game, carrier game or identity replay was played. **No independent audit of the patch has been done yet.**

Seeds: no table deal. The smoke check used 20,980,000,000 + pairing × 10,000 + i, on scratch decks only (Claude Code's diagnostic block, outside START_HERE's ranges). The unit tests' seeds are their own, as in the first round.

# Coin-flip prevention, the later round

## In plain words

- **What Pocket does** (rules/02, step 4; rules/09, "Open engine bugs"). Four Abilities read "If any damage is done to this Pokémon by attacks, flip a coin": Carefree Steps (Meowth B2 124, B2 204), Celestial Blessing (Togekiss A4 080), Guarded Grill (Bastiodon A2 114) and Securely Sheltered (Hisuian Goodra B3b 050). They apply to any damage from an attack, including damage the attacker aims after the attack is chosen.
- **The first round** (`../coin_prevention_repair_2026-09-30/`) made the coin flip for the queued damage of seven helpers and Chase Order. It recorded seven more sites "for a later round". Each still queued its damage as a plain `ApplyDamage`, which never flips the coin.
- **Now six of them flip it** (gated, through the first round's path):
  - Gyarados's Wild Swing (A4 045, A4 215), with and without the discard;
  - Wellspring Mask Ogerpon's Wellspring Dance (B2 048), on its heads;
  - Rapid Strike Urshifu's Tornado Shot (B3 051);
  - Blastoise's Double Splash (B1a 019) and Mega Blastoise ex's Triple Bombardment (B1a 020, 078, 084);
  - Hoopa's Mischievous Ring (B4 077);
  - Slowking's Litter (A4a 018).
- **The seventh, Mega Kangaskhan ex's second punch, waits on a question** (asked in CLOUD_STATUS.md, Oct 1). Its fix needs a fifth engine file, `engine/src/state/mod.rs`, so that the opponent still chooses a new Active before the second punch lands. The tests and the fix are ready; see "Mega Kangaskhan ex" below.
- **Unchanged, as Dustin ruled:** `also_choice_bench_damage` in its own-Bench form. The new gate also leaves alone any choice that hits the attacker's own Bench. No card today has an own-Bench form of the six sites.
- **Off the gate nothing changes.** A queued choice takes the new path only when one of its targets has one of the four Abilities. Every other choice is the same `ApplyDamage` as before.
- **Which games could change: none between two lists under `decks/`.** No list under `decks/` holds one of the four Abilities. One list holds a repaired attacker: the panel ladder's l-sharpedo, with 2 Gyarados A4 045 (Wild Swing). Its play changes only in a game against one of those Abilities.
- **Watch for the rules switch's step 8b.** PLAN.md's early-warning row "l-sharpedo v `meowth_carefree`" is "the Wild Swing control". If the switch takes this round, Wild Swing into that Meowth flips the coin, so the row is no longer a control for Wild Swing.

## Reach per card (`reach.py`, `reach_output.txt`)

Every printing whose attack text maps to the site's mechanic, and the lists under `decks/` (64 files) that hold it. `decks/` is the same on R and on main (d010d2d).

| site | printings | lists under `decks/` |
|---|---|---|
| Wild Swing | Gyarados A4 045, A4 215 | **A4 045: `decks/screen/panel_ladder_2026-09-26/l-sharpedo.txt` (2 copies)**; A4 215: none |
| Wellspring Dance | Wellspring Mask Ogerpon B2 048 | none |
| Tornado Shot | Rapid Strike Urshifu B3 051 | none |
| Double Splash | Blastoise B1a 019 | none |
| Triple Bombardment | Mega Blastoise ex B1a 020, B1a 078, B1a 084 | none |
| second punch (waiting) | Mega Kangaskhan ex B2 127, B2 189, B2 202, B4 231 | none |
| Mischievous Ring | Hoopa B4 077 | none |
| Litter | Slowking A4a 018 | none |
| **the defenders** | Bastiodon A2 114, Togekiss A4 080, Meowth B2 124 and B2 204, Hisuian Goodra B3b 050 | none |

- **The carrier lists** (`rl/results/engine_switch_rules_2026-10/carriers/`, not under `decks/`) hold the defenders, not these attackers: Meowth B2 124 (Garchomp Meowth; Togekiss Meowth), Togekiss A4 080, Hisuian Goodra B3b 050, and Meowth B2 204 (the fallback `coinflip_deck.txt`).
  - So a carrier game reaches this round only against an opponent holding one of these attackers. Of the panel and ladder lists, that is l-sharpedo alone.

## Commits (branch `claude/coin-prevention-round2`, from 1abdbe8)

1. The log line, in CLOUD_STATUS.md on `claude/pensive-ptolemy-spwc0b` (b9d08fc), before the job. The question about a fifth file: 621bde5.
2. `99f5bc4`: the failing tests, in their own commit (`tests_before_fix.log`: 7 failing, the six sites and the gate; 16 passing).
3. `e0ecf19`: the gated fix, in the first round's files `apply_attack_action.rs` and `apply_action.rs` (`tests_after_fix.log`: 23 of 23).
4. `0e9464a`: the counters (`instrument_scan.py`) and their check on constructed boards.
5. Then this README, `suite.log`, `reach.py` and the smoke check.

The engine diff from R is three files: `engine/src/actions/apply_attack_action.rs`, `engine/src/actions/apply_action.rs` and `engine/tests/pokemon/meowth_carefree_steps_test.rs`. `attack_outcome.rs` and `hooks/core.rs` needed no change. Nothing in `players/` or `Cargo.lock` changed.

## The gates (read them in the code; line numbers at `e0ecf19`, `engine/src/actions/apply_attack_action.rs` unless named)

- **The constructor.** `queued_attack_damage_choice` (281) now hands its one target to `queued_attack_damage_targets_choice` (294). That function also takes one choice that hits several of the opponent's Pokémon: the Active's hit and a Benched hit queued together.
  - With a coin target, it builds the attack's own `ApplyQueuedAttackDamage`, with the first round's debug line.
  - Without one, it builds the same `ApplyDamage` as before.
- **The gate.** `coin_gated_choice` (334) takes a choice built as `ApplyDamage` from the attacker's Active. It sends the choice through the constructor only when every target is the opponent's and one of them has a coin Ability (`any_coin_target`, 320, which reads `coin_damage_prevention`, 264). Anything else comes back exactly as it was. That includes a choice that also hits the attacker's own Bench.
- **The sites:**
  - Wellspring Dance: `coin_flip_also_choice_bench_damage` (5808; the gate at 5825). Its tails branch deals the Active's damage directly, which already flipped.
  - Tornado Shot: `self_discard_energy_and_choice_bench_damage` (3945; 3960).
  - Double Splash and Triple Bombardment: `conditional_bench_damage_attack` (6131; 6207). The finished choices are gated, so the own-Bench form (no card) passes through.
  - Mischievous Ring: `shuffle_opponent_tools_into_deck_before_damage` (8511; 8532). It now takes the attack, and the gate reads the board after the Tools are shuffled away.
  - Wild Swing: `discard_then_damage_choice` (359) now finds the attacker's printed attack that offered the discard, Chase Order or Wild Swing (`printed_attack`, 398), instead of Chase Order only. It is called from `apply_action.rs`'s `apply_discard_own_benched_then_damage` (1306).
  - Litter: `apply_action.rs`'s `forecast_discard_own_cards_for_attack_damage` queues its damage through `discard_tools_then_damage_choice` (`apply_action.rs` 1731; 372 here). It finds Litter among the attacker's printed attacks the same way.
  - Both of the last two build their plain `ApplyDamage` in `chosen_damage_choice` (378) and gate it with `coin_gated_choice` (391).
- **Logging.** Every gated choice writes the first round's line, "Queued attack damage at a coin-flip damage Ability: ... to slot ..., through the attack's modifiers". For a choice with two targets it reads "to slot 0 and 2".

## Tests (`engine/tests/pokemon/meowth_carefree_steps_test.rs`)

| test | before the fix (R) | after |
|---|---|---|
| `carefree_steps_flips_for_wild_swing` (was S2's `wild_swing_into_carefree_steps_pins_todays_behaviour_no_coin`, flipped as its comment asked: with and without the discard) | fails: 0 prevented, 60 hit | passes |
| `carefree_steps_flips_for_wellspring_dance_on_its_heads` (Meowth on the Bench, then in the Active Spot; only the seeds whose attack coin was heads count) | fails: 0 prevented, 39 hit | passes |
| `carefree_steps_flips_for_tornado_shot` (Bench, then Active) | fails: 0 of 60 | passes |
| `carefree_steps_flips_for_double_splash_and_triple_bombardment` (both cards, Bench then Active) | fails: 0 of 60 | passes |
| `carefree_steps_flips_for_mischievous_ring` (a Benched Bulbasaur's Giant Cape is shuffled away first) | fails: 0 of 60 | passes |
| `carefree_steps_flips_for_litter` (2 Tools in hand, 100 queued) | fails: 0 of 60 | passes |
| `only_a_choice_that_hits_a_coin_ability_pokemon_takes_the_coin_path_in_the_later_round` (the gate: Tornado Shot at a Benched Bulbasaur stays `ApplyDamage`, at a Benched Meowth it doesn't; with Meowth Active, both choices take the coin path) | fails: both `ApplyDamage` | passes |
| `the_later_rounds_sites_into_pokemon_without_a_coin_ability_are_unchanged` (the control: all seven sites, Mega Kangaskhan ex included, into Mega Latios ex, 20 seeds each; every queued damage choice stays `ApplyDamage`) | passes | passes |

- A test passes when Meowth took none of the damage in more than 10 of 60 seeds and some damage in more than 10. For Wellspring Dance the bar is 5 of the heads seeds.
- The helper `carefree_steps_counts` now runs through `carefree_steps_seed`, which also reports whether a queued choice at Meowth was offered, and can put Tools in the hand. The first round's tests use it unchanged and pass.

## The unit suite (`suite.log`)

`cargo test --release --features test-utils`, at `e0ecf19`'s engine (the last commit that touches `engine/`): **2,025 passed, 0 failed, 0 ignored.**
- That is R's 2,018 (Sonnet's suite at R, in `../engine_switch_rules_2026-10/EQUIVALENCE_sonnet.md` on b3e6eae) plus the 7 tests added here. The Wild Swing pin was flipped, not added.
- No existing test's expected value was edited, apart from the S2 pin, which asked for it.

## The counters (`instrument_scan.py`, `counter_probe_round2.rs`)

- **`../coin_prevention_repair_2026-09-30/instrument_scan.py`** (the coin repair's watch-only counters) gets this round's five helper mechanics in `HELPERS`. So `offgate_helper_choice` sees their off-gate choices, the proof that a table runs the rewritten lines.
  - The mechanics: `CoinFlipAlsoChoiceBenchDamage`, `SelfDiscardEnergyAndChoiceBenchDamage`, `ConditionalBenchDamage`, `ShuffleOpponentToolsIntoDeckBeforeDamage` and `DiscardToolsFromHandForDamage`.
  - Wild Swing's off-gate damage was already `offgate_discard_then_damage`'s.
  - The queued coin-path choices of all six are `coin_queued_offered`'s with no change.
  - The script still applies alone and with the Victory Star script in either order (the same sorted lines), and the instrumented scan compiles on this engine.
- **`counter_probe_round2.rs`** (output in `counter_probe_round2_output.txt`) uses F5's detection functions, copied, on boards built with `test_support`. For each site it checks:
  - the mechanic's name keys the right off-gate counter;
  - with Meowth there, the queued choice is offered, and choosing it runs Meowth's coin split;
  - with Bulbasaur instead, only plain choices are offered.
  - Result: **28 checks, 0 failures.**
  - Run it as an example in the engine, as F5's was: `cargo run --release --features test-utils --example counter_probe_round2`.

## The smoke check (`smoke/`)

- **Decks** (scratch only, no table deck):
  - `water_round2.txt`, made for this check: the repaired attackers that bots can get into play. That is 2 Magikarp and 2 Gyarados A4 045, 2 Kubfu and 2 Rapid Strike Urshifu, 2 Wellspring Mask Ogerpon, 2 Hoopa, Slowpoke and Slowking, plus Professor's Research, Poké Ball and 2 Giant Cape for Litter.
  - Blastoise and Mega Blastoise ex (Stage 2) and Mega Kangaskhan ex (waiting) are left to their tests.
  - Its opponents are the first round's `meowth_carefree.txt` (2 Meowth B2 124) and `fire_heatmor.txt` (no coin Ability).
- **Play:** km3 on both sides, 40 games a pairing, seeds 20,980,000,000 + pairing × 10,000 + i.
- **Three scans** (`run_smoke.sh`, each built in a scratch copy; sha256s in `run_output.txt`):
  - R (1abdbe8), plain;
  - this branch, plain;
  - this branch, with the counters.
- **Results** (`compare.py`, `compare_output.txt`):
  - **The counters change no play:** this branch's plain and watch scans give the same moves in 80 of 80 games.
  - **Without a coin Ability in play (v `fire_heatmor`): 0 of 40 games change.** The rewritten lines still ran there, off the gate: `offgate_helper_choice` fires in 38 games (172 ticks), `offgate_discard_then_damage` in 8 (9 ticks).
  - **Against Meowth (v `meowth_carefree`): 23 of 40 games change.**
    - In every one, the queued coin-path choice was offered on the board (`coin_queued_offered`, in 33 games, 71 ticks). No game changed in lookahead alone.
    - The other 10 games with a choice offered didn't change: the coin went the old way, or the bot chose another target.
    - I did not trace first differences tick by tick; that is the switch's step 8c work.
  - The legality checks found nothing in the 240 games.
- The scans' sha256: R plain `aca7d9a0…6e9`, this branch plain `b7c1c6f4…dc9`, watch `0467c6aa…b2d` (built from `0e9464a`, whose `engine/` equals `e0ecf19`'s).

## Mega Kangaskhan ex (waiting on the fifth-file question)

- **The site.** `mega_kangaskhan_ex_double_punching_family` (2197) queues the second punch, "The second attack does 40 damage", as a plain `ApplyDamage` at the opponent's Active. It inserts it at the bottom of the stack, so that a promotion after the first punch's knockout comes first.
- **Why a fifth file.** `trigger_promotion_or_declare_winner` (`engine/src/state/mod.rs:1417-1426`) puts the promotion above the waiting punch only if it sees an `ApplyDamage` aimed at the empty Active. Queued as the attack's own `ApplyQueuedAttackDamage`, the punch isn't seen. The promotion would go under it, and the punch would land on an empty Active Spot.
- **Ready, not committed:**
  - two failing tests: Celestial Blessing flips for the second punch, and Meowth promoted after a knockout flips for it;
  - the fix: the punch goes through `queued_attack_damage_choice`, gated on any of the opponent's Pokémon having a coin Ability, since the target is whichever Pokémon is Active when it lands. `state/mod.rs`'s check also recognises an `ApplyQueuedAttackDamage` at the empty Active.
  - **Checked in a scratch copy** (nothing committed; this branch's `engine/` plus the two tests):
    - before the fix, both tests fail: 0 prevented of 60;
    - with `apply_attack_action.rs` changed alone, Celestial Blessing's test passes, but the knockout case fails ("the second punch waits for the new Active": the punch lands first);
    - with the `state/mod.rs` check too, both pass, 25 of 25 in the file.
  - On a yes they go in as two more commits, followed by the suite and this README. On a no, the site stays as it is and is recorded here as still open.

## For the laptop

- **kd needs no follow-on.** Since F1 (R), kd prices the coin for every hit an attack does (`hooks/core.rs`, `persistent_defender_damage`). This round brings the engine to kd for these six sites.
- **The replay**, at the switch that takes this round (RUN5, "Engine repairs: the switch procedure"):
  - The expected number of changed table games is **0**, as for the first round: no list under `decks/` holds a coin Ability.
  - `instrument_scan.py`'s counters, as this branch has them, must read 0 for the changed-mechanic counters in every table game, and the watch scan's moves must equal the plain scan's.
  - Step 8b's l-sharpedo v `meowth_carefree` row changes meaning (see "In plain words").
- rules/09 and PLAN.md are not edited here.

## Limits

- **A copied attack.** Wild Swing's and Litter's queued damage looks for the attack among the attacker's own printed attacks, as Chase Order's discard branch already did. A copied Wild Swing or Litter (for example through Mew ex's Genome Hacking) keeps the old path.
- **The other targets of a gated choice.** When a choice that hits two Pokémon takes the coin path because one of them has a coin Ability, the other target's damage also runs the attack's modifiers. That is the attack's name and text in `modify_damage`, and the defender's Guts, point-denial and Perish Body coins.
  - That is right by the rules, since it is the attack's damage. But it differs from the plain `ApplyDamage` it replaces, which carried none of them.
  - The same side effect the first round recorded for its helpers.
- **The own-Bench forms** of `coin_flip_also_choice_bench_damage` and `conditional_bench_damage_attack` (no card today) pass through unchanged, like `also_choice_bench_damage`'s.

## Files

- `README.md`: this note.
- `tests_before_fix.log`, `tests_after_fix.log`: `meowth_carefree_steps_test` before and after the fix.
- `suite.log`: the full unit suite at `e0ecf19`.
- `reach.py`, `reach_output.txt`: reach per card.
- `counter_probe_round2.rs`, `counter_probe_round2_output.txt`: the counters on constructed boards.
- `smoke/`: the smoke check.
  - `water_round2.txt`: the scratch deck of repaired attackers. `meowth_carefree.txt` and `fire_heatmor.txt` are the first round's scratch decks, copied.
  - `pairs.tsv`, `run_smoke.sh`, `run_output.txt`: the pairings, the run, and its output (the builds' sha256s and the three scan pages).
  - `games_r_plain.jsonl`, `games_round2_plain.jsonl`, `games_round2_watch.jsonl`: the games.
  - `compare.py`, `compare_output.txt`: the comparison.
- Changed outside this folder: `../coin_prevention_repair_2026-09-30/instrument_scan.py` (the counters).
