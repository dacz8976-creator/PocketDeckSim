# bots_info — do the simulator's bots play like a real player could?

Scope note: this file isn't card-rules bugs against printed text; it's the requested audit of
bot realism / information-hiding for `src/players/*.rs`, `src/observation.rs`,
`src/public_reply_evidence.rs`, `src/game.rs`, `src/state/mod.rs`. I follow the brief's
evidence tags (VERIFIED-READ / PROBABLE / UNSURE) since I did not run new probes (existing
unit/integration tests already cover the key claims and are cited).

## Headline answer

The engine already has a real, well-tested hidden-information boundary
(`src/observation.rs`, "closed-counts-unpriced-v7"), built specifically to fix a documented
historical leak (§37–§42 in code comments). **Every real game (`Game::play_tick`,
`src/game.rs:199-246`) calls `Player::decision_fn(rng, &PlayerObservation, actions)`, never
`decide_omniscient` with the raw referee `State`.** So the search bots do not see the
opponent's hand contents, either deck's true order, or energy beyond "next" *during play*.
What remains genuinely unrealistic is narrower: (1) the **RL/data-export path bypasses this
boundary and logs the omniscient `State`**, (2) the **Python bindings only expose the
omniscient `State`**, (3) the **default bot `k3` never searches the opponent's turn**
(`opponent_ply: 0`), and (4) several chance/draw mechanics are single-sample rather than
full expectations. Details below.

## Findings

### F1 [High] RL/self-play data export logs the omniscient `State`, not the `PlayerObservation` the bot actually used (confidence: VERIFIED-READ)
- Files: `src/game.rs:199-266`, `src/data_exporter.rs:14-41,142-167`, `src/main.rs` (`--data-output`).
- `Game::play_tick` builds the redacted `observation` and feeds only that to the bot
  (`game.rs:224-234`), but then calls
  `handler.on_action(self.id, &self.state, actor, &actions, &action)` (`game.rs:260`) — `&self.state`
  is the **true, un-redacted referee state before the action**, not the observation.
- `DataExporter::on_action` stores that into `ExportedDataPoint.state: State` (`data_exporter.rs:19,150-167`),
  which serializes the opponent's actual hand, actual deck order, and (once rolled) all
  energy-zone state, one JSON file per ply under `--data-output`.
- `examples/load_exported_data.py` is the shipped "how to train a policy/value network from
  this data" example; its `extract_features` only reads counts today, but nothing in the
  format stops (and nothing documents not to) reading `state['hands'][opponent]` directly —
  the omniscient answer key is sitting right there in every exported ply.
- Impact: this is exactly the "RL/self-play" use the brief points at. The *decision* that
  produced `chosen_action` was made honestly (from `observation`), but the *training signal*
  captured alongside it is not. Anyone training a value/policy net on `state` as given trains
  on cheat information; the same is true for any hindsight labeling (e.g. "did this position
  turn out to be winning") that conditions on hidden opponent cards. This can silently make a
  distilled/learned bot memorize opponent hands it will never see at inference, and makes any
  offline metric computed from this data optimistic in a way that won't reproduce online.
- Fix is cheap: `on_action` already has access to `PlayerObservation::from_state`; store the
  observation for `actor` (or both players' observations) alongside/instead of the raw state,
  the same way `information_model`/`unpriced_branches` are already carried through.

### F2 [High] The Python bindings (`python/deckgym`) expose only the omniscient `State`; no redacted-observation binding exists (confidence: VERIFIED-READ)
- Files: `src/python_bindings.rs:385-688` (`PyState`), `692-733` (`PyGame`), whole-file grep for "Observation" → 0 hits.
- `PyState::get_hand(player)` (line 463) returns **either** player's real hand; `get_discard_pile`,
  `get_in_play_pokemon`, etc. are all unfiltered reads of `self.state`. `PyGame::get_state()`
  (line 735) hands out a fresh `PyState` wrapping `self.game.get_state_clone()` — the true state.
- There is no `PyPlayerObservation` class, and `PyGame::play_tick()` only returns a `String` of
  the action taken (line 741-744) — it doesn't expose the observation the internal bot decided
  from either.
- Impact: if any external Python tooling (a notebook, an RL loop, a hand-written bot prototype)
  is or will be built against this package — which is what `python/deckgym` and the
  `examples/*.ipynb`/`.py` scripts are for — the natural, path-of-least-resistance API call
  (`state.get_hand(1)`) hands it the opponent's exact hand. The Rust-side boundary
  (`observation.rs`) that the rest of this audit found to be solid is simply not reachable from
  Python today.
- Fix is cheap: add a `PyPlayerObservation` wrapper (mirrors what `PlayerObservation` already
  exposes: `visible_state()`, `known_own_deck`, `revealed`) and a `PyGame::observation(player)`
  method next to `get_state()`, so a Python RL loop has a legitimate redacted view available
  without having to reimplement `observation.rs`'s redaction logic itself.

### F3 [Medium] Default bot `k3` never searches the opponent's reply — `opponent_ply: 0` (confidence: VERIFIED-READ)
- Files: `src/players/mod.rs:364-372` (`PlayerCode::K` construction), `src/players/expectiminimax_player.rs:840-861`.
- `get_player` for `PlayerCode::K { max_depth }` builds
  `ExpectiMiniMaxPlayer { ..., opponent_ply: 0, consistent_horizon: false, soft_opponent: false }`
  (`mod.rs:364-372`). Contrast with `X`/`Y`/`S` (`x<N>`, `y<N>`, `s<N>`), which do set a
  nonzero `opponent_ply` (`mod.rs:391-426`) and are the tiers whose whole purpose is searching
  a bounded, public-information slice of the opponent's turn (`expectiminimax_player.rs:105-136`
  doc comments).
- With `opponent_ply == 0`, the moment `state.current_player != myself` inside the search it
  returns the static value function immediately (`expectiminimax_player.rs:846-850`,
  `LEAF_BOUNDARY_UNPRICED`). So `k3`'s lookahead is strictly "N of my own actions this turn,"
  and *nothing* about what the opponent could do next turn is searched — only what the leaf
  heuristic encodes (a crude `HP / knockout_points` "active_safety" term and an
  evolution/energy-aware "threat clock," see `value_functions.rs:1287-1296` and
  `:649-762`) stands in for "will I die next turn."
- Partial mitigation that *does* apply regardless of `opponent_ply`: `certified_public_reply_loss_value`
  (`expectiminimax_player.rs:482-515`, called at `:705-730` before the depth/opponent-ply
  checks) can still certify "this line hands the opponent a forced, publicly-visible KO" and
  price it as a loss — but only when `PublicReplyProvenance` can *prove* it from public
  information; anything short of a proven forced win falls through to the static evaluator.
- Impact: `k3` (the project's default simulation bot) is real-move-search-blind past its own
  turn. It relies entirely on heuristics for "don't leave your Active to die," "don't overextend
  the bench," etc. `x3`/`y3`/`s3` exist specifically to fix this but are not the default, and
  `x3` itself was measured to have a pilot regression (retreating too much) before `y`/`s`
  fixed the search-horizon and paranoid-opponent issues (see F5).

### F4 [Low] Random-target/random-effect mechanics are single-sampled inside the search, not enumerated with probabilities like coin flips (confidence: PROBABLE)
- Files: `src/actions/apply_action.rs:406-450` (`forecast_action_unchecked`'s "Deterministic
  Actions" match arm), vs. `:370-402` (`try_forecast_action`/`forecast_action` producing
  `Outcomes` with `(Probabilities, Mutations)`, consumed by both the expectiminimax search
  (`expectiminimax_player.rs:433-471`) and `value_function_player.rs:62-75`).
- Coin flips genuinely enumerate: `try_forecast_action` returns one branch per outcome with its
  real probability, and the search takes the probability-weighted sum
  (`expectiminimax_player.rs:467-471`), not a sample.
- But `SimpleAction::DrawCard`, `DiscardRandomOpponentActiveEnergy`,
  `MoveRandomOpponentEnergyToActive`, `ApplyStatusToOpponentActive`,
  `DiscardOwnBenchedThenDamage`, etc. are bucketed under "Deterministic Actions" →
  `forecast_deterministic_action()` (`apply_action.rs:419-450`) — a single mutation, probability
  1.0, that internally calls the search's own `rng` to pick which card/energy/target when the
  underlying effect is actually random. The code's own comment flags this for draws: `// TODO:
  DrawCard should return actual deck probabilities.` (`apply_action.rs:421`).
- Impact: the search commits to one sampled outcome (e.g. "this energy gets discarded," "this
  card gets drawn") per decision instead of weighting all possible outcomes. For `DrawCard`
  specifically this is less bad than it looks, because the acting player's own deck order was
  already fixed by `PlayerObservation::search_state`'s single shuffle for that whole decision
  (see F6) — so at least it's internally consistent within one decision — but it is still one
  hypothetical draw sequence per decision, not an expectation over draws, and for the
  random-target effects it means the value assigned to (e.g.) "discard a random attached
  energy" reflects only whichever energy the search RNG happened to pick, not the true expected
  value across the possible picks.

### F5 [Low] Known, code-documented pilot-skill gaps in the default search family (confidence: VERIFIED-READ, per in-repo tests/comments — not independently re-verified by me)
- Files: `src/players/value_functions.rs:107-171,316-329,636-648`, `src/players/expectiminimax_player.rs:113-136`.
- Historical: the pre-`d`-tier Pokémon term (`HP × (energy+1)`) scored an undamaged Basic
  higher than its own evolution (comment cites "an undamaged Bulbasaur (70 HP, 2-energy attack)
  outscores the Ivysaur it evolves into (100 HP, 1-energy utility attack) 210 to 200" and "0
  evolutions in 240 logged games" — `value_functions.rs:112-117`). Fixed by the `d`/later tiers'
  damage-aware Pokémon term, but this is exactly the kind of "won't do the thing a real player
  obviously would" gap the audit asked about, and it's the sort of regression that can
  reappear when weights are retuned.
- The value-term fix itself is flagged as a possible new regression: "Prime suspect for the
  pure-basics aggro regression (koraidon mirror ~41-42% under d/f/g)" (`value_functions.rs:323`)
  — i.e. the same additive Pokémon-value term that fixed evolution-avoidance is suspected of
  making pure-basic aggro decks pilot worse.
- `x<N>`'s horizon-inconsistency bug (`expectiminimax_player.rs:113-132`): because depth was
  checked before the turn boundary, aggressive (turn-ending) lines got charged the opponent's
  best public punish while passive lines that ran out of depth first got scored for free.
  Measured effect quoted in the comment: "`x3` picked the unpriced action about **four times**
  as often as its share of the candidate list, and its retreat rate roughly doubled against
  `p3`." Fixed by `y`/`s`, neither of which is the default.
- None of this is new information I'm asserting from scratch — it's already tracked in the
  code by the people building it; I'm surfacing it here because it directly answers "known
  pilot-skill gaps documented in the code."

### F6 [Low] `search_state` is a single hypothetical own-deck order per decision, not an ensemble (confidence: VERIFIED-READ)
- File: `src/observation.rs:144-158`.
- For the acting player's own deck, `search_state(rng)` takes the known multiset
  (`known_own_deck`), keeps any already-revealed top cards fixed in place, and shuffles the
  remainder **once** with the decision's search RNG (`observation.rs:155-156`). The opponent's
  hand/deck stay `Card::Unknown` throughout — they are never sampled into concrete cards at
  all (correctly conservative: no matchup prior is invented, per the comment at
  `observation.rs:142-143`).
- This directly and correctly answers the audit's specific example: simulating the acting
  player's own Professor's Research inside the search draws from this **one sampled
  remainder**, not the real top of the real deck. Good — that's the fix already in place.
- But it is one sample, not a distribution: two different candidate actions evaluated in the
  same decision see the same sampled order (consistent), but decision-to-decision the "future"
  of the deck is re-rolled independently, and there's no averaging over multiple
  determinizations (à la ISMCTS) to reduce variance from an unlucky/lucky single shuffle. Cheap
  determinization-averaging (F list below) would tighten this.

## Answers to the six audit questions (condensed)

1. **Default bot / player-code map.** `k3` = `PlayerCode::K{max_depth:3}` →
   `ExpectiMiniMaxPlayer{ value_function: public_clock_effect_value_function, opponent_ply: 0,
   consistent_horizon: false, soft_opponent: false }` (`mod.rs:161-195,364-372`). No dedicated
   "RL bot" exists; the two players actually built around the closed-information
   `decision_fn`/`PlayerObservation` boundary as their *only* entry point are the
   `ExpectiMiniMax*` tiers (`P` onward) and `JevPlayer` (`jev_player.rs:154-162`, which
   `panic!`s if anyone calls `decide_omniscient` on it at all — it refuses raw `State`
   entirely and talks to an external Python/LLM scorer over stdio via `jev_transport.py`).
   Full code→config map for every letter is in `mod.rs:309-428` (see F3 for `k`'s specifically).
2. **Does any bot's decision read opponent hand/deck order/future energy/future RNG?** Not in
   real games. `decision_fn` (the only entry point `Game::play_tick` calls,
   `game.rs:232-234`) always redacts first via `PlayerObservation::from_state`
   (`observation.rs:41-134`: opponent hand/deck → `Card::Unknown`, own deck order replaced by a
   fresh search-RNG shuffle). The search then clones that *redacted* `State` for every branch
   (`expectiminimax_player.rs:436-438`), so "apply an action to a cloned full State" never sees
   real hidden cards — it sees `Card::Unknown` placeholders, and `is_public_information_action`
   (`expectiminimax_player.rs:182-197`, gate-tested at `:1256-1285`) additionally stops the
   opponent-ply search from ever branching on a hand/deck-sourced opponent action. The one
   remaining leak is architectural, not per-decision: `baseline_value_function` (bare `e<N>`,
   not the default) is *unit-tested to still read opponent hand/deck contents when called
   directly on a raw State* (`tests/value_function_hidden_info_test.rs:87-105`) — harmless in
   production because `decision_fn` redacts first, but a real trap for any future code path
   that calls `decide_omniscient` with a real `State` (nothing stops that except a doc comment
   at `players/mod.rs:44-46`). See F1/F2 for the two places that currently *do* get the raw
   state: the data exporter and the Python bindings.
3. **Chance events.** Coin flips and most `Play`/`Attack`/trainer-coin mechanics are
   **enumerated with exact probabilities** via `try_forecast_action` → `Outcomes` and summed as
   an expectation (`expectiminimax_player.rs:450-471`). Draws and several "random
   target/discard" effects are **single-sampled** through the search's own RNG rather than
   enumerated (F4) — a real but narrower gap than a full future-RNG leak, and explicitly
   flagged as a TODO in the source for draws.
4. **RL observation exposure.** `observation.rs`'s own boundary is correct and matches the
   brief's "what a real player knows" list exactly (both discard piles, hand/deck *sizes*, both
   Energy Zones incl. next, revealed opponent cards — all left untouched by
   `PlayerObservation::from_state`; opponent hand/deck *contents* and own deck *order* are the
   only things redacted). What's missing is that this boundary isn't wired into the two places
   an RL pipeline would actually consume state from: the `--data-output` exporter (F1) and the
   Python bindings (F2), both of which currently hand out the omniscient `State`.
5. **Realism of play.** The default `k3` does not search the opponent's turn at all (F3);
   whatever "don't die next turn" behavior it has is heuristic
   (`active_safety = HP / knockout_points`, plus an evolution/energy-aware threat clock),
   except for a narrow "certified forced public loss" check that fires independent of
   `opponent_ply`. `x3`/`y3`/`s3` add real opponent-turn search but aren't the default, and
   `x3` specifically was measured to over-retreat from a search-horizon bug (F5, now fixed in
   `y`/`s`). The weaker heuristic bots (`aa`=AttachAttackPlayer, `et`=EndTurnPlayer,
   `w`=WeightedRandomPlayer, `er`=EvolutionRusherPlayer) *do* have hard-coded, context-blind
   priorities by design (`aa` always attaches then always attacks if it can, regardless of
   board state; `et` always ends turn; `w`'s per-action-type weight table
   (`weighted_random_player.rs:44-105`) is static and ignores context) — but none of these is
   the default. `m` (MctsPlayer) is a special case: its `decision_fn` is explicitly disabled
   in closed-information mode and falls back to a **uniform random legal move**
   (`mcts_player.rs:27-40`, comment: "closed mode uses a legal random fallback rather than fake
   rollouts") — its real MCTS tree search (`decide_omniscient`) is unreachable from
   `Game::play_tick` today, so if `m` is ever used it is not doing what its name implies.
   Retreat/promotion: `is_current_promotion_frame`
   (`expectiminimax_player.rs:199-241`) and the dedicated `promotion_continuation_tests.rs`
   suggest promotion choice is searched properly as its own frame (not a hard-coded pick), but
   I did not independently re-derive its correctness beyond reading the frame-detection logic.
6. **Cheap improvements, ranked by expected impact ÷ effort:**
   1. **Route `DataExporter`/`--data-output` through `PlayerObservation` instead of the raw
      `State`** (F1). Highest impact for "RL work" specifically, and the plumbing
      (`PlayerObservation::from_state`) already exists — this is a small, localized change to
      `game.rs`'s `on_action` call and `ExportedDataPoint`.
   2. **Add a `PyPlayerObservation`/`PyGame::observation()` binding** (F2) so any Python-side
      bot/RL work has a legitimate redacted view without reimplementing the Rust redaction.
      Also small; mirrors an API that already exists in Rust.
   3. **Give `k3` (or a new default) a small `opponent_ply`** — even `opponent_ply: 1` (their
      best public reply only) would catch the "walks into a lethal I could see coming" class of
      mistake that F3 documents, at a bounded search-size cost; the `X`/`Y`/`S` infrastructure
      to do this already exists and is tested, it's a config change plus re-validating pilot
      quality (the project already has the `y`/`s` tooling to check for the `x3` regression).
   4. **Average `search_state` over a few determinizations instead of one shuffle** (F6) —
      cheap variance reduction (run the existing single-sample search N times with different
      RNG seeds and average scores, or at minimum re-sample per top-level candidate action
      instead of once per decision) for decisions that are close and order-sensitive (e.g.
      "do I have enough draws left to hit my combo piece").
   5. **Enumerate rather than sample the "random target/discard" effects and draws** (F4),
      reusing the `Outcomes`/`Probabilities` machinery already built for coin flips — the TODO
      is already in the source; this is "finish what's started" rather than new design.
   6. **Structurally separate "redacted state for search" from "real state"** at the type level
      (e.g. a newtype/wrapper `SearchState(State)` that `decide_omniscient` requires) instead of
      relying on the `Player::decide_omniscient` doc comment ("Never pass real engine state here
      from gameplay") — lower urgency since no production path currently violates it, but it's
      the kind of guardrail that would have caught F1/F2 by construction instead of by audit.

## Rules questions
None — this scope is architectural/behavioral, not printed-card-text vs. engine.

## Checked and OK
- `Game::play_tick` (`game.rs:199-246`) is the only place a real game asks a player to decide,
  and it always goes through `decision_fn`/`PlayerObservation`, never `decide_omniscient` with
  raw state — confirmed by grepping every `decide_omniscient(` call site outside `src/players/`
  (zero hits).
- `PlayerObservation::from_state` (`observation.rs:41-134`) redacts exactly the hidden set the
  brief describes and leaves untouched exactly the visible set (discard piles, points, energy
  zones current+next for both players, hand/deck *sizes*, in-play board, revealed-card
  tracking via `RevealedKnowledge`/`update_knowledge`) — matches rules/04_actions_cards_effects.md §10 as
  summarized in the task.
- `is_public_information_action` (`expectiminimax_player.rs:182-197`) is positively
  gate-tested both ways: hand/deck-sourced actions rejected
  (`:1253-1285` `test_hand_sourced_actions_are_rejected`), public board actions allowed
  (`:1287-1313` `test_public_board_actions_are_allowed`), and stack membership does not launder
  a hidden action into a public one (`:1325-1337`).
- Future energy (beyond "next") is not merely hidden by filtering — it doesn't exist in `State`
  until rolled: `energy_zone[player].next` is only (re)rolled via the *game's* real RNG at the
  moment the previous `next` rotates into `current` (`state/mod.rs:927-931`, using
  `self.rng` in `Game::apply_action`, never the search's `rng`), so the search literally cannot
  peek further ahead than what's already been rolled into the real state before the decision.
- Search RNG and gameplay RNG are cleanly separated by design and comment: `Game.rng` is
  "Used only for dealing and real action resolution" (`game.rs:98`); per-decision search seeds
  are derived from a `GameRandomness` explicitly built to never reuse the gameplay RNG
  (`game.rs:16-22,64-93`, comment "Search seeds never come from the gameplay RNG").
- Simple heuristic players (`AttachAttackPlayer`, `EndTurnPlayer`, `EvolutionRusherPlayer`,
  `RandomPlayer`, `WeightedRandomPlayer`) only ever branch on the *shape* of already-legal
  `possible_actions` (which are legitimately generated from the acting player's own real hand)
  or the acting player's own in-play board — none of them reads the opponent's hidden zones.
- `HumanPlayer::decision_fn` explicitly uses `observation.visible_state()` (the redacted
  template), not raw state, and prints "Closed information: unknown opponent cards are not
  revealed." (`human_player.rs:15-18`) before prompting — the interactive/manual path is
  consistent with the automated one.
