# Deck codes of Dustin's six newer Kingambit ladder games (QR_DECODE.json) and the import of their packets

The same job as `rl/results/ladder_qr_decode_2026-10-15/` (read that README for the method), for the games after the first four: he is at 10 ranked games with the list, 5-5.

| game | batch | result | code filmed at (source seconds) | where the scanned frame comes from |
|---|---|---|---|---|
| 20261016_015753000_iOS | BATCH_2026-10-15_NIGHT_LADDER_FOUR | L | 1.5 | **cut from the source video** (`qr_frame/t0001.50.png`); no kept frame scans |
| 20261016_020517000_iOS | BATCH_2026-10-15_NIGHT_LADDER_FOUR | W (concession) | 1.0 | **cut from the source video** (`qr_frame/t0001.00.png`); no kept frame scans |
| 20261016_020806000_iOS | BATCH_2026-10-15_NIGHT_LADDER_FOUR | L | 1.0 | Codex's own native frame `native/t0001.00.jpg` |
| 20261016_024253000_iOS | BATCH_2026-10-15_NIGHT_LADDER_FOUR | W | 0.5 | **cut from the source video** (`qr_frame/t0000.50.png`); its packet keeps 3 evidence frames, none with the code |
| 20261016_030833000_iOS | BATCH_2026-10-15_FINAL_LADDER_TWO | L | 1.25 | **cut from the source video** (`qr_frame/t0001.25.png`); its earliest kept frame is at 19 s |
| 20261016_031512000_iOS | BATCH_2026-10-15_FINAL_LADDER_TWO | L | 0.5 | **cut from the source video** (`qr_frame/t0000.50.png`); no early kept frame |

(The game ids are UTC times; the batches are named for the Chicago date.) A scan of every kept frame of 015753, 020517, 024253, 030833 and 031512 (and, for 020517, every image of the packet, also with upscaling and
contrast variants) found no code; the cut frames are lossless native 1170 x 2532 PNGs from the video, taken with ffmpeg `-ss T -frames:v 1` at the middle of the window in which the frame scans (0.25 s steps over the first
10 s; the windows are 0.25 s wide for 015753 and 0.5 to 1.25 s for the others). They sit in a new `qr_frame/` folder of each packet; images are not imported and the cleanup will take them with the other frames.

**020517's video was an online-only OneDrive placeholder** (270 MB; WSL reads of it fail with an input/output error, and a plain copy timed out). A retrying chunked read from Windows brought it down in the end; its SHA-256
(`4d98de32a83b...`) equals the one in the packet's SOURCE.json, so the frame is from the registered video. The scratch copy was deleted afterwards.

**Result:** all six receipts (`QR_DECODE.json` in each packet, written by the committed `decode_retained_qr.py`, schema `pause_batch_retained_qr_v1`, source SHA-256 from SOURCE.json) hold the same payload string, and it
decodes to card list **73dfed58d1d6** (`decks/dustin/01-kingambit-as-played.txt`): the same cards and Energy as the deck file by `journal.py`'s own `decode_payload`/`code_cards`. None differs: he did not change the list
between the first four games and these six. 20 slots, all entities resolved, encoder round trip exact in each. `verify_qr.py` and `verify_output.txt`.

**Import** (`tools/battle_logs_import_packets.py`, Windows Python against the repo over the UNC path, source read only; run twice, the second only to add 020517's receipt): 7,788 text files selected; 221 new and 2 changed on the
first run, 1 new on the second; MANIFEST.json updated; 6.1 MB in all, no images/videos/binaries, nothing that looks like a secret. Besides the six packets it carries what Codex wrote since the last import: `_recording_qa_root`
scripts for these batches and the 9 text files of `_not_in_a_batch/CLOUD_STORAGE/`.
