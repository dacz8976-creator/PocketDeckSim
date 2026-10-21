# Exam run 3 (exam v2): pre-registration (written Oct 21, 2026, before any game is selected or any position built)

Written by the laptop session on the coordinator's instruction of Oct 21, from Dustin's decision (verbatim, to the coordinator): "I'll play more ranked games this week first; set the cutoff before Dual Fusion lands."
- **Why this run:** run 2 (`../run2/RESULTS_run2.md`) was "inconclusive". Gemini 4 Argon agreed with his first plan segment on 30 of 49 points and km3 on 22: +0.163 [−0.014, +0.347], sign-flip p 0.109.
- **What run 3 does:** it repeats the test on fresh decisions Gemini has never seen, with the same frozen judge and the same pass rule's machinery, and it decides the question **pooled with run 2 under a stricter bar**.
- **Nothing exists yet:** no game has been selected, no position built, no label written and no bot or judge run for exam v2.

## 1. The games: a mechanical window
- **In:** every ranked game Dustin recorded **after** the last game in exam v1.6, through **Sunday Oct 25, 2026, 11:59 PM Central (04:59Z Oct 26)**, or the moment Dual Fusion is released in the game, if that is earlier.
  - v1.6's games are listed in exam_2026-10-19.json, commit 5518fd60, including its excluded and diagnostic game 20261015_210617000_iOS. The last is 20261016_031512000_iOS.
  - **Times** are the recordings' start times as their packets give them (SOURCE.json and the recording name), compared in UTC.
  - **"Ranked"** follows the review rules: a computer (Auto) battle, a rules test or a pause game is not a ranked game.
- **Out:** any game already in v1.6. No game is dropped for its result, deck, opponent or content.
- **The only exclusions are v1.6's written ones,** each listed with its reason in the selection record:
  - a recording that can't be used (no full review, a clip that starts mid-game, a mode not proven to be ranked);
  - no exact deck list (QR-verified, or matched card for card to a list in the repository);
  - developer exposure (someone who builds or runs the judge saw that game's answer material).
- **Pre-Dual-Fusion only.** The engine can't convert positions holding the new dual-type cards, so a game played after the release is outside the window by definition, not dropped.
- **Already known:** the candidate games known today are the 18 of Oct 19 (`BattleLogsData/Evidence/DRIVE_INBOX_2026-10-20`) and the 6 played Oct 16-17 (`DRIVE_LADDER_2026-10-19`, `DRIVE_LADDER_REMAINING_2026-10-19`). Each still goes through the rules above. Games he plays through Oct 25 are added the same way once Codex's reviews are complete.

## 2. The points: every usable decision, v1.6's written rules unchanged
- **A point is every one of his turns that is USABLE** under v1.6's inventory brief (`../build/INV_BRIEF.md`): board_known = yes, hand_known = yes, move_known = yes and real_choice = yes, coded from the game's full review (REVIEW.md and its metadata, text only).
  - "Partly" and "unclear" are not usable. Near-usable turns aren't used.
  - Any answer kind counts (prepare, attack now, sacrifice, abandon or other).
- **No discretionary picking.** v1.6's stage 2 (`../build/A_BRIEF.md`) chose 48-56 of its usable turns with quotas and preferences:
  - at most 4 per game;
  - Kingambit at most 35% of points;
  - every sacrifice and abandon turn;
  - at least 12 "attack now";
  - preferring unusual lines.

  Those quotas and preferences are **not** applied. Every usable turn becomes a point.
- **Building:** each point is built as in v1.6's stage 3 (`../build/A_BRIEF.md`, `../build/BUILD.md`), with the same legal-moves-only program that built v1.6, `~/exam/bin/pg_legal_v14` (sha256 dcefe4ea…). It never constructs a bot.
  - **Its source** is `~/exam/src_legal`, a copy of the stage-A pg_pos source with the legal-only mode (`../build/BUILD.md`).
  - **Its `engine/src` tree is 648f4137, not the frozen tree 70652fff's `src` (a52bafd9).** Cargo.lock is the same. v1.6 was built the same way.
  - What the judge and km3 see is re-derived at run time by the frozen lister and baseline on 70652fff. The formal compare refuses a plan list or recorded line that doesn't hold there.
  - No hidden future.
  - Every approximation is marked.
  - His whole recorded move must apply step by step.
  - A point that can't be built cleanly is dropped and listed with its reason, never padded.
- **The candidate view, the scoring scope, the chance-first and free-chance rules, the label format and the references** are v1.6's (`../README.md`, v1.2-v1.6 sections).
- **Labels use v1.6's adjudication exactly** (`key_rule`):
  - the key is what a good player of his decks would do, which by default is his recorded move;
  - the accepted alternatives carry reasons, and rejected alternatives carry `certified_by`.
- **Dustin's answers** to the unclear spots (v1.6 asked him 5) are recorded verbatim and frozen, with the whole exam v2, its references and its eligibility file, **before any bot or judge output exists for it**.
- **Who labels:** the labels are made by a fresh worker that hasn't seen run 2's per-point results, from the packets and v1.6's rules only. The laptop session, which has seen those results, does the mechanics: inventory plumbing, building, validation and freezing. It doesn't decide accepted alternatives. That's an extra safeguard beyond v1.6's procedure; the coordinator may change who labels before the work starts.
- **Exposure:** Sonnet, the judge's developer, never opens exam v2 or its keys. If anyone who builds or runs the judge sees a game's answer material, that game is excluded from the primary as in v1.6, kept and reported separately with a dated reason.

## 3. The independent selection check (before any bot runs)
- A FRESH credit-worker job that hasn't seen run 2's per-point patterns checks that section 1's window and section 2's rules were applied to every game in the window. The coordinator launches it when the laptop says the build is ready.
- It reports the category mix (deck, answer kind) and the share of chance-ending points next to run 2's.
- Its findings are fixed or answered before the freeze. No bot or judge runs until it has reported.

## 4. The primary result: runs 2 + 3 pooled, the FINAL stage of this series
- **Measure:** Gemini (the frozen-7 judge's primary call) minus km3 (mean over its 3 seeds), prefix agreement, on the primary points of run 2 (49 points, 26 games) and run 3 together.
- **The game is the cluster.** Run 2's and run 3's games are different games by construction.
- **Statistics:** analysis.py's estimator and resampling, unchanged except the level.
  - the game-clustered bootstrap, two-sided **97.5%** interval, seed 20261019;
  - the game-level sign-flip test, two-sided, Monte Carlo with 100,000 draws (exact enumeration only up to 16 games), seed 20261020;
  - at least 10 games.
- **PASS = the 97.5% interval lies entirely above 0 AND the sign-flip p < 0.025.** Anything else is not a pass.
- **The pooling script** combines the two runs' formal reports (each one's per-decision rows, as the formal compare accounts for them) and calls analysis.py's functions at that level.
  - It is written, tested and committed **before run 3's km3 or judge rows exist**.
  - The test: on run 2 alone at 95% it must reproduce run 2's `report_primary.json` contrast (+0.163265, −0.014184, +0.346939, p 0.108869) to the printed digits.
- **Said plainly:**
  - **Stage 2 was declared after stage 1 was seen.** Run 2 was planned as a single test; this second stage and its pooling were decided after its "inconclusive" result. That is why the bar is stricter.
  - **There will be no stage 3,** and no re-pooling on this question, until a bigger fresh set (50 or more new labelled games) exists.

## 5. Secondary results (reported, NOT deciding)
- **Run 3 alone at run 2's rule,** the clean replication: the formal compare's primary prefix verdict on run 3's points (95% game-clustered interval and sign-flip p < 0.05, at least 10 games). With fewer than 10 primary games, no verdict, as analysis.py says.
- **The chance-ending stratum on its own:** the points where an accepted line ends at a chance event (a draw, search or coin), counted as `../run1/RESULTS_run1.md` counted them. It is reported for run 3 and pooled, with its interval, and no verdict is drawn from it.
- **Also reported:**
  - the full-scope block;
  - the repeat (sensitivity, run 2's design);
  - the categories;
  - Gemini against run 1's Sonnet judge, where points overlap (none will, since run 3's points are new).

## 6. Fixed for both stages
- **The judge:** `judge-prompt-frozen-7` (712593a1) untouched: gemini-vertex, gemini-4-argon, location global, thinking HIGH, maxOutputTokens 32,768.
  - The prompt fingerprint is 0cb2421552661b563bdb49fca31aca53f468d0853661908fbbf7730fcb5ba762.
  - The project is passed as `--vertex-project project-45583ef0-ed57-426c-bde`.
- **Run 2's rules, as in `../run2/PREREG_RUN2.md` addendum 1:**
  - `compare --failed-judge-rows miss`;
  - the >20% no-choice reporting rule (A3), for run 3 and for the pooled set;
  - the resend rule (A4: a call with no model reply is re-sent once; a reply is never asked again);
  - one primary call per decision and a separate repeat for sensitivity.
- **Engine and builds: the same as run 2,** not the newly adopted main-4d48844 engine:
  - the frozen engine tree 70652fff03af511e32a169e16209e158a998dda6;
  - the lister bd4eeb6e…;
  - the baseline f35a1a99…;
  - for building the positions, v1.6's `pg_legal_v14` (dcefe4ea…; see section 2 for its source tree).
  - `freeze_identity.py --check` must pass on the tag before any call.
- **km3 is played fresh** on run 3's positions, 3 seeds, from a NEW seed block registered in START_HERE before the run.
  - The intended block is 25,101,000,000-25,101,999,999, with km3 seeds 25,101,000,001-003.
  - If START_HERE shows that block taken, the next free block is used. Either way it is registered before any run 3 row is made.

## 7. The model version
- Every judge row records the Vertex model version string the reply gives, and the date.
- Run 2's rows say "gemini-4-argon".
- **If any run 3 row says otherwise,** pooling is off: run 3 is reported as a new series, under section 5's single-run rule only, and section 4 isn't computed.

## 8. The sentences, written now
- **If the pooled result is not a pass:** "promising, unproven; revisit when 50+ new labelled games exist".
  - With the >20% no-choice rule triggered, instead: "inconclusive about skill: too many failed replies".
- **If it passes:** "Gemini is a better plan picker than km3 on his decisions".
  - The formal kx3 test (frozen-5) still comes before anyone says it beats our best bot.

## 9. Budget
- A **$15 ledger** from Dustin's Google Cloud trial credits, under his standing OK: the primary run at `--total-usd 15 --run-cap-usd 15`, the repeat on what remains, the same per-call worst-case reservation.
- Actual spend (the replies' usage fields at the cited price) is reported apart from the reservations and from the estimate.
- No smoke calls: frozen-7 is unchanged.

## 10. Order and who
1. This file, committed and pushed on `sonnet/exam-2026-10-19` (`run3/`) before any selection. Mailboxed to the coordinator.
2. **The window closes** Oct 25, 11:59 PM Central, or at Dual Fusion's release. Codex completes the reviews.
3. **The build** (light, daytime): the usability coding per section 2 (inventory), the positions with `pg_legal_v14`, the validation, the labels (a fresh worker), and Dustin's answers.
4. **Before any bot or judge output:**
   - the independent selection check (section 3);
   - then the freeze: exam v2, references, eligibility and the pooling script, committed.
5. **The runs:** km3 rows (new seed block); then the judge (API only); then the formal compare on run 3, the pooled primary and the secondaries.
6. Results to the coordinator only, as `RESULTS_run3.md` here.
