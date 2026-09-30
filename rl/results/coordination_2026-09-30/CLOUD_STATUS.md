# Cloud Opus status (branch claude/pensive-ptolemy-spwc0b)

Written Sept 30 for the Fable coordinator session (Dustin's single delegator). Times are UTC.

1. **Current task, and the instruction that set it.** None. The last one is done: the carrier lists for the rules switch (PLAN.md step 3; the Fable coordinator via Dustin, Sept 30), commit e0d149a, rl/results/engine_switch_rules_2026-10/carriers/README.md.
   - **By the rule** (decklist_sources.json's, keyed by deck id: development events, top 8, most frequent exact list), only Garchomp Meowth has a list: shaquill10, 5th of 95, 2026-09-18.
   - **Togekiss Meowth, Hisuian Goodra and Mega Houndoom ex Victini have no top-8 development list,** so none by the rule.
   - **The plan's fallback:** fire_victini.txt (repair A) and coinflip_deck.txt (Meowth B2 204). No fallback carries Togekiss A4 080 or Hisuian Goodra.
   - **Alternates, not by the rule** (the same rule without the placing filter), for the coordinator's choice: Togekiss Meowth 19th of 118 (5-3-0); Hisuian Goodra (0-3-0, dropped); Houndoom Victini (0-1-0, dropped).
   - **Card checks** on the official programs:
     - every id is one printing, and there is no B4b card;
     - the validator is clean. The upstream coinflip_deck.txt fails on three unpadded ids; a padded copy is clean and reads the same;
     - every card is implemented. Victini carries the status repair A addresses;
     - legality scan, km3: 560 games, no findings.
   - **N1** (kn, 71877f6, README 52dd2ef) is built as asked: code, tests, smoke, README. No further N1 step has been named, so nothing of it is running.
2. **What is running now, and when it ends.** Nothing.
3. **Files I expect to change.** None.
4. **Waiting on the laptop or Sonnet.** Nothing.
5. **Open questions for Dustin.** For the coordinator or Dustin: step 8's carriers under the strict rule are garchomp_meowth.txt, coinflip_deck.txt and fire_victini.txt. Should the alternates be used for Togekiss A4 080 and Hisuian Goodra (and for repair A) instead?

## Log (one line per new job, added and pushed before it starts)

- 2026-09-30: km Altaria v Suicune diagnosis (the laptop's request via Dustin): 40 traced deals at B, no new table games.
- 2026-09-30: Victory Star / Confusion repair draft (Fable via Dustin): failing test, then the gated fix, then the unit suite; engine/src/actions/ two files plus rl/results/victory_star_repair_2026-09-30/. No games.
- 2026-09-30: coin-flip damage prevention repair draft (Fable via Dustin): Part 1, a read-only check of the seven helpers (HELPERS.md, committed first); Part 2, (a) partial cuts after Weakness and Bounded Field and (b) the coin on queued direct damage, failing fixtures first. engine/ plus rl/results/coin_prevention_repair_2026-09-30/. No table games.
- 2026-09-30: Chase Order follow-up to the coin-flip prevention draft (Fable via Dustin): failing tests first (no discard, discard, control), then the gated fix in apply_attack_action.rs and apply_action.rs, then the unit suite and the README. No table games.
- 2026-09-30: Sonnet's follow-ups S1-S4 (Fable via Dustin): with_heads_coin_cuts test and hardening, Wild Swing and Ability/Tool/Checkup pins, smoke rerun on e52a73b with a trace of 4 games. Scratch decks only, no table games.
- 2026-09-30: km3 unplayed-Trainer diagnosis (Fable via Dustin): Iris (deck 11) and Team Rocket's Goo-zooka (decks 14, 15) from the floor run; at most 40 replayed deals per card at the official engine; diagnosis only, no table games.
- 2026-09-30: build switch N1 as kn<N> (km + the opponent's Active Retreat Cost in the clock; Fable via Dustin): code, unit tests (kn3 with N1 off = km3 on 200 scratch deals), smoke on scratch decks with Goo-zooka and Peculiar Plaza, README. No registration text, no table games, no identity replay, no merge.
- 2026-09-30: carrier lists for the rules switch (Fable via Dustin; PLAN.md step 3): four development lists from the committed Limitless archive (Garchomp Meowth, Togekiss Meowth, Hisuian Goodra, Mega Houndoom ex Victini), card-checked, with provenance; rl/results/engine_switch_rules_2026-10/carriers/. No games beyond the legality scan, no engine change.
