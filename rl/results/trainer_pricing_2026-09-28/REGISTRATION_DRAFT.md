# DRAFT (Sept 28): `km`, Trainer pricing on kog, two list-free switches

**Status: draft for one review. No code and no game.** Nothing here is registered until the review's findings are applied and the text is committed. Dustin's word on the text is still needed (kt's registration says the same of itself).

**Sept 29: committed as a draft, with its review (`REVIEW.md`), for the record. This commit is not a registration.** The review found two blockers (the ordinary rule's sign at line 170; clause (d) is not yet one exact test) and 13 should-fix items. Two calls are Dustin's: keep N1 inside km, and clause (d)'s deal count.

- **Build path** (RUN5, Dustin Sept 28 about 7:30 pm, "the cloud", line 403): the cloud gets one round, meaning build, one review and the identity check. The laptop then runs the tables. This draft names the laptop jobs so the two don't overlap.
- **What was run to write it:** only read-only counts of files already in the tree (the X Speed census file, the Trainer audit TSV, the Limitless development standings) in a scratch folder outside the repo. The numbers are in `SCRATCH_NOTES.md` beside this file. No game, no build.
- **Seeds:** the table's own deals only. No new seed block.
- **Line numbers** are from the files as read on Sept 28, 6 to 7 pm. Other sessions were editing RUN5 and kph's registration while this was written; the section names are the anchor.

**At a glance**
- **What km is:** kog plus two switches, each a list-free rule the engine already has. **N1:** the opponent's Active Retreat Cost counts, as the bot's own does (the score's one one-sided board number). **N2:** the lasting Stadium damage bonus (Training Area, Arena of Antiquity) counts in the threat clock for both sides, through the engine's own damage hook.
- **Why so small:** of the 16 Trainers outside kt that the score misses or half reads, only 4 have a fix that needs no constant, no list and no hidden-hand prior. Team Rocket's Boss is among the 12 that don't (1.3, section 3). X Speed isn't one of the 16: the score reads it, and its pattern comes from the card arithmetic (1.2).
- **The X Speed finding:** the census's 23% "waste" is mostly the score's own card arithmetic (39% Copycat shape, 43% where a Hiking Trail can be in play). Only 4% of X Speed turns have no explanation. Nothing in km changes it.
- **Reach:** N2 touches the two biggest archetypes (Arena in 98% of Lucario lists, Training Area in 98% of Altaria/Espeon lists). N1 reaches Dustin's decks 12, 14, 15 and brews 03a, 03b, 05b, 10, and is close to a tie for Goo-zooka.
- **Route:** predicted footprint 13% (9 to 19%), a toss-up around the 15% line, so both routes are written out. The reserve route's clause (d) gates on Lucario.

**Two rulings that landed while this was written, and how they are used**
1. **Coverage rows** (RUN5 "How coverage rows count", Dustin Sept 28 about 6:40 pm; kph amendment 4). The brief said to use kph amendment 2's definitions for Scizor and the second lists. Amendment 4 supersedes amendment 2's *tests* (RUN5 line 483). So step 5 takes amendment 2's *row definitions* (which rows, which deals, the interval formula) and amendment 4's *test* (own-side, whole 95% interval below zero; accuracy reported only). Open question 1.
2. **"A registration written before the games and satisfying the rule outranks a reviewer's paraphrase after it"** (RUN5 line 488, kt's clause (d)). So clause (d) below names one gating archetype and one exact test. Anything else is "reported beside" and gates nothing.
3. **Goo-zooka joins the candidate's list** (Dustin, Sept 28 about 11:15 pm Central, relayed verbatim by Fable): "Brew 03b's borderline through Goo-zooka at 2.1 percent use is the Trainer-pricing blind spot showing up again, which puts a fourth card on that candidate's list."
   - The evidence: Team Rocket's Goo-zooka was played on 95 of 4,445 chances (2.1%) in brew 03b's floor check under kog3 (`../floor_brews_2026-09-28/brew-03b-arceus-crobat-nihilego-toxapex.md`, a flag under 25%). The Sept 25 audit found the same 2.1% for this deck.
   - **What this changes in the draft:** Goo-zooka is now a card the candidate is meant to move, not only a reach line. N1 prices its effect (the opponent's Active +1 Retreat Cost), but section 7 predicts it is "close to a tie" and changes little. The floor flag says the effect "pays off during the opponent's turn, which the search doesn't play out".
   - Open question 14 asks whether N1 moves 03b's Goo-zooka rate at all. If it doesn't, the list names a card km doesn't fix, and the reading must say so.

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
- **So the "23% waste" overstates it.** Shape 1 thins a dud out of the shuffle. Shape 2 is cycling a dud for a fresh draw under Trail. Neither obviously costs a game (my reading; the census measured rates, not harm). Only the 38 turns (4% of X Speed turns) have no explanation here. I could not tell from the file which of the 96 had a Trail actually in play (it records move kinds, not Stadiums), so 96 is an upper bound.
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

**Rule (one sentence):** *a Trainer whose effect changes a board number the score already knows how to read is priced by that number, for both players, through the engine's own hook.* No card is named in the evaluator, no constant is added, no list is used.

**km = kog + N1 + N2.** Diagnostic codes: `kma<N>` = kog + N1 only; `kmb<N>` = kog + N2 only; `km<N>` = both. The single-switch codes are run only if the reading needs attribution. The parser entries go before `k<N>` (see the `kt` block, `players/mod.rs:260-274`, and the parser's own comment that a prefix must come before `k<N>`, which would reject it).

### N1. The opponent's Active Retreat Cost counts, as the bot's own does

- **Today.** Eleven of the score's terms are `mine − theirs`. Two are one-sided: the opponent's discard count (0.1 a card, `:774`) and the retreat term, `(−my.active_retreat_cost) × params.active_retreat_cost` (`value_functions.rs:763`), weight 1.0 (`:51`). The opponent's cost is already extracted (`:862`, through `get_active_retreat_cost`, `:919-943`, which reads the board cost without this turn's discounts) and then dropped.
- **Change.** `(opp.active_retreat_cost − my.active_retreat_cost) × params.active_retreat_cost`. Same weight, same extraction, no new function. The setup evaluation (`:675-714`) is untouched: it never reads the opponent, whose setup is masked.
- **What it prices.** Goo-zooka (`apply_trainer_action.rs:421-427`: `IncreasedRetreatCost { amount: 1 }` on their Active for a turn), Ariados's Trap Territory (`hooks/retreat.rs:251-262`), Peculiar Plaza's −2 for **both** players' [P] Pokémon (`stadiums.rs:119-127`, read at `retreat.rs:224-230`), and which Pokémon a gust or a knockout leaves in front of them.
- **Honest size.** At weight 1 a Goo-zooka nets +1 for the effect and −1 for the card: a tie. `Iterator::max_by` keeps the last of equal scores (`expectiminimax_player.rs:340-350`), so a tie is decided by list order, not by value, and N1 is **not expected** to make Goo-zooka played. What it does fix is direction: Plaza is played 91% of offered turns in brew 05b whoever it helps; under N1 it stops paying when only their [P] Active benefits. It also removes the score's one one-sided term before the next candidate builds on it. This is the census's own fix sketch for Goo-zooka and Plaza ("Score the opponent's Active retreat cost, which is already computed").
- **Not kt's.** kt's README says of the opponent's retreat Tools: "0 (the score has no opponent retreat term; a later candidate)". This is that term. kt doesn't read it and km doesn't touch the Tool term.

### N2. The attacker's lasting Stadium bonus counts in the threat clock, both sides

- **Today.** The clock's damage is the attack's own estimate (`estimated_attack_damage_ex`, `value_functions.rs:2150+`) with nothing from the board. The engine adds a Stadium bonus to every active-to-active attack: Training Area +10 for a Stage 1 attacker, Arena of Antiquity +20 for an [F] attacker against an ex, "both yours and your opponent's" (`hooks/core.rs:1997-2012`, from `stadiums.rs:129-158`). `persistent_defender_damage` says outright that it leaves out "the attacker's bonuses" (`hooks/core.rs:1618-1619`), and `value_functions.rs` has no Stadium read except F's Rainbow Cave check (`fuel_credit.rs:181`). So the score sees these Stadiums only when an attack happens inside the same 3-action line (census: "same-line" case).
- **Change.**
  1. **A read-only hook** in `hooks/core.rs`, beside `persistent_defender_damage` and `temporary_defender_reduction` (`:1622`, `:1772`): `lasting_stadium_damage_bonus(state, attacker_stage, attacker_types, target_is_ex) -> u32`, whose body is the two calls at `:2000-2009`. The hook names the two Stadiums because the engine's own damage stage does (`stadiums.rs:129-158`); the evaluator names none, as kd's and kt's hooks don't. No existing line of `core.rs` or `stadiums.rs` changes. A test pins it to `modify_damage` (section 4).
  2. **In the clock** (`turns_until_opponent_wins_scan_projected`, `value_functions.rs:1161-1258`): after the threat is picked (`:1188-1191`), take its Pokémon's stage and types (its evolution form when the threat is one, `ThreatCandidate.form`, `:1339-1351`). Each victim's hits become `ceil(HP / (max_damage + bonus(victim)))` at the two places that compute them (`:1219-1221`, `:1250-1252`). `bonus(victim)` is the hook with the victim's ex-ness. With no such Stadium in play the bonus is 0 and the arithmetic is untouched. The flag is passed down as kph's `zone_to_bench` is (`extract_features` `:829-846` → `:1089-1100` → `:1161-1171`).
  3. **Nothing else.** kd's and kt's clocks (`kd_turns_to_win`, `kt_clocks`, `:1813`) are not touched; no km preset sets their flags. Both sides use the rule, so the bot sees a Stadium it plays helping the opponent's Stage 1 attackers, and Field Blower on a Stadium that helps them.
- **Board only.** For the opponent's threats the scan stays board-only (`read_scanned_zones` false), so no hidden card is read.
- **Reach.** Training Area and Arena are carried by the two biggest archetypes: **Arena of Antiquity in 391 of 398 Mega Lucario ex Lucario lists (98%), Training Area in 329 of 336 Mega Altaria ex Espeon lists (98%)** (Limitless development half, `SCRATCH_NOTES.md`). Both are table decks. The same hook would price Future Booster Energy Capsule and Beastite (`hooks/core.rs:1529-1558`); no top-30 list carries either and kt zeroes them by design, so they wait for a composition (section 7).

---

## 3. Why these and not others

| Considered | What it would do | Why not in km |
|---|---|---|
| **Discard pile worth what the deck is worth** (the arithmetic in 1.2 made consistent) | Removes the +1 for X Speed before Copycat and Trail cycling | It also makes every Item and Supporter play cost 2 instead of 1. Poké Ball would net 0 instead of +1, and Copycat would need the opponent to hold 2 more cards than the bot's remainder, not 1. Dustin's quiz favours the bot that plays Copycat more. It is a global re-weighting, not a Trainer fix. |
| **A rule for X Speed itself** | Stop the 38 unexplained turns | Any rule must know that "the turn effect went unused". At a leaf after the turn ends the effect has already expired, and at a mid-turn leaf the line isn't finished, so "unused" can't be read from the position. A rule per turn-effect kind would be a card table. And it is 4% of X Speed turns. |
| **Boss / hidden hand** | Price the Basics | Needs a prior; kp has none (1.3). |
| **Targeted plays don't cost a search action** (Tools, Rare Candy, Blower, Flute, Quick-Grow use 2 of 3: `expectiminimax_player.rs:940-969`; the engine already treats attack, coin, promotion and queued-target choices as free, `:659-717`) | A Tool or Blower play would leave room for the next two actions | It is a search change, not pricing, and it adds a full ply after each targeted play (cost not measured). It also changes how Tools are played, which kt is reading. Its own registration, with a timing budget. |
| **Benched threats need a way to the Active** (the clock counts every charged Pokémon as ready wherever it stands) | Would price Goo-zooka, Repel, Cyrus, retreat Tools and X Speed lines in turns | It pushes toward moving the main attacker forward, the direction of kpf's forward swaps that Dustin rejected at Q10 ("sure", kph section 1), and it changes almost every position. koh's fix B is already in that ground. |
| **Status in the clock** (`status_clock_turns`, `value_functions.rs:1323-1335`, behind `--features status-clock`) | Master Plan, Pokémon Center Lady's cure | B2b measured the Sleep half: −0.2 to +1.0 on Altaria's cells, within noise (`rl/results/status_clock_2026-09-25/README.md`). Confusion needs a duration, which is a constant. |
| **Stadium use effects and end-of-turn effects** (Cave, Forest, Mesagoza, Arcade; Shore, Trail) | Value of later uses | Needs a number of future turns, and the search stops at the start of the opponent's turn (`expectiminimax_player.rs:773-798`, `:914-929`). |
| **Mars, Ilima, Flute** | Identity, points at risk, cheapest prize | Each needs a modelling choice with a constant or a list. |
| **Board abilities in the same hook** (Lucario's Fighting Coach, `hooks/core.rs:2101-2153`) | Would raise Lucario's clock too | Pokémon-side, not Trainer pricing; and it would push the footprint over 15% by itself. Open question 4. |

---

## 4. Build and tests (the cloud: one round)

- **Build:** on the official engine (main-9b4df9b, `engine/` equal to 233bced's), as player codes beside kog and kt. `EvalFeatures` gets two flags, `opponent_retreat_cost` and `stadium_bonus_in_clock` (`value_functions.rs:343-378`), false in `OFF`, `KQ`, `KD` and `KPR`, the four presets that list every field (`:381-440`). Presets `KM`, `KMA`, `KMB` are `..EvalFeatures::KOG` (`:460`). New value functions beside kog's (`:307-312`) and `PlayerCode` arms beside kog's (`players/mod.rs:657-698`).
- **Rules-file touch:** one new read-only function in `hooks/core.rs` and nothing else there. I read RUN5's refactor rule ("A refactor of a rules file", line 457) as not triggered, because no existing line changes, and the pin test is the equivalence. Open question 5.
- **Tests on constructed boards** (numbers recomputed from `card.py` before each test is written, as kph's registration says):
  - **N1, the term:** two Actives with Retreat Costs a and b, no effects: `kma − kog = b` exactly, for b in 0, 1, 2.
  - **N1, Goo-zooka:** `IncreasedRetreatCost { 1 }` on the opponent's Active moves `kma` by exactly +1 and `kog` by 0.
  - **N1, Plaza:** a [P] Pokémon with cost 2 or more on both sides: Plaza moves `kma` by 0 and `kog` by +2. Only the bot's Active [P]: +2 under both. Only theirs: −2 under `kma`, 0 under `kog`.
  - **N1, setup and hidden cards:** the setup value equals kog's exactly. The opponent's term is unchanged when their hand and deck are swapped for other cards (after `kpr_reads_no_hidden_card`, `:4498`).
  - **N2, the pin:** for each of no Stadium, Training Area, Arena of Antiquity, times attacker Stage 0, 1, 2, types [F], [R], [P], times a target that is an ex or not: the hook equals what `modify_damage` adds at that stage for an active-to-active attack (its result with the Stadium minus without, base damage 50, no Weakness or other modifier).
  - **N2, the clock:** Mega Lucario ex (Stage 1, [F], [F][F] attached, Fighting Pulse 90) against a 190-HP Mega ex Active: 3 hits without a Stadium, **2 with Training Area** (100) and 2 with Arena (110). The survival clock is shorter by exactly 1 turn. Against 180 HP: 2 and 2, no change. A [P] attacker gets Training Area's +10 but not Arena's.
  - **N2, both sides:** the same Stadium shortens the opponent's threat's clock by the same rule (roles swapped).
  - **N2, benched and evolving threats:** a benched Stage 1 attacker gets the bonus. A Riolu with Mega Lucario ex in the bot's hand is priced as the evolved Stage 1 [F] form. The opponent's evolutions are not scanned (board only).
  - **N2 off:** with no such Stadium, or with Hiking Trail or Fragrant Forest in play, `kmb`'s clock equals kog's bit for bit.
  - **Composition:** `km − kog = (kma − kog) + (kmb − kog)` on every position of 12 random games (Altaria v Lucario, Altaria v Blaziken, Lucario v Sceptile, Hydreigon v Weezing), from each player's own view, as `koh_is_kog_with_r_prime_and_reads_as_its_parts` does (`:5340`). Both switches touch different terms, so it is exact.
  - **Parser:** `km3`, `kma3`, `kmb3`, `KM5` parse; `km`, `kmx`, `kma` alone are rejected; `kog3`, `koh3`, `kph3`, `kt3`, `kta3` parse as before.
  - **Full suite:** passes; no test edited.
- **Identity** (on the table's deals, 72,000,000 + pairing × 10,000 + i; pairings are `legality_scan`'s: 0 = Altaria v Blaziken, 2 = Altaria v Lucario, 17 = Hydreigon v Weezing):
  1. **kog3 at the km build equals its reference** on pairings 0 and 2, 40 deals each (80 games), moves, choices, openings and results: `rl/results/koh_2026-09-28/bd2907f_kog3_500.jsonl`. Pairing 2 has both Stadiums in play, so the touched clock lines are executed. k3 and kp3 at the km build equal `rules09_fixes_2026-09-26/af8489f_{k3,kp3}_500.jsonl` on the same 80 games.
  2. **Switches off:** `EvalFeatures::KM` with both flags cleared equals `KOG` (a test), and kog3 in (1) is that identity in play.
  3. **N2 on, nothing to read:** `kmb3` on pairing 17 (neither list carries Training Area or Arena) and on Hydreigon v Sceptile (14), 40 deals each, equals kog3's games exactly.
  4. **Smokes:** `km3`, `kma3`, `kmb3` on pairings 0 and 2, 40 deals: clean runs. Their changed games are counted by the reading, not here.
- **Timing:** `km3`'s 40-deal run within 1.10 × kog3's (kt allowed 1.25 for a heavier change). The laptop runs both arms fresh, as `run_kt.sh` now does.
- **Laptop jobs, so the cloud doesn't duplicate them:** the tables, mixed rows, coverage rows, the mechanism counters and the footprint.
- **Which program plays km.** The official program (`rl/engine-2026-09-28/`) has no `km` codes, so every km game, counter and trace is played by the km build's own programs, named with their sha256, and each output file name starts with that build's commit. (kt's codes are the opposite case: they already exist in the official program as kp-based presets, which kt's review flagged, F1 and C1 in `kt_2026-09-26/REVIEW_amendment2_laptop_2026-09-28.md`. `km` avoids that by being new.)

---

## 5. The reading (registered on the 45 cells, RUN5 "The frame a candidate is read in")

**Step 1. Footprint, read first and committed alone.** km3 on both sides of the 45 cells on the table's deals (72,000,000 + pairing × 10,000 + i for the 28; 21,108,000,000 + pairing × 10,000 + i, pairings 8-24, for the 17; i < 500; even i puts the first-named deck in seat 0) against kog3's `rl/results/kog_composition_2026-09-27/table_kog3.jsonl` and `new17_kog3.jsonl`, paired by (a, b, i), on the `moves` field, as `rl/results/koh_2026-09-28/laptop_reading/footprint.py` does. **Under 15%: the reserve route. 15% or more: the ordinary rule.** The route is fixed on this number, for km3. `kma3` and `kmb3` are diagnostics and get no route of their own. My prediction is 13% (9 to 19%), section 7. It is a toss-up on purpose, so both routes are registered in full.

**Step 2. Build, identity, tests** (section 4).

**Step 3. Mechanism check** (diagnostic, gates nothing). km3 against kog3 on the first 200 deals of each of the 17 cells that hold the panel Altaria or Lucario list (their own deals, so no new seeds; kt's counters used 100, but the sign lines below want more), with a counter tool that extends `tool_turn_effect_census_2026-09-25/tool_census.rs` to count Stadium plays, Field Blower's Stadium targets, and X Speed, Boss and Copycat plays (its fingerprints are checked against the table file, as kt's counters were). Predictions, from the cards' stages:
- **M1, Arena of Antiquity** (Lucario's side, 9 cells): plays per offered turn **rise**, pooled paired 95% interval above zero, and positive in at least 7 of the 9 cells. Only Lucario's [F] Pokémon gain, against ex Actives.
- **M2, Training Area** (Altaria's side, 9 cells): it rises where the opponent's main attackers are not Stage 1: Blaziken, Hydreigon, Sceptile, Suicune, Rayquaza (Mega Blaziken ex, Hydreigon, Mega Sceptile ex, Baxcalibur are Stage 2; Suicune ex and Mega Rayquaza ex are Basic). It does not rise where they are: Lucario (Mega Lucario ex), Vespiquen (Vespiquen ex), Weezing (Team Rocket's Weezing ex), Altaria/Greninja (Mega Altaria ex). Line: (mean change over the first five) − (mean change over the last four) is positive with its paired 95% interval above zero.
- **M3, Field Blower's Stadium targets:** reported.
- **Sentinels, reported:** X Speed plays and its no-retreat share (Lucario, Vespiquen, Weezing cells), Boss (Suicune cells), Copycat. No switch touches these cards. They are expected unchanged within paired noise.

**Step 4. The 45 cells, by the route.**
- **Size:** the table's 500 deals per cell. RUN5's standing "double to 2,000 when undecided" (line 543) applies as written, on new seeds the laptop picks outside START_HERE's table.
- **Ordinary rule (footprint 15% or more).** Paired ΔMSE, kog3 minus km3, whole 95% interval below zero (`score45.py`, `rl/results/kpf_2026-09-26/reading/`, on the 45 cells with the 44-cell decision set beside it as it prints; the by-event interval printed beside, RUN5 line 340). Vetoes as rule v2: a cell's miss grows more than 6, a deck's gap more than 2, a held-out deck more than 2 further. They count only when mixed rows on the same deals (km3 on the deck, kog3 on the other, against kog3 on both) show km3's own side worse beyond paired noise, and never on a cell whose Limitless band is wider than about ±15.
- **Reserve route (footprint under 15%),** RUN5 line 519 and section 8 of `docs/REVIEW_2026-09-24_direction.md`, restated as kt's registration restates it:
  - **(a)** the footprint of step 1.
  - **(b) no harm:** the τ̂ margin (kog3 minus km3) has its 90% interval's lower bound at −1.0 or above, and no veto counts under rule v2.
  - **(c)** in the mixed rows for the pairings where km3's footprint is non-zero (km3 on the first-named deck only, then the second-named only, against kog3 on both; 500 deals), no deck's own side is worse beyond paired noise.
  - **(d) the gain, one gating archetype, fixed now.** **Mega Lucario ex Lucario**, the panel's `decks/research/lucario.txt` (1 Arena of Antiquity). It is Limitless rank 1 both by the Sept 10 top 30 and by development matches, 391 of its 398 development lists carry Arena, and no file of Dustin's carries Arena. The test: Lucario's own side over its **9 cells** (its 7 table cells, Rayquaza v Lucario, Altaria/Greninja v Lucario), each cell being km3 on Lucario with kog3 on the other deck against kog3 on both, paired by deal, then the equal-weight mean over the 9 cells, with the variation check's interval, 1.96 × sqrt(Σ per-cell variance of the mean difference) / 9. **It passes if the whole interval is above zero.** The size the mechanism predicts is about the noise on a deck average (the variation check's paired intervals on 7 cells ran ±1.2 to ±1.9), so this can fail, which is what the route is for.
    - **Reported beside, gating nothing:** Mega Altaria ex Espeon (`altaria.txt`; Training Area in 329 of 336 lists; 9 cells); B2e's Manectric and Raticate (Training Area) and Whimsicott ex Ariados (Goo-zooka in 21 of 21 lists, Trap Territory in 21 of 21); Dustin's decks (section 7); the real Limitless cells of Lucario and Altaria before and after (RUN5: a reported figure, not a gate). The same direction on the beside decks is supporting evidence; the other direction is a finding to write down.
  - **(e)** adoption for the screen and the table together.
  - **Closure sentence, adapted to km's cards** (section 8's wording is for reduction Tools and turn effects): if the census finds no Limitless top-30 archetype outside Dustin's decks that carries the relevant cards, or one with no usable decklist, the route is closed for km and adoption can come only by Dustin's explicit override, recorded as such; the route is not loosened after the census is seen. The carrier count found two such archetypes, so the route is open. That count was run for this draft before this text was fixed, on the development half only. What was fixed before it ran is RUN5's route.
- **How a b-fail with a real gain reads (stated now).** Lucario's deck average is 52.2 under kog3 against 45.6 real (+6.6). If N2 makes Lucario play better, it moves further from the real figure and the τ̂ margin can fall. Then (b) fails, the own-side gain is recorded, Lucario's overshoot stays on RUN5's open-cause list, and nothing is rescued.

**Step 5. Held-out and coverage decks, before any verdict is final** (RUN5 line 508: a "not adopted" is provisional until these are read). Row definitions are kph amendment 2's. The test is amendment 4's (RUN5 lines 480-483).
- **B2e's six held-out archetypes**, pairings 0-47 (`rl/results/b2e_card_check_2026-09-26/decks/h-*.txt`; deals 21,106,000,000 + pairing × 10,000 + i): km3 on both sides against kog3 on both. **The accuracy veto stands:** an archetype ending more than 2 points further from its pooled equal-weight Limitless average than under kog3 (as `kpg_2026-09-27/heldout_check.md` reads it), counting only through mixed rows. **Also, every time,** own-side mixed rows (km3 on the held deck, kog3 on the panel list, against kog3 on both, paired by deal): the whole 95% interval below zero is harm and blocks the takeover. **Manectric, Raticate (Training Area) and Whimsicott (Goo-zooka, Trap Territory) are the ones N1 and N2 can reach.** Dustin's files (pairings 48-95: decks 09, 13, 04, 08, 12 and brew 08) are reported beside.
- **Scizor** (carries 1 Training Area): its 8 rows (`decks/gauntlet_2026-09-26/g-mega_scizor_revavroom.txt`, pairings 0-7 of `tsv/new_decks.tsv`, 21,108,000,000 + pairing × 10,000 + i): km3 on Scizor with kog3 on the panel list, against kog3 on both, the 8-row average, interval 1.96 × sqrt(Σ per-cell variance) / 8. Whole interval below zero is harm. Accuracy reported only.
- **The four second lists** (`v-lucario_2` (carries Arena), `v-suicune_2`, `v-weezing_2`, `l-charizardy`), each on its own deals (`gauntlet_runs_2026-09-26/tsv/var_*.tsv`): the same own-side test, accuracy reported only against the figures amendment 2 names.
- **Baselines.** kog3's Scizor and second-list rows exist (`koh_2026-09-28/laptop_runs/scizor_kog3.jsonl`, `var_*_kog3.jsonl`). **kog3's B2e rows are not in the tree** (only `b2e_koh3.jsonl.part`, still running). If koh's reading doesn't commit them, the laptop runs them at the km build's engine first: 96 pairings × 500 deals. Open question 3.
- A veto or harm on any of these blocks the takeover. A gain is reported, not credited.

**Step 6. Development data (RUN5 line 516).**
- **All 45 cells are development evidence for km,** as for kph. The audit, the Tool census and the X Speed census read kp3's games against the panel lists, and the variation check played Lucario, Suicune and Weezing on the table's own deals. The 17 new cells were used to design kpf.
- **Also development data:** Dustin's quiz answers used in 1.2 and 1.3, the Limitless development half (63 events) whose carrier counts fix (d) (the holdout half's standings were never opened; the scan reads `split.json`'s development ids only), and this draft's re-tally of the X Speed file.
- **The confirmation is the post-freeze read.**

**Step 7. Confirmation** (RUN5 "When post-freeze data is read"; the list is in `postfreeze_2026-09-27/README.md`). km joins that list by a commit there before the data is opened, if it is adopted before the read. Otherwise it waits for the next pull. Reserve route: the τ̂ margin's 90% lower bound at −1.0 or above and no veto, with Lucario's and Altaria's post-freeze cells reported. Ordinary rule: on the post-freeze events alone, at least half its development margin with its own 90% interval above zero. A failure reads "not confirmed at this size". km carries kog's A and F, so if any of kog's rows is not confirmed at that read, km reads "not confirmed at this size" too and both are read again at the next pull. Each check is read on the same engine as its baselines.

---

## 6. What would show it wrong (stated before any game)

1. **A pin fails.** The hook differs from `modify_damage`, or N1's terms differ from the formula. The switch prices something the engine doesn't do.
2. **The mechanism doesn't show:** M1 or M2's line fails (the Stadium plays don't move as the cards' stages say).
3. **Harm:** any deck's own side worse beyond paired noise (whole 95% interval below zero) in the mixed rows on the 45 cells (route (c) or the vetoes), B2e's held-out decks, Scizor or a second list.
4. **No gain:** on the reserve route, (d) fails. The route is closed and km is adoptable only by Dustin's explicit override.
5. **On the ordinary rule:** the ΔMSE interval isn't below zero. "Not adopted", provisional until step 5.
6. **N1 acts beyond its ties:** in cells whose lists carry neither Training Area, Arena, Goo-zooka, Plaza nor Trap Territory, more than about 3% of games differ from kog3's. Or Boss, X Speed or Copycat plays move beyond paired noise there. Both mean an interaction nobody predicted.
7. **What it would say about the class:** if neither switch gains, what is left of the Trainer gap is search cost (row 4 of section 3) and information (Boss), not board numbers. The next candidate is then the search one, registered with a timing budget.

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
| Cyrus, Sabrina, Repel (N1 only breaks ties) | nearly every list | most | most |

**Footprint on the 45 cells.**
- **N2:** the 17 cells that hold the panel Altaria or Lucario list (9 + 9 − their shared cell; 38% of the games). In those cells I expect 25 to 45% of games to differ. That is a judgment, not a measurement: the audit had the Stadium offered in 76% of Altaria's games and 68% of Lucario's (kp3, `audit_trainers.tsv`), and once it is offered or in play the clock changes many later choices, not only its own play. That gives 9 to 17% of the 22,500 games.
- **N1:** at most 1 to 2% elsewhere, from gust and promotion ties, since none of the 10 lists carries Goo-zooka, Plaza or Trap Territory.
- **km3:** about **13%, plausibly 9 to 19%.** The route depends on it, so it is read first.
- **The rest of the 28 cells** (Blaziken, Hydreigon, Sceptile, Suicune, Vespiquen, Weezing among themselves, and the Rayquaza and Altaria/Greninja cells against them) should be identical apart from N1's ties.

**Dustin's decks and brews it reaches.**
- **Deck 09** (Training Area): N2 acts. Read for free in B2e block B (pairings 48-55), reported beside.
- **Deck 12** (Goo-zooka, Trap Territory; B2e block B pairings 80-87): N1 only. **I expect no visible change, and deck 12's X Speed pattern (52%) is not touched by either switch.** It is the deck to watch for X Speed, not the deck km is expected to move. Its 57% with Trail against 10% without is the arithmetic in 1.2.
- **Decks 14 and 15, brews 03a, 03b** (Goo-zooka): N1 as for deck 12. **Brews 05b and 10** (Plaza): N1 acts on direction (91% and 54% played today).
- **Not reached by anything in km:** X Speed (decks 04, 12; brews 02, 03a, 04, 05, 07), Boss (brew 02), Master Plan (brews 05, 05b), Ilima (01, 02, 13, 15), Flute (08, 14), Rainbow Cave (brew 08, decks 08, 11), Soothing Shore (03, 13). The screen and the floor's coverage flag still mark these as unpriced: the flag keys on hand/deck text and opponent-turn markers (`engine/examples/goldfish.rs:163-215`), which doesn't cover Stadium or status text (open question 8).

**Open, not in km** (recorded so they aren't lost):
- **The loss certificate refuses any board with a Stadium in play** (`public_reply.rs:584-587`), so with Training Area, Arena or any Stadium out the bot can't see a proven lethal reply. Not a pricing change.
- **Draws are priced from one sampled shuffle** (census, Supporters finding on Copycat and Professor's Research): a max over one noisy sample favours random-effect cards. Averaging needs a sample count.
- **Future Booster and Beastite** through N2's hook, when kt is composed with km (kt gives them 0). kt's clock is separate (`kt_clocks`), so composing needs N2 built into it, with its own identity.
- **Lucario's Fighting Coach and other board abilities** through the same hook (open question 4).
- **The Suicune second-Cape swap, repeated with a non-Tool card**, would separate Boss's cost from Cape pricing.

---

## Open questions for the reviewer

1. **Amendment 2 or 4.** The brief said amendment 2's definitions. RUN5 lines 480-483 say amendment 4 supersedes amendment 2's tests. I used amendment 2's row definitions and amendment 4's test (no 2-point floor on the own-side veto). Confirm.
2. **Is N1 worth carrying?** It is near-null on the 45 cells and a tie for Goo-zooka. Its case is direction (Plaza), the retreat-cost sketch in the census and Dustin's decks and brews 12, 14, 15, 03a/b, 05b and 10. It may add 1 to 2% to a footprint that already sits near 15%. Drop it if the review prefers a one-switch candidate; the codes make that a one-line change.
3. **B2e's kog3 rows don't exist.** Who runs them (96 pairings × 500, kog3 both sides, at the pinned engine), and does koh's reading commit them first?
4. **Scope of N2's hook.** Include board-ability bonuses (Lucario's Fighting Coach)? It would reach all 9 Lucario cells more strongly and push the footprint over 15%, but it is Pokémon-side.
5. **The hook is a duplicate, not a refactor.** `modify_damage` keeps its own copy at `core.rs:1997-2012`. Is that enough to stay out of RUN5's rules-file refactor rule, or should `modify_damage` call the new function and take the three-part check?
6. **Gating archetype for (d).** Lucario (Arena, +20 against ex, one-sided) over Altaria (Training Area, +10, shared with Stage 1 opponents), because the mechanism is larger and clearer there. Altaria is beside. Confirm before any game.
7. **The accuracy direction.** Lucario is already 6.6 above real. A better-played Lucario may fail (b). Is "record it, rescue nothing" (step 4) the right reading?
8. **Coverage flag.** Should the floor's coverage flag (`goldfish.rs`) learn Stadium and status texts, so brews leaning on them read "untrusted"? A screen-tool change, not a pilot one, and the honest treatment for the Trainers km can't fix.
9. **Identity size.** I followed the brief (2 pairings × 40 deals for kog3 and k3/kp3, plus the switch-off and no-trigger identities). koh's build ran kog3 in full (14,000). Enough here?
10. **The X Speed claim.** The 96-turn "Trail can be in play" group is an upper bound (the census file has no Stadium record). If it matters, one replay of deck 12 with a Stadium counter settles it.
11. **Code letters.** `km`, `kma`, `kmb` are free (no code starts with `km`). Confirm.
12. **Timing budget** 1.10 × kog3.
13. **The card-arithmetic identity is derived, not tested.** No switch depends on it, but section 3's rejection of the discard-pile change and 1.2's reading of X Speed do. One constructed board (X Speed then Copycat against Copycat alone, no Trail: a difference of exactly +1; with Trail in play and a hand under 3: +1 for any played card) would confirm it.
14. **Does N1 move Goo-zooka where it matters?** Dustin put Goo-zooka on the candidate's list (Sept 28, about 11:15 pm): brew 03b plays it on 2.1% of chances. The floor flag gives the cause as a payoff during the opponent's turn, which the search doesn't play out. N1 makes the opponent's +1 Retreat Cost count at the leaf, but a leaf that doesn't play the opponent's turn may still see no difference.
    - Before registering: one constructed 03b board with Goo-zooka playable, scored under kog and kma, showing whether N1 changes the pick.
    - If it doesn't, either name the card as reported only ("km does not fix Goo-zooka"), or look for a list-free way to price the opponent's next-turn retreat. Don't add a constant.
