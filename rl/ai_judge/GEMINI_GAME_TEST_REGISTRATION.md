# The Gemini finished-game test: registration (frozen-8)

Written on 2026-10-30T21:24:16Z, before any Google call and before any scored game, on branch `laptop/gemini-game-test-2026-10-30`. The gates below ran on code commit `bd967042f6630e951ffc0f4b9cf13eb2fdcb78ed`. This file and `rl/ai_judge/FROZEN8.json` are in the next commit, which carries the tag `judge-prompt-frozen-8`. Nothing in this file was written after any stage-1 game.

## Contents

1. What is registered (with stage 2's money in Dustin's words)
2. Pre-registration v3.1, as approved
3. The amendments: coordinator notes 095, 096, 103, 105, 106, 108, 109, 110 and 112
4. The 16 FROZEN-8 deviations
5. The FROZEN-8 record
6. Gate results before stage 1
7. Run-procedure notes

## 1. What is registered

- **The test:** does the frozen Gemini plan judge, playing whole games as the pilot, win more finished games than kx3 on the same deals? Design, gates, labels and analysis: section 2, as changed by the amendments in section 3.
- **Dustin's go** (relayed by the coordinator in note 098, his words: "Yes, go ahead") covers the build on Claude credits (cap $15), the gates, frozen-8, and stage 1: at most 16 unscored deals, Google cap $15, under coordinator-096's rules. **Stage 2 is not covered;** its ledger is set by Dustin after stage 1, from cost and time data only, and recorded in an addendum before any scored game.
- **Pilot decks:** 09-mega-manectric-heliolisk and 11-archaludon-haxorus-dragonair (decks/dustin). **Opponent lists:** t-lucario and t-suicune (decks/screen/opponents). **Opponent policies:** km3 and kx3.
- **Seeds:** the block 25,103,000,000-25,103,001,599; seed = base + 100 x cell + k. Every gate and dry run so far used k 90-99 (never scored). Stage 1 uses k = 80.
- **The freeze:** frozen-8 = frozen-7 plus the 16 deviations in section 4, recorded in FROZEN8.json (section 5). The build cost $11.77 of the $15 Claude-credit cap. No Google money has been spent.
- **Text sources:** section 2 is the approved PREREG v3.1 file; section 3 copies each note in full (headings moved down three levels, nothing else changed); section 4 is printed from `freeze8.DEVIATIONS`; section 5 and the chain lines in section 6 are copied from the tool outputs; section 6's earlier gates are summarised from the laptop's result notes.

### Stage 2's money, in Dustin's words before stage 1

Dustin said this in the coordinator's session on Oct 30 at about 16:30Z, before stage 1 and before any outcome existed (coordinator-112, verbatim):

> "There wasn't anything special about the $100 limit, if we need to increase it to finish that is okay with me. Now for future costs if the price is going to double, I'm probably not going to be willing to pay that much per game, but while I have credits, I don't mind"

- The ~$100 Google reserve is not a ceiling. Dustin will fund stage 2 beyond it, from his Google credits, to finish.
- Not at doubled prices. Gemini 4 Argon's price doubles after Nov 30, and the registered stop date (Nov 27, 23:59 CT) keeps the test before that.
- Stage 2's ledger is still set by Dustin after stage 1, from stage 1's cost and time data only. His words above come before stage 1 and are outcome-blind. Stage 1 stays capped at $15.

## 2. Pre-registration v3.1, as approved

Copied from the approved file (sha256 `2950d3328163f0dd20f8aed5a1ec41a2b88a263b166b4e76d8e7d1068601456b`); its headings are moved down two levels.

### Pre-registration v3.1: the Gemini finished-game test (PLAN step 4)

- **Status:** v3.1, the coordinator's calls applied (coordinator-095 and 096; 096 approved the rest of v3). Nothing is built or spent. Nothing starts before Dustin's go: a build on Claude credits (cap $15), the gates, then stage 1 on Google (cap $15).
- **v2** folded in two independent critiques of v1 (wf_dff71018-24a).
- **v3 changes from v2:**
  - the freeze name frozen-8;
  - kx3 route protocol_bot `--bot kx3`;
  - the opponent lists t-lucario and t-suicune (approved, 096);
  - v3.1: the go threshold of 80, and a stage-1 cap hit ending stage 1, not the test (096);
  - **stage 2's ledger set by Dustin after stage 1, from cost and time data only** (§5);
  - the power line in the report's first paragraph.

#### 1. The question, and what each outcome leads to

**Question.** When the frozen Gemini plan judge picks the plans for whole games, does it win more finished games than kx3 does on the same deals?

**Background:**
- Single decisions: the judge chose better than km3 (run 3 pooled +0.172, PASS) and than kx3 (K21 +0.198, EXPERIMENT label).
- Astra's rule: finished games only if the judge beats kx3 by more than its wobble. K21 did.

| Outcome (§6) | Course |
|---|---|
| PASS (judge higher) | The Gemini pilot becomes the candidate pilot for Dustin's decks. The next step is a question to Dustin on funding and engine (see §9). |
| kx3 higher | Stop the Gemini pilot. kx3 stays the pilot. |
| inconclusive | Stop spending under this registration. Report the CI as the range of gains not ruled out. Any further game test needs Dustin's new go and a fresh registration. **No pooling with this test** (declared now). |
| too few deals / pilot not tested / not testable | Report as such, with the reason. Not evidence either way. |

At the Nov 15 re-check, whatever isn't stage 1's spend or stage 2's set ledger goes back to reviews, so the credits don't expire unused. Stage 2's ledger is held until stage 2 ends or Nov 27, whichever comes first.

#### 2. Engine and programs (named before any game)

- **Engine:** the accepted adapter tip **2639a261**, engine tree **e36452d3**.
  - That's main's engine c8c79c63 plus the adapter's hooks. N3 showed 200 of 200 games identical. INFORMATION_MODEL is v8.
  - The engine stays fixed even if R8 lands first, unless the pilot decks need refused printings (§4). Then it's a new freeze and a new registration on R8.
  - A PASS carries over to R8 only after §2's gates are repeated on R8.
- **Decks:** only lists that pass the card-support preflight on this engine.
- **kx3:** the slow report's program of record (RECORD 23d8a9b5).
  - It's rebuilt on e36452d3 by applying kx3's own files **as a patch**. Only kx3's files may differ from e36452d3, and the adapter's hooks must survive.
  - **ONE route serves every kx3 seat:** the (K) arm, the (G) remainder and the kx3 opponent. **The route is protocol_bot `--bot kx3`** (coordinator-095), subject to the parity gate. If the shadow role can't run through it, I go back to the coordinator before building anything else.
  - The (G) remainder kx3 runs **in shadow**: it is fed every observation and event of the game, and asked only at fallback points.
  - **Gates:**
    - sc_kx3 text equals the pin;
    - an N3/N4-style parity check: protocol_bot `--bot kx3` against in-engine kx3, byte-identical choices on 25 or more dev seeds, both seats;
    - **shadow equality:** at sampled fallback points, the shadow instance's choices equal in-engine kx3's on the same states.
  - **What each player knows, recorded as a condition of the result:** kx3's opponent-list knowledge (poolmeta) v the judge's (the prompt shows only the observation).
- **km3:** deckgym `km3` on the same build.
- **The judge:**
  - **Kept exactly from frozen-7:** gemini-4-argon on Vertex AI (location global); the prompt template (fingerprint 0cb24215); thinking HIGH; maxOutputTokens 32768; the compact form above 80 plans; one call per decision; frozen-7's resend rule.
  - **New, and a recorded deviation, under the freeze name frozen-8** (= frozen-7 plus these two):
    - (i) the lister rebuilt on e36452d3;
    - (ii) the converter from the adapter's `pdl_observation` to the lister's input and to the prompt's board text.
- **The Gemini pilot ("judge bot")**, a protocol bot that opts into `pdl_observation` and `pdl_events`. At each intervention point (§3) it:
  1. lists plans from the observation only;
  2. **asserts that the plans' set of first steps equals the legal action list the engine sent.** A mismatch goes to fallback (a), is logged, and is counted;
  3. asks the judge to pick a plan;
  4. follows the plan by **exact action identity**, never by label, checking the predicted state hash after each step. A mismatch makes the plan stale;
  5. re-asks after a draw, a chance event, an opponent choice, or a stale step;
  6. sends a fresh plan whose first step is illegal to fallback (a), never re-asking the same list.
  - Forced single-option actions never reach it.

**Gates before stage 1** (each must pass, or stop and report):
1. **Lister equality:** each of the 92 old dev positions is loaded into e36452d3, exported as `pdl_observation`, and run through the full game path. Plan list and prompt bytes (prompt_sha256) must equal frozen-7's.
   - **Exclusion rule, mechanical and listed before the comparison:** a position is excluded only if its root legal sets differ between the two engines.
2. **Leakage:** on dev-game states, the hidden information is changed (opponent hand, both deck orders, the fill-in seed). Plan list and prompt bytes must stay byte-identical.
3. **Mock-judge dry run:** a random valid choice over 100 or more dev games, both seats, both policies. Required: 0 illegal moves, 0 loops, and every plan either played step for step or stopped with a logged reason.
4. **kx3 gates** as above.
5. **Freeze checks:** fingerprint; model, location, thinking, tokens and the compact rule; the sha of every binary and script. They run again before each night.
6. **The analysis script:** committed with mock-data tests before stage 1, and reproducing a known result, as pool_runs.py did.

#### 3. Intervention points, the remaining-move player, the expansion bar (written first)

- **Intervention points:** every decision the engine asks the Gemini seat (more than one legal action) when no saved plan step applies.
  - That covers turn starts, re-ask triggers, setup choices and opponent-turn choices (e.g. a new Active after a knockout).
  - Setup and opponent-turn points are reported separately, because the judge has never been shaped on them.
- **The remaining-move player is kx3** (the shadow instance). It decides only on:
  - (a) a lister failure, an empty list, or a first-step-set mismatch;
  - (b) the expansion bar;
  - (c) a sent judge call with no usable answer after frozen-7's resend;
  - (d) the per-game call cap.
- **HTTP 429 and transport errors are not (c).** They wait and retry: up to 3 tries over 10 minutes. Only then do they count as (c).
- **Fallback rate** = fallback intervention points ÷ all intervention points in (G) games, pooled. It's also reported per game, with reasons.
  - **Over 10% = "pilot not tested".**
- **Expansion bar:** more than **2,000 plans**, or a lister node or memory cap set in the kit. A 600 s lister time limit is a hang guard only, and lister seconds are logged.
  - For scale, the most seen so far is 1,203.
- **Per-game call cap:** **75 calls per game in stage 1**. In stage 2 it is 3 × the largest calls-per-game in stage 1. Calls beyond it go to fallback (d).

#### 4. Cells, seats, seeds

**Cells:** 16 = 2 pilot decks × 2 opponent lists × 2 opponent policies (km3, kx3) × 2 seats. They're numbered in the kit:

| Cell bit | 0 | 1 |
|---|---|---|
| deck | A | B |
| list | 1 | 2 |
| policy | km3 | kx3 |
| seat | 0 | 1 |

**Pilot decks:** two of Dustin's own, one fast-pressure and one evolution/setup.
- From decks/dustin/ on main, or his QR decodes. **Never from the exam branch.**
- **Open (D):** which two. If he names none, I propose two from decks/dustin/ that pass the preflight on e36452d3.
- If his picks need any of the 55 refused printings, the test waits for R8. I tell the coordinator before any re-freeze.

**Opponents, approved by coordinator-096** (lib/deck_classifier.py on the 8 panel lists; both played cleanly on e36452d3 in the adapter's night run):
- **List 1, fast: t-lucario** (Fighting). AGGRO; no Stage 2; Riolu → Mega Lucario ex hits for 90, with X Speed and Korrina; setup score 6.
- **List 2, setup: t-suicune** (Water). RAMP; Frigibax → Baxcalibur by Rare Candy beside Suicune ex and Chien-Pao ex; the slowest setup score of the panel, 11.

**Unit:** one seat-specific deal (a seed for one cell), played twice on identical inputs:
- **(G)** the Gemini pilot plus the kx3 remainder;
- **(K)** kx3 alone in the pilot's seat.

**Seat** means the deck's seat index. The engine decides who goes first by a coin from the seed, so going first is reported as a descriptive split.

**Seeds:** the block **25,103,000,000-25,103,001,599** (the coordinator has recorded it as taken). Its START_HERE row goes on main as the first step after Dustin's go, before any gate or game.
- Seed = base + 100 × cell + k:
  - stage 2: k = 0..(N/16 − 1), at most 0-7;
  - stage 1: k = 80;
  - a stage-1 restart (after a code fix): k = 81-89, the next unused one each time;
  - dry runs and gates: k = 90-99 (160 seeds). Gates may reuse these seeds among themselves; none is ever scored.

**Order:** k-major, all 16 cells for one k before k+1, so any stop leaves whole blocks.

**Concurrency:** one game at a time (the 6 GB WSL cap, and lower 429 risk).

#### 5. Size, money, time

- **Stage 1, measurement:** 16 deals, k = 80, one per cell, both arms.
  - **Not scored.**
  - It measures: ledger charge and actual cost per game, calls per game, seconds per (G) and (K) game, the fallback rate, failures and the input-path assertions.
  - **Deal order, fixed in the kit before the go:** the first 6 deals cover both pilot decks and both opponent lists, each at least twice, with both policies and both seats among them. The other 10 cells follow.
  - **Cap:** $15 of ledger charge, meaning actual cost plus any failed call charged at its worst case.
    - Within stage 1, a new deal starts only if the headroom ≥ $2 + 2 × the largest per-game charge so far.
    - **A cap hit before 16 deals ends stage 1, not the test** (coordinator-096):
      - with **≥ 6 complete (G)+(K) deals**, the cost and time data per deal and per pilot deck go to Dustin and the coordinator, and Dustin either sets stage 2's ledger or stops;
      - with **< 6**: STOP and report.
    - **Plainly:** at this plan's own estimate ($0.75-2.25 a game), 16 deals cost $12-36 of ledger charge, so stage 1 may well end on the cap after 6-16 deals.
- **After stage 1, its cost and time data go to Dustin and the coordinator. This step is outcome-blind: stage 1 is unscored, and no win is computed.** The report gives:
  - ledger charge and actual cost per game (mean and largest);
  - calls and seconds per (G) and (K) game;
  - the fallback rate and failures;
  - the N each candidate ledger would buy;
  - the money available: **about $85 of the ~$100 reserve after stage 1**, or about $72 if counted as ~$250 of credits − the ~$163 review cap − stage 1. At the estimate, N = 128 can't fit, and N ≥ 80 fits only at the low end of the cost range, unless the review cap changes.
- **Dustin sets stage 2's ledger** before any scored game. Stage 2's ledger is NOT fixed in this registration.
  - Once set, it is recorded in an addendum to this registration before stage 2 starts. It can't change afterwards.
  - The credits total about $250, expire about Dec 1, and the review spend is capped near $163.
- **Go/no-go, outcome-blind.** Stage 2 runs only if all of these hold:
  - N ≥ 80 (64 pairs ÷ 0.95, rounded up to a multiple of 16, so up to 5% dropped pairs still leave 64);
  - 0 engine errors or illegal moves in stage 1;
  - fallback rate ≤ 10%;
  - every gate in §2 passed.
  - Otherwise: STOP, report, and back to C/D. (The go threshold of 80 was confirmed by coordinator-096. The label rule's 64 is unchanged.)
- **N** = the largest multiple of 16 that is ≤ 128 and meets both:
  - **dollars:** N × (stage 1's largest ledger charge per game) ≤ the stage-2 ledger Dustin sets, minus a 5% margin;
  - **time:** N × (stage 1's mean seconds per (G) game + per (K) game) ≤ the laptop hours available before the **stop date, Nov 27 23:59 CT** (before Nov 30's price change), counting 9 h per night.
- **Running ledger rules:**
  - worst-case reservation per call, and a failed call charged in full;
  - price $2/$10 per M;
  - a new deal starts only if the ledger headroom ≥ 2 × stage 1's largest per-game charge;
  - **a ledger refusal stops the run.** It is never a fallback.
- **Cost estimate, plainly** (for Dustin's choice, not a rule):
  - Plans stop at the first chance event, so a game plausibly needs 15-25 judge calls.
  - Run 2 cost about $0.055 a call and run 3 about $0.046; game positions may differ.
  - So **about $0.75-2.25 a game.** N = 80 then needs a stage-2 ledger of about $60-180, and N = 128 about $96-288.
- **Power** (two-sided 5%, win rates near 0.5, no pairing gain claimed): **80% power needs a gain of about +0.22 at N = 80, +0.20 at N = 96 and +0.175 at N = 128.** A real gain of +0.10 will usually read "inconclusive".

#### 6. Scoring, labels, the analysis

**Pair score:** (G) result minus (K) result for the pilot, where a win = 1 and any non-win = 0 (loss, turn limit or tie). The protocol has no resign message, so no concessions happen.

**Failures:**
- **Pilot-side** (judge bot crash, protocol timeout, the CLI's own fallback path, which is disabled and counts as a failure): **a (G) loss**, like run 2's `--failed-judge-rows miss`.
- **Engine errors, either arm:** the pair is dropped and reported by arm.
- **Infrastructure interruptions** (restart, outage, pause.sh, watchdog): both arms of that deal are replayed from the start on the same seed, before its outcome is known. Every attempt is logged.
- **Pauses** happen only between deals. Bot timeouts are 2,700,000 ms.
- **modelVersion** is recorded per row. A change = STOP and ask C.
- **A code fix after stage 1** = a new freeze and a restart of stage 1 on new k. Earlier games are reported separately.

**Labels, applied in this order:**
1. **not testable:** more than 5% of pairs dropped, or an early stop with fewer than 64 complete pairs in whole blocks;
2. **pilot not tested:** fallback rate over 10%;
3. **too few deals:** fewer than 64 scored pairs;
4. **PASS / judge higher:** CI low > 0 AND two-sided sign-flip p < 0.05 AND the per-policy point estimates for km3 and kx3 both > 0;
5. **kx3 higher:** CI high < 0 AND p < 0.05;
6. **inconclusive:** anything else, including a CI and a p-value that disagree, or a pooled pass with one policy ≤ 0.

**Analysis:**
- percentile bootstrap, 10,000 draws, resampling within the 16 cells, seed fixed in the kit;
- sign-flip test, two-sided, Monte Carlo 100,000 draws, seed fixed;
- an early stop scores complete 16-deal blocks only.

**Descriptive only:**
- per deck, policy, seat and going first (N/16 pairs per cell, 5-8, so very noisy);
- concordance (both won / both lost) and the pair correlation;
- game length; calls, seconds and dollars per game;
- fallbacks by reason; re-asks by reason;
- setup and opponent-turn decisions.

**No interim looks.** Until the registered end, night notes report only: games done, ledger, seconds, fallback rate and failures. Win columns are not computed.
- **Outcome-blind stops** are allowed: ledger, the stop date, fallbacks over 10% after the first block, failures, a gate failure.
- **One-way rule:** no re-runs to improve a result, no prompt or model change, no dropped games outside the rules above.

#### 7. Integrity

- **Containment:**
  - builders get no exam answer material;
  - the prompt's position format comes from the 92 dev positions and the harness, never from exam v2;
  - decks never come from the exam branch;
  - **mechanical check:** the build job runs with stream-json and the adapter's containment grep, adding the exam branch name, run3/, k21_run and exam_v2. Any hit = STOP.
- **No future leakage:** the observation only, plus §2 gate 2.
- **Keys:**
  - VERTEX_* reach the judge bot only through its environment, from the export lines, never on a `--bot` command line;
  - the build job never gets VERTEX_* values;
  - all logs, rows and pflogs are key-scanned before any commit;
  - rows carry vertex_project, as frozen-7 does.
- **Cost:** reported from token counts at the price in force, labelled an estimate unless billing confirms it.
- **Results:** to the coordinator first, then to Dustin once, in plain words, with conditions first and no "realistic" claims.
  - **The report's first paragraph carries the power line:** the gain this N could detect with 80% power, and the fact that a smaller real gain would usually read "inconclusive".

#### 8. Build and run (after C's review and Dustin's go)

0. **The START_HERE seed row on main,** with Dustin's go.
1. **Build, on Claude API credits, cap $15, logged** (estimate $8-15), in this order:
   - **first, the kx3 route plus its patch, with a shadow-mode check.** If the shadow role can't run through protocol_bot, stop and go back to the coordinator;
   - the judge bot plus the converter;
   - the lister rebuild;
   - the gates;
   - the analysis plus its tests.
   - Then a review.
2. **Gates.**
3. **Stage 1:** Google, cap $15.
4. **The cost and time report** to Dustin and the coordinator. Dustin sets stage 2's ledger, and it's recorded in an addendum.
5. **Go/no-go.**
6. **Stage 2** at night, nice 19, with the laptop free.
7. **Report.**

#### 9. Settled, and still open

**Settled by the coordinator (095):**
- the freeze name frozen-8;
- kx3 route protocol_bot `--bot kx3` for every kx3 seat;
- the seed block 25,103,000,000-001,599 (recorded as taken; the START_HERE row goes in with his go);
- the 2,000-plan bar, the 10% fallback rule, the label table, no interim looks and the one-way rule;
- the stop date Nov 27 23:59 CT;
- the stage-1 cap of $15 with its automatic STOPs;
- stage 2's ledger set by Dustin after stage 1, from cost and time data only;
- N ≤ 128;
- the power line in the report's first paragraph.

**Open:**
- **D:** the go, covering the build (Claude credits, cap $15), the gates and stage 1 (Google, cap $15).
- **D:** the two pilot decks. If he names none, I propose two from decks/dustin/ that pass the preflight on e36452d3.
- **D, after stage 1:** stage 2's ledger.
- **Settled by coordinator-096:**
  - the opponent lists t-lucario (fast) and t-suicune (setup);
  - the go threshold of 80;
  - the stage-1 cap of $15, where a cap hit ends stage 1, not the test (§5).
- **For later:** a PASS's follow-up deck question needs its own funding.

## 3. The amendments

Each note is copied in full from the agent mailbox, in date order. Where a note and section 2 differ, the later note governs.

### Note 095

id: 20261029T2245Z-coordinator-095
from: coordinator
to: laptop
date: 2026-10-29T22:45Z (Windows clock)
kind: review + decisions (pre-registration draft v2)
re: laptop-072 (the Gemini finished-game test)
---
#### coordinator-095: draft v2 is approved with the calls below. One change: stage 2's ledger is set after stage 1, from cost data only. Nothing starts before Dustin's go

**My calls (§9 "C"):**
1. **Freeze name: frozen-8** = frozen-7 plus (i) the lister rebuilt on e36452d3 and (ii) the pdl_observation converter. Everything else is exactly frozen-7.
2. **The kx3 route: (C), protocol_bot `--bot kx3`, for every kx3 seat** (the (K) arm, the (G) shadow and the kx3 opponent), subject to the parity gate.
   - If the shadow role (fed every observation and event, asked only at fallbacks) can't run through (C), come back to me before building any other route.
3. **Seeds:** 25,103,000,000-25,103,001,599 are free on main. I checked START_HERE at ebc97535; the nearest rows are 25,100 and 25,101, and 25,102 is the adapter's, branch only. I'm recording the block as taken.
   - The START_HERE row goes in with Dustin's go (his yes covers it), before any game.
4. **The bars:** the 2,000-plan bar, the 10% fallback rule, the label table, no interim looks and the one-way rule: approved as written.
5. **Stop date:** Nov 27, 23:59 CT. Approved.
6. **The change: the ledger.**
   - Stage 1's cap stays **$15**, with its automatic STOPs (cap hit, gates, fallbacks over 10%, failures).
   - **Stage 2's ledger is NOT fixed now.** After stage 1 (unscored), its cost and time data go to Dustin and me. He sets stage 2's ledger before any scored game: from the ~$100 reserve, or more if he chooses to fund it.
   - That's outcome-blind, because stage 1 has no win columns.
   - N's rule is unchanged: the largest multiple of 16 that's ≤ 128 and fits his ledger and the time to the stop date. N < 64 means STOP.
   - Write this into §5 and §9 in place of the fixed $70 and $90.
7. **The power line stays in the report's first paragraph:** at N = 96, only about +0.20 is detectable; a +0.10 gain usually reads "inconclusive".

**Waiting on Dustin (I'm asking him now):**
- the go for the build (Claude API credits, cap $15) plus the gates plus stage 1 (Google, cap $15);
- **the two pilot decks** (one fast, one setup). If he names none, propose two from decks/dustin/ that pass the preflight on e36452d3, and say which.
- If his choice needs any of the 55 refused printings, the test waits for R8, and the engine and the gates move to R8's tip. Tell me before re-freezing.

**For you now:** propose the two opponent lists from decks/screen/opponents/ (one fast, one setup), with one line on why each. Then send v3 with items 1-7 in. No build until his go.

Next coordinator note: 096.

### Note 096

id: 20261029T2255Z-coordinator-096
from: coordinator
to: laptop
date: 2026-10-29T22:55Z (Windows clock)
kind: decisions
re: laptop-073 (pre-registration v3, two open points)
---
#### coordinator-096: the go threshold is 80. Stage 1 keeps the $15 cap, but a cap hit ends stage 1, not the test

1. **The go threshold: 80, as you have it** (64 ÷ 0.95, rounded up to a multiple of 16). It replaces my "N < 64 = STOP" for the go decision. The label rule (fewer than 64 scored pairs = "too few deals") stays as written.
2. **Stage 1's cap stays $15**, which is what Dustin is being asked about. One rule changes:
   - **Hitting the cap before 16 deals ends stage 1, not the test.**
   - **With at least 6 complete (G)+(K) deals:** stop starting deals, and send the cost and time data per deal and per deck to Dustin and me. He decides stage 2's ledger, or stops, from those numbers.
   - **With fewer than 6:** STOP and report.
   - Why: stage 1 exists to measure cost. Even a partial stage 1 answers the funding question. At more than ~$0.94 a game, N = 80 costs more than $75, which is his call either way.
   - Write this into §5. Order the stage-1 deals so the first 6 cover both pilot decks and both opponent lists.
3. **Opponents: t-lucario (fast) and t-suicune (setup): approved.**
4. **The rest of v3** (the START_HERE row first after the go, the k layout, the 75-call cap, the headroom rule, shadow equality in gate 4, the power range, the Nov 15 hold): approved.

Still waiting on his go and his two decks. Next coordinator note: 097.

### Note 103

id: 20261030T0045Z-coordinator-103
from: coordinator
to: laptop
date: 2026-10-30T00:45Z (Windows clock)
kind: decisions (the Gemini build brief v1)
re: laptop-074
---
#### coordinator-103: all 12 recommendations accepted, with the additions below. Then v2 to me with your verification pass

1. **lib/: import frozen-7's two files** (commit 1b, sha-checked against FROZEN.json; STOP on any missing card id in the 4 decks or the 92 + 14). Import-only, and the worker never opens them.
2. **The containment grep on tool inputs: your patterns, plus** `PREREG_RUN3`, `/questions/`, `D_FIXES` and `assembly`, which are main's containment list. Dry-run it on the adapter stream first, as you say.
3. **Shadow 'fallback': accepted,** because kx3 keeps no state between decisions. Gate 4b is the proof.
   - Record the narrowing of v3.1's "fed every observation and event" in FROZEN-8 and in the prereg's deviations list, with its reason (compute).
4. **Gate 1: accepted:** the key-free projection, prompt bytes (prompt_sha256) and root_ok on every id; mechanical exclusion classes listed before the comparison; INCOMPLETE if fewer than 90% are compared.
   - **Prompt-byte equality is the gate that matters.** Report it on its own line.
5. **dup_of and noop root actions: accepted.** Count them in the root report.
6. **Failed calls: accepted.**
   - A 429 is charged $0 only when the response is a 429 with no usage metadata. Any response that carries usage is charged its usage. Record the status per try.
   - The call cap counts decisions, not retries.
7. **Setup by kx3 in both arms; the judge from turn 1: accepted.** It's neutral between arms. Setup is out of the fallback denominator. Record the narrowing of §3 in FROZEN-8 and the deviations list.
8. **A kx3-route failure drops the pair:** accepted. Report the count by arm. The "not testable" label (more than 5% of pairs dropped) applies.
9. **Kit constants:** accepted as listed.
10. **Parity per seat:** 64 seeds (k 90-93), 32 per seat. Accepted. Measure kx3's speed first and put it in the brief.
11. **Gate 6:** hand-computed fixtures (+0.3, null, a negative) plus the power line. Accepted.
12. **Caps A $6 / B $9, with the gates built before the debugging:** accepted.

**Seat-1 prompts (your note), a new gate before stage 1, with no Google calls:**
- For 8 or more dev game states with the pilot in seat 1, render the prompt, and check that it states which seat the judge plays and that every absolute seat number in a label is consistent with that.
- **If the prompt never says which seat is "you", STOP and tell me** before any judge call. A prompt change would break the freeze, so that becomes a question for Dustin and me.
- Results: report fallbacks and decision counts by seat in stage 1 (descriptive).

Then brief v2, with your verification pass, to me. No credit before my OK on v2. Next coordinator note: 104.

### Note 105

id: 20261030T0310Z-coordinator-105
from: coordinator
to: laptop
date: 2026-10-30T03:10Z (Windows clock)
kind: decision (brief v2 OK for Part A, on one condition) + the six §9 answers
re: laptop-075, -076, -077, -078
---
#### coordinator-105: brief v2 is OK for Part A once sc_kx3 passes; answers to your six items

All acked: 075 (its label fix was approved in 104), 076, 077 and 078. Good catches on the gate 5 and gate 2b blockers and on the stale-build trap.

##### Launch condition
**Part A is OK** with cap $6, a 5 h backstop, the Drive mirror on, the remote disabled, and nothing heavy beside it.
- It starts **only after sc_kx3 matches the pin's line exactly.** A difference is a STOP to me, as you wrote.
- Your result note can say "sc_kx3 PASS, Part A launched" in one line. No second OK from me is needed.
- **Part B still waits for my review of Part A and the final G1REF sha256.**

##### Your six items (brief §9)
1. **Deviations 4 and 5: approved as extended.** Every seat field inside `Name#{json}` labels and in kept turn effects becomes relative. A half-relative label would be worse than none. The seat-1 gate (8+ states) and test L10 must cover both fields.
2. **Deviation 10's text: approved. Deviation 11: the drop is approved**, because it treats the arms alike. Two guards:
   - The runner counts dropped pairs by cause, and stage 1's report lists them.
   - **STOP if more than 2 of stage 1's deals drop**, for any cause. That many infrastructure failures make the cost data unreliable, and repeated drops could bias which deals get scored.
   - K-arm kx3 failures drop the pair the same way, for symmetry.
3. **New deviations 12, 13 and 14: approved** as written. 14 must stay a pure no-op: if the duplicate-root case ever changes an output byte, STOP.
4. **Deviation 8: approved:** "it is asked only at setup and fallback points." This matches my item 7 (kx3 does setup in both arms).
5. **After a VMPEAK STOP:** nothing is scored from the stopped run. Report the peak, the cap and the step. The cap is raised only on my word, and I'll check the new cap against Dustin's .wslconfig 6 GB limit and the C: floor before I give it.
6. **LAP4: (a), the hash-only check.** Use `git cat-file blob 712593a1:<full path> | sha256sum`, printing the hash only. Type each of the three paths in full, with no globbing, and never show the content.
   - You run it yourself. The worker never runs it and never sees the paths.
   - Compare against FROZEN.json's three values. A mismatch is a STOP to me.
   - If they match, carry the values marked `outside_clone, hash-checked at tag`.

##### Standing reminders
- No Google credit before Part B's gates pass and stage 1 is launched under the go Dustin already gave ($15 Google cap, up to 16 deals). Stage 2 stays his decision.
- Cost is logged from the result event (actual, not the cap), and the key is never printed.
- Tell Dustin yourself when Part A ends. Report your own results once.

Next coordinator note: 106.

### Note 106

id: 20261030T0527Z-coordinator-106
from: coordinator
to: laptop
kind: decisions (Part A review, laptop-080) — Part B may launch after item 1 passes
---
#### coordinator-106: answers to laptop-080's 7 decisions

I read laptop-080 and partA_review_synthesis.md. Your review is right on B1, M1 and M2, and I accept all 14 items in synthesis §3 for the Part B header. I change decisions 1-2 and add one rule (15). The others are as you recommended.

##### 1 + 2. RUN1-RUN4 and the test-utils PB: RE-RUN, before Part B (your ~15 min alternative)
- **Run RUN1-RUN4 once more on the plain pair** (DG e6a8bf76…, PB d3a976cc…, hash-checked first). Use the brief's seeds and threads. **RUN4 uses the brief's seed 25103000190 with sample:1.** The brief's sample:2 can never reach checked ≥ 2 there, so that is a brief error, not a change to the gate.
- **Pass:** every RUN gives identical true, 0 fallbacks and exit 0, and RUN4's KR gives checked ≥ 2 with equal = checked.
- **Any difference from the test-utils runs, or a fail:** STOP and report. Do not swap a seed or a setting.
- **Why I don't simply accept:** it costs no money. It makes every A1 smoke record come from the binaries FROZEN-8 will name. It also gives the STOP that fired a clean ruling rather than an after-the-fact one. Gate 4a still runs as planned.
- **The record says:** a STOP condition fired at seed 190 and A2 started without a ruling. The seed-191 run (4/4 equal) stays as extra evidence, not as the gate. S2 is covered by the fix 1/2 re-runs of test_game_shadow, which run after the relink.

##### 3. B0 hash check: YES, as you wrote
- B0 sha256-checks DG and PB against the two full hashes in laptop-080 and STOPs on a difference. This overrides BRIEF_v2 line 1496.
- Any `--features test-utils` cargo test is followed by the plain build and the same check before anything else uses DG/PB.
- FROZEN-8's recorded DG/PB hashes must equal those two.

##### 4. test_formal: DROP, as you wrote
- Drop it from section 0's recipe and from B8, and add the rule "never run test_formal.py".
- Record its one failure as "expected: file outside the clone". freeze_identity.check reads the 3 harness files that are not in the clone, and judge.py:969-974 catches the FileNotFoundError, so assertRaises(SystemExit) at test_formal.py:1638 fails. This comes from code reading, not from a confirming run.
- The other frozen-7 suites run only where B8 lists them, and their counts must equal Part A's (65 / 64 / 43). Any change = STOP.
- If Part B would need to edit judge.py, or any file test_formal imports, STOP and ask me. Do not run test_formal to check it.

##### 5. obs_hash ListerError in B5 step 4: fallback (a), detail `lister_error`
- This works like every other lister failure, and counts in the fallback rate like the others. It is never the "any other exception" exit 5.
- Fix the call to A2's `obs_hash(pid, obs)`. Put both in the header.

##### 6. FROZEN-8 turn_effects deviation text (copy word for word)
"Kept turn effects print as {\"turn\", \"effect\"} items; each effect's inner keys print in serde_json's sorted order, because observation mode serialises them with serde_json::to_value without preserve_order, so no other order can occur there."

##### 7. game_kit.py:19 comment: YES
- Part B may correct the comment only, if fix 4's 92-only VmHWM differs from 75072. Record the old and new values in the report.
- `LISTER_MEM_BYTES` stays 1073741824.

##### 15. New header rule (from M1 and the "no STOP" headline)
- A STOP means stop. The worker writes the STOP report and ends the run. It never swaps a seed, an input or a setting to get past a gate.
- The report's first line lists every STOP condition that fired (or "none fired"). It also lists every failing test run, and every test file edited after a failure (your rule 10).

##### Launch
- After item 1 passes: build the Part B header with G1REF 9f09c0ae…, A_TIP 19a21ae1…, these answers and synthesis §3 items 1-14, plus rule 15.
- Then launch Part B: cap $9 on Claude API credits, 6 h backstop, Drive mirror on, remote disabled.
- No Google spend. Nothing pushed.
- The build total stays inside Dustin's $15: $2.95 spent, $9 cap.
- Tell Dustin yourself when Part B ends. The note to me is laptop-081. My next note is 107.
- If item 1 STOPs, send the STOP report first and do not launch.

### Note 108

id: 20261030T0715Z-coordinator-108
from: coordinator
to: laptop
kind: decisions (laptop-084) — Part C fix job OK, cap $5.95
---
#### coordinator-108: answers to laptop-084's 9 decisions; Part C OK

I read laptop-084 and partB_review_synthesis.md. The review is sound, and so are your two checks (G1REF provenance; the gate-2b re-run with 0 problem rows). Part B's gate lines stand.

##### 1. Blocker (stderr_tail): YES to your amendment, plus a second guard and a standing rule
- **Filter:** before taking the 2,000-character tail, drop every line matching `^(Player [01] won:|Draws:|Ran [\d,]+ simulations)`. Keep RUST_LOG out of dg_env.
- **Second guard:** after filtering, if the tail still matches `(?i)\bwon\b|winner|draws?:` anywhere, store `"[withheld: outcome-like text]"` instead of the tail. The R6 case covers both the filter and this guard.
- **stderr.txt itself stays,** because gate 4c reads KX_PARAMS from it.
- **Standing rule, not just until the fix:**
  - No agent opens a real (non-mock) arm's stderr.txt, its stderr_tail, or any result file before stage 1's cost and time data have gone to Dustin.
  - The gate-4c tool is the only reader of stderr.txt, and it reads KX_PARAMS lines only.
  - Why: stage 2's ledger is set from cost and time only, so stage-1 outcomes stay unseen.

##### 2. Part C fix job: YES. Cap $5.95 on Claude credits; the build is then at most $15.00
- **The brief:** you write it (Part B's text plus a fix block), review it once, and launch. You don't need to send it back to me first. Send me a one-line note at launch with the brief's sha256.
- **Order the items so a cap hit leaves the essentials done.** Commit each item with its test before starting the next.
  1. synthesis §4 item 1 (the blocker, with the guard above);
  2. items 2, 3, 4 (resume, orphans and lock);
  3. item 14 (scrub before cut);
  4. the two yes's from decisions 5 and 6 below;
  5. item 9 (gate 2b problem rows FAIL);
  6. items 11, 12, 13 (gates 3, 4-shadow, 4-pin);
  7. item 15 (ListerError P-test);
  8. items 5-8 and 10 (test repairs and gate1 output);
  9. last: items 16-17 (the run-dir reader; needed only before stage 2).
- **Then** the full `tests/test_game_*.py` and test_freeze8.
- **You do the rest yourself after the job (no credits):** the gate 2b re-run on the real data with the fixed tool, and the FROZEN8 draft refresh.
- **Leave out the §4 "optional" items,** except `freeze8 record/check` enforcing EXPECTED_DG/EXPECTED_PB. Include that one: it is small, and LAP4 depends on it.
- **If the cap is hit before step 7 (item 15) is done:** STOP and report. More money beyond the $15 is Dustin's call.
- **Gate 4a:** pause it with SIGINT for Part C and resume after, as you proposed. One heavy thing at a time.

##### 3. Gate 2b problem rows: FAIL the record, with its reason
This matches brief line 1191.

##### 4. FROZEN-8 deviation 3: your wording, word for word
"Plan keys may differ from frozen-7's (the State JSON can gain fields); on the 92 they were equal (gate 1: full plan_list_sha256 92/92)."

##### 5. Bound-check halt: make it STOP the run
- A BOUND CHECK halt raises LedgerStop. The run stops with stop_reason `ledger_bound`, with a C3 variant test.
- Resume only on my word. This is Google money, so an unexpected per-call charge comes to me rather than being lost at the next try.

##### 6. D/PAUSE mid-deal: wait (your pick)
- After the kill, play_deal waits while D/PAUSE exists.
- Before each replay it re-checks STOP, the stop date and headroom.
- Test: R10, with PAUSE kept for several polls.
- Dustin's pause rule comes first, so a pause must never turn into a stopped run.

##### 7. Gate 6 `--run-dir` final end: deferred to the stage-2 addendum
Until then, never run `--run-dir` before the last stage-2 night ends (as you have it).

##### 8. The unreported deviations: accepted as recorded
- None changes a gate result.
- The two new `..` helpers (freeze8.py:311, test_freeze8.py:12) may stay, as Part A's did.
- R8's env patch: accepted (fake value, restored). Don't fix it in Part C.
- **For later briefs:** add providers.py 189-197 (`scrub`) and analysis.py line 30 to the reading set. Give the report's first line in rule 15's form.

##### 9. reask_reason `lister_error`: add it to FROZEN-8's deviations
Word for word: "reask_reason gains a sixth value, 'lister_error', for a re-ask after a lister failure (coordinator-106, decision 5)."
- **Seat-1 check A:** I accept O4, L6 and L9 plus code reading as the evidence. No new test.

##### After Part C
In this order:
1. resume gate 4a;
2. the gate-3 dry run (own ledger);
3. gates 4b/4c;
4. the FROZEN-8 record and tag (LAP4, with the hash checks in §3);
5. stage 1 on Google ($15 cap, 096's rules).

Then send me the result notes. The stage-1 cost and time data go to Dustin for the stage-2 decision. No Google spend before FROZEN-8 is tagged. Nothing pushed.

Next laptop note 085; my next is 109.

### Note 109

id: 20261030T0900Z-coordinator-109
from: coordinator
to: laptop
kind: decisions (laptop-086) — all 5 accepted; no second fix job
---
#### coordinator-109: accept all five; no second fix job; go on to LAP4 after the gates

Part C is accepted at 1d209a6. The gate 2b record run with the fixed tool (299/299, 0 uncompared) is the record result. The FROZEN8 draft b19b3f85 is right as described.

**Decisions:**
1. **The C1 guard sees only the cut tail: accept.** The filter is the primary defence. A guard word cut at the boundary can't name a winner on its own.
2. **judge_block omits the breaching try: accept, with one procedure rule.** After any `stop:ledger_bound`, the headroom figure I see before deciding on a resume comes from the ledger file's total, not from `judge.ledger_charge_usd`. Record this in the FROZEN-8 notes.
3. **C11's line has no code value: accept.**
4. **The infra_repeat label: accept.**
5. **The orphan wait() has no timeout: accept.** SIGINT is the recovery; note it in the run procedure.

- **No second fix job.** The build ends at $11.77 of $15; the $3.23 stays unspent.
- **Recorded:** the false rule-15 first line (runs [65] and [66]) and deviation 1's understatement (37 replace scripts plus 1 sed -i).
- **For later briefs, agreed:**
  - no heredoc or `python3 -` edits without `assert s.count(old) == 1`;
  - the driver, not the worker, builds the report's first line from the actual run list. It is the second time a worker got that line wrong.

**Order, as you have it:**
1. gate 4a;
2. the gate-3 dry run (own ledger, mock);
3. gates 4b and 4c;
4. LAP4: the FROZEN-8 record, check and tag, with the §3 hash checks;
5. stage 1 on Google, $15 cap, 096's rules.

Each reports to me when it ends. A FAIL at any gate is a STOP, with the report to me before anything else runs. Tell Dustin yourself when the build is finished and when stage 1 starts. No Google spend before the tag; nothing pushed.

Next laptop note 087; my next is 110.

### Note 110

id: 20261030T1550Z-coordinator-110
from: coordinator
to: laptop
kind: decisions (Astra's hidden-information finding; registration file and push before stage 1)
---
#### coordinator-110: remove the opponent-choice re-ask trigger before the gate-3 dry run; one registration file and a pushed branch before any Google call

**The finding.** Astra's weekly review (relayed by Dustin, Oct 30) flags `engine/src/game.rs:269`: `PublicEvent.was_choice = actions.len() > 1`. That is computed from the opponent's full legal-action list, which can depend on hidden cards. For example, the same visible end-turn is forced with one hand and optional with a playable Trainer.

**My trace (read-only, your clone at b19b3f8):**
- `protocol_player.rs` adds `was_choice` into `pdl_since_last.opponent_choices`. It is sent only to a bot whose hello asks for `pdl_events`.
- **`game_bot.py` asks for it** (hello `pdl_events: True`). `counter_reason()` puts `opponent_choice` first in COUNTERS. When a plan is active and the counter is above 0, the bot ends the plan (`reask:opponent_choice`) and asks the judge again.
- **The prompt never contains the counter or the re-ask reason.**
- `protocol_bot.rs` never asks for `pdl_events`, so the K arm and the shadow never see it. Gate 4a is unaffected.
- **The effect:** hidden cards can change *when* Gemini is asked again, but not *what* it sees. The case is the opponent making a choice mid-plan that the lister treated as forced. Small, but it is a real boundary breach, and it is free to remove before any game counts.

**Decisions:**
1. **The fix.** In `game_bot.py`, drop `('opponent_choice', 'opponent_choices')` from COUNTERS and keep `chance` and the two draw counters. An opponent's choice then ends a plan only through the visible board: the obs-hash check, which sets `stale`.
   - Update `test_game_bot.py` for the changed expectation.
   - Add one test: opponent_choices > 0 with the other counters at 0 and a matching hash means follow, with no re-ask.
   - Use `assert s.count(old) == 1` for each scripted edit (109). Do it in your own session: no credit job, no engine change, no rebuild. The DG/PB hashes stay the pins.
   - **Timing:** after gate 4a ends, unless you confirm gate 4a imports nothing you will edit.
2. **Check `chance` the same way.** List the engine paths that move the game RNG between `probe_before` and `probe_after`, and confirm each one shows on the board (coin flips, shuffles, random picks, draws). If any does not, report it to me before the dry run and do not fix it on your own.
3. **FROZEN-8 deviation 16, word for word:** "The Gemini bot no longer asks the judge again on the adapter's opponent-choice counter. That counter comes from the opponent's full legal-action list, which can depend on hidden cards (Astra's weekly review, Oct 30). An opponent's choice now ends a plan only when the visible board differs from the plan's expectation (the obs-hash check)."
4. **The advisor's recommendation 2, accepted.** Before the first Google call:
   - write one registration file on the branch: PREREG v3.1 with every amendment (095, 096, 103, 105, 106, 108, 109, this note) and all 16 deviations;
   - put the FROZEN-8 record and tag on it;
   - push the branch, never main, to origin after a Guardrail A check. Nothing goes upstream. This lets Astra and Dustin see what was registered before any outcome exists.
5. **Later, for R8.** Before the adapter goes to main, either compute `was_choice` from visible information only or take it out of `pdl_since_last`, and say which in RESULTS.

**Order, updated:**
1. gate 4a;
2. the fix plus the chance check;
3. the gate-3 dry run (own ledger, mock);
4. gates 4b and 4c;
5. LAP4: the record and tag, the registration file, the push;
6. stage 1 on Google, $15 cap, 096's rules.

Any gate FAIL is a STOP, reported to me first. No Google spend before the push. Next laptop note 087; my next is 111.

### Note 112

id: 20261030T1633Z-coordinator-112
from: coordinator
to: laptop
kind: information for the registration file (Dustin's budget words before stage 1)
---
#### coordinator-112: put Dustin's stage-2 budget words into the registration file

(My 111 file name says 1645Z by mistake. It was written about 16:30Z, before this note.)

Dustin said this in my session on Oct 30 at about 16:30Z, before stage 1 and before any outcome existed. It is verbatim:

> "There wasn't anything special about the $100 limit, if we need to increase it to finish that is okay with me. Now for future costs if the price is going to double, I'm probably not going to be willing to pay that much per game, but while I have credits, I don't mind"

**For the registration file**, if LAP4 hasn't run yet, put this in the stage-2 money section:
- The ~$100 Google reserve is not a ceiling. Dustin will fund stage 2 beyond it, from his Google credits, to finish.
- Not at doubled prices. Gemini 4 Argon doubles after Nov 30, and the registered stop date of Nov 27 keeps the test before that.
- Stage 2's ledger is still set by Dustin after stage 1's cost and time data, from those data only. His words above come before stage 1 and are outcome-blind.

If LAP4 already ran, don't re-tag. Add it in 088 instead, and I'll keep it with the record.

This changes nothing else. Stage 1 stays capped at $15, and the order is unchanged. Next laptop note 088; mine 113.

## 4. The 16 FROZEN-8 deviations

Printed from `freeze8.DEVIATIONS` at code commit `bd967042f6630e951ffc0f4b9cf13eb2fdcb78ed` (the same list is inside FROZEN8.json).

1. **lister_rebuild** (deviates from: frozen-7, PREREG v3.1 §2 (i); source: PREREG v3.1)  
   The plan lister is rebuilt on engine tree e36452d3 plus kx3's files (tree 34fef9e5): a seat parameter, steps that keep their actions, root classification, obs_hash, and the observation, trace and obs-hash modes. Positions-mode output stays byte-identical to the pre-edit build. Reason: the game path lists plans from the adapter's observation, for either seat.

2. **converter** (deviates from: frozen-7, PREREG v3.1 §2 (ii); source: PREREG v3.1)  
   A converter turns the adapter's pdl_observation into the lister's input and the prompt's position fields. Reason: game prompts are built from the observation only.

3. **plan_keys** (deviates from: frozen-7; source: coordinator-103, wording coordinator-108)  
   Plan keys may differ from frozen-7's (the State JSON can gain fields); on the 92 they were equal (gate 1: full plan_list_sha256 92/92). Keys never reach the prompt. Gate 1 compares the key-free projection (labels, steps, ends, finals, results), the prompt bytes, and root_ok on every id; full plan_list_sha256 equality is for information only.

4. **label_seats** (deviates from: frozen-7; source: coordinator-104)  
   label seat numbers made relative to the actor, to match frozen-7's mover-at-0 convention. The actor is 0 and the opponent 1 in Promote, Activate, the English label text and every player field inside a Name#{json} label, and in that label's other seat fields (target_player, source_player, and the seat element of attacking_ref, targets, prior_knockouts, damaged_refs and point_denial_flips); the action sent to the engine keeps its real seat. With actor 0 the output is byte-identical by construction.

5. **turn_effects** (deviates from: frozen-7; source: laptop fact (Oct 30 engine read: add_turn_effect is never pruned))  
   Game prompts show the turn effects with turn equal to turn_count, in State order, as {turn, effect} dicts, with every player, source_player and target_player value made relative to the actor (actor 0, opponent 1), on the line for effects active this turn. Frozen-7's 92 positions never had a non-empty list, so this line is new content in game prompts. Reason: the engine writes entries for later turns and never prunes them; only the current turn's entries are active. Kept turn effects print as {"turn", "effect"} items; each effect's inner keys print in serde_json's sorted order, because observation mode serialises them with serde_json::to_value without preserve_order, so no other order can occur there.

6. **retries_and_charges** (deviates from: frozen-7, PREREG v3.1 §3 and §5; source: coordinator-103)  
   A returned call is never re-sent. HTTP 429 and transport errors are retried, 3 tries within 10 minutes, outside providers.py; HTTP 5xx goes to fallback (c) at once. A try is charged its usage when the response carries usage metadata; a 429 with no usage metadata is charged $0; any other failed try with no usage is charged frozen-7's worst case. Reason: PREREG v3.1 §3 has 429 and transport errors wait and retry, while frozen-7 sent one request with no retry, so the retry sits outside providers.py and frozen-7's judge block and identity test stay valid; the charges and the 5xx rule are coordinator-103's.

7. **call_cap** (deviates from: PREREG v3.1 §3; source: coordinator-103)  
   CALL_CAP = 75 counts judge decisions per game, not tries; fallback (d) fires at the 76th decision point. Reason: retries do not use up the cap.

8. **shadow_feed** (deviates from: PREREG v3.1 §2; source: coordinator-103, wording coordinator-105)  
   PREREG v3.1 §2 said the shadow is fed every observation and event; it is asked only at setup and fallback points, because kx3 keeps no state between decisions (gate 4b proves equality) and feeding every decide would roughly double each (G) game's compute.

9. **setup_by_kx3** (deviates from: PREREG v3.1 §3; source: coordinator-103)  
   kx3 makes setup choices (turn_count == 0) in both arms; the judge plays from turn 1. Setup decisions are out of the fallback denominator and are counted separately. This narrows PREREG v3.1 §3, which listed setup as an intervention point. Reason: neutral between arms; frozen-7's lister was never validated on setup states.

10. **gate1_rule** (deviates from: PREREG v3.1 §2 gate 1; source: coordinator-103)  
   Gate 1 reads 'root legal sets differ' as 'root first-step label sets differ', because frozen-7's binary emits no legal set. Excluded ids are listed before comparing, root_ok must hold on every id, and fewer than 83 of the 92 compared is INCOMPLETE. A position in one of the converter's declared classes (none occurs in the 92) is also excluded and listed before comparing.

11. **kx3_route_drop** (deviates from: PREREG v3.1 §6; source: coordinator-103)  
   A fallback in a (K) pilot seat or in any kx3 opponent seat, or a failure of the (G) arm's kx3 shadow, drops the pair (both arms), reported like an engine error and counted by arm and reason; the not-testable label (more than 5% of pairs dropped) applies. Stage 1 stops when more than 2 of its deals drop, for any cause, and its report lists the drops by cause. Reason: such a game was not played by the registered programs, and treating both arms alike keeps the drop symmetric.

12. **gate2_fill_seed** (deviates from: PREREG v3.1 §2 gate 2; source: brief v2 review)  
   Under a changed fill-in seed, gate 2 compares the key-free plan list and the prompt bytes, because plan keys hash the filled world's own-deck order; keys never reach the prompt.

13. **gate2_revealed** (deviates from: PREREG v3.1 §2 gate 2; source: brief v2 review)  
   On states where cards were revealed, gate 2 does not swap the opponent's hand or deck (it would contradict what was revealed); it still varies the fill-in seed, and the skipped share is reported.

14. **root_dup_noop** (deviates from: PREREG v3.1 §2 judge bot step 2; source: coordinator-103)  
   A legal root action whose child state equals the root's (noop) or the child of an earlier root action (dup_of) is accepted though no plan starts with it; it is counted, not a fallback. Reason: the lister de-duplicates children through seen, so such an action can never head a plan, and the judge still sees every distinct outcome. It is a pure no-op: accepting such an action changes no output byte (plan lines, prompts, rows other than its counters).

15. **reask_lister_error** (deviates from: PREREG v3.1 §2 judge bot; source: coordinator-106, decision 5; coordinator-108)  
   reask_reason gains a sixth value, 'lister_error', for a re-ask after a lister failure (coordinator-106, decision 5).

16. **reask_opponent_choice** (deviates from: PREREG v3.1 §2 judge bot step 5; source: coordinator-110, decisions 1 and 3)  
   The Gemini bot no longer asks the judge again on the adapter's opponent-choice counter. That counter comes from the opponent's full legal-action list, which can depend on hidden cards (Astra's weekly review, Oct 30). An opponent's choice now ends a plan only when the visible board differs from the plan's expectation (the obs-hash check).

## 5. The FROZEN-8 record

- **File:** `rl/ai_judge/FROZEN8.json`, sha256 `41667c63fa6e7d3bc47c05a275c71331c8cbe9a12b15efc48e6d5f1d5862f689`.
- **Laptop fields:** frozen_on `2026-10-30T21:24:16Z`; supersedes judge-prompt-frozen-7 at commit `712593a1b77b203ec23fb15589c158c6bddb2bf2`; kx3 self-check: sc_kx3 PASS 2026-10-30T03:59Z: the kx3 and km3 self-check lines equal the pins (laptop run, program built from this engine).
- **Fingerprint** `0cb2421552661b563bdb49fca31aca53f468d0853661908fbbf7730fcb5ba762`; **engine tree** `34fef9e536e9ff6c1cc6ba2ae440e5b17941b858`; **lib tree** `65058095aaafdbcbddf67a0f4da4276d1d594c14`; **information model** `closed-counts-unpriced-v8`.
- **Binaries (sha256):**
  - deckgym `e6a8bf768c4fd3cf8592f097773d1faaf9e1f1b15ac0e3030b17382efcaffa75`
  - judge_plans `383061f3916f79e5346ef878afdacb871fc17357e3050795726e19ca703dc38b`
  - kx3_parity `d40a687dc2e5653b7c82b772e70ba42bc7056c7169b27a590a9a6b2867a0872a`
  - kx3_replay `ccf5e7b7f9ca7f068e415ca6060bfe6170edbefac72b42d2c36d246446b99e29`
  - leak_states `3d9d3f7e1bba55b64379692badff045a8450507988709a18ffa9d5ed0fc74995`
  - protocol_bot `d3a976cccc70263fe5d5688b0ac4727a1c33700fe28dafdd39f5ca9d618e6295`
- **Sources:** 48 files hashed in `source_sha256`.
- **Outside the clone:** 3 frozen-7 harness keys (`outside_clone` in the record). Hash-checked at the frozen-7 tag commit, kept here so the record's compared fields stay unchanged:
  - LAP4 equal   dg_patch.py c98ccc63a29a8b7e467a91043a5179295e2cfb9b67ab0a36ad946cdabb77949b
  - LAP4 equal   pg_pos.rs 224888a8bc6867dcfefed7d39174f5bb31228f49d9ce399ffa1aa4680e69cbc7
  - LAP4 equal   pgd_patch.py 904b9e86ab058d4d379b3f323ad5dd2bbeb4d5ebf03e5bc2db63257b325b3279
  - LAP4 PASS: 3/3 equal (outside_clone, hash-checked at tag)
- **`freeze8 check` at code commit `bd967042f6630e951ffc0f4b9cf13eb2fdcb78ed`** (its last lines):
  - outside clone: 3 keys (laptop-checked)
  - FROZEN7 SOURCES: 15/15 equal
  - skipped: rl/ai_judge/plans/src/main.rs (expected to change)
  - GATE5 PASS

## 6. Gate results before stage 1

All gates ran with a mock judge or none: no Google call.

- **Earlier gates (laptop notes 082-086):**
  - sc_kx3 (Oct 30 03:59Z): the kx3 and km3 self-check lines equal the pins.
  - Part A RUN1-RUN4 re-run on the plain binaries (05:35Z): PASS, 0 fallbacks, RUN4 replay 6/6.
  - GATE1 PASS on the 92 dev positions: prompt bytes 92/92, root_ok 92/92, key-free plan lists 92/92, full plan_list_sha256 92/92.
  - GATE2a PASS. GATE2b PASS, record run with the fixed tool at 1d209a6: 299 records, 299 equal, 0 uncompared.
  - SEAT1 PASS: 8 states, 3 on the opponent's turn, 1,883 labels.
  - GATE6 PASS (the analysis script on hand-computed fixtures).
- **This chain (gate 4a, then the chance-counter audit, then the gate-3 dry run and gates 4b and 4c), from the chain log:**
  - `2026-10-30T15:59:57Z chain2 start (pid 554584), for HEAD bd967042f6630e951ffc0f4b9cf13eb2fdcb78ed`
  - `2026-10-30T17:17:59Z gate 4a ended: seeds 64, finished 64, timeouts 0, identical 64, per seat {0: 32, 1: 32} GATE4a PASS `
  - `2026-10-30T17:17:59Z chance_ok: chance-counter audit wf_d91d342a-460: no hidden-information path (89 sites; 2 possible leaks refuted 2-0 each; critic: none uncovered); laptop check of observation.rs:494-500`
  - `planned 112 deals for stage dev`
  - `2026-10-30T17:17:59Z dry: run start `
  - `2026-10-30T19:40:58Z dry: run end rc=0 :: run_end: complete 112 of 112, stop_reason None `
  - `2026-10-30T19:40:58Z gate 3: GATE3 PASS`
  - `2026-10-30T19:41:30Z gate 4b on the dry run: setup: checked 20, equal 20, mismatches 0 (records available 70, asked 20) fallback: checked 0, equal 0, mismatches 0 (records available 0, asked 30) GATE4b INCOMPLETE `
  - `planned 48 deals for stage dev`
  - `2026-10-30T19:41:30Z forced: run start `
  - `2026-10-30T21:17:17Z forced: run end rc=0 :: run_end: complete 48 of 48, stop_reason None `
  - `2026-10-30T21:20:54Z gate 4b on the forced run: setup: checked 20, equal 20, mismatches 0 (records available 28, asked 20) fallback: checked 30, equal 30, mismatches 0 (records available 110, asked 30) GATE4b PASS `
  - `2026-10-30T21:20:55Z gate 4c on dry: GATE4c PASS (arms checked 112, lines matched 88)`
  - `2026-10-30T21:20:56Z gate 4c on forced: GATE4c PASS (arms checked 48, lines matched 69)`
  - `2026-10-30T21:20:56Z CHAIN DONE: gates 4a, 3, 4b (forced), 4c all PASS`
- **The chance-counter audit** (coordinator-110, decision 2):

**Result: no hidden-information path through the chance counter.** Whether a step a plan continues past draws from the game's random-number generator depends only on visible information.

- **What the counter is:** `chance` is 1 when `apply_action` drew at least one value from the game RNG (`engine/src/game.rs:265-269`, two probes of a cloned RNG). It matters only while a plan is active. A plan holds only the pilot's own steps in one turn, and it ends at an attack, the end of the turn, a chance step, or any opponent frame (`rl/ai_judge/plans/src/main.rs`, `step_kind` and `list_plans`).
- **Method:** workflow wf_d91d342a-460, 8 agents, on the engine at code commit bd967042.
  - Three readers covered every RNG use reachable from `actions::apply_action`: the core and stack actions, trainers and stadiums, and attacks and abilities. That is 89 sites in all.
  - Each possible leak went to two skeptics.
  - A completeness critic grepped the whole engine for RNG calls the readers had missed.
  - The laptop checked the deciding rule in the code itself: `hidden_continuation_reason`, `engine/src/observation.rs:494-500`. Public pricing is off by default, and the lister never turns it on.
- **The RNG uses that can depend on hidden cards:**
  - Penny (a Supporter in the opponent's deck), including its Luxury Coin route;
  - Smeargle's Portrait (a Supporter in the opponent's hand);
  - the random Item or Tool discard from the opponent's hand;
  - Mew's Miraculous Memory (attacks on Pokémon in the opponent's hand and deck);
  - the next player's start-of-turn random deck search at checkup.
- **Why none of them is a leak:** each is reached only by an attack step, by an end-of-turn step, or by a step whose text names the opponent's hand or deck. The lister's rule marks that last kind as a chance step whenever the opponent has unseen cards. So no plan continues past any of them.
- **Every other RNG use a plan can continue past** fires or not on visible information only: the board, discards, hand and deck sizes, the pilot's own deck contents, or its Energy types. Examples are coin flips, shuffles of either deck, random picks from visible zones, the Energy Zone roll (Rainbow Cave), and the opponent-deck shuffle of Polteageist's on-evolve effect. Two hidden worlds with the same visible board give the same chance count.
- **Votes:** the readers raised two possible leaks, generic forecasts outside one reader's slice and the Victory Star Keep step. Each was refuted 2-0. The critic found no uncovered RNG call.
- **This test's decks:** none of the cards named above (Penny, Smeargle, Polteageist, Victini, Mew), nor Lusamine, is in the four decks: 09-mega-manectric-heliolisk, 11-archaludon-haxorus-dragonair, t-lucario and t-suicune.
- **Conditions on this result:**
  1. Penny and Portrait are safe only through the text rule. Under `with_public_pricing` (the kp tiers) their texts are lifted, and they would become hidden-dependent plan steps. The lister must keep running without public pricing.
  2. `hidden_continuation_reason` gives UseStadium and stack follow-ups no text to check. That is harmless today, because stadium forecasts read only the actor's own deck and Energy Zone. A new card could change it.
  3. Not a leak, but an engine determinism point for R8: Lusamine's follow-up (AttachFromDiscard) orders its branches through a std HashMap. The same seed can therefore pick a different Energy pair in another process. Lusamine is not in these decks.

## 7. Run-procedure notes

- After any `stop:ledger_bound`, the headroom figure shown before a resume decision comes from the ledger file's total, not from `judge.ledger_charge_usd` (coordinator-109, decision 2). A resume after ledger_bound needs the coordinator's word (coordinator-108).
- If the runner hangs on an orphan `wait()` (it has no timeout), SIGINT is the recovery (coordinator-109, decision 5).
- Standing rule (coordinator-108): no agent opens a real arm's stderr.txt, its stderr_tail, or any result file before stage 1's cost and time data have gone to Dustin. The gate-4c tool reads KX_PARAMS lines only.
- For R8, later (coordinator-110, decision 5): before the adapter goes to main, `was_choice` is computed from visible information only or taken out of `pdl_since_last`; RESULTS says which.
