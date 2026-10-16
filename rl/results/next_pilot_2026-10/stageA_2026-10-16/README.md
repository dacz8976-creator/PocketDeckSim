# Stage A: item 7's Kingambit pilot (Oct 16, 2026, laptop)

**Verdict in plain words.** The Blade-aware bot still doesn't play Dustin's Kingambit plan, which is to let other
Pokémon fall so Overlord's Blade grows. Pricing the Blade alone (kmb3) changes nothing. Adding "expected points"
(kmbc3) makes the bot attack with Glimmora more and win a little more against itself. It gets there by letting the
opponent score sooner and bringing Kingambit out later, which is the opposite of his plan. So by
`EXPECTED_KG.md` (sonnet/ky3-blade 0f5f234d) the verdict is **not "pilots Kingambit better"**: part (a) fails,
and part (b) is the brief's "PL2 up while G2 fails" case. The ky3 line is parked until after the Oct 19 reset
(coordinator).

**How it was run.**
- One detached tmux driver (`stageA_driver.sh`) on the laptop's WSL with serial builds (CARGO_BUILD_JOBS 6).
- Engine and code: sonnet/ky3-blade 0f5f234d (blade build) and 81ea31b5 (pilot build).
- Seeds: block 25,000,000,000 – 25,099,999,999, registered in START_HERE at main 35adace7.

## Digests (self-checks)
- **Fast** (t-altaria v t-suicune, 12 games): km3 on both builds, kmb3, kmbc3 and kmbd3 all = `81b572198c04d5d1`.
- **Slow:** ky3_r16_c12_z2_real_t0_poolmeta, `_blade` and `_blade_count` on the blade build, and ky3 poolmeta on the
  pilot build, all = `31d638dbc818b0fa` (= frozen F).
- **Test 8** (80-deal replay, km3 v kmb3, X = 1, i < 5):
  - 74 deals identical.
  - The 6 that differ all first differ at a reachable Blade (count 1-3).
  - 0 violations.
  - `test8.txt`; game logs in `t8_*.jsonl.gz`.
- **The km3 re-run equals v2/runs_km3.** Its 36 differing position-seeds are only the AttachTypedFromDiscard label
  spelling in game 030351 (`km3_diff_check.py`).

## Part (a): 92 positions × 12 seeds × 4 bots (`parta.txt`, `plans.txt`, `pos_*.tar.gz`)
- **kmbc3 passes 2 of 12 counted positives, against the 6 needed, so (a) fails.**
  - The two passes are case 10 (203719 t07) and case 11 (210823 t08). In both it promotes Glimmora and uses Venomous Hit in 12/12, against km3's 0/12.
  - Case 9: it skips Ilima in 9/12, but puts the Energy on the dying Regigigas. Case 14: 6/12.
  - The Rare Candy and knockout keep checks hold.
- **kmbc3 moves against his plan at these turns:**
  - Energy goes to the Active Regigigas instead of Kingambit at 203719 t09, 203719 t11 and 210823 t06.
  - The Glimmet placement is dropped at 010706 t13 and at 203719 t13 (a keep-check line).
- **kmb3 changes 0 positions; kmbd3 changes 4.**

## Part (b): self-play, 6 arms × 2,000 games, X = 0, his played list (`partb.txt`)
**kmbc3 − km3 per deal, seat 0 / seat 1:**

| Measure | Seat 0 | Seat 1 |
|---|---|---|
| PL1 | +1.9 ± 1.8 | +2.0 ± 1.8 |
| PL2 | +3.6 ± 2.3 | +1.9 ± 2.0 (crosses 0) |
| Win | +4.3 ± 2.2 | +1.5 ± 2.1 |
| P2 | +5.5 | +4.9 |
| P3_broken | −5.0 | −5.5 |

**G2 fails:**
- The opponent's points at the first Blade rise by +0.12 ± 0.08 / +0.09 ± 0.08.
- Blade by turn 6 falls by 6 / 4 points.

**Other arms:**
- The Blade-aware opponent arm (`_vkmb3`) shows the same signs.
- kmbd3: P2 +4 / +3.5, PL1 −1.1 ± 0.8 (seat 0).
- kmb3: about 0.

The game logs are **not committed** (about 79 MB each). `OMITTED.txt` gives their sha256 and line counts. They stay on
the laptop's WSL at `~/stageA/out/`, and they replay exactly from the registered seeds.

## Blind second reader for cases 9-15 (`blind_read/`)
- **Setup:**
  - A clean folder: positions, his moves, km3's 12 plans, card texts and his plan quotes.
  - No first read, no EXPECTED classes and no case labels.
  - Sonnet on the API credit worker.
- **Run 2 (`blind_read/run2/READ.md`) is the one that counts.** It has complete card texts and agrees with the first read on all 7, so cases 9-15 count (12 counted positives in all). Nothing went to Dustin.
- **Run 1 (`blind_read/run1_degraded/`) is degraded and kept only as a record.** My prep script looked cards up as "Name SET NNN", so no opponent card texts reached it. It agreed on 6 and called T6 unclear for lack of damage data.
- **Turn map** (kept outside the reader's folder):

| Blind turn | Game and turn |
|---|---|
| T1 | 010837 t05 |
| T2 | 210823 t08 |
| T3 | 203719 t07 |
| T4 | 210041 t06 |
| T5 | 203719 t11 |
| T6 | 010706 t11 |
| T7 | 014423 t03 |

## Files
- **Scripts:** `stageA_driver.sh`, `kg_one.sh`, `test8_compare.py`, `parta_compare.py`, `analyze_kg.py`, `plans.py`, `km3_diff_check.py` and `blind_read/blind7_prep.py`.
- **Logs:** `stageA.log` and `logs/` (builds).
