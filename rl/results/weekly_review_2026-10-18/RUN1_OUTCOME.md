# Exam run 1: outcome and decision (Oct 20, 2026)

**Run 1 does not pass the advancement rule registered before the run.** Following PLAN.md step 5 and the staged
decision in PREREG_DEVIATION.md, this week goes to maintenance and upstream work, and no kx3 port is made. That is a
resource choice, not evidence that AI approaches can't help.

## What was tested
- **Judge:** the frozen AI judge `judge-prompt-frozen-4` (commit 72eea776): prompt v1, claude-sonnet-5-5, the frozen
  settings. It picks one whole plan from the engine's legal plans.
- **Baseline:** km3, mean over its 3 registered seeds (25,100,000,001-003).
- **Exam:** v1.6 (5518fd60), 49 primary decisions from 26 of Dustin's ladder games, never seen by the judge's
  developer. The one game with developer exposure was excluded.
- **Pass condition:** the formal primary verdict "judge higher" (game-clustered interval above 0 AND the sign-flip test).

## Result
| primary prefix agreement, 49 decisions / 26 games | estimate | 95% game-clustered interval |
|---|---|---|
| km3 | 0.449 (22/49) | [0.277, 0.621] |
| judge | 0.224 (11/49) | [0.113, 0.339] |
| judge − km3 | −0.224 | [−0.410, −0.041] |

- **Verdict:** "km3 higher". Sign-flip p 0.034, from a fixed-seed Monte Carlo at 26 games.
- **Firmness:** not passing is robust. The "km3 higher" label itself is narrow:
  - the repeat call used as primary gives "inconclusive" (p 0.13);
  - the pre-registered sensitivity estimate has p 0.051.
- **Full-plan block:** 16 comparable decisions, inconclusive (+0.125 [−0.125, +0.357]). That subset is incomplete and
  depends on the outcome, so it can't rescue the primary result.

## What the numbers mean and don't mean
- They measure **agreement with the accepted plans**: the move Dustin made, or one he accepted. They are not
  correct-play rates, win rates or strength.
- A different choice is not always a bad one.
- The run doesn't show that km3 is a trustworthy deck tester.

## Limits (Astra, checkpoint 3)
- **Hidden cards:** km3's search receives the masked observation and one reshuffled imagined own-deck order. Astra
  traced the source of pg_pos, observation.rs and the km3 player: no real hidden card reaches km3's search.
- **The imagined order:** ordinary draws are scored on that one imagined order, not on all possible draws. Its effect
  on the score wasn't measured, and it doesn't explain away the gap.

## Cost
- 102 judge calls (51 primary plus 51 repeat) and 336 s of runtime.
- 1,344,268 input and 126,480 output tokens: **$3.95 at the official $2/$10 per million**. The $5.93 in the run files
  is the harness's conservative $3/$15 assumption. The billing console wasn't inspected.

## Reviews
- Astra passed the judge freeze and the run kit before the run (mailbox 20261020T0056Z).
- Astra passed the analysis after it (mailbox 20261020T0131Z-astra-run1-analysis-pass-001). It reproduced the
  statistics independently and checked every output hash.

## Where the details are
- The full results, the row-level outputs and the post-hoc descriptive breakdowns are on branch
  `sonnet/exam-2026-10-19` (tip 4b74d4e9 and later wording fixes), `rl/results/weekly_review_2026-10-18/exam/run1/`.
- That branch holds the exam's answer key and per-decision patterns. Keep them away from anyone building or tuning a
  bot. A bot changed using those patterns turns these 49 decisions from fresh evidence into a regression check
  (PLAN.md, "fresh vs used").

## Next (maintenance)
- Upstream: PRs #424 and #426 are waiting for the maintainer's merge. A further batch needs Dustin's OK.
- Engine: the Growl-to-0 fix (branch claude/growl-zero-no-weakness) and the catch-up with upstream go in at the next pin,
  which needs Dustin's word.
- Watch for the maintainer's AI. The exam is reusable for any bot, including his through docs/bot-protocol.md.
