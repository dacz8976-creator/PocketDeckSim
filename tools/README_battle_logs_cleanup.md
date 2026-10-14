# Battle Logs cleanup (`tools/battle_logs_cleanup.py`)

Sonnet ("Opus agents progress"), Oct 14, for Fable and Dustin. Branch `sonnet/battle-logs-cleanup`. **Nothing has been deleted or moved: `--apply` and `--move-to` were never run, only the dry run (read-only).**

Codex's video frames (jpg/png) in `Battle Logs\Recording_QA` are choking OneDrive. This tool deletes the frames of game packets whose results are safely in the repo, and, separately, moves **only `Recording_QA`** (the frames and the packets) out of OneDrive. **The videos are not moved: they stay where they are, in OneDrive, so they keep their cloud copy.** It deletes nothing else.

## The retention rule

| what | rule |
|---|---|
| **Text outputs** (json, txt, md: ledgers, reviews, deck files, receipts, scripts) | permanent. The tool never deletes one. |
| **Frames** (jpg, jpeg, png inside a game packet) | may be deleted once their game is **in the repo** and its positions **passed review** (below), and the packet's own text outputs are still in its folder. Frames can be cut again from the video as long as the video stays. |
| **Videos** | stay while their game has an open shot-list or rules question and through its season. The tool never touches a video, and neither step moves one: none is inside `Recording_QA` (the 203 videos, 112 GB, are in `Reviewed\` and at the top of `Battle Logs\`), and `--move-to` takes only `Recording_QA`, so the videos stay in OneDrive with their cloud copy. Deleting videos is a separate decision this tool does not make. |

## "In the repo" is not what the brief said: read this first

The brief said a batch's "ledger/packet files" are committed on main under `rl/results/pause_games_*`. **They are not.** `TURN_LEDGER.json`, `REVIEW.md`, `DECK_USED.json` and the rest of a packet exist only in `Recording_QA` (and OneDrive). What is committed is what was *derived* from them: per result folder a `games_meta.json` (game, title, the packet's folder `BATCH_x/<packet>`), `positions_all.json` (the converter's positions), the decks and the km3 tables. So the rule below uses "the game's positions are in the repo", and because the ledgers are not in the repo, the tool also requires the packet's text outputs to still be in the folder before its frames go (they are permanent; this only checks nobody removed them).

Two other numbers in the brief differ from the disk: there are **19** `BATCH_*` folders in `Recording_QA` (not 124), and **65,775** image files in all (about 46,300 in game packets of batches, 19,427 in 105 other folders such as `RETROSPECTIVE_HANDS_2026-10-02`, the old `*_sol` folders and `Luckycad_*`). Only the batches are in scope; the rest is listed in the dry run and never touched.

## The rule, per game packet

A **game packet** is a directory directly inside a `BATCH_*` folder whose name starts like `20261013_030351000_iOS`. Everything else in a batch (`__pycache__`, `qr_support`, `STALLED_INTAKE_LOCK_*`, `LIVE_UPDATE_*`, and image files at the batch level such as `LIVE_SAVE_SUMMARY.png`) is **never touched**, even in a batch that is deleted; the dry run counts them.

The frames of a game packet may go only when **all four** hold; the dry run prints the failing ones as the reason:

1. **In the repo.** `BATCH_x/<packet>` is the `folder` of a game in a `games_meta.json` committed under `rl/results/pause_games_*/` (any depth), and the `positions_all.json` in the same folder holds at least one position for that game. (Four games of BATCH_2026-10-06 are in a `games_meta.json` with **no** positions, because Codex found no exact 20-card list: 214518, 214731, 034229 and 012140. They stay.)
2. **Audited.** The game is in the `games` of the committed audit list `rl/results/battle_logs_retention_2026-10-14/audited_games.json` under the same folder. "Passed review" is a judgment about records, not something a program can read out of a markdown review, so it is a list a person owns (next section).
3. **Confirmed.** The audit list's `confirmed` field is not empty. This is checked by `--apply`, which refuses without it; the dry run only says `confirmed: NO`.
4. **Text outputs present.** `TURN_LEDGER.json`, `REVIEW.md` and `DECK_USED.json` exist in the packet and are not empty.

"Committed" means read **from git at `--ref`** (default `origin/main`), not from the working tree, so a file that exists only on someone's disk or branch does not count. Without git the tool refuses (`--no-git` reads the working tree and proves nothing; it is for tests and previews).

A batch is **DELETE** when every game packet in it passes, **PARTIAL** when some do, **keep** when none do or it has none. The unit of safety is the game packet; the batch line is a roll-up. This differs from the brief ("batches marked delete") on purpose: nearly every pause batch has a straggler (a game with no positions, a game not yet reviewed), and all-or-nothing would keep 6 GB of good frames in BATCH_2026-10-06 for the sake of 0.6 GB. `--whole-batches-only` restores the literal reading (only DELETE batches).

## The audit list (`rl/results/battle_logs_retention_2026-10-14/audited_games.json`)

Proposed by Sonnet from the records on main with `make_audited_games.py`; **it decides nothing until the laptop (or Fable, or Dustin) writes `confirmed` in it and commits it to main.**

- `games` (28, deletable once confirmed): every game of `pause_games_new_2026-10-12/games_meta.json` (BATCH_2026-10-06, -09 and -11). The laptop's first panel read all three batches against Codex's ledgers (`REVIEW_POSITIONS_laptop.md`, e9a7d35e: not ready), the converter fix was verified by the laptop's two panels (2eff1be6, 43b7d71d: every first-panel error fixed, byte-for-byte regeneration), and the 125 positions regenerate identical after the Special Condition and knock-out change (28df6315, `REVIEW_PGFIX_laptop.md`). They are the positions the kx3 study ran on.
- `pending` (14, **not** deletable): the games of `pause_games_new_2026-10-13/v2/games_meta.json` (BATCH_2026-10-12 x2 and BATCH_2026-10-13 x2). The reads and the checkup fix are integrated by the laptop (fb43ab9e, feddbce6, f6be4fd7), but no panel compared those 92 positions with their ledgers field by field, so I did not call them audited. **To release them (3.9 GB), move their entries from `pending` to `games` and commit.** That is the laptop's call.

## Running it

From PowerShell (Windows has no git on its PATH; the tool needs git, so it runs in WSL):

```
wsl python3 /home/dacz8976/pgfix/tools/battle_logs_cleanup.py --ref sonnet/battle-logs-cleanup
```

After the laptop has integrated this branch into the checkout at `C:\Users\dacz8\Projects\Pocket Deck Sim\PocketDeckSim` (and fetched main there):

```
wsl python3 "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/tools/battle_logs_cleanup.py"
```

| flag | meaning |
|---|---|
| (none), `--dry-run` | the report only: a line per batch (verdict, games that pass / total, frames and size to delete, frames and size that stay, why), the reasons per held-back game, what is never touched, the totals. About a minute (the folder is large). |
| `--apply` | delete the frames of the game packets that pass. Prints the plan, asks you to type `DELETE`; `--yes` skips the question. Refuses while the audit list is not confirmed. |
| `--whole-batches-only` | with `--apply`: only the batches marked DELETE. |
| `--only BATCH` | with `--apply`: only this batch (repeatable); it must have something to delete. Delete one batch, look, then the next. |
| `--move-to PATH` | move only `Recording_QA` to PATH (below); the videos stay in OneDrive. Separate from `--apply`: giving both is refused. |
| `--qa-root PATH` | where `Recording_QA` is (default `C:\Users\dacz8\OneDrive\Desktop\Battle Logs\Recording_QA`, then `C:\Users\dacz8\BattleLogs\Recording_QA`, or `$BATTLE_LOGS_QA`). Windows or `/mnt/c` style works from WSL. |
| `--ref REF`, `--repo DIR`, `--no-git`, `-v` | which git ref counts as committed (default `origin/main`), which checkout, the working-tree preview, every reason. |

### What `--apply` removes, and what it cannot

- Only files ending `.jpg`, `.jpeg` or `.png` (any case), at any depth **inside a game packet that passes**. Never json, txt, md, py or any other file; never a video; never an image at the batch level or in a non-game sub-folder; never anything outside `Recording_QA`; no folder is removed.
- Before the first deletion each path is checked again: it is a regular file (not a symlink, junction or OneDrive reparse point), it is under the packet, and the packet really is `Recording_QA/<batch>/<packet>`. A path that fails stops the run before anything is deleted.
- Links and junctions are never followed.
- Before and after, the tool lists every non-frame file of those packets with its size; if one is missing or changed afterwards, it says `INTEGRITY CHECK FAILED` and exits non-zero. (On the made-up trees this fires if a text file disappears during the run.)
- A log goes to `Recording_QA\CLEANUP_LOG_<UTC time>.jsonl`: one line per file removed (path relative to `Recording_QA`, bytes), failures, and a last line with the totals and the integrity result. It is a text file, so it is permanent too.
- OneDrive sees the deletions like any others and removes the files from the cloud (they stay in its recycle bin for a while).

## `--move-to PATH`: only Recording_QA

`--move-to C:\Users\dacz8\BattleLogs\Recording_QA` moves **only** the `Recording_QA` folder (the frames and the packets) out of `Battle Logs` to PATH, which becomes the new `Recording_QA` folder, and prints the path Codex should use. **The videos and everything else in `Battle Logs` (the 203 videos, 112 GB, `Reviewed\`, `Original_OBS_Recording\`, `MEDIA_LOCATIONS.json`, the review notes) stay where they are, in OneDrive.** The dry-run report and the move's own output both say so, and list what stays. It is a **rename on the same drive**: instant, nothing is copied, nothing can be half-moved. It refuses when:

- the folder to move is not named `Recording_QA` (the tool never moves `Battle Logs` itself or anything else);
- PATH already exists (even empty), is inside `Recording_QA`, or neither its parent nor the folder above the parent exists (one missing parent folder is created, and the output says so; it is removed again if the rename fails);
- PATH is on another drive (that would be a copy of everything; the tool does not do it);
- the rename fails (something has files open: Codex, Explorer, OneDrive sync). Nothing is changed in that case.

It asks you to type `MOVE` (`--yes` skips this; with `--dry-run` it only prints the plan and warns if PATH is still inside a OneDrive folder). Before it moves it lists what will go stale and edits none of it: the scripts and text at the top of `Recording_QA` and of each batch that name the old `Battle Logs` path or `MEDIA_LOCATIONS.json` (a file that stays behind), and the repo's files that name `OneDrive\Desktop\Battle Logs` (the Oct 12-13 read scripts and records; they stay valid as history, a new run needs the new path). It also says that scripts which reach files by a path *relative* to `Recording_QA` (`..\Reviewed`, `..\MEDIA_LOCATIONS.json`) cannot be found by a check and will break. After the move it prints the new `Recording_QA` path for Codex; run this tool afterwards with `--qa-root` (or `BATTLE_LOGS_QA`).

**What leaves OneDrive, and one thing to settle first.** Moving `Recording_QA` out of OneDrive removes it from the cloud, including the packets' **text outputs** (ledgers, reviews, deck files, receipts). Those are the permanent part of the retention rule and exist nowhere else: the repo holds only the positions derived from them (see above). Back the text files up before the move (or pause OneDrive while deciding); this tool does not do that. **Pause OneDrive and close Codex's sessions before moving.**

## The dry run of Oct 14 (this branch, `--ref sonnet/battle-logs-cleanup`, `dry_run_2026-10-14.txt`)

| batch | verdict | games | to delete | stays |
|---|---|---|---|---|
| 10-06 NEW_PAUSE_GAMES | PARTIAL | 13 of 17 | 12,883 frames, 5.93 GB | 608 MB (the four games with no positions) |
| 10-09 NEW_PAUSE_GAMES | DELETE | 8 of 8 | 5,758 frames, 1.64 GB | |
| 10-11 NEW_PAUSE_GAMES | DELETE | 3 of 3 | 1,296 frames, 206 MB | |
| 10-12 ADDITIONAL_TWO, NEW_LONG_VIDEOS; 10-13 NEWEST_TWO, REMAINING_SIX | keep | 0 of 14 | | 3.9 GB: the 14 games the laptop has not yet audited (`pending`) |
| 10-02 DRAFT_A_V_BLASTOISE_WAILORD | keep | 0 of 8 | | 1.76 GB: not in a committed games_meta |
| 10-09 NEW_UPLOADS | keep | 0 of 8 | | 592 MB: no ledger yet |
| 10-14 NEW_LADDER_FOUR, OLDER_FOUR, ADDITIONAL_TWO | keep | 0 of 10 | | 612 MB: ladder games, not processed into the repo |
| the 7 other batch folders | keep | | | no game packets (a few image files at the batch level) |

**To delete by `--apply` (after confirmation): 19,937 frames, 7.76 GB. Stays: 26,379 frames, 7.41 GB.** With `--whole-batches-only`: 7,054 frames, 1.84 GB. If the laptop releases the 14 pending games, 3.9 GB more. Not in scope: 19,427 images in 105 folders outside `BATCH_*` (e.g. `RETROSPECTIVE_HANDS_2026-10-02`, the old `*_sol` reviews); say so if those should follow the same rule.

## Tests

```
cd tools && python3 -B -m unittest -v test_battle_logs_cleanup      # 55 tests, made-up folder trees only
```

They cover: the decision rule (each of the four conditions failing alone and together; a partial batch; a batch with no packets; support folders and batch-level images not deciding; names that are not game packets; an audit entry that names another folder; no audit list committed), the committed-state reading (only `pause_games_*` folders; positions must be next to the meta; with git, a file that is only in the working tree is not committed), the delete scope (frames at any depth and in any case go; nothing else does: no json/txt/md/py, no video, nothing in a keep batch, in a non-game sub-folder, at the batch level, in the folder next to `Recording_QA` or in non-BATCH folders inside it; symlinks to files and folders are not followed; empty folders stay; a path outside, a non-frame path and a support-folder path are refused by the plan; unconfirmed audit, a "no", missing terminal and `--only` rules; the log; the integrity check catching a vanished text file), the move (only `Recording_QA` is renamed, with identical contents, and the videos and every other file of Battle Logs are untouched; the output says what stays; a folder not named `Recording_QA`, an existing target, a target inside, a target two levels below a missing folder, a dry run, a "no" and a failing rename leave everything in place; one missing parent is created and said, and removed again if the rename fails; scripts that name the old path are listed, not edited; a target still inside OneDrive is warned about) and the command line (the default changes nothing; `--apply` with an unconfirmed list refuses even with `--yes`; `--dry-run` wins over `--apply`).

## Not done, not known

- **Windows is untested.** The tests and the dry run ran under WSL (Linux Python on `/mnt/c`). The Windows-only parts (reparse points, `os.rename` on NTFS inside OneDrive, Windows path forms from PowerShell) are written but have not run on Windows. That is why the README runs it through `wsl`.
- The audit list is Sonnet's proposal; no one has confirmed it. The tool will not delete until someone does.
- Frames in the 105 folders outside `BATCH_*` and the videos are outside this tool. The packets' text outputs have no cloud copy once `Recording_QA` leaves OneDrive and no copy in the repo; backing them up is not done here.
- A game with positions in the repo can still have been converted from a ledger that is later corrected; its frames are then gone and only the video can answer. That is the cost of the rule and why videos stay through the season.
