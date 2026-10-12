# Slow report: smoke-held

**km3 (smoke, not kx3) on smoke-held v km3 on the public panel** (8 public lists: t-altaria, t-blaziken, t-hydreigon, t-lucario, t-sceptile, t-suicune, t-vespiquen, t-weezing). Stage `use`: a report on one deck, not development evidence.

## What it says

Question: how does smoke-held do when km3 plays it against the 8 public lists, and is that better than when km3 plays the same deck on the same deals?

**PARTIAL: 4 km3 games + 4 cheap km3 baseline games so far (8 of the 64 games planned; both pilots' games count in the 64). The numbers below will move; read them as a snapshot.**

Size: 4 km3 games + 4 cheap km3 baseline games so far, of 32 km3 games + 32 cheap km3 baseline games planned.

smoke-held scored **50.0%** over **4 games** (games from 1 of the 8 public lists so far): probably between 15.0% and 85.0% (95% interval; this range refers to these 4 km3 games). A win counts 1, a tie 1/2, a loss 0.

### How much better km3 plays this deck than km3

On the same deals, km3 scored **+0.0 points** compared with km3 piloting this deck (km3 50.0%, km3 on this deck 50.0%, over 4 paired games: each a deal and seat played by both pilots, so 4 km3 games + 4 cheap km3 baseline games); every one of the 4 comparisons gave the same difference, so no spread can be estimated from them.

## Against each public list

| opponent (km3) | km3 games | score | 95% range |
|---|---|---|---|
| t-altaria | 4 | 50.0% | 15.0% to 85.0% |
| t-blaziken | 0 | n/a | n/a |
| t-hydreigon | 0 | n/a | n/a |
| t-lucario | 0 | n/a | n/a |
| t-sceptile | 0 | n/a | n/a |
| t-suicune | 0 | n/a | n/a |
| t-vespiquen | 0 | n/a | n/a |
| t-weezing | 0 | n/a | n/a |

Each row's range refers only to the km3 games against that list (the row's games column); with so few games it can tell a very easy or a very hard list from an even one, not two similar lists from each other.

## Who went first

- When smoke-held went first: no games yet
- When smoke-held went second: 50.0% over 4 games (15.0% to 85.0%)

Each range refers only to the km3 games on its line; a few dozen games can show a large first-or-second difference, not a small one.

## The time it took

km3 took 0.3 s a game on average, median 0.3 s, slowest 0.5 s, with 2 threads going at once. km3 playing this deck took 0.4 s a game.
Running time from the run log: 2 s over 1 sitting, for 8 games in all: 4 km3 games + 4 cheap km3 baseline games.

## What these numbers can and can't say

**These numbers say how smoke-held did in simulated games with km3 playing it against the 8 public lists, probably between 15.0% and 85.0%; they are not a ranking, they say nothing about decks outside those lists, and there is no pass or fail line.**

In more detail:

- km3, a strong but slow pilot, plays your deck knowing its own cards. It does not know which of the 8 public lists it faces, but its opponent is always one of them and always plays like the program km3 imagines when it looks ahead, so it is better informed here than it would be against a person on the ladder or a deck outside the 8 lists. Read the score as the optimistic end.
- The 8 lists count equally here, not by how common they are on the ladder.
- The range covers only the luck of the shuffles and coin flips in these 4 games; it does not cover how true to the real game the simulator is. It can tell whether km3 plays smoke-held clearly above or clearly below an even score against these 8 lists; it cannot tell two decks apart whose scores differ by less than the width of such a range (70.0 points here), and more deals narrow it.
- There is no pass or fail line: whether smoke-held is worth playing is a call for the player.

## What was run

- Pilots: km3 (smoke, not kx3) on the deck, km3 on the public panel. Program `/home/dacz8976/slow_smoke2/rebuilt/strength` sha256 `c06238fbef31`.
- The program is NOT the pinned binary (`/home/dacz8976/kx/strength`, sha256 `5a8f5c83a791`): its build record says it is a rebuild of the pinned source, and it was accepted only because that record has the pinned engine tree and harness source and both self-checks were replayed on the registering machine (Dustin-Laptop) and equal the digests of the pin file in use (NOT the committed pin: test use), and the harness source in the checkout is the pinned build's. The record is written by the builder's own script and is not signed: what stands behind the program is those replayed self-checks (12 fixed games per pilot), not the record.
- Build record `strength.build.json` sha256 `503b9bec331b`: engine d513e37b473f2819075e1eb2439075a8a1e65c42 -> tree as archived `31dbd2e6e8ec` (the pin's is `31dbd2e6e8ec`), harness source `bf9c5d681400`, rustc 1.93.1 (01f6ddf75 2026-02-11) (built from a source tarball), cargo 1.93.1 (083ac5135 2025-12-15) (built from a source tarball), built 2026-10-08T07:28:49Z on Dustin-Laptop (Linux 6.18.33.2-microsoft-standard-WSL2 x86_64); to rebuild the same bytes after a restart: `env HOME=/home/dacz8976 CARGO_HOME=/home/dacz8976/.cargo STRENGTH_BUILD_DIR=/home/dacz8976/slow_smoke2/build1 STRENGTH_TARGET_DIR=/home/dacz8976/slow_smoke2/target1 STRENGTH_JOBS=8 STRENGTH_REPO='/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim' bash '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/strength/build.sh' d513e37b473f2819075e1eb2439075a8a1e65c42 /home/dacz8976/slow_smoke2/rebuilt/strength`.
- Pin `/home/dacz8976/slow_smoke2/pin_smoke.json` sha256 `97dcb802b5a0`: **NOT the committed pin** (HEAD has no rl/strength/slow_report_pin.json in /mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/2007fbb0-8999-4f68-b5ad-afe643bc4e30/scratchpad/sr/work/repo (not a git repository, no commit, or the file is not committed); git said: fatal: not a git repository (or any parent up to mount point /mnt); allowed by SLOW_REPORT_ALLOW_UNCOMMITTED_PIN (test use)): what this page says about the program rests on a pin that is not the committed one.
- **The program changed mid-run** (2026-10-08T07:36:36Z): sha256 `c06238fbef31` -> `18f39c0b9a4e` after a restart or rebuild; its build record has the pinned engine tree and harness source (record `26893dc24648`) and both self-checks were replayed again on Dustin-Laptop and equal the digests of the pin file in use (NOT the committed pin: test use). 0 games of the 8 played so far were started before this change and 8 after; the numbers above pool them.
- Self-check of `km3`: `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1` (replayed on the registering machine just before registration, equal to the pin file in use (NOT the committed pin: test use))
- Build: claude/playout-pilot d513e37b engine tree 31dbd2e6e8ec (the frozen, tested development build), built on the laptop Oct 2; km3 240/240 v the official program, self-checks km3 81b572198c04d5d1 and kx3 31d638dbc818b0fa; KX_EXTRA_LISTS unset; THIS PROGRAM (/home/dacz8976/slow_smoke2/rebuilt/strength, sha256 c06238fbef31) is NOT the pinned binary: its build record (written by rl/strength/build.sh, not signed) says it is a rebuild of that source (build record sha256 503b9bec331b: engine tree as archived 31dbd2e6e8ec, harness source bf9c5d681400, rustc 1.93.1 (01f6ddf75 2026-02-11) (built from a source tarball)), accepted because both self-checks were replayed on the registering machine and equal the digests of the pin file in use (NOT the committed pin: test use)
- Harness source sha256 `bf9c5d681400` (what rl/strength/build.sh prints); the checkout this run was registered from has the same.
- School-morning rule: off (chosen at registration, for a machine that is not the laptop).
- Deck file `decks/events/smoke-held.txt` sha256 `62006b682027`; the file is unknown (not a git repository).
- Held-out decks in this run: smoke-held. Allowed because this is a `use` report, not development evidence; the held-out lock is unchanged.
- Registered 2026-10-08T07:29:05Z, before any game; manifest sha256 `76ec59241ce1222c`; repository commit `None`; pin `/home/dacz8976/slow_smoke2/pin_smoke.json`.
- 2 deals x 2 seats; seeds `24669600000 + p x 10000 + i` (p = opponent index, i = deal). The program plays each deal with each pilot on the deck, from one seed.
- The engineering report with every number (paired differences, runtime, what more precision would cost) is `REPORT.md` beside this page.
