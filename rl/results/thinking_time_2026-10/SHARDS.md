# The thinking-time test: the shard table (6 workers; the coordinator sends the briefs)

A slice is one deck of one registration (80 kx3 and 80 km3 games). The estimated hours are the frozen kx3's laptop time per game on that
deck (the development run) × 1.7 for m32 or × 1.05 for m16, × 80 games, × 2.4 for a cloud machine, ÷ 2 for the registered `--threads 2`.
They are estimates until the first slices finish.

| slice | registration | deck | est. wall h |
|---|---|---|---:|
| 1 | think_m32_b | 05-indeedee-stoutland | 14.9 |
| 2 | think_m32_b | 01-muk-glimmora-kingambit-regigigas | 13.9 |
| 3 | think_m16_b | 05-indeedee-stoutland | 9.4 |
| 4 | think_m16_b | 01-muk-glimmora-kingambit-regigigas | 8.8 |
| 5 | think_m32_b | draft-A-shark-tempo | 7.1 |
| 6 | think_m32_a | 10-xatu-oricorio-tr-weezing | 5.5 |
| 7 | think_m16_b | draft-A-shark-tempo | 4.4 |
| 8 | think_m32_a | 09-mega-manectric-heliolisk | 4.3 |
| 9 | think_m32_a | 06-mega-blaziken-tournament-list | 3.8 |
| 10 | think_m16_a | 10-xatu-oricorio-tr-weezing | 3.5 |
| 11 | think_m16_a | 09-mega-manectric-heliolisk | 2.6 |
| 12 | think_m16_a | 06-mega-blaziken-tournament-list | 2.4 |

| worker | slices, in this order | est. wall h (+ about 1 h setup) |
|---|---|---:|
| W1 (Sonnet runner 1) | 1 | 14.9 |
| W2 (Sonnet runner 2) | 2 | 13.9 |
| W3 | 3, then 10 | 12.9 |
| W4 | 4, then 9 | 12.6 |
| W5 | 5, then 8, then 12 | 13.8 |
| W6 | 6, then 7, then 11 | 12.5 |

A worker that finishes early takes the next unplayed slice only on the coordinator's word: a deck is played by one worker only.
Each registration is complete when its three decks are in. The merge (`split_collect.py merge`, one per registration) is the laptop's.

**The exam** (the upper bound, approved): 11 shards, one held-out deck each, on the same 6 workers once the thinking-time test is read:
- W1: 02 arceus-crobat
- W2: 08 garchomp-toolbox, 13 a-ninetales-raticate
- W3: 07 skarmory-stall, 14 comfey-raticate-hypno
- W4: draft-C meowstic-hatterene, 11 archaludon-haxorus
- W5: draft-D entei-grimhound, 15 jolteon-oricorio-raticate
- W6: 12 ariados-whimsicott-ogerpon, 04 absol-hoopa-darkrai

That is about 20 h wall at most for the full candidate, and less for a cheaper pick.
