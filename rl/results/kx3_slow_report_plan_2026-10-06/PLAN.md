# kx3 in Dustin's tools: an opt-in "slow report" (plan, Oct 6)

Item (B) of RUN5's Oct 6 next steps (Dustin's yes, with Astra's review). This is a plan; nothing is built yet. It comes
after gate 3 and the Tool-rule decision.

## What it is for

Dustin asks "how does this deck do with a strong pilot?" and gets an answer with its uncertainty. The decks can be his own
lists, brews or drafts. No km3 screen is needed first: a weak km3 result may just be poor piloting.

## The rules it keeps

- **Opt-in only.** The screen, the floor and every default stay km3.
- **The exact tested version.** kx3 as frozen (d513e37b), from the laptop's build: `/home/dacz8976/kx/strength`, sha256
  `5a8f5c83…`, self-check `31d638dbc818b0fa`. A later version (for example with the Tool tie-break) replaces it only after
  its own gate.
- **Both pilots named in every output:** "kx3 (d513e37b) on your deck v km3 on the public panel".
- **No floor cutoffs.** The page reports results and uncertainty in plain words, never pass or fail. The exam supports
  better play; it doesn't calibrate the floor's cutoffs for a new pilot.
- **Realistic knowledge.** His deck is never in kx3's guessing pool, and the panel side is never handed his list.

## How it is built

The plan is a new wrapper, `rl/strength/slow_report.py`, rather than a flag on run_screen or the floor. Those two have
km3's cutoffs built in, and a separate tool keeps the slow pilot out of their numbers.

1. `slow_report.py DECKFILE [--deals N] [--paired]` writes a config: his deck against the 8 panel lists, kx3 on his deck,
   km3 on the panel, N deals × 2 seats, fresh seeds from a registered block.
2. It pre-registers into `rl/results/slow_reports/<date>_<deck>/` before any game (the harness's existing step), then
   runs with checkpoint and resume.
3. It keeps the school-morning rule: no new game after 5:15 am on class days, stopped by 6:30, pushed by 7:00.
4. It writes `SLOW_REPORT.md`:
   - the deck's score against each panel list and overall, with 95% intervals;
   - both pilots and the build;
   - the time taken;
   - one plain sentence on what the numbers can and can't say.
5. With `--paired`, it also plays km3 on his deck on the same deals. That arm is almost free (about a second a game) and
   adds "how much better kx3 pilots this deck than km3", with a tighter interval.

**The held-out lock needs one change.** Today a held-out deck runs only at stage `heldout` with the lock lifted. A slow
report is use, not development, so it gets its own stage, `use`. That stage:
- is allowed on any deck;
- is recorded as `use` in the pre-registration;
- never counts as development evidence.

A later development version still needs fresh exam decks or deals, because the 11 held-out decks have now been examined
once.

**Who builds it:** Sonnet, which owns the harness: the wrapper, the `use` stage, and the page. The laptop reviews it and
integrates it.

## The cost table (measured on the laptop, all cores, two games at a time)

These are measured, not estimated:
- **The exam** (11 decks): 528 kx3 games in 15.5 hours of running, so **about 34 kx3 games an hour** (mean 207 s per game).
- **The development run** (7 decks, including the Wailord wall): about 26 an hour (mean 269 s).
- **Wall decks are far slower.** Wailord took 770 s a game, about 9 an hour.
- The km3 games of `--paired` take about a second each.

A page is 8 opponents × N deals × 2 seats, so 16N kx3 games. Intervals are 95%, for a score near 50%. The paired-gain
interval uses the exam's measured spread (sd 0.47).

| deals per opponent (N) | kx3 games | the deck's score, ± | kx3's gain over km3 (--paired), ± | time, typical deck | time, wall deck (Wailord-like) |
|---|---|---|---|---|---|
| 3 | 48 | 14 points | 13 points | 1½-2 h | about 5 h |
| 5 | 80 | 11 points | 10 points | 2½-3 h | about 9 h |
| 10 | 160 | 8 points | 7 points | 5-6 h | about 18 h |
| 30 | 480 | 4½ points | 4 points | 14-18 h | about 2 days |

So:
- a quick look at one deck (N = 5) takes an evening;
- a careful one (N = 10) takes a night;
- a wall deck needs about three times that (about 9 hours at N = 5 and about 18 at N = 10, against 2½-3 and 5-6: 9 games an hour against 26-34).

For comparison, Dustin's own testing at 10 minutes a game: 80 games is about 13 hours of his time, and 160 about 27.

## Open points (the coordinator's or Dustin's call)

1. The `use` stage, as above: one small harness change.
2. The default page size. N = 5 (an evening) is suggested, with N = 10 when a deck looks close.
3. Whether `--paired` is on by default. It is suggested on: it costs almost nothing and shows the piloting gap.
