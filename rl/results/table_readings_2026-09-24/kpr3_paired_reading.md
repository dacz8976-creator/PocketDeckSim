# kpr3 against kp3: paired whole-table reading under veto rule v2 (Sept 26)

**In plain words: kpr3 is not adopted, and kp3 stays the pilot. But the fix it was built for worked, and moved the target cell toward real results.**
- **Did kpr3 do what it was built for? Yes.** In Hydreigon v Lucario, the cell the Hydreigon network study used, Hydreigon now uses Hyper Ray without a knockout on 91% of the turns it can: 117 of 129 on the table, 92% with kpr3 on Hydreigon only.
  - kp3 does so on 1% (1 of 128), k3 on 3%, and the network on 99%.
  - The cell moved **+8.8**, from 43.8 to 52.6, toward Limitless (v2 63.6 ± 12.7; the Sept 23 table 54.4 ± 8.0).
  - **+7.8 ± 4.4** of that comes from Hydreigon's own pilot (kpr3 on Hydreigon, kp3 on Lucario).
- **The finding (Dustin's question, Sept 26):** the chip is real and good, but in that cell it is worth about **+8**. The Hydreigon network beat kp3 by **+25.2** there (`../hydreigon_network_readout/READING.md`).
  - So the chip is about a third of the network's edge. The other two-thirds is other habits, not yet named.
  - The network also benches far less, 66% against 97%. But the Altaria study found its benching gap was a side effect, not a cause, so that is not assumed.
  - The two figures come from different deals: the network run's 2,000 against the table's 500, both paired against kp3.
- **So kpr3 fails for a different reason than its target.** The chip works. The failure is that kpr3's readiness term changed the play of every deck and made four of them worse.
- **What kpr3 was.** kp3 with one change. When it judges how ready the Pokémon in the Active Spot is, it counts the Energy on its way by that Pokémon's next attack: the Energy Zone this turn and next, and Abilities that attach Energy (some of them from the discard pile). It was built for Hydreigon. kp3 treated Hyper Ray, which discards all of Hydreigon's Energy, as crippling, so it almost never used it without a knockout. kpr3 sees next turn's refill.
- **What happened.** kpr3 does what it was built for. Hydreigon now uses Hyper Ray without a knockout on 90% of the turns it can, against kp3's 21%.
  - But the whole table fits real play clearly worse. The typical miss is 12.2 points, against kp3's 8.6.
  - This is not bad luck: the rule's test lands entirely on the wrong side of zero. So the rule says "do not adopt" before any other check is looked at.
- **It was not a Hydreigon-only change.** It changes the play in 94% of the table's games, in every deck.
  - With kpr3 on one deck at a time against kp3, it pilots Hydreigon better (+3.8 points), but Weezing, Lucario, Altaria and Vespiquen worse. Head to head it scores 48.8% against kp3.
  - Blaziken and Suicune gain on the table mainly because their opponents are piloted worse.
- **What it means.**
  - kp3 stays.
  - The readiness idea is kept as a feature for B3, where a fit on self-play games sets its weight instead of the hand-set one.
  - There is no follow-up run splitting kpr into its parts.
  - kt is built on kp3.

**Inputs:**
- **kpr3's table:** the cloud's `rl/results/kpr_2026-09-25/kpr3_500.{txt,jsonl}` on branch `claude/pensive-ptolemy-spwc0b` (head aa87fa3, engine e09fb46). It has 28 pairings × the table's 500 deals, and no rule findings.
  - It was copied out with `git show`. Its sha256 is 19b95ae0…5bde0, the same blob Fable read.
  - The laptop's copy for the mixed rows (`/home/dacz8976/engine-kpr-e09fb46/kpr3_500_cloud.jsonl`) has the same hash.
- **kp3:** `../public_pricing_2026-09-25/kp3_500_*`, the same deals.
- **Mixed rows:** `../kpr_mixed_rows_2026-09-26/` has 28,000 games, kpr3 on one side only. The design was fixed in its README before any row ran. Both identity checks passed (section 6).
- **The rule and the Limitless cells:**
  - Veto rule v2, pre-registered Sept 25, with the wide-band threshold at exactly 15.0.
  - Scoreboard v2's development cells (`../scoreboard_v2_2026-09-25/limitless_v2_dev.json`), with the per-event interval (`limitless_v2_dev_events.json`, 58 events).
- **Fable's independent review:** `../fable_reviews_2026-09-26/` (`kpr_readout_review.md`, `kpr_recompute.md` and their scripts). This reading follows its eight points.
- **Output and helper files:** all in `kpr3_reading/` (listed at the end).
  - The deciding output is `kpr3_reading/kpr3_vs_kp3_v2.txt`.
  - Descriptive only: `kpr3_vs_kp3_sept23.txt` and `kpr3_vs_k3_v2.txt`.
- **No games were played for this reading.** It is Python over existing files only; a B2e build was using the CPU.

## 1. The decision (rules v2; scoreboard v2, decision set of 27 cells, Altaria v Sceptile quarantined)

The deciding command, from `rl/results` (`kpr3_reading/run_score.sh`):

```
score.py --rules v2 --old kp3 --new kpr3 --old-games public_pricing_2026-09-25/kp3_500_worst5.jsonl public_pricing_2026-09-25/kp3_500_rest.jsonl --new-games <kpr3_500.jsonl> --mixed kpr_mixed_rows_2026-09-26/mixed_kpr3_first.jsonl kpr_mixed_rows_2026-09-26/mixed_kpr3_second.jsonl --limitless scoreboard_v2_2026-09-25/limitless_v2_dev.json --limitless-events scoreboard_v2_2026-09-25/limitless_v2_dev_events.json
```

| | k3 (reference) | kp3 | kpr3 |
|---|---:|---:|---:|
| mean squared miss (points²) | 177.5 | 131.7 | 206.4 |
| real error τ̂ | 10.9 | 8.6 | 12.2 |
| favorites right (reported only) | 22/27 | 20/27 | 15/27 |
| correlation (reported only) | 0.64 | 0.71 | 0.50 |

- **ΔMSE, kpr3 − kp3: +74.7 points².**
  - 95% interval: +28.4 to +123.1 (binomial), +29.9 to +123.2 (by event).
  - The whole interval is above zero, so the rule's verdict is **do not adopt, on the metric**. The vetoes were not consulted for the decision.
- **Real error, kp3 − kpr3: −3.60 points.**
  - 90% interval: −4.37 to −1.45 (binomial), −4.34 to −1.60 (by event).
  - kpr3 is worse by more than a point on the whole interval.
- **PASS:** neither bot.
  - kpr3 has two cells over by more than 10 beyond noise, Hydreigon v Suicune and Sceptile v Vespiquen.
  - Four decks are off by more than 6: Altaria, Hydreigon, Sceptile and Vespiquen.
- **Independent recompute** (`kpr3_reading/recompute.py`, numpy, a different random stream; not score.py's code):
  - Every point estimate is identical.
  - ΔMSE 95%: +26.5 to +124.5 (binomial), +28.8 to +124.1 (by event).
  - Margin 90%: −4.35 to −1.37 (binomial), −4.34 to −1.57 (by event).
  - Fable's recompute got +27.4 to +122.7 and −4.33 to −1.44. The three differ by 2 points² at most, which is resampling noise.
- **All 28 v2 cells (descriptive):**
  - ΔMSE +72.1 (+25.9 to +117.8; by event +26.6 to +119.0).
  - Margin −3.55 (−4.22 to −1.34).
- **Sept 23 cells (descriptive):**
  - Decision set: ΔMSE +66.5 (+31.6 to +101.6); τ̂ 9.3 → 12.4; margin −3.07 (−3.89 to −1.56).
  - All 28: +64.1 (+31.3 to +98.4).
  - The same picture as on v2.
- **Against k3 on v2 (descriptive):**
  - ΔMSE kpr3 − k3 is +28.9 (−43.3 to +104.0; by event −37.6 to +97.0).
  - The real-error margin is −1.25 (90% −3.26 to +1.20).
  - kpr3 is not measurably better than k3 on the table. kp3 was −45.8 against k3.

**Vetoes, for the record only** (the verdict does not use them). With the mixed rows in, score.py reads the v2 vetoes as follows:
- **Cells:**
  - Four of the five cells that were awaiting mixed rows now count: Altaria v Suicune (Altaria piloted worse), Blaziken v Lucario and Lucario v Suicune (Lucario piloted worse), and Suicune v Vespiquen (Vespiquen piloted worse).
  - Altaria v Hydreigon is an investigation item. Neither side is worse; Hydreigon's side is better.
  - The three band-excluded cells never count.
- **Decks:**
  - Four of the five deck vetoes count: Altaria, Vespiquen and Weezing through their own sides, and Blaziken through its opponents' sides.
  - Hydreigon's veto, the one the cloud's readout pointed at, does **not** count under v2, because kpr3 pilots Hydreigon better, not worse. It is an investigation item.
- So the vetoes would block adoption too. They are not needed.

## 2. Which table

This decision is on scoreboard v2's 27-cell decision set. The cloud's "mean squared miss 176.1 against kp3's 112.2" is a different claim: the Sept 23 table pooled over all 28 cells, including the quarantined cell. It used the Limitless cells rounded to one decimal; the exact cells give 176.5 against 112.4.

## 3. The footprint, and the census prediction

| | games whose moves differ from kp3's | games whose result differs |
|---|---:|---:|
| kpr3 table (kpr3 on both sides), of 14,000 | **13,117 (93.7%)** | **4,052 (28.9%)** |

- **For scale:** kp3 and k3 play identical games on 1,242 of the 14,000 deals. kpr3 and kp3 do on 883.
- **By cell:** the least-changed cell is Blaziken v Sceptile, 413 of 500 games; the most-changed are Altaria v Vespiquen and Vespiquen v Weezing, 492 of 500 each.
- **With kpr3 on one deck only** (the mixed rows, that deck's 3,500 games), the share of games that change:
  - Altaria 89.3%, Vespiquen 85.6%, Hydreigon 84.5%, Weezing 82.9%, Lucario 80.5%, Blaziken 76.8%, Suicune 73.9%, Sceptile 64.7%.
  - Results change in 12.3% (Sceptile) to 27.3% (Altaria) of games.
  - The change reaches every deck on its own, not just Hydreigon.
- **The reserve route is closed.** Section 8 proposed it, pending Dustin's OK, for changes the table can barely see. It has five conditions, (a) to (e); kpr3 fails each of the first three:
  - (a) The footprint trigger is under 15%; kpr3's is 93.7%.
  - (b) The no-harm bound needs the margin's 90% lower end at −1.0 or above, and no veto counting under v2; kpr3's bound is −4.37, and eight vetoes count (four cells, four decks).
  - (c) No deck's own side may be worse in the mixed rows; four decks' are.
- **The census prediction missed.** The discard-attack census said a projected-readiness term would "mainly change Hydreigon" (`../discard_attack_census_2026-09-25/READING.md`). Section 8 recorded it as "kpr's footprint on this table is essentially Hydreigon".
  - That is recorded here as a **missed prediction**. Seven of eight decks' table averages move beyond noise, and kpr3 changes 65–89% of the games of whichever deck it pilots.
  - The cloud README's "as the registration warned" is right about 9a35f54's general warning ("moves more than the discard decks"). It is not right about the census.
  - The laptop's own dated prediction in section 8 was that kpr "lifts Hydreigon everywhere and grows that deck's gap past the veto". The gap part held (+5.8). "Everywhere" did not: Hydreigon drops in 2 of its 7 cells (v Blaziken −1.6, v Sceptile −3.6, both within noise).

## 4. The mixed rows: attribution only

- **What they are.** Each of the 28 pairings has 500 deals in both directions, kpr3 on one deck and kp3 on the other. Each is compared with kp3 v kp3 on the same deals.
- **How they are read.** Only as attribution: which side of the board moved each deck. The decision above does not depend on them.
- **The pooling.** Per deck, over its seven cells, stratified as in score.py. The ranges are 95%, from the per-deal differences.

| deck | table change (kpr3 both sides) | **own side** (kpr3 on this deck only) | **opponents' side** (kpr3 on its opponents only; their own score) | part only when both sides run kpr3 | what moved it |
|---|---:|---:|---:|---:|---|
| Altaria | −3.0 ± 1.9 | **−2.6 ± 1.7** worse | +0.0 ± 1.5 | −0.4 ± 1.8 | its own pilot |
| Blaziken | +4.3 ± 1.7 | +1.2 ± 1.4 | **−3.1 ± 1.5** worse | +0.0 ± 1.6 | its opponents' pilots |
| Hydreigon | +5.8 ± 1.9 | **+3.8 ± 1.7** better | −0.2 ± 1.6 | +1.8 ± 1.9 | its own pilot |
| Lucario | −2.7 ± 1.8 | **−3.9 ± 1.6** worse | −1.0 ± 1.4 | +0.3 ± 1.7 | its own pilot |
| Sceptile | +0.9 ± 1.6 | +0.1 ± 1.2 | −0.3 ± 1.5 | +0.5 ± 1.4 | nothing beyond noise |
| Suicune | +2.4 ± 1.8 | −0.4 ± 1.4 | **−4.9 ± 1.6** worse | −2.1 ± 1.6 | its opponents' pilots |
| Vespiquen | −2.9 ± 1.8 | **−2.5 ± 1.6** worse | −0.5 ± 1.6 | −0.9 ± 1.9 | its own pilot |
| Weezing | −4.7 ± 1.7 | **−5.5 ± 1.5** worse | +0.2 ± 1.6 | +0.9 ± 1.7 | its own pilot |

**How to read a row.** A deck's table change ≈ its own side − its opponents' side + the last column.
- The opponents' side is their own score, so a negative number there helps this deck.
- The last column is within noise for every deck except Suicune (−2.1 ± 1.6).
- On the decision set, Altaria's own side is −3.6 ± 1.9 and Sceptile's +0.4 ± 1.2 (six cells each). The other decks are unchanged.
- **Head to head:** over all 28,000 mixed games kpr3 scores **48.8%** against kp3 (−1.2 ± 0.5). So as a pilot, kpr3 is slightly weaker overall.

**The questions Fable asked:**
- **Does kpr3 pilot Hydreigon's own side better? Yes: +3.8 ± 1.7.** This is the get_player test's intent, seen at table scale.
  - Its opponents' side does not move (−0.2 ± 1.6). About two-thirds of Hydreigon's +5.8 is its own pilot; the rest (+1.8 ± 1.9) is within noise.
  - Cell by cell, though, the own-side gain does not follow the rise in Hyper Ray chips. The correlation over the seven cells is −0.14 (on the table, −0.24, as Fable found).
  - Examples: against Sceptile the chip rate rises 90 points and Hydreigon's own side is −2.4 ± 4.0; against Vespiquen it rises 69 points and the own side is +9.6 ± 5.0.
  - So "kpr3 pilots Hydreigon better" is shown. "Because of the chip" is still not.
- **Suicune (+2.4): its opponents' side.** kpr3 on Suicune's opponents costs them 4.9 ± 1.6. The largest parts:
  - Weezing −12.9 ± 3.9 in Suicune v Weezing.
  - Lucario −11.6 ± 4.3 in Lucario v Suicune.
  - Vespiquen −6.4 ± 4.9 in Suicune v Vespiquen.
  - kpr3 on Suicune itself changes nothing measurable (−0.4 ± 1.4). So Suicune's own play (Diving Icicles, Ice Maker) is not what raised its cells.
- **Blaziken (+4.3 ± 1.7, no discard attack): its opponents' side.** kpr3 on Blaziken's opponents costs them 3.1 ± 1.5.
  - The largest parts are Lucario −11.6 ± 4.6 in Blaziken v Lucario and Weezing −7.6 ± 3.7 in Blaziken v Weezing.
  - Blaziken's own side is +1.2 ± 1.4. It is beyond noise only against Weezing (+5.6 ± 3.8).
  - So the two 10-point Blaziken cells Fable flagged come mainly from Lucario and Weezing being piloted worse.
- **Weezing (−4.7 ± 1.7): its own side, −5.5 ± 1.5.**
  - By cell: v Suicune −12.9, v Vespiquen −10.6, v Blaziken −7.6, v Lucario −4.2 (all beyond noise).
  - kpr3 on Weezing's opponents changes nothing (+0.2).
  - Weezing is the deck kpr3 pilots worst. Fable's candidate cause is the registered limit that an end-of-turn knockout leaves the promotion pending at the leaf, since Weezing runs Deceptive Needle. It is not tested here.
- **Altaria (−3.0): its own side, −2.6 ± 1.7** (−3.6 ± 1.9 on the decision set).
  - By cell: v Suicune −8.8 ± 4.8 and v Lucario −7.0 ± 4.0 are beyond noise, and v Blaziken just is (−4.80 against a range of ±4.76, both printed as 4.8).
  - Its opponents' side does not move.
- **Vespiquen (−2.9): its own side, −2.5 ± 1.6.**
  - The one cell beyond noise is v Suicune, −6.4 ± 4.9. The others are −3.8 to +0.8.
  - Its opponents' side does not move (−0.5).
  - In the kp3 and kd3 readings, Vespiquen's table move came mainly from its opponents' side. This time it comes from Vespiquen's own pilot.
- **Lucario (−2.7): its own side, −3.9 ± 1.6.**
  - By cell: v Blaziken −11.6, v Suicune −11.6, v Vespiquen −5.0 (beyond noise); v Weezing −3.8.
  - A candidate cause, not tested: the registered limit that Energy-dependent damage is priced at the next attack. Mega Lucario ex holding [F], with this turn's [F] unused and [F] next, is priced at 140 where an attack this turn does 90.

**Per cell, all 28 pairings, both directions.** Each row gives the first-named deck's table score, then each deck's own score change with kpr3 on it only.
- "Was awaiting" marks the five cell-veto candidates that were waiting for mixed rows. It says what the rows now show, for the record only.
- "Never counts" marks the three cells whose Limitless band is wider than ±15.

| cell | kp3 | kpr3 | Limitless v2 | miss change | first deck's side | second deck's side | note |
|---|---:|---:|---:|---:|---:|---:|---|
| Altaria v Blaziken | 58.6 | 52.6 | 76.5 ± 14.3 | +6.0 | **−4.8 ± 4.8** | −1.2 ± 3.7 | |
| Altaria v Hydreigon | 47.6 | 39.8 | 54.5 ± 13.0 | +7.8 | −0.8 ± 4.8 | **+4.2 ± 4.1** | was awaiting: neither side worse |
| Altaria v Lucario | 62.4 | 58.8 | 72.4 ± 6.9 | +3.6 | **−7.0 ± 4.0** | +0.4 ± 4.2 | |
| Altaria v Sceptile | 42.8 | 42.8 | 45.4 ± 9.4 | +0.0 | +3.4 ± 4.4 | −1.6 ± 3.3 | quarantined |
| Altaria v Suicune | 48.8 | 42.2 | 56.2 ± 12.1 | +6.6 | **−8.8 ± 4.8** | +2.2 ± 3.7 | was awaiting: Altaria worse |
| Altaria v Vespiquen | 47.4 | 50.4 | 37.6 ± 9.8 | +3.0 | +1.8 ± 4.5 | −3.8 ± 4.0 | |
| Altaria v Weezing | 40.4 | 40.4 | 33.0 ± 13.4 | +0.0 | −1.7 ± 4.5 | +0.0 ± 3.9 | |
| Blaziken v Hydreigon | 48.0 | 49.6 | 66.7 ± 18.9 | −1.6 | +2.8 ± 3.7 | +1.2 ± 4.4 | |
| Blaziken v Lucario | 45.1 | 56.0 | 40.7 ± 12.5 | +10.9 | +2.1 ± 4.3 | **−11.6 ± 4.6** | was awaiting: Lucario worse |
| Blaziken v Sceptile | 65.1 | 63.0 | 76.1 ± 17.4 | +2.1 | +0.3 ± 3.7 | +2.2 ± 2.8 | |
| Blaziken v Suicune | 59.6 | 62.2 | 64.3 ± 20.5 | −2.6 | +0.2 ± 3.8 | −1.6 ± 3.3 | |
| Blaziken v Vespiquen | 81.4 | 80.5 | 79.0 ± 14.3 | −0.9 | −1.7 ± 3.3 | +0.6 ± 3.6 | |
| Blaziken v Weezing | 48.4 | 60.1 | 41.2 ± 23.4 | +11.7 | **+5.6 ± 3.8** | **−7.6 ± 3.7** | never counts |
| Hydreigon v Lucario | 43.8 | 52.6 | 63.6 ± 12.7 | −8.8 | **+7.8 ± 4.4** | +3.0 ± 4.1 | |
| Hydreigon v Sceptile | 43.6 | 40.0 | 40.0 ± 16.2 | −3.6 | −2.4 ± 4.0 | +1.4 ± 2.8 | |
| Hydreigon v Suicune | 46.4 | 55.8 | 30.0 ± 15.2 | +9.4 | **+7.0 ± 4.6** | −2.4 ± 3.9 | never counts |
| Hydreigon v Vespiquen | 41.0 | 56.8 | 36.8 ± 15.3 | +15.8 | **+9.6 ± 5.0** | −1.4 ± 4.9 | never counts |
| Hydreigon v Weezing | 52.8 | 56.8 | 45.8 ± 19.9 | +4.0 | −0.6 ± 4.7 | −3.8 ± 4.3 | |
| Lucario v Sceptile | 35.6 | 38.6 | 39.5 ± 9.0 | −3.0 | +1.0 ± 4.2 | −1.6 ± 2.8 | |
| Lucario v Suicune | 58.8 | 49.6 | 58.8 ± 10.5 | +9.2 | **−11.6 ± 4.3** | −0.8 ± 3.4 | was awaiting: Lucario worse |
| Lucario v Vespiquen | 68.2 | 68.8 | 69.6 ± 8.7 | −0.6 | **−5.0 ± 4.3** | −3.4 ± 3.6 | |
| Lucario v Weezing | 52.8 | 55.8 | 61.5 ± 10.8 | −3.0 | −3.8 ± 4.3 | **−4.2 ± 3.6** | |
| Sceptile v Suicune | 60.6 | 62.6 | 50.0 ± 13.6 | +2.0 | −1.6 ± 3.0 | −1.2 ± 3.4 | |
| Sceptile v Vespiquen | 64.4 | 66.6 | 35.7 ± 12.5 | +2.2 | +1.8 ± 3.7 | −3.8 ± 4.2 | |
| Sceptile v Weezing | 70.0 | 69.2 | 68.1 ± 15.2 | −0.8 | +0.4 ± 2.9 | +0.8 ± 3.1 | |
| Suicune v Vespiquen | 43.0 | 49.6 | 28.5 ± 10.4 | +6.6 | +0.6 ± 4.2 | **−6.4 ± 4.9** | was awaiting: Vespiquen worse |
| Suicune v Weezing | 56.5 | 65.0 | 60.3 ± 15.4 | +1.0 | +0.5 ± 3.7 | **−12.9 ± 3.9** | |
| Vespiquen v Weezing | 65.9 | 72.7 | 83.7 ± 11.0 | −6.8 | +0.8 ± 4.6 | **−10.6 ± 4.3** | |

- Bold marks a side beyond its paired noise. Altaria's side v Blaziken is beyond it by a hair: −4.80 against ±4.76.
- **Counted over the 56 cell sides:**
  - 5 are better beyond noise: Hydreigon four times and Blaziken once.
  - 11 are worse: Weezing 4, Lucario 3, Altaria 3 and Vespiquen 1.
  - The rest are within noise.

## 5. Behaviour counters (from the per-game files)

**What the files carry.** The per-game files carry two counters (`kpr3_reading/fields_output.txt`):
- `hyper_ray`: turns with Hyper Ray on offer, as [knockout-able used, knockout-able passed, not knockout-able used, not knockout-able passed]. The per-cell sums match the scan's printed lines.
- `chase_order`: Vespiquen ex's optional discard of a Benched Basic [G] Pokémon, as {offered, discarded, names}.
- kp3's table files carry `hyper_ray` only. kp3's Chase Order counts come from `../chase_order_2026-09-25/kp3_vespiquen.jsonl`, the same games replayed with the counter; all 3,500 are identical to kp3's table games.

**Not carried:** there are no counters for Diving Icicles, Mega Burning, Terminating Tail, or the attach-Abilities (Ice Maker, Roar in Unison). Fable asked the cloud to add them before the rows; that did not happen.
- So Suicune's cells can be attributed to a side (its opponents'), but not to a behaviour.
- Blaziken's and Sceptile's attack-choice rates are not measured.

**Hyper Ray without a knockout, turns used** (all four conditions on the same deals):

| Hydreigon v | kp3 table | kpr3 table | kpr3 on Hydreigon only | kpr3 on the opponent only |
|---|---:|---:|---:|---:|
| Altaria | 5% (3 of 64) | 88% (71 of 81) | 95% (58 of 61) | 1% (1 of 97) |
| Blaziken | 1% (1 of 98) | 68% (65 of 96) | 76% (75 of 99) | 1% (1 of 85) |
| Lucario | 1% (1 of 128) | 91% (117 of 129) | 92% (103 of 112) | 3% (4 of 145) |
| Sceptile | 6% (4 of 70) | 97% (71 of 73) | 96% (76 of 79) | 4% (3 of 68) |
| Suicune | 40% (101 of 252) | 95% (322 of 338) | 93% (298 of 319) | 42% (116 of 278) |
| Vespiquen | 15% (29 of 193) | 84% (180 of 215) | 84% (167 of 198) | 15% (30 of 195) |
| Weezing | 34% (78 of 231) | 95% (279 of 295) | 94% (247 of 263) | 32% (76 of 237) |
| all | 20.9% ± 2.5 | 90.1% ± 1.7 | 90.5% ± 1.8 | 20.9% ± 2.5 |

- The chip is purely Hydreigon's own pilot. With kpr3 on Hydreigon it is 90.5%; with kpr3 only on the opponent it stays at kp3's 20.9%.
- **Knockout-able Hyper Ray passed:** kp3 88 of 2,334 (3.8%); kpr3 table 38 of 2,434 (1.6%); kpr3 on Hydreigon only 36 of 2,478 (1.5%); kpr3 on the opponent only 67 of 2,320 (2.9%).
  - Almost all of it is one cell, **Hydreigon v Vespiquen**: 22.4% ± 4.7 (79 of 353) → 9.9% ± 3.6 (35 of 352) on the table. It is 9.2% ± 3.7 (32 of 348) with kpr3 on Hydreigon only, and 18.1% ± 4.7 (63 of 348) with kpr3 on Vespiquen only.
  - Every other Hydreigon cell has 0 to 4 passes in every condition.
  - So in the cell that moves most (+15.8), Hydreigon's own pilot changed two things: it chips far more, and it declines knockouts far less.
  - The cloud README's "knockout turns are used as before" is true pooled and false in that cell, as Fable found.

**Chase Order: share of choices where Vespiquen discarded** (game-clustered 95% ranges on the pooled line):

| cell | kp3 table | kpr3 table | kpr3 on Vespiquen only | kpr3 on the opponent only |
|---|---:|---:|---:|---:|
| Altaria v Vespiquen | 54.5% (286 of 525) | 63.4% (332 of 524) | 64.3% (355 of 552) | 56.5% (291 of 515) |
| Blaziken v Vespiquen | 41.5% (131 of 316) | 42.9% (161 of 375) | 43.2% (150 of 347) | 41.9% (142 of 339) |
| Hydreigon v Vespiquen | 47.5% (280 of 589) | 55.2% (321 of 582) | 53.0% (340 of 641) | 52.5% (301 of 573) |
| Lucario v Vespiquen | 57.4% (210 of 366) | 69.3% (268 of 387) | 64.0% (228 of 356) | 58.9% (236 of 401) |
| Sceptile v Vespiquen | 88.3% (606 of 686) | 91.4% (715 of 782) | 92.2% (686 of 744) | 86.9% (631 of 726) |
| Suicune v Vespiquen | 88.9% (560 of 630) | 87.5% (561 of 641) | 88.7% (544 of 613) | 88.2% (578 of 655) |
| Vespiquen v Weezing | 74.9% (298 of 398) | 87.0% (410 of 471) | 86.3% (410 of 475) | 75.9% (325 of 428) |
| all | 67.5% ± 1.5 (3,510) | 73.6% ± 1.4 (3,762) | 72.8% ± 1.4 (3,728) | 68.8% ± 1.5 (3,637) |

- The shift is Vespiquen's own pilot. It discards more with kpr3 on Vespiquen (72.8%); with kpr3 on its opponents only, the rate barely moves (68.8%).
- Combee discards per choice: 13.1% (kp3), 15.6% (kpr3 table), 13.9% (kpr3 on Vespiquen), 13.8% (kpr3 on the opponent).
- Vespiquen's own side is −2.5 ± 1.6 at the same time. More discarding goes with worse Vespiquen play here, but that is not shown to be the cause.
- Caveat, as in the Chase Order check: these are shares over different positions, not paired choices.

## 6. Identity

- **The cloud's full replays at 53638a7.** k3, kp3 and kq3 replay the whole table, 14,000 of 14,000 each. kd3 replays its first 40 deals, 1,120 of 1,120.
  - The laptop re-checked all four field by field, including the move hash, against the reference tables (kd3's from the branch). All are identical (`kpr3_reading/identity_check_output.txt`).
  - 53638a7's bot code is 1981bb4's, one amendment (14c7d9b) behind the table's.
- **The table's own build, e09fb46.** It is covered by k3, kp3 and kq3 on the first 40 deals of every pairing, 1,120 of 1,120 each. That is 8% of the table, re-checked field by field here.
  - The rest is covered by reading the diff. From 53638a7 to e09fb46, `engine/` changes in one file, `value_functions.rs` (98 lines added, 8 removed).
  - Fable's code read found that change reachable only through kpr's flag. The laptop checked the file list and size, not the code.
  - The `engine/` tree is identical (942491391a3d…) from e09fb46 to the branch head aa87fa3.
  - The cloud's scan hash (c41b23e0…) and "1,919 passed" cannot be checked from the branch.
- **The laptop's own checks on its e09fb46 build** (`legality_scan` 3133ebaa…, from `git archive`; not the official engine):
  - The kp3 spot replay of pairings 0–2 is identical on 1,500 of 1,500 games.
  - kpr3 v kpr3 on pairing 1 is identical to the cloud's table on 500 of 500, move hash included.
  - `analysis.py` repeats both counts.
  - The compare files' "NOT IDENTICAL" last line only reflects the reference's other games, which a spot check does not play.
  - The two scan hashes differ, as builds on different machines do (as with kd). The games are the same.

## 7. What follows (Dustin decides)

- **kpr3 is not adopted.** That is the rule's verdict on the metric itself.
  - An override would be of the adoption metric, not of a veto. Fable advises against it, and so does the laptop. The change reaches every deck; it fits worse for seven decks of eight; and head to head it is a slightly weaker pilot.
- **kp3 stays the pilot** for the screen and the table. It was confirmed on the holdout on Sept 25.
  - **Dustin, Sept 26 (laptop chat):** "kpr3 not adopted, kp3 stays — fine to record, on one condition." The condition is that the record states, in the same line as the verdict, whether kpr3 chipped and whether the Hydreigon v Lucario cell moved. It did both; see the top of this file.
- **Opened by that finding, not proposed here:** a narrower change that prices the refill only where an attack discards the Active's Energy (the chip), leaving every other deck's readiness alone. It would be its own registration, with its own footprint census first.
- **The rest of the Hydreigon network's edge** (about two-thirds in Hydreigon v Lucario) is unexplained. The Altaria method, B2c with kp3 continuing, would name it. It is not run.
- **The readiness term goes to B3's feature set,** as kd's Weakness term did. B3 is the Texel-style fit:
  - It regresses game outcome on position features, over positions from self-play.
  - It is never fit against the Limitless table.
  - Its weight is fitted there instead of the hand-set 500.
  - When B3 is built, it is registered as its own candidate.
- **No split run** (score-only, clock-only, Zone-only). Nothing at stake would change a decision; this is the kd precedent.
  - The mixed rows already say where to look if kpr is ever revisited: Weezing's and Lucario's own sides, each with a registered limit as the candidate cause.
- **kt is built on kp3.**
- **"kpr on the brew's side only" is not on offer.** The plan wants one pilot for the screen and the table, and the mixed rows show kpr3 pilots four decks of eight worse on their own side.
- **Investigation list:**
  - Hydreigon's over-rating under a rule-correct chip. Its own side is now better and its gap grows. That points at the other side of its matchups or at the Limitless population, not at undoing the chip.
  - The two 10-point Blaziken cells, now traced mainly to Lucario and Weezing being piloted worse (against Weezing, Blaziken's own pilot adds +5.6).

## 8. Provenance

- **The spec was registered before the table, in commit messages.** That is enough.
  - The spec is 9a35f54 (Sept 25, 20:30 UTC). The amendments are 0adfeb7 (21:13), 1981bb4 (21:50) and 14c7d9b (22:22), each with its reason in the message.
  - e09fb46 (23:29) adds tests only.
  - The first table output is d141623 (Sept 26, 00:15). The table was complete at 8f16338 (00:42).
- **The README that presents the spec and its limits as registered was written after the results.** It names 9a35f54 as "the registered spec" and heads its limits "Known limits (kept as registered)". Exactly one commit touches `rl/results/kpr_2026-09-25/README.md`: aa87fa3 (00:51), after the table was complete. As a document it is post hoc, even where its content was known before.
- **Settled by Dustin, Sept 26 (laptop chat).**
  - **His go-ahead was for option 2:** projecting readiness into the clock's missing-Energy count as well as the online score. That is **9a35f54**, the registered spec, whose message reads "Dustin's option 2". The record is right there.
  - **He did not approve 1981bb4** (amendment 5, "each side read over its own horizon", the opponent-side fix recorded before the table). It was reported to him as already recorded, and he took it as the builder's own correction.
  - So 1981bb4's title ("Dustin's go-ahead") and body ("Dustin chose to fix it before the table"), and the cloud README's line 29, are wrong on this point. **1981bb4 is the builder's fix, not Dustin's go-ahead.** This does not affect the verdict.
- **Before Dustin's answer, the go-ahead for 1981bb4 was asserted only.** The laptop searched:
  - every commit message on every ref (`git log --all`);
  - the files under `rl/` and `docs/` on the cloud branch and on main (`git grep`);
  - the working tree's `rl/` and `docs/` notes.
  - The only sources are the commit itself (title "Dustin's go-ahead"; body "Dustin chose to fix it before the table"), the cloud README's line 29 restating it, and Fable's review files and section 8, which note that it is unquoted.
  - No chat record, quote or time was found (`kpr3_reading/git_checks_output.txt`). If Dustin remembers giving it, one line from him closes this. It does not affect the verdict.

## Where these numbers differ from Fable's

- **None in substance.**
  - score.py uses a fixed random seed, so its run here reproduces Fable's score.py output exactly.
  - The laptop's own numpy recompute agrees on every point estimate, with intervals within 2 points².
  - The footprint (13,117; 4,052), the deck rows, the cell changes, the Hyper Ray counts (including 22.4% → 9.9%) and the Chase Order rates (67.5% → 73.6%, 3,510 → 3,762 choices) all match.
- **Added here, beyond Fable's review:**
  - the mixed rows, with each deck split into own side and opponents' side;
  - the head-to-head score (48.8%);
  - the footprint of kpr3 on each deck alone;
  - the four-condition counters;
  - the finding that Hydreigon's deck veto would not count under v2.
  - These add to Fable's attribution note rather than contradict it. Fable was right that the table alone could not attribute the moves, and that Suicune's cells carry as much as Hydreigon's. The rows now show Suicune's cells come from its opponents being piloted worse.

## Files (`kpr3_reading/`)

- `run_score.sh`: the three score.py runs. It checks the kpr3 file's hash first (`kpr3_500_sha256.txt`).
- `kpr3_vs_kp3_v2.txt`: the deciding output.
- `kpr3_vs_kp3_sept23.txt`, `kpr3_vs_k3_v2.txt`: descriptive.
- `recompute.py` / `recompute_output.txt`: the independent recompute of the decision line.
- `analysis.py` / `analysis_output.txt`: integrity, identity, footprint, cells, deck sides, head to head and counters.
- `identity_check.py` / `identity_check_output.txt`: the cloud's identity files against the reference tables.
- `git_checks.sh` / `git_checks_output.txt`: read-only git checks (commit times, the engine diff, the go-ahead search).
- `fields.py` / `fields_output.txt`: which fields the per-game files carry.
- `check_*.py`, `check_*.sh` and their output files (`check_*_output.txt`, `check_score_*.txt`): a second reader's re-derivation of this reading from the raw files, with its own code (Sept 26), and its own score.py runs, identical line for line to the ones above. The corrections it made: the Altaria v Blaziken side is just beyond noise (so 11 worse sides, not 10), two cells tie for most changed, and wording in the plain summary, section 3's reserve route, section 4 (Suicune), section 7 and section 8.
