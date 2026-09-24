# R1 — Real-game battle observations relevant to rules questions

Extracted from screen-recording reviews of the owner's actual games (ranked/random/AI) in `/home/claude/rr/local/reviews/`. Each entry: question(s), what happened (exact numbers), file + timestamp, reliability (DIRECT = on-screen reading; INFERRED = reviewer's interpretation; UNCERTAIN = reviewer flagged doubt).

Files that are simulator/engine/bot-internals analysis (not observations of real gameplay) contain no rules evidence and are noted as skipped where encountered.

---

## Batch 1 (small REVIEW.md/FINDINGS.md files, ongoing-campaign-2026-09-08 + recordings/)

### Q5/Q6 — First-turn Energy Zone asymmetry (P1 gets none, P2 does)
Opponent went first (turn 1): "As the first player, the opponent has no current generated Energy: the large Energy Zone is empty and only the small next-Psychic preview is visible. No ordinary attachment or attack." Owner's first turn (turn 2, going second): "The ordinary Lightning attaches afterward, leaving Jolteon at one Lightning and the current Energy Zone empty." — DIRECT. Confirms: the player going first has no Energy Zone generation on turn 1 (only the next-energy preview is visible), while the player going second DOES get an Energy Zone generation/attachment on their own first turn.
File: `.../mega-burning-generalization-2026-09-09/video-intake/accepted-232035/REVIEW.md`, turns 1–2 (00:12–00:53).

### Q28 (NEW — possible exception to "no evolution on your first turn") 
Owner (going second) used Eevee's "Boosted Evolution" to evolve Active Eevee into Jolteon ex 140 during turn 2 — i.e., during the owner's own first turn. Standard assumption (Q28) is no evolution on either player's first turn. This is either (a) evidence the restriction is per-Pokémon-in-play-this-turn only and Eevee wasn't played that turn (was already Active from setup) — plausible since setup Pokémon "put into play" on turn 0/setup, not "this turn" — or (b) a card-specific ability exception. Reviewer did not flag this as unusual. INFERRED reliability on the "why" but the evolution itself is DIRECT (on-screen). Flag for follow-up: likely resolves Q28 by showing the "no evolution on first turn" restriction only blocks evolving a Pokémon that was put into play THAT turn — a Pokémon placed during setup is evolvable on the owner's very first turn.
File: same as above, turn 2 (00:27–00:53).

### Q38 — Tool HP boost raises current HP, not just max
Opponent attached Elegant Cape (+30 HP, Stage 1) to already-damaged Slowking ex: "the already damaged Slowking's remaining HP rises 110→140 and its maximum becomes 160." DIRECT. Confirms an HP-boosting Tool increases current remaining HP by the same amount as it raises max HP (not a heal, and not capped to old max).
File: same as above, turn 5 (01:39–02:13).

### Q17 (ability damage can hit Bench) 
Jolteon ex's ability "Electromagnetic Wall" triggered on the opponent's ordinary Energy-Zone attachment even when the receiving Pokémon was Benched (dealt 20 to Benched Slowking). DIRECT. Not a weakness case, but shows an ability's automatic damage-on-energy-attach is not restricted to the Active Pokémon.
File: same as above, turn 3 (00:53–01:15).

### Q42 — Sabrina forces an Active/Bench switch (not a retreat)
"Opponent plays Sabrina, forcing owner to switch Oricorio to Team Rocket's Raticate ex; this is a Supporter-forced switch, not a retreat." DIRECT that Sabrina swaps the target's Active with one of their own Bench Pokémon; the review does not clarify whether the affected player or the Sabrina player chooses the replacement.
File: same as above, turn 7 (02:33–02:54.94).

### Q29 — Damage carries over on evolution (2 independent confirmations)
1. "Evolving an injured Basic ... carries the 30 damage forward while increasing remaining HP 30→150" (Electrike 30 dmg taken → evolves to Mega Manectric ex, 180 printed HP, ends at 150 remaining). DIRECT.
   File: `.../native-auto-recordings/000238/REVIEW.md`, clip 60–85s.
2. "Ralts evolves into an 80-HP Kirlia carrying the existing 30 damage, leaving 50 HP." DIRECT.
   File: `.../recordings/234514/REVIEW.md`, 2:20–3:00.

### Q39 — Stadiums: replacement and symmetry (multiple confirmations)
1. "Opponent plays Area Zero. Auto subsequently plays Training Area, replacing it." DIRECT — playing a new Stadium while an opponent's Stadium is in play replaces it (no "can't play a Stadium while one is in play" restriction observed; own Stadium overwrites opponent's).
   File: `.../native-auto-recordings/000905/REVIEW.md`, 80–104s.
2. Stadium effects are symmetric/apply by card criteria, not by owner: "Miraidon is Basic, so removing Training Area does not lower its attack. Magneton's printed 60 would become 70 with the Stadium... its later Stage2 Magnezone attack does not receive Training Area's Stage1 bonus." — Training Area (+10 atk to Stage-1 attacks) applied to the OPPONENT's Stage-1 Magneton, not just the Stadium-player's own Pokémon. DIRECT/INFERRED mix (numbers direct, "symmetric" framing is reviewer's synthesis, but well-supported).
   File: same, 108–132s.
3. "Starting Plains explicitly raises Basic Pokémon HP by 20. Mega Diancie is Basic and gains that bonus; Stage2 Mega Blaziken does not." Diancie (opponent's Basic) gained +20 HP from a Stadium — again symmetric application by card stage.
   File: `.../recordings/232955/REVIEW.md`, ~3:45–4:10.

### Q38 — Field Blower can remove your OWN Stadium/Tool
"Field Blower is used; own Training Area moves to discard by 120 and the Stadium slot is empty." DIRECT — Field Blower was used on the player's own Stadium (Training Area), not just an opponent's card, at a cost of that turn's Item + 10 immediate damage (Stadium bonus) with no stated compensating benefit in that position.
File: `.../native-auto-recordings/000905/REVIEW.md`, 118–124s.

### Q21/Q20/Q14 — Retaliation Tool (Rocky Helmet) fires even when it KOs the attacker simultaneously with its own holder's KO; BOTH players score
"Castform's 30-damage Sunny Scorching knocks out the 20-HP Electrode by attack damage; a Burn icon is also applied. [next row] Castform is knocked out during retaliation. Each player receives one point and the owner promotes a healthy Mega." Electrode was carrying Rocky Helmet (confirmed elsewhere in same file: "Both Electrodes later carry Rocky Helmet"); Castform was at 20 HP (from a prior attack) when it landed the KO on Electrode. Rocky Helmet's retaliation damage (20) still fired despite Electrode being simultaneously KO'd by that same attack, and that retaliation damage also KO'd Castform (at 20 HP) — resulting in BOTH Pokémon being knocked out from the same attack/retaliation exchange, and "each player receives one point." This is a strong, direct real-game answer to Q21 (retaliation fires even though the holder is KO'd by the triggering attack) and to Q14/Q20 (simultaneous KOs on both sides award both players their points; game continues rather than ending/drawing). DIRECT (damage numbers + "each player receives one point" are on-screen-derived), though the causal chain ("during retaliation") is the reviewer's synthesis of the sequence — mark causal link as INFERRED, the simultaneous-points outcome as DIRECT.
File: `.../recordings/225430/REVIEW.md`, 2:05–2:45.

### Q16 — Damage-reduction stacking, floors at 0
"Metal Core Barrier plus the preceding Steel Wing prevents a later Turbo Shark entirely: 70 - 50 - 20 = 0." Multiple reduction sources (a Tool and an ability/attack-text reduction) stack additively against one incoming attack and the result floors at 0 (no negative/overkill "healing"). Also: "a later Jasmine plus Steel Wing again reduces Turbo Shark from 70 to 0" and "reduces Team Rocket's Articuno ex's 130-damage Hailstorm to 60 when combined with Steel Wing." DIRECT numbers, INFERRED stacking-mechanism framing.
File: `.../native-skarmory-indeedee/REVIEW.md`, "Why the game shows promise" section.

### Q20 — A Pokémon's own attack that KOs its own Benched Pokémon awards the OPPONENT the point
"The opponent's Hailstorm also knocked out its own 20-HP Benched Team Rocket's Lapras, awarding the owner one point." DIRECT. Confirms points are awarded based on whose Pokémon is KO'd, regardless of who/what caused it (here, the attacking player's own attack hit their own Bench and KO'd their own Pokémon; the opponent still scored).
File: `.../native-skarmory-indeedee/REVIEW.md`, "Weaknesses and limits" section.

### Q22 — Poison Checkup is a separate damage/KO event from the attack; Giovanni's +10 is an attack-side modifier
"the displayed Junk Spark value is 110... Poison Barb makes the attacking Rotom ex Poisoned" [from a retaliation-style Tool: "applies Poison after an attack damages its holder"]. Then: "the opponent uses Giovanni. Mach Bolt therefore deals 100 total damage, leaving the 110-HP Rotom ex at 10. The following 10-damage Poison Checkup reduces it to 0; this separate poison tick triggers the knockout." DIRECT. Confirms (a) Giovanni's damage bonus applies to the attack itself, not to Checkup damage, and (b) Poison's 10 damage at Checkup is a distinct event from the attack that can independently cause a KO right after an attack leaves the Pokémon at low HP.
File: `.../native-random-rotom/REVIEW.md`, ~5:04–5:24.

### Q22 — Burn 20/Checkup confirmed across multiple checkups
"Burn is directly visible in the late exchange: Gallade 190→70 from the 120 attack, then 50 after Checkup, and 30 after the following Checkup." DIRECT — confirms flat 20 damage per Checkup while Burned (two consecutive checkups both did exactly 20).
File: `.../recordings/230007/REVIEW.md`, "Burn is directly visible..." paragraph.

### Items skipped (not real-game evidence)
`funding-six-study-2026-09-09/FINDINGS.md` + `lead/REVIEW.md`, `gallade-planning/FINDINGS.md`, `mega-burning-repair-2026-09-09/high-review/REVIEW.md`, `opponent-ply-lead-review-2026-09-09/REVIEW.md` — these are simulator/bot decision-tree and code-path audits (engine internals, value functions, certificate registries), not observations from video review of real games. No rules-relevant real-game evidence extracted from these four files.

## Batch 2 (skarmory-field4-pilot / skarmory-oricorio-mechanics / checkup-order-work / first-altaria / second-altaria)

### Items skipped (not real-game video evidence)
`skarmory-field4-pilot/MECHANICAL_APPENDIX.md`, `MECHANICAL_INVENTORY.md`, `skarmory-oricorio-mechanics-2026-09-09/LEAD_REVIEW.md`, `MECHANICS_REVIEW.md` — these are all **simulator** trace/pilot runs ("field4 development pilot", "eight predeclared games", "checks use the unchanged frozen Field4 library"), not observations of the owner's real games. Per project instructions the simulator is not a trusted source of real-game behavior, so no entries were extracted from these four files despite containing damage-formula numbers (e.g., weakness +20 flat bonus, Tool/ability stacking) — those numbers describe simulator behavior, not confirmed real-game behavior.

`overnight-continuation-2026-09-08/reports/checkup-order-work/FINDINGS.md` is also simulator-bug analysis (checkup/KO-ordering defect), not a video review. One item worth flagging for Q11 anyway: the file quotes an external, non-Pocket-official source, the "Pokémon Zone" fan guide (pokemon-zone.com, updated 2025-05-04): "Any Pokémon that has no HP remaining at the end of Pokémon Checkup is Knocked Out," with "first status checks [assigned] to the outgoing player" and a Poison→Burn→Sleep→Paralysis order within a Pokémon. This is a written external citation, not a video observation — reliability UNCERTAIN (unofficial fan guide, not verified against an owner game in this file) — but is consistent with 01_ENGINE_FIDELITY.md's description of the "official order Poison→Burn→Sleep→Paralysis." No owner video evidence in this file establishes the promotion order when Checkup causes simultaneous KOs on both sides ("the required Pocket promotion order was not established by the public sources," per the file itself).

### Q27 — Sleep flip timing: confirmed at Checkup immediately after being put to sleep (DIRECT, clean sequence)
"1. Igglybuff's Sleepy Lullaby damaged Oricorio and made it Asleep. 2. Both Benched Darkrai applied Bad Dreams, leaving Oricorio at 20 HP. 3. Pokémon Checkup began at about 82 seconds. The coin visibly resolved Heads at 84 seconds, followed by 'Oricorio recovered from being Asleep.' Oricorio therefore entered its next turn awake." DIRECT — the sleep-recovery coin flip happened at the very next Checkup after the Pokémon was put to sleep (i.e., at the end of the turn it was put to sleep, before its own next turn), and Heads woke it in time to act normally. Reviewer's summary: "attack applies Sleep, end-of-turn Bad Dreams resolves, then Sleep checkup flips if the target remains in play."
File: `.../round-robin-checkpoint/reports/video-intake/second-altaria/REVIEW.md`, "Sleep timing and coin result" section (~70–85s).

### Q25 — Healing does NOT cure Sleep; evolving DOES
"The opponent remained Asleep long enough for this interaction to matter, healed Bulbasaur, then evolved it into Ivysaur; evolution cleared the Sleep state before Ivysaur acted, so the recording shows no illegal asleep attack or ordinary retreat." DIRECT (sequence order) / INFERRED (the causal claim "evolution cleared the Sleep state" is the reviewer's read of the outcome, but well supported since Bulbasaur stayed Asleep through a heal and only lost the status after evolving). Confirms healing alone does not remove Sleep; evolving into a new stage does.
File: `.../round-robin-checkpoint/reports/video-intake/first-altaria/REVIEW.md`, "Result and sequence" section.

### Q42 — Sabrina: the TARGET player (not the Sabrina caster) chooses their new Active
"the owner evolved the middle Eevee into Espeon and used Sabrina; the opponent selected the fresh 180-HP Mega Manectric ex as the new Active." DIRECT. The owner played Sabrina against the opponent; the opponent (whose Active was force-switched) is the one shown choosing which Benched Pokémon becomes their new Active — not the player who played Sabrina.
File: `.../round-robin-checkpoint/reports/video-intake/second-altaria/REVIEW.md`, "Last owner turn" bullet (frame f374.jpg onward).

### Q42 — Cyrus targets a damaged Benched Pokémon (confirms "damaged" requirement)
"the opponent visibly played Cyrus, whose displayed effect switches the owner's Active with one of the owner's damaged Benched Pokémon. The only damaged eligible Bench Pokémon was the 70-HP Darkrai, so Cyrus brought it Active." DIRECT — Cyrus's on-screen effect text restricts the forced-active target to a damaged Bench Pokémon of the target player; here there was only one legal target.
File: same file, "Final switch source" bullet (frame f397_5.jpg).

### Q9 — Attacking ends the turn; game warns before you commit if another action (Supporter) is still available
"The owner declined the game's warning that Copycat was still usable and attacked instead." DIRECT. Confirms (a) attacking is turn-ending / locks out further plays, and (b) the client proactively surfaces a warning prompt if the player has an unused playable card (here, an unplayed Supporter) before confirming the attack.
File: `.../round-robin-checkpoint/reports/video-intake/first-altaria/REVIEW.md`, "Final resources" bullet.

### Q39 — Stadium symmetry, third confirmation
"Training Area symmetry: The Stadium helped Mega Altaria reach 140, but it also added 10 to the opponent's Stage 1 Mega Manectric." Matches the two 000905/232955 confirmations above (own-played Stadium boosts apply to the opponent's qualifying Pokémon too).
File: same file as above, "Training Area symmetry" bullet.

### Q24 (reviewer's stated rule, not itself directly witnessed in this clip)
"A non-wake could deny Mega Manectric its attack because an Asleep Pokémon cannot ordinarily retreat, despite Mega Manectric's free retreat cost." This is the reviewer's asserted rule used to reason about an alternate (not-played) line — UNCERTAIN/INFERRED, not a directly observed Asleep-retreat-attempt in this game.
File: same file, "Missed defensive opportunity" bullet.

## Batch 3 (hailstorm-cutoff-audit / luckycad / mega-houndoom-correction / owner-auto-battle-031901)

### Items skipped (not real-game video evidence)
`hailstorm-cutoff-audit-2026-09-07/AUDIT.md`, `CONTINUATION_AUDIT.md`, `CONTINUATION_V2_DISPOSITION.md`, `README.md` — entirely synthetic simulator probes about the bot's search-horizon blindness to Hailstorm's own-Bench collateral damage (constructed fake "Safe Storm" card, not a real game). No owner video involved. Skipped in full.
`mega-houndoom-correction-2026-09-05/README.md`, `report.md`, `test-evidence.md` — a card-database/engine source-mapping fix for Mega Houndoom ex's Grimhound Flare (coin-flip damage), verified only by unit tests, not video. Confirms card text ("Flip 3 coins. This attack does 80 damage for each heads," replacing the printed 80 rather than adding to it) but this is catalog/engine work, not an observed real game. Skipped.

### Q22/Q26-adjacent (NEW) — Poison Barb retaliation confirmed again; attack-preview damage dynamically counts target's Special Condition
Poison Barb: "the attack removes 10 HP from the Poison Barb holder, the attacker becomes Poisoned, and one 10-damage poison checkpoint has resolved" — DIRECT, consistent with the native-random-rotom finding (Poison Barb poisons the ATTACKER when it damages the barb holder).
Separately (NEW, no matching question number): "inspecting Team Rocket's Magmar shows Derisive Roasting with a computed damage value of 60. The displayed rule is base 10 plus 50 for each Special Condition affecting the opposing Active" — with the target already Poisoned, the in-game attack-preview tooltip showed the conditional bonus already applied (10+50=60) even while Magmar was not the Active Pokémon. DIRECT for the 60 number and "one Special Condition" case; the reviewer explicitly notes stacking with 2+ simultaneous conditions was NOT tested here.
File: `luckycad-video-2026-09-06/evidence/luckycad-early-review/REVIEW.md`, sections 1 and 3 (~00:55–01:10, ~08:10–08:20).

### Q47 (very relevant, NEW-ish) — A player-scoped "your next attack deals +X" effect survives its source Pokémon's own Knock Out and applies through a promotion to a DIFFERENT attacker
Happiny's Active used Chubby Cheer (a "your next turn +20 damage" effect), then Happiny itself was Knocked Out by the opponent's attack before the owner's next turn. On the owner's next turn, a completely different Pokémon (Absol, promoted from Bench) attacked and the +20 bonus still applied: "The constrained damage account is 20 Enhanced Blade base + 20 Chubby Cheer = 40. Absol has no Tool, so Enhanced Blade's conditional Tool bonus does not contribute... This also shows Chubby Cheer's player-scoped next-turn boost surviving the source Happiny's Knock Out and applying to a different attacker." DIRECT (damage numbers, banner text) + reviewer's synthesis (labeled "player-scoped" — INFERRED but strongly supported: the effect is stored against the player/turn, not the casting Pokémon, since the caster was gone and a different Pokémon received the bonus). This directly informs Q47 (an "on your opponent's next turn"/"your next turn" style effect's source being KO'd does not cancel the effect; and shows such an effect isn't even tied to a specific Pokémon staying in the Active spot).
File: `owner-auto-battle-031901-2026-09-06/REVIEW.md`, "Case 1" (148.000–183.000).

### Q32 — Promotion after KO is a player choice (chooser UI shown), not automatic
"At 168.000 the Auto promotion chooser is visible. By 174.000, non-ex Absol is Active..." DIRECT — after Happiny's KO, the game presented a promotion-selection UI (used here by Auto) rather than auto-selecting the next Bench Pokémon.
File: same file, Case 1, step 4.

### Q36/Q11-adjacent — Ability resolves before the attack in the same turn, ability alone doesn't need to KO
"Nightmare Aura 20 + Dark Prism 80, with the ability resolving before the attack and the attack supplying the Knock Out for the terminal point. Nightmare Aura itself does not Knock Out Pikachu here." DIRECT (damage numbers/banners): 40 HP Pikachu → 20 HP via the (passive, energy-attachment-triggered) ability Nightmare Aura, then the same turn's attack (Dark Prism, 80) finishes it. Confirms an ability and an attack can both resolve in the same turn, in that order, contributing to the same KO.
File: same file, "Case 2" (194.000–219.000).

## Batch 4 (split-battle-review-2026-09-07 — real Auto-on video across 2 clips)

### Q20 — A multi-effect attack's secondary effect (target selection + resolution) still executes after the attack's damage has already Knocked Out the primary target
"Turbo Shark is announced... displays 70 damage... and leaves the opposing 60-HP Active Rookidee at 0... The attack then offers all three Water Bench targets... the center Magikarp has gained one Water Energy... This is direct evidence that the Bench Energy effect still resolves after lethal damage." DIRECT. Confirms the attack fully resolves ALL of its effects (including a targeted secondary effect requiring player input) even though its damage component already reduced the primary target to 0 HP — i.e., the engine/game does not short-circuit an attack's remaining effects just because the target is already lethal. Bears on Q20 ("Knock Out timing: checked after the attack fully resolves?").
File: `split-battle-review-2026-09-07/REVIEW.md`, section 1 (part1 80.000s–84.500s; part2 0.000s–4.000s). Repeated a second time with the same result in section 2 (part2 38.000s–42.000s), a "second distinct Turbo Shark attachment to the same future attacker" after another non-lethal hit.

### Q16 — Clean real-game numeric confirmation: attacker-side scaling resolves BEFORE defender-side flat reduction, and the reduction can floor damage far below the reduction amount (no negative overflow into healing)
"Discarding one Benched Water Pokémon makes Wild Swing's nominal damage 20 + 40 = 60. Metal Core Barrier reduces that by 50, and Corviknight ex settles from 110 to 100." DIRECT: 60 (attacker's own self-discard-scaled base) − 50 (defender's flat Tool reduction) = 10 actual damage dealt (110→100), confirming order attacker-modifier-first, defender-reduction-second, and confirming the reduction is a simple subtraction with no special floor issue here (10 > 0). A second instance in the same file: Metal Core Barrier "reduces Mega Blaster from 140 to the displayed 90" (140−50=90, exact).
File: same, sections 3 (part2 70.000s–80.000s) and 4 (part2 164.000s–168.000s).

### Q32 — Compulsory promotion when only one Bench Pokémon remains happens automatically/immediately, no optional action in between
"the defeated Rookidee already in the discard while the sole surviving Bench Rookidee moves into the empty Active Spot... has the forced replacement settled... No optional action is visible across the boundary." DIRECT. With only one legal replacement, promotion resolved without any other action being available in between (consistent with, but not proof of, an actual "choice" UI when more than one option exists — see the owner-auto-battle-031901 finding above for the chooser UI when multiple options exist).
File: same, section 1 (part1 84.500s to part2 0.000–4.000s).

### Q38 (card-specific but rules-relevant) — Tool with a timed self-discard triggers on schedule
Metal Core Barrier (-50 damage to its Metal-type holder) "is present at 80.000 seconds and absent by 100.000 seconds, consistent with its printed end-of-opponent's-turn discard." DIRECT-ish (presence/absence observed; exact discard animation not sampled) — a Tool can have a built-in expiration (discards itself after a specified timing, here "end of the holder's opponent's turn") separate from the Pokémon leaving play.
File: same, section 3.

### Items skipped (not real-game video evidence)
- `split-battle-review-2026-09-07/harness/split_battle_mechanics.rs`, `qualify_mechanics.py`, `validation/mechanics-build-*.json/.log`, `validation/mechanics-run-2.json` — a Rust test harness built to reproduce the above video-observed states in the simulator and assert the engine agrees; this is engine-validation of the REVIEW.md findings, not independent real-game evidence (no new numbers beyond what REVIEW.md already states).
- `skarmory-field4-pilot/MECHANICAL_APPENDIX.json`, `MECHANICAL_FLAGS.json`, and `opponent-expansion-2/pilot/MECHANICAL_INVENTORY.json` (all confirmed via their JSON `"schema"` fields to be simulator pilot/trace inventories — e.g. `"schema": "pdl-exploratory-mechanical-inventory/v1"`, `"schema": "skarmory-field4-pilot/mechanical-appendix-v1"` — recording chosen actions across many simulated games, not observations of the owner's real games). No real-game rules evidence extracted from these three large files (~5,000 lines combined); they are simulator development artifacts, out of scope per the project's stance that the simulator is not a trusted source of real-game behavior.

## Coverage summary

Questions with direct or strong supporting real-game evidence in this file set: Q5/Q6 (first-turn Energy asymmetry), Q9 (attack ends turn; UI warns of unused plays), Q14/Q20/Q21 (simultaneous KO from retaliation, both players score), Q16 (damage order: attacker mods → defender flat reduction, subtraction, floor at 0), Q17 (ability damage can hit Bench), Q20 (attack's full effect list resolves even after lethal damage), Q22 (Poison/Burn Checkup numbers and separate-event timing; Poison Barb triggers post-damage), Q25 (healing doesn't cure Sleep; evolving does), Q27 (Sleep flip at the very next Checkup, can wake before own turn), Q28 (possible carve-out: a setup Pokémon can evolve on owner's own first turn), Q29 (damage carries over evolution, twice confirmed), Q32 (promotion is a player choice via UI when >1 option; automatic/instant when only 1), Q36 (ability-then-attack same-turn sequencing), Q38 (Tool HP boost raises current HP; Field Blower can hit own Stadium; timed Tool self-discard), Q39 (Stadium replacement and symmetric application, 4 independent confirmations), Q42 (Sabrina: target player picks own replacement; Cyrus requires a damaged Bench target), Q47 (a "next turn +damage" effect is player-scoped, survives its source's KO, applies through a different attacker).

Questions this file set sheds no real-game light on at all: Q1 (deck Energy-type declaration), Q2 (opening-hand guarantee mechanism), Q3 (setup simultaneity/time limit), Q4 (coin flip visibility/Ranked differences), Q7 (attaching energy to a Pokémon played this turn), Q8 (empty-deck draw, hand-limit-10 overflow handling), Q10 (timers), Q12 (full point-rule list beyond ex/Mega ex), Q13 (loss timing when no Pokémon in play), Q15 (deck-out/concede/disconnect), Q18 ("prevent all damage" vs "prevent all effects"), Q19 (damage vs "damage from attacks" reduction scope), Q23 (Poison+Burn coexistence — plausible from Q22 evidence but never both explicitly shown together and confirmed as simultaneously active), Q26 (poison-damage-boosting effects stacking/targeting all opponents), Q30 (Rare Candy/Mega Evolution ex turn-ending rule), Q31 (which Energy is discarded on retreat — only retreat *cost display* was seen, not a discard choice), Q33 (Active-attached effects clearing on move to Bench), Q34/Q35 (ability once-per-turn scope, same-name ability stacking), Q37 (Supporter-on-first-turn, unplayable-Trainer UI blocking), Q40 (Fossils), Q41 (search/draw reveal-to-opponent rules), Q43 (public info enumeration), Q44 (independence of coin flips / flip-until-tails), Q45 (copy-attack mechanics), Q46 (non-turn Energy-Zone attachments vs the once-per-turn manual attachment), Q48 (targeting effects with no legal target), Q49 (Ranked vs casual vs AI rules differences — all reviewed games note Auto/manual but don't compare rule differences), Q50 (errata history).
