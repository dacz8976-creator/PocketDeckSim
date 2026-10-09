# Round-2 readiness (the cloud, Oct 2)

Three short jobs to make the round-2 package (everything `claude/coin-prevention-round2` adds to the official engine: the
later coin round, the card-text job and its follow-up) ready for the next rules switch. There were no table games and no
`players/` change. P2 (Oct 8, return damage left by an attack takes Weakness) adds to sections 1 and 2, and its check in
coin_probe v2 (Oct 9) to section 3.

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

**P2 (Oct 8): return damage left by an attack takes Weakness** (`../coin_prevention_round2_2026-10-01/README.md`, "P2").
`inventory.py` now also builds the five attacks' eight printings (asserted from the card text) and the copy attacks that can use
one, adds the mechanic, and names every file that names a list holding them. It was rerun on main b77652d6:
`inventory_output_p2.txt`. `inventory_output.txt` stays as this section's Oct 2 page.
- **Lists:** brew-07 (1 Mega Sableye ex) and brew-09 (2) are the only lists that hold one of the five attacks. No list holds a
  copy attack, and the other 58 twenty-card lists in the checkout hold none of either.
- **Pairings expected to change through P2:**
  - table 0, new-17 0, B2e 0, carriers 0, 7c 0;
  - screen and floor: brew-07 v `t-altaria` and brew-09 v `t-altaria`. Espeon is the only Darkness-weak Pokémon on the 8 panel
    lists. Both lists have floor pages on record (`floor_brews_2026-09-28`, `floor_dustin_2026-09-30`).
- **The package's totals on main b77652d6:** 17 named pairings (unchanged). 13 screen pairings over 6 lists: the 11 above plus
  P2's 2.
- **The files that name the two lists** are listed on the page, by file name and by label: the X Speed census, the screen pages
  under `decks/screen/`, the goldfish pages and more.
- The page's first line names the checkout it read. `--root` and `--out` choose the checkout and the page.

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

**P2 (Oct 8): two more counters** (the docstring in `instrument_scan.py` has the details).

| Mechanic | Exact counter (fires when the repaired path runs) | Off the gate (the rewritten lines ran and gave the old answer) |
|---|---|---|
| P2: return damage left by an attack takes Weakness | `attack_return_weakness`: the chosen move runs the hit back on a damaged opposing Active that carries an attack's return damage, and its forecast leaves a different board with the attacker's printed Weakness taken away | `offgate_return_by_source` {sources: ticks}: every other such tick on a defender with a return-damage source ("attack", "Rocky Helmet", "Ability", or a combination joined with "+") |

- **The method is the same,** with the attacker's printed Weakness taken away instead of an Ability.
- **The moves that run the hit back:**
  - Attack, ApplyDamage from an attack into the opposing Active, and ApplyQueuedAttackDamage;
  - Victory Star's Keep and Reroll;
  - the held-back ResolveAttackRetaliation.
- **Only forecast branches where the hit back has landed count.** A hit back the move holds behind a choice (Psy Turbo's Attach,
  U-turn's switch) is counted at its ResolveAttackRetaliation tick. A held-back frame an earlier move left doesn't hide one: an
  attack that does its damage through a choice leaves an empty frame under it.
- **A defender with no return-damage source isn't counted,** so the 49 checks above keep their sets.
- **An independent review caught a gap in the first draft.** It missed a hit back landing at an ApplyDamage tick while that empty
  frame from the same attack was still on the stack (Azelf's Psychic Arrow). It was fixed before the commit, and the probe has
  that board.

**The probe** gains 29 checks, 78 in all:
- each of the five attacks against a weak attacker (exact) and against Snorlax (off the gate, [attack]);
- a Knock Out only through Weakness (exact) and one either way (off the gate);
- Rocky Helmet, Iron Jugulis and Druddigon (off the gate);
- the Helmet with Cursed Jewel (exact; [attack+Rocky Helmet] against Snorlax);
- no source (nothing);
- Psy Turbo and U-turn: nothing at the Attack tick and at the Attach or switch tick; at the ResolveAttackRetaliation tick, exact,
  or off the gate for U-turn's Benched attacker;
- ApplyDamage from an attack (exact);
- Azelf's Psychic Arrow: exact at the ApplyDamage tick, nothing at the empty frame left under the choice;
- Heat Rotom with Victini at the Keep tick (exact).

**The probe's result:**
- On P2: **78 checks, 0 failures** (`counter_probe_readiness_output.txt`).
- On the engine before P2, the same 78 boards give 11 failures, exactly the 11 exact rows, each read off the gate
  (`counter_probe_readiness_output_at_P.txt`). So the counter sees the change and isn't true by construction.

Both watch scripts still apply alone and in either order (the same sorted lines), and the scan instrumented with both compiles on
P2.

**P2's smoke** (`counter_smoke_p2/`: `run_smoke_p2.sh`, `pairs.tsv`, `compare.py`, `compare_output.txt`, `run_output.txt` with
the three scans' sha256s; `trace_patch.py`, `trace_P.txt`, `trace_P2.txt`, `first_difference.py`, `first_difference_output.txt`).
km3 played both sides of 50 deals of brew-07 and brew-09 v `t-altaria`, brew-09 v `t-sceptile` and brew-07 v `t-blaziken`. Each
deal was played on the engine before P2, on P2, and on P2 with both watch scripts, seeds 20,960,000,000 + pairing × 10,000 + i
(Claude Code's diagnostic block). No table game was played.
- **The counters change no play:** the same moves in 200 of 200 games.
- **P2 changed 3 games, all v `t-altaria` and all in look-ahead.** `first_difference.py` reads the traces of the three deals on
  both engines. Each first differs at a choice made from the same board, before any hit back had taken Weakness. In deal 1:21 a
  flat one had already landed, on an Eevee.
  - In deals 0:31 and 1:8 the armed Mega Sableye ex faced an Active Espeon.
  - In 1:21 it faced Mega Altaria ex, and the choice was whether to retreat into the Benched Espeon.
- **The exact counter fired in 7 games v `t-altaria`.** The off-gate counter fired in every pairing: [attack] where the hit back
  stayed flat, and [Rocky Helmet] v `t-blaziken`.

## 3. coin_probe v2 and the classifier, checked on the Oct 1 hand-off

**coin_probe v2** (`coin_probe_v2.rs`; v1 is `../engine_switch_rules_2026-10/coin_probe.rs`, unchanged) counts plies the way
km3's and k3's own search does on the official engine (`expectiminimax_player.rs`).
- The root move costs a ply.
- A forced continuation costs nothing, so the search crosses the forced end of the opponent's turn. So does a free frame (a
  pending coin choice, or a frame of only queued attack-damage and random-evolution choices) and a promotion.
- The search stops where the bots stop: when the current player isn't the mover, and after 3 plies.
- Everything else is v1's. The one addition is `--node-limit`: the default stays at v1's 60,000, and any other limit is named
  on the command line.
- Its self-test passed on Oct 2: 7 checks and 3 frame checks, 0 failures. `coin_probe_v2_selftest.txt` now holds the Oct 9 run,
  with P2's boards added (below): 14 checks and 3 frame checks, 0 failures.

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

### P2's check, RETURN (Oct 9)

The coordinator via Dustin, Oct 9, decision 12: "coin_probe v2's P2 check (the return-damage gate inside the search, both
halves)", tests first. It is a third condition in `coin_probe_v2.rs`, beside QUEUED and CUT, which are unchanged.

**In plain words**

- **What it finds:** a move inside the bots' 3-ply search that makes an attack's hit back (Cursed Jewel and the other four)
  land on a weak Attacking Pokémon, so that P2's +20 changes the board. That is the gate a P2 look-ahead game needs: the bot
  saw the +20 while it searched.
- **How it decides:** it runs the exact counter `attack_return_weakness`'s own lines on each move it applies (the same text
  `instrument_scan.py --emit-fns` puts into the watch build, included in the probe). So the trace half proves the same thing the
  counter counts on the board.
- **Where it counts the ply:** the same as the bots. The root move is ply 1, an ordinary move costs a ply, and a forced or free
  move costs none. Psy Turbo holds its hit back until its Energy is attached: the Attach is ply 2, and the forced
  ResolveAttackRetaliation after it is free, so the hit back reads 2.
- **The code-gate half** is written in the probe's docstring: `handle_attack_retaliation` adds the +20 only while the switch is
  on, the Attacking Pokémon is Active, and the defender carries an attack's return damage. Its four callers are named there.
- **It must be built on the candidate engine** (P2 or later). On main-8626a35 it can never fire.
- **The output:** a RETURN block like the others, and a new last line `RESULT_P2 ret=<n|none>`. The `RESULT` line is unchanged,
  since three scripts read it with an end anchor.

**Commits**

- `5191160`: tests first. Seven self-test boards, H-N, are added. The four with a return ply fail, because nothing searches
  for RETURN yet (`coin_probe_v2_selftest_before_return.txt`). The self-test now counts its failures and asserts at the end,
  so a failing run lists them all.
- `2d3eec4`: the check.

**Checks** (`p2_probe_checks.sh`, output `p2_probe_checks_output.txt`; built at `140c0be`)

- **Self-test:** 14 checks and 3 frame checks, 0 failures (`coin_probe_v2_selftest.txt`). A-G read as before. The new boards:
  - Spooky Shot (Houndstone) into an armed Mega Sableye ex: 1;
  - Hypnoblast (Espeon): 1;
  - Psy Turbo (Gardevoir, Ralts on the Bench): 2;
  - Houndstone at 50 HP (the +20 Knocks it Out): 1;
  - Rollout (Snorlax, not weak to Darkness): none;
  - Houndstone at 30 HP (Knocked Out either way): none;
  - an unarmed Mega Sableye ex: none.
- **The control:** with P2 off (`DECKGYM_FLAT_RETURN_DAMAGE=1`) exactly the four boards with a return ply fail.
- **The three games P2's smoke changed** (all in look-ahead, `counter_smoke_p2/first_difference_output.txt`), at the first
  differing tick:
  - pairing 0, deal 31, tick 44: 2 (Attach, then Hypnoblast);
  - pairing 1, deal 21, tick 84: 3 (Attach, Retreat, then Hypnoblast);
  - pairing 1, deal 8, tick 43: 2 (Attach, then Hypnoblast).
  With P2 off, none.
- **Golden:** the seven smoke games where the exact counter fired, at its tick: 1 in all seven, none with P2 off.
- **Controls:** four ticks of Mega Sableye ex v t-sceptile and t-blaziken (neither weak to Darkness) where only the off-gate
  counter fired: none in all four.
