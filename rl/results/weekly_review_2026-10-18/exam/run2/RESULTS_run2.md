# Exam run 2: results (Oct 21, 2026, 20:00-20:31Z)

**Verdict: "inconclusive". Run 2 does NOT pass** the pre-registered rule: the PRIMARY PREFIX verdict "judge higher" against km3 (`PREREG_RUN2.md` section 5 and addendum 1).
- **The judge:** Gemini 4 Argon at thinking HIGH, through Vertex AI (`judge-prompt-frozen-7`, 712593a1), with the frozen-4 prompt byte for byte.
- **The scores:** it agreed with his first plan segment on **30 of 49** primary points (0.612). km3 agreed on **22 of 49** (0.449, run 1's rows reused unchanged).
- **The difference** is +0.163. The 95% game-clustered interval is −0.014 to +0.347, which includes 0, and the sign-flip p is 0.109 (Monte Carlo, 26 games).
- No reply lacked a valid choice (0 of 102), so the "too many failed replies" rule (addendum A3) doesn't apply. This is an ordinary inconclusive result.

Outputs: `live-20261021T2000Z/` (the kit: `run_exam2.sh`, `desc_vs_run1.py`). Both formal comparisons exited 0: `formal: true`, 0 problems, 0 rows without a choice.

## The formal result (report_primary.json)
| block | judge (Gemini) | km3 | judge − km3 [95% CI] | sign-flip p | verdict |
|---|---|---|---|---|---|
| **prefix, 49 primary points, 26 games (the pass rule)** | **0.612** [0.491, 0.725] | **0.449** [0.277, 0.621] | **+0.163 [−0.014, +0.347]** | **0.109** | **inconclusive** |
| full plan, 19 full-scope points (separate) | 0.600 (15 comparable) | 0.421 | +0.200 [−0.125, +0.474] on 15 points, 11 games | 0.5 (exact) | inconclusive |

- **Full-scope block:** 4 of its 19 points were "not comparable" for both bots (dropped, not scored). That block isn't the pass rule.
- **Diagnostic block** (game 210617, excluded for exposure; 2 points): judge 0 of 2, km3 0.33 of 2.

## Sensitivity (report_sensitivity.json; descriptive, never the result)
- **The repeat:** a separate second call per decision. The two calls chose the same plan on 40 of 49 decisions (0.82).
- **Mean of the two calls:** the judge scores 0.643, and judge − km3 is +0.194 [+0.022, +0.369], sign-flip p 0.047.
- That figure would clear the bar, but by the pre-registration the repeat is sensitivity only. The primary is the one predefined call, and no run is chosen. So the result stays **inconclusive**.
- It suggests that one primary call per decision is close to the edge with 26 games, nothing more.

## Gemini v run 1's Sonnet judge (vs_run1.json; descriptive only, no interval, p-value or verdict)
| on the 49 primary points | agreed |
|---|---|
| Gemini 4 Argon (run 2) | 30 |
| claude-sonnet-5-5 (run 1, frozen-4) | 11 |
| km3 (mean of 3 seeds) | 22.0 |

- Both judges agreed on 10 points. Gemini alone on 20, Sonnet alone on 1, neither on 18.
- The difference, Gemini − Sonnet, is +0.388.

## By category (by_category.json; descriptive, a point counts in each of its kinds)
**Answer kind:**
- attack now: judge 0.59, km3 0.36 (n 22);
- prepare: 0.64 v 0.50 (n 22);
- sacrifice: 0.60 v 0.60 (n 5).

**Deck:**
- 12: 0.64 v 0.43 (n 14);
- 13-A: 0.52 v 0.38 (n 23);
- Kingambit: 0.75 v 0.61 (n 12).

Small groups; no interval.

## How it ran
- **Before any call:**
  - `freeze_identity --check` passed;
  - the harness's 406 tests passed;
  - positions, references and eligibility matched run 1's sha256;
  - no plan list was capped;
  - the reused km3 rows matched run 1's sha256 3cc523d3….
  - A mocked dry run (`dry-20261021T1959Z`, laptop only, not a result) went through first.
- **Primary, first batch:**
  - 3 calls answered;
  - 2 failed with HTTP 429 RESOURCE_EXHAUSTED (a rate or quota refusal: no model reply);
  - the budget wrapper then held back the other 46 (no call is sent after a failure).
- **The one resend (addendum A4)** went to the 48 decisions with no row: the 2 refused calls plus the 46 never sent. All 48 answered.
  - No reply was asked twice: every one of the 51 decisions has exactly one primary reply.
  - Then the repeat: 51 calls, all answered.
- **Every reply** of the 102 finished STOP with a parsed choice: model gemini-4-argon, location global, the project recorded on every row.
- **Output size:** the largest reply used 25,246 output tokens (thinking included), under the 32,768 cap. 8,000 would have cut it off.

## Spend
- **Tokens:** 861,088 input and 391,643 output (386,705 thinking, 4,938 answer).
- **Actual cost at the introductory price** ($2 / $10 per million tokens, in force through Nov 30), from the replies' own usage fields: **$5.64**.
  - The primary was $2.98; the repeat, $2.66.
  - Sonnet's smoke test, on its own ledger, was $0.42. So everything spent on run 2 so far comes to $6.06.
- **The ledger shows $7.67 of $14.57.** The two 429 refusals were charged at their worst case ($2.03 together), because whether a refused call is billed can't be known. Google doesn't normally bill a 429. The billing console has the real figure, including whether the trial credit, not a card, paid.
- **The estimate before the run** was about $2.91 per judge run.

## What it means (by the pre-registration)
- Gemini 4 Argon, with the frozen prompt, did not show that it beats km3 on this exam. The interval includes no difference. That is not evidence that it is worse: the estimate leans its way, and the 26-game exam can't settle a difference this size.
- **Run 1's "km3 higher"** was the frozen-4 Sonnet judge, a different model, on the same exam and the same km3 rows.
- No other model is tried on this exam (PREREG_RUN2 section 2). Run 2 is reported as run, with no second attempt.
- Results go to the coordinator only.
