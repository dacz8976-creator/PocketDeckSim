# Review of the kt draft spec (Fable, Sept 26, adversarial)

Reviewed: `rl/results/tool_turn_effect_census_2026-09-25/README.md` on `origin/claude/pensive-ptolemy-spwc0b` at aa87fa3 (spec revised in c002d2f). Read against the engine on that branch (`engine/src/hooks/core.rs`, `players/value_functions.rs`, `players/mod.rs`, `hooks/counterattack.rs`, `effects.rs`, `state/mod.rs`), the Trainer audit (`rl/results/trainer_audit_2026-09-25/`), the Skarmory finding (`rl/results/skarmory_tool_jasmine_2026-09-25/`), the kd readout on the branch, and the plan (`rl/RUN5.md` "revised Sept 25"; `docs/REVIEW_2026-09-24_direction.md` lines 130-131 for the reserve route). Nothing was checked out; branch files were read with `git show`. Scripts: `scratchpad/reviews/kt_review_branch*.sh`, `kt_cards.sh`.

**In plain words.** The spec is sound in its aim and most of its facts, but it is not ready to register. Three things need fixing first: (1) it says Metal Core Barrier is already handled by kd's damage function, and it is not; (2) it says the Tool values are symmetric for the opponent's Tools, and for two Tool classes they cannot be, which will change how Field Blower is played against Hydreigon and Weezing; (3) it never says which adoption route switch 1 takes, and the route the plan pre-registered for table-invisible changes cannot be satisfied by the test the spec names (Dustin's decks). On card-agnosticism: no line is a card patch in the plan's sense, but three rows (Poncho, Elegant Cape, the reduction Tools) are written as card descriptions where a generic engine hook exists, and if built as written they become card-keyed evaluator code.

## What survived checking

- Every census number I recomputed matches `kp3_census.txt`: Field Blower 5,911 offered / 1,763 played; 1,414 removals from the opponent's Active; Small Balloon 225 of 501 (Espeon 93 + Mega Altaria ex 67 + Igglybuff 65; Igglybuff's Retreat Cost is 0, Espeon and Mega Altaria ex are Stage 1 per `lib/card.py`); Poncho 427 of 428 on the Active; the laptop's 492 of 494.
- The "Where Dustin's decks have them" list: all 16 card placements verified against `decks/dustin/*.txt`.
- The effect types exist with the stated semantics: `TurnEffect::ReducedDamageForTarget { scope, only_from_ex }` (Jasmine `NamedPokemon`, Cheren `only_from_ex`), `ReducedDamageForType`, `CardEffect::ReducedDamage`, `ReducedDamageFromEx` (`effects.rs` 9, 103, 121-156). Metal Core Barrier discards at the end of the opponent's turn (`core.rs` 504-519). Heavy Helmet reads the printed cost (`core.rs` 703-711). `get_counterattack_damage` is generic (`counterattack.rs` 13-36). `get_effective_total_hp` gates Leaf and Elegant Cape by holder (`played_card.rs` 290-310).
- kd was not adopted (kd README on the branch: ΔMSE +14.2, Lucario piloted worse −2.2 ±1.4), so building kt on kp is consistent.

## Findings

### 1. Metal Core Barrier is not in `persistent_defender_damage` (high)

Spec line 61: "reduction Tools on the victim, through the Tool stages kd's `persistent_defender_damage` already runs: Metal Core Barrier (−50 ...), Steel Apron, Heavy Helmet". The branch's function sums only `heavy_helmet_reduction` and `steel_apron_reduction` (`core.rs` 1682-1684) and its doc says "Left out ... Metal Core Barrier (it discards itself at the end of the opponent's turn); turn effects" (1601-1604; on main 1577-1580, 1613-1615). The Barrier has its own index-based function `get_metal_core_barrier_reduction(state, target_player, target_idx)` (715-735). The Skarmory README item 1 says the same. Both Tool helpers are private (`fn`, not `pub(crate)`), so the evaluator cannot call "the Tool stages" without either calling the whole function, which also applies Weakness and the Ability cuts the spec says are not taken over, or exposing the helpers. The formula for the −50 is therefore not fixed by reference. Fix: name the hook calls (a `temporary_defender_reduction` in `hooks/core.rs`, kept equal to `modify_damage` by a test, as kd did).

### 2. "Symmetric" is false for the opponent's retreat Tools and Deceptive Needle (high)

The score's retreat term is own-side only: `(-my.active_retreat_cost) * params.active_retreat_cost` (`value_functions.rs` 556); the spec itself defers "the opponent's Retreat Cost" to later. Deceptive Needle's only read is the own-side EndTurn forecast inside the search (census.json, Needle row; kp has no opponent ply). So under kt the opponent's Balloon, Boat and Needle are worth 0, and Field Blower on them scores −1. In the census, the opponent's Active Needle is the single most frequent Blower target (453 of 1,414 Active removals; first in 5 of 6 Blower decks), Balloon 93, Boat 64. Under kp3 those plays scored +10. Prediction the spec should carry: Field Blower stops answering the Needle; Hydreigon and Weezing gain on the table; Hydreigon is already the largest miss above Limitless. The spec's "Field Blower is played only where the removed Tool did something for its holder" is wrong: it will also stop where the Tool did something the evaluator cannot see.

### 3. Switch 1's adoption route is unresolved and clause (d) cannot be met by the named test (high)

The plan's reserve route (direction doc line 130, (a)-(e)) requires, for a table-invisible change, "a gain beyond paired noise on at least one Limitless top-30 archetype that is not Dustin's deck and carries the relevant cards", explicitly so that "a route judged only on his decks would [not] over several fixes build a pilot specifically good at his decks"; and "if the card census finds no [such] archetype ... the route is closed for that candidate and adoption can come only by Dustin's explicit override ... not loosened after the census is seen". Line 131 then says kt's footprint will exceed 15% (through switch 2), so "the ordinary adoption rule applies and the no-harm route is not needed". The spec follows that: switch 1's test is "Dustin's decks: 07, 05, 11, 01 and 03". Net effect: the one switch the table cannot see is adopted or rejected on evidence produced by the other two, and the pre-registered requirement is never applied. None of B2e's six held-out archetypes (09, 13, 04, 08, 12, brew-08's base) carries a reduction Tool or turn-effect card (those are in 01, 03, 05, 07 only). The registration must say which of these holds: kt adopts as one unit on the table (then record that switch 1 rides in untested and why that is acceptable), or switch 1's single-switch code is read under the reserve route with a named Limitless carrier list and its source, or switch 1 is adoptable only by Dustin's override.

### 4. The every-hit arithmetic for Steel Apron and Heavy Helmet has no formula (medium)

Spec line 64: "Steel Apron and Heavy Helmet stay attached, so they count on every hit against their holder." kp's clock uses one `max_damage` for every victim (`value_functions.rs` 966-1004); `ko_turns_after_first_attack(hp, first, max_damage)` (1345-1351) covers the first hit only; per-victim later-hit damage is kd's `(first, later)` structure (`KdPricer::hits`, 1259-1276), which the spec says is not taken over. The earlier draft's open choice 2 recommended next-attack only; the revision chose every hit without recording who decided. Write the formula before registration.

### 5. The switches are separable as flags, not as effects (medium)

Each switch can have its own `EvalFeatures` flag and code (the structure exists: `EvalFeatures` 256-297, `parse_player_code` 216-260). But the effects interact: with the +10 gone (switch 2), Barrier and Apron are played only if switch 1 credits them (the Skarmory causal test: +10 at 0 takes the Barrier from 74.6% to 1.5% and deck 07 from 132 to 97 wins of 240); Rocky Helmet is played only if switch 3 covers the card (the spec says so). A switch-2-only code will read as a Skarmory regression and a Blaziken regression that are not bugs. Pre-register that single-switch codes are diagnostics and name the expected interactions. Naming hazard: `strip_prefix("kt")` then a depth parse means diagnostic codes `kt1`/`kt2`/`kt3` would parse as kt at depth 1/2/3; name them now with non-digit suffixes.

### 6. Poison Barb in switch 3 needs the Special Conditions model the spec defers (medium)

"The expected Poison damage to the attacker, per Checkup until it leaves the Active" needs a Poison-tick and Active-tenure model; the spec lists Special Conditions under "Not in this candidate". Detection is generic (`should_poison_attacker`, `counterattack.rs` 117-124, covers Barb and `PoisonAttackerOnDamaged`), the price is not. Barb is in no table deck (brew-03a, dustin/10 only). Drop it; switch 3 becomes `get_counterattack_damage` alone, which is card-agnostic (Rocky Helmet, Spike Armor, `CounterattackDamage` abilities; none of the latter in the eight lists). Also fix the formula: the number of hits the threat lands on the holder is the other clock's KO count, so switch 3 couples the two clocks; say so.

### 7. Card-agnosticism: three rows are card descriptions where a hook exists (medium)

- **Protective Poncho.** The branch's `persistent_defender_damage` already returns (0, 0) for a Benched hit when the defender has Poncho or `PreventDamageWhileBenched` (Shell Shield) (`core.rs` 1625-1630), and kd's `only_damages_the_bench` (`value_functions.rs` 2390) finds bench-only attacks. The spec's rule ("the damage it prevents from the opponent's Bench-hitting attacks and Abilities on its next turn, up to the holder's HP") is a new term with no formula (which attacks, which Abilities, sum or max) that re-implements what the hook gates. Write it as "the threat's bench-only attacks priced on each benched Pokémon through the engine's Benched-hit modifier".
- **Elegant Cape.** `evolution_potential` prices the evolved form at printed `t.hp` (1977), without the holder's Tools, so "discounted as `evolution_potential` discounts it" is not what the function does; built literally it is `has_tool(ElegantCape) && stage == 1`, a card branch. Generic: carry `attached_tools` onto the evolved form and read `get_effective_total_hp()`, which handles Giant, Leaf, Elegant Cape and the Ancient Capsule by holder in one rule.
- **Reduction Tools.** The engine's reductions are CardId-keyed helpers; "never on card names" holds only if the evaluator calls the hooks rather than listing three Tools (finding 1).
Verdict: no line is a card patch in B5's sense (no rule names a card to force a play), but built as written these three become card-keyed evaluator code. Phrase each as a hook call in the registration commit.

### 8. Retreat Tools become a knowing under-pricing with a veto exposure (medium)

Weights: `active_retreat_cost` 1.0, `hand_size` 1.0 (`value_functions.rs` 50, 48), so an eligible Balloon or Boat on the Active nets 0 and move order decides. The census skeptic for Small Balloon says the term under-prices a later retreat ("an Energy actually kept would be worth the holder's remaining HP and online score"). Suicune plays Boat on 60% of offered turns, Altaria Balloon on 88%; the spec predicts "played less" with no basis that less is better. Under rule v2 a Suicune or Altaria own-side drop beyond noise on mixed rows is a veto. Pre-register the predicted direction for both rows.

### 9. Small points (low)

- Timing: kq's `first_attack_turn` runs only when the threat is the Active (`_threat_slot == 0`, 960); switch 1 needs the first-attack turn for any threat slot. Turn effects are stored per absolute turn (`turn_effects: BTreeMap<u8, ..>`, `add_turn_effect` writes turn_count..turn_count+duration; `get_turn_effects(turn)` exists), but `get_turn_effect_damage_reduction` (`core.rs` 1189) reads the current turn only; it needs a turn parameter to be reused.
- `heavyhelmet_test.MP4` is not in the repo (Battle Logs); cite `rules/05` #19 instead.
- Lucky Egg at 0 means it is never played under kt (deck 02 only); record as accepted.
- The census tool lists Stiffen by attack title (`REDUCTION_ATTACKS`); fine for a census, not a rule.

## Questions for the laptop and Dustin

1. Does kt adopt as one unit on the table, or does switch 1 get its own reserve-route reading with a named carrier list (finding 3)?
2. Who chose every-hit for Apron and Helmet, and what is its formula (finding 4)?
3. Will the registration express each Tool row as an engine-hook call (findings 1, 7)?
4. Diagnostic code names, fixed now with non-digit suffixes (finding 5)?
5. Poison Barb deferred with Special Conditions (finding 6)?
6. Is the Field Blower / Needle asymmetry accepted as a pre-registered prediction, or does the spec need a term for the opponent's unread Tools (finding 2)?
