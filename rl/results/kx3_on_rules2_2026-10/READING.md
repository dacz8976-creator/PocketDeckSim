# Step 4's kx3 replay check: the reading (Oct 14, as fixed in SPEC.md section 4)

**Question.** Does the frozen kx3, rebuilt on the official engine after rules switch 2, play the development run's games exactly as before?
- The rebuild is laptop/kx3-on-rules2 cd20a97a: d513e37b's players on main-c045ede's engine.
- The development run is `../strength_2026-10-03_kx3_dev/`, played on the old engine.
- The one allowed exception is deck 10 against t-weezing, where Will's new rule may act.

**Answer: yes, game for game: 202 of 202 kx3 games and 202 of 202 km3 games are identical, the Will row included.**

| registration | what | kx3 games equal | km3 games equal |
|---|---|---:|---:|
| replay_a | 09, 06, 10 v the 8 panel lists, deals 0-1, both seats | 96 of 96 | 96 of 96 |
| replay_b | 01, 05, draft A v the 8 panel lists, deals 0-1, both seats | 96 of 96 | 96 of 96 |
| replay_c | 10 v t-weezing (Will's row), deals 0-4, both seats | 10 of 10 | 10 of 10 |
| **all** | | **202 of 202** | **202 of 202** |

- **How it was compared:** each game against the development run's game on the same key, content without timing (`split_collect.py`'s
  `content`). Every seed equals the development run's. The comparisons are in `replay_*/COMPARE_DEV.txt`.
- **Will's row:** Will is played in 6 of replay_c's 20 games (deals 1, 2 and 3, one seat each, by both pilots). Every one replays
  exactly. So the new rule had the chance to act in these games and changed none of them. No changed game needed tracing.
- **Wailord left out:** Wailord was dropped from the development-deck tests (Dustin, Oct 10), so the sample is 202 games, not SPEC's
  224 + 10.
- **The builds:**
  - 7 slices, played on 3 Managed Agents workers. Each was sealed, then re-checked by the collector on the laptop
    (`workers/`, `MERGE_RECORD.md`).
  - The sandbox rebuild (sha256 f492d55e) has the laptop build's engine tree 4ebb30a941737d16 and harness bf9c5d68. Its stamps replayed
    the pinned self-checks: km3 81b572198c04d5d1, kx3 31d638dbc818b0fa.
  - The registrations' engine text ("tree 4ebb30a94173:") doesn't parse, so the merges named the full tree with `--engine-tree`, after
    checking it against the laptop build and all three workers' builds.

**What it means.**
- The slow report's new pin, the frozen kx3 on the official engine (`rl/strength/slow_report_pin.json`, e12342cd), plays these games as
  the development run did.
- The four slow reports already run on that pin (brew 07, brew 09, deck 13, draft D) stand on a check that held game for game here.
- Elsewhere, rules switch 2 changes games only where its rules act. Deck 12's page and step 8c's accounting showed where that is.
