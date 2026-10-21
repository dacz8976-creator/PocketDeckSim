# The slow report's re-pin check: kx3 on main-4d48844 (the spec; written Oct 21, before any game)

Dustin, Oct 21 (verbatim, to the coordinator): "Move the slow-report program only after its replay check passes. Until then, its reports must clearly identify the old engine." This is that check. It repeats the Oct 12 check (`../kx3_on_rules2_2026-10/`, SPEC.md section 4 and READING.md: 202 of 202 kx3 and 202 of 202 km3 games identical) on the new program. Written by the laptop session on the coordinator's instruction of Oct 21.

## 1. The program
- `/home/dacz8976/kx_r3/strength`, sha256 `7d046b6f9c1dcd9a9a834c2995bad256bc784e804ea08d351878e035cb24d319`: the frozen kx3's players (claude/playout-pilot d513e37b) on main-4d48844's engine, built from `laptop/kx3-on-engine-candidate-2026-10-20` 87a7f340 (engine tree 64de03e2; the built commit 4d488449 plus kx3's players) with `rl/strength/build.sh`, harness bf9c5d68, STRENGTH_JOBS=2, on Oct 21 (`../engine_candidate_2026-10-20/release/`).
- Its self-checks, measured on this program on Oct 21, equal the slow-report pin's: km3 81b572198c04d5d1, kx3 31d638dbc818b0fa. Each registration below replays them again.

## 2. The games (the same as Oct 12)
Three registrations of the development run's games (`../strength_2026-10-03_kx3_dev/`), on the development run's own seeds (`make_replay_configs.py` asserts every key's seed), with this program and `--repo` this branch's worktree:

| registration | decks v opponents | deals | games (kx3 + km3) |
|---|---|---|---|
| replay_a | 09, 06, 10 v the 8 panel lists | 0-1 | 96 + 96 |
| replay_b | 01, 05, draft A v the 8 panel lists | 0-1 | 96 + 96 |
| replay_c | 10 v t-weezing (Will's row) | 0-4 | 10 + 10 |

Wailord is left out (Dustin, Oct 10), as on Oct 12. The laptop plays them at night (the keeper's window, 02:00-12:55Z), nice 19, the program's environment scrubbed of KX_*, PDL_*, DECKGYM_*, JEV_* and PG_* (KX_EXTRA_LISTS unset, as in the development run). Threads change nothing about the results (every game is seeded).

## 3. Where main-4d48844 can change these games (fixed before any game)
main-4d48844 differs from main-c045ede, on which these games replayed identically on Oct 12, by six changes (`../engine_candidate_2026-10-20/RELEASE_NOTES.md`): C1 the Growl-to-0 rule (501fc1dd), C2 the hit back as attack damage (a1d3a714, 4d488449), C3 #385 (9c51453b), C4 #390 (75343578), C5 #401's Fossil part (42d2dd8e), C6 #344 narrow (764f7459). `engine/src/players/` and kx3's overlay are unchanged (`git diff 4d488449 87a7f340` touches only the overlay's files and tests, byte-identical to the Oct 12 build's). A read-only check of the 6 decks x 8 panel lists (the cards in `engine/database.json`, the code at 4d488449, and the bots' look-ahead: km3's search and kx3's play-outs, whose pool draws a list only when its Energy matches the opponent's Energy Zone) found:
- **C1 can act in two rows, both "possible", not expected:**
  - **10-xatu-oricorio-tr-weezing v t-lucario:** Bonsly's Teary Attack (B3 078, -30) on an Active Natu, then Natu's Peck (10) into a Psychic-weak Riolu, Lucario, Mega Lucario ex or Hitmonlee: 0 + 20 Weakness on the old engine, 0 now. The weak target needs Cyrus on a damaged benched Pokémon or a checkup knockout of Bonsly (Poison Barb).
  - **05-indeedee-stoutland v t-lucario:** the same with Indeedee ex's Psychic (30 + 30 per Energy on the target) into an Energy-less Psychic-weak target, brought in by Cyrus.
  - The kx3 arm is the more exposed: its play-outs reach many more positions than the games do.
- **Nowhere else.** C1 against t-lucario for decks 09, 06, 01 and draft A: their cut-to-0 attacks meet no Weakness (t-lucario is weak only to Psychic) and no list holds a "+X damage" effect or Intimidating Fang, so the old engine also gave 0; Bonsly is in t-lucario only, and the pool draws t-lucario only against a Fighting opponent. C2: no list holds a hit-back holder (Cursed Jewel, Spike Armor, Bristling Spikes, Needle Lariat, Shell Trap) or an attack copier, and without a holder the code is the same (Rocky Helmet, Poison Barb, Heavy Helmet, Protective Poncho and Solid Shell act as before). C3: no Basic in the lists has an on-Bench-from-hand Ability the change reads. C4: no list has a random multi-hit attack. C5: no list has a Fossil. C6: every list's Energy line is a selectable type.
- The rows are in `rows.json` (what `compare_dev.py` reads). The check's record: `REACH.json` (the workflow's agents' results).

## 4. The reading (fixed now)
`compare_dev.py` compares each game with the development run's game on the same key, content without timing (`split_collect.py`'s `content`), per arm and per row, and gives each changed game's first differing logged decision. Then:
- **Pass:** every one of the 202 kx3 and 202 km3 games equals the development run's; or games changed only in the two rows of section 3, and each changed game is reproduced exactly (equal to the development run's) by a build of 87a7f340 that leaves out C1 (501fc1dd reverted; built at night like the others), which shows C1 made the change.
- **Stop:** any game changed in another row, any game missing or unreadable, a self-check of any registration that differs from the pin's, or a changed game in the two rows that the build without C1 does not reproduce. A stop goes to the coordinator and Dustin as it is; nothing is activated.
- **What a pass allows:** the re-pin (the slow report's program moves to `/home/dacz8976/kx_r3/strength`, `rl/strength/slow_report_pin.json` and the docs, regenerated on main by `release/tools/slowpin_final.py`, then the pin tests), fast-forwarded onto main; Dustin's words of Oct 21 cover it ("Move the slow-report program only after its replay check passes"). The coordinator gets the result as laptop-019.

## 5. Order
1. This spec, `rows.json`, `REACH.json`, the configs and the scripts: committed on `laptop/kx3-replay-engine-2026-10-21` (from main 93806ec3) and pushed, before the night.
2. Night: the three registrations (each replays both self-checks), committed and pushed before any game; then the games (replay_b at 3 threads with replay_a at 2, then replay_c); then `compare_dev.py` (`COMPARE_DEV.txt`). The lane script is `lane_kxr.sh`.
3. If a named row changed: the build without C1 and its replay of that row (the next night window if needed).
4. The reading (READING.md), then the re-pin on main or the stop.
