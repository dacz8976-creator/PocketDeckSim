# The floor check's Payback pre-use check, Sept 25

**Written and committed before any game of this check was played.**

**What it decides:** whether `decks/screen/floor.py` may be used on Dustin's decks.
- The two Payback lists are known ladder failures, so the floor must call both of them "fail".
- A deck the bot is known to misplay must read "untrusted".
- If either condition fails, the floor is not used, and the pages go to Dustin and Fable.

**Code and engine:**
- `floor.py` at dc17627.
- The official engine `rl/engine-2026-09-25/deckgym` (main-7fc6ccb).
- The coverage from `rl/engine-2026-09-25/goldfish`, checked by hash.
- 240 games per matchup against the 8 lists in `decks/screen/opponents/`, 1,920 per deck.
- Seeds: 7,100 + 1,000 × opponent (deck in seat 0) and + 500 (seat 1), `--seed-stream`.

## Binding

1. **brew-06** (Pyukumuku/Silvally Payback) under kp3 on both sides must read exactly **fail**.
2. **brew-06b** (the Grass version with Team Rocket's Scyther) under kp3 on both sides must read exactly **fail**.
   - "untrusted" or "borderline" fails the check. At 1,920 games, 349 wins or fewer fail, 350–418 is borderline, and 419 or more clears.
   - Their roles were set in `floor.py`'s `ROLES` before any floor game: Silvally, Team Rocket's Mewtwo and Team Rocket's Scyther as attackers, Pyukumuku as a bench piece, Rocky Helmet as a Trainer.
   - **Known risk, stated in advance:** this morning's re-run put brew-06b at 17.3% ± 3.4 over 480 games, on other seeds and another game loop. If 17.3% were its true rate, 1,920 games would read "borderline" about 14% of the time. brew-06 (4.4% ± 1.8 there) is far from the line.
3. **Positive control:** deck 14 (Comfey/Raticate/Hypno) under **k3 on both sides** must read "control reading, not a floor verdict (pilots k3 …): **untrusted**".
   - Team Rocket's Raticate ex must show as an activated ability used on a small share of its opportunities.
   - The brew pilot check measured Thieving Incisors at 3–5% of offered turns under k3. The development smoke showed 1 of 70.
   - If this doesn't read untrusted, the counter is broken and the check stops.

## Descriptive only (not part of the pass/fail)

- **brew-05b** (Meowstic/Hatterene/Comfey) and **deck 07** (Skarmory stall) under kp3.
- They are anchors from the Sept 24 calibration: 05b clear of the bar (29.4% ± 4.1 this morning), and deck 07 near 45% (47.7% ± 4.5).

## Second read, in a separate session

- The hashes of floor.py's commit, the engine and the goldfish.
- A plain `run_screen.py` run at 240 games per matchup for brew-06 and brew-06b, with the same seeds. It must give the same wins per opponent and seat as each page's "For a second reader" section, which shows tracing changed no game. `run_screen.txt` here holds the laptop's own copy.
- A hand recount of one flagged card from `<deck>_games.jsonl`.
- The flagged set checked against `<deck>_coverage.json` and the list.
- Two games re-run by seed.
- The control reading untrusted.

**Files:**
- `run_check.sh`: the commands.
- `<deck>.md`: each page.
- `<deck>_games.jsonl`: per-game records.
- `<deck>_coverage.json`: A1's coverage.
- `run_screen.txt`: the plain screen at 240 per matchup.
- `timing.txt`: wall times.
