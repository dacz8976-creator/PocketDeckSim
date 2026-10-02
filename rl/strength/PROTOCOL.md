# External pilot protocol (version 1)

A pilot spec `ext:<command>` runs `<command>` through `sh -c`, **one process per seat per game**. The harness talks to it in JSON lines: one JSON object per line on the pilot's **stdin** (from the harness) and **stdout** (from the pilot). The pilot's stderr goes to the harness's stderr (use it for logs). Lines on stdout that are not JSON objects are ignored.

The pilot may be as slow as it likes. The harness has no per-move limit unless the manifest sets `ext_timeout_s`; it reports the time per decision and per game as plain facts.

## Messages from the harness

`hello`, once, at the start of the game. No reply.
```json
{"type": "hello", "protocol": 1, "seat": 0, "seed": 24300000123, "deck": [{"id": "B4 034", "name": "Carvanha"}, ...20 cards...]}
```

`decide`, for every decision the engine asks of the pilot (a choice among two or more legal actions; forced single-move frames are resolved by the engine and never asked).
```json
{"type": "decide", "seat": 0, "turn": 7,
 "observation": { ... the engine's PlayerObservation ... },
 "actions": [{"i": 0, "label": "EndTurn", "action": { ... }}, {"i": 1, "label": "Attack:Turbo Shark", "action": { ... }}, ...]}
```
- `observation` is the engine's `PlayerObservation` serialized as the engine writes it: `actor`, `information_model`, `known_own_deck` (the pilot's own remaining deck as an unordered list), `revealed` (what the opponent has publicly shown), and `template` (the public state: both boards, points, turn, discard piles, the pilot's own hand; the opponent's hand and deck are counts of `Unknown` cards). It is exactly what the engine's own pilots see; nothing hidden is sent.
- `actions` is the complete list of legal actions, in the engine's canonical order. `label` is a compact name (`Play:Misty`, `Evolve:Alolan Ninetales ex@1`, `Attach:1Water@0 zone`, `Attack:Binding Snow`, `Retreat:2`, `Ability:Boosted Evolution@0`, `EndTurn`, ...); the same labels appear in the logs and the intended-line table. `action` is the full engine action in serde JSON, for a pilot that wants the details (a trainer card's text, an attack's cost).

`end`, when the game is over (the process is then stopped).
```json
{"type": "end"}
```

## Reply to `decide`

```json
{"choice": 3, "note": "why, in a sentence", "cost_usd": 0.0123, "tokens": 4567}
```
- `choice`: the index `i` of the chosen action. Instead of `choice` a pilot may send `"label": "Attack:Binding Snow"` (the first action with that label is taken; use `choice` when two actions share a label, such as two Poké Balls in hand).
- `note` (optional): kept in the game record (up to 400 per game), for reading a game afterwards.
- `cost_usd`, `tokens` (optional): summed per game and reported per game and per decision, so a run can say what it cost.
- An answer that is not an index of a legal action stops that game: it is written to `errors.jsonl`, not counted, and replayed when the run resumes.

## What the harness guarantees

The two arms of a pair start from the same deal. A deterministic external pilot therefore repeats exactly when asked the same questions; a pilot that samples (an LLM at nonzero temperature) will not, and the paired difference then also carries the pilot's own variation, which is what the interval measures.

`ext_pilot_example.py` is a minimal pilot that reads this protocol and answers (it prefers an attack, otherwise the first action that is not `EndTurn`).
