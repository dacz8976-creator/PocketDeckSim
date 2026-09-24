# Simulator vs Limitless check, 2026-09-23 (Claude, Opus, Cowork; asked for by Dustin after the lead's review)

Two questions: (1) how closely does the rules4 simulator with k3 piloting both sides match real B4a results, now that the rules fixes are in; (2) in the two matchups where corrected-engine networks exist, does network-vs-network land closer to real results than k3-vs-k3? Games were run in the Claude cloud workspace, not on the laptop.

## Inputs

- **Limitless**, pulled 2026-09-23 about 23:30 UTC: B4a Standard, 111 tournaments, 25,143 matches. Each cell comes from a deck's matchups page. Units are **tournament match results** (a mix of BO1 games and BO3 series, see `competitive-deck-study-2026-09-08/.../research/RESULT_UNIT_AUDIT.md`). Score = (W + ½T) / N.
  Quirk: Limitless's own Blaziken and Vespiquen matchup pages show under half the matches that the other decks' pages record against them. Every pair involving those two uses the other deck's page (those pages agree with each other). Vespiquen–Blaziken (35) has only the short pages.
- **Simulator**: add-on 0.7.2 wheel SHA-256 56ca0bad…925b, engine module 0fee43ce…9101. The rules4 executable (e6593ed8…2415, as in `project_manifest.json`) replayed 10 of this table's games identically (winner, points, turns). Astra's rules4 screen replayed 40/40 identically in the cloud.
  Decks: the Sept 8 study lists (`competitive-deck-study-2026-09-08/.../research/decks/`), one per archetype. k3 vs k3, 1,000 games per pairing, 28,000 in total, draws 0.1%.
  Seeds: 72,000,000 + pairing index × 10,000 + i (i < 1,000; pairings in alphabetical order); even i = first-named deck in seat 0. 83M and 89M were not used: stage 1 uses them.

### Deck fingerprints (SHA-256 of the exact files played)

| file | SHA-256 |
|---|---|
| research/decks/altaria.txt | 435a2bebc567ca83… |
| research/decks/blaziken.txt | fb08470e8801e93c… (same 20 cards as deck 06, different formatting) |
| research/decks/hydreigon.txt | 6ea0042236b48444… |
| research/decks/lucario.txt | 46a4820bc788b4fd… |
| research/decks/sceptile.txt | 7404c99e49161e68… |
| research/decks/suicune.txt | 7affe6530b8d096b… |
| research/decks/vespiquen.txt | fc3a0ffd1997f202… |
| research/decks/weezing.txt | c322fe64d6052bf9… |
| decks/dustin/06-mega-blaziken-tournament-list.txt (part 2) | 69c521a33339a456… |

Altaria, deck 06, Lucario, Suicune and Weezing match Astra's rules4 parity-check fingerprints (`rules4-addon-recheck-2026-09-22/benchmarks/cli-addon-parity-072/summary.json`).

## Part 1: whole table, three engine versions scored against the same Limitless data

"Average miss" = mean |sim − Limitless| over the 28 pairings. "Chance alone" = the average miss expected if the simulator were exactly right, from the sample sizes of both sides. "Real error" = the miss left after removing chance: the root-mean-square figure, then the same converted to an average miss for like-for-like reading. The older tables are the Sept 8 study's k3 matrices (64 games per pairing); their extra sampling noise is removed in "real error" but still lowers their correlations a little.

| engine | matchup correlation | average miss | chance alone | real error (RMS / as avg miss) | favored side right | where Limitless is clearly one-sided | deck ranking correlation (8 decks) |
|---|---:|---:|---:|---:|---:|---:|---:|
| eval18 (Sleep bug) | 0.55 | 13.4 | 6.0 | 14.8 / 11.8 | 19/28 | 12/16 | 0.40 |
| status1 (Sleep fixed) | 0.60 | 11.5 | 6.1 | 12.1 / 9.6 | 21/28 | 13/16 | 0.60 |
| **rules4 (this run)** | **0.68** | **9.4** | **4.0** | **11.1 / 8.8** | **23/28** | **15/16** | **0.45** |

- Rules4: 9 of 28 pairings differ from Limitless by more than chance allows (95%).
- The 8-deck ranking correlation has a 95% range of about −0.4 to 0.9, so it can't separate these engines. The audit's ≥0.7 bar can't be judged with 8 decks.
- Deck averages over their 7 opponents (sim / Limitless): Sceptile 61.8 / 48.2, Blaziken 56.7 / 57.7, Lucario 53.3 / 50.2, Suicune 52.6 / 48.2, Vespiquen 48.6 / 56.5, Altaria 47.0 / 54.0, Weezing 45.3 / 42.7, Hydreigon 34.7 / 42.5.
  The simulator overrates Sceptile and underrates Vespiquen and Altaria. Altaria's four biggest misses all run the same way (the sim has it 11–16 points too low vs Lucario, Blaziken, Suicune and Sceptile).

### Rules4, every pairing (largest disagreement first)

| pairing (first deck's score) | k3 v k3, % | Limitless, % (95%) | Limitless W-L-T | sim − Limitless |
|---|---:|---:|---:|---:|
| sceptile v vespiquen | 66.1 | 33.1 ± 8.2 | 41-84-2 | +33.0 |
| hydreigon v lucario | 30.2 | 54.4 ± 8.0 | 78-65-6 | -24.2 |
| blaziken v sceptile | 60.5 | 82.8 ± 9.0 | 54-10-3 | -22.3 |
| suicune v vespiquen | 46.0 | 27.0 ± 7.7 | 33-92-3 | +19.0 |
| altaria v blaziken | 58.3 | 74.2 ± 8.8 | 69-23-3 | -15.9 |
| altaria v lucario | 56.0 | 71.9 ± 4.9 | 223-84-11 | -15.9 |
| vespiquen v weezing | 68.8 | 83.5 ± 7.9 | 70-13-2 | -14.7 |
| altaria v suicune | 39.0 | 52.3 ± 8.0 | 76-69-5 | -13.3 |
| altaria v sceptile | 38.3 | 49.1 ± 6.6 | 101-105-13 | -10.8 |
| hydreigon v sceptile | 29.2 | 39.4 ± 10.7 | 30-47-3 | -10.2 |
| sceptile v suicune | 57.0 | 47.2 ± 9.5 | 49-55-3 | +9.8 |
| hydreigon v weezing | 38.5 | 47.1 ± 13.7 | 23-26-2 | -8.6 |
| hydreigon v vespiquen | 29.9 | 38.4 ± 9.8 | 35-57-3 | -8.5 |
| sceptile v weezing | 73.2 | 66.2 ± 10.4 | 51-25-4 | +7.0 |
| blaziken v hydreigon | 65.5 | 59.0 ± 12.3 | 33-22-6 | +6.5 |
| blaziken v suicune | 54.3 | 60.8 ± 12.4 | 35-22-3 | -6.5 |
| lucario v suicune | 52.4 | 58.5 ± 7.7 | 91-64-3 | -6.1 |
| lucario v weezing | 52.1 | 56.6 ± 8.3 | 74-56-6 | -4.5 |
| altaria v vespiquen | 43.1 | 38.8 ± 6.8 | 72-117-11 | +4.3 |
| blaziken v vespiquen | 77.5 | 81.4 ± 12.9 | 28-6-1 | -3.9 |
| lucario v vespiquen | 65.7 | 69.3 ± 6.4 | 133-57-7 | -3.6 |
| hydreigon v suicune | 37.9 | 34.7 ± 11.8 | 20-39-3 | +3.2 |
| altaria v weezing | 37.5 | 34.8 ± 9.2 | 33-64-5 | +2.6 |
| lucario v sceptile | 35.7 | 37.9 ± 6.3 | 85-141-5 | -2.2 |
| blaziken v lucario | 46.9 | 44.8 ± 8.1 | 63-78-3 | +2.2 |
| suicune v weezing | 62.7 | 64.2 ± 10.4 | 50-27-4 | -1.5 |
| blaziken v weezing | 50.2 | 49.0 ± 14.1 | 22-23-3 | +1.3 |
| altaria v hydreigon | 57.0 | 57.0 ± 8.4 | 74-55-6 | -0.0 |

## Part 2: network vs network, same seeds as k3 vs k3 (mixed rows added at the lead's request)

Seeds 73,000,000 + pairing × 10,000 + i, i < 2,000. All four rows use the same seeds and seats. Networks are each run's confirmed checkpoints: step 0 Blaziken ckpt_250k and Lucario ckpt_300k; stage 1 Weezing and Lucario ckpt_1800k_avg. Loading was checked by replaying the runs' own recorded games (step 0: 24/24 identical; stage 1: 16/16).

Score of the first-named deck, %; the change from k3 v k3 on the same seeds is in brackets (paired 95%).

| pairing | k3 v k3 | first deck's network v k3 | k3 v second deck's network | network v network | Limitless |
|---|---:|---:|---:|---:|---:|
| Blaziken v Lucario | 50.7 | 57.2 (+6.5 ±2.8) | 43.5 (−7.2 ±2.7) | 42.8 (−7.9 ±2.9) | 44.8 ± 8.1 (n 144) |
| Weezing v Lucario | 49.8 | 53.9 (+4.1 ±2.5) | 25.3 (−24.5 ±2.4) | 33.7 (−16.1 ±2.6) | 43.4 ± 8.3 (n 136) |

Confirmed margins over k3 from the runs (other seeds): Blaziken +10.7, Lucario (vs Blaziken) +3.5, Weezing +3.2, Lucario (vs Weezing) +25.6.

- **Weezing–Lucario:** the Lucario network alone moves the matchup 24.5 points and the Weezing network alone 4.1. Network v network (33.7) sits a little above the simple sum (29.4). Its landing is mostly the Lucario network's pilot edge, as the lead expected.
- **Blaziken–Lucario:** the two edges don't add. The simple sum predicts 50.0; network v network gives 42.8. The Blaziken network's +6.5 against k3's Lucario disappears against the Lucario network. Draws come with the Lucario network (19 and 20 of 2,000 in its two rows, 0 otherwise).
- Both network-v-network moves go the way Limitless points (Lucario favored). Blaziken–Lucario lands within 2 points of Limitless; Weezing–Lucario overshoots by about 10, just outside Limitless's 95% range. k3 v k3 sat inside that range in both. Two pairings give a direction, not a verdict on the network path.
- For comparison, k3 v k3 Blaziken–Lucario on part 1's seeds was 46.9 (1,000 games), and step 0's bars were 47.4. Weezing–Lucario was 47.9 there and 49 in stage 1's bars.

## List refresh (added 2026-09-24): do real top-finishing lists close the Altaria, Sceptile and Vespiquen misses?

Lists were pulled from Limitless decklist pages; Njord's Sceptile and preluxe's Altaria were cross-checked against the tournament API's standings JSON. Event dates are from the API. Every card number was checked against `lib/card.py`, and every list is 20 cards and plays in the engine.

| deck | player, event, date, finish | vs the Sept 8 list |
|---|---|---|
| Sceptile | Ridz, PMPT #44, Aug 29, 4th/378 | identical |
| Sceptile | LiquidHunter, The Dark League, Sep 2, 1st/77 | identical |
| Sceptile | Nagetto_Zuki, Umbreon99's Manic Monday, Sep 7, 6th/230 | identical |
| Sceptile | Sora Aoi, PokeBounty Showdown #2NA, Sep 14, 2nd/142 | identical |
| Sceptile | Semant1c, Breakfast Club Daily, Sep 14, 1st/79 | identical |
| Sceptile | Njord, PMPT #47, Sep 19, 2nd/295 | identical |
| Altaria | JLNG, PMPT #44, Aug 29, 2nd/378 | −1 Field Blower, +1 Cyrus |
| Altaria | LaNora, Block Dragon, Sep 10, 1st/150 | −1 Swablu, +1 Igglybuff; −1 Field Blower, +1 Cyrus |
| Altaria | itachi1820, PMPT #46, Sep 12, 1st/355 | identical |
| Altaria | preluxe, PMPT #47, Sep 19, 5th/295 | identical |
| Vespiquen | TwidleUrStixx, Breakfast Club x Knowtice, Sep 2, 1st/80 | +1 Vespiquen (A2 018), −1 X Speed |
| Vespiquen | Javiercazorla, Umbreon99's Manic Monday, Sep 7, 10th/230 | identical |
| Vespiquen | kovacs469, PokeBounty Showdown #2NA, Sep 14, 10th/142 | Combee A2a 004 for B4 010; +Minior, +Lucky Ice Pop, +Elegant Cape; −1 Copycat, −1 X Speed, −1 Field Blower |

Only the four lists that differ were simulated: each against the other seven Sept 8 lists, k3 vs k3, 1,000 games per pairing on part 1's exact seeds (72,000,000 + pairing × 10,000 + i), 28,000 games in all.

The files are in `competitive-deck-study-2026-09-08/round-robin-checkpoint/reports/research/decks-variants-2026-09-23/`. It's a sibling folder because k3_screen.py and the jev experiment scripts read every .txt in `research/decks/`.

SHA-256: altaria_jlng 2e2907fd39903531…, altaria_lanora 9f44e70dc83eb07e…, vespiquen_twidleurstixx 85419edbebfc6637…, vespiquen_kovacs469 d45ee3b96c9edaa2….

The paired 95% range on each list-vs-list change is about ±3–4 points.

**Altaria** (score of Altaria, %)

| opponent | Sept 8 list | jlng | lanora | Limitless |
|---|---:|---:|---:|---:|
| blaziken | 58.3 | 56.3 | 55.9 | 74.2 |
| hydreigon | 57.0 | 59.8 | 55.1 | 57.0 |
| lucario | 56.0 | 55.1 | 62.8 | 71.9 |
| sceptile | 38.3 | 36.9 | 38.2 | 49.1 |
| suicune | 39.0 | 36.5 | 39.1 | 52.3 |
| vespiquen | 43.1 | 39.5 | 30.4 | 38.8 |
| weezing | 37.5 | 34.8 | 34.8 | 34.8 |
| **average of 7** | **47.0** | **45.6** | **45.2** | **54.0** |

**Vespiquen** (score of Vespiquen, %)

| opponent | Sept 8 list | twidle | kovacs | Limitless |
|---|---:|---:|---:|---:|
| altaria | 56.9 | 55.6 | 58.1 | 61.3 |
| blaziken | 22.5 | 23.4 | 26.6 | 18.6 |
| hydreigon | 70.1 | 66.9 | 71.7 | 61.6 |
| lucario | 34.3 | 33.7 | 34.5 | 30.7 |
| sceptile | 33.9 | 31.2 | 34.3 | 66.9 |
| suicune | 54.0 | 49.9 | 47.8 | 73.0 |
| weezing | 68.8 | 66.6 | 69.8 | 83.5 |
| **average of 7** | **48.6** | **46.8** | **49.0** | **56.5** |

- **The misses survive every real list.** Across the four variant lists, the simulator's numbers move 2–4 points per matchup on average. The largest single move is LaNora's Altaria vs Vespiquen, −12.7. The deck-level gaps stay: Altaria 45–47 in the sim against 54.0 real; Vespiquen 47–49 against 56.5. Sceptile's top lists haven't changed at all.
- **Among top-finishing lists, list drift is ruled out** as the explanation for the Altaria, Sceptile and Vespiquen misses. It isn't ruled out that the average Limitless entrant plays different lists from the top finishers.
- **What's left:** how k3 plays these decks; rules errors in cards specific to these decks; or effects in the Limitless population (skill, match format). The Sceptile–Vespiquen reversal (sim 66–34 for Sceptile, real 33–67) is the sharpest single target.

## Limits

- Limitless cells are match results pooled across BO1 and BO3 events. A BO3 series stretches a deck's edge (55% a game ≈ 57.5% a series). For lopsided pairings that can explain a few points, not the biggest misses; Limitless falls inside the sim's game-to-series range, allowing for its own sample, in 19 of 28 pairings.
- One Sept 8 list per archetype; Limitless pools every list of the archetype over the whole B4a period. List drift is a live explanation for single cells (Sceptile especially).
- Limitless players are tournament entrants, not Dustin's ladder.
