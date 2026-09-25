Decision this informs: whether k3 should price the public parts of hidden-card effects (kp3) instead of guessing opponent decklists (b3n1). kp3 gets b3n1's whole-table fit with no list knowledge, at about a third of b3n1's run time, and it comes with the same two problems: Hydreigon overshoots and Vespiquen's gap widens. So the laptop's vetoes will most likely fire for it too. Engine commit 858b6fe for the runs. c7cb688 adds the audited-text list and the get_player test the laptop asked for, and plays the same games (60 of 60 checked).

Seeds: the table's deals only. 72,000,000 + pairing × 10,000 + i, i < 500, even i = first-named deck in seat 0.

# Public pricing, kp3 (B1', item 2), Sept 25

**What kp3 is.** k3's search, still blind, but effects whose text mentions the opponent's hand or deck are priced instead of scored as doing nothing. The effect resolves against the opponent's hidden cards, which have no identity, so only its public parts count: Darkness Claw's damage, Copycat's draw count (the opponent's hand size), Mars's draw count. The rule is card-agnostic: no card is special-cased. It covers the 62 effect texts in the card database that mention the opponent's hand or deck, all audited on the laptop. A card added later stays unpriced until it is audited.

**What kp3 still misses:** any payoff that depends on what the hidden cards actually are. Penny, Portrait, Team Rocket's Boss and similar cards get credit for their public parts only.

**Checks.**
- kp3 is new player code (`kp<N>`). k3 is untouched: k3 still scores 58.3% on Altaria v Blaziken at 1,000 deals, the full suite passes (1,832 at 858b6fe; 1,835 at c7cb688), and the new tests fail without the change.
- The laptop's tier-1 read of 858b6fe: no leak, k3 unchanged, safe per thread, no panics in the 62 covered texts.
- c7cb688 adds a test that builds kp3 the way games do (get_player). It fails if the kp3 code ever builds plain k3.
- The kp3 table's games match the kp3 census games move for move (first 200 deals, 5,600 of 5,600).
- No game broke a rule.

## The five worst cells: does kp3 reproduce b3n1's gains?

| pairing (first deck's score) | k3 | b3n1 | kp3 | kp3 − k3 (95%) | kp3 − b3n1 (95%) | Limitless |
|---|---:|---:|---:|---:|---:|---:|
| Hydreigon v Lucario | 30.6 | 42.8 | 43.8 | +13.2 (+8.4, +18.0) | +1.0 (−3.1, +5.1) | 54.4 |
| Blaziken v Sceptile | 59.6 | 69.1 | 65.1 | +5.5 (+1.3, +9.7) | −4.0 (−7.3, −0.7) | 82.8 |
| Altaria v Lucario | 56.6 | 54.6 | 62.4 | +5.8 (+0.9, +10.7) | +7.8 (+3.9, +11.7) | 71.9 |
| Altaria v Blaziken | 56.0 | 59.4 | 58.6 | +2.6 (−2.4, +7.6) | −0.8 (−5.1, +3.5) | 74.2 |
| Sceptile v Vespiquen | 66.6 | 64.6 | 64.4 | −2.2 (−6.7, +2.3) | −0.2 (−3.8, +3.4) | 33.1 |

- **b3n1's +12.2 on Hydreigon v Lucario is all pricing.** kp3 gets +13.2 with no list.
- **b3n1's +9.5 on Blaziken v Sceptile is half pricing.** kp3 gets +5.5, 4.0 points short of b3n1 (range −7.3 to −0.7). The rest comes from what b3n1's sampled worlds know about the opponent's list.
- kp3 also lifts Altaria v Lucario (+5.8), where b3n1 did not.

## The whole table

Per cell: `../per_game_table_2026-09-25/analyze_tables.py --base ../per_game_table_2026-09-25/k3_500.jsonl --other <kp3_500_worst5.jsonl + kp3_500_rest.jsonl>`.

Against the Sept 23 Limitless table, over all 28 cells:

| bot | mean abs(miss) | mean squared miss |
|---|---:|---:|
| k3 | 9.66 | 159.3 |
| b3n1 | 8.30 | 111.0 |
| kp3 | 7.91 | 112.2 |

**Deck averages over their seven opponents:**

| deck | Limitless | k3 | b3n1 | kp3 |
|---|---:|---:|---:|---:|
| Altaria | 54.0 | 46.6 | 49.0 | 49.7 |
| Blaziken | 57.7 | 56.4 | 56.4 | 55.6 |
| Hydreigon | 42.6 | 34.6 | 46.4 | 47.4 |
| Lucario | 50.2 | 52.5 | 52.3 | 52.0 |
| Sceptile | 48.2 | 62.1 | 57.8 | 58.3 |
| Suicune | 48.2 | 52.9 | 47.2 | 46.5 |
| Vespiquen | 56.5 | 48.1 | 46.0 | 45.8 |
| Weezing | 42.7 | 46.6 | 44.7 | 44.7 |

What this shows:

- **kp3 and b3n1 move the table the same way.** Every deck average is within a point of b3n1's. Most of what option B does on this table is pricing, not guessing the opponent's list.
- **The same problems come along:**
  - Hydreigon overshoots: 47.4 against 42.6. Its cells against Altaria and Blaziken flip: Altaria v Hydreigon 57.8 → 47.6 against Limitless 57.0, and Blaziken v Hydreigon 64.5 → 48.0 against 59.0.
  - Vespiquen's gap widens: 48.1 → 45.8 against 56.5. Vespiquen v Weezing goes 70.9 → 65.9 against 83.5.
  - The laptop's pre-set rule vetoed b3n1 on Altaria v Hydreigon and the Vespiquen deck gap. Both look likely to fire here too. The laptop scores it.
- **Cost.** The kp3 table took 1,561 s of wall time, mostly on a free machine. b3n1 took 5,229 s, while other jobs shared the machine. So the timings aren't a controlled comparison, but kp3 does one search per move and b3n1 does one per sampled world.
- The Lucario network readout (`../lucario_network_divergence_2026-09-25`) points at a different kind of gap. That is k3's one-turn horizon: keeping a cheap front Pokémon, damage cuts on the opponent's turn, and powering the Benched attacker. Pricing doesn't touch it, and it may be where Vespiquen's and Altaria's missing points are.

## Files

- `kp3_500_worst5.{txt,jsonl}`: pairings 13, 23, 2, 0, 9.
- `kp3_500_rest.{txt,jsonl}`: the other 23.
- Together they are the whole table: one JSON line per game, same fields as `../per_game_table_2026-09-25`.
- `run_item2.sh`: the commands (legality scan built at 858b6fe). `timing.txt`: wall times.
