# Altaria detector network: the reading, set before training (Sept 25)

**Why this run exists:** Altaria is still underrated everywhere, and nothing has explained it.
- Its gap is about +7 against Limitless.
- The Sleep clock was refuted, and every search and pricing lever (k4–k6, option B, kp3, kq3) has left the gap in place.
- The Hydreigon run showed that a per-deck network's value is the audit of what it does differently, not the bot.

Approved by Dustin on Sept 25 as optional, to run only after kd is read (`rl/RUN5.md`, "The plan, revised Sept 25", item 3). **It does not start before kd's reading is in.**

**Setup:**
- **The recipe is the Hydreigon run's**, unchanged: two networks, Altaria and Lucario, trained against each other (80% self-play, 20% past versions), 2,000,000 games, encoding v2.2, the verified 0.7.2 add-on.
- **Settings:** `rl/diag_altaria_v5_settings.json`, a copy of `rl/diag_hydreigon_v5_settings.json` with only the pool and the seeds changed.
- **Seeds, a new block:**
  - training from 14,000,000,000 (each resume adds 100,000,000);
  - evaluation at 18,000,000,000 (k3), 18,100,000,000 (random), 18,200,000,000 (confirmation, and the bars' deals) and 18,300,000,000 (transfer).
- **Launch** (from the repo root, in WSL):
  `RUN=runs/diag-altaria-lucario SETTINGS_FILE=rl/diag_altaria_v5_settings.json bash rl/run_training_v5.sh --stage1`
  This is the Hydreigon run's launch form. Confirm it against `rl/run_training_v5.sh` before starting.
- **Pairing:** Altaria v Lucario. Limitless is 71.9 ± 4.9 (Sept 23 table; 72.4 on scoreboard v2's development half), the tightest band among Altaria's cells. On the table deals, kp3 gives 62.4 and k3 56.6.

**Before anything is read:**
- The pair checks must pass, as for the Hydreigon run (`rl/results/hydreigon_pair_checks_2026-09-24/`, adapted to this pool).
- The readout's identity gates must pass: the run's recorded games replay exactly, and the network re-chooses every recorded move.

## Readings, fixed now

1. **The run's own RUN5 line (reported):** the Altaria network's confirmed margin over k3 on 2,000 paired bar deals; +10 or more counts as a gain.

2. **The key comparison, decisive, fixed before training:** D = (network Altaria v kp3 Lucario) − (kp3 Altaria v kp3 Lucario). Altaria's win %, paired over the run's 2,000 bar deals, bar seats. The kp3 rows use a kp-capable add-on and must pass the same identity gates as the Hydreigon readout's `kp3_rows.py`.
   - **D at +10 or more:** the network plays Altaria better than kp3 even against a Lucario that prices its hidden-text cards. Its habits are then audited (step 3) to name the difference. That difference is a candidate cause of Altaria's gap and a B5 feature candidate, registered and read on its own.
   - **D under +10:** learning finds no large Altaria piloting gain in this matchup. Altaria's gap is then unlikely to be a piloting blind spot that play can reveal. The leads that remain are card or rules implementation (a card check of the Altaria list's texts in the engine) and the population, neither tested by this run.

3. **The audit (descriptive):** the same readout as Hydreigon's, on the same deals, network against kp3:
   - the use rate per offered turn of every attack and ability in the Altaria list (Mega Harmony, Hypnoblast, Dark Slumber, Sing, Sleepy Lullaby, Stampede, Boosted Evolution; Bad Dreams is automatic and is counted as Asleep turns created), split by whether it would knock out;
   - bench size when Mega Harmony is used;
   - benching and attacking on offered turns;
   - the knockout audit;
   - network v network against Limitless, with the Lucario network's own flaws written beside it, as last time.

4. **No follow-up training, whatever it shows.** The run is a detector, not a pilot.
