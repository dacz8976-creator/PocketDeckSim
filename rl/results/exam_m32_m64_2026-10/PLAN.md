# The held-out exam of m32 and m64: the pre-registration (written Oct 13, before registration and before any game)

**Decision.** Dustin, Oct 13, through the coordinator: test BOTH m32 and the full candidate m64 on the held-out exam, on the cloud fleet,
under Astra's conditions, which he adopted. Astra: "Test both on matched deals, with the comparison and selection rule fixed beforehand.
Don't interpret an inconclusive difference as proof they're equally good." This file fixes the design, PRIMARY and the selection rule;
`read_exam.py` computes them and was written with it (`python3 rl/results/exam_m32_m64_2026-10/read_exam.py --selftest` checks the rule on
fixed cases and runs the report on stand-ins). The registrations' PREREGISTRATION.md files point here.

**Question.** On Dustin's 11 held-out decks, never used in development, does kx3 with the Tool rule, the skip bar and close calls extended to
32 play-outs (m32) or 64 (m64, the combined candidate) play better than the frozen kx3? And is m64's extra time bought with better play
than m32's? On the development decks, m32 − frozen was +4.4 ± 3.1 points per 100 games, m64 − frozen +4.6 ± 3.4, and m32 − m64 −0.2 ± 3.0
(`../thinking_time_2026-10/READING.md`). Those decks are the ones the settings were developed on, so this exam is the real check.

## Settings and program

One program for both, the combined run's and the thinking-time test's: claude/playout-pilot 172cbe9c, laptop build
`/home/dacz8976/kxc/172cbe9c/strength`, sha256 `f5a6ae95...`. The suffixes are the pilot code's parameters (`playout_player.rs:131`).
- **m32:** `kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m32` (self-check digest on this program: 869789a10142e83f).
- **m64:** `kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m64` (724e581a9c51711f).
- **Already played, reused, no new games:** the frozen kx3 and km3 on these decks and deals, the Oct 5 exam's arm X and arm ref
  (`../strength_2026-10-05_kx3_exam/`).
  - The configs' `engine` record measured the frozen kx3's self-check (31d638dbc818b0fa) at 54209409. From there to 172cbe9c, only the
    close-call code changed, which runs only with `_m`. So this program's plain kx3 is the frozen kx3 by reading the code, not by a new
    measurement.
  - In the thinking-time test, m16 played the frozen kx3's exact moves in 402 of 480 games.

**Engine.** This program is on the engine before rules switch 2, the engine the frozen kx3's exam games were played on. That is on purpose:
the pairing needs the same engine.
- Rules switch 2 (pinned Oct 12) changes the outcome of some games on some decks.
- Between d513e37b (the Oct 5 exam's program) and 172cbe9c, `engine/` changed only in the play-out pilot's own files, examples and tests.
  So the rules and km3 are the Oct 5 exam's.
- This exam compares bot settings under one set of rules.
- Carrying the picked setting to the new engine is a separate step, as step 4 was for the frozen kx3: the candidate merge
  `laptop/kx3cand-on-rules2` 9a0bc5ac, then a replay check.

## Decks, deals and registrations

The Oct 5 exam's deals exactly:
- the 11 held-out decks, in the same order;
- against the 8 panel lists, in the same order;
- 3 deals per pairing, both seats;
- seed_base 24,500,000,000, stride 10,000.

That is 528 kx3 games per setting. Each pairs by (deck, opponent, deal, seat) with the other setting's game, the frozen kx3's and km3's.
Each setting also plays 528 km3 reference games (about a second each) for the build check.
- `make_exam_configs.py` writes the two configs (`configs/`) and checked before any game that:
  - every deck and opponent file is unchanged since Oct 5 (sha256);
  - all 1,056 keys of a setting get the Oct 5 exam's own seed.
- The seeds are reused on purpose, for the pairing: no new seed block (START_HERE's seed table says so on the exam's row).
- **One registration per setting** (`reg_m32`, `reg_m64`, all 11 decks each), on the laptop from the repository root:
  `python3 rl/strength/strength_prereg.py --config rl/results/exam_m32_m64_2026-10/configs/config_<s>.json --out rl/results/exam_m32_m64_2026-10/reg_<s> --repo .`
  - Each plays the 12-game self-checks for km3 and its setting. The two run in parallel, for up to about 3 hours (m64's, estimate).
  - Stage `heldout`: `rl/strength/heldout.json` is unlocked for these two registrations only (laptop Opus, under Dustin's Oct 13
    decision). It is relocked right after, as on Oct 5, and the unlock is added to its `unlocked_by` record. Workers aren't blocked by
    the relock: the program reads the lock from the manifest.
  - Before anything is committed, `~/runs/exam_register.sh` checks each new manifest:
    - the self-checks were run by strength_prereg.py and give km3 `81b572198c04d5d1` and the setting's digest;
    - the decks and opponents (name, path, sha256), seed_base, stride, deals and seats equal the Oct 5 manifest's;
    - the stage is `heldout`, unlocked, with repo_root `.`, program sha256 f5a6ae95…, and engine tree 69a5a4419da2 in its record.
- The games are played in slices on the cloud fleet through the collector (`SHARDS.md`, `WORKER_BRIEF_MA.md`).

**Build check.** Every km3 game of both registrations must equal the Oct 5 exam's km3 game on the same key (content without timing), 528 of
528 each, and every seed must equal the Oct 5 exam's. Otherwise the pairing is void and nothing is read. `read_exam.py` checks it again.

## PRIMARY

All on the same 528 pairs, in game score (win 1, tie ½, loss 0), in points per 100 games, mean ± 1.96 sd/√n:
1. **m32 − frozen kx3**
2. **m64 − frozen kx3**
3. **m64 − m32**, the direct comparison.

Each is reported with how many games differ each way:
- pooled (every deck has 48 pairs, so this already weights the decks equally);
- per group, setup first;
- per deck (48 pairs each, for completeness only: too few to rank decks).

The groups are fixed now. They come from km3's mean turns per game on these decks in the Oct 5 exam
(`../strength_2026-10-05_kx3_exam/GROUPS_AND_PACE.md`):
- **setup:** 13, 11, draft C, 07;
- **middle:** 02, 04, 08;
- **fast:** draft D, 12, 15, 14.

Also reported, outside the pick:
- each setting against km3, next to the frozen kx3's +21.3 ± 4.0 from Oct 5;
- win rates;
- pace: turns per game, and the deck's first-attack own turn;
- time per kx3 game.

**Sample size, before play.** Scaled from the development decks' spread to 528 pairs:
- m64 − m32 has about ±2.9 points;
- each setting against the frozen kx3 has about ±3.0 to ±3.3 points;
- the setup group alone (192 pairs) has about ±5 to ±6 points.

That ±2.9 is the measured difference needed to show a result, not the smallest real difference the exam finds. In chances (normal
approximation, at the development spread):
- **m64 − m32:**
  - a true difference of 4 points is shown about 3 times in 4;
  - 3 points about half the time;
  - 2 points about 1 time in 4.
- **m32 − frozen:**
  - a true gain of 3 points is shown about half the time;
  - the development decks' +4.4 would be shown about 4 times in 5. That is likely optimistic, since m32 was chosen on those decks.
- **The setup group alone:** a true 4 points is shown about 1 time in 3; showing one 4 times in 5 needs about 8 points.

## The selection rule, fixed now

- A setting **gains** when its interval against the frozen kx3 (pooled, 528 pairs) is entirely above zero.
- On the development decks, an m64 game took an estimated 1.7 to 1.9 times as long as an m32 game. The two were timed on different
  machines, so that ratio is an estimate.
- **When m32 itself shows a gain,** m64's extra time is worth paying only for play **detectably better** than m32's on these decks: the
  m64 − m32 interval entirely above zero. At this sample size, that means a measured difference of about +3 points per 100 games or more.
  Any difference shown this way counts. The deck tester's job is accuracy, and Dustin's standing rule puts trustworthy play before speed
  (Oct 2).
- **When only m64 shows a gain,** m64 is picked as the cheapest setting with a shown gain, the thinking-time test's own rule. It is then
  picked without being shown better than m32, and the report says so with the m64 − m32 interval.

**The pick:**
1. If m64 gains AND m64 − m32 is entirely above zero: **m64** is the deck tester.
2. Otherwise, if m32 gains: **m32** is the deck tester.
3. Otherwise, if m64 gains: **m64** is the deck tester. It is the only setting with a shown gain, and it is not shown better than m32.
4. Otherwise: the frozen kx3 stays the deck tester as well as the screener. The gain seen on the development decks is reported as not
   confirmed on the held-out decks.

Step 3's code also asks that m64 − m32 not be entirely below zero. That can't fail once steps 1 and 2 have not picked. On the same pairs,
m64 − frozen = (m32 − frozen) + (m64 − m32) exactly, and `read_exam.py` checks that.

In every case the frozen kx3 stays the screener.

**An inconclusive m64 − m32 is not read as "equally good."** When its interval includes zero:
- Under step 2 the pick goes to m32 on cost alone.
- The report states the limits in plain words, for example: "on these decks m64 is somewhere between L points worse and U points better
  than m32 per 100 games; this exam can't tell them apart within that range."
- It also says how many deals per matchup in all, and how many more than this exam's 3, would narrow it to ±2 points.

Likewise, a setting that does not gain is reported with its interval: its gain could be anywhere in that range, including zero.

The PICK line also prints the three intervals to two decimals, since the pick uses the unrounded bounds.

**The setup group, with the pick (Astra's third condition).** Building up over several turns on setup decks is the planning weakness
Dustin wanted fixed, and an overall gain could hide it.
- The setup group's three results (m32 − frozen, m64 − frozen, m64 − m32) are stated in the same paragraph as the pick.
- If the picked setting shows no gain over the frozen kx3 on the setup decks (interval not entirely above zero), the report says plainly
  that the planning weakness on setup decks is not shown fixed, whatever the pooled result.
- A group or deck result does not change the pick on its own: read alone, it would be a smaller test with more chances of a false result.
- A group or deck whose interval is entirely below zero is reported, not a veto.

**Chance** (normal approximation, and a simulation that redrew the development games):
- **If neither setting truly beats the frozen kx3,** this rule recommends one at most about 5% of the time: two one-sided 2.5% checks
  (4.3% simulated).
- **If m32 and m64 truly play alike** and both have the development gain, it picks m64 about 1 time in 10 (11% simulated):
  - about 2.5% through step 1;
  - the rest through step 3, when m64's interval happens to clear zero and m32's doesn't.

  That is the price of step 3.

**Nothing is read from part of the run.** The pick is read only when both registrations are merged COMPLETE (528 kx3 and 528 km3 games
each) with their build checks. The merge writes into each registration's own folder:
`split_collect.py merge --manifest .../reg_<s>/manifest.json --worker ... --out rl/results/exam_m32_m64_2026-10/reg_<s>`. Dustin decides from the report; the pick is the recommendation the rule gives.

## Time and cost (estimates before play)

- **Time per game.** m32 and m64 are both timed in sandboxes, so m64/m32 is measured on the same pairs. Each deck's m32 and m64 games run
  on different workers, though, whose speed varies about ±15%. The frozen kx3 ran on the laptop on Oct 5, so any ratio against it is an
  estimate.
- **Sandbox play.** The frozen kx3 took 30.4 laptop hours for its 528 exam games. On the development decks:
  - an m32 game in a sandbox took 3.7 to 4.7 times the frozen kx3's laptop time (measured);
  - an m64 game is about 1.85 times m32's (estimate).

  That makes about 64 sandbox hours for m32 and about 118 for m64, at `--threads 2`.
- **Stamps.** Each worker's stamp replays the 12-game self-checks: up to about 4 hours for m32 and about 10 to 12 for m64 on a 4-core
  sandbox. The m64 figure is an estimate, corrected after registration from about 7.5: the laptop's m64 self-check took about 5 hours.
- **Credits.** The coordinator's estimate is about $65-100.
