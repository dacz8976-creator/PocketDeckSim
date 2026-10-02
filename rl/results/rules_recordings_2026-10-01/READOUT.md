# Readout: Oct 1 rules-test recordings (7 videos)

For Dustin and the coordinator. Built from Sol's reviews (lead-accepted), Astra's bounded check, Dustin's shot-list notes, and a code read of the switch candidate. Nothing was edited, committed or played.

Words used here:
- **The simulator** is the engine. **The official engine** is main-d363ba8 (engine tree 9c84fef). **The switch** is the rules switch being prepared; its candidate commit is 5a18d31.
- **Repair A** is Victory Star after a Confusion heads. **Repair B** is coin-flip damage prevention (the cut after Weakness, the queued choices of six helpers, and Chase Order's coin path).
- **Gated** means the switch leaves a case on the old path on purpose, because the game had not been seen yet. Dustin's rule (Oct 1) is the other way round: "if there is a plain reading of the text, the engine build should go with that, unless there is contradicting evidence. Not the other way around". So every gated case below that has a plain reading goes to the next switch on that reading. Footage is welcome as proof, but nothing waits on it.
- **Will pending** means Will was played this turn and its forced heads has not been used yet.
- **Seen** means it is on screen in the review's frames. **Inferred** means it was worked out (arithmetic, timing, card text). Inferences stay labelled as inferences.
- Times are seconds into each video. "T4" means global turn 4.

---

## 1. In plain words

**Is there a STOP before the pin? No.** Nothing in today's seven videos contradicts repair A, repair B, kd's follow-ons or F1-F7.

- One video backs repair A directly. In 204634 (T4, 184-205 s), a Confused Team Rocket's Moltres ex flipped heads for Confusion. Heat Charged then flipped 0 heads and 3 tails. Victory Star was offered from the benched Victini and taken. The reroll gave 2 heads and 1 tail, and Moltres ended on 3 Fire. The candidate 5a18d31 does exactly this. The official engine offers no Victory Star while Confused, so Moltres would stay on 1 Fire. This is the third sighting after 202314 and 203025, and the first where the original batch had 0 heads.
- The simulator differs from the game in four places. In all four, the simulator also contradicts the plain card text, so they are bugs, not open questions. None is a part the switch fixes, and all four go to the next rules switch:
  1. **Victory Star with Confusion and Will pending** (210403, T14, prompt at 354-355). The game offered Victory Star. The simulator offers nothing, today and in the switch. The switch gates this case on purpose.
  2. **Will on a Confused attacker's own coins** (210403, T14). Will's text names coins "for the effect of an attack, Ability, or Trainer card", and the Confusion check is none of those. So Will waits for the attack's first coin. The footage shows it:
     - the Confusion coin landed "Heads!" at 342.0-342.75 s;
     - Will's banner "First coin flip will definitely be heads" then appeared on Heat Charged's own coin screen ("Flips: 3"), at 347.25-347.95 s, just before the first coin;
     - the three coins came up heads by 352 s.
     A 0.25 s frame check on Oct 1 found this, after Dustin pointed it out (`frames/f_342.50.jpg`, `frames/f_347.50.jpg`). The simulator wastes Will on a Confused attacker. It is older behaviour; the switch doesn't touch it.
  3. **Wild Swing into Meowth** (213822, T6, coin at 152). Carefree Steps covers "any damage ... by attacks", and Wild Swing is an attack. The game flipped the coin; the simulator never flips for Wild Swing. This is a named known limit the switch leaves for later.
  4. **Two Ariados** (213034, T5, 117-124). Each Ariados's Trap Territory adds 1 to the Retreat Cost, so two add 2. Grass Knot showed 160 on Moltres ex, which fits only if both count. The simulator counts one Ariados and would deal 130. This is outside the switch entirely.

**Today's three shot rows:**

| Row | What it verifies | Result | Where |
|---|---|---|---|
| Double Knock Out when the attacker went second (double-ko-second-player-promotes) | After an attack Knocks Out both Actives, who picks a new Active first: the attacker, or whoever went first? | **Pass**, with caveats | 203626: double KO at 229.5-241.5; promotion prompt to Dustin at 244.5; both promoted by 247.5 |
| Will, Confusion and Victory Star on the same attack (victory-star-confused-will) | What Will does to the Confusion coin and to the attack's coins, and whether Victory Star is offered (a gated case) | **Pass on all three look items** (the reroll wasn't taken) | 210403 T16 (376-389) and T14 (325-360; Will's banner at 347.25-347.95); 203626 T12 (327-347) for Will with a reroll and no Confusion |
| Gyarados's Wild Swing into Meowth's Carefree Steps (wild-swing-carefree-steps) | Does a Carefree Steps coin appear? (pass for the later fix) | **Pass** | 213822: Wild Swing at 143-145; coin tails at 152; 100 damage at 154 |

- **Double KO:** the opponent went first, Dustin went second and attacked (T8). Double Smash knocked out Zangoose. Zangoose's Counterattack then knocked out Darmanitan. The frame at 244.5 shows "Please choose a Pokemon to switch in" with Dustin's Bench highlighted and both Active spots empty. Dustin's note: "I chose my pokemon and then they did." So the attacker was asked first even though he went second. The simulator does the same. Caveats: it was Solo, not the friend battle the row asked for, so "the human is always asked first in Solo" isn't ruled out. The KO came from an Ability, not Rocky Helmet or Hoopa ex. The review's own text doesn't state the order; the frame and Dustin's note do.
- **Will, Confusion and Victory Star:**
  - Look item 1 (does Will force the Confusion coin?): **No.** Seen in 210403 T16: Will played (376), confirmed (378), Netherwing chosen (380), Confusion coin tails (384-386), attack did nothing (387-389). Astra confirmed. The simulator matches.
  - Look item 2 (is the attack's first coin heads?): **Yes, seen.** The Sol review's stills are 2-4 s apart and missed it. A 0.25 s frame check (Oct 1, after Dustin pointed it out) shows:
    - the Confusion coin "Heads!" at 342.0-342.75;
    - the Heat Charged splash at 343.5-344.75;
    - Will's banner "First coin flip will definitely be heads" on Heat Charged's own coin screen ("Flips: 3"), at 347.25-347.95, just before the first coin is flicked;
    - 3 heads at 352.
    So the Confusion check didn't use Will, and Will applied to the attack's first coin. That is also the plain reading of Will's text. The simulator wastes Will here, so it differs.
  - Look item 3 (is Victory Star offered?): **Yes.** Seen at 354-355 in T14. It was declined (inferred: the prompt fades at 357 and turn 15 starts at 360). The simulator offers nothing: it differs, in the gated case.
  - Reroll half: **not tested with Confusion** (the reroll was declined). Without Confusion, 203626 T12 shows Will is not reapplied to a reroll: the replacement's first coin was tails (345.5; 0 heads/1 tail at 346.5). That matches the simulator and Dustin's "Will does not apply on a re-roll".
- **Wild Swing:** Gyarados discarded both Benched Water Pokémon (Mega Sharpedo ex, Mega Gyarados ex, 145). Carefree Steps' text and a coin showed at 150, tails at 152, and 100 (20+40+40) on Meowth at 154. The simulator gives no coin. Not filmed: the row's suggested "discard none, Bench kept" version, and a heads.

---

## 2. Shot rows in detail

### 2.1 double-ko-second-player-promotes: Pass (203626)

- **What it checks:** after one attack Knocks Out both Actives, which player is asked to promote first. The earlier recording (225430) couldn't separate "attacker first" from "first player first", because Dustin was both.
- **Which video:** Dustin's capture names "20261001_20326000". It is read as 20261001_203626000 (see section 5 for how).
- **What the footage showed** (Sol review, plus the overview frame read by the findings):
  - Seat: the opponent went first. Dustin went second (setup 0-26; results at 365.8 say "went second").
  - T8, Dustin's turn: Darmanitan's Double Smash flipped 1 heads (Victory Star offered and declined, 220.5-226.5). The 40 knocked out Zangoose (40 HP left).
  - Zangoose's Counterattack (an Ability) then did its 20 and knocked out Darmanitan (20 HP left). Both Active spots were empty and the score went 1-1 (229.5-241.5).
  - 244.5: "Please choose a Pokemon to switch in", Dustin's Bench highlighted, both Active spots empty. By 247.5 Dustin's Darmanitan and the opponent's Skiploom are both Active.
  - Dustin: "I chose my pokemon and then they did."
- **The simulator:** after an attack, Knock Outs are sorted so the attacker's promotion comes first in either seat (apply_action_helpers.rs:895-899; the same in main and 5a18d31). It matches.
- **Limits:**
  - Solo, not a friend battle. Dustin was the attacker in both 225430 and 203626, so "the human is always asked first in Solo" is still possible.
  - After an attack, the attacker is also the turn player, so this can't separate "attacker first" from "turn player first". The simulator and rules/02 treat them as the same.
  - The cause was Counterattack, not Rocky Helmet or Hoopa ex. The simulator uses the same retaliation path for both.
- **The other six videos:** no double KO in any of them. All their Knock Outs were single, and only the Knocked-Out side promoted.
- **Changes:** a docs update only. rules/02 §7 (line 145) can cite 203626 next to 225430. The switch is not affected.

### 2.2 victory-star-confused-will: Partly tested (210403, plus 203626)

- **What it checks:** a case repair A gates (Confused attacker with Will pending), and what Will does for a Confused attacker. Setup: Master Plan's tails Confuses your own Moltres ex, then Will, then Heat Charged.
- **Footage, 210403** (Dustin's capture video):
  - T12 (281-290, 309-317): Master Plan's coin was tails, so Dustin's Moltres was Confused too. Later that turn the Confusion coin was tails and the attack did nothing. No Victory Star prompt, no self-damage. No Will was pending (both Wills still in hand).
  - T14 (325-360). The checker opened these native frames; they are not in the lead's or Astra's check sets.
    - Seen: Will played, with its banner (332). "Coin flip — Confused" heads (341.8). Heat Charged 3 heads, 0 tails (352). "Use the effect of Victory Star?" (354-355). Turn 15 starts at 360 with Moltres on 7 Energy (it had 4).
    - Inferred: the decline. No button press is shown, but turn 15 starts 3 s later, too fast for a 3-coin reroll, and 4 + 3 = 7 fits the kept batch.
  - T16 (373-390): second Will played (376), confirmed (378), Netherwing chosen (380). The coin labelled as the Confusion check came up tails (384-386) and the attack did nothing (387-389). No Victory Star prompt. Astra confirmed all of this.
- **Footage, 203626 T12** (no Confusion; Master Plan's coin was heads both times, so Darmanitan was never Confused):
  - Will played (327). Original Double Smash first coin heads (336.3), pair heads/tails (338). Victory Star offered (340.5) and taken. Replacement first coin tails (345.5), 0 heads/1 tail at 346.5, final tails/heads (347).
  - Seen: Will's guarantee did not carry to the reroll. Partly inferred: that Will forced the original first heads (a natural heads looks the same).
- **Dustin's ruling** (capture note): "Will does not apply on a re-roll or on confusion. It does apply on an attack after the confusion coin flip".
- **The simulator, by look item:**
  - Item 1 (Confusion coin not forced): **matches**. The Confusion gate's branches carry no coin record, so Will never touches them (attack_outcome.rs:590-604 at 5a18d31; 518-532 on main).
  - Item 2 (Will on the attack's first coin after a Confusion heads): **differs.** Seen at 347.25-347.95, and it is the plain reading of the card. On the old path the Confusion gate drops the coin record. force_first_heads then finds no coin, so Will isn't applied or used up and lapses at turn end (outcomes.rs:489-491; apply_action.rs:675-688, main 623-636). Same on main and 5a18d31.
  - Item 3 (Victory Star offer with Will pending): **differs.** The Will carve-out (`&& !state.has_pending_will_first_heads()`, apply_attack_action.rs:131 at 5a18d31) keeps the old path, which returns no offer (apply_action.rs:206-215). Main gives no offer for any Confused attacker (apply_action.rs:198-202). Pinned by the test confusion_with_will_pending_keeps_the_legacy_resolution_without_a_victory_star_offer (b4a_attack_batch2_test.rs:437).
  - Will and a reroll, no Confusion: **matches.** The reroll is a fresh batch with no forced heads (apply_action.rs:340-357), and Will is used up on the first batch (263-268). Pinned by will_forces_first_batch_only_and_is_consumed_before_reroll (victini_victory_star_test.rs:215-248).
- **Not filmed:** a reroll taken after a Confusion heads with Will pending. The plain reading settles it without footage:
  - Victory Star re-flips the attack's coins, and the Confusion check is not one of them, so no second Confusion check follows.
  - Will was used on the first batch, so the replacement is a fresh flip. 203626 shows this without Confusion, and Dustin says "Will does not apply on a re-roll".
- **Changes:**
  - Not a STOP. PLAN.md says this case "stays gated" (line 46), and the footage agrees with repair A's own rule: Confusion first, then an offer on the attack's coins.
  - By code reading only: deleting the term at :131 would send this case through repair A's path. There Will forces only the sampled attack batch (apply_action.rs:223-232) and the Confusion split stays unforced (:290-308). That matches Dustin's ruling, but only when a Victini is in play. Without Victini the old path still wastes Will, so that part needs its own fix.
  - Docs: rules/04 §9 and rules/09 (section 4).

### 2.3 wild-swing-carefree-steps: Pass (213822)

- **What it checks:** whether Carefree Steps flips for Gyarados's Wild Swing. Pass for the later fix: a coin appears.
- **Footage** (Dustin's turn 6; the lead checked 143/145/147/152/154/161):
  - Gyarados (4 Water) used Wild Swing into the Active Meowth with two Benched Water Pokémon and discarded both: Mega Sharpedo ex and Mega Gyarados ex (selected at 145, Bench empty at 147).
  - Carefree Steps' text over a spinning coin (150), "Tails!" (152), 100 on Meowth (154).
  - Inferred: the KO, from 100 damage against 50 HP and the 2-0 score at 161.
  - The two Mega ex left by discard and gave no points (opponent still 0 at 147).
  - Dustin: "Coin still applies. It is an attack so I don't know why you wouldn't apply it..."
- **The simulator** (5a18d31 and main):
  - No coin. With eligible Benched Water Pokémon, Wild Swing's outcome carries no damage (single_effect, apply_attack_action.rs:6423), so there is nothing to flip for.
  - The damage goes through discard_then_damage_choice (:311-326). That only takes the coin path for Chase Order (chase_order_attack, :329-343). Otherwise it queues a plain ApplyDamage (apply_action.rs:1284-1308; main 1253-1260).
  - Pinned by wild_swing_into_carefree_steps_pins_todays_behaviour_no_coin (meowth_carefree_steps_test.rs:390).
  - On tails the result matches (100, KO). The simulator only lacks the 50% heads branch.
- **Later fix:** branch claude/coin-prevention-round2 (head 78af4e8) adds Wild Swing's mechanic to discard_then_damage_choice's gate (apply_attack_action.rs:359-367 there). It is not in this switch.
- **Not filmed:** discarding none with the Bench kept (the row's suggested setup) and a heads. The simulator skips the coin on every Wild Swing choice (the pin test covers both), so the discard-two run reaches the same path.
- **The empty-Bench Wild Swing at 187-191** hit Typhlosion ex, which has no coin Ability, so it says nothing about the coin.
- **Changes:** not a STOP. It is a named known limit (PLAN.md line 61). rules/09's open entry can now cite [OBSERVED 213822]. What's new is the game's side, not the gap.

### 2.4 Other shot rows these recordings touch

- **victini-confused** (already resolved by 202314 and 203025):
  - 204634 T4 adds a third sighting of the heads case (see section 1). Two of its steps are inferred, not seen frame by frame:
    - "No second Confusion check between the batches": the gap between bracketing frames is about 1.5 s or less, too short for a separate Confusion overlay and flip.
    - "Victory Star accepted": the banner shows from the benched Victini at 197-198.
  - 210403 T12 is the tails half. The check corrected it to **neutral**: main and the candidate give the same visible result on a Confusion tails (no offer, nothing happens), so it can't favour repair A.
  - 204634-6 was also tagged victory-star-confused-will. That tag is wrong: no Will was pending that turn.
- **guarded-grill-after-weakness: still untested.**
  - 210403 T18 (420-426): Double Smash flipped 1 heads (40). The game showed 60 as Weakness damage, and Bronzong went 120 to 60. Bounded Field was in play, and Guard Press's −20 (printed at 404, used T17) was in force.
  - 40 × 2 − 20 = 60. Reducing first would give 40; ignoring the −20 would give 80. The 60 is seen; the order is arithmetic.
  - The check corrected this to **neutral for repair B**: a fixed −20 takes the same path on main and the candidate, and no coin cut was involved.
  - It is a second fixed-reduction confirmation of rules/02 step 4, after the Sept 21 Skarmory case. Don't mark the row passed.
- **heavy-helmet-retreat** (indirect only):
  - No Heavy Helmet appeared. 213034's Grass Knot shows two Ariados raising the cost an attack reads (see 3b).
  - The simulator's Heavy Helmet reads the same capped value (hooks/core.rs:706-712), so it would count one Ariados too.
  - The row's "engine" field says the simulator reads the printed cost. That is out of date: rules/04:103 records it fixed in 050cf51 (Sept 26).
- **carefree-steps-snipe:** not in any recording. 214736 had the cards (Gabite's Linear Attack, Greninja, and an opponent deck with Meowth). But Linear Attack's one use (165) hit Quilava, and Meowth only came out on T10 (319).
- **chase-order-carefree-steps:** not in any recording. Wild Swing uses the same discard-then-damage action, so 213822 is consistent with repair B's Chase Order fix by analogy only. It is not a Chase Order test.
- **victory-star-block-coin:** not in any recording. Dark Binding (204634) is an attack lock, not a block coin.
- **mimikyu-disguise-no-damage-attack:** 205658 only shows Mimikyu ex's text (306-315). Nothing attacked it.
- **greninja-shuriken-heavy-helmet / harden-hide-non-attack-damage:** neither card was in play.
  - 214736 T9 (289-297): Water Shuriken did a plain 20 to the Active Typhlosion ex.
  - Typhlosion ex is weak to Water and Greninja is a Water Pokémon (lib/card.py lookups by the finding, not stated in the review). So no Weakness was added to Ability damage. The review didn't frame this as a Weakness test.

---

## 3. Other rules observations

### 3a. The simulator matches

These are seen unless marked. Engine references are at 5a18d31 and unchanged on main unless noted.

**Victory Star without Confusion** (the path the switch leaves unchanged):
- The whole batch is replaced, and the original doesn't count:
  - 203626 T4: 0 heads/2 tails to 1 heads/1 tail, 40 damage (120-129).
  - 204634 T10 (342-350).
  - 210403 T4: 3 tails rerolled to 3 tails (99-110).
  - 214736 T6, T8, T10 (182, 240, 331).
  - In 205658 two cases can't show which batch decided the result. T3 had equal batches (1 heads/2 tails both); the original is at 104.7, the replacement at 114 and the settled board at 117, not the frames the finding cited. T11 had a 0-heads original. They still match.
- One Victory Star per turn across two Victini (seen absence of a second prompt): 203626 (180.5); 210403 (111-112).
- It resets each turn: 203626 T6 (171-180.5); 205658 T5, T7, T9, T13.
- It is offered on any result, including all heads: 205658 T7, T9, T13. The declines there are inferred from immediate resolution.
- It is never offered for a Trainer coin: Master Plan in 203626 (58.5-62, 271.5-277.5) and 204634 (148-161).
- Coins and a Victory Star offer still happen against a target with no Energy: 214736 T8 (238-246).

**Repair A's heads case:** 204634 T4 (see section 1). The candidate matches; main doesn't.

**Retaliation, Knock Outs, points, promotion:**
- Counterattack fires on a lethal hit (an Ability, first time observed); a zero-damage hit triggers none: 203626 (229.5-241.5; T6 171-180.5).
- Only the Knocked-Out side promotes after a single KO: every video.
- The game ends at 3+ points before any promotion: 205658 (391-404); 213034 (190-203).
- ex = 2 points; the circles stop at 3: 204634, 205658, 213034.
- No Pokémon left = loss at 2-1 points: 213822 (206-217). Inferred: that the empty board caused it. It is the only explanation the rules notes allow.
- An empty deck skips the draw and isn't a loss: 204634 (~472.5); 210403 (410-411, 439).
- An Ability KO of a Benched Pokémon scores at once, with no promotion, and the turn goes on: 214736 T7 (200-227). An Ability KO of an ex wins: 214736 (345-358).
- Wild Swing discarding two Mega ex gave no points: 213822 (145-161).

**Attack effects after lethal damage, before the KO:**
- Turbo Shark attached its Energy after knocking out Ogerpon: 213822 (94).
- Destructive Inferno's coins ran after lethal damage: 213822 (201.5); 214736 (177-194).
- In 214736 both Energy vanished before Gabite left play. Whether the attack or the KO cleanup removed them can't be told (2 heads = 2 Energy). The result is the same either way.

**Weakness and Bounded Field:**
- ×2 for a non-Mega attacker: 203626 (298-307, 347-356); 210403 (447: 260).
- +20 without the Stadium: 213822 (87-92, 187-191); 213034 (Flare Blitz 160 at 157.5-166).
- No Weakness on Ability damage: 214736 (289-297, above).

**Special Conditions and effects:**
- Evolution clears conditions and keeps damage and Energy: 203626 (85.5-88.5); 210403 (118); 214736 (69-70).
- Retreat clears Confusion: 204634; 210403 (412-414).
- Confusion persists across Checkups: 210403 (Bronzong T13-T19).
- Confusion heads doesn't clear Confused: 204634.
- Burn does 20 at Checkup, then a coin; both results were seen: 214736 (56-65, 119-126).
- Dark Binding locks only a Basic, and retreat or evolution ends the lock: 204634.

**Trainers and Abilities:**
- Flame Patch is separate from the turn's attachment: 204634, 205658, 210403, 213034.
- Misty puts one Water per heads on a target chosen first: 213822 (29-38). Its second use flipped 0 heads, and its target is unknown.
- Wallace: 213822 (68-78).
- Quick-Grow Extract: 213034 (61-70).
- Lucky Ice Pop heals every time; on tails it is discarded: 214736 (86-93).
- Rare Candy on the second turn: 214736.
- Netherwing is refused with 2 Fire: 205658 (193-194).
- Leftovers heals only the Active at the end of its owner's turn: 204634 (486-504).
- Full-Mouth Manner heals at the end of the opponent's turn: 204634 (543-547). The review said "start of its turn"; the frames show the end of the turn.
- Strange Singing works only from the Active Spot at the start of the turn: 205658.
- Giant Cape +20; Jump Kick 20 to the Bench: 210403.
- Guard Press −20 for one turn: 210403. Its expiry is inferred from the 260 at T20.

**Turn 1:** the first player attached no Energy: 203626, 213034, 213822. This is consistent with the rule, but the Energy Zone itself isn't shown.

### 3b. The simulator differs (each a candidate repair; none is part of this switch)

1. **Victory Star offer, Confused attacker with Will pending**
   - Where: 210403 T14, 354-355. Seen.
   - Simulator: no offer, today and in the switch.
   - Code: 5a18d31 apply_attack_action.rs:131 (Will carve-out in victory_star_waits_for_confusion_heads) → apply_action.rs:206-215. Main apply_action.rs:198-202. Test b4a_attack_batch2_test.rs:437. card_validation.rs:97 still calls it unverified.
   - Status: gated on purpose (PLAN.md:46, F2, F4). Next switch.
2. **Will wasted on a Confused attacker's own coins**
   - Where: 210403 T14. Will's banner is on Heat Charged's coin screen at 347.25-347.95, after the Confusion "Heads!" at 342. Seen in the Oct 1 frame check, and it's the plain reading of Will's text.
   - Simulator: Heat Charged's coins flip unforced (3 heads at 1/8 instead of 1/4), and Will stays unused until turn end.
   - Code: attack_outcome.rs:590-604 (main 518-532), prepend_nullifying_coin_gate; outcomes.rs:489-491; apply_action.rs:675-688 (main 623-636). Same on main and 5a18d31, with or without Victini.
   - Status: older behaviour, not named in the switch's open list. A new open item. Fix it together with item 1.
3. **Wild Swing skips Carefree Steps**
   - Where: 213822 T6, 150-154. Seen.
   - Code: apply_attack_action.rs:6413-6439 (6423), :311-326, :329-343; apply_action.rs:1284-1308. Test meowth_carefree_steps_test.rs:390.
   - Status: a named known limit (PLAN.md:61). A fix exists on claude/coin-prevention-round2 (78af4e8).
4. **Trap Territory counted once with two Ariados**
   - Where: 213034 T5 (~117-124).
   - Seen: 160 on 130-HP Moltres ex, two Ariados on the opponent's Bench, no Tool on Moltres, no Weakness match.
   - Inferred: 160 = 40 + 30 × (printed 2 + 1 + 1). The checker found no other visible source of the extra 30. Research was the last card discarded before the attack, so no Item came after it.
   - Simulator: hooks/retreat.rs:251-262 adds one Colorless for any Trap Territory and breaks at line 260, so it deals 130. Byte-identical on main and 5a18d31.
   - The same capped value feeds Grass Knot (extra_damage_per_retreat_cost, apply_attack_action.rs:4545-4556; main 4384-4394), retreat payments, Heavy Helmet (hooks/core.rs:706-712) and the other per-Retreat-Cost attacks (effect_mechanic_map.rs:24, 2250).
   - Every Ariados test uses one Ariados (legacy_ability_logic_test.rs:611 and three others).
   - Exposure: Dustin's deck 12 (decks/dustin/12-ariados-whimsicott-ogerpon.txt, 2 Ariados) and rl/results/b2e_card_check_2026-09-26/decks/h-whimsicott.txt.
   - Here the KO happened either way; only the number differed by 30.
   - Status: outside the switch. A separate repair with a two-Ariados test.

### 3c. Not checked, or the footage can't tell

**Switch parts never reached:**
- Repair B's cut after Weakness (no Bastiodon or Hisuian Goodra).
- Queued snipes into a coin-Ability Pokémon.
- Chase Order with or without the discard.
- Carefree Steps heads.
- Victory Star with CoinFlipToBlockAttack.
- A copied Chase Order.
- The own-Bench form of also_choice_bench_damage.
- kd's follow-ons and F1-F7 (tests and pricing; not visible in a game).

**Repair A:** a Confusion tails with Victini, on a coin attack named in the review. 210403 T12's attack isn't named, and both engines agree on tails anyway.

**Other untested cases:**
- A double KO in a friend battle, at Checkup, or one that ends the game.
- Rocky Helmet and Hoopa ex double-KO recipes.
- A Mega ex Knocked Out (3 points).
- The Mega-attacker exception under Bounded Field.
- Bounded Field and retaliation damage with a matching Weakness.
- Destructive Inferno discarding Energy from a surviving target (always 0 heads on survivors).
- A paid retreat under Trap Territory.
- Rainbow Cave's Energy swap.
- X Speed's effect.
- Lucky Ice Pop heads.
- Refusals for Rare Candy, Quick-Grow Extract and Wallace.

**Hidden information:** Copycat's draw counts; Poké Ball, Juliana, Fragrant Forest and Strange Singing results; the second Misty target.

**Display oddities with no rules consequence:**
- A Weakness tag over Skiploom (203626, 247.5) that doesn't match its printed Lightning Weakness. No Fire attack ever hit it.
- The results-page "damage done" totals, which include overkill.
- Which side the 485 s empty-deck banner belongs to (204634).

**Noticed while writing (outside the reviews):** the Wallace notes in rules/02:153 and rules/04:91 looked stale. Sonnet's second read (`WALLACE_second_read_sonnet.md` here, Oct 1) confirms it, and goes further:
- **What the engine does:** both Wallace's playability check and its effect read the current maximum HP. Wallace is blocked only on an empty deck or with no eligible Water Pokémon in play. A test pins this: `rules_repair_trainers.rs:276`.
- **A third note is stale too:** rules/05:85.
- **The whole ⚠ paragraph of rules/04:91 is stale:** every "from your deck" card is now blocked only by an empty deck.
- **Old code with no caller:** `card_logic/wallace.rs` still reads printed HP, but nothing calls it.

The plain text decides, and the engine already follows it. The replacement wording is in that file's section 5.

---

## 4. What to record where

### At the pin's step 13 (documents)

**rules/09**, the three entries at lines 85-128:
- Mark these fixed: Victory Star after a Confusion heads (A), the cut's order, the six helpers' queued choices, and Chase Order.
- The open entry keeps the switch's list, with today's evidence added:
  - Wild Swing still skips the coin. The game flips: [OBSERVED 213822, 150-154; DUSTIN].
  - Victory Star with Confusion and Will pending stays gated in this switch. The game offers it on the attack's coins after a Confusion heads: [OBSERVED 210403 T14, 354-355]. Lift it in the next switch.
  - Victory Star with CoinFlipToBlockAttack stays gated in this switch. Under Dustin's Oct 1 rule, the next switch follows the plain reading with no footage needed.
- New open item: Will is wasted on a Confused attacker's own coins (attack_outcome.rs:590-604; outcomes.rs:489-491). By plain text, Will applies to the attack's first coin after the Confusion coin: [OBSERVED 210403 T14, Will's banner on Heat Charged's coin screen 347.25-347.95; DUSTIN].
- New open bug: two Trap Territories count once (hooks/retreat.rs:260). By plain text each Ariados adds 1. Evidence: 213034 (Grass Knot 160, arithmetic, labelled).

**rules/04 §9:**
- Line 145: add 204634 (T4, 184-205) as a third sighting, the first with a 0-heads original. Word the "engine mismatch" line as fixed, as step 13 says.
- New line: Will does not force the Confusion coin [OBSERVED 210403 T16, 376-389; Astra; DUSTIN].
- New line, next to 144: a Victory Star replacement is a fresh flip, and Will doesn't apply to it [OBSERVED 203626 T12: the replacement's first coin was tails (345.5); the original first heads is consistent with Will but not shown to be forced; DUSTIN: "Will does not apply on a re-roll"]. Sonnet's second read caught the earlier, stronger wording.
- New line: after a Confusion heads, Will applies to the attack's own first coin [OBSERVED 210403 T14, 347.25-347.95; DUSTIN]. With Will pending, Victory Star is still offered [OBSERVED 210403 T14, 354-355].

**rules/04 line 61** ("Passive same-name Abilities stack", now [COMMUNITY]): add 213034 (117-124), Grass Knot 160 with two Ariados. Label it as arithmetic, not a shown breakdown.

**rules/02:**
- §7 line 145: cite 203626 (the attacker went second and was asked first; frame 244.5 plus Dustin's note; Solo; Counterattack).
- §5 line 119: add an Ability case, Zangoose's Counterattack fired on a lethal hit (203626, 229.5-241.5).
- §5 line 114: add 213822 (Turbo Shark at 94; Destructive Inferno at 201.5) and 214736 (174-194) as further "attack resolves before Knock Outs" sightings.
- §6 line 137: add Wild Swing discarding two Mega ex with no points (213822, 145-161).
- §1 / step 4: add 210403 T18 (40 × 2 − 20 = 60) as a second fixed-reduction case, labelled as arithmetic.
- §2 line 57: add Water Shuriken's plain 20 on Water-weak Typhlosion ex (214736, 289-297).

**Wallace notes** (from `WALLACE_second_read_sonnet.md`, section 5):
- Replace rules/02:153, rules/04:91 (the whole ⚠ paragraph) and rules/05:85 with that file's wording.
- Before "the six helpers" goes into rules/09, check the count against `EQUIVALENCE_sonnet.md` section 2. Sonnet counts seven helper functions plus Chase Order's two branches.

**Don't edit inside the switch:**
- The F4 test's comment (b4a_attack_batch2_test.rs ~432-433, "which coin Will turns to heads there has not been seen in Pocket") now has its Confusion-coin half answered.
- card_validation.rs:97's caveat.
- Both sit in switch files. Leave them for the next switch, not R.

### Shot-list rows worth adding or updating

Under Dustin's Oct 1 rule, plain card text decides, so no new rows are needed to confirm it:
- **victory-star-confused-will:** answered: items 1-3 are on screen, and the reroll follows from the text (see 2.2). Mark it captured.
- **wild-swing-carefree-steps:** passed. Nothing more needed.
- **double-ko-second-player-promotes:** passed. No card text covers promotion order, so this is exactly the kind of row that's worth having. A friend battle where the friend attacks would only add to it.
- **Two Ariados:** no row. The plain reading (each adds 1) decides it, and 213034 is consistent.
- **Earlier rows that only confirm plain text** are optional proof, low priority, with nothing waiting on them: carefree-steps-snipe (reframed Oct 1), chase-order-carefree-steps, victory-star-block-coin.
- **guarded-grill-after-weakness** asks about an order no card states (a heads cut against Weakness), so it stays a real question.

### Open cases for the next rules switch

1. **Lift the Will carve-out** at apply_attack_action.rs:131, and **make Will force the first coin of a Confused attacker's own attack** after a Confusion heads, with or without Victini. Keep the reroll a fresh flip, with no second Confusion check. Evidence: the plain text; 210403 T14 (347.25-347.95 and 354-355); 203626; Dustin.
2. **Wild Swing's coin** (the 78af4e8 fix), with 213822 as in-game evidence.
3. **Trap Territory stacking** (hooks/retreat.rs:260), with a two-Ariados test. It reaches retreat costs, Heavy Helmet and Grass Knot-type attacks.
4. **Still gated or open from this switch, each to be built on its plain reading** (Dustin's Oct 1 rule): Victory Star with CoinFlipToBlockAttack; a copied Chase Order's discard branch; also_choice_bench_damage's own-Bench form; the six other sites. The cloud's round-2 branch, claude/coin-prevention-round2 (76b87cd, then 78af4e8), has its later-round coin fixes, Wild Swing among them; check its list against this one when the next switch is planned.

---

## 5. Sources

**Reviews** (Sol, lead-accepted), each folder holding REVIEW.md, SUMMARY.json, UNCERTAINTIES.json and COVERAGE.md, under `C:\Users\dacz8\OneDrive\Desktop\Battle Logs\Recording_QA\`:
- `20261001_203626000_iOS_rule_sol\`
- `20261001_204634000_iOS_rule_sol\`
- `20261001_205658000_iOS_rule_sol\`
- `20261001_210403000_iOS_rule_sol\`
- `20261001_213034000_iOS_rule_sol\`
- `20261001_213822000_iOS_rule_sol\`
- `20261001_214736000_iOS_rule_sol\`

**Other sources:**
- Batch summary: `C:\Users\dacz8\OneDrive\Desktop\Battle Logs\BATTLE_RULE_TESTS_2026-10-01.md`.
- Astra's bounded check: `...\Recording_QA\BATCH_2026-10-01_RULES\ASTRA_CHECK.md`. It covers Will and Victory Star, the damage order, the second Misty target and the lethal Destructive Inferno. It doesn't cover 205658 or 213034.
- Dustin's notes: `scratchpad\shot_captures\captures\*.json`. Shot rows: `scratchpad\shot_items\items\*.json`.
- Switch: `rl/results/engine_switch_rules_2026-10/PLAN.md` (what the switch is, lines 9-35; repair A's gate, 41-46; Known limits, 58-61; step 13, line 172).
- Rules notes: rules/02, rules/04 §9 (lines 143-145), rules/09 (lines 76-128).
- Engine lines were read at 5a18d31 (and at main's engine tree 9c84fef where stated) by the findings and their checkers.

**The video id.** Dustin's capture for double-ko-second-player-promotes names "20261001_20326000". No such file exists: the Battle Logs folder holds seven Oct 1 evening videos, and none matches. It is read as **20261001_203626000_iOS.MP4** (a dropped "6"). Three things confirm it:
1. It is the only recording today with a double Knock Out from an attack. The other six reviews each report only single Knock Outs.
2. His note "I chose my pokemon and then they did." matches 203626's promotion sequence (244.5-247.5).
3. The capture was saved at 20:46:10. That is after 203626 (started 20:36:26, 366 s long) and 24 s before the next recording (204634) began. His other two captures follow the same pattern: saved at 21:16:05 after 210403, and at 21:43:24 after 213822. This assumes the filename clock and the capture timestamps use the same basis; the batch summary says the filename clock basis wasn't established. The pattern holds for all three captures.
