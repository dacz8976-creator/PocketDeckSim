# Cloud 3 status (branch claude/slow-reports-runner-2)

Written Oct 9 for the Fable coordinator session (Dustin's single delegator). The third cloud session, the second slow-report runner; CLOUD_STATUS.md and CLOUD2_STATUS.md are not edited here. Times are UTC.

1. **Current task, and the instruction that set it.** Slow deck reports with the frozen kx3, one deck at a time, run exactly as the first two were (recipe: CLOUD2_STATUS.md on branch claude/slow-reports-runner-xlsxu0). Set by the Fable coordinator via the direct CLI route, Oct 9.
   - Slow reports only. No engine change, no bot change, no pin edit. Never brew 07 or brew 09 (they wait for rules switch 2).
   - First deck: draft D, `decks/brews/drafts_2026-10-01/draft-D-entei-grimhound.txt` (as amended Oct 2), slot 629, seed_base 24,663,900,000, reserved on main in 2dfcb848.
   - Rules I work under: never call `strength_prereg.py` directly; never set `SLOW_REPORT_ALLOW_UNCOMMITTED_PIN`; never use `--pin`; if anything is refused I STOP and write the message here.
2. **What is running now.** Setup step 2: the replay of both self-checks on the rebuilt program (km3 first, then kx3; hours), no other games.
   - Step 1 is DONE (Oct 9, 21:54 UTC): the build printed engine tree 31dbd2e6e8ecd39f6756b15cdb86f48b1c8f8588 and harness source bf9c5d6814007f1f53b0dc06f1beba02261478ddc40bb5efa3bbc16c0734f86e (both as required); program `$HOME/slow_report_kx3/strength`, sha256 c3d51c4be7ff27615359db71d09b2de0867aed773b0c8434d46dea7b7e73a9de (a rebuild, rustc 1.97.0, build record `strength.build.json` beside it).
3. **Files I expect to change.** This file; later the report folder `rl/results/slow_reports/<date>_<draft-D>/`. Nothing else.
4. **Waiting on the laptop.** Nothing. The reservation is on main (2dfcb848, names draft D, slot 629). I merged main into this branch (text only: START_HERE.md); the deck file `decks/brews/drafts_2026-10-01/draft-D-entei-grimhound.txt` has sha256 31035755a6d0… as stated. The dry run of the registration picked seed_base 24,663,900,000 by itself (no --seed-base), as expected. I register after both setup self-checks pass.
5. **Open questions for Dustin.** None yet.

## Log (one line per step, added and pushed before it starts)

- 2026-10-09: setup step 1: cargo cache for the pinned source d513e37b, build into `$HOME/slow_report_kx3/strength` (must print engine tree 31dbd2e6e8ec and harness source bf9c5d68), no games.
- 2026-10-09: setup step 1 DONE (engine tree 31dbd2e6e8ec, harness source bf9c5d68, program sha256 c3d51c4be7ff). Setup step 2: replay of both self-checks (km3, then kx3) on the rebuilt program, the same command `slow_report.py` runs (`strength selfcheck --pilot SPEC --deck-a t-altaria --deck-b t-suicune --games 12`, scrubbed environment, nice 19), run on its own; no games beyond these 24 self-check games.
- 2026-10-09: setup step 2 running: km3 self-check started 21:54Z, kx3 follows. Reservation for draft D found on main (2dfcb848); dry run of the registration printed seeds from 24663900000 (as required) and size 160 kx3 + 160 km3 games.
- 2026-10-09: the container restarted twice during the kx3 self-check replay (it cannot resume, so each restart loses it): first started 21:55Z, restarted 22:28Z; the second run, lost at the next restart before 23:43Z. Started again 23:43Z. The km3 replay is done and equals the pin (81b572198c04d5d1). If restarts keep killing the replay, the replay may never finish on this container; I will keep restarting it and say so here.
- 2026-10-09 23:46Z, evidence on the restarts (Fable asked): at 23:45:51Z `uptime` said up 2 min, so the container itself restarted (about 23:43Z); it was not a process kill. Memory is not the cause: 16,093 MB total, 472 MB used, 15,533 MB free, no swap, 4 cores; the replay process uses about 23 MB. dmesg shows only the boot messages, no OOM line; no journal; no cgroup memory files. The replay (attempt three, started 23:43:18Z) is alive. Fewer threads would not help, so I did not change them. I now wait in a foreground loop (progress every 5 minutes) so the session stays active.
