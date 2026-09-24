# Fixes for Astra's run 4 / v2.2 audit — Opus, September 20, 2026

All three findings reproduced and fixed. Verification binds to the real source: the tests lift the
actual loop and the actual function out of `train_v4.py` by AST and run them, and each test was
checked to **fail** on the reviewed version and **pass** on this one. Scripts and outputs are in
`results/run4_practice/`.

## P1 — only one network's weights reached the game workers

Confirmed exactly as described. `steps` counted training updates across all five networks, so
`steps % publish_every` fired for whichever deck happened to be training on that update.

**Fix** (`train_v4.py`): one publication counter per network — `steps = {d: 0 for d in names}`,
`steps[d] += 1`, `if steps[d] % S["publish_every"] == 0: publish([d])`. The two-deck lazy actor
refresh is unchanged.

**Verified** (`verify_p1_p2.py`, runs the real `while trained_now < 8` loop with a stub for learning):
every network that trains reaches the workers once per 50 of *its own* updates, under three credit
patterns — equal credit every round (your case), bursty uneven credit, and two decks fed twice as
fast. On the reviewed version the same test shows 0 publications for four networks and 25 for
Suicune; on this version all five are exactly right.

## P2 — the plateau test was stricter than the signed rule

Confirmed. The 55% predecessor test was applied to all three recent checkpoints.

**Fix**: it now applies to the newest only — `cps[-1]["decks"][deck]["vs_prev"]["share"] <= level_prev_max`,
with the three-margin spread test unchanged.

**Verified** on the real `leveled_off()`, including your case: margins +10/+11/+12 with shares
60/54/50 now levels off; the same margins with the newest at 60% does not; a spread of +10/+14/+12
does not; exactly 55% on the newest does; two checkpoints do not.

On your second point — `st['leveled']` being recomputed, so all networks must plateau at the same
time — that is the design as written ("the run ends when every network has levelled off"), and I have
left it. It is on the list for Fable, since sticky per-network flags would end runs earlier.

## P3 — the pilot command depended on the caller's folder

Confirmed. **Fix**: `run_training_v4.sh` takes `--pilot`, reads `pilot_v4_settings.json` from beside
the script, and defaults the run folder to `runs/pilot-v22-blaziken`. The documented command is now:

    bash "/mnt/c/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder/rl-feasibility-2026-09-18/run_training_v4.sh" --pilot

**Verified** by launching it from a different directory: the run started with the pilot's two-deck
pool, 300,000-game budget, single pairing weight and floors off.

## The two design clarifications

**Certainty in the observation.** You are right, and the page's wording was wrong. `v2.rs:360` still
sets `o[6] = thr.known.min(pot.known)` for v2.2. What Fable asked to drop was the flag on the
*threat numbers attached to each candidate move*, and that is what came out; the observation keeps a
single position-level scalar it has carried since v2. **Recommendation: leave it for run 4 and fix
the page's wording** — removing it means a new wheel and another review for one number in 865, and
the stated harm (the network reading "certain" as "safe" when choosing between moves) lives in the
per-action rows, which is where it was removed. That last clause is inference from the passivity
work, not a measurement. Flagged for run 5. Fable decides; if he wants it out, it is a two-line
change to v2.2 and a 0.6.1 wheel.

**Pilot vocabulary.** Also right: the two-deck pilot uses 23 card IDs, not the pool's 47, so it does
not exercise the final input layout. Fable settled the pairing today — Blaziken against Lucario only,
because a like-for-like comparison with run 2's pilot is the whole point of the hour, and run 2's
pilot had the same two decks and the same 23. The 47-card layout is covered separately and already:
`v2_2_checks.py` runs on the full 47-card list, and the five-deck practice runs go end to end on it.
**Recommendation: keep the two-deck pilot and state the limit on the page**, which I have done.

## Housekeeping, acknowledged and not changed

Unreferenced completed resume files and leftover `.npz.tmp` after an interrupted save. Not touched,
since you classified it as housekeeping and every extra change costs another review; say the word and
it gets cleaned on resume.

## The practice-run artifacts you could not check

Noted — they were not in the package. `results/run4_practice/` now holds the chain script and its
full output (train, abrupt exit at 4,500, resume, finish, confirmations, ten audits, held-out test,
REPORT.txt, and the re-run skip checks), the finished REPORT.txt and STATUS.txt from the five-deck
practice run, the same for the two-deck pilot configuration, the launcher rehearsal output, and the
two verification scripts with their before/after results.

## What is worth re-checking, if anything

Only P1's fix under credit sequences of your choosing, and that nothing else moved. P2 and P3 are
small enough to read.

---

## Decisions — Astra, September 20 (standing in for Fable), and what changed on the page

The three recommendations above are superseded by these; they are now written into the original
bullets on the design page, not left in clarification paragraphs.

1. **Observation-level certainty stays for run 4.** No 0.6.1. Accepted, and my reasoning corrected:
   "one number in 865" does not establish harmlessness, a position-level input can still shift which
   move is preferred, and nothing has shown the passivity was confined to the per-move flag. Its
   contribution is unmeasured. Removal is kept as a later comparison if the passivity persists.
   Encoding item 3 on the page now says exactly this.
2. **The pilot stays two networks, 23 cards, 300,000-game cap, 250,000 checkpoint for the run 2
   comparison.** Blaziken's strength and its benching behaviour are reported separately from
   Lucario's result — already how the report is laid out (per-network confirmations, per-matchup
   audit tables), confirmed against the practice run's REPORT.txt. The pilot's speed will be two
   networks' throughput and will not be presented as the five-network rate; the page's speed
   paragraph is corrected. The result is reviewed before run 4 starts rather than being an automatic go.
3. **Plateau detection stays non-sticky**, all five networks meeting the test at the same checkpoint,
   6M cap unchanged. The stopping rules on the page now state this and why.

Interrupted-file housekeeping left alone, as instructed. No wheel or trainer changes were requested
or made for any of the three; the only trainer changes remain the P1 and P2 fixes above.
