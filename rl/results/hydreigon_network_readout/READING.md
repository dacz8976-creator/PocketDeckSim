# Hydreigon network run: the reading (Sept 25)

**Verdict under RUN5's pre-set reading:** the network clears the 10-point line and chips with Hyper Ray, which reads as "learning finds the play k3 misses."
- The Hydreigon network beats k3 at piloting Hydreigon by **+40.8 points** (75.0% vs 34.2%) on the run's 2,000 paired deals.
- It uses Hyper Ray without a knockout on **99%** of the turns it could. k3 does so on **3%** of those turns, on the same deals.

What it found is **two separate k3 blind spots**, and only one of them is pricing.

Diagnostic only. Nothing about the pilot changes because of this; the pilot decision is Dustin's.

## The two blind spots, on the run's own 2,000 deals

| Hydreigon's attack, turns it was on offer | k3 | kp3 | network |
|---|---|---|---|
| Darkness Claw (Mega Absol ex) when it knocks out | 148 used / 166 passed (**47%**) | 1,180 / 11 (99%) | 1,143 / 26 (98%) |
| Darkness Claw without a knockout | 507 / 394 (56%) | 1,068 / 0 (100%) | 605 / 55 (92%) |
| Hyper Ray (Hydreigon) when it knocks out | 1,592 / 15 (99%) | 1,221 / 15 (99%) | 1,584 / 5 (100%) |
| Hyper Ray without a knockout | 25 / 755 (**3%**) | 16 / 485 (**3%**) | 702 / 7 (**99%**) |

1. **Darkness Claw is a pricing blind spot, and kp fixes it.**
   - Darkness Claw's text says the opponent reveals their hand.
   - k3 leaves any move whose text mentions the opponent's hand or deck unpriced: it scores it as if nothing happened (`engine/src/observation.rs`, `hidden_continuation_reason`).
   - So a knockout with Darkness Claw looks like passing the turn to k3, and it takes it about half the time.
2. **The Hyper Ray chip is a readiness-cost blind spot, and pricing doesn't touch it.**
   - Hyper Ray does 130 and discards all Energy from Hydreigon.
   - k3's value for the Active counts only the Energy it has now, so emptying Hydreigon looks expensive. But Roar in Unison (2 [D] from the Zone) plus the turn's attach refills it for the next Hyper Ray.
   - k3 and kp3 both decline the chip about 97% of the time. The network takes it.

## How much of the +40.8 is which (Hydreigon's win %, paired over the same 2,000 deals)

| Hydreigon pilot / Lucario pilot | Hydreigon won |
|---|---|
| k3 / k3 (the bars) | 34.2% |
| kp3 / k3 | 48.0% |
| kp3 / kp3 | 45.1% |
| network / kp3 | 70.3% |
| network / k3 | 75.0% |
| network / network | 57.6% |

- **Pricing (kp3 over k3, Lucario blind): +13.9 ± 2.2.**
- **The network over kp3: +25.2 ± 2.6 against a Lucario that prices Darkness Claw** (+27.0 ± 2.6 against a blind one).
  - This is the decisive row, whose reading was set before it was played. +10 or more means play beyond pricing.
  - It is consistent with the Hyper Ray chip being most of that edge, but not proven. The network also plays differently elsewhere: it benches on 66% of offered turns to k3's 97%.
  - The B2c divergence tool can name the rest later.
- **The blind opponent matters little:** Lucario's own pricing takes 4.8 ± 1.9 from the network and 2.9 ± 2.1 from kp3's Hydreigon. The worry that the network was mainly exploiting a Lucario that can't see Darkness Claw is answered: it wasn't.
- **Against Limitless (Hydreigon v Lucario 54.4 ± 8.0):**
  - k3 v k3 34.2 (off by 20.2).
  - kp3 v kp3 45.1 (off by 9.3).
  - network v network 57.6 (off by 3.2, inside the range).
  - The last is an upper-ish reading, because the Lucario network misses 255 of 3,644 sure knockouts (k3: 4 of 3,416; REPORT.txt).

## Checks behind these numbers

- **The pair checks passed 17 of 17 before anything was read** (`rl/results/hydreigon_pair_checks_2026-09-24/`).
- **Every replay was exact:**
  - 2,000 of 2,000 confirmation games (winner and turns), with the Hydreigon network re-choosing 39,969 of 39,969 recorded moves;
  - the k3 counts, 2,000 of 2,000 against the bar rows;
  - the kp3 counts, 2,000 of 2,000 against the engine's own loop.
- **The kp3 rows need a scratch diagnostic add-on,** because the verified 0.7.2 wheel predates kp. The conditions agreed with Fable:
  - Source: `git archive c7cb688 engine rl/pdl_rl_env` (the add-on source is identical on main and at c7cb688).
  - Build: `cargo build --release` in WSL, at 05:42 on Sept 25.
  - Module sha256: `c048388b4bcf7103375ea0a1e7c9e965be8e350000c3ac873bd111b69e1eae19`.
  - It was never installed, never put in the repo, and never used for a run identity. Its numbers enter no table and not the readings index.
  - Before any kp3 row was played, it replayed the run's own games exactly on 200 deals: k3 v k3 against the bar rows (200 of 200), and network v k3 against the confirmation rows, every move (200 of 200).
- **Reused deals:** the run's own confirmation block (seed 13,200,000,000 + i, i < 2,000). No new seeds.

## What this does not show

- **Nothing about the table.** One cell's pilots are not a table reading, and kp3's table reading is its own file.
- **Nothing about the pilot,** which stays k3 until Dustin decides.
- **Whether the chip matters for other decks.** Mega Burning, Terminating Tail and Diving Icicles also discard Energy. The census in `rl/results/discard_attack_census_2026-09-25/` counts whether k3 declines them too, and its reading was written before its numbers.

## Files

| File | What it is |
|---|---|
| `readout.py`, `readout.txt`, `readout_nvn_games.jsonl` | The pre-set readout: four conditions, Hyper Ray, RUN5's reading |
| `readout_darkness_claw.txt` | The same readout counting Darkness Claw. Only its table 2 counts; its section 3 uses Hyper Ray's wording and thresholds and means nothing for this attack |
| `k3_counts.py`, `k3_counts.txt`, `kp3_counts.txt` | k3's and kp3's own counts on the same deals (the `--bot kp3` option was added after the k3 pass; the k3 path is unchanged) |
| `kp3_rows.py`, `kp3_rows.txt`, `kp3_rows_games.jsonl` | The decisive row and the kp3 rows, on the scratch diagnostic add-on |
| `../../runs/diag-hydreigon-lucario/REPORT.txt` | The run's own report and knockout audits |
