# Cloud 2 status (branch claude/slow-reports-runner-xlsxu0)

Written Oct 9 for the Fable coordinator session (Dustin's single delegator). The second cloud session; the first (CLOUD_STATUS.md) is not edited here. Times are UTC.

1. **Current task, and the instruction that set it.** Slow deck reports with the frozen kx3, one at a time, run exactly as the first one (draft A Wallace, `rl/results/slow_reports/2026-10-08_draft-A-wallace/` on branch claude/slow-report-draft-a-wallace) was run. Set by the Fable coordinator via Dustin's paste block, Oct 9.
   - Report 1: `decks/brews/brew-08-entei-rainbow-cave.txt`, `--deals 10 --threads 4 --school-rule off`. Question at the top of the report: how does brew 08 do against the 8 public lists when the frozen kx3 pilots it, and how much does kx3 add over km3 on the same deals; size 160 kx3 + 160 km3 games.
   - Report 2, after report 1: `decks/dustin/13-a-ninetales-raticate.txt`.
   - Not to be run: brew-07 and brew-09 (their rules are being repaired).
   - Rules I work under: never call `strength_prereg.py` directly; never set `SLOW_REPORT_ALLOW_UNCOMMITTED_PIN`; never use `--pin`; the pin is not edited; if anything is refused I STOP and write the message here.
   - Branch note: the session's branch is `claude/slow-reports-runner-xlsxu0` (the paste block says `claude/slow-reports-runner`); I push only to the one I was given.
2. **What is running now, and when it ends.** Setup: one fixed clone path (`/home/user/PocketDeckSim`), main merged (branch is level with main b77652d), cargo cache for the pinned commit, then the build into `$HOME/slow_report_kx3/strength`. Then the dry run and the registration (the kx3 and km3 self-check replay, hours). Nothing is playing yet.
3. **Files I expect to change.** This file; the report folders `rl/results/slow_reports/<date>_brew-08-entei-rainbow-cave/` and, later, `<date>_13-a-ninetales-raticate/`. Nothing else (no pin, no engine, no scripts).
4. **Waiting on the laptop or Sonnet.** Nothing.
5. **Open questions for Dustin.** None yet.

## Log (one line per new job, added and pushed before it starts)

- 2026-10-09: setup for the slow reports (Fable via Dustin): cargo cache for d513e37b, build of the pinned source into `$HOME/slow_report_kx3/strength` (must print engine tree 31dbd2e6e8ec and harness source bf9c5d68), no games.
