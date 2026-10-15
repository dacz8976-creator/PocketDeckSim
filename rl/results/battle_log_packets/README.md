# Codex's packets: the text outputs, backed up in the repo

A byte-for-byte copy of the **text outputs** of Codex's work in `Battle Logs` (ledgers, reviews, deck files, receipts, scripts, the review notes, `MEDIA_LOCATIONS.json`), so that GitHub holds them before `Recording_QA` is moved out of OneDrive (`tools/battle_logs_cleanup.py --move-to`). Made by `tools/battle_logs_import_packets.py`; **do not edit anything here by hand**: a re-run repairs any file that differs from its source.

**What is here and what is not.** Only text: json, jsonl, txt, md, csv, tsv, log, html, py, ps1, sh, and the backups named like `README.md.before_completion`. **Never** images (the 65,000 video frames), videos or binaries, and nothing from the vendored dependency folders (`deps`, `qr_dependencies`, `zxingcpp`, `*.dist-info`, `__pycache__`). The videos stay in OneDrive.

**Layout.**

| folder | what it holds |
|---|---|
| `<BATCH_*>/<game packet>/...` | a game packet of a batch (for example `BATCH_2026-10-13_NEWEST_TWO/20261013_030351000_iOS/TURN_LEDGER.json`) |
| `<BATCH_*>/_batch/...` | files and non-packet folders directly in a batch folder (its README, receipts, `qr_support`) |
| `_not_in_a_batch/<folder>/...` | the older folders of `Recording_QA` that are not batches (the `*_sol` reviews, `RETROSPECTIVE_HANDS_2026-10-02`, ...) |
| `_recording_qa_root/...` | files at the top of `Recording_QA` (Codex's scripts) |
| `_battle_logs_root/...` | files at the top of `Battle Logs` (`MEDIA_LOCATIONS.json`, the review notes). They do not move with `Recording_QA`; they are copied as a backup |

**`MANIFEST.json`** lists every file: its source path under `Battle Logs`, SHA-256 and size. The manifest is deterministic (no timestamps). `.gitattributes` here turns off line-ending conversion (`* -text`), so the committed bytes are the source bytes on every machine and the SHA-256 holds in a Windows checkout too.

**First import (Oct 14):** 6,876 files, 136.8 MB (limit 200 MB; the tool refuses above it and names what is large). Skipped by design: 65,783 images (20.8 GB), 9 videos and 5 pictures at the top of `Battle Logs`, zip/wav/mp3 files, the vendored folders. The longest path is 251 characters in a Windows checkout of this repo (the tool skips anything over 255 and says so; none was skipped).

**Re-running it** (`python3 tools/battle_logs_import_packets.py`; about ten minutes, the folder is slow): new or changed files are copied again, unchanged files and the manifest are not rewritten, and a file whose source has gone **stays here** (marked `source_missing`): the copy is a backup and is never pruned. Codex keeps writing, so **the import must be current before the move**: run it again, commit, integrate into main, and `--move-to` then checks that every text output of `Recording_QA` is committed at `origin/main` byte for byte (git's blob ids), and refuses if not. `python3 tools/battle_logs_import_packets.py --check --ref origin/main` asks the same question without moving anything.

The source is only ever read.
