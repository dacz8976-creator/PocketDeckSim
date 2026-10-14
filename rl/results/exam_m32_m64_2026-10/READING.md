# The held-out exam of m32 and m64: the reading (Oct 14)

**Question.** On the 11 held-out decks the bots were never tuned on, does the strong bot play better than the frozen strong bot with
more close-call play-outs: 32 (m32) or 64 (m64), instead of the frozen bot's settings? Both settings also carry the Tool rule and the
skip bar, which alone added nothing measurable on the development decks. And which setting, if either, should test decks from now on?

**Answer.**
- **The rule fixed beforehand recommends m64.** It is the only setting with a gain over the frozen strong bot that the exam can show:
  +3.8 points per 100 games, with a 95% range of +0.5 to +7.1.
- **m32's gain isn't shown:** +2.1, range −0.5 to +4.7.
- **The exam can't tell m64 from m32.** Against m32, m64 is somewhere between 1.1 points worse and 4.5 points better per 100 games. So
  m64 is picked because it is the only setting with a shown gain (step 3 of the rule), not because it was shown better than m32.
- **The setup decks, stated with the pick as the plan requires.** These are the decks that build up over several turns, the planning
  weakness Dustin wanted fixed. On them:
  - m32 − frozen −1.0 (−5.1 to +3.0);
  - m64 − frozen +1.6 (−3.6 to +6.7);
  - m64 − m32 +2.6 (−1.3 to +6.6).

  So the picked setting shows no gain where that weakness lives.
- **The decision is Dustin's.**

**How it was run (`PLAN.md`, fixed before any game):**
- Every pair is the same deal, seat and seed for all four bots: 11 decks × 8 opponents × 3 deals × 2 seats = 528 pairs.
- The frozen strong bot's and the everyday bot's games are the Oct 5 exam's.
- m32 and m64 played the same 528 deals on 14 cloud workers in all: 4 for m32 and 10 for m64.
- **Build check:** every everyday-bot game played alongside them equals the Oct 5 exam's game on the same deal, 528 of 528 for each
  setting. So the pairing holds.
- The figures are `read_exam.py`'s, written before any game; its full output is `reading_output.txt`. An independent recomputation from
  the raw games matched every figure.

| comparison, points per 100 games (95% range) | all 11 decks | setup decks (4) | middle decks (3) | fast decks (4) |
|---|---|---|---|---|
| m64 − frozen | **+3.8** (+0.5 to +7.1) | +1.6 (−3.6 to +6.7) | +7.6 (+1.2 to +14.1) | +3.1 (−2.5 to +8.7) |
| m32 − frozen | +2.1 (−0.5 to +4.7) | −1.0 (−5.1 to +3.0) | +4.2 (−0.9 to +9.2) | +3.6 (−0.8 to +8.1) |
| m64 − m32 | +1.7 (−1.1 to +4.5) | +2.6 (−1.3 to +6.6) | +3.5 (−2.1 to +9.1) | −0.5 (−5.6 to +4.6) |

- **Scores against the eight panel opponents** (all piloted by the everyday bot): m64 56.8%, m32 55.1%, frozen 53.0%. The everyday bot
  itself scores 31.7% with the same decks.
- **Compared with the everyday bot playing the same decks on the same deals:** m64 +25.1, m32 +23.4, frozen +21.3. The frozen figure is
  Oct 5's own, since those are the same games.
- **In games:**
  - m64 won 49 pairs the frozen bot lost and lost 29 it won.
  - m32: 30 and 19.
  - m64 against m32: 33 and 24.
- **Pace is unchanged:** about 10.6 turns per game, and the first attack on the deck's own turn 2.3, for every setting.

**How much rests on one deck.** This check was made after the games, so it doesn't change the fixed pick.
- **The Garchomp toolbox (deck 08) carries a large share of m64's gain.** It is +18.8 over the frozen bot (+4.9 to +32.6), and 9 of the
  20 net pairs.
- **Without deck 08, no gain would be shown:** m64 − frozen would be +2.3 (−1.0 to +5.6), and m64 − m32 +0.4.
- The plan treats per-deck figures as too few to rank decks. The point here is only that the shown gain is not spread evenly.

**What the exam doesn't settle:**
- **m64 against m32.** About 6 deals per matchup instead of 3 (about twice the games) would narrow that range to ±2 points. Even then, a
  difference as small as the one measured wouldn't show.
- **The chance of a wrong pick.**
  - If neither setting truly beats the frozen bot, this rule recommends one at most about 5% of the time.
  - The risk that fits this pick is a different one. If m32 and m64 truly play alike, the rule picks m64 about 1 time in 10, mostly
    through step 3, which is how it picked here.

**Caveat: his own positions.**
- In the position study (`../pause_positions_kx3_2026-10/READING.md`), the m64 setting on the current engine (the "candidate", built on
  the merge 9a0bc5ac) made Dustin's first move less often than the frozen strong bot.
- On the 68 main positions the gap is about 7 percentage points of the 12 replays per position (range 1 to 13). These are not game
  points.
- Most of that gap, about 5.6 of the 7 points, comes from four positions where it never made his move.
- In one of them it ended the turn without taking a sure knock-out. The frozen bot does that too on other positions: such skips were
  rare and about equally common in both bots in the earlier hand check.
- A proposed attack rule for the next pilot round, to be tested both ways, is meant to catch them.
- Making his move less often isn't the same as playing worse. It is a reason to read the exam's small gain with care.

**Cost.** Thinking time is what you pay for.
- **m64 against m32:** m64 took 1,509 seconds a game in the cloud sandboxes and m32 886, about 1.7 times as long on the same deals.
- **Against the frozen bot:** its 207 seconds were measured on the laptop, so any ratio to it is an estimate across machines.
  - Sandboxes ran about 2.1 to 2.7 times slower than the laptop, which puts m64 at about 2.7 to 3.5 times the frozen bot's time per game,
    and m32 at about 1.6 to 2.0 times.
  - Measured on the laptop itself, on the development decks, m64 took about 2.9 times as long.
- **A deck report with m64 as the tester** would take roughly 3 times as long as now.
- **The exam's cloud spend** was about $31 by the coordinator's count, against $65-100 estimated before play. That covers 1,056
  strong-bot games, 1,056 one-second check games, and the workers' builds and self-checks.

**If Dustin adopts m64.**
- In the plan's words: "Carrying the picked setting to the new engine is a separate step, as step 4 was for the frozen kx3: the candidate
  merge laptop/kx3cand-on-rules2 9a0bc5ac, then a replay check." That merge already exists; it is the build the position study ran.
- **The frozen strong bot stays the screener in every case,** and every report made so far stays as it is.
- As with step 4, m64 testing decks would then need the slow-report pin re-made with its own gate.

Files: `PLAN.md` (the rule), `read_exam.py`, `reading_output.txt`, `reg_m32/` and `reg_m64/` (merged games and merge records),
`workers/`.
