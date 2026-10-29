# The slow report's re-pin check: the reading (Oct 22, as fixed in SPEC.md section 4)

**Verdict: pass.**

**Question.** Does the frozen kx3, rebuilt on main-4d48844's engine, play the development run's games exactly as before?
- The rebuild is the program `/home/dacz8976/kx_r3/strength` (sha256 7d046b6f…), built from `laptop/kx3-on-engine-candidate-2026-10-20` 87a7f340: d513e37b's players on main-4d48844's engine.
- The development run is `../strength_2026-10-03_kx3_dev/`.
- SPEC.md section 3 named the only rows where main-4d48844 could change a game: 10-xatu-oricorio-tr-weezing and 05-indeedee-stoutland, each against t-lucario (C1, the Growl-to-0 rule).

**Answer: yes, game for game.** 202 of 202 kx3 games and 202 of 202 km3 games are identical, the two named rows included.

| registration | what | kx3 games equal | km3 games equal |
|---|---|---:|---:|
| replay_a | 09, 06, 10 v the 8 panel lists, deals 0-1, both seats | 96 of 96 | 96 of 96 |
| replay_b | 01, 05, draft A v the 8 panel lists, deals 0-1, both seats | 96 of 96 | 96 of 96 |
| replay_c | 10 v t-weezing (Will's row), deals 0-4, both seats | 10 of 10 | 10 of 10 |
| **all** | | **202 of 202** | **202 of 202** |

- **How it was compared:** `compare_dev.py` checks each game against the development run's game on the same key, content without timing (`split_collect.py`'s `content`).
  - Every seed equals the development run's.
  - No game is missing, and no game is outside the development run.
  - The output is `COMPARE_DEV.txt`, exit status 0.
- **The named rows:** both rows replay exactly, in both arms. C1 could act there, and changed none of these games. So section 4's second clause (a build without C1 reproducing the changed games) wasn't needed, and no such build was made.
- **The self-checks:** each of the three registrations replayed both self-checks on the program, and each equals the pin's text:
  - km3 81b572198c04d5d1;
  - kx3 31d638dbc818b0fa.
- **Order:** the registrations were committed and pushed (f6743fc8) before any game was played. The games were played on the night of Oct 21-22:
  - registrations 02:00-04:08Z;
  - replay_a and replay_b in parallel from 04:08Z (replay_a, 2 threads, ended 06:48Z; replay_b, 3 threads, ended 08:53Z);
  - replay_c, 2 threads, 06:48-07:01Z;
  - the comparison at 08:53Z.
  
  The keeper's night window was 02:00-12:55Z, at nice 19, with the program's environment scrubbed (`lane_kxr.sh`). `errors.jsonl` is empty in all three folders. The lane's record is `LANE_RECORD.txt`.
- **Wailord left out,** as on Oct 12 (Dustin, Oct 10). So the sample is 202 games per arm.

**What it means.**
- **What the pass allows (SPEC.md section 4):** the slow report's program moves to `/home/dacz8976/kx_r3/strength`. The pin (`rl/strength/slow_report_pin.json`), `rl/strength/README.md` and `make_predictions.py`'s current harness tree are regenerated on main, the pin tests run, and the result is fast-forwarded onto main.
- **Dustin's words of Oct 21 cover it:** "Move the slow-report program only after its replay check passes."
- **Old reports:** the 8 slow reports made before the re-pin (`rl/results/slow_reports/2026-10-12_*` to `2026-10-14_*`) ran on main-c045ede's engine and say so.
- **Record-keeping:**
  - SPEC.md section 4 named the coordinator's report "laptop-019". That number went to the exam's run-2 pre-registration, so this result is laptop-023.
  - A stop would have gone to the coordinator only, per the coordinator's later note.
