# The rules engine switch (Oct 2026): decisions and who does what

The plan is `PLAN.md` (0a68b0a). This file records the decisions on it and who did which part.

## Dustin's decisions (Sept 30 evening)

Given in the Fable coordinator session ("Work delegation and task routing") and relayed to the laptop session. The coordinator put the plan's questions 1-6 and 8-10 to him as nine items, each with the plan's recommendation. His answer, verbatim: **"Sure go for all 9"**. So, as recommended (numbers as in `PLAN.md`):
1. **A conditional go: "pin if all pass".**
   - Every replay must be identical and every counter must read as expected.
   - Every changed carrier or scratch game must be explained: on the board by an exact counter, or in lookahead by a trace that meets both halves.
   - A trace that needs a judgment call comes to him, and the pin waits for his word on it.
2. **Scope:** A + B + kd's follow-ons + F1-F7. 09e964f, PR #383 and B4b data are left out.
3. **The per-thread heads-cut value** is kept.
4. **Carrier lists:** real development lists, extracted by the cloud from the committed Limitless archive. The made lists are the fallback.
5. **km3's coverage baselines** are replayed at this switch, as a gate.
6. **kd3's identity** is a gate.
8. **When:** overnight laptop runs on the Oct 1 and Oct 2 nights. Each morning everything is committed and pushed, with main = origin/main, by 7:00 am Central.
9. **If A fails its mechanic check:** hold A, and ship B + kd if B passes (a revert commit of A, a new build and the replays again).
10. **09e964f:**
    - Fix 2 is recorded as not taken. It contradicts the JP ruling the fork follows (`rules/06_sources.md:124`) and would break `rules_repair_retaliation_timing.rs:136`.
    - Fix 1 stays "unchecked" until F8 or a second reader settles it.

**Question 7** (the order against the cloud's N1) was the coordinator's operational decision:
- Sonnet does F1-F7 tonight on `sonnet/rules-fixes`, cut from cae37a3, with no `players/` change, and pushes it.
- R is that branch's head.
- The cloud stays on N1.

## The carrier lists (step 3; the coordinator's choice under Dustin's Q4 answer)

The cloud extracted them from the committed Limitless archive (commit e0d149a on `claude/pensive-ptolemy-spwc0b`, `carriers/`; provenance in its `README.md` and `selection.json`). By the plan's rule, the most frequent exact list among top-8 development finishes, only one exists:
- **`garchomp_meowth.txt`** (Meowth B2 124). Shaquill10, BEC'S KING OF THE HILL, 95 players, 2026-09-18, 5th place (4-1).

The other three have real development lists, but none placed top-8. These are the "alternates":
- **`alternates/togekiss_meowth.txt`** (Togekiss A4 080 and Meowth). Alolan Jay, The Breakfast Club Nightly, 118 players, 2026-09-07, 19th place (5-3).
- **`alternates/hisuian_goodra.txt`** (Hisuian Goodra B3b 050, the (a) finite cut). tommyboistreams, TH Event's "When DX Pack?!", 68 players, dropped (0-3).
- **`alternates/houndoom_victini.txt`** (Victini B3 025, repair A). foodking90, Dark League Pocket Tournament, 118 players, 2026-09-12, dropped after round 1 (0-1).

**The coordinator's decision** (Sept 30, operational, under Dustin's Q4 answer "real lists, made lists as fallback"): step 8's carriers are `garchomp_meowth.txt` plus the three alternates.
- The reason: a carrier's job is to reach the mechanic in real play, not to measure strength, and a poor record doesn't change which cards a list holds.
- The made lists (`coinflip_deck.txt`, `fire_victini.txt`) are used only in 8b's scratch rows.
- Every list passed the cloud's card checks: one printing per id, no B4b card, the validator clean, and a 560-game legality scan with no findings.
- Each list's Energy line was added from its Pokémon's attack costs, since the archive's decklists carry none (`select_carriers.py`).

**R stays Sonnet's branch head,** never the cloud's head. The cloud's kn (N1) build is on the same cloud branch (71877f6) and changes `players/`.

## After the laptop's second read of R (Sept 30 evening)

`SECOND_READ_F1_F7_opus.md` (fa1d442) found no code bug, and four things to fix before sitting 1. The coordinator's decisions:
- **(a)** Findings 1, 3 and 4 are Sonnet's, tonight on `sonnet/rules-fixes`, and they give a new R:
  - F7's test numbers;
  - `counter_probe` cases for `offgate_discard_then_damage`;
  - every firing tick recorded.

  Finding 2's runner change is the laptop's, and it's made: step 7b requires both off-gate counters above 0. 7c's scope has no t-vespiquen pairing, so there the discard counter is reported only.
- **(b) The mechanic check's "on the board"** is tightened, in the coordinator's wording, Oct 1: an exact counter must fire in the same turn as the first differing move. Otherwise the probe must show the gate within search depth (both halves), and an earlier firing alone explains nothing. It's written into `PLAN.md`'s mechanic check.
- **(c) Victory Star smoke game 28** holds by elimination only, through one sampled Copycat draw. It goes to Dustin on Oct 1 evening as the one judgment call, and it doesn't block the build. A step 8 game that lands the same way stops, as the plan says.
- **The cloud's later-round coin branch** is cut from the old R (1abdbe8). When the new R lands, that merge touches only test files, but the laptop checks it before step 4.
- **Sitting 1:** Oct 1 from 5 pm Central, on the new R, after the laptop's short re-read of the three fixes.

## Sitting 1 (the night of Sept 30) and two notes from the coordinator (Oct 1)

**Sitting 1 passed** (record b55aad4; `STATUS.txt` and `PIN_STATUS.txt` here). Dustin asked "If it's 6.5 hours why not run it now?", so the coordinator moved the start up a day: it started at 03:10 UTC Oct 1 (10:10 pm Central) and finished at 06:47 UTC.
- **Step 4:** candidate 5a18d31 (main c9f4224 + R f8cfa9c). Its engine/ is R's tree 38af8b0, and it changes exactly the plan's 9 engine files.
- **Step 5:** deckgym 2f7e5fd6, legality_scan 97891274, goldfish cecc76fb (`programs.sha256`).
- **Step 6:** the watch legality_scan, 8d881a1b.
- **Step 7:** 151,240 of 151,240 identity games equal to their references on every field, kd3's gate included.
- **Step 7b:**
  - 28,000 watch games equal to the plain ones, with every repair counter 0.
  - offgate_helper_choice fired in 12,246 games and offgate_discard_then_damage in 3,353.
- **Step 7c:**
  - The 4 floor pages replayed, 1,920 of 1,920 games each equal.
  - The 32 pairings x 60 were identical on the watch and old programs, with repair counters 0.
  - offgate_helper_choice fired in 218 of the 540 in-scope games. offgate_discard_then_damage read 0 there; it is reported only, and rows 13 and 22 carry to steps 8 and 8b.
- **One stop: a runner fault, not a result.**
  - At 03:16 UTC, right after step 5 passed, a bare assignment failed under pipefail: `prog_sha` read `watch.sha256` before step 6 made it.
  - Fixed in 4f0a4fd. The restart at 03:19 re-checked steps 4-5's evidence and skipped them.
  - An Opus reader then checked the rest of the runner for the same kind of fault and found none on the path that ran. Sitting 2's scripts get the same check.

**F8 is done** (the cloud, 5a929c0, `f8/F8.md`). The fork already covers 09e964f's fix 1: knockouts resolve in waves, plus a nested pass.
- Upstream's Lilligant test passes on d363ba8.
- Planted faults show that only removing both guards reproduces upstream's failure.
- So at step 13, `rules/09`'s line 80 and `PLAN.md`'s line 26 change from "unchecked" to "covered, F8.md".
- Dustin's answer on fix 2 (question 10 above) stands.

**The cloud's later-round coin fixes** are on their own branch, `claude/coin-prevention-round2`.
- It is 76b87cd: six sites, with the suite at 2,025 passed and 0 failed.
- It is cut from R. This corrects the note above, which said it was cut from the old R.
- They are not in this switch: Dustin's scope answer (question 2) is A + B + kd + F1-F7. They go in the next rules switch.
- So 8b's l-sharpedo v meowth_carefree row stays this switch's Wild Swing control, as planned.

## Sitting 2 (steps 8-10): the runner and the coordinator's decisions (Oct 1)

`sitting2.sh` (with `sitting2_check.py`) runs PLAN.md's steps 8, 8b, 9 and 10 on sitting 1's programs, never rebuilt. The plan's model was sitting 1's runner. Two Opus reviews (evidence and safety) found no blocker, and their fixes are in.
- **When:** Oct 1 from 5 pm Central. Step 8 can't start on the night of Sept 30, because 8c's trace load (below) doesn't exist yet.
- **Order:**
  1. `8-seeds`: the carrier lists (e0d149a's blobs, at the same paths in `carriers/`) and 8b's scratch decks (`scratch_8b/`, the candidate's blobs) are brought onto main blob-checked, and `pairs_8.tsv` and `seeds_8.txt` are committed, all before any game.
  2. 8b.
  3. The trace-load gate.
  4. 8, if the gate allows.
  5. 9 and 10.
  6. The gate is read again; step 8 runs then if it can still end before the deadline. Otherwise the sitting ends PAUSED, and a later start runs step 8 alone.
- **The trace-load gate:** step 8 starts only when `trace_load.txt` here is committed with a line `TRACE LOAD <n> <the cloud's commit and text>` and n is about 50 or less, or with a line `DUSTIN <his words>` (PLAN 8c).
  - The load comes from the cloud's 8b early-warning rows on its build of R (`early_warning_8b/` on its branch, classified with `tightened_rule.py`); the laptop runs no traces.
  - Optional `CLOUD8B <commit> <bot> <path>` lines make the gate check that the laptop's 8b rows equal the cloud's (PLAN 8b).
- **The hand-off to 8c:** `handoff_8c.tsv` and `handoff_8c.md` list every changed game of 8b and 8 with what a tracer needs, and `touched_check.txt` gives reach per mechanic. The cloud traces from them, and Sonnet reads every hand trace.
- **Condition 3 (the coordinator's ruling, Oct 1, consistent with Dustin's Q1 answer):** PLAN.md:95's "must be identical" reads as "no exact counter fired on the board and no trace meets both halves". A game whose lookahead trace meets both halves is one where a repaired mechanic acted, so it is explained. The runner lists each such game as CONDITION 3, a pin-gate item, and one with no trace meeting both halves fails as before.
- **Frozen on main until sitting 2 ends** (a change to a step's input halts that step): `decks/screen/run_screen.py`, `decks/brews/brew-06*.txt`, `decks/research/{altaria,blaziken}.txt`, `decks/screen/opponents/*`, step 9's pairs files and their decks, and this folder.

## Who does what

| Part | Who |
|---|---|
| Repairs A and B, S1-S4 | the cloud (commits on `claude/pensive-ptolemy-spwc0b`) |
| The second read of A and B | Sonnet (`../coin_prevention_repair_2026-09-30/SECOND_READ_sonnet.md`) |
| The integrator's review and this plan | the laptop session (Opus), with its subagents, reading only |
| F1-F7 (tests first, then fixes), ending at R | Sonnet, on `sonnet/rules-fixes` |
| The second read of F1-F7 | an Opus subagent of the laptop session, reading only |
| The step 2 equivalence readings | the laptop's Opus subagent (`EQUIVALENCE_opus.md`, tracing every caller) and Sonnet (the other reading) |
| The carrier lists (step 3) | the cloud, beside N1, via Dustin's paste block |
| The build, the replays, the pin and the floor re-check | the laptop |
| The traces (step 8c) | the cloud, with Sonnet reading every hand trace |
| Routing and audit | the Fable coordinator session |

This table is updated as each part lands.

## Sitting 1's runner and the shared index (one exception, recorded for Dustin)

`sitting1.sh` never stages or commits through the shared index (the one GitHub Desktop uses). Each checkpoint commit is built in a private index, and main moves to it only if no one else moved main meanwhile, as `pin.sh` makes the pin commit.
- **The exception:** right before main moves, the shared index's entries for exactly the files being committed are set to the new commit's (`git reset <commit> -- <those files>`, `pin.sh` line 487 does the same). Without it, GitHub Desktop would show those files as deleted or changed back, and another session's commit could record them that way.
- Nothing else in the shared index is touched. A start unstages files of this folder only when they are staged with the working copy's own content, which is what an interrupted checkpoint leaves.
- It pushes only its own commits (and the runner's own commit), only as a fast-forward of origin/main. When origin/main is ahead, or main carries another session's unpushed commit, it stops and says what to do.
