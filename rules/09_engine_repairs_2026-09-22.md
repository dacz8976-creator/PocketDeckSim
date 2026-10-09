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
| M3 - Glimmora and Dusknoir | Point-denial Abilities now resolve for non-attack Knock Outs too, before points and turn advancement, and respect Ability suppression. Matches the game for a Poison Knock Out with heads [OBSERVED 200857, Sept 29; `08` T11]; Burn and tails not seen. |
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
- Eevee's Boosted Evolution exception applies only to that Eevee and respects Ability suppression. Matches the game
  [OBSERVED 194920, Sept 29: Benched Rattata refused "Unable to evolve" on the first turn with that Eevee Active;
  Rattata was also played that turn, see `04` §4].
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
- whether Burn precedes a Checkup healing Ability (settled since: Poison, then Burn and its coin, then Blessed Salt, observed in 010316 T15, `rules/03`), although all Checkup Knock Outs now wait until Checkup effects finish;
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

- **Two knockout-promotion bugs fixed upstream, not in the fork** (found Sept 29 in upstream 09e964f, "Expose public agent observations and fix stale knockout promotions"; `../rl/results/b4b_prep_2026-09-26/B4B_REPRINT_CHECK_2026-09-29.md`). **Neither is to be ported at the next upstream merge.** Fix 2 is not taken (Dustin, Sept 30). Fix 1's case is already covered in the fork (F8, Oct 1), so there is nothing to port; F8 did not audit every path (both below).
  1. **Promotion into an emptied slot** (upstream `apply_action_helpers.rs`, `handle_knockouts`; test `tests/hp_aura_promotion_test.rs`). A knockout removes an HP bonus, the only one being Lilligant's "Each of your [G] Pokémon gets +20 HP.", which knocks out a damaged Benched Pokémon after promotion choices were already queued. Promoting that emptied slot could leave the Active Spot empty.
     - **Covered in the fork (F8, Oct 1).** Upstream's test, ported, passes on d363ba8. Knockouts resolve in waves (`engine/src/actions/apply_action_helpers.rs:690-820`), with a nested pass after them (`:836-847`), before any promotion is built (`:906`), so the second knockout falls before the promotion choices exist. Either guard alone covers the case; only with both removed does the fork fail as upstream did. The fork's `prune_stale_bench_activate_choices` (`:1032`) is not what covers it, and fix 1 ported as written would do nothing here: it filters `Activate` choices, and the fork promotes with its own `Promote` move. F8's limits: the fork has no general clean-up of stale `Promote` choices, and F8 did not audit every other path. Source: `rl/results/engine_switch_rules_2026-10/f8/F8.md` (the cloud, 5a929c0, on `claude/pensive-ptolemy-spwc0b`).
  2. **Lethal knock-back asked for two promotions** (upstream `apply_attack_action.rs`, `knock_back_attack` and `coin_flip_knock_back_opponent_active`; test `tests/knock_back_knockout_test.rs`). When the hit knocks out the opponent's Active, the switch choice was still queued on top of the promotion, so the opponent chose a new Active twice.
     - It affects Hariyama's Push Out, Grapploct's Knock Back, Houndour's and Yamper's Roar, Throh's Circle Throw, and Chinchou's Luring Glow.
     - The fork's `knock_back_attack` (`engine/src/actions/apply_attack_action.rs:4952`) has no lethal check.
     - **Not taken** (Dustin, Sept 30, the rules switch's question 10). It contradicts the official JP ruling the fork follows: a Pokémon moved to the Bench by a lethal Knock Back is Knocked Out on the Bench (`06_sources.md:124`; "Lethal Knock Back finishes its switch" above). It would also break `rules_repair_retaliation_timing.rs:136`.

- **What the Oct 1 rules switch left open: bugs against the plain card text, for the next rules switch.** The switch (main-8626a35) fixed the parts under "Fixed Oct 1" below; these remain. Dustin's rule (Oct 1, `../rl/RUN5.md`): "if there is a plain reading of the text, the engine build should go with that, unless there is contradicting evidence. Not the other way around". So each case is built on its card's plain text, and none waits for footage. Line numbers are at main-8626a35, whose `engine/` is the candidate 5a18d31's.
  1. **Some attacks still never flip a coin-flip damage Ability.** Carefree Steps, Celestial Blessing, Guarded Grill and Securely Sheltered read "If any damage is done to this Pokémon by attacks, flip a coin". These attacks still queue their damage as a plain `ApplyDamage` choice, which never flips it:
     - **Gyarados's Wild Swing**, whenever it can discard a Benched [W] Pokémon, with or without the discard. `discard_then_damage_choice` (`engine/src/actions/apply_attack_action.rs:311`) takes the coin path only for Chase Order. The game flips [OBSERVED 213822 T6, 150-154, Oct 1: Wild Swing into Meowth, Carefree Steps' coin, tails, 100 damage; DUSTIN: "Coin still applies. It is an attack"]. Pinned today by `wild_swing_into_carefree_steps_pins_todays_behaviour_no_coin` (`engine/tests/pokemon/meowth_carefree_steps_test.rs:390`).
     - **Six other sites, seven attacks** (`../rl/results/coin_prevention_repair_2026-09-30/HELPERS.md`, "Found outside the seven"): Wellspring Mask Ogerpon's Wellspring Dance on heads (`coin_flip_also_choice_bench_damage`), Rapid Strike Urshifu's Tornado Shot (`self_discard_energy_and_choice_bench_damage`), Blastoise's Double Splash and Mega Blastoise ex's Triple Bombardment (`conditional_bench_damage_attack`), Mega Kangaskhan ex's second punch (`mega_kangaskhan_ex_double_punching_family`), Hoopa's Mischievous Ring (`shuffle_opponent_tools_into_deck_before_damage`) and Slowking's Litter (`forecast_discard_own_cards_for_attack_damage`, in `apply_action.rs`).
     - **The own-Bench form of `also_choice_bench_damage`** (Zapdos's Raging Thunder, Emolga A4 072, Luxray's Flash Impact). The hit on the opponent's Active is queued together with the hit on your own Bench, as one `ApplyDamage`. It has been left out so far because moving that choice to the coin path would drop a Guts coin (Ursaluna) on your own Bench.
     - **A copied Chase Order's discard branch.** The coin path needs the attacker's Active to print Chase Order (`chase_order_attack`, `apply_attack_action.rs:329`), so a Pokémon that uses it through a copy attack keeps the old path.
     - The cloud's branch `claude/coin-prevention-round2` (76b87cd, then 78af4e8; suite 2,027 passed; no independent audit yet) drafts Wild Swing and the six other sites on this switch's gated path. It leaves the own-Bench form and the copy as they are.
     - No list under `decks/` holds one of these Abilities. Of the attackers named here, only Gyarados is in a list (the panel ladder's l-sharpedo).
  2. **Victory Star with CoinFlipToBlockAttack** (on the attacker, from an attack such as "If the Defending Pokémon tries to use an attack, your opponent flips a coin. If tails, that attack doesn't happen."). No Victory Star is offered at all, not even on the attack's own coins after that coin lets the attack through: `victory_star_waits_for_confusion_heads` (`apply_attack_action.rs:117-132`) excludes the case, and `try_forecast_victory_star_attack` (`apply_action.rs:185`) then keeps the old path. Victory Star reads "after you flip any coins for an attack of 1 of your [R] Pokémon, you may ignore all results of those coin flips and begin flipping those coins again". The switch kept this case on the old path "until seen in the game"; by Dustin's rule it is built on that text instead: like the Confusion coin (`04` §9), the block coin is not one of the attack's own coins. It is flipped first, and Victory Star is offered on the attack's own coins if the attack goes ahead.
  3. **Victory Star with Confusion and a pending Will.** The game offers Victory Star on the attack's own coins after a Confusion heads with Will pending [OBSERVED 210403 T14, 354-355, Oct 1]. The engine offers nothing: the Will carve-out (`apply_attack_action.rs:131`) keeps the old path. Pinned by `confusion_with_will_pending_keeps_the_legacy_resolution_without_a_victory_star_offer` (`engine/tests/b4a_attack_batch2_test.rs:437`); Victini's card-status caveat (`engine/src/card_validation.rs:97`) still calls the case unverified.
  4. **Will is wasted on a Confused attacker.** Will reads "The next time you flip any number of coins for the effect of an attack, Ability, or Trainer card after using this card on this turn, the first coin flip will definitely be heads." The Confusion check is none of those, so Will waits for the attack's own first coin, and the game does exactly that [OBSERVED 210403 T14: the Confusion coin "Heads!" at 342.0-342.75, then Will's banner on Heat Charged's own coin screen at 347.25-347.95, and 3 heads at 352; DUSTIN: "Will does not apply on a re-roll or on confusion. It does apply on an attack after the confusion coin flip"]. The engine drops the coin record behind the Confusion coin (`prepend_nullifying_coin_gate`, `engine/src/actions/attack_outcome.rs:590-604`), so Will finds no coin to force (`outcomes.rs:489-491`; `apply_action.rs:675-688`), isn't used, and lapses at the end of the turn. This happens with or without Victini; it is older behaviour that the switch didn't touch. Fix it together with item 3: Will forces the attack's first coin, and a Victory Star reroll stays a fresh flip with no second Confusion check.
  5. **Two Ariados count as one.** Trap Territory reads "Your opponent's Active Pokémon's Retreat Cost is 1 more." on each Ariados, so two add 2 (same-name passive Abilities stack, `04` §5). The engine adds one Colorless for any number of them (`engine/src/hooks/retreat.rs:251-262`, the `break` at 260). The same capped cost feeds retreat, Heavy Helmet and attacks that count the Retreat Cost. In 213034 (T5, 117-124, Oct 1) Grass Knot did 160 to a Team Rocket's Moltres ex with two Ariados on the attacker's Bench: 40 + 30 × (printed 2 + 1 + 1), the only reading that fits (arithmetic, not a shown breakdown); the engine would deal 130. Every Ariados test uses one Ariados. Exposed: Dustin's deck 12 (two Ariados). Fix it with a two-Ariados test. It is outside the switch.
  - Sources: `../rl/results/rules_recordings_2026-10-01/READOUT.md` (§3b and §4); `../rl/results/engine_switch_rules_2026-10/PLAN.md` ("Known limits", repair A's "Still to do"); `../rl/results/engine_switch_rules_2026-10/README.md` (Dustin's rule on card text).

- **A hit back left by an attack ignores the Attacking Pokémon's own cards (found Oct 9; outside rules switch 2, for the next rules round).** The five "During your opponent's next turn, if this Pokémon is damaged by an attack, do X damage to the Attacking Pokémon" attacks (Cursed Jewel, Spike Armor, Bristling Spikes, Needle Lariat, Shell Trap) hit back with damage the game counts as damage from an attack for the attacker's own cut: Heavy Helmet cut Togedemaru's Bristling Spikes hit back from 30 to 10 [OBSERVED 20261009_223237000, Oct 9, a Solo rules test: Wailmer, Retreat Cost 3, Helmet attached; control in the same game, Spikes' own attack did 10 to it (03:05-03:10); after Wave Splash the Helmet glowed and the hit back showed 10 (03:32.5), Wailmer 90 to 80; no healing, evolution, retreat or Stadium in between; Shot List, captured Oct 9]. The engine applies every hit back as plain damage (`handle_attack_retaliation`, `engine/src/actions/apply_action_helpers.rs`:614-633, outside `modify_damage`), so no cut applies, today and after switch 2, which adds only Weakness (`02` §2). By Dustin's card-text rule the same reading extends, each by its own wording, to the attacker's Disguise, Guts, Rescue Scarf, Lucky Egg and Rocky Helmet (`../rl/results/coin_prevention_round2_2026-10-01/P2_EVIDENCE_sonnet.md`, question 10); only Heavy Helmet is seen. The release package records that no list we play reaches it.

## Fixed Oct 1 (the rules switch, main-8626a35; plan and evidence in `rl/results/engine_switch_rules_2026-10/`; what stays open is the entry above)

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
  **Fixed in main-8626a35 (Oct 1; repair B, the fix 5942d1a).** The heads cut now comes off in step 4, after the
  attacker's bonuses and Weakness, with the other defender-side effects (`modify_damage`, `engine/src/hooks/core.rs`). By
  that order the example above gives 120 − 100 = 20. kd followed in the same switch (F1, 160a9d4): its test is now
  `guarded_grill_under_bounded_field_comes_off_after_weakness`.
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
  **Fixed in main-8626a35 (Oct 1; repair B, 5942d1a, with Chase Order's e52a73b) for these seven helper functions
  and Chase Order** (Part 1's census counted the first two as one helper, the `DirectDamage` group, so it said six):
  `direct_damage` and `direct_damage_and_self_card_effect` (Heatmor's Tongue Whip now flips), `direct_damage_if_damaged`,
  `discard_all_energy_of_type_then_damage_any_opponent_pokemon`, `damage_to_any_opponent_per_target_energy`,
  `self_discard_energy_then_damage_any_opponent_pokemon` and `switch_in_opponent_benched_then_damage` (the damage to the
  Pokémon switched in); and Chase Order (`optional_discard_benched_basic_for_extra_damage`), with and without its
  discard. A queued choice aimed at a Pokémon with one of these Abilities now resolves as the attack's own damage
  (`ApplyQueuedAttackDamage`), so the coin flips; with no coin-Ability Pokémon among the possible targets, the choice is
  queued exactly as before. Ability, Tool and
  Checkup damage still never flip. kd followed (F1, 160a9d4): its test is now
  `a_direct_damage_snipe_on_togekiss_flips_celestial_blessing`. Seen in Pocket on Oct 2 [OBSERVED 20261002_161342000,
  86-94 s; Codex/Sol review, Astra checked; DUSTIN]: Heatmor's Tongue Whip at a Benched Meowth (50 HP) brought up Carefree
  Steps' coin, which landed heads, and Meowth took no damage. Still open (the entry above): Wild Swing,
  `also_choice_bench_damage`'s own-Bench form, six other sites (seven attacks) and a copied Chase Order's discard
  branch. Sources:
  `../rl/results/coin_prevention_repair_2026-09-30/HELPERS.md` (the census) and
  `../rl/results/engine_switch_rules_2026-10/EQUIVALENCE_sonnet.md` §2 (rows 12-22).
- **Victory Star is never offered while the attacker is Confused — the game offers it on the attack's coins
  after a Confusion heads. CONFIRMED in-game 2026-09-29** (Sol reviews with lead checks,
  `Battle Logs/Recording_QA/20260929_202314000_iOS_rule_sol/` and `20260929_203025000_iOS_rule_sol/`; summary
  `Battle Logs/Recording_QA/VICTORY_STAR_CONFUSION_2026-09-29.md`; rule in `04` §9). In the game the Confusion coin
  comes first and is never offered for a reroll; on tails the attack does nothing (202314, twice); on heads the
  attack's own coins are flipped and Victory Star is offered on them (203025: Confused Team Rocket's Moltres ex's Heat
  Charged flipped 1 heads 2 tails, Victory Star was taken, the three coins rerolled, no second Confusion check). The
  engine skips Victory Star entirely for a Confused attacker: `try_forecast_victory_star_attack`
  (`engine/src/actions/apply_action.rs` ~195–202) returns `None` whenever `has_unverified_attacker_coin_gate`
  (`engine/src/actions/apply_attack_action.rs` ~92–108) is true, and its comment says it is waiting for this
  evidence. Fix: flip the Confusion coin first; on heads, offer Victory Star on the attack's own coins as usual; never
  on the Confusion coin. The same gate also covers `CoinFlipToBlockAttack`, which these recordings don't test; leave
  that part gated until it is seen. A name search of `decks/` finds Victini only in a brew scorecard, not in a deck
  list. Failing test first; identity replay after the fix.
  **Fixed in main-8626a35 (Oct 1; repair A: the tests 265ce95 and d4fbc2a, 4d026a5's line-ending fix, the fix 6415e39)** for a
  Confused attacker whose attack flips coins: the Confusion coin comes first and is never offered; on tails the attack
  does nothing and nothing is offered; on heads Victory Star is offered on the attack's own coins, with no second
  Confusion check (`victory_star_waits_for_confusion_heads`, `engine/src/actions/apply_attack_action.rs:117`). Seen a
  third time on Oct 1, the first time with a 0-heads original [OBSERVED 204634 T4, 184-205]. F2 (d479f01) rewrote
  Victini's card-status caveat to match. Still open (the entry above): CoinFlipToBlockAttack and a pending Will, which
  this switch kept on the old path; both are now plain-text bugs.

## Fixed Sept 26 (cloud branch `claude/pensive-ptolemy-spwc0b`; each its own commit, replays in `rl/results/rules09_fixes_2026-09-26/`; the laptop's repair list items 1 to 10)

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
- **A 0-damage attack that targets the Active used up Mimikyu ex's Disguise** (laptop's Altaria card check, 4b24b4b;
  upheld 3 to 0). Sing does no damage, so it doesn't "first damage" the Pokémon. The zero-damage skip now comes
  before the Disguise check in `handle_damage`. **Fixed in 02fe9de (Sept 26).** Not seen in-game and left open on card text:
  `08` T14 (Dustin, Sept 29: "almost positive" Sing doesn't trigger Disguise; hard to replicate, no test planned).
- **Bad Dreams (Ability damage) was stopped by three "by attacks" protections** (same source; upheld 3 to 0): Hide
  (`PreventAllDamageAndEffects`), Blocking Shell (`PreventDamageFromBasic`) and Harden (`PreventDamageIfLessOrEqual`).
  They now gate on `is_from_active_attack`, as Safeguard and Shell Shield do. **Fixed in 53cba79 (Sept 26).**
  Matches the game for Harden [OBSERVED 204425, Sept 29; `08` T13]: Water Shuriken did the full 20 to Harden
  Cascoon (110 → 90), and the same Harden blocked Ice Wing's 40 that turn. Hide and Blocking Shell not tested.
- **Clemont's Backpack's +20 applied to non-attack damage and to its owner's Pokémon** (laptop's Raticate/Manectric
  card check, `rl/results/raticate_manectric_card_check_2026-09-26/`; upheld 3 to 0): a Poisoned or Burned Heliolisk
  took +20 at Checkup. "Attacks used by your Magneton or Heliolisk do +20 damage to your opponent's Pokémon": the
  bonus now needs an attack's damage to the opponent's Pokémon (Benched ones still count). **Fixed in 213c090
  (Sept 26).**
- **Roar in Unison was offered under Binding Snow's lock** (same source). Using it attached nothing and spent the
  Ability; Ice Maker was already gated. The three Abilities that only attach from the Zone to their holder now need
  `can_attach_energy_from_zone` for their spot. **Fixed in 4407c55 (Sept 26).**
- **Clemont from a 10-card hand reached 11 cards** (same source): searches had no hand cap. The multi-card Trainer
  search (Clemont, Serena, Cabbie, Juliana) now puts only as many of its random cards into the hand as fit, chosen at
  random; the rest stay in the deck, as for a draw past 10. **Fixed in e935f42 (Sept 26).**
