Decision this changes: whether to fix k3's clock for Sleep and Paralysis in the hope of closing Altaria's 11 to 18-point gaps to Limitless. Don't count on it: counting a sleeping threat as half a turn slower moves Altaria's four cells by −0.2 to +1.0 points, all within noise. Engine commit ca8c0b9, built with `--features status-clock` (legality_scan).

Seeds: the table's deals only. 72,000,000 + pairing × 10,000 + i, i < 500, even i = first-named deck in seat 0.

# Sleep/Paralysis clock test (B2b), Sept 25

**What changed.** k3's damage-aware clock estimates how many turns until each side wins. The diagnostic makes it count the opponent's best threat as ½ turn slower when that threat is in the Active Spot and Asleep (the checkup coin wakes it half the time), and 1 turn slower when Paralyzed. k3 used this clock on both sides. Nothing else changed. Default builds don't have it; the same deals replay k3's games move for move (checked on 120 games when the code was committed).

**Paralysis never comes up.** Of the table's eight decks, only Altaria can cause Sleep (Sing, Hypnoblast, Dark Slumber, Sleepy Lullaby, plus Bad Dreams damage). None can paralyze. So this is a Sleep test only.

| pairing (Altaria's score) | k3 | k3 + Sleep clock | change (95%) | Limitless | games identical to k3 |
|---|---:|---:|---:|---:|---:|
| Altaria v Blaziken | 56.0 | 56.8 | +0.8 (−1.1, +2.7) | 74.2 | 395 of 500 |
| Altaria v Lucario | 56.6 | 57.6 | +1.0 (−0.3, +2.3) | 71.9 | 454 of 500 |
| Altaria v Sceptile | 37.8 | 38.2 | +0.4 (−0.7, +1.5) | 49.1 | 436 of 500 |
| Altaria v Suicune | 39.2 | 39.0 | −0.2 (−1.7, +1.3) | 52.3 | 366 of 500 |
| Blaziken v Lucario (control, no Sleep) | 46.5 | 46.5 | 0 | 44.8 | 500 of 500 |
| Sceptile v Suicune (control, no Sleep) | 56.6 | 56.6 | 0 | 47.2 | 500 of 500 |

"Change" is paired over the same 500 deals, and its 95% range comes from the per-deal differences.

What this shows:

- **It is not Altaria's missing points.** The change played out differently in 9–27% of Altaria's games, but the score barely moved: +0.5 points on average over the four cells. The gap to Limitless in those cells is 11 to 18 points. Averaged over the six cells, the miss against Limitless goes from 11.5 to 11.2 points.
- **The controls did what they should.** With no Sleep in either list, the build plays k3's exact games (500 of 500 on both).
- Sleep still matters to the bot in other ways this test doesn't touch. When Altaria's opponent is asleep, k3 on the Altaria side sees a slower threat, but its search stops at its own turn's end. The value of a sleeping opponent lasting several turns (Bad Dreams damage, stalling) isn't in the clock at all. The Lucario network readout (B2c) is a better place to look for what k3 misses.

## Files

- `status_clock_k3_500.txt`, `.jsonl`: the scan's summary (no rule findings) and one line per game.
- `run_status_clock.sh`: the command (legality_scan built at ca8c0b9 with `--features status-clock`).
- The comparison table above comes from `../per_game_table_2026-09-25/analyze_tables.py --base ../per_game_table_2026-09-25/k3_500.jsonl --other status_clock_k3_500.jsonl`.
