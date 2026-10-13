# Slow report: draft-D-entei-grimhound

**kx3 (d513e37b, on main-c045ede) on draft-D-entei-grimhound v km3 on the public panel** (8 public lists: t-altaria, t-blaziken, t-hydreigon, t-lucario, t-sceptile, t-suicune, t-vespiquen, t-weezing). Stage `use`: a report on one deck, not development evidence.

## What it says

Question: how does draft-D-entei-grimhound do when kx3 plays it against the 8 public lists, and is that better than when km3 plays the same deck on the same deals?

**PARTIAL: 120 kx3 games + 120 cheap km3 baseline games so far (240 of the 320 games planned; both pilots' games count in the 320). The numbers below will move; read them as a snapshot.**

Size: 120 kx3 games + 120 cheap km3 baseline games so far, of 160 kx3 games + 160 cheap km3 baseline games planned.

draft-D-entei-grimhound scored **41.7%** over **120 games** (games from 6 of the 8 public lists so far): probably between 33.2% and 50.6% (95% interval; this range refers to these 120 kx3 games). A win counts 1, a tie 1/2, a loss 0.

### How much better kx3 plays this deck than km3

On the same deals, kx3 scored **+20.0 points** compared with km3 piloting this deck (kx3 41.7%, km3 on this deck 21.7%, over 120 paired games: each a deal and seat played by both pilots, so 120 kx3 games + 120 cheap km3 baseline games), probably between +12.4 and +27.6 points (95% interval; this range refers to those 120 paired games).

That range does not include no gain: on these 120 paired games kx3 did better than km3. It does not say by exactly how much: that part of the range is as wide as 120 paired games make it.

## Against each public list

| opponent (km3) | kx3 games | score | 95% range |
|---|---|---|---|
| t-altaria | 20 | 45.0% | 25.8% to 65.8% |
| t-blaziken | 20 | 30.0% | 14.5% to 51.9% |
| t-hydreigon | 20 | 35.0% | 18.1% to 56.7% |
| t-lucario | 20 | 50.0% | 29.9% to 70.1% |
| t-sceptile | 20 | 60.0% | 38.7% to 78.1% |
| t-suicune | 20 | 30.0% | 14.5% to 51.9% |
| t-vespiquen | 0 | n/a | n/a |
| t-weezing | 0 | n/a | n/a |

Each row's range refers only to the kx3 games against that list (the row's games column); with so few games it can tell a very easy or a very hard list from an even one, not two similar lists from each other.

## Who went first

- When draft-D-entei-grimhound went first: 44.3% over 61 games (32.5% to 56.7%)
- When draft-D-entei-grimhound went second: 39.0% over 59 games (27.6% to 51.7%)

Each range refers only to the kx3 games on its line; a few dozen games can show a large first-or-second difference, not a small one.

## The time it took

kx3 took 1236 s a game on average (about 21 min), median 1186 s, slowest 2618 s, with 4 threads going at once. km3 playing this deck took 1.2 s a game.
Running time from the run log: 10.6 h over 6 sittings, for 240 games in all: 120 kx3 games + 120 cheap km3 baseline games.

## What these numbers can and can't say

**These numbers say how draft-D-entei-grimhound did in simulated games with kx3 playing it against the 8 public lists, probably between 33.2% and 50.6%; they are not a ranking, they say nothing about decks outside those lists, and there is no pass or fail line.**

In more detail:

- kx3, a strong but slow pilot, plays your deck knowing its own cards. It does not know which of the 8 public lists it faces, but its opponent is always one of them and always plays like the program kx3 imagines when it looks ahead, so it is better informed here than it would be against a person on the ladder or a deck outside the 8 lists. Read the score as the optimistic end.
- The 8 lists count equally here, not by how common they are on the ladder.
- The range covers only the luck of the shuffles and coin flips in these 120 games; it does not cover how true to the real game the simulator is. It can tell whether kx3 plays draft-D-entei-grimhound clearly above or clearly below an even score against these 8 lists; it cannot tell two decks apart whose scores differ by less than the width of such a range (17.4 points here), and more deals narrow it.
- There is no pass or fail line: whether draft-D-entei-grimhound is worth playing is a call for the player.

## What was run

- Pilots: kx3 (d513e37b, on main-c045ede) on the deck, km3 on the public panel. Program `/root/slow_report_kx3/strength` sha256 `5011e227cf63`.
- The program is NOT the pinned binary (`/home/dacz8976/kx_r2/strength`, sha256 `76df495bef0b`): its build record says it is a rebuild of the pinned source, and it was accepted only because that record has the pinned engine tree and harness source and both self-checks were replayed earlier by slow_report.py (committed record `rl/results/slow_report_selfcheck_records/selfcheck_5011e227cf63_20261012T204539Z.json`, commit dbe31f48b3da, on vm) and equal the committed pin's digests, and the harness source in the checkout is the pinned build's. The record is written by the builder's own script and is not signed: what stands behind the program is those replayed self-checks (12 fixed games per pilot), not the record.
- Build record `strength.build.json` sha256 `e32b52e9684c`: engine cd20a97a2e76897fae9883389cee4bf7ce5b3d97 -> tree as archived `4ebb30a94173` (the pin's is `4ebb30a94173`), harness source `bf9c5d681400`, rustc 1.97.0 (2d8144b78 2026-07-07), cargo 1.97.0 (c980f4866 2026-06-30), built 2026-10-12T18:38:30Z on vm (Linux 6.18.44-fc-v114 x86_64); to rebuild the same bytes after a restart: `env HOME=/root CARGO_HOME=/root/.cargo STRENGTH_BUILD_DIR=/root/slow_report_kx3/build STRENGTH_TARGET_DIR=/root/slow_report_kx3/target STRENGTH_JOBS=8 STRENGTH_REPO=/home/user/PocketDeckSim bash /home/user/PocketDeckSim/rl/strength/build.sh cd20a97a2e76897fae9883389cee4bf7ce5b3d97 /root/slow_report_kx3/strength`.
- Pin `rl/strength/slow_report_pin.json` sha256 `1fc30ce48e36`: committed (byte-equal to HEAD's file in the repository this run was registered from).
- Self-check of `km3`: `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1` (accepted from the committed record `rl/results/slow_report_selfcheck_records/selfcheck_5011e227cf63_20261012T204539Z.json` (commit dbe31f48b3da): replayed there by slow_report.py on vm at 2026-10-12T20:45:39Z on a program with this sha256, equal to the committed pin; the record is a committed file, not signed, and this registration did not replay them again)
- Self-check of `kx3`: `selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa` (accepted from the committed record `rl/results/slow_report_selfcheck_records/selfcheck_5011e227cf63_20261012T204539Z.json` (commit dbe31f48b3da): replayed there by slow_report.py on vm at 2026-10-12T20:45:39Z on a program with this sha256, equal to the committed pin; the record is a committed file, not signed, and this registration did not replay them again)
- Build: laptop/kx3-on-rules2 cd20a97a engine tree 4ebb30a94173: the frozen kx3's players (claude/playout-pilot d513e37b, byte for byte) on main-c045ede's engine (rules switch 2, pinned Oct 12), built on the laptop Oct 12 with rl/strength/build.sh (harness bf9c5d68); gate 1: km3's self-check 81b572198c04d5d1, the pinned km3; kx3's self-check 31d638dbc818b0fa, equal to the old pin's; KX_EXTRA_LISTS unset. Replaces the Oct 2 build (d513e37b on its own engine, tree 31dbd2e6e8ec, program 5a8f5c83); spec rl/results/kx3_on_rules2_2026-10/SPEC.md; THIS PROGRAM (/root/slow_report_kx3/strength, sha256 5011e227cf63) is NOT the pinned binary: its build record (written by rl/strength/build.sh, not signed) says it is a rebuild of that source (build record sha256 e32b52e9684c: engine tree as archived 4ebb30a94173, harness source bf9c5d681400, rustc 1.97.0 (2d8144b78 2026-07-07)), accepted because both self-checks equal the committed pin's digests: replayed by slow_report.py on vm and recorded in rl/results/slow_report_selfcheck_records/selfcheck_5011e227cf63_20261012T204539Z.json (commit dbe31f48b3da), for a program with this same sha256; the record is a committed file, not signed, and this registration did not replay them again
- Harness source sha256 `bf9c5d681400` (what rl/strength/build.sh prints); the checkout this run was registered from has the same.
- School-morning rule: off (chosen at registration, for a machine that is not the laptop).
- Deck file `decks/brews/drafts_2026-10-01/draft-D-entei-grimhound.txt` sha256 `31035755a6d0`; the file is committed.
- Held-out decks in this run: draft-D-entei-grimhound. Allowed because this is a `use` report, not development evidence; the held-out lock is unchanged.
- Registered 2026-10-13T03:44:27Z, before any game; manifest sha256 `f5b86d1aa95a45d2`; repository commit `aa0a509e0b834ec25d9978da6dbc8db81c92742a`; pin `rl/strength/slow_report_pin.json`.
- 10 deals x 2 seats; seeds `24663900000 + p x 10000 + i` (p = opponent index, i = deal). The program plays each deal with each pilot on the deck, from one seed.
- The engineering report with every number (paired differences, runtime, what more precision would cost) is `REPORT.md` beside this page.
