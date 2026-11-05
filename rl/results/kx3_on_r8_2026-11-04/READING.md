# The slow report's R8 re-pin check: the reading (Nov 5, as fixed in SPEC.md section 4)

**Verdict: pass, with a timing note** (every game identical; one kx3 decision over the 120 s line, ruled on by Dustin, see Timing).

**Question.** Does the frozen kx3, rebuilt on R8's engine, play the development run's games exactly as before?
- The rebuild is the program `/home/dacz8976/pincand_work/RR_R8_48dec4f5/strength/K8/strength` (sha256 d4d4e43a…), built from K8 `b5f15351` on `laptop/kx3-on-r8-2026-11-04`: kx3's six engine files on R8's engine (48dec4f5, whose engine tree is R8's release S8 543dad00's); five of them d513e37b's blobs, and `players/mod.rs` d513e37b's plus R8's 8 protocol-adapter lines.
- The development run is `../strength_2026-10-03_kx3_dev/`.
- SPEC.md section 3 named no row where R8 could change a game (`rows.json` is `{}`). So any changed game would have been a stop.

**Answer: yes, game for game.** 202 of 202 kx3 games and 202 of 202 km3 games are identical.

| registration | what | kx3 games equal | km3 games equal |
|---|---|---:|---:|
| replay_a | 09, 06, 10 v the 8 panel lists, deals 0-1, both seats | 96 of 96 | 96 of 96 |
| replay_b | 01, 05, draft A v the 8 panel lists, deals 0-1, both seats | 96 of 96 | 96 of 96 |
| replay_c | 10 v t-weezing (Will's row), deals 0-4, both seats | 10 of 10 | 10 of 10 |
| **all** | | **202 of 202** | **202 of 202** |

- **How it was compared:** `compare_dev.py` (byte-identical to Oct 21's and R6's) checks each game against the development run's game on the same key, content without timing (`split_collect.py`'s `content`). Every seed equals the development run's; no game is missing, and no game is outside the development run. The output is `COMPARE_DEV.txt`, exit status 0: "RESULT: every changed game is in a named row", which with no named row means no game changed.
- **The self-checks:** each of the three registrations replayed both self-checks on the program, and each equals the pin's text: km3 81b572198c04d5d1; kx3 31d638dbc818b0fa.
- **The files:** in each registration every deck and list file (11, 11 and 2; 14 different files) has the development run's path and sha256. All three manifests name the program with sha256 d4d4e43a…, and the lane checked that hash at its start and before each replay.
- **Order:** the registrations were committed and pushed (86d0679f) before any game was played:
  - registrations Nov 4, 21:12-23:47Z;
  - replay_a and replay_b in parallel from 23:47Z (replay_a, 2 threads, ended Nov 5 03:00Z; replay_b, 3 threads, ended 05:26Z);
  - replay_c, 2 threads, 03:00-03:14Z;
  - the comparison at 05:26Z, then the games and the record were committed and pushed (910e1d69).

  These times come from the laptop's WSL clock.
- **Conditions:** no cutoff; nice 19 and ionice -c3 for the registrations, the games and the comparison; the program's environment scrubbed; no PAUSE during the run (`lane_kxr_r8.sh`). `errors.jsonl` is empty in all three folders. The lane's record is `LANE_RECORD.txt`.
- **Wailord left out,** as before (Dustin, Oct 10). So the sample is 202 games per arm.

**Timing: one kx3 decision over 120 s (SPEC.md section 4; plan 113 §7).**
- SPEC.md section 4 lists "a kx3 decision over 120 s" among the stops. One kx3 decision took **188,311 ms**: deck 01 (muk-glimmora-kingambit-regigigas) v t-hydreigon, deal 0, seat 0, turn 3, "Play: Poké Ball". It is the only one over 120 s here; km3's largest decision took 1,346 ms.
- **The decision itself did not change:** that game, like every other, equals the development run's, so the time changed nothing kx3 chose. The times are wall-clock milliseconds on a shared laptop with three registrations' games in parallel at nice 19.
- **The same decision on the same key:** 21,113 ms in the development run (Oct 3), 41,796 ms in R6's check (Oct 29), 188,311 ms here.
- **R6's check had two kx3 decisions over 120 s**, in the same row (154,107 ms and 120,329 ms); its reading applied no 120 s rule, and the re-pin went ahead. The development run's largest over these 202 keys was 60,455 ms.
- **Over the whole check** (the coordinator's pairing with R6's check, coordinator-157): kx3's total logged time was x1.136 R6's (23.56 h v 20.72 h); the median per-decision ratio was 1.11 (10th percentile 0.45, 90th 2.63); R6's slowest decision (154 s) took 36 s here.
- **The quiet re-time** (coordinator-157 (1); its files are in `retime/` here: `RETIME.txt`, `RUNS.txt`, the two one-key manifests, the four run folders and logs, renamed `pass1`-`pass4` from the script's `run1`-`run4` so that no path carries a never-open name, and `retime.sh`, the script as run): that key's game alone on the laptop, 1 thread, nice 19, in the order K8, R6's pinned program (`/home/dacz8976/kx_r4/strength`, 23d8a9b5…), K8, R6 (Nov 5, 05:34-06:03Z). The Poké Ball decision took 17,747 / 17,763 / 17,968 / 18,151 ms: mean K8 17,858 ms v R6 17,957 ms, **ratio 0.994** (the coordinator's line for "not much slower" was 1.3). The whole kx3 game took 442,021 / 439,146 / 438,436 / 441,420 ms over its 37 decisions. All four games equal the development run's. So on a quiet laptop R8's program is as fast as R6's here, and the 188 s was the shared machine's load.
- **The stop rule fired, so it went to Dustin.** STOP by 113 §7 / SPEC §4 (one kx3 decision at 188,311 ms). To Dustin via coordinator-157 and the coordinator's question of Nov 5. His words: "Yes finish" (Nov 5, quoted in coordinator-158). The coordinator's question put it as finishing the switch to kx3 on R8 after the re-time matched (about 18 s on both programs, every game the same); his yes is the first case of coordinator-157 §4: his yes, and the re-time within the 1.3 line (0.994).

**What it means.**
- **What a pass allows (SPEC.md section 4):** the slow report's program moves to K8's program; the pin (`rl/strength/slow_report_pin.json`) and its docs are regenerated, then the pin tests run; the self-check texts stay exactly as they are. Then the coordinator's final review, and main moves once, after it.
- **Dustin's words cover it.** Oct 21: "Move the slow-report program only after its replay check passes." Nov 4: "Adopt all three", whose approval page lists this check and the re-pin among R8's after-yes steps.
- **What a pass also shows:** evidence for RUN5's refactor rule on these rows (section 3), as far as their games play the changed code. The logs do not trace which code paths ran.
- **What it does not show:** anything about decks or cards outside these 14 files, and nothing about kx3's play on the cards R8 adds (none is in these games).

**Record-keeping.** The report for this result is laptop-118; the re-time is laptop-119; Dustin's answer is quoted in coordinator-158; the re-pin follows in laptop-120.
