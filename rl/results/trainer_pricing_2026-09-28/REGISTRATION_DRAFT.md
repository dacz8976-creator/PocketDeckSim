# DRAFT (Sept 28; the review's findings applied Sept 29): `km`, Trainer pricing on kog, two list-free switches

**Status: a draft, not registered. No code and no game.** Nothing here is registered until the text is committed as the registration, with Dustin's word on it (kt's registration says the same of itself). The review's findings (`REVIEW.md`) were applied to this text on Sept 29. Every change is listed with its finding id at the end ("Changes from the review (Sept 29)"). One check by a reader other than the editor has been done on the applied text (the review's order, step 3); its corrections are listed at the end ("Corrections at the check"). It was not a second full review.

**Sept 29: committed as a draft, with its review (`REVIEW.md`), for the record. That commit was not a registration, and neither is this text.** The review found two blockers (the ordinary rule's sign; clause (d) not yet one exact test) and 13 should-fix items. Both blockers and all 13 are applied below. Two calls are Dustin's. They are written below as open option blocks and are not decided: **D1** (keep N1 inside km) and **D2** (clause (d)'s deal count).

- **Decision this informs:** whether kog3, the working pilot, is replaced by km3. km3 counts the lasting Stadium damage bonus in the threat clock (and, under D1 option B, the opponent's Active Retreat Cost). It is read on the 45 cells, by the route the footprint fixes.
- **Dustin's word is needed, item by item** (as kt's registration lists it):
  1. **On this text as km's registration.** That covers: Lucario as the one gating archetype; the exact clause (d) test; "Stadium damage bonuses count as the relevant cards" (the closure sentence, section 5); the coverage reading (open question 1); and his answers to D1 and D2.
  2. **On the build.**
  3. **On the tables.**
  The overnight delegation to Fable (Sept 28-29) does not cover his registration gate.

### Dustin's two calls (open; the review's lean is named, nothing is decided)

**D1 (Dustin's call): does N1, the Goo-zooka switch, stay inside km's gate?**
- **Option A (the review's lean): N1 out of the gate.** km is then N2 alone (today's `kmb`; a change of letters in this text, and nothing is built yet). The N1-only code stays in the build as a diagnostic (`kma`), so N1's effect on Goo-zooka is still measured (section 5, step 3b). N1 is registered later as its own candidate if he wants it, with its own carrier: Whimsicott ex Ariados (Sept 10 rank 26; Goo-zooka and Ariados in 21 of 21 development lists; the held-out deck `h-whimsicott` exists) and the Goo-zooka rate as its evidence.
  - Why: N1 has no gain test, it adds the least certain part of the footprint, and two of the review's three lenses lean this way.
  - Cost: one more registration cycle for the Goo-zooka card.
- **Option B: N1 stays inside km.** The text then says plainly that N1 rides on N2's clause (d) with no gain evidence. It is adoptable only through the no-harm clauses (b) and (c), the vetoes and the coverage tests. A Dustin override is the only route if N2 fails alone ("Outcomes fixed now", section 6).
  - Why: it is free, list-free, and the only thing in km that touches Goo-zooka.
- **How the text reads under each.** "km3" below is **the gated code**. Under B it is kog + N1 + N2. Under A it is kog + N2 (the same flags as `kmb3`; `kmb3` is then not played as a separate code). `kma3` (kog + N1 only) is a diagnostic under both. Passages that differ carry "(A)" or "(B)". "N1 (B)" means N1 as part of the gated code.

**D2 (Dustin's call): how many deals for clause (d)?** Clause (d) is one test on Lucario's nine rows (section 5, step 4). It is read once under either option.
- **Option 500 per row.** The games clause (c) already needs (the mixed rows on the table's deals). No new seed block. The review's model says a real gain of the size this draft predicts (1.2 to 1.9 points) is caught about 31% to 99% of the time, depending on how many games flip (a model estimate, not a measurement). A real 1-point gain is missed 34% to 77% of the time. A miss closes the route.
- **Option 2,000 per row (the review's lean, for (d) only).** The first 500 deals of each row are the table's and (c)'s. 1,500 more per row go on one new named seed block, proposed as **22,900,000,000 – 22,900,081,499** (22,900,000,000 + row × 10,000 + i, row 0-8 in the order the nine cells are listed in (d), the 7 table cells in increasing table pairing number, i < 1,500; Lucario in seat 0 on even i, as kt's clause (d) block does for Rayquaza). It was free in START_HERE's seed table on Sept 29 and is written into that table in the registration commit, not before. About 27,000 to 36,000 games, roughly 52 to 70 minutes at the laptop's 8.6 games a second, and only if km lands under 15%. At this size a real 1-point gain is caught 69% to 100% of the time (model estimate). This is close to his open question from the eval-power README (run small-footprint candidates at 2,000 deals). If he answers that one for the whole reserve route, the text follows his answer.

---

- **Build path** (RUN5 "The cloud", lines 417-420; Dustin Sept 28 about 7:30 pm, "the cloud"): the cloud gets one round, meaning build, one review and the identity check. The laptop then runs the tables. Section 4 says who does what, so the two don't overlap.
- **What was run to write it:** only read-only counts of files already in the tree (the X Speed census file, the Trainer audit TSV, the Limitless development standings) in a scratch folder outside the repo. The numbers are in `SCRATCH_NOTES.md` beside this file. No game, no build. Nothing has to be run before registering (the review's verdict).
- **Seeds:** the table's own deals only, with one exception. Under D2 option 2,000, clause (d)'s extra deals use the one named block above. Under D2 option 500 there is no new seed block.
- **Line numbers** are from the files as read on Sept 28, 6 to 7 pm. Other sessions were editing RUN5 and kph's registration while this was written; the section names are the anchor. RUN5's line numbers were brought up to date on Sept 29 (RUN5 grew by 15 lines after its line 340).

**At a glance**
- **What km is:** kog plus two switches, each a list-free rule the engine already has. **N1:** the opponent's Active Retreat Cost counts, as the bot's own does (the score's one one-sided board number). **N2:** the lasting Stadium damage bonus (Training Area, Arena of Antiquity) counts in the threat clock for both sides, through the engine's own Stadium bonus functions. Under D1 option A, km is N2 alone and N1 is a diagnostic.
- **Why so small:** of the 16 Trainers outside kt that the score misses or half reads, only 4 have a fix that needs no constant, no list and no hidden-hand prior. Team Rocket's Boss is among the 12 that don't (1.3, section 3). X Speed isn't one of the 16: the score reads it, and its pattern comes from the card arithmetic (1.2).
- **The X Speed finding:** the census's 23% "waste" is mostly the score's own card arithmetic (39% Copycat shape, 43% where a Hiking Trail can be in play). Only 4% of X Speed turns have no explanation. Nothing in km changes it.
- **Reach:** N2 touches the two biggest archetypes (Arena in 98% of Lucario lists, Training Area in 98% of Altaria/Espeon lists). N1 reaches Dustin's decks 12, 14, 15 and brews 03a, 03b, 05b, 10. The code says N1 moves every Goo-zooka line by +1 where the target Active is still there at the leaf, so its play rate is expected to rise. That is a prediction, and section 5 (step 3b) registers the measure.
- **Route:** predicted footprint between about 3% and 19%, with no reliable centre (section 7). So both routes are written out. The reserve route's clause (d) gates on Lucario.

**Three rulings that landed while this was written, and how they are used**
1. **Coverage rows** (RUN5 "How coverage rows count", lines 495-498; Dustin Sept 28 about 6:40 pm; kph amendment 4). The brief said to use kph amendment 2's definitions for Scizor and the second lists. Amendment 4 supersedes amendment 2's *tests* (RUN5 lines 495-498). So step 5 takes amendment 2's *row definitions* (which rows, which deals, the interval formula) and amendment 4's *test* (own-side, whole 95% interval below zero; accuracy reported only). Open question 1: answered, confirmed.
2. **"A registration written before the games and satisfying the rule outranks a reviewer's paraphrase after it"** (RUN5 lines 503-505, kt's clause (d)). So clause (d) below names one gating archetype and one exact test. Anything else is "reported beside" and gates nothing.
3. **Goo-zooka joins the candidate's list** (Dustin, Sept 28 about 11:15 pm Central, relayed verbatim by Fable): "Brew 03b's borderline through Goo-zooka at 2.1 percent use is the Trainer-pricing blind spot showing up again, which puts a fourth card on that candidate's list."
   - The evidence: Team Rocket's Goo-zooka was played on 95 of 4,445 chances (2.1%) in brew 03b's floor check under kog3 (`../floor_brews_2026-09-28/brew-03b-arceus-crobat-nihilego-toxapex.md`, a flag under 25%). The Sept 25 audit found the same 2.1% for this deck.
   - **What this changes in the draft:** Goo-zooka is now a card the candidate is meant to move, not only a reach line. N1 prices its effect (the opponent's Active +1 Retreat Cost). The floor flag says the effect "pays off during the opponent's turn, which the search doesn't play out". The review read the code: a leaf that doesn't play the opponent's turn still shows the +1, so N1 has a mechanism to move the rate (N1's "Honest size", section 2). The draft's first reading, "close to a tie", was unsupported.
   - Whether the rate moves is a registered measure (step 3b), reported beside and gating nothing. If it doesn't move, the reading says "km does not fix Goo-zooka". Open question 14: answered in part.

---

## 1. In plain words

### 1.1 Which Trainers are mispriced, and how (measured)

**The census** (`rl/results/trainer_audit_2026-09-25/census_table.md`, `census.json`, re-counted here): 61 Trainer cards in the 36 audited decks, checked one by one against what kp3's score can see.

| What the score does with the card | Cards | Count |
|---|---|---:|
| Reads it | 27 Supporters, Items and Stadiums, plus Giant Cape and Leaf Cape (HP) | 29 |
| Reads part of it | 5 Tools, 5 Supporters, 4 Items, 9 Stadiums | 23 |
| Doesn't read it | 5 Tools (Heavy Helmet, Lucky Egg, Metal Core Barrier, Poison Barb, Rocky Helmet), Cheren, Jasmine, Team Rocket's Boss | 8 |
| Reads it backwards | Protective Poncho (+10 on the Active, where it does nothing) | 1 |

- **kt already takes 16 of the 32 unread, part-read or backwards cards** (18 of all 61, counting the two Capes, which are read but carry the spurious +10): the 11 Tools, Cheren and Jasmine, and Guzma, Field Blower and Repel (they inherit the flat +10 from the other side). kt is "Tools and turn effects" (`rl/results/kt_2026-09-26/README.md`, re-issued on kog).
- **The other 16 are this class.** By mechanism:

| Mechanism | Cards | Play rate in the audit (played / turns offered) | Can a list-free rule fix it? |
|---|---|---|---|
| **A board number the score reads for one side only** (retreat cost) | Team Rocket's Goo-zooka, Peculiar Plaza | Goo-zooka 337 / 3,330 (10%); 2 to 5% in four decks, **36% in deck 12**. Plaza 326 / 468 (70%); 91% in brew 05b | **Yes: km switch N1** |
| **A board number the clock leaves out** (attacker's damage bonus from a Stadium) | Training Area, Arena of Antiquity | Training Area 234 / 703 (33%); Arena 93 / 416 (22%) | **Yes: km switch N2** |
| Hidden hand | Team Rocket's Boss | 18 / 664 (**2.7%**) | No (1.3) |
| Effect is a use or an end-of-turn effect on later turns | Rainbow Cave, Fragrant Forest, Mesagoza, Arcade, Soothing Shore, Hiking Trail | Cave 204 / 2,397 (8.5%); Shore 474 / 1,550 (31%) | No: needs a number of future turns (3) |
| Status not read | Team Rocket's Master Plan, Pokémon Center Lady | Master Plan 269 / 1,106 (24%); Lady 1,111 / 1,509 (74%, for the heal) | No: needs a duration (3) |
| Priced by counts only | Mars, Ilima, Pokémon Flute | Mars 83 / 174 (48%); Ilima 78 / 448 (17%); Flute 4 / 248 (1.6%) | No (3) |

Rates are from `audit_trainers.tsv`, summed over decks (`SCRATCH_NOTES.md`). They are per turn the card was playable. The audit README quotes lower Stadium rates (Training Area 26%, Rainbow Cave 4.5 to 7%) from its follow-up run (`blower_stadium/`, other games, turns with no Stadium in play); I use the TSV's. The audit ran kp3. kog3 plays kp3's moves except in Altaria's opening and where Blaziken's F acts (kt README, re-issue item 5), so kp3's figures stand as "before" figures for the table decks.

### 1.2 X Speed played and not used, and the "before Copycat" shape

The census said X Speed had no retreat after it on **221 of 944 turns (23%)**, and 75 of 143 (52%) in Dustin's deck 12 (`rl/results/xspeed_census_2026-09-27/README.md`). I re-tallied its per-turn file (`games.jsonl`, 2,400 games):

| Of the 221 turns with no retreat | Turns | Share |
|---|---:|---:|
| Copycat played the same turn (63 of them the very next move; 15 played it before X Speed) | 87 | 39% |
| No Copycat, in a game of deck 12 (its own Hiking Trail) or against Blaziken (its Hiking Trail) | 96 | 43% |
| Neither of those | 38 | 17% (4% of all 944 X Speed turns) |

- **Why the first two happen, from the code, not a trace.** The score's card term is `(my.hand − opp.hand) + (opp.deck − my.deck)` (`value_functions.rs:761-762`). A player's 20 cards are always in the hand, the deck, the discard pile or in play. So the term equals, up to a constant, **2 per card in hand, 1 per card in the discard pile or in play, 0 per card in the deck**. That is my derivation. It reproduces the census's own figures (Copycat = −1 + 2 × (opponent's hand − what stays in the bot's hand); an unseen-effect card costs exactly 1). Two consequences:
  - A card played before Copycat goes to the discard pile (worth 1) and not into the shuffle (worth 0), so it is worth +1. That is X Speed before Copycat.
  - With Hiking Trail the hand is topped up to 3 at the end of the turn (`hooks/core.rs:555-568`). Playing a card that leaves the hand under 3 costs 1 and buys one extra draw (worth 2): +1 net. The census measured this: deck 12's X Speed is played 57% in games where it played its Trail and 10% without; Goo-zooka is 0.4 to 3.3% with no Trail and 12 to 32% against Blaziken (`census.json`, X Speed row and the Items finding on card counting).
  - **The identity is derived, not tested.** It holds by conservation, with two exceptions the review named: Team Rocket's Thieving Machine moves a card across players, and a leaf that stops mid-turn has no Trail top-up. Section 4 has a diagnostic for it (open question 13).
- **So the "23% waste" overstates it.** Shape 1 thins a dud out of the shuffle. Shape 2 is cycling a dud for a fresh draw under Trail. Neither obviously costs a game (my reading; the census measured rates, not harm). Only the 38 turns (4% of X Speed turns) have no explanation here. I could not tell from the file which of the 96 had a Trail actually in play (it records move kinds, not Stadiums), so **96 is an upper bound**. Step 3's counter records "Hiking Trail in play" at each X Speed turn on the same deals, which settles it at no extra cost (open question 10).
- **What the census did find that matters** is Dustin's Q02 (a free retreat into a free attacker was there): that is the cheap-attacker habit B2c named, not X Speed's price.
- **Dustin's quiz agrees the arithmetic is roughly right.** Q03 (X Speed before Copycat, or Copycat first): he did neither and ended the turn. On Copycat overall, kp3 (which plays it more than k3) matched him more often, 17 against 13 at the decision (`rl/results/blind_quiz_2026-09-25/RESULTS.md`).

### 1.3 Team Rocket's Boss

- **What the bot sees.** Boss's payoff is the Basics in the opponent's hidden hand. In the search that hand is Unknown, and Unknown is never a Basic (`apply_trainer_action.rs:340-344`; `public_pricing_player.rs:64` audits the text). So Boss costs 1, does nothing, and its target choice spends a second search action. Played 18 times in 664 offered turns (9 of 325 in the Suicune list, 9 of 339 in brew 02).
- **Why it is not fixed here.**
  - Any value for it needs a guess about the hidden hand. The engine's one rule for that is option B's sample from the opponent's list (`observation.rs:160-232`), which is a matchup prior. kp is defined without one (`observation.rs:143-144`: "no matchup prior is silently introduced").
  - Dustin's quiz sided with the bot's caution both times: Q07 "sure", Q04 at the decision ("they might not even have another basic in their hand", quiz RESULTS).
  - The sim doesn't undersell Suicune: 51.4 against a real 48.9 under kog3 (`kog_composition_2026-09-27/score45_kog3_vs_kp3.txt`).
- **The variation check's +7.3 for Boss** (`gauntlet_tables_b.md`, swap 1, ± 1.5) puts a **second Giant Cape** in its place. A Cape is a Tool: the bot plays it with the flat +10 and its +20 HP. The swap can't say how much of the +7.3 is a dead card removed and how much is Cape pricing (kt's territory). Suicune's second list (+5.8) carries the same Cape.

### 1.4 What the variation check adds

Four single-card swaps moved a deck's opponent average by 3 points or more (`gauntlet_tables_b.md`; the card named first is the one put in): Lucky Ice Pop in, Poncho out (Lucario +4.2, a Tool: kt); a second Giant Cape in, Boss out (Suicune +7.3, above); Lucky Ice Pop in, Mars out (Weezing +3.8); Sabrina in, Pokémon Center Lady out (Lucario −3.1). The last two are heal-against-disruption swaps. No list-free rule found here explains them (section 3). They stay in the open list (section 7).

---

## 2. The fix: two switches, each behind its own flag

**Rule (one sentence):** *a Trainer whose effect changes a board number the score already knows how to read is priced by that number, for both players, through the engine's own functions for it (N1: the retreat-cost extraction the score already has; N2: the engine's own Stadium bonus functions).* No card is named in the evaluator, no constant is added, no list is used.

**Codes.** `kma<N>` = kog + N1 only. `kmb<N>` = kog + N2 only. **`km<N>`, the gated code** = kog + N1 + N2 under D1 option B, and kog + N2 under D1 option A (then it has `kmb`'s flags). Under A the both-switches combination is not built as a gated code. The single-switch codes are diagnostics. They are run for the Goo-zooka and Plaza measures (step 3b) and, under B, for the N2-alone test in "Outcomes fixed now". They get no route of their own. The parser entries go before `k<N>` (see the `kt` block, `players/mod.rs:260-274`, and the parser's own comment that a prefix must come before `k<N>`, which would reject it).

### N1. The opponent's Active Retreat Cost counts, as the bot's own does

- **Today.** Eleven of the score's terms are `mine − theirs`. Two are one-sided: the opponent's discard count (0.1 a card, `:774`) and the retreat term, `(−my.active_retreat_cost) × params.active_retreat_cost` (`value_functions.rs:763`), weight 1.0 (`:51`). The opponent's cost is already extracted (`:862`, through `get_active_retreat_cost`, `:919-943`, which reads the board cost without this turn's discounts) and then dropped.
- **Change.** `(opp.active_retreat_cost − my.active_retreat_cost) × params.active_retreat_cost`. Same weight, same extraction, no new function. The setup evaluation (`:675-714`) is untouched: it never reads the opponent, whose setup is masked.
  - **Placement, a registered implementation constraint.** The new term sits in place of `(−my.active_retreat_cost) * w` at `value_functions.rs:763`, in the same position in the sum. With the flag off the expression is untouched. Appended after the fuel credit or the opponent-discard term, the same two lines could differ by 1 ulp of rounding, and a tie would then be decided by rounding noise.
- **What it prices.** Goo-zooka (`apply_trainer_action.rs:421-427`: `IncreasedRetreatCost { amount: 1 }` on their Active for a turn), Ariados's Trap Territory (`hooks/retreat.rs:251-262`), Peculiar Plaza's −2 for **both** players' [P] Pokémon (`stadiums.rs:119-127`, read at `retreat.rs:224-230`), and which Pokémon a gust or a knockout leaves in front of them. It also prices attack-applied Retreat Cost effects and the opponent's retreat Tools and abilities (`retreat.rs:153-222`): Small Balloon (`t-altaria`), Inflatable Boat (`t-suicune`) and Bombirdier (`t-hydreigon`; its Villainous Delivery makes the Active [D]'s Retreat Cost 1 less while it is on the Bench, `card.py`).
- **Honest size.** At weight 1 a Goo-zooka line is worth +1 for the effect and −1 for the card. Under kog the same line is worth 1 less, because the effect is dropped and the card leaves the hand. Under N1 it is level with not playing it. This is what the code gives:
  - The retreat code sums `IncreasedRetreatCost` effects with no duration test (`retreat.rs:239-249`; `played_card.rs:348-353`). `end_turn_maintenance` only drops effects already at 0 (`played_card.rs:460-469`). So a leaf after the bot's own turn still shows the +1.
  - The action list is sorted by each action's JSON string (`observation.rs:37-39`; `game.rs:201`). `EndTurn` is a unit variant, so it sorts first. Then come Attach, AttachTool, Attack, Evolve, Place, Play, Retreat, UseAbility.
  - `Iterator::max_by` keeps the last of equal scores, and `prefer_shorter_win` gives Equal for two `None`s (`expectiminimax_player.rs:340-350`, `:64-71`). So at an exact tie, Play beats EndTurn, Attach, AttachTool, Attack, Evolve and Place. **The tie goes toward Play, by sort order and not by value.**
  - **Prediction (not proven):** N1 moves every Goo-zooka line by +1 wherever the target Active is still there at the leaf. Goo-zooka's play rate is expected to rise. In Trail-less matchups it rises by the tie-break. With Hiking Trail it rises by strict gain (+1 today, +2 under N1).
  - **Limits.** The tie is exact only if the line has a spare action in the 3-action search and the target Active is still there. The sum is in floating point, so "level" must be tested with a tolerance. kt's registration records a Balloon tie as "decided by move order" and predicts those plays fall (kt README 352-353). So the direction of a tie depends on the action and on how many actions it uses. Nobody has measured it.
  - The draft's own data agrees with the mechanism. Of the 95 Goo-zooka plays in 03b's floor games, 72 were against Blaziken (of 541 chances), 21 against Altaria (of 624), 2 against Weezing (of 440), and 0 in the other 2,840 chances. Section 1.2 already has 12 to 32% against Blaziken (its Hiking Trail) and 0.4 to 3.3% without.
  - The measure is registered in step 3b, with its fallback.
- **What else it fixes.** Direction: Plaza is played 91% of offered turns in brew 05b whoever it helps; under N1 it stops paying when only their [P] Active benefits. It also removes the score's one one-sided term before the next candidate builds on it. This is the census's own fix sketch for Goo-zooka and Plaza ("Score the opponent's Active retreat cost, which is already computed").
- **Not kt's, but next to it.** kt's README says of the opponent's retreat Tools: "0 (the score has no opponent retreat term; a later candidate)" (README line 351). N1 is that term. kt doesn't read it and km doesn't touch the Tool term. But N1 would change what Field Blower, Guzma and Repel are worth under kt's switch 2. kt predicts Blower stops removing the opponent's Balloon and Boat (93 and 64 of its 1,414 Active removals under kp3, kt README 366-367), and N1 would give those removals value again. In the panel lists the cards are Small Balloon (`t-altaria`), Inflatable Boat (`t-suicune`) and Bombirdier (`t-hydreigon`). Composing km with kt's switch 2 needs its own check (the base-change rule below). Under D1 option A this paragraph applies to N1's own later candidate.

### N2. The attacker's lasting Stadium bonus counts in the threat clock, both sides

- **Today.** The clock's damage is the attack's own estimate (`estimated_attack_damage_ex`, `value_functions.rs:2150+`) with nothing from the board. The engine adds a Stadium bonus to every active-to-active attack: Training Area +10 for a Stage 1 attacker, Arena of Antiquity +20 for an [F] attacker against an ex, "both yours and your opponent's" (`hooks/core.rs:1997-2012`, from `stadiums.rs:129-158`). `persistent_defender_damage` says outright that it leaves out "the attacker's bonuses" (`hooks/core.rs:1618-1619`), and `value_functions.rs` has no Stadium read except F's Rainbow Cave check (`fuel_credit.rs:181`). So the score sees these Stadiums only when an attack happens inside the same 3-action line (census: "same-line" case).
- **Change.**
  1. **A read-only function in `players/`, not in the rules files.** `lasting_stadium_damage_bonus(state, attacker_stage, attacker_types, target_is_ex) -> u32`.
     - It returns 0 first thing when `state.active_stadium.is_none()`, and looks up an evolution form only after that. (`has_stadium` builds the reference card text before it looks at the board, `stadiums.rs:106-113`; without the guard it would allocate on every call, even with no Stadium in play.)
     - Its body is the two calls at `hooks/core.rs:2000-2009`, made through the engine's own functions: `crate::stadiums::get_training_area_damage_bonus` and `get_arena_of_antiquity_damage_bonus` (both `pub fn`, `stadiums.rs:131, 145`), with `State::pokemon_energy_types` (`pub(crate)`, `state/mod.rs:663`) and `get_stage` (already re-exported to the crate, `hooks/mod.rs:17`). Those two engine functions name the two Stadiums, so the new function names them by calling them, as the engine's own damage stage does (`stadiums.rs:129-158`). The evaluator names none, as kd's and kt's hooks don't.
     - **The diff touches `engine/src/players/` only.** No existing line of `core.rs`, `hooks/mod.rs` or `stadiums.rs` changes, so RUN5's refactor rule and the baseline re-run are never reached (a new function in `core.rs` would need a re-export line in `hooks/mod.rs`, a second rules file).
     - A pin test ties it to `modify_damage` (section 4). A comment on the `players/` side points at `modify_damage`. No comment goes on the `core.rs` side: that would make the diff touch a rules file. The pin test is what shows a later change on either side.
     - If Dustin or the cloud insists on `core.rs`, it is registered as an additive rules-file change instead: name the `hooks/mod.rs` line, write a one-row source equivalence (no rules code calls it), run the full suite, replay k3, kp3 and kog3 on games that execute `modify_damage`'s Stadium branch, and re-run the kog3 baselines at the build.
  2. **In the clock** (`turns_until_opponent_wins_scan_projected`, `value_functions.rs:1161-1258`): after the threat is picked (`:1188-1191`), take its Pokémon's stage and types (its evolution form when the threat is one, `ThreatCandidate.form`, `:1339-1351`). Each victim's hits become `ceil(HP / (max_damage + bonus(victim)))` at the two places that compute them (`:1219-1221`, `:1250-1252`). `bonus(victim)` is the function with the victim's ex-ness. With no such Stadium in play the bonus is 0 and the arithmetic is untouched.
     - **How the flag gets there.** `zone_to_bench` stops in `calculate_turns_until_opponent_wins_projected` (`:1089-1128`) and never reaches the scan (`:1161`). N2 must reach the scan, so it adds a parameter to it and to its callers. Either every existing signature stays as a thin wrapper that passes the new flag as false (kph's pattern for `calculate_turns_until_opponent_wins_damage_aware`, `:1059`), or the flag is carried inside `Projection`. The cloud picks one and says which in `BUILD.md`.
  3. **Nothing else.** kd's and kt's clocks (`kd_turns_to_win`, `kt_clocks`, `:1813`) are not touched; no km preset sets their flags. Both sides use the rule, so the bot sees a Stadium it plays helping the opponent's Stage 1 attackers, and Field Blower on a Stadium that helps them.
- **Board only.** For the opponent's threats the scan stays board-only (`read_scanned_zones` false), so no hidden card is read.
- **Intended simplifications, stated so the reading can be judged.**
  - N2 picks the threat on unbonused damage, then adds the bonus per victim.
  - It treats every hit as landing on the Active. A bench-only attack of an eligible attacker therefore gets a bonus `modify_damage` would not give. Both agree with kp's existing simplifications.
  - The N2 arithmetic goes at the two `None` branches (`:1219`, `:1250`) only. The kq branch is left alone; it is dormant, since km leaves `next_attack_reduction` off.
  - Whimsicott ex's Grass Knot (extra damage per Energy in the opponent's Retreat Cost, `ExtraDamagePerRetreatCost`) is not in the clock's damage estimate: `value_functions.rs` has no retreat-cost case. So Whimsicott's held-out row does not test N1 as pricing that card's payoff.
- **Reach.** Training Area and Arena are carried by the two biggest archetypes: **Arena of Antiquity in 391 of 398 Mega Lucario ex Lucario lists (98%), Training Area in 329 of 336 Mega Altaria ex Espeon lists (98%)** (Limitless development half, `SCRATCH_NOTES.md`). Both are table decks. The same function would price Future Booster Energy Capsule and Beastite (`hooks/core.rs:1529-1558`); no top-30 list carries either and kt zeroes them by design, so they wait for a composition (section 7).

### The base-change rule

kt is being read now on kog, and kt's clock replaces kog's clock. If kt (or kta) is adopted before km's first game, km is re-issued on the new base by a dated amendment, reviewed before any game (as kt's amendment 2 provides for koh). If both pass separately against kog3, they are composed under RUN5's composition rule ("Composing candidates into one pilot"), with N2 built into kt's clock (`kt_clocks`) and a fresh identity.

---

## 3. Why these and not others

| Considered | What it would do | Why not in km |
|---|---|---|
| **Discard pile worth what the deck is worth** (the arithmetic in 1.2 made consistent) | Removes the +1 for X Speed before Copycat and Trail cycling | It also makes every Item and Supporter play cost 2 instead of 1. Poké Ball would net 0 instead of +1, and Copycat would need the opponent to hold 2 more cards than the bot's remainder, not 1. Dustin's quiz favours the bot that plays Copycat more. It is a global re-weighting, not a Trainer fix. |
| **A rule for X Speed itself** | Stop the 38 unexplained turns | Any rule must know that "the turn effect went unused". At a leaf after the turn ends the effect has already expired, and at a mid-turn leaf the line isn't finished, so "unused" can't be read from the position. A rule per turn-effect kind would be a card table. And it is 4% of X Speed turns. |
| **Boss / hidden hand** | Price the Basics | Needs a prior; kp has none (1.3). |
| **Targeted plays don't cost a search action** (Tools, Rare Candy, Blower, Flute, Quick-Grow use 2 of 3: `expectiminimax_player.rs:940-969`; the engine already treats attack, coin, promotion and queued-target choices as free, `:630-771`) | A Tool or Blower play would leave room for the next two actions | It is a search change, not pricing, and it adds a full ply after each targeted play (cost not measured). It also changes how Tools are played, which kt is reading. Its own registration, with a timing budget. |
| **Benched threats need a way to the Active** (the clock counts every charged Pokémon as ready wherever it stands) | Would price Goo-zooka, Repel, Cyrus, retreat Tools and X Speed lines in turns | It pushes toward moving the main attacker forward, the direction of kpf's forward swaps that Dustin rejected at Q10 ("sure", kph section 1), and it changes almost every position. koh's fix B is already in that ground. |
| **Status in the clock** (`status_clock_turns`, `value_functions.rs:1323-1335`, behind `--features status-clock`) | Master Plan, Pokémon Center Lady's cure | B2b measured the Sleep half: −0.2 to +1.0 on Altaria's cells, within noise (`rl/results/status_clock_2026-09-25/README.md`). Confusion needs a duration, which is a constant. |
| **Stadium use effects and end-of-turn effects** (Cave, Forest, Mesagoza, Arcade; Shore, Trail) | Value of later uses | Needs a number of future turns, and the search stops at the start of the opponent's turn (`expectiminimax_player.rs:773-798`, `:914-929`). |
| **Mars, Ilima, Flute** | Identity, points at risk, cheapest prize | Each needs a modelling choice with a constant or a list. |
| **Board abilities in the same function** (Lucario's Fighting Coach, `hooks/core.rs:2101-2153`) | Would raise Lucario's clock too | Pokémon-side, not Trainer pricing; and it would push the footprint over 15% by itself. Open question 4: answered, keep out. |

---

## 4. Build and tests (the cloud: one round)

### 4.0 Who does what, and in what order

- **Cloud (one round, RUN5 "The cloud"):** the build (in `engine/src/players/` only), the tests, `BUILD.md`, the identity checks (the cloud is their one owner), and the one code review.
- **Laptop:** builds the same commit and checks the sha256; the timing run; the footprint; the tables; the mixed rows; the coverage rows; the counters; the kog3 baselines if any are missing (step 5); the reading code (below); and the tier-1 second read of the diff before the first km game (RUN5 "Owners": the laptop second-reads tier 1).
- **No overlap.** The laptop does not re-run the cloud's identity. The cloud runs no tables. A second cloud round happens only after a table has asked a question (RUN5 "The cloud").
- **Gate and order.** No km game is played before the identity and tests are committed as passed and Dustin's word on the build is recorded. The footprint is then the first result read (step 1), not the first thing run. The laptop queues km's jobs behind kt's tables and readings (RUN5 "Where things stand": kt's tables are running).
- **Output folders, one owner per file.** Cloud: `rl/results/km_build_<date of the build>/` (build, tests, `BUILD.md`, identity, timing inputs). Laptop: `rl/results/km_tables_<date of the first table>/` (footprint, tables, mixed rows, coverage, counters, readings).
- **Reading code.** `read_km.py` is written blind from the registration, reviewed, and committed before any km result is read, as kt's was. The footprint script is `footprint_km.py`, a copy of `rl/results/koh_2026-09-28/laptop_reading/footprint.py` with km3 where that script names koh3's files (its line 14) and asserts `("koh3","koh3")` (its line 17).

### 4.1 Build and tests

- **Build:** on the official engine (main-9b4df9b, `engine/` equal to 233bced's), as player codes beside kog and kt. `EvalFeatures` gets two flags, `opponent_retreat_cost` and `stadium_bonus_in_clock` (`value_functions.rs:343-378`), false in `OFF`, `KQ`, `KD` and `KPR`, the four presets that list every field (`:381-440`). Presets `KM`, `KMA`, `KMB` are `..EvalFeatures::KOG` (`:460`). (A) `KM` has `KMB`'s flags. New value functions beside kog's (`:307-312`) and `PlayerCode` arms beside kog's (`players/mod.rs:657-698`).
- **Rules files: none touched.** The diff is `engine/src/players/` only (section 2, N2 change 1). Any change elsewhere in `engine/` needs RUN5's repair or refactor rule before the build is used, and every kog3 baseline is then re-run at the build instead of identity-checked (kt README item 7). Open question 5: answered.
- **Tests on constructed boards** (numbers recomputed from `card.py` before each test is written, as kph's registration says). "Equal" between two different codes means within 1e-9: the sums are floating point, and the precedent tests use `(kp - ktb - 10.0).abs() < 1e-9`. Bitwise equality is used only for the flag-off identities named below.
  - **N1, the term:** two Actives with Retreat Costs a and b, no effects: `kma − kog = b`, for b in 0, 1, 2.
  - **N1, Goo-zooka:** `IncreasedRetreatCost { 1 }` on the opponent's Active moves `kma` by +1 and `kog` by 0. The tie test (Play(Goo-zooka) against the alternatives) is written with a tolerance.
  - **N1, Plaza:** a [P] Pokémon with cost 2 or more on both sides: Plaza moves `kma` by 0 and `kog` by +2. Only the bot's Active [P]: +2 under both. Only theirs: −2 under `kma`, 0 under `kog`.
  - **N1, setup and hidden cards:** the setup value equals kog's exactly (the setup path is untouched, so the same expression runs). The opponent's term is unchanged when their hand and deck are swapped for other cards (after `kpr_reads_no_hidden_card`, `:4498`).
  - **N2, the pin:** for each of no Stadium, Training Area, Arena of Antiquity, times attacker Stage 0, 1, 2, types [F], [R], [P], times a target that is an ex or not: the new function equals what `modify_damage` adds at that stage for an active-to-active attack (its result with the Stadium minus without, base damage 50, no Weakness or other modifier).
  - **N2, the clock:** Mega Lucario ex (Stage 1, [F], [F][F] attached, Fighting Pulse 90) against a 190-HP Mega ex Active: 3 hits without a Stadium, **2 with Training Area** (100) and 2 with Arena (110). The survival clock is shorter by exactly 1 turn. Against 180 HP: 2 and 2, no change. A [P] attacker gets Training Area's +10 but not Arena's.
  - **N2, both sides:** the same Stadium shortens the opponent's threat's clock by the same rule (roles swapped).
  - **N2, benched and evolving threats:** a benched Stage 1 attacker gets the bonus. A Riolu with Mega Lucario ex in the bot's hand is priced as the evolved Stage 1 [F] form. The opponent's evolutions are not scanned (board only).
  - **N2 off / nothing to read:** with no such Stadium, or with Hiking Trail or Fragrant Forest in play, `kmb`'s clock equals kog's (the bonus is 0, so the arithmetic is the same numbers).
  - **Flag-off identities (bitwise):** `KM` with both flags off equals `KOG`; km with N2 off equals `kma`; km with N1 off equals `kmb`.
  - **Composition (B only):** `km − kog = (kma − kog) + (kmb − kog)` on every position of 12 random games (Altaria v Lucario, Altaria v Blaziken, Lucario v Sceptile, Hydreigon v Weezing), from each player's own view, as `koh_is_kog_with_r_prime_and_reads_as_its_parts` does (`:5340`). Both switches touch different terms, but it is a float identity and not bit-exact in general, so the test uses 1e-9. Under A, `km` is `kmb` and there is nothing to compose.
  - **Wiring through `get_player` (a test in the style of the kq3, kd3 and kpr3 ones).** The shared arm ends in `_ => kor_value_function` (`players/mod.rs:685`). A code added to its or-pattern (`:657-670`) without its own inner arm would compile and play kor, and parse tests and clean-run smokes would not catch it. The test builds km3, kma3 and kmb3 through `get_player`. On a Goo-zooka board the codes with N1 on (B: km3 and kma3; A: kma3) choose Play(Goo-zooka), and kog3 and the codes with N1 off do not. On a Training Area or Arena board the codes with N2 on (km3 and kmb3) differ from kog3, and kma3 does not. The boards are built so that N1 or N2 decides the pick.
  - **Parser:** `km3`, `kma3`, `kmb3`, `KM5` parse; `km`, `kmx`, `kma` alone, `kma3x` and `km1a` are rejected (by analogy to kt's `kt1a`); `kog3`, `koh3`, `kph3`, `kt3`, `kta3` parse as before.
  - **Full suite:** passes. No existing test's expected value is edited. Call sites are updated for the new argument wherever a signature changes (tests call the clock functions positionally: `:3272, 3597, 4002, 4083, 4448, 5062, 5123, 5312`, and `turns_until_opponent_wins_scan` at `:4433, 4663, 4785, 4935`). If every existing signature stays as a thin wrapper, no call site changes.
  - **Diagnostics in the build round, not preconditions of registering:**
    - *Card arithmetic (open question 13).* Two constructed boards that end the turn (the line includes EndTurn or Attack; hands filled with inert cards; only the card term compared): X Speed then Copycat against Copycat alone, no Trail, differs by exactly +1; with Trail in play and a hand under 3, playing any card is +1. A leaf that stops mid-turn has no Trail top-up, and Thieving Machine breaks the 20-cards-per-side conservation, so neither appears in these boards.
    - *The Goo-zooka board (open question 14).* One constructed 03b board with Goo-zooka playable, scored under kog and kma, showing whether N1 changes the pick.
- **Identity** (on the table's deals, 72,000,000 + pairing × 10,000 + i; pairings are `legality_scan`'s: 0 = Altaria v Blaziken, 2 = Altaria v Lucario, 17 = Hydreigon v Weezing). The scope is kt's item 7 (kt README 206-222), with km's presets. km edits shared player code (the clock at `value_functions.rs:1161-1258` and `extract_features`' signature), and the reading pairs km3 against the stored kog3 files and counts any drift as km's. Only an identity that covers those files licenses that reuse (RUN5 "Baselines move with the engine"). Moves, choices, openings and results:
  1. **k3, kp3 and kog3 in full** (14,000 games each). k3 and kp3 against the official engine's references at the time of the build (its frozen table once the official engine carries it; otherwise `rl/results/rules09_fixes_2026-09-26/af8489f_{k3,kp3}_500.jsonl`, which equal it). kog3 against `rl/results/koh_2026-09-28/bd2907f_kog3_500.jsonl`, and also against `rl/results/kog_composition_2026-09-27/table_kog3.jsonl` (14,000) and `new17_kog3.jsonl` (8,500), the files the reading pairs km3 against.
  2. **kq3 in full** (14,000; its clock runs the touched function: `next_attack_reduction` is a parameter of it). **kd3 and kpr3 at 1,120** (i < 40 of every pairing).
  3. **The kog3 coverage baselines** (B2e, Scizor, second lists) at i < 40 of every pairing (step 5).
  4. **Switches off:** `EvalFeatures::KM` with both flags cleared equals `KOG` (a test).
  5. **N2 on, nothing to read:** `kmb3` (km3 itself under D1 option A) on the 28 cells that hold neither the panel Altaria nor the panel Lucario list (their lists carry neither Training Area nor Arena), 14,000 games, about 27 minutes. It must equal kog3 exactly. This covers Hiking Trail, Fragrant Forest and any other Stadium in play, where a unit test alone would not.
  6. **Execution, kept as an addition:** kog3 at the km build on pairings 0 and 2, 40 deals each. Pairing 2 has both Stadiums in play, so the touched clock lines are executed.
  7. **Smokes:** `km3`, `kma3`, `kmb3` on pairings 0 and 2, 40 deals: clean runs. Their changed games are counted by the reading, not here. (The wiring test above, not these runs, shows a code plays the right function.)
  8. **The diff touches `engine/src/players/` only.**
  9. **Any difference stops the reading.** After 80 identical games the 95% upper bound on an unseen difference rate is 3.7%. That is too loose for a route that sits within a few points of its threshold, which is why the scope is kt's.
- **Timing:** `km3`'s 40-deal run within **1.25 × kog3's**, with kt's rerun-once rule (kt_tables README 79-80: if the first pair is over, both arms are rerun once and the second pair decides). It is measured on pairings 0 and 2 (where Stage 1 and [F] threats and both Stadiums occur), in user CPU time or best of several runs, both arms fresh on the laptop as `run_kt.sh` now does. RUN5 has no timing rule of its own.
- **Which program plays km.** The official program (`rl/engine-2026-09-28/`) has no `km` codes, so every km game, counter and trace is played by the km build's own programs, named with their sha256, and each output file name starts with that build's commit. (kt's codes are the opposite case: they already exist in the official program as kp-based presets, which kt's review flagged, F1 and C1 in `kt_2026-09-26/REVIEW_amendment2_laptop_2026-09-28.md`. `km` avoids that by being new.)

---

## 5. The reading (registered on the 45 cells, RUN5 "The frame a candidate is read in")

**Step 1. Footprint: the first result read, committed alone.** No km game precedes the passed identity and tests (section 4.0). Then: km3 on both sides of the 45 cells on the table's deals (72,000,000 + pairing × 10,000 + i for the 28; 21,108,000,000 + pairing × 10,000 + i, pairings 8-24, for the 17; i < 500; even i puts the first-named deck in seat 0) against kog3's `rl/results/kog_composition_2026-09-27/table_kog3.jsonl` and `new17_kog3.jsonl`, paired by (a, b, i), on the `moves` field, as `footprint_km.py` (section 4.0) does after `footprint.py`. **Under 15%: the reserve route. 15% or more: the ordinary rule.** The route is fixed on this number, for km3. Under B, `kma3` and `kmb3` are diagnostics and get no route of their own. Under A, `kma3` is (`kmb3` is km3 then). There is no reliable prediction: about 3% to 19% (section 7). So both routes are registered in full.

**Step 2. Build, identity, tests** (section 4).

**Step 3. Mechanism check** (diagnostic, gates nothing). km3 against kog3 on the first 200 deals of each of the 17 cells that hold the panel Altaria or Lucario list (their own deals, so no new seeds; kt's counters used 100, but the sign lines below want more), with a counter tool that extends `tool_turn_effect_census_2026-09-25/tool_census.rs` to count Stadium plays, Field Blower's Stadium targets, and X Speed, Boss and Copycat plays (its fingerprints are checked against the table file, as kt's counters were). At each X Speed turn it also records whether Hiking Trail is in play, which settles the 96-turn upper bound of 1.2. Predictions, from the cards' stages:
- **M1, Arena of Antiquity** (Lucario's side, 9 cells): plays per offered turn **rise**, pooled paired 95% interval above zero, and positive in at least 7 of the 9 cells. Only Lucario's [F] Pokémon gain, against ex Actives.
- **M2, Training Area** (Altaria's side, 9 cells): it rises where the opponent's main attackers are not Stage 1: Blaziken, Hydreigon, Sceptile, Suicune, Rayquaza (Mega Blaziken ex, Hydreigon, Mega Sceptile ex, Baxcalibur are Stage 2; Suicune ex and Mega Rayquaza ex are Basic). It does not rise where they are: Lucario (Mega Lucario ex), Vespiquen (Vespiquen ex), Weezing (Team Rocket's Weezing ex), Altaria/Greninja (Mega Altaria ex). Line: (mean change over the first five) − (mean change over the last four) is positive with its paired 95% interval above zero.
- **Size.** At 200 deals M2's 95% half-width is about 6 to 9 points (the review's power lens, an estimate). An M1 or M2 line that fails reads "not shown at this size", not "wrong".
- **M3, Field Blower's Stadium targets:** reported.
- **Sentinels, reported:** X Speed plays and its no-retreat share (Lucario, Vespiquen, Weezing cells), Boss (Suicune cells), Copycat. No switch touches these cards. They are expected unchanged within paired noise. They are counted only in these 17 cells.

**Step 3b. The Goo-zooka and Plaza measures** (reported beside; gate nothing).
- **Goo-zooka's plays per chance** on brew 03b, and on decks 12, 14, 15 and brew 03a, under km3 (B) or kma3 (A, or B if attribution is wanted) against kog3, on floor.py's own default deals (240 games per matchup against each of the eight panel decks; seeds 7,100 + 1,000 × opponent, +500 for seat 1; `floor_brews_2026-09-28/README.md`). The kog3 arm is the floor's own games where a page exists in `../floor_brews_2026-09-28/` (03b, 10). For the others it is kog3 at the km build on the same defaults. **Prediction:** well above 2.1% in the five 03b matchups where it is 0 today (03b's 95 of 4,445 chances: 72 of 541 against Blaziken, 21 of 624 against Altaria, 2 of 440 against Weezing, 0 of 2,840 elsewhere). This is a prediction from the code, not proven (section 2, N1's "Honest size").
- **Plaza's plays per chance** on brews 05b and 10 (91% and 54% today), on the same terms, because the "direction" claim stays.
- **The fallback, stated now.** If the pick does not change, the reading says "km does not fix Goo-zooka". No constant is added. What to do next is Dustin's decision after the reading.

**Step 4. The 45 cells, by the route.**
- **Size:** the table's 500 deals per cell for the 45-cell reading and the mixed rows. RUN5's "doubling deals to 2,000 when undecided" sits in "Variants and process" next to the τ̂-margin E = 3 comparison. **km does not extend it to the ΔMSE rule, (b), (c), (d) or the coverage rows** (kt did not either: its amendment 1 kept (d) as one test, not a second chance). There is no doubling, no rerun and no second block for any of them. Clause (d)'s size is D2's.
- **Ordinary rule (footprint 15% or more).** Paired ΔMSE, **km3 minus kog3** (`score45.py`'s "dMSE new - current"), whole 95% interval below zero (`score45.py`, `rl/results/kpf_2026-09-26/reading/`, on the 45 cells with the 44-cell decision set beside it as it prints; the by-event interval printed beside, RUN5 "The yardstick"). Vetoes as rule v2: a cell's miss grows more than 6, a deck's gap more than 2, a held-out deck more than 2 further. They count only when mixed rows on the same deals (km3 on the deck, kog3 on the other, against kog3 on both) show km3's own side worse beyond paired noise, and never on a cell whose Limitless band is wider than about ±15.
  - **The two signs are opposite on purpose.** ΔMSE is km3 minus kog3 and must be below zero. The τ̂ margin below is kog3 minus km3 and must be above its bound. Both say km3 is better.
  - **Expected sign (stated now).** ΔMSE is expected to be **positive** if N2 gains on Lucario. Lucario is already over-rated by the simulator (52.2 under kog3 against 45.6 real, +6.6), and a better-played Lucario moves further from the real figure. The review's power lens puts ΔMSE at about +2.64 per point of Lucario gain (+3 to +10 for a gain of +1 to +3 points), against a ΔMSE sd of 3.7 to 6.5. So a real gain almost never clears zero on this route (model estimates).
  - **(d) and its report beside are run and reported under both routes.** On the ordinary route they gate nothing (kt README 124, for kta3 at 15% or more). The rule itself stays as Dustin set it.
- **Reserve route (footprint under 15%),** RUN5 "Reserve route for a change the table can barely see" (lines 534-541) and section 8 of `docs/REVIEW_2026-09-24_direction.md`, restated as kt's registration restates it:
  - **(a)** the footprint of step 1.
  - **(b) no harm:** the τ̂ margin (kog3 minus km3) has its 90% interval's lower bound at −1.0 or above, and no veto counts under rule v2. The by-event interval is printed beside it (RUN5: every 45-cell reading prints it).
  - **(c)** in the mixed rows for the pairings where km3's footprint is non-zero (km3 on the first-named deck only, then the second-named only, against kog3 on both; 500 deals), no deck's own side is worse beyond paired noise. Pooling: per deck, pooled over its cells, as `score.py` does.
  - **(d) the gain: one gating archetype, one exact test, fixed now.** **Mega Lucario ex Lucario**, the panel's `decks/research/lucario.txt` (1 Arena of Antiquity). It is Limitless rank 1 both by the Sept 10 top 30 and by development matches, 391 of its 398 development lists carry Arena, and no file of Dustin's carries Arena.
    - **The rows.** The nine rows are clause (c)'s mixed rows for Lucario's cells (its 7 table cells, Rayquaza v Lucario, Altaria/Greninja v Lucario), read a second time for gain. Each row is km3 on Lucario with kog3 on the other deck, against kog3 on both, paired by deal.
    - **The deals.** 72,000,000 + pairing × 10,000 + i for its 7 table cells. 21,108,000,000 + pairing × 10,000 + i for Rayquaza v Lucario and Altaria/Greninja v Lucario (their pairings among 8-24 of `new_decks.tsv`). The first-named deck is in seat 0 on even i.
    - **The statistic.** Lucario's own-side score per game (`first_deck_score` in the games files, Lucario's side whichever seat it is in), as `paired()` in `rl/results/koh_2026-09-28/laptop_reading/read_koh.py` reads it: the equal-weight mean over the 9 cells of the per-cell mean difference, in points, with the variation check's interval, 1.96 × sqrt(Σ per-cell variance of the mean difference) / 9. Draws count as `first_deck_score` counts them.
    - **The size (D2).** Option 500: N = 500 deals per row, the (c) games themselves. Option 2,000: N = 2,000 per row; the first 500 deals of each row are the (c) games, and deals 500 to 1,999 come from D2's new block (both arms, km3-on-Lucario and kog3-on-both, run on the block).
    - **It passes if the whole interval is above zero.** It is read once. No doubling, no rerun, no second block.
    - **What the size can and can't see.** The size the mechanism predicts is about the noise on a deck average (the variation check's paired intervals on 7 cells ran ±1.2 to ±1.9), so this can fail, which is what the route is for. The review's model (q = the share of games whose result flips, unknown, taken as 0.08 to 0.30) puts the 9-row half-width at about 0.8 to 1.6 points at 500 deals and 0.4 to 0.8 at 2,000 (half-width = 1.96 × 100 × sqrt(q / N) / 3 points). A real gain of 1.2 to 1.9 points clears the 500-deal test about 31% to 99% of the time (81% to 99% at q 0.08; 31% to 64% at q 0.30). A real 1-point gain is missed 34% to 77% of the time at 500 deals, and cleared 69% to 100% of the time at 2,000. These are model estimates, not measurements.
    - **Printed beside every gating interval (reporting only):** its sd, and the smallest gain it could detect half the time and 80% of the time.
    - **Reported beside, gating nothing:** Mega Altaria ex Espeon (`altaria.txt`; Training Area in 329 of 336 lists; 9 cells); B2e's Manectric and Raticate (Training Area) and Whimsicott ex Ariados (Goo-zooka in 21 of 21 lists, Trap Territory in 21 of 21); Dustin's decks (section 7); the real Limitless cells of Lucario and Altaria before and after (RUN5: a reported figure, not a gate). The same direction on the beside decks is supporting evidence; the other direction is a finding to write down.
  - **(e)** adoption for the screen and the table together.
  - **Closure sentence, adapted to km's cards.** Section 8's sentence, quoted from `docs/REVIEW_2026-09-24_direction.md` (the Skarmory bullet): "if the card census finds no Limitless top-30 archetype outside Dustin's decks that carries reduction Tools or turn-effect cards, or finds one with no usable decklist, the route is closed for that candidate and adoption can come only by Dustin's explicit override, recorded as such, as with kp3; the route is not loosened after the census is seen." Its card class is "reduction Tools or turn-effect cards". km's cards are Stadium damage bonuses (Training Area, Arena of Antiquity), which are not in that class. So the adaptation is: **"Stadium damage bonuses count as the relevant cards."** That is one of the items Dustin approves with this text. For km: if the census finds no Limitless top-30 archetype outside Dustin's decks that carries the relevant cards, or one with no usable decklist, the route is closed for km and adoption can come only by Dustin's explicit override, recorded as such; the route is not loosened after the census is seen. The carrier count found two such archetypes, so the route is open on the count. That count was run for this draft before this text was fixed, on the development half only. What was fixed before it ran is RUN5's route.
- **How a b-fail with a real gain reads (stated now; the numbers are the review's power lens, model estimates).** Lucario's deck average is 52.2 under kog3 against 45.6 real (+6.6). If N2 makes Lucario play better, it moves further from the real figure and the τ̂ margin can fall. But (b) is unlikely to be the clause that fails. The τ̂-margin sd is 0.13 to 0.23 at 500 deals. A real Lucario gain of +1.5 gives a margin of about −0.16, and +3.0 about −0.34. So (b) fails only if ΔMSE reaches about +28, far beyond what a small footprint can do. If (b) does fail, the own-side gain is recorded, Lucario's overshoot is added to RUN5's open-cause list ("each fix's reading adds to this list"), and nothing is rescued: adoption then comes only by Dustin's explicit override, recorded as such.

**Step 5. Held-out and coverage decks, before any verdict is final** (RUN5 "A 'not adopted' is provisional until the coverage decks are read", lines 523-530: a "not adopted" is provisional until these are read). Row definitions are kph amendment 2's. The test is amendment 4's (RUN5 lines 495-498).
- **Reach (stated now).** Every switch acts on both sides, so a coverage row is reached when either list carries the card (kt README item 3). Carriers: Manectric and Raticate (Training Area), Whimsicott (Goo-zooka and Trap Territory: N1, so reached under D1 option B only), Scizor (Training Area), the second Lucario list (Arena). N2 also reaches every held-out, Scizor and second-list row whose opponent is the panel Altaria (Training Area) or the panel Lucario (Arena). All coverage rows get mixed rows regardless (RUN5 "How coverage rows count"), so no gate is lost.
- **B2e's six held-out archetypes**, pairings 0-47 (`rl/results/b2e_card_check_2026-09-26/decks/h-*.txt`; deals 21,106,000,000 + pairing × 10,000 + i): km3 on both sides against kog3 on both. **The accuracy veto stands:** an archetype ending more than 2 points further from its pooled equal-weight Limitless average than under kog3 (as `kpg_2026-09-27/heldout_check.md` reads it), counting only through mixed rows. **Also, every time,** own-side mixed rows (km3 on the held deck, kog3 on the panel list, against kog3 on both, paired by deal): the whole 95% interval below zero is harm and blocks the takeover. Dustin's files (pairings 48-95: decks 09, 13, 04, 08, 12 and brew 08) are reported beside.
- **Scizor** (carries 1 Training Area): its 8 rows (`decks/gauntlet_2026-09-26/g-mega_scizor_revavroom.txt`, pairings 0-7 of `tsv/new_decks.tsv`, 21,108,000,000 + pairing × 10,000 + i): km3 on Scizor with kog3 on the panel list, against kog3 on both, the 8-row average, interval 1.96 × sqrt(Σ per-cell variance) / 8. Whole interval below zero is harm. Accuracy reported only.
- **The four second lists** (`v-lucario_2` (carries Arena), `v-suicune_2`, `v-weezing_2`, `l-charizardy`), each on its own deals (`gauntlet_runs_2026-09-26/tsv/var_*.tsv`): the same own-side test, accuracy reported only against the figures amendment 2 names.
- **Baselines (kt README item 4's rule).** kog3's coverage baselines are the committed files: `rl/results/koh_2026-09-28/laptop_runs/scizor_kog3.jsonl` and `var_*_kog3.jsonl` on main, and B2e's `rl/results/koh_2026-09-28/reading/b2e_kog3.jsonl`, which is on the cloud branch and not on main (read with `git show`). They are used if kog3 at the km build equals them at i < 40 of every pairing (section 4, identity 3). For any that fail or are missing, the laptop runs kog3 at the km build on all 500 deals (up to 96 pairings × 500 for B2e) before any km coverage row. `BUILD.md` names each baseline file before the first km game. Open question 3: answered.
- **Count of tests (stated so the harm reading can be judged).** About 21 own-side tests read "whole 95% interval below zero" with no floor (kph amendment 4): 10 decks in (c), 6 B2e archetypes, Scizor, and 4 second lists. On a harmless candidate whose every test has real noise, that blocks about 4 times in 10 (1 − 0.975²¹ ≈ 41%; the review's power lens). It is Dustin's rule, not changed here. Rows a candidate does not move at all have no noise and can't fire. The reading prints the count beside the harm reading.
- A veto or harm on any of these blocks the takeover. A gain is reported, not credited.

**Step 6. Development data (RUN5 "Development data, stated with each reading", lines 531-533).**
- **All 45 cells are development evidence for km,** as for kph. The audit, the Tool census and the X Speed census read kp3's games against the panel lists, and the variation check played Lucario, Suicune and Weezing on the table's own deals. The 17 new cells were used to design kpf.
- **Also development data:** Dustin's quiz answers used in 1.2 and 1.3; the Limitless development half (63 events) whose carrier counts fix (d) (the scan reads `split.json`'s development ids only); this draft's re-tally of the X Speed file; **the floor's 03b page** (`rl/results/floor_brews_2026-09-28/`, 95 of 4,445) and **the floor re-check under kog3** (`rl/results/floor_recheck_2026-09-28/`), which put Goo-zooka on the candidate's list.
- **The Sept 25 holdout is spent** (on kp3, RUN5 "Where things stand"). It is not fresh confirmation data for km. The holdout half's standings were not opened for this draft.
- **The confirmation is the post-freeze read.**

**Step 7. Confirmation** (RUN5 "When post-freeze data is read"; the list is in `postfreeze_2026-09-27/README.md`). km joins that list by a commit there before the data is opened, if it is adopted before the read. Otherwise it waits for the next pull. Reserve route: the τ̂ margin's 90% lower bound at −1.0 or above and no veto, with Lucario's and Altaria's post-freeze cells reported. Ordinary rule: on the post-freeze events alone, at least half its development margin with its own 90% interval above zero. A failure reads "not confirmed at this size". **The lapse clause is kt's** (kt README 201-204): km carries kog's A and F, so if kog's row, or kpg's or koa's that kog inherits, has not passed by the pull at which km's own check passes, km is not confirmed yet. km's passed check stands and is not read again. km stays "unconfirmed" and is confirmed at the first later pull at which kog's, kpg's and koa's rows pass. A failed check, km's or kog's, is read again at the next pull, on the events after it (the rolling freeze). Each check is read on the same engine as its baselines.

---

## 6. What would show it wrong (stated before any game)

Each item says whether it gates or is a diagnostic.

1. **A pin fails (gates).** The new function differs from `modify_damage`, or N1's terms differ from the formula. The switch prices something the engine doesn't do.
2. **The mechanism doesn't show (diagnostic, gates nothing):** M1 or M2's line fails (the Stadium plays don't move as the cards' stages say). It reads "not shown at this size".
3. **Harm (gates):** any deck's own side worse beyond paired noise (whole 95% interval below zero) in the mixed rows on the 45 cells (route (c) or the vetoes), B2e's held-out decks, Scizor or a second list.
4. **No gain (gates, on the reserve route):** (d) fails: no Lucario gain of about X or more at this size, with X printed from the reading's sd. The route is closed and km is adoptable only by Dustin's explicit override, recorded as such.
5. **On the ordinary rule (gates):** the ΔMSE interval isn't below zero. "Not adopted", provisional until step 5. It is not read as evidence that km is wrong: the mechanism itself predicts a positive ΔMSE if N2 gains on Lucario (step 4).
6. **N1 acts beyond its ties (B; diagnostic, reported, no threshold):** the share of games that differ from kog3's in cells whose lists carry none of Training Area, Arena, Goo-zooka, Plaza, Trap Territory, Small Balloon, Inflatable Boat or Bombirdier is read from km3's footprint file and reported. Boss, X Speed and Copycat plays are counted only in step 3's 17 cells. A move there beyond paired noise means an interaction nobody predicted.
7. **What it would say about the class (diagnostic):** if km3 shows no Lucario gain of about X or more at this size, what is left of the Trainer gap may be search cost (row 4 of section 3) and information (Boss), not board numbers. The next candidate is then the search one, registered with a timing budget.

### Outcomes fixed now

Drafted from kt's "Outcomes fixed now" (kt README 401-406). Dustin's word on the text covers them. **A spec change after any reading is a new code.**

- **(A) N1 out of the gate; km = N2 alone.**
  - km3 passes its route: km adopted (screen and table).
  - km3 fails: nothing adopted. `kma3` is read only for the Goo-zooka and Plaza measures (step 3b). The next candidate is registered afresh. N1 as its own candidate is Dustin's to ask for.
- **(B) N1 inside km.** N1 is untested for gain. It is adoptable only through the no-harm clauses (b) and (c), the vetoes and the coverage tests.
  - **Reserve route.**
    - km3 passes (a) to (e), and `kmb3` (N2 alone) also shows (d)'s gain (the same test, rows, deals and size, `kmb3` in place of km3): km adopted (screen and table).
    - km3 passes but `kmb3` does not show (d)'s gain: nothing adopted as built. Dustin's explicit override, recorded as such, is the only route. What to register next is his decision after the reading.
    - km3 fails: nothing adopted. The diagnostic codes are read for attribution only, and the next candidate is registered afresh.
    - `kmb3`'s (d) rows are run only if km3 passes (a) to (c), so no games are spent otherwise.
  - **Ordinary rule.** km3 passes the ordinary rule and step 5: km adopted, on the same terms. km3 fails: nothing adopted.
- **Both:** if the reserve route's (d) fails or the route is closed, adoption comes only by Dustin's explicit override, recorded as such.
- *(Needs Dustin's word: the (B) bullets that make `kmb3`'s (d) a condition are drafted from kt's pattern and the review's text. The review did not spell them out.)*

---

## 7. Predicted footprint and reach

**The affected cards, by list.**

| Card | In the 45-cell lists | In the coverage and held-out lists | Dustin's decks and brews |
|---|---|---|---|
| Arena of Antiquity (N2) | Lucario (1) | v-lucario_2 | none |
| Training Area (N2) | Altaria (1) | Scizor, B2e Manectric, B2e Raticate | deck 09 |
| Goo-zooka (N1) | none | B2e Whimsicott (2) | decks 12 (2), 14, 15; brews 03a (2), 03b |
| Trap Territory, Ariados (N1) | none | B2e Whimsicott | deck 12 |
| Peculiar Plaza (N1) | none | none | brews 05b, 10 |
| Small Balloon, Inflatable Boat, Bombirdier (N1) | Altaria, Suicune, Hydreigon | not counted here | not counted here |
| Cyrus, Sabrina, Repel (N1 only breaks ties) | nearly every list | most | most |

**Footprint on the 45 cells (restated).**
- **N2:** the 17 cells that hold the panel Altaria or Lucario list (9 + 9 − their shared cell; 17 of 45 cells is 37.8% of the games). In those cells I expect 25 to 45% of games to differ. That is a judgment, not a measurement: the audit had the Stadium offered in 76% of Altaria's games and 68% of Lucario's (kp3, `audit_trainers.tsv`), and once it is offered or in play the clock changes many later choices, not only its own play. That gives 9.4% to 17.0% of the 22,500 games.
- **N1 (B only):** at most 1 to 2% elsewhere, from gust and promotion ties, since none of the 10 lists carries Goo-zooka, Plaza or Trap Territory. The other cells are 62.2% of the games, so that is 0.6 to 1.2 points of all games. That is a guess (the guard list in section 6, item 6, is longer now: Small Balloon, Inflatable Boat and Bombirdier are in Altaria's, Suicune's and Hydreigon's lists).
- **The draft's own arithmetic** therefore gives about 9% to 17% under A (centre 13%) and about 10% to 18% under B (centre 14%). The first draft said 13% (9 to 19%) with N1 in.
- **The closest analogues put it lower.** In kt's footprints (as the review read `footprint.txt`), kta3 differed in 559 of 8,500 reached-cell games (6.6%) and ktc3 in 1,315 of 4,500 (29.2%). Applied to N2's 17 cells (37.8% of the games), that is 2.5% and 11.0% of all games. Against that, a Stadium is offered in 76% and 68% of Altaria's and Lucario's games, and kt3 and koh3 (65% and 93%) show broad changes can reach far. None of these is like-for-like.
- **So the statement is: between about 3% and 19%, no reliable centre.** Both routes are registered in full and the compute plan is ready for both:
  - ordinary rule: the 45-cell reading and its mixed rows;
  - reserve route: (c)'s mixed rows can need 45,000 games, about 87 minutes at 8.6 games a second; (d) adds 27,000 to 36,000 games under D2 option 2,000 (about 52 to 70 minutes). Under D1 option B, `kmb3`'s (d) rows add one more arm on the same deals if km3 passes (a) to (c): 4,500 games at 500 per row, 18,000 at 2,000 (about 9 and 35 minutes).
- **The reading prints** the smallest ΔMSE and the smallest own-side gain it could detect, from the same games (reporting only).
- **The rest of the 28 cells** (Blaziken, Hydreigon, Sceptile, Suicune, Vespiquen, Weezing among themselves, and the Rayquaza and Altaria/Greninja cells against them) should be identical apart from N1's ties (B).

**Dustin's decks and brews it reaches.**
- **Deck 09** (Training Area): N2 acts. Read for free in B2e block B (pairings 48-55), reported beside.
- **Deck 12** (Goo-zooka, Trap Territory; B2e block B pairings 80-87): **N1 acts** (B: km3; A: `kma3` only). Its Goo-zooka lines go from +1 to +2 under Hiking Trail (strict gain), so its Goo-zooka rate is expected to rise, and its Trap Territory lines are priced too. **Its X Speed pattern (52%) is not touched by either switch.** It is the deck to watch for X Speed. Its 57% with Trail against 10% without is the arithmetic in 1.2.
- **Decks 14 and 15, brews 03a, 03b** (Goo-zooka): N1 as for deck 12. **Brews 05b and 10** (Plaza): N1 acts on direction (91% and 54% played today). Step 3b registers the measures.
- **Not reached by anything in km:** X Speed (decks 04, 12; brews 02, 03a, 04, 05, 07), Boss (brew 02), Master Plan (brews 05, 05b), Ilima (01, 02, 13, 15), Flute (08, 14), Rainbow Cave (brew 08, decks 08, 11), Soothing Shore (03, 13). The screen and the floor's coverage flag still mark these as unpriced: the flag keys on hand/deck text and opponent-turn markers (`engine/examples/goldfish.rs:163-215`), which doesn't cover Stadium or status text (open question 8: not part of km).

**Open, not in km** (recorded so they aren't lost):
- **The loss certificate refuses any board with a Stadium in play** (`public_reply.rs:584-587`), so with Training Area, Arena or any Stadium out the bot can't see a proven lethal reply. Not a pricing change.
- **Draws are priced from one sampled shuffle** (census, Supporters finding on Copycat and Professor's Research): a max over one noisy sample favours random-effect cards. Averaging needs a sample count.
- **Future Booster and Beastite** through N2's function, when kt is composed with km (kt gives them 0). kt's clock is separate (`kt_clocks`), so composing needs N2 built into it, with its own identity (the base-change rule, section 2).
- **N1 under kt's switch 2** (the opponent's retreat Tools) needs its own check when the two are composed.
- **Lucario's Fighting Coach and other board abilities** through the same function (open question 4: keep out; its own candidate on top of km if wanted).
- **Whimsicott's Grass Knot payoff** is not in the clock's damage estimate (section 2, simplifications).
- **The Suicune second-Cape swap, repeated with a non-Tool card**, would separate Boss's cost from Cape pricing.

---

## Open questions for the reviewer

Each is marked with the review's answer (`REVIEW.md`, section 4), or **Dustin's call**. Only question 2 is Dustin's call among the 14. D2 is a second call that was not among them.

1. **Amendment 2 or 4.** The brief said amendment 2's definitions. RUN5 lines 495-498 say amendment 4 supersedes amendment 2's tests. I used amendment 2's row definitions and amendment 4's test (no 2-point floor on the own-side veto). Confirm.
   - **Answered: "confirmed."** No 2-point floor on own-side harm; the whole 95% interval below zero is harm and blocks the takeover. Accuracy on Scizor and the second lists is reported only. B2e's "more than 2 further" veto stands, through mixed rows. All three kinds get own-side mixed rows every time. Stale line numbers fixed.
2. **Is N1 worth carrying?** It is near-null on the 45 cells. Its case is direction (Plaza), the retreat-cost sketch in the census and Dustin's decks and brews 12, 14, 15, 03a/b, 05b and 10. It may add 1 to 2% to a footprint that sits near 15%. Drop it if the review prefers a one-switch candidate; the codes make that a one-line change.
   - **Dustin's call (D1, at the top).** The review's lean is option A, N1 out of km's gate. "Whatever he picks, S1's outcomes text is needed": it is in section 6.
3. **B2e's kog3 rows don't exist.** Who runs them (96 pairings × 500, kog3 both sides, at the pinned engine), and does koh's reading commit them first?
   - **Answered: "they exist. Nothing needs to run."** `reading/b2e_kog3.jsonl` is on the cloud branch. Use it if kog3 at the km build equals it at i < 40 of every pairing; otherwise run kog3 at the km build on all 500 deals (about 2.2 hours for 48,000 games, if it ever had to run). Step 5.
4. **Scope of N2's function.** Include board-ability bonuses (Lucario's Fighting Coach)? It would reach all 9 Lucario cells more strongly and push the footprint over 15%, but it is Pokémon-side.
   - **Answered: "keep out."** The class queued is Trainer pricing, and the rule sentence is "a Trainer whose effect changes a board number". It would confound clause (d) and M1. If wanted, it is its own candidate on top of km.
5. **The function is a duplicate, not a refactor.** `modify_damage` keeps its own copy at `core.rs:1997-2012`. Is that enough to stay out of RUN5's rules-file refactor rule, or should `modify_damage` call the new function and take the three-part check?
   - **Answered.** A duplicate leaves `modify_damage` untouched, so it is not a refactor in letter. But the record does not let the draft declare the rule "not triggered" while it also edits `hooks/mod.rs`. "The clean answer is to put the function in `players/`": done (section 2, N2 change 1).
6. **Gating archetype for (d).** Lucario (Arena, +20 against ex, one-sided) over Altaria (Training Area, +10, shared with Stage 1 opponents), because the mechanism is larger and clearer there. Altaria is beside. Confirm before any game.
   - **Answered: Lucario.** Rank 1, Arena in 391 of 398 lists, no file of Dustin's carries Arena. Altaria is "reported beside". "Make the test exact (B2)": done. Dustin's word on the text covers it.
7. **The accuracy direction.** Lucario is already 6.6 above real. A better-played Lucario may fail (b). Is "record it, rescue nothing" (step 4) the right reading?
   - **Answered: yes,** with two corrections: the overshoot is added to the open-cause list, and adoption then comes only by Dustin's explicit override. (b) is unlikely to be the clause that fails; the real exposure is the ordinary route. Both are in step 4.
8. **Coverage flag.** Should the floor's coverage flag (`goldfish.rs`) learn Stadium and status texts, so brews leaning on them read "untrusted"? A screen-tool change, not a pilot one, and the honest treatment for the Trainers km can't fix.
   - **Answered for km: "not part of km."** Changing the flag changes the goldfish program's sha, which the floor pages cite, so it needs its own build and pin. It is a separate screen change and his to ask for.
9. **Identity size.** I followed the brief (2 pairings × 40 deals for kog3 and k3/kp3, plus the switch-off and no-trigger identities). koh's build ran kog3 in full (14,000). Enough here?
   - **Answered: "not enough."** Use kt's item 7 scope: section 4, identity 1 to 9.
10. **The X Speed claim.** The 96-turn "Trail can be in play" group is an upper bound (the census file has no Stadium record). If it matters, one replay of deck 12 with a Stadium counter settles it.
    - **Answered: "no separate replay."** Keep it labelled an upper bound. Step 3's counter records "Hiking Trail in play" at each X Speed turn.
11. **Code letters.** `km`, `kma`, `kmb` are free (no code starts with `km`). Confirm.
    - **Answered: free.** No code starts with `km` on main or on the cloud branch. Entries go before the `k<N>` fallback. Parser tests reject `kma3x` and `km1a`.
12. **Timing budget** 1.10 × kog3.
    - **Answered: use kt's 1.25 × kog3 with the rerun-once rule**, after the function's guard. RUN5 has no timing rule. Registered in section 4.
13. **The card-arithmetic identity is derived, not tested.** No switch depends on it, but section 3's rejection of the discard-pile change and 1.2's reading of X Speed do. One constructed board (X Speed then Copycat against Copycat alone, no Trail: a difference of exactly +1; with Trail in play and a hand under 3: +1 for any played card) would confirm it.
    - **Answered: "it holds by conservation, with two exceptions"** (Thieving Machine; a mid-turn leaf). Confirm with two constructed boards that end the turn. Not a precondition of registering; 1.2 and section 3 stay labelled "derived". Section 4, diagnostics.
14. **Does N1 move Goo-zooka where it matters?** Dustin put Goo-zooka on the candidate's list (Sept 28, about 11:15 pm): brew 03b plays it on 2.1% of chances. The floor flag gives the cause as a payoff during the opponent's turn, which the search doesn't play out. N1 makes the opponent's +1 Retreat Cost count at the leaf, but a leaf that doesn't play the opponent's turn may still see no difference.
    - **Answered in part.** "The draft's worry is refuted by the code": a leaf that doesn't play the opponent's turn still sees the +1, and the sort order breaks the resulting tie toward Play (section 2, N1's "Honest size"). Whether the pick actually changes on real boards is unmeasured. So the measure and the fallback are registered now (step 3b): if the pick does not change, the reading says "km does not fix Goo-zooka". The constructed board is a build-round diagnostic (section 4), not needed before registering. What next is Dustin's, after the reading.

---

## Changes from the review (Sept 29)

The finding ids are `REVIEW.md`'s. "Note N1" to "Note N11" are the review's NOTE items; they are not the switch N1. Before applying, each fix was checked against the rules and code. The checks that held: B1 (koh's printout reads "dMSE new - current ... (not below 0)"); S3 (`hooks/mod.rs` re-exports every hook by name; the two Stadium bonus functions are `pub fn`; `pokemon_energy_types` is `pub(crate)`); S4 (`has_stadium` builds the reference text first, `stadiums.rs:106-113`); S5 (`zone_to_bench` stops at `:1089-1128`; the scan is at `:1161`); S6 (`players/mod.rs:685`); S11 (`git ls-tree`: `b2e_kog3.jsonl` is on the cloud branch only); Note N1 (the RUN5 line numbers); Note N10 (Bombirdier's text by `card.py`; `ExtraDamagePerRetreatCost` is not in `value_functions.rs`); the sort order and `max_by` behind S2. Not re-read: the power figures (model estimates), kt's identity counts and `footprint.txt` (kt result files were not opened), kt_tables README 77-81.

**Blockers**
- **B1:** the ordinary rule now reads "km3 minus kog3 (`score45.py`'s 'dMSE new - current'), whole 95% interval below zero". The τ̂ margin stays kog3 minus km3. The two opposite signs are stated once (step 4).
- **B2:** clause (d) is one exact test: the rows (clause (c)'s mixed rows for Lucario's nine cells), the deals, the statistic (`first_deck_score`, `paired()` in `read_koh.py`), the size (D2), "read once, no doubling, no rerun, no second block". The doubling phrase is limited to the τ̂-margin case and never reaches (b), (c), (d), the ΔMSE rule or the coverage rows. "No new seed block" (Seeds line) is now true under both D2 options, with one proposed named block under option 2,000. Its sd and the smallest detectable gain are printed beside every gating interval (reporting only). The size itself is D2, open.

**Should-fix**
- **S1:** new "Outcomes fixed now" (section 6), for D1's two options. States what is adopted, that N1 is untested for gain and adoptable only under no-harm, that a Dustin override is the only route if N2 fails alone, and "a spec change after any reading is a new code".
- **S2:** N1's "Honest size", the "at a glance" Reach line, ruling 3, the deck 12 line and question 14 rewritten (the tie goes toward Play by sort order; the rate is expected to rise; a prediction, not proven, with the limits). New step 3b registers the Goo-zooka and Plaza measures, reported beside, with the fallback "km does not fix Goo-zooka". The constructed 03b board is a build-round diagnostic. Question 2's "and a tie for Goo-zooka" is dropped for the same reason.
- **S3:** the function lives in `players/` (`crate::stadiums` functions called). The rule line reads "through the engine's own functions". The diff is `players/` only. The core.rs fallback is written as an additive rules-file change. Section 4's "Rules-file touch" bullet and question 5 follow.
- **S4:** the function returns 0 first when `state.active_stadium.is_none()`; the evolution-form lookup comes after. Timing is 1.25 × kog3 with kt's rerun-once rule, on pairings 0 and 2, in user CPU time or best of several runs.
- **S5:** the flag path is named (a new scan parameter, with thin wrappers or carried in `Projection`). "No test edited" now reads "no existing test's expected value is edited; call sites updated if a signature changes".
- **S6:** a `get_player`-level test; parser tests reject `kma3x` and `km1a`.
- **S7:** N1's placement is a registered implementation constraint. Bitwise equality only for flag-off identities; 1e-9 for the composition and tie tests. The Q13 boards end the turn, use inert hands, and compare only the card term.
- **S8:** the identity scope is kt's item 7 with km's presets (section 4, identity 1 to 9). The old identity 3 (pairings 17 and 14) is replaced by `kmb3` on the 28 non-carrier cells. The pairing-2 execution argument is kept as an addition.
- **S9:** new section 4.0 (cloud, laptop, no overlap, gate and order, two output folders, `read_km.py` written blind and committed before any result, queue behind kt, the laptop's tier-1 second read). Step 1 now says the footprint is the first result read, not the first thing run. Timing added to the laptop jobs.
- **S10:** the lapse clause is replaced by kt's (a passed check stands and is not read again; a failed check is read again at the next pull).
- **S11:** the baseline paragraph is rewritten on kt's item 4 rule with the committed files named; "who runs them" is no longer open (question 3 answered).
- **S12:** new "base-change rule" (re-issue by dated amendment if kt or kta is adopted first; composition under RUN5's rule with N2 built into `kt_clocks`). "Not kt's" is rewritten to say N1 prices the opponent's retreat Tools that kt parked, and that composing needs its own check.
- **S13:** step 4 states that ΔMSE is expected positive if N2 gains on Lucario (the review's power numbers), and that (d) and its report beside run and are reported on both routes. Section 6 item 5 no longer reads a ΔMSE fail as evidence against km.

**Notes**
- **Note N1:** RUN5 line numbers updated (417-420, 495-498, 503-505, 523-530, 531-533, 534-541); the refactor rule (472-478) and the doubling phrase (558-559) are cited by section name only; section names added beside the others. The by-event interval is printed beside the τ̂ margin under the reserve route too.
- **Note N2:** a "Decision this informs" line; the heading now says "Three rulings"; a status block listing Dustin's word on the text, the build and the tables, and that the overnight delegation to Fable does not cover it.
- **Note N3:** the footprint prediction is restated as between about 3% and 19%, no reliable centre, with the arithmetic and the analogues (the review's figures for kt's footprints). Compute plan for both routes; the reading prints the smallest detectable ΔMSE and own-side gain.
- **Note N4:** the "b-fail" paragraph replaced with the review's numbers; "added to the open-cause list"; the override sentence; section 6 items 4 and 7 use "no Lucario gain of about X or more at this size".
- **Note N5:** (c)'s pooling stated (per deck, over its cells, as `score.py` does); the count of own-side tests and the 41% figure stated; the reading prints the count.
- **Note N6:** each item of section 6 marked "gates" or "diagnostic"; item 6 is a reported figure with no threshold; sentinel counts are stated as 17-cell counts; M1 and M2 misses read "not shown at this size", with M2's size.
- **Note N7:** section 8's closure sentence quoted verbatim beside the adaptation; "Stadium damage bonuses count as the relevant cards" is listed among the items Dustin approves.
- **Note N8:** opponent-Stadium reach for coverage rows added (step 5); all coverage rows get mixed rows regardless.
- **Note N9:** development data adds the floor's 03b page and the floor re-check, and says the Sept 25 holdout is spent; the footprint script is named (`footprint_km.py`, from `footprint.py`).
- **Note N10:** simplifications 1, 3 and 5 stated (section 2); Small Balloon, Inflatable Boat and Bombirdier added to the guard list; the citation for "free" choices fixed to `:630-771`.
- **Note N11:** the 96-turn group stays labelled an upper bound; the step 3 counter records "Hiking Trail in play" at each X Speed turn.

**Open questions:** all 14 marked (13 answered or answered in part, question 2 Dustin's call). D2 added as a second call.

**Not applied, or applied differently**
- **S3, "put a comment on both sides pointing at the other":** applied on the `players/` side only. A comment in `hooks/core.rs` would make the build diff touch a rules file, which is what S3 avoids. The pin test is the guard against a later change on either side.
- **S2, "on the floor's own deals and seeds (`floor_brews_2026-09-28`)":** that folder holds pages for brews 02, 03b, 07, 08, 09 and 10 only. Decks 12, 14, 15 and brews 03a and 05b have no page there. The measure uses floor.py's default deals for all of them, and kog3 at the km build for the arms that are not on file.
- **S1, the option-B outcome bullets that make `kmb3`'s (d) a condition:** drafted from kt's pattern and the review's list. The review did not spell them out. Flagged in the text.
- **The D2 seed block** (22,900,000,000 – 22,900,081,499) is a proposal. START_HERE.md was not edited; the registration commit writes it into the seed table.

**Notes left:** none skipped. Two are partial. Note N1: the numbers are updated, and they will drift again, so section names are kept beside them. Note N3: the sizes and analogues are the review's figures, not re-derived (the 37.8% and the arithmetic were re-checked).

**Corrections at the check (Sept 29, by a reader other than the editor; the review's order, step 3)**
Each finding (B1, B2, S1 to S13, Note N1 to N11) was compared with the text, the rules and the code. All are applied, or answered with a reason that holds. D1 and D2 were checked both ways and are still open. No new rule or number was found, apart from the items already flagged (the option-B bullets, the D2 seed block). These slips were fixed in place:
- **Section 2, N2 change 1:** "the new function and the evaluator name none" was wrong for the new function, which calls the two Stadium functions. It now says the function names them by calling them, as the engine's damage stage does, and the evaluator names none.
- **Step 1:** "`kma3` and `kmb3` are diagnostics" now says under B. Under A, `kmb3` is km3.
- **Section 4, identity 5:** `kmb3` marked as km3 itself under A.
- **D2 option 2,000:** the block's row order made exact (the 7 table cells in table pairing order).
- **Step 4 (d), power line:** the review's "0.3 to 0.8" half-width at 2,000 deals is 0.4 to 0.8 by the review's own formula (0.41 at q 0.08). The formula is written in.
- **Section 7 compute plan:** the cost of `kmb3`'s (d) rows under B added (arithmetic only: 9 rows × N games).
- **Section 4.0:** the footprint script's two lines to change (14 and 17) both named.
- **Base-change rule:** "did for koh" now "provides for koh" (kt README line 56 is a rule, not a past act).
- **Question 12's answer:** the stale "(or state why 1.10 is right)" removed.
- **N1's sort-order bullet:** AttachTool added to what Play beats (it sorts before Attack, as the bullet above it says).
- **Section 4 full suite:** the four `turns_until_opponent_wins_scan` test call sites (`:4433, 4663, 4785, 4935`) added to the positional-call list.
- **Step 5 reach:** Whimsicott's N1 reach marked "under B only".
- **Timing:** kt_tables README's rerun-once rule re-read (lines 79-80) and cited.
- **Changes list, Note N1:** 472-478 and 558-559 are not cited by number in the text (section names only). Corrected.
Left open, not fixed (the review's wording, a choice for Dustin or the next editor):
- **Timing measure:** the text says "user CPU time or best of several runs". kt's rule gates on wall time, with CPU seconds recorded beside. One measure should be named before the text is committed.
- **(d) on the ordinary route** is run and reported but its size is not stated. It gates nothing there, so the gap is harmless. D2's cost line ("only if km lands under 15%") suggests the 500-deal rows.
- **Power figures:** the review's "+3 to +10 ΔMSE for a +1 to +3 point Lucario gain" does not follow from its own "+2.64 per point" (that gives +2.6 to +7.9). It is a model estimate and was not changed.

**Still needs a decision**
- **D1** (N1 inside km's gate): open. The review's lean is option A.
- **D2** (clause (d)'s deal count, and its seed block if 2,000): open. The review's lean is 2,000 for (d) only.
- **Under D1 option B:** whether `kmb3`'s (d) is a condition of adoption, as drafted in "Outcomes fixed now".
- **Dustin's word** on the text (including "Stadium damage bonuses count as the relevant cards"), then on the build, then on the tables.
- **A second reader** for this applied text: the review's step 3 check was done Sept 29 (see "Corrections at the check"). It was not a second full review. Whether anyone else reads it is Dustin's or the laptop's call.
