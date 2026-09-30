# Cloud Opus status (branch claude/pensive-ptolemy-spwc0b)

Written Sept 30 for the Fable coordinator session (Dustin's single delegator). Times are UTC.

1. **Current task, and the instruction that set it.** None. The last one is done: the km3 unplayed-Trainer diagnosis (the Fable coordinator via Dustin, Sept 30), commit 3c5221e, rl/results/trainer_unplayed_diag_2026-09-30/README.md. Nothing gates on it.
   - **Iris (deck 11): km3 plays it exactly when it matters.**
     - Its effect adds 0 to the score; km3 sees it only when its three-move search reaches a Haxorus knockout in the same turn.
     - In the 40 replayed games it played Iris on all 3 turns where Iris made the winning third point.
     - Of the 83 turns it held Iris back, 78 had no Haxorus in play, and on none of them would Iris have added a point that mattered.
     - The low rate is how seldom Haxorus attacks.
   - **Team Rocket's Goo-zooka (decks 14, 15): km3's score never sees it.**
     - Its effect adds exactly 0 on all 147 chance turns: there's no term for the opponent's Retreat Cost, and the search stops when the turn ends. So the card is worth −1, a card leaving the hand, and km3 keeps it.
     - In 10 hand-picked turns where it wasn't played, 7 would have been worth playing: after Sabrina, or when the opponent's Active had exactly its Retreat Cost in Energy and retreated the next turn.
     - This agrees with the Trainer census.
   - **Checks:** all 80 replays match the floor's games and its chance counts. km3's played move had the best root score at all 844 probed decisions.
   - No engine change, no players/ change, no table games, no candidate proposed.
2. **What is running now, and when it ends.** Nothing.
3. **Files I expect to change.** None. The diagnosis changed only its new folder and this file.
4. **Waiting on the laptop or Sonnet.** Nothing.
5. **Open questions for Dustin.** None.

## Log (one line per new job, added and pushed before it starts)

- 2026-09-30: km Altaria v Suicune diagnosis (the laptop's request via Dustin): 40 traced deals at B, no new table games.
- 2026-09-30: Victory Star / Confusion repair draft (Fable via Dustin): failing test, then the gated fix, then the unit suite; engine/src/actions/ two files plus rl/results/victory_star_repair_2026-09-30/. No games.
- 2026-09-30: coin-flip damage prevention repair draft (Fable via Dustin): Part 1, a read-only check of the seven helpers (HELPERS.md, committed first); Part 2, (a) partial cuts after Weakness and Bounded Field and (b) the coin on queued direct damage, failing fixtures first. engine/ plus rl/results/coin_prevention_repair_2026-09-30/. No table games.
- 2026-09-30: Chase Order follow-up to the coin-flip prevention draft (Fable via Dustin): failing tests first (no discard, discard, control), then the gated fix in apply_attack_action.rs and apply_action.rs, then the unit suite and the README. No table games.
- 2026-09-30: Sonnet's follow-ups S1-S4 (Fable via Dustin): with_heads_coin_cuts test and hardening, Wild Swing and Ability/Tool/Checkup pins, smoke rerun on e52a73b with a trace of 4 games. Scratch decks only, no table games.
- 2026-09-30: km3 unplayed-Trainer diagnosis (Fable via Dustin): Iris (deck 11) and Team Rocket's Goo-zooka (decks 14, 15) from the floor run; at most 40 replayed deals per card at the official engine; diagnosis only, no table games.
