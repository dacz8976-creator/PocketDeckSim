Decision this informs: whether the pilot after kp3 prices the defender's temporary damage cuts and reduction Tools in the threat clock, replaces the flat +10 for a Tool on the Active by what the Tool does for its holder, and credits damage back to the attacker; read against kp3 by the Sept 25 plan. **Amendment 2 (Sept 28; reviewed once, its fixes folded in; waiting on Dustin's word) re-issues kt on kog: read against kog3 on the 45 cells. Once Dustin approves it, it holds over the text below (its Status says what else each kt game waits for).** This file is kt's registration (Sept 26), committed before any kt code or game. kt was first built on kp at 43cef0b (`BUILD.md`, kept as history); the codes re-issued on kog need a new build (amendment 2, item 7).

Seeds: kt's table on the table's deals (72,000,000 + pairing × 10,000 + i, i < 500, even i = first-named deck in seat 0). Under amendment 2 also: the 17 new cells on 21,108,000,000 + pairing × 10,000 + i (pairings 8-24 of `../gauntlet_runs_2026-09-26/tsv/new_decks.tsv`, i < 500, even i = the new deck in seat 0); B2e's rows on 21,106,000,000 + pairing × 10,000 + i (pairings 0-95); the Scizor row on 21,108,000,000 + pairing × 10,000 + i (pairings 0-7 of `new_decks.tsv`, Scizor in seat 0 on even i); the second lists on their main lists' deals, with no new seeds (`tsv/var_<version>.tsv`: Lucario's at table pairings 2, 8, 13 and 18-21, Suicune's at 4, 10, 15, 19, 22, 25 and 26, Weezing's at 6, 12, 17, 21, 24, 26 and 27, all on 72,000,000; Charizard Y's on B2e pairings 40-47 on 21,106,000,000; even i = the file's first-named deck in seat 0); the Rayquaza v Lucario traces on 21,108,900,000+ (`--seed-stream`, 200 games); clause (d)'s rows on 22,700,000,000 + panel index × 10,000 + i (amendment 1); the Dustin-deck A/B on the new block 22,600,000,000 – 22,699,999,999 (START_HERE's seed table).

# kt: Tools and temporary damage cuts priced by what they do (registration, Sept 26)

**Source.** Fable's proposed registration text (`rl/results/fable_reviews_2026-09-26/kt_spec_review.md` on main, "The registration text Fable proposes the cloud commit"), taken as written except where marked **[amended]** or **[filled]** below, with the reason beside each; the laptop's answers of Sept 26 (A/B size, opponent seat, Jasmine's denominator, seed block, kp3 regenerated after the rules/09 fixes); and the laptop's carrier census for clause (d) (`rl/results/kt_carrier_census_2026-09-26/README.md` on main). The earlier draft (`../tool_turn_effect_census_2026-09-25/README.md`, c002d2f) is superseded; its census stands. Any change after this commit is a dated amendment before any kt game, and a spec change after any reading is a new code.

## Amendment 2 (Sept 28, before any kt game on kog): kt re-issued on kog. Reviewed once; waiting on Dustin's word

**Status.**
- **Review.** The draft (2b01c65) had its one review on Sept 28 (`REVIEW_amendment2_laptop_2026-09-28.md` in this folder, on main at 9cdcd3b). Skeptics confirmed 34 findings (R1-R13, C1-C10, F1-F11), and all are folded in below. The 7 refuted findings aren't taken up. The harm tests for the Scizor row and the second lists are kph amendment 2's, as that amendment offers them to kt (item 4).
- **Before any kt game, Dustin's word is needed on:**
  1. this text as kt's registration on kog (amendment 1: the registration is his decision, "the text he is asked to approve");
  2. the new build on kog, with its timing run. His Sept 27 go-ahead was "build kt now, as registered", on kp3 (`BUILD.md`). Whether it extends to a build on kog is his to say.
  3. kt's tables. `BUILD.md` records that the tables wait for his word, and notes that his word depends on which pilot kt is read against.
- **Also needed before any kta game,** from Dustin or the laptop: amendment 1's open confirmation, Rayquaza as the one clause (d) test, with Suicune reported. A commit records it and names who gave it; a review can't supply it.
- **The order, set by this amendment:** kog's check, then koh's reading, then kt. No kt build or game comes before koh's verdict is committed, coverage included.
- **The rules-file refactor gate** (item 1): no kt game until the Sept 28 engine switch's check of kt's refactor of the rules files is committed as passed.

**Why an amendment re-issues kt.** The base line (BASE AND CODES below) says: "Built on the pilot the kpr reading leaves: kp3. If that changes, this registration is re-issued, not amended." The base has changed.
- kog passed its composition check on Sept 28. It is the working pilot, "unconfirmed" (RUN5 "Composing candidates into one pilot"; `../kog_composition_2026-09-27/READING.md`, 5bca434). kog is kp3 plus koa's opening switch A plus kpg's discard credit F.
- The laptop asked for the re-issue as a dated amendment to this file. That keeps the registration in one place with its history visible. In substance it is the re-issue the base line asks for: every clause below is re-read on the new base, before any kt game on it.
- **What kt games exist.** All are on kp3; none is on kog, none is a table game, and none is on clause (d)'s seed block or the A/B's.
  - The build at 43cef0b ran identity replays and 40-deal smokes on the table's deals, all 28 pairings (`BUILD.md`).
  - The smokes were read for how often, and in which cells, a game's choices differ from kp3's: kt3 65.7% (every cell), kta3 1.4% (Suicune's cells), ktb3 66.7% (every cell), ktc3 8.8% (Blaziken's cells).
  - Their scan pages also print, for deals 0-39 of the 28 pairings under the kp-based codes:
    - each cell's first-deck win rate;
    - `legality_scan`'s counters (Hyper Ray, Mega Burning, Terminating Tail, Diving Icicles, Chase Order and Ability turns).

    No reading uses them. Item 9's counters are new runs of the kog-based codes at the kt build.
- **If koh's reading makes koh the working pilot,** kt is re-issued on koh by a further dated amendment, reviewed before any kt game. That is not a flag change.
  - kt's clock replaces the whole threat clock and takes no projection. In `players/value_functions.rs`, `extract_features` uses a given clock in place of `calculate_turns_until_opponent_wins_projected`, and `kt_clock` calls `threat_candidates` with no projection.
  - So on koh, switches 1 and 3 would switch off two things: R′'s projected clock (kpr's minimum over the clock with and without the projection), and fix B, which acts only inside it.
  - These stay on: R's readiness projection with fix A (the Active online score, in setup and after it), R's projection of the pile F reads, and F itself. ktb keeps all of R′.
  - That amendment says how switches 1 and 3 combine with R′'s clock, and the new build tests it.

**Where this amendment and the text below (amendment 1 included) differ, this amendment holds.** Everything it doesn't name stands as written:
- the rule and the three switches;
- the reserve route and its clauses (item 2 adds kt3's);
- amendment 1's rulings.

Dustin's go-ahead of Sept 27 covered the build on kp3; for the build on kog, see Status.

1. **Base and codes.** `kt<N>` = `kog<N>` with the three switches on. `kta<N>`, `ktb<N>` and `ktc<N>` = `kog<N>` with switch 1, 2 or 3 only. kq's, kd's and kpr's features (R, and kph's fixes A and B) are off.
   - **Every "kp3" below that names the base or the paired comparator reads kog3.** That covers:
     - the reference and the footprint;
     - the mixed rows' other side;
     - the τ̂ margin in clause (b) (kog3 minus kta3);
     - clause (d)'s comparator arm and the panel's pilot;
     - the Dustin-deck A/B's comparator and opponent seat;
     - the readout counters' baseline;
     - the timing budget.
   - **The code names already mean the kp-based bots** (C1, F1).
     - In every build since ed81c8b, kt3, kta3, ktb3 and ktc3 are the kp-based codes of 43cef0b. That includes 233bced, the official engine being pinned on Sept 28 (deckgym sha256 4f46c87f…, the laptop's `PIN_STATUS.txt`).
     - The kt build redefines them on kog, and its parser and preset tests check that.
     - **Every game under this amendment is played by the kt build's own programs,** with their sha256 recorded in `BUILD.md`: the tables, the mixed rows, the coverage rows, clause (d), the A/B, the Rayquaza traces, the readout counters and the timing run.
     - **Each output file name starts with that build's commit** (`<build>_kta3_500.jsonl`).
     - The official program is not used for any kt code until an engine switch carries the re-issued presets.
     - Files from 43cef0b's kp-based codes are never compared with, or pooled with, the re-issued ones.
   - **How the parts meet** (`parametric_value_function_ex6`, read at bd2907f):
     - Switch A is read only in the setup evaluation, which returns before any clock is computed.
     - F is its own term, added after the score is summed. It reads the discard pile (the whole pile, since R is off), not the clock.
     - kt's clocks replace kog's, which are kp's (kog has no projection).
     - Switch 2 zeroes only the flat Tool term.
     - So kt on kog is kog's value in setup. After setup it is kt's clock and Tool term, plus F. Item 7 tests this on values.
   - **What shows kt's shared code changes nothing for other bots** (C2, R3). The build at 43cef0b (kt on kp) stays as history. The evidence comes in two parts:
     1. **The refactor of the rules files** `hooks/core.rs` and `hooks/mod.rs` (ed81c8b, 92c4563). This is judged by RUN5's rule for a refactor of a rules file (Dustin, Sept 28), through the Sept 28 engine switch's check (`../engine_switch_2026-09-28/`): the written source equivalence, the full suite, and games that reach the touched paths on the Barrier, Jasmine, Cheren and Blue carriers and the Scizor row, replayed on both builds.
        - The whole-table replays at 43cef0b don't qualify on their own. The table's lists reach the changed lines only on their "no cut" branch.
        - **No kt game until that check's result is committed.** If it fails, kt waits with the engine.
     2. **The shared player code** in `value_functions.rs` (`threat_candidates`, `owner_next_turn`, `first_attack_turn_number`, `extract_features`' optional clock). This is shown by the full table replays of the bots whose clocks run it: kp3, kq3 and kog3 (item 7).
2. **The frame: the 45 cells.** RUN5 "The frame a candidate is read in" (Sept 27) registers every candidate from Sept 27 on the 45 cells, and this amendment is dated Sept 28.
   - **On the 45 cells** (R4, F11):
     - the footprint;
     - the ordinary rule;
     - clause (b)'s τ̂ margin (kog3 minus kta3), and kt3's reported τ̂ margin, each with its 90% interval;
     - the vetoes;
     - clause (c)'s mixed rows;
     - kt's four tables.

     Details:
     - The cells are the table's 28 on the table's deals, and the 17 new cells, which are pairings 8-24 of `../gauntlet_runs_2026-09-26/tsv/new_decks.tsv` (the same rows as `new_decks_run.tsv`). Altaria v Sceptile is included, as in scoreboard v3 and kog's and kph's readings.
     - Each code's table is 45 × 500 paired games: step 4's "28 × 500 on the table's deals" plus 17 × 500 on the new cells.
     - "Scoreboard v2's 27-cell decision set" reads "scoreboard v3's 45 cells", and "the 28-pairing mixed rows" reads "the 45 cells' mixed rows".
     - Everything is read with `score45.py`, with the event-level interval beside the match-level one, as the standing column requires. Step 5's "score.py" reads "score45.py".
     - "The table" in clause (e) ("adoption for the screen and the table") and in step 4 ("the table's commit", "before the table") names the pilot's role and kt's own run. Those uses are unchanged.
     - Identity is as item 7 states.
   - **The references** (R3, C3, C4):
     - They are kog3's own runs from the laptop's build of a823b6d (`../kog_composition_2026-09-27/table_kog3.jsonl`, `new17_kog3.jsonl`).
     - a823b6d is main 83e17ae plus the branch's player code (kt, kog) and kt's refactor of `hooks/core.rs` and `hooks/mod.rs`. That refactor is qualified only through item 1's check.
     - At the cloud's build of a823b6d, k3 and kp3 replay the official references 14,000 of 14,000. At the laptop's build they replay 1,120 of 1,120, and its `table_kog3` equals the cloud's on 14,000 of 14,000.
     - **The kt build** is the official engine's commit at the time plus kt's preset change only. That is 233bced once it is pinned; its `engine/` equals bd2907f's.
     - The references stay `table_kog3` and `new17_kog3` whichever commit is official, because item 7 checks kog3 at the kt build against both. kog3 at 233bced already equals `table_kog3` on 14,000 of 14,000 (the laptop's `PIN_STATUS.txt`).
   - **Footprint:** the share of the 45 cells' 22,500 paired games whose moves differ from kog3's. It is read first and fixes the route for kt3 and kta3 alike: under 15%, the reserve route; otherwise, the ordinary adoption rule.
   - **The ordinary rule:** paired ΔMSE against kog3 on the 45 cells, with the whole 95% interval below zero. Vetoes are rule v2's, counting only through mixed rows against kog3 on the same deals.
   - **kta3 on the reserve route:** clause (c)'s mixed rows are the pairings of the 45 cells where kta3's footprint isn't zero, both directions, 500 deals.
   - **kta3 at 15% or more** (F4, R2). As amendment 1 rules, kta3 then goes by the ordinary rule against kog3:
     - paired ΔMSE on the 45 cells, rule v2's vetoes through its mixed rows, and the coverage no-harm tests of item 4;
     - "kta3 passes" in the outcomes (FOOTPRINT AND ROUTES) then means passing that rule;
     - clause (d) and its report beside are still run and reported, but gate nothing ("the one test" applies under the reserve route);
     - BASE AND CODES' "except kta under the reserve route" reads "except kta, by the route its footprint fixes".
   - **kt3 under 15%** (R2). kt3 takes the reserve route with kog3 as comparator:
     - (a) that footprint;
     - (b) the τ̂ margin (kog3 minus kt3), 90% lower bound at −1.0 or above, and no rule-v2 veto;
     - (c) the 45 cells' mixed rows wherever kt3's footprint isn't zero, both directions, 500 deals;
     - (d) kt3's own-side gain beyond paired noise on the census Rayquaza list's eight rows, on the same seeds and at the same size as kta3's (kt3's own test, not a second chance for kta3's);
     - (e) as written.
3. **Where the switches reach on the 45 cells.** This is read from the lists, not from games, with the carrier census's card set (`../kt_carrier_census_2026-09-26/cards.json`) and the card database. Every switch acts on both sides, so a cell is reached when either list carries the card.
   - **Switch 1 reaches 17 of the 45 cells, not just Suicune's seven:**
     - Suicune's list (one Frigibax P-B 037, Stiffen): its 7 table cells and its 2 new cells (Rayquaza v Suicune and Mega Altaria ex Greninja v Suicune).
     - The scoreboard's Rayquaza list, `decks/gauntlet_2026-09-26/g-dragonair_mega_rayquaza.txt`, carries 2 Gouging Fire B3a 054 (a self-cutting attack, amendment 1). So switch 1 reaches all 9 Rayquaza cells.
     - Mega Altaria ex Greninja carries no switch-1 card.
   - **Switch 2 reaches every cell.** Every list carries a Tool.
     - Rayquaza carries a Small Balloon and an Ancient Booster Energy Capsule. The capsule is an HP Tool (+40 HP on an Ancient Pokémon, as `card.py` prints it), priced by the rule like the Capes, with no spec edit.
     - Mega Altaria ex Greninja carries a Small Balloon.
   - **Switch 3** is carried only by Blaziken's list (Rocky Helmet). So it reaches Blaziken's 7 table cells and 2 new cells (Rayquaza v Blaziken and Mega Altaria ex Greninja v Blaziken).
   - **The prediction "kta3's footprint under 5%"** was made on the 28 cells, where only Suicune's seven carry a switch-1 card. It is not restated for the 45, where the Rayquaza cells are new ground for switch 1. Predictions never choose the route (amendment 1); the measured footprint does. Item 2 fixes both routes for both codes.
   - **Clause (d) stays the one test under the reserve route** (amendment 1): kta3 against kog3 on the census's Rayquaza list, 8 × 500 deals on the 22,700,000,000 block.
     - The scoreboard's Rayquaza list is a different list: two Trainers and the Dratini card differ.
     - Its 45-cell rows are read under clause (c), for no harm, and never as a second chance at (d).
   - **The Rayquaza archetype's real cells are no longer ungated** (R13).
     - As 45-cell cells, they count for no harm in (b), in the vetoes and in the ordinary rule.
     - What stays ungated ("reported, not gated" in the text below) is any gain through them. It is reported and never credited to (d).
   - **Amendment 1's report beside (d)** ("Suicune's own side on its seven kta3-v-kp3 mixed rows, the same rows (c) reads") now reads: Suicune's own side on its nine rows (7 table and 2 new), kta3 against kog3.
4. **Coverage** (RUN5 "The frame a candidate is read in"). Held-out and coverage decks are read before any verdict is final, whatever the 45-cell result (as kph's registration, section 5 item 6).
   - **A veto there blocks the takeover.** A gain is reported, not credited.
   - **"Not adopted" is provisional** (R1; RUN5 "A 'not adopted' is provisional until the coverage decks are read").
     - A "nothing adopted" under FOOTPRINT AND ROUTES (kt3 fails; kta3 fails or is closed) stands only once kt3 has been read on all the coverage rows: B2e's 96 pairings, the Scizor row and the four second lists. kta3 is read on them too, if it took the reserve route.
     - Coverage evidence can reopen kt only through a new reading under the rules in force, never by re-reading this one.
   - **Who is read and how** (R5):
     - Coverage is run for kt3, and for kta3 when it takes the reserve route (its (b) includes the held-out veto).
     - First each code runs on both sides, as kpg and koh did.
     - Then mixed rows (the code on the held-out or coverage deck, kog3 on the other deck) are run on:
       - every B2e held-out deck that moves more than 2 points further from its figure;
       - every Scizor and second-list row, which the harm tests below always read.
   - **B2e's held-out archetypes (pairings 0-47):** one moving more than 2 points further from its Limitless pooled equal-weight average is a veto, through mixed rows as above. The development half's figure is printed beside, as in kpg's held-out check. Dustin's files (48-95) are reported beside.
   - **The second lists, per kph amendment 2** (F2). The lists are `decks/gauntlet_2026-09-26/v-lucario_2.txt`, `v-suicune_2.txt` and `v-weezing_2.txt`, and `l-charizardy.txt` from `decks/screen/panel_ladder_2026-09-26/`.
     - Each stands for its archetype's usual list (RUN5, the variation check), so it is read against its archetype's Limitless figure:
       - for Lucario, Suicune and Weezing, the development half's 7-opponent average (scoreboard v3's cells);
       - for Charizard Y, the figure B2e's held-out rule reads for Charizard Y Entei.
     - **A veto:** the list's opponent average under the kt code (on both sides) ends more than 2 points further from that figure than under kog3 (on both sides).
     - It counts only when the list's own side is worse beyond the variation check's paired 95% interval. The own side is read from mixed rows: the kt code on the list and kog3 on the other deck, against kog3 on both, 500 deals, paired by deal.
     - Cell-level vetoes don't apply to these rows.
     - The deals are each version's own: `../gauntlet_runs_2026-09-26/tsv/var_v-lucario_2.tsv`, `var_v-suicune_2.tsv`, `var_v-weezing_2.tsv` and `var_l-charizardy.tsv`, as the variation check ran them.
   - **The Scizor row, per kph amendment 2** (F3). It has no usable Limitless figure: 0 to 6 development matches per cell, two cells empty. So harm there means the kt code plays Scizor worse.
     - **A veto:** Scizor's own-side average over its 8 rows falls by more than 2 points, and its paired 95% interval lies wholly below zero.
       - The own-side rows: the kt code on Scizor with kog3 on the panel list, against kog3 on both sides, paired by deal, 500 deals per row (21,108,000,000 + pairing × 10,000 + i, pairings 0-7 of `tsv/new_decks.tsv`).
       - The interval is the variation check's: 1.96 × sqrt(Σ per-cell variance of the mean difference) / 8.
       - The 2-point size is rule v2's deck-level size, so a drop inside the average's own noise (about ±1.5) can't veto.
     - The other direction (the kt code on the panel list, kog3 on Scizor) is reported only. The panel decks' harm is read on the 45 cells.
     - Scizor's real figure (32.2 ± 10.2 pooled; 25.7 ± 11.7 development, 6 opponents; `../gauntlet_runs_2026-09-26/README.md`) is printed beside, and gates nothing.
   - **Reach there** (both sides, as in item 3):
     - **Switch 1:** the Scizor list carries 2 Metal Core Barrier B2 148, so switch 1 reaches its 8 rows. Through the panel's Suicune it also reaches every coverage row against Suicune:
       - B2e pairings 4, 12, 20, 28, 36 and 44 (held-out) and 52 to 92 in steps of 8 (Dustin's);
       - the second lists' rows against Suicune: v-lucario_2's row 19, v-weezing_2's row 26 and l-charizardy's row 44.

       No B2e list or second list carries a switch-1 card of its own.
     - **Switch 2** reaches every coverage row. Every held-out list, every panel list and every second list but Lucario's carries a Tool, all of kinds the registration already prices. Protective Poncho, priced at 0 as Lucario's is, is in the held-out Garchomp list and in Charizard Y's second list.
     - **Switch 3:** through the panel's Blaziken, every coverage row against Blaziken.
   - **kog3's coverage baselines** (F5, R12). These are B2e's 96 pairings, the Scizor row's 8 and the second lists' 29 rows.
     - They are the files koh's reading commits for them, at koh's build bd2907f (queued Sept 28: `../koh_2026-09-28/reading/b2e_kog3.jsonl`, `scizor_kog3.jsonl` and `var_<list>_kog3.jsonl`), if they are committed before kt's build. Item 7 checks them at the kt build on i < 40 of every pairing.
     - Any not committed by then are run with kog3 at the kt build on all 500 deals, before any kt coverage row.
     - `BUILD.md` names each baseline file before the first kt game.
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
   - **A failed check reads "not confirmed at this size"** (RUN5; F10). kt's own check is read on its own row, and kog's row stays kog3 against kp3.
   - **If kog's row is not confirmed** at any read up to and including kt's own (R8), then kt is not confirmed either, since it carries switch A and F. The same holds if kpg's or koa's row, which kog inherits, is not confirmed.
     - Both are read again at the next pull (the rolling freeze).
     - kt's switches get a new reading only if the working pilot changes from kog.
   - **Until confirmed,** an adopted kt is the working pilot, "unconfirmed". The screen moves to it once the official engine carries its code.
7. **Identity at the new build.**
   - **Presets:** kt's preset with its three switches off is kog's, and each single-switch preset is kog's plus that switch. The parser tests check that kt3, kta3, ktb3 and ktc3 now parse to the kog-based presets.
   - **Values** (C6), as kog's and koh's builds had. The test runs on every position of 12 random games (Altaria v Blaziken, Blaziken v Suicune, Suicune v Lucario, and Rayquaza v Blaziken with the scoreboard's Rayquaza list), from each player's own view:
     - where the opponent's setup is masked, kt, kta, ktb and ktc equal koa's value, and so kog's;
     - everywhere else, each equals the same switches on kp (EvalFeatures with kog's two flags off) plus kog's F term, exactly.
   - **k3 and kp3:** all 500 deals, 14,000 of 14,000 each, against the official engine's references at the time of the build. That is its frozen table once 233bced is pinned; otherwise `../rules09_fixes_2026-09-26/af8489f_{k3,kp3}_500.jsonl`, which equal it.
   - **kog3 at the kt build:**
     - equal to kog3's table (`../kog_2026-09-27/a823b6d_kog3_500.jsonl`, which the laptop's `table_kog3` equals), all 14,000 games;
     - equal to `new17_kog3.jsonl` on the 17 new cells, all 8,500 games;
     - equal to the coverage baselines of item 4 on i < 40 of every pairing.
   - **kq3** (14,000 games), **kd3 and kpr3** (1,120 each), as registered.
   - **The diff** (C5, R12): a diff of `engine/` from 233bced to the kt build, or from a later commit replayed in full. 233bced has full k3, kp3 and kog3 replays (the laptop's `PIN_STATUS.txt`).
     - It touches `engine/src/players/` only: the kt presets, the code comments and the tests.
     - A change anywhere else in `engine/` needs RUN5's repair or refactor rule before the build is used, and every kog3 baseline (table, new17, coverage) is then re-run at the kt build instead of checked by identity.
   - **Timing:** kt3's 40-deal run within 1.25× kog3's.
8. **Clause (d) and the Dustin-deck A/B keep their lists, sizes and seeds.** Only the comparator changes:
   - (d): kta3 against kog3 on the Rayquaza list's eight rows, with kog3 on the panel lists in both arms.
   - The A/B: kt3 against kog3 on the deck seat, with kog3 on the opponent's seat in both arms.
9. **The predictions' "before" figures and the readout counters.**
   - **Each prediction is judged against kog3's own readout counter** on the same deals, at the kt build's engine.
   - **Why not kp3's census figures:** those are kp3's games on the Sept 25 engine, before the rules/09 repairs. kog3's games also differ from kp3's in 1,175 of the 14,000 table games (a823b6d): 116 to 152 of 500 in each Altaria cell and 26 to 60 in each Blaziken cell, since a changed opening or F choice changes the rest of the game. That is where the Balloon and Rocky Helmet predictions sit.
   - **The census figures are printed beside, as history:** Stiffen 55 of 124 (44%); Balloon 88% and 225 of 501; Boat 60%; Poncho 68% and 427 of 428; Rocky Helmet 69%; Blower's 453 + 93 + 64 of 1,414. Jasmine's and the Barrier's "before" is kog3's arm of the Dustin-deck A/B.
   - **Hydreigon's gap** (F7): the "before" for switch 2's expected Hydreigon deck-gap veto is kog3's on the 45 cells, 51.2 against 43.9 (+7.3; `../kog_composition_2026-09-27/score45_kog3_vs_kp3.txt`).
   - **The readout counters stay as fixed:** `tool_census.rs` and `legality_scan`'s counters, on the first 100 deals of each of the 28 table pairings, for kog3, kt3, kta3, ktb3 and ktc3. Fingerprints are checked against each code's table file. `tool_census.rs` is written for the eight table decks and counts Stiffen as the only self-cutting attack, and `legality_scan` has no Scorching Interruption counter.
   - **So switch 1 on Rayquaza is read through the Rayquaza traces** (C10, F8), as kpf's reading ran them (`../kpf_2026-09-26/reading/run_traces.sh`) and kph's registration specifies them (section 5, step 4), but with the kt build's own deckgym (item 1). There are two arms, both run from the kt build with its sha256 printed:
     - `python3 rl/results/gauntlet_runs_2026-09-26/trace_pilot.py decks/gauntlet_2026-09-26/g-dragonair_mega_rayquaza.txt decks/screen/opponents/t-lucario.txt --games 200 --seed 21108900000 --pilot kta3 --opp-pilot kog3 --engine <the kt build's deckgym>`;
     - the same with `--pilot kog3`.
   - Rayquaza is in seat 0 in every game. The traces report Scorching Interruption's turns offered and used, and wins, with paired differences. They are reported only.

**Changes at the review** (2b01c65 → this commit; the finding IDs are the review's). All were made before any kt game on kog.
- **Status:**
  - Dustin's word listed item by item (R7, F9);
  - the (d) confirmation's source (R9);
  - the order as this amendment's own (R10);
  - the refactor gate (C2).
- **What exists:** the smokes' disclosure completed (C8).
- **The koh case:** stated in full (C7).
- **Item 1:**
  - the code names and the kt build's own programs (C1, F1);
  - the two-part evidence, with the refactor gate (C2, R3).
- **Item 2:**
  - the 45-cell list with (b)'s margin and `score45.py` (R4, F11);
  - the references' true source and the kt build's base commit (R3, C3, C4);
  - both codes' routes at either footprint (R2, F4).
- **Item 3:** the Rayquaza real cells' gating (R13).
- **Item 4:**
  - "not adopted" provisional until coverage (R1);
  - who is read on coverage and how (R5);
  - the second lists' and Scizor's harm tests taken from kph amendment 2 (F2, F3, R6);
  - the coverage baselines and their fallback (F5, R12).
- **Item 6:** confirmation wording and the lapse clause (R8, F10).
- **Item 7:**
  - the values test (C6);
  - k3 and kp3 against the official references at the time (C4);
  - the diff from 233bced, players/ only (C5, R12).
- **Item 9:**
  - Hydreigon's "before" (F7);
  - the traces' exact command (C10, F8).
- **Seeds line:** completed (R11, C9, F6).

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
