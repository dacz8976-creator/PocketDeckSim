# kp3 confirmed on the frozen holdout (Sept 25, 2026)

**In plain words: kp3 is confirmed as the pilot.**
- On the half of the real tournament data kept aside and never used for any decision (1,948 matches from 57 events), kp3 plays closer to real results than k3, by about as much as on the development half.
- All four conditions set before the data was opened hold. Dustin's earlier adoption of kp3 by override becomes a confirmed adoption.
- **Plainly, one caveat:** on the holdout alone, the interval that decides condition 4 clears zero (+0.18). The per-tournament interval beside it does not quite (−0.22). The rule named the first one as the test and the second as reported only, so this is not a failure. But it shows the holdout's margin is not far from noise on its own.

**What was done, in order:**
- The rule was written and pushed before anything was opened: conditions (1)–(3) at 10c4e66, (4) at e45eb50, and a reporting note at b1740b4.
- Dustin said "Kp3" in the laptop session's chat.
- The mixed rows were complete and checked first. kp3 against k3, all 28 pairings, both directions, 28,000 games, no rule findings, on the official legality_scan (`../kp3_mixed_rows_2026-09-25/`). Their Vespiquen cells replay this morning's Vespiquen mixed rows move for move, 7,000 of 7,000.
- The holdout was opened once, at **2026-09-25T19:49:50Z** (`OPENED.txt`), by `run_confirmation.sh`. Its counting script first reproduced the v2 development cells exactly from the same file.

## The four conditions (decision set of 27 cells, Altaria v Sceptile quarantined)

| | development half | holdout half | pooled (both) | condition | holds? |
|---|---:|---:|---:|---|---|
| real error τ̂, k3 → kp3 | 10.9 → 8.6 | 10.9 → 8.6 | 11.5 → 9.3 | | |
| ΔMSE kp3 − k3 (points²) | −45.8 | **−44.6** | −44.8 | (1) same sign on the holdout as on development | ✔ |
| ΔMSE 95%, binomial | −101.1 to +9.2 | −94.3 to +5.7 | **−85.5 to −4.9** | (2) pooled interval entirely below 0 | ✔ |
| ΔMSE 95%, by event | −100.9 to +8.2 | −96.4 to +15.5 | **−86.5 to −2.5** | (2) the same, by event | ✔ |
| vetoes that count (rule v2) | none | **none** | none | (3) no veto on the holdout cells | ✔ |
| τ̂ margin k3 − kp3 | +2.36 | **+2.29** | +2.15 | (4) holdout ≥ +1.18 | ✔ |
| its 90% interval, binomial | +0.01 to +3.69 | **+0.18 to +3.59** | +0.48 to +3.37 | (4) entirely above 0 | ✔ |
| its 90% interval, by event (reported only) | +0.00 to +3.74 | −0.22 to +3.59 | +0.44 to +3.40 | not a gate (agreed before opening) | — |

**Vetoes on the holdout cells:**
- **Altaria v Hydreigon** (miss grows 10.2): an investigation item. With kp3 on one side only, neither side gets worse. Altaria's side is +3.0 ± 4.3 and Hydreigon's +14.2 ± 5.1; the cell moves because Hydreigon is piloted much better.
- **Hydreigon v Suicune** (+7.6): never counts. The holdout band is ±16.4, wider than ±15.
- **Vespiquen deck** (+2.3): an investigation item. Its own side is +2.9 ± 1.5, and its opponents' side +5.6 ± 1.5.

**What the other outputs say:**
- The holdout alone, like the development half alone, has too few matches for ΔMSE's own interval to clear zero. That is why the rule combined its own sign and size (1, 4) with the pooled interval (2).
- The generic "do not adopt" line in `kp3_vs_k3_holdout.txt` is score.py's adoption rule applied to half the data. It is not this confirmation rule.
- **Condition (2) was close to guaranteed.** The pooled table is essentially the Sept 23 table rebuilt from pairings. Conditions (1) and (4), the holdout's own sign and size, carry the real test, and both hold.

## What the full mixed rows add: kp3 is a better pilot for every deck

With kp3 on one deck only, against k3 on both sides, on the same deals, pooled over each deck's cells:

| deck | own side, kp3 on it | its opponents' side, kp3 on them |
|---|---:|---:|
| Altaria | +6.2 ± 1.8 | +2.6 ± 1.7 |
| Blaziken | +6.0 ± 1.6 | +6.9 ± 1.4 |
| Hydreigon | +15.5 ± 1.8 | +3.1 ± 1.5 |
| Lucario | +4.6 ± 1.5 | +4.3 ± 1.4 |
| Sceptile | +1.7 ± 1.2 | +6.0 ± 1.6 |
| Suicune | +0.2 ± 1.2 | +6.6 ± 1.6 |
| Vespiquen | +2.9 ± 1.5 | +5.6 ± 1.5 |
| Weezing | +3.8 ± 1.5 | +5.9 ± 1.5 |

**What this shows:**
- No deck is piloted worse by kp3. Seven of eight play better beyond noise on their own side, and Suicune is level.
- The table's remaining misses are not kp3 hurting anyone. They are decks it helps more than others, set against each deck's own open gaps. On the holdout cells:
  - Vespiquen stays about 11 points under Limitless (45.8 against 57.1).
  - Sceptile stays about 12 points over it (58.5 against 46.6).
  - Altaria stays about 4 under (50.9 against 55.1).

## What this changes

- **kp3 is the confirmed pilot.** It is the screen's pilot on both sides, and the table pilot used to judge new candidates. k3 stays the reproduction reference.
- **The holdout is spent.** Any later candidate (kpr, B3) is judged on the development half by the adoption rule and confirmed only on events after the freeze date.
- **Not changed:**
  - kp3 still fails PASS: real error 8.6 against the 5.5 target. Sceptile v Vespiquen is still off by more than 10 beyond noise, and Sceptile and Vespiquen are still off by more than 6.
  - The screen's ranking hold stays as Dustin set it.

**Files here:**
- `kp3_vs_k3_holdout.txt`, `kp3_vs_k3_pooled.txt`, `kp3_vs_k3_development.txt`: score.py outputs.
- `limitless_holdout*.json`, `limitless_pooled*.json`: the cells and the per-event cells.
- `OPENED.txt`: the opening time and counts.
- `build_holdout.py` and `run_confirmation.sh`: the code.
