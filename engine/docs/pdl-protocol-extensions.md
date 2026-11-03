# PDL bot-protocol extensions

The adapter speaks upstream's bot protocol v1 (JSON lines: `hello` / `new_game` / `decide`, reply `{"i": n}`)
and adds opt-in `pdl_*` keys. Without an opt-in the messages have exactly upstream's key sets.

## Known limits

1. As a protocol bot, km3 needs `pdl_observation` and `pdl_search_seed`, so it cannot play inside upstream's
   engine, which sends neither.
2. Upstream's MCTS (`mcts_player.rs`) searches the full `State`, including the opponent's hand and deck
   order. It is not a fair opponent until masked or determinized, and is not used here.
3. The protocol adapter is for trusted bots and runs. Any bot that sets pdl_observation in its hello receives
   pdl_search_seed, which can be turned back into the game seed (its own deck order, the RNG behind later chance).
   The protocol logs record the seed too. A run with an untrusted bot also needs unpredictable game seeds; our
   registered seed blocks are public. No registered result used it: the Gemini arm's bot opts in but never reads the
   seed, and the in-repo protocol bot uses it only to replay in-process search (parity).

## Opt-ins (keys in the bot's `hello` reply; a missing key means false, unknown keys are ignored)

| Opt-in | Effect |
|---|---|
| `"agent_snapshot": true` | as upstream: `new_game.deck_definition`; in `decide`: `legal_actions` and `agent_snapshot` (the observation's visible state, with our own deck replaced by `Unknown` cards of the right count) |
| `"pdl_observation": true` | `new_game.deck_definition`; every `decide` gets `legal_actions` (the full `Action` list, in the order of `actions`), `pdl_observation` (the serialized `PlayerObservation` that `decision_fn` received) and `pdl_search_seed` (the u64 from the most recent `before_decision` since the previous decide, or null) |
| `"pdl_events": true` | every `decide` gets `pdl_since_last = {chance_events, cards_left_deck_mine, cards_left_deck_opponent}` |

Each `pdl_*` key is absent unless opted in. `pdl_since_last` counts what happened since the bot's previous
decide (or the game start); the counters are reset at every decide, opted in or not.

* `chance_events`: applied actions during which "the game RNG advanced". That covers coin flips, random picks,
  shuffles, and every EndTurn (the next Energy Zone roll), so `chance_events` is at least 1 at the start of
  each of the bot's turns.
  Known limit: near deck-out, `chance_events` can show whether a deck search had a choice. An action whose forecast
  has one branch is applied with no RNG draw, and a shuffle of a 1-card deck draws nothing: for example, Poké Ball
  with 2 cards left draws from the RNG with 0 Basics or 2 Basics (even two copies of the same card) in the deck, but
  not with exactly 1. The Gemini arm's bot counts chance events for its re-ask (COUNTERS since 93fa49a8), so in that
  rare case its re-ask timing could depend on it: when Gemini is asked again, never what it sees (the same class as
  deviation 16). The Oct 30 chance audit (wf_d91d342a-460) did not cover this case. The fix (a game change) comes
  after R8.
* `cards_left_deck_mine` / `cards_left_deck_opponent`: how many cards left each deck.

There is no count of the opponent's choices (R8 removed `opponent_choices`): whether the opponent had more than
one legal action depends on its hidden hand (a playable card adds an option), so the count leaked hidden cards.
Test `opponent_hidden_options_do_not_reach_the_bot` plays two games that differ only in one hidden card of the
opponent's hand and checks that every `decide` line the bot receives is the same.

## Observation

A Pokémon Asleep from Jigglypuff's Soothing Lullaby (C1 051, C1 184) carries `"sleep_coins_override": 2` in its
`template.in_play_pokemon` entry: it flips 2 coins at Pokémon Checkup and wakes only if both are heads. The key appears
nowhere else. It is present exactly while that Sleep lasts: waking at Pokémon Checkup, any cure, Paralysis or
Confusion, an ordinary Sleep, a switch to the Bench, evolution or devolution, or the Pokémon leaving play (a Knock Out,
or being returned to the hand or shuffled into the deck) removes it.

Sweet Honey (C1 119, C1 152, R8-07a) uses Misty's pre-coin slot: the state's `pending_misty_target_choice` now also
holds Sweet Honey's chosen target. The field name stays.

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
`instance, ply, search_seed, n_actions, i, secs, startup_secs, fallback, error, bot_name`. `secs` is only the
decide round trip (from just before the `decide` line is written to the reply line arriving, before parsing); it is
null when no `decide` was written. `startup_secs` is the first decision's spawn + hello + `new_game` time (null on
every other line, and when no spawn happened). On drop, a summary line:
`{"summary":true,"decisions","fallbacks","errors","ignored_optional_keys","first_ignored","child_pid"}`.

Reply handling, as upstream: in a decide reply only `i` is required (a non-negative integer below the number of
actions; missing, wrong-typed, out of range, invalid JSON or a non-object is a failure). `note` (string) and
`scores` (one finite number per action) are optional; if present but malformed they are ignored. In the hello reply
`name`, `agent_snapshot`, `pdl_observation` and `pdl_events` are optional, and a wrong-typed one counts as absent.
Each ignored optional key is counted in `ignored_optional_keys`; the first one's text is `first_ignored`.

## CLI

`deckgym simulate A B --players proto,km3 --bot-a "<command>" [--bot-b ...] [--bot-timeout-ms 10000] [--bot-log DIR]`.
A `proto` seat needs its flag, and a flag needs a `proto` seat (else exit 2).

## Bots (`engine/bots/`)

`protocol_bot --bot km3` (Rust binary) answers with an engine bot and opts in to `pdl_observation`; through
`ProtocolPlayer` it chooses exactly what km3 chooses when run directly. The Python bots are listed in
`engine/bots/README.md`.

## Test note: EndTurn and `chance`

Test T10 checks `chance` on the tick on which the turn advances, not on every EndTurn: an EndTurn may hand the turn end
to forced steps (Quick Growth -> Checkup), so the Energy roll belongs to the tick on which the turn advances
(`engine/tests/protocol_adapter_test.rs`, the comment above that check).
