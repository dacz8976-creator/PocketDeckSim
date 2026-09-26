# kpr3 mixed rows, Sept 26 (written before any of them ran)

**What these are for:** the laptop reads kpr3 against kp3 under rule v2 (`rl/results/table_readings_2026-09-24/score.py --rules v2`).
- Under v2, a veto counts only when mixed rows on the same deals show the changed pilot's own side got worse beyond paired noise.
- A mixed row has kpr3 on one deck and kp3 on the other.
- These rows cover all 28 pairings in both directions, on the table's first 500 deals. That is the same design as kd3's (`../kd_mixed_rows_2026-09-25/`), fixed here before the laptop reads the table, so no choice depends on which vetoes fire.
- They also answer the attribution question: is kpr3 better at piloting a deck on its own side (Hydreigon's Hyper Ray chip), or does its table move come from the opponents' side?

**The table:** the cloud's `rl/results/kpr_2026-09-25/` on branch `claude/pensive-ptolemy-spwc0b` (aa87fa3), engine e09fb46.

**Build:** `build_kpr_scan.sh`.
- It runs `git archive e09fb46 engine decks` into `/home/dacz8976/engine-kpr-e09fb46`, then `cargo build --release --example legality_scan`, and records the sha256.
- This is not the official engine; it is used for these rows only.
- `decks/research` is identical at e09fb46 and at main.

**Checks before the rows are used** (`run_kpr_mixed.sh`):
1. **A kp3 spot replay of pairings 0-2 on this build**, compared move by move with `../public_pricing_2026-09-25/kp3_500_*` (`spot_kp3_p0-2_compare.txt`). kp3 plays the other side of every mixed game. The cloud already replayed kp3 in full at 53638a7, and on 40 deals at e09fb46.
2. **kpr3 v kpr3 on pairing 1 from this build**, compared move by move with the cloud's `kpr3_500.jsonl` (`kpr3_replay_p1_compare.txt`). This confirms the kpr3 here is the table's kpr3.
- If either check fails, the rows are not used.

**How they are read:**
```
score.py --rules v2 --old kp3 --new kpr3 --old-games kp3_500_* --new-games kpr3_500.jsonl --mixed mixed_kpr3_first.jsonl mixed_kpr3_second.jsonl --limitless limitless_v2_dev.json --limitless-events limitless_v2_dev_events.json
```

**Files:**
- `build_kpr_scan.sh`, `run_kpr_mixed.sh`: the commands.
- `identity.txt`: the scan's sha256.
- `spot_kp3_p0-2*`, `kpr3_replay_p1*`: the two checks.
- `mixed_kpr3_first*`: kpr3 on the first-named deck.
- `mixed_kpr3_second*`: kpr3 on the second-named deck.
- `timing.txt`: wall times.
