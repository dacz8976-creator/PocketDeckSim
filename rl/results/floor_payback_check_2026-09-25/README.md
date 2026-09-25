# The floor check's Payback pre-use check, Sept 25

**Result: the check passes on the laptop's run.** Both Payback lists read "fail", and the k3 control reads "untrusted". The floor can be used once the second read in a separate session agrees.

| deck | pilots | wins of 1,920 | verdict | needed |
|---|---|---:|---|---|
| brew-06 (Pyukumuku/Silvally Payback) | kp3, kp3 | 128 (6.7%) | **fail** | fail ✔ |
| brew-06b (Grass, Team Rocket's Scyther) | kp3, kp3 | 281 (14.6%) | **fail** | fail ✔ |
| deck 14 (Comfey/Raticate/Hypno), control | k3, k3 | 195 (10.2%) | **control reading: untrusted** | untrusted ✔ |
| brew-05b (Meowstic/Hatterene/Comfey) | kp3, kp3 | 597 (31.1%) | clears the floor | descriptive |
| deck 07 (Skarmory stall) | kp3, kp3 | 908 (47.3%) | clears the floor | descriptive |

**What the pages show:**
- **The Payback lists fail with their flagged cards in use**, so a fail is not the bot ignoring their plan:
  - brew-06: Silvally attacks on 595 of 597 chances, Pyukumuku is benched on 58%, Rocky Helmet is played on 90%.
  - brew-06b: Silvally 592 of 599, Team Rocket's Scyther 182 of 188, Pyukumuku 66%, Rocky Helmet 62%.
  - Both are worst against Sceptile, at 2%.
- **brew-06b was well clear of the borderline line.** 281 wins against the 349 edge. The risk stated below did not happen.
- **The control works.** Team Rocket's Raticate ex uses Thieving Incisors on 50 of 1,628 chances (3.1%), inside the 3–5% the brew pilot check measured. Team Rocket's Goo-zooka is also under 25% (64 of 4,510).
- **The anchors hold.**
  - brew-05b is 31.1%, against 29.4% ± 4.1 this morning.
  - Deck 07 is 47.3%, against 47.7% ± 4.5.
- **For a person to look at, not part of the check:** on deck 07, kp3 plays Jasmine on 50 of 3,968 chances (1.3%). Deck 07 clears the floor anyway, but it is Dustin's own deck, and it is the kind of thing the flag is for.
- **Tracing changed no game.** A plain `run_screen.py` at 240 games per matchup, same seeds (`run_screen.txt`), gives exactly the same wins against every opponent for brew-06 and brew-06b.

Everything below this line was written and committed (32b3d6a) before any game of this check was played.

---

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
- A hand recount of one flagged card from `<deck>_games.jsonl`. [Amended after the read, on Fable's note: the per-game records written at dc17627 carry no per-card counts, so the recount was done from a re-traced call instead (READ_BY_FABLE.md, item 5). Later floor.py versions write them.]
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
