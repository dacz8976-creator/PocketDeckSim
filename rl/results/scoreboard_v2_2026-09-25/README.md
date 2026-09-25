# Scoreboard v2 (development half), Sept 25

**What this is:** the 28 Limitless cells rebuilt from the tournament pairings of the **development half only**, then every candidate re-scored on it with the unchanged adoption rule.
- The development half is B6's 63 events. The frozen holdout half was not read.
- Fable's morning reconciliation (section 8) put this first.

**This is clerical and adopts nothing.**
- The frozen table pilot stays k3 until Dustin decides.
- Whether v2 replaces the Sept 23 table as the scoreboard is Dustin's call.
- Diagnostic only; never for ranking decks.

## The cells

Built by `build_v2.py` from `../limitless_skill_model_2026-09-25/development_matches.csv`:
- **1,608 panel matches from 58 development events.** This agrees with B6's 1,918 panel matches minus its 310 mirrors.
- **Match rule** (the same as B6's `analyze.py`): two different panel archetypes, by exact deck ID; decisive or tied; one pairing entry = one match.
- **Cross-check:** Altaria v Blaziken's 25-7-2 equals B6's early plus late rows.
- **Files:** the cells are in `limitless_v2_dev.json`; `cells_v2.txt` lists all 28 against the Sept 23 table.

**No Sept 23 cell differs from its v2 cell by more than binomial noise:** 0 of 28 fall outside the Sept 23 score's own 95% band at v2's n. The samples overlap, so this is descriptive.

The largest moves:

| cell | Sept 23 | v2 (n) |
|---|---|---|
| Hydreigon v Lucario | 54.4 | 63.6 (55) |
| Blaziken v Weezing | 49.0 | 41.2 (17) |
| Blaziken v Hydreigon | 59.0 | 66.7 (24) |
| Blaziken v Sceptile | 82.8 | 76.1 (23) |

**v2 has about half of the Sept 23 table's matches per cell,** because the holdout events are set aside. Its cells are therefore noisier. Several Blaziken cells have fewer than 25 matches.

## Candidates re-scored on v2

Paired, 4,000 replicates, the same per-game files as the Sept 23 readings. `score.py --limitless limitless_v2_dev.json`; the default without that option is unchanged. Decision set: 27 cells, Altaria v Sceptile still quarantined.

| | real error τ̂ | ΔMSE vs k3, 95% | vetoes | rule |
|---|---|---|---|---|
| k3 | 10.9 | reference | | |
| kp3 | 8.6 | −45.8 (−101.1 to +9.2), **not below 0** | Blaziken v Hydreigon +16.5, Hydreigon v Suicune +7.6; Vespiquen deck +2.3 | not adopted |
| b3n1 | 8.5 | −47.3 (−99.4 to +7.1), not below 0 | Blaziken v Hydreigon +12.4; Vespiquen deck +2.1 | not adopted |
| kq3 | 10.5 | −9.6 (−72.1 to +54.0) | six cells; Vespiquen deck +5.9 | not adopted; **vs kp3 +36.2 (+7.4 to +65.5), worse** |

kp3's margin quantity (k3's τ̂ minus kp3's) is +2.36, with a 90% interval of +0.01 to +3.69.

## Reading, plainly

- **kp3's gain looks the same on v2 as on the Sept 23 table:** ΔMSE −45.8 against −45.5, and τ̂ drops 2.3 to 2.4 points on both. But v2 holds half the tournament data, so the interval widens and now crosses zero. On v2 alone, kp3 fails the adoption metric itself, not only the vetoes.
- **The vetoes change with the scoreboard:**
  - Altaria v Hydreigon no longer fires. Its v2 cell is 54.5, which kp3's 47.6 is closer to than the Sept 23 cell was.
  - Blaziken v Hydreigon now fires (+16.5). That cell has 24 matches (±18.9), so this veto is mostly the scoreboard's noise.
  - Hydreigon v Suicune and the Vespiquen deck veto are unchanged.
  - This is the case for Fable's proposed veto refinement: a veto counts only when mixed rows show the changed pilot's own side got worse. It is written for Dustin to pre-register for future tables and does not apply to these readings.
- **kq3 stays reliably worse than kp3 on v2.** The stop on the kq/kv line holds.
- **The frozen holdout half is what settles kp3.** v2's development half alone can't separate kp3 from k3 with 95% confidence, and the plan already reserves the holdout for confirming an adoption. The holdout can be used once.
  - Recommendation: spend it once, on the pilot Dustin chooses, after kd's reading. If kd supersedes kp3, the holdout confirms kd instead, and it is not spent twice.
- **For kd:** its table is read against kp3 on v2, as section 8's reconciliation says.

## Files

| File | What it is |
|---|---|
| `build_v2.py` | Builds the cells; writes `limitless_v2_dev.json` and `cells_v2.txt` |
| `kp3_vs_k3_v2.txt`, `b3n1_vs_k3_v2.txt`, `kq3_vs_k3_v2.txt`, `kq3_vs_kp3_v2.txt` | Full score.py output on v2 |
