# kd3 against kp3: paired whole-table reading under veto rule v2 (Sept 25)

**In plain words: kd3 is not adopted, and kp3 stays the pilot.**
- kd3 adds the defender's Weakness and lasting damage cuts to kp3's clock. It does not fit real play better than kp3. Its point estimate is slightly worse, and the difference is within noise.
- With kd3 on one deck only, several decks play slightly worse than under kp3, beyond noise: Lucario, Hydreigon and Vespiquen. So kd3 is a slightly weaker pilot, not a fix.
- The Vespiquen gap it was aimed at narrows by 1.1 points, within noise. That gain comes from Vespiquen's opponents playing worse, not from Vespiquen playing better.

**Inputs:**
- **kd3's table:** the cloud's `rl/results/kd_2026-09-25/kd3_500.{txt,jsonl}` on branch `claude/pensive-ptolemy-spwc0b` (c416591; README 1fe625a). It has 28 pairings × the table's 500 deals, and no rule findings.
- **The code:** engine commit 0c0e7f9, whose read passed (`kd3_tier1_read.md`).
- **kp3:** `../public_pricing_2026-09-25/kp3_500_*`, the same deals.
- **Mixed rows:** `../kd_mixed_rows_2026-09-25/` has 28,000 games, kd3 on one side only, on the same deals.
  - They were run on a laptop build of 0c0e7f9.
  - kd3 from that build plays the cloud's pairing 1 identically, 500 of 500.
  - kp3 from it plays pairings 0–2 of the reference identically, 1,500 of 1,500.
- **The rule and the Limitless cells:**
  - Veto rule v2, pre-registered Sept 25, with the wide-band threshold fixed at exactly 15.0 before this table.
  - Scoreboard v2's development cells, with the per-event interval alongside the binomial one.
- **Output files:** the deciding output is `kd3_vs_kp3_v2.txt`. Descriptive only: `kd3_vs_k3_v2.txt` and `kd3_vs_kp3_sept23.txt` (the Sept 23 cells).

## The decision (decision set of 27 cells, Altaria v Sceptile quarantined)

| | kp3 | kd3 |
|---|---:|---:|
| real error τ̂ | 8.6 | 9.4 |
| favorites right (reported only) | 20/27 | 17/27 |
| correlation (reported only) | 0.71 | 0.67 |

- **ΔMSE, kd3 − kp3: +14.2 points².** The 95% interval is −11.1 to +39.6 (binomial) and −10.0 to +39.5 (by event). It is not below zero, so the rule says **do not adopt**.
- **Real error, kp3 − kd3: −0.79 points.** The 90% interval is −1.49 to +0.30, far inside the E = 3 margin. kd3 buys nothing measurable.
- **Vetoes:** none fire, cell or deck.
- **PASS:** neither bot. Sceptile v Vespiquen is the one cell over 10 beyond noise, and Sceptile and Vespiquen are the decks off by more than 6, for both bots.
- **On the Sept 23 cells** (descriptive): the same picture. ΔMSE is +11.4 (−9.6 to +31.3), and no vetoes fire.
- **Against k3 on v2** (descriptive): ΔMSE is −31.7 (−86.3 to +23.0), not below zero.
  - Real error improves 1.57, with a 90% interval of −0.55 to +3.14.
  - kp3 did better against k3 on v2: −45.8, with a 95% interval of −101.1 to +9.2.

## What the mixed rows say

The mixed rows compare each deck's own score with kd3 on one side only against kp3 on both sides, on the same deals, pooled over the deck's cells:

| deck | own side, kd3 on it | its opponents' side, kd3 on them |
|---|---:|---:|
| Altaria | +0.0 ± 1.0 | −0.3 ± 1.1 |
| Blaziken | −0.7 ± 1.1 | −0.6 ± 1.0 |
| Hydreigon | **−1.1 ± 0.9** | −0.3 ± 1.1 |
| Lucario | **−2.2 ± 1.4** | +0.4 ± 1.1 |
| Sceptile | −0.5 ± 0.9 | −0.6 ± 1.2 |
| Suicune | +0.2 ± 0.9 | **−1.6 ± 1.1** |
| Vespiquen | **−1.5 ± 1.5** | **−2.3 ± 1.4** |
| Weezing | −0.3 ± 1.2 | −0.7 ± 1.2 |

**What this shows:**
- **kd3 is a slightly weaker pilot than kp3 for several decks.** No deck is piloted better beyond noise.
- **Lucario is hurt the most.** It drops −6.6 ± 4.1 against Suicune and −6.2 ± 4.4 against Vespiquen. The tier-1 read predicted trouble here.
  - When a Bench-only sniper is the main threat, kd prices benched victims by sniping even when the Active attacker is faster.
  - It can also lean toward powering the sniper.
  - Lucario runs Hitmonlee.
  - Hydreigon (−5.4 against Vespiquen) and Vespiquen (−5.2 against Altaria) have the other large single-cell drops.
- **Vespiquen's small gain is its opponents playing worse.**
  - Vespiquen's deck average moves 45.8 → 46.9, against 56.6 real.
  - With kd3 on Vespiquen's side only, Vespiquen does worse (−1.5). With kd3 on its opponents only, they do worse (−2.3).
  - This is the mirror of the kp3 reading, where the opponents improved. kd's defender modifiers don't reach Vespiquen's own weakness.
- **Lucario's deck average moves toward Limitless** (52.0 → 50.1, against 50.4), but because Lucario is piloted worse. It is an example of a table cell moving the right way for the wrong reason, which is what the mixed rows are for.

## What the verdict refutes (Fable's attribution note, agreed)

- kd is a bundle: Weakness and reductions in the clock, the fallback attacker, reach, defender bonuses, and the promotion order.
- The one clear signal in the mixed rows is Lucario (−2.2; −6.6 against Suicune, −6.2 against Vespiquen). It fits the sniper-as-threat pricing, which comes from the **reach** sub-change, not the Weakness term.
- So this reading refutes **the bundle as built**, not Weakness pricing as such. Reach is the suspect if anyone ever revisits kd.
- No split run now: nothing at stake would change a decision.
- **On B3 (corrected at Dustin's word, relayed by Fable):** the Weakness term stays available as a position feature for B3. B3 is the Texel-style fit the plan describes:
  - It regresses **game outcome on position features, over positions from self-play** (k3 or kp3 games).
  - It is **never a fit against the Limitless table.** Tuning to the table was dropped on Sept 24, because it overfits 28 cells and has no value for brews.
  - The table only judges the fitted evaluation afterwards, by the adoption rule and the held-out decks. The weights are then left alone.
  - When B3 is built, it is registered as its own candidate with the overfitting answer written into its registration, not as a sub-clause of this negative result.

## Known limits of kd3 (for the record, not a reason for the verdict)

- Effects that last a turn are left out: attack-stored cuts, Metal Core Barrier, turn effects.
- The coin-flip exemption misses attacks whose damage is queued as a separate step (the tier-1 read). No table deck has a coin-flip damage Ability.
- The sniper-as-threat pricing and the two stated "never" limits (`kd3_tier1_read.md`, section 4). The first is visible in Lucario's mixed rows above.
- The one-attacker gap flagged by the external review was closed before the table (97ca8f4).

## What follows (Dustin decides)

- **The pilot stays kp3.** It is the screen's pilot on both sides and the working table pilot.
- **The holdout.** The plan spends it once, on the pilot Dustin picks after this reading. The laptop recommends kp3. If he agrees, the next step is scoring kp3 against k3 on the frozen holdout half.
- **kd's line stops here as a pilot candidate.** Its per-victim damage function stays in the code, since k3, kp3 and kq3 are unaffected. A fix to the sniper pricing would be a new registered code, not kd3.
- **kpr** (projected readiness, from the Hydreigon network's Hyper Ray finding) is the next candidate. It builds on kp, not kd.
- **The optional Altaria detector network** can start now that kd is read. It is read against kp3 afterwards, as approved.
