# Request to Astra: re-check the RL add-on on rules2 before Run 5

September 22, 2026. Written by Opus on Dustin's go; order of work set by Fable. Nothing here trains,
rebuilds, or changes any existing wheel, checkpoint or result. It does not authorize Run 5.

## Why

The add-on (0.6.0, encodings v1 / v2.1 / v2.2) was built against unified1. `0.1.0-pdl.rules2` is now
active, and the repair notes already require a rebuilt, versioned environment for any new training.
This request is about what the rebuild has to prove, because the repair changed the engine's move stream
in a way that the add-on's forecasts may not handle.

**What changed that touches the add-on** [read from `rules-repair-2026-09-22/repair-working-tree.patch`;
not run]:
- New single-option rule steps pushed onto the move-generation stack: `ResolveAttackRetaliation`,
  `ResolveKnockoutPoints`, `ResolvePokemonCheckup`, `FinishPokemonCheckup`, `ResolveEndTurnEvolution`.
  There's also one new real choice, `ChooseRandomEvolutionTarget`. Required promotions are now inserted
  below pending Checkup and later-hit frames (`state/mod.rs`, around 1404).
- k3 and the value-function player were patched in the same repair to treat those rule steps as forced
  (`expectiminimax_player.rs` around 570, `value_function_player.rs` around 80). The add-on was not
  touched, on purpose.
- The patch doesn't change `play_tick` itself (only a test calls it), so the add-on's copy of the loop
  (`advance()`, which auto-plays any single-option step) is *probably* still faithful. The replay check
  is what proves it.

**The suspected fault** [inference from the code; untested]. `v2.rs` builds each move's row by applying
the move one step on a copy (`branches()` → `try_forecast_action`). `features()` then reads points
gained, win/loss, HP change and the v2.2 numbers straight from that one-step state (rows 1–7, 13–14).
Usually the repair still settles retaliation, knockouts and points within the attack itself, because
`attack_outcome.rs` removes the reaction frame when nothing is stacked above it. Three cases leave them
waiting on the stack instead:
1. **An attack whose post-damage effect leaves a choice** (e.g. a switch after attacking). The
   retaliation frame is deferred (`retaliation_deferred`), and `handle_knockouts` returns early while that
   frame is pending, so the knockout and its points happen later.
2. **A Pokémon in the knockout wave with a coin flip to deny knockout points**
   (`CoinFlipToDenyKnockoutPoints`). A `ResolveKnockoutPoints` frame is pushed and the knockout waits.
3. **End turn with a pending point-denial coin, or with an Active that evolves at the end of the
   opponent's turn.** `forecast_end_turn` queues `ResolvePokemonCheckup` / `ResolveEndTurnEvolution`
   instead of finishing.

In those cases a move's row could say "no point, not a win" for a move that knocks out or wins. Those are
the numbers the knockout audits show the network relying on. The threat numbers may also drop to
"unknown" there: `project_d` doesn't project our own pending follow-up. And `hidden_continuation_reason`
can now refuse the Checkup steps (under the same conditions as End turn) and the random-evolution steps
(when the deck is unknown), which `resolve_then_threat` would then skip. Fable notes this is the
same class of problem as the stale forecasts in your v2 review: a one-step read is only right if the
engine settles the result within that step.

**Why the current checks may miss it:** `v2_2_checks.py` skips "moves that open a follow-up choice" and
counts them as skipped, not wrong. The Step 1 checks ran on the brew-03a mirror, which probably never
reaches these cases. So the skipped counts are the finding, not a footnote.

## What we're asking, in order

**A. In parallel**
1. Rebuild the add-on against the rules2 source as a new version, with a fresh identity. Leave the old
   wheels as they are.
2. Re-measure k3 on rules2, **k2 vs k3 first, because it picks Run 5's deck.** Same design as the Sept 20
   table (`results/run3_checks/`, 1,000 paired games per directed matchup), at least over the run 4 pool
   so the two tables compare. Then the k3-vs-k3 seat baseline (the 45% floor came from it) and the whole
   k3 screen. Old k3 numbers are unified1 numbers and shouldn't be mixed with these.

**B. Before committing to the candidate decks**
Do a static reachability check on the two candidate lists, as in `RUN4_RULES_EXPOSURE_20260921.md`:
- Which still-open rules they can reach. These are listed in `rules-repair-2026-09-22/README.md` under
  "Remaining limits", in `review-replay-priority-2026-09-22/README.md` under "Evidence boundaries", and
  in `rules/10_review_of_rules1_2026-09-22.md`.
- Whether they reach any of the three cases above.

**C. On the chosen decks, with the rebuilt add-on**
1. The Step 1 replay: k3 through the add-on reproduces the engine's own games, with legal moves, state
   and observation compared at every decision, both seats, on the chosen matchup.
2. The hidden-card probe: opponent hand/deck and own deck-order reshuffles, with the own-hand control.
3. `v2_2_checks` on the chosen decks. **Report skipped counts broken down by reason**, not only "0
   wrong". A skipped attack or End turn in one of the three cases is a possible wrong answer.
4. If the decks reach those cases: make the forecast play through the single-option rule steps (the
   same list k3's patch uses) before reading the result. Then repeat C3 and show that rows outside
   those cases are unchanged. That changes the encoding's content, so it's a new add-on version and part
   of Run 5's identity.
5. Confirm that `ChooseRandomEvolutionTarget` shows up in the move list as an encoded choice and isn't
   refused.

## What to send back

In plain words:
- the rebuilt add-on's identity;
- each check's result, with the skipped counts;
- the k2-vs-k3 table;
- the reachability result for the candidates;
- whether the forecast change was needed.

If none of the three cases is reachable in the chosen decks, say so. The concern is then moot for Run 5,
but it still matters for any later pool.
