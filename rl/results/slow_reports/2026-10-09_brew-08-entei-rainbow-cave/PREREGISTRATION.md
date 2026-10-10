# Pre-registration: slow_report_brew-08-entei-rainbow-cave

Written 2026-10-09T15:29:52Z, **before any game was played**. The manifest (`manifest.json`, sha256 `cf90a886ef22e9d4b9dbb0763a2b7fd42b2d3dd7e2a4706d0246a7527432b338`) is exactly what the program runs; the report refuses a run whose manifest no longer matches.

## Question

kx3 (d513e37b) on brew-08-entei-rainbow-cave v km3 on the public panel. A slow report on one deck, not development: how does brew-08-entei-rainbow-cave do when the strong, slow pilot kx3 plays it against the eight public panel lists played by km3, 10 deals x 2 seats each? Primary: the deck's score (win 1, tie 1/2, loss 0) overall and against each list, with 95% ranges; and how much better kx3 plays this deck than km3 on the same deals. Realistic knowledge: kx3 plays the deck knowing its own cards; the deck is never one of the lists kx3 guesses its opponent from, and the panel side is never handed it. No pass or fail line; time per game is reported as a fact.

## Pilots

- **Pilot under test (arm X):** `kx3` (kx3 from claude/playout-pilot@d513e37b, frozen Oct 4-5)
- **Reference (arm ref, and the opponent in both arms):** `km3` (km3 in the same build; it equals the pinned km3 (step 10's 240 games field for field, self-check 81b572198c04d5d1))
- Program: `/root/slow_report_kx3/strength` sha256 `c3d51c4be7ff27615359db71d09b2de0867aed773b0c8434d46dea7b7e73a9de`; engine: claude/playout-pilot d513e37b engine tree 31dbd2e6e8ec (the frozen, tested development build), built on the laptop Oct 2; km3 240/240 v the official program, self-checks km3 81b572198c04d5d1 and kx3 31d638dbc818b0fa; KX_EXTRA_LISTS unset; THIS PROGRAM (/root/slow_report_kx3/strength, sha256 c3d51c4be7ff) is NOT the pinned binary: its build record (written by rl/strength/build.sh, not signed) says it is a rebuild of that source (build record sha256 c368b19fc39f: engine tree as archived 31dbd2e6e8ec, harness source bf9c5d681400, rustc 1.97.0 (2d8144b78 2026-07-07)), accepted because both self-checks were replayed on the registering machine and equal the committed pin's digests; repository commit: `494202760a0a59f0c5af0e5cd56516185bc78597`
- Self-check of `km3` on this build (12 fixed games, t-altaria v t-suicune): `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1` (replayed by slow_report.py on the registering machine just before registration and equal to the committed pin). The same pilot code on another build must print the same digest.
- Self-check of `kx3` on this build (12 fixed games, t-altaria v t-suicune): `selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa` (replayed by slow_report.py on the registering machine just before registration and equal to the committed pin). The same pilot code on another build must print the same digest.

## Design

- Each deck under test plays each opponent: **arm X** (pilot X on the deck, the reference on the opponent) and **arm ref** (the reference on both), on the **same deals**: the same seed, the same seat for the deck, so the same shuffles, opening hands and first player in both arms.
- Deal `i` of the pair at position `p` (deck index x 1000 + opponent index) has seed `24628600000 + p x 10000 + i`; each deal is played with the deck in seats [0, 1]. 10 deals x 2 seats x 2 arms per pair; 8 pairs; **320 games in all**.
- Threads: 4 (they change nothing about the results: every game is seeded). Logging: `deck`. Every finished game is appended to `games.jsonl` before the next starts; a stopped run resumes by skipping the games already there.

## Decks under test

| deck | file | sha256 (first 12) |
|---|---|---|
| brew-08-entei-rainbow-cave | `decks/brews/brew-08-entei-rainbow-cave.txt` | b3392d824751 |

## Opponents

t-altaria, t-blaziken, t-hydreigon, t-lucario, t-sceptile, t-suicune, t-vespiquen, t-weezing

## Held-out decks

Stage `use`: a report on a deck, not development, so it is allowed on any deck and is **not development evidence**: nothing in it may be used to tune or choose a pilot. Held-out list `['02-arceus-crobat', '04-absol-hoopa-darkrai', '07-skarmory-stall', '08-garchomp-toolbox', '11-archaludon-haxorus-dragonair', '12-ariados-whimsicott-ogerpon', '13-a-ninetales-raticate', '14-comfey-raticate-hypno', '15-jolteon-oricorio-raticate', 'draft-C-meowstic-hatterene-v2', 'draft-D-entei-grimhound']`, lock `on`, unchanged by this run. Held-out decks in this run: `(none)`. The manifest lists no held-out names for the program's own guard (`heldout_decks`), which would refuse them; the names are kept under `heldout_registry` and `heldout_in_run`.

## Slow report

**kx3 (d513e37b) on brew-08-entei-rainbow-cave v km3 on the public panel**. Stage use. 10 deals x 2 seats against each of the eight public lists. No pass or fail line; not development evidence.

- deck_file: `decks/brews/brew-08-entei-rainbow-cave.txt`
- deck_file_sha256: `b3392d82475130e400887897b75e1add156ca4151f3ce85b38042233bd7336a0`
- deck_file_state: `committed`
- deals: `10`
- paired: `True`
- pin: `{"path": "rl/strength/slow_report_pin.json", "sha256": "2d1a3ac4735671772efe2767d0f0d305af8d3e02b99e3f4a851eaebcb25a092c"}`
- program_route: `rebuilt`
- pinned_program: `/home/dacz8976/kx/strength`
- pinned_program_sha256: `5a8f5c83a7915090437e91ae7c644bdd67d1aed713f50a1f7de0bf905802a3d2`
- harness_source_sha256: `bf9c5d6814007f1f53b0dc06f1beba02261478ddc40bb5efa3bbc16c0734f86e`
- harness_source_checkout_sha256: `bf9c5d6814007f1f53b0dc06f1beba02261478ddc40bb5efa3bbc16c0734f86e`
- engine_ref: `d513e37b473f2819075e1eb2439075a8a1e65c42`
- engine_tree: `31dbd2e6e8ecd39f6756b15cdb86f48b1c8f8588`
- pin_committed: `yes`
- pin_committed_detail: `none`
- registered_on: `vm`
- build_record: `{"build_dir": "/root/slow_report_kx3/build", "build_env_unset": [], "build_fs": "ext2/ext3", "built_at": "2026-10-09T13:36:20Z", "cargo": "cargo 1.97.0 (c980f4866 2026-06-30)", "cargo_config_files": [], "cargo_home": "/root/.cargo", "engine": "d513e37b473f2819075e1eb2439075a8a1e65c42 engine tree 31dbd2e6e8ecd39f6756b15cdb86f48b1c8f8588", "engine_arg": "d513e37b473f2819075e1eb2439075a8a1e65c42", "engine_ref": "d513e37b473f2819075e1eb2439075a8a1e65c42", "engine_tree_archived": "31dbd2e6e8ecd39f6756b15cdb86f48b1c8f8588", "harness_source_sha256": "bf9c5d6814007f1f53b0dc06f1beba02261478ddc40bb5efa3bbc16c0734f86e", "home": "/root", "host": "vm", "jobs": "8", "libc": "ldd (Ubuntu GLIBC 2.39-0ubuntu8.9) 2.39", "machine": "Linux 6.18.44-fc-v80 x86_64", "program": "/root/slow_report_kx3/strength", "program_sha256": "c3d51c4be7ff27615359db71d09b2de0867aed773b0c8434d46dea7b7e73a9de", "rebuild_command": "env HOME=/root CARGO_HOME=/root/.cargo STRENGTH_BUILD_DIR=/root/slow_report_kx3/build STRENGTH_TARGET_DIR=/root/slow_report_kx3/target STRENGTH_JOBS=8 STRENGTH_REPO=/home/user/PocketDeckSim bash /home/user/PocketDeckSim/rl/strength/build.sh d513e37b473f2819075e1eb2439075a8a1e65c42 /root/slow_report_kx3/strength", "record_file": "/root/slow_report_kx3/strength.build.json", "record_sha256": "c368b19fc39f2d6a9223183534bfa9d258a811d97ffcb5ad8f5805da1b8a35c7", "rustc": "rustc 1.97.0 (2d8144b78 2026-07-07)\nbinary: rustc\ncommit-hash: 2d8144b7880597b6e6d3dfd63a9a9efae3f533d3\ncommit-date: 2026-07-07\nhost: x86_64-unknown-linux-gnu\nrelease: 1.97.0\nLLVM version: 22.1.6", "schema": 1, "target_dir": "/root/slow_report_kx3/target"}`
- school_rule: `off`
- school_days: `mon,tue,wed,thu,fri`

## Analysis plan (fixed now)

- Score of a game for the deck: win 1, tie 0.5, loss 0. The page (`SLOW_REPORT.md`) reports the deck's score over the pilot's games, overall and against each opponent list, each with a **Wilson 95% range** (valid at 0% and 100% and for few games), and by who went first.
- The baseline comparison is **on** (the default): the **paired difference** `d = score(arm X) - score(arm ref)` on each (deck, opponent, deal, seat), reported as its mean with a **Student t 95% interval** over the paired games (a deal and seat played by both pilots), and what that range does and does not include.
- The page states its question before its size, says which games each range refers to, and says what a wide range can and cannot answer; it has no pass or fail line. `REPORT.md` is the engineering view of the same games (it uses mean ± 1.96·sd/√n for its paired tables) and is a detail, not the headline.
- Intended-line rates from `rl/strength/intended_lines.json` (sha256 `80778f3c4a58`): per game and per use, per arm, with the paired difference where it is per game.
- No pass/fail threshold is set by this document. A slow pilot is reported with its time and cost, not rejected.

## Run

A slow report is run and resumed through its wrapper, which removes the variables that would tune the pilot or change the rules from the program's environment, does NOT apply the school-morning rule (chosen at registration: it never pauses for school mornings), and checks the registration, the deck files and the program it was registered with, a rebuild of the pinned source by its build record (accepted after both self-checks were replayed on the registering machine; a resume needs the same sha256, or a rebuild whose build record has the same engine tree and harness hash and whose two self-checks are replayed again) before every sitting:

```
python3 rl/strength/slow_report.py --dir /home/user/PocketDeckSim/rl/results/slow_reports/2026-10-09_brew-08-entei-rainbow-cave --school-rule off
```
