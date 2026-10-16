# Deck codes of the four Kingambit ladder games of Oct 15, 2026 (QR_DECODE.json) and the import of their packets

Job from the coordinator (Oct 15): the journal's `add_played` refuses a packet without `QR_DECODE.json`, and the four packets were not on main.

| game | batch | code filmed at (source seconds) | retained image the receipt names | read by |
|---|---|---|---|---|
| 20261015_201201000_iOS | BATCH_2026-10-15_LADDER_TWO | 0.0 | `native/t0000.00.jpg` (Codex's frame) | ZXing on the native frame |
| 20261015_201850000_iOS | BATCH_2026-10-15_LADDER_TWO | 2.3 | `qr_frame/t0002.30.png` (cut from the source video, see below) | ZXing on the native frame |
| 20261015_205332000_iOS | BATCH_2026-10-15_LATE_LADDER_TWO | 0.0 | `evidence/t0000.00.jpg` (Codex's frame) | ZXing on the native frame |
| 20261015_210617000_iOS | BATCH_2026-10-15_LATE_LADDER_TWO | 1.5 | `qr_frame/t0001.50.png` (cut from the source video) | ZXing on the native frame |

**All four films show the deck's sharing code** (the "Share With 2D Pattern Code" popup, first seconds). Codex retained a scannable frame for two of them. For 201850 the only retained frame with the popup is a 390 px
"dense" frame (the code is whole but too small for ZXing, also with 2x upscaling); for 210617 the earliest retained frame (2.0 s) shows the popup still sliding up. For those two I cut one lossless native frame
(1170 x 2532 PNG) from the source video in `Battle Logs\Reviewed` (both pinned, local; their SHA-256 are the ones in SOURCE.json), with ffmpeg `-ss T -frames:v 1` at the time in the table (a 2.0 s frame of 201850 was
mid-transition and did not scan; 2.1 to 2.6 s do). These PNGs sit in a new `qr_frame/` folder of the packet (images are not imported to the repo, and the cleanup tool will remove them with the other frames; the
receipt keeps the frame's SHA-256, the source video's SHA-256 and the second).

**Receipts** were written with the committed `decode_retained_qr.py` of the Oct 6 support folder (`rl/results/battle_log_packets/BATCH_2026-10-06_NEW_PAUSE_GAMES/_batch/qr_support/`; Windows runtime Python, ZXing-C++,
the pinned payload codec, `s216_card_catalog_v1.json`), schema `pause_batch_retained_qr_v1`, one `QR_DECODE.json` in each packet (key `payload`, which `journal.py` reads), with `--source-sha256` from the packet's SOURCE.json.
Each receipt: 20 card slots, all entities resolved, Energy Darkness, round trip through the encoder exact.

**Check against the deck list** (`verify_qr.py`, `verify_output.txt`; it uses `rl/deck_journal/journal.py`'s own `decode_payload` and `code_cards` and the list id): the four payload strings are byte-identical, and the card set
and Energy they hold equal those of `decks/dustin/01-kingambit-as-played.txt`, card list id **73dfed58d1d6**. None differs.

**Import** (`tools/battle_logs_import_packets.py`, run with the Windows Python against the repo over the UNC path, because WSL ran out of memory scanning OneDrive while three cargo builds were running; source read only):
7,566 text files, 148.6 MB selected; 654 new, 6 changed, 6,906 unchanged; MANIFEST.json rewritten. The four packets are in `rl/results/battle_log_packets/BATCH_2026-10-15_LADDER_TWO/` and `.../BATCH_2026-10-15_LATE_LADDER_TWO/`.
It also brought in what Codex wrote since the last import: BATCH_2026-10-14_EVENING_LADDER, _LATE_LADDER_TWO, _NEWER_LADDER_FOUR, _NIGHT_LADDER_FOUR, more of _OFFLINE_LADDER_FOUR, Recording_QA's root scripts and
`CLEANUP_LOG_20261015T165404Z.jsonl`. No images, videos or binaries; the new and changed files total 14.2 MB, none looks like a secret (grep for keys, passwords, tokens).

**Odd or worth knowing**
- `CLEANUP_LOG_20261015T165404Z.jsonl` (now in the repo) records that `battle_logs_cleanup --apply` was run on Oct 15 at 16:54Z against origin/main 3eea18ee with the acceptance "Dustin via the laptop, 2026-10-14, games_sha256
  c161dea6...": 32,124 frames deleted, 11.59 GB freed, 0 failed. I did not run it.
- Receipts name OneDrive paths of images that the cleanup will delete later; the receipt still stands on the source video's SHA-256 and the second.
