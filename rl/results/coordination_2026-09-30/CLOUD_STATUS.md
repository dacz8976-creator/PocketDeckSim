# Cloud Opus status (branch claude/pensive-ptolemy-spwc0b)

Written Sept 30 for the Fable coordinator session (Dustin's single delegator). Times are UTC.

## STOP (step 8c, Oct 2): 5 UNEXPLAINED games; a ruling is needed

Step 8c is done: all 3,813 changed games of the hand-off (main 1ba07d9) are traced, in `rl/results/engine_switch_rules_2026-10/trace_8c_cloud/` (README.md, by_hand.md).

| | count |
|---|---:|
| on the board | 2,414 |
| lookahead only, both halves | 1,391 |
| needs a judgment | 1 |
| **UNEXPLAINED** | **5** |
| LENGTH, explained by hand | 2 |

Every trace reproduces its row (3,813 of 3,813). PLAN.md: the 5 unexplained games stop the switch until they are resolved.
- **The 5, all the same shape:** an attack knocks out the Active, and the first difference is the Promote. R promotes a sniper; the old engine promotes another Pokémon.
  - step 8 km3, pairing 1 (garchomp_meowth v t-blaziken), deal 399, tick 81: Heatmor (Tongue Whip at two Benched Meowth);
  - step 8 k3, pairing 4 (garchomp_meowth v t-sceptile), deal 7, tick 95: Grovyle (Slicing Snipe at a Benched Meowth);
  - step 8 km3, pairing 4, deal 7, tick 84: Grovyle;
  - step 8 km3, pairing 4, deal 360, tick 57: Grovyle;
  - step 8 km3, pairing 21 (hisuian_goodra v t-suicune), deal 310, tick 87: Chien-Pao ex (Diving Icicles at Hisuian Goodra).
- **By hand:** `coin_probe.rs` stops at any state where the opponent is to move, so it never looks past the end of the opponent's turn. km3's and k3's own search does (`expectiminimax_player.rs` at R, 631-655: a forced EndTurn costs no ply, ahead of the cutoffs at 773 and 908). Their line is:
  - the Promote (ply 1);
  - the forced EndTurn (no ply);
  - the draw (ply 2);
  - the snipe (ply 3);
  - the queued coin-path choice, in a frame of only queued choices, priced at depth 0 (659-700).
  - So the repaired choice is inside their 3 plies.
- **A scratch variant of coin_probe** (`make_coin_probe_xturn.py`) resolves those forced continuations as the bots do. It is not the accepted probe and no verdict uses it.
  - It finds the gate in all 5 ("queued after 3, a pure frame").
  - It agrees with the accepted probe on 139 of 139 sampled lookahead games (same or smaller ply), and finds nothing at 12 controls.
- **Ruling needed (coordinator / Dustin):** may this reading, or the variant, count as the second half for these 5? Until then the stop stands.
- **The 2 LENGTH games** (km3 31/12, k3 31/81): R adds the Victory Star choice after a Confused Mega Houndoom ex's attack, and the old game ends there. The reach counters fired at that tick and at its cause, in the same turn: on the board, repair A, by hand.
- **The 1 needing a judgment** (km3 4/106, a CONDITION 3 game; `judgment.md`): `coin_probe` counts a one-choice evolution pick as a ply, so the queued choice reads "at the leaf". The bots don't count it, so by hand the choice is inside their search at ply 3.
- **CONDITION 3:** of step 8's 296, 295 are lookahead only with both halves and 1 needs a judgment (the game above). Each is listed with its probe in `condition3.tsv`.

## Question (the card-text job, Oct 2): files outside the five, and two cases outside the three sources (still open)

The audit is committed: `rl/results/coin_prevention_round2_2026-10-01/TEXT_AUDIT.md` (539594a, branch claude/coin-prevention-round2). The four text-decided cases that fit the five files and Trap Territory are now fixed (item 1 below). Nothing below is touched until you say:
- **A sixth file, `engine/src/card_validation.rs`:** Victini's caveat (96-98) still calls Confusion with Will and the block coin "unverified ... legacy". A text change only.
- **A sixth file, `engine/src/actions/trainer_coin_plan.rs`:** Luxury Coin ("coins for an effect of your Trainer cards") is offered on the opponent's Mesagoza or Arcade. The fix is a check of `active_stadium_owner` in `stadium_route` (95).
- **A sixth file, `engine/src/move_generation/move_generation_trainer.rs`:** a Fossil can be played under an Item lock (the Item check at 65 skips the Fossil type). Its premise is that a Fossil's printed type is Item (rules/01, rules/04 §6; the local database can't show it).
- **In the five files but outside rules/09, rules/04 and the caveats:** Guts on the attacker's own Pokémon in an attack's outcome (E1), and Perish Body on a plain queued hit at the Active (E2). Both are decided by their text. Fix them in this job, or leave them listed?

1. **Current task, and the instruction that set it.** None running. **The card-text job is done** (Fable via Dustin, Oct 1 evening; branch claude/coin-prevention-round2, head 94bd46e; `rl/results/coin_prevention_round2_2026-10-01/README.md`, "The card-text job"). Tests first for every fix; no table game; nothing in `players/`.
   - **Item 1, Will with a Confused attacker:** after a Confusion heads, Will makes the attack's first coin heads and Victory Star is still offered (210403). F4's guard test flipped to the card text (59c7c2a, failing first), the fix 27a0c37.
   - **Item 2, `TEXT_AUDIT.md`** (539594a, before any further code): decided by text and contradicted by the engine 9; decided and already followed 7; not decided by any text 17 (each a shot-list row with what to record); not rules questions 4.
   - **Item 3, the text-decided fixes in the five files** (tests 7e13132, all 7 failing first; fixes 46953bf): Victory Star with a block coin (the block coin first, never offered; the attack's own coins offered on its heads); Will with a block coin (Will makes it heads); the coin Abilities on the attacker's own Pokémon hit by its own attack, and on the opponent's Active in an own-Bench choice; a copied discard attack (Chase Order, Wild Swing through Ditto).
   - **Item 4, Trap Territory** (`hooks/retreat.rs`; tests 05eb849, failing at two Ariados; fix 5155ff7): each Ariados adds 1 (zero, one, two Ariados: Retreat Cost 1, 2, 3 more by retreat legality; Grass Knot 100, 130, 160).
   - **Full suite at 5155ff7: 2,035 passed, 0 failed, 0 ignored** (`suite_card_text.log`).
   - **Reach under `decks/`:** Trap Territory changes Dustin's deck 12 (2 Ariados); the Will fix changes brew-01, brew-04 and Dustin's 10 only when a Confused attacker attacks with coins after Will. No list holds Victini, a block-coin attacker, a coin Ability, an own-side attacker or Ditto.
   - **Waiting on you:** the question above (three sixth files; E1 and E2).
   - Main has since gained 669f7b3 ("8c: the five lookahead games and the judgment game explained ... confirmed by check (b)"), the laptop's; I have not read it against the STOP above.
   The jobs before it are done: step 8c (its result is the STOP above), and the Oct 1 jobs:
   - **PLAN step 8b's early-warning rows** (3a107f4, `rl/results/engine_switch_rules_2026-10/early_warning_8b/README.md`), on a scratch build of R (f8cfa9c, engine tree 38af8b0, the laptop's candidate's):
     - 960 games, pairings 32-35 × 40 × km3 and k3 × old, new and watch, every program built from `git archive` in a fresh target folder.
     - The checks:
       - watch = new 160/160 per bot;
       - the pinned old `legality_scan` = the old built from source, 160/160 per bot;
       - no rule findings;
       - the laptop's `sitting2_check.py touched` and `stepsum` pass both bots.
     - **63 of 320 deals change.** By `tightened_rule.py`:
       - 50 on the board;
       - 13 lookahead only, with both halves found by `coin_probe` or `vs_probe`;
       - 0 needing a judgment, 0 unexplained.
     - CONDITION 3: 1 game (km3 34/35). It is one of the 13 lookahead games, explained under the Oct 1 ruling.
     - Rows 13/22: pairing 35 met (15 games). Pairing 34 is NOT met: no unchanged game fired the off-gate discard counter. That is a report line, not a stop.
     - **The trace load:**
       - changed games with no exact counter: 13/320, about 1,050 for step 8 by the plan's arithmetic, all of them the automated check's;
       - needing a hand trace: 0 on this sample (by the rule of three, up to about 240);
       - which number goes on TRACE LOAD is the coordinator's call.
     - CLOUD8B lines, if wanted:
       - `CLOUD8B 3a107f4 km3 rl/results/engine_switch_rules_2026-10/early_warning_8b/8b_new_km3.jsonl`
       - `CLOUD8B 3a107f4 k3 rl/results/engine_switch_rules_2026-10/early_warning_8b/8b_new_k3.jsonl`
   - **Job 1, F8** (5a929c0): accepted. F8's wording goes into rules/09 and PLAN.md at the pin.
   - **Job 2, the later round of coin-flip prevention**, all seven sites, on `claude/coin-prevention-round2` (from Sonnet's R, 1abdbe8; README `rl/results/coin_prevention_round2_2026-10-01/README.md`, 78af4e8). The six sites were accepted (76b87cd). Round 2 stays out of the current switch and goes in the next one.
     - Mega Kangaskhan ex's second punch, after the fifth file was approved:
       - 9145eb3: the tests, the knockout-then-promotion case and the non-knockout case, both failing;
       - 29e126a: the fix;
       - bfe8aeb: the counters;
       - 78af4e8: the README.
     - `engine/src/state/mod.rs`: only the pending-hit check changed. It now also recognises an `ApplyQueuedAttackDamage` aimed at the empty Active, from the other player's frame.
       - The `ApplyDamage` arm's attacker clause is not mirrored. A Mega Kangaskhan ex Knocked Out on its own turn gives 3 points and ends the game (checked in a scratch copy), and mirroring it would have reordered the first round's choices.
     - Full suite at 29e126a: 2,027 passed, 0 failed (R's 2,018 plus the 9 new tests). The counter probe: 32 checks, 0 failures.
     - The scratch smoke, rerun on the final engine, gives byte-identical game files to its first run (80 of 80 for each scan).
2. **What is running now, and when it ends.** The card-text job, starting now.
3. **Files I expect to change.** None. The 8b rows are in `rl/results/engine_switch_rules_2026-10/early_warning_8b/` (this branch). The coin round-2 job changed these on its branch:
   - engine: `engine/src/actions/apply_attack_action.rs`, `engine/src/actions/apply_action.rs`, `engine/src/state/mod.rs` (the approved fifth file), `engine/tests/pokemon/meowth_carefree_steps_test.rs`;
   - results: `rl/results/coin_prevention_repair_2026-09-30/instrument_scan.py` (the counters) and `rl/results/coin_prevention_round2_2026-10-01/`.
4. **Waiting on the laptop or Sonnet.** Nothing.
5. **Open questions for Dustin.** None. The fifth-file question was answered yes (Oct 1), for the pending-hit check only.

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
