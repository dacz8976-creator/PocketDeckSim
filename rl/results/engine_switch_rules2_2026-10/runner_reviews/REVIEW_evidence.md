# Evidence review of the rules switch 2 runner copies (Opus, read-only)

**Scope.** I read all of `sitting1.sh`, `sitting1_check.py`, `sitting2.sh`, `sitting2_check.py`, `switch_check.py` (its diff), `pin/pin_rules.sh`, `pin/update_manifest_rules.py` and `pin/README.md` in `rl/results/engine_switch_rules2_2026-10/`. I compared them with the Oct 1 originals, PLAN.md (section 0, sections 3-6 and the Oct 9 status), RELEASE_PACKAGE.md and ADAPTATION_SPEC.md.

**Git facts.** I checked these with read-only `git show`, `ls-tree` and `log` on refs already fetched:
- branch tip `056158c3` (22:39 UTC);
- the last engine commit is `31616338` (engine tree `639d2f80`, 26 files against 8626a35, 24 engine commits);
- (a) landed after it, in `77aa8e3d` and `056158c3`, and touches `rl/results/round2_readiness_2026-10-02/` only;
- main is `d9f867c7`.

**What I did not run.** Nothing was built, played, fetched or committed. I ran no runner and no dry run.

**The numbers match PLAN.** Every game count and seed block below matches PLAN's tables:
- 199,400 and 137,090 games; 151,240, 28,000, 20,160, 54,750, 74,500 and 5,040 by step;
- 8b plays 2,800, against PLAN's 2,320. The 480 extra are the cloud's rows 36-37, which ADAPTATION_SPEC A5 records.

**The identity sets match Oct 1.**
- Step 7's REF7 and SPEC7, step 7b's SPEC7B and step 9's SPEC9 are byte-identical to Oct 1's.

**The counter model matches the coin script at the tip.**
- 16 reach2 counters: da08620's 15 EXACT plus `attack_return_weakness`.
- 10 offgate2 counters and 1 superset2 counter.
- R2_COUNTERS plus R2_KEYED are 27 names. With round 1's 15, the total is 42.

**The cloud's 8b files fit what sitting 2 compares.**
- The cloud's pinned rows came from the same official legality_scan the laptop uses as "old".
- Its pairs file holds pairings 32-37 on the 23.1B block.

**The deck 10 page and the D pages fit the checker.**
- On deck 10's page, the opponent field is `t-weezing` (240 games each).
- D's coverage key is `B3 025`, and its page row is `| Victini (B3 025) |`.

**Caveat text.** Between 8626a35 and the tip, `card_validation.rs` changes only Victini's and Gholdengo's caveats. So step 10's goldfish coverage (altaria and the panel) should stay byte-equal.

---

## Blocker

### B1. The data files and two byte copies are missing, so nothing can start or dry-run
- **Where:**
  - `sitting1.sh`:246 (DATAFILES) and :439 (HELPERS: `floor_with.py`, `.gitignore`);
  - `sitting2.sh`:216 (DATA_FILES) and :346 (HELPERS: `.gitignore`);
  - `pin/pin_rules.sh`:91 (DATA_TSV).
- **What:** As of 18:26 local, the folder holds none of these files:
  - `switch2.env`, `allowed_engine_files.tsv`, `engine_commits.tsv`, `counters.tsv`, `floor_7c.tsv`, `reuse.tsv`, `tools_8c.tsv`;
  - `floor_with.py`, `.gitignore`.
- **Failure:**
  - Both dry runs halt with "switch2.env is missing".
  - Every start refuses.
  - The evidence the runners check against cannot be reviewed as real files: the allowed list, the counter roles, the floor pages, the reused files and the 8c tools. I reviewed ADAPTATION_SPEC Appendix A as their intended content.
- **Smallest fix:** Write the seven data files from Appendix A, with the changes below. Byte-copy `floor_with.py` (7e4880fe) and `.gitignore` (ff44c03a) from the Oct 1 folder. Then run both dry runs.

---

## Should fix

### S1. The 8c tools are checked only for existence at the candidate, so the hand-off can name a probe without round 2's conditions
- **Where:**
  - `sitting2.sh`:873-877 and :1491-1492 (`tools_missing`, `git cat-file -e`);
  - `sitting2_check.py`:855-858 (the hand-off lists `<C7>:<path>`);
  - ADAPTATION_SPEC A.7.
- **What:** "P = the final engine commit" literally means `31616338`, the last commit touching `engine/` and the last row of engine_commits.tsv. But (a), coin_probe v2's round-2 conditions, landed after it (`77aa8e3d`, `056158c3`).
  - With P = `31616338`, the candidate's `coin_probe_v2.rs` is the version from before (a).
  - The existence check still passes.
  - `validate_v2.py` (tools_8c's `probe_validate`) still reads round 1's REACH at the tip (`validate_v2.py`:30-32). PLAN section 6, change 1, says those never count.
- **Failure:** The hand-off tells 8c to use the candidate's tools. A Will, Trap Territory or plain-hit look-ahead game in 8b, 8 or 9 then reads UNEXPLAINED (a stop), or it is classified with round 1's reach list.
- **Smallest fix:**
  - Give `tools_8c.tsv` a `blob` column, holding the versions with (a) and (b), and check it at the candidate.
  - Or state in switch2.env that P must contain (a) and (b), for example the tip `056158c3`, whose `engine/` is still `639d2f80`.
  - Drop `validate_v2.py`, or require its round-2 version.

### S2. The revert switch for the "sites" mechanic names one switch where the engine needs two
- **Where:**
  - ADAPTATION_SPEC A.4: the `coin_queued_by_attack` row gets `DECKGYM_PLAIN_QUEUED_SITES`;
  - `sitting1_check.py`:152: the regex allows a single name;
  - `sitting2_check.py`:640 (the `revert_switches` column) and :791-794 (RULE item 3: "its switch below, alone, and all together");
  - `pin/pin_rules.sh`:317-320.
- **What:** The engine's own G2 comment (`apply_action_helpers.rs`:697-700 at 31616338) says: "Off: a plain `ApplyDamage`, as before ... The old damage needs G1 off too". So the old engine at a Wild Swing site needs both `DECKGYM_PLAIN_QUEUED_SITES` and `DECKGYM_NO_PLAIN_HIT_COIN`.
- **Failure:**
  - 8c runs the revert check with G2 alone, as the hand-off says.
  - With G2 alone off, the site queues a plain hit and G1 still flips the coin on it. That is not the old engine at that site, by design, so the old move need not come back.
  - A correctly explained look-ahead game (like the cloud's 17 Wild Swing games in 8b pairing 35) can then fail the revert check. Under PLAN section 6, change 3, that is a stop or a judgment call for Dustin.
  - Also, the mapping for the other gates was assigned by the code's order, not read from it.
- **Smallest fix:**
  - Allow `A+B` in `revert_switch`, and set the sites row to `DECKGYM_PLAIN_QUEUED_SITES+DECKGYM_NO_PLAIN_HIT_COIN`. Make the pin's check split on `+`.
  - Reword RULE item 3: "the gate's switch set reproduces alone, and `DECKGYM_ROUND2_OFF` reproduces together".
  - Fill every row from the G1-G11 comments at P.

### S3. "A game where every counter is 0 must be identical" is dropped without a recorded ruling
- **Where:**
  - `sitting2_check.py`:333-343 (`classify`) and :615-644;
  - `sitting2.sh` header :21-24;
  - `pin/pin_rules.sh`:384-438;
  - ADAPTATION_SPEC A7.
- **What:** PLAN section 6 (line 292) says the mechanic check is "the last plan's (lines 126-150), with three changes". Old PLAN line 148, "A game where every counter is 0 must be identical", is not among the three changes.
  - The Oct 1 condition-3 ruling, which Dustin's yes carries, covers games where only off-gate counters fired. It does not cover games with no counter.
  - The copies send the `none` and `other_only` categories to 8c. The pin then accepts them as look-ahead games, with no count of their own and no word from Dustin.
- **Evidence it will happen:** The cloud's own 8b already has one: k3 pairing 37 i 35 has every counter at 0 in its watch row, and I checked it.
- **Failure:** PLAN's literal stop rule and its question 1 ("explained ... or the bots saw it in their look-ahead and the revert check brings the old move back") disagree on that game. The runners decide it silently.
- **Smallest fix:**
  - Record the coordinator's or Dustin's reading in README before sitting 2, as was done for condition 3 on Oct 1.
  - Add `none <x> traced <x>` and `other_only <y> traced <y>` to the 8C grammar, checked against the hand-off as `condition3` is, so the pin commit, the manifest and the engine README state the count.

### S4. 7c's deck 10 v t-weezing watch row is treated as a named row, but PLAN names only the floor row
- **Where:**
  - `sitting1.sh`:1751-1753 (`--exclude-pairings 7`) and :1100-1115 (`touched_7c`);
  - ADAPTATION_SPEC A11.
- **What:** PLAN line 284 names "8b, 8, 9's pairings 32-39 and 80-87, and deck 10's t-weezing floor row". The new watch row (pairing 7 on 23,300,000,000) is not named, so under PLAN a change there is a stop. The copy hands its changed games to 8c and never halts.
- **Failure:** The stop rule is relaxed without anyone's recorded word.
- **Smallest fix:** Record the coordinator's word (PLAN or README note). Otherwise, drop `--exclude-pairings 7` and the `touched_7c` hand-off, and require 1,440 identical deals.

### S5. 7c's counter check on Oct 1's 32 rows is copied by name, not by purpose
- **Where:**
  - `sitting1.sh`:1744-1746;
  - Oct 1's `sitting1.sh`:1224-1227, which says "every repair counter 0".
- **What:** On Oct 1, "as before" meant two things: the switch's own repair counters at 0, and the rewritten lines shown to run (`offgate_helper_choice` in OFFGATE7C).
  - The copy instead zeroes round 1's counters (r1_exact, r1_heads, r1_superset), which both engines have.
  - It only reports round 2's reach2.
  - It does not require round 2's off-gate for the same Absol, Heatmor and Gabite attacks: `offgate_by_attack` fires for "the first round's helpers and Chase Order, whose constructor it rewrote".
  - P's coin script widened two round-1 counters: `coin_queued_offered` now includes "the later round's sites", and `vs_confusion_first_built` "also fires when Will is pending or a block coin is there".
- **Failure:**
  - A round-2 exact counter firing on Dustin's lists passes as a NOTE.
  - A widened round-1 counter can halt sitting 1 for a reason outside the switch.
  - The off-gate evidence proves round 1's rewritten lines ran, not round 2's.
- **Smallest fix:** Use `--zero-role reach2 --zero-role superset2 --require offgate_helper_choice,offgate_by_attack --in $OFFGATE7C --report-rest`, with round 1's counters reported. Or record why the round-1 zero check is kept.

### S6. The trace-load gate's n does not cover the laptop's new 8b rows 40-46
- **Where:**
  - `sitting2.sh`:1143-1190;
  - `sitting2_check.py`:892-922.
- **What:** The cloud's `TRACE LOAD 0` covers pairings 32-37 only, on 140c0be2. Its README says: "Scope. Only the rows the decision names ... the 5 other smoke pairings and 2 block-coin rows ... weren't asked for".
  - PLAN precondition (d) has the cloud play step 8b's rows, all 11 of them.
  - The laptop's 40-46 are Trap Territory, Will and block coin, whose look-ahead conditions the probe only learned in (a).
  - The gate passes on n = 0, whatever the laptop's own 40-46 hand-off holds.
- **Failure:** Step 8 (54,750 games) starts with an untested trace load on the round-2 mechanics.
- **Smallest fix:** Let the gate also read the laptop's 8b hand-off rows for 40-46 that have no reach2 counter. Require n + that count ≤ 50, or a DUSTIN line. Alternatively, require `trace_load.txt` to list the pairings it covers, and wait when 40-46 are missing.

### S7. A change in deck 10's floor row is never tied to the Will rows
- **Where:**
  - `sitting1.sh`:1064-1068 (only REPORT-OPPONENT is recorded);
  - `pin/pin_rules.sh`:794 (STEP15 says "a new page if it differed");
  - PLAN lines 200-202: deck 10's change "is judged in step 8's Will rows".
- **What:** Floor games have no watch build, so PLAN judges them through Will row 60, deck 10 v t-weezing. Nothing checks that link.
- **Failure:** Deck 10's t-weezing floor games could change for another reason (a coin site, P2, a fault) while row 60 shows Will unreached. Step 15 would then make a new page anyway.
- **Smallest fix:** In pin gate 3 (or in sitting 2 after step 8), when 7c's REPORT-OPPONENT count is above 0, require two things: step 8's stepsum shows "Will Confused" reached in pairing 60, and pairing 60's changed games are on the board or in look-ahead in the 8C line. Otherwise treat it as a judgment call that needs `PIN_DUSTIN`.

### S8. The pin's documents PLAN lists are only NOTEs
- **Where:**
  - `pin/pin_rules.sh`:101-104 and :816-820;
  - `pin/README.md`:78.
- **What:** PLAN steps 11-14 (line 272) list these documents:
  - rules/09's open entries closed;
  - rules/04 §9's Victory Star lines and the 2b note;
  - Sonnet's note 8 and READOUT §4;
  - km3's new B2e reference for the 16 rows (question 3a).

  Only START_HERE, CLAUDE.md, RUN5 and README are required. The rest, and `PIN_NOTED_EXTRA`, print a NOTE. This is the same structure as Oct 1.
- **Failure:** The pin finishes with rules/09 still listing the fixed items as open, and with no record of km3's new B2e reference. A later km reading could then use the old reference for pairings 32-39 and 80-87.
- **Smallest fix:**
  - Move rules/09, rules/04 and rules/02 (P2's rule, section 0) into REQUIRED_DOCS.
  - Make `PIN_NOTED_EXTRA` required, naming the question 3a record.
  - Alternatively, let a missing one pass only with a written waiver, as `PIN_DUSTIN` works.

### S9. Step 4's allowed list checks P against itself
- **Where:**
  - `sitting1.sh`:684-685 and :730-731;
  - ADAPTATION_SPEC A.2 and A2/A19.
- **What:** The list is written from `git diff --name-status 8626a35 P` and then checked against that same diff. PLAN's list does not match P:
  - PLAN line 260 names `effect_mechanic_map.rs` and `effect_ability_mechanic_map.rs` for P3. P never touches them.
  - P changes these source files that PLAN's step 4 does not name: `apply_abilities_action.rs`, `models/card.rs`, `apply_action_helpers.rs`, `hooks/counterattack.rs`, `hooks/mod.rs` and `actions/mod.rs`.
  - P also adds a test with status A.
- **Failure:** The check can no longer catch a file outside the approved scope, which was its purpose.
- **Smallest fix:**
  - When finalizing, give each row a `scope` column: 20e2651's 17, P1, P2, P2-switch, P3, Bounded Field or (e).
  - Get the coordinator's word for the files PLAN doesn't name.
  - Give precondition (f)'s readers the same list.

---

## Notes

**N1. The coin script deviates from PLAN step 6.**
- **Where:** `sitting1.sh`:26-27 and :1660-1666.
- **What:** PLAN says "da08620's version", but the copy uses P's `306f1f69` (b7e3bc00's; +114/−2 lines, all P2 counters).
- **Why it is right:** Section 0 (c) needs those counters.
- **To record:** Note in README which script step 6 uses and why. Precondition (c)'s 49/49 probe and the cf3cffe smoke were run on da08620's version, so the second read must cover `306f1f69`. `counter_probe_readiness_output_at_P.txt` exists on the branch.

**N2. Only the existence of `MAGNEZONE_CARD_CHECK` is checked.**
- **Where:** `sitting2.sh`:1493.
- **What:** Only its `<commit>:<path>` is checked to exist, so a file recording a failed or open card check passes.
- **Fix:** Require a PASS line in it.

**N3. The seed-row check passes on the new 23.3B row alone.**
- **Where:** `sitting1.sh`:1270-1275 and `sitting2.sh`:853-858.
- **What:** The amended 23,100,000,000 row that registers 36-37 on that block (`seed_row_23_3B.md` §2) is never checked.
- **Fix:** Also require the 23,100,000,000 line to hold `36–37`.

**N4. The 8C line cannot show "both halves".**
- **Where:** `pin/pin_rules.sh`:405-429 and `update_manifest_rules.py`:95-104.
- **What:** `lookahead <l>` with `revert <l> of <l>` does not show that the code gate and v2 at k were found for each of those games, as PLAN line 295 requires.
- **Fix:** Add `both_halves <l>` to the grammar and check it equals l.

**N5. The cross-check with the cloud covers only part of 8b.**
- **Where:** `sitting2.sh`:1017-1038.
- **What:** Only new 32-37 and old 36-37 are compared. The cloud also committed `8b_watch_<bot>.jsonl`, which its classification and TRACE LOAD 0 used, built on the same coin script blob. Rows 40-46 have no cloud counterpart (only 8c's cross-check).
- **Fix:** Also compare watch 32-37 on the fields both record, counters included.

**N6. The data files can change between sittings.**
- **Where:** `sitting2.sh`:1529-1535.
- **What:** Sitting 2 copies `counters.tsv` and the other data files as they are now. It never compares them with the sums sitting 1's START line recorded. So the reach roles that sorted 7c's hand-off can differ from those for 8b, 8 and 9.
- **Fix:** Refuse sitting 2 when switch2.env, counters.tsv or floor_7c.tsv differ from sitting 1's last START data sums.

**N7. A failed hand-off rebuild is only a note.**
- **Where:** `sitting2.sh`:473-476.
- **What:** The pin checks only the counts per step.
- **Fix:** Have the pin check that `handoff_8c.tsv` equals the concatenation of the per-set `handoff_*.tsv` files in the step manifests.

**N8. `floor_py_check` reads only ATTACKERS.**
- **Where:** `sitting1.sh`:813-836.
- **What:** It never reads ROLES, both of which are keyed by repository path (`floor.py`:88-104). For D_root it checks the copy's path, not D's original path. Today neither table names D or the Sept 30 decks, so there is no effect now.

**N9. PLAN line citations are stale by 4 lines from section 5 on.**
- **Where:** All copies, and the hand-off's RULE and TOOLS text in `sitting2_check.py`:775-799.
- **What:** PLAN.md was edited at 18:05, after the spec at 17:46, so citations such as "line 262" for 8b, "286", "288-291" and "290" now point 4 lines early (8b is now line 266). These texts go into committed evidence: STATUS lines, `handoff_8c.md`, the manifest and the engine README.
- **Fix:** Cite by step or section, or renumber them before committing.

**N10. Watch is never compared with plain on 7c's rows.**
- **What:** 7c compares watch with old only, so watch = plain rests on 7b's table run. This is as on Oct 1, and noted for completeness.

---

## Checked and found as PLAN requires (no finding)

**Step 4:**
- P is taken by commit and must be on its branch.
- P's `engine/` must be P_TREE, P must stack on 8626a35, and the engine commits must match the list, each of its kind.
- `players/`, every Cargo.lock and Cargo.toml must be unchanged, and nothing may be deleted.
- The candidate's `engine/` must be P's tree byte for byte, and the watch scripts must be P's blobs.
- Reserved names are checked.

**Steps 5-6:**
- One archive feeds each build, with `--locked`.
- The references come from the candidate, blob-checked, with step 7's sha256 values.
- The floor pages are the blobs at their commits, and each deck is its blob.
- Inputs are hashed and checked before and after every step.
- The watch build's source differs only in `legality_scan.rs`. It must write all of counters.tsv's names, and the script lists must equal counters.tsv's round-2 rows.

**Step 7b:**
- Every reach2 counter must be 0 in all 28,000 games, counting every key of `coin_queued_by_attack`.
- The three named off-gate counters must be above 0.
- The others are reported.
- Watch must equal plain, and the keys the watch build adds must equal counters.tsv's.

**Step 7c:**
- The 7 pages are replayed. Deck 10's t-weezing games are reported, and every other game must be equal, compared per game, so the page-level allowances can't hide anything.
- D's root page comes from the 9cc6667 copy (blob and sha256 checked), and D amended from today's blob.
- Only Victini's caveat may differ, in the coverage's limitations and the page's engine cell.
- The old-engine replay runs before every page halt, with a clear verdict.
- `offgate_vs_ungated_built` must fire on D's rows. The seeds are recorded and committed before any 7c game.

**8b:**
- Old 32-35 reuses Oct 1's games: the .run record names 97891274, the command is checked, and they equal the cloud's pinned rows.
- The 5 smoke pairings are 40-44, and the 2 block-coin rows are 45-46.
- New 32-37 and old 36-37 must equal the cloud's at P, or the run halts.
- Watch must equal new.

**Step 8:**
- Old 0-31 is reused and checked the same way.
- The Will rows 60-62 are km3 500 and k3 250, played old, new and watch, on 23,300,000,000 + pairing × 10,000 + i, written and committed before any game.

**Step 9:**
- The 80 B2e pairings, Scizor and the second lists must be equal (40,000 + 4,000 + 14,500).
- The named 16 run on watch, watch must equal plain, and their changed games go to 8c.

**Step 10:** Unchanged from Oct 1.

**Program hashes:** They are checked before and after every step in both sittings and at the pin. The floor replays and the screen run check their deckgym's sha256.

**The pin waits for Dustin when it must:**
- It needs `PIN_DUSTIN` when unexplained + judgment > 0.
- It needs `PIN_AFTER_HALT` after any halt.
- It requires every lookahead game to have passed the revert check ("revert l of l reproduced").

**Environment:** A start refuses while any `DECKGYM_*` variable is set.
