# The Gemini finished-game test: stage 2 results

Written on 2026-11-01, after stage 2 ended (128 of 128 deals, 09:29:03Z). The test is registered in `../GEMINI_GAME_TEST_REGISTRATION.md` (tag `judge-prompt-frozen-8`), with `../GEMINI_GAME_TEST_REGISTRATION_ERRATA.md` and `../GEMINI_GAME_TEST_REGISTRATION_ADDENDUM_STAGE2.md`. This file and the outputs beside it were added afterwards. Nothing in the registration, FROZEN8.json, the errata or the addendum was changed. The section order was set by the coordinator (note 117). The registered result report, coordinator note laptop-091, carried the power line in its first paragraph.

## Conditions
- **Bots only.** The opponents are bots. Nothing here measures play against people.
- **Engine:** the pre-R8 adapter build, engine tree 34fef9e5 (e36452d3 plus kx3's six files). It is not main and not the R8 engine. Per registration §2, a PASS carries over to R8 only after §2's gates are repeated there.
- **The cells:**
  - 2 of Dustin's decks: 09-mega-manectric-heliolisk and 11-archaludon-haxorus-dragonair;
  - × 2 opponent lists: t-lucario and t-suicune;
  - × 2 opponent policies: km3 and kx3;
  - × both seats.
  - That makes 16 cells × k 0-7 = 128 deals, 8 per cell.
- **The two arms, played on the same deal** (same game seed, same decks, same seats):
  - **(G):** the frozen-8 Gemini plan judge (gemini-4-argon on Vertex AI) chose at every own-turn and opponent-turn intervention point: 1,166 + 112 = 1,278 points. The shadow kx3 took the 8 fallback points;
  - **(K):** kx3 alone.
- **Setup was kx3's in both arms.** The 92 setup decisions, in 41 G games, drew no judge call (`setup_check.txt`).
- **What each player knew:** kx3 and the shadow kx3 played with the opponent-list knowledge (poolmeta). The judge saw only the observation.

## The label and the numbers
**Registered label: PASS / judge higher** (registration §6, rule 4: CI low > 0, two-sided sign-flip p < 0.05, and both per-policy means > 0).

| | |
|---|---|
| (G) wins | 73 of 128 |
| (K) wins | 56 of 128 |
| pairs: Gemini-only win / kx3-only win / same result | 30 / 13 / 85 |
| mean pair score (G − K) | +0.1328 |
| 95% CI (percentile bootstrap within the 16 cells, 10,000 draws, kit seed) | [+0.0391, +0.2266] |
| two-sided sign-flip p (Monte Carlo, 100,000 draws, kit seed) | 0.01372 |
| per-policy means (64 pairs each) | km3 +0.1406, kx3 +0.1250 |
| fallback rate (setup excluded) | 8 / 1,278 = 0.0063 |
| dropped pairs, failures, infra replays, ties | 0, 0, 0, 0 |

- **No turn limit was hit:** the highest final turn is 17.
- **Fallback reasons:** 7 expansion-bar, 1 no usable answer. That one call drew only two rate-limit (HTTP 429) replies. Counting all 92 setup decisions as non-judge points would give 100 / 1,370 = 0.073, still under the 10% limit.

## The power line
At N = 128 the test had 80% power for a true gain of about +0.175 (two-sided 5%, win rates near 0.5, no pairing gain assumed). A much smaller real gain would usually read "inconclusive"; under that assumption, power at a true +0.10 is about 36%.

The observed +0.133 is an estimate, not the size of the gain. The power line is the true gain the test catches 4 times in 5. It is not the smallest result that passes. Without the pairing, the observed result would have passed only just: with the ~65 discordant pairs expected for independent arms, a sum of +17 gives p ≈ 0.047. The arms agreed on 85 of 128 deals (pair correlation 0.352), which brought p to 0.014.

## What it does not show
- The size of the gain. Anything from about +0.04 to +0.23 is not ruled out.
- Other decks, other opponent lists, or the R8 engine.
- Play against people, or strength on the ladder.

## Descriptive only (registration §6: noisy, not a test)
These are differences between the two pilots on the same deals. They are not a measure of how strong any deck or list is.

| split | pairs | Gemini-only wins | kx3-only wins | same result | mean D |
|---|---|---|---|---|---|
| deck 09-mega-manectric-heliolisk | 64 | 10 | 9 | 45 | +0.016 |
| deck 11-archaludon-haxorus-dragonair | 64 | 20 | 4 | 40 | +0.250 |
| list t-lucario | 64 | 14 | 8 | 42 | +0.094 |
| list t-suicune | 64 | 16 | 5 | 43 | +0.172 |
| pilot in seat 0 | 64 | 15 | 7 | 42 | +0.125 |
| pilot in seat 1 | 64 | 15 | 6 | 43 | +0.141 |
| pilot went first | 47 | 15 | 3 | 29 | +0.255 |
| pilot went second | 81 | 15 | 10 | 56 | +0.062 |

- **The first-player caveat:** the pilot went first in only 47 of 128 deals. That is 3.0 SD under a fair 64 (exact two-sided binomial p ≈ 0.003).
  - The field (the runner's `went_first_of()`, from turn parity) fits every game's end. In 128/128 G games and 128/128 K games, the winner owns the final turn (`parity.txt`). So G and K had the same first player in every deal, and the imbalance can't by itself make a G − K gap.
  - Why the engine's draw is lopsided has not been checked. Reweighted to 64/64 first/second, the mean D would be about +0.16.
- **Game length (G):** mean final turn 9.3, mean 67.7 plies.
- **Re-asks:** chance 1,097, own draw 175, after a fallback 6.

## Checks
- **Gate 6 self-test:** GATE6 PASS right before scoring, at commit c1e5642e, in a clean clone (`selftest.txt`, `score.log`, `score_stage2.sh`). The inputs' sha256 are in `inputs.sha256`.
- **Independent recompute:** separate code, sharing no functions with `game_analysis.py` (`indep_check.py`, `indep.txt`).
  - It agrees exactly on the scored and dropped counts, the mean, the policy means, the fallback rate and the label.
  - It agrees on p and the CI within its stated tolerances (p within 0.005, CI ends within 0.02):
    - an exact binomial sign-flip p of 0.013718;
    - its own bootstrap, [+0.0469, +0.2266]. The low end is one 1/128 step from the kit's.
- **Integrity over all 256 arm rows** (`integrity.txt`, `integrity2.txt`, `parity.txt`, `setup_check.txt`):
  - `integrity.txt`'s first pass ended "INTEGRITY PROBLEMS" because the whole-matchup record differs between G and K. `integrity2.txt` shows that the only differing key is player_codes, i.e. the pilot program, as designed.
  - The pilot's seat equals the cell's seat bit.
  - The outcome equals state_winner.
  - Seeds follow the registered formula and are the same in G and K.
  - Every played 20-card list equals its registered deck file (512 of 512).
  - The model returned gemini-4-argon on all 128 G rows. mock is false.
- **Review:** before the result was reported, three read-only review rounds checked the score, the data and the report: wf_820d64b6-b7e, wf_f1aa5ab6-902, and a final one-reviewer pass, wf_00547e0f-241. A fourth, wf_69ece3f3-790, checked this write-up before the commit. None changed a number.

## Cost and time
- **Google, stage 2:** about $63.36, from token counts at $2/$10 per M tokens. This is an estimate, not billing.
  - The ledger shows $64.78 of $127. The difference is two failed tries, each charged at its worst case. They were transport errors in deals 19 and 127, and both were retried successfully.
  - Per G game: mean $0.495, max $2.009.
  - Calls: 1,271 (mean 9.9 per game, max 20, cap 45).
- **Time:** 30 h 38 m wall time. G games took 84,966 s and K games 25,322 s. There were no pauses.
- **The whole test:** Google about $71 (stage 1 $7.59 + stage 2), and $11.77 of Claude credits for the build.

## Trail
- **The missing notes, now filed:** the errata says coordinator notes 101, 102 and 104 are not in the mailbox. They were direct messages. On 2026-11-01 the coordinator filed all three as verbatim records from its transcript: `laptop__20261029T2330Z-coordinator-101.md`, `laptop__20261029T2332Z-coordinator-102.md` and `laptop__20261030T0037Z-coordinator-104.md`. The mailbox is not in this repository. Note 104 is deviation 4's approval; its text, verbatim:

  > coordinator-104 (short; no mailbox file): RELATIVE player numbers in labels are accepted (the actor is 0, the opponent 1, inside Name#{json} too); the action sent to the engine keeps its real seat. It restores exactly frozen-7's meaning ("mover at index 0"), with judge.py and fingerprint 0cb24215 unchanged and seat 0 byte-identical.
  > Conditions:
  > - Test L10 plus the no-Google gate on ≥ 8 seat-1 states: the "player on the move" line is present and every label number satisfies action seat == actor ? 0 : 1. STOP on a mismatch.
  > - Include at least 2 opponent-turn intervention states, e.g. choosing a new Active after a knockout, where the actor isn't the turn player.
  > - Record it in FROZEN-8 and the deviations list as "label seat numbers made relative to the actor, to match frozen-7's mover-at-0 convention".
  > Then v2 to me.

- **How the stage-2 numbers were set:** Dustin picked stage 2's $127 ledger and N = 128 from options written by the running agent. The options he picked, for the ledger and for the schedule, were the ones it had marked "(Recommended)". The addendum's §1 quotes, verbatim, the questions, his answers and the text of the options he picked.

## Files here
- `analysis.json`: the registered analysis output (`game_analysis.py` at c1e5642e), unchanged (sha256 f950ec34…). Its `fallbacks_per_game` list gives fallback counts per deal. It has no per-deal outcomes.
- `selftest.txt`, `score.log`, `inputs.sha256`, `score_stage2.sh`: gate 6 and the scoring run.
- `indep.txt` + `indep_check.py`: the independent recompute. Its per-split win counts are descriptive too. They come from bot games on this engine, not from any measure of deck strength.
- `integrity.txt` + `integrity_check.py`, `integrity2.txt` + `integrity2.py`, `parity.txt` + `parity_check.sh`, `setup_check.txt` + `setup_check.sh`: the integrity checks.
- `splits.txt` + `splits.sh`: the paired descriptive splits above.

Per-deal result files, prompts, model replies and stderr are not included.
