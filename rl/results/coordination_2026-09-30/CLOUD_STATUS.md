# Cloud Opus status (branch claude/pensive-ptolemy-spwc0b)

Written Sept 30 for the Fable coordinator session (Dustin's single delegator). Times are UTC.

1. **Current task, and the instruction that set it.** The carrier lists for the rules switch, step 3 of rl/results/engine_switch_rules_2026-10/PLAN.md (main 0a68b0a). Set by the Fable coordinator via Dustin, Sept 30, "about 1 hour, before N1's next long step".
   - The lists: one development list each, by decklist_sources.json's rule (the most frequent exact list among the top 8), from the committed archive rl/results/limitless_skill_model_2026-09-25/raw/*_standings.json.gz (no web access):
     - Garchomp Meowth (garchomp-b4a-meowth-b2);
     - Togekiss Meowth (togekiss-a4-meowth-b2);
     - the most-played Hisuian Goodra list;
     - Mega Houndoom ex Victini (mega-houndoom-ex-p-b-victini-b3).
   - Each is card-checked (lib/card.py, card status, a legality scan on the official engine), with no B4b card and provenance (event, player, date) per list. The plan's fallback applies where a list can't be had.
   - Output: rl/results/engine_switch_rules_2026-10/carriers/ on this branch (no engine file).
   - The rules fixes F1-F7 are Sonnet's, on a separate branch; not started here.
   - The N1 build before it is done: 71877f6, README 52dd2ef, rl/results/kn_build_2026-09-30/.
2. **What is running now, and when it ends.** Starting now: reading the archive and the plan's rule, then the card checks and a legality scan. About an hour.
3. **Files I expect to change.** Only the new folder rl/results/engine_switch_rules_2026-10/carriers/ and this file.
4. **Waiting on the laptop or Sonnet.** Nothing.
5. **Open questions for Dustin.** None.

## Log (one line per new job, added and pushed before it starts)

- 2026-09-30: km Altaria v Suicune diagnosis (the laptop's request via Dustin): 40 traced deals at B, no new table games.
- 2026-09-30: Victory Star / Confusion repair draft (Fable via Dustin): failing test, then the gated fix, then the unit suite; engine/src/actions/ two files plus rl/results/victory_star_repair_2026-09-30/. No games.
- 2026-09-30: coin-flip damage prevention repair draft (Fable via Dustin): Part 1, a read-only check of the seven helpers (HELPERS.md, committed first); Part 2, (a) partial cuts after Weakness and Bounded Field and (b) the coin on queued direct damage, failing fixtures first. engine/ plus rl/results/coin_prevention_repair_2026-09-30/. No table games.
- 2026-09-30: Chase Order follow-up to the coin-flip prevention draft (Fable via Dustin): failing tests first (no discard, discard, control), then the gated fix in apply_attack_action.rs and apply_action.rs, then the unit suite and the README. No table games.
- 2026-09-30: Sonnet's follow-ups S1-S4 (Fable via Dustin): with_heads_coin_cuts test and hardening, Wild Swing and Ability/Tool/Checkup pins, smoke rerun on e52a73b with a trace of 4 games. Scratch decks only, no table games.
- 2026-09-30: km3 unplayed-Trainer diagnosis (Fable via Dustin): Iris (deck 11) and Team Rocket's Goo-zooka (decks 14, 15) from the floor run; at most 40 replayed deals per card at the official engine; diagnosis only, no table games.
- 2026-09-30: build switch N1 as kn<N> (km + the opponent's Active Retreat Cost in the clock; Fable via Dustin): code, unit tests (kn3 with N1 off = km3 on 200 scratch deals), smoke on scratch decks with Goo-zooka and Peculiar Plaza, README. No registration text, no table games, no identity replay, no merge.
- 2026-09-30: carrier lists for the rules switch (Fable via Dustin; PLAN.md step 3): four development lists from the committed Limitless archive (Garchomp Meowth, Togekiss Meowth, Hisuian Goodra, Mega Houndoom ex Victini), card-checked, with provenance; rl/results/engine_switch_rules_2026-10/carriers/. No games beyond the legality scan, no engine change.
