Decision this informs: the composition check for the one pilot Dustin ruled on Sept 27 (kp3 + koa's opening + kpg's discard credit; `rl/RUN5.md` "Rules", composing candidates). The laptop runs the composition table on the 45 cells with its mixed rows; this note records the build it reads and the identity checks that make the composition. Build commit BUILD_COMMIT, scan sha256 SCAN_SHA.

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
