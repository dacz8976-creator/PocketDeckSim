Decision this informs: the composition check for the one pilot Dustin ruled on Sept 27 (kp3 + koa's opening + kpg's discard credit; `rl/RUN5.md` "Rules", composing candidates). The laptop runs the composition table on the 45 cells with its mixed rows; this note records the build it reads and the identity checks that make the composition. Build commit a823b6d (`cargo build --release --example legality_scan`; the `--pairs` option is in it), scan sha256 1fbf36060fbd88e9166ced52364df7cdd556fb10644a82ae001fcf1cfdb1716c.

Seeds: the table's deals only (72,000,000 + pairing × 10,000 + i, even i = first-named deck in seat 0).

# kog: kp + koa's switch A + kpg's F (build, Sept 27)

## What was built

- **`kog<N>`** = kp<N> with two `EvalFeatures` flags on, each exactly as its own code sets it:
  - `opening_first_turn_active`: koa's switch A, read only in the setup evaluation (`opening_class::opening_active_term`);
  - `fuel_credit`: kpg's part F, read only after setup. It is the credit as built for kpf/kpg, with the second read's fix (an Ability's holder is never its own target) and Dustin's Sada rule (one Energy of each different type, up to 3).
  - No other change. It is not a new candidate: each part keeps its own verdict and evidence (koa's reading, kpg's registration), and the pilot inherits both.
- **Why the two compose cleanly.** The setup evaluation returns before F is added, and switch A is read only there. So kog's value is koa's while the opponent's setup is masked, and kpg's everywhere else. A test checks this on each player's own view over 12 random games.
- **The name.** "kog" is koa's opening plus kpg's credit. It is parsed with koa, kob and kor, before `k<N>`. No existing code starts with "ko" except those three, and they are unchanged. Tests: kog3 and KOG5 parse; kog and kogx are rejected; koa3, kob3, kor3, kpg3 and kpf3 parse as before.
- **The build also carries kt's code** (on this branch since 43cef0b; `../kt_2026-09-26/BUILD.md`). kt's code runs only for the kt codes. Its shared refactors are checked by kt's identity runs and, for this build, by the k3 and kp3 replays below.

## Where each part can act on the table

- **Switch A** acts in Altaria's games: koa's reading measured a 6.06% footprint, all through Altaria's opening.
- **F** needs a recovery source. Of the eight table lists only Blaziken's carries one (2 Flame Patch B1 217). The opponent's side counts only a source visible in play, and Flame Patch is a Trainer, so F acts only on Blaziken's own side, in Blaziken's 7 pairings.
- **Both** can act only in Altaria v Blaziken.

## Tests

- `kog_tests::kog_is_koa_in_setup_and_kpg_after_it`: the flags (switch A and F on, everything else off), and on every position of 12 random games (Altaria v Blaziken, Blaziken v Suicune, Altaria v Lucario), from each player's own view, kog's value equals koa's where the opponent's setup is masked and kpg's everywhere else.
- The parser tests above.
- **Full suite:** 1,964 passed, 0 failed.

## Identity: the composition proof (all at a823b6d; `compose.py`, `composition_check.txt`)

**Every check passes.** The references are the official engine's tables: `../koa_2026-09-26/reading/table_koa3.jsonl`, `../kpf_2026-09-26/reading/table_kpg3.jsonl`, and kp3's and k3's `../rules09_fixes_2026-09-26/af8489f_*_500.jsonl`. A game is equal when its moves, choices, openings and result all are.

| check | result |
|---|---|
| kog3 on all 14,000 table games | clean (no rule findings) |
| 1. Games in the 21 pairings with no recovery source for F: kog3 = koa3 | 10,500 of 10,500 |
| 2. Games where koa3 = kp3 (switch A changed nothing): kog3 = kpg3 | 13,152 of 13,152 |
| 3. Games equal to neither koa3 nor kpg3 | 10, all Altaria v Blaziken; each needs both switches (below) |
| 4. k3 at the kog build vs the official reference, all 500 deals | 14,000 of 14,000; clean |
| 4. kp3 at the kog build vs the official reference, all 500 deals | 14,000 of 14,000; clean |
| koa3 and kpg3 at the kog build vs the official tables, first 40 deals | 1,120 of 1,120 each; clean |

**Check 3, the 10 games** (seeds 72,000,015, 068, 139, 180, 217, 228, 253, 354, 389, 422). The logic: kog and koa3 share the setup evaluation and differ only after setup (F); kog and kpg3 differ only in setup (switch A). So a game equal to neither was changed by both.
- The data agree. In all 10, kog3's openings equal koa3's (Altaria opens with Eevee, B1 184) and differ from kpg3's.
- `first_divergence.rs` (a watch-only example; `check3_traces.txt`) replays each game under kog3, koa3 and kpg3 and finds the first differing choice. Every replay reproduces the table game exactly (20 of 20 fingerprints).
  - **Against kpg3:** the first difference is Altaria's setup placement in 10 of 10. That is switch A.
  - **Against koa3:** the first difference is a later Blaziken choice, on turns 4 to 9, in 10 of 10. That is F.
    - Blaziken has a Flame Patch in hand or deck in all 10, and a Fire in the discard pile in 9. kog3 attaches or attacks where koa3 plays Flame Patch.
    - In the tenth the discard pile is empty at that choice, so F acts only through the search's lookahead (Energy reaching the discard within the turn).
- For information: in 4 of the 10, F also changes kp3's own game (kpg3 ≠ kp3). In the other 6 it changes only the game koa's opening led to.

**By cell** (`composition_check.txt`):
- Pairings with neither Altaria nor Blaziken: kog3 = koa3 = kpg3 in every game.
- Altaria v X: kog3 = koa3 in all 500.
- Blaziken v X: kog3 = kpg3 in all 500.
- Altaria v Blaziken: 447 = koa3, 391 = kpg3, 348 both, 10 neither.

## Files

- `compose.py`, `composition_check.txt`, `first_divergence.rs`, `check3_traces.txt`, `run_identity.sh`, `timing.txt`.
- The raw outputs: `a823b6d_kog3_500`, `a823b6d_{k3,kp3}_500`, `a823b6d_{koa3,kpg3}_40` (`.jsonl` and `.txt`).
- The laptop's composition table (the 45 cells with mixed rows; no veto, and accuracy no worse than the better component) is next.
