# Eval14 source bindings and probe recommendation

Source reviewed read-only: `/home/dacz8976/.codex/visualizations/2026/09/05/01a0730b-bcce-7423-ac18-e3e069a0d887/rocket-frenzy-followup-20260907/source`.

`SOURCE_HASHES.sha256` records the exact bytes of every cited source and test file. The aggregate SHA-256 of the sorted per-file hashes for `src/` plus `tests/` was `95f1722688f7a71096f3a52de3b88fa5b5d7ebbe65bdf4185637021dc84642b8` at review time.

## Card and mechanic bindings

- `src/database.rs:72538`, `:73377`, and `:73493` define the three Mega Sableye ex reprints (`B3b 041`, `B3b 081`, `B3b 088`) with the same 170 HP, Cursed Jewel base 80, Darkness+Colorless cost, and exact delayed 40-damage text.
- `src/database.rs:80304` defines the video-visible Gabite as `B4a 053`: 80 HP Dragon, no Weakness, Water+Fighting Linear Attack.
- `src/database.rs:77357` defines Rainbow Cave as `B4 155`. Its Energy-Zone replacement effect does not alter attack damage.
- `src/actions/effect_mechanic_map.rs:544` maps the exact Cursed Jewel text to deterministic `Mechanic::DamageAndCardEffect { opponent: false, effect: CardEffect::Counterattack { amount: 40 }, duration: 1, coin_flip: false }`.
- `src/actions/apply_attack_action.rs:720` dispatches that mechanic, and `:3460` applies its effect to the attacker's Active after the damage. `src/actions/attack_outcome.rs:131` fixes the general order as pre-effect, damage/counterattacks, post-effect, then knockouts. This matches the footage's 80 hit, delayed-effect announcement, then point.
- `src/state/played_card.rs:340` documents duration 1 as the opponent's next turn; `:448` decrements/removes stored effects during turn maintenance.
- `src/hooks/counterattack.rs:13` adds stored `CardEffect::Counterattack` values. `src/actions/apply_action_helpers.rs:539` applies positive damage first, then at `:571` triggers counterattack only for damage from an Active attack to the Active, and at `:589` damages the attacking Active. `:659` resolves knockouts/points; `:798` sets a points winner before promotions and explicitly allows an attacker to lose to counterattack KO.
- `src/models/card.rs:204` awards one point for ordinary Gabite. The observed score therefore advances from 2 to 3.

## Existing meaningful controls

`tests/pokemon/alolan_sandslash_spike_armor_test.rs` exercises the same exact 40-damage effect-text mapping through an actual attack: one test arms it, ends the turn, and verifies 40 damage to the next attacker; another verifies expiry after the opponent's next turn. `tests/mechanics/attack_effects_test.rs` verifies a Rocky Helmet counterattack can knock out an attacker, award points, and still resolve a queued post-attack effect before promotion. These are strong shared-pipeline controls.

There is no test naming Cursed Jewel or any Mega Sableye ex ID. The existing controls also do not combine this attack-driven duration-1 effect with a counterattack that supplies the terminal point, nor do they reproduce the video's terminal direct-attack path.

## Conservative terminal-certificate boundary

The public immediate-reply certifier deliberately does not forecast Cursed Jewel. `src/players/public_reply.rs:453` admits effect-free fixed damage, typed self-Energy discard, and Hit and Hide only; every other `DamageAndCardEffect`, including Cursed Jewel, returns `UnsupportedAttackMechanic`. If a `Counterattack` effect is already stored on the board, `src/players/public_reply.rs:601` rejects it as `UnsupportedHook`. This is a conservative false negative, not a missing generic attack forecast and not evidence that a position is safe.

## Minimal composite probe

Use the ordinary `Game::apply_action`/`try_forecast_action` path and parameterize the database-equivalent Sableye IDs `[B3b041MegaSableyeEx, B3b081MegaSableyeEx, B3b088MegaSableyeEx]`.

1. **Video-bound terminal attack.** Put Sableye Active for player 1 with payable Energy, `B4a053Gabite` Active for player 0 at 60 HP, no player-0 Bench, `B4155RainbowCave` in play, points `[1, 2]`, and turn 10/player 1. Apply Cursed Jewel. Assert one deterministic branch; Gabite is removed; points are `[1, 3]`; winner is `Win(1)`; Sableye remains 170; no promotion/forced choice is queued. Optionally assert the self `Counterattack { amount: 40 }` was installed before terminal resolution, without treating it as having fired.
2. **Synthetic delayed-retaliation control, clearly separate from the video.** Start the Sableye player at 2 points. Have Cursed Jewel hit a pre-damaged, payable Mewtwo ex at 120 remaining HP, leaving 40. End Sableye's turn, then have Mewtwo ex damage the still-Active Sableye. Assert Sableye takes the attack damage, Mewtwo ex takes exactly 40 and is knocked out, the Sableye player receives the ex points and wins, and no promotion is queued when the attacker has no Bench. This covers effect creation, duration, damage trigger, counter-KO, points, and terminal short-circuit in one action-driven path.

Meaningful negative controls:

- Give Sableye both the armed counterattack and full attack-damage prevention; an incoming attack reduced/prevented to zero must not damage the attacker because `handle_damage_only` exits before the trigger.
- Let the opponent's next turn pass without an attack and verify a later attack does not trigger 40. The existing Spike Armor expiry test already supplies shared-mechanic coverage; a Cursed Jewel-specific version is useful only if exact-card regression coverage is desired.
- From a public observation in which a terminal Cursed Jewel attack is legal, assert the generic forecast reaches the win while `assess_observation` abstains with an unsupported attack mechanic. This prevents widening the audited certificate registry by accident.

No source edits, Rust compilation, or test execution were performed for this review.
