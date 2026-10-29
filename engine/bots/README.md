# Protocol bots

Python bots for the bot protocol (see `engine/docs/pdl-protocol-extensions.md`). Standard library only; each is one file.

- `random_bot.py`: unchanged copy of `examples/bots/random_bot.py` from bcollazo/deckgym-core at `dfe6ff30`.
  License: AGPL-3.0, the same as `engine/` (`engine/LICENSE.txt` is identical to upstream's).
- `first_legal_bot.py`: base protocol, no opt-in; always replies `{"i":0}`. No flags.
- `seeded_random_bot.py --seed N`: base protocol; `i = random.Random(N*1000003 + ply).randrange(len(actions))`.
- `plan_follower_bot.py --seed N [--log PATH]`: opts in with `pdl_events`; follows a saved plan (from `DummyPlanSource`)
  and re-asks when `pdl_since_last` counters are non-zero or the next step is stale. `--log` writes one record per decide.
- `test_bad_bot.py --mode {garbage,range,sleep,exit,nohello}`: correct for 2 decides, then misbehaves from the 3rd.
- `test_plan_follower.py`: unittest for the plan follower. Run from the repo root: `python3 -I engine/bots/test_plan_follower.py -v`.

The Rust bot `protocol_bot --bot <code>` (`engine/src/bin/protocol_bot.rs`) answers the protocol with an engine bot.
