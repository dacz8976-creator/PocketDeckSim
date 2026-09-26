Decision this informs: whether kpr (each Active priced as it will stand at its next attack, in the Active score and the threat clock) goes into the pilot on top of kp3. **Decided: not adopted; kp3 stays the pilot** (the laptop's rule-v2 reading, main 055f6f0, `rl/results/table_readings_2026-09-24/kpr3_paired_reading.md`, which supersedes this file's fit figures: on scoreboard v2's 27-cell decision set kp3 131.7 → kpr3 206.4, ΔMSE +74.7, 95% +28.4 to +123.1, whole interval above zero, so "do not adopt" on the metric before any veto; real-error margin −3.60, 90% −4.37 to −1.45). kpr does what it was built for: Hydreigon uses Hyper Ray without a knockout on 90% of the turns it can, against kp3's 21%. But the change reaches every deck: 13,117 of the 14,000 paired games (93.7%) play differently from kp3's and 4,052 (28.9%) change result. Engine commit e09fb46 for the kpr3 table (legality_scan SHA-256 `c41b23e0208506c7bf7056db710413f8699b421ad2f9813d4af81aae35eb1aa5`; no later branch commit up to aa87fa3 touches `engine/`). Identity: k3, kp3 and kq3 replayed the whole table unchanged at 53638a7, one amendment before the table (14,000 of 14,000 each; kd3 1,120 of 1,120 on the first 40 deals); the table's own build is covered by 1,120 games per bot (k3, kp3, kq3 on the first 40 deals of every pairing, all identical) plus a kpr-only diff (14c7d9b, reachable only through kpr's flag).

Corrections of Sept 26, from Fable's review (`rl/results/fable_reviews_2026-09-26/kpr_readout_review.md` on main) and the laptop's reading, are marked "(Sept 26)" below; the original sentences they replace are in the history of this file (aa87fa3).

Seeds: the table's deals only. 72,000,000 + pairing × 10,000 + i, i < 500, even i = first-named deck in seat 0.

# kpr3: kp3 plus projected readiness for the Active (Sept 25)

## What kpr is

`kpr<N>` = `kp<N>` (k's blind search, PublicPricingPlayer with the 62 audited texts) with one evaluator change, on both sides. kq's and kd's features are off.

- **The change.** Wherever k reads how ready an Active is, kpr reads a copy of the Active with the Energy its owner's public sources will have given it by then (`projected_active_energy`):
  - the Active online score (weight 500);
  - the damage-aware threat clock, for the Active's missing Energy and its damage estimate, its own attacks and its evolution forms'. The clock takes the faster of the clock with and without the projection.
- **The sources:**
  - the turn's attach from the Energy Zone, of the visible type;
  - Abilities that attach Energy to the Active (Ice Maker, Roar in Unison, Forest Breath, Volt Charge, Combust, Dragon's Blessing), keyed on mechanic;
  - each discarded Energy taken once;
  - none that would knock the Active out;
  - none on a turn when a turn effect blocks Zone attaches to the Active.
- **When.** Each side is read so that its value doesn't step inside the searcher's own search, which runs from its turn to the start of the opponent's:
  - the searcher's own Active by its next turn at the latest (this turn's unused sources and next turn's while its turn runs; otherwise next turn's);
  - the opponent's Active at its very next attack.
  "Turn over" covers an attack used, a pending or forced end, a deferred or paused Checkup, an end-of-turn evolution, and, for the own reading, positions where the search scores the EndTurn on the state before it (an Active Caterpie against an unknown deck).
- **Why.** Hyper Ray (Hydreigon) empties the attacker. k counts that as a lost Active and three turns of missing Energy, and declines to chip with it (19% without a knockout in the census). Next turn's [D] plus Roar in Unison refill it; kpr sees that and chips (the get_player test pins it).

**The spec and its amendments,** all registered before any kpr table, each with its reason in the commit message:
- 9a35f54: the registered spec (Dustin's option 2: the clock too, not only the score).
- 0adfeb7: two reviews' fixes: timing through the next turn on the owner's turn, min of the clocks, projected damage, the discard pile taken once, Dragon's Blessing's choice, the self-knockout guard.
- 1981bb4: each side over its own horizon (the opponent at its next attack), after the second read found a turn-start step against the searcher of up to about 800 in the Suicune rows. (Sept 26, the record of "Dustin's go-ahead", Fable's question 4.) The go-ahead was given in this cloud session's chat, which is not in the repo; this is the cloud's record of it. After 0adfeb7 was pushed (21:13 UTC Sept 25) and before 1981bb4 was written (21:50), the cloud asked, as a multiple-choice question: "kpr's spec now has five changes from the reviews: the four I listed before, plus this fix for the opponent's side. Can I make the fix, rerun the checks (tests, mutation checks, a replay proving the other bots are unchanged, and a quick adversarial review), and then run the kpr table?" Dustin chose "Fix it, then table (Recommended)". The laptop session then relayed the same instruction via Dustin ("Fix it, then table. Record the opponent-side fix and its reason in the spec before any table, rerun the tests, mutation checks, the k3/kp3/kq3 replay and the adversarial review, then run the 28-matchup kpr table."), which reached the cloud after 1981bb4 had been pushed.
- 14c7d9b: the own reading counts the turn as over where the search scores the EndTurn before it (the Caterpie case), from the adversarial review. (Sept 26) It had no review of its own: the adversarial review's skeptics read it at HEAD while checking the finding it fixed, and its guard is one test plus four mutations (all caught at e09fb46), not a separate read.
- 53638a7, e09fb46: tests only.

## How it was checked before the table

- **Reviews:** two independent reviews of 9a35f54 (rules fidelity; identity, hidden information, tests); a second read of 0adfeb7; an adversarial review of 1981bb4 (five lenses, three skeptics per finding, a completeness critic; 36 agents; 8 of 10 findings upheld, 2 from the critic). Everything upheld was fixed, tested or written down below as a limit. Raw output: `review_1981bb4_workflow_output.json`.
- **Tests:** 25 kpr tests (23 feature tests, 2 through get_player); the full suite passes at e09fb46: 1,919 passed, 0 failed.
- **Mutations:** 63 of 64 mutations of the kpr code are caught at e09fb46 (`mutation_results_e09fb46.txt`). The one survivor, the tie-break key of Dragon's Blessing's choice, is equivalent on every card in the database. Earlier rounds: 53 of 54 at 1981bb4, 8 of 41 at 0adfeb7 before it was stopped for the next amendment.
- **Identity:** k3, kp3 and kq3 replay the whole table exactly at 53638a7, 14,000 of 14,000 games each, and kd3 its first 40 deals (1,120 of 1,120). The bot code after 53638a7 changed only inside kpr (14c7d9b), and at the table's own build k3, kp3 and kq3 replay the first 40 deals of every pairing exactly (1,120 of 1,120 each).

## The table

`kpr3_500.{txt,jsonl}`: all 28 pairings × 500 table deals, one line per game. No rule findings.

**Against Limitless: the Sept 23 table, pooled over all 28 cells including the quarantined Altaria v Sceptile** (`analyze_tables.py` reads `limitless_check_2026-09-23.md`). (Sept 26) This is not the plan's decision table; the laptop's reading on scoreboard v2's 27-cell decision set supersedes it (kp3 131.7, kpr3 206.4, k3 177.5; real error 8.6 to 12.2 points).

| bot | mean abs(miss) | mean squared miss |
|---|---:|---:|
| k3 | 9.66 | 159.3 |
| kp3 | 7.91 | 112.2 |
| kq3 | 9.44 | 147.3 |
| kd3 | 8.59 | 124.5 |
| kpr3 | 10.28 | 176.1 |

**Deck averages over their seven opponents**, and each deck's change against kp3 on the same deals (95% range):

| deck | Limitless | k3 | kp3 | kpr3 | kpr3 − kp3 |
|---|---:|---:|---:|---:|---:|
| Altaria | 54.0 | 46.6 | 49.7 | 46.7 | −3.0 ± 1.9 |
| Blaziken | 57.7 | 56.4 | 55.6 | 59.8 | +4.3 ± 1.7 |
| Hydreigon | 42.6 | 34.6 | 47.4 | 53.2 | +5.8 ± 1.9 |
| Lucario | 50.2 | 52.5 | 52.0 | 49.3 | −2.7 ± 1.8 |
| Sceptile | 48.2 | 62.1 | 58.3 | 59.1 | +0.9 ± 1.6 |
| Suicune | 48.2 | 52.9 | 46.5 | 48.9 | +2.4 ± 1.8 |
| Vespiquen | 56.5 | 48.1 | 45.8 | 42.9 | −2.9 ± 1.8 |
| Weezing | 42.7 | 46.6 | 44.7 | 40.0 | −4.7 ± 1.7 |

**Cells that changed most against kp3** (paired on the same deals, 95% range; the first-named deck's score):
- Hydreigon v Vespiquen +15.8 (+10.2, +21.4)
- Blaziken v Weezing +11.7 (+7.6, +15.8)
- Blaziken v Lucario +10.9 (+5.8, +16.0)
- Hydreigon v Suicune +9.4 (+4.4, +14.4)
- Lucario v Suicune −9.2 (−13.8, −4.6)
- Hydreigon v Lucario +8.8 (+4.0, +13.6)
- Suicune v Weezing +8.5 (+4.1, +12.9)
- Altaria v Hydreigon −7.8 (−12.9, −2.7)
- Vespiquen v Weezing +6.8 (+2.1, +11.5)
- Suicune v Vespiquen +6.6 (+1.5, +11.7)
- Altaria v Suicune −6.6 (−11.7, −1.5)
- Altaria v Blaziken −6.0 (−11.0, −1.0)

Every cell, against k3 and kp3: `../per_game_table_2026-09-25/analyze_tables.py --base <base file> --other kpr3_500.jsonl`, where the base is `../per_game_table_2026-09-25/k3_500.jsonl`, or for kp3 one file made by joining its two parts (`cat ../public_pricing_2026-09-25/kp3_500_worst5.jsonl ../public_pricing_2026-09-25/kp3_500_rest.jsonl > kp3_500_all.jsonl`); (Sept 26) as first written the command couldn't run for kp3, whose table is two files. Deck averages: `deck_averages.py` (and `--paired`).

**The footprint (Sept 26; the plan registers a candidate with it, and the reserve route keys on 15%).** kpr3's moves differ from kp3's in 13,117 of the 14,000 paired games (93.7%); 883 are identical (kp3 and k3 share 1,242). 4,052 games (28.9%) change result. Least-changed cell Blaziken v Sceptile (413 of 500 differ), most Altaria v Vespiquen and Vespiquen v Weezing (492 of 500). With kpr3 on one deck only (the laptop's mixed rows) it changes 65% (Sceptile) to 89% (Altaria) of that deck's games. **The discard-attack census's prediction, that a projected-readiness term would "mainly change Hydreigon", is recorded as missed.** 9a35f54's general warning ("it moves more than the discard decks") was right; the census was not. The reserve route is closed for kpr (footprint, no-harm bound and own-side conditions all fail).

**Hyper Ray without a knockout** (turns where it was on offer and wouldn't knock out; used, of those turns):

| Hydreigon v | k3 | kp3 | kpr3 |
|---|---:|---:|---:|
| Altaria | 3% (4 of 135) | 5% (3 of 64) | 88% (71 of 81) |
| Blaziken | 1% (2 of 152) | 1% (1 of 98) | 68% (65 of 96) |
| Lucario | 3% (8 of 233) | 1% (1 of 128) | 91% (117 of 129) |
| Sceptile | 3% (4 of 131) | 6% (4 of 70) | 97% (71 of 73) |
| Suicune | 35% (203 of 578) | 40% (101 of 252) | 95% (322 of 338) |
| Vespiquen | 14% (33 of 242) | 15% (29 of 193) | 84% (180 of 215) |
| Weezing | 33% (103 of 315) | 34% (78 of 231) | 95% (279 of 295) |
| all | 20% | 21% | 90% |

For reference, the census reading puts the network at 99% and the see-everything searched bots at 82–84%. (Sept 26) Knockout turns are used as before pooled (kpr3 passes 38 of 2,434, kp3 88 of 2,334), but not in Hydreigon v Vespiquen, the cell that moved most: there kp3 passed 79 of 353 knockout-able turns (22.4%) and kpr3 35 of 352 (9.9%); every other Hydreigon cell passed 0 to 4 under both. So that cell's +15.8 mixes two Hyper Ray changes with whatever Vespiquen's side did.

**Other behaviour that moved (Sept 26):** Vespiquen's Chase Order choices went from 3,510 to 3,762 and the discard rate from 67.5% to 73.6% (higher in six of seven cells; Combee discards 460 to 588). Counters for Mega Burning, Terminating Tail, Diving Icicles and the attach Abilities (Roar in Unison, Ice Maker) did not exist at this table; they were added to `legality_scan` on Sept 26 (a03f491) and their kp3 and kpr3 figures, from a full identity replay, are in `../kpr_counters_2026-09-26/`.

What this shows, plainly:

- **kpr fixes the play it was built for.** Hydreigon now chips with Hyper Ray, the way the network and the searched bots do, where kp3 almost never did.
- **Hydreigon ends further above Limitless** (47.4 against 42.6 under kp3; 53.2 under kpr3). (Sept 26) But that is not the explanation of the worse fit, and the story as first written here (chip, so Hydreigon lifts, so the fit is worse) was asserted, not shown:
  - Hydreigon's seven cells carry 42% of the rise in mean squared miss; the other 21 cells carry 58%, Suicune's as much as Hydreigon's.
  - Across Hydreigon's cells, the rise in chipping has no relation to the score change (r = −0.24; v Sceptile 6% to 97% and −3.6).
  - The laptop's mixed rows attribute the table: kpr3 pilots Hydreigon better (+3.8 ± 1.7 on its own side) but Altaria, Lucario, Vespiquen and Weezing worse on theirs; Blaziken and Suicune gain because their opponents are piloted worse.
  - "A change that is right by the rules" is not earned for kpr as built: the change is much broader than the chip.
- **The change is broader than Hyper Ray:** counting the turn's attach and next turn's Energy moves every deck (the footprint above).
  - Blaziken gains too (+4.3). (Sept 26) On the Sept 23 cells that is no change in its gap (2.1 to 2.2); on v2 it is a deck veto (+3.6).
  - Vespiquen and Altaria lose ground and move further under Limitless.
  - Weezing drops past it (44.7 to 40.0, against 42.7).
  - Lucario moves toward Limitless. (Sept 26) Suicune does only as a deck average on the Sept 23 cells, and moves away on v2: four of its cells' misses grew by 6 or more (Altaria v Suicune, Lucario v Suicune, Hydreigon v Suicune, Suicune v Vespiquen), offset by others.
- **The overall fit is the worst of the five bots.** (Sept 26) The vetoes, for the record only (the metric decides first): on v2, five deck vetoes (Hydreigon +5.8, Blaziken +3.6, Altaria +3.5, Vespiquen +2.9, Weezing +2.8) and eight cells whose miss grows by more than 6, three of them band-excluded (Blaziken v Weezing, Hydreigon v Suicune, Hydreigon v Vespiquen). With the mixed rows, four cells and four decks count; Hydreigon's deck veto does not, because kpr3 pilots Hydreigon better. Altaria also trips on the Sept 23 cells (gap 4.3 to 7.3), which the first version of this list left out.
- The laptop's adoption rule and its mixed rows decide. This file only reports.

## Known limits

(Sept 26) This README was first committed after the table (aa87fa3), so this list is post hoc as a document. Its content was known before the table: the first two items were findings of the adversarial review of 1981bb4 (`review_1981bb4_workflow_output.json`, committed in df46e0a before the first table game), the rest were in the commit messages of 9a35f54, 0adfeb7, 1981bb4 and 14c7d9b. e09fb46's message says two limits were "written into the kpr README"; no README existed then.


- **An end-of-turn knockout leaves the promotion pending at the leaf** (review finding). When the searcher's end of turn (Deceptive Needle, poison, burn, Bad Dreams) knocks the opponent's Active out, the search scores the leaf with the replacement not yet promoted, so the opponent reads "no Active"; on a line where an attack takes the knockout, the replacement is promoted and projected. k has the same leaf, but there an unpowered replacement reads about 0 anyway; kpr widens the gap by up to 500 × the replacement's projected readiness plus 100 per clock turn, in favour of letting the end of turn take the knockout. Five of the eight lists do end-of-turn damage.
- **The self-knockout guard reads the HP now**, not after end-of-turn damage that lands before the owner's next attack (Checkup burn or poison, Bad Dreams, Deceptive Needle). A Roar in Unison priced now can become one that would knock the holder out by then.
- **Energy-dependent damage is projected in the clock, not "this turn if it pays"**: Mega Lucario ex holding [F] with this turn's [F] unused and [F] next is priced at 140, where an attack this turn does 90. The clock doesn't model whose turn it is.
- **Not counted:** an attach that puts the Active to sleep (Snoozing Habit, Comatose, Stellar Cradle); Energy moved from the Bench; an estimate that reads the Active from the board (Energized Leaves' combined count).
- **Two-type decks:** a `next` drawn inside the search (Rainbow Cave, or a search crossing into the searcher's next turn) is a guess, and extra Energy can move the online score's yardstick to a better attack with a lower ratio with mixed-type costs. The eight table decks each use one type; Dustin's 08 and 11 use two.
- **Observations hide the opponent's stack**, so a paused end of its turn (a point-denial coin at Checkup) reads as its turn running. Between Kiawe and its attach choice the turn reads as over.
- **The engine's own deviations it reads through:** discard-all-Energy attacks (Hyper Ray) don't put the Energy in the discard pile, so Combust and Dragon's Blessing see less there than the rules would give (rules/09; no table deck pairs them).

## Files

- `kpr3_500.{txt,jsonl}`: the kpr3 table. `run_kpr3_table.sh`: its command, plus the identity subset at the same build (`table_commit_identity_{k3,kp3,kq3}_40.*`).
- `identity_{k3,kp3,kq3}_500.*`, `identity_kd3_40.*`: the full replay at 53638a7. `run_identity.sh`: its command. `identity_k3_9a35f54_partial.*`: the first, stopped replay.
- `mutate.py`, `mutation_results_{0adfeb7,1981bb4,e09fb46}.txt`: the mutation checks.
- `review_1981bb4_workflow_output.json`: the adversarial review.
- `timing.txt`: wall times.
