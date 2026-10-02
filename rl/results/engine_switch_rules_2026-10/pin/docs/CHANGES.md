# Step 13's documents for the rules switch's pin: what changed, and the source for each claim

Drafted Oct 1 (laptop session, a subagent; nothing committed, staged or played). Each file under `pin/docs/` is the full new content of the repository file at the same relative path. Every line not listed below is byte-identical to the working copy at main 26e2670 (all targets are LF, no BOM, ending in a newline, and equal to HEAD).

- **Placeholders:** `@@MERGE@@` is the pin's merge commit (full sha) and `@@MERGE_SHORT@@` its short form (`main-@@MERGE_SHORT@@` is the engine's name in the manifest). Replace both before committing.
- **`BASE.sha256`:** the sha256 of each existing target in the working copy when this was drafted; check with `sha256sum -c rl/results/engine_switch_rules_2026-10/pin/docs/BASE.sha256` from the repository root. `rl/engine-2026-10-02/README.md` is new: it is absent from the working copy, so it has no line there.
- **`DOCS.sha256`:** the sha256 of each drafted file (placeholders still in), paths relative to `pin/docs/`; check with `sha256sum -c DOCS.sha256` from `pin/docs/`. It doesn't cover this file or the two sha256 files.
- **Dates:** "Oct 1" for the pin follows the folder name `rl/engine-2026-10-02/` (Central time). If the pin lands after midnight Central, change "Pinned Oct 2" and "since Oct 2" to the real date.
- **Assumed at the pin:** that 8c passed on Dustin's five conditions and the coordinator audited it (his word, README "Dustin's word on game 28 and the pin"). The engine README and the switch README name `8c_RESULT.txt` with its counts (3,813 changed = 63 + 3,750, the pin's gate 3; 297 CONDITION 3 cases, Dustin's word); Sonnet's result commit is in that file and the manifest, not repeated here.
- **Review fixes, Oct 1** (the three reviews of the pin and its documents): "six other attacks" became "six other sites (seven attacks)"; item 2's open question is replaced by the plain reading; RUN5:338 names `floor_recheck_2026-10/`; `rules/05:84` and `rules/04:91` agree with WALLACE §6 and `09`:44-45; Fixed entry 2's "every other target" is narrowed to EQUIV row 20's test; the id-keyed backlog names `COIN_IDS`, `FINITE` and `FULL`; 09e964f's two fixes are attributed separately (fix 2: Dustin; fix 1: F8, with F8's two limits); RUN5's "Pinned Oct 2" gives the replays, not `players/`, as the reason; "Team Rocket's Moltres ex"; 4d026a5 is the line-ending fix. Each is noted at its file below.

Abbreviations for sources: **README** = `rl/results/engine_switch_rules_2026-10/README.md`; **PLAN** = that folder's `PLAN.md`; **PIN_STATUS**, **identity_check**, **touched_check**, **programs.sha256**, **candidate.txt** = that folder's files; **READOUT** = `rl/results/rules_recordings_2026-10-01/READOUT.md`; **WALLACE** = `rl/results/rules_recordings_2026-10-01/WALLACE_second_read_sonnet.md`; **HELPERS** = `rl/results/coin_prevention_repair_2026-09-30/HELPERS.md` at 5a18d31; **EQUIV** = `rl/results/engine_switch_rules_2026-10/EQUIVALENCE_sonnet.md` at 5a18d31; **F8** = `rl/results/engine_switch_rules_2026-10/f8/F8.md` at 5a929c0 (cloud branch only, not on main and not brought by the pin's merge); **ROUND2** = `rl/results/coin_prevention_round2_2026-10-01/README.md` at 78af4e8; **code@C** = the engine read with `git show 5a18d31:<path>` (C's `engine/` = R's tree 38af8b0 = the pin's).

---

## `rules/09_engine_repairs_2026-09-22.md` (2 lines changed, 43 added; the three entries at old lines 85-128 are untouched)

Layout: the three entries stay byte for byte where they were, but a new heading "## Fixed Oct 1 (...)" now sits above them, and each gets a "**Fixed in main-@@MERGE_SHORT@@ ...**" note, as the "Fixed Sept 26" section did. One new open entry goes between the 09e964f entry and that heading.

- **Line 78 (09e964f entry):** "Take them at the next upstream merge, with their tests" becomes "Neither is to be ported ...", with fix 2 attributed to Dustin (Sept 30) and fix 1 to F8 (nothing to port; F8 did not audit every path). Not taking fix 1 is an inference from F8, not a decision of Dustin's. Sources: F8 (fix 1 covered; its limits, lines 55-56: no general clean-up of stale `Promote` choices, not every path audited); README "Dustin's decisions" item 10 and "F8 is done" (fix 2 not taken; line 80 changes to covered); PLAN question 10.
- **Line 80:** "Whether it covers this case is unchecked" becomes "Covered in the fork (F8, Oct 1)". The waves at `apply_action_helpers.rs:690-820`, the nested pass at `:836-847`, promotion at `:906`, "either guard alone covers it", the prune "is not what covers it", and "fix 1 ported as written would do nothing" all come from F8's "In plain words" and its suggested wording.
- **New sub-bullet under fix 2, "Not taken":** README item 10 / PLAN question 10 (`06_sources.md:124`, `rules_repair_retaliation_timing.rs:136`); "Lethal Knock Back finishes its switch" is rules/09 line 54.
- **New open entry, "What the Oct 1 rules switch left open"** (the task's ONE open entry, worded as plain-text bugs for the next switch):
  - Dustin's rule, quoted: README "His rule on card text"; RUN5 437-441.
  - Item 1, the attacks that still skip the coin. Ability text: `lib/card.py` (Meowth B2 124 Carefree Steps), and old line 97. Wild Swing: READOUT §2.3 and §3b-3 (213822 150-154, "Coin still applies. It is an attack"); `discard_then_damage_choice` at :311 and `chase_order_attack` at :329 (code@C); the pin test at `meowth_carefree_steps_test.rs:390` (code@C, git grep). The six other attacks, with names and functions: HELPERS, "Found outside the seven" (function names checked at code@C). The own-Bench form, its cards and the Guts reason: HELPERS, the `also_choice_bench_damage` row and "Not changed, though it skips". The copied Chase Order: PLAN "Known limits" and code@C `chase_order_attack`. The round-2 branch (76b87cd, then 78af4e8, suite 2,027, "No independent audit", own-Bench left open): ROUND2 and its commit log; README "The cloud's later-round coin fixes". "Only Gyarados is in a list": ROUND2 "Reach per card" plus HELPERS (own-Bench form: none). "Six other sites, seven attacks": HELPERS' table has six functions, and Double Splash and Triple Bombardment share `conditional_bench_damage_attack`; PLAN "Known limits" and ROUND2 say "six other sites".
  - Item 2, CoinFlipToBlockAttack. The gate: code@C `apply_attack_action.rs:117-132` and `apply_action.rs:185-216`. The block text: code@C `effect_mechanic_map.rs:1243-1250`. Victory Star's text: `lib/card.py "B3 025"`. "Until seen in the game": README, last paragraph of "Dustin's word". The reading (the block coin, like the Confusion coin, is not one of the attack's own coins; Victory Star is offered on the attack's own coins if it goes ahead) is the plain reading by `04` §9's Confusion rule; READOUT §4 ("the next switch follows the plain reading with no footage needed") and README leave no question open.
  - Item 3, a pending Will: READOUT §2.2 and §3b-1 (210403 T14, 354-355; the carve-out at :131; the test at `b4a_attack_batch2_test.rs:437`; `card_validation.rs:97`), checked at code@C.
  - Item 4, Will wasted: READOUT §2.2 and §3b-2 (342.0-342.75, 347.25-347.95, 352; `attack_outcome.rs:590-604`; `outcomes.rs:489-491`; `apply_action.rs:675-688`, each checked at code@C). Will's text: `lib/card.py "Will"`. Dustin's capture quote: READOUT §2.2. The fix shape ("forces the attack's first coin; the reroll stays a fresh flip") is READOUT §4, open case 1.
  - Item 5, two Ariados: READOUT §3b-4 (213034 T5 117-124; 160 = 40 + 30 × (2 + 1 + 1); `hooks/retreat.rs:251-262`, break at 260, checked at code@C; deck 12). Trap Territory's text: `lib/card.py "Ariados"`. The card is Team Rocket's Moltres ex (READOUT's "130-HP Moltres ex"; plain Moltres ex has 140 HP); its printed Retreat Cost 2: `lib/card.py "Team Rocket's Moltres ex"`. Stacking: rules/04:61.
- **"Fixed Oct 1" heading and three notes:**
  - Entry 1 (the cut's order). Commits: PLAN "What the switch is" (B: 5942d1a the fix). The step-4 placement: EQUIV row 7 and PLAN repair B's "The rule". The example's 120 − 100 = 20 is the old entry's own arithmetic. kd's follow-on F1 is 160a9d4 (git log of R), and the test name `guarded_grill_under_bounded_field_comes_off_after_weakness` is at code@C `hooks/core.rs:3191`.
  - Entry 2 (the queued choices). **The count:** EQUIV §2 rows 14-20 give seven helper functions plus Chase Order's two branches (rows 13 and 18). HELPERS' "Changed" list gives six, because it counts `direct_damage` and `direct_damage_and_self_card_effect` together as the `DirectDamage` group. So the note names all seven and says why Part 1 said six. The "queued as the attack's own damage" mechanism: EQUIV rows 12-13 and code@C `queued_attack_damage_choice` :281. kd's test name: code@C `hooks/core.rs:3224`. "Ability, Tool and Checkup damage still never flip": HELPERS ("The rest are left as they are") and EQUIV (only attack helpers rewritten). "With no coin-Ability Pokémon among the possible targets, the choice is queued exactly as before": EQUIV rows 12-20 (row 20: for `switch_in_opponent_benched_then_damage` the test is whether any Benched candidate has a coin Ability, so a non-coin Pokémon switched in can still take the coin path).
  - Entry 3 (Victory Star). Commits: PLAN "What the switch is" (A); `git log -1 4d026a5` is "Restore Windows line endings in b4a_attack_batch2_test.rs", so it is named as the line-ending fix, not a test. The rule: PLAN repair A's "The rule" and code@C :117. The third sighting, 204634 T4 184-205: READOUT §1 and §2.4. F2 is d479f01 (git log of R).

## `rules/04_actions_cards_effects.md` (3 lines changed, 3 added)

- **Line 61 (passive same-name Abilities stack):** adds the two-Ariados case, labelled as arithmetic, with a ⚠ pointing to `09`. Source: READOUT §4 "rules/04 line 61" and §3b-4; WALLACE §7 point 4 agrees with the label.
- **Line 91 (the whole stale ⚠ paragraph):** replaced by the "Engine ✓ since rules1" line. "Blocked only by an empty deck or a missing visible prerequisite (a hand card, a board target)": rules/09:44-45 ("Visible prerequisites such as a hand card or board target still apply"). Sources: WALLACE §5 (Wallace), §6 (Gladion, Team Galactic Grunt, Clemont, Serena, Juliana, Cabbie, Arven and Traveling Merchant are `can_search_nonempty_deck`; Pokémon Communication; the one-line wording; the caution on the Tool-searching Ability check); rules/09:44-45 (the rules1 repair the line cites).
- **§9, new line after 144 (a Victory Star replacement is a fresh flip; Will doesn't apply to it):** READOUT §4, with Sonnet's weaker wording from WALLACE §7 point 2. "Engine ✓": READOUT §2.2 ("Will and a reroll, no Confusion: matches").
- **§9, line 145:** adds 204634 T4 as a third sighting (READOUT §1, §2.4 and §4, with §2.4's two inferences labelled). The "⚠ Engine mismatch" sentence becomes "Engine ✓ since main-@@MERGE_SHORT@@", plus a "still open" note for CoinFlipToBlockAttack and a pending Will (PLAN step 13; PLAN repair A's "Still to do").
- **§9, two new lines after 145:** "Will doesn't force the Confusion coin" (READOUT §2.2 item 1 and §4: 210403 T16 376-389, Astra, Dustin) and "after a Confusion heads, Will applies to the attack's own first coin, and Victory Star is still offered" (READOUT §2.2 items 2-3 and §4: T14 342-355). The engine ⚠ comes from READOUT §2.2's "The simulator, by look item". Will's printed wording: `lib/card.py "Will"`.

## `rules/02_damage_knockouts_points.md` (6 lines changed, 2 added)

- **New paragraph after line 49 (§1, a second fixed-reduction case, 210403 T18):** READOUT §2.4 "guarded-grill-after-weakness" and §4 "§1 / step 4". The arithmetic is labelled. "Engine matches since rules1": rules/09:30-31 and READOUT §2.4 ("a fixed −20 takes the same path on main and the candidate").
- **Line 57 (§2):** Water Shuriken's plain 20 on a Water-weak Typhlosion ex (214736, 289-297). Source: READOUT §2.4 and §4; the types were confirmed in WALLACE §7 point 5.
- **Line 114 (§5):** adds 213822 (Turbo Shark at 94; Destructive Inferno at 201.5) and 214736. **The times for 214736 are 177-194, not 174-194.** READOUT §4 says 174-194, but READOUT §3a and the lead acceptance (`Battle Logs/Recording_QA/20261001_214736000_iOS_rule_sol/LEAD_ACCEPTANCE.json`: "177 Gabite0 ... 194 point") give 177-194.
- **Line 119 (§5):** Counterattack on a lethal hit (203626, 229.5-241.5). Source: READOUT §4 and §3a.
- **Line 137 (§6):** Wild Swing discarding two Mega ex with no points (213822, 145-161). Source: READOUT §2.3 and §4.
- **Line 145 (§7):** cites 203626 with its caveats (Solo; an Ability KO). Source: READOUT §2.1 and §4.
- **Line 153 (§8, Wallace):** replaced with WALLACE §5's wording, word for word.

## `rules/05_open_questions.md` (2 lines changed)

- **Line 84 (v1.7.0 named-card searches):** "Engine: Gladion and Grunt wrong" becomes "Engine ✓ since rules1", blocked only by an empty deck, so it agrees with the new `rules/04:91`. Source: WALLACE §6. The Supporter-count clause stays as a check: WALLACE doesn't read it.
- **Line 85 (Wallace):** the last sentence becomes "Engine ✓ (timing; maximum HP after bonuses, rules1; `09`)", plus the 213822 sentence. Source: WALLACE §5 and §7 point 1, word for word apart from the date added to the citation.

## `START_HERE.md` (1 line changed)

- **Line 16, the engine line:** it now names `rl/engine-2026-10-02/`, main-@@MERGE_SHORT@@, and what the Oct 1 repairs add. The rest of the line is unchanged. Sources: PLAN step 13; the task.
- **The seed row is checked and unchanged.** Line 142 already registers 23,100,000,000 + pairing × 10,000 + i, with pairings 0-31 (step 8), 32-35 (8b) and 40-71 (7c). These are the pairings `PIN_STATUS` and `seeds_8.txt`/`seeds_7c.txt` record as played.

## `CLAUDE.md` (the official-engine paragraph: 6 lines become 7; the "Hashes for all of them" line is unchanged)

- The new folder and engine name, "a rules switch", `engine/src/players/` unchanged, km3 still the pilot, and `rl/engine-2026-09-30/` added to the history list. Sources: PLAN "What the switch is"; candidate.txt (players/ unchanged); the Sept 30 wording kept where still true.

## `rl/RUN5.md` (6 lines changed, 1 added)

- **Line 338 (the floor's pre-use re-check):** now names `results/floor_recheck_2026-10/` (its `PLAN.md` is committed with this pin, PLAN step 13), then Sept 30's and Sept 28's.
- **Line 335 ("Where things stand", Official engine):** now names main-@@MERGE_SHORT@@ in `rl/engine-2026-10-02/`. Sources: PIN_STATUS (step 7: kta3, km3, k3, kp3, kog3, kq3, kpr3 and kd3 equal; k3 and kp3 on 28 + 17 cells); identity_check; README "Dustin's word" (8c's condition). This line was not in the task's list. It is changed because RUN5 wins on status (START_HERE) and would otherwise name the old engine. The Sept 30 pin changed the same line.
- **Line 415 (Dustin's decision 10):** the record is kept, completed with "until F8 or a second reader settles it" (his actual answer: README "Dustin's decisions" item 10; PLAN question 10), and "F8 has: covered" is added (README "F8 is done"; F8).
- **New line after 436, "Pinned Oct 2":** the short pinned bullet the task asks for. Sources: README "Dustin's word" (game 28, the conditions); PIN_STATUS (sitting 1's programs, never rebuilt); candidate.txt; PLAN step 14 (pilot stays km3) and step 15 (`results/floor_recheck_2026-10/PLAN.md`). The reason games are unchanged without a Victini or coin-Ability Pokémon is the replays (steps 7-10), not `players/`: kd's follow-on is in `hooks/core.rs`.
- **Line 454 (Finished):** "and the rules switch of Oct 1" is added. It is not in the task's list; the Sept 30 pin made the same kind of change.
- **Line 483 (A5, the B4b refresh):** the pinned engine named there becomes `rl/engine-2026-10-02/`. It is not in the task's list; the Sept 30 pin changed the same phrase. The references named there (k3, kp3 and kog3 tables; kta3's and km3's recorded games) are unchanged, since step 7 replayed them identical.
- **Line 506 (09e964f, "rules/09 lists them for the next merge"):** this is PLAN step 13's "RUN5:468" (the line has moved). It now says fix 2 is not taken (Dustin) and fix 1 has nothing to port (F8; F8 did not audit every path). Sources: F8; README item 10.

## `rl/engine-2026-10-02/README.md` (new; modelled on `rl/engine-2026-09-30/README.md`)

- The three sha256: programs.sha256 and PIN_STATUS lines 5-7.
- The build (03:16 UTC Oct 1, one archive, `--locked`, fresh folder, empty target): PIN_STATUS lines 4 and 11.
- The candidate and its ref: PIN_STATUS line 2; candidate.txt; `sitting1.sh` line 199 (`CREF=refs/pocketdecksim/rules-switch-candidate # not a branch`).
- The watch build, 8d881a1b: watch.sha256; PIN_STATUS line 14.
- **What it is:** the commits for A and B (PLAN "What the switch is", each checked with `git log -1`); F1 160a9d4 and F2 d479f01 (git log of R); the 9 files (candidate.txt and `git diff --name-status c9f4224 5a18d31 -- engine/`).
- **What didn't change:** PIN_STATUS lines 16-18 and 26-28; identity_check. The 7b counts: PIN_STATUS line 17. The card list for "where games change": PLAN "What should change".
- **Where games change:** PIN_STATUS lines 23 and 25 (3,750 of 24,000; 63 of 320). The 8c outcome and game 28: README "Dustin's word" (see "Assumed at the pin" above).
- **Approved:** README "Dustin's decisions" and "Dustin's word", verbatim fragments.
- **Known limits:** PLAN "Known limits" and "Left out"; README "Dustin's word" (the card-text rule); READOUT §3b.

## `rl/results/engine_switch_rules_2026-10/README.md` (25 lines added; no existing line changed)

- **New section "The pin (Oct 1)"**, placed before "Who does what". The task named only the backlog section; PLAN step 13 lists "this folder's README", and the Sept 30 switch README has this section. **It can be dropped if `pin.sh` or another draft writes the pin's record.** Sources: PLAN steps 11, 12 and 14; candidate.txt; programs.sha256; PIN_STATUS; the merge's contents (`git diff --name-status 4690810 f8cfa9c -- . ':!engine'`: all under `rl/results/`; `git merge-tree --write-tree main f8cfa9c` is clean today). "Scoreboard v3 re-verified at the new engine, 45 cells" is the sentence PLAN's "frozen tables" asks this README to record, backed by PIN_STATUS lines 11, 16 and 17.
- **New section "Next switch backlog"**, as the task asked. The B4b refresh's id-keyed items: PLAN "Left out". The reprint ids were checked at `b4b_prep_2026-09-26/B4B_REPRINT_CHECK_2026-09-29.md` lines 70, 99, 235, 322 and 407. `card_validation.rs:96` was checked at code@C. `COIN_IDS`, `FINITE` and `FULL` were checked at lines 82-84 of the coin `instrument_scan.py` at 5a18d31 (EQUIV §7 lists all three); the Victory Star script keys no ids. The next-switch items: rules/09's new open entry; READOUT §4 ("Don't edit inside the switch"; open cases 1-4); WALLACE §3. The upstream-merge line: PLAN "Left out" (PR #383, "keep ours") and F8 / README item 10.

## `rl/results/engine_switch_rules_2026-10/PLAN.md` (1 line changed; an extra, not in the task's list)

- **Line 26:** "unchecked" becomes "covered, F8.md". The switch README says in so many words that this line changes at step 13 ("So at step 13, `rules/09`'s line 80 and `PLAN.md`'s line 26 change from 'unchecked' to 'covered, F8.md'"). **Drop this file if the plan is to stay as Dustin approved it.**

---

## Left alone on purpose (possible follow-ups, not drafted)

- `rules/05_open_questions.md:79` (double-KO order) could cite 203626 as rules/02 §7 now does. It wasn't on the list.
- The switch README's "Who does what" table (the 8c row) isn't updated: who ran 8c, and with what cross-check, isn't recorded yet.
- `PIN_STATUS.txt` is the pin script's to write.
