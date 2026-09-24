# Review request for Astra — encoding v2.2 (add-on 0.6.0) and the per-deck trainer

**Audit only, please: no source changes, no training, nothing on Dustin's laptop.** Everything below is in `Boss Folder/rl-feasibility-2026-09-18/`. Nothing under `deckgym-fork-s193/src/` was touched.

## What changed

**1. The add-on, `pdl_rl_env` 0.5.0 → 0.6.0** (`pdl_rl_env/src/v2.rs`, `pdl_rl_env/src/lib.rs`). A third encoding name, `"v2.2"`, with 194 numbers per move instead of v2.1's 193:
- Slot 13, which in v2.1 held the threat "certain" flag, now holds **how many Pokémon I would have in play after this move**, divided by 4. The flag is gone: it only ever meant "the opponent's current Active's attacks could be simulated", and the lines that actually kill the bot (evolving, switching in a benched attacker, a Supporter first) were never in it.
- New slot 14: **if my Active were knocked out right after this move, would I lose** — true when nothing is left in play besides it, or when that knockout would give the opponent their third point.
- Asleep/paralyzed and poisoned/burned move from 14/15 to 15/16.
- Both new numbers are probability-weighted over the move's outcomes, like every other number in the row, and read only from `PlayerObservation`-visible state plus the engine's own forecast of the move.
- `"v1"` and `"v2.1"` are unchanged and must stay so; `"v2"` (0.4.0's spelling) is still refused.

**2. The trainer, `train_v3.py` → `train_v4.py`** — run 3's program with one thing changed: **one network per pool deck** instead of one shared network. Each seat in a training game is piloted by its own deck's network, so a game produces training rows for two networks, each only from its own side's decisions. Five replay buffers, five sets of training credit, per-network floors, per-network levelling off, per-network confirmation. Checkpoints and resume files are per deck: `ckpt_500k_blaziken.npz`, `resume_<stamp>_blaziken.npz`. `audit_v4.py`, `transfer_v4.py`, `report_v4.py` follow, and `report_inputs()` now fingerprints one checkpoint file per network rather than one per run.

## What I already checked (so you don't have to)

- `v2_2_checks.py` (in the folder; writes `results/v2_2_checks.txt`) — sizes; the first 13 numbers and the shifted status flags identical to v2.1 in 9,882/9,882 move rows; and both new numbers checked **against the real game**, by playing the move on a copy of the position and comparing: in-play count 8,034 moves, 0 wrong; "losing the Active loses the game" 6,810 moves, 0 wrong. Skipped classes are counted and named in the file.
- v1 and v2.1 are **byte-identical** between 0.5.0 and 0.6.0: the same 1,762 decisions encoded under both hash the same (`results/v2_2_checks/`, dumps and the script that made them).
- A full small practice run in the cloud: trained, killed mid-run, resumed, finished with every network levelled off, then confirmations, audit (10 checkpoint audits, 0 replay problems), held-out test, REPORT.txt. Finished steps skip on re-run; changing one network's weights makes only that network's audit redo itself.

## Where I would most like your eyes, in priority order

1. **Do the two new numbers ever see something the bot may not?** Anything in the forecast that reveals the opponent's hand, deck order or a face-down card would poison the whole run.
2. **Training-credit and buffer isolation across the five networks.** A network must learn only from the decisions it made. I'd like the cross-contamination case checked specifically: the past-checkpoint seat, and the two-decks-in-play refresh that only reloads the networks in the current game.
3. **Crash and resume with five networks.** Run 3's guarantee was that an interrupted save can never pair newer weights with an older game count; I kept the mechanism but there are now five files per save.
4. **Seeds.** Run 3 fixed worker seed overlap with per-epoch blocks plus a unique claimed game number. Please check that still holds with five networks and the past-checkpoint seat.
5. **The verdict.** `finish()` picks each network's best confirmed checkpoint and then judges every matchup by the pass rules on the design page. A wrong pick or a mis-scored matchup would be believed.

The design page section is "Run 4 design — one network per piloted deck" in `FEASIBILITY.md`, with the pass rules, floors and stopping rules it is meant to implement.
