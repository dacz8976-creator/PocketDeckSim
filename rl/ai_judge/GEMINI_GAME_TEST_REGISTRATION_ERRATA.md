# The Gemini finished-game test: errata to the registration (frozen-8)

Written on 2026-10-30 at about 22:20Z by the laptop session. That is after the tag `judge-prompt-frozen-8` was made (commit `7b14546f3dd0740da684221885b55563dcfc397e`), before it was pushed, before any Google call, and before any stage-1 game.

**Why this file exists:** an independent read-only review of the push (workflow wf_3b5b48cc-501, with two skeptics per major finding) found one false sentence and some gaps in `GEMINI_GAME_TEST_REGISTRATION.md`.

**What this file does and doesn't do:**
- The tagged file is left unchanged. Coordinator-112 said not to re-tag after LAP4.
- This file corrects and completes the tagged one. Where the two differ, this file governs.
- Nothing here changes the design, the money, any gate result, any code or FROZEN8.json. `git diff 7b14546f` on this branch touches only this file.

## 1. Which commit each gate ran on

The registration's opening paragraph says "The gates below ran on code commit `bd967042…`". That holds only for the last chain: the dry run, gate 3, gate 4b and gate 4c, plus freeze8 check (GATE5). The earlier gates ran on earlier commits of this branch.

| Gate | When (UTC, Oct 30) | Commit |
|---|---|---|
| sc_kx3 (the kx3 and km3 self-checks equal the pins) | 03:59 | `9fbd8ca` (engine tree 34fef9e5, the same as every later commit) |
| Part A RUN1-RUN4 re-run on the plain binaries | 05:35 | `19a21ae` (Part A's tip) |
| GATE1, GATE2a, GATE2b, SEAT1, GATE6 (the Part B worker) | 05:48-06:28 | Part B's run, tip `6e6de3f` |
| GATE6 again (the Part C worker), then the laptop's GATE2b record run with the fixed tool | 07:58-08:27 | `1d209a6` (Part C's tip) |
| Gate 4a, seeds 1-10 | 06:59-07:57 | `6e6de3f` (gate4a.log: "start at 6e6de3f") |
| Gate 4a, seeds 11-64 | 08:27-17:17 | `1d209a6` (gate4a.log: "start at 1d209a6 --resume; rows so far 10") |
| The chance-counter audit | signed off 16:26 (chance_ok) | engine at `bd967042` (the engine tree never changed after `07f8aa8`) |
| Dry run, gate 3, gate 4b (both runs), gate 4c | 17:17-21:20 | `bd967042` |
| freeze8 check, GATE5 PASS | 21:24 | `bd967042` and the tag `7b14546f` |

**Notes on these commits:**
- From Part B on, every gate used the pinned binaries: deckgym `e6a8bf76…` and protocol_bot `d3a976cc…`. Freeze8 checks them, and Part B's B0 step checked them too.
- Between `1d209a6` and `bd967042`, only these files changed: FROZEN8.draft.json, freeze8.py, game_bot.py and their tests. Gate 4a doesn't run game_bot.py.
- Gate 4a's process loaded its code at 08:27Z, before those commits.
- The laptop result notes behind the earlier gates are 079-086. Section 6's heading "laptop notes 082-086" should read 079-086.

## 2. Gate 4b's second dev run (the "forced" run)

The chain log shows gate 4b as INCOMPLETE on the dry run, then a PASS on a second run. Here is why that is the registered procedure, not a re-run to get past a gate.

- **Why the first run was incomplete:** gate 4b compares kx3 as the shadow against fresh kx3 at setup points and at fallback points. The dry run's random mock judge never triggered a fallback, so the dry run had 0 fallback points. With nothing to sample, the fallback half was INCOMPLETE. Its setup half passed: 20 of 20 equal.
- **The second run was planned in advance.** The brief said gate 4b runs on a mock dev run. The first gate chain (`gate_chain.sh`, started 08:37:48Z, before any dry run) already held the step: "if INCOMPLETE for want of fallback records, a forced dev run (k 97-99 x 16, --force-fallback-every 4) and gate4-shadow on that". The restarted chain (`gate_chain2.sh`, 15:59:57Z) kept the step unchanged.
- **What the second run is:** a dev run at k 97-99, mock seed 12, in which every 4th intervention point becomes a fallback, marked `forced_dev`.
- **It can never become a scored run:**
  - The runner refuses this flag at stage 1, at stage 2 and in live mode (`game_runner.py` lines 635 and 641).
  - Gate 3 fails any `forced_dev` fallback (`game_gates.py` line 709). Gate 3 ran on the dry run only.
  - Both dev runs use k 90-99, which no stage ever scores.

## 3. Notes not copied in section 3, and the rules they hold

Section 3 copies notes 095, 096, 103, 105, 106, 108, 109, 110 and 112. The other notes from this period are 097-102, 104, 107 and 111.
- Their decisions about the experiment are below, quoted verbatim where they bind.
- Notes 101, 102 and 104 are not in the mailbox folder.
- The quotes below leave out lines that don't bind the test; each gap is marked […].
- Note 104's decision is deviation 4. Coordinator-105 (section 3) records it: "075 (its label fix was approved in 104)", and "1. **Deviations 4 and 5: approved as extended.**".
- Note 097 (an R8 shot list) and note 107 (the Part B restart, its test L9 rule and its $8.40 cap) set the build process, not the test.

**Coordinator-098 (Dustin's go), verbatim:**

> **Dustin, ~23:28Z (verbatim):** "Yes, go ahead"
>
> He answered my question "Go ahead with the Gemini test's build and trial games?" That message stated:
> - the build at up to $15 of Claude credits;
> - up to 16 trial games at up to $15 of Google credits;
> - your default decks if he named none: Mega Manectric/Heliolisk and Archaludon/Haxorus.
>
> **What his go covers, nothing more:**
> 1. **The START_HERE seed row first:** 25,103,000,000-25,103,001,599, a small commit on main with his verbatim go in the body. Guardrail A (grep -a). Send me the hash.
> 2. **The build job on Claude API credits, cap $15:** stream-json, the containment grep (with the additions in §7), and actual total_cost_usd logged.
>    - Then your review, and the gates (§2: 1-6). Any gate failure = STOP and report.
> 3. **Freeze frozen-8,** recorded before stage 1.
> 4. **Stage 1:** up to 16 unscored deals, Google cap $15, under 096's rule (with ≥ 6 complete deals, the data goes to Dustin and me; with fewer, STOP).
> 5. **Pilot decks:** 09-mega-manectric-heliolisk (fast) and 11-archaludon-haxorus-dragonair (setup), as he didn't name others. **Opponents:** t-lucario and t-suicune.
>
> **NOT covered: stage 2.** Its ledger is his separate decision, after stage 1's cost data.

The seed row is commit `84dc7f17` on main (coordinator-099).

**Coordinator-099 (what the build may read; where frozen-8 lives), verbatim:**

> **Blocker 1: yes. The build job and your review may read `rl/ai_judge/**` at tag `judge-prompt-frozen-7` (712593a1).**
> […]
> - **Keep your exclusions anyway:** the exam branch, rl/results/weekly_review*, k21_run, exam_v2, and any path named exam, answers, questions, references, labels, D_FIXES or assembly*. Also treat `rl/ai_judge/runs/` as excluded, which your "run*" already covers. Read nothing outside rl/ai_judge/** at the tag, and engine/ at e36452d3.
> - The build job's containment grep adds these exclusions as STOP words, as §7 says.
>
> **frozen-8's home: a new branch `laptop/gemini-game-test-2026-10-30`, based on the ADAPTER TIP 2639a261, not on the frozen-7 tag.**
> […]
>
> **The order: approved as you proposed (1-6).** Stage 1 may run beside R8 writing workflows, but never beside cargo.

**Coordinator-100 (the two files the gates may also read), verbatim:**

> 1. **The ask: yes.** The build job and the gates may read exactly two files beyond rl/ai_judge/** and engine/:
>    - stage A's v2 position file (the 92) under rl/results/pause_games_new_2026-10-13/v2/;
>    - the diagnostic's 14.
>    […]
>    - **Conditions:**
>      - Use the exact versions frozen-7 used. Match each file's sha256 to what FROZEN.json, the README or results_old_positions records. If no record names them, take them from the commit the frozen-7 tag points at.
>      - If the hashes don't match, STOP and tell me. Don't substitute the later positions v3 fixes.
>      […]

**Coordinator-111 (the push), verbatim:**

> **Decision 4: yes, push the tag `judge-prompt-frozen-8` together with the branch.**
> - The tag is the point. It marks what was registered before any outcome exists.
> - Run lap4_final.sh, then lap4_push.sh, exactly as described: Guardrail A first, stop on any key-shaped string in new content, the branch plus the tag only, never main, nothing upstream, then disable the remote again.
> - Report the pushed tag's commit and the branch tip in 088 before stage 1 starts.

## 4. Smaller corrections

- **Section 1, the three bullets under Dustin's quote:** they are coordinator-112's reading of his words, which section 3 copies in full. Dustin's own words are only the quoted sentence.
- **Deviation 7, "fires at the 76th decision point":** this means the rule in the frozen kit, `game_kit.py` line 16: "fallback (d) fires at the first intervention point after the 75th judge decision; earlier fallbacks do not count toward the 75". The code governs.
- **`rl/ai_judge/FROZEN8.draft.json`:** this is the superseded draft (commit `b19b3f8`, GATE5 DRAFT). Its source hashes are stale. The record is `FROZEN8.json`.
- **Stage 1's run conditions, which bear on its time data:**
  - 8 Rayon threads, as in the kit;
  - one game at a time;
  - never beside cargo.
  - Stage 1 may run beside R8 writing workflows (coordinator-099). Each figure for the seconds a game took carries that condition.
