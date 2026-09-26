Decision this informs: whether kpr (each Active priced as it will stand at its next attack, in the Active score and the threat clock) goes into the pilot on top of kp3, read against kp3 by rule v2. kpr does what it was built for: Hydreigon uses Hyper Ray without a knockout on 90% of the turns it can, against kp3's 21%. But on its own table the fit to Limitless gets worse: mean squared miss 176.1 against kp3's 112.2 (and k3's 159.3), and Hydreigon, already over-rated, gains the most (+5.8 ± 1.9). Engine commit e09fb46 for the kpr3 table (legality_scan SHA-256 `c41b23e0208506c7bf7056db710413f8699b421ad2f9813d4af81aae35eb1aa5`; every later branch commit up to this README has the same `engine/`). k3 and kp3 replayed the whole table unchanged at 53638a7 (14,000 of 14,000 each), kq3 too (14,000 of 14,000; kd3 1,120 of 1,120 on the first 40 deals), and k3, kp3 and kq3 again on the first 40 deals at the table's own build (1,120 of 1,120 each).

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
- 1981bb4: each side over its own horizon (the opponent at its next attack). Dustin's go-ahead after the second read found a turn-start step against the searcher of up to about 800 in the Suicune rows.
- 14c7d9b: the own reading counts the turn as over where the search scores the EndTurn before it (the Caterpie case), from the adversarial review.
- 53638a7, e09fb46: tests only.

## How it was checked before the table

- **Reviews:** two independent reviews of 9a35f54 (rules fidelity; identity, hidden information, tests); a second read of 0adfeb7; an adversarial review of 1981bb4 (five lenses, three skeptics per finding, a completeness critic; 36 agents; 8 of 10 findings upheld, 2 from the critic). Everything upheld was fixed, tested or written down below as a limit. Raw output: `review_1981bb4_workflow_output.json`.
- **Tests:** 25 kpr tests (23 feature tests, 2 through get_player); the full suite passes at e09fb46: 1,919 passed, 0 failed.
- **Mutations:** 63 of 64 mutations of the kpr code are caught at e09fb46 (`mutation_results_e09fb46.txt`). The one survivor, the tie-break key of Dragon's Blessing's choice, is equivalent on every card in the database. Earlier rounds: 53 of 54 at 1981bb4, 8 of 41 at 0adfeb7 before it was stopped for the next amendment.
- **Identity:** k3, kp3 and kq3 replay the whole table exactly at 53638a7, 14,000 of 14,000 games each, and kd3 its first 40 deals (1,120 of 1,120). The bot code after 53638a7 changed only inside kpr (14c7d9b), and at the table's own build k3, kp3 and kq3 replay the first 40 deals of every pairing exactly (1,120 of 1,120 each).

## The table

`kpr3_500.{txt,jsonl}`: all 28 pairings × 500 table deals, one line per game. No rule findings.

**Against Limitless, over 28 cells:**

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

Every cell, against k3 and kp3: `../per_game_table_2026-09-25/analyze_tables.py --base <k3_500 or kp3_500_*> --other kpr3_500.jsonl`. Deck averages: `deck_averages.py` (and `--paired`).

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

For reference, the census reading puts the network at 99% and the see-everything searched bots at 82–84%. Knockout turns are used as before (kpr3 passes 38 of 2,434, kp3 88 of 2,334).

What this shows, plainly:

- **kpr fixes the play it was built for.** Hydreigon now chips with Hyper Ray, the way the network and the searched bots do, where kp3 almost never did.
- **On this table that moves Hydreigon further from Limitless.** It was already over-rated under kp3 (47.4 against 42.6); kpr3 puts it at 53.2. The discard-attack census predicted exactly this before kpr was registered, and the reading set then with Fable applies: a change that is right by the rules and moves a deck away from reality points at blind spots on the other side of its matchups (or the population), not at undoing the change.
- **The change is broader than Hyper Ray,** as the registration warned: counting the turn's attach and next turn's Energy moves every deck.
  - Blaziken gains too (+4.3, past Limitless).
  - Vespiquen and Altaria lose ground and move further under Limitless.
  - Weezing drops past it (44.7 to 40.0, against 42.7).
  - Lucario and Suicune move toward Limitless.
- **The overall fit is the worst of the five bots** (mean squared miss 176.1). The deck-gap vetoes may fire: Vespiquen (42.9 against 56.5) and Hydreigon (53.2 against 42.6).
- The laptop's adoption rule and its mixed rows decide. This file only reports.

## Known limits (kept as registered)

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
