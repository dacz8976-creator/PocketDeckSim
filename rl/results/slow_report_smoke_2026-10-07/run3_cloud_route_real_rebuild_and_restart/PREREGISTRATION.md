# Pre-registration: slow_report_smoke-held

Written 2026-10-08T07:29:05Z, **before any game was played**. The manifest (`manifest.json`, sha256 `76ec59241ce1222ce8ff4cb2b071d74d7a1b74b538d1800915439a3240a0323c`) is exactly what the program runs; the report refuses a run whose manifest no longer matches.

## Question

km3 (smoke, not kx3) on smoke-held v km3 on the public panel. A slow report on one deck, not development: how does smoke-held do when the strong, slow pilot km3 plays it against the eight public panel lists played by km3, 2 deals x 2 seats each? Primary: the deck's score (win 1, tie 1/2, loss 0) overall and against each list, with 95% ranges; and how much better km3 plays this deck than km3 on the same deals. Realistic knowledge: km3 plays the deck knowing its own cards; the deck is never one of the lists km3 guesses its opponent from, and the panel side is never handed it. No pass or fail line; time per game is reported as a fact.

## Pilots

- **Pilot under test (arm X):** `km3` (kx3 from claude/playout-pilot@d513e37b, frozen Oct 4-5)
- **Reference (arm ref, and the opponent in both arms):** `km3` (km3 in the same build; it equals the pinned km3 (step 10's 240 games field for field, self-check 81b572198c04d5d1))
- Program: `/home/dacz8976/slow_smoke2/rebuilt/strength` sha256 `c06238fbef317a1357663a2280f68cb15bebb2b213cfd3216721d5b62338074b`; engine: claude/playout-pilot d513e37b engine tree 31dbd2e6e8ec (the frozen, tested development build), built on the laptop Oct 2; km3 240/240 v the official program, self-checks km3 81b572198c04d5d1 and kx3 31d638dbc818b0fa; KX_EXTRA_LISTS unset; THIS PROGRAM (/home/dacz8976/slow_smoke2/rebuilt/strength, sha256 c06238fbef31) is NOT the pinned binary: its build record (written by rl/strength/build.sh, not signed) says it is a rebuild of that source (build record sha256 503b9bec331b: engine tree as archived 31dbd2e6e8ec, harness source bf9c5d681400, rustc 1.93.1 (01f6ddf75 2026-02-11) (built from a source tarball)), accepted because both self-checks were replayed on the registering machine and equal the digests of the pin file in use (NOT the committed pin: test use); repository commit: `None`
- Self-check of `km3` on this build (12 fixed games, t-altaria v t-suicune): `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1` (replayed by slow_report.py on the registering machine just before registration and equal to the pin file in use, which is NOT the committed pin: test use). The same pilot code on another build must print the same digest.

## Design

- Each deck under test plays each opponent: **arm X** (pilot X on the deck, the reference on the opponent) and **arm ref** (the reference on both), on the **same deals**: the same seed, the same seat for the deck, so the same shuffles, opening hands and first player in both arms.
- Deal `i` of the pair at position `p` (deck index x 1000 + opponent index) has seed `24669600000 + p x 10000 + i`; each deal is played with the deck in seats [0, 1]. 2 deals x 2 seats x 2 arms per pair; 8 pairs; **64 games in all**.
- Threads: 2 (they change nothing about the results: every game is seeded). Logging: `deck`. Every finished game is appended to `games.jsonl` before the next starts; a stopped run resumes by skipping the games already there.

## Decks under test

| deck | file | sha256 (first 12) |
|---|---|---|
| smoke-held | `decks/events/smoke-held.txt` | 62006b682027 |

## Opponents

t-altaria, t-blaziken, t-hydreigon, t-lucario, t-sceptile, t-suicune, t-vespiquen, t-weezing

## Held-out decks

Stage `use`: a report on a deck, not development, so it is allowed on any deck and is **not development evidence**: nothing in it may be used to tune or choose a pilot. Held-out list `['02-arceus-crobat', '04-absol-hoopa-darkrai', '07-skarmory-stall', '08-garchomp-toolbox', '11-archaludon-haxorus-dragonair', '12-ariados-whimsicott-ogerpon', '13-a-ninetales-raticate', '14-comfey-raticate-hypno', '15-jolteon-oricorio-raticate', 'draft-C-meowstic-hatterene-v2', 'draft-D-entei-grimhound']`, lock `on`, unchanged by this run. Held-out decks in this run: `['smoke-held']`. The manifest lists no held-out names for the program's own guard (`heldout_decks`), which would refuse them; the names are kept under `heldout_registry` and `heldout_in_run`.

## Slow report

**km3 (smoke, not kx3) on smoke-held v km3 on the public panel**. Stage use. 2 deals x 2 seats against each of the eight public lists. No pass or fail line; not development evidence.

- deck_file: `decks/events/smoke-held.txt`
- deck_file_sha256: `62006b682027c4737111d789e342100db506809a71e5fe0962042bb6b77ca209`
- deck_file_state: `unknown (not a git repository)`
- deals: `2`
- paired: `True`
- pin: `{"path": "/home/dacz8976/slow_smoke2/pin_smoke.json", "sha256": "97dcb802b5a051a87664366642a0d61437bec0a37cfa01fb70f7480d06de52c5"}`
- program_route: `rebuilt`
- pinned_program: `/home/dacz8976/kx/strength`
- pinned_program_sha256: `5a8f5c83a7915090437e91ae7c644bdd67d1aed713f50a1f7de0bf905802a3d2`
- harness_source_sha256: `bf9c5d6814007f1f53b0dc06f1beba02261478ddc40bb5efa3bbc16c0734f86e`
- harness_source_checkout_sha256: `bf9c5d6814007f1f53b0dc06f1beba02261478ddc40bb5efa3bbc16c0734f86e`
- engine_ref: `d513e37b473f2819075e1eb2439075a8a1e65c42`
- engine_tree: `31dbd2e6e8ecd39f6756b15cdb86f48b1c8f8588`
- pin_committed: `bypassed`
- pin_committed_detail: `HEAD has no rl/strength/slow_report_pin.json in /mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/2007fbb0-8999-4f68-b5ad-afe643bc4e30/scratchpad/sr/work/repo (not a git repository, no commit, or the file is not committed); git said: fatal: not a git repository (or any parent up to mount point /mnt); allowed by SLOW_REPORT_ALLOW_UNCOMMITTED_PIN (test use)`
- registered_on: `Dustin-Laptop`
- build_record: `{"build_dir": "/home/dacz8976/slow_smoke2/build1", "build_env_unset": [], "built_at": "2026-10-08T07:28:49Z", "cargo": "cargo 1.93.1 (083ac5135 2025-12-15) (built from a source tarball)", "cargo_config_files": [], "cargo_home": "/home/dacz8976/.cargo", "engine": "d513e37b473f2819075e1eb2439075a8a1e65c42 engine tree 31dbd2e6e8ecd39f6756b15cdb86f48b1c8f8588", "engine_arg": "d513e37b473f2819075e1eb2439075a8a1e65c42", "engine_ref": "d513e37b473f2819075e1eb2439075a8a1e65c42", "engine_tree_archived": "31dbd2e6e8ecd39f6756b15cdb86f48b1c8f8588", "harness_source_sha256": "bf9c5d6814007f1f53b0dc06f1beba02261478ddc40bb5efa3bbc16c0734f86e", "home": "/home/dacz8976", "host": "Dustin-Laptop", "jobs": "8", "libc": "ldd (Ubuntu GLIBC 2.43-2ubuntu2.4) 2.43", "machine": "Linux 6.18.33.2-microsoft-standard-WSL2 x86_64", "program": "/home/dacz8976/slow_smoke2/rebuilt/strength", "program_sha256": "c06238fbef317a1357663a2280f68cb15bebb2b213cfd3216721d5b62338074b", "rebuild_command": "env HOME=/home/dacz8976 CARGO_HOME=/home/dacz8976/.cargo STRENGTH_BUILD_DIR=/home/dacz8976/slow_smoke2/build1 STRENGTH_TARGET_DIR=/home/dacz8976/slow_smoke2/target1 STRENGTH_JOBS=8 STRENGTH_REPO='/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim' bash '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/strength/build.sh' d513e37b473f2819075e1eb2439075a8a1e65c42 /home/dacz8976/slow_smoke2/rebuilt/strength", "record_file": "/home/dacz8976/slow_smoke2/rebuilt/strength.build.json", "record_sha256": "503b9bec331b5f151fb03b2e207a4286f5c22ae5d09dd373a7effbf49f2b1c97", "rustc": "rustc 1.93.1 (01f6ddf75 2026-02-11) (built from a source tarball)\nbinary: rustc\ncommit-hash: 01f6ddf7588f42ae2d7eb0a2f21d44e8e96674cf\ncommit-date: 2026-02-11\nhost: x86_64-unknown-linux-gnu\nrelease: 1.93.1\nLLVM version: 21.1.8", "schema": 1, "target_dir": "/home/dacz8976/slow_smoke2/target1"}`
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
python3 rl/strength/slow_report.py --dir /home/dacz8976/slow_smoke2/runs/2026-10-09_smoke-held --school-rule off
```
