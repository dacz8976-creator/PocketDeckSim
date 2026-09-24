# core_damage_status — shared damage / KO / Special Condition / end-of-turn / Checkup machinery

Scope: `src/hooks/core.rs`, `src/hooks/counterattack.rs`, `src/actions/attack_outcome.rs`,
`src/actions/apply_action_helpers.rs`, `src/state/played_card.rs`, `src/state/mod.rs`, `src/effects.rs`.
Rules read in full: `rules/02_damage_knockouts_points.md`, `rules/03_status_checkup_timing.md`.

## Findings

### CDS-1 [High] Pokémon Checkup Knocks Out per-condition instead of at the end of the whole Checkup — breaks Checkup-healing Abilities (VERIFIED-RUN)
- Rule: "Any Pokémon that has no HP remaining **at the end of Pokémon Checkup** is Knocked Out." [OFFICIAL] — `rules/03_status_checkup_timing.md` §5 step 4: "Knock Outs wait until the whole Checkup is done, and a heal during the same Checkup (Blessed Salt) can save a Pokémon that Poison/Burn took to 0."
- Engine: `src/actions/apply_action_helpers.rs` `apply_pokemon_checkup` (lines 237–324) applies Poison (247–261) and Burn (264–287) damage via `handle_damage(...)` (line 487–505: `handle_damage_only` **then** `handle_knockouts`), not the KO-deferring `handle_damage_only`. So each poisoned/burned Pokémon is individually discarded — points awarded, promotion queued — *inside* the same loop, **before** `apply_blessed_salt_checkup_healing` (Garganacl's "During Pokémon Checkup, heal 10 damage from each of your Pokémon", called at line 315, after all the damage loops) ever runs, and before Sleep/Paralysis are even processed for that Checkup.
- Probe (`tests/zz_core_damage_status_checkup_ko_order.rs`): player 0 board = Bulbasaur (Poisoned, exactly 10 remaining HP) + Garganacl (Blessed Salt) on Bench; opponent = Bulbasaur. `EndTurn` for player 0:
  ```
  BEFORE: p0 active remaining_hp=Some(10), points=[0, 0]
  AFTER: p0 slot0=Some(("Garganacl", 150)) slot1=None, points=[0, 1], current_player=1
  ```
  The poisoned Bulbasaur is discarded, the opponent scores the point, and Garganacl is promoted — all before Blessed Salt's heal has a chance to save it (it should have ended the Checkup at 10 − 10 + 10 = 10 HP, still in play, no points, no promotion).
- Impact: any deck that pairs Poison/Burn pressure against a Checkup-healer (Garganacl's Blessed Salt; presumably any future "heal during Checkup" ability) gets the KO/points/promotion the instant that one Pokémon's tick lands, not after the healer's own Checkup ability runs. Also a more general architectural issue: Checkup KOs, points and promotions resolve incrementally per-Pokémon-per-condition rather than atomically after all of Poison→Burn→Sleep→Paralysis (+ Checkup Abilities) have applied to both players' boards, which is what "not part of either player's turn" / "at the end of Pokémon Checkup" implies.

### CDS-2 [High] Heavy Helmet reduces non-attack damage (Poison/Burn ticks, Ability damage, retaliation) — should only reduce damage from attacks (VERIFIED-RUN)
- Card text: Heavy Helmet (B1 219) — "If the Pokémon this card is attached to has a Retreat Cost of 3 or more, it takes **-20 damage from attacks** from your opponent's Pokémon." (`src/database.rs:48733`)
- Rule: "Damage from Abilities and Special Conditions is not 'damage from an attack': effects that reduce or prevent attack damage ('-20 from attacks' Tools) do nothing against poison ticks, ability pings or Rocky Helmet." [OFFICIAL, Mimikyu ex FAQ] — `rules/02_damage_knockouts_points.md` §4; also RULES_FOR_AGENTS.md.
- Engine: `get_heavy_helmet_reduction(state, (target_player, target_idx))` in `src/hooks/core.rs:682-695` takes **no `is_from_active_attack` parameter at all** and unconditionally applies its -20 whenever the tool + retreat-cost condition hold. Contrast with its siblings in the same `finite_damage_reductions` list, which correctly gate on it: `get_metal_core_barrier_reduction` (`core.rs:697-717`, `if !is_from_active_attack { return 0; }`) and `get_steel_apron_reduction` (`core.rs:719-740`, same guard).
- Probe (`tests/zz_core_damage_status_heavy_helmet_nonattack.rs`): Blastoise (retreat cost 3) holding Heavy Helmet, Poisoned, one Checkup tick:
  ```
  BEFORE: Blastoise remaining_hp=150
  AFTER 1 Poison Checkup tick: Blastoise remaining_hp=Some(150) (should be 140 ...)
  RESULT: BUG -- Heavy Helmet reduced/blocked non-attack (Poison) damage.
  ```
  Poison's 10 damage is fully negated (10 − 20 saturates to 0). By the same code path Burn's 20 would also be fully negated, and any Ability-damage ping (Water Shuriken, Snowy Terrain, on-KO retaliation like Destiny Burst) landing on a Heavy-Helmet holder with Retreat Cost ≥3 is reduced by 20 as well.
- Impact: any deck running Heavy Helmet on a heavy-retreat-cost wall becomes wrongly immune to Poison and Burn ticks entirely (not just reduced), and takes reduced Ability/retaliation damage. This is a common, simulated Tool, so this changes outcomes broadly whenever it faces a status or Ability-damage deck.

### CDS-3 [Medium] Clemont's Backpack's Bench bonus never applies — the engine restricts *all* `IncreasedDamageForSpecificPokemon` boosts to the Active target, even ones worded "your opponent's Pokémon" (VERIFIED-RUN)
- Rule: "Attacker-side boosts apply to whatever targets their text names. '+X damage to your opponent's **Active** Pokémon' ... does not add to Bench hits; '+X damage to your opponent's **Pokémon**' (Clemont's Backpack) **does**." [OBSERVED ×4] — `rules/02_damage_knockouts_points.md` §3; this exact card is the checklist's named counter-example.
- Card text: Clemont's Backpack (B1a 066) — "During this turn, attacks used by your Magneton or Heliolisk do +20 damage to **your opponent's Pokémon**." (`src/database.rs:52730`, no "Active"). Compare Blaine/Cynthia/Hau/Sophocles, which use the same `TurnEffect::IncreasedDamageForSpecificPokemon` variant but all say "...Active Pokémon" (`src/actions/apply_trainer_action.rs:981,996,1007,1717` — all "Active").
- Engine: `get_increased_turn_effect_modifiers` (`src/hooks/core.rs:1007-1080`) starts with `if !is_active_to_active { return 0; }` (line 1015-1017), so **every** `TurnEffect::Increased*` variant — including Clemont's Backpack's — contributes 0 to any Bench-target damage calculation, regardless of whether the source card's text says "Active Pokémon" or just "Pokémon". Only Clemont's Backpack (`clemonts_backpack_effect`, `apply_trainer_action.rs:2358-2367`) is wrongly swept in by this blanket gate; every other user of the same `TurnEffect` variant is correctly Active-only by its own wording, so the fix must special-case Clemont's Backpack rather than removing the gate.
- Probe (`tests/zz_core_damage_status_clemont_backpack_bench.rs`): Heliolisk (Electrispark: 40 to Active + 10 to each Benched) + Clemont's Backpack played first, vs. opponent Active + 1 Benched Pokémon:
  ```
  BEFORE attack: opponent bench remaining_hp=70
  AFTER attack: ... bench_damage_taken=10 (expected 30 ...)
  RESULT: BUG -- Clemont's Backpack's bonus did not apply to the Bench hit.
  ```
- Impact: Magneton/Heliolisk decks running Clemont's Backpack (matches the rules doc's own Electrispark/trial-manectric observation) undercount Bench damage by 20 per hit.

### CDS-4 [Low] Rocky Helmet-style Tool retaliation fires before the attack's own post-damage effects, not after (VERIFIED-READ)
- Rule: observed order after an attack's damage: "attack damage → the attack's own effects (Burn, Energy discard) → Tool retaliation (Rocky Helmet 20) → on-KO Ability (Destiny Burst 70) → Knock Outs, points, promotion." [OBSERVED, twice in the same battle] — `rules/02_damage_knockouts_points.md` §5.
- Engine: `handle_damage_only` (`src/actions/apply_action_helpers.rs:509-618`) applies the target's damage **and** the Rocky Helmet-style counterattack (`get_counterattack_damage`, lines 574-608) together, per target, inside one loop. `AttackOutcome::into_mutation` (`src/actions/attack_outcome.rs:133-167`) calls `handle_damage_only` first (line ~144), then runs `post_damage_effect` — the attack's own additional effects (status, Energy discard, etc.) — afterward (lines 156-158), and only then `handle_knockouts` (line 164, which is where on-KO Abilities like Destiny Burst fire, via `on_knockout`/`apply_knockout_retaliation` in `core.rs:1973-2064`). So the engine's actual order is: damage → **Rocky Helmet retaliation** → the attack's own effects → on-KO Ability → Knock Outs — Rocky Helmet and the attack's own effects are swapped relative to the documented order.
- What is correctly implemented (verified while tracing this): retaliation only fires on attack damage and only while Active (`is_from_active_attack && target_pokemon_idx == 0` gate, line 576), and it fires even when its holder was Knocked Out by the same hit (the code doesn't check `is_knocked_out()` before applying counter-damage) — both match the rules.
- Impact: unclear how often this changes final board state (most attack-own-effects and Rocky Helmet's target-the-attacker damage don't interact), which is why this is rated Low rather than Medium; flagging because it's a real, clean code-order inversion and could matter for an attack whose own effect reads the attacker's just-modified HP, or for cards keying off "damaged by an attack this turn" ordering.

## Rules questions (real rule unknown or text ambiguous)
None beyond what `05_open_questions.md` already tracks; nothing new surfaced in this area.

## Checked and OK
- Damage order bug (#1 in "Already known"): confirmed still present, unchanged, at `hooks/core.rs:1705-1719` (`saturating_sub` reductions, then Weakness applied after) — not re-reported.
- Known bug #7 ("Asleep/Paralyzed/Confused don't replace each other"): confirmed still present, unchanged — `played_card.rs` `set_status_raw` (411-424) and `state/mod.rs` `apply_status_condition` (1125-1177) have no mutual-exclusion logic. Directly relevant to checklist item 5's "confirm the 2026-09-10 fix is present": the *attack/retreat-blocking* half of that fix **is** present (see below), but the *mutual-exclusivity* half is not — not re-reported since already listed, but flagging that the fix is only partial.
- Weakness: Active-only (never Bench), gated on `is_active_to_active` (`get_weakness_application`, `core.rs:1418-1459`).
- Weakness not applied when the attack's own (pre-modifier) damage is 0 (`modify_damage` early return, `core.rs:1519-1522`).
- Bounded Field: Weakness ×2 for non-Mega-ex attackers only (`core.rs:1448-1454`, checks `is_mega() && is_ex()`).
- "Isn't affected by Weakness" (Hitmonchan ex) vs. "isn't affected by any effects on opponent's Active" (Morgrem/Mega Medicham ex) vs. both combined (Ledian Swift) are three distinct, correctly-scoped string constants and skip exactly the right steps (`core.rs:1210-1233,1404-1416`).
- Damage never below 0 (`saturating_sub` throughout, `u32`).
- Multiple boosts/reductions from different sources add up; same-name passive Abilities stack (loop over all in-play Pokémon in `get_board_ability_damage_bonus`, `core.rs:1754-1806`).
- Non-attack damage (Poison/Burn Checkup ticks, Ability pings, on-KO retaliation) is dealt with `is_from_active_attack: false`, which correctly disables Weakness, attacker-side boosts, "-X from attacks" Tool/Ability/turn-effect reductions (`get_turn_effect_damage_reduction`, `get_ability_damage_reduction`, `get_metal_core_barrier_reduction`, `get_steel_apron_reduction`, `get_reduced_card_effect_modifiers` — all gate on it), Safeguard (`PreventAllDamageFromEx`), Shell Shield, and Disguise/`PreventFirstAttack` (`checkapply_prevent_first_attack`, `apply_action_helpers.rs:422-449`) — **except Heavy Helmet (CDS-2)**.
- Rocky Helmet-style retaliation doesn't chain into itself/another Rocky Helmet (applied via raw `apply_damage`, not routed back through `handle_damage_only`).
- The three prevention wordings are modeled as genuinely different mechanisms: damage-only prevention lives entirely in `modify_damage`; effects-only/both-prevention (Crystal Body, Clear Veil, Shinx's Hide) go through the separate `prevents_attack_effects` chokepoint (`state/mod.rs:670-695`) that `apply_attack_status_condition` and other effect-appliers call, and which explicitly does *not* touch damage.
- `PreventDamageIfLessOrEqual` (Cascoon's Harden-style threshold) is checked against `final_damage` — i.e. **after** Weakness — matching the rules doc's inferred ordering (`core.rs:1722-1728`).
- Attack's own effects still run after lethal damage (`post_damage_effect` runs unconditionally in `into_mutation` regardless of any HP reaching 0 during `handle_damage_only`; Knock Outs are deferred to the very end via `handle_knockouts`).
- Special Conditions: immunity (`ImmuneToStatusConditions`/Fabled Luster, Steel Apron, SoothingWind/Comfey/Ogerpon) blocks application entirely, no cure needed (`state/mod.rs:1125-1177`).
- Poison: 10 base, +10 per opposing Nihilego (Active only), Toxic/Severe Poison's custom Checkup amount correctly replaces the old one on reapplication (`get_poison_damage`, `apply_action_helpers.rs:166-203`; `set_status_raw` resets `poison_checkup_damage` on every fresh Poisoned, `played_card.rs:415-420`; `inflict_poison_with_custom_checkup_damage_attack`, `apply_attack_action.rs:2496-2510`).
- Burn: 20 dealt, then coin flip; heads cures but can't retroactively save a Pokémon the 20 already KO'd (`apply_pokemon_checkup`, `apply_action_helpers.rs:264-287`).
- Asleep: coin flip at every Checkup (no owner-turn restriction), so it can wake before its own turn (`collect_checkup_targets`/`apply_pokemon_checkup` sleep handling).
- Paralyzed: only checked (and cured) at the Checkup where `player == state.current_player` (the player whose turn just ended) — correctly costs the victim exactly one full turn (`collect_checkup_targets`, `apply_action_helpers.rs:219-222`).
- Asleep and Paralyzed both block Attack and Retreat generation via the shared `special_condition_blocks_attack_or_retreat` gate (`hooks/retreat.rs:32-34`, used by `move_generation/attacks.rs:23-25` and `can_retreat`) — **confirms the 2026-09-10 fix is present** for this part.
- Confused does not block retreat (only Asleep/Paralyzed do, per the same gate).
- Moving to the Bench or evolving clears all Special Conditions and stored `CardEffect`s (`clear_status_and_effects`; called from retreat/switch paths in `apply_action.rs:929,1197` and from `apply_evolve`, which builds a brand-new `PlayedCard` via `to_playable_card`).
- Evolution keeps damage counters, attached Energy, Tools, and `cards_behind`, and clears status/effects (`apply_evolve`, `apply_action.rs:1460-1499`).
- HP bonuses (Giant/Leaf/Elegant Cape, Starting Plains) raise both max and remaining HP by the same amount, computed live in `get_effective_total_hp` (`played_card.rs:289-310`), so removal is reflected immediately with no stale cache.
- Removing an HP bonus triggers an immediate catch-all Knock Out check after every action (`apply_common_action_suffix`, `apply_action_helpers.rs:1003-1018`) — a single pass at the end of the action, unlike the broken per-condition Checkup path (CDS-1).
- Healing is capped at max HP (`heal_pokemon`/`heal_raw` use `saturating_sub` on damage counters, can't go negative, `state/mod.rs:858-868`; `played_card.rs:227-229`).
- Points: every Knock Out in a "wave" (simultaneous or sequential within one `handle_knockouts` pass) scores independently, so multiple Checkup KOs or a double KO both award points correctly (`handle_knockouts`, `apply_action_helpers.rs:650-843`) — known bug #3 (double-KO promotion by seat rather than attacker-first) is unchanged and not re-reported.
- Player-wide `TurnEffect`s (e.g. Blue's "-10 to all your Pokémon during opponent's next turn") are stored on `State`, not on the granting Pokémon's `PlayedCard`, so they persist even if that Pokémon leaves play; duration-based expiry (`add_turn_effect` duration + `end_turn_maintenance`) is unrelated to board presence.

## Not fully verified given time budget
- Did not exhaustively trace every retreat/switch code path (Cyrus, Sabrina-style forced switches, etc.) for `clear_status_and_effects` — spot-checked two call sites plus the generic `Activate`/evolve paths; no discrepancy found.
- Did not verify "your opponent's last turn" memory (Wobbuffet's Reply Strongly-style flags) survives the Checkup in every edge case, only that the shift happens in `end_turn_maintenance`.
- CDS-1's downstream interaction with other same-Checkup Abilities (e.g., whether a Pokémon promoted mid-Checkup by an early Poison KO could see or be seen by a not-yet-processed "During Pokémon Checkup" Ability later in the same Checkup) was not chased further; the core bug (Checkup healing arriving too late to save a Poison/Burn KO) is demonstrated directly.
