# Exam run 3: results (2026-10-26, 02:00-06:39Z)

Run folder `live-20261026T020013Z` (kit `32c7c9cafdcb202bd7ed0f2c488fdc5fd6c16205`, K20; exam v2 frozen at 6e5fab0c, K19; judge `judge-prompt-frozen-7`). Results go to the coordinator only.

## The registered primary, and run 3 alone (equal prominence)

| | decisions (games) | Gemini | km3 (mean of 3 seeds) | Gemini minus km3 | sign-flip p | verdict |
|---|---|---|---|---|---|---|
| **PRIMARY: runs 2 + 3 pooled, 97.5%** (section 4) | 307 (102) | 0.622 [0.567, 0.677] | 0.451 [0.381, 0.520] | **+0.172 [+0.089, +0.254]** | 3e-05 | **judge higher; PASS = True** |
| **Run 3 alone, run 2's rule (95%)** (section 5) | 258 (76) | 0.624 [0.571, 0.677] | 0.451 [0.388, 0.515] | **+0.173 [+0.095, +0.250]** | 9e-05 | **judge higher** |
| Run 2 alone (for reference; its own report) | 49 (26) | | | +0.163 [-0.014, +0.347] | 0.108869 | inconclusive |

- **The PRIMARY passes** (section 4: the 97.5% game-clustered interval lies entirely above 0 AND the sign-flip p < 0.025; 102 games, at least 10).
- **Run 3 alone also gives "judge higher"** at run 2's rule (its 95% interval above 0, sign-flip p < 0.05, 76 games). The two runs are different games and points by construction.
- **The model:** every judge row returned `gemini-4-argon`, run 2's model (section 7: pooling ON). frozen-7's analysis.py was used unchanged (sha256 64f78cbd7f6d…); 20,000 resamples, seed 20261019; sign-flip Monte Carlo, 100,000 draws, seed 20261020.
- **Failed judge replies (no choice, scored as misses):** 0 of 258 (run 3); pooled 0 (0.0%). The >20% rule (A3) is not triggered.
- **The formal compare:** `judge.py compare --on-problem fail --failed-judge-rows miss`, status complete, formal True, problems 0; rows 1032 of 1032 (km3 {'ok': 774}, judge {'ok': 258}).

## Section 8, the sentence written in advance

> "Gemini is a better plan picker than km3 on his decisions."

- As registered: **the formal kx3 test (frozen-5) still comes before anyone says it beats our best bot.** km3 is a frozen, untuned baseline.
- What is measured is **prefix agreement** with his first plan segment (v1.6's scoring; R1's lister segments): it is not plan quality.
- **Stage 2 was declared after stage 1 was seen** (section 4), which is why the bar was 97.5%. There is no stage 3 on this question until 50+ new labelled games exist.

## Secondaries (reported, not deciding)

| | decisions (games) | Gemini | km3 | Gemini minus km3 | sign-flip p |
|---|---|---|---|---|---|
| Chance-ending stratum, run 3 alone (95%) | 168 (74) | 0.649 [0.582, 0.713] | 0.490 [0.426, 0.556] | +0.159 [+0.075, +0.242] | 0.0006 |
| Chance-ending stratum, pooled (97.5%) | 201 (96) | 0.647 [0.577, 0.714] | 0.489 [0.418, 0.559] | +0.158 [+0.067, +0.247] | 0.00019 |
| Full-scope block, run 3 alone (95%; the formal compare's) | 86 of 90 (46) | 0.591 [0.500, 0.686] | 0.368 [0.259, 0.478] | +0.209 [+0.070, +0.349] | 0.00876 |

- **The chance-ending stratum** (section 5; `strata/STRATA.md`, fixed before any row): 33 points from run 2 and 168 from run 3, 201 pooled. No verdict is drawn from it.
- **The full-scope block:** 4 of the 90 full-scope points were not comparable for both bots and were dropped, not scored (km3's plan stops at a chance event: 20261020_000857000_SR-t1, 20261023_122720000_SR-t1, 20261024_175606000_SR-t1; Gemini's: 20261023_122720000_SR-t1, 20261023_215109000_SR-t3). K9's caveat point 122720-t1 is one of them; the other four K9 points are not full-scope.
- **The sensitivity repeat** (run 2's design): **incomplete, so no sensitivity comparison** (K20). 257 of 258 decisions have a repeat row. LAD-20261023_225646000_SR-t11 got HTTP 429 on both of its issued repeat calls (repeat pass 0 and its single resend in pass 1), so by K20 it was not sent again. The same decision had also hit HTTP 429 in the primary's pass 0; its resend in the primary's pass 1 returned a reply.
- **Gemini against run 1's Sonnet judge:** no point overlaps (run 3's points are new), so there is nothing to report.

### By category (by_category.json; descriptive, a point counts in each of its kinds; no interval, no verdict)

- **Answer kind:** attack now (92): Gemini 0.565, km3 0.475; prepare (151): Gemini 0.669, km3 0.435; sacrifice (15): Gemini 0.533, km3 0.467
- **Deck kind:** Bench preparation (223): Gemini 0.619, km3 0.466; control and combinations (178): Gemini 0.629, km3 0.406; evolution and setup (212): Gemini 0.627, km3 0.454; fast pressure (83): Gemini 0.590, km3 0.538; sacrifice and recovery (139): Gemini 0.619, km3 0.477
- **By deck:** in `by_category.json` and `categories.txt` (24 decks, most with few points; deck ids are mapped to their lists in `decks/DECKS.json`). Note: categories.py's own `what` text says "the 49 primary points" (run 1's wording); here it is all 258.

## REPORT-ONLY (K19): his third lines, beside what the judge and km3 played (no scoring)

Slots are as in the position: 0 is his Active, 1-3 his Bench from the left. km3 played the same line on all 3 seeds at each of these points.

- **Q8** `LAD-20261022_235420000_SR-t10` (his answer: "Not sure"). His board: 0 Flygon ex, 1 Goomy, 2 Trapinch, 3 Dragonair.
  - His note: "The other line here seems to value the second point, but that is worthless when they are about to get 3 points and win the game. But a move I see now that I'm unsure why I didn't do would be to retreat and put goomy in the active spot, since I have one card left to draw and it is a second flygon that I could evolve and use next turn. Playing cyrus and retreating to goomy might have been the best move."
  - His move: `Attach:1Grass@2 zone, Attack:Dragon Pulse`
  - Gemini: `Attach:1Grass@2 zone, Play:Cyrus, Activate:1@1, Retreat:1, ChooseRetreatEnergy#{"energies":["Grass","Fighting"],"to_in_play_idx":1}, Ability@3, AttachTypedFromDiscard:Grass@0, EndTurn` (stops at: end_turn)
  - km3: `Play:Cyrus, Activate:1@1, Attach:1Grass@3 zone, Attack:Dragon Pulse` (stops at: attack)
- **Q9** `LAD-20261022_235420000_SR-t4` (his answer: "Both were fine"). His board: 0 Dratini, 1 Trapinch, 2 Goomy, 3 Trapinch.
  - His note: "Upon reflection, I think retreating would have been the smartest move. I think I was trying to take the kill, but retreating to goomy might have been the best move. The opponent would then have had to waste their next energy attaching it to happiny, or retreat and attack with riolu and wouldn't have been able to attack with lucario. This would have given me time to get the dragonair for the energy attaching ability or just the turn based energy I needed to get flygon ready to attack, before exposing him to the danger."
  - His move: `Play:Rare Candy, Evolve:Flygon ex@1, Play:Professor's Research, Play:Hiking Trail, Attach:1Fighting@1 zone, Attack:Slam`
  - Gemini: `Play:Professor's Research` (stops at: chance)
  - km3: `Retreat:3, Play:Rare Candy, Evolve:Flygon ex@0, Play:Professor's Research` (stops at: chance)
- **Q11** `LAD-20261023_005124000_SR-t8` (his answer: "Not sure"). His board: 0 Pheromosa, 1 Celesteela, 2 Buzzwole ex, 3 Buzzwole.
  - His note: "Honestly not sure. My thinking was, the only way to win this is to kill their mega. Doing damage to butterfree is virtually worthless unless I kill it, which the other line wouldn't do. Then they use butterfree's attack, do 60 damage, I then either have to switch to someone else, but also they now have damaged my ex and can use cyrus at any time to pull him up and kill him in one shot with mega sceptile. Retreating and attacking with buzzwole maybe would have been the best move, but my logic was using pheromosa does damage to sceptile and that is the only way to win."
  - His move: `Play:Lusamine, AttachFromDiscard#{"in_play_idx":2,"num_random_energies":1}, Attach:1Grass@3 zone, Attack:Jump Blues`
  - Gemini: `Attach:1Grass@3 zone, Retreat:2, Play:Lusamine, AttachFromDiscard#{"in_play_idx":0,"num_random_energies":2}, Attack:Big Beat` (stops at: attack)
  - km3: `Play:Cyrus, Activate:1@1, Attach:1Grass@2 zone, Ability@1, Activate:0@2, Attack:Punch` (stops at: attack)
  - Engine note: the non-ex Buzzwole is not an Ultra Beast in the engine data (the cause of the 3 G1 drops): a line through its Ultra Beast effects is outside what the engine plays.
- **Q15** `LAD-20261023_204548000_SR-t7` (his answer: "My play was better"). His board: 0 Oricorio, 1 Wartortle.
  - His note: "Once again, the only way you win is getting blastoise with enough energy, the other line waste an energy to put the more valuable pokemon into a vulnerable position. I think that is the worst move possible. That being said, switching to bench eiscue wouldn't have been unreasonable"
  - His move: `Play:Poké Ball, Attach:1Water@1 zone, Place:Eiscue@2, EndTurn`
  - Gemini: `Attach:1Water@1 zone, Place:Squirtle@2, Play:Poké Ball` (stops at: chance)
  - km3: `Play:Poké Ball` (stops at: chance)

## How it ran

- **Launch:** tmux `run3live`, armed at 22:44Z, started 02:00:13Z (the night window opens 02:00Z). The worktree was at the kit commit; the key came from ~/.bashrc and was never printed. freeze_identity passes; the harness tests (406) pass; the inputs equal K19 and are unchanged at the tip.
- **km3:** 774 rows at 02:02:27Z (seeds 25,101,000,001-003, nice 19, the frozen baseline).
- **The judge** (2 workers; K20's passes):

| batch | pass | asked | sent | NOT SENT | failed | without a row after | spend |
|---|---|---|---|---|---|---|---|
| primary | 0 | 258 | 195 | 63 | 1 | 64 | $9.91 |
| primary | 1 | 64 | 64 | 0 | 0 | 0 | $2.61 |
| repeat | 0 | 258 | 196 | 62 | 1 | 63 | $9.81 |
| repeat | 1 | 63 | 2 | 61 | 1 | 62 | $0.79 |
| repeat | 2 | 61 | 55 | 6 | 1 | 8 | $3.25 |
| repeat | 3 | 7 | 7 | 0 | 0 | 1 | $0.17 |

- Every failed call was HTTP 429 (TPM quota). Each one halted its pass (frozen-7's rule), and the tasks after it were recorded NOT SENT and went in a later pass, as K20 registered. The primary was complete after 1 later pass; the repeat used all 3 and ended with 1 decision issued twice without a row.
- **The compare** ran at 03:57:28Z; the pooled primary and both strata immediately after (no API call); then the repeat.
- **STATUS STOP** at the end only because the repeat was incomplete (K20: no sensitivity comparison; everything else written). Nothing unregistered happened; nothing was worked around.

## Spend (ACTUAL where the records give it; caps are not spending)

- **Gemini (this run):** 515 calls, 4,043,395 input tokens, 1,545,092 output tokens, $23.538 at the assumed prices (assumed list price per million tokens; verify in the console). That is the harness's own token counts at its price table (Gemini 4 Argon on Vertex, $2 / $10 per 1M input / output tokens through 2026-11-30): **an estimate, until the Google billing page confirms it.**
  - The ledger shows $26.53: the same plus the full worst case charged for each of the 4 calls that got HTTP 429 (frozen-7 charges a failed call its worst case because whether it was billed is unknown). The caps ($40 primary, $75 ledger) were never near.
- **The Claude credit-worker jobs for run 3's prep** (INV, Part A, the labels, the relabel, the second pass, Part B): their logs (`job.log`, `--output-format text`) **record no cost**, so only the caps are known: INV + Part A $8 per part (6 parts, at most $48); the labels $15 per part (5 parts, at most $75); the relabel $5; the second pass $8 per part (2 parts, at most $16); Part B $10 + 5 x $5 (at most $35). **The actual amounts are in the Anthropic Console** (API usage) if Dustin wants them.

## Records

- **This folder:** `run3/live-20261026T020013Z/` (the run's own files, without its git clone), with `run_manifest.json` (every file's sha256, the inputs, the kit commit, the passes).
- **Reads (C1):** the laptop session read the run's outputs to write this report. While gathering the credit-worker job logs for their cost, a glob also matched the `label_out_p*.aborted_20261025T172559Z` folders: it ran a byte count and a text search for cost strings on their `job.log` files, which are empty (0 bytes). Nothing else in those folders was opened or read.
- **To-dos for after the runs** (K19): Q1's note asks "I would be curious to know if one was definitely better than the other". Q14's note assumes the alternatives came from "the bot"; they came from the labellers.
- **Queued after this report** (Astra's weekly review, via the coordinator): the containment line in the agent rules (answer-material files named; developers get answer-free excerpts only).
