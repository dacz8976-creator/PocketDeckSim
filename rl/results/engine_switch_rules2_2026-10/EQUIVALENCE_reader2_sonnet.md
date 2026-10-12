# Rules switch 2, reader two (Sonnet): (f) the source equivalence, read from the callers

Oct 10. Reader two, as briefed: read-only, no cargo, nothing edited outside my two files. Lean, by myself, no agents.
I did not open reader one's files (`EQUIVALENCE_reader1_opus.md`, `SECOND_READ_reader1_opus.md`) before committing these.

- **Old** = main-8626a35, engine tree 38af8b0 (the official engine).
- **P** = c7a25df4 on `origin/claude/coin-prevention-round2`, engine tree 70652fff (31616338 plus F1: f601abcb tests, c7a25df4 the fix).
- **Verified first:** `git diff --no-renames --name-status 8626a35 c7a25df4 -- engine/` is identical, row for row, to the 26 rows of
  `allowed_engine_files.tsv` (17 `src` M, 8 tests M, 1 test A). Nothing else under `engine/` changed (so `database.json` and
  every other file are byte-equal), and `players/`, `Cargo.lock` and `Cargo.toml` are unchanged.
- **Standard** (the Sept 28 refactor rule, Oct 1's reading): wherever none of switch 2's rules applies, the same returned values
  in the same ORDER with the same probabilities in every Outcomes/Mutations/Actions Vec, the same state mutations in the same
  order, the same RNG draws, the same early returns and panics.
- **Switch-2 domain** (the inputs I excluded): round-2 coin sites G1-G3, G7, G8; Will/Confusion/block coin G4, G5; Trap
  Territory G6; Luxury Coin G9; Fossil as an Item G10, G11 (P3); P2's return damage with Weakness; the per-gate off switches.

## 0. Verdict

**(f) equivalent**, with the list: **C1** is the one path I could not show unreachable by construction (the F1 arm reaching an
official `ApplyQueuedAttackDamage` frame); I showed it unreachable for every attack in the database and found no input that
exposes a difference. N1-N7 are notes, none a difference. No path outside the domain differs.

## 1. What I covered (the mapping for allowed_engine_files.tsv: 26 of 26 rows)

"Full" = the whole diff 8626a35..c7a25df4 read (a 8-line-context diff per file), every changed function's callers followed with
grep over `engine/src` (and `engine/tests`, `players/`) at P, and the off-domain path argued below. "Names" = diff-stat, the
list of removed lines and the test names only; I did not read those files line by line.

| # | File | Read | Section |
|---|---|---|---|
| 1 | `src/actions/apply_abilities_action.rs` | full | 4.10 |
| 2 | `src/actions/apply_action.rs` | full | 4.1-4.3, 4.6 |
| 3 | `src/actions/apply_action_helpers.rs` | full | 3, 4.2 |
| 4 | `src/actions/apply_attack_action.rs` | full | 4.3-4.7, 4.10 |
| 5 | `src/actions/apply_trainer_action.rs` | full | 4.10 |
| 6 | `src/actions/attack_outcome.rs` | full | 4.4, 4.5 |
| 7 | `src/actions/mod.rs` | full | 3 |
| 8 | `src/actions/shared_mutations.rs` | full | 4.10 |
| 9 | `src/actions/trainer_coin_plan.rs` | full | 4.9 |
| 10 | `src/card_validation.rs` | full (text only) | N4 |
| 11 | `src/hooks/core.rs` | full | 4.4, 4.2 |
| 12 | `src/hooks/counterattack.rs` | full | 4.2 |
| 13 | `src/hooks/mod.rs` | full (re-exports) | 3 |
| 14 | `src/hooks/retreat.rs` | full | 4.8 |
| 15 | `src/models/card.rs` | full | 4.10 |
| 16 | `src/move_generation/move_generation_trainer.rs` | full | 4.9, 4.10 |
| 17 | `src/state/mod.rs` | full (F1) | 4.11, C1 |
| 18 | `tests/b4a_attack_batch2_test.rs` (442+/93-) | names | 5 |
| 19 | `tests/gholdengo_luxury_coin_test.rs` (64+/9-) | names, the replaced test read | 5 |
| 20 | `tests/pokemon/galarian_cursola_perish_body_test.rs` (121+) | names | 5 |
| 21 | `tests/pokemon/legacy_ability_logic_test.rs` (114+) | names | 5 |
| 22 | `tests/pokemon/meowth_carefree_steps_test.rs` (1039+/37-) | names | 5 |
| 23 | `tests/pokemon/ursaluna_guts_test.rs` (81+) | names | 5 |
| 24 | `tests/rules_repair_return_damage_weakness.rs` (A, 891+) | names | 5 |
| 25 | `tests/rules_repair_trainers.rs` (521+) | names | 5 |
| 26 | `tests/victini_victory_star_test.rs` (16+) | names | 5 |

## 2. The gate map (what each off switch is, and where it is read)

All in `apply_action_helpers.rs` (the `round2_switch!` macro): a `LazyLock` reads the env flag once (`"1"` or `"true"`), a
`thread_local Cell<Option<bool>>` holds a `with_*` override, `*_on()` = override, else `!(env || DECKGYM_ROUND2_OFF)`. `scoped()`
restores each setting in reverse order on drop (also on a panic). `with_round2` sets RETURN_WEAKNESS and G1-G11 (12 settings).
With nothing set every gate is on. I checked that the 12 settings in `with_round2`, the 12 spellings and `counters.tsv`'s
`revert_switch` column agree (G1 `DECKGYM_NO_PLAIN_HIT_COIN` ... G11 `DECKGYM_FOSSIL_NOT_ITEM`, P2 `DECKGYM_FLAT_RETURN_DAMAGE`).

| Gate | Read at | Off means |
|---|---|---|
| G1 plain-hit coin | `forecast_apply_damage` (apply_action.rs:801) | `coin_targets` is empty: no coin for a plain queued hit |
| G2 seven sites | `site_coin_gated_choice`, `discard_then_damage_choice`, `discard_tools_then_damage_choice`, Mega Kangaskhan's second punch (all apply_attack_action.rs), `State::trigger_promotion_or_declare_winner` (state/mod.rs:1432) | each site queues a plain `ApplyDamage`; no promotion arm. The old damage needs G1 off too (a plain `ApplyDamage` at a coin target then flips under G1) |
| G3 own side | `apply_defender_damage_prevention_if_needed`, `forecast_apply_damage` filter, `modify_damage`'s `heads_coin_cut` (hooks/core.rs) | opponent's Pokemon only |
| G4 Will | `will_goes_to_the_block_coin`, `victory_star_stages_gate_coins`, the Will step in `apply_attack_common_modifiers` | Will is not used on a gate coin |
| G5 Victory Star after a block coin | `victory_star_stages_gate_coins` | a block coin keeps the legacy resolution |
| G6 Trap Territory | `get_retreat_cost_for_player_internal` (hooks/retreat.rs) | the old loop: one 1, however many Ariados |
| G7 own-side Guts | `apply_defender_guts_if_needed` | opponent's Guts Pokemon only |
| G8 Perish Body on a queued hit | `forecast_apply_damage_after_coins` | no Perish Body coin there |
| G9 Luxury Coin | `luxury_coin_covers` (trainer_coin_plan.rs) | every Stadium is covered |
| G10 Fossil lock | `generate_possible_trainer_actions` | an Item lock stops Items only |
| G11 Fossil as an Item (P3) | `TrainerType::is_printed_as` (models/card.rs) | a type matches only itself |
| P2 return damage | `handle_attack_retaliation` (apply_action_helpers.rs:783) | `weakness_extra` is 0 |

## 3. Plumbing (apply_action_helpers.rs, actions/mod.rs, hooks/mod.rs)

New statics, thread-locals, `scoped`, the macro, `with_round2` and the re-exports. They add no behaviour of their own: a
`LazyLock` env read on first use, a `Cell` read per call, no state, no RNG. The only effect at a default setting is that each
`*_on()` returns true. `hooks/mod.rs` re-exports `attack_return_weakness_extra` and `attack_counterattack_damage`; `actions/mod.rs`
re-exports the `*_on` readers (`pub(crate)`) and the `with_*` functions (`pub`). Equivalent.

## 4. Function by function

### 4.1 `forecast_apply_damage` and `forecast_apply_damage_after_coins` (apply_action.rs 790-960)
Callers: `forecast_apply_damage` only from `forecast_action`'s `ApplyDamage` arm (:557); `_after_coins` only from it (:815, :845).
Off-domain path (G1 on but no target, other than an own-side one with G3 off, has a coin Ability and takes damage; or G1 off):
`coin_targets` is empty, so `forecast_apply_damage_after_coins(state, attacking_ref, targets.to_vec(), vec![], flag)` runs.
There:
- `damage_map` is the same HashMap sum. `perish_body` is `perish_on_queued_hit_on() && is_from_active_attack && <defender's Active has Perish Body> && would_knock_out(..)`; the first three terms short-circuit it false for every input without a Perish Body Active (domain G8 otherwise); `would_knock_out` is a pure forecast.
- `flipping` is the old filter wrapped in `with_heads_coin_cuts(vec![], ..)`. With no cuts and none in force that wrapper just runs `f` (attack_outcome.rs:45-48). No cuts can be in force here: the scopes are opened only at attack_outcome.rs:228, 804, 899, 1009, 1093 and in this function, and each wraps a pure damage calculation or `handle_damage_only`, none of which calls `forecast_apply_damage`.
- `flipping.is_empty() && !perish_body`: the same `Outcomes::single_fn` calling `handle_damage(state, attacking_ref, &targets, flag, None)` (the wrapper is a pass-through).
- Otherwise: `perish_coins = [false]`, so the probabilities are `1.0 / (combos * 1)`, identical to `1.0 / combos`; the masks run in the old order; each mutation runs `handle_damage_only`, sets the survivors to 10 HP, `handle_attack_retaliation`, `handle_knockouts`, in the old order. `if perish_heads` is false.
The new BTreeMap `raw` is built always and used only for G1's `coin_targets`. Equivalent. (N1: the `flipping` order comes from a HashMap, in the old code too.)

### 4.2 `handle_attack_retaliation`, `get_counterattack_damage`, `attack_counterattack_damage`, `attack_return_weakness_extra`
Callers of `handle_attack_retaliation` (5, none changed): apply_action_helpers.rs:531 (inside `handle_damage`), apply_action.rs:635 and :959, attack_outcome.rs:281, players/public_reply.rs:564. `get_counterattack_damage` callers: the function itself, value_functions.rs:1936, :5038.
`get_counterattack_damage` moves the `CardEffect::Counterattack` sum into `attack_counterattack_damage` unchanged (the same `filter_map` and `sum::<u32>()`); the Tool, effect and Ability terms are added in the same order. Equal.
`handle_attack_retaliation`: `weakness_extra` is computed only when `return_weakness_on() && attacking_ref.1 == 0 && attack_counterattack_damage(target) > 0`. Without a `CardEffect::Counterattack` on the damaged Pokemon (Rocky Helmet, an Ability, or nothing) the value is 0 and `apply_damage(counter_damage + 0)` is the old call. With one, the extra is Weakness or Bounded Field: P2's domain. The poison, `maybe_attach_energy_on_damaged` and hand-shuffle lines are untouched. Equivalent.

### 4.3 Victory Star staging and the attack's gates (apply_action.rs 187-400, apply_attack_action.rs 93-240)
Callers: `victory_star_waits_for_gate_heads` (apply_action.rs:200), `will_goes_to_the_block_coin` (:206 and apply_attack_action.rs:226), `victory_star_stages_gate_coins` (:210, :378), `gate_heads_probability` (:294), `gate_tails_outcomes` (:297), `finish_attack_after_gate_heads` (:384). The five removed functions (`has_unverified_attacker_coin_gate`, `victory_star_waits_for_confusion_heads`, `confusion_tails_outcomes`, `finish_attack_after_confusion_heads`, `chase_order_attack`) have no caller left at P (the only text hits are a comment and a test comment).
Every combination of attacker state, with `S` = `victory_star_stages_gate_coins`, all other inputs as in the official engine:

| Attacker (not a copied attack) | Official | P (all gates on) | Domain? |
|---|---|---|---|
| not Confused, no block coin (any Will) | no gate: continues, `branches` as built, Will forced on the sample as before | `gates_first` false, `will_on_block` false (needs a block coin): the same path | no, equal |
| Confused only, no Will | `confusion_first`: tails `0.5*p` then heads `0.5*p`, tails from the same `apply_defender_attack_modifiers` call | `heads = 0.5*1.0`, tails `(1.0-0.5)*p`, heads `0.5*p`, the same order, same tails function (renamed), `will_on_block` false | no, equal (0.5 and `1.0-0.5` are exact) |
| Confused, Will pending | `None` (legacy resolution) | `S` true with G4 on: stages | G4 |
| Block coin (with or without Confusion) | `None` | `S` true with G5 on: stages | G5 |
| a copied attack (`is_stack`) | all false | all false | equal |

`forecast_victory_star_choice`: `S` equals the official `victory_star_waits_for_confusion_heads` exactly when G4 and G5 are off (`confused && !block && !Will`), and when they are on it differs only for a block coin or a Will. `apply_attack_common_modifiers`: the new Will step needs `confused && !block && Will pending && G4`, the new block branch needs `block && Will pending && G4`; otherwise `apply_confusion_coin_flip` and `apply_block_attack_coin_flip` are called as before and `has_block_coin` is the old inline predicate. The new `force_first_heads_using_will`, `block_coin_heads_by_will` and `using_will_first` (attack_outcome.rs) have no other caller. Equivalent.

### 4.4 `apply_defender_damage_prevention_if_needed`, `split_with_damage_prevention`, `modify_damage`'s cut (apply_attack_action.rs 280-320, attack_outcome.rs, hooks/core.rs)
Callers of `split_with_damage_prevention`: only `apply_defender_damage_prevention_if_needed` (and tests, updated to the new tuple). The reductions become `(bool, usize, u32)`; the opponent's entries are `(true, idx, r)` in the old enumeration order, with the old Active exclusion for "ignores effects"; own-side entries come after, through a `.chain` filtered by `own_side_coin_on()` and by the Pokemon having the Ability. With no own-side coin Ability (or G3 off) the Vec is the old one. In the split, `is_opponent == target_side` with `target_side = true` is the old `*is_opponent && idx == target_idx`; the full-prevention retain and the `heads_coin_cuts` push (`(true, idx, cut)` resolved to `(opponent, idx)` by `resolved_heads_coin_cuts`) reduce to the old expressions. `modify_damage`: `attacking_player != target_player || own_side_coin_on()`; for `attacking_player != target_player` unchanged; for an own-side target `heads_coin_cut` is non-zero only when an own-side entry was put in force, which needs an own-side coin Ability (G3's domain). The `coin_damage_prevention` visibility change is a keyword. Equivalent.

### 4.5 `apply_defender_guts_if_needed` and `split_with_guts_survival`
Only caller of the split. Slots `(true, idx)` for the opponent first (old order), then `(false, idx)` for the attacker's own side behind G7 and the Ability. Without an own-side Guts Pokemon the Vec equals the old indices; in the split `is_opponent == target_side` and `target_player = opponent` are the old filter and the old `(opponent, *target_idx)`; the survivor loop picks `opponent` for `true`. Equivalent.

### 4.6 The queued-choice helpers (apply_attack_action.rs 330-460, 2270-2290, 4010-4040, 5870-5900, 6270-6285, 8575-8610; apply_action.rs 1436, 1861)
- `queued_attack_damage_choice` now delegates to `queued_attack_damage_targets_choice` with one target: the same `ApplyQueuedAttackDamage { attack, targets: [(damage, true, idx)] }` or `ApplyDamage { (actor, 0), [(damage, (actor+1)%2, idx)], true }` as before. Its callers (apply_attack_action.rs:2285, 3056, 3095, 3133, 4095, 4586, 4736, 6727) are unchanged and keep their own `coin_target` test.
- `discard_then_damage_choice` (only caller apply_action.rs:1436, `apply_discard_own_benched_then_damage`): with G2 off the source test is the Chase Order mechanic only; `chosen_damage_choice` then builds the same plain `ApplyDamage` and `coin_gated_choice` queues it as `ApplyQueuedAttackDamage` exactly when the opponent's Active has a coin Ability, with the printed Chase Order attack found by the same `.find` (first attack with that mechanic): the old `chase_order_attack` and test, in the same order. Only `DiscardOwnBenchedThenDamage` producers: apply_attack_action.rs:4596 (Chase Order) and :6582, :6588 (Wild Swing, G2).
- `discard_tools_then_damage_choice` (only caller apply_action.rs:1861): with G2 off the source test is false, so `printed_attack` is `None` and the plain `ApplyDamage` is pushed, as before (the inline `ApplyDamage` it replaced was built with the same fields). `DiscardOwnCardsForAttackDamage` producers: apply_attack_action.rs:5663, :5669.
- `site_coin_gated_choice` returns `choice` unchanged with G2 off; with G2 on `coin_gated_choice` changes only an `ApplyDamage` from the attacker's Active whose targets are all the opponent's with at least one coin Ability, so without a coin target every site still queues the old `ApplyDamage`. Its four sites: `self_discard_energy_and_choice_bench_damage` (:4032), `coin_flip_also_choice_bench_damage` (:5895), `conditional_bench_damage_attack` (:6277, a no-op `map`/`collect` when off), `shuffle_opponent_tools_into_deck_before_damage` (:8602, same RNG draws: the shuffle precedes the push). The three changed signatures each have one dispatch call, updated.
- `mega_kangaskhan_ex_double_punching_family`: `coin_in_play` is false with G2 off or without a coin target among the opponent's Pokemon, giving `ApplyDamage { (actor, 0), [(40, opponent, 0)], true }` and the same `insert(0, ..)` as before.
Equivalent.

### 4.7 `also_choice_bench_damage` and other official `ApplyQueuedAttackDamage` producers
Unchanged code; listed for C1. Equivalent (not in the diff).

### 4.8 Trap Territory (hooks/retreat.rs)
G6 on replaces "one 1 for any number of Ariados, when the mechanic is `IncreaseRetreatCostForOpponentActive { amount: 1 }`" with "`amount` Colorless for each such Pokemon". The mechanic has a single producer, `amount: 1` (effect_ability_mechanic_map.rs:692). With no such Pokemon in play both loops add nothing; with exactly one, both add one Colorless. The G6-off branch is the old loop, byte for byte. Differs only with two or more Ariados (domain). N2: the new pattern drops `amount: 1`; with a future card of another amount it would add that amount where the old code added none.

### 4.9 Luxury Coin and the Item lock
`luxury_coin_covers` is false only for G9 on, `UseStadium`, and a Stadium whose recorded owner is the opponent. Both entry points call it right after finding the Luxury Coin source (`try_sample_entry_actual` returns `None`, `try_forecast_entry` returns `Ok(None)`, the same value the missing source returns). Otherwise unchanged. The Item lock: `(Item || (G10 && Fossil)) && !can_play_item(state)`; for any non-Fossil card, or with no Item lock, `can_play_item` is true and the line behaves as before. Equivalent.

### 4.10 P3 (`is_printed_as`, `Card::is_item`, G11)
`is_printed_as(self, printed)` is `self == printed` unless G11 is on, `printed == Item` and `self == Fossil`. Eight call sites changed from `==` to it: apply_abilities_action.rs (trainer-type search of the deck), apply_trainer_action.rs (Thieving Machine), shared_mutations.rs (`item_search_outcomes`), move_generation_trainer.rs (`can_play_team_rockets_thieving_machine`), apply_attack_action.rs (`SearchRandomTrainerTypeFromDiscardToHand`, `extra_damage_per_trainer_type_in_discard_attack`, `discard_top_self_deck_extra_damage_if_trainer_type`, and `matches_hand_card_kind` through `Card::is_item`). Each differs only when the card compared is a Fossil and the printed kind is Item. A query for another kind (Supporter, Tool, Stadium, Fossil) is `==` as before. Equivalent.

### 4.11 The promotion floor (state/mod.rs 1411-1440): see C1.
With G2 off the new arm is `false && ..`; the other arm is the old `ApplyDamage` arm, and the closure's new `(actor, choices)` pattern binds a name nothing else reads. Equivalent with G2 off. With G2 on it differs from the official engine whenever a promotion is triggered for player E while an `ApplyQueuedAttackDamage` frame with `actor == E`, or with `(actor+1)%2 == E` and a target at the opponent's index 0, is on the stack at or above `phase_floor`. C1 shows the official engine never has that state.

## 5. The tests (names and removed lines only)

`git diff -U0 8626a35 c7a25df4 -- engine/tests` removes 139 lines in three files; the other six modified/added files only add lines.
- `b4a_attack_batch2_test.rs` (93 removed): the two tests that pinned the legacy resolution of a block coin with Victory Star (and the F7 equal-to-old test) and the Confusion-with-Will legacy test, plus an `Action, SimpleAction` import: G4/G5's old pins, replaced.
- `gholdengo_luxury_coin_test.rs` (9 removed): `activated_stadium_records_placer_but_eligibility_belongs_to_actor` is renamed `luxury_coin_is_offered_only_on_the_players_own_stadium` and now expects no offer on the opponent's Arcade; `revert_g9_luxury_coin_is_offered_on_any_stadium` re-pins the old behaviour verbatim inside `with_luxury_coin_own_stadium_only(false, ..)`.
- `meowth_carefree_steps_test.rs` (37 removed): the helper loop and `wild_swing_into_carefree_steps_pins_todays_behaviour_no_coin` (it said it would fail on purpose when Wild Swing was repaired): G2's old pin.
Each removed line sits in a test of the old behaviour inside the switch-2 domain; none is an off-domain pin.

## 6. Findings and notes

**C1. The F1 arm and the official `ApplyQueuedAttackDamage` producers.** The arm tests the stack, not the attack, so it also reaches frames the official engine builds. Producers at P: `also_choice_bench_damage`'s opponent form (apply_attack_action.rs:2939; bundled Active + Bench damage, pushed by `single_effect`, no earlier damage), and every `queued_attack_damage_choice` caller above (2285 Mega Kangaskhan, G2; 3056 `push_direct_damage_choices`; 3095; 3133; 4095; 4586; 4736; 6727 `switch_in_opponent_benched_then_damage`). For the arm to act, a Knock Out must trigger a promotion (callers of `trigger_promotion_or_declare_winner`: apply_action.rs:1329, 1385, 1405; apply_action_helpers.rs:1076; apply_trainer_action.rs:1634; apply_attack_action.rs:5457, 5535, 6365, 6681) while such a frame is still on the stack. Every producer above except 2285 is built by `active_damage_effect_doutcome(0, ..)`/`single_effect` (0 or bundled damage), so nothing is Knocked Out between the push and the player's pick. The one with a fixed damage first is `switch_in_opponent_benched_then_damage` (damage_then_effect): its three database cards (Sandy Shocks B3a 035 Pull In and Pound; Team Rocket's Hypno B4a 028 and B4a 074 Entrap) have `fixed_damage: 0`. So the window does not exist for any attack in `database.json`. I cannot prove it for a card not yet in the database. **Input that would expose it:** a card with a Switch-in (or other pre-damage) effect and `fixed_damage > 0` whose follow-up damage is queued with a coin-Ability Pokemon on the opponent's Bench, with the fixed damage Knocking Out the Active. The first condition (`*actor == E`) is the same kind of window: any future producer that leaves an `ApplyQueuedAttackDamage` frame pending across a Knock Out of the attacker's own Active (a retaliation, a recoil).

**N1 (not a difference).** The `flipping` Vec in `forecast_apply_damage_after_coins` comes from iterating a `HashMap<(usize, usize), u32>` in the official code and at P alike, so with two or more flipping targets the order of the masks is not reproducible run to run in either engine.
**N2.** G6 widening from `amount: 1` to any `amount` (4.8). One producer, amount 1.
**N3.** An environment variable named in section 2 silently turns that gate off for the whole process (read once). `pin_rules.sh`'s refusal of any `DECKGYM_*` is what protects the runs. The `with_*` overrides are thread-local and are not seen by `deckgym simulate`'s worker threads (the file says so).
**N4.** `card_validation.rs` changes `implementation_limitations` text for Victini (B3 025, PB 049: the first string replaced, a second added) and for Gholdengo (B4a 051, B4a 109: the second string replaced). Any output that prints those strings differs. PLAN step 7c says "only the Victini caveat line may differ"; a list with a Gholdengo would also show its changed line. Text only.
**N5.** `debug!`/`log::debug!` lines were added and changed. They run only when the logger is at debug level.
**N6.** The nine test files were read by name, diff-stat and removed lines only (section 5).
**N7.** With G2 on, `printed_attack` takes the first printed attack whose mechanic is Chase Order's or Wild Swing's. I know of no card with both.

I ran nothing: no cargo, no tests. The compile and test state is the cloud's, fc6307c0: 2,103 passed, 0 failed at P.

**(f) equivalent** — with the list: C1 (shown unreachable on every attack in the database, not provable for a future card); N1-N7 are notes.
