# The thinking-time test: the reading (Oct 13, as fixed in PLAN.md)

All four registrations are merged COMPLETE: 480 games each, from 12 slices on 6 Managed Agents workers, each sealed and re-checked by
the collector. Every km3 game equals the development run's (960 of 960), and every seed matches. `read_thinking.py` computes the
reading below, and two independent recomputations plus a critic, using their own code, reproduced every number
(`recheck_output.json`).

## PRIMARY (points per 100 games; paired on 480 deals: 6 development decks without Wailord, 8 opponents, 5 deals, 2 seats)

| setting | − frozen kx3 | − candidate (m64) | win rate |
|---|---|---|---:|
| m16: `_tools _zs3`, no close-call extension | **+0.4 ± 1.4** | −4.2 ± 3.4 | 54.2 |
| m32: close calls extended to 32 play-outs | **+4.4 ± 3.1** (interval +1.3 to +7.5) | −0.2 ± 3.0 | 58.1 |
| candidate m64 (already played) | +4.6 ± 3.4 | | 58.3 |
| frozen kx3 | | | 53.8 |

**Reading, by the fixed rule: m32 is the recommended deck tester.** It is the cheapest setting whose interval against the frozen kx3 is
entirely above zero. The frozen kx3 stays the screener. Dustin picks; the held-out exam then runs his pick.

## What the numbers do and don't carry (the critic's points)

- **m32 against the candidate is −0.2 ± 3.0:** no loss detected. m32 is anywhere from about 3 points worse to about 3 points
  better than the full candidate. That is not proof that it keeps all of the gain.
- **The gain sits in the fast group and draft A.**
  - fast: +5.0 ± 4.3;
  - draft A: +10.0 ± 8.3 (one deck, 80 games);
  - setup decks: +0.6 ± 5.4 (deck 01: −1.2 ± 8.2).
- **These are the development decks the settings were developed on,** so the held-out exam is the real check.
- **m16 is about the frozen kx3:** only 12 of 480 results differ. The Tool rule and the skip bar add nothing measurable on their
  own; the gain comes from the close-call extension (m32 − m16: +4.0 ± 3.1).
- Two settings were read in order, so the chance of a false recommendation is up to about 5%.
- **Pace is unchanged.**
  - Turns per game: m32 − frozen +0.11 ± 0.21.
  - First-attack own turn: candidate +0.04, m32 −0.03, m16 −0.01 (all within ±0.07).

## Time per kx3 game

| measured | frozen | candidate | m32 | m16 |
|---|---:|---:|---:|---:|
| where | laptop | laptop | sandbox | sandbox |
| mean seconds | 186 | 548 | 780 | 490 |

- **Measured directly:** m32 takes 1.59 times m16's time, both in sandboxes.
- **Against the frozen kx3: an estimate.** m16 plays the frozen kx3's exact moves in 402 games, so m16's cost is about the frozen
  kx3's. That makes m32 about 1.6 to 1.75 times the frozen kx3, and about 0.55 to 0.6 times the full candidate. The
  laptop-to-sandbox factor (2.4 to 2.7) was not measured in this run, and worker speed varies by about ±15%.
- **The program:** m16 and m32 ran on a cloud rebuild (sha256 7e8cc544), admitted by its 12-game self-checks. 402 exact copies of
  the frozen kx3's games support that it plays the same.
