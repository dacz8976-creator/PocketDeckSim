# Consistency: research-suicune

`decks/research/suicune.txt` · Energy: Water · main attacker: Suicune ex (Basic), Crystal Waltz [WW] 20 · combo: Suicune ex + Baxcalibur

**In one line:** research-suicune: one-Basic opening 63%; Suicune ex online by own T3 87% first / 88% second (T4 92%/92%); combo by T4 75%/74%; goldfish (scripted pilot v aa): damaging attack by own T3 81% with 0.2 pts conceded first, Suicune ex attacks by T4 69% with 0.5 conceded first, 2.4 dead cards/turn; unpriced-text cards (a): 2

Turns are the player's own turns (own turn 1 is your first turn whether you go first or second). Going first: no Energy on own turn 1, but you draw. Nobody evolves on their own turn 1. Solitaire figures come from 10,000 deals per seat (about ±1 point); the opening table is exact.

## 1. Opening hand

5 Basic Pokémon in 20 cards. The 5-card hand is dealt at random; only a hand with no Basic has one random card swapped for a random Basic, so extra Basics are not favoured. The opening is the same going first or second.

| Basics in the opening hand | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| exact | 63% | 29% | 7% | 0% | 0% |
| solitaire check | 63% | 30% | 7% | 0% | 0% |

**Exactly one Basic: 63%** (of which 19% are swap-in hands that had none).

| Only Basic in the hand is… | chance | | Card in the opening hand | chance |
|---|---|---|---|---|
| Frigibax | 25% | | Frigibax | 52% |
| Suicune ex | 25% | | Baxcalibur | 43% |
| Chien-Pao ex | 13% | | Suicune ex | 52% |

## 2. Main attacker online

"Online" = Suicune ex in play (Active or Bench) with the Energy for Crystal Waltz [WW] attached, at the moment you would attack. Fastest possible without acceleration: own turn 3 going first, 2 going second.

| | going first T2 | T3 | T4 | going second T2 | T3 | T4 |
|---|---|---|---|---|---|---|
| Suicune ex online | 19% | 87% | 92% | 79% | 88% | 92% |
| Suicune ex in play (any Energy) | 87% | 92% | 95% | 88% | 92% | 95% |
| online, draw/search cards not played | 5% | 65% | 70% | 58% | 64% | 70% |

Where "in play" is well above "online", Energy is the limit (one a turn); where both are low, finding the cards is the limit. The last row shows what the list's draw and search cards add.

## 3. Stage 2 in play

Stage 2 cards: Baxcalibur. Rare Candy in the list: yes.

| | going first T3 | T4 | going second T3 | T4 |
|---|---|---|---|---|
| any Stage 2 in play (list as built) | 61% | 78% | 61% | 77% |
| same deals, Rare Candy never played | 0% | 0% | 0% | 0% |

## 4. Combo assembled

Pieces: Suicune ex + Baxcalibur. A Pokémon piece counts when it is in play; a Trainer piece when it is in hand or already played.

| by own turn | 2 | 3 | 4 | 5 |
|---|---|---|---|---|
| going first | 34% | 57% | 75% | 85% |
| going second | 34% | 57% | 74% | 84% |

Each piece on its own (going first / second):

| piece | by T3 | by T5 |
|---|---|---|
| Suicune ex | 92% / 92% | 98% / 98% |
| Baxcalibur | 61% / 61% | 87% / 86% |

### Drawing each card

Each card, drawn or fetched at least once by own turn 3 / by own turn 5 (the opening hand counts; going first, the list's draw and search cards played; "no draw" = the same deals with them left in hand):

| card | copies | by T3 | by T5 | by T3, no draw | by T5, no draw |
|---|---|---|---|---|---|
| Frigibax | 2 | 96% | 99% | 70% | 80% |
| Baxcalibur | 2 | 86% | 94% | 64% | 75% |
| Suicune ex | 2 | 92% | 98% | 70% | 80% |
| Chien-Pao ex | 1 | 81% | 93% | 43% | 52% |
| Professor's Research | 2 | 77% | 90% | 63% | 75% |
| Team Rocket's Boss | 1 | 64% | 84% | 39% | 49% |
| Pokémon Center Lady | 1 | 63% | 83% | 39% | 49% |
| Copycat | 1 | 60% | 81% | 39% | 49% |
| Rare Candy | 2 | 86% | 94% | 64% | 75% |
| Poké Ball | 2 | 85% | 94% | 63% | 75% |
| Field Blower | 1 | 63% | 83% | 39% | 49% |
| Inflatable Boat | 1 | 64% | 84% | 40% | 51% |
| Giant Cape | 1 | 64% | 84% | 38% | 48% |
| Soothing Shore | 1 | 63% | 83% | 39% | 49% |

## 5. Goldfish against the engine

The real engine (rules4: rl/addon-0.7.2/deckgym and the pdl_rl_env 0.7.2 add-on built from the same rules) plays this list against `decks/research/weezing.txt` piloted by the engine's `aa` bot (attach-and-attack: it puts its Energy on the Active and attacks whenever it can, and nothing else). Because the engine lists End Turn first among the legal moves and `aa` takes the first move when it cannot attach or attack, `aa` never benches a Pokémon, not even at setup, and never plays a Trainer: the opponent is one Active Pokémon, and knocking it out wins. That makes it a fixed clock (here mostly Hoopa ex: 30 a turn from its first Energy, 100 from its third), not a real opponent.

Two pilots for this list. **sp** (scripted pilot, the main reading): the solitaire model's priorities playing the real engine through the add-on: benches Basics, plays the draw, search, Rare Candy and Energy cards, evolves, puts Energy on the main line, attaches defensive Tools, heals a hurt Active, retreats to a Pokémon that can attack, and attacks for the most damage. **aa** (the brief's pilot): the engine's own bot on this side too, so both sides have a single Pokémon and the game ends at the first knockout; its "points conceded" can never exceed what one knockout gives. `et` ends every turn at once and never attacks, so it is not used. 150 games per pilot; the coin decides who goes first.

"Damaging attack" = the list's first attack that damaged or knocked out the opposing Active (poison it applied counts). "Conceded" = the opponent's points at that moment (or at the end if it never came). "Main attacks" = the first attack by the main attacker. "Dead" = cards in hand at the end of the turn that the rules did not let you play then (own turns 1-4; a second Supporter after one was played counts as dead; cards that need an opposing Bench, such as Cyrus and Sabrina, are left out because this opponent never has one).

| pilot | seat | games | won | damaging attack by T2 | by T3 | by T4 | never | points conceded before it | conceded 2+ | main attacks by T3 | by T4 | never | conceded before main | dead cards / turn |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sp | first | 66 | 65% | 26% | 65% | 88% | 9% | 0.39 | 11% | 55% | 70% | 23% | 0.64 | 2.3 |
| sp | second | 84 | 88% | 71% | 94% | 98% | 1% | 0.07 | 2% | 57% | 69% | 29% | 0.40 | 2.4 |
| aa | first | 75 | 4% | 29% | 29% | 29% | 71% | 1.13 | 53% | - | - | - | - | 1.7 |
| aa | second | 75 | 20% | 33% | 33% | 33% | 67% | 1.20 | 55% | - | - | - | - | 1.7 |

Most often dead at end of turn (sp): Rare Candy 48%, Baxcalibur 42%, Field Blower 26%, Team Rocket's Boss 21% of turn-ends.

Most often dead at end of turn (aa): Rare Candy 53%, Baxcalibur 48%, Field Blower 36%, Pokémon Center Lady 10% of turn-ends.

Engine game seeds (one per game): sp: 21,002,160,000 to 21,002,160,149, aa: 21,002,165,000 to 21,002,165,149. The won column is against a single Pokémon that never plays a Trainer and means little; read the tempo columns. The `aa` opponent also never plays a card, so its hand grows and Copycat draws more than it would on the ladder.

## 6. Coverage flag

Cards that hit known blind spots of the engine's bots, so the simulator's numbers for this list are less trustworthy where these cards matter:
- **(a)** text names the opponent's hand or deck: blind k3 leaves the move unpriced (engine/src/observation.rs `hidden_continuation_reason`).
- **(b)** attack effect outside the damage estimator: the bots value the attack at printed damage (engine/src/players/value_functions.rs `estimated_attack_damage_ex`, fallback `_ => fixed`; effect texts read from engine/src/actions/effect_mechanic_map.rs). "b-" = the effect does not change damage (status, self-damage), so only its side effect is unvalued.
- **(c)** played from hand: the opponent-reply search (the `o` tiers such as b3o3n4; k3 has no reply ply) only considers attacks, retreats, Abilities, draws and the turn's Energy (engine/src/players/expectiminimax_player.rs `is_public_information_action`).

| card | flags |
|---|---|
| Baxcalibur ×2 | **(c)** evolves from hand: the opponent's reply search never sees the evolution |
| Suicune ex ×2 | **(c)** a copy benched from hand changes the board (passive Ability): not seen by the reply search |
| Team Rocket's Boss ×1 | **(a)** card names the opponent's hand or deck: blind k3 leaves it unpriced |
| Pokémon Center Lady ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Copycat ×1 | **(a)** card names the opponent's hand or deck: blind k3 leaves it unpriced |
| Rare Candy ×2 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Field Blower ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Inflatable Boat ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Giant Cape ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |
| Soothing Shore ×1 | **(c)** played from hand and changes the next exchange: the opponent's reply search never sees it |

**Reading:** k3 leaves Team Rocket's Boss, Copycat unpriced. Bot numbers for this list are untrusted to that extent.

## Draw, search and Energy effects in this list

What the solitaire model plays (card text from lib/card.py):

| card | text | model |
|---|---|---|
| Baxcalibur ×2 | Ability Ice Maker: Once during your turn, you may take a [W] Energy from your Energy Zone and attach it to the [W] Pokémon in the Active Spot. | ability modeled: extra 1 [W] to the Active |
| Suicune ex ×2 | Ability Legendary Pulse: At the end of your turn, if this Pokémon is in the Active Spot, draw a card. | ability modeled: end of turn draw 1 (if Active) |
| Professor's Research ×2 | Draw 2 cards. | modeled: draw 2 |
| Team Rocket's Boss ×1 | Look at your opponent's hand and put any number of Basic Pokémon you find there onto your opponent's Bench. | ignored: not a draw, search, evolution or Energy effect |
| Pokémon Center Lady ×1 | Heal 30 damage from 1 of your Pokémon, and it recovers from all Special Conditions. | ignored: not a draw, search, evolution or Energy effect |
| Copycat ×1 | Shuffle your hand into your deck. Draw a card for each card in your opponent's hand. | modeled: shuffle hand in, draw opponent-hand-size |
| Rare Candy ×2 | Choose 1 of your Basic Pokémon in play. If you have a Stage 2 card in your hand that evolves from that Pokémon, put that card onto the Basic Pokémon to evolve it, skipping the Stage 1. You can't use this card during your first turn or on a Basic Pokémon that was put into play this turn. | modeled: Basic straight to Stage 2 (not own turn 1, not a Basic played this turn) |
| Poké Ball ×2 | Put a random Basic Pokémon from your deck into your hand. | modeled: search 1 random Basic Pokémon to hand |
| Field Blower ×1 | Discard a Pokémon Tool card from a Pokémon (yours or your opponent's), or discard a Stadium card in play. | ignored: not a draw, search, evolution or Energy effect |
| Inflatable Boat ×1 | The Retreat Cost of the [W] Pokémon this card is attached to is 1 less. | ignored: not a draw, search, evolution or Energy effect |
| Giant Cape ×1 | The Pokémon this card is attached to gets +20 HP. | ignored: not a draw, search, evolution or Energy effect |
| Soothing Shore ×1 | At the end of each player's turn, that player heals 20 damage from each of their Pokémon that has any [W] Energy attached. | ignored: needs a board state the solitaire model does not track |

## How the solitaire pilot plays

Setup: all Basics in hand go into play (Active: a Basic with an "if Active" draw Ability, else one outside the main line). Each own turn: draw; then repeat until nothing changes: play a Stadium that does something here, use it, play Items (Poké Ball and other searches take a random matching card, as printed; Rare Candy on the main line first), bench Basics the plan needs (others only while the Bench has room to spare), evolve (main line first), use draw Abilities, attach Tool pieces; when nothing else moves, one Supporter: a search that finds a missing piece, else a draw, else Copycat when the hand is small and holds nothing needed (Copycat assumes the opponent holds 4 cards). Then the turn's Energy (random among the declared types) goes to the main line first, then other combo attackers, else the Active; Energy from the discard or from Abilities is added; then the check; an Ability that ends the turn is used only when the main attacker cannot attack. No opponent, no knockouts, no retreat, no attacks (attack effects that set up, such as Flock or Glittering Gift, are ignored), no coin-flip Supporters. Hand limit 10.

Generated by `lib/consistency.py` in 38 s; solitaire seed 21,002,160,000 (Python random, same deals across variants).
