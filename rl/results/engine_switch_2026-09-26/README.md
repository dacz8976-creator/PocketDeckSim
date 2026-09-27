# The engine switch's literal check (Sept 26-27)

Dustin approved making the repaired engine official, on one condition: "for each of the cloud's three fixes, every game that came out differently is one in which the mechanic fired … If any changed game doesn't reach a mechanic, that's a different engine and it waits."

## In plain words

- **Eight of the ten repairs change no table game** (the cloud's replays and the laptop's), so there is nothing to check for them. That includes the random-Energy fix, the third of the cloud's three.
- **Legendary Pulse passes literally.**
  - Every game it changed had a Legendary Pulse end of turn: 3,124 of 3,124 under k3 and 3,197 of 3,197 under kp3.
  - Its mechanic is any Pulse draw, not only one with Hiking Trail in play. That is why it reaches all seven Suicune cells.
- **Promotion timing passes for 7,437 of the 7,461 games it changed. 24 (0.3%) show no end-of-turn or Checkup Knock Out on the board.**
  - **Why, from the code:** the commit (5bab907) changes one engine function (`apply_action_helpers.rs`), and only inside `if lowest_promotion_frame(...)`, which is true only when a promotion is pending after the Checkup, i.e. after an end-of-turn or Checkup Knock Out.
  - The bots' search plays the same engine forward, so a changed choice needs that Knock Out on the board or in a line the search looks at.
  - **Why, from the games** (`divergences.txt`): each of the 24 was traced move by move on both engines to where they first split. At that point a Checkup Knock Out is within the turn's reach in every case:
    - **22 plainly:** a Poisoned, Burned or Asleep Active at 10-30 HP, or a 30-HP Active facing the Poison deck (Hoopa ex / Weezing ex / Deceptive Needle) or Altaria's Bad Dreams.
    - **2 less plainly** (Grovyle 60 v Blaziken's deck; Darkrai ex 90 v Castform 70): it needs an attack plus Burn in the same turn.
  - All 24 are in the Weezing, Altaria (Bad Dreams) and Blaziken (Burn) cells, like the fix's other changes.
  - So the 24 are the same fix acting inside the bots' lookahead, not a different rule.
- **Dustin's ruling (Sept 27): it counts. The rule is restated** (RUN5 "Rules", "Engine repairs").
  - "The second is the engine's rule reaching the game through the bot's imagination, and it's the same fix, not a different one. Excluding it would mean no rule fix that a bot can anticipate could ever pass the check, which is backwards."
  - The guard: "'in lookahead' counts only when both halves are present — a code path gated on the mechanic's condition, and a trace showing the condition reachable within the bot's search depth at the first divergence."
  - These 24 are the worked example.
  - The check (gate in the code, instrumentation, trace to the first divergence) is the standing template for every future repair.
  - **So the repaired engine passes and becomes official.**

## Files

- `instrument_scan.py`: watch-only per-game counters (`pulse`, `eot_ko`). The instrumented 5b75bf9 scan replays the cloud's 5b75bf9 games on 14,000 of 14,000 for k3 and for kp3, so the counters change no play.
- `run_watch.sh`, `watch_5b75bf9_{k3,kp3}_500.jsonl`: the instrumented games.
- `check_literal.py` → `literal_check.txt`: the check, per fix and pilot. It reads the cloud's per-repair files from `claude/pensive-ptolemy-spwc0b`.
- `unexplained.json`: the 24 games.
- `instrument_dump.py`, `trace_unexplained.sh`, `redo_missing.sh`, `dump_*.txt`: move-by-move traces of those games on 5b75bf9 and 5bab907.
- `compare_dumps.py`, `summarize_divergences.py` → `divergences.txt`: where each game first splits, and the board there.
