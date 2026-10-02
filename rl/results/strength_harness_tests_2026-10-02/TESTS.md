# Strength harness: tests (Oct 2, 2026)

Built by `rl/strength/build.sh` against the engine tree of main-8626a35 (`engine/` tree `38af8b0cc4f35fdccc647ed540a56ec8f5e6c1d5`, equal to origin/main's at the time), nice 19, offline, with the engine's own Cargo.lock. Light runs only: two threads, nice 19, 5 deals per pair. Each run directory here holds the pre-registration, manifest, report and the games (`games.jsonl.gz`); `tests_script.sh` and `tests_output.txt` are the script and its output for tests A-D.

| test | what | result |
|---|---|---|
| **km3 v km3** (`smoke_km3_km3/`) | the required identity check: 3 decks (t-altaria, t-hydreigon, draft-A-shark-tempo) against 3 panel lists, 5 deals x 2 seats x 2 arms = 180 games | **every paired difference exactly 0**: 90 of 90 paired games identical in winner, points and turns; pooled +0.0 ± 0.0; 32 s wall, 0.36 s per game |
| **km3 v kog3** (`smoke_km3_kog3/`) | the same pool, kog3 as pilot X against km3 as reference | pooled +1.1 ± 2.2 points over 90 paired games (not a measurement; 5 deals); the arms differ only on t-altaria (pooled +3.3 ± 6.5; against t-suicune +10.0 ± 19.6), the other two decks are identical; 31 s wall |
| **A. resume** (`resume_test/`) | stop after 50 of 180 games, append a torn line, run again | the run repaired the torn line, played the 130 missing games, and **every one of the 180 game results equals the straight run's** (winner, points, turns, first player) |
| **B. external pilot** (`ext_test/`) | `ext:python3 rl/strength/ext_pilot_example.py attack` as pilot X against km3 | 12 games, 0 errors; the protocol works end to end; decisions, ms per decision and the pilot's notes are in the report (the example reports no cost) |
| **C. held-out guard** | a held-out list naming t-lucario, locked | `strength_prereg.py` refuses (exit 1); the program refuses a manifest that lists a held-out deck (exit 101) |
| **D. self-check** | `strength selfcheck`, 12 fixed games, t-altaria v t-suicune | km3 `digest=81b572198c04d5d1` (8-4, 127 turns); kog3 `digest=63f520e3318376ae`. A second build of the same pilot code must print the same digest; it is recorded in every pre-registration |

Also exercised: the program-hash check (a config naming a stale `program_sha256` is refused), the pre-registration order check (the report prints that the first game started after registration), the same-deal check (no pair was excluded), the intended-line kinds on the starting lines (Turbo Shark by own turn 3 in draft A: 30% in both arms of the smoke runs; Hyper Ray without a knockout: 0 of 28 uses; Eevee Active on own turn 1: 40% of games in both arms; Thieving Incisors, which is an ability choice, `Ability:Thieving Incisors`, and Boosted Evolution, which is passive and so measured as Eevee Active on own turn 1).

Not tested yet: a pilot built from an experimental engine branch (none exists yet), an external pilot that is slow or reports cost, and a run of the default pool (56 pairs x 200 deals x 2 seats x 2 arms is about 45,000 games, a few hours at two threads for km3-speed pilots).
