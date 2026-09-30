# Engine switch plan: put kta and km into the official engine (Sept 30, for Dustin's decision)

## In one paragraph

The switch makes the official program carry the adopted kog-based kta3 and km3, so the screen and the floor can use them. It changes only the players code. The game rules stay exactly as they are today. The laptop builds the programs and replays about 110,000 games (about 3.5 hours; about 4.3 hours with the suggested extra checks) to prove kta3 and km3 play exactly the games already on record. Then, with your word, the laptop pins the new programs and moves the screen and floor default from kog3 to km3. Finally it re-runs the floor's pre-use check under km3, about 1 hour more. I recommend keeping every pending rules item out of this switch.

## What the switch is

- **Engine:** today's main plus B's players code. B is km's build, 1f6319e.
  - In practice: merge the cloud branch head 53fc5a1 into main. Checked today after a fetch: main is 9dda21a, and the merge has no conflicts.
  - The merged `engine/` must equal B's exactly (tree 9c84fef). That tree is the byte check.
- **Players-only: yes.** Against today's official engine, only three files in `engine/src/players/` change (+793/−40). The rules code is the same as 233bced's, which is what the official engine was built from.
- **What the new program carries:**
  - k3, kp3 and kog3, unchanged.
  - `kta<N>`: ec7e1a8's kog-based kta.
  - `km<N>`: kta plus N2, the Stadium bonus in the clock.
- **Name change to know about:** in today's official program, kt3, kta3, ktb3 and ktc3 are the old kp-based presets. After the switch they are kog-based.
  - The old kp-based records (`kt_2026-09-26/identity/43cef0b_*`) can still be replayed on the kept `rl/engine-2026-09-28/` programs. Those programs are never overwritten.
- **Steps this skips, because it is players-only:**
  - the repair mechanic check;
  - the refactor check;
  - new frozen k3 and kp3 tables (the frozen table stays as long as k3 and kp3 replay identically);
  - the "first replay on ec7e1a8's rules" step.
  - All four come back if any rules item is bundled in.

## The laptop's steps, in order

Times use about 8.6 games per second. The plain codes (k3, kp3, kog3) ran faster at the Sept 28 pin: 42,000 games in 29 minutes. So treat these times as upper bounds. Run steps 1-4 at home or overnight, not during class or travel.

**Before your word** (preparation only; nothing is pinned):

| # | Step | Games | Time | Evidence |
|---|---|---:|---|---|
| 1 | **Build** `deckgym`, `legality_scan` and `goldfish` from one `git archive` of the merge candidate. (The laptop's current km build has no goldfish.) | none | ~30 min | three sha256 in a new PIN_STATUS.txt |
| 2 | **Identity: kta3 on fresh deals** against ec7e1a8's committed fresh games (`fresh_table28.tsv` from 23,000,000,000; `fresh_new_decks.tsv` from 23,001,000,000). This comes first because it is the only replay never played at B. | 22,500 | ~45 min | `identity_check.txt`: one line per file, n of n |
| 3 | **Identity: kta3 on dev deals** against `ec7e1a8_kta3_table.jsonl` and `_new17.jsonl` | 22,500 | ~45 min | same |
| 4 | **Identity: km3** against B's committed `1f6319e_km3_table.jsonl` and `_new17.jsonl` | 22,500 | ~45 min | same |
| 5 | **Identity: k3, kp3, kog3** on the full table (the Sept 28 references) | 42,000 | ~1 h 20 min (Sept 28 took 29 min) | same, plus `pin_identity.txt` |
| 6 | **Suggested extras** (not gates, reported beside): kq3 table, kog3 new17, kd3, kpr3 | 24,740 | ~50 min | same |
| 7 | **Command line and goldfish.** `deckgym simulate` 240 games: k3, kp3 and kog3 must repeat the Sept 28 lines (150/90/0, 144/96/0, 149/91/0), and kta3 and km3 must run clean. `goldfish --coverage` must run; diff it against the Sept 28 file. Suggested: `run_screen.py` under kog3 on brew-06 and 06b must equal `floor_recheck_2026-09-28/run_screen.txt`, because the screen uses `simulate`, not `legality_scan`. | ~5,000 | ~15 min | PIN_STATUS lines, then **PREPARE DONE** |

- **Every replay:** matched by (pairing, game number), with counts asserted. It compares moves, decisions, openings, winner seat, points, seed, both bots, both decks and first seat.
- **Totals:**
  - required steps 2-5: 109,500 games, about 3.5 hours;
  - with step 6: 134,240 games, about 4.3 hours;
  - build and step 7 included, about 5 hours of laptop time.
- **Test suite:** not required for a players-only change. The cloud already passed 1,991 with 0 failed at B. If you want it anyway, it takes about 20 minutes.
- **A stop:** any mismatch stops the switch. The manifest stays untouched, and the laptop reports to you first (the Sept 25 rule). Because only players code changes, a mismatch can only be a build or script problem. It can never be blamed on a rules change.

**After your word** (one commit, as 33f56da did on Sept 28; no games):

| # | Step | Evidence |
|---|---|---|
| 8 | Merge 53fc5a1 into main with `--no-ff`. Confirm `engine/` is tree 9c84fef, and that nothing outside `rl/results/` changed except the three players files. This also brings the cloud's build and identity records onto main (`km_build_2026-09-29/`, `-09-30/`, `kt_kog_2026-09-28/`). | merge commit, tree check line |
| 9 | Pin: copy the three programs into a new `rl/engine-<date>/` with `SHA256SUMS`. In the manifest, the current release moves to history as "superseded". The new entry's purpose says: kta = ec7e1a8's kog-based kta; km = kta + N2; kt3, ktb3 and ktc3 carry no identity claim. `current_engine.py` needs no change. | manifest entry, SHA256SUMS |
| 10 | Screen and floor defaults move from kog3 to km3 (`run_screen.py` and `floor.py` together). **Fix the pricing-pilot pattern** in `floor.py`:77: today it does not match kta3 or km3, so the floor would silently mark the 62 audited cards as unpriced. | the diff, plus a small pattern test |
| 11 | Documents: the engine README, the switch README and PIN_STATUS, START_HERE's engine line, CLAUDE.md, and RUN5 (the "stay on kog3 until the switch" lines at :379 and :383, and A5 at :424) | the commit |

**After the pin** (Sept 28 precedent):

| # | Step | Games | Time | Evidence |
|---|---|---:|---|---|
| 12 | **Floor pre-use re-check under km3.** The plan is committed before any game. brew-06 and brew-06b must read "fail" with km3 on both sides. The deck 14 control under k3 must read "untrusted". `run_screen` at 240 games must give exactly the floor's wins. brew-05b and deck 07 are reported beside. | ~13,400 | 30-60 min | `floor_recheck_<date>/README.md` with verdicts |

If step 12 fails, the floor isn't used until you have seen the pages (the Sept 28 rule).

## What the cloud can do in parallel (small jobs only)

These come after, or beside, its Altaria–Suicune diagnosis. Each takes under an hour. Neither counts as the pin's evidence: that has to come from the programs being pinned, which are the laptop's.

1. **Early warning on the one untested replay.** Using the cloud's existing build of B, replay a slice of kta3 on the fresh deals: the first 40 games of each of the 45 fresh pairings, 1,800 games. Compare them game for game with ec7e1a8's committed fresh files. If this fails, we learn it before the laptop spends hours.
2. **Draft the `floor.py` pattern fix, with a tiny test.** The test lists every code B builds as a public-pricing player (`players/mod.rs`:668-708 at 1f6319e). It checks that the pattern matches all of them and does not match k3. The cloud sends it as a patch, and local Opus puts it into the pin commit.

Also tell Sonnet's calibration task: the calibration refuses to run when the screen and the floor name different pilots, and both change in step 10.

## Default pilot: km3, and why

- **km3 is the working pilot in the tables** (km READING; RUN5:380).
- **The Sept 28 switch set the precedent.** It moved the screen and floor to the tables' working pilot, kog3, in the pin commit. Doing the same now keeps one pilot across the tables, the screen and the floor.
- **The difference from kta3 is narrow.** km3 is kta3 plus the Stadium bonus in the clock, and nothing else.
- **The caveat.** km's gain is tentative: adopted "unconfirmed", Lucario +0.444 with a lower edge of only +0.026, and Training Area's predicted pattern didn't appear.
  - If the post-freeze confirmation drops km, the default goes back to kta3. The switch carries and verifies kta3 anyway, so that is a two-line change plus another floor re-check.
- **The alternative is kta3.** It keeps the screen off the tentative N2, but then the screen and the tables would use different pilots. I don't recommend it.

## What needs your word

1. **The switch itself (the pin).** A conditional go works, as on Sept 25: proceed if the preparation passes; a failed replay leaves the manifest untouched and comes to you first. Preparation (steps 1-7) pins nothing, and the Sept 30 note you pasted already gives it to local Opus.
2. **Rules items: keep them out (recommended).** This covers Victory Star/Confusion, upstream 09e964f, PR #383 and the B4b card data.
   - **No gain.** None of the affected cards is in any deck under `decks/`, so no table, screen or floor game would change.
   - **Real cost.** Any of them would add a second build and a two-step replay, the mechanic check, and new frozen k3 and kp3 tables. They would also put kta3 and km3 on a different engine from their recorded evidence.
   - **Not ready anyway.** 09e964f isn't a clean pick (it brings observation and serde changes). The Victory Star repair isn't written yet. B4b is already pinned to Mega Garchomp ex's release.
   - Each of them goes in a later switch, under the full procedure.
3. **The default pilot:** km3 (recommended) or kta3.
4. **The floor re-check under the new pilot (step 12):** recommended, about 1 hour.
5. **kt3, ktb3 and ktc3.** Recommended: keep them as B defines them and label them "diagnostic, no identity claim, never adopted". Removing them would break B's tests. Giving them an identity claim would cost about 67,500 more games (about 2.2 hours); it is optional.

Not part of this plan: the one-line confirmation of your km "go ahead" reading (c74d8df) closes that record separately.

## Risks

- **The fresh kta3 replay has never been played at B.** It is the one real unknown. The cloud slice gives early warning, and a mismatch stops the switch.
- **The kt-family names change meaning in the official program.** After the switch, anyone who passes `--pilot kta3` (or kt3, ktb3, ktc3) to `trace_pilot.py`, `run_screen.py`, `floor.py` or `candidate_run.py` gets the kog-based version, which is the intended one. The documents must say so, and the old programs stay for replaying the kp-based records.
- **The `floor.py` pattern.** If it is missed, nothing crashes; the floor just flags the wrong cards and can give a wrong "untrusted". It has to go in the pin commit, with its test.
- **Screen, floor and calibration must change together,** or the calibration refuses to run.
- **The default rests on an "unconfirmed" adoption.** The fallback is kta3, as above.
- **Script slips.** The Sept 28 pin stopped once on an unquoted path with spaces. This repo's path has spaces too.
- **The merge brings 68 branch commits onto main.** Step 8 checks that nothing outside `rl/results/` and the three players files comes with them.
- **Laptop time and heat.** About 5 hours of play before the pin, and about 1 hour after it. Run at home or overnight.
- **This switch doesn't clear the pending rules items.** The next switch (the upstream merge with 09e964f, or B4b at the Garchomp release) still needs the full procedure, including new frozen tables.
