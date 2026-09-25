# Consistency: brew-03a-arceus-nihilego-toxapex

`decks/brews/brew-03a-arceus-nihilego-toxapex.txt` · Energy: Darkness · main attacker: Arceus ex (Basic), Ultimate Force [CCC] 70 · combo: Toxapex + Nihilego

Ladder record: 1-3

**In one line:** brew-03a-arceus-nihilego-toxapex: one-Basic opening 52%; Arceus ex online by own T3 0% first / 75% second (T4 82%/83%); combo by T4 66%/65%; goldfish (scripted pilot v aa): damaging attack by own T3 35% with 0.7 pts conceded first, Arceus ex attacks by T4 49% with 0.8 conceded first, 0.7 dead cards/turn; unpriced-text cards (a): 0

Turns are the player's own turns (own turn 1 is your first turn whether you go first or second). Going first: no Energy on own turn 1, but you draw. Nobody evolves on their own turn 1. Solitaire figures come from 10,000 deals per seat (about ±1 point); the opening table is exact.

## 1. Opening hand

6 Basic Pokémon in 20 cards. The 5-card hand is dealt at random; only a hand with no Basic has one random card swapped for a random Basic, so extra Basics are not favoured. The opening is the same going first or second.

| Basics in the opening hand | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| exact | 52% | 35% | 12% | 1% | 0% |
| solitaire check | 51% | 36% | 12% | 1% | 0% |

**Exactly one Basic: 52%** (of which 13% are swap-in hands that had none).

| Only Basic in the hand is… | chance | | Card in the opening hand | chance |
|---|---|---|---|---|
| Arceus ex | 17% | | Arceus ex | 49% |
| Nihilego | 17% | | Nihilego | 49% |
| Mareanie | 17% | | Mareanie | 49% |
|  |  | | Toxapex | 43% |

## 2. Main attacker online

"Online" = Arceus ex in play (Active or Bench) with the Energy for Ultimate Force [CCC] attached, at the moment you would attack. Fastest possible without acceleration: own turn 4 going first, 3 going second.

| | going first T2 | T3 | T4 | going second T2 | T3 | T4 |
|---|---|---|---|---|---|---|
| Arceus ex online | 0% | 0% | 82% | 0% | 75% | 83% |
| Arceus ex in play (any Energy) | 82% | 88% | 92% | 83% | 88% | 93% |
| online, draw/search cards not played | 0% | 0% | 62% | 0% | 56% | 62% |

Where "in play" is well above "online", Energy is the limit (one a turn); where both are low, finding the cards is the limit. The last row shows what the list's draw and search cards add.

## 3. Stage 2 in play

No Stage 2 in the list.

## 4. Combo assembled

Pieces: Toxapex + Nihilego. A Pokémon piece counts when it is in play; a Trainer piece when it is in hand or already played.

| by own turn | 2 | 3 | 4 | 5 |
|---|---|---|---|---|
| going first | 39% | 54% | 66% | 77% |
| going second | 39% | 53% | 65% | 77% |

Each piece on its own (going first / second):

| piece | by T3 | by T5 |
|---|---|---|
| Toxapex | 62% / 62% | 81% / 81% |
| Nihilego | 88% / 88% | 95% / 96% |

### Drawing each card

Each card, drawn or fetched at least once by own turn 3 / by own turn 5 (the opening hand counts; going first, the list's draw and search cards played; "no draw" = the same deals with them left in hand):

| card | copies | by T3 | by T5 | by T3, no draw | by T5, no draw |
|---|---|---|---|---|---|
| Arceus ex | 2 | 88% | 96% | 68% | 78% |
| Nihilego | 2 | 88% | 96% | 68% | 78% |
| Mareanie | 2 | 88% | 96% | 68% | 79% |
| Toxapex | 2 | 76% | 88% | 64% | 75% |
| Professor's Research | 2 | 64% | 77% | 65% | 76% |
| Poké Ball | 2 | 75% | 86% | 65% | 76% |
| Team Rocket's Goo-zooka | 2 | 76% | 87% | 65% | 76% |
| Giant Cape | 1 | 48% | 62% | 39% | 49% |
| Cyrus | 1 | 49% | 62% | 38% | 49% |
| Rocky Helmet | 1 | 49% | 64% | 39% | 50% |
| Poison Barb | 1 | 50% | 65% | 40% | 50% |
| Sabrina | 1 | 49% | 63% | 39% | 49% |
| X Speed | 1 | 49% | 63% | 40% | 49% |

## 5. Goldfish against the engine

The real engine (rules4: rl/addon-0.7.2/deckgym and the pdl_rl_env 0.7.2 add-on built from the same rules) plays this list against `decks/research/weezing.txt` piloted by the engine's `aa` bot (attach-and-attack: it puts its Energy on the Active and attacks whenever it can, and nothing else). Because the engine lists End Turn first among the legal moves and `aa` takes the first move when it cannot attach or attack, `aa` never benches a Pokémon, not even at setup, and never plays a Trainer: the opponent is one Active Pokémon, and knocking it out wins. That makes it a fixed clock (here mostly Hoopa ex: 30 a turn from its first Energy, 100 from its third), not a real opponent.

Two pilots for this list. **sp** (scripted pilot, the main reading): the solitaire model's priorities playing the real engine through the add-on: benches Basics, plays the draw, search, Rare Candy and Energy cards, evolves, puts Energy on the main line, attaches defensive Tools, heals a hurt Active, retreats to a Pokémon that can attack, and attacks for the most damage. **aa** (the brief's pilot): the engine's own bot on this side too, so both sides have a single Pokémon and the game ends at the first knockout; its "points conceded" can never exceed what one knockout gives. `et` ends every turn at once and never attacks, so it is not used. 150 games per pilot; the coin decides who goes first.

"Damaging attack" = the list's first attack that damaged or knocked out the opposing Active (poison it applied counts). "Conceded" = the opponent's points at that moment (or at the end if it never came). "Main attacks" = the first attack by the main attacker. "Dead" = cards in hand at the end of the turn that the rules did not let you play then (own turns 1-4; a second Supporter after one was played counts as dead; cards that need an opposing Bench, such as Cyrus and Sabrina, are left out because this opponent never has one).

| pilot | seat | games | won | damaging attack by T2 | by T3 | by T4 | never | points conceded before it | conceded 2+ | main attacks by T3 | by T4 | never | conceded before main | dead cards / turn |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sp | first | 72 | 85% | 0% | 15% | 42% | 39% | 1.00 | 35% | 0% | 25% | 53% | 1.08 | 0.7 |
| sp | second | 78 | 95% | 17% | 54% | 87% | 10% | 0.45 | 9% | 37% | 71% | 27% | 0.50 | 0.8 |
| aa | first | 84 | 27% | 0% | 39% | 54% | 46% | 0.86 | 39% | - | - | - | - | 0.6 |
| aa | second | 66 | 30% | 50% | 100% | 100% | 0% | 0.00 | 0% | - | - | - | - | 0.4 |

Most often dead at end of turn (sp): Toxapex 28%, Mareanie 7%, Arceus ex 5%, Professor's Research 5% of turn-ends.

Most often dead at end of turn (aa): Toxapex 46% of turn-ends.

Engine game seeds (one per game): sp: 21,002,030,000 to 21,002,030,149, aa: 21,002,035,000 to 21,002,035,149. The won column is against a single Pokémon that never plays a Trainer and means little; read the tempo columns. The `aa` opponent also never plays a card, so its hand grows and Copycat draws more than it would on the ladder.

## 6. Coverage flag

Cards that hit known blind spots of the engine's bots, so the simulator's numbers for this list are less trustworthy where these cards matter:
- **(a)** text names the opponent's hand or deck: blind k3 leaves the move unpriced (engine/src/observation.rs `hidden_continuation_reason`).
- **(b)** attack effect outside the damage estimator: the bots value the attack at printed damage (engine/src/players/value_functions.rs `estimated_attack_damage_ex`, fallback `_ => fixed`; effect texts read from engine/src/actions/effect_mechanic_map.rs). "b-" = the effect does not change damage (status, self-damage), so only its side effect is unvalued.
- **(c)** played from hand: the opponent-reply search (the `o` tiers such as b3o3n4; k3 has no reply ply) only considers attacks, retreats, Abilities, draws and the turn's Energy (engine/src/players/expectiminimax_player.rs `is_public_information_action`).

| card | flags |
|---|---|
| Arceus ex ×2 | **(c)** a copy benched from hand changes the board (passive Ability): not seen by the reply search |
| Nihilego ×2 | **(b-)** attack New Wave: effect not in the damage estimate (mechanic InflictStatusConditions has no damage estimator); damage read as printed 30<br>**(c)** a copy benched from hand changes the board (passive Ability): not seen by the reply search |
| Mareanie ×2 | **(b)** attack Venoshock: damage-changing effect, mechanic ExtraDamageIfDefenderStatus has no damage estimator; the bots value it at printed 20 |
| Toxapex ×2 | **(b)** attack Severe Poison: damage-changing effect, mechanic InflictPoisonWithCustomCheckupDamage has no damage estimator; the bots value it at printed 0<br>**(c)** evolves from hand: the opponent's reply search never sees the evolution |
| Team Rocket's Goo-zooka ×2 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Giant Cape ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Cyrus ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Rocky Helmet ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Poison Barb ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Sabrina ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| X Speed ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |

**Reading:** the damage of Mareanie, Toxapex is read as printed. Bot numbers for this list are untrusted to that extent.

## Draw, search and Energy effects in this list

What the solitaire model plays (card text from lib/card.py):

| card | text | model |
|---|---|---|
| Professor's Research ×2 | Draw 2 cards. | modeled: draw 2 |
| Poké Ball ×2 | Put a random Basic Pokémon from your deck into your hand. | modeled: search 1 random Basic Pokémon to hand |
| Team Rocket's Goo-zooka ×2 | Until the end of your opponent's next turn, your opponent's Active Pokémon's Retreat Cost is 1 more. | ignored: not a draw, search, evolution or Energy effect |
| Giant Cape ×1 | The Pokémon this card is attached to gets +20 HP. | ignored: not a draw, search, evolution or Energy effect |
| Cyrus ×1 | Switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot. | ignored: not a draw, search, evolution or Energy effect |
| Rocky Helmet ×1 | If the Pokémon this card is attached to is in the Active Spot and is damaged by an attack from your opponent's Pokémon, do 20 damage to the Attacking Pokémon. | ignored: not a draw, search, evolution or Energy effect |
| Poison Barb ×1 | If the Pokémon this card is attached to is your Active Pokémon and is damaged by an attack from your opponent's Pokémon, the Attacking Pokémon is now Poisoned. | ignored: not a draw, search, evolution or Energy effect |
| Sabrina ×1 | Switch out your opponent's Active Pokémon to the Bench. (Your opponent chooses the new Active Pokémon.) | ignored: not a draw, search, evolution or Energy effect |
| X Speed ×1 | During this turn, the Retreat Cost of your Active Pokémon is 1 less. | ignored: not a draw, search, evolution or Energy effect |

## How the solitaire pilot plays

Setup: all Basics in hand go into play (Active: a Basic with an "if Active" draw Ability, else one outside the main line). Each own turn: draw; then repeat until nothing changes: play a Stadium that does something here, use it, play Items (Poké Ball and other searches take a random matching card, as printed; Rare Candy on the main line first), bench Basics the plan needs (others only while the Bench has room to spare), evolve (main line first), use draw Abilities, attach Tool pieces; when nothing else moves, one Supporter: a search that finds a missing piece, else a draw, else Copycat when the hand is small and holds nothing needed (Copycat assumes the opponent holds 4 cards). Then the turn's Energy (random among the declared types) goes to the main line first, then other combo attackers, else the Active; Energy from the discard or from Abilities is added; then the check; an Ability that ends the turn is used only when the main attacker cannot attack. No opponent, no knockouts, no retreat, no attacks (attack effects that set up, such as Flock or Glittering Gift, are ignored), no coin-flip Supporters. Hand limit 10.

Generated by `lib/consistency.py` in 30 s; solitaire seed 21,002,030,000 (Python random, same deals across variants).
