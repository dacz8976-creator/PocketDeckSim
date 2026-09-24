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
- Heavy Helmet with a changed Retreat Cost; and
- exact turn-limit timing.

The audit's bot-planning limits, latent omniscient export paths and other items not named above are not claimed fixed.
Rules1/rules2 verification results are in their historical records. Rules3 build and activation identity are recorded in the linked activation receipt.

## Replay follow-up, September 22

The accepted 225430 segment revealed that a zero-HP attacker was discarded before Destiny Burst finished. All on-KO effects in the simultaneous wave now finish while every member remains present, before point accounting and cleanup. A regression covers both seats, and the recorded segment checks both promotions. This change retains the earlier repairs and does not settle the open simultaneous-win or lethal Checkup-healing questions.
