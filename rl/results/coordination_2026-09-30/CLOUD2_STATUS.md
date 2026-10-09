# Cloud 2 status (branch claude/slow-reports-runner-xlsxu0)

Written Oct 9 for the Fable coordinator session (Dustin's single delegator). The second cloud session; the first (CLOUD_STATUS.md) is not edited here. Times are UTC.

1. **Current task, and the instruction that set it.** Slow deck reports with the frozen kx3, one at a time, run exactly as the first one (draft A Wallace, `rl/results/slow_reports/2026-10-08_draft-A-wallace/` on branch claude/slow-report-draft-a-wallace) was run. Set by the Fable coordinator via Dustin's paste block, Oct 9.
   - Report 1: `decks/brews/brew-08-entei-rainbow-cave.txt`, `--deals 10 --threads 4 --school-rule off`. Question at the top of the report: how does brew 08 do against the 8 public lists when the frozen kx3 pilots it, and how much does kx3 add over km3 on the same deals; size 160 kx3 + 160 km3 games.
   - Report 2, after report 1: `decks/dustin/13-a-ninetales-raticate.txt`.
   - Not to be run: brew-07 and brew-09 (their rules are being repaired).
   - Rules I work under: never call `strength_prereg.py` directly; never set `SLOW_REPORT_ALLOW_UNCOMMITTED_PIN`; never use `--pin`; the pin is not edited; if anything is refused I STOP and write the message here.
   - Branch note: the session's branch is `claude/slow-reports-runner-xlsxu0` (the paste block says `claude/slow-reports-runner`); I push only to the one I was given.
2. **What is running now, and when it ends.** Report 1 (brew 08) is REGISTERED (Oct 9, 15:3x UTC, before any game; manifest sha256 cf90a886ef22; folder `rl/results/slow_reports/2026-10-09_brew-08-entei-rainbow-cave/`, pushed). The replay on this machine gave kx3 31d638dbc818b0fa and km3 81b572198c04d5d1, equal to the committed pin. Program `/root/slow_report_kx3/strength` (sha256 c3d51c4be7ff, a rebuild; rustc 1.97.0; engine tree 31dbd2e6e8ec, harness source bf9c5d68). Now playing in slices of `--max-games 40` (8 slices of 40 games across both arms, about 20 kx3 games each; 4 threads; estimate 4.7 to 6.2 hours of play in all), committing and pushing the folder between slices. Progress is the report folder's own commits on this branch ("slice k, N of 320 games played"; each slice is pushed when it ends); slice 1 (40 of 320) was pushed 16:24 UTC. A small driver script (outside the repo) plays the slices one after another and stops at any non-zero exit without retrying.
3. **Files I expect to change.** This file; the report folders `rl/results/slow_reports/<date>_brew-08-entei-rainbow-cave/` and, later, `<date>_13-a-ninetales-raticate/`. Nothing else (no pin, no engine, no scripts).
4. **Waiting on the laptop or Sonnet.** Nothing.
5. **Open questions for Dustin.** None yet.

## Log (one line per new job, added and pushed before it starts)

- 2026-10-09: setup for the slow reports (Fable via Dustin): cargo cache for d513e37b, build of the pinned source into `$HOME/slow_report_kx3/strength` (must print engine tree 31dbd2e6e8ec and harness source bf9c5d68), no games.
- 2026-10-09: report 1, brew 08 (Entei, Rainbow Cave): registration only, `--deals 10 --threads 4 --school-rule off`; replays both self-checks (hours), then the registered folder is pushed before any game.
- 2026-10-09: report 1, brew 08: playing the 320 registered games in slices of --max-games 40 (8 slices), report folder pushed between slices; the question, the size and the final numbers go in the folder's SLOW_REPORT.md.
- Direct route test received 2026-10-09T21:19Z; I am the Sonnet cloud; my session id is session_01LbhnEkPxKLoYA6VUG1N33k
