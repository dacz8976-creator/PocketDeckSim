# 09 - Engine rules repairs, 2026-09-22

This ledger records verified rules1/rules2 repairs and the active rules3 repairs. The findings remain documented in
`07_engine_audit_2026-09-22.md`.

**Status (updated Sept 24): rules4 is active** as `deckgym 0.1.0-pdl.rules4` (executable SHA-256 `e6593ed816d0d5dbaf24fc8bc81a8317ed8069cda6ae7162c3d53e1fa7a12415`; it keeps every repair below and adds the T2 simultaneous-finish tie, see [the rules4 README](../rl/addon-0.7.2/rules4-repair-README.md)). The rest of this paragraph is the rules3 record: rules3 was active as `deckgym 0.1.0-pdl.rules3`. Its executable SHA-256 is `66acb493724ec189300ddaae6bd61de9a175d07677ad3df23da36414a3a922f2`; the active manifest and runtime match. Full engine suite: 1,823 passed, 0 failed. Replay corpus: 44 segments and 441 assertions passed. Replay tools: 48 Python/Rust tests passed. Four smoke games passed, two before activation with the actual binary and two after activation through the normal launcher. The [activation receipt](../Boss%20Folder/rules3-repairs-2026-09-22/validation/activation.json) and [rules3 repair report](../Boss%20Folder/rules3-repairs-2026-09-22/README.md) contain details. Project fixture checks had 32 passes and the same two preexisting failures (`driver_progress`, `run_records`). Historical RL wheels and training environments were not rebuilt.

## Main audit repairs

| Audit | Implemented repair |
|---|---|
| H1 - opening hand | Deal a random five-card hand. Only a hand with no Basic is repaired by swapping in a random Basic; extra Basics are no longer favored. |
| H2 - Heavy Helmet | Attack-only reductions apply only to an opponent's attack damage. Poison, Burn, Ability damage and the Tool owner's own damage bypass them. |
| M1 - Checkup Knock Outs | Poison, Burn and Checkup Ability effects finish before the Checkup Knock Out wave. Point-denial choices and promotion continuations pause and resume Checkup without starting the next turn early. |
| M2 - Clemont's Backpack | Its boost reaches damage to any opposing Pokémon, including the Bench, while Active-only boosts remain Active-only. |
| M3 - Glimmora and Dusknoir | Point-denial Abilities now resolve for non-attack Knock Outs too, before points and turn advancement, and respect Ability suppression. |
| M4 - retaliation Abilities | Retaliation uses the active Ability-mechanic path, respects Ability loss, includes the missing Iron Jugulis and Dragalge ex printings, and is staged after the attack's own effects. |
| M5 - Mythical Slab | Keeps a Psychic Pokémon of any stage and moves a non-Psychic top card to the bottom. |
| M6 - Stadium limit | Tracks one Stadium card play per turn separately from each player's once-per-turn Stadium effect use. |

## Rules3 repairs

- **R1 - Cubone, Clefable and Bonsly attack reductions:** the effect is carried by the opposing Active Pokémon whose attacks were reduced and subtracts from its attack damage before Weakness. It applies to that Pokémon's attacks against Active or Benched targets, and attack effects clear when it evolves or leaves the Active Spot.
- **R2/M7 - player-selected Energy discards:** retreat and Gouging Fire's Scorching Interruption / Walking Wake's Sweeping Billow now stage distinct physical Energy choices. The attack choices resolve after damage and before retaliation and Knock Outs.

These repairs are validated and active. Full details and preserved evidence are in the [rules3 repair record](../Boss%20Folder/rules3-repairs-2026-09-22/README.md).

## Other implemented repairs in this batch

- Damage calculation now applies attacker-side changes, then Weakness, then defender reductions. The unresolved
  zero-damage Weakness question remains outside this change.
- Double-Knock-Out promotion after an attack gives the turn player the first required promotion.
- Checkup processes the player whose turn ended first.
- Asleep, Paralyzed and Confused replace one another while Poison and Burn remain independent.
- Eevee's Boosted Evolution exception applies only to that Eevee and respects Ability suppression.
- Quick-Grow Extract and Wallace let the player choose the visible target before the engine randomly chooses an
  eligible deck evolution. Wallace uses maximum HP after bonuses.
- Lum Berry and Bad Dreams follow turn-owner order. Caterpie's Quick Growth resolves before Checkup.
- Protective Poncho checks the source owner and no longer blocks its owner's attacks.
- Pichu's Crackly Toss targets only Benched Basic Pokémon. Politoed and Weavile require the named prior evolution.
- Garchomp's Reckless Shearing and confirmed draw/search effects are blocked by a visibly empty deck.
- Hidden deck contents no longer suppress legal Trainer, Stadium, Pokémon Communication, Pokémon-search Ability or
  Tool-search Ability attempts. Visible prerequisites such as a hand card or board target still apply.
- Mesagoza, Kid's Room and Fragrant Forest follow the same hidden-deck rule; Arcade cannot draw from an empty deck.
- Potion, Erika, Marlon and Lillie offer only damaged eligible targets.
- Piers now discards two random attached Energy without replacement.

Focused regressions are grouped in `deckgym-fork-s193/tests/rules_repair_damage_opening.rs`,
`rules_repair_timing.rs`, `rules_repair_retaliation_timing.rs`, `rules_repair_end_turn.rs`, `rules_repair_status_evolution.rs` and `rules_repair_trainers.rs`, with narrow updates to
older card tests where the repaired action sequence changed.

Lethal Knock Back finishes its switch before the target is Knocked Out on the Bench, as confirmed by the [official Pocket FAQ](https://app-ptcgp.pokemon-support.com/hc/ja/articles/41083304332057). Perish Body rechecks its printed Active Spot requirement at that point; the location check follows the ruling and card text.

## Explicitly unresolved or outside this repair

These rules remain source questions and were not settled by the code work:

- the winner when a player's last Pokémon is Knocked Out in the exchange that gives that player a third point;
- whether Burn precedes a Checkup healing Ability (Poison before Blessed Salt is observed; Burn order remains inferred), although all Checkup Knock Outs now wait until Checkup effects finish;
- promotion order after a Checkup double Knock Out;
- what happens when a card effect returns a card to an already full hand;
- whether Weakness applies when an attack's damage has been reduced to zero before Weakness;
- Heavy Helmet with a changed Retreat Cost (settled since, 2026-09-25: it reads the current cost; the engine bug is
  listed under "Open engine bugs" below); and
- exact turn-limit timing.

The audit's bot-planning limits, latent omniscient export paths and other items not named above are not claimed fixed.
Rules1/rules2 verification results are in their historical records. Rules3 build and activation identity are recorded in the linked activation receipt.

## Replay follow-up, September 22

The accepted 225430 segment revealed that a zero-HP attacker was discarded before Destiny Burst finished. All on-KO effects in the simultaneous wave now finish while every member remains present, before point accounting and cleanup. A regression covers both seats, and the recorded segment checks both promotions. This change retains the earlier repairs and does not settle the open simultaneous-win or lethal Checkup-healing questions.

## Open engine bugs (not fixed yet)

- **Coin-flip damage cuts come off before Weakness** (found Sept 25, in the kd review). Guarded Grill (Bastiodon A2
  114, heads: −100) and Securely Sheltered (Hisuian Goodra B3b 050, heads: −80) are Abilities. The engine takes their
  cut off the attack's raw damage in the attack outcome (`AttackOutcomes::split_with_damage_prevention`,
  `engine/src/actions/attack_outcome.rs`), before `modify_damage` adds Weakness or applies Bounded Field. By the
  rules (`02_damage_knockouts_points.md`, step 4) coin-flip prevention is a defender-side effect and comes after
  Weakness; the repair above moved the fixed reductions there, but not this one. Example: Charmeleon's Fire Claws
  (60) into Bastiodon under Bounded Field, heads: the engine does (60 − 100) → 0, the rules 120 − 100 = 20. None of
  these cards are in the eight table decks. The kd bot prices the engine's current order on purpose. Its test
  `guarded_grill_under_bounded_field_pins_the_engines_current_order_coin_cut_before_weakness`
  (`engine/src/hooks/core.rs`) fails when this is fixed and names the matching one-line kd change. Fix the engine
  first; kd follows.
- **Coin-flip damage Abilities never flip for damage dealt through a queued choice** (found Sept 25, in the kd
  review). Carefree Steps, Celestial Blessing, Guarded Grill and Securely Sheltered read "If any damage is done to
  this Pokémon by attacks, flip a coin". The engine flips only for damage carried in the attack's outcome
  (`split_with_damage_prevention` skips entries of 0). Direct-damage attacks put 0 there and deliver their damage
  through a queued `ApplyDamage` choice, so they never trigger the coin. Verified for `DirectDamage` (Heatmor's Tongue
  Whip, an attack, into a benched Togekiss: always 30). Only attacks trigger these Abilities. Damage from an Ability
  (Darkrai ex's Nightmare Aura, Darkrai's Bad Dreams), a Tool or Checkup must never flip them, and the engine already
  gets that right: the coin is only set up in the attack path (`apply_attack_action.rs`). Keep it that way when
  fixing this. Several other attacks also deliver damage through `ApplyDamage` choices
  and are likely affected; check them when fixing. They include the functions `also_choice_bench_damage`,
  `optional_discard_benched_basic_for_extra_damage` (Chase Order),
  `discard_all_energy_of_type_then_damage_any_opponent_pokemon`, `damage_to_any_opponent_per_target_energy`,
  `self_discard_energy_then_damage_any_opponent_pokemon`, `switch_in_opponent_benched_then_damage` and
  `direct_damage_if_damaged` in `engine/src/actions/apply_attack_action.rs`. None of the coin Abilities are in the
  eight table decks. The kd bot mirrors the engine for the direct-damage group (`DirectDamage`,
  `DirectDamageAndSelfCardEffect`, `DirectDamageIfDamaged`). Its test
  `a_direct_damage_snipe_on_togekiss_pins_the_engines_current_behaviour_no_coin` (`engine/src/hooks/core.rs`)
  fails when this is fixed. For the other attacks kd still flips the coin, as the card text says, so kd and the
  engine disagree there until the engine is fixed. Fix the engine first; kd follows.
- **A 0-damage attack that targets the Active uses up Mimikyu ex's Disguise** (laptop's Altaria card check, 4b24b4b,
  `rl/results/altaria_card_check_2026-09-26/` on main; upheld 3 to 0). Sing, which does no damage, removes Disguise.
  Not reachable on the table. Fix with an identity replay.
- **Bad Dreams (Ability damage) is stopped by three "by attacks" protections** (same source; upheld 3 to 0).
  `PreventAllDamageAndEffects`, `PreventDamageFromBasic` (Darkrai is a Basic) and `PreventDamageIfLessOrEqual` read
  "damage from attacks" but also stop Darkrai's Bad Dreams. Not reachable on the table. Fix with an identity replay.

## Fixed Sept 26 (cloud branch `claude/pensive-ptolemy-spwc0b`; each its own commit, replays in `rl/results/rules09_fixes_2026-09-26/`)

- **"Discard all Energy from this Pokémon" never puts that Energy in the discard pile** (found Sept 25 in the laptop's
  recordings check, `rl/results/recordings_check_2026-09-25/` on main; confirmed in the code here). The attack effect
  `damage_and_discard_all_energy` (`engine/src/actions/apply_attack_action.rs`) clears the Active's Energy without
  adding it to `state.discard_energies`; the normal discard path does (`State::discard_from_active`). Affected
  attacks: Hyper Ray (Hydreigon), Thunderbolt (Raichu, Pikachu ex, Heliolisk), Luster Purge (Latios), Gaia Impact
  (Landorus), Sonic Impulse (Mega Latios ex) and Supreme Blast (Mesprit). Cards and code that read the pile then
  undercount it: Volkner, Lusamine, Professor Sada, Flame Patch, Combust, Dragon's Blessing, the bot's
  `discard_energy_credit` and kpr's projection. No deck in `decks/research`, `decks/dustin` or `decks/brews` has a
  combination that reads the pile after one of these attacks. Fixing it changes game states, so it needs an identity
  replay, and it waits until kpr's table is read.
  **Fixed in a30b5f8 (Sept 26).**
- **Two "random" Energy effects always take the last-attached Energy** (same source, confirmed in the code). Crawdaunt's
  Unruly Claw ("discard a random Energy from your opponent's Active Pokémon",
  `SimpleAction::DiscardRandomOpponentActiveEnergy`) and the Supporter Psychic ("move a random Energy",
  `SimpleAction::MoveRandomOpponentEnergyToActive` through `apply_move_last_energy`) use `.last()` in
  `engine/src/actions/apply_action.rs`, and treat the outcome as fixed, so the bots do too. Piers, which their comment
  cites, was already fixed to pick at random. It matters only when the Pokémon holds more than one Energy type: the
  table decks each use one type; Dustin's two-type decks (08, 11) are exposed to Crawdaunt on the ladder. The fix is a
  chance branch per distinct type held, weighted by count, and needs an identity replay after kpr's table is read.
  **Fixed in 3102c9e (Sept 26).**
- **Rare Candy ignores Aerodactyl ex's Primeval Law** (same source, confirmed in the code). "Your opponent can't play
  any Pokémon from their hand to evolve their Active Pokémon" is checked only in `can_evolve_at_position`
  (`engine/src/move_generation/mod.rs`); `can_play_rare_candy` (`move_generation_trainer.rs`) checks Malamar's
  Evolution Jammer but not Primeval Law, though the engine's own comment on Evolution Jammer says the same wording
  stops Rare Candy. **Confirmed in-game by Dustin, 2026-09-25** (video uploading to `Battle Logs`): Rare Candy can't
  be used on your Active while the opponent's Aerodactyl ex is in play, as for Evolution Jammer. No deck here
  has Aerodactyl ex; against one, the Rare Candy decks (research: Hydreigon, Blaziken, Suicune; Dustin's 01, 02, 05,
  06; brews 01, 03b, 05, 05b, 09) would get an illegal play. Fix after kpr's table is read.
  **Fixed in 14745ce (Sept 26).**
- **Heavy Helmet reads the printed Retreat Cost, not the current one — CONFIRMED in-game 2026-09-25** (Dustin's
  recording `Battle Logs/heavyhelmet_test.MP4`: printed Retreat Cost 3, Peculiar Plaza in play, Helmet attached, a
  40-damage attack did 40; the engine would have made it 20). "If the Pokémon this card is attached to has a Retreat
  Cost of 3 or more, it takes −20 damage from attacks" reads the current cost, like attacks that depend on it. The engine checks the printed cost (`heavy_helmet_reduction`,
  `engine/src/hooks/core.rs`), so it gives −20 under Peculiar Plaza at 1–2 and none when Ariados's Trap Territory or
  Goo-zooka raises a printed 2 to 3. No table deck has Heavy Helmet; Dustin's 01 and 03 do, his 12 has Ariados, and
  brews 05b and 10 play Plaza. The fix is to read the effective Retreat Cost the engine already computes for retreat
  (`get_retreat_cost_for_player`); it needs an identity replay, after kpr's table is read. Any scorer that prices Heavy
  Helmet (kd did; the kt draft would) follows the engine until then and changes with it.
  **Fixed in 050cf51 (Sept 26)**, through `get_board_retreat_cost_at`, the board's cost where the holder sits: on the
  Bench without the modifiers that name the Active (Trap Territory, Sky Support, the typed Bench discounts).
- **Legendary Pulse draws after Hiking Trail instead of before — CONFIRMED in-game 2026-09-25** (Dustin's
  `Battle Logs/pulse_hikingtrail_order.MP4`). At the end of the Suicune ex player's turn with Hiking Trail in play,
  Legendary Pulse ("At the end of your turn, if this Pokémon is in the Active Spot, draw a card") draws first and Hiking
  Trail then tops the hand up to 3: the player ends on 3 cards. The engine queues Pulse's draw
  (`on_end_turn`, `engine/src/hooks/core.rs`: a `DrawCard` frame pushed for the ending player) while Hiking Trail draws
  at once in the same function, and the queued draw resolves only after the Checkup and the turn change (under the
  next player's own turn draw): the player ends on 4. It is the only end-of-turn draw the engine queues; checked
  Sept 25: `EndTurnDrawCardIfActive` is Legendary Pulse on all 13 printings of Entei ex, Suicune ex and Raikou ex, and no
  other end-of-turn effect in `on_end_turn` draws. **Table impact:** the Suicune v Blaziken cell (Blaziken's list runs
  Hiking Trail) and Dustin's Hiking Trail decks 06, 10 and 12. Fix: draw Pulse's card at once, before Hiking Trail, in
  `on_end_turn`. It needs an identity replay, after kpr's table is read.
  **Fixed in 5b75bf9 (Sept 26).**
- **The A2b 111 printing of Poké Ball can be played with an empty deck** (found by the laptop's Trainer audit,
  2026-09-25; confirmed in the code). Poké Ball "Put a random Basic Pokémon from your deck into your hand" is blocked
  with an empty deck only for P-A 005 (`can_play_poke_ball`, `engine/src/move_generation/move_generation_trainer.rs`);
  A2b 111 is in the always-playable list in the same file. `rules/04` (the "Blocked because it's visibly impossible"
  list) says both are blocked. No deck in `decks/research`, `decks/dustin` or `decks/brews` uses A2b 111. Fix: route
  both printings to `can_play_poke_ball`; identity replay after kpr's table is read.
  **Fixed in 3c2250f (Sept 26).**
- **After an end-of-turn or Checkup knockout, the next player drew before the knocked-out player promoted**
  (laptop's Altaria card check, 4b24b4b; confirmed on footage 07aafa3, `promotion_timing.json`: 4 of 4 recorded
  knockouts, Poison, Bad Dreams and two Burns, promote before the next turn's banner and draw). The engine advanced the
  turn (draw, Energy, start-of-turn Abilities) with the promotion frame still below. A FinishPokemonCheckup frame now
  goes below the promotion, as point denial already did, so the turn advances after it. It reaches table games.
  **Fixed in 5bab907 (Sept 26).**
