# Battle Logs cleanup (`tools/battle_logs_cleanup.py`)

Sonnet ("Opus agents progress"), Oct 14, for Fable and Dustin. Branch `sonnet/battle-logs-cleanup`. **Nothing has been deleted or moved: `--apply` and `--move-to` were never run, only the dry run (read-only).** This is the version after the laptop's adversarial review of the first tool (a65a535e); the fixes are listed at the end.

Codex's video frames (jpg/png) in `Battle Logs\Recording_QA` are choking OneDrive. This tool deletes the frames of game packets whose results are safely in the repo, and, separately, moves **only `Recording_QA`** (the frames and the packets) out of OneDrive. **The videos are not moved: they stay where they are, in OneDrive, so they keep their cloud copy.** It deletes nothing else.

## The retention rule

| what | rule |
|---|---|
| **Text outputs** (json, txt, md: ledgers, reviews, deck files, receipts, scripts) | permanent. The tool never deletes one. |
| **Frames** (jpg, jpeg, png inside a game packet) | may be deleted once their game is **in the repo**, its positions **passed review and a person accepted that** (below), the packet's own text outputs are still in its folder, and **the source video is still in Battle Logs**. Frames can be cut again from the video as long as the video stays. |
| **Videos** | stay while their game has an open shot-list or rules question and through its season. The tool never touches a video, and neither step moves one: none is inside `Recording_QA` (the 203 videos, 112 GB, are in `Reviewed\` and at the top of `Battle Logs\`), and `--move-to` takes only `Recording_QA`, so the videos stay in OneDrive with their cloud copy. Deleting videos is a separate decision this tool does not make. |

## "In the repo" is not what the first brief said: read this first

The brief said a batch's "ledger/packet files" are committed on main under `rl/results/pause_games_*`. **They are not.** `TURN_LEDGER.json`, `REVIEW.md`, `DECK_USED.json` and the rest of a packet exist only in `Recording_QA` (and OneDrive). What is committed is what was *derived* from them: per result folder a `games_meta.json` (game, title, the packet's folder `BATCH_x/<packet>`), `positions_all.json` (the converter's positions), the decks and the km3 tables. So the rule below uses "the game's positions are in the repo", and because the ledgers are not in the repo, the tool also requires the packet's text outputs to still be in the folder before its frames go (they are permanent; this only checks nobody removed them). The text outputs themselves are being copied into the repo by `tools/battle_logs_import_packets.py` (`rl/results/battle_log_packets/`), which the move step requires to be current.

There are **19** `BATCH_*` folders in `Recording_QA` (not 124), and **65,775** image files in all (about 46,300 in game packets of batches, 19,427 in 105 other folders such as `RETROSPECTIVE_HANDS_2026-10-02`, the old `*_sol` folders and `Luckycad_*`). Only the batches are in scope; the rest is listed in the dry run and never touched.

## The rule, per game packet

A **game packet** is a directory directly inside a `BATCH_*` folder whose name starts like `20261013_030351000_iOS`. Everything else in a batch (`__pycache__`, `qr_support`, `STALLED_INTAKE_LOCK_*`, `LIVE_UPDATE_*`, and image files at the batch level such as `LIVE_SAVE_SUMMARY.png`) is **never touched**, even in a batch that is deleted; the dry run counts them.

The frames of a game packet may go only when **all five** hold; the dry run prints the failing ones as the reason:

1. **In the repo, with positions.** `BATCH_x/<packet>` is the `folder` of a game in a `games_meta.json` committed under `rl/results/pause_games_*/` (any depth), and the `positions_all.json` in the same folder holds at least one position for that game. (Four games of BATCH_2026-10-06 are in a `games_meta.json` with **no** positions, because Codex found no exact 20-card list: 214518, 214731, 034229 and 012140. They stay, and the audit list keeps them in `pending`.)
2. **Audited.** The game is in the `games` of the committed audit list `rl/results/battle_logs_retention_2026-10-14/audited_games.json` under the same folder, **and the entry names the same `games_meta.json` and the same number of positions that the repo has now**. If a later commit changes either, the game is held back as "not audited as it is now". "Passed review" is a judgment about records, not something a program can read out of a markdown review, so it is a list a person owns (next section).
3. **Accepted** (checked by `--apply`; the dry run prints the status). The audit list's `confirmed` field is a structured acceptance of exactly the `games` listed now (below). A free-text string, `"no"`, `"pending"`, `"false"`, `"not yet"`, a number or a boolean is not an acceptance.
4. **Text outputs present.** `TURN_LEDGER.json`, `REVIEW.md` and `DECK_USED.json` exist in the packet and are not empty.
5. **Source video present.** The packet's `SOURCE.json` names its video (`video_basename`, `bytes`) and that file is in `Battle Logs` (top level or `Reviewed\`) with that size. A packet that does not say which video it came from is held back too.

**A packet that holds a second game keeps that game's frames.** A packet folder can contain another game (for example `20261006_012927000_iOS/game_02/`, which `RELATED_GAME_PACKETS.json` lists next to the first). The tool finds those (a `RELATED_GAME_PACKETS.json` path other than `.`; a `game_NN` folder; a sub-folder with its own `TURN_LEDGER.json` and a `SUMMARY.json` whose `game_id` differs from the packet's) and **never deletes their frames** unless that game passes by its own folder. The dry run lists each one as `stays <packet>/game_02: a second game recorded in the same packet`. Backup copies of the same game (`original_before_*`, `submitted_before_*`, `before_*`, `independent_sol`, `rejected_*`) are not second games and go with the packet.

"Committed" means read **from git at one commit**: the ref (default `origin/main`) is resolved to a commit once, and every file of the rule is read from that commit, not from the working tree, so a file that exists only on someone's disk or branch does not count. The report prints the commit and its date. `--apply` accepts only `origin/main` and also compares the local `origin/main` with `git ls-remote origin main`: if the remote is ahead (for example the audit list was revoked) it refuses and says to `git fetch origin`; if the remote cannot be reached it says so and goes on with the local one.

A batch is **DELETE** when every game packet in it passes, **PARTIAL** when some do, **keep** when none do or it has none. The unit of safety is the game packet; the batch line is a roll-up. This differs from the brief ("batches marked delete") on purpose: nearly every pause batch has a straggler (a game with no positions, a second game), and all-or-nothing would keep 6 GB of good frames in BATCH_2026-10-06 for the sake of 0.7 GB. `--whole-batches-only` restores the literal reading (only DELETE batches).

## The audit list and its acceptance (`rl/results/battle_logs_retention_2026-10-14/audited_games.json`)

Proposed by Sonnet from the records on main with `make_audited_games.py`; **it decides nothing until a person writes the acceptance into it and commits it to main.**

```
"confirmed": {"by": "<who>", "date": "YYYY-MM-DD", "games_sha256": "<what --audit-hash prints>"}
```

`python3 tools/battle_logs_cleanup.py --audit-hash` prints the hash of the `games` listed now (folder, games_meta and position count of each; the evidence text and `pending` are not part of it). Editing `games` (adding a game, changing a position count) makes the old hash wrong, so **an acceptance covers exactly the games it was made for**; moving an entry from `pending` to `games` needs a new acceptance. `by` must be a name (not "no", "pending", ...), `date` a real date.

- `games` (24, deletable once accepted): the games of `pause_games_new_2026-10-12/games_meta.json` (BATCH_2026-10-06, -09 and -11) **that have positions**. The laptop's first panel read all three batches against Codex's ledgers (`REVIEW_POSITIONS_laptop.md`, e9a7d35e: not ready), the converter fix was verified by the laptop's two panels (2eff1be6, 43b7d71d: every first-panel error fixed, byte-for-byte regeneration), and the positions regenerate identical after the Special Condition and knock-out change (28df6315, `REVIEW_PGFIX_laptop.md`). They are the positions the kx3 study ran on. Each entry records the `games_meta` file and the number of positions that were reviewed.
- `pending` (18, **not** deletable): the four no-position games above (tier `A0`: the review of the 125 positions cannot cover a game with none), and the 14 games of `pause_games_new_2026-10-13/v2/games_meta.json` (tier `B`: BATCH_2026-10-12 x2 and BATCH_2026-10-13 x2). The laptop's review of the 92 positions (373b41a6, `v2/REVIEW_POSITIONS_laptop.md`) found three wrong-card blockers and nine majors; the fix job is "positions v3", and the frames of those 14 packets stay until it passes review. **To release them (3.9 GB), move their entries from `pending` to `games` (with the reviewed games_meta and positions) and write a new acceptance.** That is the laptop's call.

## Running it

From PowerShell (Windows has no git on its PATH; the tool needs git, so it runs in WSL). **Write Windows paths with forward slashes (`C:/Users/...`) or as `/mnt/c/...`**: backslashes typed after `wsl` are eaten by the shell, and the tool refuses a path like `C:Usersdacz8...` instead of guessing.

```
wsl python3 /home/dacz8976/pgfix/tools/battle_logs_cleanup.py --ref sonnet/battle-logs-cleanup
```

After the laptop has integrated this branch into the checkout at `C:\Users\dacz8\Projects\Pocket Deck Sim\PocketDeckSim` (and fetched main there):

```
wsl python3 "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/tools/battle_logs_cleanup.py"
```

| flag | meaning |
|---|---|
| (none), `--dry-run` | the report only: a line per batch (verdict, games that pass / total, frames and size to delete, frames and size that stay, why), the reasons per held-back game, second games that stay, what is never touched, links and unreadable entries that were not examined, the totals. About two minutes (the folder is large and on OneDrive). With `--apply` it previews what `--apply` would do (with `--only`, just that batch). |
| `--apply` | delete the frames of the game packets that pass. Prints the plan, asks you to type `DELETE`; `--yes` skips the question. Refuses without a valid acceptance, with `--no-git`, and with any `--ref` other than `origin/main` (unless `--allow-ref-other-than-origin-main`, for a branch under review). |
| `--whole-batches-only` | with `--apply`: only the batches marked DELETE. |
| `--only BATCH` | the report shows only this batch (repeatable); with `--apply` only this batch is deleted, and it must have something to delete. Delete one batch, look, then the next. |
| `--audit-hash` | print the hash an acceptance must carry for the `games` listed now, and exit. |
| `--move-to PATH` | move only `Recording_QA` to PATH (below); the videos stay in OneDrive; refused unless the text outputs are committed in `rl/results/battle_log_packets/` at `--ref`. Separate from `--apply`: giving both is refused. |
| `--no-import-check` | with `--move-to`: skip that check (at your own risk). |
| `--qa-root PATH` | where `Recording_QA` is (default `C:/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA`, then `C:/Users/dacz8/BattleLogs/Recording_QA`). Use this flag after a move; an environment variable does not survive `wsl` from PowerShell without `WSLENV`, so there is none. |
| `--ref REF`, `--repo DIR`, `--no-git`, `-v` | which git ref counts as committed (default `origin/main`), which checkout, the working-tree preview (never for `--apply`), every reason. |

### What `--apply` removes, and what it cannot

- Only files ending `.jpg`, `.jpeg` or `.png` (any case), at any depth **inside a game packet that passes**, outside any second game recorded in that packet. Never json, txt, md, py or any other file; never a video; never an image at the batch level or in a non-game sub-folder; never anything outside `Recording_QA`; no folder is removed.
- The plan re-validates every path, and **again just before each deletion**: it is a regular file (not a symlink or junction), its folder still resolves, through real paths, to a place inside the packet, and the packet's three required text outputs are still there and non-empty. A packet whose text outputs vanished while the question was open is skipped (and logged), not deleted from.
- Links are never followed. Only *name-surrogate* reparse points count as links on Windows (symlinks and junctions); every OneDrive file carries a plain reparse attribute and is an ordinary file for this purpose.
- **Before the question** the tool lists every non-frame file of the packets with its size **and SHA-256**; after the deletion it lists them again. If one is missing or its content changed, it says `INTEGRITY CHECK FAILED` and exits non-zero.
- The log goes to `Recording_QA\CLEANUP_LOG_<UTC time>.jsonl`, written **line by line** (line-buffered, with an fsync at the start, at the end, and every 1,000 files): the header names the committed state and commit, who accepted, and each packet with its game key, `games_meta` and position count; then one line per file removed (written right after the removal), failures, skipped packets, and a last line with the totals and the integrity result. It is a text file, so it is permanent too.
- **If the run is interrupted** (Ctrl-C, `SIGTERM`, `SIGHUP` when the terminal closes) the log gets an `interrupted` line, the tool prints `interrupted: N deleted, integrity check not run`, and exits 130; run `--apply` again to finish (what was already deleted is simply not there).
- **Exit code:** 0 only when every planned frame was deleted and the integrity check passed. If some deletions failed (a file held open) or a packet was skipped, it prints `INCOMPLETE ...` and exits 1.
- Progress is printed every 1,000 files.
- OneDrive sees the deletions like any others and removes the files from the cloud (they stay in its recycle bin for a while).

## `--move-to PATH`: only Recording_QA

`--move-to C:/Users/dacz8/BattleLogs/Recording_QA` moves **only** the `Recording_QA` folder (the frames and the packets) out of `Battle Logs` to PATH, which becomes the new `Recording_QA` folder, and prints the path Codex should use. **The videos and everything else in `Battle Logs` (the 203 videos, 112 GB, `Reviewed\`, `Original_OBS_Recording\`, `MEDIA_LOCATIONS.json`, the review notes) stay where they are, in OneDrive.** The dry-run report and the move's own output both say so, and list what stays. It is a **rename on the same drive**: instant, nothing is copied, nothing can be half-moved. It refuses when:

- the folder to move is not named `Recording_QA` (the tool never moves `Battle Logs` itself or anything else);
- PATH is relative, or directly in a drive root (`C:/Recording_QA`), or already exists (even empty), or is inside `Recording_QA` (compared without regard to case, the way NTFS does), or neither its parent nor the folder above the parent exists (one missing parent folder is created, and the output says so; it is removed again if the rename fails);
- PATH has lost its backslashes on the way through `wsl` (a drive letter not followed by `/` or `\`);
- PATH is on another drive (that would be a copy of everything; the tool does not do it);
- the rename fails (something has files open: Codex, Explorer, OneDrive sync). Nothing is changed in that case.

It asks you to type `MOVE` and **repeats the target path in that prompt** (`--yes` skips this; with `--dry-run` it only prints the plan and warns if PATH is still inside a OneDrive folder). Before it moves it lists what will go stale and edits none of it: the scripts and text at the top of `Recording_QA` and of each batch that name the old `Battle Logs` path or `MEDIA_LOCATIONS.json` (a file that stays behind), and the repo's files that name `OneDrive\Desktop\Battle Logs`. It also says that scripts which reach files by a path *relative* to `Recording_QA` (`..\Reviewed`, `..\MEDIA_LOCATIONS.json`) cannot be found by a check and will break. After the move it prints the new `Recording_QA` path for Codex; run this tool afterwards with `--qa-root <that path>`.

**What leaves OneDrive: the import must be current before the move.** Moving `Recording_QA` out of OneDrive removes it from the cloud, including the packets' **text outputs** (ledgers, reviews, deck files, receipts). Those are the permanent part of the retention rule and existed nowhere else. They are copied into the repo by `tools/battle_logs_import_packets.py` (`rl/results/battle_log_packets/`, with a manifest; its README has the details), so GitHub is their backup. **Run that import again, commit it and get it into main immediately before the move, because Codex keeps writing new files** (the last check found 56 new and 3 changed text files). `--move-to` enforces this: it hashes every text output of `Recording_QA` and refuses unless each one is committed at `--ref` (default `origin/main`), byte for byte, under `rl/results/battle_log_packets/` (git's own blob ids are compared), and says how many are not; with `--dry-run` it only shows that. `--no-import-check` skips the check, at your own risk. **Pause OneDrive and close Codex's sessions before moving.**

## The dry run of Oct 14 (`dry_run_2026-10-14.txt`: this branch at 93f5c4e1, which contains main 373b41a6)

| batch | verdict | games | to delete | stays |
|---|---|---|---|---|
| 10-06 NEW_PAUSE_GAMES | PARTIAL | 13 of 17 | 12,741 frames, 5.87 GB | 663 MB: the four games with no positions and **game_02 of packet 012927 (142 frames, 55 MB)** |
| 10-09 NEW_PAUSE_GAMES | DELETE | 8 of 8 | 5,758 frames, 1.64 GB | |
| 10-11 NEW_PAUSE_GAMES | DELETE | 3 of 3 | 1,296 frames, 206 MB | |
| 10-12 ADDITIONAL_TWO, NEW_LONG_VIDEOS; 10-13 NEWEST_TWO, REMAINING_SIX | keep | 0 of 14 | | 3.9 GB: the 14 games not yet audited (`pending`; positions v3 first) |
| 10-02 DRAFT_A_V_BLASTOISE_WAILORD | keep | 0 of 8 | | 1.76 GB: not in a committed games_meta |
| 10-09 NEW_UPLOADS | keep | 0 of 8 | | 592 MB: no ledger yet |
| 10-14 NEW_LADDER_FOUR, OLDER_FOUR, OFFLINE_LADDER_FOUR, ADDITIONAL_TWO | keep | 0 of 14 | | 1.0 GB: ladder games, not processed into the repo |
| the other batch folders | keep | | | no game packets (a few image files at the batch level) |

**To delete by `--apply` (after acceptance and confirmation): 19,795 frames, 7.71 GB. Stays: 27,712 frames, 7.84 GB.** With `--whole-batches-only`: 7,054 frames, 1.84 GB. If the laptop releases the 14 pending games, 3.9 GB more. Not in scope: 19,427 images in 105 folders outside `BATCH_*` (e.g. `RETROSPECTIVE_HANDS_2026-10-02`, the old `*_sol` reviews); say so if those should follow the same rule.

## Tests

```
cd tools && python3 -B -m unittest -v test_battle_logs_cleanup      # 103 tests: made-up folder trees and throwaway git repos only
cd tools && python3 -B -m unittest -v test_battle_logs_import_packets   # 30 tests
```

They cover: the decision rule (each condition failing alone and together; a partial batch; a batch with no packets; support folders and batch-level images not deciding; names that are not game packets; an audit entry that names another folder or another games_meta or number of positions; no audit list committed; the source video missing, of another size, or not recorded), second games inside a packet (found through the related-packets file, through the folder name and through their own ledger with another game id; a backup copy is not one; their frames survive a real `--apply`; the plan refuses one of their frames), the acceptance (a table of valid and invalid values; the hash; editing `games` voids it; `--apply` refuses without one), the committed-state reading (only `pause_games_*` folders; positions must be next to the meta; a file that is only in the working tree is not committed; the commit is resolved once), the delete scope (frames at any depth and in any case go; nothing else does; symlinks are not followed; the plan refuses non-frame and out-of-scope paths; `--only`, partial and whole-batch modes), the log (line by line, header, progress, `SIGTERM`/Ctrl-C leave an `interrupted` line and exit 130, failures make the run incomplete), races between the plan and the deletion (a ledger removed while the question is open, a text file rewritten with the same size, a folder swapped for a link), the move (only `Recording_QA` is renamed; the videos untouched; every refusal in the list above; the import check) and the command line against a throwaway repo (the default changes nothing; `--apply` refuses `--no-git`, another ref, a "no" string, a stale acceptance and a remote that is ahead; exit code 1 when a delete fails; `--only` with `--dry-run`; `--audit-hash`).

## What changed after the laptop's review of a65a535e

Blocker: packets that hold a second game (scope-1). Majors: the acceptance is structured (gating-2); `--apply` reads only the committed state of `origin/main` (gating-1); the four no-position games are `pending`, and the audit entries carry and the tool checks games_meta and positions (gating-3); Windows paths through `wsl`, relative and drive-root move targets, the target in the `MOVE` prompt (platform-1); the log is written line by line, interruptions are logged, progress is printed (scope-2). Minors: SHA-256 inventory before the question and a per-packet text check just before deleting (scope-3); real-path check before each deletion (scope-4); reparse-point wording (scope-5, platform-3); source video check (scope-6); commit sha and game keys in the log (scope-7); no `BATTLE_LOGS_QA` hint through `wsl` (platform-2); non-zero exit when deletes failed (platform-4); case-insensitive move checks (platform-5); skipped links and unreadable entries counted, an unreadable packet is held (platform-6); ref resolved once, date printed, remote compared (gating-4); the acceptance tied to the games it covers (gating-5); `--apply --only X --dry-run` previews that batch (gating-6).

## Not done, not known

- **Windows is untested.** The tests and the dry run ran under WSL (Linux Python on `/mnt/c`). The Windows-only parts (reparse tags, `os.rename` on NTFS inside OneDrive) are written but have not run on Windows. That is why the README runs it through `wsl`.
- The audit list is Sonnet's proposal; no one has accepted it. The tool will not delete until someone does.
- Frames in the 105 folders outside `BATCH_*` and the videos are outside this tool. The text outputs are backed up by the separate import tool, which the move requires to be current.
- A game with positions in the repo can still have been converted from a ledger that is later corrected; its frames are then gone and only the video can answer. That is the cost of the rule and why videos stay through the season.
