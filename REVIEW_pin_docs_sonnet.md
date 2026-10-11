# Review of the 11 pin documents for rules switch 2 (credit worker, Sonnet 5.5)

Branch `review-pin-docs` = laptop branch `laptop/rules2-pin-docs` at dda8dd54. Drafts are under
`rl/results/engine_switch_rules2_2026-10/pin/docs/`. Nothing was edited. Method: I diffed each draft against main's file and
opened each cited source (PIN_STATUS, STATUS, 8c_RESULT, 8c_DECISION, PLAN, switch2.env, engine_commits.tsv, commit messages,
`lib/card.py`, the Oct 2 floor files). Not run: builds, games, `pin_rules.sh`.

**Scope checks (all OK):**
- `git diff --name-only main HEAD` lists only the 11 drafts plus `BASE.sha256`, `DOCS.sha256` and `CHANGES.md`, all under `pin/docs/`. No file outside the list is changed.
- `sha256sum -c DOCS.sha256` (in `pin/docs/`) and `sha256sum -c BASE.sha256` (from the repo root) both pass.
- The line-level diffs match CHANGES.md's counts exactly: RUN5 +6 lines and 4 changed; rules/04 4 changed and 2 added; rules/09 and READOUT (7 lines in 4 places) as described; READING 2 lines; CLAUDE.md 7 lines.
- `switch2.env` holds the three values CHANGES.md quotes (ENGINE_DIR, FR_REL, PIN_NOTED_EXTRA).
- Wording against START_HERE's standing rules: no document ranks decks by the simulator, the language is plain, and nothing is said about Dustin's words beyond the committed quotes.

| Document | Claim | Source | Verdict | Note |
|---|---|---|---|---|
| all | Placeholders `@@MERGE@@`/`@@MERGE_SHORT@@` only; no `@@DUSTIN@@` | grep of drafts; 8c_DECISION.md line 18 | OK | Dustin's word "Yes the hand trace is good" is verbatim at line 18 (Oct 11, about 16:20 UTC). |
| all | Pin date Oct 12 | CHANGES.md | OK | Today is Oct 11; the drafts say "Oct 12" deliberately and CHANGES lists every place to change if the pin moves. |
| START_HERE | Engine line names `rl/engine-2026-10-12/`, adds "since Oct 12 rules switch 2: round 2's coin-prevention rules and card-text fixes, Fossils as Item cards, Weakness on return damage" | PLAN §0, §2; RELEASE; switch2.env | OK | CHANGES cites "pin/README line 84", but that line is the docs-list rule and has no engine-line wording. Citation only; PLAN §0/§2 do carry the content. |
| START_HERE | Seed row 144 unchanged, 23,300,000,000 pairings 0-23, 40-46, 60-62 | PIN_STATUS lines 16, 20, 21, 23; row text | OK | Row says 0-23 (7c), 40-46 (8b), 60-62 (Will rows); matches the played sets. |
| CLAUDE.md | Engine paragraph: new folder and name; `engine/src/players/` unchanged; Oct 2 engine joins history | candidate.txt, PIN_STATUS line 3 ("players/ ... unchanged"), switch2.env OLD_DIR | OK | "round 2's rules on top of main-8626a35" matches OFFICIAL in switch2.env. |
| RUN5 | Dustin's words "1-3 sure", "update if everything passes", "Alright it is fine to use the laptop over the weekend" | PLAN.md lines 24-29 | OK | Verbatim. |
| RUN5 | Both sittings passed Oct 11, records 7f7581ca and a9890744 | `git log` | OK | Commit subjects confirm. |
| RUN5 | 151,240 identity games; k3 and kp3 on all 45 cells | PIN_STATUS line 14 | OK | |
| RUN5 | Deck 10 t-weezing: 0 of 240 differ (wins 8 to 8) | PIN_STATUS line 16 | OK | |
| RUN5 | 8c: 1,133 changed; 511 on board; 621 look-ahead; 0 unexplained; 1 judgment | 8c_RESULT.txt | OK | 511+621+0+1 = 1,133. |
| RUN5 | Judgment game: step 9, Whimsicott v Sceptile, km3, Trap Territory, hand trace | 8c_DECISION.md | OK | Pairing 34, deal 449. |
| RUN5 | 16 pairings (32-39 h-whimsicott, 80-87 deck 12), 1,044 of 8,000 changed; other 80 pairings, Scizor and second lists unchanged | PIN_STATUS lines 24, 27 | OK | 66,500 played, 58,500 equal + 8,000 = 66,500. |
| RUN5 | `08a9b3a_cov_b2e_km3.jsonl` is the new reference | `step_9.sha256` line 1; `sha256sum` | OK | 84247fb4… |
| RUN5 | Line 415: Oct 2 engine, Sept 30 and Sept 28 engines kept | existing text and switch2.env | OK | |
| RUN5 | Line 418: FR_REL `results/floor_recheck_rules2_2026-10/`; Oct 2's `floor_recheck_2026-10/` | switch2.env; existing folder | OK | |
| RUN5 | Line 542 "rules switch 2 (Oct 11-12)"; line 571 engine path | CHANGES.md; diff | OK | |
| rules/09 | Hit-back entry stays open, moved under "Open engine bugs"; `:614-633` becomes `:774` | `git grep` at c7a25df4: `handle_attack_retaliation` at apply_action_helpers.rs:774 | OK | |
| rules/09 | Fix (1): Wild Swing and six other sites; commits e0ecf19f, 29e126a8, c7a25df4 (F1), 46953bf3, 3090abbb | engine_commits.tsv; e0ecf19f message | OK | Draft names Wild Swing, Wellspring Dance, Tornado Shot, Double Splash, Triple Bombardment, Mischievous Ring, Litter (seven attacks from six functions), plus Mega Kangaskhan ex separately. Consistent with the commit. CHANGES.md says "five gated sites" where the draft says "six other sites"; both count the same functions differently. Wording only. |
| rules/09 | (2) block coin = gate coin, Victory Star on its heads (46953bf3) | 46953bf3 message | OK | |
| rules/09 | (3)(4) Will carve-out gone (27a0c37d); (5) each Ariados adds 1 (5155ff7a, tests 05eb8492) | engine_commits.tsv | OK | |
| rules/09 | Revert switches commit 31616338 | engine_commits.tsv (31616338…) | OK | |
| rules/09 | "Also fixed" block: Guts (Ursaluna B3b 058, Conkeldurr A3 096), Perish Body (A4a 035), Luxury Coin (B4a 051) texts | `lib/card.py` | OK | Quoted card texts match. |
| rules/09 | P3's seven places listed | 140c0be2 message | OK | Scrounge-and-Scarf, Thieving Machine, Arven/Order Pad, Junk Spark, Crackling Snap, Scavenge, Treasure Collecting. |
| rules/09 | P2 5543a4ba +20; Bounded Field b0dc4844 doubles unless holder is Mega ex; P1 b8a8621a | commit messages | OK | |
| rules/09 | "Fixed Oct 1" headings and the two "Still open" lines reworded | diff | OK | Only those three lines change. |
| rules/04 | Line 61 two Ariados now ✓ (5155ff7a) | engine_commits.tsv | OK | |
| rules/04 | Line 76 Fossil as Item (3090abbb, 140c0be2) | commit messages | OK | |
| rules/04 | Lines 147 and 149: Victory Star with Will pending and after block coin ✓ (27a0c37d, 46953bf3) | commit messages; PLAN line 219-224 | OK | |
| rules/04 | New line 150: Mirror Shot text (B1a 026), Victory Star text (B3 025), Will text (A4 156), "seven other cards" | `lib/card.py`; `second_read_dbscan_output.txt` ("9 printings of 8 cards") | OK | 8 cards = Magnezone plus seven. |
| rules/04 | New line 151: Confusion coin vs block coin order, no shot-list row | PLAN line 402 (2b); SECOND_READ_sonnet.md note 5 | OK | |
| rules/02 | Line 60: Engine ✓ since main-@@MERGE_SHORT@@, `:774`, Tools and Abilities flat | 5543a4ba, b0dc4844; `git grep` at P | OK | Optional document (a noted extra), as CHANGES says. |
| READOUT | §4 "Done at the Oct 1 pin" (24374a00), listed items | `git show 24374a00 --stat`; Oct 1 `pin/docs/CHANGES.md` exists | OK | |
| READOUT | F4 comment ("has not been seen in Pocket") gone; test `...still_offers_victory_star` at `b4a_attack_batch2_test.rs`:456 | `git grep` at c7a25df4 | OK | No "has not been seen in Pocket" at P; test at :456. |
| READOUT | Victini caveat `card_validation.rs`:97-98 | P's file; CHANGES says 96-98 | OK | Arm starts at :96, caveat text on the next lines. CHANGES vs draft differ by one line; harmless. |
| READOUT | "All four are done"; PLAN checked the list | PLAN lines 219-224 | OK | |
| READOUT | §3b line "all four simulator-differs items fixed (27a0c37d, e0ecf19f, 5155ff7a)" | Commit ids exist | OK | Droppable extra, as CHANGES says. |
| READING | New reference file, sha256 84247fb4…, 16 rows, 1,044 of 8,000, other 80 equal, B = 1f6319e | step_9.sha256; PLAN §9 question 3a; PIN_STATUS line 24 | OK | |
| READING | "Dustin accepted the new reference in advance ('1-3 sure')" | PLAN lines 24-29, question 3a line 405 | OK | |
| switch README | P = c7a25df4, tree 70652fff; 26 files, 17 source + 9 tests; suite 2,103 passed, 0 failed (fc6307c0) | switch2.env; allowed_engine_files.tsv; SUITE_AT_P | OK | allowed file has 26 rows plus a header. |
| switch README | 13 `DECKGYM_*` revert switches | engine README list | OK | I counted 13 names in the engine README's list. |
| switch README | Sitting 1: 07:17-10:38 UTC, 199,400 games; sitting 2: 10:38-13:14, 137,090 games | PIN_STATUS | OK | |
| switch README | Step counts: 8b 2,800 games, 89 of 1,040 changed; step 8 54,750 / 0 of 26,250; step 9 74,500; 7c 20,160 | PIN_STATUS | OK | |
| switch README | 8c table 1,133 = 511 + 621 + 0 + 1; 111 CONDITION 3; 25 changed in the cloud's rows; 15:03-15:53 UTC | 8c_RESULT; 8c/README lines 5, 11, 22 | OK | 89 + 1,044 = 1,133. |
| switch README | "The laptop session ran 8c" | 8c/README "No agents" | OK | PLAN §7 had planned Sonnet for the traces; 8c/README says no agents were used. Wording follows the record. |
| switch README | Dustin's word at 980ca8c8, verbatim | 8c_DECISION.md | OK | |
| switch README | Heavy Helmet and the "left out" list (Disguise, Guts, Rescue Scarf, Lucky Egg, Rocky Helmet); bots 50/50 at `value_functions.rs`:1976/2011 | rules/09 entry; value_functions.rs | OK | Lines 1976 and 2011 exist and mention CoinFlipToBlockAttack. |
| switch README | B4b reprints, Victini caveat keyed by id | Oct 1 README "Next switch backlog" | OK | |
| engine README | Hashes 0a9199bc…, bf9d7502…, d8cfb779… and build time 07:23 UTC | programs.sha256; PIN_STATUS lines 4-7 | OK | Full 64-hex values match. |
| engine README | Watch build 60797708 | PIN_STATUS line 12 | OK | |
| engine README | Evidence counts (151,240; 28,000; 20,160; 2,800; 54,750; 74,500; 111 CONDITION 3; result 18e8020) | PIN_STATUS; 8c_RESULT | OK | |
| engine README | Luxury Coin "works only on the player's own Stadium" | 3090abbb message ("only for coins from the player's own Trainer cards") | OK | Slight paraphrase; same effect. |
| floor PLAN | Part A: 13,440 games, about 18 minutes (1,064 s) | Oct 2 timing.txt | OK | 5 decks × 1,920 + 2 × 8 × 240 = 13,440. I did not re-add the 1,064 s total. |
| floor PLAN | Oct 2 wins: 125, 262, 196, 577, 1,098 | `floor_recheck_2026-10/verdicts.txt` | OK | |
| floor PLAN | Old pages: deck 12 602; brew 07 1,168; brew 09 835; D 693 / 597 / 693; deck 10 324 | the page files | OK | Verdicts "clears" for all but deck 10 ("fail"). |
| floor PLAN | Part B 7,680 games; total 21,120 | arithmetic | OK | |
| floor PLAN | Goo-zooka is a Trainer (B4a 068) | `lib/card.py` | OK | |
| floor PLAN | "step 7c replayed ... 1,920 of 1,920 games each equal" | PIN_STATUS line 16, STATUS STEP 7c | OK | |

**Findings that are not mismatches, for the coordinator:**
1. CHANGES.md cites "pin/README line 84" as a source for START_HERE's engine line, but that line only lists the docs rule. PLAN §0/§2 and RELEASE (also cited) carry the content, so this is a citation slip only.
2. CHANGES.md counts rules/09's first fix as "Wild Swing and the five gated sites"; the draft text says "Wild Swing and the six other sites". The same attacks, counted two ways. Pick one before pinning if the wording matters.
3. Three new files (engine README, switch README, step 15 plan) go against START_HERE's "no new files unless Dustin asks", but PLAN steps 11-15 and the Oct 1 pin both call for them. I treat them as approved scope.
4. I did not re-run `pin_rules.sh --check` (CHANGES.md says it refuses until `switch2.env` is finalised; ENGINE_DIR, FR_REL and PIN_NOTED_EXTRA are now set, so it may run).
5. A draft that depends on a later step (the floor PLAN's `run_check.sh`, Part B runners) is flagged by CHANGES as not yet written; that is a step 15 item, not a pin-document defect.

**Verdict: ready to pin.** No MISMATCH and no UNSOURCED claim. Two optional wording fixes: the "pin/README line 84" citation (finding 1) and the "five/six sites" count (finding 2). Neither changes a pinned document's meaning.
