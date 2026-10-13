# Pre-registration: slow_report_brew-07-hoopa-darkrai-sableye

Written 2026-10-12T20:49:33Z, **before any game was played**. The manifest (`manifest.json`, sha256 `1536d72073d7573d9f4ffb1ebb6d5cbed2d49255d2c07b63fa9bf5389424b941`) is exactly what the program runs; the report refuses a run whose manifest no longer matches.

## Question

kx3 (d513e37b, on main-c045ede) on brew-07-hoopa-darkrai-sableye v km3 on the public panel. A slow report on one deck, not development: how does brew-07-hoopa-darkrai-sableye do when the strong, slow pilot kx3 plays it against the eight public panel lists played by km3, 10 deals x 2 seats each? Primary: the deck's score (win 1, tie 1/2, loss 0) overall and against each list, with 95% ranges; and how much better kx3 plays this deck than km3 on the same deals. Realistic knowledge: kx3 plays the deck knowing its own cards; the deck is never one of the lists kx3 guesses its opponent from, and the panel side is never handed it. No pass or fail line; time per game is reported as a fact.

## Pilots

- **Pilot under test (arm X):** `kx3` (kx3 from claude/playout-pilot@d513e37b, frozen Oct 4-5; on rules switch 2's engine since Oct 12 (laptop/kx3-on-rules2 cd20a97a))
- **Reference (arm ref, and the opponent in both arms):** `km3` (km3 in the same build; it equals the pinned km3 (step 10's 240 games field for field, self-check 81b572198c04d5d1))
- Program: `/root/slow_report_kx3/strength` sha256 `5011e227cf63619cc8ca9750ee69090037844f8e7abcd0432776b1e2ae3b7f0e`; engine: laptop/kx3-on-rules2 cd20a97a engine tree 4ebb30a94173: the frozen kx3's players (claude/playout-pilot d513e37b, byte for byte) on main-c045ede's engine (rules switch 2, pinned Oct 12), built on the laptop Oct 12 with rl/strength/build.sh (harness bf9c5d68); gate 1: km3's self-check 81b572198c04d5d1, the pinned km3; kx3's self-check 31d638dbc818b0fa, equal to the old pin's; KX_EXTRA_LISTS unset. Replaces the Oct 2 build (d513e37b on its own engine, tree 31dbd2e6e8ec, program 5a8f5c83); spec rl/results/kx3_on_rules2_2026-10/SPEC.md; THIS PROGRAM (/root/slow_report_kx3/strength, sha256 5011e227cf63) is NOT the pinned binary: its build record (written by rl/strength/build.sh, not signed) says it is a rebuild of that source (build record sha256 a20475b7438b: engine tree as archived 4ebb30a94173, harness source bf9c5d681400, rustc 1.97.0 (2d8144b78 2026-07-07)), accepted because both self-checks equal the committed pin's digests: replayed by slow_report.py on vm and recorded in rl/results/slow_report_selfcheck_records/selfcheck_5011e227cf63_20261012T204746Z.json (commit 381f955b7f7c), for a program with this same sha256; the record is a committed file, not signed, and this registration did not replay them again; repository commit: `051bd9dcfb1ab5e30eee897e84bd85dfbe60c735`
- Self-check of `km3` on this build (12 fixed games, t-altaria v t-suicune): `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1` (accepted from the committed record rl/results/slow_report_selfcheck_records/selfcheck_5011e227cf63_20261012T204746Z.json (commit 381f955b7f7c): an earlier replay by slow_report.py of a program with this sha256, equal to the committed pin; not replayed at this registration). The same pilot code on another build must print the same digest.
- Self-check of `kx3` on this build (12 fixed games, t-altaria v t-suicune): `selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa` (accepted from the committed record rl/results/slow_report_selfcheck_records/selfcheck_5011e227cf63_20261012T204746Z.json (commit 381f955b7f7c): an earlier replay by slow_report.py of a program with this sha256, equal to the committed pin; not replayed at this registration). The same pilot code on another build must print the same digest.

## Design

- Each deck under test plays each opponent: **arm X** (pilot X on the deck, the reference on the opponent) and **arm ref** (the reference on both), on the **same deals**: the same seed, the same seat for the deck, so the same shuffles, opening hands and first player in both arms.
- Deal `i` of the pair at position `p` (deck index x 1000 + opponent index) has seed `24608700000 + p x 10000 + i`; each deal is played with the deck in seats [0, 1]. 10 deals x 2 seats x 2 arms per pair; 8 pairs; **320 games in all**.
- Threads: 4 (they change nothing about the results: every game is seeded). Logging: `deck`. Every finished game is appended to `games.jsonl` before the next starts; a stopped run resumes by skipping the games already there.

## Decks under test

| deck | file | sha256 (first 12) |
|---|---|---|
| brew-07-hoopa-darkrai-sableye | `decks/brews/brew-07-hoopa-darkrai-sableye.txt` | 304227955001 |

## Opponents

t-altaria, t-blaziken, t-hydreigon, t-lucario, t-sceptile, t-suicune, t-vespiquen, t-weezing

## Held-out decks

Stage `use`: a report on a deck, not development, so it is allowed on any deck and is **not development evidence**: nothing in it may be used to tune or choose a pilot. Held-out list `['02-arceus-crobat', '04-absol-hoopa-darkrai', '07-skarmory-stall', '08-garchomp-toolbox', '11-archaludon-haxorus-dragonair', '12-ariados-whimsicott-ogerpon', '13-a-ninetales-raticate', '14-comfey-raticate-hypno', '15-jolteon-oricorio-raticate', 'draft-C-meowstic-hatterene-v2', 'draft-D-entei-grimhound']`, lock `on`, unchanged by this run. Held-out decks in this run: `(none)`. The manifest lists no held-out names for the program's own guard (`heldout_decks`), which would refuse them; the names are kept under `heldout_registry` and `heldout_in_run`.

## Slow report

**kx3 (d513e37b, on main-c045ede) on brew-07-hoopa-darkrai-sableye v km3 on the public panel**. Stage use. 10 deals x 2 seats against each of the eight public lists. No pass or fail line; not development evidence. Self-check: accepted from the committed record rl/results/slow_report_selfcheck_records/selfcheck_5011e227cf63_20261012T204746Z.json (commit 381f955b7f7c), not replayed at registration.

- deck_file: `decks/brews/brew-07-hoopa-darkrai-sableye.txt`
- deck_file_sha256: `304227955001a14076eeeebf8de4d7868e4643242ca8a18e0c804c67651f6c49`
- deck_file_state: `committed`
- deals: `10`
- paired: `True`
- pin: `{"path": "rl/strength/slow_report_pin.json", "sha256": "1fc30ce48e364f0669c4840c98f26fe31dbc35708007e977e9ccc2e8d2a050a1"}`
- program_route: `rebuilt`
- pinned_program: `/home/dacz8976/kx_r2/strength`
- pinned_program_sha256: `76df495bef0b057fd28b4991dce76d3e3e1772667694161c945f17364f9c4e08`
- harness_source_sha256: `bf9c5d6814007f1f53b0dc06f1beba02261478ddc40bb5efa3bbc16c0734f86e`
- harness_source_checkout_sha256: `bf9c5d6814007f1f53b0dc06f1beba02261478ddc40bb5efa3bbc16c0734f86e`
- engine_ref: `cd20a97a2e76897fae9883389cee4bf7ce5b3d97`
- engine_tree: `4ebb30a941737d16b80adddbd1466761e0670e63`
- pin_committed: `yes`
- pin_committed_detail: `none`
- registered_on: `vm`
- build_record: `{"build_dir": "/root/slow_report_kx3/build", "build_env_unset": [], "build_fs": "ext2/ext3", "built_at": "2026-10-12T18:38:54Z", "cargo": "cargo 1.97.0 (c980f4866 2026-06-30)", "cargo_config_files": [], "cargo_home": "/root/.cargo", "engine": "cd20a97a2e76897fae9883389cee4bf7ce5b3d97 engine tree 4ebb30a941737d16b80adddbd1466761e0670e63", "engine_arg": "cd20a97a2e76897fae9883389cee4bf7ce5b3d97", "engine_ref": "cd20a97a2e76897fae9883389cee4bf7ce5b3d97", "engine_tree_archived": "4ebb30a941737d16b80adddbd1466761e0670e63", "harness_source_sha256": "bf9c5d6814007f1f53b0dc06f1beba02261478ddc40bb5efa3bbc16c0734f86e", "home": "/root", "host": "vm", "jobs": "8", "libc": "ldd (Ubuntu GLIBC 2.39-0ubuntu8.9) 2.39", "machine": "Linux 6.18.44-fc-v114 x86_64", "program": "/root/slow_report_kx3/strength", "program_sha256": "5011e227cf63619cc8ca9750ee69090037844f8e7abcd0432776b1e2ae3b7f0e", "rebuild_command": "env HOME=/root CARGO_HOME=/root/.cargo STRENGTH_BUILD_DIR=/root/slow_report_kx3/build STRENGTH_TARGET_DIR=/root/slow_report_kx3/target STRENGTH_JOBS=8 STRENGTH_REPO=/home/user/PocketDeckSim bash /home/user/PocketDeckSim/rl/strength/build.sh cd20a97a2e76897fae9883389cee4bf7ce5b3d97 /root/slow_report_kx3/strength", "record_file": "/root/slow_report_kx3/strength.build.json", "record_sha256": "a20475b7438b55fd257c7ad2f0636b16e39c3c5468e4c93b72fca9ff073e695b", "rustc": "rustc 1.97.0 (2d8144b78 2026-07-07)\nbinary: rustc\ncommit-hash: 2d8144b7880597b6e6d3dfd63a9a9efae3f533d3\ncommit-date: 2026-07-07\nhost: x86_64-unknown-linux-gnu\nrelease: 1.97.0\nLLVM version: 22.1.6", "schema": 1, "target_dir": "/root/slow_report_kx3/target"}`
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
python3 rl/strength/slow_report.py --dir /home/user/PocketDeckSim/rl/results/slow_reports/2026-10-12_brew-07-hoopa-darkrai-sableye --school-rule off
```
