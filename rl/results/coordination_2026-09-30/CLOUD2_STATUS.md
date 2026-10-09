# Cloud 2 status (branch claude/slow-reports-runner-xlsxu0)

Written Oct 9 for the Fable coordinator session (Dustin's single delegator). The second cloud session; the first (CLOUD_STATUS.md) is not edited here. Times are UTC.

1. **Current task, and the instruction that set it.** Slow deck reports with the frozen kx3, one at a time, run exactly as the first one (draft A Wallace, `rl/results/slow_reports/2026-10-08_draft-A-wallace/` on branch claude/slow-report-draft-a-wallace) was run. Set by the Fable coordinator via Dustin's paste block, Oct 9.
   - Report 1: `decks/brews/brew-08-entei-rainbow-cave.txt`, `--deals 10 --threads 4 --school-rule off`. Question at the top of the report: how does brew 08 do against the 8 public lists when the frozen kx3 pilots it, and how much does kx3 add over km3 on the same deals; size 160 kx3 + 160 km3 games.
   - Report 2, after report 1: `decks/dustin/13-a-ninetales-raticate.txt`.
   - Not to be run: brew-07 and brew-09 (their rules are being repaired).
   - Rules I work under: never call `strength_prereg.py` directly; never set `SLOW_REPORT_ALLOW_UNCOMMITTED_PIN`; never use `--pin`; the pin is not edited; if anything is refused I STOP and write the message here.
   - Branch note: the session's branch is `claude/slow-reports-runner-xlsxu0` (the paste block says `claude/slow-reports-runner`); I push only to the one I was given.
2. **What is running now, and when it ends.**
   - **Report 1 (brew 08, Entei / Rainbow Cave) is FINISHED** (Oct 9, 21:40 UTC; all 320 games, 0 game errors; 6.0 h over 8 sittings; pushed in d3d0844b). Folder `rl/results/slow_reports/2026-10-09_brew-08-entei-rainbow-cave/`, page `SLOW_REPORT.md`, numbers `REPORT.md`.
     - Plain reading: with kx3 playing it against the 8 public lists, brew 08 scored **75.6%** over 160 games (probably between 68.4% and 81.6%). On the same deals km3 playing it scored 62.5%, so kx3 adds **+13.1 points** (probably between +6.1 and +20.2; the range does not include no gain).
     - By list (20 games each): t-vespiquen 95%, t-hydreigon, t-sceptile, t-suicune and t-weezing 85% each, t-altaria and t-lucario 65% each, **t-blaziken 40%** (the one list it lost to, range 22% to 61%). First 71.6% (74 games), second 79.1% (86 games).
     - It is the optimistic end (kx3 knows its opponent is one of the 8 lists); not a ranking, no pass or fail line, and a 20-game row can tell an easy list from a hard one, not two similar lists apart.
     - Registration check: the replay on this machine gave kx3 31d638dbc818b0fa and km3 81b572198c04d5d1, equal to the committed pin. The program is a rebuild (sha256 c3d51c4be7ff, rustc 1.97.0, engine tree 31dbd2e6e8ec, harness source bf9c5d68), not the laptop's pinned binary.
   - **Report 2 (deck 13, Ninetales / Raticate)**: the first registration try (started 21:41 UTC) was killed by a container restart at about 22:55 UTC, before it wrote anything (no deck 13 folder, nothing to resume). After the restart the clone, the built program (sha256 c3d51c4be7ff, same build record) and the cargo cache were all still in place, so no rebuild was needed. Registration restarted 22:58 UTC with the same command (`--register-only`, `--deals 10 --threads 4 --school-rule off`): it replays both self-checks again (about 2 hours), then the registered folder is pushed before any game, then slices of `--max-games 40`.
   - **Restart diagnosis (Fable's Oct 9 night request: reclaim or out-of-memory?).**
     - First restart: the machine came back at about 22:56 UTC (`uptime` 22:56:45: "up 0 min", load 0.07). It had been running deck 13's first registration try since 21:41 UTC, and I had only a watch armed (an hour between checks), no foreground wait.
     - The old boot's logs did not survive the restart (`journalctl`: no journal files; `dmesg` shows only the new boot), so the cause of that one cannot be read back. The first try's replay log ends without any kill or error line.
     - Second try, started 22:57 UTC. At 23:48:21 UTC: `uptime` up 51 min, load 3.54, `free -m` total 16094, used 493, free 15504, available 15601, swap 0; the kx3 self-check process holds about 28 MB; `dmesg` has no "out of memory" or "killed process" line; memory pressure (PSI) total 0 since boot. So nothing in this boot looks like memory trouble, and the replay is far too small (28 MB of 16 GB) for an out-of-memory kill to be likely on the first boot; the likelier reading is reclaim of an idle-looking machine, not OOM.
     - From now on: at the start of each long step I record `uptime` and `free -m` here; after any restart I record the new uptime and check `dmesg` and the replay log for a kill. I now wait in a foreground loop (progress line every 5 minutes, returning before the command timeout, then again) instead of a watch an hour apart.
3. **Files I expect to change.** This file; the report folders `rl/results/slow_reports/<date>_brew-08-entei-rainbow-cave/` and, later, `<date>_13-a-ninetales-raticate/`. Nothing else (no pin, no engine, no scripts).
4. **Waiting on the laptop or Sonnet.** Nothing.
5. **Open questions for Dustin.** None yet.

## Log (one line per new job, added and pushed before it starts)

- 2026-10-09: setup for the slow reports (Fable via Dustin): cargo cache for d513e37b, build of the pinned source into `$HOME/slow_report_kx3/strength` (must print engine tree 31dbd2e6e8ec and harness source bf9c5d68), no games.
- 2026-10-09: report 1, brew 08 (Entei, Rainbow Cave): registration only, `--deals 10 --threads 4 --school-rule off`; replays both self-checks (hours), then the registered folder is pushed before any game.
- 2026-10-09: report 1, brew 08: playing the 320 registered games in slices of --max-games 40 (8 slices), report folder pushed between slices; the question, the size and the final numbers go in the folder's SLOW_REPORT.md.
- Direct route test received 2026-10-09T21:19Z; I am the Sonnet cloud; my session id is session_01LbhnEkPxKLoYA6VUG1N33k
- 2026-10-09: report 2, deck 13 (decks/dustin/13-a-ninetales-raticate.txt): dry run, then registration only (`--deals 10 --threads 4 --school-rule off`, hours for the self-check replay), registered folder pushed before any game; then slices of --max-games 40.
