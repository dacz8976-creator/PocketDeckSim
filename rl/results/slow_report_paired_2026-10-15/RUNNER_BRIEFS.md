# Briefs for the two Sonnet cloud runners: paired variants of deck 13-A (written Oct 15; send only after the laptop has merged branch `sonnet/slow-report-paired` into main)

Both briefs are for a paired variant of the finished report `rl/results/slow_reports/2026-10-12_13-a-ninetales-raticate` (kx3 70.6% over 160 games, km3 51.2%; program 5011e227cf63; seed_base 24,606,700,000 = slot 57,
10 deals, 4 threads, school rule off; its manifest.json has sha256 `f3dacac4e131…`). The variant plays the very same deals, so a slot is reused on purpose: no START_HERE edit, and the registration says "paired with <folder>".
Each variant swaps the one Ilima A3 149 in the deck for one other card on Ilima's own line. About 7 cloud hours each (the base took 6.6 h). The runners do not share cores; run them side by side.

## Runner 1 ("Slow deck reports runner", CLOUD2_STATUS.md, branch claude/slow-reports-runner-xlsxu0): variant A, Giant Cape

```
From the coordinator (via the direct cloud route), to the Sonnet cloud runner 1 (CLOUD2_STATUS.md). If you are not runner 1, say so in your status file and do nothing else.

JOB (report 7): a PAIRED VARIANT of deck 13-A: 13-a-giant-cape = the deck of decks/dustin/13-a-ninetales-raticate.txt with -1 Ilima A3 149, +1 Giant Cape A2 147 (+20 HP), played on the very deals of
rl/results/slow_reports/2026-10-12_13-a-ninetales-raticate (seed_base 24,606,700,000, slot 57, reused on purpose: no new slot, no START_HERE edit). Does the Cape help 13-A's opening Basic?

1. Merge main (text only): git fetch origin main && git merge origin/main. Check: rl/strength/slow_report_paired.py and decks/variants-2026-10-15/13-a-giant-cape.txt exist;
   sha256 of that deck starts 75097ab4fd85; sha256 of rl/strength/slow_report_pin.json starts 1fc30ce48e36 (unchanged); rl/results/slow_reports/2026-10-12_13-a-ninetales-raticate/ is there
   (its manifest.json sha256 starts f3dacac4e131).
2. Your program must be the one the base was played with: $HOME/slow_report_kx3/strength with sha256 5011e227cf63... (the program you built on Oct 12). If it is missing or has another sha256, rebuild with the
   rebuild_command in the base folder's manifest (slow_report.build_record); if the sha256 still differs, STOP and write it in CLOUD2_STATUS.md.
3. Dry run (writes nothing):
   python3 rl/strength/slow_report.py --paired-with rl/results/slow_reports/2026-10-12_13-a-ninetales-raticate --deck decks/variants-2026-10-15/13-a-giant-cape.txt --program $HOME/slow_report_kx3/strength --threads 4 --school-rule off --dry-run
   It must print: "paired with rl/results/slow_reports/2026-10-12_13-a-ninetales-raticate: 13-a-ninetales-raticate -> 13-a-giant-cape: -1 Ilima A3 149, +1 Giant Cape A2 147"; "(card 17 of 20)";
   "seeds from 24606700000, the base report's: no new seed slot is taken; 10 deals ... 4 threads, school rule off"; program sha256 5011e227cf63, rebuilt, both self-checks accepted from the committed
   record (no replay); "dry run: nothing written"; exit 0. Anything else (a REFUSED, another seed_base, a self-check replay): STOP and write the message in CLOUD2_STATUS.md.
4. Register: the same command with --register-only instead of --dry-run. The folder is rl/results/slow_reports/<Chicago date at registration>_13-a-giant-cape: take the path from the line
   "registered in ...", do not guess the date. Commit and push the folder before any game.
5. Play: the resume command it prints (python3 rl/strength/slow_report.py --dir <folder> --school-rule off), in slices of --max-games 40 under your driver, one poll every 280 s, folder pushed after each slice
   (never commit slow_report.lock). 320 games = 160 kx3 + 160 km3. After a machine restart resume with the same command.
6. Finish: the last slice writes SLOW_REPORT.md (it has a new section "Compared with the base report") and REPORT.md; push. The console also prints "compared with the base report: kx3: ... points on the same deals" and the same for km3.
   Report once to Dustin in chat: those two lines (the score change variant minus base with its range), then in one line each: how often Giant Cape was played and where, and the "turns a charged Pokémon did not attack, against t-altaria"
   row (base v variant). Do not interpret beyond that; say it is the optimistic end and that one card rarely moves a score by a visible amount.

Rules unchanged: never call strength_prereg.py directly; never set SLOW_REPORT_ALLOW_UNCOMMITTED_PIN; never use --pin; never set a DECKGYM_* variable; the pin and the scripts are not edited;
stop only for an error, a digest mismatch or a tool refusal, and then write the message in CLOUD2_STATUS.md; record uptime and free -m at the start of each long step.
```

## Runner 2 ("Awaiting delegator instructions", CLOUD3_STATUS.md, branch claude/slow-reports-runner-2): variant B, Big Malasada

```
From the coordinator (via the direct cloud route), to the Sonnet cloud runner 2 (CLOUD3_STATUS.md). If you are not runner 2, say so in your status file and do nothing else.

JOB (report 7): a PAIRED VARIANT of deck 13-A, which you played on Oct 12: 13-a-big-malasada = the deck of decks/dustin/13-a-ninetales-raticate.txt with -1 Ilima A3 149, +1 Big Malasada A3 142
(heal 10 and remove a random Special Condition from your Active), played on the very deals of rl/results/slow_reports/2026-10-12_13-a-ninetales-raticate (your report: seed_base 24,606,700,000, slot 57,
reused on purpose: no new slot, no START_HERE edit). Does Big Malasada help 13-A against Sleep?

1. Merge main (text only): git fetch origin main && git merge origin/main. Check: rl/strength/slow_report_paired.py and decks/variants-2026-10-15/13-a-big-malasada.txt exist;
   sha256 of that deck starts 0e9607b4c6b1; sha256 of rl/strength/slow_report_pin.json starts 1fc30ce48e36 (unchanged); your deck-13 folder is there (its manifest.json sha256 starts f3dacac4e131).
2. Your program must be the one your deck-13 report was played with: $HOME/slow_report_kx3/strength with sha256 5011e227cf63... If it is missing or has another sha256, rebuild with the rebuild_command in that
   folder's manifest (slow_report.build_record); if the sha256 still differs, STOP and write it in CLOUD3_STATUS.md.
3. Dry run (writes nothing):
   python3 rl/strength/slow_report.py --paired-with rl/results/slow_reports/2026-10-12_13-a-ninetales-raticate --deck decks/variants-2026-10-15/13-a-big-malasada.txt --program $HOME/slow_report_kx3/strength --threads 4 --school-rule off --dry-run
   It must print: "paired with rl/results/slow_reports/2026-10-12_13-a-ninetales-raticate: 13-a-ninetales-raticate -> 13-a-big-malasada: -1 Ilima A3 149, +1 Big Malasada A3 142"; "(card 17 of 20)";
   "seeds from 24606700000, the base report's: no new seed slot is taken; 10 deals ... 4 threads, school rule off"; program sha256 5011e227cf63, rebuilt, both self-checks accepted from the committed
   record (no replay); "dry run: nothing written"; exit 0. Anything else (a REFUSED, another seed_base, a self-check replay): STOP and write the message in CLOUD3_STATUS.md.
4. Register: the same command with --register-only instead of --dry-run. The folder is rl/results/slow_reports/<Chicago date at registration>_13-a-big-malasada: take the path from the line
   "registered in ...", do not guess the date. Commit and push the folder before any game.
5. Play: the resume command it prints (python3 rl/strength/slow_report.py --dir <folder> --school-rule off), in slices of --max-games 40 under your driver, one poll every 280 s, folder pushed after each slice
   (never commit slow_report.lock). 320 games = 160 kx3 + 160 km3. After a machine restart resume with the same command.
6. Finish: the last slice writes SLOW_REPORT.md (it has a new section "Compared with the base report") and REPORT.md; push. The console also prints "compared with the base report: kx3: ... points on the same deals" and the same for km3.
   Report once to Dustin in chat: those two lines (the score change variant minus base with its range), then in one line each: how often Big Malasada was played, and the "turns a charged Pokémon did not attack,
   against t-altaria" row (base v variant). Do not interpret beyond that; say it is the optimistic end and that one card rarely moves a score by a visible amount. (Which Special Condition it removed is not recorded.)

Rules unchanged: never call strength_prereg.py directly; never set SLOW_REPORT_ALLOW_UNCOMMITTED_PIN; never use --pin; never set a DECKGYM_* variable; the pin and the scripts are not edited;
stop only for an error, a digest mismatch or a tool refusal, and then write the message in CLOUD3_STATUS.md; record uptime and free -m at the start of each long step.
```

Order if only one runs: A (Giant Cape) first. Both can run at the same time on their own machines.
