# Slow report: smoke-held

**km3 (smoke, not kx3) on smoke-held v km3 on the public panel** (8 public lists: t-altaria, t-blaziken, t-hydreigon, t-lucario, t-sceptile, t-suicune, t-vespiquen, t-weezing). Stage `use`: a report on one deck, not development evidence.

## What it says

Question: how does smoke-held do when km3 plays it against the 8 public lists, and is that better than when km3 plays the same deck on the same deals?

Size: 32 km3 games + 32 cheap km3 baseline games (2 deals x 2 seats against each of the 8 public lists; the baseline games are the same deals with km3 on the deck).

smoke-held scored **53.1%** over **32 games** (2 deals x 2 seats against each of the 8 public lists): probably between 36.4% and 69.1% (95% interval; this range refers to these 32 km3 games). A win counts 1, a tie 1/2, a loss 0.

### How much better km3 plays this deck than km3

On the same deals, km3 scored **+0.0 points** compared with km3 piloting this deck (km3 53.1%, km3 on this deck 53.1%, over 32 paired games: each a deal and seat played by both pilots, so 32 km3 games + 32 cheap km3 baseline games); every one of the 32 comparisons gave the same difference, so no spread can be estimated from them.

## Against each public list

| opponent (km3) | km3 games | score | 95% range |
|---|---|---|---|
| t-altaria | 4 | 75.0% | 30.1% to 95.4% |
| t-blaziken | 4 | 25.0% | 4.6% to 69.9% |
| t-hydreigon | 4 | 100.0% | 51.0% to 100.0% |
| t-lucario | 4 | 0.0% | 0.0% to 49.0% |
| t-sceptile | 4 | 50.0% | 15.0% to 85.0% |
| t-suicune | 4 | 75.0% | 30.1% to 95.4% |
| t-vespiquen | 4 | 50.0% | 15.0% to 85.0% |
| t-weezing | 4 | 50.0% | 15.0% to 85.0% |

Each row's range refers only to the km3 games against that list (the row's games column); with so few games it can tell a very easy or a very hard list from an even one, not two similar lists from each other.

## Who went first

- When smoke-held went first: 53.3% over 15 games (30.1% to 75.2%)
- When smoke-held went second: 52.9% over 17 games (31.0% to 73.8%)

Each range refers only to the km3 games on its line; a few dozen games can show a large first-or-second difference, not a small one.

## The time it took

km3 took 1.2 s a game on average, median 1.1 s, slowest 3.3 s, with 2 threads going at once. km3 playing this deck took 1.3 s a game.
The run log has a sitting that did not close (for example the program was stopped by the 6:30 school-morning cut, or the run was interrupted), so the running time is estimated from the game times and the thread count: 40 s, for 64 games in all: 32 km3 games + 32 cheap km3 baseline games.

## What these numbers can and can't say

**These numbers say how smoke-held did in simulated games with km3 playing it against the 8 public lists, probably between 36.4% and 69.1%; they are not a ranking, they say nothing about decks outside those lists, and there is no pass or fail line.**

In more detail:

- km3, a strong but slow pilot, plays your deck knowing its own cards. It does not know which of the 8 public lists it faces, but its opponent is always one of them and always plays like the program km3 imagines when it looks ahead, so it is better informed here than it would be against a person on the ladder or a deck outside the 8 lists. Read the score as the optimistic end.
- The 8 lists count equally here, not by how common they are on the ladder.
- The range covers only the luck of the shuffles and coin flips in these 32 games; it does not cover how true to the real game the simulator is. It can tell whether km3 plays smoke-held clearly above or clearly below an even score against these 8 lists; it cannot tell two decks apart whose scores differ by less than the width of such a range (32.7 points here), and more deals narrow it.
- There is no pass or fail line: whether smoke-held is worth playing is a call for the player.

## What was run

- Pilots: km3 (smoke, not kx3) on the deck, km3 on the public panel. Program `/home/dacz8976/kx/strength` sha256 `5a8f5c83a791`.
- Pin `/home/dacz8976/slow_smoke2/pin_smoke.json` sha256 `97dcb802b5a0`: **NOT the committed pin** (HEAD has no rl/strength/slow_report_pin.json in /mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/2007fbb0-8999-4f68-b5ad-afe643bc4e30/scratchpad/sr/work/repo (not a git repository, no commit, or the file is not committed); git said: fatal: not a git repository (or any parent up to mount point /mnt); allowed by SLOW_REPORT_ALLOW_UNCOMMITTED_PIN (test use)): what this page says about the program rests on a pin that is not the committed one.
- Self-check of `km3`: `selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1` (copied from the pin, not replayed: the pin says it was measured on this exact binary)
- Build: claude/playout-pilot d513e37b engine tree 31dbd2e6e8ec (the frozen, tested development build), built on the laptop Oct 2; km3 240/240 v the official program, self-checks km3 81b572198c04d5d1 and kx3 31d638dbc818b0fa; KX_EXTRA_LISTS unset
- Harness source sha256 `bf9c5d681400` (what rl/strength/build.sh prints); the checkout this run was registered from has the same.
- School-morning rule: off (chosen at registration, for a machine that is not the laptop).
- Deck file `decks/events/smoke-held.txt` sha256 `62006b682027`; the file is unknown (not a git repository).
- Held-out decks in this run: smoke-held. Allowed because this is a `use` report, not development evidence; the held-out lock is unchanged.
- Registered 2026-10-08T07:20:47Z, before any game; manifest sha256 `10b59c8b90d8e611`; repository commit `None`; pin `/home/dacz8976/slow_smoke2/pin_smoke.json`.
- 2 deals x 2 seats; seeds `24669500000 + p x 10000 + i` (p = opponent index, i = deal). The program plays each deal with each pilot on the deck, from one seed.
- The engineering report with every number (paired differences, runtime, what more precision would cost) is `REPORT.md` beside this page.
