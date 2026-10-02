Decision this informs: none yet. This is a drafted engine repair for a later engine switch (the Fable coordinator via Dustin, Oct 1). It stacks on Sonnet's R (1abdbe8, `origin/sonnet/rules-fixes`) on its own branch, `claude/coin-prevention-round2`, and is not merged or pinned. **It stays out of the current rules switch, whose scope is fixed, and goes in the next one** (the coordinator, Oct 1). No table game, carrier game or identity replay was played. **No independent audit of the patch has been done yet.** **Since Oct 2 it also carries the card-text job** (the coordinator via Dustin, Oct 1 evening): see "The card-text job" below and `TEXT_AUDIT.md`.

Seeds: no table deal. The smoke check used 20,980,000,000 + pairing × 10,000 + i, on scratch decks only (Claude Code's diagnostic block, outside START_HERE's ranges). The unit tests' seeds are their own, as in the first round.

# Coin-flip prevention, the later round

## In plain words

- **What Pocket does** (rules/02, step 4; rules/09, "Open engine bugs"). Four Abilities read "If any damage is done to this Pokémon by attacks, flip a coin": Carefree Steps (Meowth B2 124, B2 204), Celestial Blessing (Togekiss A4 080), Guarded Grill (Bastiodon A2 114) and Securely Sheltered (Hisuian Goodra B3b 050). They apply to any damage from an attack, including damage the attacker aims after the attack is chosen.
- **The first round** (`../coin_prevention_repair_2026-09-30/`) made the coin flip for the queued damage of seven helpers and Chase Order. It recorded seven more sites "for a later round". Each still queued its damage as a plain `ApplyDamage`, which never flips the coin.
- **Now all seven flip it** (gated, through the first round's path):
  - Gyarados's Wild Swing (A4 045, A4 215), with and without the discard;
  - Wellspring Mask Ogerpon's Wellspring Dance (B2 048), on its heads;
  - Rapid Strike Urshifu's Tornado Shot (B3 051);
  - Blastoise's Double Splash (B1a 019) and Mega Blastoise ex's Triple Bombardment (B1a 020, 078, 084);
  - Hoopa's Mischievous Ring (B4 077);
  - Slowking's Litter (A4a 018);
  - Mega Kangaskhan ex's second punch (B2 127, 189, 202; B4 231), with or without a knockout first.
- **The second punch needed a fifth engine file, `engine/src/state/mod.rs`** (asked in CLOUD_STATUS.md, approved by the coordinator via Dustin, Oct 1: its pending-hit check only). The check now also sees the punch in its coin-flipping form, so the opponent still chooses a new Active before it lands. See "Mega Kangaskhan ex" below.
- **Unchanged, as Dustin ruled (superseded Oct 2 by his card-text rule; it now flips, see "The card-text job"):** `also_choice_bench_damage` in its own-Bench form. The new gate also leaves alone any choice that hits the attacker's own Bench. No card today has an own-Bench form of these sites.
- **Off the gate nothing changes.** A queued choice takes the new path only when one of its targets has one of the four Abilities. Every other choice is the same `ApplyDamage` as before.
- **Which games could change: none between two lists under `decks/`.** No list under `decks/` holds one of the four Abilities. One list holds a repaired attacker: the panel ladder's l-sharpedo, with 2 Gyarados A4 045 (Wild Swing). Its play changes only in a game against one of those Abilities.
- **For the next switch's early-warning rows.** The current switch's step 8b has a row "l-sharpedo v `meowth_carefree`" as "the Wild Swing control". On an engine with this round, Wild Swing into that Meowth flips the coin, so a row like it is no longer a control for Wild Swing.

## The card-text job (Oct 2)

Set by the Fable coordinator via Dustin, Oct 1 evening, on this branch, with Dustin's rule: plain card text is the rule, and a simulator path that contradicts it is a bug. Tests first for every fix; no table game; nothing in `players/`.

### In plain words

1. **Will with a Confused attacker** (item 1). Will names coins flipped "for the effect of an attack, Ability, or Trainer card"; the Confusion coin is none of those. So after a Confusion heads, Will now makes the attack's first coin heads, and Victory Star is still offered. Before: Will lapsed unused, and Victini offered nothing. The game does this (Recording_QA 210403, T14).
2. **The audit** (item 2, `TEXT_AUDIT.md`): every gated or "not seen" case in rules/09, rules/04 and `card_validation.rs`'s caveats, with the card texts. 9 are decided by the text and contradicted by the engine, 7 are decided and already followed, 17 are not decided by any text (each a shot-list row, with what to record), and 4 are not rules questions.
3. **The four text-decided fixes that fit the five files** (item 3):
   - **Victory Star with a block coin** (Smokescreen and the like): the block coin comes first and is never offered; on its heads the attack's own coins are offered. Before: no offer at all.
   - **Will with a block coin:** Will makes the block coin heads (it is flipped "for the effect of an attack", the opponent's), and the attack's own coins stay fair. Before: Will lapsed unused.
   - **The coin Abilities on the attacker's own Pokémon:** Carefree Steps, Celestial Blessing, Guarded Grill and Securely Sheltered now flip for your own attack's damage to your own Pokémon (Zapdos's and Emolga's Raging Thunder, Luxray's Flash Impact, Mimikyu's Shadow Hit, the Earthquake family, Shaking Stomp, Hailstorm, Enormous Explosion), and for the opponent's Active hit in an own-Bench choice. Before: never. This supersedes Dustin's earlier "unchanged" for the own-Bench form.
   - **A copied discard attack** (Chase Order through Ditto's Copy Anything, Wild Swing through either Ditto) now flips the coin. Before: never.
4. **Trap Territory** (item 4): two Ariados add 2 to the opponent's Active's Retreat Cost, not 1 (213034: Grass Knot did 160). That changes retreat, Grass Knot and the other per-Retreat-Cost attacks, and Heavy Helmet.
- **Asked in CLOUD_STATUS.md, not done** (de0d53c): Victini's caveat text in `card_validation.rs`; Luxury Coin on the opponent's Stadium (`trainer_coin_plan.rs`); a Fossil under an Item lock (`move_generation_trainer.rs`); Guts on your own Pokémon and Perish Body on a plain queued hit (in the five files, but outside the three sources).
- **Which games could change** (the 79 lists under `decks/` on this branch):
  - Trap Territory: Dustin's deck 12 (`decks/dustin/12-ariados-whimsicott-ogerpon.txt`, 2 Ariados B1a 006). Its own Grass Knot (Whimsicott ex) and its opponent's retreats change whenever both Ariados are in play.
  - Will: `decks/brews/brew-01-arceus-crobat-xatu.txt`, `decks/brews/brew-04-xatu-slowking.txt` and `decks/dustin/10-xatu-oricorio-tr-weezing.txt` hold Will. Their games change only when Will is played and the attacker is then Confused and attacks with coins.
  - Nothing else: no list holds Victini, a block-coin attacker, a coin Ability, an own-side damage attacker or Ditto.
- **The suite** (`suite_card_text.log`), at `5155ff7`, the last engine commit: **2,035 passed, 0 failed, 0 ignored**: the 2,027 above plus the 11 tests added here, less the 3 old pins they replace.

### Commits

- The log line on the coordination branch (d13b9d2); the sixth-file question (de0d53c).
- `59c7c2a`: item 1's tests (`tests_before_fix_will.log`: the 2 new tests fail, 14 pass). `27a0c37`: its fix (`tests_after_fix_will.log`).
- `539594a`: `TEXT_AUDIT.md`, before any further code.
- `7e13132`: item 3's tests (`tests_before_fix_text.log`: 7 fail; 0 prevented of 60 for every own-side and copied case). `46953bf`: the fixes (`tests_after_fix_text.log`).
- `05eb849`: item 4's tests (`tests_before_fix_trap_territory.log`: both fail at two Ariados only). `5155ff7`: the fix (`tests_after_fix_trap_territory.log`).
- Then the suite and this README.

The engine diff from R is now nine files: the five (`apply_attack_action.rs`, `apply_action.rs`, `attack_outcome.rs`, `hooks/core.rs`, `state/mod.rs`), `hooks/retreat.rs` (allowed for Trap Territory only), and the test files `tests/pokemon/meowth_carefree_steps_test.rs`, `tests/b4a_attack_batch2_test.rs` and `tests/pokemon/legacy_ability_logic_test.rs`. Nothing in `players/` or `Cargo.lock` changed.

### Tests

| test | file | before | after |
|---|---|---|---|
| `confusion_with_will_pending_forces_the_attacks_first_coin_and_still_offers_victory_star` (replaces F4's `confusion_with_will_pending_keeps_the_legacy_resolution_without_a_victory_star_offer`) | `b4a_attack_batch2_test.rs` | fails: no pause | passes |
| `confusion_with_will_pending_forces_the_attacks_first_coin_without_victory_star` (the exact forecast) | same | fails: nothing attached 0.5625, Will unused | passes |
| `a_block_coin_comes_first_then_victory_star_is_offered_on_the_attacks_own_coins` (replaces `coin_flip_to_block_attack_keeps_its_resolution_without_a_victory_star_offer` and `coin_flip_to_block_attack_result_is_the_old_paths`) | same | fails: no pause | passes |
| `will_makes_the_block_coin_heads_and_leaves_the_attacks_own_coins_fair` (the exact forecast, Confused or not) | same | fails: Will unused | passes |
| `will_on_the_block_coin_then_victory_star_on_the_attacks_fair_coins` | same | fails: no pause | passes |
| `carefree_steps_flips_for_your_own_attacks_damage_to_your_own_meowth` (Raging Thunder, Shadow Hit, Earthquake) | `meowth_carefree_steps_test.rs` | fails: 0 prevented of 60 | passes |
| `securely_sheltered_cuts_your_own_shaking_stomp_on_your_benched_goodra` | same | fails: 0 of 60 | passes |
| `carefree_steps_flips_for_the_active_hit_of_an_own_bench_choice` | same | fails: 0 of 60 | passes |
| `carefree_steps_flips_for_a_copied_discard_attack` (Copy Anything + Chase Order, Copy a Friend + Wild Swing; the discard offered on all 60 seeds) | same | fails: 0 of 60 | passes |
| `trap_territory_adds_one_to_the_retreat_cost_for_each_ariados` (retreat legality with 0, 1, 2 Ariados) | `legacy_ability_logic_test.rs` | fails at 2 Ariados | passes |
| `grass_knot_reads_one_more_retreat_cost_for_each_ariados` (100, 130, 160 into Charizard ex) | same | fails: 130, not 160 | passes |

The three replaced tests pinned the old resolution, as their comments said. Two in-crate tests in `attack_outcome.rs` were updated to the prevention split's new (side, index, cut) form, with the same values. No other test changed.

### How (line numbers at `5155ff7`)

- **Will on a Confused attacker:** `AttackOutcomes::force_first_heads_using_will` (`attack_outcome.rs`) conditions the attack's own coins on a first heads, as `Outcomes::force_first_heads` does, and uses Will in each branch before its damage. `apply_attack_common_modifiers` (`apply_attack_action.rs`) applies it before the Confusion gate. With Victini, the Confusion-first staging takes the case (the Will carve-out is gone).
- **The block coin:** `victory_star_waits_for_gate_heads` (formerly `..._confusion_heads`) covers both gate coins, with `gate_heads_probability`, `gate_tails_outcomes` and `finish_attack_after_gate_heads`; `has_unverified_attacker_coin_gate` and its early return in `try_forecast_victory_star_attack` are gone. Will: `will_goes_to_the_block_coin`, and `AttackOutcomes::block_coin_heads_by_will`, which keeps every branch, uses Will, and drops the coin record so `finish_forecast` doesn't apply Will again.
- **The attacker's own Pokémon:** `split_with_damage_prevention` takes (side, index, cut) and `heads_coin_cuts` carry the side; `apply_defender_damage_prevention_if_needed` collects both sides; `modify_damage`'s heads cut applies to either side (`hooks/core.rs`). `forecast_apply_damage` (`apply_action.rs`) flips the coin for any target of an attack's queued `ApplyDamage`, with the heads cut in force and the Guts check after it; that covers the own-Bench and own-Pokémon choices and a copied discard attack.
- **Trap Territory:** `get_retreat_cost_for_player_internal` (`hooks/retreat.rs`) adds each Ariados's amount; the loop no longer stops at the first.

### For the laptop

- The replay at the next switch: Trap Territory moves deck 12's games, and Will moves the three Will lists' games only in the Confused case (above).
- `instrument_scan.py`'s counters don't see the new paths (Victory Star after a block coin, Will on a gate, the own-side coin, the queued `ApplyDamage` coin). They would need new counters if the replay wants a proof that a table ran them.
- `players/value_functions.rs` prices the block coin at 50/50 (its comment at 1976). With Will pending the engine now makes it heads, so the bots' clock is off in that rare case. `players/` is not changed here.

### The follow-up (Oct 2): the answer to the sixth-file question, all yes

The coordinator via Dustin, Oct 2: the card-text job accepted, and the question answered "all yes, tests first, same branch, same limits". Before it, origin/main (the pinned rules engine, `rl/engine-2026-10-02`, main-8626a35, pin 24374a0) was merged into this branch (`d1b986c`). Main's engine tree equals R's (38af8b0), so the merge changed no engine line here: this branch now stacks on the official engine.

**In plain words:**
1. **Victini's caveat** (`card_validation.rs`) now says what is implemented: the gate coins, Confusion and a block coin, come first and are never offered; after their heads the attack's own coins are offered; Will goes to a block coin, else to the attack's first coin; a reroll is a fresh batch. It also says what stays open: the order of the two gate coins when both apply (nothing visible depends on it), and the block coin's reading, which shot row `victory-star-block-coin` would confirm. Victini stays "rules unverified" for that.
2. **Luxury Coin isn't offered on the opponent's Mesagoza or Arcade** (`trainer_coin_plan.rs`). Its text covers "coins for an effect of your Trainer cards", and a Stadium is the Trainer card of the player who played it. A Stadium with no recorded player (a board set up without playing it) keeps the offer.
3. **A Fossil can't be played under an Item lock** (`move_generation_trainer.rs`): its printed type is Item. A Pocket Shot List row, `fossil-item-lock`, asks for a recording as supporting proof, not as a gate.
4. **Guts on your own Pokémon** (E1): Guts now flips when your own attack would Knock Out your own Guts Pokémon in the attack's outcome (Earthquake on your Benched Ursaluna, for example). Before, only the opponent's flipped.
5. **Perish Body on a plain queued hit** (E2): an attack's queued `ApplyDamage` that would Knock Out the opponent's Active Galarian Cursola now flips its coin (Chase Order or Wild Swing into Cursola, for example); on heads the attacker is Knocked Out after the retaliation, as in the attack's own outcome. Before, never.

**Which games could change** (the 83 lists now under `decks/`, 15 of them Dustin's):
- **No list holds a Fossil, and none holds Gholdengo (Luxury Coin).** So none of Dustin's decks has either. Mesagoza is in Dustin's 01 and 08 and Arcade in brew-04, but with no Gholdengo anywhere the Luxury Coin change reaches no game.
- No list holds an Item-lock attacker, a Guts Pokémon (Conkeldurr, Ursaluna) or Galarian Cursola.
- So this follow-up changes no game between lists under `decks/`.
- Rechecked on the 83 lists, the card-text job's reach is unchanged (Trap Territory: Dustin's 12; Will: brew-01, brew-04, Dustin's 10). One new list holds Victini: `decks/brews/drafts_2026-10-01/draft-D-entei-grimhound.txt` (2 Victini, 2 Mega Houndoom ex). The block-coin change reaches it only against a block-coin attacker, and no list holds one; it holds no Will.

**Commits:** the log line and the STOP's one line on the coordination branch (20540c0); `53a3cca`, the five tests, all failing first (`tests_before_fix_followup.log`); `3090abb`, the five changes (`tests_after_fix_followup.log`); then the suite and this README.

**Tests:**

| test | file | before | after |
|---|---|---|---|
| `victini_caveat_names_the_gate_coins_and_what_stays_open` | `victini_victory_star_test.rs` | fails: the text still said "legacy resolution" | passes |
| `luxury_coin_is_offered_only_on_the_players_own_stadium` (replaces `activated_stadium_records_placer_but_eligibility_belongs_to_actor`, which pinned the offer whoever had played the Stadium) | `gholdengo_luxury_coin_test.rs` | fails: the opponent's Arcade paused for Luxury Coin | passes |
| `an_item_lock_stops_a_fossil` (Chingling's Jingly Noise; Poké Ball is the control that the lock is in force) | `rules_repair_trainers.rs` | fails: the Fossil was offered under the lock | passes |
| `guts_flips_for_your_own_attacks_damage_to_your_own_ursaluna` (Whiscash's Earthquake, Ursaluna at 10 HP) | `pokemon/ursaluna_guts_test.rs` | fails: 0 survived of 60 | passes |
| `perish_body_flips_for_a_plain_queued_hit_at_the_active` (Chase Order with the discard into Galarian Cursola) | `pokemon/galarian_cursola_perish_body_test.rs` | fails: 0 attackers Knocked Out of 60 | passes |

One in-crate test in `attack_outcome.rs` was updated to the Guts split's new (side, index) form, with the same values.

**How (line numbers at `3090abb`):**
- Luxury Coin: `luxury_coin_covers` (`trainer_coin_plan.rs`), checked right after the Luxury Coin source in both entry points (`try_sample_entry_actual`, `try_forecast_entry`). The Stadium's own coins then take the ordinary path.
- Fossil: the Item-lock check in `generate_possible_trainer_actions` covers the Fossil type too.
- E1: `split_with_guts_survival` takes (side, index); `apply_defender_guts_if_needed` collects both sides.
- E2: `forecast_apply_damage_after_coins` (`apply_action.rs`) adds Perish Body's coin when the hit would Knock Out the opponent's Active Perish Body Pokémon (`would_knock_out`, now shared), and applies `apply_perish_body_retaliation` on heads between the retaliation and the knockouts.

**The suite** (`suite_followup.log`), at `3090abb`, the last engine commit: **2,039 passed, 0 failed, 0 ignored**: the 2,035 above plus the 5 tests added here, less the one pin replaced.

**The engine diff from the official engine** (main-8626a35) is now 17 files: `apply_action.rs`, `apply_attack_action.rs`, `attack_outcome.rs`, `hooks/core.rs`, `state/mod.rs` (the five); `hooks/retreat.rs` (Trap Territory); `trainer_coin_plan.rs`, `move_generation_trainer.rs`, `card_validation.rs` (allowed for this follow-up); and 8 test files. Nothing in `players/` or `Cargo.lock` changed.

## Reach per card (`reach.py`, `reach_output.txt`)

Every printing whose attack text maps to the site's mechanic, and the lists under `decks/` (64 files) that hold it. `decks/` is the same on R and on main (d010d2d).

| site | printings | lists under `decks/` |
|---|---|---|
| Wild Swing | Gyarados A4 045, A4 215 | **A4 045: `decks/screen/panel_ladder_2026-09-26/l-sharpedo.txt` (2 copies)**; A4 215: none |
| Wellspring Dance | Wellspring Mask Ogerpon B2 048 | none |
| Tornado Shot | Rapid Strike Urshifu B3 051 | none |
| Double Splash | Blastoise B1a 019 | none |
| Triple Bombardment | Mega Blastoise ex B1a 020, B1a 078, B1a 084 | none |
| second punch | Mega Kangaskhan ex B2 127, B2 189, B2 202, B4 231 | none |
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
5. `44751d3`, `76b87cd`: this README, `suite.log`, `reach.py` and the smoke check.
6. **The seventh site**, after the fifth file was approved:
   - the log line on the coordination branch (e787a94);
   - `9145eb3`: its two failing tests, in their own commit (`tests_before_fix_kangaskhan.log`: both fail, 0 prevented of 60; 23 passing);
   - `29e126a`: the gated fix, in `apply_attack_action.rs` and `state/mod.rs` (`tests_after_fix_kangaskhan.log`: 25 of 25);
   - `bfe8aeb`: the counters;
   - then the suite, the smoke rerun and this README.

The engine diff from R is four files:
- `engine/src/actions/apply_attack_action.rs` and `engine/src/actions/apply_action.rs` (two of the first round's four);
- `engine/src/state/mod.rs`, the approved fifth file, in its pending-hit check only;
- `engine/tests/pokemon/meowth_carefree_steps_test.rs`.

`attack_outcome.rs` and `hooks/core.rs` needed no change. Nothing in `players/` or `Cargo.lock` changed.

## The gates (read them in the code; line numbers at `29e126a`, `engine/src/actions/apply_attack_action.rs` unless named)

- **The constructor.** `queued_attack_damage_choice` (281) now hands its one target to `queued_attack_damage_targets_choice` (294). That function also takes one choice that hits several of the opponent's Pokémon: the Active's hit and a Benched hit queued together.
  - With a coin target, it builds the attack's own `ApplyQueuedAttackDamage`, with the first round's debug line.
  - Without one, it builds the same `ApplyDamage` as before.
- **The gate.** `coin_gated_choice` (334) takes a choice built as `ApplyDamage` from the attacker's Active. It sends the choice through the constructor only when every target is the opponent's and one of them has a coin Ability (`any_coin_target`, 320, which reads `coin_damage_prevention`, 264). Anything else comes back exactly as it was. That includes a choice that also hits the attacker's own Bench.
- **The sites:**
  - Wellspring Dance: `coin_flip_also_choice_bench_damage` (5804; the gate at 5821). Its tails branch deals the Active's damage directly, which already flipped.
  - Tornado Shot: `self_discard_energy_and_choice_bench_damage` (3941; 3956).
  - Double Splash and Triple Bombardment: `conditional_bench_damage_attack` (6127; 6203). The finished choices are gated, so the own-Bench form (no card) passes through.
  - Mischievous Ring: `shuffle_opponent_tools_into_deck_before_damage` (8507; 8528). It now takes the attack, and the gate reads the board after the Tools are shuffled away.
  - Wild Swing: `discard_then_damage_choice` (359) now finds the attacker's printed attack that offered the discard, Chase Order or Wild Swing (`printed_attack`, 398), instead of Chase Order only. It is called from `apply_action.rs`'s `apply_discard_own_benched_then_damage` (1306).
  - Litter: `apply_action.rs`'s `forecast_discard_own_cards_for_attack_damage` queues its damage through `discard_tools_then_damage_choice` (`apply_action.rs` 1731; 372 here). It finds Litter among the attacker's printed attacks the same way.
  - Both of the last two build their plain `ApplyDamage` in `chosen_damage_choice` (378) and gate it with `coin_gated_choice` (391).
  - Mega Kangaskhan ex's second punch: `mega_kangaskhan_ex_double_punching_family` (2197) queues the 40 through `queued_attack_damage_choice` (2209). The gate (2207-2208) is any of the opponent's Pokémon having a coin Ability, since the punch lands on whichever Pokémon is Active then: the one hit now, or the one promoted after a knockout. The coin is read on the Active when the damage resolves, as for the first round's Pull In and Pound.
- **The fifth file**, `engine/src/state/mod.rs`, `trigger_promotion_or_declare_winner`'s pending-hit check (1417-1432). Its new arm (1428-1430) also recognises an `ApplyQueuedAttackDamage` aimed at the empty Active, from the other player's frame. So the promotion still goes above the waiting punch.
  - The `ApplyDamage` arm's other clause (the attacker's own empty Active) is not mirrored. Every Mega Kangaskhan ex printing is a Mega ex, so a Kangaskhan Knocked Out on its own turn (by Rocky Helmet, say) gives 3 points and ends the game.
  - I checked that in a scratch copy: 40 seeds, every such knockout ends the game, no panic.
  - Mirroring the clause would also reorder the first round's queued choices when an attacker's Active empties.
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
| `celestial_blessing_flips_for_both_punches_of_double_punching_family` (the non-knockout case: into Togekiss, 140 HP; the damage is 0, 40, 80 or 120, and the second punch must sometimes be prevented, 0 or 80, and sometimes not) | fails: second punch 0 prevented, 60 hit | passes |
| `carefree_steps_flips_for_the_second_punch_after_a_knock_out` (the first punch Knocks Out Bulbasaur; player 1 promotes Meowth before the second punch's damage resolves, and Meowth's coin flips) | fails: 0 prevented, 60 hit | passes |
| `the_later_rounds_sites_into_pokemon_without_a_coin_ability_are_unchanged` (the control: all seven sites, Mega Kangaskhan ex included, into Mega Latios ex, 20 seeds each; every queued damage choice stays `ApplyDamage`) | passes | passes |

- A test passes when Meowth took none of the damage in more than 10 of 60 seeds and some damage in more than 10. For Wellspring Dance the bar is 5 of the heads seeds. For the punches it is the second punch: more than 10 prevented and more than 10 not.
- The "before" column for the first six sites is R; for the two punch tests it is `76b87cd`, this branch before the seventh fix.
- The helper `carefree_steps_counts` now runs through `carefree_steps_seed`, which also reports whether a queued choice at Meowth was offered, and can put Tools in the hand. The first round's tests use it unchanged and pass.

## The unit suite (`suite.log`)

`cargo test --release --features test-utils`, at `29e126a`'s engine (the last commit that touches `engine/`): **2,027 passed, 0 failed, 0 ignored.**
- That is R's 2,018 (Sonnet's suite at R, in `../engine_switch_rules_2026-10/EQUIVALENCE_sonnet.md` on b3e6eae) plus the 9 tests added here. The Wild Swing pin was flipped, not added.
- At `e0ecf19`, before the seventh site, it was 2,025: the 2 punch tests are the difference.
- No existing test's expected value was edited, apart from the S2 pin, which asked for it.

## The counters (`instrument_scan.py`, `counter_probe_round2.rs`)

- **`../coin_prevention_repair_2026-09-30/instrument_scan.py`** (the coin repair's watch-only counters) gets this round's six helper mechanics in `HELPERS`. So `offgate_helper_choice` sees their off-gate choices, the proof that a table runs the rewritten lines.
  - The mechanics: `CoinFlipAlsoChoiceBenchDamage`, `SelfDiscardEnergyAndChoiceBenchDamage`, `ConditionalBenchDamage`, `ShuffleOpponentToolsIntoDeckBeforeDamage`, `DiscardToolsFromHandForDamage` and `MegaKangaskhanExDoublePunchingFamily`.
  - Wild Swing's off-gate damage was already `offgate_discard_then_damage`'s.
  - The queued coin-path choices of all seven are `coin_queued_offered`'s with no change.
  - The script still applies alone and with the Victory Star script in either order (the same sorted lines), and the instrumented scan compiles on this engine.
- **`counter_probe_round2.rs`** (output in `counter_probe_round2_output.txt`) uses F5's detection functions, copied, on boards built with `test_support`. For each site it checks:
  - the mechanic's name keys the right off-gate counter;
  - with Meowth there, the queued choice is offered, and choosing it runs Meowth's coin split (for the second punch, Togekiss, since the first punch would Knock Out a Meowth);
  - with Bulbasaur instead (Mega Latios ex for the punch), only plain choices are offered.
  - Result: **32 checks, 0 failures.**
  - Run it as an example in the engine, as F5's was: `cargo run --release --features test-utils --example counter_probe_round2`.

## The smoke check (`smoke/`)

- **Decks** (scratch only, no table deck):
  - `water_round2.txt`, made for this check: the repaired attackers that bots can get into play. That is 2 Magikarp and 2 Gyarados A4 045, 2 Kubfu and 2 Rapid Strike Urshifu, 2 Wellspring Mask Ogerpon, 2 Hoopa, Slowpoke and Slowking, plus Professor's Research, Poké Ball and 2 Giant Cape for Litter.
  - Blastoise and Mega Blastoise ex (Stage 2) and Mega Kangaskhan ex are left to their tests.
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
- **Run twice.** First at `0e9464a`, before the seventh site; then again at `bfe8aeb`, whose `engine/` equals `29e126a`'s (the final engine, with `state/mod.rs`).
  - All three game files of the second run are byte-identical to the first's, 80 of 80 lines each.
  - So the seventh site's change, `state/mod.rs`'s pending-hit check included, changed none of these games. Mega Kangaskhan ex isn't in the decks.
  - The files here are the second run's.
- The scans' sha256 (`run_output.txt`):
  - second run: R plain `aca7d9a0…6e9`, this branch plain `24cf696f…c3a`, watch `452dfada…f04`;
  - first run: this branch plain `b7c1c6f4…dc9`, watch `0467c6aa…b2d`.

## Mega Kangaskhan ex

- **The site.** `mega_kangaskhan_ex_double_punching_family` (2197) queued the second punch, "The second attack does 40 damage", as a plain `ApplyDamage` at the opponent's Active. It inserts it at the bottom of the stack, so that a promotion after the first punch's knockout comes first.
- **Why a fifth file.** `trigger_promotion_or_declare_winner` puts the promotion above the waiting punch only if its pending-hit check sees the punch. That check looked only for an `ApplyDamage` aimed at the empty Active. Queued as the attack's own `ApplyQueuedAttackDamage`, the punch wasn't seen. The promotion would have gone under it, and the punch would have landed on an empty Active Spot.
  - Approved by the coordinator via Dustin, Oct 1: the pending-hit check only, nothing else in the file.
- **The fix** (`29e126a`): see "The gates". `state/mod.rs`'s diff is that one check: its new arm and a three-line comment.
- **Before and after:**
  - Before (`tests_before_fix_kangaskhan.log`): both tests fail, 0 prevented of 60.
  - With `apply_attack_action.rs` changed alone (checked in a scratch copy, before the approval): the Togekiss test passes, but the knockout case fails ("the second punch waits for the new Active": the punch lands first).
  - With the `state/mod.rs` check too (`tests_after_fix_kangaskhan.log`): both pass, 25 of 25 in the file.

## For the laptop

- **kd needs no follow-on.** Since F1 (R), kd prices the coin for every hit an attack does (`hooks/core.rs`, `persistent_defender_damage`). This round brings the engine to kd for these seven sites.
- **The replay**, at the next switch, which takes this round (RUN5, "Engine repairs: the switch procedure"):
  - The expected number of changed table games is **0**, as for the first round: no list under `decks/` holds a coin Ability.
  - `instrument_scan.py`'s counters, as this branch has them, must read 0 for the changed-mechanic counters in every table game, and the watch scan's moves must equal the plain scan's.
  - A Wild Swing control row like the current step 8b's l-sharpedo v `meowth_carefree` changes meaning (see "In plain words").
- rules/09 and PLAN.md are not edited here.

## Limits

- **A copied attack.** Wild Swing's and Litter's queued damage looks for the attack among the attacker's own printed attacks, as Chase Order's discard branch already did. A copied one keeps a plain `ApplyDamage`, which since the card-text job (Oct 2) flips the coin itself (`forecast_apply_damage`).
- **The other targets of a gated choice.** When a choice that hits two Pokémon takes the coin path because one of them has a coin Ability, the other target's damage also runs the attack's modifiers. That is the attack's name and text in `modify_damage`, and the defender's Guts, point-denial and Perish Body coins.
  - That is right by the rules, since it is the attack's damage. But it differs from the plain `ApplyDamage` it replaces, which carried none of them.
  - The same side effect the first round recorded for its helpers.
- **The own-Bench forms** of `coin_flip_also_choice_bench_damage` and `conditional_bench_damage_attack` (no card today) pass through the gate unchanged, like `also_choice_bench_damage`'s; since the card-text job their plain `ApplyDamage` flips the coin itself.
- **The fifth file's new arm sees any queued attack damage aimed at the empty Active**, not only the second punch: also the first round's gated choices and `also_choice_bench_damage`'s opponent-Bench form. That is the same as the `ApplyDamage` arm already does for their plain twins.
  - I found no path where one of them is still on the stack when a promotion is queued, but I did not audit every one.
  - The smoke check's games are unchanged by it (below).

## Files

- `README.md`: this note.
- `tests_before_fix.log`, `tests_after_fix.log`: `meowth_carefree_steps_test` before and after the six sites' fix.
- `tests_before_fix_kangaskhan.log`, `tests_after_fix_kangaskhan.log`: the same, for the seventh.
- `suite.log`: the full unit suite at `29e126a`.
- The card-text job: `TEXT_AUDIT.md`; `tests_before_fix_will.log`, `tests_after_fix_will.log`; `tests_before_fix_text.log`, `tests_after_fix_text.log`; `tests_before_fix_trap_territory.log`, `tests_after_fix_trap_territory.log`; `suite_card_text.log` (the full suite at `5155ff7`).
- The follow-up: `tests_before_fix_followup.log`, `tests_after_fix_followup.log`, `suite_followup.log` (the full suite at `3090abb`).
- `reach.py`, `reach_output.txt`: reach per card.
- `counter_probe_round2.rs`, `counter_probe_round2_output.txt`: the counters on constructed boards.
- `smoke/`: the smoke check.
  - `water_round2.txt`: the scratch deck of repaired attackers. `meowth_carefree.txt` and `fire_heatmor.txt` are the first round's scratch decks, copied.
  - `pairs.tsv`, `run_smoke.sh`, `run_output.txt`: the pairings, the run, and its output (the builds' sha256s and the three scan pages).
  - `games_r_plain.jsonl`, `games_round2_plain.jsonl`, `games_round2_watch.jsonl`: the games.
  - `compare.py`, `compare_output.txt`: the comparison.
- Changed outside this folder: `../coin_prevention_repair_2026-09-30/instrument_scan.py` (the counters), and the engine files named under "Commits".
