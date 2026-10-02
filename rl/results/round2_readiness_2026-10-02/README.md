# Round-2 readiness (the cloud, Oct 2)

Three short jobs to make the round-2 package (everything `claude/coin-prevention-round2` adds to the official engine: the
later coin round, the card-text job and its follow-up) ready for the next rules switch. There were no table games and no
`players/` change.

## 1. Which lists and pairings the package can change

Inputs: main at 7c1b62f, with all 68 deck lists under `decks/` (`drafts_2026-10-01/` included; the other 15 `.txt` files there are
coverage and check pages), plus the 14 lists outside `decks/` that the pairing files name (B2e, and the carriers and scratch
lists of steps 8 and 8b). The card sets come from the card text in `engine/database.json`. `inventory.py` builds them and
`inventory_output.txt` prints every printing. A pairing is **expected to change** when a repaired mechanic can act in its games.
"Can act" does not mean it will: a game changes only if the cards meet in play. A pairing not listed cannot change through the
package.

Which lists hold the cards:

| Mechanic | Lists |
|---|---|
| Wild Swing (Gyarados) v a coin Ability | `l-sharpedo` (2 Gyarados A4 045). Four carriers supply the coin Ability. |
| Wellspring Dance, Tornado Shot, Double Splash, Triple Bombardment, second punch, Mischievous Ring, Litter | none |
| Will with a Confused attacker | Users: brew-01, brew-04, Dustin's 10. Twelve lists supply the Confusion (Weezing lists, Meowstic lists, brew-04, Dustin's 10, two scratch lists). |
| Victory Star with a block coin | none (draft D holds Victini, but no list holds a block-coin attack) |
| Will with a block coin | none |
| coin Abilities on your own Pokémon; the opponent's Active in an own-Bench choice; a copied discard attack | none |
| Trap Territory, two Ariados | Dustin's 12 and B2e's `h-whimsicott`. Both are one-sided: every pairing of these lists can change. |
| Luxury Coin on the opponent's Stadium | none (no Gholdengo list meets Mesagoza or Arcade) |
| a Fossil under an Item lock | none |
| Guts on your own Pokémon (E1) | none |
| Perish Body on a plain queued hit (E2) | none (no list holds Galarian Cursola) |

The pairings expected to change:

| Set | Expected to change | Which |
|---|---|---|
| Table, 28 cells (research lists) | 0 | |
| New 17 cells (scoreboard v3) | 0 | |
| B2e, 96 | 16 | `h-whimsicott` and Dustin's 12, each v all 8 panel lists (Trap Territory) |
| Carriers, steps 8 and 8b, 36 | 1 | `l-sharpedo` v `meowth_carefree` (Wild Swing) |
| Dustin's decks v the panel, step 7c, 32 | 0 | (it holds Dustin's 02, 06, 08 and 14) |
| Screen and floor (60 lists x 8 panel lists) | 11 | Dustin's 12 v all 8 (Trap Territory; floor page on record); brew-01, brew-04 and Dustin's 10 (floor page on record) v `t-weezing` (Will with a Confused attacker) |

So the switch costs 17 named pairings: 16 B2e and 1 carrier. The table and scoreboard v3 don't move. The screen and floor have
11 pairings over 4 lists. Two of those lists have floor pages that would need rerunning: Dustin's 10 (one pairing) and Dustin's
12 (all eight).

The amended draft D (one Mega Houndoom ex) doesn't change this. D holds no Will. Its Victini changes only against a block-coin
attacker, and no list holds one. Draft D's Victini against a Confused attacker is the official engine's Victory Star repair,
not the round-2 package.

## 2. Counters for every repaired mechanic

`../coin_prevention_repair_2026-09-30/instrument_scan.py`, the package's watch script, gets the round-2 package's counters (its
docstring has the full list). Each counter records every tick it fires at (the F5 pattern as corrected on Oct 1). They watch
only: they read the board before a tick, the moves offered and chosen, and the engine's own forecasts on copies of the board.

The method: where a counter compares forecasts, the copy is the same board with one Pokémon's printed Ability taken away. If the
engine's forecast of the move changes, that Ability's repaired path ran. Nothing else on the board moves, so the engine decides
the rest: suppression, damage and knockouts.

| Mechanic | Exact counter (fires when the repaired path runs) | Off the gate (the rewritten lines ran and gave the old answer) |
|---|---|---|
| The later round's seven sites | `coin_queued_by_attack` {attack: ticks}: the queued coin choice offered, by attack | `offgate_by_attack` {attack: ticks}: a plain choice after one of the rewritten attacks; Wild Swing apart from Chase Order |
| A4 own-Bench choice, A5 copied discard attack (plain queued damage) | `coin_plain_damage_by_attack`, `coin_plain_damage_chosen` | `offgate_plain_attack_damage` |
| E2 Perish Body on a plain queued hit | `perish_plain_hit_offered`, `perish_plain_hit_chosen` | `offgate_plain_attack_damage` |
| A4 coin Abilities on your own Pokémon (attack outcome) | `coin_own_side_split` | the opponent-side split, already counted (`coin_cut_recorded`, `coin_full_prevention`) |
| E1 Guts on your own Pokémon | `guts_own_side_split` | `offgate_guts_opponent_split` |
| Item 1 Will with a Confused attacker | `will_confused_attack` | `offgate_confused_attack` |
| A2 Will with a block coin | `will_block_coin_attack` | `offgate_block_coin_attack` |
| A1 Victory Star with a block coin | `vs_block_coin_built`, `vs_block_coin_choice_offered` | `offgate_vs_ungated_built` |
| Item 4 Trap Territory | `trap_territory_offer_changed`, `trap_territory_outcome_changed` (against the same board with one Ariados) | `offgate_trap_territory_one`; superset `trap_territory_two_in_play` |
| Luxury Coin on the opponent's Stadium | `luxury_coin_opp_stadium` | `offgate_luxury_coin_offered` |
| A Fossil under an Item lock | `fossil_item_lock` | `offgate_fossil_offered` |

Victini's caveat text changes no play, so it has no counter.

**The probe** (`counter_probe_readiness.rs`, output in `counter_probe_readiness_output.txt`) runs the counters' own lines on
boards built with `test_support`. `instrument_scan.py --emit-fns` writes out the same text the script puts into the scan. Every
counter is checked on a board where it must fire and a matching board where it must not, and each check compares the exact set
of counters that fire at that tick. Result: **49 checks, 0 failures.** The boards are the ones the package's own tests use: the
seven sites into Meowth or Togekiss and into Bulbasaur, Raging Thunder, a copied Chase Order, Chase Order into Galarian Cursola,
Earthquake with your own Meowth or Ursaluna, Team Rocket's Moltres ex with Will, Confusion, a block coin and Victini, Trap
Territory with one and two Ariados, Gholdengo with Arcade, and a Helix Fossil under Jingly Noise.

Both watch scripts still apply alone and in either order, giving the same sorted lines, and the instrumented scan compiles on this
branch's engine.

On this branch the Victory Star script's `vs_confusion_first_built` also fires when Will is pending or a block coin is present
too. The old engine built no pause in those cases. `will_confused_attack` and `vs_block_coin_built` tell those cases apart.

**The smoke check** (`counter_smoke/`: `run_smoke.sh`, `pairs.tsv`, `compare.py`, `compare_output.txt`, `run_output.txt` with
the scans' sha256s). This branch's scan was run plain and with both watch scripts, on 6 pairings where the package can act: your
deck 12 v `t-weezing` and v `t-lucario`, your deck 10 and brew-04 v `t-weezing`, l-sharpedo v `meowth_carefree`, and the
later round's scratch deck v its Meowth deck. km3 played both sides, 20 games a pairing, on seeds 20,990,000,000 + pairing ×
10,000 + i (Claude Code's diagnostic block). No table game was played.
- **The counters change no play:** the moves are the same in 120 of 120 games, and the legality checks found nothing.
- **They fire in real games:**
  - Deck 12 v `t-lucario`: two Ariados were in play in 8 games; that changed the moves offered in 6 games (16 ticks) and an
    outcome in 1.
  - Deck 12 v `t-weezing`: two Ariados in 3 games, with no move or outcome changed.
  - The later round's queued choice was offered against Carefree Steps (Wild Swing, Tornado Shot, Wellspring Dance,
    Mischievous Ring), and its off-gate choices ran too, Litter included.
- **Silent here:** the Will lists never attacked while Confused in these 40 games, so their counters read 0 (the inventory's
  "can act" is not "will act"). No list has a block coin, own-side coin, Guts, Perish Body, Gholdengo or a Fossil, so those
  counters are proven on the probe's boards only.

## 3. coin_probe v2 and the classifier, checked on the Oct 1 hand-off

**coin_probe v2** (`coin_probe_v2.rs`; v1 is `../engine_switch_rules_2026-10/coin_probe.rs`, unchanged) counts plies the way
km3's and k3's own search does on the official engine (`expectiminimax_player.rs`).
- The root move costs a ply.
- A forced continuation costs nothing, so the search crosses the forced end of the opponent's turn. So does a free frame (a
  pending coin choice, or a frame of only queued attack-damage and random-evolution choices) and a promotion.
- The search stops where the bots stop: when the current player isn't the mover, and after 3 plies.
- Everything else is v1's. The one addition is `--node-limit`: the default stays at v1's 60,000, and any other limit is named
  on the command line.
- Its self-test (`coin_probe_v2_selftest.txt`) passes: 7 checks and 3 frame checks, 0 failures.

**tightened_rule v2** (`tightened_rule_v2.py`; v1 unchanged) changes one thing.
- When one game is a prefix of the other and R's game is the longer one, R's first extra tick is a move the old engine never
  offered.
- If an exact counter fires at that tick, the game now reads ON THE BOARD (`extra_tick_hits`), not unexplained.

**The check** (`validate_v2.py`, `v2_verdicts.tsv`, `v2_summary.txt`) covered all 3,813 changed games of the hand-off. It used
step 8c's stored traces and counters, ran coin_probe v2 again on the official engine (main-8626a35), and kept step 8c's Victory
Star probe results.
- **The first difference is the same as step 8c's in 3,813 of 3,813 games.**
- **Exactly the 8 expected verdicts changed; the other 3,805 are unchanged.**
  - The 5 promotion games (km3 1/399, 4/7, 4/360, 21/310 and k3 4/7): UNEXPLAINED → lookahead. The probe now finds the
    queued coin choice 3 plies deep, after the promotion and the free end of the opponent's turn, in a frame the bots resolve
    for free.
  - km3 4/106: NEEDS A JUDGMENT → lookahead. The choice is found after 2 plies, since Quick-Grow Extract's random evolution
    is free.
  - The 2 pairing-31 games (km3 31/12, k3 31/81): LENGTH → ON THE BOARD. `vs_confused_choice_offered` and `_chosen` fire at R's
    extra tick.
- Verdicts now: 2,416 on the board and 1,397 lookahead only. No game is unexplained, needs a judgment, or is a length case.
- Golden checks (v2 at the last coin tick that explains each on-the-board game): 2,379 of 2,379 show the gate on the table.
- Step 8c's 12 negative controls: v2 finds nothing in all 12.
- **The node limit.** In the first full run, two other games (pairing 12, game 69, both bots) fell to unexplained. The probe
  stopped at 60,000 nodes there before finding anything: counting free frames free makes its search tree bigger.
  - At 600,000 nodes both are found: queued 3 plies deep in a free frame, as v1 found them.
  - The check now runs again, at 600,000 nodes, any probe that stops at the limit having found nothing. That was these 2 games
    and no control.
  - Three other probes stopped at the limit after they had already found their path.
- Against v1 on the 1,397 lookahead games (the smallest ply found): 1,382 the same, 1 smaller, 5 found only by v2 (the
  promotion games), 0 found only by v1.
  - 9 games have no coin path in either probe. All 9 are Victory Star games, explained by the Victory Star probe as in step 8c.
