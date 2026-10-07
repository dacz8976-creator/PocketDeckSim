# Cloud Opus status (branch claude/pensive-ptolemy-spwc0b)

Written Sept 30 for the Fable coordinator session (Dustin's single delegator). Times are UTC.

**Step 8c's STOP is resolved** (Fable via Dustin, Oct 2): the cloud's run (abb49cf) and Sonnet's agree game for game; Dustin accepted all 8 games as documented exceptions ("Accept all 8 and pin"), on Sonnet's revert check (1,395 of 1,395 lookahead games) and the Victory Star offers at the extra tick; the rules switch is pinned (rl/engine-2026-10-02, main-8626a35, pin 24374a0), merged into both cloud branches (9a5fb3d here, d1b986c on claude/coin-prevention-round2).

## Question (the card-text job, Oct 2): files outside the five, and two cases outside the three sources (answered Oct 2: all yes; the follow-up job is in the log)

The audit is committed: `rl/results/coin_prevention_round2_2026-10-01/TEXT_AUDIT.md` (539594a, branch claude/coin-prevention-round2). The four text-decided cases that fit the five files and Trap Territory are now fixed (item 1 below). Nothing below is touched until you say:
- **A sixth file, `engine/src/card_validation.rs`:** Victini's caveat (96-98) still calls Confusion with Will and the block coin "unverified ... legacy". A text change only.
- **A sixth file, `engine/src/actions/trainer_coin_plan.rs`:** Luxury Coin ("coins for an effect of your Trainer cards") is offered on the opponent's Mesagoza or Arcade. The fix is a check of `active_stadium_owner` in `stadium_route` (95).
- **A sixth file, `engine/src/move_generation/move_generation_trainer.rs`:** a Fossil can be played under an Item lock (the Item check at 65 skips the Fossil type). Its premise is that a Fossil's printed type is Item (rules/01, rules/04 §6; the local database can't show it).
- **In the five files but outside rules/09, rules/04 and the caveats:** Guts on the attacker's own Pokémon in an attack's outcome (E1), and Perish Body on a plain queued hit at the Active (E2). Both are decided by their text. Fix them in this job, or leave them listed?

1. **Current task, and the instruction that set it.** None running; idle. The two builds after quiz 4 (Fable via
   Dustin, Oct 7) are done, both off by default, tests first, gates 1-2, km3 untouched, no table games.
   **The skip bar (`_zs<z>`): the narrower "attack when you can".**
   - **Where.** Branch claude/playout-pilot: tests first 094962a1, code f03780eb, results b704f32e. Read
     `rl/results/playout_attack_skip_2026-10-07/README.md`.
   - **The rule.** The larger lead applies only when the best move's own line (its play-outs) attacks this turn in fewer
     than half of its play-outs. Each candidate now reports that count.
   - **The 26 development-run cases.**
     - **The 9 true skips:** it keeps km3's attack at 7, Q12 included. One switch stands on a lead of 3.4 SE. The other
       is a Copycat after which km3 attacks in 16 of 16 play-outs; kx3's later End Turn in that same turn is among the
       7 kept.
     - **The 17 moves before an attack:** it touches none. Their lines attack this turn in 15 or 16 of 16 play-outs.
       `_za3` had stopped 14 of them.
   - **Gate 1:** suite 2,084/0; km3 240/240; self-checks unchanged, `_zs3` included.
   - **Gate 2:** the bar can't act at the 20 positions.
   **Close calls (`_m<R_max>`): more play-outs where the best moves are within the noise.**
   - **Where.** Tests first eea12479, code 22958cd1, head 7d3639d0. Read
     `rl/results/playout_close_calls_2026-10-07/README.md`.
   - **The rule.** After R rounds, the best candidate, every other within z SE of it, and km3's move play blocks of 16
     more rounds on the same worlds, until the call is clear or R_max. The trace gives each candidate's rounds.
   - **The gate positions** (8 continuation and 12 development, the latter also at their Tool placement; 2 seeds each;
     64 decisions):
     - 38 are close calls, and 8 choices change against R = 16. 7 of those are switches R = 16 had left within the
       noise.
     - **The time cost is x2.36** (1,271 s to 2,994 s; median 14.5 s to 32.2 s per decision).
     - 87% of the extra time is spent on close calls involving km3's move.
   - **Quiz 4's 12 positions** (the game's own randomness): 4 choices change, at x2.1 the time.
     - Q11 moves to Turbo Shark and Q07 to the retreat into Stoutland: Dustin's first moves, though narrowly.
     - Q04 moves to End Turn and Q10 to a retreat.
   - **Gate 1:** suite 2,087/0; km3 240/240; self-checks unchanged with the parameter off. `_m20` on gives
     d0c281641a7db61f.
   **Quiz 4's three items (Oct 6) are done, as below.**
   **Quiz 4's items: each its own parameter, off by default; gates 1 and 2 passed; km3 untouched; no table games.**
   - **Where.** Branch claude/playout-pilot, head 683e7df2 (code unchanged since gate 1's 25522e5a). Read
     `rl/results/playout_quiz4_items_2026-10-06/README.md`.
     - Code: attack bar tests 2ea4754d, code 8d16d49f; no-effect reader tests 3c8e4626, code d0423aae (five Supporters:
       ab9233b0, 7c5cde73); "neither" tests 0209c17b, code d77be090.
   - **1. "Attack when you can" (`_za<z>`): built, but as asked it also stops good moves.**
     - In the development run, kx3 left km3's attack at 26 of 1,902 decisions (1.4%). `_za3` keeps the attack at 22,
       including Q12 (Dustin's "Not sure why you wouldn't attack"). That was checked by deciding again with the bar on.
     - **The catch:** only 9 of the 26 skipped the attack that turn. 17 played Misty, Copycat, a Stadium or a retreat
       first and attacked later in the turn, and the bar stops 14 of those.
     - A narrower bar (only when the switch leaves the turn without an attack) isn't built: your call.
     - Q01, Q02, Q03 and Q08 are out of its reach: km3's first move there was a preparation step, not the attack.
   - **2. No-effect actions (`_noeffect`).** The reader works from the card database's texts, not a name list.
     - All 190 texts that can be a move are read: 122 have needs, 68 always do something.
     - Both bots spend about 1 in 6 card-text moves on something that can do nothing now: km3 970 of 5,835, kx3 1,004
       of 5,952. The panel decks are at 1.3%.
       - Watch Over at full HP: 682 and 717.
       - Fragrant Forest with no Basic Grass: every use, 125 and 119.
       - Elegant Cape with no Stage 1: 61 and 62.
     - Gate 2: km3's move does something at all 20 positions, so the rule never acts there.
     - **kx3's 1,004 such plays, decided again with the rule on** (all 560 games replayed exactly):
       - the tie-break plays another move at 979;
       - km3's move is kept at 5, by a lead beyond the noise;
       - 20 were kx3's own switches past the bar, which the rule can't touch.
       - It's mostly a reordering of free moves: Watch Over is replaced by the turn's Energy 402 times, Fragrant
         Forest by End Turn 95 times.
       - What changes the game is a card kept in hand when the attack comes first: an Elegant Cape, a Poké Ball or a
         Heavy Helmet.
       - In the play-outs it's neutral (-0.003 on average). Whether it helps strength would take a gate 3.
   - **3. The "neither" positions** (R = 128, LAB, Dustin's plans from his notes; the laptop hadn't added them).
     **His plan doesn't beat the move kx3 actually played at any of the three.**
     - Q06: 0 of 128, against 0.289 for kx3's move.
     - Q07: within noise of both bots (0.500; kx3 0.578, km3 0.477).
     - Q11: Turbo Shark with its Water to Lapras beats km3's bench-the-Vulpix line by +0.141 [+0.076, +0.205] (his
       Crystal Waltz reason), and ties kx3's retreat-and-Gnaw.
       - km3's own first move is the miss.
       - kx3 had the move as a candidate and, on 16 play-outs, chose an equal one.
   - **Gate 1** (25522e5a, items 2 and 3; 8d16d49f for item 1):
     - suite 2,080 passed, 0 failed;
     - km3 240 of 240 equal to the official program;
     - self-checks unchanged: km3 81b572198c04d5d1, LAB 3a2eb43bd9053639 with each new parameter off and on.
   **The Tool rule at kx3's own decision is built as a within-noise tie-break; gates 1 and 2 passed; gate 3 is
   re-registered for this version** (Fable via Dustin, Oct 6, amended the same day: no candidate drops).
   - **Where.** Branch claude/playout-pilot: tie-break tests first 8861c875, the tie-break dcd703d5, head 11b4836a. The
     candidate filter (c775972d) was built, never run, and replaced. Read
     `rl/results/playout_tool_rule_2026-10-06/README.md`, "The tie-break at kx3's own decision".
   - **What it does.** Every placement stays in kx3's pool and gets its play-outs.
     - Only when no move clears the z bar, and km3's proposed placement has no printed effect now while another has
       one, kx3 plays the placement with an effect that km3 prefers (the play-out rule's choice, same randomness).
     - The trace says "tie-break: Tool effect". km3's placement is kept when its play-outs lead that one by more than 2
       standard errors.
     - The play-out rule is unchanged. `_tools` means both.
   - **Gate 1: passed.**
     - km3 240 of 240 equal to the official program.
     - Suite 2,066 passed, 0 failed; 2,067 with the kept-case test.
     - km3 self-check 81b572198c04d5d1; LAB self-check 3a2eb43bd9053639 with `_tools` off (twice) and on.
   - **kx3's 62 development-run misplacements, decided again** (each game replayed exactly; a fresh kx3 from the game's
     own observation and search randomness).
     - With `_tools` off it repeats the logged placement 62 of 62 (131 of 131 placements without effect).
     - With `_tools`, **60 now land where the Tool has an effect**, all by the tie-break: Poncho 45/45, Heavy Helmet
       14/14, Rocky Helmet 1/2.
     - **2 stay by a play-out lead.** km3 had proposed the Active; kx3's play-outs moved the Tool to the Bench by
       2.2 and 3.0 standard errors.
     - The play-out rule alone moves none. The 69 placements with no spot that helps are unchanged.
   - **Gate 2: it doesn't hurt** (LAB, 64 rounds).
     - The 8 continuation positions aren't placements: unchanged.
     - At the 12 development positions advanced to the placement: the tie-break applies at 9, and the play-outs are
       already right at 2.
     - **The kept case** is dev04: deck 05's Poncho on the Active Indeedee ex leads every Bench spot by +0.0625 (2.05
       SE) and stays. It is now a test.
     - On − off is within the noise at all 12.
   - **Gate 3 (registered, not run; `gate3/config.json`, pushed).**
     - This version, decks 01, 10, 06, 05 and 03, on the development run's own deals: 400 kx3 games, about 15 hours.
     - The laptop's build must print self-check **c426e4c860e836ed** for `kx3_r16_c12_z2_real_t0_poolmeta_tools` (2 h 11
       min in the cloud), and km3 81b572198c04d5d1.
     - The steps (one `--only-deck` per deck) are in the README.
   **The Tool-placement rule, before it, is built; gates 1 and 2 passed** (Fable via Dustin, Oct 5).
   - **Where.** Branch claude/playout-pilot: tests first 7607ef7f, the rule 4021a4e8, gate 1 and the development run's
     Tool placements 14773e51, gates 2 and 3 24682db9, head 9c33a685. Read `rl/results/playout_tool_rule_2026-10-06/README.md`.
   - **The rule.**
     - In the play-outs only (both sides), a Tool goes only where its printed effect can apply. km3 chooses first; if its
       choice has no effect and another placement has one, it chooses again among those.
     - Where no placement has an effect, km3's choice stands.
     - It reads each Tool's text from the card database (spot, stage, type, Ancient/Future/Ultra Beast, printed Retreat
       Cost). All 26 distinct Tool texts read cleanly.
     - Off by default; `_tools` turns it on. kx3's own move and km3 are untouched. New code only under
       `engine/src/players/` (`mod.rs` unchanged), its tests and examples.
   - **Gate 1 (identity): passed.**
     - km3 240 of 240 equal to the official program.
     - Suite 2,061 passed, 0 failed.
     - km3 self-check 81b572198c04d5d1.
     - The LAB self-check is the same 3a2eb43bd9053639 with the rule off and on (it never acts there).
   - **Gate 2 (rule on v off, paired, every candidate): it doesn't hurt.**
     - The 8 continuation positions: untouched. The rule acted in 4 of 9,472 play-outs and no score moved; the rule-off
       scores equal the continuation run's kx3 scores, 74 of 74.
     - 12 development positions (where km3 misplaced a Tool in the development run): on − off averages +0.008.
     - kx3's choice changed at 2. Deck 03 v t-altaria: "play Heavy Helmet" goes 0.48 → 0.80, because it now lands on
       Wailord instead of Indeedee ex, so kx3 keeps it. Deck 05: within the noise.
     - Watch: deck 05's Poncho scored slightly lower with the rule on at 4 of 6 positions, never higher (−0.02 on
       average, one beyond its interval). Perhaps a Poncho on the Active helps after a retreat; only deck 05 can show it.
   - **kx3's own placements (the question asked).** In the development run kx3 put a Tool where the rule would move it
     62 times in 506 (km3: 63 in 517), so the play-outs don't catch it.
     - By Tool: Poncho 45 (deck 05), Heavy Helmet 14 (01 and 03), Rocky Helmet 2, Poison Barb 1.
     - A play-out rule can't fix this, because kx3's own placement isn't in a play-out.
   - **Gate 3 (registered, not run): `gate3/config.json`.**
     - Decks 01, 10 and 06 on the development run's own deals, so its kx3 games are the rule-off arm.
     - This build replays them exactly (16 of 16 games, 8 kx3; every km3 game of four decks, 320).
     - Its self-check for the gate-3 pilot with the rule alone printed 31d638dbc818b0fa, the development run's own kx3
       digest. Gate 3 now tests the rule with the tie-break (above), whose digest is c426e4c860e836ed.
     - 240 kx3 games: about 9 hours on the laptop's 2 threads, resumable.
     - The fixed reading is `gate3/pair_with_dev.py`. The laptop's steps are in the README.
     - Note: 10 and 06 meet the rule mostly through the opponent's Tools (km3 misplaces one in 6 and 11 of their 80
       games). Deck 05 (50 of 80) and deck 03 can be added to the same run with one `--only-deck` each.
   **The Trainer-habit diagnosis, before it, is done** (Fable via Dustin, Oct 5: km3's late Trainer play inside the play-outs).
   - **Where.** Branch claude/playout-pilot: 1185c4db, head 530be45e. Read
     `rl/results/playout_trainer_habits_2026-10-05/README.md`.
   - **Changes.** No table games, no engine change. One read-only instrument, `engine/examples/trainer_habits.rs`.
   - **The data.**
     - The development run kept no KX_TRACE, so its 560 km3 games (km3 on both sides) were replayed as the harness built
       them: all 560 exactly.
     - The continuation study's 2,048 km3 play-outs at the 8 positions: all end in the study's digest.
     - The cost of each habit was measured by withholding it from draft A's side, using the accepted plan continuation's
       `avoid` rule on the study's worlds.
   - **(1) Copycat** is played 1.8 times a game. The hold rule (>= 2 playable) holds 38% in km3's own games and 39% in
     the play-outs.
     - On average it improves the hand (2.6 cards out, 3.4 in).
     - Withholding it: +0.19 at position 4, +0.06 at 8 (within noise), −0.12 and −0.18 at positions 1 and 2.
     - The hold rule points the wrong way here: it holds 35% at position 2 and 3% at position 8.
   - **(2) Tools.**
     - On a Pokémon that never attacks, with time to: 5%.
     - But Protective Poncho went on the Active 100 of 100 times (it protects only on the Bench).
     - Elegant Cape went on a non-Stage-1 Pokémon 62 of 108 times.
     - Withholding the Cape: +0.17 at position 6, −0.07 and −0.11 at position 7.
   - **(3) Heal Supporters:** not a habit. They heal 20 or less 0–11% of the time, always the card's maximum, and
     withholding Irida only costs (up to −0.41).
   - **kx3 doesn't change these at its own decisions:** Copycat 0.91 a game for kx3 and km3 alike.
   - **20 examples:** `examples.md`.
   - **The proposal (not built).** In the play-outs only, Copycat is held:
     - unless it draws at least 2 more cards than it shuffles away (the opponent's hand count is public); and
     - always when an evolution for a Pokémon in play would go back.
     - At the 8 positions it holds 7% and 24% where Copycat helps, and 83% and 100% where it hurts. In km3's own games
       it holds 74%: a big change.
     - Tested in three gated steps: identity tests; the 8 positions on the same worlds (about 12 minutes); then the
       development decks paired with kx3's own games (a first cut on decks 01, 10 and 06 is 240 games, about 18 hours on
       the laptop).
   **The continuation experiment, before it, is done** (Fable via Dustin, Oct 5: "does km3's continuation of the play-outs hide good
   first moves?").
   - **Where.** Branch claude/playout-pilot, nothing merged.
   - **Commits.** Main merged in first (a02f0f70). Tests first (e48fe5ee), the option and the plans (32ef0b98), the keep
     fix (7c3d62f6), run 2 (77b71d1b), head 01ce5826.
   - **Read** `rl/results/playout_continuation_2026-10-05/README.md`.
   - **What was built.**
     - `playout_plan.rs`: for the pilot's next K own turns, a scripted plan is played. Its steps are written by intent;
       km3 fills in what the plan doesn't name, within avoid and keep rules; then km3 takes over. The opponent is km3
       throughout.
     - `continuation_study`: runs on `evaluate`'s own sampled worlds and seeds.
     - Tests first: with K = 0 it is km3's play-outs, final state for final state, and the study's km3 numbers are kx3's
       own. 6 tests.
   - **What was run.** The laptop's 8 positions (CONTINUATION_POSITIONS.md, main 2c689e83), built by the position runner
     at seed 1. LAB (the computer deck), R = 128, seeds 24,200,001,000 + i.
   - **The answer: mostly no.** The plan's continuation overtakes kx3's move at 2 of 8 positions.
     - **Position 6 (B-210952-t16).** km3's later Elegant Cape on the Active Ninetales makes "bench the Vulpix" lose
       128 of 128. Without it, the move edges past Binding Snow, +0.020 [+0.003, +0.036]: real, tiny, in a lost game.
     - **Position 1 (B-214254-t06).** The Water leads only inside the plan, +0.055. The plan's whole line is weaker than
       km3's own from either first move (0.70 and 0.64 v 0.77 and 0.78).
     - **Positions 2 and 4:** the same game in another order.
     - **Position 3:** won either way.
     - **Position 5:** the plan's move is worse either way, −0.24.
     - **Position 7:** kx3's Misty is right (+0.297 under km3). The plan's turn 20 lock loses every play-out where km3
       instead switches to a Mega for Turbo Shark.
     - **Position 8:** the plan's move leads either way (+0.062 under km3), too small for 16 play-outs.
   - **The pattern.**
     - The plan beat km3's own continuation where it withheld a Trainer km3 plays later: Copycat at 4 and 8, Elegant
       Cape at 6 (+0.19, +0.08, +0.13).
     - It lost where it held an Active or attack that km3 changes: positions 1, 2 and 7.
     - kx3 at 128 play-outs picks End Turn at position 8, a turn without Copycat.
   - **Item 4 is not triggered,** so no policy change is proposed. The evidence argues against a "stick to the intention"
     rule; it points, if anywhere, at km3's late Trainer play (a separate check, not run).
   - **Run 1 and run 2.** Run 1 scripted "keep the Active" unconditionally, which at position 2's turn 14 blocked km3's
     own route to the lock. Every keep rule now names its Pokémon, and all 8 were rerun. Only position 2 changed (the
     plan −0.31 → −0.05); the rest were identical round for round. Both runs are kept.
   - **Checks on 7c3d62f6.**
     - km3's 240 step-10 games are equal to the official program field for field (9dde28db2de6c9bc), and to the pinned
       record.
     - Self-checks: 81b572198c04d5d1, and the pilot's LAB 3a2eb43bd9053639 twice (kx3 unchanged).
     - Suite: 2,053 passed, 0 failed. `mod.rs` untouched.
   **Unfamiliar opponents (round 4), before it** (Fable via Dustin, Oct 4, the coordinator's "round 3"; branch claude/playout-pilot, on top, d513e37b kept: main merged in first 2654a488 (rl/ and decks/ only), tests first c6f32640, the fix 0d1c6d57 and 63cbe91f, the smoke 38c8d7b8, head eefa24d0; README section "Round 4"):
   - **(1) The pool**, a parameter: `_poolwide` (the default) holds 35 lists, the 8 meta lists plus the gauntlet's 14, the 2 panel-ladder lists, the computer deck, the 4 Sept 23 variants and the 6 B2e held-out lists, each embedded with its sha256 (`pool/generate_pool.py`, `pool/pool_manifest.tsv`); `_poolmeta` is the 8 of Oct 2, byte-identical. decks/dustin and decks/brews (drafts included) excluded by path and content. **Finding:** the panel's t-blaziken (and research/blaziken) is card for card Dustin's 06-mega-blaziken-tournament-list, the public list he owns; kept in the meta pool as since Oct 2 (dropping it would break LAB v the panel's Blaziken), recorded in the manifest.
   - **(2) Archetype inference** replaces round 3's placeholders when no pooled list is consistent: the 3 most similar zone-covering lists (seen cards by name, zone types), one drawn per play-out as the base weighted by similarity; the seen cards kept, then **the seen Pokémon's own evolution lines from the card database** (beyond the letter of the instruction: without them the inferred opponent evolved 2 times in 12 play-outs against its real list's 10), then the base's cards (Trainers dropped first); the zone's Energy; trace "inferred from N lists: <base>".
   - **(3) The rate test:** t-suicune v t-blaziken, 12 worlds, the opponent's attacks / evolutions in km3 play-outs: pooled 25 / 10, inferred 31 / 28, round 3's filler 36 / 0 (attacks don't separate them; evolutions do). The no-leak tests pass. 30 pilot tests.
   - **(4) The smoke:** kx3 on draft A v km3 on Dustin's deck 01 (in no pool), 10 deals × 2 seats: 99.5% of 11,840 rounds inferred, all "inferred from 3 lists", bases the Darkness lists (t-hydreigon 36%, t-weezing 25%, v-weezing_2 21%, v-weezing_swap1 19%); pilot 0.900, km3 0.750, +0.150 ± 0.214 (no evidence at 20 games); 19.4 s a decision (median 13.9, max 109), 719 s a game on 4 threads, about 3½ times the first smoke (longer games, 7.0 candidates a decision).
   - **Checks on 38c8d7b8:** km3's 240 step-10 games equal to the official program field for field and to the pinned record; self-check 81b572198c04d5d1; the pilot's LAB self-check unchanged; suite 2,047 passed, 0 failed. `mod.rs` untouched.
   **The fix for Astra's review, before it** (Fable via Dustin, Oct 3, the coordinator's "fix round 2"; numbered round 3 on the branch because the laptop's round 2, b96296a5, came first; same branch, on top: c6af74fd failing tests, e02c9d65 the fix, head 62e8dc81; README section "Fixes, round 3"). The laptop's development run on the registered d513e37b build is untouched.
   - **The case:** Swablu seen with a Water Energy Zone was modelled as t-altaria (Psychic), and the play-outs rolled Psychic Energy for a Water opponent (the failing test reproduced it: "t-altaria (closest, 1 of 1 tied; no list consistent)").
   - **The fix:** REALISTIC filters the pool first by the zone's visible types (a list whose Energy types don't cover them is inconsistent), then by the seen cards; a remaining list is drawn as before. With none, no list is borrowed: the opponent's hidden hand and deck are filler (unknown cards, drawn but never played; no named card), the Energy is the zone's types (the seen Pokémon's types if it shows none), and the trace says "no consistent list (filler; Energy [...])". A setup decision against an opponent still to set up from filler keeps km's move. There is no "closest" any more.
   - **What it changes:** nothing against pool lists (the strength harness's panel). Against an unfamiliar opponent (the position runner's ladder opponents unless given by KX_EXTRA_LISTS) the play-outs now model a passive opponent with dead draws: too weak, so optimistic. README "What to expect to go wrong" says so.
   - **Checks on e02c9d65:** km3's 240 step-10 games equal to the official program field for field (9dde28db2de6c9bc) and to the pinned record; the pinned self-check 81b572198c04d5d1; the pilot's LAB self-check unchanged (3a2eb43bd9053639, twice); full suite 2,044 passed, 0 failed. `mod.rs` untouched.
   **The play-out pilot's fixes, round 2, before it** (laptop Opus via Dustin, Oct 3, on d513e37b; same branch, head b96296a5; README section "Fixes, round 2"):
   - (1) `KX_EXTRA_LISTS` refuses paths under decks/dustin as well as decks/brews, and any list whose card-id multiset matches a .txt under the repository's decks/brews/** or decks/dustin/, wherever the copy lives (the position runner's decks/ folder holds copies of brew-08, draft A and deck 03). The repository is `KX_REPO` if set, else the first folder holding both above the build's engine directory, the working directory or a list; refused with the reason if none or unreadable. Both harnesses build from a copy of engine/ outside the repository, so **run run_pilot.sh from inside the repository or set KX_REPO**. Each extra list records `checked_against` in KX_PARAMS and every KX_TRACE.
   - (2) The time-budget test runs in a 2-thread pool: 2 rounds at every position on any machine, km's move kept, and the "fewer than the 8" reason asserted where a rival leads (a middle-game position, +0.5; on the immediate-win board km3 takes the win itself).
   - (3) The list-free test with lists of different lengths and rounds > 0; a canonicalize refusal test; test pilots built without the environment's lists; a panicking ranking world named once (`cap_note`); the opponent's list kept in the pilot only for LAB.
   - **Checks on 8205ba8b:** km3's 240 step-10 games equal to the official program field for field (digest 9dde28db2de6c9bc) and to the pinned record; the pinned self-check 81b572198c04d5d1; the pilot's LAB self-check unchanged (3a2eb43bd9053639, twice); full suite 2,042 passed, 0 failed (+3 tests). `mod.rs` untouched.
   **Round 1 before it** (on the review of f1aacbe2; head then d513e37b):
   - (1) REALISTIC respects the opponent's Energy Zone (a list is consistent only if its Energy types include the zone's; closest by missing seen cards, then missing zone types). (2) The cap's ranking runs inside catch_unwind; a panic there is a named drop. (3) The pool is deduplicated at load (8 lists; research/X = t-X), the closest tie is broken at random with the world's own rng, and REALISTIC reads the constant 20, not the real list's length. (4) `KX_EXTRA_LISTS="name=path;..."` (read once per process; a path under decks/brews refused, also with backslashes, any case or once resolved; each extra recorded with an FNV-1a hash of its file in KX_PARAMS, every KX_TRACE and the label; no new crate); LAB and REALISTIC share one multiset-aware printing swap; known deck-top cards count as seen. (5) Tests for each README claim: REALISTIC list-free, LAB exact on a pool pairing, LAB off-pool = REALISTIC exactly, a foreign hidden card through Game, the LAB no-leak swap on a pool pairing, the brews refusal, the extra list (its own test binary), plus 5 unit tests. (6) With `_t`, no switch before 8 rounds; `decide_omniscient` counted and traced.
   - **Checks on the final code:** km3 v km3, step 10's 240 games, equal to the official program in every per-game field (240 of 240, digest 9dde28db2de6c9bc) and to the pinned record; the strength harness built from the branch prints the pinned self-check 81b572198c04d5d1; the pilot's own LAB self-check is unchanged (3a2eb43bd9053639, twice); full suite 2,039 passed, 0 failed (2,025 + 14 new). `mod.rs` untouched (12 lines, Windows line endings); nothing else in engine/ outside players/, its tests and the example. No new smoke, as asked.
   **The play-out chooser, the first prototype, was done before it** (Fable via Dustin, Oct 2; branch `claude/playout-pilot`, cut from main 551a348, head f1aacbe2, not merged; `rl/results/playout_pilot_2026-10-02/README.md`):
   - **What it is.** `kx<N>`, for example `kx3`, a new player on km<N>. At each decision with real alternatives it takes every distinct legal move (cap 12; drops named), plays each out to the end R = 16 times with km<N> on both sides from worlds sampled from its own observation only, with common random numbers (round j of every candidate shares the world and seed), and switches from km<N>'s move only if the best move's paired lead exceeds z = 2 standard errors. Parameters in the code: `kx<depth>[_r<R>][_c<cap>][_z<z>][_lab|_real][_t<s>][_trace]`, printed per game (`KX_PARAMS`); per-decision trace (`KX_TRACE`). Knowledge: REALISTIC (default; the opponent's list drawn per play-out from the 16 lists of decks/screen/opponents and decks/research consistent with the cards seen) or LAB (the exact list, labelled a laboratory condition, only when it is one of those meta lists, so a brew's list is never handed over).
   - **km3 and the official engine unchanged.** The engine diff from main-8626a35 is 12 added lines in `players/mod.rs` plus the new files. `deckgym` built from the branch and the official program play km3's step-10 run (240 games, seed 7,100) equal in every per-game field, 240 of 240, and equal to the pinned record; the strength harness built from the branch prints the pinned km3 self-check digest 81b572198c04d5d1. Full suite on the final code: 2,025 passed, 0 failed.
   - **Tests first** (a3612b71, failing to compile), then the player: 7 tests pass, among them the no-leak test (same observation over a different opponent hand and both decks' order: same play-out scores and the same move, both modes, also through `Game`), km3's move kept within the noise, an immediate win taken, determinism.
   - **Both harnesses.** `strength selfcheck --pilot kx3_r2_c3_lab --games 2`: digest 3a2eb43bd9053639 three times (two builds); `run_pilot.sh` through a kx-aware pg_pos (pgd_build.sh with PGD_ENGINE = the branch's engine): one position, two seeds, 33 s, traces written. The pilot silences PG_DUMP during its own decisions, so the runner has no root-score tables for kx.
   - **The smoke** (venusaur-exeggutor v weezing-arbok, 20 deals, both seats, 40 games, seeds 24,200,000,000 + i, registered in START_HERE): pilot 0.875, km3 on the same deals 0.850, paired difference +0.025 ± 0.111 (no evidence either way). 31 of 1,097 decisions with play-outs changed from km3's move (2.8%). Time on 4 threads: 7.4 s per decision (median 6.2, max 32), 204 s per game. The container restarted after 19 games; the run resumed (`--resume`), and two first-run games replayed afterwards equal in every field and every traced decision.
   - **What to expect to go wrong** (README): km3 plays the later turns of every play-out, so coordinated plans can be undervalued (and km3's weaknesses get exploited, which the trace can't tell from real gains); at R = 16 only large leads switch, and some switches are luck; it is several hundred times slower than km3. **And one weakness found by the smoke:** against a list not in the pool, no list is consistent once a foreign card is seen, the "closest" ties, and the tie goes to the pool's first list, t-altaria (85% of the smoke's rounds). The strength harness never hits it (its panel lists are all in the pool); the position runner hits it at every position. Not repaired here, so the smoke describes the code as it stands; see question (b) below.
   - **Laptop time** (from the smoke): about 204 × 4 / T seconds per pilot game on T threads; a development comparison of one deck × 8 panel lists × 25 deals × 2 seats is about 23 hours on 4 threads, 6 on 16; the pre-registration's kx self-check about 1½ hours on 4 threads (estimate); the position runner about 1½ hours on 4 threads.
   **The data pipeline stopped where it was** (branch `claude/planning-pilot-data`, head 22d56999; `rl/results/planning_pilot_data_2026-10-02/README.md`, "Where it stopped"): the first pass done (9,600 games, 467,146 rows; held-out log loss 0.525 against 0.631 for km's value alone; the Bench Energy feature's sign negative), the second pass cancelled; Dustin's 04, 08 and 11 are in its pool but in the locked final-exam list, so their rows must be dropped before development use.
   **Earlier jobs, done** (the readiness jobs, the card-text follow-up and step 8c read and accepted): the round-2 readiness jobs (57c65860, `rl/results/round2_readiness_2026-10-02/README.md`), the card-text follow-up (20e2651) and the card-text job, step 8c, step 8b's rows (3a107f4), F8, and the later round of coin-flip prevention (`claude/coin-prevention-round2`); details in their READMEs and the log below.
2. **What is running now, and when it ends.** Nothing.
3. **Files I expect to change.** None. The play-out job changed, on its branch only: `engine/src/players/mod.rs` (12 lines), new `engine/src/players/playout_player.rs`, `engine/src/players/playout_pool.rs`, `engine/tests/playout_pilot_test.rs`, `engine/examples/playout_smoke.rs`, `rl/results/playout_pilot_2026-10-02/`, and START_HERE's seed table (one row: 24,200,000,000-24,200,099,999).
4. **Waiting on the laptop or Sonnet.** The laptop: its examples run on d513e37b (not interrupted); a look at rounds 2 to 4 (head eefa24d0) when it suits.
5. **Open questions.**
   - (a) For Dustin, still open from before: remove the Pocket Shot List rows `chase-order-carefree-steps` and `carefree-steps-snipe`? Nothing is done until he answers.
   - (b) Answered by round 4: the pool is widened (35 lists) and unfamiliar opponents are inferred. Still open, for the coordinator or Dustin: add the scoreboard's Limitless lists to the wide pool?
   - (c) Answered by the laptop's round 2: decks/dustin is refused too, by path and by content.

## Log (one line per new job, added and pushed before it starts)

- 2026-09-30: km Altaria v Suicune diagnosis (the laptop's request via Dustin): 40 traced deals at B, no new table games.
- 2026-09-30: Victory Star / Confusion repair draft (Fable via Dustin): failing test, then the gated fix, then the unit suite; engine/src/actions/ two files plus rl/results/victory_star_repair_2026-09-30/. No games.
- 2026-09-30: coin-flip damage prevention repair draft (Fable via Dustin): Part 1, a read-only check of the seven helpers (HELPERS.md, committed first); Part 2, (a) partial cuts after Weakness and Bounded Field and (b) the coin on queued direct damage, failing fixtures first. engine/ plus rl/results/coin_prevention_repair_2026-09-30/. No table games.
- 2026-09-30: Chase Order follow-up to the coin-flip prevention draft (Fable via Dustin): failing tests first (no discard, discard, control), then the gated fix in apply_attack_action.rs and apply_action.rs, then the unit suite and the README. No table games.
- 2026-09-30: Sonnet's follow-ups S1-S4 (Fable via Dustin): with_heads_coin_cuts test and hardening, Wild Swing and Ability/Tool/Checkup pins, smoke rerun on e52a73b with a trace of 4 games. Scratch decks only, no table games.
- 2026-09-30: km3 unplayed-Trainer diagnosis (Fable via Dustin): Iris (deck 11) and Team Rocket's Goo-zooka (decks 14, 15) from the floor run; at most 40 replayed deals per card at the official engine; diagnosis only, no table games.
- 2026-09-30: build switch N1 as kn<N> (km + the opponent's Active Retreat Cost in the clock; Fable via Dustin): code, unit tests (kn3 with N1 off = km3 on 200 scratch deals), smoke on scratch decks with Goo-zooka and Peculiar Plaza, README. No registration text, no table games, no identity replay, no merge.
- 2026-09-30: carrier lists for the rules switch (Fable via Dustin; PLAN.md step 3): four development lists from the committed Limitless archive (Garchomp Meowth, Togekiss Meowth, Hisuian Goodra, Mega Houndoom ex Victini), card-checked, with provenance; rl/results/engine_switch_rules_2026-10/carriers/. No games beyond the legality scan, no engine change.
- 2026-09-30: N1 timing assessment (Fable via Dustin): rl/results/kn_build_2026-09-30/TIMING.md, why kn3 plays Goo-zooka on a tie, which simplification causes it, up to three list-free candidate rules with footprint, carrier and smoke, and a recommendation. No new build, no table games.
- 2026-09-30: build C2 (TIMING.md; Fable via Dustin): a benched threat pays its Active's missing retreat Energy in km's clock, both sides, N1 off, plus a one-sided diagnostic code; tests first (the retreat pin, 200 scratch deals with the term off = km3, the 10 judged turns), then the scratch smoke and README. players/ and tests only; no table games, no identity replay, no merge.
- 2026-10-01: F8 (Fable via Dustin): upstream 09e964f's hp_aura_promotion_test.rs ported as a scratch test under rl/results/engine_switch_rules_2026-10/f8/, run against d363ba8's engine; F8.md on fix 1. No engine change.
- 2026-10-01: coin-flip prevention, the later round (Fable via Dustin): the seven recorded sites, failing tests first, then the gated fix; on a new branch claude/coin-prevention-round2 cut from Sonnet's R (1abdbe8). Own-Bench form left open. No players/ change, no table games, no merge.
- 2026-10-01: coin-flip prevention, the later round's seventh site (Fable via Dustin): Mega Kangaskhan ex's second punch on claude/coin-prevention-round2, with engine/src/state/mod.rs's pending-hit check as the approved fifth file; tests first (the knockout-then-promotion case and the non-knockout case), then the fix, the full suite and the README. Then idle. Round 2 goes in the next switch, not the current one.
- 2026-10-01: PLAN.md step 8b's early-warning rows (Fable via Dustin): on a scratch build of R (f8cfa9c; engine = ab56bf4, fresh target dir), pairings 32-35 of the 23.1B block (fire_victini v psychic_confuse, fire_heatmor v meowth_carefree, t-vespiquen v meowth_carefree, l-sharpedo v meowth_carefree), 40 games each, km3 and k3, on the old engine (rl/engine-2026-09-30's source), the new, and the watch build; every changed game classified with tightened_rule.py; rows to rl/results/engine_switch_rules_2026-10/early_warning_8b/. Then idle.
- 2026-10-02: step 8c of the rules switch (Fable via Dustin, Oct 1 evening; first, before the card-text job): every changed game of step 8's hand-off (main 1ba07d9, handoff_8c.tsv: 3,750 changed deals, 306 with no reach counter, CONDITION 3 = 296) traced on old (rl/engine-2026-09-30's source) and new (R f8cfa9c) to the first differing tick, fingerprint-checked against the row, classified with tightened_rule.py, both probes on every lookahead-only game; output rl/results/engine_switch_rules_2026-10/trace_8c_cloud/, pushed as pairings finish. An unexplained game is a stop, written at the top of this file at once.
- 2026-10-02: card text is the rule (Dustin, Oct 1; Fable via Dustin) on claude/coin-prevention-round2, tests first, no table games, no players/ change: (1) Will with a Confused attacker and Victory Star, F4's test flipped to the card text failing first, then the fix; (2) TEXT_AUDIT.md (read-only, committed before any further code): every gated or 'unverified' case in rules/09, rules/04 and card_validation.rs's caveats, decided by text or not; (3) fix the text-decided cases that fit the five allowed files, ask here before a sixth; (4) Trap Territory counts twice with two in play (engine/src/hooks/retreat.rs, allowed for this fix only), failing test first. Full suite after the last engine commit; README updated.
- 2026-10-02: the card-text follow-up (Fable via Dustin, Oct 2; the answer to the sixth-file question: all yes) on claude/coin-prevention-round2, now stacked on the official engine (origin/main merged first: d1b986c; 9a5fb3d here), tests first, same limits, no further file without asking: (1) card_validation.rs: Victini's caveat text updated to what is implemented and what stays open; (2) trainer_coin_plan.rs: Luxury Coin only for coins from the player's own Trainer cards (active_stadium_owner in stadium_route); (3) move_generation_trainer.rs: a Fossil can't be played under an Item lock (its printed type is Item), plus a shot-list row for it as supporting proof, not a gate; (4) E1 Guts on the attacker's own Pokémon in an attack's outcome and E2 Perish Body on a plain queued hit at the Active, in the five files. Full suite after the last engine commit; README with reach per list under decks/ (which of Dustin's decks hold a Fossil or Luxury Coin); CLOUD_STATUS.md after. Then idle.
- 2026-10-02: round-2 readiness (Fable via Dustin, Oct 2; the follow-up 20e2651 accepted; Sonnet reviews the package, the laptop drafts the next switch's plan) on claude/coin-prevention-round2, origin/main 7c1b62f merged into both branches first, no table games, no players/ change: (1) the affected-deck inventory against current main: every list under decks/ (drafts_2026-10-01 included) and the carriers, per repaired mechanic, which lists hold the card and which table, screen (decks/screen/opponents) and floor pairings are EXPECTED to change; (2) instrument_scan.py exact counters (every firing tick, F5 as corrected Oct 1) for every round-2 and card-text mechanic, plus off-gate counters per rewritten site, each with a constructed-board probe; (3) coin_probe v2 (plies counted as the bots count them: free frames free, crossing the turn boundary) and tightened_rule.py (an extra offer tick whose exact counter fires there reads as on the board), validated on the Oct 1 hand-off (handoff_8c.tsv): the 5 promotion games and km3 4/106 found, the 2 pairing-31 games on the board, the other 3,805 verdicts unchanged. Not duplicating the laptop's draft-A comparison or Sonnet's review. CLOUD_STATUS.md after.
- 2026-10-02: the planning pilot's data pipeline (Fable via Dustin, Oct 2; the readiness jobs 57c6586 accepted; rules switch 2 parked; direction: a pilot built for playing strength on an experimental branch, the official engine rl/engine-2026-10-02 and km3 stay the reference) on a NEW branch claude/planning-pilot-data cut from main, no change to the official engine's behaviour: (1) a scratch example playing km3 self-play that writes one row per decision of each side's own turn (a feature vector from that side's view: value_functions.rs's km terms one by one, plus Bench Energy and missing Energy to the cheapest and priciest attack, the same for what it evolves into, whether the Active can attack this turn and next, the opponent's clock on the Active, points at risk, hand, deck, turn, went first; the final result and points; seed and tick); (2) a varied pool written down before any game (the 8 panel lists, at least three early-aggression and three slow-setup lists from decks/, both seats) and a held-out group named in a file; (3) a first dataset of about an hour on two cores, its summary statistics and throughput; (4) a baseline logistic regression of the win on the features with held-out games, as a sanity check only (no pilot change, no claim). README first, seeds outside START_HERE's ranges, CLOUD_STATUS.md after; the design note (planning_pilot_design_2026-10-02/DESIGN.md) read if it lands.
- 2026-10-02: the play-out chooser, the first prototype (Fable via Dustin, Oct 2; replaces the data pipeline as the priority: its work committed where it stopped; DESIGN.md f81cc964 and its addendum 551a348 read first) on a NEW branch claude/playout-pilot cut from main; the official engine's behaviour and km3 unchanged (km3 in the build reproduces the pinned self-check and games); new code only under engine/src/players/ plus tests and an example: a new player that at each of its own decisions with real alternatives plays every distinct legal first action (capped by a parameter, drops reported) out to the end R times with km3 on both sides from states sampled from what its side may observe (no leak; a test for it), common random numbers across candidates, km3's move kept within the paired noise; knowledge modes LAB (the opponent's exact list, labelled) and REALISTIC (lists sampled from candidates consistent with the cards seen); parameters printed per game, time per decision and per game; deterministic; a trace option. Tests first, then the code, the full suite, a smoke on scratch decks (20 deals, both seats); it runs through rl/strength/ and run_pilot.sh. No table games, no change to the pinned engine, no merge. README; CLOUD_STATUS.md after.
- 2026-10-03: the play-out pilot's fixes, round 1 (laptop Opus via Dustin, on claude/playout-pilot at f1aacbe2; the laptop built it beside the pinned engine: km3's 240 games field for field and the self-check 81b572198c04d5d1; one review: no leak, km3 and the engine untouched), on the same branch, engine/ outside src/players/ (and its tests and example) untouched, mod.rs's Windows line endings kept: (1) REALISTIC respects the opponent's visible Energy Zone (consistent only if the list's Energy types include it; closest by missing seen cards, then Energy mismatch); (2) the cap's ranking inside catch_unwind (a panic is a named drop); (3) the pool deduplicated by card multiset (8 lists), the closest tie broken at random with the world's own rng, REALISTIC reads no list length (20); (4) KX_EXTRA_LISTS (name=path;...; decks/brews refused; recorded with a content hash in KX_PARAMS, every KX_TRACE and the label), LAB with the multiset-aware printing swap shared with REALISTIC, known deck-top cards counted as seen; (5) tests: REALISTIC list-free, LAB exact on a pool pairing, LAB off-pool = REALISTIC, a foreign hidden card through Game, the extra lists and the brews refusal; (6) with _t no switch before 8 rounds; omniscient decisions named in the trace. Then the suite, the 240-game km3 replay and the self-check; README updated; no new smoke. CLOUD_STATUS.md after.
- 2026-10-03: the play-out pilot's fixes, round 2 (laptop Opus via Dustin, on claude/playout-pilot d513e37b), same branch and limits: (1) KX_EXTRA_LISTS refuses a list whose card-id multiset matches a .txt under the repository's decks/brews/** or decks/dustin/ (the repository found from the build's engine directory; a clear refusal if those folders can't be read), and paths under decks/dustin/ too; (2) the time-budget test runs in a 2-thread rayon pool on a position where a rival clearly leads, asserting fewer than 8 rounds and the reason unconditionally; (3) realistic_reads_no_opponent_list asserts rounds > 0 with lists of different lengths, a canonicalize refusal test, the test file's pilot() without the environment's extra lists, a panicking ranking world named once, and (optional) the opponent's list kept in Core only for LAB. Suite, km3 replay and self-check after; README; CLOUD_STATUS.md after.
- 2026-10-03: the play-out pilot's fix for Astra's review (Fable via Dustin, Oct 3; the coordinator's "fix round 2", written up as round 3 because the laptop's round 2, b96296a5, already sits on top of round 1's d513e37b) on claude/playout-pilot, on top: REALISTIC's fallback could model an unfamiliar opponent with contradictory Energy (Swablu seen with a Water zone chose t-altaria and sampled Psychic). The pool is filtered first by the visible Energy Zone types, then by the seen cards; with no list left, the unseen part is built from the seen cards' types only (filler, no named cards), labelled "no consistent list" in the trace. Failing test first (Swablu/Water), then the fix, the suite, a README note. The laptop's development run on the registered d513e37b build is not touched. CLOUD_STATUS.md after.
- 2026-10-04: the play-out pilot, unfamiliar opponents (Fable via Dustin, Oct 4; the Energy-types fix accepted; kx3's development run on d513e37b +16.6 over km3; the coordinator's "round 3", numbered round 4 on the branch) on claude/playout-pilot, on top (d513e37b kept): tests first; (1) the pool widened to every list under decks/ except Dustin's own and the drafts (research, screen/opponents, B2e held-out, gauntlet variants, the panel-ladder lists, the computer deck when supplied), each with its sha256, selectable by a parameter; (2) with no consistent list, the opponent's unseen part by archetype inference (the most similar pooled lists by shared cards and Energy types, filled weighted by similarity; trace "inferred from N lists") instead of placeholders; (3) a test that such an opponent attacks and evolves at rates comparable to a pooled list, and the no-leak test still passing; (4) a smoke: kx3 on draft A v one of Dustin's decks not in the pool, trace on, time per decision, the inference labels. README; CLOUD_STATUS.md after.
- 2026-10-06: the Tool-placement rule for the play-outs (Fable via Dustin, Oct 5; the Trainer-habit diagnosis 530be45e read and accepted; the Copycat hold rule parked, to be revisited with positions from setup decks): on claude/playout-pilot, play-outs only (km3 untouched as the reference), text-decided and constant-free: a Tool is attached only where its printed effect can apply (Protective Poncho never on the Active, Elegant Cape only on a Stage 1 Pokemon; generalised from each Tool's text via the card database, not a name list); where no legal placement has an effect, km3's choice stands. Gated: (1) identity tests (rule off = km3's play-outs exactly; the pilot's LAB self-check unchanged with the rule off); (2) the 8 continuation positions on the same worlds, rule on v off, paired; (3) only if (2) doesn't hurt, a first paired cut on development decks 01, 10 and 06 sized for the laptop (it runs after the exam; the cloud prepares the registration). Also: how often kx3 itself, at its own decisions, placed a Tool wrongly in the development run's games. README, suite.
- 2026-10-06: the Tool rule at kx3's own decision (Fable via Dustin, Oct 6; the Tool-placement rule 9c33a685 accepted through gate 2; gate 3 on the laptop after the exam, with decks 05 and 03 added by --only-deck; kx3's own placements as wrong as km3's, 62 of 506): on claude/playout-pilot, the same text-decided rule as a filter on kx3's candidate pool: when km3's proposed placement has no printed effect and another placement has one, the no-effect placements are dropped (the trace names each drop and why), so the play-outs compare only placements that can act; where no placement has an effect, nothing changes. `_tools` covers both the play-outs and the pool. Tests first (identity with the parameter off; the 62 misplacements of the development run re-decided with the filter on: how many now land right); gate 1 (km3 240/240; LAB self-check unchanged with the parameter off); gate 2 on the same 12 + 8 positions, paired; then gate3/config.json updated so gate 3 tests the filter and the play-out rule together, pushed before the laptop starts. README, suite; CLOUD_STATUS.md after.
- 2026-10-06: the Tool job amended (Fable via Dustin, Oct 6): do NOT drop candidates; a planning bot must keep legal preparation moves evaluable (Poncho on an Active that will retreat; a Tool placed ahead of an evolution). The candidate filter (c775972d, never used in a run) is replaced by a within-noise tie-break at kx3's own decision: every placement stays in the pool with its play-outs; only when no candidate clears the z bar, and km3's proposed placement has no printed effect now while another placement has one, the placement with an effect is chosen (trace: "tie-break: Tool effect"). The play-out rule stays as built. Tests: identity with _tools off; the 62 development misplacements re-decided (how many land right, how many stay by a play-out lead); a case where the no-effect placement wins its play-outs beyond noise and is kept. Gates 1 and 2 again; gate3/config.json for this version with decks 01, 10, 06, 05 and 03, pushed before the laptop starts tonight. README, suite; CLOUD_STATUS.md after.
- 2026-10-07: the skip bar and close calls combined (Fable via Dustin, Oct 7; _zs3 and _m<R_max> accepted on their own; the laptop's review of 7d3639d0: a gap in how they combine), on claude/playout-pilot, tests first, gates 1-2, km3 untouched: (a) closeness tested against the bar that will decide (z_skip for km3's attack when the best line skips the attack); (b) extended candidates run to R_max and the decision is made at the end, not at the first clear block; (c) optional: no extension for a candidate equal to km3's move in every round. Add a combination test for _tools _zs3 _m64; self-check digests for the exact combined code (REALISTIC/poolmeta/_tools, and _lab); the 26-case skip scan with the full combined code (kept / touched for the 9 true skips and the 17 attack-later moves); a note in the _m README that the _tools tie-break can play a placement the extension dropped. README, suite, push; CLOUD_STATUS.md after. The laptop registers the combined development run on the fixed head.
- 2026-10-07: two builds after quiz 4 (Fable via Dustin, Oct 7; the three items 683e7df2 read and accepted; _za as built NOT shipped, _noeffect stays a parameter, no gate 3 now), on claude/playout-pilot, tests first, gates 1-2, km3 untouched: (1) the narrower attack bar: the larger lead required only when switching away from km3's attack would leave this turn without an attack in the candidate's own line (its play-outs' first turn: did the pilot's side attack before End Turn?); re-run the 26 development-run cases, which of the 9 true skips it keeps and whether it touches the 17; (2) adaptive play-outs for close calls: when the best candidates are within the z bar after R rounds, continue in blocks of 16 up to R_max (a parameter, e.g. 64) for those candidates only, the same common random numbers extended, decide at the end, trace the rounds used; the time cost on the development positions and the 8 continuation positions, and how many decisions change against R = 16. README, suite, push each; CLOUD_STATUS.md after.
- 2026-10-06: three items from Dustin's quiz 4 notes (Fable via Dustin, Oct 6; the Tool tie-break 11b4836a accepted, gate 3 on the laptop; quiz 4 read: km3's plan 6, kx3's 2, neither 4, kx3's game won 9 of 12), on claude/playout-pilot, each its own parameter, tests first, gates 1-2 as before, no table games, km3 untouched: (1) "attack when you can": a stricter bar (a parameter, e.g. z_attack = 3) for switching away from km3's attack to a non-attack, every such switch in the trace with both scores; and how often kx3 switched away from an available attack in the development run's games and the quiz positions, and what those games did; (2) no-effect actions: the Tool tie-break generalised to any action whose printed effect cannot apply now (the set found from the card database's effect preconditions, not a name list), never a candidate drop, a within-noise tie-break toward the candidate that does something, else km3's move; how often each bot spends such an action in the development run; (3) the continuation experiment on the three "neither" positions (Q06, Q07, Q11): Dustin's plan v km3's continuation, R >= 128, the same method; per position whether his plan wins in the play-outs and, if so, why neither bot found it. README, suite, push each item; CLOUD_STATUS.md after.
- 2026-10-05: km3's late Trainer play inside the play-outs, a bounded diagnosis (Fable via Dustin, Oct 5; the continuation experiment 01ce5826 read and accepted, its no-rule conclusion right): on the 8 continuation positions' sampled worlds and the development run's traces (strength_2026-10-03_kx3_dev; no KX_TRACE kept there, so its km3 games, replayed): (1) Copycat: the hand it shuffles away (playable cards, Supporters, Energy-matching Pokemon) and what it draws into; how often a competent player would have held it (held when the hand has >= 2 cards playable this or next turn); (2) Tools (Elegant Cape, Giant Cape, Rocky Helmet, Poncho): on which Pokemon, whether it attacks or is knocked out within two turns, the share on a Pokemon that never attacks; (3) heal Supporters (Lady, Irida) played with little damage on the board. Rates for km3 in its own games and as the play-out policy, 20 hand-picked examples; then propose, not build, the smallest change to the play-out policy only (not km3) that removes the worst of it, with how to test it on the 8 positions and the development decks. No table games, no engine change.
- 2026-10-05: does km3's continuation hide good first moves? (Fable via Dustin, Oct 5; round 4 eefa24d0 accepted; kx3 d513e37b frozen as an experimental baseline after the k3 check, +15.2 (+10.8 to +19.6), its final exam on the laptop) on claude/playout-pilot, a new preset, nothing merged, km3 untouched: tests first (the continuation option reproduces km3's play-outs exactly at K = 0); (1) a plan continuation for the pilot's own side for K own turns (a per-position rule set: attach target, which Pokémon stays Active, when to promote, which attack), then km3; the opponent km3 throughout; the same sampled worlds and common random numbers; (2) per position, the paired play-out score of the plan's first move and of kx3's move under km3 continuation and under plan continuation, with intervals, R >= 32; (3) per position: spoiled by km3 later, or not better; with the trace lines; (4) if the plan continuation wins on most, propose (not build) the smallest general change to the play-out policy with its cost. Positions: the laptop's CONTINUATION_POSITIONS.md when it lands, until then BEFORE_AFTER.md's 'preparing an attacker' / 'managing a sacrifice' positions where kx3 did not choose the plan's first move. Suite; README; CLOUD_STATUS.md after.
