# The rules switch's pin (PLAN.md steps 11-13)

`pin_rules.sh` merges R (f8cfa9c) into main, copies the tested programs to `rl/engine-2026-10-02/`, updates the manifest, installs the reviewed documents and makes one pin commit. It plays no game, builds nothing and pushes nothing. It is adapted from `../../engine_switch_2026-09-30/pin.sh`, and its header lists every check. `update_manifest_rules.py` writes the new manifest for it.

## Before the pin

1. 8c passes and the coordinator audits it. Then the laptop writes `../8c_RESULT.txt` (below) and commits it.
2. The reviewed documents are in `docs/` (below).
3. `../../floor_recheck_2026-10/PLAN.md` is there (or drafted in `docs/`), and no game of the floor re-check has run.
4. Run the check in WSL. It changes nothing:

   ```
   bash "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/engine_switch_rules_2026-10/pin/pin_rules.sh" --check
   ```

   - Before `8c_RESULT.txt` is in, put `PIN_CHECK_WITHOUT_8C=1 ` in front. That skips only the 8c gate, and the check prints the exact line `8c_RESULT.txt` must hold.
   - It lists the uncommitted files of this switch's folder and `floor_recheck_2026-10/` that the pin commit will also carry. Anything there that shouldn't go in is moved out first. At the commit each must be unchanged, and nothing new may appear, or the pin stops.
   - It ends with `CHECK PASSED: nothing was changed`, or with `PIN STOPPED: <why>`.

## The pin

Run the same command without `--check`, at home (no games, a few minutes).
- **For those few minutes, no commits and no runs from anywhere else.** That includes GitHub Desktop and the other sessions. The pin's busy check only sees WSL processes. Main moves only from the value the pin read, and an undo checks whether another commit landed, but a commit made in the moment between the pin setting the shared index and moving main would carry the pin's files.
- It ends with `pin commit <sha> on merge <sha>. Not pushed.`
- A stop writes `PIN STOPPED: <why>` to `../PIN_STATUS.txt` and undoes what it had installed. Each file is re-checked just before it is overwritten.
- Once main is on the merge, the merge stays, the stop line says so, and a re-run carries on from there (it finds the merge by its `MERGING` or `MERGED` line). **Don't push while main is on the merge without the pin commit.**
- After a hard kill (the window closed, no stop line), restore the paths `git status` shows to main's first. That applies during the merge's install too, since main had not moved. Then re-run.

## After the pin (GitHub Desktop)

1. **Fetch origin.** If it then offers **Pull origin**, stop and ask the laptop session before pulling.
2. Otherwise **Push origin**.
3. Tell Sonnet, and the cloud through Dustin's paste block, the new engine name (main-<short>, `rl/engine-2026-10-02/`). km3 stays the working pilot.
4. Then the floor's pre-use re-check (PLAN.md step 15), as its `PLAN.md` says.

## `../8c_RESULT.txt`

One line, exactly:

```
8C PASS <Sonnet's result commit, 40 hex> rule verdicts: unexplained <u>, judgment <j>; all <u+j> accepted by Dustin <dates> as documented exceptions explained by A/B (8c_DECISION.md; <evidence>); net unaccounted 0; changed <n> accounted <n>; condition3 297 traced 297; 8b_rows_vs_cloud equal
```

- `<n>` is the number of changed games in `handoff_8c.tsv`: 3,813 (63 in 8b, 3,750 in 8). Both must equal it.
- 297 is the CONDITION 3 count in `handoff_8c.tsv` (296 + 1), the "297 flagged cases" of Dustin's word.
- The commit must be here (Fetch origin first).
- Other lines are free text (who audited it, when), but none may start with `8C`.
- The file must be committed and unchanged in the working copy.

The pin refuses if the file is missing, if it has no such line or more than one, or if any number is off.

PLAN.md's 8c row gives its evidence as "`touched_check.txt` complete, then PREPARE DONE". `8c_RESULT.txt` takes the place of `touched_check.txt` there: the pin writes the `PREPARE DONE` line from it (with the line itself) once every gate has passed.

## `docs/`

Each file in `docs/` is the full new text of the repository file at the same relative path (`docs/rl/RUN5.md` is `rl/RUN5.md`).
- `docs/DOCS.sha256`: `sha256sum` of each draft, paths relative to `docs/` (`<hash>  START_HERE.md`). Every file in `docs/` must be listed, except the two lists and `docs/CHANGES.md` (the drafter's notes: what changed and the source of each claim).
- `docs/BASE.sha256`: `sha256sum` of each target as it was when drafted, paths relative to the repository. A file that doesn't exist yet gets no line (or 64 zeros).
- Placeholders: `@@MERGE@@` (the merge commit, 40 hex) and `@@MERGE_SHORT@@` (its first 7). Any other `@@NAME@@` stops the pin.
- Only `.md` files, none under `engine/`. `START_HERE.md`, `CLAUDE.md`, `rl/RUN5.md` and this switch's `README.md` must be among them, and `START_HERE.md` and `CLAUDE.md` must name `rl/engine-2026-10-02`.
- A target outside this switch's folder and the floor re-check's must also be main's committed file.
- If a target changed after drafting (RUN5 moves often), the pin stops: re-draft, re-review, rewrite both lists, and run `--check` again.
- `rl/engine-2026-10-02/README.md` comes from `docs/` if it is drafted there, else from the pin's own text.

**The drafts are not committed** (`BASE.sha256`, `DOCS.sha256` and `CHANGES.md` are).
- They are copies of `START_HERE.md`, `CLAUDE.md` and RUN5 with placeholders in them. A second `CLAUDE.md` or `START_HERE.md` under `rl/results/` would be read by later sessions as instructions.
- The installed files are in the same commit, and `../PIN_STATUS.txt`'s DOCS line gives each draft's and each installed file's sha256.
- Once the pin commit is on main, the pin moves the drafts out of the repository, to `~/pin_rules_drafts_<merge short>/` in WSL, and says where. Then GitHub Desktop doesn't offer them for a commit, and no session reads them. They are not part of the record.
