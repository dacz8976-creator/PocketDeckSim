# Slow report: brew-08-entei-rainbow-cave

**kx3 (d513e37b) on brew-08-entei-rainbow-cave v km3 on the public panel** (8 public lists: t-altaria, t-blaziken, t-hydreigon, t-lucario, t-sceptile, t-suicune, t-vespiquen, t-weezing). Stage `use`: a report on one deck, not development evidence.

## What it says

Question: how does brew-08-entei-rainbow-cave do when kx3 plays it against the 8 public lists, and is that better than when km3 plays the same deck on the same deals?

**PARTIAL: 140 kx3 games + 140 cheap km3 baseline games so far (280 of the 320 games planned; both pilots' games count in the 320). The numbers below will move; read them as a snapshot.**

Size: 140 kx3 games + 140 cheap km3 baseline games so far, of 160 kx3 games + 160 cheap km3 baseline games planned.

brew-08-entei-rainbow-cave scored **74.3%** over **140 games** (games from 7 of the 8 public lists so far): probably between 66.5% and 80.8% (95% interval; this range refers to these 140 kx3 games). A win counts 1, a tie 1/2, a loss 0.

### How much better kx3 plays this deck than km3

On the same deals, kx3 scored **+12.9 points** compared with km3 piloting this deck (kx3 74.3%, km3 on this deck 61.4%, over 140 paired games: each a deal and seat played by both pilots, so 140 kx3 games + 140 cheap km3 baseline games), probably between +5.1 and +20.6 points (95% interval; this range refers to those 140 paired games).

That range does not include no gain: on these 140 paired games kx3 did better than km3. It does not say by exactly how much: that part of the range is as wide as 140 paired games make it.

## Against each public list

| opponent (km3) | kx3 games | score | 95% range |
|---|---|---|---|
| t-altaria | 20 | 65.0% | 43.3% to 81.9% |
| t-blaziken | 20 | 40.0% | 21.9% to 61.3% |
| t-hydreigon | 20 | 85.0% | 64.0% to 94.8% |
| t-lucario | 20 | 65.0% | 43.3% to 81.9% |
| t-sceptile | 20 | 85.0% | 64.0% to 94.8% |
| t-suicune | 20 | 85.0% | 64.0% to 94.8% |
| t-vespiquen | 20 | 95.0% | 76.4% to 99.1% |
| t-weezing | 0 | n/a | n/a |

Each row's range refers only to the kx3 games against that list (the row's games column); with so few games it can tell a very easy or a very hard list from an even one, not two similar lists from each other.

## Who went first

- When brew-08-entei-rainbow-cave went first: 70.8% over 65 games (58.8% to 80.4%)
- When brew-08-entei-rainbow-cave went second: 77.3% over 75 games (66.7% to 85.3%)

Each range refers only to the kx3 games on its line; a few dozen games can show a large first-or-second difference, not a small one.

## The time it took

kx3 took 530 s a game on average (about 9 min), median 463 s, slowest 1330 s, with 4 threads going at once. km3 playing this deck took 0.6 s a game.
Running time from the run log: 5.3 h over 7 sittings, for 280 games in all: 140 kx3 games + 140 cheap km3 baseline games.

## What these numbers can and can't say

**These numbers say how brew-08-entei-rainbow-cave did in simulated games with kx3 playing it against the 8 public lists, probably between 66.5% and 80.8%; they are not a ranking, they say nothing about decks outside those lists, and there is no pass or fail line.**

In more detail:

- kx3, a strong but slow pilot, plays your deck knowing its own cards. It does not know which of the 8 public lists it faces, but its opponent is always one of them and always plays like the program kx3 imagines when it looks ahead, so it is better informed here than it would be against a person on the ladder or a deck outside the 8 lists. Read the score as the optimistic end.
- The 8 lists count equally here, not by how common they are on the ladder.
- The range covers only the luck of the shuffles and coin flips in these 140 games; it does not cover how true to the real game the simulator is. It can tell whether kx3 plays brew-08-entei-rainbow-cave clearly above or clearly below an even score against these 8 lists; it cannot tell two decks apart whose scores differ by less than the width of such a range (14.3 points here), and more deals narrow it.
- There is no pass or fail line: whether brew-08-entei-rainbow-cave is worth playing is a call for the player.

## What was run

- Pilots: kx3 (d513e37b) on the deck, km3 on the public panel. Program `/root/slow_report_kx3/strength` sha256 `c3d51c4be7ff`.
- The program is NOT the pinned binary (`/home/dacz8976/kx/strength`, sha256 `5a8f5c83a791`): its build record says it is a rebuild of the pinned source, and it was accepted only because that record has the pinned engine tree and harness source and both self-checks were replayed on the registering machine (vm) and equal the committed pin's digests, and the harness source in the checkout is the pinned build's. The record is written by the builder's own script and is not signed: what stands behind the program is those replayed self-checks (12 fixed games per pilot), not the record.
- Build record `strength.build.json` sha256 `c368b19fc39f`: engine d513e37b473f2819075e1eb2439075a8a1e65c42 -> tree as archived `31dbd2e6e8ec` (the pin's is `31dbd2e6e8ec`), harness source `bf9c5d681400`, rustc 1.97.0 (2d8144b78 2026-07-07), cargo 1.97.0 (c980f4866 2026-06-30), built 2026-10-09T13:36:20Z on vm (Linux 6.18.44-fc-v80 x86_64); to rebuild the same bytes after a restart: `env HOME=/root CARGO_HOME=/root/.cargo STRENGTH_BUILD_DIR=/root/slow_report_kx3/build STRENGTH_TARGET_DIR=/root/slow_report_kx3/target STRENGTH_JOBS=8 STRENGTH_REPO=/home/user/PocketDeckSim bash /home/user/PocketDeckSim/rl/strength/build.sh d513e37b473f2819075e1eb2439075a8a1e65c42 /root/slow_report_kx3/strength`.
- Pin `rl/strength/slow_report_pin.json` sha256 `2d1a3ac47356`: committed (byte-equal to HEAD's file in the repository this run was registered from).
- Self-check of `km3`: `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1` (replayed on the registering machine just before registration, equal to the committed pin)
- Self-check of `kx3`: `selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa` (replayed on the registering machine just before registration, equal to the committed pin)
- Build: claude/playout-pilot d513e37b engine tree 31dbd2e6e8ec (the frozen, tested development build), built on the laptop Oct 2; km3 240/240 v the official program, self-checks km3 81b572198c04d5d1 and kx3 31d638dbc818b0fa; KX_EXTRA_LISTS unset; THIS PROGRAM (/root/slow_report_kx3/strength, sha256 c3d51c4be7ff) is NOT the pinned binary: its build record (written by rl/strength/build.sh, not signed) says it is a rebuild of that source (build record sha256 c368b19fc39f: engine tree as archived 31dbd2e6e8ec, harness source bf9c5d681400, rustc 1.97.0 (2d8144b78 2026-07-07)), accepted because both self-checks were replayed on the registering machine and equal the committed pin's digests
- Harness source sha256 `bf9c5d681400` (what rl/strength/build.sh prints); the checkout this run was registered from has the same.
- School-morning rule: off (chosen at registration, for a machine that is not the laptop).
- Deck file `decks/brews/brew-08-entei-rainbow-cave.txt` sha256 `b3392d824751`; the file is committed.
- Registered 2026-10-09T15:29:52Z, before any game; manifest sha256 `cf90a886ef22e9d4`; repository commit `494202760a0a59f0c5af0e5cd56516185bc78597`; pin `rl/strength/slow_report_pin.json`.
- 10 deals x 2 seats; seeds `24628600000 + p x 10000 + i` (p = opponent index, i = deal). The program plays each deal with each pilot on the deck, from one seed.
- The engineering report with every number (paired differences, runtime, what more precision would cost) is `REPORT.md` beside this page.
