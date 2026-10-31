# Registration addendum: stage 2's ledger and size

This addendum records stage 2's ledger. The registration (tag `judge-prompt-frozen-8`, commit 7b14546f, §5) asks for it:
"Once set, it is recorded in an addendum to this registration before stage 2 starts. It can't change afterwards."

- It is committed before stage 2's first Google call, on top of the errata commit 4a09f326.
- There is no code change and no FROZEN8.json change. The tag is not moved.
- Where the registration and the errata leave a point open, this file governs for stage 2.

## 1. Dustin's decision, verbatim

He answered in the laptop session's chat on Oct 30, 2026 (CT), about 21:30-21:40 (Oct 31 ~02:33-02:40Z). He answered by picking from the options shown, after reading the stage-1 cost and time report.

**Question 1:** "How big should stage 2 (the scored part of the Gemini test) be?"
- **His answer:** "128 deals, $127 (Recommended)"
- **The option's text as shown:** "Best chance of a clear answer. Likely real cost ~$61, about 4 laptop nights; it goes ~$35 past the $100 you set aside (the cap, not the likely spend)."

**Question 2** (asked because the ledger is above the ~$92 left of the $100 reserve; coordinator-115 condition 2): "The $127 budget goes past the ~$92 left of your $100 reserve. Did you check your Google credit balance, or should I go ahead without checking?"
- **His answer:** "Go ahead without checking"

**Question 3:** "Stage 2 needs about 33 hours of laptop time in total. When can it run?"
- **His answer:** "Tonight, straight through (Recommended)"
- **The option's text as shown:** "Starts tonight and runs whenever you don't need the laptop, finishing around Sunday morning. Run pause.sh any time you need the laptop; the game in progress gets replayed later."

His Oct 30 money words, already in the registration's §1 ("Stage 2's money"), say the $100 is not a ceiling while credits last.

**Stage 2's ledger: $127.00.** As the registration says, it is held until stage 2 ends or Nov 27, whichever comes first.

## 2. The stage-1 data it was set from (outcome-blind)

Stage 1 ran 22:15:22Z Oct 30 to 02:21:46Z Oct 31 (rc 0): 16 of 16 deals, `stop_reason` null, model `gemini-4-argon`.

The data came from the runner's `status` and an arm-row breakdown of cost and time fields only. No result file, stderr or win count was opened.

- **Ledger charge per G game:** mean $0.4744, max $0.9405. Actual cost equals the ledger charge. Total: $7.5910 of $15.
- **Judge calls per G game:** mean 9.9, max 15.
- **Seconds per game:** G mean 732.6, K mean 191.3, so 923.9 s per deal.
- **Fallback rate:** 2 of 161 interventions = 0.0124, setup excluded.
- **Failures and errors:**
  - failures by class {}; dropped deals 0; infra attempts {};
  - protocol errors 0 and lifecycle errors 0, so 0 engine errors and 0 illegal moves.

## 3. N and the go/no-go (§5's rules applied)

**N** is the largest multiple of 16 that is ≤ 128 and meets both:
- **dollars:** 128 × $0.9405 = $120.38 ≤ 0.95 × $127 = $120.65. Holds.
- **time:** 128 × 923.9 s = 32.8 h, against about 250 laptop hours (9 h a night) before Nov 27 23:59 CT. Holds.

**So N = 128:** k = 0-7, all 16 cells per k, k-major. Seeds are 25,103,000,000 + 100 × cell + k.

**Go/no-go:**
- N ≥ 80: holds.
- 0 engine errors or illegal moves in stage 1: holds.
- Fallback rate ≤ 10%: holds.
- Every gate in §2 passed: holds (errata §1).

**So stage 2 runs.**

## 4. Stage 2's run settings

**Plan:** `game_runner.py plan --stage 2 --k-range 0-7 --cells 0-15` (128 deals).

**Run flags:**
- `--stage 2 --ledger-total-usd 127`, on a new ledger file of its own;
- `--call-cap 45` (3 × stage 1's largest calls per game, 15; §2);
- `--stage1-max-game-charge 0.9405`, so a new deal starts only if headroom ≥ $1.881;
- `--expect-model-version gemini-4-argon`;
- arms G,K; no mock or force flags (the runner refuses them).

**The runner's own stops:**
- the pooled fallback rate checked after each complete 16-deal block (> 0.10 stops);
- `stop_date` at 2026-11-28T05:59:00Z;
- the model-version check;
- ledger headroom.

**Conditions (unchanged from stage 1, errata §4):**
- one game at a time, 8 threads, nice 19;
- never beside a cargo build or a workflow;
- an auto-pause when C: falls below 5 GB free.

**Schedule:** Dustin's answer to question 3.
- Stage 2 starts tonight and runs whenever the laptop is free, pausing when he runs pause.sh.
- A game in progress at a pause is replayed as an `infra` attempt (pause gap or pause marker). The aborted attempt's Google spend counts toward the ledger.
- The registration's plan list says "Stage 2 at night, nice 19, with the laptop free". Running through free daytime hours too only makes it finish sooner.
  - §5's time term counted 9 h a night, so it does not change N.
  - No scoring rule depends on the hour of play.

## 5. Unchanged

- Scoring, labels and the analysis (§6).
- Outcomes stay closed until stage 2 ends: no result file, stderr or win count is opened before then.
- No change to stage 2's ledger after this commit.
