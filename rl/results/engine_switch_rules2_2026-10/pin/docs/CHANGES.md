# Steps 11-14's documents for rules switch 2's pin: what changed, and the source for each claim

Drafted Oct 11 (laptop session, a subagent; nothing committed, staged, built or played; git only read, from WSL). Each file under `pin/docs/` is the full new text of the repository file at the same relative path. Every line not listed below is byte-identical to the working copy at main 1c34c00c (drafting began at 980ca8c8; the two commits since, 788c8d3f and 1c34c00c, touch none of the targets). All targets are LF, no BOM, ending in a newline, and equal to main's committed blob (`git hash-object` against `HEAD:<path>` for each, and `git diff --quiet HEAD` at 980ca8c8); the drafts keep that.

- **Placeholders:** `@@MERGE@@` (the pin's merge commit, 40 hex) and `@@MERGE_SHORT@@` (its first 7). No `@@DUSTIN@@`: Dustin's word is committed in `8c_DECISION.md` (980ca8c8, line 18), so the drafts quote it: "Yes the hand trace is good".
- **`BASE.sha256`:** the sha256 of the 8 existing targets as they are now, paths relative to the repository (check: `sha256sum -c rl/results/engine_switch_rules2_2026-10/pin/docs/BASE.sha256` from the repository root). The 3 new files have no line.
- **`DOCS.sha256`:** the sha256 of all 11 drafts, placeholders in, paths relative to `pin/docs/` (check: `sha256sum -c DOCS.sha256` from `pin/docs/`). It doesn't list this file or the two lists.
- **The date:** the pin on Monday Oct 12, Central. If it lands on another date, change `2026-10-12` everywhere (`switch2.env`'s ENGINE_DIR; the folder `docs/rl/engine-2026-10-12/` and its line in `DOCS.sha256`; START_HERE 1, CLAUDE.md 2, RUN5 3, the switch README 2, the step 15 plan 6) and "Oct 12" (START_HERE 1, CLAUDE.md 1, RUN5 3 plus "Oct 11-12" at its line 548, `rules/09` 6, `rules/04` 5, `rules/02` 1, READOUT 3, km's reading 1, the switch README 2, the engine README 2), then rewrite `DOCS.sha256`.
- **Values for `switch2.env`** (set and committed by the laptop session; I didn't touch it):
  - `ENGINE_DIR=rl/engine-2026-10-12`
  - `FR_REL=rl/results/floor_recheck_rules2_2026-10`
  - `PIN_NOTED_EXTRA=rules/09_engine_repairs_2026-09-22.md,rules/04_actions_cards_effects.md,rl/results/km_tables_2026-09-30/READING.md`
  - and at the pin, `PIN_DUSTIN='Yes the hand trace is good'` (`8c_RESULT.txt` has dustin 1).
- **Checked:** the Python of `pin_rules.sh`'s `build_docs` (lines 691-772, extracted verbatim) run read-only against these drafts, with main's HEAD 1c34c00c standing in for the merge (as `--check` does), the required list plus the PIN_NOTED_EXTRA above, ENGINE_DIR and seed block 23300000000, and the paths P changes since its merge base with main as the merge's paths. Exit 0: 8 drafts replace their BASE, 3 are new, no unknown placeholder, START_HERE and CLAUDE.md name `rl/engine-2026-10-12`, START_HERE keeps the 23,300,000,000 row, no target is a merge path. **Not run:** `pin_rules.sh --check` itself, which refuses while `switch2.env` holds TO_FINALIZE values. It will print one NOTE: this switch's `PLAN.md` is not drafted (not a stop).

Abbreviations: **PLAN**, **STATUS**, **PIN_STATUS**, **RELEASE**, **8c/README**, **8c_RESULT**, **8c_DECISION** = this switch's `PLAN.md`, `STATUS.txt`, `PIN_STATUS.txt`, `RELEASE_PACKAGE.md`, `8c/README.md`, `8c_RESULT.txt`, `8c_DECISION.md`; **pin/README** = `pin/README.md`; **NOTE8** = `rl/results/coin_prevention_round2_2026-10-01/SECOND_READ_sonnet.md`:88; **commits** = `engine_commits.tsv` and each commit's message (`git log -1`); **at P** = read with `git show c7a25df4:<path>` or `git grep` at P (the merge's `engine/` is P's tree 70652fff). Card texts are from `python3 lib/card.py` (WSL).

---

## `START_HERE.md` (1 line changed)

- **Line 16, the engine line:** names `rl/engine-2026-10-12/` and main-@@MERGE_SHORT@@, and adds "since Oct 12 rules switch 2: round 2's coin-prevention rules and card-text fixes, Fossils as Item cards, and Weakness on an attack's return damage". The rest is unchanged. Sources: PLAN.md line 326 (the pin's documents: "START_HERE's engine line and seed row"); pin/README line 84 only for the rule that START_HERE.md names ENGINE_DIR; PLAN section 0 ("Scope: three parts") and section 2; RELEASE "What it is".
- **The seed row (line 144) is checked and unchanged**, as asked: 23,300,000,000 + pairing × 10,000 + i, pairings 0-23 (7c), 40-46 (8b) and 60-62 (Will), which PIN_STATUS lines 16 and 20 and STATUS's STEP 8-seeds line record as played. Step 15 uses no new seeds (the floor's 7,100 row).

## `CLAUDE.md` (the official-engine paragraph: 7 lines rewritten, still 7)

- `rl/engine-2026-10-12/deckgym` (since Oct 12; main-@@MERGE_SHORT@@: rules switch 2, round 2's coin-prevention rules on top of main-8626a35, with the card-text fixes, Fossils as Item cards and return-damage Weakness); `engine/src/players/` unchanged (candidate.txt line 7; STATUS's STEP 4 line); the new engine README; `rl/engine-2026-10-02/` joins the history list. The "Hashes for all of them" line is unchanged. The task's wording, and the Oct 1 pin's change to the same paragraph (`git show 24374a00 -- CLAUDE.md`).

## `rl/RUN5.md` (6 lines added after line 384; lines 415, 418, 542 and 571 changed)

- **New "Pinned Oct 12" bullet, under (E)'s "Rules switch 2 is unparked"** (the switch's only status entry in RUN5), with 5 sub-bullets:
  - Dustin's words: PLAN lines 24-29 ("1-3 sure", about 4:50 pm Central) and the laptop answer (about 5:15 pm Central).
  - The sittings: STATUS's SITTING 1 DONE and SITTING 2 DONE lines; the record commits 7f7581ca and a9890744 (`git log`); 151,240 and 45 cells: PIN_STATUS line 14; deck 10's row: PIN_STATUS line 16 ("page 10's t-weezing: 0 of 240 games differ (wins 8 -> 8)").
  - 8c: 8c_RESULT (on_board 511, lookahead 621, unexplained 0, judgment 1; changed 1133); the game: 8c_DECISION and 8c/README ("The one game the tools left"); Dustin's word: 8c_DECISION line 18 (980ca8c8).
  - The reference that moved: PLAN lines 246 and 266 and question 3a (line 405); STATUS's STEP 9 line (1,044 of 8,000); `08a9b3a_cov_b2e_km3.jsonl`: `step_9.sha256` line 1 and `handoff_8c.md`:120 (48,000 games), and I read the file (96 pairings; 8,000 games in pairings 32-39 and 80-87). km's mixed table: PLAN question 3a.
  - Next: pin/README "After the pin" items 4-5 and `pin_rules.sh`:868 (the STEP 15 HANDOFF line); brews 07/09 provisional: PLAN section 0's table; kx3 and the slow report: RELEASE "The order" and pin/README.
- **Line 415, "Official engine":** the new folder and name, and the replays and the B2e reference (PIN_STATUS lines 14-27). The Oct 2 engine joins the kept list. The Oct 1 pin changed the same line.
- **Line 418:** the floor's pre-use re-check is now `results/floor_recheck_rules2_2026-10/` (FR_REL); Oct 2's is listed beside the earlier ones.
- **Line 542, "Finished":** adds "rules switch 2 (Oct 11-12)" (sittings Oct 11, pin Oct 12).
- **Line 571 (A5, the B4b refresh):** the pinned engine named there becomes `rl/engine-2026-10-12/`. The references named there are unchanged: step 7 replayed them identical (PIN_STATUS line 14). The Oct 1 pin changed the same phrase.

## `rules/09_engine_repairs_2026-09-22.md` (one entry moved and amended; one new heading, two new blocks; three lines changed)

- **The hit-back entry stays open** (old line 100; added Oct 9 at d9f867c7, `git blame`). This switch doesn't fix it: P2 adds only Weakness (5543a4ba's message; at P, `handle_attack_retaliation` adds `counter_damage + weakness_extra` through `apply_damage`, outside `modify_damage`), and Dustin approved the scope without it (PLAN lines 30-33). It moves up, from after the Oct 1 left-open entry to right after the 09e964f entry, so that it stays under "Open engine bugs". Two edits in it: the line reference `:614-633` becomes `:774 at main-@@MERGE_SHORT@@` (`git grep` at P), and "so no cut applies, today and after switch 2, which adds only Weakness" becomes the same fact said after the pin, with PLAN's reason for keeping it open.
- **The 09e964f entry is unchanged:** it isn't this switch's (Dustin, Sept 30; F8).
- **New heading "Fixed Oct 12"** above the Oct 1 left-open entry, which stays byte for byte (old lines 86-98), as the Oct 1 pin did with its three entries.
- **Its "Fixed in main-@@MERGE_SHORT@@" note**, item by item: (1) e0ecf19f (six sites: Wild Swing and five of the six other sites; its message lists each function), 29e126a8 (the sixth other site, Mega Kangaskhan ex's second punch, and its promotion): Wild Swing and the six other sites in all, as the rules/09 draft says, c7a25df4 (F1), 46953bf3 (`forecast_apply_damage` "flips them for any target ... which covers the own-Bench and own-Pokemon choices and a copied discard attack"; the own-side coin), 3090abbb (Guts, E1); (2) 46953bf3 ("a block coin is a gate coin like Confusion ... Will makes the block coin heads"); (3) and (4) 27a0c37d ("the Will carve-out ... is gone"); (5) 5155ff7a (each Ariados), with its tests 05eb8492 ("both fail at two Ariados"). Evidence line: STATUS (every changed game in a named row, or the sitting would have stopped: PLAN section 6) and 8c_RESULT; the revert switches: 31616338.
- **New "Also fixed in rules switch 2" block** (no rules/09 entry before): Guts, Perish Body, Luxury Coin, the Fossil lock and the Victini caveat (3090abbb's message); P1 (b8a8621a); P3's seven places, named as in 140c0be2's message; the bots' Junk Spark estimate unchanged (140c0be2's message; RELEASE question 2); P2 (5543a4ba) and Bounded Field (b0dc4844: "+20, or under Bounded Field the attack's return damage doubled for a holder that isn't a Mega Evolution Pokemon ex"). Card texts: Ursaluna B3b 058, Conkeldurr A3 096, Galarian Cursola A4a 035, Gholdengo B4a 051 (`lib/card.py`).
- **"Fixed Oct 1":** its heading's "what stays open is the entry above" becomes "what it left open was fixed Oct 12, the section above", and its two "Still open (the entry above)" sentences (old lines 150 and 174-175) now say those cases were left open then and fixed Oct 12.
- NOTE8's first stale item ("rules/09's 'Open engine bugs' entries for these sites") is this change.

## `rules/04_actions_cards_effects.md` (4 lines changed, 2 added)

- **Line 61 (§5, two Ariados):** "⚠ The engine counts one Trap Territory ..." becomes "Engine ✓ since main-@@MERGE_SHORT@@ ...". Source: 5155ff7a.
- **Line 76 (§6, Fossils as Items):** NOTE8's "§6's Fossil line". "the cloud's round-2 package treats it as an Item, for the next rules switch" becomes engine ✓: the Item lock (3090abbb) and the seven other places (140c0be2).
- **Line 147 (§9, Victory Star with a Confused attacker):** NOTE8's "⚠ line on Victory Star". "⚠ Still open on `09`: with CoinFlipToBlockAttack ... or with a Will pending, the engine offers no Victory Star at all" becomes: since main-@@MERGE_SHORT@@ it is offered with a Will pending too, and after a block coin's heads (27a0c37d, 46953bf3).
- **Line 149 (§9, Will after a Confusion heads):** "⚠ Engine: Will is wasted here ..." becomes engine ✓ (27a0c37d), keeping what it was before.
- **New line 150 (§9, a block coin):** Mirror Shot's text (`lib/card.py "B1a 026"`); "seven other cards" from `second_read_dbscan_output.txt` ("block coin (attack text): 9 printings of 8 cards"); Victory Star's words (`lib/card.py "B3 025"`); Will's words (`lib/card.py "A4 156"`); the reading: 46953bf3's message and NOTE8's table items 2-3; "not seen in a game". I left out the shot row `victory-star-block-coin` that P's Victini caveat names: PLAN lines 88-90 say Dustin's Oct 9 cleanup left the Heavy Helmet hit-back row as the list's only row.
- **New line 151 (§9, the two gate coins, question 2b):** PLAN line 402 (2b's reasoning, close to word for word) and SECOND_READ_sonnet.md note 5; "no shot-list row" is 2b's.

## `rules/02_damage_knockouts_points.md` (1 line changed; an extra: `pin_rules.sh` lists it as a noted document)

- **Line 60 (§2, return damage takes Weakness), its engine sentence:** "no Weakness on any return damage today ... queued for the next rules switch" becomes "Engine ✓ since main-@@MERGE_SHORT@@": +20 on an Active attacker weak to the holder's type, doubled under Bounded Field unless the holder is a Mega ex, Tools and Abilities flat (5543a4ba, b0dc4844; `handle_attack_retaliation` at P, :774). **Drop this draft if rules/02 is to wait;** the pin then prints a NOTE, not a stop.

## `rl/results/rules_recordings_2026-10-01/READOUT.md` (7 lines added in 4 places)

- **§4, "At the pin's step 13":** "Done at the Oct 1 pin" (24374a00). Each listed item is in that pin's CHANGES.md (`../engine_switch_rules_2026-10/pin/docs/CHANGES.md`) and `git show 24374a00 --stat` (rules/09, rules/04, rules/02, rules/05).
- **§4, "Don't edit inside the switch":** done in this switch. At P, `b4a_attack_batch2_test.rs` has no line "has not been seen in Pocket" (the F4 comment, :432-433 at 8626a35) and the case is tested by `confusion_with_will_pending_forces_the_attacks_first_coin_and_still_offers_victory_star` (:456); Victini's caveat is at `card_validation.rs`:96-98, reworded by 3090abbb.
- **§4, "Open cases for the next rules switch":** all four done; PLAN lines 219-224 checked the list against this one.
- **§3b, one line under its heading** (beyond §4, which the task named; droppable): all four "simulator differs" items are fixed (27a0c37d, e0ecf19f, 5155ff7a).
- Left alone: §4's shot-list paragraph (the shot list was cleaned up on Oct 9; its state lives in the list).

## `rl/results/km_tables_2026-09-30/READING.md` (2 lines added after the title; question 3a's record)

- km3's B2e reference for pairings 32-39 and 80-87 is step 9's replay `../engine_switch_rules2_2026-10/08a9b3a_cov_b2e_km3.jsonl` (sha256 84247fb4…: `step_9.sha256` line 1, and `sha256sum` of the file); the other 80 pairings equal (STATUS's STEP 9 line; `identity_9.txt` line 1); 1,044 of 8,000 changed, all accounted for (8c_RESULT; 8c/README block C); Dustin's yes (PLAN lines 24-29 and question 3a, line 405); "km's Sept 30 reading stays a reading on its own engine" and the mixed table's rule (PLAN lines 266 and 405); B = 1f6319e (this READING, lines 6-7).
- **Why this file:** no document recorded the B2e reference as such. The runners name it (`sitting2.sh`'s step 9; `handoff_8c.md`:31, "km3's B2e reference (`km_tables_2026-09-30/1f6319e_b2e_km3.jsonl`)"), and that folder has no README, so its reading is where a later km reading looks. START_HERE and RUN5 never named the file; RUN5's pin note and the switch README now carry the same record.

## `rl/results/engine_switch_rules2_2026-10/README.md` (new: this switch's summary)

- What the switch is: switch2.env (P, P_TREE); PLAN sections 0 and 2; RELEASE "What it is"; commits (P1 b8a8621a, P2 5543a4ba and b0dc4844, P3 140c0be2, F1 c7a25df4, the switches 31616338); the 13 switches: `git grep -o 'DECKGYM_[A-Z0-9_]+'` at P minus those at 8626a35 (`DECKGYM_UNBOUNDED_ENERGY_MOVES` predates the switch), as `pin_rules.sh`:327-330 computes them; 26 files, 17 + 9: `allowed_engine_files.tsv`; the suite: `switch2.env`'s SUITE_AT_P (fc6307c0: "TOTAL: 2103 passed, 0 failed").
- Dustin's decisions: PLAN lines 24-33; scope details: RELEASE question 2; the two stricter checks: PLAN question 1.
- Sitting 1: PIN_STATUS lines 1-18 (times, 199,400 games, each step); sitting 2: lines 19-28 (137,090 games); the trace load: line 22 and `trace_load.txt`.
- 8c: 8c_RESULT; 8c/README (the table, the times, "No agents", the 25 games against the cloud); the coordinator's audit: 8c/README's last section, "added after the coordinator's audit, Oct 11" (1c34c00c).
- The judgment call: 8c_DECISION and 8c/README; Dustin's word: 8c_DECISION line 18, quoted exactly.
- The pin: pin/README and `pin_rules.sh`'s header (what it does); main's `engine/` unchanged since c4f27f2 (`git diff --quiet c4f27f2 HEAD -- engine/`, at 1c34c00c); the records the merge brings: `git diff --name-status HEAD c7a25df4` ("A" paths under `coin_prevention_round2_2026-10-01/` and `round2_readiness_2026-10-02/`); "Scoreboard v3 re-verified": PIN_STATUS lines 11 and 14, as the Oct 1 README says it.
- After the pin: pin/README "After the pin"; deck 10: PIN_STATUS line 16. Left out: PLAN lines 30-33 and 229; RELEASE question 2; PLAN question 2b; `card_validation.rs`:96 at P (`CardId::B3025Victini | CardId::PB049Victini`). Who did what: PLAN section 7 and its Oct 9-10 status lines; 8c/README; PLAN line 86 (`revert_8c.py`, Sonnet).

## `rl/engine-2026-10-12/README.md` (new; modelled on `rl/engine-2026-10-02/README.md` and on `pin_rules.sh`'s own text, lines 802-830)

- The three sha256: `programs.sha256` and PIN_STATUS lines 5-7. The build: PIN_STATUS lines 2 and 4 (07:23 UTC Oct 11, `--locked`, fresh folder, empty target). The candidate ref: switch2.env's CREF. The watch build 60797708: PIN_STATUS line 12. The switches: as above. The evidence: PIN_STATUS lines 14-27 and 8c_RESULT. Approved: PLAN lines 24-29 and 8c_DECISION.
- Because it is drafted here, the pin installs it instead of its own text (pin/README line 88). Like the pin's text, it quotes Dustin's 8c word (pin/README line 69).

## `rl/results/floor_recheck_rules2_2026-10/PLAN.md` (new; FR_REL's plan, step 15)

- Modelled on `../floor_recheck_2026-10/PLAN.md`. Its list is pin/README's step 15 (items 1-6) and `pin_rules.sh`:868; PLAN row 15 and section 0 (brews 07 and 09).
- Part A: the five decks, wins and expected byte-equality from Oct 2's verdicts (`../floor_recheck_2026-10/verdicts.txt`) and its outputs as committed at 2d7082cf (`git log`); 13,440 games and about 18 minutes: Oct 2's `timing.txt` (1,064 s). "No card a rule of the switch reads": a name check (grep) of the 5 decks and 8 panel lists against `second_read_dbscan_output.txt`'s lists and the five hit-back attackers; the only hits were Teal Mask Ogerpon ex, Team Rocket's Raticate ex, Hoopa ex, Team Rocket's Weezing ex and Team Rocket's Goo-zooka, none of them a card the switch reads (Goo-zooka is a Trainer: `lib/card.py "B4a 068"`; the Trap Territory change loops over the Ability only, `hooks/retreat.rs` at P). The coverage note: `git diff 8626a35 c7a25df4 -- engine/src/card_validation.rs` changes only Victini's and Gholdengo's texts. floor.py and run_screen.py: Oct 2's `run_check.log` lines 4-5 (8e5395e6, d7bde1af), today's sha256 (7632786…, d7bde1af…), `floor_7c.tsv`'s FLOOR_PY_DIFF line. The start rule: RUN5 line 413.
- Part B: the old pages and their verdicts read from their files (deck 12 602; brew 07 1,168; brew 09 835; D 693, amended 597, passive 693; deck 10 324); the passive page's recipe: `../floor_drafts_2026-10-02/draft-D_victini-passive/` (`run_d2.sh`, `floor_copy.diff`, `run_copy.py`); D's first list: switch2.env (D_FIRST_*) and `floor_7c/d_first/`; floor.py keys ROLES by the list's path (`floor.py`:489 and 523); step 7c's D replays took the old goldfish's coverage (`floor_7c/NOTE.txt`; their coverage files equal Oct 2's, `cmp`); the 8b rows for brews 07/09: START_HERE's 23,100,000,000 row (pairings 36-37); "return Weakness 17 games": STATUS's STEP 8b line.

---

## Left alone on purpose

- **This switch's `PLAN.md`** (a noted document): nothing in it must change at the pin. `--check` prints a NOTE.
- **RUN5 line 340** ("The reference stays the official engine (main-8626a35) and km3", in the Oct 2 direction): it is the planning-pilot work's reference, and kx3 stays on main-8626a35 until it is rebuilt after step 15. Change it then, or now if the coordinator prefers.
- **RUN5 line 384** ("provisional until it's pinned", Oct 7): kept as said; the new pin note says they stay provisional until the new pages.
- **Stale lines from before this switch, not in the list:** `rules/08_tests_to_record.md`:45 (Victory Star after a Confusion heads still "engine mismatch, open bug on `09`", fixed Oct 1); `rules/05_open_questions.md`:62 (#19, Heavy Helmet's printed cost "an open bug on `09`", fixed Sept 26); `rules/09`'s line-6 status paragraph (rules4, Sept 24).
- **NOTE8's other items:** "`card_validation.rs`'s old caveats" are engine text that P itself rewrote (3090abbb, b8a8621a), not a document; "rules/ and PLAN.md are not edited" is the round-2 README's own statement (at P, README.md:592), which the merge brings, so it can't be drafted and isn't stale.

## Open items

1. **`switch2.env`** still has ENGINE_DIR, FR_REL and PIN_NOTED_EXTRA at TO_FINALIZE. The laptop session sets the three values above and commits it; then `--check`.
2. **Step 15's runner doesn't exist yet.** The plan names `run_check.sh` in FR_REL (a copy of Oct 2's, adapted) and Part B's page runs. Each must be written, reviewed and committed before any game. The pin lets FR_REL hold `.sh`/`.py` files before its commit.
3. **Draft D's victini-passive remake:** the copy's ROLES entry is keyed by the list's path, and D's first list now lives at `floor_7c/d_first/`, so the rebuilt copy's key must name that path (the plan says so). Whoever writes the runner should confirm this matches "the way it was made on Oct 2".
4. **Draft D's root and amended pages "(text)":** the plan builds them from step 7c's replays plus the new goldfish's coverage, with no games, as PLAN row 15 and pin/README say. `floor.py` has no text-only mode, so the runner does this by hand-free scripting or, if preferred, replays the two pages through `floor.py` (2 × 1,920 games, a check that they equal step 7c's). That choice is the coordinator's.
5. **If RUN5 or another target changes before the pin** (RUN5 moves often), the pin stops on its BASE hash: re-draft that file, re-review it, and rewrite both lists.
6. **The date** (above).
7. **Extras that can be dropped without a stop:** `rules/02` (a noted document) and READOUT's §3b line.

## Oct 11, after the drafting (the laptop session, on the coordinator's decisions)

- `rl/results/floor_recheck_rules2_2026-10/PLAN.md`, Part B item 4: one line added. Each of draft D's root and amended text pages says that
  its games are step 7c's replays, equal to Oct 2's, and that no game was played for it. This is the coordinator's decision (d), Oct 11: assemble
  from 7c's replays plus the coverage, no new replay. `DOCS.sha256` was updated for this file only.
- The coordinator's other decisions, Oct 11: (a) the Heavy Helmet hit-back entry stays open in `rules/09`; (b) the `rules/02` §2 line stays,
  NOTEd at the pin as beyond PLAN's list; (c) km3's new B2e reference stays recorded in `km_tables_2026-09-30/READING.md`.

- Review fixes, Oct 11 (the credit worker's REVIEW_pin_docs_sonnet.md, sonnet/pin-docs-review b072bc40, through the coordinator): the START_HERE engine line's citation now names PLAN.md line 326; the site count reads "Wild Swing and the six other sites" (e0ecf19f's six sites plus 29e126a8's second punch), as in rules/09. CHANGES.md only; no draft or hash changed.
