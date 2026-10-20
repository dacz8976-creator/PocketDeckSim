# Exam run 1: results (live, Oct 20, 2026, 00:59-01:05Z)

**For Astra's checkpoint-3 review (the analysis review). Not yet for Dustin: the coordinator reports to him after the review.**

## What ran
- **Judge:** `judge-prompt-frozen-4`, commit 72eea776. `freeze_identity.py --check` passed (freeze_check.txt: "identity matches FROZEN.json").
  - The model is claude-sonnet-5-5 with the FROZEN settings, and every judge row is `frozen: true`.
  - `run_manifest.json` field `judge_ref_commit` is f7d5f4e5. That is the annotated TAG OBJECT, which points to commit 72eea776; prep_inputs.py used
    `git rev-parse` without `^{commit}`.
- **Kit:** the scripts at a2db950c, byte-identical at 0c0add4d (a docs-only record correction committed at 00:59:30Z, 15 s before launch). The
  spend-bound tests passed 21/21 on the tag before any call.
- **Exam:** v1.6, 5518fd60; `references.json` sha 12e0e997…, `references_meta.json` 6adca41e…. 51 points:
  - 49 primary points in 26 games, 19 of which are full-scope (in 13 games);
  - 2 diagnostic points.
- **km3:** played afresh by the frozen baseline executable (sha f35a1a99…) on the registered seeds 25,100,000,001-003.
  - 153 rows; no dry-run row was reused.
  - Per decision, km3's value is the mean over its 3 seeds. This is the frozen analysis contract (FROZEN.md, analysis.py), which PREREG_DEVIATION.md
    didn't restate. km3 is nearly deterministic: its seeds chose different plans at only 5 of the 49 primary decisions.
- **Judge calls:**
  - primary: ONE call per decision, 51 rows;
  - repeat: a SEPARATE run of 51 calls for sensitivity only;
  - both under the hard spend bound.
  - The two calls got byte-identical prompts.
- **Comparisons:** `judge.py compare --on-problem fail`. Primary and sensitivity both exited 0: `status: complete`, `formal: true`, 0 problems, 196/196
  and 245/245 expected rows resolved, no warnings.
- **Outputs:** committed with this note in `run1/live-20261020T0059Z/`. The sparse clone `repo/` is left out.
  - `run_manifest.json` holds the sha256 of every output written before it.
  - run.log gained its final "done" line after the manifest was written, so the manifest hash covers the log without that line.
  - STATUS was written after the manifest.

## The formal result: run 1 does NOT pass
**The pass condition** (pre-registered in PREREG_DEVIATION.md) was the PRIMARY PREFIX verdict "judge higher". The verdict is **"km3 higher"**.

| Prefix agreement, 49 primary points, 26 games | estimate | 95% game-clustered bootstrap interval |
|---|---|---|
| km3 (mean over its 3 seeds per decision) | 0.449 (22/49) | [0.277, 0.621] |
| judge (the one primary call per decision) | 0.224 (11/49) | [0.113, 0.339] |
| **judge − km3** | **−0.224** | **[−0.410, −0.041]** |

- **Sign-flip test over games:** p = 0.0336.
  - With 26 games this is analysis.py's fixed-seed Monte Carlo version: 100,000 draws, seeded with SEED + 1 = 20261020. The bootstrap uses
    SEED = 20261019.
  - The exact enumeration is used only up to 16 games. Computed independently over all 2^26 patterns, the exact p is 0.0344.
- **Verdict reason** (report text): "the interval excludes 0 and the sign-flip test over games agrees".
- **Per-game direction:** 12 games favour km3, 4 favour the judge, and 10 tie.
- **Interval coverage:** the interval is nominal 95%. analysis.py's own simulation puts its coverage at about 89-94% at 10-17 games; this run has 26.

**Reproduction.** An independent re-run of both compare commands from the live clone gave byte-identical reports. A from-scratch recomputation
(own bootstrap and own sign-flip test, without the harness's code) gives the same estimates, an interval within 0.005, and the same verdict.

**What the pre-registered rule says now** (PREREG_DEVIATION.md, staged decision 1, quoted):
- The coming week goes to "maintenance and upstream work, and no kx3 port is made".
- "That is a **resource choice**, not evidence that the AI approach can't help."
- "'km3 higher' would be a result about this frozen judge on these points only": prompt v1, claude-sonnet-5-5, the frozen settings, these 49 points.

### How firm the result is
**Not passing is very robust.** A pass needs the whole interval above 0, and the estimate is −0.224. No resampling seed, game left out, km3 seed or
judge call gets anywhere near "judge higher".

**The direction label "km3 higher", as opposed to "inconclusive", is narrow.** All of the checks below were done after the run, are descriptive, and
were not pre-registered:
- **Margins.** The interval's upper end is 2.0 decisions' worth below zero (−0.041 × 49), and p is 0.016 below the 0.05 threshold.
- **One more agreement.** Turning any one of 28 of the judge's 38 misses into an agreement makes the verdict "inconclusive".
- **One game left out.** Leaving out one game at a time gives "inconclusive" for 12 of the 26 games. Every interval still excludes 0; p is
  0.051-0.064 in those cases.
- **The repeat call as primary.** The repeat call agreed at 14/49 (0.286), against the primary call's 11/49. Used as primary, it gives −0.163
  [−0.363, +0.030], p 0.13: "inconclusive".
- **One km3 seed alone.** Seed 25,100,000,002 alone gives "inconclusive" (p 0.075). Seeds …001 and …003 alone give "km3 higher".
- **Sensitivity.** The pre-registered sensitivity estimate (below) has p 0.051, which the same rule would call inconclusive.

The staged decision is the same for "inconclusive" and "km3 higher", so none of this changes what happens next.

### Where the gap sits (after the run; descriptive, not a test)
- **Chance-ending points.** At 33 of the 49 primary points, the accepted plan ends at a chance event (a draw, search or coin). There the judge agreed
  at 3/33 and km3 at 16/33. At the other 16 points the judge led, 8 to 6.
- **Extra moves before the draw.** The largest single kind of judge miss is 13 of 38: a "superset" plan with every accepted move plus extra moves,
  usually an Energy attach, before the same draw or search.
  - Example: accepted `Play:Poké Ball`; the judge played `Attach:1Darkness@0 zone, Play:Poké Ball`.
  - The pre-registered plan-identity rule scores these as misses for both bots; km3 has 24 such rows. Attaching before the draw commits the Energy
    before seeing the card, so it is a real difference in the decision, not a scoring defect.
  - A post-hoc lenient rescoring that forgives superset plans gives judge 0.490 and km3 0.612. That is descriptive only.
- **Attacking at once.** In 9 more misses, the judge attacked at once where the accepted plan drew or searched first.
- **Compact prompts don't explain the gap.** On the 17 compact-form prompts (more than 80 plans) the judge was level with km3, 3 vs 2. The whole gap
  is on the 32 full-form points: judge 8, km3 20.
- **A weak hint about list position.** The judge may favour plans shown early in its shuffled list: mean relative rank 0.43, p ≈ 0.07. The
  first-shown plan wasn't over-chosen (2 of 51). This is weak and post hoc.

## Separate blocks (not part of the pass condition)
**Full-plan agreement** (the 19 full-scope points, 13 games):
- **Over all 19:** km3 0.421 (8/19).
- **Over its 16 comparable decisions (12 games):** the judge 0.500 (8/16).
- **On those same 16 decisions:** km3 0.375 (6/16). Both agree at 5, the judge only at 3, km3 only at 1, neither at 7.
- **judge − km3:** +0.125 [−0.125, +0.357]. The exact sign-flip p is 0.625 (12 games ≤ 16, so the exact test applies). Verdict: **inconclusive**.
- **3 judge plans aren't comparable.** They stop at a chance event, so they have no complete turn, and the rule drops them unscored:
  LAD-20261014_231006000_iOS-t9, LAD-20261014_233402000_iOS-t5 and LAD-20261016_015753000_iOS-t5.
- **The drop isn't neutral.** km3 fully agreed at 2 of those 3, and the judge's plan had already failed prefix agreement at 2 of them. So the drop
  favours the judge; analysis.py warns that dropping depends on the outcome.
- **The block is one-sided by structure.** All 57 full-scope km3 rows reached the end of the turn, so km3 is always comparable there.

**Sensitivity** (the judge's per-decision mean over its 2 calls; no verdict is drawn from it):
- judge: 0.255 (25/98) [0.157, 0.351].
- judge − km3: −0.194 [−0.377, −0.014]. The Monte Carlo sign-flip p is 0.051, just above 0.05. The direction therefore rests on the one primary
  call.
- **Repeat consistency:** the two calls chose the same plan at 31 of 49 primary decisions (63%) and at 32 of all 51.
- **At the 18 primary decisions where the calls differ,** only the primary call agreed at 2 and only the repeat at 5.

**Diagnostic** (the excluded game 20261015_210617000_iOS, 2 points; descriptive only):
- km3's agreement summed over the 2 decisions is 0.333: one of its 3 seeds agreed at t2.
- The judge's primary calls agreed at 0. By design only the primary call counts there; the repeat call did agree at t2.

**Category breakdown** (descriptive, primary prefix agreement, no interval or verdict; from `by_category.json`):

| group | n | judge | km3 |
|---|---|---|---|
| deck kind: Bench preparation | 30 | 0.100 | 0.433 |
| deck kind: control and combinations | 33 | 0.242 | 0.414 |
| deck kind: evolution and setup | 28 | 0.179 | 0.429 |
| deck kind: fast pressure | 7 | 0.286 | 0.429 |
| deck kind: sacrifice and recovery | 7 | 0.429 | 0.524 |
| answer kind: attack now | 22 | 0.273 | 0.364 |
| answer kind: prepare | 22 | 0.182 | 0.500 |
| answer kind: sacrifice | 5 | 0.200 | 0.600 |
| deck: 12 Ariados / Whimsicott / Ogerpon | 14 | 0.143 | 0.429 |
| deck: 13-A Ninetales / Raticate | 23 | 0.217 | 0.377 |
| deck: Kingambit list A | 12 | 0.333 | 0.611 |

- **Deck kinds overlap.** A point can carry several deck kinds: 105 memberships over 49 points.
- **The other groups don't.** The answer-kind rows and the deck rows each add up to the 49 points.
- **Not independent.** Points of one game aren't independent.

## Data quality
**The judge calls**
- All 102 ended normally (`stop_reason: end_turn`), with no parse error and no parse warning.
- The longest reply was 4,213 output tokens of the 8,000 cap; output counts include the model's thinking.
- 98 of the 102 calls returned a thinking block. The other 4 replied with text only: both calls at LAD-20261016_020517000_iOS-t2 (6 plans) and
  LAD-20261016_024253000_iOS-t1 (3 plans). The primary call missed at both.
- All judge rows are `frozen: true` and carry the expected tag (exam_run1_primary / exam_run1_repeat); no MOCK row is present.

**Plan lists**
- Both bots chose from the same plan lists: every row's `plan_list_sha256` equals the report's.
- No list was capped: median 36 plans, 6,310 in all, at most 1,236.
- The label check found no ambiguous labels.

**km3 rows**
- `pg_pos_cut`: 87 at the end of the turn and 66 at a first draw card. pg_pos plays to the end of the turn or to its first draw card, whichever comes
  first.

**Not checked: what km3 can see**
- pg_pos plays each position on a seeded deal: km3's unseen deck order, and the opponent's hidden cards filled from the pilot's own list. These are
  random fill-ins, not the recorded game's cards.
- Whether km3's search reads them wasn't checked. No answer key reached either bot: the candidate positions hold the position and id only, and all
  51 equal the exam commit's.

**Other**
- No secret appears in any committed file (count-only check).
- The verification itself made no API call and changed no output. One checker's read-only `git status` refreshed the uncommitted clone's index stat
  cache; the index contents are unchanged.

## API usage: actual, kept apart from the estimates
**Actual** (the API's own `usage` fields on every row, priced at the harness's assumed list price of $3 / $15 per million tokens; no cache tokens; the
console bill is the authority on dollars):

| | calls | input tokens | output tokens | $ at list price |
|---|---|---|---|---|
| primary | 51 | 672,134 | 63,590 | 2.970 |
| repeat | 51 | 672,134 | 62,890 | 2.960 |
| **total** | **102** | **1,344,268** | **126,480** | **5.930** |

**Conservative figures, which are NOT what was spent:**
- **The pre-run estimate:** $3.2155 per run, printed as $3.22 ($6.43 for both). It assumed 689,336 input tokens from the prompt sizes and 1,500
  output tokens a call. The actual figures were 672,134 input tokens per run (97.5%) and about 1,240 output tokens a call.
- **The spend bound's worst-case reservations:**
  - peak spent-plus-reserved was $3.50 in the primary run and $6.46 overall, against the $12-per-run and $25 caps;
  - 0 calls were refused, none failed, and the ledger closed at $5.93 of $25.
