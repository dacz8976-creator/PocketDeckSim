# Pair checks for the Altaria detector network (Sept 25)

**Result: the gate is met under a corrected C2 completeness rule (Fable's ruling, Sept 25, written before any training result existed; Dustin can overrule). 18 of 18 checks pass under it (`READOUT_corrected.txt`).**
- Under the original rule, 16 of 17 checks pass (`READOUT.txt`, kept unchanged). The one failure is a counting condition this matchup can fail through legal play. It is not a leak.
- **The corrected rule:**
  - Every C2 game in which the probed seat had at least one decision must contribute at least one probed decision.
  - A game in which the probed seat had no decision is counted and listed with its seed and how it ended, and is not a failure.
  - Such a game is one that ends with no error before the probed seat has any choice; the add-on plays single-option moves itself.
- **Why the rule was changed:** C2 exists to test that no hidden card reaches the network's inputs or legal moves, and a game with no decision has nothing to probe. Rerunning on fresh seeds until all 100 games had a probe would pass by luck about 13% of the time and prove nothing.
- **Under it:** 98 games were probed, and 2 had no decision for the probed seat (listed below). There were 0 errors. Hidden invariance held on all 4,971 probed decisions.
- The network has not been trained or read.

**What these are:**
- These are the Hydreigon run's pair checks (`../hydreigon_pair_checks_2026-09-24/`), with only three things changed:
  - the decks: Altaria v Lucario;
  - the seeds: Claude Code's 21,101,000,000 block;
  - where the rules4 identity is looked up: the manifest's `historical_releases`, since the official release moved to main-7fc6ccb on Sept 25. The add-on 0.7.2 is rules4.
- `run_checks.sh` has the commands, and `READOUT.txt` the plain readout.

| check | result |
|---|---|
| C1: 100 recorded k3 decisions replayed through the add-on | **100 of 100 exact**; 2,033 decisions compared; 0 fingerprint mismatches |
| C2: hidden-information invariance | **no change on 4,971 probed decisions** (4,182 random-play, 789 one-k3), for both features and legal moves |
| C2: own-hand positive controls (they must detect a change) | detected (3,097 and 764 changed) |
| C2: every one of the 100 games has at least one probed decision | **98 of 100: FAIL** |
| v2.2 feature check, 20 games | passed |
| Command-line / add-on parity, 8 cases × 2 seeds | **16 of 16 games matched** |

## The two games with no decision to probe

- **The games:** C2 games 83 and 88 (seeds 21,101,100,083 and 21,101,100,088). Both are "one-k3" games: k3 plays Altaria, and the probed seat is Lucario.
- **What happened** (game 83 replayed with the rules4 program and traces):
  - Lucario's opening hand held one Basic, Bonsly (30 HP), so its setup was forced.
  - Altaria went first. Igglybuff used **Sleepy Lullaby** (no Energy cost: 10 damage, and the opponent's Active is Asleep).
  - At the end of the turn, a Benched Darkrai's **Bad Dreams** did 20 to the Asleep Bonsly and knocked it out. Lucario had no other Pokémon, so Altaria won on turn 1.
  - The probed seat never had a choice. The environment plays single-option moves automatically, so the game ended before any decision could be probed.
- **This is legal Pocket play:**
  - `RULES_FOR_AGENTS.md` lines 38–40 (from the official FAQ): the player going first may use a zero-cost attack and play a Supporter on their first turn.
  - `rules/03_status_checkup_timing.md` lines 53–68: Bad Dreams resolves at the end of the turn, before the Checkup's Sleep flip. This was observed in a recorded Altaria battle.
  - The engine follows that order (`engine/src/hooks/core.rs` 414, 618–644).
- **Why it matters for the check:** the Hydreigon pair never produces a no-choice game, so its C2 passed 100 of 100. Altaria's turn-1 Sleep + Bad Dreams kill against a lone 30-HP Basic makes a few such games unavoidable. Rerunning on new seeds would pass only by luck: with 2 games in 100 like this, all 100 of a fresh draw have a decision about 13% of the time.

Game 88 was replayed too: the same line, with Altaria in the other seat. Altaria went first, Sleepy Lullaby put a lone Bonsly to sleep, and Bad Dreams knocked it out at the end of turn 1. Lucario's setup was forced.

## What the gate needed (the laptop's recommendation before the ruling, kept for the record)

- The preset reading (`../../runs/diag-altaria-lucario/PRESET_READING.md`) says the pair checks must pass, as for the Hydreigon run, before anything is read.
- **The laptop's recommendation:** treat the gate as met on substance, with this record kept beside it.
  - What C2 exists to test held on every probed decision: no hidden card changes the network's inputs or its legal moves.
  - The one failed condition counts games, and this matchup fails it through legal play.
  - The run is not read until the ruling.
