# Four older recordings requested October 14, 2026

The four sources below match the owner's named October 2 and September 26 files. Original hashes and creation dates are bound in `SOURCE_INVENTORY.json` and per-source `SOURCE.json`. Prior intake and partial-review packets are preserved.

| Source filename | Result | Reviewed scope | Disposition |
| --- | --- | --- | --- |
| `20261002_011527000_iOS.MP4` | Computer win, 3-2; 14 turns; 490 damage | Setup through Victory; Auto briefly ON, including Water Shuriken resolution | Corrected independent acceptance, registration and hash-preserving move to Reviewed completed; space release pending sync |
| `20261002_012229000_iOS.MP4` | Computer loss, 2-3; 12 turns | AI setup through named Defeat result; Auto OFF observed | Independently accepted, registered and hash-preserving move to Reviewed completed; space release pending sync |
| `20260926_211809000_iOS.MP4` | Win against XaBy8 by opponent concession | Entire 43.463333-second late-match excerpt; setup, earlier turns and first owner point unavailable | Available footage independently accepted and registered partial; moved to Reviewed under explicit owner exception; release pending sync |
| `20260926_212155000_iOS.MP4` | Win against StefaGo by opponent concession | Entire 205.771927 seconds; setup and beginning of initial owner turn unavailable; no whole previous turn established | Available footage independently accepted and registered partial; moved to Reviewed under explicit owner exception; release pending sync |

The October filename dates are UTC creation dates. Their Chicago creation-derived match date is October 1, 2026, at 8:15 PM and 8:22 PM. The September clips have a September 26 Chicago date.

The separate 011527 check corrected the first draft's Auto timing. The control is hidden in the 338-second ability animation, visibly ON through 341 seconds, and OFF at 342 seconds. The interval is bounded by retained source frames. This matters for input authorship; it does not change computer classification or outcome. Rejected inputs and check receipt are preserved.

The StefaGo recheck corrects the earlier missing-ending claim: an explicit concession appears at 199.5-201 seconds and Dacz8976 Victory appears at 203.5/204 seconds. Its absent opening remains a real recording limit. XaBy8 also shows an explicit concession and named Victory.

Both computer battles are excluded from Ladder Log and Pause Games. The two September concession wins are prepared in [LADDER_CANDIDATES.md](LADDER_CANDIDATES.md) and `LADDER_CANDIDATES.json`. The live Ladder Log has not been checked for duplicate source filenames or changed this turn. After an initial automatic approval rejection, the owner explicitly approved a fresh browser retry and verified saves. Fresh browser inventory succeeded, but Chrome activation failed with GetCursorPos access denied; one bounded selection recovery then timed out during get_window_state. No external save occurred. See `EXTERNAL_STATUS.json`.

Routine archival requires full-battle completion. The owner explicitly approved an exception for these two completed excerpt reviews, while retaining their partial-battle status and missing-opening notes. `OWNER_EXCERPT_ARCHIVE_APPROVAL.json` and per-source `LEAD_ARCHIVE_EXCEPTION.json` bind that exception. It does not apply to any other partial source.

All four archive moves preserve source bytes and hashes. OneDrive metadata currently reports the four archived videos not in sync, so no unsafe space release was requested. They retain 1,776,398,998 allocated bytes. The completed written reviews and source-bound evidence remain locally available. `storage_release.py --apply --wait-seconds 45` performs a bounded metadata-only follow-up and releases space only after sync.

Each completed review has per-source independent and lead receipts. `REGISTRATION_RESULT.json` identifies normal append-only events; `MOVE_RECEIPT.*.json` binds archive hashes. `BATCH_COMPLETION_CHECK.json` reconciles source identity, index, location map and unrelated rows. `FINAL_STORAGE_CHECK.json` reports cloud sync and allocated storage without reading archived video contents. `MIRROR_RECEIPT.json` verifies the required Boss Folder evidence copy when completed.
