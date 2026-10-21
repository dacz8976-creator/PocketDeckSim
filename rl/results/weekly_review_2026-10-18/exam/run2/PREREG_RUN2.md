# Exam run 2: pre-registration (written Oct 21, 2026, before any adapter is frozen and before any call)

Written by the laptop session on the coordinator's instruction of Oct 21. Dustin asked for this run out of curiosity: the BoardBench benchmark shows Gemini and GPT models well ahead of Claude at board-game puzzles. He allowed about $10-15 of his Google API credits. This file is committed and pushed **before** Sonnet freezes the adapter and before any call to the model, on the exam or anywhere else, for this run.

## 1. The question
Does the frozen-4 judge prompt, answered by **one** pre-registered model, Gemini 4 Argon at high reasoning effort, pick his first plan segment more often than km3 on the unseen-positions exam? Same exam, same positions, same references, same scoring and same analysis as run 1 (`../run1/`, README_run1.md and RESULTS_run1.md). Only the model answering the prompt changes.

## 2. The judge
- **Prompt:** the frozen-4 prompt v1, byte-identical. Its fingerprint must be `0cb2421552661b563bdb49fca31aca53f468d0853661908fbbf7730fcb5ba762` (tag `judge-prompt-frozen-4`, commit 72eea776). The same render, plan-list order (shuffle-id), compact form above 80 plans and reply parser as frozen-4. Any wrapper text the adapter adds (a system instruction, a role label) must be none, or fixed, recorded in FROZEN.md and the same for every call.
- **Model:** Gemini 4 Argon, high reasoning effort. That is the only model for this exam. No other model will be tried on it, and none is a fallback: if this model can't be called, run 2 stops and is reported as not run. Trying several models and keeping the best one would let luck pass as skill.
- **The freeze:** Sonnet builds the adapter as tag `judge-prompt-frozen-5`. Its FROZEN.json must name:
  - the exact API model id and every request setting: reasoning level, max output tokens, and temperature (left at the provider's default unless FROZEN.md says otherwise, as frozen-4 left Sonnet's);
  - the official price per million input and output tokens (reasoning tokens are billed as output), with its source and the date Sonnet read it.
- **Unchanged from frozen-4,** checked by `freeze_identity.py --check` on the frozen-5 tag:
  - the plan lister (`plans_binary_sha256` bd4eeb6e…);
  - the baseline executable (`baseline_sha256` f35a1a99…) and its engine tree `70652fff03af511e32a169e16209e158a998dda6`;
  - the prompt fingerprint, and the plan settings (plan_world_seed 1, max_plans 2000, max_nodes 200000, max_steps 30).
  - `git diff 72eea776 <frozen-5>` touches only the model adapter, its tests and the freeze records.
  - The judge's engine is the exam's frozen tree, not the newly adopted main-4d48844. Changing it would change the plan lists and the baseline.
- **Development and smoke calls:** on the OLD positions only (stage A's 92 and the diagnostic's 14), never the exam, at most 5 live calls. They count against the $15 below.
- **Who:** Sonnet builds and freezes. The coordinator reviews the freeze. The laptop runs it only after the coordinator's go. Sonnet never opens the exam or its keys.

## 3. The baseline: run 1's km3 rows, reused unchanged
- **Rows:** `../run1/live-20261020T0059Z/km3.jsonl`, 153 rows (51 points × seeds 25,100,000,001-003), sha256 `3cc523d32f7290780881f79b5ec67d7945843c72af92bd0d0a8dab34a1f76fab`. Each row records `pg_pos_sha256` f35a1a99… and its `plan_list_sha256`.
- **Why they are the identical baseline:**
  - km3 is a frozen, untuned bot played by the same baseline executable on the same engine tree (70652fff), on the same exam (v1.6, `5518fd604760edb40b41d1406723f14cd8343b78`), the same plan lists and the same registered seeds.
  - Playing it again would reproduce these rows. The formal compare re-derives every plan list and checks each row's plan number, key and replay against it.
  - Reusing them spends no new seeds and keeps the two runs' km3 side literally the same.
- **Checks before use:** the run copies the file from the exam branch and checks its sha256. The compare's `--seeds` is 25100000001,25100000002,25100000003. A row that the formal path can't account for fails the batch, as in run 1.

## 4. The analysis (the same as run 1)
- **Inputs:** from exam commit 5518fd60, exactly as `../run1/prep_inputs.py` builds them.
  - The candidate view is each point's `position` only.
  - `references.json`: sha256 12e0e997….
  - `references_meta.json`: 6adca41e….
  - `eligibility.json`: 6199ddef….
  - positions: 17bea6e3….
  - The run checks all of these hashes.
- **The judge, primary:** ONE call per decision on the 51 points, through the budget wrapper (section 6).
- **The formal comparison, primary:** `judge.py compare --on-problem fail`, judge against km3.
  - Prefix agreement on the **49 primary points from 26 games**: this block carries the pass condition.
  - Full-plan agreement on the 19 full-scope points, as a separate block.
  - The 2 diagnostic points (game 20261015_210617000_iOS, excluded for exposure) in their own descriptive block.
  - Any problem at a primary point fails the batch, and then there is no verdict.
- **The repeat:** a SEPARATE second judge run for sensitivity only (`relabel_repeat.py`, then `compare --judge-repeats 2`). It never replaces the primary.
- **Statistics:** analysis.py unchanged.
  - The game-clustered bootstrap, seeded 20261019.
  - The fixed-seed Monte Carlo sign-flip test over games: 100,000 draws, seeded SEED + 1 = 20261020, the version used at 26 games.
  - At least 10 games.

## 5. The pass condition (fixed now)
- **Run 2 passes only if** the formal PRIMARY PREFIX verdict is **"judge higher"** against km3: `analysis.prefix.contrasts[0]` in `report_primary.json`, a = judge, b = km3. That means the 95% game-clustered interval of judge minus km3 lies above zero AND the sign-flip p < 0.05, with 49 points over 26 games.
- **Not a pass:** "inconclusive", "km3 higher", a failed batch or a run that stops.
- **Separate from the pass condition:** the full-scope block, the repeat, the diagnostic block and the categories.
- **What a pass means:** this model with this prompt beat km3 on this exam, and nothing more. What follows (for example a kx3 comparison, or any use of the judge) is decided afterwards, with its own cost and time.
- **Gemini against Sonnet's run 1 primary (descriptive only).** Run 1's frozen-4 judge (claude-sonnet-5-5) agreed on 11 of the 49 primary points (`../run1/live-20261020T0059Z/judge_primary.jsonl`, sha256 26381b68…; km3 22 of 49; verdict "km3 higher"). The run-2 report gives, on the same 49 points:
  - both judges' prefix agreement counts;
  - the points where they differ;
  - the paired difference.
  It has no interval, no p-value and no verdict, and no conclusion about the models rests on it.

## 6. Spend
- **Hard cap: $15 in all** (Dustin's Google API credits), through the budget wrapper (`../run1/budget_judge.py` adapted to frozen-5, same rule):
  - before a call is sent, its worst case is reserved: the prompt's bytes plus 2,000 tokens at the input price, plus the frozen max output tokens at the output price, at the official price FROZEN.json cites;
  - a call is sent only if the spent plus the reserved plus this worst case stays within the cap;
  - a call's reservation is replaced by its actual cost when it returns.
- **One ledger** carries the smoke calls, the primary and the repeat.
- **Before any exam call:**
  - The worst case of all 51 primary calls must fit within what is left of the $15, or the run stops with no call. Then Dustin and the coordinator decide; the cap is never raised silently.
  - The repeat runs only within what is left. If the cap would cut it short, it is reported as incomplete (sensitivity only).
- **A call that returns no answer** (a transport or server error) may be sent again with the identical request, at most twice, logged. An answer that was received is never asked again: the first received answer counts.
- **Reported apart:** the estimate made before the run, and the actual spend, from the provider's usage fields and the official price.

## 7. Exam freshness
- The prompt is unchanged since frozen-2.
- The model was chosen from an outside benchmark (BoardBench), not from run 1's answers. No Gemini call has been made on the exam for this project.
- So this exam is fair, unseen evidence for this model.
- A prompt change prompted by run 1's results or lessons would need new positions, not this exam.

## 8. Who and in what order
1. This file: committed and pushed on `sonnet/exam-2026-10-19` before anything else. It is mailboxed to the coordinator with its commit.
2. Sonnet: the frozen-5 adapter, developed and tested on the old positions (≤5 live calls), then the tag. The coordinator reviews it.
3. The laptop: a dry run with the mocked judge, then the live run after the coordinator's go, in a kit under `run2/` (run 1's `run_exam.sh` with the km3 step replaced by the copy and check of section 3).
4. The results go to the coordinator only, then to Dustin. The laptop writes RESULTS_run2.md on this branch.


---

## Addendum 1 (Oct 21, 2026, about 20:00Z; committed before any exam call)
Written by the laptop session from the coordinator's notes 021 (19:00Z) and 022 (19:40Z) and its go of about 19:55Z. The coordinator had reviewed Sonnet's freeze and smoke report (mailbox `coordinator__20261021T1953Z-sonnet-006`). The sections above stay as written. Where this addendum differs, it replaces them for run 2. The model and the prompt don't change. Every change below comes from the transport and from settings, and none from any reply on the exam: none has been made.

**A1. The freeze is `judge-prompt-frozen-7`** (commit 712593a1b77b203ec23fb15589c158c6bddb2bf2, annotated tag object 11e8b2d7).
- **Why Vertex AI:** Dustin chose his Google Cloud trial credits (verbatim: "Use the trial credits: build the Vertex AI version, and send me the steps to make that key"). The trial credits don't pay for AI Studio's Gemini API, so the same model is called through Vertex AI generateContent.
- **The two earlier freezes never ran on the exam:**
  - frozen-5 (544d80ff) was the AI Studio version;
  - frozen-6 (3783c9ab) called a URL without a project, which pins us-central1, where the model isn't served (HTTP 404, no charge).
- **Provider and model:** provider `gemini-vertex`, model `gemini-4-argon`, location `global` (a frozen setting every row records and the compare checks), thinking level HIGH.
- **Output and temperature:** **maxOutputTokens 32,768** (instead of the 8,000 of section 2's plan); temperature left at the provider's default.
- **Key:** `VERTEX_API_KEY`, taken from the environment, or else from the last export line of `~/.bashrc`. It is read as text, never printed, never stored.
- **Project:** passed as `--vertex-project project-45583ef0-ed57-426c-bde`. It is Dustin's project id, not a secret, and is recorded in every row. It isn't part of the freeze.
- **Price** (FROZEN.json, as Sonnet cited it): $2 / $10 per million input / output tokens through Nov 30, 2026, then $4 / $20. Reasoning tokens are billed as output. The budget wrapper reserves at the higher price.
- **Unchanged, checked by `freeze_identity.py --check` on the tag:**
  - the prompt fingerprint `0cb2421552661b563bdb49fca31aca53f468d0853661908fbbf7730fcb5ba762`;
  - the lister bd4eeb6e…;
  - the baseline f35a1a99… and its engine tree 70652fff;
  - the plan settings.
- **Section 2's "only the adapter" doesn't fully hold.** `git diff 72eea776 712593a1` also changes `formal.py` and `analysis.py`: the failed-rows setting (A3) and the game gate behind it. The setting is off by default (`abort`, run 1's behaviour). Sonnet compared the reports with frozen-6's on 2,000 randomized scenarios: they are byte-identical apart from the new report fields.
- **Why 32,768:** the smoke test's largest call, on old positions, used 11,799 output tokens (11,750 of them thinking). Under 8,000 it would have been cut off with no choice.

**A2. The smoke test** (Sonnet, OLD positions only, never the exam): 5 calls, all finished STOP with a parsed choice, $0.4234 in all at the introductory price, on its own $2 ledger.

**A3. Failed primary rows count as misses.**
- The primary compare runs with `judge.py compare --failed-judge-rows miss`. A primary judge row with no valid choice counts as a MISS (agreement 0) in the prefix and the full-scope scoring, instead of failing the batch. That covers a reply cut at the output cap, a blocked prompt, any finish but STOP, and an invalid label.
- The count of such rows, and the rows themselves, are reported.
- Any other problem still fails the batch: a missing row, a duplicate, a row that doesn't hold together, or a km3 row that can't be accounted for. In that case there is no verdict.
- This replaces, for this one case, section 4's "any problem at a primary point fails the batch".
- **The reporting rule:** if MORE than 20% of the 49 primary decisions have no valid choice (10 or more), a result that isn't a pass is reported as **"inconclusive about skill: too many failed replies"**, not as evidence about the model. A pass stays a pass, because misses can only lower the judge's prefix score.
- **Sonnet's caveats, recorded:**
  - (a) In the full-scope CONTRAST, a miss pair is kept where an answered plan that stops at a chance event would have been dropped. So that contrast can move toward zero. A game that exists only because of a miss doesn't count toward the 10-game gate. The full-scope block isn't the pass rule.
  - (b) Rows aren't authenticated. A hit hand-edited into a "failed reply" could only lower the score.
  - (c) If every judge row failed, the compare would still finish ("km3 higher"). The 20% rule above reports that as inconclusive, not as evidence.

**A4. Resending replaces section 6's rule.**
- A call that got NO model reply may be sent again ONCE, with the identical request, into a NEW `--out` file on the same ledger. That means a network or HTTP error, which `budget_judge.py` reports as exit 2, an incomplete batch.
- A model reply, including one that was cut or invalid, is NEVER asked again. The first reply counts, and A3 decides how it's scored.
- If a primary decision still has no row after that one resend, the batch is incomplete and run 2 has no verdict. That is reported as such.

**A5. The budget replaces section 6's pre-run check.** That check required the worst case of all 51 primary calls to fit. At 32,768 output tokens, that worst case is about $17-18, more than the cap. So the bound is the ledger's per-call reservation:
- each call's worst case is reserved before it is sent;
- a call is sent only while spent + reserved + its worst case stays within the cap;
- the reservation becomes the actual cost when the reply arrives.

The amounts:
- **The ledger:** the coordinator's go sets a $15 ledger. Section 6 says "$15 in all", and the smoke's $0.4234 was spent on its own ledger. So this run's ledger is **$14.57**: `--total-usd 14.57 --run-cap-usd 14.57` for the primary, on one ledger.
- **The repeat** gets what remains, under the same flags. If the bound stops it short, it is reported as incomplete (sensitivity only).
- **If the bound refuses a primary call,** the primary is incomplete: no verdict, and the cap is not raised.
- **Spend reporting:** actual spend (the provider's usage fields at the cited price) is reported apart from the reservations and from the estimate made before the run.

**A6. Who and when.** The coordinator gave the go for run 2 after this addendum is committed. API calls only, so daytime is fine. The laptop runs it:
1. a dry run first, mocked (`budget_judge.py --mock`: no key, no call);
2. then live;
3. then the formal compare with run 1's reused km3 rows, after the same freeze-identity and input-hash checks as run 1.

Results go to the coordinator only.
