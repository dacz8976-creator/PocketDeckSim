Decision this informs: none yet. This is a drafted engine repair for a later engine switch (the Fable coordinator via Dustin, Oct 1). It stacks on Sonnet's R (1abdbe8, `origin/sonnet/rules-fixes`) on its own branch, `claude/coin-prevention-round2`, and is not merged or pinned. **It stays out of the current rules switch, whose scope is fixed, and goes in the next one** (the coordinator, Oct 1). No table game, carrier game or identity replay was played. **No independent audit of the patch has been done yet.** **Since Oct 2 it also carries the card-text job** (the coordinator via Dustin, Oct 1 evening): see "The card-text job" below and `TEXT_AUDIT.md`. **Since Oct 8 it also carries P2**, return damage left by an attack taking Weakness: see "P2" below. **Since Oct 9 it also
carries P2's off-switch and P3** (a Fossil is an Item card at seven more places), with the full suite at the final engine commit
`140c0be`: see "Oct 9" below. Step 8b's rows on that engine are in `../engine_switch_rules2_2026-10/early_warning_8b/`.

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

## P2 (Oct 8): return damage left by an attack takes Weakness

The coordinator via Dustin, Oct 8 (main `rl/results/engine_switch_rules2_2026-10/PLAN.md`, section 0: part 3 and precondition (h),
:29; 7fa6cdb7): its own engine commit on this branch, tests first, after the draft A slow report.

### In plain words

- **Five attacks** read "During your opponent's next turn, if this Pokémon is damaged by an attack, do X damage to the Attacking
  Pokémon":
  - Mega Sableye ex's Cursed Jewel, 40 (B3b 041, 081, 088);
  - Alolan Sandslash's Spike Armor, 40 (A3 039);
  - Togedemaru's Bristling Spikes, 30 (A3b 048, P-A 090);
  - Chesnaught's Needle Lariat, 80 (B2 010);
  - Turtonator's Shell Trap, 20 (B1 047).
- **That hit back is the attack's own damage, so it now takes Weakness:** +20 when the Attacking Pokémon is weak to the holder's
  type and is still in the Active Spot. Before, it was always flat.
- **Rocky Helmet's 20 and every Ability's return damage stay flat**, as before: Rough Skin, Steel Spikes, Automated Combat and the
  rest of the `CounterattackDamage` Abilities.
- **The evidence** (main `rules/02_damage_knockouts_points.md`, section 2; `rl/results/new_pause_games_triage_2026-10-06/TRIAGE.md`,
  2.1; this branch's own `rules/02` doesn't have the row yet):
  - your recording 183108 @306-308 and @384-386: Cursed Jewel did 60 to a Darkness-weak Houndstone, twice, the second time with
    the Mega Knocked Out by the same attack;
  - 215749 @99 and @161: Rocky Helmet did a flat 20 to a Fire-weak Tinkatink;
  - 20261006_220700000: Automated Combat did a flat 20 to Darkness-weak attackers, five times.
- **Three readings the tests pin, for you to confirm or overrule.** None has been seen in a game, and none can change a recorded
  game (see "Which games can change").
  1. **Bounded Field** left the hit back's extra at +20: Bounded Field's ×2 wasn't applied to it. **Replaced Oct 9 by the plain
     reading** (the coordinator via Dustin's card-text rule; `6b111ba` tests first, then the fix): the hit back is the attack's own
     damage, so under Bounded Field its Weakness is ×2 unless the holder is a Mega Evolution Pokémon ex (Chesnaught's 80 becomes
     160; Mega Sableye ex's Cursed Jewel keeps +20). The off-switch still gives the flat path. No recorded game reaches it, and
     shot-list rows 30-33 hold the four readings.
  2. **Steelix's Metal Defender** ("During your opponent's next turn, this Pokémon has no Weakness") doesn't protect Steelix from
     the hit back on the attack that uses it. The engine adds the effect before the hit back lands, but the card covers only the
     opponent's next turn.
  3. **Ledian's Swift** ("This attack's damage isn't affected by Weakness or by any effects on your opponent's Active Pokémon")
     doesn't stop the hit back or its Weakness: that text is about Swift's own damage.
- **A Benched attacker takes the hit back flat**: one that switched itself to the Bench with U-turn before the hit back landed.
  This follows rules/02's [OFFICIAL] "Don't apply Weakness for Benched Pokémon"; it hasn't been seen for return damage.

### Commits

- The log line first, on the coordination branch (e532aade).
- `d3739b7`: the 17 tests, 13 of them failing on the engine as it was (`tests_before_fix_p2.log`).
- `5543a4b`: P2, the engine change; all 17 pass (`tests_after_fix_p2.log`).
- Then the suite, the counters, the inventory and this README.

### Tests

`engine/tests/rules_repair_return_damage_weakness.rs`. The boards are constructed, not replays. Where an attack's return damage is
armed, the attack is used for real so the engine arms it; the two tests marked "constructed" add the `Counterattack` directly
instead. The attacker under test then replaces the stand-in Snorlax that took the setup hit, so that hit can't add Weakness of its
own.

| test | before (`57c6586`'s engine) | after (P2) |
|---|---|---|
| `each_attack_hits_back_with_weakness_on_a_weak_attacker` (all 8 printings) | fails: Houndstone 90, not 70 | passes |
| `each_attack_hits_back_flat_on_an_attacker_not_weak_to_it` (Snorlax) | passes | passes |
| `weakness_decides_the_knockout_by_the_hit_back` (X + 20 HP Knocked Out, X + 21 left at 1, no Bench loses) | fails | passes |
| `recording_183108_t8_cursed_jewel_returns_60` | fails: 90, not 70 | passes |
| `recording_183108_t10_hit_back_lands_when_the_holder_is_knocked_out` | fails: 80, not 60 | passes |
| `double_knockout_by_the_hit_back_the_attacker_promotes_first` | fails: Bulbasaur left at 20 | passes |
| `rocky_helmet_stays_flat_on_a_weak_attacker` (A2 148, A4b 322, A4b 323) | passes | passes |
| `ability_return_damage_stays_flat` (Automated Combat, Steel Spikes; Rough Skin on a constructed Dragon Weakness, since no card is weak to Dragon) | passes | passes |
| `tool_and_attack_return_on_one_defender_each_by_its_own_rule` | fails: 70, not 50 | passes |
| `ability_and_attack_return_on_one_defender` (constructed) | fails: 90, not 70 | passes |
| `held_back_hit_back_takes_weakness` (Psy Turbo's Attach first, then `ResolveAttackRetaliation`) | fails: 90, not 70 | passes |
| `apply_damage_path_takes_weakness` (`handle_damage`) | fails: 90, not 70 | passes |
| `perish_body_branch_hit_back_takes_weakness` (the `ApplyDamage` coin branch, constructed) | fails: a tails Tauros at 60, not 40 | passes |
| `hit_back_on_a_benched_attacker_stays_flat` (U-turn) | passes | passes |
| `metal_defender_does_not_shield_its_own_hit_back` | fails: 130, not 110 | passes |
| `swift_does_not_shield_the_hit_back` | fails: 60, not 40 | passes |
| `bounded_field_keeps_the_hit_back_extra_at_20` (Oct 9: `bounded_field_doubles_the_hit_back_x2`, Stonjourner Knocked Out; and `bounded_field_keeps_plus_20_for_a_mega_ex_holder`) | fails: Stonjourner 40, not 20 | passes |

### How (line numbers at `5543a4b`)

- `hooks/counterattack.rs`: the stored `Counterattack` sum moves into `attack_counterattack_damage` (:34), the part an attack
  left. `get_counterattack_damage` (:13) calls it and keeps its value (Rocky Helmet + attack + Ability).
- `hooks/core.rs`: `attack_return_weakness_extra` (:1535). It gives 20 when the Attacking Pokémon's printed Weakness is one of the
  holder's types, read through `pokemon_energy_types` (so Double Type counts, as in `printed_weakness_application`, :1503), and 0
  otherwise. It reads no `NoWeakness` and no Bounded Field: the two stated choices. (Oct 9: it now reads Bounded Field through
  `printed_weakness_application`, ×2 of the attack's return damage for a holder that isn't a Mega ex.)
- `hooks/mod.rs`: the two exports (:34-35).
- `handle_attack_retaliation` (`actions/apply_action_helpers.rs`:616): the extra (:625) goes into the same `apply_damage` (:637).
  It is computed only when the attacker is in the Active Spot (`attacking_ref.1 == 0`) and the defender carries an attack's
  return damage.

### The suite

`suite_p2.log`, at `5543a4b`: **2,056 passed, 0 failed, 0 ignored**, 102 targets (101 test binaries and the doc-tests). That is
the 2,039 at `3090abb` plus the 17 tests added here; no existing test changed. (`suite_followup.log`'s "104 targets" counted three
test names that begin with "result"; its totals are right.)

**The engine diff from the official engine** (main-8626a35) is now 21 files: the 17 above, plus `apply_action_helpers.rs`,
`hooks/counterattack.rs`, `hooks/mod.rs` and the new test file (`hooks/core.rs` was already in it). Nothing in `players/` or
`Cargo.lock` changed.

### Which games can change

From `../round2_readiness_2026-10-02/inventory_output_p2.txt`, run on main b77652d6:
- **Only two lists hold one of the five attacks:** brew-07 (1 Mega Sableye ex) and brew-09 (2).
- **No list holds a copy attack that could use one:** Mew ex's Genome Hacking, Mimikyu's Try to Imitate, Clefairy's
  Mini-Metronome, Mew's Miraculous Memory. Ditto's copies are Colorless, and no card is weak to Colorless.
- A scan of the other 58 twenty-card lists in the checkout finds none either. That agrees with the laptop's scan
  (`return_damage_scan.txt`: 2 of 135 files).
- **So:** the table, the new-17 cells, B2e, the carriers and 7c are 0. On the screen and floor, only brew-07 v t-altaria and
  brew-09 v t-altaria can change: t-altaria's Espeon is the only Darkness-weak Pokémon on the 8 panel lists. That is one row of 8
  on each list's floor pages (`floor_brews_2026-09-28`, `floor_dustin_2026-09-30`).
- The inventory page also names every other file that names the two lists, by file name or by label: the X Speed census, the
  screen pages under `decks/screen/` and the goldfish pages among them.

**In real games** (`../round2_readiness_2026-10-02/counter_smoke_p2/`). km3 played both sides of 50 deals each:
- brew-07 v t-altaria;
- brew-09 v t-altaria;
- brew-09 v t-sceptile (no Darkness-weak attacker);
- brew-07 v t-blaziken (Rocky Helmet).

Each deal was played on the engine before P2 and on P2, seeds 20,960,000,000 + pairing × 10,000 + i (Claude Code's diagnostic
block).
- **P2 changed 3 of the 200 games, 1 of them in its result. All three changed in look-ahead.** At the first differing tick the bot
  chose a different move from the same board, before any hit back had taken Weakness (`first_difference_output.txt`). In deal
  1:21 a flat hit back had already landed earlier, on an Eevee.
  - In deals 0:31 and 1:8 the armed Mega Sableye ex faced an Active Espeon.
  - In 1:21 it faced Mega Altaria ex, and the choice was whether to retreat into the Benched Espeon.

  km3's search runs the engine, so it sees the +20 coming and plays around it.
- **The exact counter fired in 7 games (7 ticks), all v t-altaria:** Espeon hit an armed Sableye and took 60. In those 7 games the
  moves stayed the same; the +20 changed HP, not the play that followed.
- **v t-sceptile and v t-blaziken nothing changed.** Only the off-gate counter fired there: the hit back stays flat on attackers
  not weak to Darkness, and Rocky Helmet is flat.
- **The counters change no play:** the P2 scan with and without them gives the same moves in 200 of 200 games.

### `players/` is unchanged

- **The bots see the +20 without a pricing change.** Their look-ahead forecasts each move through the engine
  (`expectiminimax_player.rs`:457, `try_forecast_action`).
- **public_reply never meets the change.** It calls the engine's own `handle_attack_retaliation` (`public_reply.rs`:564), and it
  gives up on any board whose Pokémon carries a stored effect other than PreventAllDamageAndEffects (:632-638).
- **kt switch 3's `counter_cut` still prices return damage flat** (`value_functions.rs`:1928-1948, through
  `get_counterattack_damage`). So it under-prices a weak attacker's hit back by 20. Only kt and ktc turn switch 3 on (:479-480,
  :486), and both are diagnostic; km3 and kta3 don't read it (:482, :488).

### For the equivalence readers

Main PLAN.md precondition (f) adds `handle_attack_retaliation`. In the format of
`rl/results/engine_switch_rules_2026-10/EQUIVALENCE_opus.md`:

| Hunk at `5543a4b` | Callers | Old | New on the table path | Why it's the same |
|---|---|---|---|---|
| `handle_attack_retaliation` (`apply_action_helpers.rs`:614-645) | `handle_damage` (:529; `ApplyDamage`'s plain branch, `apply_action.rs`:908), the immediate outcome (`attack_outcome.rs`:281), the held-back `ResolveAttackRetaliation` (`apply_action.rs`:627), the Guts and Perish Body branches (`apply_action.rs`:948), public_reply (`public_reply.rs`:564) | `apply_damage(get_counterattack_damage(..))` | `apply_damage(get_counterattack_damage(..) + weakness_extra)` | `weakness_extra` is 0 unless the damaged defender carries a `CardEffect::Counterattack`. Without one, the same number is applied in the same branch, with no new draws and no new frames. |
| `counterattack.rs` (:13-42) | `get_counterattack_damage`: `handle_attack_retaliation`; `value_functions.rs`:1936 (kt's `counter_cut`) and :5038 (a test) | the stored `Counterattack` sum inline | the same sum, through `attack_counterattack_damage` | the same expression, moved |
| `core.rs` (:1530-1548) | the new function only | — | — | no existing function changes |
| `mod.rs` (:34-35) | two `use` lines | — | — | — |

- **The function runs on every attack that damages the opposing Active**, not only into a defender with any retaliation
  (PLAN.md:37's wording). So the reading covers the zero case for all attacks; the row above does.
- **The root fact.** `CardEffect::Counterattack` is made only by the five attacks' text (`effect_mechanic_map.rs`:526-550 and
  :2537-2544), on the attacker's own Active (`apply_attack_action.rs`:3721-3754), or by a copy attack using one. No table,
  identity, coverage or panel list holds the eight ids or a copier (the inventory above).
- **Step 4's allowed file list** (PLAN.md:222, "exactly the 17 engine files") **and (f)'s list gain**
  `engine/src/actions/apply_action_helpers.rs`, `engine/src/hooks/counterattack.rs`, `engine/src/hooks/mod.rs` and
  `engine/tests/rules_repair_return_damage_weakness.rs`: 21 in all. `hooks/core.rs` is already listed.

### Open points (none changes a recorded game)

1. **For Dustin:** the readings above (Metal Defender, Swift) and the Bench. Bounded Field's is replaced by the plain reading, ×2
   (Oct 9).
2. **The hit back as attack damage, beyond Weakness.** P2 gives it only Weakness. The engine applies it as a plain `apply_damage`,
   so none of these touch it:
   - the Attacking Pokémon's own damage reductions, Disguise or full prevention;
   - Guts, Hala, Rescue Scarf or Lucky Egg when it Knocks the attacker Out;
   - the attacker's own Rocky Helmet or Rough Skin.

   Whether Pocket applies any of them is open. rules/02 section 4 says an Ability's return damage triggers none; for an attack's
   it isn't recorded. Spiritomb's Final Scream (B2 103), an on-Knock-Out Ability, stays flat.
3. **A holder that the same attack moves to the Bench or devolves** loses its `Counterattack` before the hit back, so nothing
   lands (a knock-back or devolving attack). This is existing behaviour, not P2's, and it hasn't been seen in a game.
4. **Other damage an attack leaves stays flat:** Galarian Stunfisk's Snapping Trap (B2 117: "this attack does 40 damage to the
   new Active Pokémon", `apply_action.rs`:1675) and the delayed damage effects (`hooks/core.rs`:441 and :496). They are outside
   P2's rule; Snapping Trap's wording is the nearest relative.
5. **main rules/02:60 has Rocky Helmet's roles swapped** ("a Fire Torchic hitting Metal Tinkatink"). TRIAGE.md :73 and :105 and
   the card types say Torchic held the Helmet and Tinkatink attacked. That is a one-line fix on main, outside this branch.
6. **For the go** (PLAN (a) and (e)):
   - coin_probe v2 needs a P2 condition. A bot's search sees Cursed Jewel's +20, so a brew-07 or brew-09 v t-altaria game can
     change in look-ahead before any hit back lands, and would read UNEXPLAINED. The smoke shows this is the usual case: all 3
     of its changed games changed in look-ahead.
   - (e) needs a P2 revert switch.
   - Neither is built here. **Both built Oct 9:** the probe's RETURN check (`../round2_readiness_2026-10-02/`, README section 3)
     and the off-switch (below).

### For the laptop

- **The counters:** `attack_return_weakness` (exact) and `offgate_return_by_source` {sources} (off the gate), in
  `../coin_prevention_repair_2026-09-30/instrument_scan.py`. The probe has 78 checks (49 before) and passes at P2.
- **The equivalence list** is above.
- **The files:** the four engine files named under "How" (`apply_action_helpers.rs`, `hooks/core.rs`, `hooks/counterattack.rs`,
  `hooks/mod.rs`) and the test file named under "Tests".

## Oct 9: P2's off-switch, P3 and the suite

The coordinator via Dustin, Oct 9 (decisions 12 and 14, and "the remaining 7 Fossil-as-Item places"): on this branch, tests
first, gates 1-2 as before.

### P2's off-switch

**In plain words**

- **P2 can now be turned off.** Off, the engine plays as it did before P2: an attack's hit back is flat again. On is the
  default, so every program built from this branch plays P2 unless asked otherwise.
- **Two ways to turn it off:**
  - for a whole program, the environment variable `DECKGYM_FLAT_RETURN_DAMAGE=1` (or `true`), read once, as
    `DECKGYM_UNBOUNDED_ENERGY_MOVES` is;
  - for one piece of code on one thread, `deckgym::actions::with_return_weakness(false, || ...)`. The setting comes back
    afterwards, even after a panic. This is what a revert check needs: one decision decided as the engine before P2 would.
- **What it is for:** the switch plan's precondition (e), the revert check.

**Commits**

- `14abfb0`: the 4 tests first. They don't compile without the switch (`tests_before_switch.log`).
- `35e6acf`: the switch, in `actions/apply_action_helpers.rs` (`handle_attack_retaliation` asks it before adding the +20),
  exported from `actions/mod.rs`. All 21 tests in `rules_repair_return_damage_weakness.rs` pass (`tests_after_switch.log`).
- `e51a151`: gates 1 and 2 (`switch_gates/`).

**Tests** (in `engine/tests/rules_repair_return_damage_weakness.rs`)

- `switch_off_each_attack_hits_back_flat_again`: the five attacks hit back flat again, and the Knock Out the +20 decided is gone.
- `switch_off_gives_the_engine_before_p2`: every other board P2 changes gives the number it gave before P2
  (`tests_before_fix_p2.log`).
- `switch_changes_nothing_where_p2_does_not_act`: an attacker not weak to the holder, Rocky Helmet, an Ability, a Benched
  attacker: the whole state is the same on and off.
- `switch_scoping`: on by default; an inner call wins for its length; the setting comes back after a return and after a
  panic; another thread keeps its own.

**Gates** (`switch_gates/run_switch_gates.sh`; output `switch_gates/run_output.txt`; every program built from `git archive`)

- **Gate 1, on (the default) is P2:**
  - P2's smoke, 200 games (`../round2_readiness_2026-10-02/counter_smoke_p2/`): byte for byte `games_p2_plain.jsonl`;
  - km3 v km3, 240 games of altaria v blaziken at seed 7100: game for game the official program's, and equal to the pinned
    record `5a18d31_10_cli_km3.txt` except its wall-time line;
  - the counter probe prints `counter_probe_readiness_output.txt` exactly (78 checks, 0 failures).
- **Gate 2, off is the engine before P2** (`d3739b7`):
  - the same 200 games: byte for byte `games_p_plain.jsonl`;
  - the same 240 games: equal again;
  - the probe prints `counter_probe_readiness_output_at_P.txt` exactly (78 checks, 11 failures: the 11 P2 rows);
  - **the revert check at the three games P2 changed** (all in look-ahead). At the first differing tick, the P2 head decides
    that one move with the switch off. The scores come from main's print-only `dg_patch.py`, applied to both engines
    (`switch_gates/revert_dumps/`).

    | Game | Before P2 | P2 | P2, switch off for that move | Every candidate's score as before P2 (within 1e-9) |
    |---|---|---|---|---|
    | pairing 0, deal 31, tick 44 (5 candidates) | Attach a Psychic Energy to the Active | Small Balloon | the same Attach | yes |
    | pairing 1, deal 21, tick 84 (9 candidates) | Retreat (Bench slot 1 comes in) | Attach a Psychic Energy to Bench slot 2 | Retreat | yes |
    | pairing 1, deal 8, tick 43 (8 candidates) | Place Darkrai | Sabrina | Place Darkrai | yes |

- **Order with P3.** P3 came after the switch, so from P3 on "off" is the engine before P2 with P3 in it. P3 changes only
  boards with a Fossil, and no replayed list holds one.
- **Step 4's allowed list** gains `actions/mod.rs` (the export): 22 files with P2.

### P3: a Fossil is an Item card at seven more places

**In plain words**

- **A Fossil's printed kind is Item** (rules/01, rules/04 §6; Dustin's Sail Fossil screenshot, Oct 2). The Item lock already
  reads it that way (the follow-up, `3090abb`). Seven more places look for "an Item card" and missed a Fossil. Now they find it:
  - Alolan Raticate's Scrounge-and-Scarf (A3 107): "Discard a random Item card from your opponent's hand";
  - Team Rocket's Thieving Machine (B4a 067): its effect, and whether it can be played (a discard pile holding only a Fossil
    now counts);
  - Arven (B2a 091, 108, 115) and Order Pad (B4 145): the Item card found on heads;
  - Rotom ex's Junk Spark (B4 055, 184, 202): 10 more for each Item card in your discard pile;
  - Pachirisu's Crackling Snap (B4 054, P-B 085): 20 more if the discarded top card is an Item;
  - Team Rocket's Slowpoke's Scavenge (B4a 025): a random Item card from your discard pile;
  - Raticate's Treasure Collecting (B4 130, 178, 221): every Item card in the top 4.
- **How.** One helper in `models/card.rs`: `TrainerType::is_printed_as` (a Fossil is printed as Item; every other kind matches
  only itself), and `Card::is_item`. Everything else about a Fossil stays as it was: a 40-HP Basic in play, can't retreat,
  placed rather than played. The mechanic maps keep `TrainerType::Item`. Chandelure's Past Friends shares Junk Spark's code but
  counts Supporters, and still counts only Supporters.
- **Which lists hold a Fossil: none in any replayed set.** Checked on main 1163ebb7 and on this branch: no list under
  `decks/` and none of the lists the pairing files name. In the whole repository two lists do, and neither is replayed:
  `engine/example_decks/donphan.txt` (2 Old Amber, an upstream example) and
  `rl/results/kt_carrier_census_2026-09-26/decks/c-dragonair_mega_rayquaza_ex.txt` (1 Skull Fossil).
- **So no recorded game changes.** Every change only widens a check to also accept a Fossil, so a game without one plays as
  before. The smoke confirms it (`p3_smoke/`): brew-04 (the only replayed list holding one of these cards, 2 Team Rocket's
  Slowpoke) and the Skull Fossil list, each v the 8 panel lists, km3, 40 deals, seeds 20,920,000,000 + pairing × 10,000 + i:
  640 of 640 games the same before and after P3.

**Commits**

- `c17e415`: 12 tests first (`engine/tests/rules_repair_trainers.rs`, names starting `fossil_`). 10 fail, and the 2 controls
  pass (Past Friends, and a Supporter on top of Crackling Snap's deck): `tests_before_fix_p3.log`.
- `140c0be`: P3. All 22 tests in the file pass (`tests_after_fix_p3.log`).

**Files.** 8 engine sites in 6 files:
- `models/card.rs`: the helper;
- `actions/apply_attack_action.rs`: Scrounge-and-Scarf, Scavenge, Junk Spark, Crackling Snap;
- `actions/apply_trainer_action.rs`: Thieving Machine's effect;
- `move_generation/move_generation_trainer.rs`: Thieving Machine's playability (not among the plan's seven; it must change
  with the effect);
- `actions/shared_mutations.rs`: Arven and Order Pad;
- `actions/apply_abilities_action.rs`: Treasure Collecting.

Step 4's allowed list gains `apply_trainer_action.rs`, `shared_mutations.rs`, `apply_abilities_action.rs` and `models/card.rs`;
the other two were already in it. The two map files the plan named (`effect_mechanic_map.rs`, `effect_ability_mechanic_map.rs`)
don't change. Each changed line keeps its file's own line endings.

**Open (none changes a recorded game)**

- The bots' own Junk Spark estimate (`players/value_functions.rs`:2385) still counts with `==`, so it reads 10 low for each
  Fossil in the discard pile. `players/` stays unchanged. No list holds both Rotom ex and a Fossil.
- Aside, existing behaviour: Treasure Collecting puts the cards in hand with no 10-card cap, unlike the deck searches.

### The suite at the final engine commit

`suite_final.log`, at `140c0be`: **2,072 passed, 0 failed, 0 ignored**, 102 targets. That is P2's 2,056 plus the 4 switch
tests and the 12 Fossil tests. The engine diff from the official engine (main-8626a35) is now 26 files: 17 in `engine/src/`
and 9 test files. Nothing in `players/`, `Cargo.lock` or `Cargo.toml` changed.

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
- P2: `tests_before_fix_p2.log`, `tests_after_fix_p2.log`, `suite_p2.log` (the full suite at `5543a4b`).
  - Its counters are in `../coin_prevention_repair_2026-09-30/instrument_scan.py`.
  - Its probe, inventory and smoke are in `../round2_readiness_2026-10-02/`.
- Oct 9: `tests_before_switch.log`, `tests_after_switch.log` (the off-switch); `switch_gates/` (its gates: `run_switch_gates.sh`,
  `run_output.txt`, `compare_simulate.py`, `score_dump_p2.rs`, the three simulate pages and `revert_dumps/`);
  `tests_before_fix_p3.log`, `tests_after_fix_p3.log` (P3); `p3_smoke/` (`pairs.tsv`, `run_p3_smoke.sh`, `run_output.txt`,
  `games_p3.jsonl`, which equals the run before P3 byte for byte); `suite_final.log` (the full suite at `140c0be`).
- `reach.py`, `reach_output.txt`: reach per card.
- `counter_probe_round2.rs`, `counter_probe_round2_output.txt`: the counters on constructed boards.
- `smoke/`: the smoke check.
  - `water_round2.txt`: the scratch deck of repaired attackers. `meowth_carefree.txt` and `fire_heatmor.txt` are the first round's scratch decks, copied.
  - `pairs.tsv`, `run_smoke.sh`, `run_output.txt`: the pairings, the run, and its output (the builds' sha256s and the three scan pages).
  - `games_r_plain.jsonl`, `games_round2_plain.jsonl`, `games_round2_watch.jsonl`: the games.
  - `compare.py`, `compare_output.txt`: the comparison.
- Changed outside this folder: `../coin_prevention_repair_2026-09-30/instrument_scan.py` (the counters), and the engine files named under "Commits".
