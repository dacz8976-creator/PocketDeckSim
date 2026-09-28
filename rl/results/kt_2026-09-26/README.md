Decision this informs: whether the pilot after kp3 prices the defender's temporary damage cuts and reduction Tools in the threat clock, replaces the flat +10 for a Tool on the Active by what the Tool does for its holder, and credits damage back to the attacker; read against kp3 by the Sept 25 plan. **Amendment 2 (Sept 28, a draft for one review) re-issues kt on kog: read against kog3 on the 45 cells. Once its review is committed, it holds over the text below.** This file is kt's registration (Sept 26), committed before any kt code or game. kt was first built on kp at 43cef0b (`BUILD.md`, kept as history); the codes re-issued on kog need a new build (amendment 2, item 7).

Seeds: kt's table on the table's deals (72,000,000 + pairing × 10,000 + i, i < 500, even i = first-named deck in seat 0) and, under amendment 2, the 17 new cells' (21,108,000,000 + pairing × 10,000 + i); B2e's rows on 21,106,000,000 + pairing × 10,000 + i and the Scizor row on 21,108,000,000 + pairing × 10,000 + i (pairings 0-7), as in every reading; clause (d)'s rows on 22,700,000,000 + panel index × 10,000 + i (amendment 1); the Dustin-deck A/B on the new block 22,600,000,000 – 22,699,999,999 (START_HERE's seed table).

# kt: Tools and temporary damage cuts priced by what they do (registration, Sept 26)

**Source.** Fable's proposed registration text (`rl/results/fable_reviews_2026-09-26/kt_spec_review.md` on main, "The registration text Fable proposes the cloud commit"), taken as written except where marked **[amended]** or **[filled]** below, with the reason beside each; the laptop's answers of Sept 26 (A/B size, opponent seat, Jasmine's denominator, seed block, kp3 regenerated after the rules/09 fixes); and the laptop's carrier census for clause (d) (`rl/results/kt_carrier_census_2026-09-26/README.md` on main). The earlier draft (`../tool_turn_effect_census_2026-09-25/README.md`, c002d2f) is superseded; its census stands. Any change after this commit is a dated amendment before any kt game, and a spec change after any reading is a new code.

## Amendment 2 (Sept 28, before any kt game on kog): kt re-issued on kog. DRAFT for one review

**Status.**
- This is a draft for one review, as the laptop asked on Sept 28. It comes into force when the review's outcome is committed, as written or as the review amends it. That commit is dated and comes before any kt game on kog.
- **Coming into force doesn't start any kt game.** kt's tables still wait for Dustin's word (`BUILD.md`). His Sept 27 go-ahead covered the build on kp3, and his word on the tables "also depends on which pilot kt is read against". Amendment 1's open confirmation is also still due from Dustin or the laptop before any kta game, unless the review's commit records it: Rayquaza as the one clause (d) test, with Suicune reported.
- **No kt build or game until koh's verdict is committed,** coverage included (see Order below).

**Why an amendment re-issues kt.** The base line (BASE AND CODES below) says: "Built on the pilot the kpr reading leaves: kp3. If that changes, this registration is re-issued, not amended." The base has changed.
- kog passed its composition check on Sept 28. It is the working pilot, "unconfirmed" (RUN5 "Composing candidates into one pilot"; `../kog_composition_2026-09-27/READING.md`, 5bca434). kog is kp3 plus koa's opening switch A plus kpg's discard credit F.
- The laptop asked for the re-issue as a dated amendment to this file. That keeps the registration in one place with its history visible. In substance it is the re-issue the base line asks for: every clause below is re-read on the new base, before any kt game on it.
- **What kt games exist.** All are on kp3; none is on kog, none is a table game, and none is on clause (d)'s seed block or the A/B's.
  - The build at 43cef0b ran identity replays and 40-deal smokes on the table's deals, all 28 pairings (`BUILD.md`).
  - The smokes were read only for how often a game's choices differ from kp3's: kt3 65.7%, kta3 1.4% (all in Suicune's cells), ktb3 66.7%, ktc3 8.8%.
  - Their scan pages also print a first-deck win rate for each cell, as every scan page does. No reading uses them.
- **Order** (the review, relayed by the laptop on Sept 27; `../kog_composition_2026-09-27/READING.md`, "What follows"):
  1. kog's check;
  2. kph's reading on the resulting base, running now as `koh` (kog + R′);
  3. kt.
- **If koh's reading makes koh the working pilot,** kt is re-issued on koh by a further dated amendment, reviewed before any kt game. That is not a flag change.
  - kt's clock replaces the whole threat clock and takes no projection (`players/value_functions.rs`: `extract_features` uses a given clock in place of `calculate_turns_until_opponent_wins_projected`; `kt_clocks` has no horizon).
  - So on koh, switches 1 and 3 would switch off R′'s projected clock and fix B, while R's readiness projection and F stay on. ktb would keep them.
  - That amendment says how switches 1 and 3 combine with R′'s clock, and the new build tests it.

**Where this amendment and the text below (amendment 1 included) differ, this amendment holds.** Everything it doesn't name stands as written:
- the rule, the three switches, the reserve route and its clauses;
- amendment 1's rulings;
- Dustin's go-ahead of Sept 27 for the build (Bench Poncho is not covered; it is a named gap in `BUILD.md`).

1. **Base and codes.** `kt<N>` = `kog<N>` with the three switches on. `kta<N>`, `ktb<N>` and `ktc<N>` = `kog<N>` with switch 1, 2 or 3 only. kq's, kd's and kpr's features (R, and kph's fixes A and B) are off.
   - **Every "kp3" below that names the base or the paired comparator reads kog3.** That covers:
     - the reference and the footprint;
     - the mixed rows' other side;
     - the τ̂ margin in clause (b) (kog3 minus kta3);
     - clause (d)'s comparator arm and the panel's pilot;
     - the Dustin-deck A/B's comparator and opponent seat;
     - the readout counters' baseline;
     - the timing budget.
   - **How the parts meet** (`parametric_value_function_ex6`, read at bd2907f):
     - Switch A is read only in the setup evaluation, which returns before any clock is computed.
     - F is its own term, added after the score is summed. It reads the discard pile (the whole pile, since R is off), not the clock.
     - kt's clocks replace kog's, which are kp's (kog has no projection).
     - Switch 2 zeroes only the flat Tool term.
     - So kt on kog is kog's value in setup. After setup it is kt's clock and Tool term, plus F.
   - The build at 43cef0b (kt on kp) stays as history. Its identity runs remain the evidence that kt's shared code changes nothing for other bots. The re-issued codes need a new build.
2. **The frame: the 45 cells.** RUN5 "The frame a candidate is read in" (Sept 27) registers every candidate from Sept 27 on the 45 cells, and this amendment is dated Sept 28.
   - **On the 45 cells:** the footprint, the ordinary rule, the vetoes, clause (c)'s mixed rows and kt's four tables.
     - The cells are the table's 28 on the table's deals, and the 17 new cells on 21,108,000,000 + pairing × 10,000 + i. Altaria v Sceptile is included, as in scoreboard v3 and kog's and kph's readings.
     - Each code's table is 45 × 500 paired games: step 4's "28 × 500 on the table's deals" plus 17 × 500 on the new cells.
     - "Scoreboard v2's 27-cell decision set" reads "scoreboard v3's 45 cells", and "the 28-pairing mixed rows" reads "the 45 cells' mixed rows".
     - "The table" in clause (e) ("adoption for the screen and the table") and in step 4 ("the table's commit", "before the table") names the pilot's role and kt's own run. Those uses are unchanged.
     - Identity is as item 7 states.
   - **The references:** kog3's own runs from the laptop's build of a823b6d, which is the official engine's source (main 83e17ae) plus the branch's player code (`../kog_composition_2026-09-27/table_kog3.jsonl`, `new17_kog3.jsonl`). kog isn't in the official program yet. At a823b6d, k3 and kp3 replay the official references 14,000 of 14,000, and the laptop's `table_kog3` equals the cloud's.
   - **Footprint:** the share of the 45 cells' 22,500 paired games whose moves differ from kog3's. It is read first and fixes the route for kt3 and kta3 alike: under 15%, the reserve route; otherwise, the ordinary adoption rule.
   - **The ordinary rule:** paired ΔMSE against kog3 on the 45 cells, with the whole 95% interval below zero. Vetoes are rule v2's, counting only through mixed rows against kog3 on the same deals.
   - **kta3's reserve route:** clause (c)'s mixed rows are the pairings of the 45 cells where kta3's footprint isn't zero, both directions, 500 deals.
3. **Where the switches reach on the 45 cells.** This is read from the lists, not from games, with the carrier census's card set (`../kt_carrier_census_2026-09-26/cards.json`) and the card database. Every switch acts on both sides, so a cell is reached when either list carries the card.
   - **Switch 1 reaches 17 of the 45 cells, not just Suicune's seven:**
     - Suicune's list (one Frigibax P-B 037, Stiffen): its 7 table cells and its 2 new cells (Rayquaza v Suicune and Mega Altaria ex Greninja v Suicune).
     - The scoreboard's Rayquaza list, `decks/gauntlet_2026-09-26/g-dragonair_mega_rayquaza.txt`, carries 2 Gouging Fire B3a 054 (a self-cutting attack, amendment 1). So switch 1 reaches all 9 Rayquaza cells.
     - Mega Altaria ex Greninja carries no switch-1 card.
   - **Switch 2 reaches every cell.** Every list carries a Tool.
     - Rayquaza carries a Small Balloon and an Ancient Booster Energy Capsule. The capsule is an HP Tool (+40 HP on an Ancient Pokémon, as `card.py` prints it), priced by the rule like the Capes, with no spec edit.
     - Mega Altaria ex Greninja carries a Small Balloon.
   - **Switch 3** is carried only by Blaziken's list (Rocky Helmet). So it reaches Blaziken's 7 table cells and 2 new cells (Rayquaza v Blaziken and Mega Altaria ex Greninja v Blaziken).
   - **The prediction "kta3's footprint under 5%"** was made on the 28 cells, where only Suicune's seven carry a switch-1 card. It is not restated for the 45, where the Rayquaza cells are new ground for switch 1. Predictions never choose the route (amendment 1); the measured footprint does.
   - **Clause (d) stays the one test** (amendment 1): kta3 against kog3 on the census's Rayquaza list, 8 × 500 deals on the 22,700,000,000 block.
     - The scoreboard's Rayquaza list is a different list: two Trainers and the Dratini card differ.
     - Its 45-cell rows are read under clause (c), for no harm, and never as a second chance at (d). A gain there is reported, not credited to (d).
   - **Amendment 1's report beside (d)** ("Suicune's own side on its seven kta3-v-kp3 mixed rows, the same rows (c) reads") reads: Suicune's own side on its nine rows (7 table and 2 new), kta3 against kog3.
4. **Coverage** (RUN5 "The frame a candidate is read in": no harm only). A veto there blocks the takeover; a gain is reported, not credited.
   - B2e's held-out archetypes (pairings 0-47): one moving more than 2 points further from its Limitless average is a veto, through mixed rows as above. Dustin's files (48-95) are reported beside.
   - The variation check's second lists (all four decks' second lists, `../gauntlet_runs_2026-09-26/README.md`) and the Scizor row count for no harm only.
   - **Open for the review, to be fixed before any kt game: what harm means on the Scizor row and the second lists.** They have no usable Limitless figure, so rule v2's vetoes can't fire there as written, and kpg's reading reported Scizor without gating it. Scizor is the one coverage deck that carries a switch-1 card.
     - Proposed wording: through mixed rows against kog3 on the same deals, both directions, 500 deals; the deck's own-side average against the panel worse beyond its paired noise is a veto.
     - The alternative is "reported only", said explicitly.
   - **Reach there** (both sides, as in item 3):
     - **Switch 1:** the Scizor list carries 2 Metal Core Barrier B2 148, so switch 1 reaches its 8 rows. Through the panel's Suicune it also reaches every coverage row against Suicune: B2e pairings 4, 12, 20, 28, 36 and 44 (held-out) and 52 to 92 in steps of 8 (Dustin's), and the second lists' rows against Suicune. No B2e list or second list carries a switch-1 card of its own.
     - **Switch 2** reaches every coverage row. Every held-out list, every panel list and every second list but Lucario's carries a Tool, all of kinds the registration already prices. Protective Poncho, priced at 0 as Lucario's is, is in the held-out Garchomp list and in Charizard Y's second list (`l-charizardy.txt`).
     - **Switch 3:** through the panel's Blaziken, every coverage row against Blaziken.
   - **The base's coverage runs:** kog3's B2e and Scizor rows are being run now, as koh's held-out baselines, at koh's build bd2907f (`../koh_2026-09-28/reading/b2e_kog3.jsonl`, `scizor_kog3.jsonl`). kog3's runs on the second lists are made at kt's build if none exist then.
5. **Development data** (RUN5 "Development data, stated with each reading").
   - The Tool census and the Trainer audit read kp3's games on the 28 table cells, so those cells are development data for kt.
   - Of the 17 new cells, the carrier census read the Rayquaza archetype's real Limitless results against the eight panel decks (pooled 46.3 ± 4.8) when it chose clause (d)'s deck. Those 8 cells' real results are development data for kt.
   - The other 9 new cells weren't used in kt's design. For all 17, the holdout is post-freeze events anyway (RUN5).
6. **Confirmation** (RUN5 "When post-freeze data is read").
   - **Joining the list.** If kt is adopted before the post-freeze read, it joins that pull's list by a commit to `../postfreeze_2026-09-27/README.md` before the data is opened. Otherwise it waits for the next pull (the rolling freeze).
   - **kt3's check follows kt3's route.**
     - Ordinary rule: on the post-freeze events alone, kt3's τ̂ margin over kog3 must be at least half its development margin, with its own 90% interval above zero. The pooled figure and the sign are reported beside it.
     - Reserve route: the no-harm re-check (the τ̂ margin's 90% lower bound at −1.0 or above, and no veto), with its own real cells reported.
   - **If kta3 passed by the reserve route,** its no-harm re-check also applies: the τ̂ margin (kog3 minus kta3) with its 90% lower bound at −1.0 or above, and no veto. Suicune's and Rayquaza's real cells are reported.
   - kt is confirmed only if every check that applies passes.
   - **If kog is not confirmed** at that read (its own row, or kpg's or koa's that it inherits), kt's verdict lapses with it, since kt carries switch A and F. kt's switches are then read again on the base in force at that time, as a new reading under the rules in force, as kph's registration does for F.
7. **Identity at the new build.**
   - kt's preset with its three switches off is kog's, and each single-switch preset is kog's plus that switch (a test).
   - k3 and kp3, all 500 deals, 14,000 of 14,000 each, against the official references (`../rules09_fixes_2026-09-26/af8489f_{k3,kp3}_500.jsonl`), as registered.
   - kog3 at the kt build:
     - equal to kog3's table (`../kog_2026-09-27/a823b6d_kog3_500.jsonl`, which the laptop's `table_kog3` equals), all 14,000 games;
     - equal to `new17_kog3.jsonl` on the 17 new cells, all 8,500 games;
     - equal to koh's `b2e_kog3` and `scizor_kog3` on i < 40 of every pairing.
   - kq3 (14,000 games), kd3 and kpr3 (1,120 each), as registered.
   - A diff of `engine/` from the kt build's parent to the kt build, showing kt's changes only. The full replays above are made at the kt build itself.
   - Timing: kt3's 40-deal run within 1.25× kog3's.
8. **Clause (d) and the Dustin-deck A/B keep their lists, sizes and seeds.** Only the comparator changes:
   - (d): kta3 against kog3 on the Rayquaza list's eight rows, with kog3 on the panel lists in both arms.
   - The A/B: kt3 against kog3 on the deck seat, with kog3 on the opponent's seat in both arms.
9. **The predictions' "before" figures and the readout counters.**
   - **Each prediction is judged against kog3's own readout counter** on the same deals, at the kt build's engine.
   - **Why not kp3's census figures:** those are kp3's games on the Sept 25 engine, before the rules/09 repairs. kog3's games also differ from kp3's in 1,175 of the 14,000 table games (a823b6d): 116 to 152 of 500 in each Altaria cell and 26 to 60 in each Blaziken cell, since a changed opening or F choice changes the rest of the game. That is where the Balloon and Rocky Helmet predictions sit.
   - **The census figures are printed beside, as history:** Stiffen 55 of 124 (44%); Balloon 88% and 225 of 501; Boat 60%; Poncho 68% and 427 of 428; Rocky Helmet 69%; Blower's 453 + 93 + 64 of 1,414. Jasmine's and the Barrier's "before" is kog3's arm of the Dustin-deck A/B.
   - **The readout counters stay as fixed:** `tool_census.rs` and `legality_scan`'s counters, on the first 100 deals of each of the 28 table pairings, for kog3, kt3, kta3, ktb3 and ktc3, with fingerprints checked against each code's table file. `tool_census.rs` is written for the eight table decks and counts Stiffen as the only self-cutting attack, and `legality_scan` has no Scorching Interruption counter.
   - **So switch 1 on Rayquaza is read through the Rayquaza traces:** `trace_pilot.py` on the 200 Rayquaza v Lucario deals (21,108,900,000+), as kpf's and kph's readings ran it, kta3 and kog3 on Rayquaza with kog3 on Lucario in both. The traces count Scorching Interruption's offered and used turns, and are reported only.

**Main changes from the first draft of this re-issue** (966d75d, committed as in force; this draft is not). The full diff is `git diff 966d75d -- README.md`. Every change was made before any kt game on kog, and none after any reading of kt on kog.
- Recast as amendment 2, a draft for one review.
- Status: coming into force starts no kt game (Dustin's word; amendment 1's open (d) confirmation).
- The kt games that do exist on kp3, and what was read of them.
- The order, and the koh case as a design question, not a flag change.
- The frame stated item by item instead of by blanket substitution, with the table size.
- The references' true source: a823b6d, not the official program.
- The reach on the 45 cells and on coverage, both sides.
- Clause (d) stays the one test, with amendment 1's report beside it restated.
- Scizor's and the second lists' harm test left open for the review.
- Confirmation by route, plus the lapse clause.
- Identity in full: k3 and kp3 on 14,000, and kog3 on the new cells and coverage.
- The before figures are kog3's own counters, with the census as history; switch 1 on Rayquaza is read through the traces.
- Development data corrected: the Rayquaza archetype's real cells were read by the carrier census.

## Amendment 1 (Sept 26, before any kt code or game): Dustin's rulings

Dustin's rulings of Sept 26 morning, recorded by the laptop in section 8 of `docs/REVIEW_2026-09-24_direction.md` (main, 0d424cf and c7999ef), applied here. Where this section and the text below differ, this section holds.

- **The reserve route is approved** ("the gain must show on at least one deck that isn't yours"). **Each code's route is fixed by its measured footprint, read before anything else:**
  - under 15%, the reserve route;
  - 15% or more, the ordinary adoption rule.

  This applies to kt3 and kta3 alike. The expectations below (kt3 over 15%, kta3 under 5%) are predictions, not route choices.
- **(i) Dragonair Mega Rayquaza ex is not Dustin's deck.** "His decks" means only the files he gave the project. So reading 2 of the carrier section below holds.
- **(ii) A panel archetype may serve as the (d) deck.** "The same ruling covers Suicune for the Tool fix."
- **Both carriers are self-cutting attacks,** not Tools or Supporter effects: Gouging Fire's Scorching Interruption and Frigibax's Stiffen. The census's section-1 wording question (do these count as "the relevant cards"?) is therefore treated as answered yes by these two rulings, as the laptop records it. It was not asked as a separate question.
- **Clause (d), fixed now as one test, so there are not two chances to pass:**
  - **The test:** kta3's own-side gain beyond paired noise on the Dragonair Mega Rayquaza ex list (`rl/results/kt_carrier_census_2026-09-26/decks/c-dragonair_mega_rayquaza_ex.txt`), pooled over its eight rows against the panel lists.
    - One arm has kta3 on the Rayquaza list, the other kp3; kp3 plays the panel list in both.
    - 8 × 500 deals per arm (8,000 games), on the new seed block below.
  - Rayquaza carries the card in 135 of its 143 lists, 132 of them with two copies. The panel's Suicune list carries one Stiffen card.
  - **Reported beside it, not a second test:** Suicune's own side on its seven kta3-v-kp3 mixed rows (the same rows (c) reads). Also the Rayquaza archetype's Limitless cells before and after (pooled 46.3 ± 4.8).
  - **For Dustin or the laptop to confirm before any kta game:** Rayquaza as the one test, with Suicune reported. Ruling (ii) also allows Suicune as the test; choosing it, or pooling both, is a further dated amendment, and only before any kta game.
- **Seeds for the Rayquaza rows:** 22,700,000,000 + panel index × 10,000 + i, i < 500. Even i puts the Rayquaza list in seat 0. The panel lists are the eight table lists in `decks/research` (card for card the panel's `decks/screen/opponents/t-*.txt`); panel index is the list's position in sorted order (altaria 0 to weezing 7). The block 22,700,000,000 – 22,700,079,999 is written into START_HERE's seed table in this commit.
- **The broader test group** Dustin approved for engine and pilot changes (the gauntlet: the table decks, the six held-out archetypes against them, and additions for missing Energy types): kt takes the parts Dustin approves by a further dated amendment, before the table they belong to, as koa did (its amendment 1).
- **Still Dustin's:** section 8 lists kt's registration as his decision (item 2: Fable's text as the base, switch 1 as its own code, and the Hydreigon deck-gap veto as switch 2's expected readout). This file is the text he is asked to approve. The engine fixes come first either way.
- **Engine repairs now in the order section (step 1):** the laptop's repair list of Sept 26 adds five more:
  - Mimikyu ex's Disguise used up by a 0-damage attack;
  - Bad Dreams stopped by three "by attacks" protections;
  - Clemont's Backpack's +20 on non-attack damage and on its owner's Pokémon;
  - Roar in Unison offered under Binding Snow's lock;
  - Clemont's search passing the 10-card hand.

  Each is its own commit with a full k3 and kp3 replay. kp3's reference table is regenerated after the last of them (`../rules09_fixes_2026-09-26/`).

## BASE AND CODES

- kt<N> = kp<N> (k's blind search, PublicPricingPlayer with the 62 audited texts) with three EvalFeatures flags, all on. kq's, kd's and kpr's features off. Built on the pilot the kpr reading leaves: **kp3** (the laptop's rule-v2 reading, main 055f6f0, did not adopt kpr3). If that changes, this registration is re-issued, not amended.
- Diagnostic codes, each with one flag on: kta<N> (switch 1), ktb<N> (switch 2), ktc<N> (switch 3). They are parsed before "kt", which is parsed before "k"; the parser test covers kta3, ktb3, ktc3, kt3, kt13 and rejects kt1a. Single-switch readings are attribution, never adoption, except kta under the reserve route below.
  - Pre-registered interactions: ktb alone removes Barrier, Apron and Rocky Helmet play (the +10 is gone and nothing credits them), so a Skarmory or Blaziken regression under ktb is expected, not a bug. ktc alone changes Blaziken's row only.
- The score's flat Tool term (`active_has_tool`, weight 10, both sides) is 0 under kt and ktb, and 10 under kta and ktc.

## RULE (card-agnostic)

A Tool or a temporary damage cut is worth exactly what the engine's own hooks make it worth to its holder where it sits, through terms the score already has, and 0 otherwise. The evaluator calls hooks; it names no card. The per-card table below is the consequence of the rule, kept so a reader can check it; a new Tool needs no spec edit.

## SWITCH 1: the defender's temporary cuts and reduction Tools, in the threat clock (both sides)

- **A new engine hook** in `hooks/core.rs`, next to `persistent_defender_damage`: `temporary_defender_reduction(state, victim, threat, turn) -> u32`. It sums:
  - turn effects registered for `turn` (`State::get_turn_effects`) whose scope covers the victim and whose only-from-ex condition matches the threat (`ReducedDamageForTarget`, `ReducedDamageForType`);
  - the victim's own `CardEffect::ReducedDamage` / `ReducedDamageFromEx` still live on `turn`;
  - Metal Core Barrier's cut, only when `turn` is the holder's opponent's next turn (the engine discards it at the end of that turn whether or not it was hit).
- **Pinned by a test.** For turn == the current turn, on constructed positions covering each effect type, the value equals what `modify_damage` subtracts at those stages. The Weakness stage is not taken over (kd's term stays in B3). Known limit: where the victim is Weak, the engine's cut lands on a bigger number than the clock's estimate, so kt under-counts the cut there.
- **Permanent cuts.** `persistent_defender_damage`'s Tool stages (Steel Apron, Heavy Helmet) as the engine computes them. Heavy Helmet reads the current Retreat Cost once the rules/09 fix is in; the fix goes in first, with its replay, and kt does not mirror the engine.
- **Timing is the clock's own, not a new one.** f = the absolute turn on which the clock already puts the threat's first hit (its missing-Energy count included; for a Benched threat, what the clock uses for it).
  - Temporary cuts are read for turn f.
  - A card effect counts only if its turns_left reaches f.
  - A turn effect counts only if registered for f; Jasmine, Cheren and Blue live on t and t+1 only.
  - Two engine changes this needs: `first_attack_turn` is extended from the Active threat to any slot, and `get_turn_effect_damage_reduction` takes a turn.
- **Hits.** d_first = max(0, damage − temporary − permanent); d_later = max(0, damage − permanent). KO turns = `ko_turns_after_first_attack(hp, d_first, d_later)`, where d_later is per victim.
  - This is the one change to the clock's arithmetic: kp uses one max_damage for every victim.
  - kd's (first, later) structure is not taken over, only this per-victim later damage.
- **Units, stated so the reading can be judged.** The clock counts whole turns at 100 per turn, so a cut that doesn't change the number of hits is worth 0 here.
  - Prediction: Jasmine and the Barrier are played under kt only on turns where they save a hit, so their play rate will be well below the flat +10's 82%.
  - If deck 07 shows no gain, that refutes clock-only pricing, and a finer safety term is a new registered code, not an amendment.
- **Where the table sees it.** Frigibax's Stiffen (Suicune) only. **[filled]** The carrier census confirms the panel's `t-suicune.txt` carries one Frigibax P-B 037 (13 Limitless lists equal it card for card), so switch 1 reaches the table's own Suicune cells.
  - Prediction: Stiffen use rises from 44% of offered turns (55 of 124 under kp3).
  - No table cell moves beyond paired noise under kta3 (footprint expected under 5%).

## SWITCH 2: the flat +10 replaced by the holder's terms (both sides, the same rule each side)

- **HP Tools** (Giant Cape, Leaf Cape, Elegant Cape on a Stage 1): `get_effective_total_hp`, already in the board term (HP × (relevant Energy + 1)), the Active's safety and the clock; nothing more.
  - Predicted worth on a powered Active: up to +80 (Giant Cape) and +120 (Leaf Cape); the same for Field Blower on the opponent's.
  - Elegant Cape on a Basic: 0 on both sides. There is no deck or hand read: `evolution_potential` isn't used (it is off in kp and 0 under public evaluation).
- **Retreat Tools** (Small Balloon, Inflatable Boat): the own Active's retreat term through `get_board_retreat_cost_for_player`, which already prices the eligible case; 0 on an ineligible holder.
  - The opponent's retreat Tools: 0 (the score has no opponent retreat term; a later candidate).
  - Recorded: an eligible Balloon or Boat on the own Active is +1 against −1 for the card, an exact tie decided by move order.
  - Prediction: Altaria's Balloon plays fall from 88% of offered turns, and its useless placements (225 of 501) to near 0. Suicune's Boat plays fall from 60%.
  - The direction of the Altaria and Suicune rows is not predicted. An own-side drop beyond the mixed row's paired noise on either is a rule-v2 veto, and is expected to be the first thing the rows are asked.
- **Damage-cut Tools** (Metal Core Barrier, Steel Apron, Heavy Helmet): through switch 1 on a qualifying holder, 0 otherwise. Under ktb alone: 0.
- **Protective Poncho:** 0 on both sides, Active or Benched, in this candidate.
  - Reason: kp's clock prices hits on the Active only. Bench-hit pricing is the "reach" sub-change that broke Lucario in kd3, and is a later candidate of its own (through `persistent_defender_damage`'s DefenderHit gate and `only_damages_the_bench`, when it comes).
  - Prediction: Lucario's Poncho plays fall from 68% of offered turns (427 of 428 on the Active) to near 0. No prediction for Lucario's row.
- **Counter-damage Tools** (Rocky Helmet; Poison Barb): switch 3.
- **Deceptive Needle:** own side as now (its first chip lands inside the searcher's EndTurn, which the search resolves); opponent's side 0 (the opponent's EndTurn is never searched). Recorded asymmetry.
- **Tools no term reads** get 0, so they are never played under kt:
  - Lucky Egg, Electrical Cord, Leftovers, Memory Light, Lucky Mittens, Lum Berry, Sitrus Berry, Rescue Scarf, Beastite, Dark Pendant, Clear Veil and Future Booster Energy Capsule;
  - any Tool whose only job is to enable "+X if a Tool is attached".

  Accepted and listed. brew-04 (Lucky Egg, 147 attached in 240 audit games) and any B2e held-out deck carrying one are reported under the "no more than 2 further from Limitless" rule.
- **Field Blower, Guzma and Repel** gain exactly what removing or moving the Tool changes under the rule above. Prediction, both directions stated:
  - Blower stops removing the opponent's Needle, Balloon and Boat (453 + 93 + 64 of its 1,414 Active removals under kp3) and keeps removing Capes and Rocky Helmet.
  - Hydreigon's and Weezing's rows rise, and Hydreigon's gap grows (already +5.2 above Limitless on v2 under kp3). A Hydreigon deck-gap veto is the expected readout of this switch.
  - If the mixed rows show the rise is on the opponents' side (Blower decks piloted worse), that is the recorded cause, and the opponent's Needle is the first item of the later candidate "opponent's Tools the search cannot play out".

## SWITCH 3: damage back to the attacker, in the holder's own side's KO clock (both sides)

- **Through `get_counterattack_damage`:** Rocky Helmet, `CardEffect::Counterattack` such as Spike Armor, and `CounterattackDamage` Abilities. None of the latter is in the eight lists; declared here.
- **Formula.** For our clock on threat T against our Active holder H with counter damage c:
  - T's HP for our clock is reduced by c × k, where k is the number of hits T lands on H before our knockout of T;
  - **[amended]** k = min(n_ours − 1 + s, n_theirs) — Fable's text had n_theirs − 1;
  - n_ours is our clock's hit count on T without the counter, n_theirs the opponent's clock's hit count on H, and s = 1 if T's owner is to move (T attacks first), else 0;
  - the count is then recomputed once with the reduced HP.

  Reason for the amendment: the engine applies the counter-damage to the attacker for every damaged Active, whether or not the hit knocked it out (`handle_attack_retaliation`, `actions/apply_action_helpers.rs`), and the rules say the same ("still fires if the holder is Knocked Out", `rules/04`). So the knockout hit counts, and T lands at most n_theirs hits on H.
  - **[amended]** It applies only when T is both the opponent's threat in its own clock and our clock's current victim, the opponent's Active. A Benched threat has not attacked H yet, so its hits are not counted.
  - This couples the two clocks by one read each way, and is stated so.
- **Poison Barb:** not in this candidate. It needs the Special Conditions model, deferred with it, and Barb is in no table deck. `should_poison_attacker` is not called.
- **Prediction:** Blaziken keeps playing Rocky Helmet under kt and ktc (69% of offered turns now) and stops under ktb; Blaziken's row is switch 3's to explain.

## FOOTPRINT AND ROUTES (section 8 line 130, restated verbatim so nothing is loosened later)

- **Footprint** = the share of the table's 14,000 paired games in which the new bot's play differs from kp3's at least once (move fingerprint), measured against the kp3 reference regenerated at the same engine. Reported for kt3, kta3, ktb3 and ktc3.
- **kt3 (all three):** expected over 15%, so the ordinary adoption rule applies:
  - paired ΔMSE against kp3 on scoreboard v2's 27-cell decision set, with the whole 95% interval below zero (binomial, by-event beside it);
  - vetoes under rule v2 (a cell's miss grows by more than 6, a deck's gap by more than 2, a B2e held-out deck more than 2 further), counting only when the 28-pairing mixed rows on the same deals show kt3's own side worse beyond the row's paired noise, and never on a cell with a Limitless band over 15.0;
  - the tau margin with its 90% interval reported beside it.
- **kta3 (switch 1)** under the reserve route, its own reading:
  - (a) footprint under 15% on the same paired files;
  - (b) no harm: tau margin (kp3 minus kta3) 90% lower bound at −1.0 or above, and no rule-v2 veto;
  - (c) mixed rows for the pairings where kta3's footprint is non-zero (Suicune's seven, both directions, 500 deals): no meta deck's own side worse beyond noise;
  - (d) a gain beyond paired noise on kta3's own side on at least one Limitless top-30 archetype that is not Dustin's deck and carries the relevant cards, named below before any list is read; deck 07 and Dustin's other carriers reported too, as motivation and not as the test;
  - (e) adoption for the screen and the table together.

  Stated now: if the carrier census finds no such archetype, or one with no usable decklist, the route is closed for switch 1 and it is adoptable only by Dustin's explicit override, recorded as such. The route is not loosened after the census is seen.
- **Outcomes fixed now:**
  - kt3 passes and kta3 passes: kt adopted (screen and table).
  - kt3 passes and kta3 fails or is closed: nothing adopted as built. Switches 2 and 3 are re-registered as a new code with a new table, unless Dustin overrides for kt as a whole.
  - kt3 fails: nothing adopted. The diagnostic codes are read for attribution only, and the next candidate is registered afresh.

  A spec change after any reading is a new code.

## CARRIER CENSUS FOR (d) **[filled]**: done by the laptop before this commit, before any kt game

**Order, stated plainly.** Fable's text had the census run after this commit. It was run first, by the laptop, and its README was read before this was written, so the archetype names below were chosen with the lists in view. What was fixed before the census ran is the route itself: section 8 line 130's clauses and its closure sentence. The census applied them without choosing between readings, and this file doesn't choose either.

The laptop's census (`rl/results/kt_carrier_census_2026-09-26/`) scanned the Cowork Limitless pull's 63 development events (4,722 decklists; holdout never opened) for the switch-1 card set, over 35 top-30 archetypes (the Sept 10 top 30 and the window's). It found three carrier archetypes; every other archetype carries 0.
- **Dragonair Mega Rayquaza ex**: Gouging Fire B3a 054 (an attack that registers ReducedDamage 30 on itself) in 135 of 143 lists (94%). Sept 10 rank 22; window rank 6.
  - A usable list: `rl/results/kt_carrier_census_2026-09-26/decks/c-dragonair_mega_rayquaza_ex.txt` (20 cards, Energy Fire and Lightning). It is thefossilman's list, 1st of 219 at Umbreon99's Aura Sphere #4 on 2026-09-11 (event 6a7e2b83cdc0391d7fa65afb, development split). deck_check is clean and all 13 cards are fully implemented.
  - Limitless cells against all eight panel decks: pooled equal-weight 46.3 ± 4.8 over 606 matches, none under 20 pooled (`cells_c-dragonair_mega_rayquaza_ex.csv`). These are the before figures for the "reported, not gated" line.
- **Suicune ex Baxcalibur**: Frigibax P-B 037 (Stiffen) in 22 of 200 lists (11%). The panel's own `t-suicune.txt` is one of them, equal to 13 Limitless lists.
- **Vespiquen ex Shuckle ex**: Blue A1a 067 in 4 of 233 lists (1.7%, all Sept 21); no list built.

**The (d) archetype turns on Dustin's ruling, to be recorded in a dated commit before any kta game:**
- **If the Dragonair overlap with his deck 11 does not make Rayquaza "his deck"** (the census's reading 2: Mega Rayquaza ex and Gouging Fire are in no file of his): the (d) archetype is **Dragonair Mega Rayquaza ex** with the list above.
- **If it does** (reading 1, the census's conservative rule, since 2 Dragonair B4 117 are in `decks/dustin/11-archaludon-haxorus-dragonair.txt`): the route is open only through the occasional carriers. Each needs the gain shown on a list that actually carries the card:
  - Suicune ex Baxcalibur with Frigibax P-B 037 (the panel's own list, or the two-Stiffen shell in the census's `carrier_entries.csv`);
  - Vespiquen ex Shuckle ex with Blue (a list to be built from `carrier_entries.csv`).

  Whether an 11% or 1.7% carrier share satisfies "carries the relevant cards", and whether a panel deck can serve, are readings of the fixed text for Dustin.
- **A third reading for Dustin, from the census's section 1.** Section 8's closure sentence names "reduction Tools or turn-effect cards". Gouging Fire and Frigibax are neither: each is a Pokémon whose own attack cuts the damage it takes on the opponent's next turn, a card kind switch 1 prices through the same hook. The only turn-effect carrier outside Dustin's decks is Blue, in 4 Vespiquen lists. Whether that kind counts as "the relevant cards" is also Dustin's to rule.
- Where the (d) archetype has real Limitless cells against the eight table decks, those cells are reported before and after, and not gated.

## DUSTIN-DECK A/B (reported for kt3 and kta3; motivation for switch 1, not its test) **[filled with the laptop's answers]**

- **Decks and arms.** Decks 07, 05, 11, 01 and 03 against the floor panel. kt3 on the deck seat against kp3 on the deck seat, with **kp3 on the opponent's seat in both arms** (the mixed-row design).
- **Size.** 240 games per matchup × 8 = **1,920 games per arm**, paired by seed, with McNemar beside the paired difference.
- **Measures:**
  - deck win rate;
  - Jasmine's play rate with **"offered"** as the denominator (turns on which Jasmine was a legal play, the census's definition);
  - Barrier, Apron and Heavy Helmet placement (qualifying holder or not).
- **Seeds:** **22,600,000,000 – 22,699,999,999**, written into START_HERE's seed table in this commit.
- **The comparison size, separated as Fable noted:**
  - the flat +10 took Jasmine to 82.4% on the 240-seed causal block;
  - the deck-seat-only Jasmine pricing gave +5.7 points on a separate fresh 1,920-game block.

## READOUT COUNTERS (fixed now) **[amended: added]**

- For kp3 (regenerated), kt3, kta3, ktb3 and ktc3 on the same deals:
  - `tool_census.rs`'s per-card table: turns offered, turns played, holder by spot and name, and Field Blower's targets. The tool is in `../tool_turn_effect_census_2026-09-25/`, run on the first 100 deals of each pairing, with fingerprints checked against the table file.
  - `legality_scan`'s Hyper Ray, Chase Order, discard-attack and Ability counters (a03f491).
- Field Blower's rate is reported with the census's denominator, turns on which it was a legal play. The Trainer audit's "turns with an opponent target" figure is quoted beside it, not mixed.

## IDENTITY AND ORDER

1. **rules/09 fixes first**, each its own commit with a full k3 and kp3 replay of the 14,000 table games. Each lists the games that differ and shows they lie in cells where the mechanic is reached (Blaziken v Suicune for Pulse and Hiking Trail; Poké Ball games listed by seed). The fixes:
   - Legendary Pulse v Hiking Trail;
   - Heavy Helmet at the current Retreat Cost;
   - Rare Candy v Primeval Law;
   - Poké Ball A2b 111 with an empty deck;
   - Crawdaunt's "random" Energy discard (Fable's text). **[amended: added]** The Supporter Psychic, which takes the last-attached Energy in the same way (rules/09).
   - **[amended: added]** Discard-all-Energy attacks putting the Energy in the discard pile.
   - **[amended: added]** The end-of-turn and Checkup knockout promotion timing (the knocked-out player promotes before the next player's draw; footage 07aafa3, `docs/REVIEW_2026-09-24_direction.md` on main). Like Pulse, it reaches table games, so its replay is read for changed games.
2. **kp3's reference table regenerated at the fixed engine** (kp3_500 at that commit), and scoreboard v2's kp3 row re-scored on it by the laptop. This is kt's paired base and the base for the footprint.
3. **At kt's build:**
   - k3, kp3 and kq3 replay 14,000 of 14,000 against the fixed-engine references;
   - kd3 and kpr3 replay at least 1,120 of 1,120 (i < 40 of every pairing);
   - a kt-only diff of everything after the last full replay, as the kpr reading required.
4. **The tables.** kt3's table (28 × 500 on the table's deals), then kta3, ktb3 and ktc3 on the same deals.
   - The laptop's mixed rows are run from a build of the table's commit.
   - timing.txt has kt3's 40-deal run within 1.25× kp3's, or the per-leaf Tool classification is rewritten before the table (one pass over `attached_tools` against the effect texts in `tools.rs`, not a `tool_count` call per Tool id).
5. **Everything above is read by the laptop** under rule v2 with score.py; this folder only reports.

## Amendments to Fable's text, in one place

- **Switch 3's hit count:** k caps at n_theirs, not n_theirs − 1, because the engine and the rules fire Rocky Helmet on the knockout hit. It applies only to the opponent's Active threat.
- **Filled in:**
  - the (d) archetype, with both readings, the group-3 wording point, and Dustin's ruling to come (the census ran before this commit, not after);
  - the Stiffen baseline and the Suicune list's one Stiffen card (from the census);
  - the A/B size, opponent seat, denominator and seeds (the laptop's answers);
  - the base (kp3, per the kpr reading).
- **Added:**
  - the readout counters;
  - three engine fixes to step 1: discard-all-Energy to the discard pile; the Supporter Psychic's Energy pick; promotion timing after an end-of-turn or Checkup knockout.
