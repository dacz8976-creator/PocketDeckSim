# Step 8c: the games the automated rule did not settle, read by hand

The cloud, Oct 2. Eight games of the 3,813 did not get an automated ON THE BOARD or LOOKAHEAD ONLY verdict:
- 5 UNEXPLAINED;
- 2 LENGTH;
- 1 NEEDS A JUDGMENT.

**Every verdict in `results.tsv` stays as the accepted rule gave it.** This note adds the by-hand reading for the coordinator, Dustin and Sonnet. Line numbers are R's, f8cfa9c, `engine/src/players/expectiminimax_player.rs`.

## How km3 and k3 count their search (the code)

- The root decision is searched with `max_depth - 1` = 2 more plies (257-275); "3" in km3 and k3 is `max_depth`.
- **A forced continuation costs no ply** (631-655): the stack's top frame is exactly one of EndTurn, ResolveKnockoutPoints, ResolveAttackRetaliation, ResolvePokemonCheckup, FinishPokemonCheckup, ResolveEndTurnEvolution, or the stack is empty with `end_turn_pending`.
  - This check comes before the hidden-hand cutoff (773) and the turn boundary (908), whoever is to move.
- **A pure continuation costs no ply either, even at depth 0** (659-700): a frame whose choices are all ApplyQueuedAttackDamage or ChooseRandomEvolutionTarget.
- **Every other move costs a ply.** That includes the draw at the start of a turn (`DrawCard`, the mover's own stack move).

`coin_probe.rs`, the accepted probe, counts differently in two places:
- It stops at any state where the mover isn't to move. So it never follows the opponent's forced EndTurn into the mover's next turn.
- It counts a ChooseRandomEvolutionTarget frame as a ply. It treats such a frame as "pure" only for the `free` flag of the frame where a queued choice is found.

## The 5 UNEXPLAINED: a Promote, then a snipe on the next turn (the same shape in all five)

| step, bot, pairing (lists), deal | tick k (turn) | what knocked out the Active | R promotes (old engine) | the gate on the next turn |
|---|---|---|---|---|
| 8 km3, 1 (garchomp_meowth v t-blaziken), 399 | 81 (13) | Garchomp's Land Crush | Heatmor (Torchic) | Tongue Whip at two Benched Meowth (Carefree Steps) |
| 8 k3, 4 (garchomp_meowth v t-sceptile), 7 | 95 (13) | Land Crush | Grovyle (Butterfree) | Slicing Snipe at a Benched Meowth |
| 8 km3, 4 (garchomp_meowth v t-sceptile), 7 | 84 (11) | Land Crush | Grovyle (Butterfree) | Slicing Snipe at a Benched Meowth |
| 8 km3, 4 (garchomp_meowth v t-sceptile), 360 | 57 (8) | Land Crush | Grovyle (Caterpie) | Slicing Snipe at a Benched Meowth |
| 8 km3, 21 (hisuian_goodra v t-suicune), 310 | 87 (12) | Hisuian Goodra's Heavy Impact | Chien-Pao ex (Suicune ex) | Diving Icicles at Hisuian Goodra (Securely Sheltered), and the finite heads cut |

- **The first difference is the Promote itself.** It is a "lookahead" difference: the same state, the same offered Promote choices, a different choice. No reach counter fired in the window.
- **Both traces reproduce their hand-off rows.** Both accepted probes find nothing within 3 plies.
- **In the bots' search** (above), the line from the Promote is:
  - the Promote (ply 1);
  - the opponent's forced EndTurn (no ply);
  - the draw (ply 2);
  - the snipe (ply 3);
  - the queued coin-path choice at the coin-Ability Pokémon. Its frame holds only queued choices, so it is priced at depth 0 (no ply).
  - So the repaired choice is inside km3's and k3's own search.
- **The cross-turn variant** (`make_coin_probe_xturn.py`, `xturn_check.py`, `xturn.tsv`, `xturn_summary.txt`) is `coin_probe.rs` with one change: it resolves the forced continuations the bots resolve without a ply.
  - It finds exactly that line in all 5: "queued after 3, a pure frame"; in 21/310 also "a finite heads cut at ply 3".
  - **Checked against the accepted probe:** on every 10th of the 1,382 lookahead games coin_probe explains, 139 games, it finds the gate at the same or a smaller ply in 139 of 139.
  - **Its 12 negative controls** (controls.txt's deals and ticks) find nothing.
  - **The first build crashed** (a stack overflow on a finished game's forced EndTurn) in 18 of those 139. Those were crashes, not wrong answers. That is fixed: a settled game is a leaf, and a forced chain is capped at 8 steps. The numbers above are the fixed build's.
- **The ruling needed:** whether this reading, or the variant, may count as the second half ("a probe showing the gate's condition within the mover's search depth at k") for these 5 games. Until then they are UNEXPLAINED, and PLAN.md stops the switch.

## The 2 LENGTH games: repair A, on the board (by hand)

| step, bot, pairing (lists), deal | old / R ticks | the last common tick | R's extra tick | reach counters |
|---|---|---|---|---|
| 8 km3, 31 (houndoom_victini v t-weezing), 12 | 48 / 49 | 47: a Confused Mega Houndoom ex attacks (Grimhound Flare), Victini in play | 48: KeepAttackCoinResults (the Victory Star choice) | vs_confusion_first_built at 47; vs_confused_choice_offered and _chosen at 48 |
| 8 k3, 31 (houndoom_victini v t-weezing), 81 | 72 / 73 | 71: the same attack | 72: KeepAttackCoinResults | vs_confusion_first_built at 61 and 71; vs_confused_choice_offered and _chosen at 72 |

- The two engines agree on every move and every state hash up to the last common tick. Then the old engine's game ends, and R's has one more tick: the Victory Star choice that repair A offers after a Confusion heads. The winner and points are the same.
- `first_difference` has no tick to compare when one game ends where the other goes on, so it returns "length".
- **Read as a "state" difference at the extra tick:**
  - its cause is the last common tick, where vs_confusion_first_built fired;
  - the choice counters fired at the extra tick, in the same turn.
  - That is ON THE BOARD for repair A by the rule's own window.

## The 1 NEEDS A JUDGMENT: an evolution pick counted as a ply (`judgment.md`)

**8 km3, pairing 4 (garchomp_meowth v t-sceptile), deal 106 (seed 23,100,040,106), tick 82 (turn 12); a CONDITION 3 game.**
- **The position:**
  - The Sceptile side has only Treecko (60 HP, 2 Energy) in play.
  - The other side has Celebi (10 HP) Active, and Garchomp and two Meowth (Carefree Steps) on the Bench.
- **The choice:** the old engine plays Quick-Grow Extract (evolve Treecko); R plays Pound (20 damage to the 10 HP Celebi).
- **What `coin_probe` finds:** Quick-Grow Extract, then ChooseRandomEvolutionTarget, then Slicing Snipe, which offers the queued choice at a Meowth "after 3 moves, in a mixed frame" (Garchomp's choice is a plain one). So it reads the choice as offered only at the leaf, never applied: NEEDS A JUDGMENT.
- **By hand:** the ChooseRandomEvolutionTarget frame here has a single choice of that kind, a pure continuation the bots resolve without a ply (659-700). So in km3's search the line is:
  - Quick-Grow Extract (ply 1);
  - the evolution target (no ply);
  - Slicing Snipe (ply 2);
  - the target choice (ply 3), applied: inside the search.
- The cross-turn variant counts the evolution pick as the original does, and also says "leaf only".
- **For Dustin:** whether the repaired choice, reached on that line, counts as the mechanic acting at the root.
