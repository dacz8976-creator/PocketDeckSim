# The slow report's R6 re-pin check: the reading (Oct 29, as fixed in SPEC.md section 4)

**Verdict: pass.**

**Question.** Does the frozen kx3, rebuilt on R6's engine, play the development run's games exactly as before?
- The rebuild is the program `/home/dacz8976/kx_r4/strength` (sha256 23d8a9b5…), built from K `e3ddc014` on `laptop/kx3-on-r6-2026-10-29`: d513e37b's six kx3 engine files on S's engine (affe56e8, the R6 release commit).
- The development run is `../strength_2026-10-03_kx3_dev/`.
- SPEC.md section 3 named no row where R6 could change a game (`rows.json` is `{}`). So any changed game would have been a stop.

**Answer: yes, game for game.** 202 of 202 kx3 games and 202 of 202 km3 games are identical.

| registration | what | kx3 games equal | km3 games equal |
|---|---|---:|---:|
| replay_a | 09, 06, 10 v the 8 panel lists, deals 0-1, both seats | 96 of 96 | 96 of 96 |
| replay_b | 01, 05, draft A v the 8 panel lists, deals 0-1, both seats | 96 of 96 | 96 of 96 |
| replay_c | 10 v t-weezing (Will's row), deals 0-4, both seats | 10 of 10 | 10 of 10 |
| **all** | | **202 of 202** | **202 of 202** |

- **How it was compared:** `compare_dev.py` (byte-identical to Oct 21's) checks each game against the development run's game on the same key, content without timing (`split_collect.py`'s `content`).
  - Every seed equals the development run's.
  - No game is missing, and no game is outside the development run.
  - The output is `COMPARE_DEV.txt`, exit status 0. Its line "RESULT: every changed game is in a named row" means, with no named row, that no game changed.
- **The self-checks:** each of the three registrations replayed both self-checks on the program, and each equals the pin's text:
  - km3 81b572198c04d5d1;
  - kx3 31d638dbc818b0fa.
- **The files:** in each registration, every deck and list file (11, 11 and 2; 14 different files) has the development run's path and sha256. All three manifests name the program with sha256 23d8a9b5…, and the lane checked that hash at its start and again before each replay.
- **Order:** the registrations were committed and pushed (5f5ef7d2) before any game was played. Everything ran on Oct 29:
  - registrations 06:50-09:09Z;
  - replay_a and replay_b in parallel from 09:09Z (replay_a, 2 threads, ended 12:00Z; replay_b, 3 threads, ended 14:07Z);
  - replay_c, 2 threads, 12:00-12:13Z;
  - the comparison at 14:07Z, then the games and the record were committed and pushed (6bbc271e).

  These times come from the laptop's WSL clock, which ran about 10-15 minutes ahead of the Windows clock that day.
- **Conditions:** no cutoff; nice 19, ionice -c3; the program's environment scrubbed (`lane_kxr_r6.sh`).
  - `errors.jsonl` is empty in all three folders.
  - The lane's record is `LANE_RECORD.txt`.
- **Wailord left out,** as on Oct 12 and Oct 21 (Dustin, Oct 10). So the sample is 202 games per arm.

**What it means.**
- **What the pass allows (SPEC.md section 4):**
  - the slow report's program moves to `/home/dacz8976/kx_r4/strength`;
  - the pin (`rl/strength/slow_report_pin.json`) and its docs are regenerated on main, then the pin tests run;
  - the self-check texts stay exactly as they are.

  The re-pin goes to the coordinator for review before main moves (coordinator-082).
- **Dustin's words cover it.**
  - Oct 21: "Move the slow-report program only after its replay check passes."
  - Oct 28: his "Yes" to the Dual Fusion adoption, whose R6 lists the slow-report pin, the kx3 rebuild and the self-check digests.
- **What a pass also shows:** evidence for RUN5's refactor rule on these rows (section 3), as far as their games play the changed cards. The logs do not trace which code paths ran.
- **What it does not show:** anything about decks or cards outside these 14 files. The check replays the development run's games only.

**Record-keeping.**
- **A wording slip in the spec:** SPEC.md section 1 calls K's branch a "local branch". K was on origin before the registrations named it, as section 2 says (origin `laptop/kx3-on-r6-2026-10-29` = e3ddc014). The committed spec is left as written (coordinator-082).
- **The report** for this result is laptop-063.
