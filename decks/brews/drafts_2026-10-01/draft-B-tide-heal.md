# Draft B: Tide Heal (Water, no ex)

Draft, not run, not a ranking. List: `draft-B-tide-heal.txt`. Written Oct 1, 2026 by the Sonnet session "Opus agents progress".
This is the weakest-evidenced of the four; it is here because it is the one built around the Lucario list's design.

## The list (Water energy)

| # | Card | Id | Text (from the database) |
|---|---|---|---|
| 2 | Staryu | B4 032 | Water Basic, HP 50, weak Lightning. [W] Swift 20: damage isn't affected by Weakness or by any effects on your opponent's Active |
| 2 | Starmie | B4 033 | Water Stage 1 from Staryu, HP 90, weak Lightning. [WC] Swift 60: same text |
| 2 | Feebas | A4a 021 | Water Basic, HP 30, weak Lightning. [W] Leap Out: switch this Pokémon with 1 of your Benched Pokémon |
| 2 | Milotic | A4a 022 | Water Stage 1 from Feebas, HP 120, weak Lightning, retreat 2. Ability Healing Ripples: once during your turn, when you play this Pokémon from your hand to evolve 1 of your Pokémon, you may heal 60 damage from 1 of your [W] Pokémon. [WC] Aqua Edge 60 |
| 1 | Wailmer | B1 056 | Water Basic, HP 100, weak Lightning, retreat 3. [CCC] Surf 50 |
| 1 | Wailord | B1 057 | Water Stage 1 from Wailmer, HP 200, weak Lightning, retreat 4. [CCCC] Whale Pump 60: 10 more damage for each [W] Energy attached to it |
| 2 | Professor's Research | P-A 007 | Supporter: draw 2 |
| 2 | Poké Ball | P-A 005 | Item: a random Basic from your deck into your hand |
| 1 | Copycat | B1 225 | Supporter: shuffle your hand into your deck, draw a card for each card in your opponent's hand |
| 1 | Cyrus | A2 150 | Supporter: switch in 1 of your opponent's Benched Pokémon that has damage on it |
| 1 | Irida | A2a 072 | Supporter: heal 40 from each of your Pokémon with any [W] Energy attached |
| 1 | Soothing Shore | B4 154 | Stadium: at the end of each player's turn, that player heals 20 from each of their Pokémon with any [W] Energy attached |
| 1 | Lucky Ice Pop | B2 145 | Item: heal 20 from your Active; on a coin heads it goes back to your hand |
| 1 | Elegant Cape | B3b 065 | Tool: +30 HP on a Stage 1 Pokémon |

Ten Pokémon (five Basics), ten Trainers, **no Pokémon ex**.

## Why it exists

`t-lucario.txt` is built to hit ex Pokémon: Arena of Antiquity +20 and Korrina +30 against an Active ex, Riolu +30 against an ex,
Fighting Coach +20 on every Fighting attack. A deck with no ex takes up to 160 from Mega Lucario ex instead of up to 210, and every
Knock Out it gives away is one point instead of two, so the opponent needs three Knock Outs and a lot of 120-HP bodies are healed
back each turn. Dustin's own deck 03 (Wailord / Indeedee wall) is the nearest thing he has logged on the floor (61% overall,
53% against Lucario); this list takes out the ex and adds two cheap attackers.

## The plan, by turn

1. **Turn 1.** Staryu Active, Feebas on the Bench; attach [W] to Staryu. (Feebas's Leap Out is a one-energy attack that swaps
   the Active with a Benched Pokémon: a pivot when Feebas or Wailmer is stuck in front.)
2. **Turn 2.** Evolve Staryu into Starmie and hit **Swift for 60** with two energies (second player on turn 2; first player on turn
   3). Swift ignores Weakness and anything on their Active, so it is a flat 60 through Heavy Helmet or a Metal Core Barrier.
3. **Turn 3.** Evolve Feebas into Milotic: **Healing Ripples** heals 60 from a Water Pokémon, then Aqua Edge for 60. Irida (40 on
   every Pokémon with a Water energy) and Soothing Shore (20 at the end of every turn) keep the bodies up.
4. **Late.** Wailord (200 HP, 60 plus 10 per Water energy, retreat 4) is the one big body; the rest are 60-damage Pokémon that
   share energy by swapping. The win is three Knock Outs on small Pokémon, or two Swifts plus a Cyrus finish on a Benched one.

## Interactions and engine support

Engine: all 14 ids complete in the coverage, no named limitation, **no card flagged for the bot** (the only one of the four with
an empty flag list).

- **Healing Ripples fires when Milotic evolves from your hand**, once per turn, and heals 60 from any Water Pokémon of yours
  (not only the Feebas it lands on): a damaged Starmie or Wailord is the target.
- **Swift's bypass is in the engine**: `hooks/core.rs:1257-1280` (the Sawk / Ledian clause) ignores ability-derived reductions,
  stored effects and damage-reducing Tools such as Heavy Helmet and Metal Core Barrier, and Weakness.
- **Soothing Shore is symmetric**: the opponent's Water Pokémon heal too. In a Suicune mirror that is a cost.
- **Swift is not affected by Weakness**: it does not gain the +20 on Fire decks either. Aqua Edge does.
- Starmie has HP 90 and Staryu 50: each is a one-point Knock Out for them and dies to any real hit. The plan is that the heals
  do not matter, but that the opponent spends three attacks on three points.

## What the bot may get wrong in a test

Nothing is flagged, so a floor page will not mark a role. The unflagged risk is the usual one: a depth-three search values heals
(Irida, Shore, Ripples) at the leaf by HP only, which is the right reading, and values cheap attackers by their damage, so I
expect a fair reading. The Water mirror and the Lightning decks are the panel lists to watch (see below).

## Versus the panel decks he loses to

**Lucario: no ex to punish, so Arena and Korrina do nothing; three Knock Outs are needed.** Lucario still deals 90 to 160 per
attack, so this is a plan that has to out-heal and out-trade, not out-damage them. Deck 03's 53% is the only floor evidence, and
it has ex. Suicune, Sceptile, Blaziken: no special claim; Starmie's Swift gives the deck a way through Heavy Helmet and Metal Core
Barrier decks.

## What would make me drop it

If a floor page puts it under 30% against Lucario, the no-ex idea has not worked for the bot and I would not spend a ladder game on
it. Brew 06 (also no ex, built against ex) lost its three ladder games for tempo; this list's first attack is a turn 2 Swift for
60, not a turn 3.
