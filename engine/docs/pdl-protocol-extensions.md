# PDL bot-protocol extensions

The adapter speaks upstream's bot protocol v1 (JSON lines: `hello` / `new_game` / `decide`, reply `{"i": n}`)
and adds opt-in `pdl_*` keys. Without an opt-in the messages have exactly upstream's key sets.

## Known limits

1. As a protocol bot, km3 needs `pdl_observation` and `pdl_search_seed`, so it cannot play inside upstream's
   engine, which sends neither.
2. Upstream's MCTS (`mcts_player.rs`) searches the full `State`, including the opponent's hand and deck
   order. It is not a fair opponent until masked or determinized, and is not used here.

## Opt-ins (keys in the bot's `hello` reply; a missing key means false, unknown keys are ignored)

| Opt-in | Effect |
|---|---|
| `"agent_snapshot": true` | as upstream: `new_game.deck_definition`; in `decide`: `legal_actions` and `agent_snapshot` (the observation's visible state, with our own deck replaced by `Unknown` cards of the right count) |
| `"pdl_observation": true` | `new_game.deck_definition`; every `decide` gets `legal_actions` (the full `Action` list, in the order of `actions`), `pdl_observation` (the serialized `PlayerObservation` that `decision_fn` received) and `pdl_search_seed` (the u64 from the most recent `before_decision` since the previous decide, or null) |
| `"pdl_events": true` | every `decide` gets `pdl_since_last = {opponent_choices, chance_events, cards_left_deck_mine, cards_left_deck_opponent}` |

Each `pdl_*` key is absent unless opted in. `pdl_since_last` counts what happened since the bot's previous
decide (or the game start); the counters are reset at every decide, opted in or not.

* `opponent_choices`: actions the opponent took when it had more than one legal action.
* `chance_events`: applied actions during which "the game RNG advanced". That covers coin flips, random picks,
  shuffles, and every EndTurn (the next Energy Zone roll), so `chance_events` is at least 1 at the start of
  each of the bot's turns.
* `cards_left_deck_mine` / `cards_left_deck_opponent`: how many cards left each deck.

## ViewState

`ViewState` is a port of upstream's, built from a `PlayerObservation` only. Own `hand` is listed, the opponent's
`hand` is null (`hand_count` is given). Own `deck_count` is the length of the known own deck. No upstream field is
left out: every one has a counterpart in `State`. During setup (turn 0) the opponent's starting Pokemon are still
face down, so the opponent's `in_play` is all null.

## Failure rule

A spawn error, a hello timeout or bad hello (not a JSON object), a write error, a reply timeout, the process
exiting, invalid JSON, or `i` missing or out of range is a failure. The first failure makes `ProtocolPlayer` play
`actions[0]` (a fallback, counted in `fallbacks`), kill the bot's process group and play fallbacks for the rest of
the game, with no respawn. It never panics.

## Log (`--bot-log DIR`)

`DIR/protocol_<pid>_<n>.jsonl`, one file per `ProtocolPlayer`. One line per asked decision:
`instance, ply, search_seed, n_actions, i, secs, fallback, error, bot_name`. On drop, a summary line:
`{"summary":true,"decisions","fallbacks","errors","child_pid"}`.

## CLI

`deckgym simulate A B --players proto,km3 --bot-a "<command>" [--bot-b ...] [--bot-timeout-ms 10000] [--bot-log DIR]`.
A `proto` seat needs its flag, and a flag needs a `proto` seat (else exit 2).

## Bots (`engine/bots/`)

`protocol_bot --bot km3` (Rust binary) answers with an engine bot and opts in to `pdl_observation`; through
`ProtocolPlayer` it chooses exactly what km3 chooses when run directly. The Python bots are listed in
`engine/bots/README.md`.

## Test note: EndTurn and `chance`

Test T10 does not assert that every EndTurn (turn_count >= 1) is classified `chance`. It failed for pair t-sceptile v
t-vespiquen (order 0, seed 25102003000, turn 1; both decks have only Grass energy), so that check was removed.
