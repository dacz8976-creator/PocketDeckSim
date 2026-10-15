# Source review: 20261002_161342000_iOS.MP4

**Current status: lead-accepted rule_test_review_complete; original archived unchanged in `Reviewed`. Excluded from Ladder Log.**

All available footage, 0.00 to 227.676667 seconds, was reviewed. The filmed bench snipe triggers Meowth's Carefree Steps, heads prevents Tongue Whip's 30 damage, and Meowth remains at 50 HP. This concludes the owner-requested rules test. The recording later shows a computer-battle Victory, 3-1, at turn 15. Both split files are excluded from Pause Games and Ladder Log.

## Source binding and method

Frozen SOURCE.json and ASSIGNMENT.json were read before decoding, after root confirmed completed intake. SHA256: `3db01a8db2f4229fd3327591a6012fe38da60e16fa47e71d0875c866bfbfd475`; 417877242 bytes. The shared overview uses a four-second interval and two decode threads. All seven sheets, 57 sampled frames, were inspected. Native frames establish attack text, selected targets, named coin context, HP before/after, Auto change and final result. Times are local to this file; phase bounds below are approximate.

## Full available timeline

| Local time | Observed phase and meaningful actions |
| --- | --- |
| 0-33s | Continuation of owner turn 7. Entei ex retreats, spending its two attached Fire Energy, and Heatmor 100 HP becomes active and receives Fire Energy. Tongue Whip targets benched Combusken 20 HP for 30, knocking it out and taking the owner to one point. Meowth is active and cannot be chosen in this Bench-only prompt. |
| 33-43s | Opponent turn 8: Cyndaquil 60 HP benched. Active Meowth uses Feelin' Fine to draw, with no damage to Heatmor. |
| 43-58s | Owner turn 9: Magby inspected but not played. Heatmor's Tongue Whip targets benched Victini 70 HP, dealing 30 and leaving 40 HP. Active Meowth stays at 50 HP; no Meowth defense coin belongs to this attack. |
| 58-81s | Opponent turn 10: Cyndaquil evolves into Quilava 80 HP, Meowth retreats to the Bench and a Torchic 60 HP is benched. Quilava uses Heat Wave for 30 and Burn, taking Heatmor from 100 to 70 HP. Checkup deals another 20 to 50 HP; a tails recovery coin leaves Heatmor Burned. |
| 81-105s | Owner turn 11: Heatmor targets benched Meowth 50 HP with Tongue Whip. Carefree Steps triggers, its coin is heads and a shield prevents all 30 damage. Meowth remains 50 HP. Subsequent Burn checkup takes Heatmor from 50 to 30 HP; recovery text follows. |
| 105-130s | Owner Auto changes from off to on between native 105.00 and 106.00s. Opponent turn 12: Quilava evolves into Typhlosion ex 180 HP, Torchic into Combusken 80 HP. Destructive Inferno deals 110 and flips one heads then tails for its Energy-discard effect. Heatmor 30 HP is knocked out, tying points 1-1. The replacement prompt contains Entei ex 70 HP and Houndour 60 HP; Houndour becomes active. |
| 130-166s | Owner turn 13 under Auto: empty-deck notice; Houndour evolves into Mega Houndoom ex, 190 printed HP plus Elegant Cape's 30 for 220 HP. Flame Patch and Energy attachments prepare the attack. New Heatmor 80 HP with Rocky Helmet and a second Entei ex 140 HP are benched. Grim Hound Flare produces two heads and one tails, dealing 160 to Typhlosion ex and leaving 20 HP. |
| 166-193s | Opponent turn 14: Combusken evolves into Mega Blaziken ex 210 HP; Typhlosion ex retreats to the Bench. Mega Burning deals 120 plus Burn to Mega Houndoom ex, taking 220 to 100 HP. Checkup deals 20 to 80 HP; heads recovers Burn. Rocky Helmet is attached to benched Heatmor and does not damage Mega Blaziken ex. |
| 193-227.676667s | Owner turn 15 under Auto: empty-deck notice; Cyrus brings damaged benched Typhlosion ex 20 HP active. Fire Energy added to benched Heatmor. Grim Hound Flare gives one heads and two tails, deals 80 and knocks out Typhlosion ex. Two points produce the 3-1 Victory. Terminal results name the computer deck, first player, 15 turns and 360 damage. |

## Decisive bench-snipe evidence

| Native timestamp | Direct observation |
| --- | --- |
| [19.00s](evidence/t0019.00.jpg) | Heatmor attack text: Tongue Whip costs one Fire Energy and does 30 damage to one opponent Benched Pokémon. |
| [86.00s](evidence/t0086.00.jpg) | Bench target prompt: Meowth 50 HP at upper left, Torchic 60 HP and Victini 40 HP on the Bench; Quilava 80 HP active. Meowth is the selected defender in the ensuing sequence. Heatmor is active at 50 HP. |
| [87.00s](evidence/t0087.00.jpg) | Named `Ability Carefree Steps` banner and Meowth glow. |
| [89.00s](evidence/t0089.00.jpg) | Coin prompt repeats the attack-damage prevention text: flip if attacks damage this Pokémon; heads prevents that damage. |
| [91.00s](evidence/t0091.00.jpg) | Explicit `Heads!` result. |
| [92.00s](evidence/t0092.00.jpg) | Tongue Whip attack banner and 30-damage Bench attack text. |
| [94.00s](evidence/t0094.00.jpg) | Shield surrounds benched Meowth. Its HP remains 50; other Bench HP remains Torchic 60 and Victini 40. No 30 damage is applied to Meowth. |

The causal observation is attack damage from Heatmor invoking a defensive Ability on Meowth. It is not damage dealt by an Ability. Victory Star is a different Fire-attack coin-reroll Ability on Victini; no Victory Star banner or reroll appears in this Carefree Steps sequence. Tongue Whip has no inherent coin in its displayed attack text. Burn recovery coins and later attack-effect coins have separate visible contexts.

Normal Tongue Whip damage is also established: [Combusken target prompt](evidence/t0023.00.jpg) and [Combusken at zero HP](evidence/t0027.00.jpg) show 20 to 0 after the 30-damage attack; [Victini target prompt](evidence/t0053.00.jpg) and [30 damage to Victini](evidence/t0056.00.jpg) show 70 to 40. Meowth is active during both controls, so they do not test its defensive Ability.

## Cut and continuity

The last frame of part 1 (206.80s) and first frame of part 2 (0.00s) show the same public board at owner turn 7: owner Entei ex 70 HP active with two Fire Energy and Lum Berry, Heatmor 100 HP with Giant Cape and Houndour 60 HP with Elegant Cape on the Bench; opponent Meowth 50 HP active with one Fire Energy, Combusken 20 HP with two Fire Energy and Victini 70 HP on the Bench; Rainbow Cave and a 0-0 score. Both show Dacz8976 and phone time 11:13. This supports the owner testimony that these are two parts of one battle. The visible hand differs, so no unseen draw or action is reconstructed. The recording cut is real; its duration and intervening actions are not established. All timestamps stay local to each file.

This packet's start evidence is [0.00s](evidence/t0000.00.jpg). Counterpart: [part 1 review](C:/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/20261002_161001000_iOS_rule_sol/REVIEW.md); source hash `6fd7b61e49ad599261696438f83d07da2512c790a33f5a63517dd7e558b77c30`. The public-board match supports one battle, while the missing interval prevents any claim of an uninterrupted recording.

## Mode, Auto and result

At [105.00s](evidence/t0105.00.jpg), Auto remains off; at [106.00s](evidence/t0106.00.jpg), it is checked on. It stays on through the concluding owner turns. This establishes the owner's toggle only, not a separately displayed opponent toggle.

At [221.00s](evidence/t0221.00.jpg), Victory appears. At [227.60s](evidence/t0227.60.jpg), results identify `vs. Mega Blaziken ex & Typhlosion ex Deck (Deluxe Pack: Mega)`, say the owner went first, and show 15 turns, 3 owner points, 1 opponent point and 360 damage. This directly supports computer mode and the terminal win. Recorded owner attack damage across both sources reconciles as 60 + 30 + 30 + 0 + 160 + 80 = 360.

## Comparison and limits

The owner-provided engine description predicts no defense coin and unconditional 30 damage for this queued Tongue Whip target choice. The footage instead shows Carefree Steps, heads and full prevention. This contradicts that described behavior for this concrete case and agrees with the proposed repair's described behavior. Current engine code and the repair state were not inspected, so this is a footage-to-prediction comparison only.

The test is the class of snipe attacks against benched Meowth, with Tongue Whip as the concrete recorded attack. Linear Attack is unfilmed, but is not a missing required test. There is no Meowth tails trial, damaging Ability trial, Absol trial or Hypno trial. The light-blue Meowth icon is described without assigning a Special Condition. Complete available-footage review: true; uninterrupted whole-battle coverage: false; terminal battle result observed: true. Registered completion: `rule_test_review_complete`.


## Independent lead check

Lead read the entire source review, coverage, summary and uncertainty packet, reconciling all visible turns7-15 and the60+30+30+0+160+80=360 attack-damage ledger. Independently inspected ordinary overview sheets01 and04, start0s public continuity, Combusken KO27s and Victini30 damage56s, snipe target86s, named Carefree Steps87s, prevention prompt89s, explicit heads91s, shield and unchanged Meowth50HP94s. Auto is off105s and on106s; terminal227.6s explicitly names the computer deck and Victory3-1, first,15turns,360damage. Astra independently confirms the defender prevention context. Tongue Whip is the filmed example of the intended snipe class; no separate Linear Attack trial was requested. Comparison with repair B is conditional on owner-provided code context, not a running-engine audit. Entire available source accepted as one continuation, missing cut interval retained, battle_complete false, no Pause Games or Ladder Log entry.

First-pass reviewer: sol_rules_20261002_carefree_steps; gpt-6.1-sol high. Independent lead and targeted Astra checks: October 2, 2026.

[Targeted Astra check](../BATCH_2026-10-02_CAREFREE_SNIPES/ASTRA_CAREFREE_CHECK.md).
