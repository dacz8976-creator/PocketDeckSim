# R2 Battle Observations — extracted from screen-recording reviews

Format: **Q#s** — observation (exact numbers) — file:ref — RELIABILITY

Reliability: DIRECT = on-screen reading of numbers/text; INFERRED = reviewer's interpretation; UNCERTAIN = reviewer flagged doubt. Where a file is engine-source analysis (not the video itself), this is noted explicitly and treated as lower value for "real game" claims.

---

## Batch 1: split-battle mechanics-run-2.log; flygon-sableye video mechanics review

### Q20, Q32 (KO points, promotion)
- Flygon ex's Dragon Pulse deals 140 to Aerodactyl ex (130 HP remaining) → Aerodactyl ex (an "ex", 2-point Pokémon) is Knocked Out; on-screen banner reads "+2 points!"; recorder's score goes 0→2 immediately, before the opponent's next action. Opponent then promotes Marshadow from Bench (70 HP, 1 Fighting Energy). — `flygon-video/EVIDENCE.md` timestamps 143.0–154.5s — DIRECT (on-screen damage number, point banner, HP values, promoted Pokémon all read from frames).
- Regular (non-ex) Pokémon KO awards exactly 1 point: Gabite (60/80 HP) Knocked Out by Cursed Jewel (80 dmg) → opponent's score goes 2→3 (i.e., +1). — `sableye-video/EVIDENCE.md` timestamps 235.0–242.0s — DIRECT.

### Q13 (loss with empty bench, timing)
- Owner had **no Benched Pokémon** when Gabite (Active) was Knocked Out by Cursed Jewel. UI went directly from the KO/point animation to a "Defeat" screen — no promotion prompt, no other forced choice appeared. Confirms loss triggers immediately when Active is KO'd with an empty Bench. — `sableye-video/EVIDENCE.md` — DIRECT (on-screen "Defeat" shown, no other UI in between; reviewer explicitly notes "no promotion or other forced choice appears").

### NEW — Checkup ability damage (Sand Slammer) hits Active + all Bench, flat (no weakness)
- With Flygon ex Active (has ability "Sand Slammer"), during the Pokémon Checkup following the turn, **10 damage was applied to all three of the opponent's Pokémon** (their Active Marshadow AND both remaining Bench): Hitmonchan 50→40, Marowak ex 130→120, Marshadow 70→60. Applied uniformly (no weakness/type differences visible) — this is an ability's own fixed Checkup damage, not poison/burn. — `flygon-video/EVIDENCE.md` timestamps 155.5–158.0s — DIRECT (three separate on-screen HP transitions read from frames).
- Note: this is an *ability*-driven Checkup effect (Sand Slammer text maps in source to "CheckupDamageToAllOpponentPokemon"), separate from the standard Poison/Burn/Sleep/Paralysis Checkup sequence in Q11 — relevant context but not itself evidence about the Poison/Burn/Sleep/Paralysis ordering question.

### Q47 (effects referencing "opponent's last turn" surviving into the following turn)
- Marshadow's attack "Revenge" (base 40, +60 conditional if "one of its player's Pokémon was Knocked Out by damage from an opponent's attack during the opponent's last turn") dealt **100 damage** (40+60) on Marshadow's very next turn after Aerodactyl ex was KO'd by Flygon's attack the prior turn — confirming the "last turn KO" condition read true across the intervening Checkup/opponent-turn boundary. 100 damage KO'd Flygon ex (100 HP remaining) for the win (opponent 1→3 points). — `flygon-video/EVIDENCE.md` timestamps 163.5–172.5s — DIRECT (on-screen damage number 100, HP 100→0, final score).
- (Engine-source note, not video: reviewer's source reading says this KO-memory is stored as a "this_turn"/"last_turn" flag that rotates during Checkup — this explains the mechanism but is INFERRED/engine-source, not itself an observed game fact.)

### Q21 (retaliation timing / whether it fires immediately)
- **Correction to an earlier (wrong) intake label**: Mega Sableye ex's "Cursed Jewel" dealt 80 damage, Knocking Out Gabite, and the game then displayed a callout: "If damaged by an attack, do 40 to the Attacking Pokémon." This callout is Cursed Jewel **arming an effect for Mega Sableye's own next turn** (i.e., a self-buff/delayed counterattack condition), NOT an immediate 40-damage retaliation from the Pokémon being KO'd. The video shows the 80-damage KO and then the effect text announcement, then immediately the winning point and "Defeat" screen — **no 40-damage event ever fires** in this clip because the game ends first. The original intake had mislabeled this sequence as a retaliation KO; the focused review corrects that. — `sableye-video/EVIDENCE.md` timestamps 234.0–244.0s; also stated plainly in `README.md` — DIRECT for what is shown (80 dmg, then text callout, then Defeat with no further damage shown); the "this is arming not immediate retaliation" characterization is the reviewer's DIRECT reading of the on-screen effect text combined with the fact no further damage animation occurs.
- Related but NOT from this video (engine-source only, INFERRED): reviewer's source-code reading states the engine's general order for this class of effect is "pre-effect, damage/counterattacks, post-effect, then knockouts" and that a Rocky-Helmet-style *immediate* counterattack (different from Cursed Jewel's delayed self-buff) is confirmed by an unrelated existing engine test to be able to KO the attacker and still let a queued post-attack effect resolve before promotion. This is not itself video evidence and should not be treated as confirmed real-game behavior — flag as INFERRED/engine-source-only.

### Q16 (damage calc — no unexplained modifiers when none apply)
- Cursed Jewel's 80 printed base damage landed as exactly 80 on Gabite, which has no Weakness in the database, no Tool, and Rainbow Cave (Stadium in play) has no damage-modifying effect — confirms no hidden/unexplained modifier applies when none of the modifier conditions are met. — `sableye-video/EVIDENCE.md` — DIRECT (on screen 80 dmg number) + INFERRED (absence-of-modifier reasoning from card database).
- Dragon Pulse's 140 printed damage landed as exactly 140 on Aerodactyl ex — same pattern (no visible modifier). — `flygon-video/EVIDENCE.md` — DIRECT.

### UNCERTAIN / low-confidence — Tool damage reduction and forced energy attachment (mechanics-run-2.log)
This is a **constructed validation-harness log** (engine eval13, "visible-public-input fixtures; not a hidden-zone reconstruction or full replay"), not a raw video observation — treat as UNCERTAIN/lower-value for real-game rules claims, but recorded since it's the only evidence of its kind in this batch:
- `WILD_SWING`: with a protecting Tool/effect in place, damage was 10; without it, 60, against Pokémon at 100/50 HP respectively — suggests a Tool or effect reduced damage from 60 to 10 (a −50 reduction, not the usual small increments), but the exact card/mechanism is not named in the log, only card-ID bindings (MetalCoreBarrier_B2_148 is likely the reducing card). Relevant to Q38 (Tool effects) but UNCERTAIN which specific numbers map to which mechanic. — `split-battle-review-2026-09-07/validation/mechanics-run-2.log` line 6.
- `TURBO_SHARK`: log shows `forced_attachment=1Water->Magikarp`, i.e., an effect forced an Energy attachment (from a KO'd/discarded Pokémon's held Energy?) to a specific surviving Pokémon (Magikarp) as part of attack resolution — possibly relevant to Q46 (effects that attach energy outside the manual once-per-turn attachment) but too terse to be confident. UNCERTAIN.
- `MEGA_BLASTER`: shows a case where "protected" (90 dmg, KO at 90 HP) vs "unprotected" (140 dmg) framing again implies a Tool/ability damage reduction; final line shows points transitioning "1-1_to_3-1" with "winner=0" — consistent with a multi-point ex/Mega KO ending the game. Too compressed to extract exact rule mechanics with confidence. UNCERTAIN.

---

## Batch 2: video-review-coordinator battles 014933, 020124, 023511, 024406, 025604

### Q6 (Energy Zone "next energy" preview) — CONFIRMED real and player-facing
- Rainbow Cave (Stadium), when activated by its prompt, **discards the currently-generated Energy, generates the previously-shown "next" Energy in its place, and the preview advances to a new type** — this proves the "next energy" preview is a real, usable game value (not just a display), since Rainbow Cave's whole effect is built on swapping current-for-next. — `battle-20260907-014933/REVIEW.md` turn 4 (00:59–01:31); also `battle-20260907-020124/REVIEW.md` turn 5 ("Owner accepts Rainbow Cave's prompt, discards the currently generated Energy, advances the Energy Zone, and attaches the replacement ordinary Metal Energy") — DIRECT.

### Q46 (attack/effect energy attachment vs. the once-per-turn manual attachment) — they are independent
- In the same turn, the owner **manually attached the turn's generated Energy** (Fire, taking Moltres to 3) **and then used the attack "Heat Charged,"** whose own effect attached 2 more Energy from coin flips (Moltres 3→6 after a Victory Star reflip). Both the manual once-per-turn attachment and the attack's own Energy-Zone attachment occurred in the same turn without conflict — confirms an attack's built-in Energy attachment does not use up / is not blocked by the once-per-turn manual attachment. — `battle-20260907-020124/REVIEW.md` Owner T9 (03:02–03:40) — DIRECT.
- Note: ending the turn without having attached Energy triggers a UI warning ("`Energy can be attached` warning"); the player can cancel and attach before actually ending. — same turn — DIRECT.

### Q44 (coin flips) — Victini's "Victory Star" reflip replaces the WHOLE batch, not additive
- Heat Charged's attack flips 3 coins for Energy attachment. With Victory Star (gold Victini's passive), the player may accept or decline a full reroll of the entire coin batch. Observed: original flip Tails/Tails/Heads (1 head) → reflip accepted → replacement Heads/Heads/Heads (3 heads) → **only the replacement batch counts**; the original 1 head is not kept/added. In a separate battle the player declined ("No") and the original batch (2 heads/1 tails) was kept and resolved normally. — `battle-20260907-020124/REVIEW.md` Owner T9; `battle-20260907-014933/REVIEW.md` turn 18 — DIRECT (exact coin-by-coin results and resulting Energy counts read from screen).

### Q19 (damage from attacks vs. Ability damage — modifiers that target "attacks" only) — CONFIRMED
- Aegislash's Ability "Superb Shield" text: "during the opposing player's next turn, [Aegislash] takes 80 less damage from attacks by that player's Pokémon ex." When Crobat (an Indeedee-ex-owner's Pokémon, but Crobat itself is not an "ex") used its **Ability** "Cunning Link" for 30 (Ability damage, not an attack) against Aegislash, **the −80 modifier did not apply** — Aegislash simply took 30 (140→110). The reviewer explicitly notes: "Cunning Link is Ability damage rather than attack damage, so Superb Shield's −80 modifier does not apply." A later instance: the same modifier also does not apply to Crobat's own attack "Darkness Fang" because Crobat is not a Pokémon ex (separate reason, same net non-application). — `battle-20260907-025604/REVIEW.md` turns 9, 11, 13 — DIRECT (explicit reviewer note tied to on-screen damage numbers matching un-reduced values).

### Q34 (Ability "once per turn" — per Pokémon instance; using Ability doesn't consume the attack)
- **Two separate copies of Indeedee ex, each with its own "Watch Over" Ability, were each activated once in the same owner turn** (turn 7: 60→80 then 80→100; turn 9: 50→70 then 70→90) — confirms "once per turn" is scoped per Pokémon instance, not per player/team. — `battle-20260907-023511/REVIEW.md` turns 7, 9 — DIRECT.
- **Using an Ability that itself deals damage and KOs the target does not consume/replace the Pokémon's attack for that turn**: Crobat used Ability "Cunning Link" (30 dmg, KO'd Aegislash from 30 HP) and then, same turn, also used its attack "Darkness Fang" (50 dmg) against the newly-promoted Mega Mawile. — `battle-20260907-025604/REVIEW.md` turn 13 — DIRECT.

### Q12 (points — Mega Evolution ex = 3) — CONFIRMED with exact on-screen text
- Knocking out **Mega Mawile ex** (a "Mega" ex Pokémon) produced a literal on-screen **"+3 points!"** overlay, filling the owner's third goal marker and ending the battle at the win threshold. — `battle-20260907-025604/REVIEW.md` turn 15 (final KO) — DIRECT (exact on-screen text quoted).
- Regular (non-ex) Pokémon KO = 1 point, confirmed repeatedly: Numel KO → +1 (`023511`); Buneary KO → +1 (`014933`); Gabite KO → +1 (batch 1); Munchlax/Crobat KOs each → +1 for opponent (`025604`).
- ex Pokémon KO = 2 points, confirmed repeatedly: Aerodactyl ex (batch 1), Moltres ex ×2 instances (`023511`, `014933`), Indeedee ex (`024406`).

### Q20 (multiple/simultaneous KOs from one attack; self-inflicted KO awards the opponent a point)
- **Hailstorm** (Articuno's attack) damages the opponent's Active for its full value **and simultaneously damages the attacker's own Bench** (a "self-bench" attack effect, not targeting the opponent's Bench at all — confirmed because the defending player's Benched Indeedee took zero damage both times). On the deciding use, Hailstorm **simultaneously KO'd the owner's Active Indeedee ex (130→0) AND the opponent's own 10-HP benched Carvanha (10→0, self-damage)**. Both KOs were scored in the same resolution: opponent +2 (Indeedee ex) → reaches 3 and wins; owner +1 (opponent's self-KO'd Carvanha) → reaches 1. This directly shows that **a Pokémon KO'd by its own side's attack-effect damage awards the point(s) to the opponent**, and that this is resolved together with the "main" KO from the same attack. — `battle-20260907-024406/REVIEW.md` turn 8/terminal — DIRECT (exact HP numbers, point overlay reasoning, final 1–3 score).
- Note this is the *same mechanism* the Codex `mechanics-run-2.log` in Batch 1 was gesturing at with `winner=0` / mixed points from one attack sequence — corroborating evidence across two independent sources.

### Q29 (evolution carries over damage) — CONFIRMED
- "Owner evolves the damaged Active Varoom; damage is retained and it becomes 100/120" (was damaged 20 pre-evolution on a 70-HP Basic, becomes 100/120 post-evolution to Revavroom — i.e., the same 20 damage taken carries forward onto the new, higher max HP). — `battle-20260907-020124/REVIEW.md` Owner T3 — DIRECT.

### Q30 (Rare Candy) — confirms Basic→Stage 2 direct evolution skip
- "Rare Candy visibly evolves Lillipup directly into Stage 2 Stoutland" (skipping the Stage 1 form entirely). Also elsewhere: "Plays Rare Candy, evolving benched Honedge directly to Aegislash" and "evolving one benched Zubat directly to Crobat." — `battle-20260907-023511/REVIEW.md` turn 3; `battle-20260907-025604/REVIEW.md` turns 6, 7, 15 — DIRECT.

### Q39 (Stadium effects symmetric) — CONFIRMED
- **Starting Plains** (Stadium): "raising each Basic Pokémon's maximum HP by 20" — applied to Basic Pokémon on **both** sides (owner's Arceus/Munchlax/Zubat AND opponent's Meowth/Mega Mawile all gained 20 max HP), while a Stage 2 (Aegislash) on the opponent's side was correctly excluded since it isn't Basic. — `battle-20260907-025604/REVIEW.md` turns 3, 4, 6, etc. — DIRECT (explicit "Findings useful to research" note plus HP numbers throughout the ledger).

### Q31 (retreat cost — reduction effects genuinely change Energy paid)
- Trainer "X Speed" reduced Active Carvanha's retreat cost by 1, and the Pokémon then **retreated for zero Energy cost, retaining its attached Water Energy** (no Energy discarded) — confirms retreat-cost reduction effects reduce the actual Energy paid/discarded, down to zero if the reduction covers the full cost. — `battle-20260907-024406/REVIEW.md` turn 6 — DIRECT.

### NEW — Trainer card whose coin flip decides "return to hand" vs. discard, not the heal itself
- "Lucky Ice Pop" (Item): observed twice. Heads: heals (100→120) **and the card returns to hand** instead of being discarded. Tails: heals (60→80) and **the card is discarded** as normal. In both observed cases the heal occurred regardless of the coin result — the coin only decided the card's own fate (hand vs. discard), not whether the heal happened. This is card-specific text, not a general rule, but worth flagging since it's easy to misread as "heal only on heads." — `battle-20260907-014933/REVIEW.md` turn 12; `battle-20260907-020124/REVIEW.md` Owner T5 — DIRECT for both instances; the "heal always happens" generalization is the reviewer's/our synthesis across 2 data points, so treat the general pattern as INFERRED even though each instance is DIRECT.

### Q37 (UI blocks unplayable Trainer effects) — CONFIRMED
- Attempting to play "Kid's Room" (its effect exchanges a held card for a random Tool) with an otherwise-empty hand: "the game says its conditions are not met because the hand is empty" — the Trainer's effect was blocked/refused by the game rather than silently doing nothing. — `battle-20260907-020124/REVIEW.md` Owner T9 — DIRECT.

### Q9 (attack ends the turn — including 0-damage attacks)
- "Hungrily Draw, a zero-damage draw attack, draws cards and ends the turn" — confirms even a non-damaging, card-draw-only attack still ends the turn like a normal attack. — `battle-20260907-025604/REVIEW.md` turn 9 — DIRECT.

### Q16 (damage calc — per-Energy scaling attacks, confirms formula reads correctly on screen)
- Indeedee ex's "Psychic" (printed "30, +30 for each Energy attached to the Defending Pokémon") showed exactly **90** (2 Energy: 30+60), **120** (3 Energy: 30+90), and **180** (5 Energy: 30+150) across three separate uses in one battle, and again **120** (3 Energy) in a different battle — all matching the printed formula precisely with no unexplained deviation. — `battle-20260907-023511/REVIEW.md` turns 5, 7, 9; `battle-20260907-024406/REVIEW.md` turn 7 — DIRECT.

### Context / not directly a listed question but notable
- Trainer "Ilima" returns a damaged Active Pokémon to hand; that Pokémon's attached Tool and all attached Energy "no longer remain in play" (i.e., are discarded, not returned with it) — the Pokémon itself goes to hand while its attachments are lost. — `battle-20260907-025604/REVIEW.md` turn 9 — DIRECT.
- A Tool ("Metal Core Barrier") with a temporary effect was present for one exchange and confirmed gone (no longer attached) a few turns later — some Tools/effects are duration-limited, though the exact duration text wasn't captured. — `battle-20260907-025604/REVIEW.md` turns 8, 11 — DIRECT (presence/absence observed) but duration rule itself UNCERTAIN (not quoted from card text).
- Card "enlargement"/inspection in the UI is repeatedly confirmed to NOT indicate a card was played — multiple battles show cards enlarged and then still sitting in hand afterward. This is a review-methodology note, not a rules point, but is called out because it could otherwise corrupt "what was played" observations across all these files.

---

## Batch 3: battles 031007, 031901, 170229, 181914

### Q16 (damage calc order / floor at 0) — CONFIRMED with exact numbers, including a full-prevention case
- Goodra's ability "Securely Sheltered" flips a coin on each incoming damaging attack: **Tails = no reduction** (Quick Straight base 50 + Fighting Coach +20 = 70 dealt, Goodra 150→80); **Heads = −80 reduction**, applied to a would-be 70, producing a **literal 0-damage outcome** ("the blue result state and the literal 0-damage outcome show the attack was fully prevented") — confirms damage floors at 0 rather than going negative when a reduction exceeds the modified total. — `battle-20260907-031007/REVIEW.md` Opponent Turns 7 and 9 — DIRECT (exact damage numbers and an explicit "0-damage" reading).
- Separately, an attacker-side ability bonus (Fighting Coach +20) and a defender-side Tool reduction (Heavy Helmet −20) were both live on the same hit: Gigantic Press's own scaled base was 50+60=110 (bonus for ≥2 extra attached Energy), Fighting Coach added +20, Heavy Helmet subtracted −20, and the displayed result was **110** (i.e., +20 and −20 net to zero against the 110 base) — confirms both attacker-side additions and defender-side Tool reductions apply together predictably. — `battle-20260907-031007/REVIEW.md` Opponent Turns 11 and 13 — DIRECT.

### Q17/Q18 (bench damage vs. protective/"prevent attack damage" effects) — IMPORTANT nuance
- Oricorio's Ability "Safeguard" (text: prevents attack damage from Pokémon ex) blocked Shadow Bullet's damage to Oricorio itself (the Active) but **did NOT block that same attack's separate Bench-damage component**, which still landed on the caped Pikachu on the Bench. **Safeguard also did not block a Tool's end-of-turn damage** (Deceptive Needle) because that damage is not "attack damage." — `battle-20260907-031901/REVIEW.md` Owner Turn 4 — DIRECT (explicit reviewer note tied to the two different HP changes in the same turn: Active unaffected, Bench −20, Tool −10 landed).
- Later, in a different battle, the same Safeguard-style Ability again blocked an attack's damage to its own holder (Oricorio) but did not stop a *different* attack ("Pierce the Pain") from directly targeting and damaging/KO'ing an already-damaged Benched Pokémon on the same side — i.e., the protection is scoped to "this Pokémon," not the whole side. — `battle-20260907-170229/REVIEW.md` Opponent Turns 11, 15 — DIRECT.
- A separate attack ("Jump Blues," 1-Energy cost) directly damaged **both** the opposing Active and a chosen opposing Benched Pokémon for 20 each, in a single attack (not a Checkup ability) — confirms attacks (not just checkup abilities) can hit Bench directly, and that Bench damage from an attack "counts" for later effects that require a damaged-Pokémon target. — `battle-20260907-170229/REVIEW.md` Opponent Turn 13 — DIRECT.

### Q34/Q35 (Ability "once per turn" scope) — further confirmation, per-instance
- Two **separate instances of the same evolved Pokémon** ("Baxcalibur") each used their own copy of the Ability "Ice Maker" once in the **same opponent turn** (one attaching Energy to itself before retreating, the other attaching Energy to the newly-promoted Iron Bundle ex) — reinforces that "once per turn" abilities are scoped per Pokémon instance, not per player. — `battle-20260907-181914/REVIEW.md` Opponent Turn 13 — DIRECT.
- Nightmare Aura (Darkrai ex's Ability, triggers on an Energy attachment to it) fired both **while Darkrai was on the Bench** and, later, **while it was Active** — confirms triggered Abilities function from the Bench, not just Active. — `battle-20260907-031901/REVIEW.md` Owner Turns 4, 6, 10 — DIRECT.

### Q47 (next-turn/persistent effects surviving the source Pokémon's KO or absence)
- Happiny's attack "Chubby Cheer" established a "+20 damage to the owner's next attack" effect; Happiny was then Knocked Out by the opponent, and on the owner's following turn **the +20 still applied to a completely different attacking Pokémon (Absol's Enhanced Blade)** — confirms such "your next attack" effects are stored at the player/turn level, not tied to the originating Pokémon staying in play. — `battle-20260907-031901/REVIEW.md` Owner Turns 6, 8 — DIRECT (explicit damage-composition note: "20 Enhanced Blade + 20 Chubby Cheer").

### Q29 (evolution carries over damage, Energy, AND Tools) — CONFIRMED for Tools specifically
- Rowlet (90 HP current, with Leaf Cape attached raising it to a higher max) was evolved via Rare Candy directly into Decidueye ex: **the Leaf Cape remained attached** (new max HP 200) **and the existing 50 damage carried over**, settling at 150 current HP. — `battle-20260907-170229/REVIEW.md` Opponent Turn 11 — DIRECT. Confirms all three of damage, Energy, and Tools persist through evolution (Energy-carry was already well established in Batch 2; this adds the Tool-carry confirmation with exact numbers).
- Second instance: damaged Gimmighoul (40/60) evolved into Gholdengo, and "the existing 20 damage carries," settling at 80/100. — `battle-20260907-170229/REVIEW.md` Owner Turn 14 — DIRECT.

### Q25 (what removes Special Conditions) — Poison cleared by retreating, with explicit UI confirmation
- A Poisoned Active Suicune ex (at 50 HP) retreated (paying its full retreat cost), and **"the UI confirms Poison recovery"** upon becoming a Benched Pokémon — an explicit on-screen status-cure message tied to retreating. — `battle-20260907-181914/REVIEW.md` Opponent Turn 11 — DIRECT (reviewer explicitly cites a UI confirmation of the cure, not just inference from the icon disappearing).

### Q24 (can a Poisoned Pokémon retreat?) — CONFIRMED yes
- The same Poisoned Active Suicune ex above retreated normally, paying its printed Energy cost, with no block or restriction shown — Poison (unlike Sleep/Paralysis) does not prevent retreating. — `battle-20260907-181914/REVIEW.md` Opponent Turn 11 — DIRECT.

### Q22 (Poison exact value) — reconfirmed multiple times, same battle
- Poison dealt exactly **10 per Checkup**, repeatedly, stacked on top of attack damage from the poisoning attack itself: e.g. "Venomous Hit for 30 and Poison: Suicune 140→110, then Poison 10 settles it at 100" and again "90→60, then Poison 10 settles it at 50." — `battle-20260907-181914/REVIEW.md` Owner Turns 8, 10 and the Checkups following — DIRECT.

### Q12/Q20 (points from a KO are not always automatic — a card effect can deny the point while the KO still happens)
- **"Shattering Crystal"** (an attack/effect, coin-flip based): this single battle shows **both branches** — on **Heads**, an explicit on-screen notice states the opponent "was unable to get any points" even though the Knock Out itself still occurred (the Pokémon was removed from play) and the game continued; on **Tails**, the normal point was awarded (opponent's score went 1→2). This is a concrete counter-example to "every KO always awards its point(s)": a specific card effect can sever the KO from the point award. — `battle-20260907-181914/REVIEW.md` Opponent Turns 9 (Heads, point denied) and 11 (Tails, point awarded) — DIRECT (exact on-screen notice quoted by reviewer).
- Follow-on: Kingambit's attack "Overlord's Blade" (180 damage) scales by a per-KO count of the owner's own Knocked-Out Pokémon; the 180 result is "consistent with 60 + 40×3 actual owner Pokémon KOs," and **the point-denied Glimimora (denied by Shattering Crystal Heads) still counted as a real KO for this scaling** even though it hadn't produced a point for the opponent. This shows "Knocked Out" (a board-state fact usable by other card text) and "point awarded" are tracked separately. — `battle-20260907-181914/REVIEW.md` Owner Turn 12 — DIRECT/INFERRED (the 180 = 60+40×3 arithmetic is the reviewer's inference, but the underlying KO count and point-denial are DIRECT).

### Q12/Q14 (points cap at 3, no overflow shown)
- A 2-point ex KO that would bring a score from 2 to 4 instead is shown as advancing "the displayed goal from two to the capped three-point win state" — the UI shows only 3 filled markers and ends the game; no overflow beyond 3 is displayed. — `battle-20260907-181914/REVIEW.md` Owner Turn 14 (also seen in Batch 2, `battle-20260907-025604`) — DIRECT.

### Q39 (Stadiums — replacing an existing Stadium with a new one)
- A Stadium already in play (Mesagoza) was replaced by a newly played Stadium (Area Zero) mid-battle with no apparent restriction. — `battle-20260907-181914/REVIEW.md` Opponent Turn 9 — DIRECT (though this is the same player replacing their own prior Stadium; it does not by itself test replacing an *opponent's* Stadium).

### Context / not directly a listed question but notable
- An Ability that disables other Basic Pokémon's Abilities ("Power of Alchemy," Alolan Muk) visibly suppressed **both** copies of an opposing Ability ("Legendary Pulse" on two separate Suicune ex) at once, with persistent on-screen "disable" icons, and no further triggers were credited afterward. — `battle-20260907-181914/REVIEW.md` — DIRECT.
- An Ability ("Sticky Membrane," Goomy) displayed a rules message that the opponent's Active Pokémon's attacks cost one additional Energy while Goomy is Active — a card-specific cost-increase effect, not one of the listed questions but worth flagging as a mechanic type. — `battle-20260907-031007/REVIEW.md` Opponent Turn 5.
- Healing effects (Watch Over) were repeatedly capped at the target's max HP (e.g., 140→150 showed only "effective 10" heal even though the base heal is 20) — confirms overheal is capped, not wasted/rolled over. — `battle-20260907-031007/REVIEW.md` Owner Turn 10 — DIRECT.

---

## Batch 4: split-battle 220914-221051 (this is the video behind Batch 1's mechanics-run-2.log), battles 221914, 222326

### Q15 (deck-out is not a loss) — CONFIRMED with exact on-screen text
- The game displayed the literal message **"No cards left in deck; unable to draw cards"** on the draw step, and play simply continued (turn proceeded normally, no loss was triggered) — happened twice in the same battle (owner's Turns 11 and 13). — `battle-20260907-220914-221051/REVIEW.md` — DIRECT (exact UI string quoted). Corroborates the softer observation in Batch 2 (`battle-20260907-014933`, "the game reports no cards left in the owner's deck") with the precise message text.

### Q20 (attack resolution / KO timing — does the rest of an attack's effect still resolve after its damage KOs the target?) — CONFIRMED yes
- "Turbo Shark deals literal 70 to Rookidee 60, leaving it at 0. **The attack's post-damage effect still resolves** and attaches Water from the Energy Zone to the center Benched Magikarp" — i.e., even though the attack's damage Knocked Out its target, the attack's separate secondary effect (attaching Energy to an unrelated Pokémon) still executed afterward in the same action. This happened on 3 separate uses of the same attack across the battle (Turns 3, 5, 11), always resolving its Energy-attachment effect regardless of whether the hit was lethal. — `battle-20260907-220914-221051/REVIEW.md` — DIRECT. This is the video behind Batch 1's `mechanics-run-2.log` (`TURBO_SHARK ... rookidee_ko=true ... forced_attachment=1Water->Magikarp`), now fully explained: it is Turbo Shark's own printed secondary effect, not an anomaly.

### Q38 (Tool damage reduction) — exact numbers, now identified: "Metal Core Barrier" is a flat −50 reduction
- Same Tool, two different attacks, same reduction both times: **Wild Swing** nominal 60 → Metal Core Barrier reduces it to literal **10** (−50); later **Mega Blaster** nominal 140 → Metal Core Barrier reduces it to literal **90** (−50). Confirms Metal Core Barrier is a flat, attack-independent −50 damage reduction Tool. — `battle-20260907-220914-221051/REVIEW.md` Turns 7 and 13 — DIRECT. (This is also the video behind Batch 1's log lines `protected_damage=10 unprotected_damage=60` and `protected_effective_damage=90 ... unprotected_damage=140`.)
- Separately, an attack ("Wild Swing") that discards a chosen damaged Benched Pokémon **also discards that Pokémon's attached Tool** along with it (Elegant Cape went to discard together with the Pokémon) and its attached Energy — confirms discarding a Pokémon via an effect takes its Tool and Energy with it, same as a normal KO would. — `battle-20260907-220914-221051/REVIEW.md` Turn 7 — DIRECT.

### Q44 (coin flips — effect capped by available resources, not an error)
- "Team Rocket Grunt" flipped 3 heads then 1 tails (a "discard 1 Energy per heads, up to some max" style effect); the target Pokémon (Gyarados) had only 2 Energy attached, and **"the observed result removes both; there is no third Energy available to discard"** — the effect simply discards what exists rather than erroring or discarding from elsewhere. — `battle-20260907-220914-221051/REVIEW.md` Turn 8 — DIRECT.

### Q42 (Sabrina — who chooses the replacement Active) — CONFIRMED twice, independently
- Both times Sabrina was played, the **caster's opponent** (i.e., the player being forced to switch) is the one who selected which Benched Pokémon became the new Active — not the caster. Instance 1: "the opponent actually plays Sabrina; owner selects and promotes the one-Psychic Houndstone." Instance 2 (different battle/decks): "The opponent actually plays Sabrina. The recorder switches Active [chooses which Bench Pokémon comes in]." — `battle-20260907-221914/REVIEW.md` Turn 6; `battle-20260907-222326/REVIEW.md` Turn 7 — DIRECT, corroborated twice.

### Q16 (attack sequencing — an attack's own cost/side-effect resolves after its damage)
- "Soul Shot visibly applies 30 [damage] before the required hand discard animation" — the attack's own listed cost (discard a card from hand) is paid after damage is dealt, not before. — `battle-20260907-221914/REVIEW.md` Owner Turn 3 — DIRECT.

### Q39 (Stadium symmetry, type-scoped) — further corroboration
- "Peculiar Plaza": printed effect "the Retreat Cost of Psychic-type Pokémon is two less" — applied to a Psychic-type Pokémon (Meloetta) regardless of which player controlled it, consistent with the earlier "Starting Plains" symmetric confirmation (Batch 3). — `battle-20260907-221914/REVIEW.md` Opponent Turn 4 — DIRECT (though only one side had a qualifying Pokémon in this clip, so it doesn't independently re-test both sides).

### Context / not directly a listed question but notable
- An attack that deals damage based on the attacker's own hand size ("Hand Kinesis," printed as 20-per-card) produced 160/180/200 across three uses as the caster's hand grew from 8→9→10 cards — consistent with a 10-card hand cap (200/20=10) without itself testing what happens beyond 10. — `battle-20260907-221914/REVIEW.md` — DIRECT numbers / INFERRED hand-size back-calculation.
- A specific evolved-Pokémon Ability text ("Aerodactyl ex... Primeval Law") produces an on-screen notice "Can't play Pokémon from the hand to evolve Active Pokémon" — the reviewer flags this is an effect announcement, not a failed user action; i.e., some Pokémon's Abilities impose their own extra evolution restriction beyond the standard rules, surfaced via a specific UI message. — `battle-20260907-222326/REVIEW.md` Opponent Turn 5 — DIRECT.
- Sand Slammer (Checkup ability, corroborating Batch 1) again confirmed hitting **every** opposing Pokémon (Active + all Bench) for 10 each, at two separate Checkups in the same battle, fully consistent with Batch 1's flygon-video findings. — `battle-20260907-222326/REVIEW.md` — DIRECT.
- Revenge's 40+60=100 conditional-boost branch (triggers off "a Pokémon was KO'd by attack damage during the preceding turn") reconfirmed again in a third independent battle. — `battle-20260907-222326/REVIEW.md` — DIRECT.

---

## Batch 5: battles 224312, 232035, log-scroll (post-match text log)

### Q21 (Rocky Helmet-style retaliation — does it fire if the holder is KO'd by that very attack?) — CONFIRMED YES, high-value finding
- "Linear Attack does literal 50 to Hydreigon 50→0. **Rocky Helmet triggers and deals 20 to the attacking Gabite**, which settles at 60/80." Hydreigon (Rocky Helmet's holder) was simultaneously Knocked Out by that exact attack (50 damage on 50 remaining HP), and the retaliation **still fired and dealt its 20 damage to the attacker** afterward. This directly answers Q21: an "on damaged by an attack" retaliation effect still resolves even when that same attack Knocks Out the holder. — `battle-20260907-224312/REVIEW.md` Owner Turn 9 — DIRECT (explicit before/after HP on both sides: Hydreigon 50→0, Gabite 80→60).
- Earlier in the same battle, the same Rocky Helmet (attached first to Deino, carried through its evolution into Hydreigon — confirming Tools persist through evolution, corroborating Q29) retaliated normally (non-lethal case) after Munchlax's attack: "Deino settles at 50; Rocky Helmet then damages Munchlax 50→30" (a 20-point retaliation). — `battle-20260907-224312/REVIEW.md` Owner Turn 3 — DIRECT.
- Contrast with Batch 1's Cursed Jewel: Rocky Helmet's retaliation is *immediate* (same-attack resolution), unlike Cursed Jewel's *delayed* next-turn self-buff — these are two different mechanic shapes and should not be conflated when answering Q21.

### Q6 (Energy Zone on P1's very first turn) — CONFIRMED: no current Energy exists yet, only the "next" preview
- "As the first player, the opponent has no current generated Energy: **the large Energy Zone is empty and only the small next-[type] preview is visible**." — direct, explicit confirmation that on the very first turn of the game (the player going first), there is no "current" generated Energy at all yet — only the "next energy" preview slot is populated. — `battle-20260907-232035/REVIEW.md` Opponent (=P1) Turn 1 — DIRECT.

### Q31 (do Trainer-forced switch effects count as "retreat"?) — CONFIRMED: no
- "Opponent plays Sabrina, forcing owner to switch Oricorio to Team Rocket's Raticate ex; **this is a Supporter-forced switch, not a retreat**." Explicit reviewer statement distinguishing the two mechanisms. (Relevant because retreat has its own restrictions/costs — a forced switch via Sabrina is a separate mechanism and, consistent with all observed Sabrina instances, costs no Energy and is not blocked/enabled by retreat-specific rules.) — `battle-20260907-232035/REVIEW.md` Turn 7 — DIRECT.

### Q11 (Pokémon Checkup — occurs after every single turn, not just when a status is active)
- The post-match Battle Log text scroll shows **three distinct "Checkup" entries within the battle's first ~75 seconds**, spanning only a few turns in which **no Poison/Burn/Sleep/Paralysis was ever in play** — confirming the Checkup step is logged as a discrete event after every turn regardless of whether any status condition exists to process. — `log-scroll/REVIEW.md` "Corrections and duplicate handling," rows 26/31/37 — DIRECT (this is a textual, exact on-screen log entry, arguably the single most reliable evidence type in this dataset since it is the game's own structured record rather than a frame reading).

### Q12/Q20 (point-per-KO, from an authoritative source: the game's own post-match log text)
- The structured post-match log records exact point events as literal text, e.g. "`Got 1 point`, `Points 2 > 3`" for a regular (non-ex) Pokémon KO (Dewott) — reconfirms 1 point per regular-Pokémon KO from the most reliable evidence type available (exact UI log text, not a frame reading). — `log-scroll/REVIEW.md` — DIRECT.

### Context / not directly a listed question but notable
- "Thieving Incisors" is an Ability that triggers specifically **on evolution** (moving an Energy from an opposing Pokémon to the newly-evolved one) — an example of an evolution-triggered Ability distinct from "once per turn" or "on Energy attachment" triggers; relevant context for Q36 (triggered-ability timing) though not one of the exact listed trigger types. — `battle-20260907-232035/REVIEW.md` Owner Turn 6 — DIRECT.
- "Electromagnetic Wall" (Jolteon ex's ability, triggers on the *opponent's* Energy Zone attachment) fired identically whether the opponent attached to their Active or a Benched Pokémon — an ability that reacts to the opponent's own action can target/apply to a Benched recipient. — `battle-20260907-232035/REVIEW.md` — DIRECT.
- Recoil-style self-damage from an attack ("Roar in Unison": attach 2 Energy + deal 30 damage to the user itself) occurred three times without ever being lethal in this battle — confirms self-damaging attacks are a real mechanic, but this battle doesn't test the "recoil KO gives opponent the point" part of Q20. — `battle-20260907-224312/REVIEW.md` — DIRECT (occurrence) / not conclusive for the KO-attribution question.
- Lucky Ice Pop's "Heads = returns to hand, Tails = discarded, heal happens either way" pattern (flagged in Batch 2) was reconfirmed on 5 more coin flips across 2 turns in this battle (Heads, Heads, Heads, Heads, Tails) — strengthening that generalization. — `battle-20260907-224312/REVIEW.md` Turns 5, 7 — DIRECT per-instance.

---

## Batch 6: previously-finished-audit battles 023151, 225430, 230007

### Q17 (do attacker-side damage bonuses apply to an attack's Bench-spread component?) — nuanced, effect-text-dependent
- Same attack ("Electrispark"), two components in one use: **Active-target damage got both a Tool bonus (Clemont's Backpack, +20) and a Stadium bonus (Training Area, +10)** — 40 base + 20 + 10 = 70 — while the **Bench-spread component of the same attack only got the Tool bonus, not the Stadium bonus**: printed 10 + Backpack's 20 = 30 (no +10 Training Area). Reconfirmed on a later use: Active hit again got Training Area's +10 (40→50 total), while the Bench-spread stayed at the plain printed 10 with no Stadium bonus. — `battle-023151/REVIEW.md` Turns 5, 7 — DIRECT (exact arithmetic breakdowns given by the reviewer, tied to on-screen totals). **Conclusion: whether a damage bonus reaches an attack's Bench-spread portion depends on that specific bonus's own printed text (a Tool bonus here did; a Stadium bonus here didn't) — this is not a fixed universal rule and must be checked per effect.**

### Q39 (Stadium effects are symmetric) — now confirmed for a damage-boosting Stadium, not just HP boosts
- **Training Area** (played by the owner) added +10 not only to the owner's own attacks but also to the **opponent's** attack: "Training Area increases High Jump Kick from 50 to 60" for the opponent's Combusken. This extends the Q39 symmetry finding (previously only seen for max-HP-boosting Stadiums) to a Stadium that boosts attack damage. — `battle-023151/REVIEW.md` Opponent Turn 6 — DIRECT.

### Q21 (retaliation-on-damage Tools fire even through a lethal/simultaneous KO of the holder) — now confirmed 3+ times across different decks/battles, including a full resolution-order chain
- **Battle 225430, most detailed instance:** Sunny Scorching (30 dmg) Knocks Out a 20-HP Electrode holding Rocky Helmet AND (separately) about to also have a Burn applied. The reviewer's frame-by-frame order is explicit: **(1)** attack damage lands and KOs Electrode, **(2)** Burn is "applied after the hit" (does not affect this KO), **(3)** Rocky Helmet's retaliation then fires 20 onto the attacker (Castform, already at 20 HP) — **this retaliation is itself lethal, KO'ing Castform** — **(4)** a further on-KO Ability ("Destiny Burst") then also resolves for 70 more onto the already-zero Castform (no further effect, it's already gone). Final: each side gets exactly 1 point (Electrode's KO for the owner, Castform's KO for the opponent) — i.e., **a Tool retaliation and an Ability trigger can both queue and resolve in sequence after an attack, even against a target(s) already Knocked Out, and even when the retaliation itself causes a second, independent KO in the same action chain.** — `previously-finished-audit/battle-225430/REVIEW.md` Turn 5 — DIRECT (exact HP numbers and explicit before/after/sequence language throughout).
- Reconfirmed non-lethally in the same battle: "Rocky Helmet deals 20 to Mega180→160, then Destiny Burst deals 70 more to 160→90" after the holder (second Electrode) was KO'd by Mega Burning — same order, this time without a second KO. — `battle-225430/REVIEW.md` Turn 7.
- Third independent confirmation, different deck: "Submarine Blow's 40 becomes a literal 60 through Fighting Coach, knocking out Heatmor; Rocky Helmet retaliates for a literal 20 and leaves Lucario at 80" — Heatmor (Rocky Helmet's holder) was KO'd by the attack, and the retaliation still fired onto the attacker afterward. — `battle-230007/REVIEW.md` Turn 3 — DIRECT.

### Q22/Q23 (Burn — 20 per Checkup, coin-flip cure) — reconfirmed extensively, all outcomes shown
- Multiple full Burn cycles shown with both coin outcomes: "Lucario Tails after the first 20 and remains Burned, then Heads after the second 20 and recovers; Gallade Tails after the first 20 and remains Burned, then Heads after the second 20 and recovers." Also "Sunny Scorching deals 30 ... applies Burn. Burn Checkup deals 20 more ... The Burn coin is visibly Heads, and Voltorb recovers." All instances: exactly 20 damage per Checkup, Heads cures, Tails continues. — `battle-230007/REVIEW.md`, `battle-225430/REVIEW.md` — DIRECT, several independent instances.
- Burn is applied "after the hit" that inflicts it, i.e., the attack's own damage resolves fully (including any KO check) before the Burn condition is applied to the survivor — consistent with Poison/Burn being separate from the attack's immediate damage application. — `battle-225430/REVIEW.md` — DIRECT.

### Q16 (damage formulas — additional confirmed scaling examples)
- "Gallade uses Energized Blade. Its printed formula is 70 plus 20 per Energy attached to the opponent's Active. Mega holds one Fire ... so the displayed damage is 90" — another attack whose damage scales off the *defender's* attached-Energy count (same pattern as Indeedee ex's Psychic, Batch 2/3), reconfirmed with exact arithmetic across multiple turns (repeated 90 twice with 1 Fire on the defender each time). — `battle-230007/REVIEW.md` Turns 10, 12 — DIRECT.

### Context / not directly a listed question but notable
- A "Mega [X] ex" evolution (Mega Manectric ex) evolved directly from a Basic Pokémon (Electrike) while that Pokémon was on the Bench, in the same turn the Active Pokémon (a different, already-evolved Pokémon) still attached Energy and attacked normally — i.e., this turn was not ended or restricted by the Mega Evolution occurring. This doesn't directly test "does Mega-evolving your Active end your turn" (physical TCG's XY rule) since the Mega evolution happened on the Bench, but it's a data point that a Mega Evolution elsewhere on the board that turn does not prevent further normal actions. — `previously-finished-audit/battle-023151/REVIEW.md` Turn 5 — DIRECT for what's shown; INFERRED/incomplete for the Q30 question itself (doesn't test evolving the *Active* Pokémon into its Mega form and then trying to also attack with it the same turn).
- Tool persistence through evolution reconfirmed again: Elegant Cape stayed attached (and its HP bonus recalculated) through the Electrike→Mega Manectric ex evolution. — `battle-023151/REVIEW.md` — DIRECT.

---

## Batch 7: previously-finished-audit battles 232955, 234514

### Q22 (Burn — checkup damage is unconditional; the coin only affects future persistence, not the current hit) — clean confirmation
- "The literal checkup coin is Tails, but the knockout is already determined" and, in a second instance, "The literal checkup result is Tails, but recovery cannot prevent damage already dealt" — both explicitly show that Burn's 20 Checkup damage is applied first/unconditionally, and the coin flip only determines whether Burn continues into the future — it cannot undo or prevent the damage that Checkup already dealt (including when that damage is lethal). — `battle-232955/REVIEW.md` Turns 5, 9; `battle-234514/REVIEW.md` Turn 8 ("Checkup deals 20 before the coin; Heads and a recovery message follow, but Kirlia has already reached lethal damage and is removed") — DIRECT, three independent instances with clean, quotable reviewer language.

### Q42 (Cyrus — confirmed exactly as the question describes it)
- "Cyrus is played, pulling the damaged 10-HP Mewtwo with one Psychic back Active" — the caster chose the opponent's damaged Benched Pokémon and forced it into the Active slot, precisely matching the assumed Cyrus behavior in Q42. — `battle-234514/REVIEW.md` Turn 12 — DIRECT.

### Q38 (Tool-based retreat cost reduction, distinct from Trainer-card reductions like X Speed)
- "Small Balloon" (a Tool, not a Trainer card): "the Tool's readable text reduces retreat cost by one," making a printed 1-cost retreat free. Later removed by Field Blower. — `battle-232955/REVIEW.md` Turn 2, Turn 7 — DIRECT. Broadens the Q31/Q38 evidence base beyond Trainer-card retreat reduction (X Speed, Leaf) to Tool-based reduction as well.

### Q39 (Stadium symmetry) — third independent confirmation
- "Starting Plains: the Stadium gives 20 HP to Basic Pokémon on both sides. Both Mega Diancie ex cards are Basic and gain 20; Stage 2 Mega Blaziken does not [gain HP]." — `battle-232955/REVIEW.md` Turn 8 — DIRECT.

### Q41 (search effects with no valid target)
- "Poké Ball explicitly finds no eligible target" when no Basic Pokémon remained in the deck — the effect simply resolves as a whiff (Trainer card still used/discarded) rather than being blocked from being played or causing an error. — `battle-234514/REVIEW.md` Turn 8 — DIRECT.

### Context / not directly a listed question but notable
- A team-wide Energy-scaling attack was observed: "Brilliant Storm ... `40 + 20 per Psychic Energy attached to all of your Pokémon`" — confirmed exactly at 120 (4 total team Psychic) and 140 (5 total team Psychic) across two turns. This is a third distinct damage-scaling pattern seen in this dataset (attacker's-own-Energy scaling, defender's-Energy scaling, and now attacker's-team-wide-Energy scaling), all resolving exactly per printed formula with no unexplained deviation — useful general confirmation that Q16's damage arithmetic reads correctly on screen across many formula shapes. — `battle-232955/REVIEW.md` Turns 6, 8 — DIRECT.
- Mega Evolution ex KO = 3 points reconfirmed again ("the final Mega Diancie knockout awards three points under the readable Mega Evolution ex rule"). — `battle-232955/REVIEW.md` Turn 9 — DIRECT.

---

## Batch 8: previously-finished-audit first-altaria, second-altaria

### Q25 (evolution removes Special Conditions) — CONFIRMED with exact on-screen text
- A Trainer effect ("Quick-Grow Extract") evolved a **sleeping** Bulbasaur into Ivysaur, and "the game explicitly reports that **Ivysaur recovered from being Asleep**" — an explicit on-screen cure message tied directly to the evolution. — `first-altaria/REVIEW.md` Opponent Turn 3 — DIRECT (exact UI message quoted).

### Q27 / Q11 (Sleep flip timing at Checkup; interaction with other Checkup damage that KOs the sleeper first)
- Standard case: Sing put Bulbasaur Asleep; "the between-turns Sleep check is Tails, so Bulbasaur remains Asleep" — sleep-check coin flip confirmed at Checkup, Tails = stays asleep. — `first-altaria/REVIEW.md` — DIRECT.
- Standard recovery case: Sleepy Lullaby put Oricorio Asleep; "the coin is visibly Heads, and the game reports that **Oricorio recovered from Sleep**" — exact cure message again. — `second-altaria/REVIEW.md` Owner Turn 1 — DIRECT.
- **Important ordering case:** on a later turn, Sleepy Lullaby put a 10-HP Oricorio to Sleep, and a Benched Darkrai's Checkup-damage Ability ("Bad Dreams," which only damages a *sleeping* opposing Active) then Knocked Out that same Oricorio during the same Checkup resolution — and **"No Sleep check occurs because Oricorio leaves play"** before the sleep-flip step would happen. A second Darkrai's Bad Dreams "also announces, but there is no second live-target HP transition" (the target is already gone). This shows Checkup-time damage effects (here, an Ability) can remove the sleeping Pokémon **before** the sleep-recovery flip is reached, in which case the flip simply never happens for that (now-KO'd) Pokémon; a second copy of the same triggered Ability still "announces" but has no further effect once the target is gone. — `second-altaria/REVIEW.md` Owner Turn 3 — DIRECT (explicit reviewer statement about the skipped check).

### Q13 (loss with empty bench, immediate) — further confirmation
- After the winning Knock Out, "Cool Hand has no Benched Pokémon to promote, so the battle immediately ends" — the game did not pause for a promotion prompt at all when none was possible; it went straight to the win. — `first-altaria/REVIEW.md` — DIRECT.

### Q17 (Stadium attack-damage bonuses apply to the Active-target hit only, not to Bench damage) — now stated explicitly by the reviewer, not just inferred from arithmetic
- "Electrode uses Random Spark for 30 on the owner's left Darkrai [a Benched Pokémon], moving it 100→70; **Training Area does not add damage because the attack targets the Bench**." This is the reviewer directly stating the rule behind the arithmetic (matches and generalizes the nuance already found in Batch 6 with Electrispark). — `second-altaria/REVIEW.md` Opponent Turn 8 — DIRECT.

### Q16 (damage formulas) — a fourth distinct scaling variable confirmed: attacker's own score/points
- "Lightning Accelerator['s] readable text is 80 plus 30 for each point the user has obtained." Confirmed at three different point totals in the same battle: 0 points → base 80 (no Stadium yet); 1 point + Training Area → 80+30+10 = **120**; 2 points + Training Area → 80+30×2+10 = **150**. All three matched the displayed damage and resulting KOs exactly. Combined with the other scaling types already documented (attacker's-own-Energy, defender's-Energy, team-wide-Energy, attacker's-Bench-count), this is strong general confirmation that damage arithmetic reads correctly and consistently on screen regardless of which variable a given attack's formula scales on. — `second-altaria/REVIEW.md` Turns 4, 6, 10 — DIRECT.
- Also: "Mega Harmony deals 40 plus 30 for each owner Benched Pokémon" — confirmed at 100 (2 Bench) +10 Training Area = 110, and separately at 140 (3 Bench) +10 Training Area = 140 total, twice. — `first-altaria/REVIEW.md`; `second-altaria/REVIEW.md` Turns 7, 9 — DIRECT.

### Q42 (Sabrina / Cyrus) — further independent confirmations (now 4 total instances for Sabrina)
- Sabrina: "The opponent chooses the fresh 180-HP Mega Manectric as the new Active" — again the *target* of Sabrina (not its caster) chose the replacement. — `second-altaria/REVIEW.md` Owner Turn 9 — DIRECT.
- Cyrus: "BigGutSnorlax first plays Cyrus, whose readable text switches one damaged opposing Benched Pokémon into the Active Spot... the damaged 70-HP Darkrai is the only eligible damaged owner Bench Pokémon, so Cyrus pulls it Active" — matches Q42's Cyrus description exactly (caster picks target's damaged Benched Pokémon). — `second-altaria/REVIEW.md` Opponent Turn 10 — DIRECT.

### Context / not directly a listed question but notable
- A lethal attack resolved before the defending player got any further action window: "It Knocks Out Darkrai70 before the owner receives another action window, so Small Balloon cannot enable the planned retreat" — confirms retreat is strictly a main-phase action on your own turn; there is no way to retreat "in response to" an incoming/resolving attack. — `second-altaria/REVIEW.md` Opponent Turn 10 — DIRECT.
- "Protective Poncho ... visibly activates its prevention against opposing attack and Ability damage" only once its holder moved from Active to Bench — a Tool whose protective effect is specifically scoped to the Benched state. — `second-altaria/REVIEW.md` Opponent Turn 8 — DIRECT.
- Heavy Helmet's "take 20 less damage" condition (tied to the holder's retreat cost) was shown turning on/off across an evolution, reconfirming these Tools have real conditional-activation logic rather than being flat modifiers. — `first-altaria/REVIEW.md` — DIRECT.

---

## Questions this file's evidence sheds little or no light on

Scanning across all 41 reviewed files, the following question numbers have **no or only extremely weak evidence** in this batch of files (either never arose in the recorded games, or arose but the reviewers explicitly flagged the underlying fact as hidden/unresolved):

- **Q1** (deck construction / Energy-type declaration rules) — never addressed; these are battle-in-progress reviews, not deck-builder observations.
- **Q2/Q3** (opening-hand mulligan mechanics, simultaneous/face-down setup) — setup is shown as already resolved in every file; no mulligan or redraw event ever appears.
- **Q4** (how "who goes first" is presented — coin flip visibility) — every file states who went first but none describes seeing an actual coin-flip animation or its timing relative to setup.
- **Q10** (timers — per-turn/total time limits, timeout behavior) — never observed; no file mentions a clock running out.
- **Q14** (simultaneous win conditions / true ties) — no file shows a genuine simultaneous 3–3 or "both reach 3 in the same instant" case; the closest (Batch 2's Hailstorm double-KO) was a 1-point/2-point split, not a tie.
- **Q26** (poison-damage-boosting effects like Nihilego) — no such card appeared in any reviewed battle.
- **Q28** (evolution restrictions beyond the basics already well-covered — e.g., twice-in-one-turn on the same Pokémon) — not directly tested; only ordinary single evolutions are shown.
- **Q30** (Mega Evolution "ends your turn" rule specifically) — only indirectly touched (Batch 6: a Bench Mega-evolution didn't halt the turn); no file shows evolving the *Active* Pokémon into a Mega and then attempting to also attack with it that same turn.
- **Q33** (effects on the Active that end when it moves to Bench) — not directly tested; no file shows an Active-only buff/debuff persisting or clearing on a subsequent switch.
- **Q35** (identical-named Ability stacking, e.g. two copies of the *same passive/static* Ability both active at once) — Batch 3/6 showed two separate Pokémon instances each independently *using* a triggered/activated Ability once per turn, but no file shows two simultaneous *passive* same-name Abilities stacking their effect.
- **Q40** (Fossils) — no Fossil card appeared in any reviewed battle.
- **Q43** (what exactly is public — hand size, deck count, discard, Energy Zone) — implicitly touched everywhere (reviewers routinely note opponent hand/deck contents are hidden while board state, discard, and Energy Zone are public) but never stated as an explicit rules summary.
- **Q45** (copy-attack effects like Mew ex Genome Hacking) — no such card appeared.
- **Q48** (effects needing a target that doesn't exist, e.g. switch with empty Bench) — not tested; every switch/forced-switch effect in these files had a valid target available.
- **Q49** (Ranked vs. casual vs. Solo/AI rules/timer differences) — several files flag mode ambiguity (Solo/AI vs. manual PvP) as an *evidence* limitation, but none shows an actual rules or timer difference between modes.
- **Q50** (official rule changes/errata with dates) — out of scope for battle footage entirely.

---

## Batch 9 (final): trial-manectric, trial-revavroom

### Q37 (Items are unlimited per turn) — CONFIRMED directly
- The Supporter "Clemont" fetched two copies of the Item "Clemont's Backpack" into hand, and **both copies were played in the same turn**, each applying its own separate "+20 attack" modifier (stacking to +40 total on top of base). This is a clean, direct confirmation that Item-type Trainer cards are not limited to one per turn (unlike Supporters). — `trial-manectric/REVIEW.md` Owner Turn 5 — DIRECT (exact damage arithmetic ties both plays to two separate +20 contributions: "40 base + 20 + 20 from two Clemont's Backpacks + 10 from Training Area = 90").

### Q17 (Stadium attack-damage bonus vs. Bench damage) — 4th independent confirmation, now with a clean Tool-vs-Stadium contrast in one turn
- Same turn, same attack: the **Tool-based** bonuses (two separate Clemont's Backpack plays, +20 each) applied to **both** the Active-target hit ("40 base + 20 + 20 ... = 90") **and** the Bench-spread hit ("10 base + 20 + 20 ... = 50" to each of three Benched Pokémon), while the **Stadium** bonus (Training Area, +10) applied **only** to the Active-target hit — the reviewer states plainly: "Training Area does not add damage to Benched targets." This is now consistent across 4 separate battles/decks (Batches 6, 8, and here) with the same pattern: Tool bonuses reach Bench-spread damage, this particular Stadium's bonus does not. — `trial-manectric/REVIEW.md` Owner Turn 5 — DIRECT.

### Context / not directly a listed question but notable
- A Pokémon with two Tool slots (Revavroom, confirmed in Batch 2 as well) held two separate Sitrus Berries; when its HP checkup-healing condition was met, **both Berries triggered in sequence, each healing 30 and each being discarded independently** (20→50→80), rather than only one firing or both being blocked by the other's presence. — `trial-revavroom/REVIEW.md` Turn 6 — DIRECT.
- The attack-damage UI explicitly displays a **"Weakness 100"** banner/label when a Weakness-boosted attack resolves, rather than silently including it in a single number — i.e., Weakness's contribution is visibly flagged on screen, not merely inferable from arithmetic. — `trial-revavroom/REVIEW.md` — DIRECT.
- A Stadium with a repeatable, player-chosen effect ("Kid's Room") was used by the same player on multiple different turns in a row, including a turn where it explicitly reported "no card in the deck can be targeted" — reconfirms the "whiff, not a block" pattern for search-style effects with no valid target (consistent with Poké Ball/Mesagoza in earlier batches). — `trial-revavroom/REVIEW.md` Turns 4, 6, 8 — DIRECT.
- Mega Pokémon's zero retreat cost was reconfirmed again (Mega Manectric ex retreated keeping its attached Energy because its displayed retreat cost was zero). — `trial-manectric/REVIEW.md` Owner Turn 5 — DIRECT.
