# Slow-report demonstration for deck 03 (Wailord), built from existing games

**Existing development evidence, not a fresh test.** No game was played for this folder, kx3 or otherwise. `SLOW_REPORT_EXISTING.md` is the slow-report page for
`03-wailord-indeedee-wall`, built by `rl/strength/slow_report_existing.py` from games that were already on disk:

- the 80 kx3 games and 80 km3 baseline games of the kx3 development run (`rl/results/strength_2026-10-03_kx3_dev`, the pinned build d513e37b, deck 03 only);
- the 80 kx3 games (and 80 km3 replays) of gate 3 of the Tool tie-break (`rl/results/strength_2026-10-06_kx3_tools_gate3`, a candidate build with the rule switched on, deck 03 only).

Both source folders were only read; their games.jsonl and manifest.json hashes were the same before and after (listed on the page, and in `sources.sha256` here).
This is **not** the km3 floor check and does not touch its result: the floor check has km3 on both sides and its own line; this page has kx3 on the deck and has no pass or fail line.

## What the page answers

1. **How does the deck do with kx3, and is that better than with km3?** 80 kx3 games + 80 cheap km3 baseline games: kx3 scored 80.6% (probably 70.6% to 87.8%), km3 on the
   same deals 74.4%, a gain of +6.2 points, probably between -1.9 and +14.4 (95%). That range includes no gain at all: the 80 paired games (each a deal and seat played by both pilots)
   do not show kx3 better on this deck and do not show it worse. They do argue against a gain much larger than 14.4 points or a loss much larger than 1.9. More deals narrow it
   (each added deal against every list is 16 more kx3 games, 2 seats against each of the 8 lists, about 1¾ hours on this deck at its 9 games an hour; the plan's cost table gives the totals: a wall deck like this one takes about three times as long as a typical deck).
2. **Does the Tool tie-break change what kx3 does with this deck?** 80 kx3 games with the rule on + the 80 existing games with it off, on the same deals: the rule changed a logged
   decision in 15 of the 80 games, changed points or turns in 12, and changed the winner in none (on minus off exactly +0.0 points over 80 deals). That bounds the share of
   deals whose winner it changes at about 4.6 in 100 or less (95%); it does not show the rule useful or harmless on other decks or in more games.

## Checked against the existing pages

| item | this page | existing page |
|---|---|---|
| kx3 score, deck 03 | 80.6% | `strength_2026-10-03_kx3_dev/REPORT.md`: 80.6% |
| km3 score, same deals | 74.4% | the same file: 74.4% |
| gain, kx3 minus km3 | +6.2, probably between -1.9 and +14.4 (t interval, half-width 8.2) | the same file and `PAIR_WITH_DEV.txt`: +6.2 +- 8.1 |
| games whose logged decisions, points or turns differ with the rule on | 15 of 80 (page counts the three kinds separately: decisions 15, winners 0, points or turns 12) | `PAIR_WITH_DEV.txt`: "differ at all 15 of 80" |
| on minus off | +0.0, all 80 differences exactly 0 | `PAIR_WITH_DEV.txt`: +0.0 +- 0.0 |
| km3 baseline replayed by the gate-3 build | 80 of 80 exactly | `PAIR_WITH_DEV.txt`: 400 of 400 over the five decks |

The one difference, a half-width of 8.2 points (the page prints the two ends, -1.9 and +14.4, each rounded once from the unrounded numbers) against +- 8.1, is the interval rule only: the existing pages use 1.96 standard errors, this page (like the fresh slow report) uses the t value for
79 degrees of freedom (1.99), which is a little wider for the same 80 deals. Nothing else differs. The page's "the gain's range is 16.3 points wide" is worked out from the two printed ends (14.4 minus -1.9), so a reader can check it from the numbers on the page (twice the half-width, 16.4, would not match them).

## Regenerate

From the repo root (needs the two source folders as committed):

```
python3 rl/strength/slow_report_existing.py --deck 03-wailord-indeedee-wall --dev rl/results/strength_2026-10-03_kx3_dev --tool rl/results/strength_2026-10-06_kx3_tools_gate3 --out rl/results/slow_report_demo_wailord_2026-10-07
```

It refuses (writes no page) when a source run's manifest no longer matches its recorded hash, when the development run was not played by the pinned build, when the gate-3 run is not the
Tool tie-break build, when a gate-3 game is not one of the development run's deals, when either run does not have every game of the deck's design (80 kx3 + 80 km3 games, 10 + 10 against each list),
when the gate-3 build does not replay the development run's km3 baseline exactly, or when a gate-3 kx3 game did not start from the development run's own deal (same seed, same first player).
The page counts the gain over km3 in "paired games" (a deal and seat played by both pilots: 80 kx3 games + 80 cheap km3 baseline games), because "deals" would mean 5 per list in one place and 80 in another.

## Limits worth knowing

- The two questions are answered from the same 80 deals, so they are not independent evidence: question 2's "on" games are the development run's deals played again with one rule changed.
- Five deals against each of the 8 public lists is a small sample per list (10 kx3 games each); the per-list table separates very easy or very hard lists from even ones, not similar lists from each other.
- kx3 is better informed on these games than it would be against a person: its opponent is always one of the 8 public lists, and the opponent it imagines when it looks ahead plays like km3.
- A fresh report for this deck (new deals, kx3 on the pinned build) is `rl/strength/slow_report.py`'s job; this page asks the same first question the same way (question first, then the size, then the range and which games it refers to), but from games that already exist, and it adds the Tool tie-break question that a fresh report does not ask.
