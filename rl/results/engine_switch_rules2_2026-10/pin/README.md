# Rules switch 2's pin (PLAN.md steps 11-14, and the hand-off to step 15)

`pin_rules.sh` merges P (the final engine commit of `claude/coin-prevention-round2`, `../switch2.env`'s `P`) into main, copies the tested programs to `rl/engine-<the pin's date>/` (`switch2.env`'s `ENGINE_DIR`), updates the manifest, installs the reviewed documents and makes one pin commit. It plays no game, builds nothing and pushes nothing. It is a copy of `../../engine_switch_rules_2026-10/pin/pin_rules.sh` (the Oct 1 switch's pin, which made main-8626a35), adapted for switch 2, and its header lists every check and every change. `update_manifest_rules.py` writes the new manifest for it.

## Before the pin

1. 8c passes and the coordinator audits it. Then the laptop writes `../8c_RESULT.txt` (below) and commits it. If it has any game the rule left unexplained or any judgment call, Dustin's word comes first (PLAN.md section 6), and `../8c_DECISION.md` records it, his words verbatim. The same holds when step 7c reported deck 10's t-weezing floor row changed and no changed game of its Will row (step 8, pairing 60) shows `will_confused_attack`: PLAN.md section 3 judges that floor row through the Will row, so that is a judgment call too.
2. The data files in `..` are final and committed. The pin needs every value: no `# TO FINALIZE` first line in a `.tsv`, and no `TO_FINALIZE` in `switch2.env`. The laptop session sets three values for the pin itself:
   - `ENGINE_DIR=rl/engine-<the pin's date>` (a new folder, never `rl/engine-2026-10-02`);
   - `FR_REL=rl/results/<step 15's folder>` (a new folder: `../../floor_recheck_2026-10/` already holds the Oct 2 re-check's games);
   - `PIN_NOTED_EXTRA=<path>,<path>`, the files holding Sonnet's note 8's stale items and km3's new B2e reference for the 16 rows (question 3a). PLAN.md steps 11-14 list them among the pin's documents, so each must be drafted in `docs/`; the pin refuses to start without this value (`--check` prints a NOTE).
3. The reviewed documents are in `docs/` (below).
4. Step 15's `PLAN.md` is in `FR_REL` (or drafted in `docs/`), and no game of step 15 has run.
5. No `DECKGYM_*` variable is set (nor `PDL_EQUIV_DEALS` or `GOLDFISH_TRACE`). At P the engine reads its revert switches from the environment; the pin refuses to start with one set.
6. Run the check in WSL. It changes nothing:

   ```
   bash "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/engine_switch_rules2_2026-10/pin/pin_rules.sh" --check
   ```

   - Before `8c_RESULT.txt` is in, put `PIN_CHECK_WITHOUT_8C=1 ` in front. That skips only the 8c gate, and the check prints the exact line `8c_RESULT.txt` must hold.
   - When a judgment call waits for Dustin's word (above), put `PIN_DUSTIN='<his words>' ` in front (the check needs it too). The words must be in the committed `8c_DECISION.md` as he gave them (spaces and line breaks aside), or the pin stops.
   - It lists the uncommitted files of this switch's folder and step 15's folder that the pin commit will also carry. Anything there that shouldn't go in is moved out first. At the commit each must be unchanged, and nothing new may appear, or the pin stops.
   - It ends with the STEP 15 HANDOFF line, then `CHECK PASSED: nothing was changed`, or with `PIN STOPPED: <why>` (or `start refused: <why>`, which writes nothing).

## The pin

Run it without `--check`, at home (no games, a few minutes), with the same `PIN_DUSTIN` if one was needed, through `rl/strength/launch_detached.sh` like every run that must outlive the process that starts it (a closed window or a tool call's time limit could otherwise cut it mid-install, with no trap run):

```
bash rl/strength/launch_detached.sh start rules2-pin --dir "$R" -- bash "$R/rl/results/engine_switch_rules2_2026-10/pin/pin_rules.sh"
```

(`R` is the repository's WSL path; `launch_detached.sh status rules2-pin` and its log `~/runs/rules2-pin.log` show how it ended.)
- **For those few minutes, no commits and no runs from anywhere else.** That includes GitHub Desktop and the other sessions. The pin's busy check sees WSL processes and `launch_detached.sh`'s live runs in this working copy only. Main moves only from the value the pin read, and an undo checks whether another commit landed, but a commit made in the moment between the pin setting the shared index and moving main would carry the pin's files.
- It ends with `pin commit <sha> on merge <sha>. Not pushed.`
- A stop writes `PIN STOPPED: <why>` to `../PIN_STATUS.txt` and undoes what it had installed. Each file is re-checked just before it is overwritten.
- Once main is on the merge, the merge stays, the stop line says so, and a re-run carries on from there (it finds the merge by its `MERGING` or `MERGED` line). **Don't push while main is on the merge without the pin commit.**
- After a hard kill (the window closed, no stop line), restore the paths `git status` shows to main's first. That applies during the merge's install too, since main had not moved. Then re-run.

## After the pin (GitHub Desktop), and step 15

1. **Fetch origin.** If it then offers **Pull origin**, stop and ask the laptop session before pulling.
2. Otherwise **Push origin**.
3. Tell Sonnet and the cloud sessions the new engine name (main-<short>, `rl/engine-<date>/`). km3 stays the working pilot, and no `DECKGYM_*` variable is ever set in a recorded run.
4. Then step 15 (PLAN.md step 15; the pin writes the same list to `../PIN_STATUS.txt` as its STEP 15 HANDOFF line). Each new page goes to Dustin beside its old one, and a new failure or judgment call stops and goes to him:
   1. the floor's pre-use re-check under km3, as `FR_REL/PLAN.md` says (about 13,400 games);
   2. deck 12's new page (1,920 games);
   3. draft D's victini-passive page, remade the way it was made on Oct 2: its copy rebuilt from `floor_copy.diff` and run through `run_copy.py` on D's first list (1,920);
   4. brew 07's and brew 09's new pages (2 × 1,920). Until then their conclusions stay provisional (Dustin, Oct 7; PLAN.md section 0);
   5. D's root and amended pages (text), from step 7c's replays (`../floor_7c/D_root/` and `../floor_7c/D_amended/`);
   6. deck 10's new page, only if step 7c's page check reported a difference in its t-weezing row (`../floor_7c/10/`; STATUS.txt's STEP 7c line).
   
   Then kx3 is rebuilt on the new engine and checked, and the slow report's program is rebuilt, its self-checks replayed, and pinned again (RELEASE_PACKAGE.md, "The order").

## `../8c_RESULT.txt`

One line, exactly:

```
8C PASS <the 8c result commit, 40 hex> verdicts: on_board <b>, lookahead <l>, unexplained <u>, judgment <j>; both_halves <l> of <l>; revert <l> of <l> reproduced; condition3 <c> traced <c>; none <z> traced <z>; other_only <o> traced <o>; changed <n> accounted <n>; dustin <u+j> (8c_DECISION.md); net unaccounted 0; 8b_rows_vs_cloud equal
```

- `<n>` is the number of rows in `../handoff_8c.tsv`. It must equal the sum of the `changed <N> of <M> deals` phrases of the last STEP 7c, 8b, 8 and 9 DONE lines, step by step (each step's rows in the hand-off against its own line). `handoff_8c.tsv` itself must be exactly its per-set files (`handoff_<set>.tsv`, each in its step's manifest) put together.
- `b + l + u + j = n`: every changed game has one verdict.
- `both_halves <l> of <l>` and `revert <l> of <l>`: every look-ahead game meets both halves (the code gate, and coin_probe v2 finding the condition inside the bots' search at the first differing tick) and the revert check reproduces the old choice and scores (PLAN.md section 6, change 3). A game that fails either is a stop, so it can't be among them.
- `<c>` is the hand-off's CONDITION 3 count: its rows with category `offgate_only` (only round 2's off-gate counters fired; the Oct 1 ruling, carried by Dustin's yes to question 1).
- `<z>` and `<o>` are the hand-off's rows with category `none` (no counter fired at all) and `other_only` (only round 1's or a superset's counters), each traced. The last plan's mechanic check said a game with every counter 0 must be identical; the reading that admits such a game when it is explained in look-ahead (as the cloud's 8b found for k3 pairing 37 i 35) is the coordinator's to record before sitting 2, as the condition-3 ruling was on Oct 1.
- `dustin <u+j>`: the games that need Dustin's word. When it is above 0 (or another judgment call waits, see "Before the pin"), `../8c_DECISION.md` must be committed and unchanged, and the pin runs only with `PIN_DUSTIN='<his words>'`, words that are in `8c_DECISION.md` (noted in PIN_STATUS.txt as `PIN DUSTIN: ...`, and quoted in the manifest, the engine README and the pin commit).
- Numbers are plain (no commas, no leading zeros). The commit must be here (Fetch origin first).
- Other lines are free text (who audited it, when, the cloud's cross-check), but none may start with `8C`.
- The file must be committed and unchanged in the working copy.

The pin refuses if the file is missing, if it has no such line or more than one, or if any number is off.

PLAN.md's 8c row gives its evidence as "touched_check.txt complete, then PREPARE DONE". `8c_RESULT.txt` takes the place of `touched_check.txt` there: the pin writes the `PREPARE DONE` line from it (with the line itself) once every gate has passed.

## `docs/`

Each file in `docs/` is the full new text of the repository file at the same relative path (`docs/rl/RUN5.md` is `rl/RUN5.md`).
- `docs/DOCS.sha256`: `sha256sum` of each draft, paths relative to `docs/` (`<hash>  START_HERE.md`). Every file in `docs/` must be listed, except the two lists and `docs/CHANGES.md` (the drafter's notes: what changed and the source of each claim).
- `docs/BASE.sha256`: `sha256sum` of each target as it was when drafted, paths relative to the repository. A file that doesn't exist yet gets no line (or 64 zeros).
- Placeholders: `@@MERGE@@` (the merge commit, 40 hex) and `@@MERGE_SHORT@@` (its first 7). Any other `@@NAME@@` stops the pin.
- Only `.md` files, none under `engine/`. PLAN.md steps 11-14's documents must be among them: `START_HERE.md`, `CLAUDE.md`, `rl/RUN5.md`, this switch's `README.md`, `rules/09_engine_repairs_2026-09-22.md` (its open entries closed), `rules/04_actions_cards_effects.md` (§9's Victory Star lines and the note on the two gate coins, question 2b), `rl/results/rules_recordings_2026-10-01/READOUT.md` (§4's stale items) and the files of `PIN_NOTED_EXTRA`. `START_HERE.md` and `CLAUDE.md` must name `ENGINE_DIR`, and `START_HERE.md` must keep this switch's seed row (a line holding 23,300,000,000).
- `rules/02` (P2's rule) and this switch's `PLAN.md` are not in PLAN.md's list: a missing draft of one of them is a NOTE, not a stop.
- A target outside this switch's folder and step 15's must also be main's committed file. A path the merge brings (P's records in this folder) can't be drafted.
- If a target changed after drafting (RUN5 moves often), the pin stops: re-draft, re-review, rewrite both lists, and run `--check` again.
- `rl/engine-<date>/README.md` comes from `docs/` if it is drafted there, else from the pin's own text.

**The drafts are not committed** (`BASE.sha256`, `DOCS.sha256` and `CHANGES.md` are).
- They are copies of `START_HERE.md`, `CLAUDE.md` and RUN5 with placeholders in them. A second `CLAUDE.md` or `START_HERE.md` under `rl/results/` would be read by later sessions as instructions.
- The installed files are in the same commit, and `../PIN_STATUS.txt`'s DOCS line gives each draft's and each installed file's sha256.
- Once the pin commit is on main, the pin moves the drafts out of the repository, to `~/pin_rules2_drafts_<merge short>/` in WSL, and says where. Then GitHub Desktop doesn't offer them for a commit, and no session reads them. They are not part of the record.
